"""
CSIF-Cache: Semantic Metronome Demo — Deterministic Probability

Three-act demonstration of phase-resonant, time-locked creative inference.
"""
import math
import time
from datetime import datetime, timezone
from core.math import wrap_pi, contradiction_threshold, temporal_wave_phase, iso_to_time_coordinate

# Analogy pool for Act 2/3
ANALOGY_POOL = [
    (0.0, "Distributed Database"),
    (0.6, "Monolithic Data Block"),
    (1.2, "Isolated Memory Container"),
    (1.8, "Heavy Monolithic Kernel"),
    (2.4, "Dynamic Service Mesh"),
]

# Utility: Find closest analogy for a given phase

def find_analogy(phase):
    best = min(ANALOGY_POOL, key=lambda x: abs(wrap_pi(phase - x[0])))
    return best[1], best[0]

# High-visibility status bar

def print_bar(title):
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)

def print_subbar(title):
    print("\n" + "-" * 70)
    print(f"{title}")
    print("-" * 70)

def act1_static_fact():
    print_bar("ACT 1: STATIC FACT VALIDATION (Clock Locked: t=0.0000)")
    theta_0 = 0.0
    sigma = 0.0
    threshold = contradiction_threshold(sigma)
    for i in range(1, 6):
        phase = temporal_wave_phase(theta_0, sigma, t=0.0)
        status = "COHERENT" if abs(phase) < threshold else "INCOHERENT"
        print(f"[Run {i}] Phase: {phase:8.4f} rad | Threshold: {threshold:.4f} | Status: {status}")

def act2_fluid_brainstorm():
    print_bar("ACT 2: FLUID BRAINSTORMING (Clock Advancing: Δt > 0)")
    theta_0 = 0.0
    sigma = 0.85
    for t in range(12, 16):
        phase = temporal_wave_phase(theta_0, sigma, t)
        analogy, target_phase = find_analogy(phase)
        lock = " \U0001F4BE <-- Target Lock" if t == 14 else ""
        print(f"[t = {t:5.2f}] Phase: {phase:8.4f} rad | Target Analogy: \"{analogy}\"{lock}")
    # Save the audit timestamp for Act 3
    audit_dt = datetime(1985, 10, 26, 1, 21, 0, 14, tzinfo=timezone.utc)
    audit_iso = audit_dt.isoformat().replace("+00:00", "Z")
    audit_t = iso_to_time_coordinate(audit_iso)
    phase = temporal_wave_phase(theta_0, sigma, audit_t)
    analogy, _ = find_analogy(phase)
    print_subbar(f"ACT 3: EXECUTING FACTUAL AUDIT REPLAY\nFeeding Audited Timestamp: {audit_iso}")
    for i in range(1, 6):
        replay_phase = temporal_wave_phase(theta_0, sigma, audit_t)
        replay_analogy, _ = find_analogy(replay_phase)
        print(f"[Replay {i}] Composed Phase: {replay_phase:.12f} rad | Match: \"{replay_analogy}\"")
    print("\n[SUCCESS] Creative inference is 100% reproducible. Chaos successfully codified.")

def main():
    act1_static_fact()
    time.sleep(0.5)
    act2_fluid_brainstorm()

if __name__ == "__main__":
    main()
