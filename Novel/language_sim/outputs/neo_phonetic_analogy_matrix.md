# Neo Phonetic Analogy Matrix

This experiment asks what each phonetic manner is in Neo terms.

The mapping is not `sound = glyph`. It is `speech event = Neo interaction pattern`. A plosive is therefore not simply `P`; it is a closure-and-release event that can be modeled through operations like Opposition, Anchor, Propel, and Fracture.

## Manner Analogies

| Phonetic manner | Speech event | Neo interaction analog | Neo reading | Likely glyph families | Naming tendency |
|---|---|---|---|---|---|
| Stops / plosives | complete closure, pressure buildup, then release | Opposition -> Anchor -> Propel -> Fracture | a blocked force that becomes an event | B/H for pressure and refusal; M when closure is held; A or Forfeda when release crosses the boundary | starts, cuts, gates, warnings, tools, vows that begin under pressure |
| Fricatives | narrowed passage with continuous noisy flow | Dampen -> Distort -> Turbulence | flow under constraint, audible abrasion, or noisy mutation | H for constriction; B for directed hiss; Forfeda when the noise bends or mutates the field | erosion, danger, taboo breath, warning, soft force, weathered surfaces |
| Tongue-teeth threshold | tongue held at the teeth while breath crosses a boundary | Opposition -> Dampen -> Gate | a boundary held in the mouth before permission or refusal | H for restraint; M when the threshold becomes a gate; Forfeda when crossing changes the state | thresholds, taboos, old heat, tests of safety, edge-law |
| Affricates | closure released into friction | Gate -> Fracture -> Distort -> Turbulence | a stop-event whose release becomes noisy transformation | M/H for closed gate; B for burst; Forfeda for the fricative tail | sparks, snapped changes, ritual triggers, dangerous thresholds |
| Nasals | oral closure with sound rerouted through the body | Anchor -> Gate -> Stream | a held relation that finds an alternate passage | M for binding; A for rerouted flow; H when the mouth closure is emphasized | memory, kinship, interiority, carrying, obligation, hidden continuity |
| Approximants | near-contact without full closure | Stream -> Propel -> Gate | guided transition without hard separation | A for glide; B for directional approach; M when the glide becomes relation | routes, water, approach, social movement, flexible names |
| Lateral approximant | central obstruction with side-channel release | Dampen -> Gate -> Stream | flow moves around resistance instead of breaking it | H for obstruction; M for valve; A for side flow | paths, negotiations, side routes, cleverness, speech smoothing |
| Liquids | flexible resonance that bends without fully closing | Gate -> Stream -> Anchor | structure that stays mobile | M for relational hold; A for flow; B when the liquid carries action forward | law, lineage, rivers, repeated practice, flexible social forms |

## Current IW Hooks

These hooks connect the analogy layer back to the current root-initial consonants and the vowel-combination grid.

| Manner | Current onsets | Vowel-contour probes | Notes |
|---|---|---|---|
| Stops / plosives | `br`, `dr`, `g`, `k`, `p`, `t` | `brao`, `brea`, `brua`, `drao`, `drea`, `drua` | `br` and `dr` are included because liquid clusters preserve the stop event while adding structure. |
| Fricatives | `f`, `h`, `s`, `sh`, `v`, `z` | `fai`, `fao`, `fui`, `hai`, `hao`, `hui` | Use these as sound-taste probes, not fixed lexical entries. |
| Tongue-teeth threshold | `dh`, `th` | `dhae`, `dhai`, `dhea`, `thae`, `thai`, `thea` | Use these as sound-taste probes, not fixed lexical entries. |
| Affricates | `ch` | `chae`, `chei`, `chao` | Now seeded through `ch`, making release-friction available for sparks, snapped change, and danger-register forms. |
| Nasals | `m`, `n` | `moa`, `mua`, `mei`, `noa`, `nua`, `nei` | Use these as sound-taste probes, not fixed lexical entries. |
| Approximants | none yet | needs future sound | No consonant-root onset now; `w` is treated as a glide that emerges with vowel pairs. |
| Lateral approximant | `l` | `lia`, `leo`, `lui` | Use these as sound-taste probes, not fixed lexical entries. |
| Liquids | `br`, `dr`, `l`, `r` | `brua`, `brei`, `brou`, `drua`, `drei`, `drou` | Use these as sound-taste probes, not fixed lexical entries. |

## Operation Gloss

| Neo operation | Phonetic feel |
|---|---|
| Opposition | two articulatory pressures meet or block each other |
| Anchor | closure is held long enough to become a state |
| Propel | pressure releases as directed motion |
| Fracture | closure breaks instead of smoothly opening |
| Dampen | flow is resisted, narrowed, or muffled |
| Distort | flow is shaped by noise or asymmetry |
| Turbulence | airflow becomes unstable, mixed, or hissed |
| Gate | an obstruction controls where sound can pass |
| Stream | sound passes smoothly through an open contour |

## Design Implication

This gives the simulator a stronger middle layer: phonetic manner can become a rule-bearing function before the formal alphabet exists. Consonants set the event posture; vowels then determine whether that posture holds, releases, flows, or mutates.
