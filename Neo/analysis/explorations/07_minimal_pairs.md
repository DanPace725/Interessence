# Task 7: Minimal Pair Studies

Minimal-pair word families test how sharply small spelling changes move a Neo signature. This is the microscope pass after the broader controlled syntax test.

All words run with `--missing canonical`.

## Family Summary

| Family | Base | Members | Avg pair cosine | Avg pair Euclid | Most moved from base |
| :--- | :--- | :--- | :--- | :--- | :--- |
| gate_family | GATE | 5 | +0.810 | 0.456 | FATE (0.556) |
| light_family | LIGHT | 4 | +0.801 | 0.389 | RIGHT (0.423) |
| stone_family | STONE | 4 | +0.823 | 0.347 | STORM (0.546) |
| break_family | BREAK | 3 | +0.842 | 0.330 | BREATHE (0.373) |
| care_family | CARE | 4 | +0.991 | 0.078 | CIRCE (0.109) |

Mean Euclidean movement for one-edit pairs: **0.357**

## Per-Family Detail

### break_family

| Word | Edit from base | Cos from base | Euclid from base | Dominant | Chord |
| :--- | :--- | :--- | :--- | :--- | :--- |
| BREAK | 0 | +1.000 | 0.000 | `Anchor` | (-0.29, +0.44, +0.00, +0.27) |
| BREAD | 1 | +0.943 | 0.220 | `Anchor` | (-0.11, +0.56, +0.00, +0.33) |
| BREATHE | 3 | +0.785 | 0.373 | `Anchor` | (-0.12, +0.35, +0.32, +0.21) |

### care_family

| Word | Edit from base | Cos from base | Euclid from base | Dominant | Chord |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CARE | 0 | +1.000 | 0.000 | `Gate` | (-0.35, +0.26, +0.39, +0.00) |
| CURE | 1 | +0.988 | 0.093 | `Gate` | (-0.31, +0.23, +0.46, +0.00) |
| CORE | 1 | +0.997 | 0.049 | `Gate` | (-0.33, +0.25, +0.43, +0.00) |
| CIRCE | 2 | +0.984 | 0.109 | `Dampen` | (-0.38, +0.18, +0.45, +0.00) |

### gate_family

| Word | Edit from base | Cos from base | Euclid from base | Dominant | Chord |
| :--- | :--- | :--- | :--- | :--- | :--- |
| GATE | 0 | +1.000 | 0.000 | `Dampen` | (-0.22, +0.24, +0.54, +0.00) |
| FATE | 1 | +0.731 | 0.556 | `Dampen` | (+0.21, +0.00, +0.79, +0.00) |
| LATE | 1 | +0.836 | 0.552 | `Dampen` | (+0.04, +0.00, +0.96, +0.00) |
| MATE | 1 | +0.982 | 0.132 | `Dampen` | (-0.25, +0.14, +0.61, +0.00) |
| RATE | 1 | +0.916 | 0.255 | `Dampen` | (-0.16, +0.45, +0.39, +0.00) |

### light_family

| Word | Edit from base | Cos from base | Euclid from base | Dominant | Chord |
| :--- | :--- | :--- | :--- | :--- | :--- |
| LIGHT | 0 | +1.000 | 0.000 | `Propel` | (-0.20, +0.18, +0.62, +0.00) |
| NIGHT | 1 | +0.868 | 0.334 | `Gate` | (-0.29, +0.37, +0.35, +0.00) |
| RIGHT | 1 | +0.784 | 0.423 | `Gate` | (-0.24, +0.46, +0.30, +0.00) |
| SIGHT | 1 | +0.893 | 0.325 | `Propel` | (+0.12, +0.20, +0.68, +0.00) |

### stone_family

| Word | Edit from base | Cos from base | Euclid from base | Dominant | Chord |
| :--- | :--- | :--- | :--- | :--- | :--- |
| STONE | 0 | +1.000 | 0.000 | `Gate` | (+0.20, +0.22, +0.59, +0.00) |
| STORE | 1 | +0.981 | 0.127 | `Gate` | (+0.17, +0.32, +0.51, +0.00) |
| STORM | 2 | +0.652 | 0.546 | `Opposition` | (+0.24, +0.58, +0.18, +0.00) |
| STERN | 3 | +0.709 | 0.501 | `Opposition` | (+0.16, +0.59, +0.25, +0.00) |
