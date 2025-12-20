"""
Neo Layer Generator
Proof of Concept: Deriving all 4 Functional Layers from a single Neo Noise Inscription.
"""

import numpy as np
import matplotlib.pyplot as plt
import neo_noise_core as core
import os

OUTPUT_DIR = "samples/layers"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_multi_layer_map(inscription, size=256):
    print(f"Generating Layers for '{inscription}'...")
    
    # 1. STRUCTURE LAYER (Base Field)
    # The foundation.
    structure, seed = core.generate_field(inscription, size, size, normalize=True)
    
    # 2. FLOW LAYER (Gradient Magnitude)
    # We compute the gradient vector field.
    grad_y, grad_x = np.gradient(structure)
    # Magnitude of flow
    flow_mag = np.sqrt(grad_x**2 + grad_y**2)
    # Normalize Flow
    flow = (flow_mag - flow_mag.min()) / (flow_mag.max() - flow_mag.min() + 1e-8)
    
    # 3. CONSTRAINT LAYER (Laplacian / Variance)
    # High frequency changes = High constraint (Edges/Cliffs)
    # We can use the Laplacian (2nd derivative) or local variance.
    # Let's use standard deviation of a 3x3 window (Edge detection)
    
    # Simple Laplacian approximation from gradients
    laplacian = np.abs(np.gradient(grad_x, axis=1) + np.gradient(grad_y, axis=0))
    constraint = (laplacian - laplacian.min()) / (laplacian.max() - laplacian.min() + 1e-8)
    
    # 4. VITALITY LAYER (Anti-Entropy Evolution)
    # We evolve the field to find stable "life" pools.
    # We run the Time-Step integration.
    vitality = core.evolve_field(structure, steps=15, feed_rate=0.012, decay=0.01)
    # Normalize? Vitality might be sparse, so regular normalization might amplify noise.
    # Let's Clip to 0-1 and keep absolute values (treating 0 as dead).
    vitality = np.clip(vitality, 0, 1)

    return {
        "Structure": structure,
        "Flow": flow,
        "Constraint": constraint,
        "Vitality": vitality
    }, seed

def visualize_layers(layers, inscription, seed):
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle(f"Neo Semantic Layers: {inscription} (Seed: {seed})", fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    cmaps = {
        "Structure": "inferno",   # Standard Heatmap
        "Flow": "viridis",        # Vector/Movement feel
        "Constraint": "gray",     # Hard edges
        "Vitality": "Greens"      # Life/Biomass
    }
    
    for i, (name, field) in enumerate(layers.items()):
        ax = axes[i]
        im = ax.imshow(field, cmap=cmaps[name], interpolation='bicubic')
        ax.set_title(name.upper(), color='white', fontsize=12)
        ax.axis('off')
        
    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"layers_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved: {filename}")

def main():
    inscriptions = ["School", "WAR", "NATURE", "MAGIC"]
    
    for word in inscriptions:
        layers, seed = generate_multi_layer_map(word, size=256)
        visualize_layers(layers, word, seed)

if __name__ == "__main__":
    main()
