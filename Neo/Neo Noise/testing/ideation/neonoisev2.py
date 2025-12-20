"""
NEO Noise: Procedural generation driven by NEO inscription semantics
Uses glyph properties to generate coherent, reproducible patterns
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# NEO Glyph definitions (structure from our earlier work)
NEO_GLYPHS = {
    # Left marks
    'B': {'type': 'left', 'magnitude': 1, 'name': 'beith'},
    'L': {'type': 'left', 'magnitude': 2, 'name': 'luis'},
    'F': {'type': 'left', 'magnitude': 3, 'name': 'fearn'},
    'S': {'type': 'left', 'magnitude': 4, 'name': 'sail'},
    'P': {'type': 'left', 'magnitude': 5, 'name': 'peith'},
    
    # Right marks
    'H': {'type': 'right', 'magnitude': 1, 'name': 'huath'},
    'D': {'type': 'right', 'magnitude': 2, 'name': 'duir'},
    'T': {'type': 'right', 'magnitude': 3, 'name': 'tinne'},
    'C': {'type': 'right', 'magnitude': 4, 'name': 'coll'},
    'W': {'type': 'right', 'magnitude': 5, 'name': 'ceirt'},
    
    # Cross marks
    'M': {'type': 'cross', 'magnitude': 1, 'name': 'muin'},
    'G': {'type': 'cross', 'magnitude': 2, 'name': 'gort'},
    'N': {'type': 'cross', 'magnitude': 3, 'name': 'ngeadal'},  # NG simplified to N
    'Z': {'type': 'cross', 'magnitude': 4, 'name': 'straif'},
    'R': {'type': 'cross', 'magnitude': 5, 'name': 'ruis'},
    
    # Diagonal marks (vowels)
    'A': {'type': 'diagonal', 'magnitude': 1, 'name': 'ailm'},
    'O': {'type': 'diagonal', 'magnitude': 2, 'name': 'onn'},
    'U': {'type': 'diagonal', 'magnitude': 3, 'name': 'ur'},
    'E': {'type': 'diagonal', 'magnitude': 4, 'name': 'eadhadh'},
    'I': {'type': 'diagonal', 'magnitude': 5, 'name': 'idad'},
    
    # Backslash marks (diphthongs - using simplified single letters)
    'Q': {'type': 'backslash', 'magnitude': 1, 'name': 'ae'},  # AE as Q
    'V': {'type': 'backslash', 'magnitude': 2, 'name': 'oi'},  # OI as V
    'X': {'type': 'backslash', 'magnitude': 3, 'name': 'ui'},  # UI as X
    'Y': {'type': 'backslash', 'magnitude': 4, 'name': 'ea'},  # EA as Y
    'J': {'type': 'backslash', 'magnitude': 5, 'name': 'io'},  # IO as J
}

# Type interaction rules (from our pair analysis)
TYPE_INTERACTIONS = {
    ('left', 'right'): 'oppose',
    ('right', 'left'): 'oppose',
    ('left', 'left'): 'reinforce',
    ('right', 'right'): 'reinforce',
    ('cross', 'cross'): 'anchor',
    ('cross', 'diagonal'): 'crystallize',
    ('cross', 'backslash'): 'fracture',
    ('diagonal', 'diagonal'): 'stream',
    ('diagonal', 'backslash'): 'turbulence',
    ('backslash', 'backslash'): 'phase_shift',
}

def inscription_to_seed(inscription):
    """Convert inscription to deterministic seed"""
    return hash(inscription.upper()) & 0xFFFFFFFF

def glyph_at(x, y, seed):
    """Get glyph properties at coordinate using deterministic hash"""
    # Hash coordinates with seed
    h = (x * 73856093 ^ y * 19349663 ^ seed)
    
    # Pick glyph type (5 types)
    types = ['left', 'right', 'cross', 'diagonal', 'backslash']
    glyph_type = types[h % 5]
    
    # Pick magnitude (1-5)
    magnitude = ((h >> 8) % 5) + 1
    
    return {'type': glyph_type, 'magnitude': magnitude}

def get_interaction_strength(g1, g2):
    """Calculate interaction strength between two glyphs"""
    type_pair = (g1['type'], g2['type'])
    interaction = TYPE_INTERACTIONS.get(type_pair, 'neutral')
    
    mag_delta = abs(g1['magnitude'] - g2['magnitude'])
    
    # Interaction type determines base strength
    strength_map = {
        'anchor': 3.0,
        'reinforce': 2.5,
        'oppose': -1.5,
        'crystallize': 4.0,
        'fracture': 5.0,
        'stream': 2.0,
        'turbulence': 3.5,
        'phase_shift': 6.0,
        'neutral': 0.5,
    }
    
    base_strength = strength_map.get(interaction, 1.0)
    
    # Magnitude delta adds variation
    return base_strength + (mag_delta * 0.3)

def neo_noise_field(inscription, width=80, height=80):
    """Generate noise field from inscription"""
    seed = inscription_to_seed(inscription)
    field = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            # Sample local neighborhood (3x3)
            local_glyphs = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        local_glyphs.append(glyph_at(nx, ny, seed))
            
            # Calculate interaction score
            score = 0
            for i in range(len(local_glyphs)):
                for j in range(i + 1, len(local_glyphs)):
                    score += get_interaction_strength(local_glyphs[i], local_glyphs[j])
            
            field[y, x] = score
    
    # Normalize to 0-1 range
    field = (field - field.min()) / (field.max() - field.min() + 1e-8)
    
    return field

def visualize_inscriptions(inscriptions, width=80, height=80):
    """Generate and visualize noise fields for multiple inscriptions"""
    n = len(inscriptions)
    fig = plt.figure(figsize=(15, 4))
    gs = GridSpec(1, n, figure=fig, wspace=0.3)
    
    for idx, inscription in enumerate(inscriptions):
        field = neo_noise_field(inscription, width, height)
        
        ax = fig.add_subplot(gs[0, idx])
        im = ax.imshow(field, cmap='viridis', interpolation='bilinear')
        ax.set_title(f'{inscription}\n(seed: {inscription_to_seed(inscription)})', 
                     fontsize=10, fontweight='bold')
        ax.axis('off')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    plt.suptitle('NEO Noise: Inscription-Driven Procedural Generation', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig

def analyze_inscription_patterns(inscription, width=80, height=80):
    """Detailed analysis of what an inscription produces"""
    field = neo_noise_field(inscription, width, height)
    
    stats = {
        'inscription': inscription,
        'seed': inscription_to_seed(inscription),
        'mean': np.mean(field),
        'std': np.std(field),
        'min': np.min(field),
        'max': np.max(field),
        'high_intensity_ratio': np.sum(field > 0.7) / field.size,
        'low_intensity_ratio': np.sum(field < 0.3) / field.size,
    }
    
    return stats, field

# Test with game-relevant inscriptions
if __name__ == "__main__":
    print("=" * 60)
    print("NEO Noise: Inscription-Driven Procedural Generation")
    print("=" * 60)
    
    # Test basic inscriptions
    test_words = ['FIRE', 'WATER', 'STONE', 'TREE']
    
    print("\nGenerating noise fields for:", test_words)
    fig1 = visualize_inscriptions(test_words)
    plt.savefig('/mnt/user-data/outputs/neo_noise_basic.png', dpi=150, bbox_inches='tight')
    print("Saved: neo_noise_basic.png")
    
    # Test variations
    print("\nTesting variations:")
    variations = ['FIRE', 'FIER', 'RIFE', 'REEF']
    fig2 = visualize_inscriptions(variations)
    plt.savefig('/mnt/user-data/outputs/neo_noise_variations.png', dpi=150, bbox_inches='tight')
    print("Saved: neo_noise_variations.png")
    
    # Detailed analysis
    print("\n" + "=" * 60)
    print("Pattern Analysis:")
    print("=" * 60)
    
    for word in test_words:
        stats, field = analyze_inscription_patterns(word)
        print(f"\n{word}:")
        print(f"  Seed: {stats['seed']}")
        print(f"  Mean intensity: {stats['mean']:.3f}")
        print(f"  Std deviation: {stats['std']:.3f}")
        print(f"  High intensity zones: {stats['high_intensity_ratio']*100:.1f}%")
        print(f"  Low intensity zones: {stats['low_intensity_ratio']*100:.1f}%")
    
    # Test same inscription produces same result
    print("\n" + "=" * 60)
    print("Reproducibility Test:")
    print("=" * 60)
    
    field1 = neo_noise_field('STONE')
    field2 = neo_noise_field('STONE')
    
    identical = np.array_equal(field1, field2)
    print(f"STONE field 1 == STONE field 2: {identical}")
    print(f"Difference: {np.sum(np.abs(field1 - field2))}")
    
    if identical:
        print("✓ Fields are perfectly reproducible!")
    
    plt.show()