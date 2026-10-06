# Neo Rotation and Stroke-Order Analysis

Date: 2026-05-17

## Purpose

This note analyzes what happens when a Neo glyph is rotated while preserving:

- the original glyph identity
- the drawn stem direction
- the drawn mark order
- the directed vector of each mark
- the occupied mark slots

The working question is:

> When a rotated glyph looks like another glyph, is it actually the same glyph?

The short answer is no. A rotated glyph can become projection-equivalent to a primary glyph without becoming inscriptionally identical to it.

## Current Model

The current Neo drawing model differs from traditional centered Ogham in a subtle but important way.

Traditional single-stroke Ogham can be imagined as:

```text
   |
---|
   |
```

Neo single-stroke glyphs are top-biased inside a five-slot lattice:

```text
---|
   |
   |
   |
   |
```

So `B@R180` does not become canonical `H`.

It becomes a left-facing stroke in the lower slot:

```text
   |
   |
   |
   |
|---
```

Canonical `H` is a left-facing stroke in the upper slot:

```text
|---
   |
   |
   |
   |
```

This means `B@R180` is better described as the inverse of `H`, not as `H`.

## Rotation State

A primary glyph can be represented as:

```text
Glyph = {
  letter,
  family,
  magnitude,
  stem_direction,
  mark_order,
  mark_vectors,
  occupied_slots
}
```

For canonical vertical Neo:

```text
stem_direction = T->B
mark_order = 1..n
occupied_slots = top n slots of a five-slot lattice
```

The four 90-degree rotations preserve the stroke sequence but rotate the directed geometry:

| Rotation | Preserved stem direction |
| :--- | :--- |
| `R0` | `T->B` |
| `R90` | `R->L` |
| `R180` | `B->T` |
| `R270` | `L->R` |

This is already enough to separate a rotated glyph from a primary glyph. Even when the visible silhouette matches, the stem direction can differ.

## Projection vs Identity

There are at least three levels of comparison:

| Level | What is compared | Example |
| :--- | :--- | :--- |
| Silhouette | Undirected visible geometry only | `P@R180` looks like `W` |
| Directed projection | Visible geometry plus arrows/order | `P@R180` has reversed stem and mark order |
| Inscriptional identity | Origin plus all preserved residue | `P@R180` remains a derived state of `P` |

So:

```text
P@R180 ~= W    visual match
P@R180 != W    directed identity mismatch
```

This distinction is probably essential. It lets Neo rotation create relations without collapsing identity.

## Slot Law

The top-biased five-slot lattice produces a strong pattern:

```text
canonical count n = top n slots
R180 count n      = bottom n slots
```

Therefore:

- counts `1-4` do not exactly match a primary glyph after `R180`
- count `5` does exactly match a primary glyph after `R180`, because all five slots are occupied

This is the accidental identity-preservation effect you noticed.

For example:

| Glyph | `R180` visual relation | Why |
| :--- | :--- | :--- |
| `B` | inverse of `H` | left-facing, but lower slot |
| `L` | inverse of `D` | left-facing, but lower two slots |
| `F` | inverse of `T` | left-facing, but lower three slots |
| `S` | inverse of `C` | left-facing, but lower four slots |
| `P` | exact silhouette as `W` | all five slots occupied |

This same count rule applies across the other families:

| Family | Counts `1-4` at `R180` | Count `5` at `R180` |
| :--- | :--- | :--- |
| Right | inverse of matching Left glyph | exact silhouette as `W`/`P` counterpart |
| Left | inverse of matching Right glyph | exact silhouette as `P`/`W` counterpart |
| Cross | inverse of same Cross magnitude | exact silhouette as `R` |
| Diagonal | inverse of same Diagonal magnitude | exact silhouette as `I` |
| Backslash | inverse of same Backslash magnitude | exact silhouette as `IO` |

In this model, `inverse` means:

```text
same family relation or counterpart family,
same magnitude,
but occupied slots are inverted through the lattice
```

It is not a new primary glyph unless all five slots are occupied.

## Stroke-Order Law

Preserving stroke order creates another distinction.

Canonical `W` is drawn top-to-bottom:

```text
W@R0:
stem T->B
marks 1 2 3 4 5
screen order 1 2 3 4 5
```

But `P@R180`, even though it has the same silhouette as `W`, preserves `P`'s original draw sequence through rotation:

```text
P@R180:
stem B->T
draw order 1 2 3 4 5
screen order 5 4 3 2 1
mark vectors L L L L L
```

So `P@R180` is not simply `W`. It is:

```text
P-derived / W-shaped / reverse-stem / reverse-screen-order
```

That suggests a useful notation:

```text
P@R180 -> W[derived: stem B->T, screen 54321]
```

Or more compactly:

```text
P@R180 ~= W ; residue(P, B->T, 54321)
```

## Rotation Families

### Right and Left Families

Right/Left are the clearest case because `R180` flips side:

```text
Right@R180 -> Left-shaped
Left@R180  -> Right-shaped
```

But the slot law prevents exact matching except at magnitude `5`.

Pattern:

| Magnitude | Right glyph | `R180` relation |
| :--- | :--- | :--- |
| 1 | `B` | inverse of `H` |
| 2 | `L` | inverse of `D` |
| 3 | `F` | inverse of `T` |
| 4 | `S` | inverse of `C` |
| 5 | `P` | exact silhouette as `W`, but reversed residue |

And the reverse:

| Magnitude | Left glyph | `R180` relation |
| :--- | :--- | :--- |
| 1 | `H` | inverse of `B` |
| 2 | `D` | inverse of `L` |
| 3 | `T` | inverse of `F` |
| 4 | `C` | inverse of `S` |
| 5 | `W` | exact silhouette as `P`, but reversed residue |

### Cross Family

Cross marks are bilateral, so they do not become Right or Left in the same way. But because the marks still occupy top-biased slots, counts `1-4` still invert under `R180`.

Pattern:

| Magnitude | Cross glyph | `R180` relation |
| :--- | :--- | :--- |
| 1 | `M` | inverse of `M` |
| 2 | `G` | inverse of `G` |
| 3 | `N` | inverse of `N` |
| 4 | `Z` | inverse of `Z` |
| 5 | `R` | exact silhouette as `R`, but reversed residue |

This is interesting because the family is self-symmetric in silhouette but not self-identical in directed history.

### Diagonal and Backslash Families

Diagonals preserve or invert flow depending on whether we care about undirected shape or directed stroke vector.

The silhouette may remain diagonal-like, but the vector residue changes.

Pattern:

| Magnitude | Diagonal glyph | `R180` relation |
| :--- | :--- | :--- |
| 1 | `A` | inverse of `A` |
| 2 | `O` | inverse of `O` |
| 3 | `U` | inverse of `U` |
| 4 | `E` | inverse of `E` |
| 5 | `I` | exact silhouette as `I`, but reversed residue |

And:

| Magnitude | Backslash glyph | `R180` relation |
| :--- | :--- | :--- |
| 1 | `AE` | inverse of `AE` |
| 2 | `OI` | inverse of `OI` |
| 3 | `UI` | inverse of `UI` |
| 4 | `EA` | inverse of `EA` |
| 5 | `IO` | exact silhouette as `IO`, but reversed residue |

For diagonals, the word `inverse` may need a more specific term later, because flow direction and slash family can be interpreted differently depending on whether the reader treats a diagonal line as directed or undirected.

## 90-Degree Rotations

In the current vertical-primary atlas, `R90` and `R270` do not exactly match primary glyphs because the stem becomes horizontal:

```text
R90  stem R->L
R270 stem L->R
```

These are still meaningful derived states. They may be the basis for a horizontal Neo register rather than a match to the canonical vertical alphabet.

The screen-order behavior is:

| Rotation | Screen order for multi-mark glyphs |
| :--- | :--- |
| `R0` | `1..n` |
| `R90` | `n..1` |
| `R180` | `n..1` |
| `R270` | `1..n` |

But order along the preserved stem remains the original draw order:

```text
stem-order = 1..n
```

This means there are at least two valid readings:

- screen-order reading: what an observer sees spatially
- stem-order reading: what the glyph remembers procedurally

That distinction may be central to traversal logic.

## Emerging Algorithm

A first-pass rotation classifier could be:

```text
rotate(glyph, r):
  geometry' = rotate all directed segments by r
  stem_direction' = rotate canonical stem direction by r
  mark_vectors' = rotate each mark vector by r
  draw_order' = original draw order
  screen_order' = sort marks by screen position
  stem_order' = sort marks along preserved stem direction
  exact_match = primary glyph with same undirected geometry, if any
  inverse_relation = counterpart glyph with same magnitude and inverted slots, if any
  return derived_rotation_state
```

The derived state should not overwrite the original glyph:

```text
identity = origin + rotation + residue
projection = apparent primary match or inverse relation
```

## Consequences

### 1. Neo accidentally gained rotational memory

The top-biased mark layout prevents most rotated glyphs from collapsing into another primary glyph. This is especially visible in the single-stroke family:

```text
B@R180 != H
B@R180 = inverse(H)
```

This is probably useful. It preserves identity while still creating a relation.

### 2. Maximal glyphs are special

Magnitude `5` occupies the whole lattice, so it erases the slot-asymmetry under `R180`.

That makes maximal glyphs more rotationally permeable:

```text
P@R180 ~= W
W@R180 ~= P
R@R180 ~= R
I@R180 ~= I
IO@R180 ~= IO
```

But even these exact silhouettes preserve stroke-order residue.

So maximal glyphs are visually more symmetric but procedurally still marked.

### 3. Stroke order creates hidden polarity

Two identical silhouettes can encode opposite histories:

```text
W@R0:
  stem T->B
  screen order 12345

P@R180:
  stem B->T
  screen order 54321
```

That gives Neo a way to represent hidden polarity without changing the final visible shape.

### 4. Rotated glyphs may be better treated as operators

A rotated glyph might not be a malformed primary glyph. It may be a primary glyph under a transformation operator:

```text
R180(P) = W-shaped inverse-action residue
```

That makes rotation itself part of the grammar.

## Proposed Terms

These are provisional:

| Term | Meaning |
| :--- | :--- |
| Primary glyph | Canonical unrotated Neo glyph |
| Derived glyph-state | A glyph after rotation while preserving origin/residue |
| Projection-equivalent | Same visible silhouette as a primary glyph |
| Inverse-slot relation | Same counterpart family/magnitude, but slots inverted |
| Residue | Preserved origin, stem direction, mark order, and mark vectors |
| Screen order | Order as seen spatially after rotation |
| Stem order | Order along the preserved directed stem |

## Current Open Questions

1. Should the stem always count as stroke `0` or stroke `1`?
2. Should mark numbers count draw order only, or should they also expose screen order?
3. Should `R90` and `R270` be treated as horizontal Neo glyphs rather than non-primary states?
4. Should diagonal inverse states be named differently from side-family inverse states?
5. Does a projection-equivalent maximal glyph, such as `P@R180 ~= W`, behave more like `P`, more like `W`, or like an interference state between both?

## Working Thesis

Neo rotation appears to produce a two-layer glyph:

```text
surface = what shape the glyph projects as
residue = where the glyph came from and how it was drawn
```

The surface can match another glyph.
The residue does not disappear.

That means rotated glyphs are not aliases. They are transformed states.

This may be the beginning of a real rotation grammar:

```text
primary glyph + rotation = derived glyph-state
derived glyph-state + observer traversal = projected reading
projected reading + residue = full Neo interpretation
```

