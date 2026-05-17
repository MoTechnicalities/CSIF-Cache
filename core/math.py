import datetime
def iso_to_time_coordinate(iso_ts: str) -> float:
    """
    Convert ISO 8601 timestamp to a deterministic float time coordinate.
    Uses seconds + fractional microseconds for high precision.
    """
    dt = datetime.datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    return dt.timestamp()

def temporal_wave_phase(theta_0: float, sigma: float, t: float) -> float:
    """
    Deterministic temporal wave function for phase modulation.
    theta(t) = theta_0 + sigma * sin(0.5 * t)
    """
    return wrap_pi(theta_0 + sigma * math.sin(0.5 * t))
"""
Phase geometry primitives for CSIF-Sync
Shared mathematical substrate with CSIF-Guard.
IEEE 754 double precision throughout — determinism guaranteed.
"""
import math

def wrap_pi(theta):
    """Wrap angle to principal interval [-pi, pi]."""
    return ((theta + math.pi) % (2 * math.pi)) - math.pi

def phase_distance(theta_a, theta_b):
    """Angular distance between two phase values. Always non-negative."""
    return abs(wrap_pi(theta_a - theta_b))

def normalized_resonance(theta_a, theta_b):
    """0.0 = perfect coherence, 1.0 = maximum opposition."""
    return phase_distance(theta_a, theta_b) / math.pi

def contradiction_threshold(sigma, c=0.5):
    """Adaptive contradiction detection threshold."""
    return math.pi / 2 + c * sigma

def circular_mean(phases):
    """Correct circular mean of a list of angles."""
    sin_sum = sum(math.sin(p) for p in phases)
    cos_sum = sum(math.cos(p) for p in phases)
    return math.atan2(sin_sum, cos_sum)

def compose_path_phase(phases):
    """Compose phase angles along a directed path."""
    return wrap_pi(sum(phases))

def nudge_phase(theta, error_signal, evidence_weight, alpha=0.1):
    """Apply one outcome-driven phase correction."""
    return wrap_pi(theta + alpha * error_signal * evidence_weight)

def tighten_sigma(sigma, evidence_weight, rate=0.1):
    """Tighten confidence band as evidence accumulates."""
    return sigma * (1.0 - evidence_weight * rate)
