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
        
    def run(self, enable_hydraulic_erosion: bool = True) -> ClosureResult:
        """
        Execute the full Closure Pipeline in Stages:
        0. Hydraulic Erosion (Optional - sculpts terrain, generates water accumulation)
        1. Hydrology (Rivers, Lakes)
        2. Hydration Feedback (Water -> Vitality)
        3. Ecology (Forests)
        4. Commitment (Final erosion)
        """
        print("    Running Sequential Closure Pipeline...")
        all_committed = []
        
        # --- Stage 0: Hydraulic Erosion (Pre-Pass) ---
        if enable_hydraulic_erosion:
            self.run_hydraulic_erosion()
        
        # --- Stage 1: Hydrology ---
        hydro_candidates = []
        rivers = self.detect_rivers()
        hydro_candidates.extend(rivers)
        # Lakes depend on rivers
        lakes = self.detect_lakes(rivers)
        hydro_candidates.extend(lakes)
        
        # Resolve Hydro competition
        hydro_committed = self.resolve_competition(hydro_candidates)
        all_committed.extend(hydro_committed)
        
        # --- Stage 2: Feedback (Hydration & Erosion) ---
        # 1. Erosion: Rivers carve the land (physically)
        self.apply_feedback(hydro_committed)
        
        # 2. Hydration: Water boosts Vitality (ecologically)
        self.apply_hydration(hydro_committed)
        
        # --- Stage 3: Ecology ---
        # Now that Vitality is boosted near rivers, detecting forests will find 'Oases'.
        eco_candidates = self.detect_forests()
        
        # Resolve Eco competition (Forests usually don't overlap rivers due to logic, but good to check)
        eco_committed = self.resolve_competition(eco_candidates)
        all_committed.extend(eco_committed)
        
        # --- Stage 4: Final Output ---
        
        # We generate overlay from ALL features
        overlay = self.generate_overlay(all_committed)
        
        return ClosureResult(all_committed, overlay)
    
    def run_hydraulic_erosion(self):
        """
        Run particle-based hydraulic erosion on the Structure layer.
        This sculpts the terrain realistically and generates a water accumulation map.
        """
        from neo_hydrology import HydraulicSimulator, HydroParams
        
        # Use subtle erosion parameters
        params = HydroParams(
            num_droplets=50000,
            erosion_rate=0.01,      # Subtle erosion
            deposition_rate=0.02,
            evaporation_rate=0.01,
            inertia=0.3
        )
        
        simulator = HydraulicSimulator(
            self.ctx.layers['Structure'],
            params,
            seed=self.ctx.seed
        )
        
        result = simulator.simulate()
        
        # Update Structure with eroded heightmap
        self.ctx.layers['Structure'] = result.heightmap
        
        # Store water accumulation for river detection
        self.ctx.layers['WaterAccumulation'] = result.accumulation

    def apply_hydration(self, features: List[FeatureCandidate]):
        """
        Boost Vitality layer near water features.
        """
        vitality = self.ctx.layers['Vitality']
        w, h = self.ctx.width, self.ctx.height
        
        print(f"    Applying Hydration to {len(features)} water features...")
        
        # Create a hydration mask
        hydration_boost = np.zeros_like(vitality)
        
        # Parameters
        RIVER_BOOST = 0.4
        LAKE_BOOST = 0.5
        RADIUS = 3 # Pixel radius for hydration
        
        for feat in features:
            boost_val = 0.0
            if feat.type == 'river': boost_val = RIVER_BOOST
            elif feat.type == 'lake': boost_val = LAKE_BOOST
            else: continue
            
            for x, y in feat.coordinates:
                # Simple box blur / radius spread
                for dy in range(-RADIUS, RADIUS+1):
                    for dx in range(-RADIUS, RADIUS+1):
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < h and 0 <= nx < w:
                            # Distance falloff?
                            dist = np.sqrt(dx*dx + dy*dy)
                            if dist <= RADIUS:
                                factor = 1.0 - (dist / (RADIUS + 1))
                                current = hydration_boost[ny, nx]
                                # Keep max hydration
                                hydration_boost[ny, nx] = max(current, boost_val * factor)
        
        # Apply mask to Vitality
        # Clip to 1.0
        # self.ctx.layers['Vitality'] = np.clip(vitality + hydration_boost, 0, 1) # In-place update?
        # Actually numpy add is distinct.
        self.ctx.layers['Vitality'] = np.clip(vitality + hydration_boost, 0.0, 1.0)

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
        River logic: Combine Flow AND WaterAccumulation for best results.
        - Flow provides gradient direction (where water would go)
        - WaterAccumulation provides magnitude (how much water collects)
        """
        flow = self.ctx.layers['Flow']
        constraint = self.ctx.layers['Constraint']
        
        # Combine Flow with WaterAccumulation if available
        if 'WaterAccumulation' in self.ctx.layers:
            accum = self.ctx.layers['WaterAccumulation']
            # Normalize both to 0-1 range
            flow_norm = (flow - flow.min()) / (flow.max() - flow.min() + 1e-8)
            accum_norm = (accum - accum.min()) / (accum.max() - accum.min() + 1e-8)
            # Combined score: weighted sum
            river_score = flow_norm * 0.4 + accum_norm * 0.6
            print("    Using combined Flow + WaterAccumulation for river detection")
        else:
            river_score = (flow - flow.min()) / (flow.max() - flow.min() + 1e-8)
            print("    Using Flow layer only for river detection")
            
        # Phase 1 tuning v2: Middle ground (98% was too tight)
        major_thresh = np.percentile(river_score, 96)  # Top 4%
        minor_thresh = np.percentile(river_score, 88)  # Top 12%
        
        candidates = []
        
        # Configuration for Tiers - balanced constraints
        TIERS = [
            {'name': 'major', 'flow_thresh': major_thresh, 'constraint_max': 0.55, 'min_len': 30, 'weight': 1.0},
            {'name': 'minor', 'flow_thresh': minor_thresh, 'constraint_max': 0.45, 'min_len': 15, 'weight': 0.5}
        ]
        
        flat_flow = river_score.flatten()
        # Scan top 500 flow points to find more river starts
        n_candidates = min(500, len(flat_flow) - 1)
        top_indices = np.argpartition(flat_flow, -n_candidates)[-n_candidates:]
        
        potential_starts = 0
        traced_rivers = 0
        
        # Keep track of pixels occupied by rivers to avoid dupes/bundling nearby lines too much
        occupied = np.zeros_like(river_score, dtype=bool)
        
        # Sort indices by river_score (highest first)
        sorted_indices = top_indices[np.argsort(flat_flow[top_indices])[::-1]]
        
        for idx in sorted_indices:
            y, x = np.unravel_index(idx, river_score.shape)
            
            # Skip if already part of a river
            if occupied[y, x]: continue
            
            f_val = river_score[y, x]
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
                # Calculate score based on river_score along path
                score = np.mean([river_score[py, px] for px, py in path])
                
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
        Realistic river tracer: follow gradient downhill until reaching sea level
        or a true local minimum (basin). No arbitrary loop detection.
        """
        structure = self.ctx.layers['Structure']
        h, w = structure.shape
        
        # Calculate gradients once
        gy, gx = np.gradient(structure)
        
        path = []
        
        # Continuous position for sub-pixel movement
        px, py = float(start_x), float(start_y)
        
        # Momentum for coasting through minor flat areas
        vx, vy = 0.0, 0.0
        inertia = 0.85  # High inertia = rivers meander
        gravity = 0.4
        
        # Track last few positions to detect true stagnation (not loops)
        last_height = structure[int(py), int(px)]
        stagnant_steps = 0
        
        path.append((int(px), int(py)))
        
        max_steps = 1000  # Generous limit for long rivers
        sea_level = 0.08  # Rivers end at coastline
        
        for step in range(max_steps):
            ix, iy = int(px), int(py)
            
            # Boundary check
            if not (0 <= ix < w and 0 <= iy < h):
                break  # Flowed off map edge
                
            current_height = structure[iy, ix]
            
            # Stop at sea level (coastline)
            if current_height < sea_level:
                break
            
            # Get gradient (downhill direction)
            dx = -gx[iy, ix]
            dy = -gy[iy, ix]
            
            mag = np.sqrt(dx*dx + dy*dy)
            
            if mag > 1e-8:
                # Normalize gradient
                dx /= mag
                dy /= mag
            else:
                # True flat area - check if this is a local minimum (basin)
                # A basin is lower than all 8 neighbors
                is_basin = True
                for ndy in [-1, 0, 1]:
                    for ndx in [-1, 0, 1]:
                        if ndx == 0 and ndy == 0:
                            continue
                        nix, niy = ix + ndx, iy + ndy
                        if 0 <= nix < w and 0 <= niy < h:
                            if structure[niy, nix] < current_height:
                                is_basin = False
                                break
                    if not is_basin:
                        break
                
                if is_basin:
                    break  # True basin - river ends here (becomes lake)
            
            # Update velocity with momentum
            vx = vx * inertia + dx * gravity
            vy = vy * inertia + dy * gravity
            
            # Move
            px += vx
            py += vy
            
            nx, ny = int(px), int(py)
            
            # Did we actually move to a new cell?
            if (nx, ny) != (ix, iy):
                if not (0 <= nx < w and 0 <= ny < h):
                    break  # Off map
                
                new_height = structure[ny, nx]
                
                # Check if we're making downhill progress
                if new_height >= last_height:
                    stagnant_steps += 1
                    if stagnant_steps > 50:  # Increased from 20 - allow more flat traversal
                        # Not going downhill - stuck
                        break
                else:
                    stagnant_steps = 0
                    last_height = new_height
                
                path.append((nx, ny))
                
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
