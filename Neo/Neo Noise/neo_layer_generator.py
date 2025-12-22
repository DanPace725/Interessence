"""
Neo Layer Generator
Proof of Concept: Deriving all 4 Functional Layers from a single Neo Noise Inscription.
Now includes Biome Classification and optional Hydraulic Erosion.
"""

import numpy as np
import matplotlib.pyplot as plt
import neo_noise_core as core
import os

OUTPUT_DIR = "samples/layers"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_multi_layer_map(inscription, size=256, enable_erosion=True):
    print(f"Generating Layers for '{inscription}'...")
    
    # 1. STRUCTURE LAYER (Base Field)
    structure, seed = core.generate_field(inscription, size, size, normalize=True)
    
    # 2. Derive Semantic Layers via Core
    layers = core.generate_semantic_layers(structure, seed)
    
    # 3. Optional: Run Hydraulic Erosion (adds WaterAccumulation layer)
    if enable_erosion:
        from neo_hydrology import HydraulicSimulator, HydroParams
        
        params = HydroParams(
            num_droplets=50000,
            erosion_rate=0.01,
            deposition_rate=0.02
        )
        
        simulator = HydraulicSimulator(layers['Structure'], params, seed=seed)
        result = simulator.simulate()
        
        layers['Structure'] = result.heightmap
        layers['WaterAccumulation'] = result.accumulation

    return layers, seed

def visualize_layers(layers, inscription, seed):
    # Check if we have 5 layers (with WaterAccumulation) or 4
    n_layers = len(layers)
    fig, axes = plt.subplots(1, n_layers, figsize=(5 * n_layers, 5))
    fig.suptitle(f"Neo Semantic Layers: {inscription} (Seed: {seed})", fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    cmaps = {
        "Structure": "terrain",     # Terrain heightmap
        "Flow": "viridis",          # Vector/Movement feel
        "Constraint": "gray",       # Hard edges
        "Vitality": "Greens",       # Life/Biomass
        "WaterAccumulation": "Blues" # Watershed
    }

    for i, (name, field) in enumerate(layers.items()):
        ax = axes[i] if n_layers > 1 else axes
        cmap = cmaps.get(name, "inferno")
        im = ax.imshow(field, cmap=cmap, interpolation='bicubic')
        ax.set_title(name.upper(), color='white', fontsize=12)
        ax.axis('off')
        
    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"layers_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved: {filename}")

def visualize_biomes(layers, inscription, seed):
    """Visualize discovered biomes using the BiomeClassifier."""
    import neo_biomes as biomes
    
    classifier = biomes.BiomeClassifier(n_biomes=6, seed=seed)
    biome_map = classifier.fit_predict(layers)
    classifier.print_biome_summary()
    
    # Generate biome texture
    rgb = biomes.generate_biome_texture(biome_map, classifier)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0f172a')
    ax.imshow(rgb)
    ax.set_title(f"Biomes: {inscription}", color='white', fontsize=14)
    ax.axis('off')
    
    filename = os.path.join(OUTPUT_DIR, f"biomes_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved: {filename}")

def visualize_closure_overlay(closure_result, layers, inscription):
    """
    Visualize the GCO result (Rivers) overlaid on ALL layers to prove alignment.
    """
    import neo_gco as gco
    
    # Create a 4-panel plot (skip WaterAccumulation for overlay viz)
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle(f"GCO Closure Analysis: {inscription} (Rivers)", fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    # Overlay: Rivers (Cyan for high visibility across maps)
    overlay_mask = closure_result.overlay
    height, width = overlay_mask.shape
    
    # Define the 4 views
    views = [
        ('Structure', 'terrain', "Final Terrain (Eroded)"),
        ('Flow', 'viridis', "Following Flow (Validation)"),
        ('Constraint', 'gray', "Avoiding Constraint (Validation)"),
        ('Vitality', 'Greens', "Ecological Context (Hydrated)")
    ]
    
    for i, (layer_name, cmap, title) in enumerate(views):
        ax = axes[i]
        
        # 1. Base Layer
        ax.imshow(layers[layer_name], cmap=cmap, interpolation='bicubic')
        
        # 2. River/Lake/Forest Overlay
        # Create RGBA
        rgba = np.zeros((height, width, 4))
        
        # We need to map the scalar overlay back to colors
        # 1.0 = River (Cyan) -> (0, 1, 1)
        # 0.6 = Lake (Blue) -> (0, 0, 1)
        # 0.3 = Forest (Green) -> (0, 1, 0)
        
        # Vectorized color mapping
        # Major River (1.0) -> Cyan (0, 1, 1)
        is_major = (overlay_mask > 0.9)
        rgba[is_major] = [0.0, 1.0, 1.0, 1.0]

        # Minor River (0.8) -> Light Cyan/Teal (0, 0.8, 0.8)
        is_minor = (overlay_mask > 0.7) & (overlay_mask < 0.9)
        rgba[is_minor] = [0.0, 0.7, 0.9, 0.8] # Slightly dimmer, slightly transp
        
        # Lake
        is_lake = (overlay_mask > 0.5) & (overlay_mask < 0.7)
        rgba[is_lake] = [0.0, 0.4, 1.0, 1.0]
        
        # Forest
        is_forest = (overlay_mask > 0.2) & (overlay_mask < 0.4)
        rgba[is_forest] = [0.2, 0.8, 0.2, 0.6] # Semi-transparent green
        
        ax.imshow(rgba, interpolation='nearest')
        
        ax.set_title(title, color='white', fontsize=12)
        ax.axis('off')

    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"closure_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved Closure Analysis: {filename}")

def main():
    import neo_gco as gco
    
    inscriptions = ["FLAME", "WATER", "NATURE", "MAGIC"]
    
    for word in inscriptions:
        # Generate layers with hydraulic erosion
        layers, seed = generate_multi_layer_map(word, size=256, enable_erosion=True)
        
        # Visualize raw layers
        visualize_layers(layers, word, seed)
        
        # Visualize biomes
        visualize_biomes(layers, word, seed)
        
        # Run GCO (skip hydraulic erosion since we already did it)
        print(f"Running GCO for {word}...")
        context = gco.ClosureContext(layers=layers, seed=seed)
        operator = gco.GlobalClosureOperator(context)
        result = operator.run(enable_hydraulic_erosion=False)  # Already done above
        print(f"  -> Committed {len(result.committed_features)} features.")
        
        visualize_closure_overlay(result, layers, word)

if __name__ == "__main__":
    main()

