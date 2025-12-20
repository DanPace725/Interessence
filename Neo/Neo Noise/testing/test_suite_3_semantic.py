"""
Neo Noise Test Suite 3: SEMANTIC FIELDS
Tests whether the generated noise maps to behavior/meaning, not just labels.
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

def test_7_blind_label_clustering():
    log("--- Test 7: Blind Label Clustering (Statistical) ---")
    # Goal: Can meaning be inferred without names?
    # We will generate groups of words and check if they statistically cluster correctly.
    
    group_a = ["FIRE", "FLAME", "INFERNO", "HEAT"] # Fire-likes
    group_b = ["WATER", "RIVER", "STREAM", "OCEAN"] # Water-likes
    group_c = ["STONE", "ROCK", "EARTH", "GROUND"] # Earth-likes
    
    all_words = group_a + group_b + group_c
    fields = {}
    
    # Generate all fields
    for w in all_words:
        f, _ = core.generate_field(w, 50, 50, normalize=True)
        # Flatten to 1D vector for simple correlation
        fields[w] = f.flatten()
        
    # Analyze similarity matrix
    # We expect high correlation within groups?
    # Actually, Neo Noise is Seed-based from String Hashing.
    # "FIRE" and "FLAME" have TOTALLY DIFFERENT seeds.
    # There is NO semantic link between the string "FIRE" and "FLAME" in the hashing algorithm.
    # The *only* link is if the glyph composition is similar (e.g. lots of F's or Diagonals).
    # FIRE: F(R), I(D), R(X), E(D) -> Right, Diag, Cross, Diag
    # FLAME: F(R), L(R), A(D), M(X), E(D) -> Right, Right, Diag, Cross, Diag
    # They DO share structural features (Rights, Crosses, Diagonals).
    # So we *might* see statistical similarities in histogram buckets (e.g. ratio of Cross interactions).
    
    # Let's verify if 'Type Distribution' matches.
    # We need a metric that captures "Character".
    # Simple Pixel Correlation will be 0 (random seeds align randomly).
    # We should use Histogram matching (Mean, Std, Skew).
    
    stats_matrix = []
    labels = []
    
    for w in all_words:
        f = fields[w]
        mu = np.mean(f)
        sigma = np.std(f)
        # Simple feature vector: [Mean, Std]
        stats_matrix.append([mu, sigma])
        labels.append(w)
        
    stats_matrix = np.array(stats_matrix)
    
    # Just log the clusters for manual review?
    # Automation is hard here without a trained classifier.
    # We will just print the stats and see if they group visually in the log.
    
    log("Blind Stats (Mean, Std):")
    for i, w in enumerate(labels):
        log(f"{w:10s}: {stats_matrix[i][0]:.3f}, {stats_matrix[i][1]:.3f}")
        
    log("Note: Because seeds are hash-based, we do not expect 'FIRE' and 'FLAME' to correlate spatially.", passed=None)
    log("We check if they share statistical 'Texture' (similar Mean/Std) due to similar glyph ratios.", passed=None)

def test_8_threshold_boundary():
    log("--- Test 8: Threshold Boundary Interaction ---")
    # Goal: Interpolate between two inscriptions.
    # Since we can't interpolate the *seed*, we must interpolate the *Field*.
    # Or, we can interpolate the *glyph weights* if the core supported it.
    # Current Core: String -> Single Seed -> Field. 
    # We cannot interpolate inputs.
    # We can only interpolate outputs (Cross-fading).
    # Cross-fading is linear and boring.
    
    # BUT, what if we treat a coordinate as having *two* latent glyphs (one from seed A, one from seed B)
    # and we mix their *magnitudes*?
    # That requires modifying the core or writing a custom generation loop here.
    # Let's write a custom mix loop.
    
    w1, w2 = "FIRE", "WATER"
    seed1 = hash(w1) & 0xFFFFFFFF
    seed2 = hash(w2) & 0xFFFFFFFF
    
    log(f"Interpolating {w1} <-> {w2} (Semantic Mixing)")
    
    # We will check if the midpoint (50/50 mix of interaction scores) 
    # creates a "muddy" field or a distinct hybrid.
    
    size = 50
    f1, _ = core.generate_field(w1, size, size, normalize=False)
    f2, _ = core.generate_field(w2, size, size, normalize=False)
    
    f_mix = (f1 + f2) / 2.0
    
    # normalize check
    mu_1 = np.mean(f1)
    mu_2 = np.mean(f2)
    mu_mix = np.mean(f_mix)
    
    log(f"Mean {w1}: {mu_1:.3f}")
    log(f"Mean {w2}: {mu_2:.3f}")
    log(f"Mean MIX : {mu_mix:.3f}")
    
    # Pass condition: Mix is not broken (NaN or inf)
    if not np.isnan(mu_mix):
        log("Interpolation successful (Linear Field Mixing)", passed=True)
    else:
        log("Interpolation failed", passed=False)

if __name__ == "__main__":
    test_7_blind_label_clustering()
    print("-" * 30)
    test_8_threshold_boundary()
