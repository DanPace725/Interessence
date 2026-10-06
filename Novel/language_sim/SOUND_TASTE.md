# IW Sound Taste

This is the working taste target for early IW forms.

The language should feel older than Neo, more bodily than scholarly notation, and close to breath, pressure, handling, and place. It should not sound like a decorative fantasy naming list. Forms should feel as though they were worn down by use, protected by taboo, or compressed by specialists.

The central philosophical pressure is:

> Because the world is volatile, people learn not to be hard.

This should show up in the sound system. Early IW speech should avoid over-discrete blocks where possible. Roots are not clean letters yet. They are phonogestural contours: breath, vowel movement, consonant transition, hand sign, body posture, and relational bias moving together.

Later Neo can discretize these contours into glyphs, but early IW should sound more like continuous posture becoming voice.

## Current Sound Direction

- Roots are short: usually one or two syllables, but phrase speech fuses them into flowing contours.
- Common forms prefer open vowels, diphthongs, and resonant endings.
- `h` carries breath, hush, dampening, cave-safety, or mourning pressure.
- `m`, `n`, `r`, and `l` carry memory, relation, flow, and softened social use.
- `k`, `t`, `b`, `v`, and `f` carry harder handling, action, fracture, tools, or threshold risk.
- `sh` and `th` are marked older sounds that often soften in daily or trade forms.
- Vowel pairs such as `ai`, `ea`, `ia`, `oa`, `ou`, and `ui` should feel resonant, ritual, place-bound, or later Neo-facing.
- Sounds should merge at phrase boundaries when the body would naturally carry one posture into another.
- Hard separations should be meaningful. Ordinary speech should bend before it strikes.

## Phonogestural Contours

An early root should eventually be modeled as a bundle:

```text
breath shape + vowel movement + consonant transition + hand sign + body posture + relational bias
```

The current prototype still stores `proto_sound` as a simple string, but phrase generation should already behave as if the sound is contour-based. This means adjacent roots fuse in speech:

- adjacent vowels become diphthongs or long vowels,
- final nasals flow into the next consonant,
- repeated consonants collapse,
- final liquids soften before resonant vowels,
- ritual speech preserves more contour,
- specialist speech re-discretizes later.

## Vowel Duration

Vowel length is postural duration.

- Long vowels are held relations: stabilization, attention, restraint, memory, oath, or continued flow.
- Short vowels are quick contacts: strike, warning, release, onset, or transition.
- Diphthongs are posture movement: the body or attention moves from one relation into another.

The same spelling can be misleading if read with English habits. The simulator should therefore show a pronunciation layer:

```text
spelling: keam
reading: ke-aam
duration: short-long
marked: kĕām
```

Bias gives the first-pass length pattern:

| Bias | Duration Tendency |
|---|---|
| Action | short-long-short |
| Resistance | long/held |
| Binding | short-long |
| Flow | moving/diphthongal |
| Mutation | short-long or broken contrast |

This keeps the language tied to the posture philosophy: volatile world, controlled duration.

## Register Taste

Early IW should sound different depending on how a form survives.

| Register | Taste |
|---|---|
| First event | Raw, short, pressure-responsive |
| Daily / child speech | Smoothed, easier, less technical |
| Ritual / taboo | Preserved, slightly marked, slower |
| Specialist / proto-Neo | Compressed, structured, bias-marked |
| Place fossil | Old root plus local pressure residue |
| Trade speech | Open, public, smoother across groups |

Phrase surfaces should usually be fused. Underlying root sequences can remain visible in reports, but the audible surface should avoid sounding like separate beads on a string.

## Naming Taste

Names should come from routes, not just suffixes.

- Personal names should feel like omens, carried pressures, or social hopes.
- Place names should preserve old accidents, taboos, ecological responses, or remembered practices.
- Material names should sound more technical because they descend through handling rules.
- Tool/work names should be practical and public.
- Ritual names should preserve older, less-eroded forms.

## Current Constraint

The current 28-root set is enough to test the taste rules and the first targeted repair pass, but it will still repeat ancestors quickly. The next expansion should aim for 50 roots once the register routes feel right.

Before expanding, prefer tuning:

1. sound inventory,
2. register operations,
3. name routes,
4. root quality criteria.

Then expand roots by ecological need: more caves, more rivers, more crystal gardens, more metalworking, more biology, more kin/legal/mourning terms.
