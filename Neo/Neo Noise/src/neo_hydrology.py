"""
Neo Hydraulic Erosion System
Particle-based hydraulic erosion simulation for realistic terrain sculpting.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class HydroParams:
    """Parameters for hydraulic erosion simulation."""
    num_droplets: int = 50000       # Number of rain droplets to simulate
    erosion_rate: float = 0.01     # How much terrain is eroded per step (subtle)
    deposition_rate: float = 0.02   # How much sediment is deposited per step
    evaporation_rate: float = 0.01  # Water loss per step
    min_slope: float = 0.001        # Minimum slope for sediment capacity calculation
    max_lifetime: int = 100         # Max steps before droplet dies
    inertia: float = 0.3            # How much momentum is preserved (0 = none, 1 = full)
    initial_water: float = 1.0      # Starting water volume per droplet
    initial_speed: float = 1.0      # Starting speed
    gravity: float = 10.0           # Downhill acceleration
    sediment_capacity_factor: float = 4.0  # Multiplier for sediment carrying capacity
    erosion_radius: int = 2         # Radius of erosion/deposition brush
    # Bedrock constraint (NEW)
    bedrock_depth_factor: float = 0.3  # How deep below initial surface bedrock sits (0-1)
                                        # Low constraint = deep bedrock (0.4), High constraint = shallow (0.1)


@dataclass
class HydroResult:
    """Result of hydraulic erosion simulation."""
    heightmap: np.ndarray           # Eroded heightmap
    accumulation: np.ndarray        # Water accumulation map (for river detection)
    sediment: np.ndarray            # Sediment deposition map
    erosion_map: np.ndarray         # Where erosion occurred


class Droplet:
    """A single water droplet particle."""
    def __init__(self, x: float, y: float, params: HydroParams):
        self.x = x
        self.y = y
        self.dx = 0.0  # Direction x
        self.dy = 0.0  # Direction y
        self.speed = params.initial_speed
        self.water = params.initial_water
        self.sediment = 0.0
        self.lifetime = 0
        self.alive = True


class HydraulicSimulator:
    """
    Particle-based hydraulic erosion simulator.
    
    Algorithm:
    1. Spawn droplets randomly across terrain
    2. Each droplet moves downhill following gradient
    3. Droplet erodes terrain if carrying < capacity
    4. Droplet deposits sediment if carrying > capacity
    5. Water evaporates, droplet eventually dies
    """
    
    def __init__(self, heightmap: np.ndarray, params: HydroParams = None, seed: int = None,
                 constraint_layer: np.ndarray = None):
        """
        Initialize hydraulic erosion simulator.
        
        Args:
            heightmap: Initial terrain heights (0-1 normalized)
            params: Erosion parameters
            seed: Random seed for reproducibility
            constraint_layer: Optional constraint layer (0-1). High values = hard rock,
                              low values = soft soil. Used to compute bedrock floor.
        """
        self.heightmap = heightmap.copy().astype(np.float64)
        self.original_heightmap = heightmap.copy().astype(np.float64)  # For bedrock calc
        self.params = params or HydroParams()
        self.seed = seed
        self.h, self.w = heightmap.shape
        
        # Compute bedrock floor from constraint layer
        # Bedrock = original_surface - depth_factor * (1 - constraint)
        # High constraint = hard rock = shallow bedrock (can't erode much)
        # Low constraint = soft soil = deep bedrock (can erode more)
        if constraint_layer is not None:
            # Constraint-aware bedrock: soft areas allow deeper erosion
            softness = 1.0 - np.clip(constraint_layer, 0, 1)
            max_erosion_depth = self.params.bedrock_depth_factor * softness
            self.bedrock = self.original_heightmap - max_erosion_depth
        else:
            # Default: uniform minimum depth (15% below surface)
            self.bedrock = self.original_heightmap - 0.15
        
        # Ensure bedrock doesn't go below 0
        self.bedrock = np.maximum(self.bedrock, 0.0)
        
        # Tracking maps
        self.accumulation = np.zeros_like(heightmap, dtype=np.float64)
        self.erosion_map = np.zeros_like(heightmap, dtype=np.float64)
        self.sediment_map = np.zeros_like(heightmap, dtype=np.float64)
        
        # RNG
        self.rng = np.random.default_rng(seed)
        
    def _get_gradient(self, x: float, y: float) -> Tuple[float, float, float]:
        """
        Get terrain gradient at position using bilinear interpolation.
        Returns (grad_x, grad_y, height_at_position).
        """
        # Clamp coordinates
        x = max(0.0, min(x, self.w - 1.001))
        y = max(0.0, min(y, self.h - 1.001))
        
        # Integer coordinates
        x0, y0 = int(x), int(y)
        x1, y1 = min(x0 + 1, self.w - 1), min(y0 + 1, self.h - 1)
        
        # Fractional part
        fx, fy = x - x0, y - y0
        
        # Heights at corners
        h00 = self.heightmap[y0, x0]
        h10 = self.heightmap[y0, x1]
        h01 = self.heightmap[y1, x0]
        h11 = self.heightmap[y1, x1]
        
        # Bilinear interpolation for height
        height = (h00 * (1 - fx) * (1 - fy) +
                  h10 * fx * (1 - fy) +
                  h01 * (1 - fx) * fy +
                  h11 * fx * fy)
        
        # Gradient (finite differences)
        grad_x = (h10 - h00) * (1 - fy) + (h11 - h01) * fy
        grad_y = (h01 - h00) * (1 - fx) + (h11 - h10) * fx
        
        return grad_x, grad_y, height
    
    def _deposit(self, x: float, y: float, amount: float):
        """Deposit sediment at position using erosion brush."""
        # Simple single-cell deposit for now
        ix, iy = int(x), int(y)
        if 0 <= ix < self.w and 0 <= iy < self.h:
            self.heightmap[iy, ix] += amount
            self.sediment_map[iy, ix] += amount
    
    def _erode(self, x: float, y: float, amount: float) -> float:
        """
        Erode terrain at position using erosion brush.
        Returns actual amount eroded (may be less if hitting bedrock).
        
        Bedrock constraint: Cannot erode below the bedrock floor, which is
        computed from the constraint layer. This forces water to spread
        laterally when hitting hard rock, creating longer river networks.
        """
        ix, iy = int(x), int(y)
        if not (0 <= ix < self.w and 0 <= iy < self.h):
            return 0.0
        
        current = self.heightmap[iy, ix]
        bedrock_floor = self.bedrock[iy, ix]
        
        # Can only erode down to bedrock, not below
        max_possible_erosion = max(0, current - bedrock_floor)
        actual_erosion = min(amount, max_possible_erosion)
        
        self.heightmap[iy, ix] -= actual_erosion
        self.erosion_map[iy, ix] += actual_erosion
        
        return actual_erosion
    
    def _simulate_droplet(self, start_x: float, start_y: float):
        """Simulate a single water droplet."""
        p = self.params
        
        x, y = start_x, start_y
        dx, dy = 0.0, 0.0
        speed = p.initial_speed
        water = p.initial_water
        sediment = 0.0
        
        for step in range(p.max_lifetime):
            # Check bounds
            if x < 0 or x >= self.w - 1 or y < 0 or y >= self.h - 1:
                break
                
            ix, iy = int(x), int(y)
            
            # Get gradient
            gx, gy, old_height = self._get_gradient(x, y)
            
            # Update direction (with inertia)
            dx = dx * p.inertia - gx * (1 - p.inertia)
            dy = dy * p.inertia - gy * (1 - p.inertia)
            
            # Normalize direction
            length = np.sqrt(dx * dx + dy * dy)
            if length < 1e-8:
                # Random direction if flat
                angle = self.rng.random() * 2 * np.pi
                dx, dy = np.cos(angle), np.sin(angle)
                length = 1.0
            else:
                dx /= length
                dy /= length
            
            # Move droplet
            new_x = x + dx
            new_y = y + dy
            
            # Check new position bounds
            if new_x < 0 or new_x >= self.w - 1 or new_y < 0 or new_y >= self.h - 1:
                break
            
            # Get new height
            _, _, new_height = self._get_gradient(new_x, new_y)
            height_diff = new_height - old_height
            
            # Record water flow for accumulation
            self.accumulation[iy, ix] += water
            
            # Calculate sediment capacity
            # Capacity increases with speed and slope, decreases at flat areas
            slope = max(-height_diff, p.min_slope)
            capacity = slope * speed * water * p.sediment_capacity_factor
            
            # Erosion vs Deposition
            if sediment > capacity or height_diff > 0:
                # Deposit sediment (carrying too much OR going uphill)
                if height_diff > 0:
                    # Going uphill - deposit enough to fill the hole
                    deposit_amount = min(sediment, height_diff)
                else:
                    # Carrying too much - deposit excess
                    deposit_amount = (sediment - capacity) * p.deposition_rate
                
                deposit_amount = min(deposit_amount, sediment)
                sediment -= deposit_amount
                self._deposit(x, y, deposit_amount)
            else:
                # Erode terrain (have capacity to carry more)
                erode_amount = min((capacity - sediment) * p.erosion_rate, -height_diff)
                eroded = self._erode(x, y, erode_amount)
                sediment += eroded
            
            # Update speed
            # Speed increases going downhill, decreases going uphill
            speed = np.sqrt(max(0.01, speed * speed + height_diff * p.gravity))
            
            # Evaporate water
            water *= (1 - p.evaporation_rate)
            
            # Move to new position
            x, y = new_x, new_y
            
            # Die if too little water
            if water < 0.01:
                break
        
        # Deposit remaining sediment
        if sediment > 0 and 0 <= int(x) < self.w and 0 <= int(y) < self.h:
            self._deposit(x, y, sediment)
    
    def simulate(self, progress_callback=None) -> HydroResult:
        """
        Run the full hydraulic erosion simulation.
        
        Args:
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            HydroResult with eroded heightmap and accumulation map
        """
        print(f"    Running Hydraulic Erosion ({self.params.num_droplets} droplets)...")
        
        report_interval = self.params.num_droplets // 10
        
        for i in range(self.params.num_droplets):
            # Random spawn position
            x = self.rng.random() * (self.w - 1)
            y = self.rng.random() * (self.h - 1)
            
            self._simulate_droplet(x, y)
            
            # Progress update
            if progress_callback and i % report_interval == 0:
                progress_callback(i, self.params.num_droplets)
        
        # Normalize accumulation for visualization
        if self.accumulation.max() > 0:
            self.accumulation = self.accumulation / self.accumulation.max()
        
        print(f"    Erosion complete. Max erosion depth: {self.erosion_map.max():.4f}")
        
        return HydroResult(
            heightmap=self.heightmap,
            accumulation=self.accumulation,
            sediment=self.sediment_map,
            erosion_map=self.erosion_map
        )


# Quick test
if __name__ == "__main__":
    import neo_noise_core as core
    import matplotlib.pyplot as plt
    
    print("Testing Hydraulic Erosion...")
    
    # Generate test terrain
    structure, seed = core.generate_field("MOUNTAIN", 128, 128, normalize=True, octaves=4)
    
    print(f"Original terrain: min={structure.min():.3f}, max={structure.max():.3f}")
    
    # Run erosion with subtle parameters
    params = HydroParams(
        num_droplets=20000,  # Fewer for quick test
        erosion_rate=0.01,   # Subtle
        deposition_rate=0.02
    )
    
    simulator = HydraulicSimulator(structure, params, seed=seed)
    result = simulator.simulate()
    
    print(f"Eroded terrain: min={result.heightmap.min():.3f}, max={result.heightmap.max():.3f}")
    print(f"Total erosion: {result.erosion_map.sum():.4f}")
    print(f"Total deposition: {result.sediment.sum():.4f}")
    
    # Visualize
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    
    axes[0, 0].imshow(structure, cmap='terrain')
    axes[0, 0].set_title('Original')
    
    axes[0, 1].imshow(result.heightmap, cmap='terrain')
    axes[0, 1].set_title('Eroded')
    
    axes[1, 0].imshow(result.accumulation, cmap='Blues')
    axes[1, 0].set_title('Water Accumulation')
    
    axes[1, 1].imshow(result.erosion_map, cmap='Reds')
    axes[1, 1].set_title('Erosion Map')
    
    plt.tight_layout()
    plt.savefig('samples/hydrology_test.png')
    print("Saved: samples/hydrology_test.png")
