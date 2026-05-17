"""
Phase-keyed inverted index for CSIF-Cache.

Maps normalized tokens to stable node references so query routing can avoid
high-dimensional vector scans. Persistence uses atomic file replacement.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple

from storage.rwif import CrystalBank

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class NodeRef:
    """Stable reference to a node inside a crystal bank."""

    node_id: str
    crystal_id: str
    label: str
    slot64: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "node_id": self.node_id,
            "crystal_id": self.crystal_id,
            "label": self.label,
            "slot64": self.slot64,
        }

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "NodeRef":
        return NodeRef(
            node_id=str(data["node_id"]),
            crystal_id=str(data["crystal_id"]),
            label=str(data["label"]),
            slot64=int(data["slot64"]),
        )


def normalize_tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def token_slot64(token: str) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


class InvertedIndex:
    """
    Token -> node reference index for phase-resonant semantic routing.

    Internals:
      token_map: token -> set(node_id)
      refs:      node_id -> NodeRef
    """

    def __init__(self) -> None:
        self.token_map: Dict[str, Set[str]] = {}
        self.refs: Dict[str, NodeRef] = {}

    def add_node(self, crystal_id: str, node_id: str, label: str, aliases: Iterable[str]) -> None:
        terms: List[str] = []
        terms.extend(normalize_tokens(label))
        for alias in aliases or []:
            terms.extend(normalize_tokens(alias))

        if node_id not in self.refs:
            self.refs[node_id] = NodeRef(
                node_id=node_id,
                crystal_id=crystal_id,
                label=label,
                slot64=token_slot64(label.lower()),
            )

        for term in terms:
            self.token_map.setdefault(term, set()).add(node_id)

    def index_bank(self, bank: CrystalBank) -> None:
        self.token_map.clear()
        self.refs.clear()
        for crystal in bank.crystals.values():
            for node in crystal.nodes.values():
                self.add_node(crystal.crystal_id, node.node_id, node.label, node.aliases)

    def lookup(self, query: str, top_k: int = 10) -> List[Tuple[NodeRef, int]]:
        """
        Return ranked candidates as (NodeRef, token_overlap_score).
        """
        hits: Dict[str, int] = {}
        for token in normalize_tokens(query):
            for node_id in self.token_map.get(token, ()):
                hits[node_id] = hits.get(node_id, 0) + 1

        ranked_ids = sorted(hits.items(), key=lambda item: (-item[1], item[0]))[:top_k]
        return [(self.refs[node_id], score) for node_id, score in ranked_ids if node_id in self.refs]

    def to_dict(self) -> Dict[str, object]:
        return {
            "token_map": {k: sorted(v) for k, v in self.token_map.items()},
            "refs": {node_id: ref.to_dict() for node_id, ref in self.refs.items()},
        }

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "InvertedIndex":
        idx = InvertedIndex()
        token_map = data.get("token_map", {})
        refs = data.get("refs", {})

        for token, node_ids in token_map.items():
            idx.token_map[str(token)] = set(str(nid) for nid in node_ids)
        for node_id, ref_data in refs.items():
            idx.refs[str(node_id)] = NodeRef.from_dict(ref_data)
        return idx

    def save_json(self, path: str) -> None:
        """Persist index atomically to avoid partial writes on crashes."""
        directory = os.path.dirname(path) or "."
        os.makedirs(directory, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory, delete=False, prefix=".idx-", suffix=".tmp"
        ) as tmp:
            json.dump(self.to_dict(), tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name

        os.replace(tmp_path, path)

    @staticmethod
    def load_json(path: str) -> "InvertedIndex":
        with open(path, "r", encoding="utf-8") as handle:
            return InvertedIndex.from_dict(json.load(handle))
