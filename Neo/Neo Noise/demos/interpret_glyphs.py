"""
Neo Glyph Interpreter
Reads the latent glyph grid and decodes it to Latin letters.

The glyph substrate can be "read" back to letters since each (type, magnitude)
pair maps to exactly one letter in the Neo alphabet.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import neo_noise_core as core
import neo_reading as reading


# Build reverse mapping: (type, magnitude) -> letter
GLYPH_TO_LETTER = {}
for letter, props in core.NEO_GLYPHS.items():
    key = (props['type'], props['mag'])
    GLYPH_TO_LETTER[key] = letter


def interpret_glyph_grid(seed: int, width: int, height: int, 
                         cell_size: int = 14) -> list:
    """
    Read the glyph grid and decode each cell to its Latin letter.
    
    Args:
        seed: Inscription seed (from core.generate_field)
        width, height: Grid dimensions in pixels
        cell_size: Size of each glyph cell
        
    Returns:
        List of strings (one per row)
    """
    grid_w = width // cell_size
    grid_h = height // cell_size
    
    decoded = []
    for gy in range(grid_h):
        row = []
        for gx in range(grid_w):
            # Sample at cell center
            cx = gx * cell_size + cell_size // 2
            cy = gy * cell_size + cell_size // 2
            
            # Get glyph props (scale to match noise generation)
            glyph_type, magnitude = reading.get_glyph_at(seed, cx // 4, cy // 4)
            
            # Decode to letter
            letter = GLYPH_TO_LETTER.get((glyph_type, magnitude), '?')
            row.append(letter)
        decoded.append(''.join(row))
    
    return decoded


def print_mapping():
    """Print the glyph-to-letter mapping table."""
    print("Glyph -> Letter Mapping:")
    print("-" * 40)
    for gtype in ['right', 'left', 'cross', 'diagonal', 'backslash']:
        letters = []
        for mag in range(1, 6):
            letter = GLYPH_TO_LETTER.get((gtype, mag), '?')
            letters.append(f"{mag}={letter}")
        print(f"  {gtype:10}: {', '.join(letters)}")
    print()


if __name__ == "__main__":
    inscription = "INTERESSENCE"
    size = 256
    cell_size = 14
    
    # Get seed from inscription
    _, seed = core.generate_field(inscription, 4, 4)
    
    print_mapping()
    
    print(f'Reading glyph layer for "{inscription}" (seed: {seed}):')
    print("=" * 60)
    
    # Decode the grid
    decoded = interpret_glyph_grid(seed, size, size, cell_size)
    
    # Print all rows
    for i, row in enumerate(decoded):
        print(f"{i:2}: {row}")
    
    print()
    print(f"Grid size: {len(decoded[0])} x {len(decoded)} letters")
    
    # Count letter frequencies
    all_letters = ''.join(decoded)
    from collections import Counter
    freq = Counter(all_letters)
    print(f"\nLetter frequencies:")
    for letter, count in freq.most_common():
        print(f"  {letter}: {count} ({100*count/len(all_letters):.1f}%)")
