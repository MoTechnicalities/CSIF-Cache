"""
CSIF-Cache phase-resonant semantic router.

Implements preflight short-circuit routing for high-certainty memory retrieval.
If certainty is low or drift is high, route to deep validation.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from core.math import normalized_resonance
from storage.inverted_index import InvertedIndex, NodeRef
from storage.rwif import CrystalBank

PREFLIGHT_RN_THRESHOLD = 0.05
PREFLIGHT_SIGMA_THRESHOLD = 0.05


@dataclass
class CandidateState:
    node_ref: NodeRef
    token_score: int
    phase: float
    sigma: float
    fact_text: str


@dataclass
class RouteResult:
    route: str
    cache_key: str
    latency_ms: float
    response: Optional[str]
    reason: str
    resonance: Optional[float]
    sigma: Optional[float]
    candidate_node_id: Optional[str]


class SemanticRouter:
    """Query proxy that short-circuits high-certainty memory lookups."""

    def __init__(self, bank: CrystalBank, index: Optional[InvertedIndex] = None) -> None:
        self.bank = bank
        self.index = index or InvertedIndex()
        if not self.index.refs:
            self.index.index_bank(bank)

        self._query_cache: Dict[str, Dict[str, object]] = {}
        self._node_state: Dict[str, Tuple[float, float]] = self._build_node_state()

    @staticmethod
    def query_cache_key(query_text: str, query_phase: float, query_sigma: float) -> str:
        # Quantize to keep deterministic keys while still encoding query-state context.
        canonical = f"{query_text.strip().lower()}|{query_phase:.6f}|{query_sigma:.6f}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _build_node_state(self) -> Dict[str, Tuple[float, float]]:
        """
        Build node phase/sigma estimates from incident edges.
        phase: mean of incident edge current phases
        sigma: max of incident edge sigmas
        """
        bucket: Dict[str, List[Tuple[float, float]]] = {}

        for crystal in self.bank.crystals.values():
            for edge in crystal.edges.values():
                edge_phase = edge.current_phase
                edge_sigma = edge.current_sigma
                bucket.setdefault(edge.source_node, []).append((edge_phase, edge_sigma))
                bucket.setdefault(edge.target_node, []).append((edge_phase, edge_sigma))

        state: Dict[str, Tuple[float, float]] = {}
        for node_id, samples in bucket.items():
            if not samples:
                continue
            phase = sum(p for p, _ in samples) / len(samples)
            sigma = max(s for _, s in samples)
            state[node_id] = (phase, sigma)
        return state

    def _fact_for_node(self, node_id: str) -> str:
        """Create a stable factual text from the first outgoing edge available."""
        for crystal in self.bank.crystals.values():
            nodes = crystal.nodes
            for edge in crystal.edges.values():
                if edge.source_node != node_id:
                    continue
                source_label = nodes[edge.source_node].label
                target_label = nodes[edge.target_node].label
                return f"{source_label} {edge.relation} {target_label}."

        for crystal in self.bank.crystals.values():
            if node_id in crystal.nodes:
                return crystal.nodes[node_id].label
        return "No fact available"

    def _candidate_states(self, query_text: str, top_k: int = 8) -> List[CandidateState]:
        candidates: List[CandidateState] = []
        for node_ref, token_score in self.index.lookup(query_text, top_k=top_k):
            phase, sigma = self._node_state.get(node_ref.node_id, (0.0, 1.0))
            candidates.append(
                CandidateState(
                    node_ref=node_ref,
                    token_score=token_score,
                    phase=phase,
                    sigma=sigma,
                    fact_text=self._fact_for_node(node_ref.node_id),
                )
            )
        return candidates

    def route_query(self, query_text: str, query_phase: float = 0.0, query_sigma: float = 0.02) -> RouteResult:
        started = time.perf_counter()
        key = self.query_cache_key(query_text, query_phase, query_sigma)

        cached = self._query_cache.get(key)
        if cached:
            latency_ms = (time.perf_counter() - started) * 1000.0
            return RouteResult(
                route="CACHE_HIT",
                cache_key=key,
                latency_ms=latency_ms,
                response=str(cached["response"]),
                reason="Query hash hit in local cache.",
                resonance=float(cached.get("resonance", 0.0)),
                sigma=float(cached.get("sigma", 0.0)),
                candidate_node_id=str(cached.get("candidate_node_id", "")) or None,
            )

        candidates = self._candidate_states(query_text)
        if not candidates:
            latency_ms = (time.perf_counter() - started) * 1000.0
            return RouteResult(
                route="DEEP_VALIDATION",
                cache_key=key,
                latency_ms=latency_ms,
                response=None,
                reason="No indexed concept match; route to full retrieval.",
                resonance=None,
                sigma=None,
                candidate_node_id=None,
            )

        best = max(candidates, key=lambda c: (c.token_score, -abs(c.phase - query_phase)))
        resonance = normalized_resonance(query_phase, best.phase)
        sigma = max(query_sigma, best.sigma)

        if best.sigma <= PREFLIGHT_SIGMA_THRESHOLD and resonance < PREFLIGHT_RN_THRESHOLD:
            self._query_cache[key] = {
                "response": best.fact_text,
                "resonance": resonance,
                "sigma": best.sigma,
                "candidate_node_id": best.node_ref.node_id,
            }
            latency_ms = (time.perf_counter() - started) * 1000.0
            return RouteResult(
                route="PREFLIGHT_SHORT_CIRCUIT",
                cache_key=key,
                latency_ms=latency_ms,
                response=best.fact_text,
                reason="High certainty and high coherence; return cached fact.",
                resonance=resonance,
                sigma=best.sigma,
                candidate_node_id=best.node_ref.node_id,
            )

        latency_ms = (time.perf_counter() - started) * 1000.0
        return RouteResult(
            route="DEEP_VALIDATION",
            cache_key=key,
            latency_ms=latency_ms,
            response=None,
            reason="Wide sigma or drift detected; escalate to deep validation.",
            resonance=resonance,
            sigma=sigma,
            candidate_node_id=best.node_ref.node_id,
        )

    def save_query_cache(self, path: str) -> None:
        """Persist query cache atomically to prevent corruption on crashes."""
        directory = os.path.dirname(path) or "."
        os.makedirs(directory, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory, delete=False, prefix=".cache-", suffix=".tmp"
        ) as tmp:
            json.dump(self._query_cache, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name

        os.replace(tmp_path, path)

    def load_query_cache(self, path: str) -> None:
        if not os.path.exists(path):
            self._query_cache = {}
            return
        with open(path, "r", encoding="utf-8") as handle:
            self._query_cache = json.load(handle)
