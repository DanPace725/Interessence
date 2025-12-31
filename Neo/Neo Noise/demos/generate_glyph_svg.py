"""
Generate SVG glyph layer from inscription.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import neo_noise_core as core
import neo_reading as reading

def generate_glyph_svg(inscription: str, size: int = 256, cell_size: int = 14,
                       output_path: str = None) -> str:
    """Generate SVG of the glyph layer."""
    _, seed = core.generate_field(inscription, 4, 4)
    
    svg_lines = [
        f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="black"/>',
        '<g stroke="white" stroke-width="1.5" stroke-linecap="round">'
    ]

    for cy in range(cell_size // 2, size, cell_size):
        for cx in range(cell_size // 2, size, cell_size):
            glyph_type, magnitude = reading.get_glyph_at(seed, cx // 4, cy // 4)
            half = cell_size // 2
            mark_len = cell_size // 3
            
            # Vertical stem (subtle)
            svg_lines.append(f'  <line x1="{cx}" y1="{cy-half}" x2="{cx}" y2="{cy+half}" stroke-opacity="0.3"/>')
            
            # Draw marks based on type
            for i in range(magnitude):
                offset_y = -half + int((i + 1) * cell_size / (magnitude + 1))
                py = cy + offset_y
                
                if glyph_type == 'right':
                    svg_lines.append(f'  <line x1="{cx}" y1="{py}" x2="{cx+mark_len}" y2="{py}"/>')
                elif glyph_type == 'left':
                    svg_lines.append(f'  <line x1="{cx}" y1="{py}" x2="{cx-mark_len}" y2="{py}"/>')
                elif glyph_type == 'cross':
                    svg_lines.append(f'  <line x1="{cx-mark_len}" y1="{py}" x2="{cx+mark_len}" y2="{py}"/>')
                elif glyph_type == 'diagonal':
                    svg_lines.append(f'  <line x1="{cx-mark_len}" y1="{py+mark_len}" x2="{cx+mark_len}" y2="{py-mark_len}"/>')
                elif glyph_type == 'backslash':
                    svg_lines.append(f'  <line x1="{cx-mark_len}" y1="{py-mark_len}" x2="{cx+mark_len}" y2="{py+mark_len}"/>')

    svg_lines.append('</g>')
    svg_lines.append('</svg>')
    
    svg_content = '\n'.join(svg_lines)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(svg_content)
        print(f"Saved: {output_path}")
    
    return svg_content


if __name__ == "__main__":
    inscription = "INTERESSENCE"
    output = os.path.join(os.path.dirname(__file__), 
                          '..', 'samples', '3d', 'blender', 
                          f'glyph_layer_{inscription}.svg')
    generate_glyph_svg(inscription, output_path=output)
