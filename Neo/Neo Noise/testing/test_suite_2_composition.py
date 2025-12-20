"""
Neo Noise Test Suite 2: COMPOSITION & ORDER
Tests whether the system respects sequential structure and semantic composition.
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

def compare_fields(f1, f2, threshold=0.01):
    return utils.compare_fields(f1, f2, threshold)

def test_4_permutation_sensitivity():
    log("--- Test 4: Permutation Sensitivity ---")
    # Goal: Does order matter?
    # Compare FIRE, FIER, RIFE
    
    w = 50
    h = 50
    
    f1, _ = core.generate_field("FIRE", w, h, normalize=True)
    f2, _ = core.generate_field("FIER", w, h, normalize=True)
    f3, _ = core.generate_field("RIFE", w, h, normalize=True)
    
    # Check 1: Are they identical?
    if compare_fields(f1, f2):
        log("FIRE == FIER (Bad: Order didn't matter)", passed=False)
    else:
        log("FIRE != FIER (Good: Order changed output)", passed=True)
        
    if compare_fields(f1, f3):
        log("FIRE == RIFE (Bad: Order didn't matter)", passed=False)
    else:
        log("FIRE != RIFE (Good: Order changed output)", passed=True)
        
    # Check 2: How different are they?
    # RIFE (Cross First) might be more structured than FIRE (Left First)?
    # We can check mean intensity or variance.
    v1 = np.var(f1)
    v3 = np.var(f3)
    
    log(f"FIRE Variance: {v1:.4f}")
    log(f"RIFE Variance: {v3:.4f}")
    
    # We don't have a strict pass condition for *how* they differ yet, 
    # just THAT they differ.
    
def test_5_subtractive_glyph():
    log("--- Test 5: Subtractive Glyph ---")
    # Goal: Does removing a letter remove a feature?
    
    base = "TREE"
    minus = "TEE" # Removed 'R' (Cross/Structure)
    
    f1, _ = core.generate_field(base, 50, 50, normalize=True)
    f2, _ = core.generate_field(minus, 50, 50, normalize=True)
    
    # We expect TREE (contains R=Cross) to have higher 'structure' peaks than TEE?
    # Actually, R is Cross-5 (Ruis).
    # Cross-Cross interactions are strongest.
    # TREE = T(R) R(X) E(D) E(D).
    # R interacts with T, E, E.
    # TEE = T(R) E(D) E(D).
    
    # If the system works, TREE should have higher max peaks or different texture.
    
    diff_val = np.mean(np.abs(f1 - f2))
    log(f"TREE vs TEE Diff: {diff_val:.4f}")
    
    if compare_fields(f1, f2):
         log("TREE == TEE (Fail)", passed=False)
    else:
         log("TREE != TEE (Pass)", passed=True)

def test_6_additive_saturation():
    log("--- Test 6: Additive Saturation ---")
    # Goal: Does repetition cause a crash or convergence?
    
    seqs = ["FIRE", "FIREFIRE", "FIRE" * 4]
    means = []
    
    for s in seqs:
        f, _ = core.generate_field(s, 50, 50, normalize=False) # Check raw values
        m = np.mean(f)
        means.append(m)
        log(f"Raw Mean '{s[:8]}...': {m:.4f}")
        
    # Check change
    d1 = abs(means[1] - means[0])
    d2 = abs(means[2] - means[1])
    
    log(f"Delta 1 (1x -> 2x): {d1:.4f}")
    log(f"Delta 2 (2x -> 4x): {d2:.4f}")
    
    # We essentially want to know if it's identical (bad hashing loop?) 
    # or if it varies.
    # Note: hash("FIREFIRE") is completely different seed than hash("FIRE").
    # So this test checks if the *algorithm* scales linearly with length?
    # calculate_local_intensity loops through neighbors... 
    # The *length* of the inscription changes the seed, which changes the glyphs.
    # Wait, the current algorithm uses a SINGLE seed for the whole map.
    # It does NOT iterate through the string characters at each point.
    # So "FIRE" -> Seed A -> Field A.
    # "FIREFIRE" -> Seed B -> Field B.
    # There is no additive saturation logic in the current *core*.
    # The core logic is: String -> Hash -> Latent Field.
    # It does NOT map letters to positions.
    # So this test reveals that our current implementation is "Holographic" (Seed-based)
    # rather than "Sequential" (String-based).
    # Effectively, "FIRE" and "FIREFIRE" are just two random seeds.
    
    log("[NOTE] Current implementation uses Holographic Seeding.", passed=None)
    log("Length of string changes Seed, creating totally new field.", passed=None)
    log("Strict Additive Saturation is N/A for this hashing model.", passed=None)

if __name__ == "__main__":
    test_4_permutation_sensitivity()
    print("-" * 30)
    test_5_subtractive_glyph()
    print("-" * 30)
    test_6_additive_saturation()
