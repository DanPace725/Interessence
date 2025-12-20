"""
Neo World Generator
Multi-scale world generation with continental and regional layers.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import neo_noise_core as core
import os

OUTPUT_DIR = "samples/world"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


@dataclass
class MacroBiome:
    """Continental-scale biome definition."""
    id: int
    name: str
    color: Tuple[float, float, float]
    # Thresholds for classification
    min_elevation: float = 0.0
    max_elevation: float = 1.0
    min_moisture: float = 0.0
    max_moisture: float = 1.0


# Continental biome definitions (Whittaker-inspired)
MACRO_BIOMES = [
    MacroBiome(0, "Deep Ocean",    (0.05, 0.10, 0.30), max_elevation=0.20),
    MacroBiome(1, "Ocean",         (0.10, 0.20, 0.50), min_elevation=0.20, max_elevation=0.30),
    MacroBiome(2, "Coast",         (0.20, 0.40, 0.60), min_elevation=0.30, max_elevation=0.35),
    MacroBiome(3, "Desert",        (0.85, 0.75, 0.50), min_elevation=0.35, max_moisture=0.25),
    MacroBiome(4, "Savanna",       (0.70, 0.65, 0.35), min_elevation=0.35, min_moisture=0.25, max_moisture=0.40),
    MacroBiome(5, "Grassland",     (0.55, 0.70, 0.35), min_elevation=0.35, min_moisture=0.40, max_moisture=0.55),
    MacroBiome(6, "Forest",        (0.20, 0.55, 0.20), min_elevation=0.35, min_moisture=0.55, max_moisture=0.75),
    MacroBiome(7, "Rainforest",    (0.10, 0.40, 0.15), min_elevation=0.35, max_elevation=0.55, min_moisture=0.75),
    MacroBiome(8, "Taiga",         (0.30, 0.45, 0.35), min_elevation=0.55, max_elevation=0.70, min_moisture=0.40),
    MacroBiome(9, "Tundra",        (0.60, 0.65, 0.65), min_elevation=0.55, max_elevation=0.70, max_moisture=0.40),
    MacroBiome(10, "Alpine",       (0.50, 0.55, 0.55), min_elevation=0.70, max_elevation=0.85),
    MacroBiome(11, "Snow Peaks",   (0.95, 0.95, 1.00), min_elevation=0.85),
]


@dataclass
class ContinentalMap:
    """Container for continental-scale world data."""
    inscription: str
    seed: int
    width: int
    height: int
    elevation: np.ndarray      # Height/landmass
    moisture: np.ndarray       # Precipitation/water availability
    temperature: np.ndarray    # Climate (derived from elevation + latitude)
    biome_ids: np.ndarray      # Macro-biome classification
    

def generate_continental_map(inscription: str, width: int = 512, height: int = 256) -> ContinentalMap:
    """
    Generate a continental-scale world map using low-frequency Neo Noise.
    
    Args:
        inscription: World seed string (e.g., "INTERESSENCE")
        width, height: World map resolution (default 512x256 for 2:1 aspect)
        
    Returns:
        ContinentalMap with elevation, moisture, temperature, and biome data
    """
    print(f"Generating Continental Map for '{inscription}' ({width}x{height})...")
    
    # Create base seed
    base_seed = hash(inscription.upper()) & 0xFFFFFFFF
    
    # 1. ELEVATION: Low-frequency noise for landmasses
    # Only 2 octaves = very smooth, continental-scale features
    elevation_raw, _ = core.generate_field(
        base_seed,
        width, height,
        normalize=True,
        octaves=2,
        persistence=0.5,
        lacunarity=2.0
    )
    
    # STRETCH to full 0-1 range for dramatic continental features
    # This creates oceans (low) and mountains (high)
    e_min, e_max = elevation_raw.min(), elevation_raw.max()
    if e_max - e_min > 0.01:
        elevation = (elevation_raw - e_min) / (e_max - e_min)
    else:
        elevation = np.full_like(elevation_raw, 0.5)
    
    # Apply contrast curve (S-curve) for more distinct land/water
    elevation = np.clip(elevation * 1.2 - 0.1, 0, 1)
    
    # 2. MOISTURE: Different seed, also low frequency
    # Represents precipitation patterns
    moisture_seed = base_seed ^ 0xDEADBEEF
    moisture_raw, _ = core.generate_field(
        moisture_seed,
        width, height,
        normalize=True,
        octaves=2,
        persistence=0.6,
        lacunarity=2.0
    )
    
    # STRETCH moisture to full range
    m_min, m_max = moisture_raw.min(), moisture_raw.max()
    if m_max - m_min > 0.01:
        moisture = (moisture_raw - m_min) / (m_max - m_min)
    else:
        moisture = np.full_like(moisture_raw, 0.5)
    
    # 3. TEMPERATURE: Derived from elevation + latitude gradient
    # Hot at equator (center), cold at poles (top/bottom)
    latitude = np.linspace(1.0, 0.0, height).reshape(-1, 1)
    latitude = np.abs(latitude - 0.5) * 2  # 0 at equator, 1 at poles
    latitude = np.tile(latitude, (1, width))
    
    # Temperature decreases with altitude and latitude
    temperature = 1.0 - (latitude * 0.6) - (elevation * 0.4)
    temperature = np.clip(temperature, 0, 1)
    
    # 4. BIOME CLASSIFICATION
    biome_ids = classify_continental_biomes(elevation, moisture, temperature)
    
    return ContinentalMap(
        inscription=inscription,
        seed=base_seed,
        width=width,
        height=height,
        elevation=elevation,
        moisture=moisture,
        temperature=temperature,
        biome_ids=biome_ids
    )


def classify_continental_biomes(elevation: np.ndarray, moisture: np.ndarray, 
                                 temperature: np.ndarray) -> np.ndarray:
    """
    Classify each pixel into a macro-biome based on Whittaker-style rules.
    """
    h, w = elevation.shape
    biome_ids = np.zeros((h, w), dtype=int)
    
    for y in range(h):
        for x in range(w):
            elev = elevation[y, x]
            moist = moisture[y, x]
            temp = temperature[y, x]
            
            # Find matching biome (first match wins, order matters)
            biome_id = 5  # Default: Grassland
            
            for biome in MACRO_BIOMES:
                if (biome.min_elevation <= elev <= biome.max_elevation and
                    biome.min_moisture <= moist <= biome.max_moisture):
                    biome_id = biome.id
                    break
                    
            biome_ids[y, x] = biome_id
            
    return biome_ids


def get_region_context(world_map: ContinentalMap, region_x: int, region_y: int,
                       region_size: int = 8) -> Dict:
    """
    Sample the continental map at a region location to get context for regional generation.
    
    Args:
        world_map: The continental map
        region_x, region_y: Region coordinates (in world grid)
        region_size: Size of region to sample (averages over area)
        
    Returns:
        Dict with context values for regional generation
    """
    # Calculate pixel bounds
    px = min(region_x * region_size, world_map.width - region_size)
    py = min(region_y * region_size, world_map.height - region_size)
    
    # Sample region
    elev_sample = world_map.elevation[py:py+region_size, px:px+region_size]
    moist_sample = world_map.moisture[py:py+region_size, px:px+region_size]
    temp_sample = world_map.temperature[py:py+region_size, px:px+region_size]
    biome_sample = world_map.biome_ids[py:py+region_size, px:px+region_size]
    
    # Find dominant biome
    biome_counts = np.bincount(biome_sample.flatten(), minlength=len(MACRO_BIOMES))
    dominant_biome_id = np.argmax(biome_counts)
    
    return {
        'base_elevation': float(np.mean(elev_sample)),
        'moisture': float(np.mean(moist_sample)),
        'temperature': float(np.mean(temp_sample)),
        'dominant_biome': MACRO_BIOMES[dominant_biome_id].name,
        'biome_id': dominant_biome_id,
        'region_x': region_x,
        'region_y': region_y
    }


def visualize_continental_map(world_map: ContinentalMap, show_layers: bool = True):
    """
    Visualize the continental map with multiple views.
    """
    if show_layers:
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f"Continental Map: {world_map.inscription}", fontsize=16, color='white')
        fig.patch.set_facecolor('#0f172a')
        
        # Elevation
        ax = axes[0, 0]
        ax.imshow(world_map.elevation, cmap='terrain', interpolation='bicubic')
        ax.set_title('Elevation', color='white')
        ax.axis('off')
        
        # Moisture
        ax = axes[0, 1]
        ax.imshow(world_map.moisture, cmap='Blues', interpolation='bicubic')
        ax.set_title('Moisture', color='white')
        ax.axis('off')
        
        # Temperature
        ax = axes[1, 0]
        ax.imshow(world_map.temperature, cmap='coolwarm', interpolation='bicubic')
        ax.set_title('Temperature', color='white')
        ax.axis('off')
        
        # Biomes (colored)
        ax = axes[1, 1]
        biome_rgb = np.zeros((world_map.height, world_map.width, 3))
        for biome in MACRO_BIOMES:
            mask = world_map.biome_ids == biome.id
            biome_rgb[mask] = biome.color
        ax.imshow(biome_rgb, interpolation='nearest')
        ax.set_title('Biomes', color='white')
        ax.axis('off')
        
        plt.tight_layout()
        filename = os.path.join(OUTPUT_DIR, f"continental_layers_{world_map.inscription}.png")
        plt.savefig(filename, facecolor=fig.get_facecolor())
        plt.close()
        print(f"Saved: {filename}")
    
    # Main biome map (high quality)
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor('#0f172a')
    
    biome_rgb = np.zeros((world_map.height, world_map.width, 3))
    for biome in MACRO_BIOMES:
        mask = world_map.biome_ids == biome.id
        biome_rgb[mask] = biome.color
        
    ax.imshow(biome_rgb, interpolation='nearest')
    ax.set_title(f"World Map: {world_map.inscription}", color='white', fontsize=14)
    ax.axis('off')
    
    # Add biome legend
    legend_text = "  ".join([f"{b.name}" for b in MACRO_BIOMES])
    
    filename = os.path.join(OUTPUT_DIR, f"world_{world_map.inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


def generate_region_tile(world_map: ContinentalMap, region_x: int, region_y: int,
                         tile_size: int = 256) -> Dict:
    """
    Generate a regional tile (256x256) biased by continental context.
    
    Returns dict with layers ready for GCO processing.
    """
    # Get continental context
    ctx = get_region_context(world_map, region_x, region_y)
    
    # Create unique seed for this region
    region_seed = hash(f"{world_map.inscription}_{region_x}_{region_y}") & 0xFFFFFFFF
    
    # Generate base structure with regional detail
    structure, seed = core.generate_field(
        region_seed,
        tile_size, tile_size,
        normalize=True,
        octaves=4,  # More detail than continental
        persistence=0.5,
        lacunarity=2.0
    )
    
    # BIAS by continental context
    # Shift local elevation toward continental elevation
    base_elev = ctx['base_elevation']
    structure = structure * 0.6 + base_elev * 0.4
    
    # Get semantic layers
    layers = core.generate_semantic_layers(structure, seed)
    
    # Bias vitality by moisture (wet = more life)
    moisture_boost = ctx['moisture'] - 0.5  # -0.5 to +0.5
    layers['Vitality'] = np.clip(layers['Vitality'] + moisture_boost * 0.3, 0, 1)
    
    return {
        'layers': layers,
        'context': ctx,
        'seed': seed
    }


def demo_world_with_regions():
    """
    Demo: Generate a world and zoom into specific regions.
    """
    import neo_gco as gco
    import neo_biomes as biomes
    
    inscription = "INTERESSENCE"
    
    # 1. Generate continental map
    world = generate_continental_map(inscription, width=512, height=256)
    visualize_continental_map(world, show_layers=True)
    
    # 2. Pick interesting regions to zoom into
    regions_to_sample = [
        (20, 10),   # Should be varied
        (40, 15),   # Different area
        (30, 20),   # Another spot
    ]
    
    fig, axes = plt.subplots(1, len(regions_to_sample), figsize=(18, 6))
    fig.suptitle(f"Regional Tiles from {inscription}", fontsize=16, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    for i, (rx, ry) in enumerate(regions_to_sample):
        # Generate region
        result = generate_region_tile(world, rx, ry)
        layers = result['layers']
        ctx = result['context']
        
        # Run GCO (no erosion for speed)
        context = gco.ClosureContext(layers=layers, seed=result['seed'])
        operator = gco.GlobalClosureOperator(context)
        gco_result = operator.run(enable_hydraulic_erosion=False)
        
        # Classify biomes
        classifier = biomes.BiomeClassifier(n_biomes=6, seed=result['seed'])
        biome_map = classifier.fit_predict(layers)
        
        # Generate texture
        rgb = biomes.generate_biome_texture(biome_map, classifier, gco_result.overlay)
        
        ax = axes[i]
        ax.imshow(rgb)
        ax.set_title(f"Region ({rx},{ry})\n{ctx['dominant_biome']}", color='white')
        ax.axis('off')
    
    filename = os.path.join(OUTPUT_DIR, f"regions_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


def main():
    # Run the demo
    demo_world_with_regions()


if __name__ == "__main__":
    main()

