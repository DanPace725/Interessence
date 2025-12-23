"""
Bias Strength Comparison Test
Generates noise maps at different semantic_bias_strength values to visualize the effect.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add Neo Noise folder to path (go up two directories from testing/bias_strength)
neo_noise_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, neo_noise_dir)
import neo_noise_core as core

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_bias_comparison(inscription, size=200):
    """Generate a comparison grid showing different bias strengths."""
    
    # Bias strengths to test
    bias_values = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'Semantic Bias Strength Comparison: "{inscription}"', fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    axes = axes.flatten()
    
    for i, bias in enumerate(bias_values):
        field, seed = core.generate_field(inscription, size, size, 
                                          normalize=True, 
                                          semantic_bias_strength=bias)
        
        ax = axes[i]
        ax.imshow(field, cmap='inferno', interpolation='bicubic')
        ax.set_title(f'Bias = {bias}', color='white', fontsize=12)
        ax.axis('off')
        
        # Add stats
        mean_val = np.mean(field)
        std_val = np.std(field)
        ax.text(0.05, 0.95, f'μ={mean_val:.2f} σ={std_val:.2f}', 
                transform=ax.transAxes, color='white', fontsize=9, 
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
    
    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"bias_comparison_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), dpi=150)
    plt.close()
    print(f"Saved: {filename}")

def generate_word_comparison(words, bias_strength=0.3, size=150):
    """Compare different words at the same bias strength."""
    
    n = len(words)
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    fig.suptitle(f'Word Comparison (bias={bias_strength})', fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if hasattr(axes, 'flatten') else axes
    
    for i, word in enumerate(words):
        field, seed = core.generate_field(word, size, size, 
                                          normalize=True, 
                                          semantic_bias_strength=bias_strength)
        
        # Get bias info
        bias_info = core.get_inscription_bias(word)
        
        ax = axes[i]
        ax.imshow(field, cmap='inferno', interpolation='bicubic')
        ax.set_title(f'{word}', color='white', fontsize=11)
        ax.axis('off')
        
        # Show dominant dimension
        dims = ['Act', 'Str', 'Mod', 'Trn']
        weights = [bias_info['action'], bias_info['structure'], 
                   bias_info['modulation'], bias_info['transform']]
        dominant_idx = np.argmax(weights)
        ax.text(0.05, 0.95, f'{dims[dominant_idx]}={weights[dominant_idx]:.0%}', 
                transform=ax.transAxes, color='cyan', fontsize=9, 
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
    
    # Hide unused axes
    for j in range(i+1, len(axes)):
        axes[j].axis('off')
        axes[j].set_visible(False)
    
    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"word_comparison_bias{bias_strength}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), dpi=150)
    plt.close()
    print(f"Saved: {filename}")

def main():
    print("=" * 50)
    print("Bias Strength Comparison Test")
    print("=" * 50)
    
    # Test 1: Same word, different bias strengths
    test_words = ["FIRE", "WATER", "INTERESSENCE"]
    for word in test_words:
        generate_bias_comparison(word)
    
    # Test 2: Different words at same bias
    # Anagrams to show order sensitivity
    anagrams = ["FIRE", "FIER", "RIFE", "ERIF"]
    generate_word_comparison(anagrams, bias_strength=0.5)
    
    # Test 3: Semantically different words
    elements = ["FIRE", "WATER", "EARTH", "AIR", "STONE", "WIND"]
    generate_word_comparison(elements, bias_strength=0.5)
    
    print("\nDone! Check the output folder for comparison images.")

if __name__ == "__main__":
    main()
