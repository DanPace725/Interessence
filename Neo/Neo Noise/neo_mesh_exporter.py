"""
Neo Mesh Exporter
Generates a 3D Grid Mesh (.obj) from the Neo Noise Structure Layer.
"""

import numpy as np
import neo_noise_core as core
import os
import matplotlib.pyplot as plt

OUTPUT_DIR = "samples/3d"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def export_obj(inscription, size=256, height_scale=40.0, erosion_steps=10):
    print(f"Generating 3D Mesh for '{inscription}' (Smoothing: {erosion_steps})...")
    
    # 1. Generate Field
    # This is the Raw Bedrock (Jagged)
    raw_structure, seed = core.generate_field(inscription, size, size, normalize=True)
    
    # 2. Apply Erosion (Smoothing)
    # The user noted "Jaggedness". This is "Volatility".
    # Real terrain has sediment. We simulate this by running the Diffusion part of evolution.
    # High 'steps' = Older, smoother mountains.
    structure = core.evolve_field(raw_structure, steps=erosion_steps, diffusion=0.15, decay=0.0)
    
    # Re-normalize after smoothing to keep height consistent
    structure = (structure - structure.min()) / (structure.max() - structure.min() + 1e-8)
    
    # 3. Write OBJ
    obj_path = os.path.join(OUTPUT_DIR, f"{inscription}.obj")
    
    with open(obj_path, 'w') as f:
        f.write(f"# Neo Noise Terrain: {inscription}\n")
        f.write(f"o {inscription}\n")
        
        # Vertices: v x y z
        # We look straight down: x=x, y=height, z=y
        for y in range(size):
            for x in range(size):
                h = structure[y, x] * height_scale
                # Center the mesh
                px = x - size/2
                pz = y - size/2
                f.write(f"v {px:.4f} {h:.4f} {pz:.4f}\n")
                
        # UVs (Optional, but good for texturing)
        for y in range(size):
            for x in range(size):
                u = x / (size - 1)
                v = 1.0 - (y / (size - 1)) # Flip V usually
                f.write(f"vt {u:.4f} {v:.4f}\n")
                
        # Faces (Quads)
        # vertex index is 1-based
        for y in range(size - 1):
            for x in range(size - 1):
                # Indices in the grid
                i00 = (y * size) + x + 1
                i10 = (y * size) + (x + 1) + 1
                i01 = ((y + 1) * size) + x + 1
                i11 = ((y + 1) * size) + (x + 1) + 1
                
                # Face: v/vt
                # p00, p01, p11, p10 (CCW winding)
                # Obj index: i00 i01 i11 i10
                f.write(f"f {i00}/{i00} {i01}/{i01} {i11}/{i11} {i10}/{i10}\n")
                
    print(f"Saved Mesh: {obj_path}")

    # 3. Create Composite Texture Map (The 4-Layer Splat)
    # R = Rock/Structure (Grey)
    # G = Vitality (Green)
    # B = Flow/Water (Blue)
    
    print("  Synthesizing Composite Texture...")
    
    # Generate the other layers derived from the SMOOTHED structure
    # Flow
    gy, gx = np.gradient(structure)
    flow = np.sqrt(gx**2 + gy**2)
    flow = (flow - flow.min()) / (flow.max() - flow.min() + 1e-8)
    
    # Vitality (Simulation)
    # We use the smoothed structure as the base for life
    vitality = core.evolve_field(structure, steps=10, feed_rate=0.012, decay=0.01)
    vitality = np.clip(vitality, 0, 1)

    # Constraint (Slope/Roughness)
    laplacian = np.abs(np.gradient(gx, axis=1) + np.gradient(gy, axis=0))
    constraint = (laplacian - laplacian.min()) / (laplacian.max() - laplacian.min() + 1e-8)

    # Composite logic:
    # Base = Rock (Grey based on Height)
    # If High Vitality -> Green (Forest)
    # If High Flow (and Low Slope) -> Blue (River)
    
    rgb = np.zeros((size, size, 3))
    
    for y in range(size):
        for x in range(size):
            h = structure[y, x]
            v = vitality[y, x]
            f = flow[y, x]
            c = constraint[y, x]
            
            # Base Color (Stone/Dirt)
            # Darker at low altitude, lighter at high
            base_val = 0.2 + (h * 0.6)
            color = np.array([base_val, base_val-0.05, base_val-0.1]) # Slight brownish tint
            
            # Vitality (Vegetation)
            # Grows where life is high, but not too high altitude (Snow)
            if v > 0.3 and h < 0.8:
                strength = (v - 0.3) * 1.5
                strength = min(strength, 1.0)
                # Mix in Green
                target = np.array([0.1, 0.5, 0.1])
                color = (color * (1-strength)) + (target * strength)
                
            # Flow (Water)
            # Accumulates in valleys (Low H) with high flow
            if f > 0.6 and h < 0.4:
                strength = (f - 0.6) * 2.0
                strength = min(strength, 1.0)
                # Mix in Blue
                target = np.array([0.1, 0.3, 0.8])
                color = (color * (1-strength)) + (target * strength)
                
            # Snow (High Altitude)
            if h > 0.85:
                strength = (h - 0.85) * 6.0
                strength = min(strength, 1.0)
                target = np.array([0.95, 0.95, 1.0])
                color = (color * (1-strength)) + (target * strength)
                
            rgb[y, x] = np.clip(color, 0, 1)

    plt.imsave(os.path.join(OUTPUT_DIR, f"{inscription}_texture.png"), rgb)
    print(f"Saved Texture: {inscription}_texture.png")

def main():
    # Comparing a "Jagged" concept vs a "Smooth" concept
    # But applying erosion to both to fix the artifacting.
    export_obj("SPIRE", size=256, height_scale=50.0, erosion_steps=5)   # Young mountains (Jagged)
    export_obj("PLAINS", size=256, height_scale=20.0, erosion_steps=20) # Old terrain (Smooth)

if __name__ == "__main__":
    main()
