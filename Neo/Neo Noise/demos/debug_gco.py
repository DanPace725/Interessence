"""
Debug script for GCO
"""
import neo_noise_core as core
import neo_gco as gco
import numpy as np

def debug_run():
    print("--- GCO DEBUG RUN ---")
    
    # 1. Generate Layers
    seed_str = "RIVER" # This seed SHOULD have rivers!
    size = 128
    print(f"Generating field for '{seed_str}' ({size}x{size})...")
    
    structure, seed = core.generate_field(seed_str, size, size, normalize=True)
    layers = core.generate_semantic_layers(structure, seed)
    
    flow = layers['Flow']
    constraint = layers['Constraint']
    print(f"Layer Stats:")
    print(f"  Flow: Min={flow.min():.3f}, Max={flow.max():.3f}, Mean={flow.mean():.3f}")
    print(f"  Constraint: Min={constraint.min():.3f}, Max={constraint.max():.3f}, Mean={constraint.mean():.3f}")
    
    # 2. Run GCO
    print("\nInitializing GCO...")
    context = gco.ClosureContext(layers=layers, seed=seed)
    operator = gco.GlobalClosureOperator(context)
    
    # Manually run detection to debug
    print("\nRunning River Detection...")
    candidates = operator.detect_rivers()
    
    print(f"\nCandidates Found: {len(candidates)}")
    for i, c in enumerate(candidates[:5]):
        print(f"  [{i}] Score={c.score:.3f}, Len={len(c.coordinates)}")
        # Print first few points
        print(f"      Start: {c.coordinates[0]} -> End: {c.coordinates[-1]}")

    if not candidates:
        print("\nDIAGNOSIS: No candidates found.")
        # Check thresholds
        FLOW_THRESHOLD = 0.5
        CONSTRAINT_MAX = 0.6
        
        flat_flow = flow.flatten()
        top_indices = np.argpartition(flat_flow, -50)[-50:]
        print("\nChecking Top 5 Flow Points:")
        for idx in top_indices[-5:]:
            y, x = np.unravel_index(idx, flow.shape)
            f_val = flow[y, x]
            c_val = constraint[y, x]
            print(f"  ({x},{y}) Flow={f_val:.3f}, Constr={c_val:.3f}")
            if f_val < FLOW_THRESHOLD: print("    -> FAIL: Flow too low")
            if c_val > CONSTRAINT_MAX: print("    -> FAIL: Constraint too high")
            
            # Try tracing anyway to see length
            path = operator._trace_river_downhill(x, y)
            print(f"    -> Trace Length: {len(path)}")

if __name__ == "__main__":
    debug_run()
