# Task 6: Controlled Syntax Tests

These rows hold syntax almost fixed while swapping the central frame: `THE X OPENS THE Y`, `THE X HOLDS THE Y`, `THE X BREAKS THE Y`, and `THE X WAITS NEAR THE Y`. Each frame uses the same five noun pairs.

All phrases run with `--missing canonical`.

## Frame Cohesion

| Frame | Members | Within-avg cosine | Dominant consensus | Centroid |
| :--- | :--- | :--- | :--- | :--- |
| waits_near | 5 | +0.942 | `Dampen` (5/5) | action_net=-0.280, structure=+0.268, flow=+0.384, transform=+0.068 |
| opens | 5 | +0.909 | `Dampen` (3/5) | action_net=-0.087, structure=+0.240, flow=+0.658, transform=+0.000 |
| breaks | 5 | +0.897 | `Dampen` (4/5) | action_net=-0.233, structure=+0.269, flow=+0.426, transform=+0.072 |
| holds | 5 | +0.885 | `Dampen` (4/5) | action_net=-0.262, structure=+0.176, flow=+0.563, transform=+0.000 |

## Cross-Frame Centroid Cosine

| | breaks | holds | opens | waits_near |
| :--- | :--- | :--- | :--- | :--- |
| **breaks** | +1.00 | +0.96 | +0.92 | +0.99 |
| **holds** | +0.96 | +1.00 | +0.96 | +0.95 |
| **opens** | +0.92 | +0.96 | +1.00 | +0.88 |
| **waits_near** | +0.99 | +0.95 | +0.88 | +1.00 |

High off-diagonal values mean the fixed sentence shell is stronger than the verb/frame distinction. Lower values suggest the frame itself is moving the signature.

## Noun-Pair Stability Across Frames

| Noun pair | Cross-frame avg cosine |
| :--- | :--- |
| fire_wall | +0.936 |
| stone_gate | +0.944 |
| hand_door | +0.945 |
| child_book | +0.946 |
| river_road | +0.967 |

## Per-Frame Detail

### breaks

| Phrase | Dominant | Disrupt | Chord |
| :--- | :--- | :--- | :--- |
| THE HAND BREAKS THE DOOR | Dampen | 2 | (-0.30, +0.31, +0.32, +0.07) |
| THE STONE BREAKS THE GATE | Dampen | 2 | (-0.17, +0.24, +0.51, +0.07) |
| THE RIVER BREAKS THE ROAD | Gate | 2 | (-0.13, +0.44, +0.38, +0.06) |
| THE FIRE BREAKS THE WALL | Dampen | 2 | (-0.15, +0.24, +0.53, +0.08) |
| THE CHILD BREAKS THE BOOK | Dampen | 2 | (-0.41, +0.12, +0.40, +0.07) |

### holds

| Phrase | Dominant | Disrupt | Chord |
| :--- | :--- | :--- | :--- |
| THE HAND HOLDS THE DOOR | Dampen | 0 | (-0.34, +0.22, +0.44, +0.00) |
| THE STONE HOLDS THE GATE | Dampen | 0 | (-0.19, +0.14, +0.67, +0.00) |
| THE RIVER HOLDS THE ROAD | Gate | 0 | (-0.14, +0.39, +0.47, +0.00) |
| THE FIRE HOLDS THE WALL | Dampen | 0 | (-0.17, +0.12, +0.71, +0.00) |
| THE CHILD HOLDS THE BOOK | Dampen | 0 | (-0.47, +0.00, +0.53, +0.00) |

### opens

| Phrase | Dominant | Disrupt | Chord |
| :--- | :--- | :--- | :--- |
| THE HAND OPENS THE DOOR | Dampen | 0 | (-0.17, +0.29, +0.54, +0.00) |
| THE STONE OPENS THE GATE | Dampen | 0 | (-0.01, +0.21, +0.78, +0.00) |
| THE RIVER OPENS THE ROAD | Gate | 0 | (-0.00, +0.45, +0.55, +0.00) |
| THE FIRE OPENS THE WALL | Propel | 0 | (+0.04, +0.19, +0.78, +0.00) |
| THE CHILD OPENS THE BOOK | Dampen | 0 | (-0.29, +0.07, +0.64, +0.00) |

### waits_near

| Phrase | Dominant | Disrupt | Chord |
| :--- | :--- | :--- | :--- |
| THE HAND WAITS NEAR THE DOOR | Dampen | 2 | (-0.33, +0.29, +0.31, +0.07) |
| THE STONE WAITS NEAR THE GATE | Dampen | 2 | (-0.24, +0.25, +0.44, +0.07) |
| THE RIVER WAITS NEAR THE ROAD | Dampen | 2 | (-0.19, +0.40, +0.35, +0.06) |
| THE FIRE WAITS NEAR THE WALL | Dampen | 2 | (-0.23, +0.24, +0.45, +0.07) |
| THE CHILD WAITS NEAR THE BOOK | Dampen | 2 | (-0.41, +0.16, +0.36, +0.07) |
