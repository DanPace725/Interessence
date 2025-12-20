
import sys
import os
import numpy as np

# Add local path to import neo_noise_core
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Neo Noise"))
import neo_noise_core as core

def main():
    # Use a fixed integer seed to avoid Python hash randomization
    SEED_INT = 42069
    WIDTH = 5
    HEIGHT = 5
    
    print(f"Generating Neo Field with Int Seed: {SEED_INT}")
    print(f"Dimensions: {WIDTH}x{HEIGHT}")
    
    field, seed = core.generate_field(SEED_INT, WIDTH, HEIGHT, normalize=True)
    
    print("\n--- Expected Values (Row Major) ---")
    for y in range(HEIGHT):
        row_str = ""
        for x in range(WIDTH):
            val = field[y, x]
            row_str += f"{val:.6f} "
        print(row_str)
        
    # Also print raw interaction values for debugging if needed
    # (By disabling normalization temporarily)
    raw_field, _ = core.generate_field(SEED_INT, WIDTH, HEIGHT, normalize=False)
    print("\n--- Raw Values ---")
    for y in range(HEIGHT):
        row_str = ""
        for x in range(WIDTH):
            val = raw_field[y, x]
            row_str += f"{val:.4f} "
        print(row_str)

if __name__ == "__main__":
    main()
