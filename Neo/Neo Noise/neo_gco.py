"""
Neo Global Closure Operator (GCO)
The pipeline that turns Neo Noise probability fields into committed World State.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# --- Data Structures ---

@dataclass
class ClosureContext:
    """
    input context for the GCO.
    """
    layers: Dict[str, np.ndarray] # Structure, Flow, Constraint, Vitality
    seed: int
    world_state: Dict = field(default_factory=dict) # Existing features
    
    @property
    def width(self):
        return self.layers['Structure'].shape[1]
    
    @property
    def height(self):
        return self.layers['Structure'].shape[0]

@dataclass
class FeatureCandidate:
    """
    A potential feature identified in the fields.
    """
    type: str # 'river', 'lake', 'forest', 'cliff'
    score: float # How strongly the fields support this
    coordinates: List[Tuple[int, int]] # Pixel path/region
    metadata: Dict = field(default_factory=dict)

@dataclass
class ClosureResult:
    """
    The output of a GCO pass.
    """
    committed_features: List[FeatureCandidate]
    overlay: np.ndarray # Visualization of commitments (0-1 heatmap)

# --- The Operator ---

class GlobalClosureOperator:
    def __init__(self, context: ClosureContext):
        self.ctx = context
        
    def run(self) -> ClosureResult:
        """
        Execute the full Closure Pipeline:
        1. Detect Candidates
        2. Resolve Competition
        3. Commit (Feedback)
        """
        # 1. Detection
        candidates = self.detect_candidates()
        
        # 2. Composition/Competition
        # For this prototype, we just verify they don't overlap blindly, 
        # or we just accept top N.
        # Let's simple filter by score for now.
        committed = self.resolve_competition(candidates)
        
        # 3. Commit (Feedback)
        self.apply_feedback(committed)
        
        # 4. Visualization
        # We generate overlay AFTER feedback, though detecting features was done on PRE-feedback layers.
        # This is fine.
        overlay = self.generate_overlay(committed)
        
        return ClosureResult(committed, overlay)

    def apply_feedback(self, features: List[FeatureCandidate]):
        """
        Modify the underlying layers based on committed features to ensure consistency.
        'History writing'.
        """
        structure = self.ctx.layers['Structure']
        w, h = self.ctx.width, self.ctx.height
        
        print(f"    Applying Feedback (Erosion) to {len(features)} features...")
        
        for feat in features:
            if feat.type == 'river':
                # Erosion
                # Deeper erosion for Major rivers
                width = feat.metadata.get('width', 1.0)
                erosion_base = 0.05 * width # 0.05 for major, 0.025 for minor
                
                # We want to carve a channel
                for x, y in feat.coordinates:
                    current_h = structure[y, x]
                    target_h = max(0.0, current_h - erosion_base)
                    structure[y, x] = target_h
                    
                    # Erode banks slightly (3x3)
                    # This creates the 'Valley' effect
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0: continue
                            ny, nx = y+dy, x+dx
                            if 0 <= ny < h and 0 <= nx < w:
                                # Banks erode less
                                structure[ny, nx] = max(0.0, structure[ny, nx] - (erosion_base * 0.3))
                                
            elif feat.type == 'lake':
                # Flatten Lakes
                coords = feat.coordinates
                if not coords: continue
                
                # Find the lowest point in the lake (the drain)
                # Or just average? Lakes are flat.
                # Usually determined by outlet height.
                # Here, let's just flatten to the min height found in the detected blob.
                min_h = min(structure[y, x] for x, y in coords)
                
                for x, y in coords:
                    structure[y, x] = min_h

    def detect_candidates(self) -> List[FeatureCandidate]:
        """
        Scan layers for all supported feature types.
        """
        candidates = []
        
        # 1. Rivers
        rivers = self.detect_rivers()
        candidates.extend(rivers)
        
        # 2. Lakes (Dependent on Rivers)
        lakes = self.detect_lakes(rivers)
        candidates.extend(lakes)
        
        # 3. Forests (Independent, but spatially competitive)
        forests = self.detect_forests()
        candidates.extend(forests)
        
        return candidates

    def detect_rivers(self) -> List[FeatureCandidate]:
        """
        River logic: High Flow + Low Constraint (Smooth).
        Hierarchical detection:
        1. Major Rivers: High Flow start, long path.
        2. Minor Rivers: Medium Flow start, shorter path OK.
        """
        flow = self.ctx.layers['Flow']
        constraint = self.ctx.layers['Constraint']
        
        candidates = []
        
        # Configuration for Tiers
        TIERS = [
            {'name': 'major', 'flow_thresh': 0.5, 'constraint_max': 0.6, 'min_len': 15, 'weight': 1.0},
            {'name': 'minor', 'flow_thresh': 0.25, 'constraint_max': 0.5, 'min_len': 8, 'weight': 0.5}
        ]
        
        flat_flow = flow.flatten()
        # Scan way more points to find tributaries
        # Top 300 flow points
        top_indices = np.argpartition(flat_flow, -300)[-300:]
        
        potential_starts = 0
        traced_rivers = 0
        
        # Keep track of pixels occupied by rivers to avoid dupes/bundling nearby lines too much
        occupied = np.zeros_like(flow, dtype=bool)
        
        # Sort indices by flow (highest first)
        sorted_indices = top_indices[np.argsort(flat_flow[top_indices])[::-1]]
        
        for idx in sorted_indices:
            y, x = np.unravel_index(idx, flow.shape)
            
            # Skip if already part of a river
            if occupied[y, x]: continue
            
            f_val = flow[y, x]
            c_val = constraint[y, x]
            
            # Determine Tier
            tier = None
            for t in TIERS:
                if f_val >= t['flow_thresh'] and c_val <= t['constraint_max']:
                    tier = t
                    break
            
            if not tier: continue
            
            potential_starts += 1
            
            # Trace River
            path = self._trace_river_downhill(x, y)
            
            if len(path) >= tier['min_len']:
                # Calculate score
                score = np.mean([flow[py, px] for px, py in path])
                
                # Create Candidate
                cand = FeatureCandidate('river', float(score), path)
                cand.metadata['tier'] = tier['name']
                cand.metadata['width'] = tier['weight']
                
                candidates.append(cand)
                traced_rivers += 1
                
                # Mark occupied with a small brush to prevent parallel bundling
                for px, py in path:
                    # Mark 3x3 approx
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = py+dy, px+dx
                            if 0 <= ny < self.ctx.height and 0 <= nx < self.ctx.width:
                                occupied[ny, nx] = True
                
        print(f"    DEBUG: Potential Starts={potential_starts}, Valid Rivers Traced={traced_rivers}")
        return candidates

    def detect_lakes(self, rivers: List[FeatureCandidate]) -> List[FeatureCandidate]:
        """
        Form lakes at the end of rivers that don't reach sea level.
        """
        structure = self.ctx.layers['Structure']
        h, w = self.ctx.height, self.ctx.width
        lakes = []
        visited_global = set()
        
        SEA_LEVEL = 0.2
        
        for river in rivers:
            if not river.coordinates: continue
            
            end_x, end_y = river.coordinates[-1]
            if structure[end_y, end_x] <= SEA_LEVEL:
                continue # Reached sea, no lake
            
            # Check edge of map
            if end_x <= 0 or end_x >= w-1 or end_y <= 0 or end_y >= h-1:
                continue # Flowed off map
                
            # Basin Flood Fill
            # Expand outward from end point until we find a 'spillover' point 
            # (a neighbor lower than current lake level) OR max size.
            # Simplified: Just fill all connected neighbors < threshold? 
            # No, that's just a puddle.
            # Proper basin fill:
            # 1. Start at P. Height H = Structure[P].
            # 2. Find all neighbors >= H. Wait, no.
            # 3. Water accumulates. Level rises.
            # Simplified Logic: Expanding BFS. Add neighbors if Structure[N] < LakeSurfaceHeight.
            # But we don't know surface height.
            
            # Let's use a simple "Puddle" logic:
            # Expand to all connected neighbors that are <= (EndHeight + 0.05)
            # and verify it forms a cup (Constraint usually high around it).
            
            lake_surface = structure[end_y, end_x] + 0.02 # Tiny rise
            queue = [(end_x, end_y)]
            lake_cells = set([(end_x, end_y)])
            
            while queue:
                cx, cy = queue.pop(0)
                
                if len(lake_cells) > 200: break # Max lake size
                
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = cx+dx, cy+dy
                    
                    if 0 <= nx < w and 0 <= ny < h:
                        if (nx, ny) in lake_cells: continue
                        if (nx, ny) in visited_global: continue
                        
                        elev = structure[ny, nx]
                        
                        # If elevation is lower than our "dam" level, it's part of the basin
                        if elev <= lake_surface + 0.05: # Allow slightly higher banks
                             if elev <= lake_surface:
                                 # It's definitely in
                                 lake_cells.add((nx, ny))
                                 queue.append((nx, ny))
                             else:
                                 # Banks associated
                                 pass
            
            if len(lake_cells) > 5:
                lakes.append(FeatureCandidate('lake', 1.0, list(lake_cells)))
                visited_global.update(lake_cells)
                
        return lakes

    def detect_forests(self) -> List[FeatureCandidate]:
        """
        identify forests based on Vitality and Stability.
        """
        vitality = self.ctx.layers['Vitality']
        constraint = self.ctx.layers['Constraint']
        structure = self.ctx.layers['Structure']
        w, h = self.ctx.width, self.ctx.height
        
        forests = []
        
        # Parameters
        VITALITY_MIN = 0.6
        CONSTRAINT_MAX = 0.5 # Can't grow on cliffs
        SEA_LEVEL = 0.2
        
        # Boolean Mask
        mask = (vitality > VITALITY_MIN) & (constraint < CONSTRAINT_MAX) & (structure > SEA_LEVEL)
        
        # extract connected components (blobs) from mask
        # We can implement a simple scan or use scipy if available (not assumed)
        # Using manual grid scan (slow but safe)
        visited = np.zeros_like(mask, dtype=bool)
        
        for y in range(0, h, 2): # Optimization: Skip lines
            for x in range(0, w, 2):
                if mask[y, x] and not visited[y, x]:
                    # Found a new forest blob
                    blob_cells = []
                    queue = [(x, y)]
                    visited[y, x] = True
                    
                    while queue:
                        cx, cy = queue.pop(0)
                        blob_cells.append((cx, cy))
                        
                        # 4-neighbors
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nx, ny = cx+dx, cy+dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if mask[ny, nx] and not visited[ny, nx]:
                                    visited[ny, nx] = True
                                    queue.append((nx, ny))
                                    
                    if len(blob_cells) > 20: # Min forest size
                        # Calculate density score
                        score = np.mean([vitality[cy, cx] for cx, cy in blob_cells])
                        forests.append(FeatureCandidate('forest', float(score), blob_cells))
                        
        return forests

    def _trace_river_downhill(self, start_x, start_y) -> List[Tuple[int, int]]:
        """
        Gradient descent tracer using continuous particle physics to overcome
        pixel-grid local minima.
        """
        structure = self.ctx.layers['Structure']
        h, w = structure.shape
        
        # Calculate gradients lazily (or cache them in context if expensive)
        gy, gx = np.gradient(structure)
        
        path = []
        visited = set()
        
        # Continuous position
        px, py = float(start_x), float(start_y)
        
        # Momentum
        vx, vy = 0.0, 0.0
        inertia = 0.7 # 0.0 = no momentum, 1.0 = infinite slide
        gravity = 0.5 
        
        path.append((int(px), int(py)))
        visited.add((int(px), int(py)))
        
        max_steps = 300
        
        for _ in range(max_steps):
            ix, iy = int(px), int(py)
            
            if not (0 <= ix < w and 0 <= iy < h):
                break
                
            # Sample gradient at current integer position
            # (Inverting because gradient points UPHILL, we want DOWNHILL)
            dx = -gx[iy, ix]
            dy = -gy[iy, ix]
            
            # Normalize gradient force
            mag = np.sqrt(dx*dx + dy*dy)
            if mag < 1e-4:
                # Flat area / Local Minima
                # If we have momentum, we might coast through
                # If momentum is also low, we stop (Lake)
                speed = np.sqrt(vx*vx + vy*vy)
                if speed < 0.1:
                    break
            else:
                dx /= mag
                dy /= mag
            
            # Update velocity
            vx = (vx * inertia) + (dx * gravity)
            vy = (vy * inertia) + (dy * gravity)
            
            # Update position
            px += vx
            py += vy
            
            # Digitize
            nx, ny = int(px), int(py)
            
            if (nx, ny) != (ix, iy):
                # We moved to a new cell
                if not (0 <= nx < w and 0 <= ny < h):
                    break # Flowed off map
                    
                if (nx, ny) in visited:
                    # Loop detected or merging into self
                    break
                    
                path.append((nx, ny))
                visited.add((nx, ny))
                
                # Check height (Sea Level)
                if structure[ny, nx] < 0.2:
                    break
                    
        return path

    def resolve_competition(self, candidates: List[FeatureCandidate]) -> List[FeatureCandidate]:
        """
        Simple greedy acceptance for now.
        Sort by score, accept if not overlapping too much.
        """
        # Sort desc by score
        candidates.sort(key=lambda c: c.score, reverse=True)
        
        committed = []
        occupied_mask = np.zeros((self.ctx.height, self.ctx.width), dtype=bool)
        
        for cand in candidates:
            # Check overlap
            # For rivers, we allow some overlap (merging), but let's just say
            # we don't want identical rivers.
            
            # Simple check: Does this candidate add significant new terrain info?
            # Or just visual check.
            
            committed.append(cand)
            
        return committed

    def generate_overlay(self, features: List[FeatureCandidate]) -> np.ndarray:
        """
        Create a visualization mask (heatmap style).
        0.0 = Empty
        0.3 = Forest
        0.6 = Lake
        0.8 = Minor River
        1.0 = Major River
        """
        overlay = np.zeros((self.ctx.height, self.ctx.width))
        
        # Draw in order of precedence: Forest -> Lake -> River
        # Sort features by type priority
        priority = {'forest': 1, 'lake': 2, 'river': 3}
        features.sort(key=lambda f: priority.get(f.type, 0))
        
        for feat in features:
            val = 0.0
            if feat.type == 'river': 
                # Check Metadata for Tier
                tier = feat.metadata.get('tier', 'major')
                if tier == 'minor':
                    val = 0.8
                else:
                    val = 1.0
            elif feat.type == 'lake': val = 0.6
            elif feat.type == 'forest': val = 0.3
            
            for x, y in feat.coordinates:
                # Simple overwrite for now
                overlay[y, x] = val
                
        return overlay
