# Minimal Neo Noise prototype visualization
# This creates a 2D grid where each cell samples local "glyph biases"
# and computes a simple interaction/closure score, visualized as an image.

import numpy as np
import matplotlib.pyplot as plt

# Grid size
WIDTH, HEIGHT = 80, 80
SEED = 42
np.random.seed(SEED)

# Define a very small glyph basis
# orientation encoded as integers for simplicity
# 0=right, 1=left, 2=cross, 3=diagonal, 4=backslash
glyph_orientations = np.array([0, 1, 2, 3, 4])
glyph_magnitudes = np.array([1, 2, 3, 4, 5])

# Deterministic hash-like assignment from coordinates
def glyph_at(x, y):
    idx = (x * 73856093 ^ y * 19349663 ^ SEED) % len(glyph_orientations)
    mag = ((x * 83492791 + y * 297657976) % 5) + 1
    return glyph_orientations[idx], mag

# Simple interaction heuristic
def interaction_score(glyphs):
    # glyphs: list of (orientation, magnitude)
    score = 0
    for i in range(len(glyphs)):
        for j in range(i + 1, len(glyphs)):
            o1, m1 = glyphs[i]
            o2, m2 = glyphs[j]
            delta = abs(m1 - m2)
            
            # Orientation-based bias
            if o1 == o2:
                score += 1.5
            elif (o1 + o2) % 2 == 0:
                score += 0.5
            else:
                score -= 0.5
            
            # Magnitude influence (steepness, not dominance)
            score += delta * 0.2
    return score

# Generate Neo Noise field
field = np.zeros((HEIGHT, WIDTH))

for y in range(HEIGHT):
    for x in range(WIDTH):
        local_glyphs = []
        # Sample a small neighborhood
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    local_glyphs.append(glyph_at(nx, ny))
        field[y, x] = interaction_score(local_glyphs)

# Normalize for visualization
field = (field - field.min()) / (field.max() - field.min())

# Visualize
plt.figure(figsize=(6, 6))
plt.imshow(field)
plt.title("Minimal Neo Noise Prototype")
plt.axis("off")
plt.show()
