# Sound Taste Report

This report summarizes the current sound-taste layer and shows how a few roots behave across registers.

## Inventory

- Vowels: a, e, i, o, u
- Resonant vowels: ai, ea, ia, oa, ou, ui, ae, uo, ei
- Common consonants: b, d, f, g, h, k, l, m, n, r, s, t, v, y, z
- Marked consonants: sh, th, dh, ch, hm, hn, hl, vr, dr, gw
- Favored shapes: CV, CVC, VC, CVR, CVCV

## Register Operations

| Register | Description | Operations |
|---|---|---|
| first event | The first pressure-response form, before social smoothing. | normalize |
| daily / child speech | Frequent-use form. It erodes, smooths, and loses some final liquids. | normalize, soften_marked_clusters, collapse_vowel_pairs, erode_final_liquid |
| ritual / taboo-preserved | A preserved form with the primary bias marked by a small vowel or breath-residue. | normalize, append_primary_ritual_marker |
| specialist / proto-Neo facing | A compressed technical form that appends primary and secondary bias markers. | normalize, append_primary_specialist_marker, append_secondary_specialist_marker |
| place fossil | A place-preserved form. Older sounds survive, but endings compact through repeated naming. | normalize, soften_marked_clusters, append_primary_route_syllable |
| trade speech | A smoother form for cross-group exchange and public naming. | normalize, soften_marked_clusters, collapse_vowel_pairs, open_final_vowel |

## Vowel Duration

Vowel length is postural duration. Held relations lengthen; quick contact, warning, and release shorten; flow prefers movement between vowels.

| Bias | Pattern |
|---|---|
| B / Action | short-long-short |
| H / Resistance | long |
| M / Binding | short-long |
| A / Flow | moving |
| Forfeda / Mutation | short-long |

## Name Routes

| Route | Type | Base Register | Register |
|---|---|---|---|
| personal_omen | personal | ritual_taboo | personal / omen |
| place_fossil | place | place_fossil | place-memory |
| material_handling | material | specialist_proto_neo | craft / specialist |
| tool_work | tool | trade_speech | work / handling |
| ritual_title | ritual | ritual_taboo | ritual / taboo |

## Sample Register Forms

### ha
- first event: `ha`
- daily / child speech: `ha`
- ritual / taboo-preserved: `hah`
- specialist / proto-Neo facing: `hahama`
- place fossil: `hahal`
- trade speech: `ha`

### kel
- first event: `kel`
- daily / child speech: `ke`
- ritual / taboo-preserved: `kelm`
- specialist / proto-Neo facing: `kelmara`
- place fossil: `kelmor`
- trade speech: `kela`

### ta
- first event: `ta`
- daily / child speech: `ta`
- ritual / taboo-preserved: `ta`
- specialist / proto-Neo facing: `tabara`
- place fossil: `tatar`
- trade speech: `ta`

### om
- first event: `om`
- daily / child speech: `om`
- ritual / taboo-preserved: `omi`
- specialist / proto-Neo facing: `omraha`
- place fossil: `omrin`
- trade speech: `oma`

### rin
- first event: `rin`
- daily / child speech: `ri`
- ritual / taboo-preserved: `rini`
- specialist / proto-Neo facing: `rinraba`
- place fossil: `rinrin`
- trade speech: `rina`

## Phase Judgment

The root model is stable enough for sound-taste work because every seed root now carries event pressure, embodied form, danger, social carriers, drift, taboo, and a Neo bridge.

The next sound-taste work should tune whether generated forms feel too mechanical, too repetitive, or too close to later Neo notation.
