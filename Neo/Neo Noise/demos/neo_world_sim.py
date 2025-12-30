"""
Neo World Simulation
A 'Zero-Player Game' to test the game-readiness of the Neo Noise layers.
- Agents spawn in continuous High-Vitality zones (Cites).
- Agents move along High-Flow vectors (Roads/Rivers).
- Agents avoid High-Constraint zones (Cliffs).
"""

import numpy as np
import matplotlib.pyplot as plt
import neo_noise_core as core
import os
import random

OUTPUT_DIR = "samples/simulation"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class Agent:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.path = [(self.x, self.y)]
        self.active = True
        
    def move(self, dx, dy, width, height):
        if not self.active: return
        
        self.x += dx
        self.y += dy
        
        # Bounds check
        if self.x < 0 or self.x >= width-1 or self.y < 0 or self.y >= height-1:
            self.active = False
            return
            
        self.path.append((self.x, self.y))

def run_simulation(inscription, steps=1000, agent_count=50, size=128):
    print(f"Simulating World: '{inscription}'...")
    
    # 1. Generate Layers
    structure, seed = core.generate_field(inscription, size, size, normalize=True)
    
    # Flow (Vector Field)
    grad_y, grad_x = np.gradient(structure)
    # Normalize vectors roughly
    mag = np.sqrt(grad_x**2 + grad_y**2) + 1e-8
    flow_x = grad_x / mag
    flow_y = grad_y / mag
    
    # Constraint (Walls)
    laplacian = np.abs(np.gradient(grad_x, axis=1) + np.gradient(grad_y, axis=0))
    constraint = (laplacian - laplacian.min()) / (laplacian.max() - laplacian.min() + 1e-8)
    
    # Vitality (Spawns)
    vitality = core.evolve_field(structure, steps=15, feed_rate=0.012, decay=0.01)
    vitality = np.clip(vitality, 0, 1)
    
    # Debug Stats
    v_mean = np.mean(vitality)
    v_max = np.max(vitality)
    c_mean = np.mean(constraint)
    print(f"  Vitality: Mean={v_mean:.2f}, Max={v_max:.2f}")
    print(f"  Constraint: Mean={c_mean:.2f}")

    # 2. Spawn Agents
    agents = []
    
    # OLD: Hard threshold (Too strict)
    # potential_spawns = np.argwhere((vitality > 0.6) & (constraint < 0.6))
    
    # NEW: Percentile Method (Always find the best spots)
    # We want High Vitality and Low Constraint.
    # Score = Vitality - Constraint
    score_map = vitality - (constraint * 0.5) 
    
    # Find top 5% of scores
    threshold = np.percentile(score_map, 95)
    potential_spawns = np.argwhere(score_map >= threshold)
    
    print(f"  Found {len(potential_spawns)} valid spawn tiles (Threshold score: {threshold:.2f})")
    
    if len(potential_spawns) == 0:
        # Fallback to pure random if math fails completely (unlikely with percentile)
        print("  WARN: No spans found, falling back to random.")
        potential_spawns = [ [size//2, size//2] ]
        
    for _ in range(agent_count):
        idx = random.randint(0, len(potential_spawns)-1)
        # argwhere returns [y, x]
        y, x = potential_spawns[idx]
        agents.append(Agent(x, y))
        
    # 3. Simulation Loop
    for t in range(steps):
        for agent in agents:
            if not agent.active: continue
            
            ix, iy = int(agent.x), int(agent.y)
            
            # Read local forces
            fx = flow_x[iy, ix]
            fy = flow_y[iy, ix]
            c = constraint[iy, ix]
            
            # Logic:
            # 1. Follow Flow (Path of Least Resistance)
            # 2. Avoid Constraint (Slow down or deflect)
            # 3. Random Wander (Exploration)
            
            # Speed depends on constraint transparency (1 - c)
            speed = 1.0 * (1.0 - c)
            
            # If constraint is too high, essentially stop/block
            if c > 0.8:
                speed = 0.1
                
            # Direction:
            # Mostly follow flow, some wiggle
            dx = (fx * 0.7) + (random.uniform(-0.5, 0.5) * 0.3)
            dy = (fy * 0.7) + (random.uniform(-0.5, 0.5) * 0.3)
            
            agent.move(dx * speed, dy * speed, size, size)
            
    # 4. Visualization
    plt.figure(figsize=(10, 10), facecolor='#0f172a')
    
    # Background: Structure (Terrain)
    plt.imshow(structure, cmap='gray', alpha=0.5, extent=[0, size, size, 0])
    
    # Overlay: Vitality (Green patches)
    # Create an alpha map
    vitality_map = np.zeros((size, size, 4))
    vitality_map[..., 1] = 1.0 # Green channel
    vitality_map[..., 3] = vitality * 0.4 # Alpha based on vitality
    plt.imshow(vitality_map, extent=[0, size, size, 0])
    
    # Overlay: Paths
    for agent in agents:
        path = np.array(agent.path)
        if len(path) > 1:
            # Color paths based on... age? Gold.
            plt.plot(path[:, 0], path[:, 1], color='#f59e0b', linewidth=0.8, alpha=0.6)
            
    # Overlay: Spawns
    start_x = [a.path[0][0] for a in agents]
    start_y = [a.path[0][1] for a in agents]
    plt.scatter(start_x, start_y, color='#ec4899', s=10, zorder=10, label='Spawn')
            
    plt.title(f"Simulated Exploration: {inscription}", color='white', fontsize=16)
    plt.axis('off')
    
    filename = os.path.join(OUTPUT_DIR, f"sim_{inscription}.png")
    plt.savefig(filename, facecolor='#0f172a')
    plt.close()
    print(f"Simulation saved: {filename}")

def main():
    cmds = ["QUEST", "EMPIRE", "DESOLATION"]
    for cmd in cmds:
        # Run for 2000 steps to see long-term trade routes form
        run_simulation(cmd, size=256, steps=2000)

if __name__ == "__main__":
    main()
