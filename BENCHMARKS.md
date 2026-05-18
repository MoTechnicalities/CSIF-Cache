# CSIF-Cache Benchmark Report

## Scope

This report compares current Python demo behavior with native Rust implementations in this repository.

## Environment

- Workspace: CSIF-Cache
- Date: 2026-05-17
- Build profile: Rust `--release`

## Commands Used

```bash
python3 demo_deterministic_probability_colab.py
cd rust/csif_phase_bench
cargo run --release --bin semantic_metronome
cargo run --release --bin csif_phase_bench
```

## Results

### Python: Semantic Metronome (Colab-ready)

- Script completed successfully.
- Demonstrated all three acts:
  - Static coherence
  - Temporal evolution
  - Deterministic audit replay
- Latency printouts are in milliseconds, as expected for interpreted Python execution.

### Rust: Semantic Metronome (Parity Demo)

- Binary completed successfully.
- Matched deterministic logic and replay behavior.
- Demonstrated significantly lower per-step latency than Python (native execution path).

### Rust: Core Benchmark

- Core phase throughput: approximately **99 Mops/s**
- Resonance scan throughput: approximately **520.59 million edges/s**

## Interpretation

The Rust implementation confirms that CSIF phase geometry maps efficiently to low-level systems programming:

- Determinism is preserved in native execution.
- Throughput scales to high-rate resonance scanning on CPU.
- This provides a concrete path to SIMD/GPU/ASIC acceleration without changing the semantic model.

## Reproducibility Notes

Performance values vary by CPU model, thermal state, and compiler version. Always run in release mode for meaningful numbers.
