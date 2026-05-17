"""
CSIF-Cache demo

Shows semantic routing behavior:
1) PREFLIGHT_SHORT_CIRCUIT for high-certainty coherent memory
2) CACHE_HIT on repeated query
3) DEEP_VALIDATION for speculative / drifted state
"""
import math
import time
import uuid
from datetime import datetime, timezone

from engine.router import SemanticRouter
from storage.inverted_index import InvertedIndex
from storage.rwif import CrystalBank, Crystal, Edge, Node, PhaseTrajectoryEvent


def build_demo_bank() -> CrystalBank:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    n1 = Node(str(uuid.uuid4()), "master bath flusher", ["bath flusher", "flush actuator"], "English", {
        "source_document": "home-assistant-state", "extraction_timestamp": now, "extractor": "demo"
    })
    n2 = Node(str(uuid.uuid4()), "healthy", ["operational", "nominal"], "English", {
        "source_document": "home-assistant-state", "extraction_timestamp": now, "extractor": "demo"
    })
    n3 = Node(str(uuid.uuid4()), "water pressure", ["line pressure"], "English", {
        "source_document": "sensor-readings", "extraction_timestamp": now, "extractor": "demo"
    })

    e1 = Edge(
        str(uuid.uuid4()),
        n1.node_id,
        "status_is",
        n2.node_id,
        "English",
        True,
        0.0,
        0.02,
        [
            PhaseTrajectoryEvent(now, 0.0, 0.02, 0.0, "crystallization", {"source": "verified-consensus"})
        ],
        {"encoding_model": "demo", "source_documents": ["home-assistant-state"]},
    )

    e2 = Edge(
        str(uuid.uuid4()),
        n3.node_id,
        "supports",
        n2.node_id,
        "English",
        True,
        0.12,
        0.08,
        [
            PhaseTrajectoryEvent(now, 0.12, 0.08, 0.03, "initial_encoding", {"source": "sensor-readings"})
        ],
        {"encoding_model": "demo", "source_documents": ["sensor-readings"]},
    )

    nodes = {n.node_id: n for n in (n1, n2, n3)}
    edges = {e1.edge_id: e1, e2.edge_id: e2}
    crystal = Crystal(str(uuid.uuid4()), "home_automation", "automation", "English", True, nodes, edges, [], 1.0)
    return CrystalBank(str(uuid.uuid4()), "cache_demo_bank", "English", {crystal.crystal_id: crystal})


def print_result(title, result):
    print(f"\n--- {title} ---")
    print(f"Route        : {result.route}")
    print(f"Latency      : {result.latency_ms:.4f} ms")
    print(f"Cache key    : {result.cache_key[:16]}...")
    print(f"Node         : {result.candidate_node_id}")
    print(f"Resonance    : {result.resonance}")
    print(f"Sigma        : {result.sigma}")
    print(f"Reason       : {result.reason}")
    if result.response:
        print(f"Response     : {result.response}")


def main():
    print("\n=== CSIF-Cache: Phase-Resonant Semantic Routing Demo ===")

    bank = build_demo_bank()
    index = InvertedIndex()
    index.index_bank(bank)

    router = SemanticRouter(bank=bank, index=index)

    query = "What is the status of the master bath flusher?"

    # Scenario 1: coherent query, high certainty -> preflight short-circuit.
    r1 = router.route_query(query_text=query, query_phase=0.0, query_sigma=0.01)
    print_result("Scenario 1: Preflight short-circuit", r1)

    # Scenario 2: exact same query -> immediate cache hit.
    r2 = router.route_query(query_text=query, query_phase=0.0, query_sigma=0.01)
    print_result("Scenario 2: Query-hash cache hit", r2)

    # Scenario 3: drifted query state -> deep validation route.
    drifted = router.route_query(query_text=query, query_phase=math.pi * 0.55, query_sigma=0.35)
    print_result("Scenario 3: Drift/wide sigma deep validation", drifted)

    # Optional persistence demonstration for crash-safe atomic replacement.
    started = time.perf_counter()
    router.save_query_cache(".csif_cache/query_cache.json")
    save_ms = (time.perf_counter() - started) * 1000.0
    print(f"\nAtomic cache save completed in {save_ms:.4f} ms")

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
