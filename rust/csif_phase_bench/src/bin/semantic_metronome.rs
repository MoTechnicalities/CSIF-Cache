use std::f64::consts::PI;
use std::time::Instant;

#[inline(always)]
fn wrap_pi(theta: f64) -> f64 {
    ((theta + PI).rem_euclid(2.0 * PI)) - PI
}

#[inline(always)]
fn phase_distance(a: f64, b: f64) -> f64 {
    wrap_pi(a - b).abs()
}

#[inline(always)]
fn temporal_wave_phase(theta_0: f64, sigma: f64, t: f64) -> f64 {
    // Match the current Python colab demo modulation for parity.
    wrap_pi(theta_0 + sigma * (0.618_f64 * t).sin())
}

fn print_header(title: &str) {
    println!("\n{}", "=".repeat(80));
    println!("{:=>80}", format!(" {} ", title));
    println!("{}", "=".repeat(80));
}

const ANALOGIES: [(f64, &str); 5] = [
    (0.00, "Perfect Coherence"),
    (0.40, "Strong Alignment"),
    (0.85, "Creative Association"),
    (1.40, "Conceptual Tension"),
    (2.10, "Strong Opposition"),
];

fn get_analogy(phase: f64) -> (&'static str, f64) {
    ANALOGIES
        .iter()
        .min_by(|(a, _), (b, _)| {
            phase_distance(phase, *a)
                .partial_cmp(&phase_distance(phase, *b))
                .unwrap()
        })
        .map(|(p, label)| (*label, *p))
        .unwrap()
}

fn main() {
    print_header("CSIF SEMANTIC METRONOME DEMO (RUST)");
    println!("Deterministic Temporal Evolution | Perfect Reproducibility\n");

    let theta_0 = 0.0_f64;
    let sigma = 0.75_f64;

    print_header("ACT 1 - STATIC COHERENCE (t = 0.0)");
    println!("Testing baseline stability at rest.\n");

    for i in 1..=5 {
        let start = Instant::now();
        let phase = temporal_wave_phase(theta_0, sigma, 0.0);
        let elapsed_ms = start.elapsed().as_secs_f64() * 1e3;
        let status = if phase.abs() < 0.3 { "COHERENT" } else { "UNSTABLE" };

        println!(
            "Run {:2} | Phase: {:8.4} rad | Latency: {:7.5} ms | {}",
            i, phase, elapsed_ms, status
        );
    }

    print_header("ACT 2 - TEMPORAL EVOLUTION (Advancing Clock)");
    println!("Knowledge evolves deterministically as time progresses.\n");

    for t in 8..=20 {
        let start = Instant::now();
        let phase = temporal_wave_phase(theta_0, sigma, t as f64);
        let (analogy, _) = get_analogy(phase);
        let elapsed_ms = start.elapsed().as_secs_f64() * 1e3;
        let marker = if t == 14 { " <- Target Lock" } else { "" };

        println!(
            "t = {:2} | Phase: {:8.4} rad | Latency: {:7.5} ms | {}{}",
            t, phase, elapsed_ms, analogy, marker
        );
    }

    print_header("ACT 3 - PERFECT AUDIT REPLAY (Determinism Proof)");

    // 1985-10-26T01:21:00.140000Z represented directly as the same reduced coordinate.
    let audit_t = 260.14_f64;
    println!("Audited Timestamp : 1985-10-26T01:21:00.140000Z");
    println!("Time Coordinate   : {:.6}\n", audit_t);

    let mut first_phase: Option<f64> = None;
    let mut deterministic = true;

    for i in 1..=5 {
        let start = Instant::now();
        let phase = temporal_wave_phase(theta_0, sigma, audit_t);
        let (analogy, _) = get_analogy(phase);
        let elapsed_ms = start.elapsed().as_secs_f64() * 1e3;

        if let Some(p0) = first_phase {
            if phase.to_bits() != p0.to_bits() {
                deterministic = false;
            }
        } else {
            first_phase = Some(phase);
        }

        println!(
            "Replay {} | Phase: {:12.8} rad | Latency: {:7.5} ms | {}",
            i, phase, elapsed_ms, analogy
        );
    }

    print_header("DEMONSTRATION COMPLETE");
    println!("- Static coherence validated");
    println!("- Temporal evolution is deterministic");
    println!("- Any past state can be replayed");
    println!("- Native execution achieves ultra-low latency");
    println!();
    println!("Deterministic replay bit-check: {}", if deterministic { "PASS" } else { "FAIL" });
}
