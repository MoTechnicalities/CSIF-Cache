use std::f64::consts::PI;
use std::time::Instant;

#[inline(always)]
fn wrap_pi(theta: f64) -> f64 {
    ((theta + PI).rem_euclid(2.0 * PI)) - PI
}

#[inline(always)]
fn phase_distance(a: f64, b: f64) -> f64 {
    (wrap_pi(a - b)).abs()
}

#[inline(always)]
fn temporal_wave_phase(theta_0: f64, sigma: f64, t: f64) -> f64 {
    wrap_pi(theta_0 + sigma * (0.618 * t).sin())
}

fn run_microbench(iterations: usize) {
    let theta_0 = 0.0_f64;
    let sigma = 0.75_f64;

    let mut sink = 0.0_f64;
    let start = Instant::now();

    for i in 0..iterations {
        let t = (i as f64) * 0.0001;
        let phase = temporal_wave_phase(theta_0, sigma, t);
        let d = phase_distance(phase, 0.4);
        sink += d;
    }

    let elapsed = start.elapsed();
    let total_ns = elapsed.as_secs_f64() * 1e9;
    let ns_per_op = total_ns / (iterations as f64);
    let mops = (iterations as f64) / elapsed.as_secs_f64() / 1e6;

    println!("\nMicrobench: core phase operations");
    println!("iterations: {}", iterations);
    println!("elapsed: {:.3} ms", elapsed.as_secs_f64() * 1e3);
    println!("throughput: {:.2} Mops/s", mops);
    println!("cost: {:.2} ns/op", ns_per_op);
    println!("checksum: {:.8}", sink);
}

fn run_resonance_scan(crystals: usize, edges_per_crystal: usize) {
    let total_edges = crystals * edges_per_crystal;
    let mut phases = Vec::with_capacity(total_edges);

    for i in 0..total_edges {
        let seed = (i as f64) * 0.00123;
        phases.push(wrap_pi(seed.sin()));
    }

    let query_phase = 0.35_f64;
    let threshold = 0.05_f64 * PI;

    let start = Instant::now();
    let mut hits = 0usize;

    for &p in &phases {
        if phase_distance(query_phase, p) <= threshold {
            hits += 1;
        }
    }

    let elapsed = start.elapsed();
    let scans_per_sec = (total_edges as f64) / elapsed.as_secs_f64();

    println!("\nResonance scan: synthetic bank");
    println!("crystals: {}", crystals);
    println!("edges per crystal: {}", edges_per_crystal);
    println!("total edges scanned: {}", total_edges);
    println!("elapsed: {:.3} ms", elapsed.as_secs_f64() * 1e3);
    println!("scan rate: {:.2} M edges/s", scans_per_sec / 1e6);
    println!("hits: {}", hits);
}

fn main() {
    println!("CSIF Rust Prototype: deterministic phase benchmark");
    println!("Build: release mode recommended for realistic speed");

    run_microbench(20_000_000);
    run_resonance_scan(10_000, 256);

    println!("\nDone.");
}
