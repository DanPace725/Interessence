# Task 2: Phase Shift / Turbulence Probes

Phase Shift (Backslash + Backslash) and Turbulence (Diagonal + Backslash) are sparse in natural corpus rows. This task reads synthetic probes from `neo_phrase_corpus.csv`, confirms those matrix cells are reachable, and observes what kind of chord the Forfeda glyphs produce when concentrated.

Probes use `--missing strict` (no transliteration), so the parse is unambiguous.

## Hits per interaction across all probes

- Reinforce: 0
- Opposition: 0
- Anchor: 0
- Propel: 0
- Distort: 2
- Dampen: 0
- Invert: 1
- Crystalize: 0
- Gate: 0
- Fracture: 2
- Stream: 1
- Turbulence: 11
- Phase Shift: 22

## Per-probe detail

### `AEUI`  (phase_shift_min)

- Intent: AE to UI single Phase Shift event
- Glyph parse: `AE UI`
- Pair events: `AE->UI`=Phase Shift
- Interaction counts: Phase Shift=1
- Chord: action_net=+0.000, structure=+0.000, flow=+0.000, transform=+1.000

### `AEAEAE`  (phase_shift_chain)

- Intent: AE to AE to AE
- Glyph parse: `AE AE AE`
- Pair events: `AE->AE`=Phase Shift, `AE->AE`=Phase Shift
- Interaction counts: Phase Shift=2
- Chord: action_net=+0.000, structure=+0.000, flow=+0.000, transform=+1.000

### `UIEAIO`  (phase_shift_climb)

- Intent: UI to EA to IO
- Glyph parse: `UI EA IO`
- Pair events: `UI->EA`=Phase Shift, `EA->IO`=Phase Shift
- Interaction counts: Phase Shift=2
- Chord: action_net=+0.000, structure=+0.000, flow=+0.000, transform=+1.000

### `OIAEUIEA`  (phase_shift_walk)

- Intent: OI to AE to UI to EA
- Glyph parse: `OI AE UI EA`
- Pair events: `OI->AE`=Phase Shift, `AE->UI`=Phase Shift, `UI->EA`=Phase Shift
- Interaction counts: Phase Shift=3
- Chord: action_net=+0.000, structure=+0.000, flow=+0.000, transform=+1.000

### `AEA`  (turbulence_min)

- Intent: AE to A
- Glyph parse: `AE A`
- Pair events: `AE->A`=Turbulence
- Interaction counts: Turbulence=1
- Chord: action_net=+0.000, structure=+0.000, flow=+0.474, transform=+0.526

### `AAE`  (turbulence_min_rev)

- Intent: A to AE
- Glyph parse: `A AE`
- Pair events: `A->AE`=Turbulence
- Interaction counts: Turbulence=1
- Chord: action_net=+0.000, structure=+0.000, flow=+0.526, transform=+0.474

### `IEAU`  (turbulence_chain)

- Intent: I to EA to U
- Glyph parse: `I EA U`
- Pair events: `I->EA`=Turbulence, `EA->U`=Turbulence
- Interaction counts: Turbulence=2
- Chord: action_net=+0.000, structure=+0.000, flow=+0.706, transform=+0.294

### `OIOOIO`  (turbulence_oscillate)

- Intent: OI to O to OI to O
- Glyph parse: `OI O OI O`
- Pair events: `OI->O`=Turbulence, `O->OI`=Turbulence, `OI->O`=Turbulence
- Interaction counts: Turbulence=3
- Chord: action_net=+0.000, structure=+0.000, flow=+0.515, transform=+0.485

### `FAEUIEA`  (distort_then_phase)

- Intent: F to AE to UI to EA
- Glyph parse: `F AE UI EA`
- Pair events: `F->AE`=Distort, `AE->UI`=Phase Shift, `UI->EA`=Phase Shift
- Interaction counts: Distort=1, Phase Shift=2
- Chord: action_net=+0.326, structure=+0.000, flow=+0.000, transform=+0.674

### `RAEIO`  (fracture_then_phase)

- Intent: R to AE to IO
- Glyph parse: `R AE IO`
- Pair events: `R->AE`=Fracture, `AE->IO`=Phase Shift
- Interaction counts: Fracture=1, Phase Shift=1
- Chord: action_net=+0.000, structure=+0.485, flow=+0.000, transform=+0.515

### `MIOAE`  (fracture_then_turb_phase)

- Intent: M to IO to AE
- Glyph parse: `M IO AE`
- Pair events: `M->IO`=Fracture, `IO->AE`=Phase Shift
- Interaction counts: Fracture=1, Phase Shift=1
- Chord: action_net=+0.000, structure=+0.170, flow=+0.000, transform=+0.831

### `BEAOIIO`  (distort_chain)

- Intent: B to EA to OI to IO
- Glyph parse: `B EA OI IO`
- Pair events: `B->EA`=Distort, `EA->OI`=Phase Shift, `OI->IO`=Phase Shift
- Interaction counts: Distort=1, Phase Shift=2
- Chord: action_net=+0.101, structure=+0.000, flow=+0.000, transform=+0.899

### `AEUI EAIO OIAE`  (phase_shift_phrase)

- Intent: three short tokens
- Glyph parse: `AE UI EA IO OI AE`
- Pair events: `AE->UI`=Phase Shift, `UI->EA`=Phase Shift, `EA->IO`=Phase Shift, `IO->OI`=Phase Shift, `OI->AE`=Phase Shift
- Interaction counts: Phase Shift=5
- Chord: action_net=+0.000, structure=+0.000, flow=+0.000, transform=+1.000

### `TAE OIO UIEA`  (mixed_natural)

- Intent: word-like Forfeda load
- Glyph parse: `T AE OI O UI EA`
- Pair events: `T->AE`=Invert, `AE->OI`=Phase Shift, `OI->O`=Turbulence, `O->UI`=Turbulence, `UI->EA`=Phase Shift
- Interaction counts: Invert=1, Phase Shift=2, Turbulence=2
- Chord: action_net=-0.210, structure=+0.000, flow=+0.126, transform=+0.664

### `AOEAIOU`  (vowel_storm)

- Intent: pure vowels mixing diagonal and backslash
- Glyph parse: `A O EA IO U`
- Pair events: `A->O`=Stream, `O->EA`=Turbulence, `EA->IO`=Phase Shift, `IO->U`=Turbulence
- Interaction counts: Phase Shift=1, Stream=1, Turbulence=2
- Chord: action_net=+0.000, structure=+0.000, flow=+0.495, transform=+0.505

## Reachability conclusion

- Phase Shift events fired: **22**
- Turbulence events fired: **11**

Both rare cells are reachable from the existing transliteration pipeline once Forfeda digraphs (AE/OI/UI/EA/IO) are introduced. They are effectively absent from natural English/Latin/Irish prose because the digraphs only appear sparsely and almost never adjacent. This means the matrix cells are sound but live in a 'ritual register' of intentional Forfeda-heavy inscription.
