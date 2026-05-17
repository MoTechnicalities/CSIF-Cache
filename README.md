# CSIF-Cache: Phase-Resonant Semantic Routing Layer v1.0

[![Status: Unified Architecture](https://img.shields.io/badge/Status-Unified__Architecture-blueviolet)](https://github.com/MoTechnicalities/Crystal-Structure-Information-Format)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache__2.0-blue)](LICENSE)
[![Latency: <2ms](https://img.shields.io/badge/Latency-%3C2ms-green)]()
[![Trilogy: Guard+Sync+Cache](https://img.shields.io/badge/Trilogy-Guard%2BSync%2BCache-orange)]()

> **The Problem:** Local agent systems still rely on vector databases for retrieval, paying an expensive runtime tax in RAM, similarity-matrix compute, and re-embedding overhead.
>
> **The Solution:** `CSIF-Cache` converts retrieval from dense vector search into deterministic phase-resonant routing on existing RWIF crystals, enabling near-instant memory lookups with complete trajectory auditability.

---

## Why CSIF-Cache Exists

Traditional vector retrieval pipelines use high-dimensional cosine similarity over embeddings (often 768 to 1536 dimensions). As memory grows, search cost and RAM footprint rise sharply.

`CSIF-Cache` avoids this by routing through crystal topology:

1. **Phase-Keyed Inverted Indexing**
   Canonical concept labels are tokenized and mapped to stable node references with a deterministic 64-bit slot address.

2. **Resonant Path Short-Circuiting**
   A query is phase-checked against the candidate concept state.
   If $\sigma \approx 0$ and $R_N < 0.05$, the router returns the factual response immediately.

3. **Deep Validation Fallback**
   If confidence is wide or drift is active, the query is escalated to deeper validation rather than returning a brittle cache answer.

---

## Repository Architecture

```text
csif-cache/
├── core/
│   └── math.py                 # Shared phase geometry substrate
├── storage/
│   ├── rwif.py                 # RWIF CrystalBank serialization
│   └── inverted_index.py       # Token -> node_id phase-keyed index
├── engine/
│   ├── phase_graph.py          # Shared conflict/resonance graph utilities
│   └── router.py               # Preflight short-circuit semantic router
├── demo_cache.py               # Live cache routing simulation
├── README.md
└── LICENSE
```

---

## Quickstart

```bash
git clone https://github.com/MoTechnicalities/CSIF-Cache.git
cd CSIF-Cache
python3 demo_cache.py
```

### Expected Routing Outcomes

---

## Unique Demo: Semantic Metronome

A one-of-a-kind, deterministic probability demo is provided:

- **demo_deterministic_probability.py** — The "Semantic Metronome". Demonstrates phase-resonant, time-locked creative inference with bit-perfect reproducibility. See the script for a three-act, high-visibility terminal showcase.

---

## Quickstart: Semantic Metronome Demo

```bash
python3 demo_deterministic_probability.py
```

- `PREFLIGHT_SHORT_CIRCUIT` for high-certainty coherent query
- `CACHE_HIT` on repeated identical query
- `DEEP_VALIDATION` when phase drift or uncertainty is high

---

## Mathematical Contract

### Principal Wrap

$$\mathrm{wrap}_{\pi}(\theta) = ((\theta + \pi) \bmod 2\pi) - \pi$$

### Resonance

$$R_N = \frac{\lvert \mathrm{wrap}_{\pi}(\theta_q - \theta_m) \rvert}{\pi}$$

### Preflight Acceptance Boundary

Short-circuit is allowed only if both conditions hold:

$$R_N < 0.05 \quad \text{and} \quad \sigma \leq 0.05$$

Otherwise the query is routed to deep validation.

---

## Key Modules

### storage/inverted_index.py

- Deterministic token normalization
- SHA-256 backed 64-bit token slots
- Stable node references linked to RWIF node IDs
- Crash-safe persistence via atomic temp-file replacement

### engine/router.py

- Query hash key generation using SHA-256
- Preflight semantic routing with phase resonance thresholds
- Deep-validation escalation path when confidence is weak
- Atomic query-cache save and load helpers

---

## ── Trilogy Architecture

The CSIF trilogy is engineered as one deterministic local intelligence stack.

| Pillar | Responsibility | Failure Mode Prevented |
|---|---|---|
| **CSIF-Guard** | Semantic firewall for write interception and contradiction blocking | Hallucinated memory corruption |
| **CSIF-Sync** | Multi-agent phase consensus and state propagation | Split-brain drift across local nodes |
| **CSIF-Cache** | Phase-resonant semantic routing with preflight short-circuit retrieval | Vector DB latency and retrieval overhead |

### Shared Contract Language

- **Determinism:** Given identical inputs, each module must return identical outputs across runs and platforms.
- **Append-Only Trajectories:** Phase history is never rewritten; new evidence is appended, not mutated.
- **Auditability:** Every acceptance, rejection, and routing decision must be reconstructable from stored artifacts.
- **Graceful Degradation:** If optional network or upstream services are unavailable, local geometric validation remains operational.

### Cross-Repository Links

- [CSIF-Guard](https://github.com/MoTechnicalities/CSIF-Guard)
- [CSIF-Sync](https://github.com/MoTechnicalities/CSIF-Sync)
- [CSIF-Cache](https://github.com/MoTechnicalities/CSIF-Cache)

---

## License

Apache License 2.0. See [LICENSE](LICENSE).
