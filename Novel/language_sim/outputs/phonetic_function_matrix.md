# Phonetic Function Matrix

This experiment maps consonant manners and current IW onsets onto Neo-style operations.

It is deliberately provisional. It tests whether sound can carry functional pressure before the later Neo glyph system formalizes those pressures as Aicme, magnitude, pairwise interference, and multiglyph chord logic.

Local Neo anchors used for this experiment:

- `../../Neo/docs/Neo_Reference_Table.md`: glyph group, orientation, magnitude, and structural bias.
- `../../Neo/Neo Signals/Pairwise_Interference_Logic.md`: Aicme interaction matrix and intensity rules.
- `../../Neo/Neo Signals/Multi_Glyph_Logic.md`: chord vectors and position weighting.

## Manner To Function

| Manner | English consonants | IW function | Neo-role hypothesis | Possible use |
|---|---|---|---|---|
| Stops / plosives | p, b, t, d, k, g | closure followed by release; pressure crossing a boundary | action or resistance; voiced/back stops may bind | warnings, tool acts, doors, cuts, starts, refusals |
| Fricatives | f, v, th, dh, s, z, sh, zh, h | continuous contact; pressure that can be heard before it breaks | action when directed; resistance when breathy; mutation when noisy | abrasion, danger, taboo breath, erosion, soft force |
| Affricates | ch, j | stop released into friction | action + mutation | trigger events, sparks, snapped changes |
| Nasals | m, n, ng | closed-mouth continuity; carried relation inside the body | binding | memory, kinship, inside/outside, held obligations |
| Approximants | w, r, y | near-contact without closure; glide, approach, carried transition | flow or binding; w is treated as a glide emerging around vowel pairs | routes, water, social approach, names that should move easily |
| Lateral approximant | l | side-channel flow around an obstruction | action softened toward flow | paths, speech smoothing, negotiated movement |
| Liquids | l, r | posture that remains flexible while carrying structure | action + binding, often flow-adjacent in early IW | law, lineage, rivers, repeated practice |

## Aicme-Style Interaction Matrix

Read this as a sound-function matrix: if one onset role meets another, the pair inherits the corresponding Neo-style operation.

| Role | Action | Resistance | Binding | Flow | Mutation |
|---|---|---|---|---|---|
| B / Action | Reinforce | Opposition | Anchor | Propel | Distort |
| H / Resistance | Opposition | Reinforce | Anchor | Dampen | Invert |
| M / Binding | Anchor | Anchor | Crystalize | Gate | Fracture |
| A / Flow | Propel | Dampen | Gate | Stream | Turbulence |
| Forfeda / Mutation | Distort | Invert | Fracture | Turbulence | Phase Shift |

## Current Onsets As Functional Sounds

| Onset | Manner | Neo glyph route | Primary role | Chord vector | Dominant field | Pair reading |
|---|---|---|---|---|---|---|
| `br` | stop + liquid cluster | B Beith (1, action), R Ruis (5, binding) | B / Action | action 1.0, structure 4.5 | structure | dominance anchor: locked state |
| `ch` | affricate | T Tinne (3, resistance), S Sail (4, action) | H / Resistance | action 3.6, resistance 3.0 | action | modulation opposition: tension or balance |
| `dh` | tongue-teeth threshold | D Duir (2, resistance), H Huath (1, resistance) | H / Resistance | resistance 2.9 | resistance | modulation reinforce: aligned pressure |
| `dr` | stop + liquid cluster | D Duir (2, resistance), R Ruis (5, binding) | H / Resistance | resistance 2.0, structure 4.5 | structure | dominance anchor: locked state |
| `f` | fricative | F Fearn (3, action) | B / Action | action 3.0 | action | single-glyph pressure |
| `g` | stop / plosive | G Gort (2, binding) | M / Binding | structure 2.0 | structure | single-glyph pressure |
| `h` | fricative | H Huath (1, resistance) | H / Resistance | resistance 1.0 | resistance | single-glyph pressure |
| `k` | stop / plosive | C Coll (4, resistance) | H / Resistance | resistance 4.0 | resistance | single-glyph pressure |
| `l` | lateral approximant / liquid | L Luis (2, action) | B / Action | action 2.0 | action | single-glyph pressure |
| `m` | nasal | M Muin (1, binding) | M / Binding | structure 1.0 | structure | single-glyph pressure |
| `n` | nasal | N Ngeadal (3, binding) | M / Binding | structure 3.0 | structure | single-glyph pressure |
| `p` | stop / plosive | P Peith (5, action) | B / Action | action 5.0 | action | single-glyph pressure |
| `r` | approximant / liquid | R Ruis (5, binding) | M / Binding | structure 5.0 | structure | single-glyph pressure |
| `s` | fricative | S Sail (4, action) | B / Action | action 4.0 | action | single-glyph pressure |
| `sh` | fricative | S Sail (4, action) | B / Action | action 4.0 | action | single-glyph pressure |
| `t` | stop / plosive | T Tinne (3, resistance) | H / Resistance | resistance 3.0 | resistance | single-glyph pressure |
| `th` | tongue-teeth threshold | T Tinne (3, resistance), H Huath (1, resistance) | H / Resistance | resistance 3.9 | resistance | dominance reinforce: aligned pressure |
| `v` | fricative | F Fearn (3, action) | B / Action | action 3.0 | action | single-glyph pressure |
| `z` | fricative | Z Straif (4, binding) | M / Binding | structure 4.0 | structure | single-glyph pressure |

## Cluster Probes

Clusters are the most useful test case because they let an early sound act like a tiny Neo inscription.

| Cluster | Glyph sequence | Pairwise operation | Chord reading | Naming implication |
|---|---|---|---|---|
| `br` | B Beith (1, action) + R Ruis (5, binding) | dominance anchor: locked state | action 1.0, structure 4.5; dominant structure | A good candidate for names about vows, bridges, bloodlines, carried force, or action becoming structure. |
| `ch` | T Tinne (3, resistance) + S Sail (4, action) | modulation opposition: tension or balance | action 3.6, resistance 3.0; dominant action | A possible specialist or fossilized cluster. |
| `dh` | D Duir (2, resistance) + H Huath (1, resistance) | modulation reinforce: aligned pressure | resistance 2.9; dominant resistance | A possible specialist or fossilized cluster. |
| `dr` | D Duir (2, resistance) + R Ruis (5, binding) | dominance anchor: locked state | resistance 2.0, structure 4.5; dominant structure | A good candidate for gates, laws, patient endurance, difficult craft, or resistance becoming structure. |
| `th` | T Tinne (3, resistance) + H Huath (1, resistance) | dominance reinforce: aligned pressure | resistance 3.9; dominant resistance | A good candidate for thresholds, taboo edges, not-yet-safe matter, or boundary restraint. |

## What Happens

- The current onset inventory is already biased toward action, resistance, and binding. That fits the world premise: survival speech begins with pressure, refusal, and relation before abstract flow is formalized.
- `br` and `dr` become especially interesting. They are not just hard clusters; they read as action/resistance entering binding, which makes them plausible for names tied to vows, gates, craft, law, and load-bearing social forms.
- `th` now carries the threshold family as reinforced resistance. That makes it useful for danger-remains, taboo edges, and boundaries that must be tested before crossing.
- `w` has moved out of the root-onset set and into glide behavior around vowel pairs. It can still fossilize later, but it should not currently anchor a consonant root.
- Vowels may be the main carriers of flow and mutation in early IW. Consonants set posture and contact; vowel contours decide whether the posture releases, holds, or transforms.

## Next Experiment

Use the vowel combination grid as the nucleus layer: onset function + vowel contour + optional coda. That would let `brua`, `drei`, `thae`, or `shao` produce a small Neo-like field profile without yet becoming a formal glyph string.
