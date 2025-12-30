"""
Emergent Water Network System
Let water flow naturally downhill and form rivers/lakes without manual control.

Algorithm:
1. Compute flow direction at every pixel (steepest descent)
2. Compute flow accumulation (how much upstream area drains through each pixel)
3. Rivers = threshold on accumulation
4. Lakes = basins (local minima) that collect water
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Dict
import matplotlib.pyplot as plt


@dataclass  
class WaterNetwork:
    """Result of emergent water network generation."""
    heightmap: np.ndarray           # Terrain
    flow_direction: np.ndarray      # D8 direction at each pixel (0-7)
    accumulation: np.ndarray        # Flow accumulation (upstream drainage area)
    river_mask: np.ndarray          # Boolean: is this pixel a river?
    lake_mask: np.ndarray           # Boolean: is this pixel a lake?
    river_order: np.ndarray         # Strahler order (1=headwater, higher=bigger river)


def compute_flow_direction(heightmap: np.ndarray) -> np.ndarray:
    """
    Compute D8 flow direction for each pixel.
    Direction is encoded as 0-7 (8 neighbors) or -1 for flat/pit.
    
    Directions:
        5 6 7
        4 x 0
        3 2 1
    """
    h, w = heightmap.shape
    flow_dir = np.full((h, w), -1, dtype=np.int8)
    
    # Neighbor offsets: E, SE, S, SW, W, NW, N, NE
    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, 1, 1, 1, 0, -1, -1, -1]
    # Distance weight (diagonal = sqrt(2))
    dist = [1.0, 1.414, 1.0, 1.414, 1.0, 1.414, 1.0, 1.414]
    
    for y in range(h):
        for x in range(w):
            current_h = heightmap[y, x]
            steepest_slope = 0
            steepest_dir = -1
            
            for d in range(8):
                nx, ny = x + dx[d], y + dy[d]
                if 0 <= nx < w and 0 <= ny < h:
                    drop = current_h - heightmap[ny, nx]
                    slope = drop / dist[d]
                    if slope > steepest_slope:
                        steepest_slope = slope
                        steepest_dir = d
            
            flow_dir[y, x] = steepest_dir
    
    return flow_dir


def compute_flow_accumulation(flow_dir: np.ndarray, moisture_weight: np.ndarray = None) -> np.ndarray:
    """
    Compute flow accumulation using upslope contributing area.
    
    Args:
        flow_dir: D8 flow direction array
        moisture_weight: Optional per-pixel rainfall/moisture contribution (0-1).
                        If None, all pixels contribute 1.0 (uniform rainfall).
                        Use Vitality layer to simulate more rain in lush areas.
    """
    h, w = flow_dir.shape
    
    # Initial contribution per pixel (rainfall)
    if moisture_weight is not None:
        accumulation = moisture_weight.astype(np.float32).copy()
    else:
        accumulation = np.ones((h, w), dtype=np.float32)
    
    # Neighbor offsets
    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, 1, 1, 1, 0, -1, -1, -1]
    
    # Build dependency count (how many pixels flow INTO each pixel)
    in_degree = np.zeros((h, w), dtype=np.int32)
    
    for y in range(h):
        for x in range(w):
            d = flow_dir[y, x]
            if d >= 0:
                nx, ny = x + dx[d], y + dy[d]
                if 0 <= nx < w and 0 <= ny < h:
                    in_degree[ny, nx] += 1
    
    # Process in topological order (start from sources with in_degree=0)
    queue = []
    for y in range(h):
        for x in range(w):
            if in_degree[y, x] == 0:
                queue.append((x, y))
    
    while queue:
        x, y = queue.pop(0)
        d = flow_dir[y, x]
        
        if d >= 0:
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < w and 0 <= ny < h:
                accumulation[ny, nx] += accumulation[y, x]
                in_degree[ny, nx] -= 1
                if in_degree[ny, nx] == 0:
                    queue.append((nx, ny))
    
    return accumulation


def find_lakes(heightmap: np.ndarray, flow_dir: np.ndarray) -> np.ndarray:
    """
    Find lakes as pixels that are local minima (flow_dir == -1) 
    plus connected flat regions.
    """
    h, w = heightmap.shape
    lake_mask = np.zeros((h, w), dtype=bool)
    
    # A lake forms at pits (no outflow)
    pits = flow_dir == -1
    
    # Expand pits into lakes via flood fill at same height
    visited = np.zeros((h, w), dtype=bool)
    
    for y in range(h):
        for x in range(w):
            if pits[y, x] and not visited[y, x]:
                # Flood fill this basin
                pit_height = heightmap[y, x]
                queue = [(x, y)]
                lake_cells = []
                
                while queue:
                    cx, cy = queue.pop(0)
                    if visited[cy, cx]:
                        continue
                    visited[cy, cx] = True
                    
                    # Include if at or below pit + small tolerance
                    if heightmap[cy, cx] <= pit_height + 0.01:
                        lake_cells.append((cx, cy))
                        
                        # Check neighbors
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx]:
                                if heightmap[ny, nx] <= pit_height + 0.02:
                                    queue.append((nx, ny))
                
                # Mark lake cells
                for lx, ly in lake_cells:
                    lake_mask[ly, lx] = True
    
    return lake_mask


def compute_ocean_mask(heightmap: np.ndarray, sea_level: float) -> np.ndarray:
    """
    Phase 2: Ocean = connected to map edge AND below sea level.
    
    This prevents inland seas by requiring ocean cells to be connected
    to the world boundary via flood-fill.
    
    Args:
        heightmap: 2D terrain array
        sea_level: Elevation threshold for ocean
        
    Returns:
        Boolean mask where True = ocean (connected to edge)
    """
    h, w = heightmap.shape
    ocean = np.zeros((h, w), dtype=bool)
    
    # Use collections.deque for efficient queue operations
    from collections import deque
    queue = deque()
    
    # Seed from all edge cells below sea level
    # Top and bottom edges
    for x in range(w):
        if heightmap[0, x] < sea_level:
            ocean[0, x] = True
            queue.append((x, 0))
        if heightmap[h-1, x] < sea_level:
            ocean[h-1, x] = True
            queue.append((x, h-1))
    
    # Left and right edges
    for y in range(h):
        if heightmap[y, 0] < sea_level:
            ocean[y, 0] = True
            queue.append((0, y))
        if heightmap[y, w-1] < sea_level:
            ocean[y, w-1] = True
            queue.append((w-1, y))
    
    # Flood fill to connected low cells
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if not ocean[ny, nx] and heightmap[ny, nx] < sea_level:
                    ocean[ny, nx] = True
                    queue.append((nx, ny))
    
    return ocean


def compute_net_runoff(vitality_layer: np.ndarray,
                       constraint_layer: np.ndarray,
                       rainfall_base: float = 0.15,
                       infiltration_rate: float = 0.25) -> np.ndarray:
    """
    Phase 2: Compute net runoff = precipitation - infiltration.
    
    This implements the water budget: R(x,y) - L(x,y)
    - Precipitation comes from vitality (lush areas get more rain)
    - Infiltration/loss comes from inverse constraint (soft soil absorbs water)
    
    Args:
        vitality_layer: High = more rainfall (0-1)
        constraint_layer: High = rock/hard surface, Low = soil (0-1)
        rainfall_base: Minimum rainfall everywhere (0-1)
        infiltration_rate: How much soft soil absorbs (0-1)
        
    Returns:
        Net runoff per cell (can be 0 where infiltration > precipitation)
    """
    h, w = vitality_layer.shape
    
    # Precipitation: base + vitality bonus
    precipitation = rainfall_base + vitality_layer * (1.0 - rainfall_base)
    
    # Infiltration: low constraint = soft soil = high infiltration
    # High constraint = rock = low infiltration
    infiltration = (1.0 - constraint_layer) * infiltration_rate
    
    # Net runoff (clamp to 0 - can't have negative water)
    net_runoff = np.maximum(precipitation - infiltration, 0.0)
    
    print(f"  Precipitation range: {precipitation.min():.3f} - {precipitation.max():.3f}")
    print(f"  Infiltration range: {infiltration.min():.3f} - {infiltration.max():.3f}")
    print(f"  Net runoff range: {net_runoff.min():.3f} - {net_runoff.max():.3f}")
    
    return net_runoff


def generate_water_network(heightmap: np.ndarray, 
                           constraint_layer: np.ndarray = None,
                           vitality_layer: np.ndarray = None,
                           river_threshold_percentile: float = 95,
                           min_catchment_area: int = 50,
                           min_lake_size: int = 10,
                           sea_level: float = 0.1,
                           evaporation_factor: float = 0.3,
                           rainfall_base: float = 0.3,
                           infiltration_rate: float = 0.25,
                           use_edge_ocean: bool = True) -> WaterNetwork:
    """
    Generate a complete water network from terrain with realistic constraints.
    
    Args:
        heightmap: 2D terrain array (0-1 normalized)
        constraint_layer: Optional constraint layer (high = rock, low = soil)
        vitality_layer: Optional vitality layer (high = more rainfall/moisture source)
        river_threshold_percentile: Accumulation percentile for river classification
        min_catchment_area: Minimum pixels of upstream area to be a river
        min_lake_size: Minimum pixels for a lake to be shown
        sea_level: Elevation below which is ocean (not rivers)
        evaporation_factor: How much constraint reduces water after accumulation (0-1)
        rainfall_base: Base rainfall for all pixels (0-1)
        infiltration_rate: Phase 2 - How much soft soil absorbs water (0-1)
        use_edge_ocean: Phase 2 - Require ocean to be connected to map edge
        
    Returns:
        WaterNetwork with all computed layers
    """
    h, w = heightmap.shape
    
    print("Computing flow directions...")
    flow_dir = compute_flow_direction(heightmap)
    
    # Phase 2: Compute net runoff with infiltration if we have both layers
    if vitality_layer is not None and constraint_layer is not None:
        print("Computing net runoff (Phase 2: precipitation - infiltration)...")
        net_runoff = compute_net_runoff(
            vitality_layer, 
            constraint_layer,
            rainfall_base=rainfall_base,
            infiltration_rate=infiltration_rate
        )
        moisture = net_runoff
    elif vitality_layer is not None:
        # Fallback: just vitality-weighted rainfall
        moisture = rainfall_base + vitality_layer * (1.0 - rainfall_base)
        print(f"Using vitality-weighted rainfall (base={rainfall_base})")
    else:
        moisture = None  # Uniform rainfall
    
    print("Computing flow accumulation...")
    accumulation = compute_flow_accumulation(flow_dir, moisture_weight=moisture)
    
    # Apply additional evaporation loss (post-accumulation)
    if constraint_layer is not None:
        retention = 1.0 - (constraint_layer * evaporation_factor)
        accumulation = accumulation * retention
        print(f"Applied post-accumulation evaporation (factor={evaporation_factor})")
    
    print("Identifying lakes...")
    lake_mask = find_lakes(heightmap, flow_dir)
    
    # CONSTRAINT 1: Minimum lake size
    if min_lake_size > 1:
        from scipy import ndimage
        labeled_lakes, n_lakes = ndimage.label(lake_mask)
        for lake_id in range(1, n_lakes + 1):
            lake_size = np.sum(labeled_lakes == lake_id)
            if lake_size < min_lake_size:
                lake_mask[labeled_lakes == lake_id] = False
        print(f"Filtered lakes: {n_lakes} -> {ndimage.label(lake_mask)[1]} (min size={min_lake_size})")
    
    # Phase 2: Ocean with edge-connectivity (prevents inland seas)
    if use_edge_ocean:
        print("Computing edge-connected ocean mask (Phase 2)...")
        ocean_mask = compute_ocean_mask(heightmap, sea_level)
    else:
        # Fallback: simple height threshold
        ocean_mask = heightmap < sea_level
    
    # Log-transform accumulation for thresholding
    log_accum = np.log1p(accumulation)
    
    # Rivers = high accumulation
    threshold = np.percentile(log_accum[~ocean_mask], river_threshold_percentile)
    river_mask = log_accum > threshold
    
    # CONSTRAINT 3: Minimum catchment area
    river_mask = river_mask & (accumulation >= min_catchment_area)
    
    # Exclude lakes and ocean from rivers
    river_mask = river_mask & ~lake_mask & ~ocean_mask
    
    # Simple Strahler order approximation based on accumulation value
    river_order = np.zeros_like(accumulation, dtype=np.int8)
    if np.any(river_mask):
        river_order[river_mask] = np.clip(
            np.floor(np.log2(accumulation[river_mask] / min_catchment_area + 1)).astype(np.int8),
            1, 7
        )
    
    print(f"Network complete: {np.sum(river_mask)} river pixels, {np.sum(lake_mask)} lake pixels, {np.sum(ocean_mask)} ocean pixels")
    
    return WaterNetwork(
        heightmap=heightmap,
        flow_direction=flow_dir,
        accumulation=accumulation,
        river_mask=river_mask,
        lake_mask=lake_mask,
        river_order=river_order
    )


def visualize_water_network(network: WaterNetwork, title: str = "Water Network"):
    """Visualize the emergent water network."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle(title, fontsize=14, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    # Terrain
    ax = axes[0, 0]
    ax.imshow(network.heightmap, cmap='terrain', interpolation='bicubic')
    ax.set_title('Terrain', color='white')
    ax.axis('off')
    
    # Flow accumulation (log scale)
    ax = axes[0, 1]
    ax.imshow(np.log1p(network.accumulation), cmap='Blues', interpolation='nearest')
    ax.set_title('Flow Accumulation (log)', color='white')
    ax.axis('off')
    
    # Rivers + Lakes on terrain
    ax = axes[1, 0]
    ax.imshow(network.heightmap, cmap='terrain', interpolation='bicubic')
    # Overlay rivers in blue, lakes in darker blue
    overlay = np.zeros((*network.heightmap.shape, 4))
    overlay[network.river_mask] = [0.2, 0.6, 1.0, 0.8]  # Rivers
    overlay[network.lake_mask] = [0.1, 0.3, 0.7, 0.9]   # Lakes
    ax.imshow(overlay)
    ax.set_title('Rivers & Lakes', color='white')
    ax.axis('off')
    
    # River order (Strahler)
    ax = axes[1, 1]
    order_display = np.where(network.river_order > 0, network.river_order, np.nan)
    ax.imshow(network.heightmap, cmap='Greys', alpha=0.3)
    im = ax.imshow(order_display, cmap='cool', interpolation='nearest', vmin=1, vmax=5)
    ax.set_title('River Order (Strahler)', color='white')
    ax.axis('off')
    
    plt.tight_layout()
    return fig


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import neo_noise_core as core
    
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "samples", "water_network")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Generate terrain
    words = ["RIVER", "MOUNTAIN", "INTERESSENCE"]
    
    for word in words:
        print(f"\n{'='*50}")
        print(f"Generating water network for: {word}")
        print(f"{'='*50}")
        
        # Generate terrain and semantic layers
        structure, seed = core.generate_field(word, 256, 256, normalize=True, octaves=4)
        layers = core.generate_semantic_layers(structure, seed)
        
        # Use Constraint layer for evaporation and Vitality for rainfall source
        constraint = layers.get('Constraint', None)
        vitality = layers.get('Vitality', None)
        
        # EXTREME anti-water test: clamp everything down
        network = generate_water_network(
            structure, 
            constraint_layer=constraint,
            vitality_layer=vitality,
            river_threshold_percentile=99.5, # Only top 0.5% become rivers
            min_catchment_area=500,          # Need 500 pixels upstream!
            min_lake_size=100,               # Min 100 pixels for a lake
            sea_level=0.02,                  # Almost no ocean
            evaporation_factor=0.5,          # 50% evaporation
            rainfall_base=0.05,              # Only 5% base rainfall
            infiltration_rate=0.6,           # 60% soil absorption!
            use_edge_ocean=True
        )
        
        fig = visualize_water_network(network, f"Water Network: {word} (constrained)")
        filename = os.path.join(OUTPUT_DIR, f"water_network_{word}_v2.png")
        fig.savefig(filename, facecolor=fig.get_facecolor(), dpi=120, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")
