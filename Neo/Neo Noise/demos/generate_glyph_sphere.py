"""
Generate a spherical mesh with glyph strokes on its surface.
Maps the 2D glyph grid onto a UV sphere and extrudes glyph marks as geometry.
"""

import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import neo_noise_core as core
import neo_reading as reading


def spherical_to_cartesian(theta: float, phi: float, radius: float = 1.0):
    """Convert spherical coords (theta=azimuth, phi=polar) to cartesian."""
    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.cos(phi)
    z = radius * math.sin(phi) * math.sin(theta)
    return x, y, z


def generate_uv_sphere(radius: float, segments: int, rings: int):
    """Generate a UV sphere mesh."""
    vertices = []
    faces = []
    uvs = []
    
    # Top pole
    vertices.append((0, radius, 0))
    uvs.append((0.5, 1.0))
    
    # Middle rings
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        v = 1.0 - ring / rings
        
        for seg in range(segments):
            theta = 2 * math.pi * seg / segments
            u = seg / segments
            
            x, y, z = spherical_to_cartesian(theta, phi, radius)
            vertices.append((x, y, z))
            uvs.append((u, v))
    
    # Bottom pole
    vertices.append((0, -radius, 0))
    uvs.append((0.5, 0.0))
    
    # Top cap faces
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        faces.append((0, 1 + seg, 1 + next_seg))
    
    # Middle ring faces
    for ring in range(rings - 2):
        ring_start = 1 + ring * segments
        next_ring_start = 1 + (ring + 1) * segments
        
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            
            v1 = ring_start + seg
            v2 = ring_start + next_seg
            v3 = next_ring_start + next_seg
            v4 = next_ring_start + seg
            
            faces.append((v1, v2, v3, v4))
    
    # Bottom cap faces
    bottom = len(vertices) - 1
    last_ring_start = 1 + (rings - 2) * segments
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        faces.append((bottom, last_ring_start + next_seg, last_ring_start + seg))
    
    return vertices, faces, uvs


def uv_to_spherical(u: float, v: float):
    """Convert UV coords to spherical angles."""
    theta = 2 * math.pi * u
    phi = math.pi * (1 - v)
    return theta, phi


def add_glyph_stroke_on_sphere(vertices: list, faces: list, 
                                x1: float, y1: float, x2: float, y2: float,
                                radius: float, stroke_width: float = 0.01):
    """
    Add a glyph stroke as geometry on the sphere surface.
    Coords are in UV space (0-1).
    """
    base_idx = len(vertices)
    
    # Convert endpoints to spherical
    theta1, phi1 = uv_to_spherical(x1, y1)
    theta2, phi2 = uv_to_spherical(x2, y2)
    
    # Get 3D positions slightly above surface
    outer_radius = radius * 1.02  # Raised above surface
    
    p1 = spherical_to_cartesian(theta1, phi1, outer_radius)
    p2 = spherical_to_cartesian(theta2, phi2, outer_radius)
    
    # Get surface positions
    s1 = spherical_to_cartesian(theta1, phi1, radius)
    s2 = spherical_to_cartesian(theta2, phi2, radius)
    
    # Create a thin quad (extruded line)
    vertices.extend([s1, s2, p2, p1])
    faces.append((base_idx, base_idx + 1, base_idx + 2, base_idx + 3))


def generate_glyph_sphere(inscription: str, radius: float = 10.0,
                           glyph_radius: float = 10.5,  # Outer shell for glyphs
                           segments: int = 64, rings: int = 32,
                           cell_size: int = 14, output_dir: str = None):
    """
    Generate two separate meshes:
    1. Base sphere (inner core)
    2. Glyph layer (outer shell with strokes only)
    
    This allows independent editing in Blender.
    """
    _, seed = core.generate_field(inscription, 4, 4)
    
    # Generate base sphere
    sphere_verts, sphere_faces, uvs = generate_uv_sphere(radius, segments, rings)
    print(f"Base sphere: {len(sphere_verts)} vertices, {len(sphere_faces)} faces")
    
    # Generate glyph strokes as separate mesh
    glyph_verts = []
    glyph_faces = []
    
    size = 256  # Virtual UV resolution
    stroke_count = 0
    
    for cy in range(cell_size // 2, size, cell_size):
        for cx in range(cell_size // 2, size, cell_size):
            glyph_type, magnitude = reading.get_glyph_at(seed, cx // 4, cy // 4)
            
            half = cell_size // 2
            mark_len = cell_size // 3
            
            # Convert to UV (0-1)
            u_center = cx / size
            v_center = 1.0 - cy / size  # Flip V
            u_scale = 1 / size
            v_scale = 1 / size
            
            # Add vertical stem
            u1, v1 = u_center, v_center - half * v_scale
            u2, v2 = u_center, v_center + half * v_scale
            add_glyph_stroke_on_sphere(glyph_verts, glyph_faces, u1, v1, u2, v2, glyph_radius)
            stroke_count += 1
            
            # Add marks based on type
            for i in range(magnitude):
                offset_v = -half + int((i + 1) * cell_size / (magnitude + 1))
                v_mark = v_center - offset_v * v_scale
                
                if glyph_type == 'right':
                    add_glyph_stroke_on_sphere(glyph_verts, glyph_faces,
                        u_center, v_mark, 
                        u_center + mark_len * u_scale, v_mark, glyph_radius)
                elif glyph_type == 'left':
                    add_glyph_stroke_on_sphere(glyph_verts, glyph_faces,
                        u_center - mark_len * u_scale, v_mark,
                        u_center, v_mark, glyph_radius)
                elif glyph_type == 'cross':
                    add_glyph_stroke_on_sphere(glyph_verts, glyph_faces,
                        u_center - mark_len * u_scale, v_mark,
                        u_center + mark_len * u_scale, v_mark, glyph_radius)
                elif glyph_type == 'diagonal':
                    add_glyph_stroke_on_sphere(glyph_verts, glyph_faces,
                        u_center - mark_len * u_scale, v_mark - mark_len * v_scale,
                        u_center + mark_len * u_scale, v_mark + mark_len * v_scale, glyph_radius)
                elif glyph_type == 'backslash':
                    add_glyph_stroke_on_sphere(glyph_verts, glyph_faces,
                        u_center - mark_len * u_scale, v_mark + mark_len * v_scale,
                        u_center + mark_len * u_scale, v_mark - mark_len * v_scale, glyph_radius)
                stroke_count += 1
    
    print(f"Glyph layer: {len(glyph_verts)} vertices, {len(glyph_faces)} faces ({stroke_count} strokes)")
    
    # Write OBJ files
    if output_dir:
        # 1. Base sphere
        sphere_path = os.path.join(output_dir, f'sphere_core_{inscription}.obj')
        with open(sphere_path, 'w') as f:
            f.write(f"# Base Sphere Core: {inscription}\n")
            f.write(f"# Radius: {radius}\n")
            f.write(f"o sphere_core_{inscription}\n\n")
            
            for v in sphere_verts:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            f.write("\n")
            for face in sphere_faces:
                if len(face) == 3:
                    f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
                else:
                    f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1} {face[3]+1}\n")
        print(f"Saved: {sphere_path}")
        
        # 2. Glyph layer (separate)
        glyph_path = os.path.join(output_dir, f'sphere_glyphs_{inscription}.obj')
        with open(glyph_path, 'w') as f:
            f.write(f"# Glyph Shell Layer: {inscription}\n")
            f.write(f"# Radius: {glyph_radius}, Seed: {seed}\n")
            f.write(f"o sphere_glyphs_{inscription}\n\n")
            
            for v in glyph_verts:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            f.write("\n")
            for face in glyph_faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1} {face[3]+1}\n")
        print(f"Saved: {glyph_path}")
    
    return sphere_verts, sphere_faces, glyph_verts, glyph_faces


if __name__ == "__main__":
    inscription = "INTERESSENCE"
    output_dir = os.path.join(os.path.dirname(__file__), 
                              '..', 'samples', '3d', 'blender')
    generate_glyph_sphere(inscription, 
                          radius=10.0,       # Core sphere
                          glyph_radius=10.5, # Outer glyph shell
                          output_dir=output_dir)
