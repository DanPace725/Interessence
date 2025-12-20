"""
Neo Mesh Exporter
Generates a 3D Grid Mesh (.obj) from the Neo Noise Structure Layer.
"""

import numpy as np
import neo_gco as gco
import neo_noise_core as core
import os
import matplotlib.pyplot as plt

OUTPUT_DIR = "samples/3d"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def export_obj(inscription, size=256, height_scale=40.0):
    print(f"Generating 3D GCO Terrain for '{inscription}'...")
    
    # 1. Generate Layers using Core
    # This gives us {Structure, Flow, Constraint, Vitality}
    # Initial raw state.
    base_structure, seed = core.generate_field(inscription, size, size, normalize=True)
    layers = core.generate_semantic_layers(base_structure, seed)
    
    # 2. Run GCO Pipeline
    # This detects features AND applies Erosion to layers['Structure']
    print("  Running Global Closure Operator...")
    context = gco.ClosureContext(layers=layers, seed=seed)
    operator = gco.GlobalClosureOperator(context)
    result = operator.run() # Returns ClosureResult, but also mutates context.layers['Structure']
    
    # 3. Retrieve Data
    structure = layers['Structure'] # Eroded!
    overlay = result.overlay
    
    # Re-normalize? Maybe not, we want true valleys.
    # But for display, maybe clamp 0-1.
    structure = np.clip(structure, 0.0, 1.0)
    
    # 4. Write OBJ
    obj_path = os.path.join(OUTPUT_DIR, f"terrain_{inscription}.obj")
    mtl_filename = f"terrain_{inscription}.mtl"
    tex_filename = f"texture_{inscription}.png"
    
    with open(obj_path, 'w') as f:
        f.write(f"# Neo Noise GCO Terrain: {inscription}\n")
        f.write(f"mtllib {mtl_filename}\n")
        f.write(f"o {inscription}\n")
        
        # Vertices & UVs
        for y in range(size):
            for x in range(size):
                # Vertex
                h = structure[y, x] * height_scale
                px = x - size/2
                pz = y - size/2
                f.write(f"v {px:.4f} {h:.4f} {pz:.4f}\n")
                
                # UV
                u = x / (size - 1)
                v = 1.0 - (y / (size - 1))
                f.write(f"vt {u:.4f} {v:.4f}\n")
                
        # Faces
        f.write(f"usemtl Material\n")
        for y in range(size - 1):
            for x in range(size - 1):
                i00 = (y * size) + x + 1
                i10 = (y * size) + (x + 1) + 1
                i01 = ((y + 1) * size) + x + 1
                i11 = ((y + 1) * size) + (x + 1) + 1
                f.write(f"f {i00}/{i00} {i01}/{i01} {i11}/{i11} {i10}/{i10}\n")
                
    print(f"Saved Mesh: {obj_path}")

    # 5. Write MTL file (simple link to texture)
    mtl_path = os.path.join(OUTPUT_DIR, mtl_filename)
    with open(mtl_path, 'w') as f:
        f.write("newmtl Material\n")
        f.write("Ka 1.0 1.0 1.0\n")
        f.write("Kd 1.0 1.0 1.0\n")
        f.write(f"map_Kd {tex_filename}\n")

    # 6. Generate Texture Map
    print("  Synthesizing GCO Texture...")
    rgb = np.zeros((size, size, 3))
    
    # Pre-calculate base terrain color (Summit vs Valley)
    # Simple gradient from dark dirt to snow
    for y in range(size):
        for x in range(size):
            h = structure[y, x]
            
            # Base Biome
            if h < 0.3: col = [0.2, 0.18, 0.15] # Dark Dirt
            elif h < 0.6: col = [0.3, 0.28, 0.25] # Dirt
            elif h < 0.8: col = [0.4, 0.4, 0.45] # Rock
            else: col = [0.95, 0.95, 1.0] # Snow
            
            val = np.array(col)
            
            # GCO Overlay Features
            # 1.0 = Major River (Cyan)
            # 0.8 = Minor River (Teal)
            # 0.6 = Lake (Blue)
            # 0.3 = Forest (Green)
            
            feat = overlay[y, x]
            
            if feat >= 0.9: # Major River
                val = [0.0, 1.0, 1.0] # Cyan
            elif feat >= 0.7: # Minor River
                val = [0.0, 0.7, 0.9] # Teal
                # Mix slightly with base to fade edges? No, distinct is better for debugging.
            elif feat >= 0.5: # Lake
                val = [0.0, 0.4, 1.0] # Deep Blue
            elif feat >= 0.2: # Forest
                # Mix Green with base
                forest_col = np.array([0.1, 0.5, 0.1])
                val = (val * 0.4) + (forest_col * 0.6)
            
            rgb[y, x] = np.clip(val, 0, 1)
            
    tex_path = os.path.join(OUTPUT_DIR, tex_filename)
    plt.imsave(tex_path, rgb)
    print(f"Saved Texture: {tex_path}")

def main():
    # Test High Density Region
    export_obj("FIRE", size=256, height_scale=40.0)
    export_obj("MAGIC", size=256, height_scale=40.0)

if __name__ == "__main__":
    main()
