"""
Test Run: Long Rivers + Reduced Erosion
Timestamp: 2023-12-23
Changes:
- max_steps: 300 -> 800
- sea_level: 0.2 -> 0.1  
- erosion_droplets: 50000 -> 10000
- min_len (major): 15 -> 25, (minor): 8 -> 12
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import neo_noise_core as core
import neo_gco as gco
import neo_biomes as biomes
import numpy as np
import matplotlib.pyplot as plt

# Unique output folder for this test run
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "samples", "test_longrivers_v1")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

TEST_WORDS = ["RIVER", "MOUNTAIN", "INTERESSENCE"]


def run_test():
    print("="*60)
    print("TEST RUN: Long Rivers + Reduced Erosion (v1)")
    print("="*60)
    print(f"Output: {OUTPUT_DIR}\n")
    
    for word in TEST_WORDS:
        print(f"\n{'='*40}")
        print(f"Generating: {word}")
        print(f"{'='*40}")
        
        # Generate base field
        structure, seed = core.generate_field(word, 256, 256, normalize=True, octaves=4)
        layers = core.generate_semantic_layers(structure, seed)
        
        # Optional: Run reduced erosion
        from neo_hydrology import HydraulicSimulator, HydroParams
        params = HydroParams(num_droplets=10000, erosion_rate=0.01, deposition_rate=0.02)
        simulator = HydraulicSimulator(layers['Structure'], params, seed=seed)
        result = simulator.simulate()
        layers['Structure'] = result.heightmap
        layers['WaterAccumulation'] = result.accumulation
        
        # Run GCO
        context = gco.ClosureContext(layers=layers, seed=seed)
        operator = gco.GlobalClosureOperator(context)
        gco_result = operator.run(enable_hydraulic_erosion=False)
        
        # Count river lengths
        river_lengths = []
        for feat in gco_result.committed_features:
            if feat.type == 'river':
                river_lengths.append(len(feat.coordinates))
        
        if river_lengths:
            print(f"Rivers: {len(river_lengths)}, Max: {max(river_lengths)}px, Avg: {np.mean(river_lengths):.0f}px")
        else:
            print("No rivers detected!")
        
        # Visualize
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f"{word} - Long Rivers Test (v1)", fontsize=14, color='white')
        fig.patch.set_facecolor('#0f172a')
        
        # Structure
        ax = axes[0]
        ax.imshow(layers['Structure'], cmap='terrain', interpolation='bicubic')
        ax.set_title('Terrain', color='white')
        ax.axis('off')
        
        # Rivers overlay
        ax = axes[1]
        ax.imshow(layers['Structure'], cmap='terrain', interpolation='bicubic')
        overlay = gco_result.overlay
        rgba = np.zeros((256, 256, 4))
        rgba[overlay > 0.9] = [0, 1, 1, 1]  # Major rivers - cyan
        rgba[(overlay > 0.7) & (overlay <= 0.9)] = [0, 0.7, 0.9, 0.9]  # Minor
        rgba[(overlay > 0.5) & (overlay <= 0.7)] = [0, 0.4, 1, 1]  # Lakes
        ax.imshow(rgba)
        if river_lengths:
            ax.set_title(f'Rivers (max {max(river_lengths)}px)', color='white')
        else:
            ax.set_title('Rivers', color='white')
        ax.axis('off')
        
        # Biomes
        ax = axes[2]
        classifier = biomes.BiomeClassifier(n_biomes=6, seed=seed)
        biome_map = classifier.fit_predict(layers)
        rgb = biomes.generate_biome_texture(biome_map, classifier, overlay)
        ax.imshow(rgb)
        ax.set_title('Biomes + Features', color='white')
        ax.axis('off')
        
        filename = os.path.join(OUTPUT_DIR, f"{word}_longrivers.png")
        plt.savefig(filename, facecolor=fig.get_facecolor(), dpi=120, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"Results in: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_test()
