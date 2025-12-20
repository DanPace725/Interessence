"""
Neo Noise Test Suite 4: TEMPORAL & EVOLUTION
Tests whether the system survives time-integration without collapsing into chaos or mush.
"""

import sys
import os
import numpy as np
import test_utils as utils

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neo_noise_core as core

def log(msg, passed=None):
    utils.log(msg, passed)

def test_9_time_step_integration():
    log("--- Test 9: Time-Step Integration ---")
    inscription = "EVOLUTION"
    f0, _ = core.generate_field(inscription, 50, 50, normalize=True)
    
    # Evolve with defaults (feed_rate > 0)
    f5 = core.evolve_field(f0, steps=5)
    f10_a = core.evolve_field(f5, steps=5)
    f10_b = core.evolve_field(f0, steps=10)
    
    if utils.compare_fields(f10_a, f10_b, threshold=0.0001):
        log("Deterministic Evolution confirmed.", passed=True)
    else:
        log("Deterministic Evolution failed.", passed=False)
        
    corr = np.corrcoef(f0.flatten(), f10_b.flatten())[0, 1]
    
    if corr > 0.5:
        log("Identity Preserved (>0.5 Correlation)", passed=True)
    else:
        log("Identity Lost (<0.5 Correlation)", passed=False)

def test_10_entropy_drift():
    log("--- Test 10: Entropy Drift (With Anti-Entropy) ---")
    # Goal: Ensure efficient prevents total death
    
    inscription = "ENTROPY"
    f, _ = core.generate_field(inscription, 50, 50, normalize=True)
    
    variances = []
    means = []
    
    tracker = f.copy()
    for i in range(10):
        # Batch of 10
        # ADJUSTMENT: Feed Rate (0.012) > Decay (0.01) to enable sustainable life
        tracker = core.evolve_field(tracker, steps=10, feed_rate=0.012, decay=0.01)
        v = np.var(tracker)
        m = np.mean(tracker)
        variances.append(v)
        means.append(m)
        
    log(f"Final Variance: {variances[-1]:.4f}")
    log(f"Final Mean: {means[-1]:.4f}")
    
    # We want Mean to stabilize > 0 (Alive)
    if means[-1] > 0.05:
        log("Anti-Entropy effective (System remains alive).", passed=True)
    else:
        log("System collapsed to zero (Feed rate too low?).", passed=False)
        
def test_13_semantic_axes():
    log("--- Test 13: Semantic Axes Extraction ---")
    inscription = "AXIS"
    f, _ = core.generate_field(inscription, 50, 50, normalize=True)
    
    axes = core.get_semantic_axes(f)
    log("Semantic Axes:")
    for k, v in axes.items():
        log(f"  {k}: {v:.4f}")
        
    # Check if values are valid floats
    if all(isinstance(v, float) for v in axes.values()):
        log("Axes extraction successful.", passed=True)
    else:
        log("Axes extraction failed (types).", passed=False)

if __name__ == "__main__":
    test_9_time_step_integration()
    print("-" * 30)
    test_10_entropy_drift()
    print("-" * 30)
    test_13_semantic_axes()
