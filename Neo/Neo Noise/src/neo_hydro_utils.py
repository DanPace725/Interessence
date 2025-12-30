"""
Neo Hydrology Utilities
Shared functions for physics-based water network generation.

Used by:
- neo_gco.py (for river detection)
- demos/neo_water_network.py (for standalone testing)
"""

import numpy as np
from collections import deque


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


def compute_flow_accumulation(flow_dir: np.ndarray, 
                               moisture_weight: np.ndarray = None) -> np.ndarray:
    """
    Compute flow accumulation using upslope contributing area.
    
    Args:
        flow_dir: D8 flow direction array
        moisture_weight: Optional per-pixel rainfall/moisture contribution (0-1).
    """
    h, w = flow_dir.shape
    
    if moisture_weight is not None:
        accumulation = moisture_weight.astype(np.float32).copy()
    else:
        accumulation = np.ones((h, w), dtype=np.float32)
    
    # Neighbor offsets
    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, 1, 1, 1, 0, -1, -1, -1]
    
    # Build dependency count
    in_degree = np.zeros((h, w), dtype=np.int32)
    
    for y in range(h):
        for x in range(w):
            d = flow_dir[y, x]
            if d >= 0:
                nx, ny = x + dx[d], y + dy[d]
                if 0 <= nx < w and 0 <= ny < h:
                    in_degree[ny, nx] += 1
    
    # Process in topological order
    queue = deque()
    for y in range(h):
        for x in range(w):
            if in_degree[y, x] == 0:
                queue.append((x, y))
    
    while queue:
        x, y = queue.popleft()
        d = flow_dir[y, x]
        
        if d >= 0:
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < w and 0 <= ny < h:
                accumulation[ny, nx] += accumulation[y, x]
                in_degree[ny, nx] -= 1
                if in_degree[ny, nx] == 0:
                    queue.append((nx, ny))
    
    return accumulation


def compute_ocean_mask(heightmap: np.ndarray, sea_level: float) -> np.ndarray:
    """
    Ocean = connected to map edge AND below sea level.
    
    This prevents inland seas by requiring ocean cells to be connected
    to the world boundary via flood-fill.
    """
    h, w = heightmap.shape
    ocean = np.zeros((h, w), dtype=bool)
    queue = deque()
    
    # Seed from edge cells below sea level
    for x in range(w):
        if heightmap[0, x] < sea_level:
            ocean[0, x] = True
            queue.append((x, 0))
        if heightmap[h-1, x] < sea_level:
            ocean[h-1, x] = True
            queue.append((x, h-1))
    
    for y in range(h):
        if heightmap[y, 0] < sea_level:
            ocean[y, 0] = True
            queue.append((0, y))
        if heightmap[y, w-1] < sea_level:
            ocean[y, w-1] = True
            queue.append((w-1, y))
    
    # Flood fill
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
    Compute net runoff = precipitation - infiltration.
    
    This implements the water budget: R(x,y) - L(x,y)
    - Precipitation comes from vitality (lush areas get more rain)
    - Infiltration comes from inverse constraint (soft soil absorbs water)
    """
    # Precipitation: base + vitality bonus
    precipitation = rainfall_base + vitality_layer * (1.0 - rainfall_base)
    
    # Infiltration: low constraint = soft soil = high infiltration
    infiltration = (1.0 - constraint_layer) * infiltration_rate
    
    # Net runoff (clamp to 0)
    net_runoff = np.maximum(precipitation - infiltration, 0.0)
    
    return net_runoff
