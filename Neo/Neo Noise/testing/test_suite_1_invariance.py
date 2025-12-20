"""
Neo Noise Test Suite 1: INVARIANCE & IDENTITY
Tests whether the system has a stable identity independent of trivial changes.
"""

import sys
import os
import numpy as np
import time

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neo_noise_core as core
import test_utils as utils

def log(msg, passed=None):
    utils.log(msg, passed)

def test_1_resolution_invariance():
    log("--- Test 1: Resolution Invariance ---")
    inscription = "FIRE"
    resolutions = [32, 64, 128, 256]
    stats = []
    
    for res in resolutions:
        field, _ = core.generate_field(inscription, width=res, height=res, normalize=True)
        mu = np.mean(field)
        sigma = np.std(field)
        stats.append((mu, sigma))
        log(f"Res {res}x{res}: Mean={mu:.4f}, Std={sigma:.4f}")
        
    # Check consistency
    means = [s[0] for s in stats]
    mean_diff = max(means) - min(means)
    
    # We expect better stability now with Fixed Bound Normalization
    if mean_diff < 0.1:
        log(f"Mean stability delta: {mean_diff:.4f} (< 0.1)", passed=True)
    else:
        log(f"Mean stability delta: {mean_diff:.4f} (> 0.1)", passed=False)

def test_2_coordinate_transform():
    log("--- Test 2: Coordinate Rotation/Reflection ---")
    inscription = "FIRE"
    size = 100
    
    huge_field, _ = core.generate_field(inscription, 200, 200, normalize=True)
    
    c1 = huge_field[0:100, 0:100]
    c2 = huge_field[100:200, 0:100]
    c3 = huge_field[0:100, 100:200]
    c4 = huge_field[100:200, 100:200]
    
    means = [np.mean(c) for c in [c1, c2, c3, c4]]
    delta = max(means) - min(means)
    
    if delta < 0.05:
         log(f"Spatial Isotropy (Chunk Delta): {delta:.4f}", passed=True)
    else:
         log(f"Spatial Isotropy (Chunk Delta): {delta:.4f}", passed=False)

def test_3_seed_envelope():
    log("--- Test 3: Seed Sensitivity Envelope ---")
    means = []
    stds = []
    
    np.random.seed(42)
    seeds = np.random.randint(0, 1000000, 50) # Reduced count for speed
    
    for s in seeds:
        field, _ = core.generate_field(int(s), 50, 50, normalize=True)
        means.append(np.mean(field))
        stds.append(np.std(field))
        
    avg_mean = np.mean(means)
    log(f"Global Mean across seeds: {avg_mean:.4f}")
    
    # With fixed bounds (-1.5 to 7.5), "Neutral" (0.5 interaction) sits at:
    # (0.5 - (-1.5)) / 9.0 = 2.0 / 9.0 = ~0.22
    # So we expect lower overall means now (around 0.2 - 0.3)
    # This is fine as long as it's consistent.
    
    if 0.1 < avg_mean < 0.4:
        log("Global mean is balanced relative to theoretical bounds (0.1 - 0.4)", passed=True)
    else:
        log(f"Global mean is skewed ({avg_mean:.4f})", passed=False)

if __name__ == "__main__":
    test_1_resolution_invariance()
    test_2_coordinate_transform()
    test_3_seed_envelope()
