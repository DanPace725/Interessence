"""
Generate noise map samples to visualize refactored Neo Noise.
"""
import neo_noise_core as core
import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = 'samples/refactored'
os.makedirs(OUTPUT_DIR, exist_ok=True)

inscriptions = ['FIRE', 'WATER', 'WOLF', 'INTERESSENCE', 'MAGIC', 'STONE']

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Neo Noise: Sequential Composition + Actual Bounds', fontsize=16, color='white')
fig.patch.set_facecolor('#0f172a')

for idx, word in enumerate(inscriptions):
    ax = axes[idx // 3, idx % 3]
    
    field, seed = core.generate_field(word, 256, 256, normalize=True, octaves=4)
    bias = core.get_inscription_bias(word)
    
    ax.imshow(field, cmap='terrain', interpolation='bicubic')
    
    title = f"{word}\nA={bias['action']:.2f} S={bias['structure']:.2f} M={bias['modulation']:.2f} T={bias['transform']:.2f}"
    ax.set_title(title, color='white', fontsize=10)
    ax.axis('off')

plt.tight_layout()
filename = os.path.join(OUTPUT_DIR, 'noise_comparison_refactored.png')
plt.savefig(filename, facecolor=fig.get_facecolor(), dpi=150)
plt.close()
print(f'Saved: {filename}')
