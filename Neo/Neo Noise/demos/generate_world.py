"""
Large World Generator Demo
Generates a continental-scale world map with integrated GCO hydrology.
"""

import sys
import os

# Add src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
import neo_noise_core as core
import neo_world as world
import neo_gco as gco

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "samples", "world_gco")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def generate_world_with_hydrology(inscription: str, 
                                   size: int = 512,
                                   run_gco: bool = True):
    """
    Generate a large world map with integrated GCO hydrology.
    
    Args:
        inscription: World seed string
        size: Map size (square)
        run_gco: Whether to run GCO for rivers/lakes/forests
    """
    print(f"\n{'='*60}")
    print(f"Generating World: '{inscription}' ({size}x{size})")
    print(f"{'='*60}")
    
    # Step 1: Generate continental map
    print("\n[1/4] Generating continental elevation and climate...")
    world_map = world.generate_continental_map(
        inscription, 
        width=size, 
        height=size // 2,  # 2:1 aspect for world map
        semantic_bias_strength=0.4
    )
    
    # Step 2: Create semantic layers from elevation
    print("[2/4] Deriving semantic layers...")
    layers = core.generate_semantic_layers(world_map.elevation, world_map.seed)
    
    # Override Vitality with moisture (more realistic for world-scale)
    layers['Vitality'] = world_map.moisture
    
    # Step 3: Run GCO with integrated hydrology
    committed_features = []
    overlay = np.zeros_like(world_map.elevation)
    
    if run_gco:
        print("[3/4] Running GCO with integrated hydrology...")
        ctx = gco.ClosureContext(layers=layers, seed=world_map.seed)
        operator = gco.GlobalClosureOperator(ctx)
        result = operator.run(enable_hydraulic_erosion=False)  # Skip erosion for speed at this scale
        
        committed_features = result.committed_features
        overlay = result.overlay
        
        print(f"      Committed {len(committed_features)} features")
        
        # Count by type
        rivers = sum(1 for f in committed_features if f.type == 'river')
        lakes = sum(1 for f in committed_features if f.type == 'lake')
        forests = sum(1 for f in committed_features if f.type == 'forest')
        print(f"      Rivers: {rivers}, Lakes: {lakes}, Forests: {forests}")
    
    # Step 4: Visualize
    print("[4/4] Generating visualization...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f"World: {inscription} (GCO Integrated Hydrology)", fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    # Row 1: Base layers
    axes[0, 0].imshow(world_map.elevation, cmap='terrain', interpolation='bicubic')
    axes[0, 0].set_title('Elevation', color='white')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(world_map.moisture, cmap='Blues', interpolation='bicubic')
    axes[0, 1].set_title('Moisture', color='white')
    axes[0, 1].axis('off')
    
    # Biome map (from continental classification)
    biome_rgb = np.zeros((*world_map.biome_ids.shape, 3))
    for biome in world.MACRO_BIOMES:
        mask = world_map.biome_ids == biome.id
        biome_rgb[mask] = biome.color
    axes[0, 2].imshow(biome_rgb, interpolation='nearest')
    axes[0, 2].set_title('Continental Biomes', color='white')
    axes[0, 2].axis('off')
    
    # Row 2: GCO results
    # Flow layer
    axes[1, 0].imshow(layers['Flow'], cmap='viridis', interpolation='bicubic')
    axes[1, 0].set_title('Flow (Gradient)', color='white')
    axes[1, 0].axis('off')
    
    # Constraint layer
    axes[1, 1].imshow(layers['Constraint'], cmap='gray', interpolation='bicubic')
    axes[1, 1].set_title('Constraint (Edges)', color='white')
    axes[1, 1].axis('off')
    
    # GCO overlay on terrain
    ax = axes[1, 2]
    ax.imshow(world_map.elevation, cmap='terrain', interpolation='bicubic', alpha=0.7)
    
    # Color overlay
    h, w = overlay.shape
    rgba = np.zeros((h, w, 4))
    
    # Rivers (cyan)
    is_river = overlay > 0.7
    rgba[is_river] = [0.0, 1.0, 1.0, 1.0]
    
    # Lakes (blue)
    is_lake = (overlay > 0.5) & (overlay <= 0.7)
    rgba[is_lake] = [0.0, 0.4, 1.0, 1.0]
    
    # Forests (green)
    is_forest = (overlay > 0.2) & (overlay <= 0.4)
    rgba[is_forest] = [0.2, 0.8, 0.2, 0.5]
    
    ax.imshow(rgba, interpolation='nearest')
    ax.set_title('Rivers & Forests (GCO)', color='white')
    ax.axis('off')
    
    plt.tight_layout()
    
    filename = os.path.join(OUTPUT_DIR, f"world_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {filename}")
    
    return world_map, committed_features


def main():
    # Generate a few world maps
    inscriptions = ["PANGAEA", "ARCHIPELAGO", "INTERESSENCE"]
    
    for word in inscriptions:
        generate_world_with_hydrology(word, size=512, run_gco=True)
    
    print("\n" + "="*60)
    print("World generation complete!")
    print("="*60)


if __name__ == "__main__":
    main()
