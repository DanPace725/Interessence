# Neo Vector Order Matrix

Date: 2026-05-17

## Purpose

This note analyzes Neo glyphs as ordered stroke-vector sequences.

The question is:

> If each stroke is reduced to a vector letter, what patterns appear when glyphs are rotated while preserving stroke order?

This is a separate layer from the rotation/stroke-order analysis. That prior layer preserved exact slot placement and stem residue. This layer intentionally compresses the glyph into a vector sequence.

## Vector Alphabet

The working vector alphabet is:

| Letter | Vector class | Meaning |
| :--- | :--- | :--- |
| `D` | Down | vertical downward stroke |
| `U` | Up | vertical upward stroke |
| `L` | Left | horizontal leftward stroke |
| `R` | Right | horizontal rightward stroke |
| `C` | Cross | bilateral mark crossing the stem |
| `F` | Forward slash | `/` shaped mark |
| `B` | Backslash | `\` shaped mark |

Important limitation: this is a coarse vector alphabet. It treats slash/backslash as visual classes, not fully directed diagonal vectors. If we later need full polarity, `F` and `B` may need signed variants such as `F+`, `F-`, `B+`, and `B-`.

Cross needs one extra rule. A cross stroke has a bilateral shape, but it still has a source-to-target draw direction. So this document uses two-letter cross tokens:

| Token | Meaning |
| :--- | :--- |
| `CR` | cross stroke drawn left-to-right |
| `CL` | cross stroke drawn right-to-left |
| `CD` | cross stroke drawn top-to-bottom after rotation |
| `CU` | cross stroke drawn bottom-to-top after rotation |

In other words, `C` is the structural class, and the second letter is the preserved vector residue.

## Stem Prefix

If the stem is included as a numbered stroke, its preserved direction rotates as:

| Rotation | Stem vector |
| :--- | :--- |
| `R0` | `D` |
| `R90` | `L` |
| `R180` | `U` |
| `R270` | `R` |

So a full vector word can be written as:

```text
stem + marks
```

For example:

```text
B@R0   = D.R
B@R90  = L.D
B@R180 = U.L
B@R270 = R.U
```

The dot separates the stem stroke from mark strokes.

## Family Rotation Matrix

If only the mark strokes are considered, each family rotates through this matrix:

| Family | `R0` | `R90` | `R180` | `R270` |
| :--- | :--- | :--- | :--- | :--- |
| Right | `R` | `D` | `L` | `U` |
| Left | `L` | `U` | `R` | `D` |
| Cross | `CR` | `CD` | `CL` | `CU` |
| Diagonal | `B` | `F` | `B` | `F` |
| Backslash | `F` | `B` | `F` | `B` |

This reveals three different rotation behaviors:

1. Right/Left form a four-state directional cycle.
2. Cross preserves bilateral structure while carrying a four-state direction residue.
3. Diagonal/Backslash form a two-state slash cycle.

## Full Family Matrix With Stem

Including the stem prefix makes the derived state more specific:

| Family | `R0` | `R90` | `R180` | `R270` |
| :--- | :--- | :--- | :--- | :--- |
| Right | `D.R...` | `L.D...` | `U.L...` | `R.U...` |
| Left | `D.L...` | `L.U...` | `U.R...` | `R.D...` |
| Cross | `D.CR...` | `L.CD...` | `U.CL...` | `R.CU...` |
| Diagonal | `D.B...` | `L.F...` | `U.B...` | `R.F...` |
| Backslash | `D.F...` | `L.B...` | `U.F...` | `R.B...` |

The stem prefix is doing real work. Without it, `P@R180` and `W@R0` both reduce to `LLLLL`. With it:

```text
P@R180 = U.LLLLL
W@R0   = D.LLLLL
```

So the stem preserves a polarity that the mark sequence alone loses.

## Full Glyph Table: Mark Vectors Only

| Glyph | Canonical family | `R0` | `R90` | `R180` | `R270` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `B` | Right 1 | `R` | `D` | `L` | `U` |
| `L` | Right 2 | `RR` | `DD` | `LL` | `UU` |
| `F` | Right 3 | `RRR` | `DDD` | `LLL` | `UUU` |
| `S` | Right 4 | `RRRR` | `DDDD` | `LLLL` | `UUUU` |
| `P` | Right 5 | `RRRRR` | `DDDDD` | `LLLLL` | `UUUUU` |
| `H` | Left 1 | `L` | `U` | `R` | `D` |
| `D` | Left 2 | `LL` | `UU` | `RR` | `DD` |
| `T` | Left 3 | `LLL` | `UUU` | `RRR` | `DDD` |
| `C` | Left 4 | `LLLL` | `UUUU` | `RRRR` | `DDDD` |
| `W` | Left 5 | `LLLLL` | `UUUUU` | `RRRRR` | `DDDDD` |
| `M` | Cross 1 | `CR` | `CD` | `CL` | `CU` |
| `G` | Cross 2 | `CR CR` | `CD CD` | `CL CL` | `CU CU` |
| `N` | Cross 3 | `CR CR CR` | `CD CD CD` | `CL CL CL` | `CU CU CU` |
| `Z` | Cross 4 | `CR CR CR CR` | `CD CD CD CD` | `CL CL CL CL` | `CU CU CU CU` |
| `R` | Cross 5 | `CR CR CR CR CR` | `CD CD CD CD CD` | `CL CL CL CL CL` | `CU CU CU CU CU` |
| `A` | Diagonal 1 | `B` | `F` | `B` | `F` |
| `O` | Diagonal 2 | `BB` | `FF` | `BB` | `FF` |
| `U` | Diagonal 3 | `BBB` | `FFF` | `BBB` | `FFF` |
| `E` | Diagonal 4 | `BBBB` | `FFFF` | `BBBB` | `FFFF` |
| `I` | Diagonal 5 | `BBBBB` | `FFFFF` | `BBBBB` | `FFFFF` |
| `AE` | Backslash 1 | `F` | `B` | `F` | `B` |
| `OI` | Backslash 2 | `FF` | `BB` | `FF` | `BB` |
| `UI` | Backslash 3 | `FFF` | `BBB` | `FFF` | `BBB` |
| `EA` | Backslash 4 | `FFFF` | `BBBB` | `FFFF` | `BBBB` |
| `IO` | Backslash 5 | `FFFFF` | `BBBBB` | `FFFFF` | `BBBBB` |

## Full Glyph Table: Stem Plus Marks

| Glyph | `R0` | `R90` | `R180` | `R270` |
| :--- | :--- | :--- | :--- | :--- |
| `B` | `D.R` | `L.D` | `U.L` | `R.U` |
| `L` | `D.RR` | `L.DD` | `U.LL` | `R.UU` |
| `F` | `D.RRR` | `L.DDD` | `U.LLL` | `R.UUU` |
| `S` | `D.RRRR` | `L.DDDD` | `U.LLLL` | `R.UUUU` |
| `P` | `D.RRRRR` | `L.DDDDD` | `U.LLLLL` | `R.UUUUU` |
| `H` | `D.L` | `L.U` | `U.R` | `R.D` |
| `D` | `D.LL` | `L.UU` | `U.RR` | `R.DD` |
| `T` | `D.LLL` | `L.UUU` | `U.RRR` | `R.DDD` |
| `C` | `D.LLLL` | `L.UUUU` | `U.RRRR` | `R.DDDD` |
| `W` | `D.LLLLL` | `L.UUUUU` | `U.RRRRR` | `R.DDDDD` |
| `M` | `D.CR` | `L.CD` | `U.CL` | `R.CU` |
| `G` | `D.CR CR` | `L.CD CD` | `U.CL CL` | `R.CU CU` |
| `N` | `D.CR CR CR` | `L.CD CD CD` | `U.CL CL CL` | `R.CU CU CU` |
| `Z` | `D.CR CR CR CR` | `L.CD CD CD CD` | `U.CL CL CL CL` | `R.CU CU CU CU` |
| `R` | `D.CR CR CR CR CR` | `L.CD CD CD CD CD` | `U.CL CL CL CL CL` | `R.CU CU CU CU CU` |
| `A` | `D.B` | `L.F` | `U.B` | `R.F` |
| `O` | `D.BB` | `L.FF` | `U.BB` | `R.FF` |
| `U` | `D.BBB` | `L.FFF` | `U.BBB` | `R.FFF` |
| `E` | `D.BBBB` | `L.FFFF` | `U.BBBB` | `R.FFFF` |
| `I` | `D.BBBBB` | `L.FFFFF` | `U.BBBBB` | `R.FFFFF` |
| `AE` | `D.F` | `L.B` | `U.F` | `R.B` |
| `OI` | `D.FF` | `L.BB` | `U.FF` | `R.BB` |
| `UI` | `D.FFF` | `L.BBB` | `U.FFF` | `R.BBB` |
| `EA` | `D.FFFF` | `L.BBBB` | `U.FFFF` | `R.BBBB` |
| `IO` | `D.FFFFF` | `L.BBBBB` | `U.FFFFF` | `R.BBBBB` |

## What This Reveals

### 1. Magnitude becomes run length

Under vector compression, the magnitude axis is simply sequence length:

```text
B = R
L = RR
F = RRR
S = RRRR
P = RRRRR
```

This is clean and potentially useful. A glyph family becomes a vector type; magnitude becomes repeated intensity.

### 2. Rotation becomes substitution

Rotation can be described as a substitution table:

```text
R90:
  R -> D
  D -> L
  L -> U
  U -> R
  F -> B
  B -> F
  CR -> CD
  CD -> CL
  CL -> CU
  CU -> CR
```

`R180` is:

```text
R -> L
L -> R
D -> U
U -> D
F -> F
B -> B
CR -> CL
CL -> CR
CD -> CU
CU -> CD
```

`R270` is:

```text
R -> U
U -> L
L -> D
D -> R
F -> B
B -> F
CR -> CU
CU -> CL
CL -> CD
CD -> CR
```

That means a rotation operator can be implemented as a simple vector rewrite over the alphabet.

### 3. Right/Left and Up/Down form one four-cycle

The side families are part of one cyclic directional system:

```text
R -> D -> L -> U -> R
```

So Right and Left are not merely opposites. They are phase positions in a rotational cycle.

This makes the left/right pair look less like a binary and more like a compass orbit.

### 4. Cross is structurally invariant but directionally marked

The cross family should not reduce to plain:

```text
C, CC, CCC, CCCC, CCCCC
```

That notation preserves the bilateral crossing shape, but it loses the left-to-right or right-to-left distinction inherited from the source glyph.

The better notation is:

```text
CR, CR CR, CR CR CR, CR CR CR CR, CR CR CR CR CR
```

under `R0`, with the direction residue rotating as `CR -> CD -> CL -> CU`.

So Cross is invariant only at the structural level:

```text
shape class: C
direction residue: R/D/L/U
```

This matters because `R@R180` can be an exact silhouette match to canonical `R`, but it is not the same directed cross state:

```text
R@R0   = D.CR CR CR CR CR
R@R180 = U.CL CL CL CL CL
```

The shape is self-matching. The source-to-target vector history is reversed.

### 5. Diagonal and Backslash form a two-cycle

The slash families toggle under quarter-turns:

```text
B -> F -> B -> F
F -> B -> F -> B
```

This is different from the four-cycle used by `R/L/D/U`.

That means diagonal glyphs have a lower-period rotation behavior:

```text
R180(B) = B
R180(F) = F
```

At the coarse slash-class level, a 180-degree rotation does not change slash family. But it does reverse stroke polarity if we care about exact directed endpoints.

So the vector alphabet shows a useful fact and hides a dangerous one:

```text
useful: diagonal class survives R180
hidden: diagonal direction reverses under R180
```

### 6. Vector-only identity collapses too much

The mark-only vector table says:

```text
P@R180 = LLLLL
W@R0   = LLLLL
```

That is true as a mark-vector sequence.

But the stem-plus-mark table says:

```text
P@R180 = U.LLLLL
W@R0   = D.LLLLL
```

And the stroke-order analysis says:

```text
P@R180 screen order = 54321
W@R0   screen order = 12345
```

So vector-only analysis identifies projection equivalence, not full identity.

This is probably the right division of labor:

- vector matrix: reveals rotational grammar
- slot/order matrix: preserves glyph identity

## Proposed Programmatic Form

A vector signature can be represented as:

```json
{
  "origin": "P",
  "rotation": 180,
  "stem": "U",
  "marks": "LLLLL",
  "draw_order": "12345",
  "screen_order": "54321"
}
```

The compact notation is:

```text
P@R180 = U.LLLLL {draw:12345, screen:54321}
```

This preserves the benefit of the vector matrix without losing the identity residue.

## Working Thesis

The vector matrix reveals Neo as a small rotational rewrite system:

```text
glyph = vector family repeated by magnitude
rotation = substitution over vector letters
stem = orientation prefix
identity = origin + order residue
```

The most important result is that Neo has at least two simultaneous grammars:

1. A vector grammar, where rotation is clean substitution.
2. A residue grammar, where stroke order and slot position preserve identity.

Those grammars agree sometimes, diverge sometimes, and the divergence is where the interesting Neo behavior probably lives.
