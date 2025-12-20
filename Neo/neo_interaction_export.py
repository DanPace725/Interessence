"""
Neo Interaction Export Script
Generates a CSV file containing all pairwise interactions between Neo glyphs.
"""

import csv
import os
from neo_generator import NEO_ALPHABET, NEO_SIGNALS, AICME_INTERACTIONS

OUTPUT_FILE = 'neo_interactions_v2.csv'

def calculate_interaction(g1_code, g1_data, g2_code, g2_data):
    """
    Calculate interaction metrics between two glyphs.
    """
    # Unpack data: (position, count, name)
    p1, m1, name1 = g1_data
    p2, m2, name2 = g2_data
    
    # 1. Magnitude Logic
    diff = abs(m1 - m2)
    mag_result = ""
    if diff == 0:
        mag_result = "Resonance"
    elif diff == 1:
        mag_result = "Modulation"
    else:
        mag_result = "Dominance"
        
    # 2. Matrix Logic
    interaction_type = AICME_INTERACTIONS[p1][p2]
    
    # 3. Signals
    sig1 = NEO_SIGNALS[name1]['fingerprint']
    sig2 = NEO_SIGNALS[name2]['fingerprint']
    
    return {
        'Glyph A': g1_code,
        'Glyph B': g2_code,
        'Name A': name1,
        'Name B': name2,
        'Group A': p1,
        'Group B': p2,
        'Marks A': m1,
        'Marks B': m2,
        'Magnitude Delta': diff,
        'Magnitude Result': mag_result,
        'Interaction Type': interaction_type,
        'Signal A': sig1,
        'Signal B': sig2
    }

def main():
    print("Generating Neo Interaction data...")
    
    # Get all glyphs (sorted by group/count is nice but not strictly required for CSV)
    # We use the keys from NEO_ALPHABET
    glyphs = list(NEO_ALPHABET.items())
    
    results = []
    
    for g1_code, g1_data in glyphs:
        for g2_code, g2_data in glyphs:
            result = calculate_interaction(g1_code, g1_data, g2_code, g2_data)
            results.append(result)
            
    # Write to CSV
    headers = [
        'Glyph A', 'Glyph B', 'Name A', 'Name B', 
        'Group A', 'Group B', 'Marks A', 'Marks B', 
        'Magnitude Delta', 'Magnitude Result', 'Interaction Type',
        'Signal A', 'Signal B'
    ]
    
    try:
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Successfully exported {len(results)} interactions to {OUTPUT_FILE}")
        print(f"Path: {os.path.abspath(OUTPUT_FILE)}")
        
    except Exception as e:
        print(f"Error writing CSV: {e}")

if __name__ == "__main__":
    main()
