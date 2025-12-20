"""
Neo Noise Test Suite 5: GAME RELEVANCE
Tests whether the system behaves predictably for gameplay mechanics.
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

def test_11_locality_shock():
    log("--- Test 11: Locality Shock ---")
    # Goal: Does perturbation propagate chaotically?
    
    inscription = "STABILITY"
    size = 50
    f0, _ = core.generate_field(inscription, size, size, normalize=True)
    
    # Create shock: Set centeter pixel to 1.0 (Singularity)
    cx, cy = size//2, size//2
    f_shock = f0.copy()
    f_shock[cy, cx] = 1.0
    
    # Evolve both
    f0_next = core.evolve_field(f0, steps=5)
    f_shock_next = core.evolve_field(f_shock, steps=5)
    
    # Check difference
    diff = np.abs(f_shock_next - f0_next)
    
    # Check radius of effect
    # Pixels where diff > 0.01
    affected_pixels = np.sum(diff > 0.01)
    total_pixels = size * size
    ratio = affected_pixels / total_pixels
    
    log(f"Affected Pixels: {affected_pixels} ({ratio*100:.2f}%)")
    
    # In diffusion, radius grows as sqrt(t). 
    # 5 steps shouldn't affect the whole map.
    if ratio < 0.2:
        log("Shock contained locally (<20% affected).", passed=True)
    else:
        log("Shock exploded globally (>20% affected).", passed=False)

def test_12_stability_anchor():
    log("--- Test 12: Stability Anchor ---")
    # Goal: Do stable regions persist?
    
    inscription = "VILLAGE"
    f, _ = core.generate_field(inscription, 50, 50, normalize=True)
    
    # Identify 'stable' regions (Low Variance neighborhoods)?
    # Or simply: does the field change *slowly*?
    
    f_next = core.evolve_field(f, steps=1)
    delta = np.abs(f - f_next)
    max_change = np.max(delta)
    mean_change = np.mean(delta)
    
    log(f"Max single-step change: {max_change:.4f}")
    log(f"Mean single-step change: {mean_change:.4f}")
    
    # If the simulation is stable, mean change should be small (decay rate + diffusion)
    if mean_change < 0.05:
        log("Field is temporally stable.", passed=True)
    else:
        log("Field is volatile.", passed=False)

if __name__ == "__main__":
    test_11_locality_shock()
    print("-" * 30)
    test_12_stability_anchor()
