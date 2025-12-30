"""
NEO Noise Generator
Formalized procedural generation script based on Semantic Interference Patterns.
Generates batch samples for analysis.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import neo_noise_core as core

# Configuration
OUTPUT_DIR = 'samples'
WIDTH, HEIGHT = 100, 100

def save_heatmap(field, name, seed):
    """Render and save the field."""
    plt.figure(figsize=(10, 10))
    
    # Visualize
    plt.imshow(field, cmap='inferno', interpolation='bicubic')
    
    # Metadata
    plt.title(f'Neo Noise: "{name}"\nSeed: {seed}', fontsize=12)
    plt.axis('off')
    
    # Stats
    mean_val = np.mean(field)
    max_val = np.max(field)
    plt.text(5, HEIGHT-5, f'μ={mean_val:.2f} max={max_val:.2f}', color='white', fontsize=8)
    
    filename = os.path.join(OUTPUT_DIR, f'neo_noise_{name}2.png')
    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Generated: {filename}")

def generate_collage(title, words, output_filename):
    """Generate a grid collage of multiple fields."""
    n = len(words)
    cols = 2
    rows = (n + 1) // 2
    
    fig, axes = plt.subplots(rows, cols, figsize=(10, 5 * rows))
    fig.suptitle(title, fontsize=16, fontweight='bold', color='black')
    
    # Handle single row case (axes is 1D array) or multiple (2D)
    if rows == 1 and cols == 1:
        axes = [axes]
    elif rows > 1 or cols > 1:
        axes = axes.flatten()
    
    for i, word in enumerate(words):
        # Use Core Module for generation
        field, seed = core.generate_field(word, WIDTH, HEIGHT, normalize=True)
        
        ax = axes[i]
        im = ax.imshow(field, cmap='inferno', interpolation='bicubic')
        ax.set_title(f'"{word}"', fontsize=12)
        ax.axis('off')
        
        # Add basic stats
        mean_val = np.mean(field)
        ax.text(0.05, 0.95, f'μ={mean_val:.2f}', transform=ax.transAxes, color='white', fontsize=8, verticalalignment='top')

    # Turn off unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Generated Collage: {path}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("Starting Neo Noise Batch Generation...")
    
    # 1. Elemental Batch
    elements = ['FIRE', 'WATER', 'EARTH', 'AIR']
    for word in elements:
        field, seed = core.generate_field(word, WIDTH, HEIGHT, normalize=True)
        save_heatmap(field, word, seed)
    generate_collage("Elemental Series", elements, "collage_elements.png")
        
    # 2. Structure Batch
    structures = ['STONE', 'STEEL', 'GLASS', 'WOOD']
    for word in structures:
        field, seed = core.generate_field(word, WIDTH, HEIGHT, normalize=True)
        save_heatmap(field, word, seed)
    generate_collage("Structural Series", structures, "collage_structures.png")
        
    # 3. Abstract/Long Sequence Batch
    abstracts = ['INTERESSENCE', 'NEOGHAM_SYSTEM', 'CHAOS_THEORY', 'ORDER']
    for word in abstracts:
        field, seed = core.generate_field(word, WIDTH, HEIGHT, normalize=True)
        save_heatmap(field, word, seed)
    generate_collage("Abstract Series", abstracts, "collage_abstracts.png")
        
    print("\nBatch Complete.")

if __name__ == "__main__":
    main()
