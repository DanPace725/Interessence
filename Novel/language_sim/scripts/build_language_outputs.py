from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

VALID_BIASES = {"action", "resistance", "binding", "flow", "mutation"}

NEO_FAMILY = {
    "action": "B / Action",
    "resistance": "H / Resistance",
    "binding": "M / Binding",
    "flow": "A / Flow",
    "mutation": "Forfeda / Mutation",
}

BIAS_TONE = {
    "action": "initiating pressure",
    "resistance": "dampening or refusal",
    "binding": "stabilizing relation",
    "flow": "carried motion",
    "mutation": "threshold change",
}

NEO_GLYPHS = {
    "B": {"name": "Beith", "role": "action", "magnitude": 1, "fingerprint": "atomic initiation"},
    "L": {"name": "Luis", "role": "action", "magnitude": 2, "fingerprint": "weak coupling"},
    "F": {"name": "Fearn", "role": "action", "magnitude": 3, "fingerprint": "median assertion"},
    "S": {"name": "Sail", "role": "action", "magnitude": 4, "fingerprint": "strong enforcement"},
    "P": {"name": "Peith", "role": "action", "magnitude": 5, "fingerprint": "maximal drive"},
    "H": {"name": "Huath", "role": "resistance", "magnitude": 1, "fingerprint": "atomic reaction"},
    "D": {"name": "Duir", "role": "resistance", "magnitude": 2, "fingerprint": "weak resistance"},
    "T": {"name": "Tinne", "role": "resistance", "magnitude": 3, "fingerprint": "median balance"},
    "C": {"name": "Coll", "role": "resistance", "magnitude": 4, "fingerprint": "strong barrier"},
    "W": {"name": "Ceirt", "role": "resistance", "magnitude": 5, "fingerprint": "maximal opposition"},
    "M": {"name": "Muin", "role": "binding", "magnitude": 1, "fingerprint": "atomic bind"},
    "G": {"name": "Gort", "role": "binding", "magnitude": 2, "fingerprint": "loose knot"},
    "N": {"name": "Ngeadal", "role": "binding", "magnitude": 3, "fingerprint": "median lock"},
    "Z": {"name": "Straif", "role": "binding", "magnitude": 4, "fingerprint": "strong anchor"},
    "R": {"name": "Ruis", "role": "binding", "magnitude": 5, "fingerprint": "maximal fusion"},
    "A": {"name": "Ailm", "role": "flow", "magnitude": 1, "fingerprint": "atomic flow"},
    "O": {"name": "Onn", "role": "flow", "magnitude": 2, "fingerprint": "weak current"},
    "U": {"name": "Ur", "role": "flow", "magnitude": 3, "fingerprint": "median stream"},
    "E": {"name": "Eadhadh", "role": "flow", "magnitude": 4, "fingerprint": "strong torrent"},
    "I": {"name": "Idad", "role": "flow", "magnitude": 5, "fingerprint": "maximal jet"},
    "AE": {"name": "Ae", "role": "mutation", "magnitude": 1, "fingerprint": "atomic twist"},
    "OI": {"name": "Oi", "role": "mutation", "magnitude": 2, "fingerprint": "weak vortex"},
    "UI": {"name": "Ui", "role": "mutation", "magnitude": 3, "fingerprint": "median shift"},
    "EA": {"name": "Ea", "role": "mutation", "magnitude": 4, "fingerprint": "strong warp"},
    "IO": {"name": "Io", "role": "mutation", "magnitude": 5, "fingerprint": "maximal chaos"},
}

SOUND_TO_NEO = {
    "b": ["B"],
    "br": ["B", "R"],
    "d": ["D"],
    "dh": ["D", "H"],
    "dr": ["D", "R"],
    "ch": ["T", "S"],
    "f": ["F"],
    "g": ["G"],
    "h": ["H"],
    "k": ["C"],
    "l": ["L"],
    "m": ["M"],
    "n": ["N"],
    "p": ["P"],
    "r": ["R"],
    "s": ["S"],
    "sh": ["S"],
    "t": ["T"],
    "th": ["T", "H"],
    "v": ["F"],
    "w": ["W"],
    "z": ["Z"],
}

SOUND_MANNERS = {
    "b": "stop / plosive",
    "br": "stop + liquid cluster",
    "d": "stop / plosive",
    "dh": "tongue-teeth threshold",
    "dr": "stop + liquid cluster",
    "ch": "affricate",
    "f": "fricative",
    "g": "stop / plosive",
    "h": "fricative",
    "k": "stop / plosive",
    "l": "lateral approximant / liquid",
    "m": "nasal",
    "n": "nasal",
    "p": "stop / plosive",
    "r": "approximant / liquid",
    "s": "fricative",
    "sh": "fricative",
    "t": "stop / plosive",
    "th": "tongue-teeth threshold",
    "v": "fricative",
    "w": "approximant",
    "z": "fricative",
}

MANNER_FUNCTIONS = [
    {
        "manner": "Stops / plosives",
        "english": "p, b, t, d, k, g",
        "iw_function": "closure followed by release; pressure crossing a boundary",
        "neo_roles": "action or resistance; voiced/back stops may bind",
        "use": "warnings, tool acts, doors, cuts, starts, refusals",
    },
    {
        "manner": "Fricatives",
        "english": "f, v, th, dh, s, z, sh, zh, h",
        "iw_function": "continuous contact; pressure that can be heard before it breaks",
        "neo_roles": "action when directed; resistance when breathy; mutation when noisy",
        "use": "abrasion, danger, taboo breath, erosion, soft force",
    },
    {
        "manner": "Affricates",
        "english": "ch, j",
        "iw_function": "stop released into friction",
        "neo_roles": "action + mutation",
        "use": "trigger events, sparks, snapped changes",
    },
    {
        "manner": "Nasals",
        "english": "m, n, ng",
        "iw_function": "closed-mouth continuity; carried relation inside the body",
        "neo_roles": "binding",
        "use": "memory, kinship, inside/outside, held obligations",
    },
    {
        "manner": "Approximants",
        "english": "w, r, y",
        "iw_function": "near-contact without closure; glide, approach, carried transition",
        "neo_roles": "flow or binding; w is treated as a glide emerging around vowel pairs",
        "use": "routes, water, social approach, names that should move easily",
    },
    {
        "manner": "Lateral approximant",
        "english": "l",
        "iw_function": "side-channel flow around an obstruction",
        "neo_roles": "action softened toward flow",
        "use": "paths, speech smoothing, negotiated movement",
    },
    {
        "manner": "Liquids",
        "english": "l, r",
        "iw_function": "posture that remains flexible while carrying structure",
        "neo_roles": "action + binding, often flow-adjacent in early IW",
        "use": "law, lineage, rivers, repeated practice",
    },
]

MANNER_ANALOGIES = [
    {
        "id": "plosive",
        "manner": "Stops / plosives",
        "speech_event": "complete closure, pressure buildup, then release",
        "neo_analogy": ["Opposition", "Anchor", "Propel", "Fracture"],
        "neo_reading": "a blocked force that becomes an event",
        "glyph_families": "B/H for pressure and refusal; M when closure is held; A or Forfeda when release crosses the boundary",
        "current_onset_labels": ["stop / plosive", "stop + liquid cluster"],
        "vowel_contours": ["ao", "ea", "ua"],
        "naming_tendency": "starts, cuts, gates, warnings, tools, vows that begin under pressure",
    },
    {
        "id": "fricative",
        "manner": "Fricatives",
        "speech_event": "narrowed passage with continuous noisy flow",
        "neo_analogy": ["Dampen", "Distort", "Turbulence"],
        "neo_reading": "flow under constraint, audible abrasion, or noisy mutation",
        "glyph_families": "H for constriction; B for directed hiss; Forfeda when the noise bends or mutates the field",
        "current_onset_labels": ["fricative"],
        "vowel_contours": ["ai", "ao", "ui"],
        "naming_tendency": "erosion, danger, taboo breath, warning, soft force, weathered surfaces",
    },
    {
        "id": "threshold",
        "manner": "Tongue-teeth threshold",
        "speech_event": "tongue held at the teeth while breath crosses a boundary",
        "neo_analogy": ["Opposition", "Dampen", "Gate"],
        "neo_reading": "a boundary held in the mouth before permission or refusal",
        "glyph_families": "H for restraint; M when the threshold becomes a gate; Forfeda when crossing changes the state",
        "current_onset_labels": ["tongue-teeth threshold"],
        "vowel_contours": ["ae", "ai", "ea"],
        "naming_tendency": "thresholds, taboos, old heat, tests of safety, edge-law",
    },
    {
        "id": "affricate",
        "manner": "Affricates",
        "speech_event": "closure released into friction",
        "neo_analogy": ["Gate", "Fracture", "Distort", "Turbulence"],
        "neo_reading": "a stop-event whose release becomes noisy transformation",
        "glyph_families": "M/H for closed gate; B for burst; Forfeda for the fricative tail",
        "current_onset_labels": ["affricate"],
        "vowel_contours": ["ae", "ei", "ao"],
        "naming_tendency": "sparks, snapped changes, ritual triggers, dangerous thresholds",
    },
    {
        "id": "nasal",
        "manner": "Nasals",
        "speech_event": "oral closure with sound rerouted through the body",
        "neo_analogy": ["Anchor", "Gate", "Stream"],
        "neo_reading": "a held relation that finds an alternate passage",
        "glyph_families": "M for binding; A for rerouted flow; H when the mouth closure is emphasized",
        "current_onset_labels": ["nasal"],
        "vowel_contours": ["oa", "ua", "ei"],
        "naming_tendency": "memory, kinship, interiority, carrying, obligation, hidden continuity",
    },
    {
        "id": "approximant",
        "manner": "Approximants",
        "speech_event": "near-contact without full closure",
        "neo_analogy": ["Stream", "Propel", "Gate"],
        "neo_reading": "guided transition without hard separation",
        "glyph_families": "A for glide; B for directional approach; M when the glide becomes relation",
        "current_onset_labels": ["approximant"],
        "vowel_contours": ["ai", "oa", "uo"],
        "naming_tendency": "routes, water, approach, social movement, flexible names",
    },
    {
        "id": "lateral",
        "manner": "Lateral approximant",
        "speech_event": "central obstruction with side-channel release",
        "neo_analogy": ["Dampen", "Gate", "Stream"],
        "neo_reading": "flow moves around resistance instead of breaking it",
        "glyph_families": "H for obstruction; M for valve; A for side flow",
        "current_onset_labels": ["lateral approximant / liquid"],
        "vowel_contours": ["ia", "eo", "ui"],
        "naming_tendency": "paths, negotiations, side routes, cleverness, speech smoothing",
    },
    {
        "id": "liquid",
        "manner": "Liquids",
        "speech_event": "flexible resonance that bends without fully closing",
        "neo_analogy": ["Gate", "Stream", "Anchor"],
        "neo_reading": "structure that stays mobile",
        "glyph_families": "M for relational hold; A for flow; B when the liquid carries action forward",
        "current_onset_labels": ["approximant / liquid", "lateral approximant / liquid", "stop + liquid cluster"],
        "vowel_contours": ["ua", "ei", "ou"],
        "naming_tendency": "law, lineage, rivers, repeated practice, flexible social forms",
    },
]

AICME_INTERACTIONS = {
    "action": {
        "action": "Reinforce",
        "resistance": "Opposition",
        "binding": "Anchor",
        "flow": "Propel",
        "mutation": "Distort",
    },
    "resistance": {
        "action": "Opposition",
        "resistance": "Reinforce",
        "binding": "Anchor",
        "flow": "Dampen",
        "mutation": "Invert",
    },
    "binding": {
        "action": "Anchor",
        "resistance": "Anchor",
        "binding": "Crystalize",
        "flow": "Gate",
        "mutation": "Fracture",
    },
    "flow": {
        "action": "Propel",
        "resistance": "Dampen",
        "binding": "Gate",
        "flow": "Stream",
        "mutation": "Turbulence",
    },
    "mutation": {
        "action": "Distort",
        "resistance": "Invert",
        "binding": "Fracture",
        "flow": "Turbulence",
        "mutation": "Phase Shift",
    },
}

AICME_EFFECTS = {
    "Reinforce": "aligned pressure",
    "Opposition": "tension or balance",
    "Anchor": "locked state",
    "Propel": "vectorized movement",
    "Distort": "mutated direction",
    "Dampen": "resisted flow",
    "Invert": "flipped polarity",
    "Crystalize": "rigid structure",
    "Gate": "controlled flow",
    "Fracture": "broken bond",
    "Stream": "laminar flow",
    "Turbulence": "chaotic mixing",
    "Phase Shift": "transmuted state",
}

LIGHT_DEEP_SOUNDS = {
    "f": "light",
    "v": "deep",
    "p": "light",
    "b": "deep",
    "s": "light",
    "z": "deep",
    "th": "light",
    "dh": "deep",
    "t": "light",
    "d": "deep",
    "k": "light",
    "g": "deep",
}

SPECIAL_CONSONANT_TOKENS = ["ch", "sh", "th", "dh"]

WORD_COMBINATION_RULES = {
    "preferred_min": 3,
    "preferred_max": 8,
    "general_max": 10,
    "rare_hard_max": 15,
    "max_consonant_run": 3,
    "notes": [
        "Dictionary headwords should mostly land between 3 and 8 characters.",
        "10 characters is the normal upper limit for common lexical items.",
        "15 characters is a rare hard limit for technical, ritual, or fossilized forms.",
        "Identical vowels collapse at compound boundaries.",
        "When consonants meet at a compound boundary, preserve the earlier consonant posture and drop the initial consonant or cluster from the added word.",
        "No word should retain more than three consonant characters in a row.",
    ],
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def slug_sound(value: str) -> str:
    return re.sub(r"[^a-z]", "", value.lower())


def title_form(value: str) -> str:
    return value[:1].upper() + value[1:]


def smooth_join(base: str, suffix: str) -> str:
    if not base:
        return suffix
    if not suffix:
        return base
    if base[-1] == suffix[0]:
        return base + suffix[1:]
    return base + suffix


def primary_bias(root: dict) -> str:
    return root["proto_neo_mapping"]["primary_bias"]


def secondary_bias(root: dict) -> str | None:
    return root["proto_neo_mapping"].get("secondary_bias")


def bias_marker(phonology: dict, bias: str, marker_type: str) -> str:
    return phonology["bias_markers"][bias][marker_type]


def soften_marked_clusters(form: str) -> str:
    return form.replace("sh", "s").replace("th", "t")


def collapse_vowel_pairs(form: str) -> str:
    replacements = [
        ("ai", "e"),
        ("ea", "e"),
        ("ia", "i"),
        ("oa", "o"),
        ("ou", "u"),
    ]
    for old, new in replacements:
        form = form.replace(old, new)
    return form


def erode_final_liquid(form: str) -> str:
    if len(form) > 2 and form.endswith(("l", "r", "n")):
        return form[:-1]
    return form


def open_final_vowel(form: str) -> str:
    if form and form[-1] not in "aeiou":
        return form + "a"
    return form


def is_vowel(char: str) -> bool:
    return char in "aeiou"


def apply_register(root: dict, phonology: dict, register_id: str) -> str:
    form = root["proto_sound"]
    bias = primary_bias(root)
    secondary = secondary_bias(root)
    operations = phonology["registers"][register_id]["operations"]

    for operation in operations:
        if operation == "normalize":
            form = slug_sound(form)
        elif operation == "soften_marked_clusters":
            form = soften_marked_clusters(form)
        elif operation == "collapse_vowel_pairs":
            form = collapse_vowel_pairs(form)
        elif operation == "erode_final_liquid":
            form = erode_final_liquid(form)
        elif operation == "open_final_vowel":
            form = open_final_vowel(form)
        elif operation == "append_primary_ritual_marker":
            form = smooth_join(form, bias_marker(phonology, bias, "ritual"))
        elif operation == "append_primary_specialist_marker":
            form = smooth_join(form, bias_marker(phonology, bias, "specialist"))
        elif operation == "append_secondary_specialist_marker":
            if secondary:
                form = smooth_join(form, bias_marker(phonology, secondary, "specialist"))
        elif operation == "append_primary_route_syllable":
            form = smooth_join(form, bias_marker(phonology, bias, "route_syllable"))
        else:
            raise ValueError(f"Unknown register operation: {operation}")

    return form


def fuse_pair(left: str, right: str, phonology: dict) -> str:
    if not left:
        return right
    if not right:
        return left

    fusion = phonology.get("phrase_fusion", {})
    left_final = left[-1]
    right_initial = right[0]

    if is_vowel(left_final) and is_vowel(right_initial):
        pair = left_final + right_initial
        bridge = fusion.get("vowel_bridges", {}).get(pair, pair)
        return left[:-1] + bridge + right[1:]

    for rule in fusion.get("boundary_rules", []):
        if left_final == rule["final"] and right_initial == rule["initial"]:
            return left[:-1] + rule["replacement"] + right[1:]

    if (
        fusion.get("drop_duplicate_boundary_consonants", True)
        and left_final == right_initial
        and not is_vowel(left_final)
    ):
        return left + right[1:]

    separator = fusion.get("separator", "")
    return left + separator + right


def fuse_forms(forms: list[str], phonology: dict) -> str:
    if not forms:
        return ""
    if not phonology.get("phrase_fusion", {}).get("enabled", True):
        return " ".join(forms)
    surface = forms[0]
    for form in forms[1:]:
        surface = fuse_pair(surface, form, phonology)
    return surface


def descendant_forms(root: dict, phonology: dict) -> list[dict]:
    register_ids = [
        "first_event",
        "daily_child",
        "ritual_taboo",
        "specialist_proto_neo",
        "place_fossil",
        "trade_speech",
    ]
    changes = {
        "first_event": "initial pressure response",
        "daily_child": "shortened and smoothed for frequent use",
        "ritual_taboo": f"primary {primary_bias(root)} marker preserved by formal use",
        "specialist_proto_neo": "compressed toward bias-family notation",
        "place_fossil": "older form fossilized by place memory",
        "trade_speech": "smoothed for public exchange",
    }
    return [
        {
            "generation": index,
            "register": phonology["registers"][register_id]["label"],
            "form": apply_register(root, phonology, register_id),
            "change": changes[register_id],
        }
        for index, register_id in enumerate(register_ids)
    ]


def render_gloss(template: str, root: dict, bias: str) -> str:
    return template.format(
        current_gloss=root["semantic_drift_path"][-1],
        original_pressure=root["original_pressure"],
        first_context=root["first_context"],
        bias_tone=BIAS_TONE[bias],
    )


def route_surface(root: dict, phonology: dict, route: dict) -> str:
    bias = primary_bias(root)
    form = apply_register(root, phonology, route["base_register"])
    prefix = route.get("prefix_by_bias", {}).get(bias, "")
    suffix = route.get("suffix_by_bias", {}).get(bias, "")
    if prefix:
        form = smooth_join(prefix, form)
    if suffix:
        form = smooth_join(form, suffix)
    return title_form(form)


def name_candidates(root: dict, phonology: dict) -> list[dict]:
    bias = primary_bias(root)
    candidates = []
    for route in phonology["name_routes"]:
        candidates.append(
            {
                "route": route["id"],
                "type": route["type"],
                "surface": route_surface(root, phonology, route),
                "register": route["register"],
                "gloss": render_gloss(route["gloss_template"], root, bias),
            }
        )
    return candidates


def validate_roots(roots: list[dict]) -> list[str]:
    required = [
        "root_id",
        "proto_sound",
        "phonogestural_contour",
        "original_pressure",
        "first_context",
        "gesture",
        "body_posture",
        "danger_if_wrong",
        "world_response",
        "social_role_carriers",
        "semantic_drift_path",
        "proto_neo_mapping",
        "story_fragment",
    ]
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, root in enumerate(roots, start=1):
        label = root.get("root_id", f"root #{index}")
        for key in required:
            if key not in root or root[key] in ("", [], {}):
                errors.append(f"{label}: missing {key}")
        contour = root.get("phonogestural_contour", {})
        for key in [
            "breath_shape",
            "vowel_movement",
            "consonant_transition",
            "hand_enactment",
            "posture_enactment",
        ]:
            if not contour.get(key):
                errors.append(f"{label}: missing phonogestural_contour.{key}")
        if label in seen_ids:
            errors.append(f"{label}: duplicate root_id")
        seen_ids.add(label)
        bias = root.get("proto_neo_mapping", {}).get("primary_bias")
        if bias not in VALID_BIASES:
            errors.append(f"{label}: invalid primary_bias {bias!r}")
        secondary = root.get("proto_neo_mapping", {}).get("secondary_bias")
        if secondary is not None and secondary not in VALID_BIASES:
            errors.append(f"{label}: invalid secondary_bias {secondary!r}")
    return errors


def render_root_ledger(roots: list[dict], phonology: dict) -> str:
    lines = [
        "# IW Root Ledger",
        "",
        f"Roots: {len(roots)}",
        "",
        "Each entry preserves first context, embodied form, drift, and a later proto-Neo bridge.",
        "",
    ]
    for root in roots:
        bias = primary_bias(root)
        secondary = secondary_bias(root)
        lines.extend(
            [
                f"## {root['proto_sound']} ({root['root_id']})",
                "",
                f"- Original pressure: {root['original_pressure']}",
                f"- Phonogestural contour: breath `{root['phonogestural_contour']['breath_shape']}`; vowel `{root['phonogestural_contour']['vowel_movement']}`; consonant `{root['phonogestural_contour']['consonant_transition']}`",
                f"- First context: {root['first_context']}",
                f"- Gesture: {root['gesture']}",
                f"- Body posture: {root['body_posture']}",
                f"- Danger if wrong: {root['danger_if_wrong']}",
                f"- World response: {root['world_response']}",
                f"- Carriers: {', '.join(root['social_role_carriers'])}",
                f"- Proto-Neo bias: {NEO_FAMILY[bias]}"
                + (f" + {NEO_FAMILY[secondary]}" if secondary else ""),
                f"- Surviving taboo: {root.get('surviving_taboo', 'none recorded')}",
                f"- Story fragment: {root['story_fragment']}",
                "",
                "Semantic drift:",
            ]
        )
        for i, step in enumerate(root["semantic_drift_path"], start=1):
            lines.append(f"{i}. {step}")
        lines.extend(["", "Descendant forms:"])
        for form in descendant_forms(root, phonology):
            lines.append(
                f"- G{form['generation']} {form['register']}: `{form['form']}` - {form['change']}"
            )
        lines.append("")
    return "\n".join(lines)


def render_name_candidates(roots: list[dict], phonology: dict) -> str:
    lines = [
        "# IW Name Candidates",
        "",
        "These are deterministic candidates from root lineages and register routes, not final names.",
        "",
        "| Root | Route | Type | Surface | Register | Gloss |",
        "|---|---|---|---|---|---|",
    ]
    for root in roots:
        for candidate in name_candidates(root, phonology):
            lines.append(
                "| {root} | {route} | {type} | {surface} | {register} | {gloss} |".format(
                    root=root["proto_sound"],
                    route=candidate["route"],
                    type=candidate["type"],
                    surface=candidate["surface"],
                    register=candidate["register"],
                    gloss=candidate["gloss"].replace("|", "/"),
                )
            )
    return "\n".join(lines)


def render_proto_neo_bridge(roots: list[dict]) -> str:
    bias_counts = Counter(primary_bias(root) for root in roots)
    lines = [
        "# Proto-Neo Bridge",
        "",
        "This report checks whether early root lineages can plausibly become later Neo abstractions.",
        "",
        "## Bias Coverage",
        "",
    ]
    for bias in sorted(VALID_BIASES):
        lines.append(f"- {NEO_FAMILY[bias]}: {bias_counts[bias]}")
    lines.extend(
        [
            "",
            "## Root Mapping",
            "",
            "| Root | Primary | Secondary | Later abstraction | Feature bridge |",
            "|---|---|---|---|---|",
        ]
    )
    for root in roots:
        bias = primary_bias(root)
        secondary = secondary_bias(root) or ""
        feature_map = root["proto_neo_mapping"].get("early_feature_map", {})
        feature_bridge = "; ".join(f"{k} -> {v}" for k, v in feature_map.items())
        later = f"{root['semantic_drift_path'][-1]} as {BIAS_TONE[bias]}"
        lines.append(
            "| {root} | {primary} | {secondary} | {later} | {features} |".format(
                root=root["proto_sound"],
                primary=NEO_FAMILY[bias],
                secondary=NEO_FAMILY.get(secondary, secondary),
                later=later.replace("|", "/"),
                features=feature_bridge.replace("|", "/"),
            )
        )
    return "\n".join(lines)


def assess_root_quality(root: dict) -> dict:
    checks = [
        (
            "concrete_first_context",
            len(root["first_context"].split()) >= 6,
            "first context needs more scene-level specificity",
        ),
        (
            "embodied_form",
            bool(root.get("gesture")) and bool(root.get("body_posture")),
            "gesture and posture should both be present",
        ),
        (
            "danger_pressure",
            bool(root.get("danger_if_wrong")) and bool(root.get("world_response")),
            "danger and world response should both be present",
        ),
        (
            "social_carriers",
            len(root.get("social_role_carriers", [])) >= 2,
            "at least two carrier roles should preserve the form",
        ),
        (
            "drift_depth",
            len(root.get("semantic_drift_path", [])) >= 5,
            "semantic drift should have at least five steps",
        ),
        (
            "taboo_or_constraint",
            bool(root.get("surviving_taboo")),
            "surviving taboo or constraint should be recorded",
        ),
        (
            "story_fragment",
            len(root.get("story_fragment", "").split()) >= 8,
            "story fragment should be long enough to imply narrative use",
        ),
        (
            "neo_primary",
            primary_bias(root) in VALID_BIASES,
            "primary Neo bias should be valid",
        ),
        (
            "neo_secondary",
            secondary_bias(root) in VALID_BIASES,
            "secondary Neo bias should be present and valid",
        ),
        (
            "feature_bridge",
            len(root.get("proto_neo_mapping", {}).get("early_feature_map", {})) >= 3,
            "at least three early features should bridge to later Neo",
        ),
    ]
    passed = [name for name, ok, _ in checks if ok]
    missing = [description for _, ok, description in checks if not ok]
    return {
        "score": len(passed),
        "max_score": len(checks),
        "missing": missing,
    }


def render_root_quality_report(roots: list[dict]) -> str:
    assessments = [(root, assess_root_quality(root)) for root in roots]
    score_counts = Counter(assessment["score"] for _, assessment in assessments)
    average = sum(assessment["score"] for _, assessment in assessments) / len(assessments)
    lines = [
        "# Root Quality Report",
        "",
        "This report checks whether the root model is stable enough to support naming, drift, and later Neo abstraction.",
        "",
        f"Roots assessed: {len(roots)}",
        f"Average score: {average:.1f}/10",
        "",
        "## Score Distribution",
        "",
    ]
    for score in sorted(score_counts, reverse=True):
        lines.append(f"- {score}/10: {score_counts[score]}")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "A root is considered stable for the current prototype at 8/10 or higher.",
            "Scores below that should be revised before the root becomes part of the larger naming ecology.",
            "",
            "| Root | Score | Status | Gaps |",
            "|---|---:|---|---|",
        ]
    )
    for root, assessment in assessments:
        status = "stable" if assessment["score"] >= 8 else "revise"
        gaps = "; ".join(assessment["missing"]) if assessment["missing"] else "none"
        lines.append(
            f"| {root['proto_sound']} | {assessment['score']}/10 | {status} | {gaps} |"
        )
    return "\n".join(lines)


def render_sound_taste_report(roots: list[dict], phonology: dict) -> str:
    sample_roots = roots[:5]
    lines = [
        "# Sound Taste Report",
        "",
        "This report summarizes the current sound-taste layer and shows how a few roots behave across registers.",
        "",
        "## Inventory",
        "",
        f"- Vowels: {', '.join(phonology['sound_inventory']['vowels'])}",
        f"- Resonant vowels: {', '.join(phonology['sound_inventory']['resonant_vowels'])}",
        f"- Common consonants: {', '.join(phonology['sound_inventory']['common_consonants'])}",
        f"- Marked consonants: {', '.join(phonology['sound_inventory']['marked_consonants'])}",
        f"- Favored shapes: {', '.join(phonology['sound_inventory']['favored_shapes'])}",
        "",
        "## Register Operations",
        "",
        "| Register | Description | Operations |",
        "|---|---|---|",
    ]
    for register in phonology["registers"].values():
        operations = ", ".join(register["operations"])
        lines.append(f"| {register['label']} | {register['description']} | {operations} |")
    lines.extend(
        [
            "",
            "## Vowel Duration",
            "",
            phonology["vowel_duration"]["principle"],
            "",
            "| Bias | Pattern |",
            "|---|---|",
        ]
    )
    for bias, pattern in phonology["vowel_duration"]["bias_patterns"].items():
        lines.append(f"| {NEO_FAMILY[bias]} | {'-'.join(pattern)} |")
    lines.extend(
        [
            "",
            "## Name Routes",
            "",
            "| Route | Type | Base Register | Register |",
            "|---|---|---|---|",
        ]
    )
    for route in phonology["name_routes"]:
        lines.append(
            f"| {route['id']} | {route['type']} | {route['base_register']} | {route['register']} |"
        )
    lines.extend(["", "## Sample Register Forms", ""])
    for root in sample_roots:
        lines.append(f"### {root['proto_sound']}")
        for form in descendant_forms(root, phonology):
            lines.append(f"- {form['register']}: `{form['form']}`")
        lines.append("")
    lines.extend(
        [
            "## Phase Judgment",
            "",
            "The root model is stable enough for sound-taste work because every seed root now carries event pressure, embodied form, danger, social carriers, drift, taboo, and a Neo bridge.",
            "",
            "The next sound-taste work should tune whether generated forms feel too mechanical, too repetitive, or too close to later Neo notation.",
        ]
    )
    return "\n".join(lines)


def roots_by_sound(roots: list[dict]) -> dict[str, dict]:
    return {root["proto_sound"]: root for root in roots}


def phrase_surface(probe: dict, roots_by_id: dict[str, dict], phonology: dict) -> str:
    forms = [
        apply_register(roots_by_id[root_sound], phonology, probe["register_id"])
        for root_sound in probe["roots"]
    ]
    if probe.get("fuse", True):
        return fuse_forms(forms, phonology)
    return probe.get("connector", " ").join(forms)


def initial_consonant_cluster(value: str) -> str:
    tokens = sound_tokens(value)
    cluster = []
    for token in tokens:
        if token in "aeiou":
            break
        cluster.append(token)
    return "".join(cluster)


def collapse_identical_vowels(value: str) -> str:
    result = []
    for char in value:
        if result and char in "aeiou" and result[-1] == char:
            continue
        result.append(char)
    return "".join(result)


def trim_consonant_runs(value: str, max_run: int = WORD_COMBINATION_RULES["max_consonant_run"]) -> str:
    result = []
    run = 0
    for char in value:
        if char in "aeiou":
            run = 0
            result.append(char)
            continue
        run += 1
        if run <= max_run:
            result.append(char)
    return "".join(result)


def combine_word_pair(left: str, right: str) -> str:
    left = slug_sound(left)
    right = slug_sound(right)
    if not left:
        return right
    if not right:
        return left

    if left[-1] in "aeiou" and right[0] in "aeiou":
        combined = left + right[1:] if left[-1] == right[0] else left + right
        return trim_consonant_runs(collapse_identical_vowels(combined))

    if left[-1] not in "aeiou" and right[0] not in "aeiou":
        if left[-1] in "mn" and right[0] in "mn" and left[-1] != right[0]:
            combined = left + right
            return trim_consonant_runs(collapse_identical_vowels(combined))
        cluster = initial_consonant_cluster(right)
        combined = left + right[len(cluster) :]
        return trim_consonant_runs(collapse_identical_vowels(combined))

    return trim_consonant_runs(collapse_identical_vowels(left + right))


def combine_words_for_lexicon(parts: list[str]) -> str:
    if not parts:
        return ""
    combined = slug_sound(parts[0])
    for part in parts[1:]:
        combined = combine_word_pair(combined, part)
    return combined


def lexical_fallback_from_roots(root_sounds: list[str]) -> str:
    if not root_sounds:
        return ""
    combined = combine_words_for_lexicon(root_sounds)
    if len(combined) <= WORD_COMBINATION_RULES["general_max"]:
        return combined

    first = root_sounds[0]
    fragments = [first]
    for root_sound in root_sounds[1:]:
        vowels = "".join(char for char in root_sound if char in "aeiou")
        fragments.append(root_onset(root_sound)[:1] + (vowels[:1] or "a"))
    return combine_words_for_lexicon(fragments)


def enforce_word_length(headword: str, root_sounds: list[str]) -> tuple[str, str]:
    hard_max = WORD_COMBINATION_RULES["rare_hard_max"]
    general_max = WORD_COMBINATION_RULES["general_max"]
    if len(headword) <= hard_max:
        status = "preferred" if WORD_COMBINATION_RULES["preferred_min"] <= len(headword) <= WORD_COMBINATION_RULES["preferred_max"] else "long-common"
        if len(headword) > general_max:
            status = "rare-long"
        return headword, status

    fallback = lexical_fallback_from_roots(root_sounds)
    if len(fallback) > hard_max:
        fallback = fallback[:hard_max]
    return fallback, "compressed-from-overlong"


def constrained_lexicon_headword(parts: list[str], root_sounds: list[str]) -> dict:
    raw = combine_words_for_lexicon(parts)
    headword, status = enforce_word_length(raw, root_sounds)
    return {
        "headword": headword,
        "raw_combination": raw,
        "shape_status": status,
        "length": len(headword),
    }


def phrase_underlying(probe: dict, roots_by_id: dict[str, dict], phonology: dict) -> str:
    forms = [
        apply_register(roots_by_id[root_sound], phonology, probe["register_id"])
        for root_sound in probe["roots"]
    ]
    return " + ".join(forms)


def phrase_root_gloss(probe: dict, roots_by_id: dict[str, dict]) -> str:
    parts = []
    for root_sound in probe["roots"]:
        root = roots_by_id[root_sound]
        parts.append(f"{root_sound}: {root['semantic_drift_path'][-1]}")
    return "; ".join(parts)


def render_phrase_samples(roots: list[dict], phonology: dict, phrase_probes: dict) -> str:
    root_lookup = roots_by_sound(roots)
    lines = [
        "# IW Phrase Samples",
        "",
        "These are generated phrase probes for hearing how the current roots work together.",
        "",
        "They are not final grammar. They use the current register rules in `data/phonology.json` and the editable probe list in `data/phrase_probes.json`.",
        "",
        "## Samples",
        "",
        "| ID | Type | Register | Underlying | Fused Surface | Gloss | Scene Use |",
        "|---|---|---|---|---|---|---|",
    ]
    for probe in phrase_probes["probes"]:
        surface = phrase_surface(probe, root_lookup, phonology)
        underlying = phrase_underlying(probe, root_lookup, phonology)
        register = phonology["registers"][probe["register_id"]]["label"]
        lines.append(
            "| {id} | {type} | {register} | `{underlying}` | `{surface}` | {gloss} | {scene} |".format(
                id=probe["id"],
                type=probe["type"],
                register=register,
                underlying=underlying,
                surface=surface,
                gloss=probe["gloss"].replace("|", "/"),
                scene=probe["scene_use"].replace("|", "/"),
            )
        )
    lines.extend(["", "## Root Breakdown", ""])
    for probe in phrase_probes["probes"]:
        surface = phrase_surface(probe, root_lookup, phonology)
        underlying = phrase_underlying(probe, root_lookup, phonology)
        lines.extend(
            [
                f"### {probe['id']}",
                "",
                f"- Surface: `{surface}`",
                f"- Underlying register forms: `{underlying}`",
                f"- Context: {probe['context']}",
                f"- Register: {phonology['registers'][probe['register_id']]['label']}",
                f"- Root sequence: {' + '.join(probe['roots'])}",
                f"- Root drift glosses: {phrase_root_gloss(probe, root_lookup)}",
                f"- Phrase gloss: {probe['gloss']}",
                f"- Scene use: {probe['scene_use']}",
                "",
            ]
        )
    lines.extend(
        [
            "## What To Listen For",
            "",
            "- Daily forms should be quick and speakable.",
            "- Ritual forms should feel slower and slightly preserved.",
            "- Fused surfaces should feel like posture-contours, not separate root blocks.",
            "- Place-fossil forms may repeat route syllables because place memory is currently marked by bias family.",
            "- Specialist forms are intentionally more mechanical; if they feel too Neo-like too early, the specialist register should be softened.",
            "- Repeated roots across samples are now a review signal rather than a failure. If a family dominates too many phrases, expand that family with a new embodied root instead of forcing the old root to carry everything.",
        ]
    )
    return "\n".join(lines)


def root_lexicon_entries(roots: list[dict], phonology: dict, later_alphabet: dict) -> list[dict]:
    entries = []
    for root in roots:
        profile = root_compression_profile(root, later_alphabet)
        entries.append(
            {
                "headword": root["proto_sound"],
                "kind": "root sound-event",
                "gloss": root["semantic_drift_path"][-1],
                "source": root["proto_sound"],
                "lineage": root["original_pressure"],
                "form": profile["compressed_form"],
                "evolved": apply_register(root, phonology, "daily_child"),
                "usage": root["first_context"],
                "raw_combination": root["proto_sound"],
                "shape_status": "preferred",
                "length": len(root["proto_sound"]),
            }
        )
    return entries


def proto_lexicon_entries(proto_words: list[dict], roots: list[dict], phonology: dict, later_alphabet: dict) -> list[dict]:
    root_lookup = roots_by_sound(roots)
    entries = []
    for proto_word in proto_words:
        if proto_word["meaning_index"] == 0:
            continue
        root = root_lookup[proto_word["source_root"]]
        profile = root_compression_profile(root, later_alphabet)
        entries.append(
            {
                "headword": proto_word["utterance"],
                "kind": "adjacent proto-word",
                "gloss": proto_word["meaning"],
                "source": proto_word["source_root"],
                "lineage": f"semantic drift step {proto_word['meaning_index'] + 1}",
                "form": profile["compressed_form"],
                "evolved": evolved_proto_word_form(proto_word, phonology),
                "usage": proto_word["source_pressure"],
                "raw_combination": proto_word["utterance"],
                "shape_status": "preferred" if WORD_COMBINATION_RULES["preferred_min"] <= len(proto_word["utterance"]) <= WORD_COMBINATION_RULES["preferred_max"] else "watch",
                "length": len(proto_word["utterance"]),
            }
        )
    return entries


def phrase_lexicon_entries(roots: list[dict], phonology: dict, phrase_probes: dict, later_alphabet: dict) -> list[dict]:
    root_lookup = roots_by_sound(roots)
    entries = []
    for probe in phrase_probes["probes"]:
        source_roots = probe["roots"]
        raw_surface = trim_consonant_runs(collapse_identical_vowels(phrase_surface(probe, root_lookup, phonology)))
        headword, shape_status = enforce_word_length(raw_surface, source_roots)
        constrained = {
            "headword": headword,
            "raw_combination": raw_surface,
            "shape_status": shape_status,
            "length": len(headword),
        }
        profiles = [
            root_compression_profile(root_lookup[root_sound], later_alphabet)["compressed_form"]
            for root_sound in source_roots
        ]
        entries.append(
            {
                "headword": constrained["headword"],
                "kind": f"{probe['type']} phrase",
                "gloss": probe["gloss"],
                "source": " + ".join(source_roots),
                "lineage": phonology["registers"][probe["register_id"]]["label"],
                "form": " + ".join(profiles),
                "evolved": phrase_underlying(probe, root_lookup, phonology),
                "usage": probe["scene_use"],
                "raw_combination": constrained["raw_combination"],
                "shape_status": constrained["shape_status"],
                "length": constrained["length"],
            }
        )
    return entries


def lexicon_entries(roots: list[dict], proto_words: list[dict], phonology: dict, phrase_probes: dict, later_alphabet: dict) -> list[dict]:
    entries = []
    entries.extend(root_lexicon_entries(roots, phonology, later_alphabet))
    entries.extend(proto_lexicon_entries(proto_words, roots, phonology, later_alphabet))
    entries.extend(phrase_lexicon_entries(roots, phonology, phrase_probes, later_alphabet))
    return sorted(entries, key=lambda entry: (entry["headword"], entry["kind"]))


def lexicon_thinness(roots: list[dict], entries: list[dict], later_alphabet: dict) -> dict:
    coverage = later_alphabet_coverage(roots, later_alphabet)
    family_counts = coverage["consonant_counts"]
    thin_families = [
        family["id"]
        for family in later_alphabet["consonant_families"]
        if family_counts[family["id"]] <= 1
    ]
    root_counts = Counter()
    kind_counts = Counter(entry["kind"] for entry in entries)
    shape_counts = Counter(entry.get("shape_status", "unknown") for entry in entries)
    over_hard_limit = [
        entry["headword"]
        for entry in entries
        if entry.get("length", len(entry["headword"])) > WORD_COMBINATION_RULES["rare_hard_max"]
    ]
    for entry in entries:
        for root_sound in entry["source"].split(" + "):
            root_counts[root_sound] += 1
    underused_roots = [root["proto_sound"] for root in roots if root_counts[root["proto_sound"]] <= 2]
    overused_roots = [root for root, count in root_counts.items() if count >= 6]
    return {
        "kind_counts": kind_counts,
        "shape_counts": shape_counts,
        "family_counts": family_counts,
        "thin_families": thin_families,
        "underused_roots": underused_roots,
        "overused_roots": sorted(overused_roots),
        "over_hard_limit": over_hard_limit,
    }


def families_in_trace(trace: str) -> set[str]:
    parts = re.split(r"[^A-Z]+", trace)
    return {part for part in parts if part}


def review_lexicon_entry(entry: dict, thin_families: set[str], overused_roots: set[str]) -> dict:
    reasons = []
    source_roots = set(entry["source"].split(" + "))
    entry_families = families_in_trace(entry["form"])

    if entry["shape_status"] == "rare-long":
        status = "ritual-only"
        reasons.append("long form should stay fossilized, ritual, or specialist")
    elif entry["shape_status"] == "compressed-from-overlong":
        status = "watch"
        reasons.append("compressed from an overlong underlying form; needs sound-taste review")
    elif entry["shape_status"] == "watch":
        status = "watch"
        reasons.append("too short or under-shaped for a stable public word")
    elif entry_families & thin_families:
        status = "watch"
        reasons.append("depends on a thin mouth-family")
    elif source_roots & overused_roots:
        status = "watch"
        reasons.append("depends on an overworked root")
    else:
        status = "promote"
        reasons.append("shape, length, and ancestry are stable enough for current use")

    if len(entry["headword"]) < WORD_COMBINATION_RULES["preferred_min"] and entry["kind"] == "adjacent proto-word":
        status = "watch"
        reasons.append("adjacent proto-word is shorter than the preferred word range")

    return {
        **entry,
        "review_status": status,
        "review_reason": "; ".join(dict.fromkeys(reasons)),
    }


def lexicon_review_entries(roots: list[dict], proto_words: list[dict], phonology: dict, phrase_probes: dict, later_alphabet: dict) -> list[dict]:
    entries = lexicon_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    thinness = lexicon_thinness(roots, entries, later_alphabet)
    thin_families = set(thinness["thin_families"])
    overused_roots = set(thinness["overused_roots"])
    return [review_lexicon_entry(entry, thin_families, overused_roots) for entry in entries]


def root_expansion_targets(review_entries: list[dict], later_alphabet: dict) -> list[dict]:
    status_counts_by_family = {family["id"]: Counter() for family in later_alphabet["consonant_families"]}
    for entry in review_entries:
        for family_id in families_in_trace(entry["form"]):
            if family_id in status_counts_by_family:
                status_counts_by_family[family_id][entry["review_status"]] += 1

    suggestions = {
        "SZ": "Stabilize short alarm words or add a neighboring root for voiced surface buzz and pressure heard before speech.",
        "TH": "Stabilize threshold words or add another dh/th root for oath, tested safety, or named limit.",
        "CHSH": "Stabilize scrape-release words or add another ch/sh root for spark-change or released danger.",
        "H": "Stabilize breath-gate words or add another vent root for grief, taboo, or pressure release.",
    }
    targets = []
    for family in later_alphabet["consonant_families"]:
        counts = status_counts_by_family[family["id"]]
        total = sum(counts.values())
        if total <= 3 or counts["watch"] + counts["ritual-only"] >= counts["promote"]:
            targets.append(
                {
                    "family": family["id"],
                    "letter_name": family["letter_name"],
                    "current_load": total,
                    "watch_pressure": counts["watch"] + counts["ritual-only"],
                    "suggestion": suggestions.get(
                        family["id"],
                        f"Add a root that makes {family['name']} less dependent on current entries.",
                    ),
                }
            )
    return targets


def render_lexicon_review(roots: list[dict], proto_words: list[dict], phonology: dict, phrase_probes: dict, later_alphabet: dict) -> str:
    entries = lexicon_review_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    status_counts = Counter(entry["review_status"] for entry in entries)
    targets = root_expansion_targets(entries, later_alphabet)
    lines = [
        "# Lexicon Review",
        "",
        "This report flags the current dictionary batch before adding more roots.",
        "",
        "Statuses are provisional: `promote` means usable now, `watch` means keep but review, `ritual-only` means preserve as a marked/fossil form, and `respin` is reserved for forms that should be rebuilt.",
        "",
        "## Status Counts",
        "",
    ]
    for status in ["promote", "watch", "ritual-only", "respin"]:
        lines.append(f"- {status}: {status_counts[status]}")

    lines.extend(
        [
            "",
            "## Review Table",
            "",
            "| Headword | Status | Len | Kind | Gloss | Source | Reason |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for entry in entries:
        lines.append(
            "| `{headword}` | {status} | {length} | {kind} | {gloss} | {source} | {reason} |".format(
                headword=entry["headword"],
                status=entry["review_status"],
                length=entry["length"],
                kind=entry["kind"],
                gloss=entry["gloss"].replace("|", "/"),
                source=entry["source"],
                reason=entry["review_reason"].replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Root Expansion Targets",
            "",
            "| Family | Letter name | Current load | Watch pressure | Suggested root pressure |",
            "|---|---|---:|---:|---|",
        ]
    )
    for target in targets:
        lines.append(
            "| {family} | {name} | {load} | {watch} | {suggestion} |".format(
                family=target["family"],
                name=target["letter_name"],
                load=target["current_load"],
                watch=target["watch_pressure"],
                suggestion=target["suggestion"],
            )
        )

    lines.extend(
        [
            "",
            "## Next Move",
            "",
            "Use this report to add a targeted batch of roots rather than expanding evenly. The strongest immediate candidates are the families with high watch pressure or very little ecological evidence.",
        ]
    )
    return "\n".join(lines)


def render_lexicon_expansion_report(roots: list[dict], proto_words: list[dict], phonology: dict, phrase_probes: dict, later_alphabet: dict) -> str:
    entries = lexicon_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    review_entries = lexicon_review_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    thinness = lexicon_thinness(roots, entries, later_alphabet)
    status_counts = Counter(entry["review_status"] for entry in review_entries)
    phrase_entries = [entry for entry in entries if entry["kind"].endswith("phrase")]
    watch_entries = [entry for entry in review_entries if entry["review_status"] == "watch"]
    ritual_entries = [entry for entry in review_entries if entry["review_status"] == "ritual-only"]
    repaired_forms = [
        {
            "root": root,
            "meaning": next(
                (
                    item["meaning"]
                    for item in proto_words
                    if item["source_root"] == root and item["meaning_index"] == meaning_index
                ),
                "",
            ),
            "headword": form,
        }
        for (root, meaning_index), form in sorted(PROTO_WORD_FORM_OVERRIDES.items())
    ]
    new_probe_ids = {
        "alarm_before_fall",
        "kept_alarm",
        "edge_oath",
        "edge_walk",
        "spark_release",
        "spark_cover",
        "clear_alarm",
        "gate_refusal",
    }
    probe_lookup = {probe["id"]: probe for probe in phrase_probes["probes"]}
    second_pass_rows = []
    root_lookup = roots_by_sound(roots)
    for probe_id in sorted(new_probe_ids):
        probe = probe_lookup[probe_id]
        headword = next(
            entry["headword"]
            for entry in phrase_entries
            if entry["source"] == " + ".join(probe["roots"]) and entry["gloss"] == probe["gloss"]
        )
        second_pass_rows.append(
            {
                "id": probe_id,
                "headword": headword,
                "roots": " + ".join(probe["roots"]),
                "surface": phrase_surface(probe, root_lookup, phonology),
                "gloss": probe["gloss"],
            }
        )

    lines = [
        "# Lexicon Expansion Report",
        "",
        "This pass updates a few public headwords that had become too eroded, then expands the dictionary through phrase-use rather than new roots.",
        "",
        "## Current Totals",
        "",
        f"- roots: {len(roots)}",
        f"- proto-words: {len(proto_words)}",
        f"- phrase probes: {len(phrase_probes['probes'])}",
        f"- lexicon entries: {len(entries)}",
        f"- promoted / watch / ritual-only: {status_counts['promote']} / {status_counts['watch']} / {status_counts['ritual-only']}",
        "",
        "## Updated Adjacent Words",
        "",
        "| Root | Updated headword | Meaning |",
        "|---|---|---|",
    ]
    for item in repaired_forms:
        lines.append(f"| `{item['root']}` | `{item['headword']}` | {item['meaning']} |")

    lines.extend(
        [
            "",
            "## Second-Pass Phrase Growth",
            "",
            "| Probe | Headword | Surface | Roots | Gloss |",
            "|---|---|---|---|---|",
        ]
    )
    for row in second_pass_rows:
        lines.append(
            f"| {row['id']} | `{row['headword']}` | `{row['surface']}` | {row['roots']} | {row['gloss']} |"
        )

    lines.extend(
        [
            "",
            "## What Arises",
            "",
            f"- Underused roots after this pass: {', '.join(thinness['underused_roots']) or 'none'}",
            f"- Heavily used roots after this pass: {', '.join(thinness['overused_roots']) or 'none'}",
            f"- Watch words now cluster around: {', '.join(entry['headword'] for entry in watch_entries[:12]) or 'none'}",
            f"- Ritual/fossil forms: {', '.join(entry['headword'] for entry in ritual_entries) or 'none'}",
            "",
            "The main pressure is no longer missing mouth-family coverage. It is register choice: daily speech wants short forms, while the lexicon wants enough body left in the word that ancestry remains audible.",
        ]
    )
    return "\n".join(lines)


def render_lexicon_first_batch(roots: list[dict], proto_words: list[dict], phonology: dict, phrase_probes: dict, later_alphabet: dict) -> str:
    entries = lexicon_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    thinness = lexicon_thinness(roots, entries, later_alphabet)
    lines = [
        "# IW Lexicon Current Batch",
        "",
        "This is the current dictionary pass grown from the current root base.",
        "",
        "It treats the later 15-letter alphabet as a horizon the dictionary grows toward, not a linear spelling source. Roots remain embodied sound-events; adjacent words emerge by drift, register, phrase-use, and repeated social need.",
        "",
        f"Entries: {len(entries)}",
        "",
        "## Entry Mix",
        "",
    ]
    for kind, count in sorted(thinness["kind_counts"].items()):
        lines.append(f"- {kind}: {count}")
    lines.extend(
        [
            "",
            "## Lexicon",
            "",
            "| Headword | Len | Shape | Kind | Gloss | Source | Later family trace | Raw / underlying form | Use note |",
            "|---|---:|---|---|---|---|---|---|---|",
        ]
    )
    for entry in entries:
        lines.append(
            "| `{headword}` | {length} | {shape} | {kind} | {gloss} | {source} | `{form}` | `{raw}` / `{evolved}` | {usage} |".format(
                headword=entry["headword"],
                length=entry.get("length", len(entry["headword"])),
                shape=entry.get("shape_status", "unknown"),
                kind=entry["kind"],
                gloss=entry["gloss"].replace("|", "/"),
                source=entry["source"],
                form=entry["form"],
                raw=entry.get("raw_combination", entry["headword"]),
                evolved=entry["evolved"],
                usage=entry["usage"].replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Thinness And Pressure",
            "",
            "| Check | Result |",
            "|---|---|",
            f"| Thin later consonant families | {', '.join(thinness['thin_families']) or 'none'} |",
            f"| Underused roots | {', '.join(thinness['underused_roots']) or 'none'} |",
            f"| Heavily used roots | {', '.join(thinness['overused_roots']) or 'none'} |",
            f"| Over hard limit | {', '.join(thinness['over_hard_limit']) or 'none'} |",
            f"| Shape mix | {', '.join(f'{key}: {value}' for key, value in sorted(thinness['shape_counts'].items()))} |",
            "",
            "## Draft Rules Before The Next Iteration",
            "",
            "1. A dictionary entry should keep root ancestry visible until the writing system becomes culturally stable.",
            "2. Adjacent words may split from a root only when they carry a narrower meaning than the root bundle.",
            "3. Phrase entries should become standalone words only after repeated social use gives them a scene, role, or taboo.",
            "4. The later alphabet may annotate mouth-family traces, but it should not decide word shape by itself.",
            "5. Thin mouth families should be expanded through new embodied roots before they are expanded through abstract spelling.",
            "6. Overused roots should trigger either new neighboring roots or sharper semantic splits.",
            "7. Combined headwords should prefer 3-8 characters, treat 10 as the common ceiling, and reserve 11-15 for rare fossilized or specialist words.",
            "8. Identical vowels collapse at joins; consonant joins preserve the earlier consonant posture and drop the entering consonant cluster, except where nasal continuity carries binding.",
            "9. No accepted headword should keep more than three consonant characters in a row.",
        ]
    )
    return "\n".join(lines)


def render_word_combination_ruleset() -> str:
    examples = [
        ("om + nu", combine_words_for_lexicon(["om", "nu"]), "nasal continuity survives because it carries binding"),
        ("kelm + morm", combine_words_for_lexicon(["kelm", "morm"]), "matching consonant posture keeps the first consonant"),
        ("sa + tae", combine_words_for_lexicon(["sa", "tae"]), "open vowel into plosive remains speakable"),
        ("fairafa + vekfaba + paemara", constrained_lexicon_headword(["fairafa", "vekfaba", "paemara"], ["fai", "vek", "pae"])["headword"], "overlong specialist phrase compresses from roots"),
        ("ta + ari", combine_words_for_lexicon(["ta", "ari"]), "same vowel at boundary collapses"),
    ]
    lines = [
        "# Provisional Word Combination Ruleset",
        "",
        "These rules govern dictionary headwords made by combining roots, adjacent words, or repeated phrase forms.",
        "",
        "They do not erase older ritual or specialist forms. The lexicon may preserve a raw underlying form while giving the accepted headword a shorter, more speakable public shape.",
        "",
        "## Length",
        "",
        f"- Preferred common word range: {WORD_COMBINATION_RULES['preferred_min']}-{WORD_COMBINATION_RULES['preferred_max']} characters.",
        f"- General common ceiling: {WORD_COMBINATION_RULES['general_max']} characters.",
        f"- Rare hard ceiling: {WORD_COMBINATION_RULES['rare_hard_max']} characters.",
        "- Forms above the hard ceiling must compress, usually by returning to root sounds and preserving only the most important onset/vowel traces.",
        "",
        "## Joining",
        "",
        "- Same vowels collapse at joins: `a + a` becomes `a`.",
        "- Different vowels may remain as a diphthong if they are pronounceable and semantically useful.",
        "- If consonants meet, preserve the earlier consonant posture and drop the entering consonant or consonant cluster.",
        "- Nasal continuity is an exception: `m + n` or `n + m` may survive because it carries binding.",
        f"- No accepted headword should keep more than {WORD_COMBINATION_RULES['max_consonant_run']} consonant characters in a row.",
        "- Glides like `w` can emerge between vowel fields later, but they should not be introduced automatically in this first dictionary pass.",
        "",
        "## Examples",
        "",
        "| Input | Output | Note |",
        "|---|---|---|",
    ]
    for source, output, note in examples:
        lines.append(f"| `{source}` | `{output}` | {note} |")
    lines.extend(
        [
            "",
            "## Open Questions",
            "",
            "- Which long forms are prestigious enough to survive as ritual or specialist exceptions?",
            "- Should some vowel pairs trigger glide insertion in later iterations?",
            "- Should final nasals resist truncation more strongly than other consonants because they carry binding?",
            "- Should child speech enforce the 3-8 character range more aggressively than ritual speech?",
        ]
    )
    return "\n".join(lines)


def consonant_family(root: dict) -> str:
    transition = root["phonogestural_contour"]["consonant_transition"].replace("-", "")
    if transition.startswith(("h", "sh", "s")):
        return "breath"
    if transition.startswith(("ch", "z")):
        return "breath"
    if transition.startswith(("th", "dh")):
        return "strike"
    if transition.startswith(("f", "v", "w", "y")):
        return "glide"
    if transition.startswith(("m", "n")):
        return "nasal"
    if transition.startswith(("l", "r")):
        return "liquid"
    if transition.startswith(("b", "d", "g", "k", "p", "t")):
        return "strike"
    return "mixed"


def cluster_key(root: dict) -> str:
    return f"{primary_bias(root)}:{consonant_family(root)}"


def alphabet_clusters(roots: list[dict]) -> dict[str, list[dict]]:
    clusters: dict[str, list[dict]] = {}
    for root in roots:
        clusters.setdefault(cluster_key(root), []).append(root)
    return dict(sorted(clusters.items()))


def cluster_onset(family: str, roots: list[dict]) -> str:
    if roots:
        transition = roots[0]["phonogestural_contour"]["consonant_transition"].replace("-", "")
        if transition.startswith("sh"):
            return "h"
        if transition.startswith("dr"):
            return "d"
        return transition[:1]
    return {
        "breath": "h",
        "glide": "w",
        "liquid": "r",
        "mixed": "l",
        "nasal": "m",
        "strike": "t",
    }[family]


def vowel_edges(value: str) -> tuple[str, str]:
    vowels = [char for char in value if is_vowel(char)]
    if not vowels:
        return ("a", "a")
    return (vowels[0], vowels[-1])


def compress_cluster_vowels(roots: list[dict], phonology: dict) -> str:
    first = roots[0]["phonogestural_contour"]["vowel_movement"]
    last = roots[-1]["phonogestural_contour"]["vowel_movement"]
    start, _ = vowel_edges(first)
    _, end = vowel_edges(last)
    pair = start + end
    return phonology.get("phrase_fusion", {}).get("vowel_bridges", {}).get(pair, pair)


def alphabet_attractor_form(key: str, roots: list[dict], phonology: dict) -> str:
    bias, family = key.split(":", 1)
    onset = cluster_onset(family, roots)
    vowel = compress_cluster_vowels(roots, phonology)
    marker = bias_marker(phonology, bias, "ritual")
    return smooth_join(onset + vowel, marker)


def vowel_positions(value: str) -> list[int]:
    return [index for index, char in enumerate(value) if is_vowel(char)]


def duration_pattern_for_form(form: str, bias: str, phonology: dict) -> list[str]:
    positions = vowel_positions(form)
    base_pattern = phonology["vowel_duration"]["bias_patterns"][bias]
    if not positions:
        return []
    if base_pattern == ["moving"]:
        return ["moving"] * len(positions)
    return [base_pattern[index % len(base_pattern)] for index in range(len(positions))]


def marked_vowel(char: str, duration: str, phonology: dict) -> str:
    if duration == "long":
        return phonology["vowel_duration"]["marked_long"].get(char, char)
    if duration == "short":
        return phonology["vowel_duration"]["marked_short"].get(char, char)
    return char


def ascii_vowel(char: str, duration: str, phonology: dict) -> str:
    if duration == "long":
        return phonology["vowel_duration"]["ascii_long"].get(char, char)
    return char


def pronunciation_for_form(form: str, bias: str, phonology: dict) -> dict:
    positions = vowel_positions(form)
    pattern = duration_pattern_for_form(form, bias, phonology)
    marked_chars = list(form)
    reading_parts: list[str] = []

    if pattern and all(duration == "moving" for duration in pattern):
        return {
            "spelling": form,
            "reading_ascii": form,
            "duration_pattern": "-".join(pattern),
            "marked_form": form,
        }

    for index, (position, duration) in enumerate(zip(positions, pattern)):
        marked_chars[position] = marked_vowel(form[position], duration, phonology)
        start = 0 if index == 0 else positions[index - 1] + 1
        reading_parts.append(form[start:position] + ascii_vowel(form[position], duration, phonology))

    if positions and positions[-1] + 1 < len(form):
        reading_parts[-1] += form[positions[-1] + 1 :]
    elif not positions:
        reading_parts.append(form)

    return {
        "spelling": form,
        "reading_ascii": "-".join(part for part in reading_parts if part),
        "duration_pattern": "-".join(pattern),
        "marked_form": "".join(marked_chars),
    }


def evolution_lineage(root: dict, phonology: dict, attractor_form: str) -> list[dict]:
    return [
        {
            "stage": "0 event contour",
            "form": root["proto_sound"],
            "pressure": "embodied response before stable speech",
        },
        {
            "stage": "1 daily erosion",
            "form": apply_register(root, phonology, "daily_child"),
            "pressure": "simplified by repetition, children, and ordinary use",
        },
        {
            "stage": "2 ritual preservation",
            "form": apply_register(root, phonology, "ritual_taboo"),
            "pressure": "protected by taboo, danger, and formal handling",
        },
        {
            "stage": "3 specialist expansion",
            "form": apply_register(root, phonology, "specialist_proto_neo"),
            "pressure": "expanded into bias-marked technical contour",
        },
        {
            "stage": "4 alphabet attractor",
            "form": attractor_form,
            "pressure": "crystallized into a repeatable sign family",
        },
    ]


def render_evolution_fastforward(roots: list[dict], phonology: dict) -> str:
    clusters = alphabet_clusters(roots)
    attractors = {
        key: alphabet_attractor_form(key, grouped_roots, phonology)
        for key, grouped_roots in clusters.items()
    }
    pronunciations = {
        key: pronunciation_for_form(attractor, key.split(":", 1)[0], phonology)
        for key, attractor in attractors.items()
    }
    lines = [
        "# IW Language Evolution Fast-Forward",
        "",
        "This is a speculative simulation of how embodied roots could grow, merge, compress, and crystallize toward a formal alphabet-like system.",
        "",
        "The output is not final canon. It is an instrument for asking whether the direction feels plausible.",
        "",
        "## Model",
        "",
        "1. Event contour: a sound/posture/gesture bundle answers pressure.",
        "2. Daily erosion: frequent use smooths and simplifies it.",
        "3. Ritual preservation: dangerous or sacred contexts preserve a marked contour.",
        "4. Specialist expansion: handlers make the bias structure explicit.",
        "5. Alphabet attractor: related contours merge into a legible sign family.",
        "",
        "## Provisional Alphabet Attractors",
        "",
        "| Attractor | Bias | Consonant Family | Spelling | Reading | Duration | Marked | Roots | What Stabilized |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for key, grouped_roots in clusters.items():
        bias, family = key.split(":", 1)
        roots_label = ", ".join(root["proto_sound"] for root in grouped_roots)
        stabilized = "; ".join(root["semantic_drift_path"][-1] for root in grouped_roots)
        pronunciation = pronunciations[key]
        lines.append(
            "| {key} | {bias} | {family} | `{sound}` | `{reading}` | {duration} | `{marked}` | {roots} | {stabilized} |".format(
                key=key,
                bias=NEO_FAMILY[bias],
                family=family,
                sound=pronunciation["spelling"],
                reading=pronunciation["reading_ascii"],
                duration=pronunciation["duration_pattern"],
                marked=pronunciation["marked_form"],
                roots=roots_label,
                stabilized=stabilized.replace("|", "/"),
            )
        )
    lines.extend(["", "## Root Lineages", ""])
    for root in roots:
        key = cluster_key(root)
        lineage = evolution_lineage(root, phonology, attractors[key])
        contour = root["phonogestural_contour"]
        pronunciation = pronunciations[key]
        lines.extend(
            [
                f"### {root['proto_sound']} -> {pronunciation['spelling']}",
                "",
                f"- Attractor: `{key}`",
                f"- Pronunciation: `{pronunciation['reading_ascii']}`; duration `{pronunciation['duration_pattern']}`; marked `{pronunciation['marked_form']}`",
                f"- Contour: breath `{contour['breath_shape']}`; vowel `{contour['vowel_movement']}`; consonant `{contour['consonant_transition']}`",
                f"- Gesture: {contour['hand_enactment']}",
                f"- Posture: {contour['posture_enactment']}",
                "",
                "| Stage | Form | Selection Pressure |",
                "|---|---|---|",
            ]
        )
        for stage in lineage:
            lines.append(f"| {stage['stage']} | `{stage['form']}` | {stage['pressure']} |")
        lines.append("")
    lines.extend(
        [
            "## Reading Notes",
            "",
            "- Spelling is not English pronunciation. Use the reading and marked columns for intended sound.",
            "- Short vowels are marked with breves; long vowels are marked with macrons.",
            "- Duration comes from relational posture: held relations lengthen, quick contact shortens, flow moves.",
            "- Merging is expected: related roots collapse toward shared alphabet attractors.",
            "- Expansion is also expected: specialist forms become more explicit before later compression.",
            "- The candidate sounds are sign-family names, not final letters.",
            "- If an attractor feels too broad, the next step is to split by gesture or posture rather than by sound alone.",
            "- If an attractor feels too narrow, the next step is to let it absorb neighboring roots through phrase-use or ritual-use evidence.",
        ]
    )
    return "\n".join(lines)


DERIVED_LETTER_SPECS = [
    {
        "root": "ha",
        "register_id": "ritual_taboo",
        "name": "held hush",
    },
    {
        "root": "kel",
        "register_id": "ritual_taboo",
        "name": "carried binding",
    },
    {
        "root": "pae",
        "register_id": "ritual_taboo",
        "name": "threshold hold",
    },
    {
        "root": "sil",
        "register_id": "ritual_taboo",
        "name": "listening hold",
    },
    {
        "root": "thae",
        "register_id": "ritual_taboo",
        "name": "threshold remainder",
    },
]


PROTO_WORD_EXTRA_COUNT = 10


PROTO_WORD_AFFIXES = {
    "action": ["", "a", "ai"],
    "resistance": ["", "h", "ai"],
    "binding": ["", "m", "ae"],
    "flow": ["", "i", "ea"],
    "mutation": ["", "u", "ei"],
}


PROTO_WORD_FORM_OVERRIDES = {
    ("kel", 1): "kelm",
    ("rin", 1): "rini",
    ("mor", 1): "morm",
    ("sha", 1): "shah",
    ("sil", 1): "silh",
    ("mea", 1): "meam",
    ("fai", 1): "fei",
    ("gan", 1): "ganm",
    ("zai", 1): "zaih",
    ("zun", 1): "zunh",
    ("thol", 1): "tholi",
    ("hea", 1): "heah",
}


LETTER_NAME_MARKERS = {
    "action": "ra",
    "resistance": "ai",
    "binding": "ma",
    "flow": "li",
    "mutation": "ei",
}


LETTER_NAME_EXTENSION_SUFFIXES = {
    "ha": "la",
    "kel": "i",
    "pae": "o",
    "sil": "a",
    "thae": "m",
}


def proto_word_form(root: dict, meaning_index: int, phonology: dict) -> str:
    bias = primary_bias(root)
    base = root["proto_sound"]
    override = PROTO_WORD_FORM_OVERRIDES.get((base, meaning_index))
    if override:
        return override
    if meaning_index == 0:
        return base
    if meaning_index == 1:
        daily = apply_register(root, phonology, "daily_child")
        if daily != base:
            return daily
    affixes = PROTO_WORD_AFFIXES[bias]
    affix = affixes[meaning_index % len(affixes)]
    if not affix:
        affix = bias_marker(phonology, bias, "ritual")
    return base + affix


def generate_proto_words(roots: list[dict], phonology: dict, target_count: int | None = None) -> list[dict]:
    proto_words = []
    for root_index, root in enumerate(roots):
        selected_count = 3 if root_index < PROTO_WORD_EXTRA_COUNT else 2
        for meaning_index, meaning in enumerate(root["semantic_drift_path"][:selected_count]):
            proto_words.append(
                {
                    "id": f"pw_{len(proto_words) + 1:03d}",
                    "source_root": root["proto_sound"],
                    "utterance": proto_word_form(root, meaning_index, phonology),
                    "meaning": meaning,
                    "meaning_index": meaning_index,
                    "bias": primary_bias(root),
                    "gesture": root["phonogestural_contour"]["hand_enactment"],
                    "posture": root["phonogestural_contour"]["posture_enactment"],
                    "source_pressure": root["first_context"],
                }
            )
            if target_count is not None and len(proto_words) == target_count:
                return proto_words
    return proto_words


def evolved_proto_word_form(proto_word: dict, phonology: dict) -> str:
    fake_root = {
        "proto_sound": proto_word["utterance"],
        "proto_neo_mapping": {"primary_bias": proto_word["bias"]},
    }
    if proto_word["meaning_index"] == 0:
        return apply_register(fake_root, phonology, "daily_child")
    if proto_word["meaning_index"] == 1:
        return apply_register(fake_root, phonology, "ritual_taboo")
    return apply_register(fake_root, phonology, "trade_speech")


def proto_words_by_root(proto_words: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for proto_word in proto_words:
        grouped.setdefault(proto_word["source_root"], []).append(proto_word)
    return grouped


def render_proto_words(proto_words: list[dict], phonology: dict) -> str:
    lines = [
        "# IW Proto-Words",
        "",
        "This layer expands the compressed root meanings into atomic utterance-meaning units.",
        "",
        "Each proto-word carries one meaning. Later usage can merge, erode, preserve, or formalize these into alphabet letters.",
        "",
        f"Proto-words: {len(proto_words)}",
        "",
        "| ID | Source Root | Utterance | Evolved Form | Meaning | Bias | Gesture |",
        "|---|---|---|---|---|---|---|",
    ]
    for proto_word in proto_words:
        lines.append(
            "| {id} | {root} | `{utterance}` | `{evolved}` | {meaning} | {bias} | {gesture} |".format(
                id=proto_word["id"],
                root=proto_word["source_root"],
                utterance=proto_word["utterance"],
                evolved=evolved_proto_word_form(proto_word, phonology),
                meaning=proto_word["meaning"].replace("|", "/"),
                bias=NEO_FAMILY[proto_word["bias"]],
                gesture=proto_word["gesture"].replace("|", "/"),
            )
        )
    return "\n".join(lines)


def render_proto_word_collapse(proto_words: list[dict], alphabet_entries: list[dict], phonology: dict) -> str:
    grouped = proto_words_by_root(proto_words)
    letters_by_root = {
        entry["root"]: entry
        for entry in alphabet_entries
        if entry["kind"] == "base"
    }
    lines = [
        "# Proto-Word Collapse",
        "",
        f"This report fast-forwards from {len(proto_words)} atomic proto-words back toward the semi-formal provisional alphabet.",
        "",
        "The goal is not to lose meaning. The goal is to show how repeated usage could let many single-meaning utterances settle under a smaller set of learnable letters while retaining semantic fields.",
        "",
        "| Letter | Source Root | Proto-Word Count | Proto-Word Meanings | Collapse Logic |",
        "|---|---|---:|---|---|",
    ]
    for root, items in grouped.items():
        letter = letters_by_root[root]["letter"]
        meanings = "; ".join(item["meaning"] for item in items)
        evolved_forms = ", ".join(evolved_proto_word_form(item, phonology) for item in items)
        lines.append(
            "| `{letter}` | {root} | {count} | {meanings} | `{forms}` settle as the {root} letter family |".format(
                letter=letter,
                root=root,
                count=len(items),
                meanings=meanings.replace("|", "/"),
                forms=evolved_forms,
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This makes the alphabet a historical compression of usage, not a direct collapse of root bundles. The proto-words carry atomic meanings first; the alphabet comes later as a stabilized teaching and inscription layer.",
            "",
            "The next refinement should decide which proto-words resist collapse and deserve their own derived letters.",
        ]
    )
    return "\n".join(lines)


def compact_letter_name(value: str) -> str:
    value = re.sub(r"[^a-z]", "", value.lower())
    for old, new in [
        ("aaa", "aa"),
        ("eee", "ee"),
        ("iii", "ii"),
        ("ooo", "oo"),
        ("uuu", "uu"),
        ("hh", "h"),
        ("mm", "m"),
        ("ll", "l"),
        ("rr", "r"),
        ("nn", "n"),
    ]:
        value = value.replace(old, new)
    if len(value) > 6:
        value = value[:6]
    return value


def stable_letter_name_for_root(root: dict) -> str:
    marker = LETTER_NAME_MARKERS[primary_bias(root)]
    candidate = compact_letter_name(root["proto_sound"] + marker)
    if candidate == root["proto_sound"]:
        candidate = compact_letter_name(candidate + marker[:1])
    if len(candidate) < 3:
        candidate = compact_letter_name(candidate + marker)
    return candidate


def stable_letter_name_entries(roots: list[dict], proto_words: list[dict], phonology: dict) -> list[dict]:
    grouped = proto_words_by_root(proto_words)
    entries = []
    used_names = set()
    for root in roots:
        source_words = grouped[root["proto_sound"]]
        candidate = stable_letter_name_for_root(root)
        while candidate in used_names:
            candidate = compact_letter_name(candidate + "i")
        used_names.add(candidate)
        entries.append(
            {
                "kind": "base",
                "source_root": root["proto_sound"],
                "stable_name": candidate,
                "proto_words": source_words,
                "meaning": "; ".join(item["meaning"] for item in source_words),
                "gesture": root["phonogestural_contour"]["hand_enactment"],
                "posture": root["phonogestural_contour"]["posture_enactment"],
                "collapse_logic": "root sound plus relational marker, lightly compacted",
            }
        )
    root_lookup = roots_by_sound(roots)
    for spec in DERIVED_LETTER_SPECS:
        root = root_lookup[spec["root"]]
        ritual_form = apply_register(root, phonology, spec["register_id"])
        suffix = LETTER_NAME_EXTENSION_SUFFIXES[root["proto_sound"]]
        candidate = compact_letter_name(ritual_form + suffix)
        while candidate in used_names:
            candidate = compact_letter_name(candidate + "u")
        used_names.add(candidate)
        source_words = grouped[root["proto_sound"]]
        entries.append(
            {
                "kind": "extension",
                "source_root": root["proto_sound"],
                "stable_name": candidate,
                "proto_words": source_words,
                "meaning": f"{spec['name']}; " + "; ".join(item["meaning"] for item in source_words),
                "gesture": root["phonogestural_contour"]["hand_enactment"],
                "posture": root["phonogestural_contour"]["posture_enactment"],
                "collapse_logic": "ritual-preserved form plus light extension vowel",
            }
        )
    return entries


def render_stable_letter_names_experiment(roots: list[dict], proto_words: list[dict], phonology: dict) -> str:
    entries = stable_letter_name_entries(roots, proto_words, phonology)
    lines = [
        "# Stable Letter Names Experiment",
        "",
        "This experiment takes the full proto-word list, accelerates usage drift, then lightly collapses the proto-words into stable letter names.",
        "",
        "Unlike the evolution fast-forward attractors, these names stay close to their sources. They are intended to be learnable names of letters, not distant phonetic descendants.",
        "",
        f"Stable letter names: {len(entries)}",
        "",
        "| Kind | Source Root | Letter Name | Length | Proto-Words | Accelerated Forms | Meaning Field | Gesture |",
        "|---|---|---|---:|---|---|---|---|",
    ]
    for entry in entries:
        proto_word_labels = ", ".join(f"{item['utterance']}={item['meaning']}" for item in entry["proto_words"])
        evolved_forms = ", ".join(evolved_proto_word_form(item, phonology) for item in entry["proto_words"])
        lines.append(
            "| {kind} | {root} | `{name}` | {length} | {proto} | `{evolved}` | {meaning} | {gesture} |".format(
                kind=entry["kind"],
                root=entry["source_root"],
                name=entry["stable_name"],
                length=len(entry["stable_name"]),
                proto=proto_word_labels.replace("|", "/"),
                evolved=evolved_forms,
                meaning=entry["meaning"].replace("|", "/"),
                gesture=entry["gesture"].replace("|", "/"),
            )
        )
    lines.extend(["", "## Letter Notes", ""])
    for entry in entries:
        lines.extend(
            [
                f"### {entry['stable_name']}",
                "",
                f"- Kind: {entry['kind']}",
                f"- Source root: `{entry['source_root']}`",
                f"- Collapse logic: {entry['collapse_logic']}",
                f"- Meanings carried: {entry['meaning']}",
                f"- Gesture: {entry['gesture']}",
                f"- Posture: {entry['posture']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Reading",
            "",
            "This is the middle path: more evolved than the raw roots, but much less divergent than the compressed attractor experiment.",
            "",
            "The next pass should mark which names sound good enough to keep, which should be respun, and which proto-word families deserve separate letter names instead of collapsing.",
        ]
    )
    return "\n".join(lines)


def family_by_id(later_alphabet: dict) -> dict[str, dict]:
    return {family["id"]: family for family in later_alphabet["consonant_families"]}


def vowel_family_by_sound(later_alphabet: dict) -> dict[str, dict]:
    return {family["sound"]: family for family in later_alphabet["vowel_families"]}


def consonant_family_for_token(token: str, later_alphabet: dict) -> str | None:
    token = token.lower()
    for family in later_alphabet["consonant_families"]:
        if token in {family["light_sound"], family["deep_sound"]}:
            return family["id"]
    return None


def sound_tokens(value: str) -> list[str]:
    value = slug_sound(value)
    tokens = []
    index = 0
    while index < len(value):
        two = value[index : index + 2]
        if two in SPECIAL_CONSONANT_TOKENS:
            tokens.append(two)
            index += 2
        else:
            tokens.append(value[index])
            index += 1
    return tokens


def root_compression_profile(root: dict, later_alphabet: dict) -> dict:
    tokens = sound_tokens(root["proto_sound"])
    contour_tokens = sound_tokens(root["phonogestural_contour"]["consonant_transition"])
    vowel_tokens = [
        token
        for token in sound_tokens(
            root["proto_sound"] + root["phonogestural_contour"]["vowel_movement"]
        )
        if token in "aeiou"
    ]
    consonant_hits = []
    state_notes = []
    seen_families = set()
    seen_state_notes = set()
    families = family_by_id(later_alphabet)

    for token in tokens + contour_tokens:
        family_id = consonant_family_for_token(token, later_alphabet)
        if not family_id:
            continue
        if family_id not in seen_families:
            consonant_hits.append(family_id)
            seen_families.add(family_id)
        family = families[family_id]
        state_note = None
        if family["contrast_axis"] == "light_deep":
            state_note = f"{family_id}:{LIGHT_DEEP_SOUNDS.get(token, 'context')}"
        elif family_id == "MN":
            state_note = f"{family_id}:{'lip-nasal' if token == 'm' else 'tongue-nasal'}"
        elif family_id == "LR":
            state_note = f"{family_id}:{'side-route' if token == 'l' else 'back/rolled-route'}"
        elif family_id == "CHSH":
            state_note = f"{family_id}:{'short-release' if token == 'ch' else 'long-scrape'}"
        elif family_id == "H":
            state_note = f"{family_id}:breath-gate"
        if state_note and state_note not in seen_state_notes:
            state_notes.append(state_note)
            seen_state_notes.add(state_note)

    vowel_lookup = vowel_family_by_sound(later_alphabet)
    vowel_hits = []
    seen_vowels = set()
    for token in vowel_tokens:
        if token in vowel_lookup and token not in seen_vowels:
            vowel_hits.append(vowel_lookup[token]["id"])
            seen_vowels.add(token)

    compressed_parts = consonant_hits + vowel_hits
    return {
        "root": root["proto_sound"],
        "consonant_families": consonant_hits,
        "vowel_fields": vowel_hits,
        "state_notes": state_notes,
        "compressed_form": "+".join(compressed_parts) if compressed_parts else "unmapped",
        "closure_behavior": closure_behavior(root["proto_sound"]),
        "survival_function": root["original_pressure"],
        "embodied_event": f"{root['phonogestural_contour']['breath_shape']}; {root['gesture']}; {root['body_posture']}",
    }


def closure_behavior(form: str) -> str:
    tokens = sound_tokens(form)
    if not tokens:
        return "none"
    final = tokens[-1]
    if final in "aeiou":
        return "open release"
    if final in {"m", "n"}:
        return "nasal binding"
    if final in {"l", "r"}:
        return "liquid routing / soft hold"
    if final in {"p", "b", "t", "d", "k", "g"}:
        return "closed cut or sealed release"
    if final in {"f", "v", "s", "z", "sh", "ch", "th", "dh"}:
        return "frictional fade"
    if final == "h":
        return "breath vent"
    return "contextual release"


def later_alphabet_coverage(roots: list[dict], later_alphabet: dict) -> dict:
    profiles = [root_compression_profile(root, later_alphabet) for root in roots]
    consonant_counts = Counter()
    vowel_counts = Counter()
    for profile in profiles:
        consonant_counts.update(profile["consonant_families"])
        vowel_counts.update(profile["vowel_fields"])
    missing_consonants = [
        family["id"]
        for family in later_alphabet["consonant_families"]
        if consonant_counts[family["id"]] == 0
    ]
    missing_vowels = [
        family["id"]
        for family in later_alphabet["vowel_families"]
        if vowel_counts[family["id"]] == 0
    ]
    return {
        "profiles": profiles,
        "consonant_counts": consonant_counts,
        "vowel_counts": vowel_counts,
        "missing_consonants": missing_consonants,
        "missing_vowels": missing_vowels,
    }


def render_later_alphabet_compression(roots: list[dict], later_alphabet: dict) -> str:
    coverage = later_alphabet_coverage(roots, later_alphabet)
    family_counts = Counter(
        family
        for profile in coverage["profiles"]
        for family in profile["consonant_families"]
    )
    repaired_families = [
        family_id
        for family_id in ("TH", "CHSH", "H", "SZ")
        if family_counts[family_id] >= 3
    ]
    lines = [
        "# Later Alphabet Compression Audit",
        "",
        "This report treats the 15-letter alphabet as a later analytical compression of older embodied sound-events.",
        "",
        later_alphabet["motto"],
        "",
        "The goal is not to force roots to begin as letters. The goal is to check whether the current root base contains enough mouth-action evidence for later scholars to compress it into 10 consonant families and 5 vowel fields.",
        "",
        "## Later Consonant Families",
        "",
        "| Family | Operation | Contrast axis | Two common realizations | Conditioning |",
        "|---|---|---|---|---|",
    ]
    for family in later_alphabet["consonant_families"]:
        lines.append(
            "| {id} | {operation} | {axis} | `{light}` / `{deep}` | {conditioning} |".format(
                id=family["id"],
                operation=family["operation"],
                axis=family["contrast_axis"],
                light=family["light_sound"],
                deep=family["deep_sound"],
                conditioning=family["conditioning"],
            )
        )

    lines.extend(
        [
            "",
            "## Later Vowel Fields",
            "",
            "| Field | Sound | Resonance | Contrast axis | States |",
            "|---|---|---|---|---|",
        ]
    )
    for family in later_alphabet["vowel_families"]:
        lines.append(
            "| {id} | `{sound}` | {field} | {axis} | {light} / {deep} |".format(
                id=family["id"],
                sound=family["sound"],
                field=family["field"],
                axis=family["contrast_axis"],
                light=family["light_state"],
                deep=family["deep_state"],
            )
        )

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            "| Type | Present | Missing |",
            "|---|---|---|",
            "| Consonant families | {present}/10 | {missing} |".format(
                present=10 - len(coverage["missing_consonants"]),
                missing=", ".join(coverage["missing_consonants"]) or "none",
            ),
            "| Vowel fields | {present}/5 | {missing} |".format(
                present=5 - len(coverage["missing_vowels"]),
                missing=", ".join(coverage["missing_vowels"]) or "none",
            ),
            "",
            "## Root Compression Profiles",
            "",
            "| Root | Embodied event | Mouth families | State notes | Vowel fields | Closure | Later compressed form |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for profile in coverage["profiles"]:
        lines.append(
            "| `{root}` | {event} | {families} | {states} | {vowels} | {closure} | `{compressed}` |".format(
                root=profile["root"],
                event=profile["embodied_event"].replace("|", "/"),
                families=", ".join(profile["consonant_families"]) or "vowel-led",
                states=", ".join(profile["state_notes"]) or "context-conditioned",
                vowels=", ".join(profile["vowel_fields"]) or "none",
                closure=profile["closure_behavior"],
                compressed=profile["compressed_form"],
            )
        )

    lines.extend(
        [
            "",
            "## Revision Guidance",
            "",
            "- Keep roots as performed events: sound, hand, posture, danger, and world response remain primary.",
            "- Use the compressed form only as a later scholarly reading of repeated mouth-actions.",
            "- The current set now covers all ten consonant families and all five vowel fields, so the later 15-letter compression is structurally plausible.",
            f"- The targeted repair pass strengthened {', '.join(f'`{family}`' for family in repaired_families) or 'the previously thin families'} with multiple embodied ancestors; future expansion should now watch ecological diversity and overuse rather than simple missing coverage.",
            "- Light/deep is only one contrast axis. `MN`, `LR`, `CHSH`, and `H` should stay position-, routing-, duration-, or breath-phase based.",
        ]
    )
    return "\n".join(lines)


def contrast_label(value: str) -> str:
    labels = {
        "light_deep": "light/deep",
        "duration_or_release": "duration/release",
        "breath_phase": "breath phase",
    }
    return labels.get(value, value)


def dual_phonetics_for_consonant(family: dict) -> str:
    return f"{family['light_sound']} / {family['deep_sound']} ({contrast_label(family['contrast_axis'])})"


def dual_phonetics_for_vowel(family: dict) -> str:
    return f"{family['sound']} / {family['sound']}{family['sound']} ({contrast_label(family['contrast_axis'])})"


def complete_alphabet_entries(later_alphabet: dict) -> list[dict]:
    entries = []
    for family in later_alphabet["consonant_families"]:
        entries.append(
            {
                "type": "consonant",
                "name": family["letter_name"],
                "letter": family["letter"],
                "dual_phonetics": dual_phonetics_for_consonant(family),
                "gesture": family["gesture"],
                "brief_meaning": family["brief_meaning"],
                "operation": family["operation"],
                "conditioning": family["conditioning"],
            }
        )
    for family in later_alphabet["vowel_families"]:
        entries.append(
            {
                "type": "vowel",
                "name": family["letter_name"],
                "letter": family["letter"],
                "dual_phonetics": dual_phonetics_for_vowel(family),
                "gesture": family["gesture"],
                "brief_meaning": family["brief_meaning"],
                "operation": family["field"],
                "conditioning": f"{family['light_state']} versus {family['deep_state']}",
            }
        )
    return entries


def render_complete_later_alphabet(later_alphabet: dict) -> str:
    entries = complete_alphabet_entries(later_alphabet)
    consonants = [entry for entry in entries if entry["type"] == "consonant"]
    vowels = [entry for entry in entries if entry["type"] == "vowel"]
    lines = [
        "# Complete Later IW Alphabet",
        "",
        "This is the later analytical alphabet: 10 consonant mouth-family letters and 5 vowel-field letters.",
        "",
        "It is not the primitive root language. Each letter is a fossilized mouth-operation abstracted from older embodied sound-events, gestures, postures, and survival contexts.",
        "",
        later_alphabet["motto"],
        "",
        "## Consonant Mouth-Families",
        "",
        "| Name | Letter | Dual phonetics | Gesture | Brief meaning |",
        "|---|---|---|---|---|",
    ]
    for entry in consonants:
        lines.append(
            "| {name} | `{letter}` | `{phonetics}` | {gesture} | {meaning} |".format(
                name=entry["name"],
                letter=entry["letter"],
                phonetics=entry["dual_phonetics"],
                gesture=entry["gesture"],
                meaning=entry["brief_meaning"],
            )
        )

    lines.extend(
        [
            "",
            "## Vowel Fields",
            "",
            "| Name | Letter | Dual phonetics | Gesture | Brief meaning |",
            "|---|---|---|---|---|",
        ]
    )
    for entry in vowels:
        lines.append(
            "| {name} | `{letter}` | `{phonetics}` | {gesture} | {meaning} |".format(
                name=entry["name"],
                letter=entry["letter"],
                phonetics=entry["dual_phonetics"],
                gesture=entry["gesture"],
                meaning=entry["brief_meaning"],
            )
        )

    lines.extend(
        [
            "",
            "## Reading Rules",
            "",
            "- The written letter names the mouth-operation, not a single fixed sound.",
            "- `FV`, `PB`, `SZ`, `TH`, `DT`, and `KG` use light/deep contrast: breath-light versus body/throat-deep.",
            "- `MN`, `LR`, `CHSH`, and `H` use position, routing, release/duration, or breath-phase contrast.",
            "- Vowel letters use short/held duration as their dual realization.",
            "- `w` is not a consonant-family letter in this stage. It behaves as a glide that emerges around vowel pairs.",
            "",
            "## Alphabet Order",
            "",
            "`FV PB SZ TH DT KG MN LR CHSH H A E I O U`",
        ]
    )
    return "\n".join(lines)


def root_onset(value: str) -> str:
    match = re.match(r"^[^aeiou]+", value)
    return match.group(0) if match else ""


def current_beginning_consonants(roots: list[dict]) -> list[str]:
    onsets = sorted({root_onset(root["proto_sound"]) for root in roots if root_onset(root["proto_sound"])})
    return onsets


def vowel_combinations(phonology: dict) -> list[str]:
    vowels = phonology["sound_inventory"]["vowels"]
    return [left + right for left in vowels for right in vowels]


def render_vowel_consonant_grid(roots: list[dict], phonology: dict) -> str:
    onsets = current_beginning_consonants(roots)
    vowels = phonology["sound_inventory"]["vowels"]
    combos = vowel_combinations(phonology)
    lines = [
        "# Vowel Combination Grid",
        "",
        "This experiment pairs every two-vowel combination with each current root-initial consonant or consonant cluster.",
        "",
        "These are sound probes, not lexicon entries. Use them to test what feels fluid, harsh, learnable, or worth promoting into future roots/proto-words.",
        "",
        f"Beginning consonants: {', '.join(f'`{onset}`' for onset in onsets)}",
        f"Vowel combinations: {len(combos)}",
        f"Total probes: {len(onsets) * len(combos)}",
        "",
        "## Compact Matrix",
        "",
        "| Onset | a* | e* | i* | o* | u* |",
        "|---|---|---|---|---|---|",
    ]
    for onset in onsets:
        cells = []
        for first_vowel in vowels:
            forms = [f"`{onset}{first_vowel}{second_vowel}`" for second_vowel in vowels]
            cells.append(", ".join(forms))
        lines.append(f"| `{onset}` | " + " | ".join(cells) + " |")

    lines.extend(["", "## By Onset", ""])
    for onset in onsets:
        lines.append(f"### {onset}")
        lines.append("")
        lines.append("| Vowel 1 | Vowel 2 Forms |")
        lines.append("|---|---|")
        for first_vowel in vowels:
            forms = [f"`{onset}{first_vowel}{second_vowel}`" for second_vowel in vowels]
            lines.append(f"| `{first_vowel}` | {', '.join(forms)} |")
        lines.append("")

    lines.extend(
        [
            "## Listening Notes",
            "",
            "- Forms with smooth vowel movement may be candidates for flow, place, or ritual speech.",
            "- Forms with abrupt onset plus wide vowel movement may suit action or warning roots.",
            "- Repeated vowels should be considered possible length marks, not English double-vowel spelling by default.",
            "- Clusters like `br` and `dr` may be too hard for early daily speech but useful for craft, hunt, or specialist registers.",
        ]
    )
    return "\n".join(lines)


def letter_duration(root: dict, phonology: dict) -> str:
    pattern = phonology["vowel_duration"]["bias_patterns"][primary_bias(root)]
    return "-".join(pattern)


def provisional_alphabet_entries(roots: list[dict], phonology: dict) -> list[dict]:
    root_lookup = roots_by_sound(roots)
    entries = []
    for root in roots:
        entries.append(
            {
                "kind": "base",
                "root": root["proto_sound"],
                "letter": root["proto_sound"],
                "phoneme": root["proto_sound"],
                "duration": letter_duration(root, phonology),
                "meaning": root["semantic_drift_path"][-1],
                "gesture": root["phonogestural_contour"]["hand_enactment"],
                "posture": root["phonogestural_contour"]["posture_enactment"],
                "bias": NEO_FAMILY[primary_bias(root)],
                "source": root["first_context"],
            }
        )
    for spec in DERIVED_LETTER_SPECS:
        root = root_lookup[spec["root"]]
        letter = apply_register(root, phonology, spec["register_id"])
        entries.append(
            {
                "kind": "derived",
                "root": f"{root['proto_sound']} -> {letter}",
                "letter": letter,
                "phoneme": letter,
                "duration": letter_duration(root, phonology),
                "meaning": f"{spec['name']}; {root['semantic_drift_path'][-1]}",
                "gesture": root["phonogestural_contour"]["hand_enactment"],
                "posture": root["phonogestural_contour"]["posture_enactment"],
                "bias": NEO_FAMILY[primary_bias(root)],
                "source": root["first_context"],
            }
        )
    return entries


def render_provisional_alphabet(roots: list[dict], phonology: dict) -> str:
    entries = provisional_alphabet_entries(roots, phonology)
    base_count = sum(1 for entry in entries if entry["kind"] == "base")
    extension_count = len(entries) - base_count
    lines = [
        "# Provisional IW Alphabet",
        "",
        "This is a provisional alphabet grown from individual roots and lightly evolved root forms.",
        "",
        "This intentionally does not collapse many roots into a small set of letters. The fast-forward attractors remain useful as a compression experiment, but the alphabet should preserve root-level richness before later Neo abstraction.",
        "",
        f"The current set has {base_count} base letters and {extension_count} derived extension letters. The spelling and phoneme columns are kept close on purpose so the system stays learnable.",
        "",
        "## Alphabet Table",
        "",
        "| Root | Letter | Phoneme | Meaning | Gesture |",
        "|---|---|---|---|---|",
    ]
    for entry in entries:
        lines.append(
            "| {root} | `{letter}` | `{phoneme}` | {meaning} | {gesture} |".format(
                root=entry["root"],
                letter=entry["letter"],
                phoneme=entry["phoneme"],
                meaning=entry["meaning"].replace("|", "/"),
                gesture=entry["gesture"].replace("|", "/"),
            )
        )

    lines.extend(["", "## Letter Notes", ""])
    for entry in entries:
        lines.extend(
            [
                f"### {entry['letter']}",
                "",
                f"- Kind: {entry['kind']}",
                f"- Root: `{entry['root']}`",
                f"- Phoneme: `{entry['phoneme']}`",
                f"- Duration pressure: {entry['duration']}",
                f"- Bias: {entry['bias']}",
                f"- Meaning: {entry['meaning']}",
                f"- Gesture: {entry['gesture']}",
                f"- Posture: {entry['posture']}",
                f"- Source pressure: {entry['source']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation",
            "",
            "This alphabet is intentionally under-compressed. Each root remains available as a potential letter, and only a few derived extensions have been added where ritual or danger would plausibly preserve a distinct evolved form.",
            "",
            "A later pass can add more letters by expanding the root corpus or by promoting additional evolved forms. Compression toward Neo should happen after this richer alphabet layer exists, not before it.",
        ]
    )
    return "\n".join(lines)


def neo_glyph_label(glyph_id: str) -> str:
    glyph = NEO_GLYPHS[glyph_id]
    return f"{glyph_id} {glyph['name']} ({glyph['magnitude']}, {glyph['role']})"


def neo_intensity(left: dict, right: dict) -> str:
    delta = abs(left["magnitude"] - right["magnitude"])
    if delta == 0:
        return "Resonance"
    if delta == 1:
        return "Modulation"
    return "Dominance"


def neo_pair_result(left_id: str, right_id: str) -> dict:
    left = NEO_GLYPHS[left_id]
    right = NEO_GLYPHS[right_id]
    matrix = AICME_INTERACTIONS[left["role"]][right["role"]]
    intensity = neo_intensity(left, right)
    return {
        "pair": f"{left_id}+{right_id}",
        "intensity": intensity,
        "matrix": matrix,
        "effect": AICME_EFFECTS[matrix],
        "reading": f"{intensity.lower()} {matrix.lower()}: {AICME_EFFECTS[matrix]}",
    }


def chord_weight(index: int, length: int) -> float:
    if index == 0:
        return 1.0
    if index == length - 1:
        return 0.9
    if index == 1:
        return 0.8
    return 0.6


def neo_chord_vector(glyph_ids: list[str]) -> dict[str, float]:
    vector = {"action": 0.0, "resistance": 0.0, "structure": 0.0, "modulation": 0.0, "transform": 0.0}
    for index, glyph_id in enumerate(glyph_ids):
        glyph = NEO_GLYPHS[glyph_id]
        contribution = glyph["magnitude"] * chord_weight(index, len(glyph_ids))
        if glyph["role"] == "action":
            vector["action"] += contribution
        elif glyph["role"] == "resistance":
            vector["resistance"] += contribution
        elif glyph["role"] == "binding":
            vector["structure"] += contribution
        elif glyph["role"] == "flow":
            vector["modulation"] += contribution
        elif glyph["role"] == "mutation":
            vector["transform"] += contribution
    return vector


def dominant_chord_dimension(vector: dict[str, float]) -> str:
    return max(vector, key=lambda key: vector[key])


def format_chord_vector(vector: dict[str, float]) -> str:
    return ", ".join(f"{key} {value:.1f}" for key, value in vector.items() if value)


def current_onsets_for_labels(roots: list[dict], labels: list[str]) -> list[str]:
    onsets = current_beginning_consonants(roots)
    matches = [onset for onset in onsets if SOUND_MANNERS.get(onset) in labels]
    return matches


def analogy_probe_forms(onsets: list[str], contours: list[str], limit: int = 6) -> list[str]:
    forms = []
    for onset in onsets:
        for contour in contours:
            forms.append(f"{onset}{contour}")
            if len(forms) == limit:
                return forms
    return forms


def sound_function_entries(roots: list[dict]) -> list[dict]:
    entries = []
    for onset in current_beginning_consonants(roots):
        glyph_ids = SOUND_TO_NEO[onset]
        vector = neo_chord_vector(glyph_ids)
        pair = neo_pair_result(glyph_ids[0], glyph_ids[1]) if len(glyph_ids) > 1 else None
        dominant = dominant_chord_dimension(vector)
        entries.append(
            {
                "onset": onset,
                "manner": SOUND_MANNERS[onset],
                "glyphs": glyph_ids,
                "glyph_labels": [neo_glyph_label(glyph_id) for glyph_id in glyph_ids],
                "primary_role": NEO_GLYPHS[glyph_ids[0]]["role"],
                "vector": vector,
                "dominant": dominant,
                "pair": pair,
            }
        )
    return entries


def phonetic_analogy_entries(roots: list[dict]) -> list[dict]:
    entries = []
    for analogy in MANNER_ANALOGIES:
        onsets = current_onsets_for_labels(roots, analogy["current_onset_labels"])
        examples = analogy_probe_forms(onsets, analogy["vowel_contours"])
        entries.append({**analogy, "current_onsets": onsets, "examples": examples})
    return entries


def render_phonetic_function_matrix(roots: list[dict]) -> str:
    entries = sound_function_entries(roots)
    role_order = ["action", "resistance", "binding", "flow", "mutation"]
    lines = [
        "# Phonetic Function Matrix",
        "",
        "This experiment maps consonant manners and current IW onsets onto Neo-style operations.",
        "",
        "It is deliberately provisional. It tests whether sound can carry functional pressure before the later Neo glyph system formalizes those pressures as Aicme, magnitude, pairwise interference, and multiglyph chord logic.",
        "",
        "Local Neo anchors used for this experiment:",
        "",
        "- `../../Neo/docs/Neo_Reference_Table.md`: glyph group, orientation, magnitude, and structural bias.",
        "- `../../Neo/Neo Signals/Pairwise_Interference_Logic.md`: Aicme interaction matrix and intensity rules.",
        "- `../../Neo/Neo Signals/Multi_Glyph_Logic.md`: chord vectors and position weighting.",
        "",
        "## Manner To Function",
        "",
        "| Manner | English consonants | IW function | Neo-role hypothesis | Possible use |",
        "|---|---|---|---|---|",
    ]
    for item in MANNER_FUNCTIONS:
        lines.append(
            "| {manner} | {english} | {function} | {roles} | {use} |".format(
                manner=item["manner"],
                english=item["english"],
                function=item["iw_function"],
                roles=item["neo_roles"],
                use=item["use"],
            )
        )

    lines.extend(
        [
            "",
            "## Aicme-Style Interaction Matrix",
            "",
            "Read this as a sound-function matrix: if one onset role meets another, the pair inherits the corresponding Neo-style operation.",
            "",
            "| Role | Action | Resistance | Binding | Flow | Mutation |",
            "|---|---|---|---|---|---|",
        ]
    )
    for left in role_order:
        cells = [AICME_INTERACTIONS[left][right] for right in role_order]
        lines.append(f"| {NEO_FAMILY[left]} | " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## Current Onsets As Functional Sounds",
            "",
            "| Onset | Manner | Neo glyph route | Primary role | Chord vector | Dominant field | Pair reading |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for entry in entries:
        pair_reading = entry["pair"]["reading"] if entry["pair"] else "single-glyph pressure"
        lines.append(
            "| `{onset}` | {manner} | {glyphs} | {role} | {vector} | {dominant} | {pair} |".format(
                onset=entry["onset"],
                manner=entry["manner"],
                glyphs=", ".join(entry["glyph_labels"]),
                role=NEO_FAMILY[entry["primary_role"]],
                vector=format_chord_vector(entry["vector"]),
                dominant=entry["dominant"],
                pair=pair_reading,
            )
        )

    lines.extend(
        [
            "",
            "## Cluster Probes",
            "",
            "Clusters are the most useful test case because they let an early sound act like a tiny Neo inscription.",
            "",
            "| Cluster | Glyph sequence | Pairwise operation | Chord reading | Naming implication |",
            "|---|---|---|---|---|",
        ]
    )
    cluster_implications = {
        "br": "A good candidate for names about vows, bridges, bloodlines, carried force, or action becoming structure.",
        "dr": "A good candidate for gates, laws, patient endurance, difficult craft, or resistance becoming structure.",
        "th": "A good candidate for thresholds, taboo edges, not-yet-safe matter, or boundary restraint.",
    }
    for entry in entries:
        if not entry["pair"]:
            continue
        lines.append(
            "| `{cluster}` | {glyphs} | {pair} | {vector}; dominant {dominant} | {implication} |".format(
                cluster=entry["onset"],
                glyphs=" + ".join(entry["glyph_labels"]),
                pair=entry["pair"]["reading"],
                vector=format_chord_vector(entry["vector"]),
                dominant=entry["dominant"],
                implication=cluster_implications.get(entry["onset"], "A possible specialist or fossilized cluster."),
            )
        )

    lines.extend(
        [
            "",
            "## What Happens",
            "",
            "- The current onset inventory is already biased toward action, resistance, and binding. That fits the world premise: survival speech begins with pressure, refusal, and relation before abstract flow is formalized.",
            "- `br` and `dr` become especially interesting. They are not just hard clusters; they read as action/resistance entering binding, which makes them plausible for names tied to vows, gates, craft, law, and load-bearing social forms.",
            "- `th` now carries the threshold family as reinforced resistance. That makes it useful for danger-remains, taboo edges, and boundaries that must be tested before crossing.",
            "- `w` has moved out of the root-onset set and into glide behavior around vowel pairs. It can still fossilize later, but it should not currently anchor a consonant root.",
            "- Vowels may be the main carriers of flow and mutation in early IW. Consonants set posture and contact; vowel contours decide whether the posture releases, holds, or transforms.",
            "",
            "## Next Experiment",
            "",
            "Use the vowel combination grid as the nucleus layer: onset function + vowel contour + optional coda. That would let `brua`, `drei`, `thae`, or `shao` produce a small Neo-like field profile without yet becoming a formal glyph string.",
        ]
    )
    return "\n".join(lines)


def render_neo_phonetic_analogy_matrix(roots: list[dict]) -> str:
    entries = phonetic_analogy_entries(roots)
    lines = [
        "# Neo Phonetic Analogy Matrix",
        "",
        "This experiment asks what each phonetic manner is in Neo terms.",
        "",
        "The mapping is not `sound = glyph`. It is `speech event = Neo interaction pattern`. A plosive is therefore not simply `P`; it is a closure-and-release event that can be modeled through operations like Opposition, Anchor, Propel, and Fracture.",
        "",
        "## Manner Analogies",
        "",
        "| Phonetic manner | Speech event | Neo interaction analog | Neo reading | Likely glyph families | Naming tendency |",
        "|---|---|---|---|---|---|",
    ]
    for entry in entries:
        lines.append(
            "| {manner} | {event} | {ops} | {reading} | {families} | {tendency} |".format(
                manner=entry["manner"],
                event=entry["speech_event"],
                ops=" -> ".join(entry["neo_analogy"]),
                reading=entry["neo_reading"],
                families=entry["glyph_families"],
                tendency=entry["naming_tendency"],
            )
        )

    lines.extend(
        [
            "",
            "## Current IW Hooks",
            "",
            "These hooks connect the analogy layer back to the current root-initial consonants and the vowel-combination grid.",
            "",
            "| Manner | Current onsets | Vowel-contour probes | Notes |",
            "|---|---|---|---|",
        ]
    )
    for entry in entries:
        onsets = ", ".join(f"`{onset}`" for onset in entry["current_onsets"]) or "none yet"
        examples = ", ".join(f"`{example}`" for example in entry["examples"]) or "needs future sound"
        if entry["id"] == "affricate":
            note = "Now seeded through `ch`, making release-friction available for sparks, snapped change, and danger-register forms."
        elif entry["id"] == "plosive":
            note = "`br` and `dr` are included because liquid clusters preserve the stop event while adding structure."
        elif entry["id"] == "approximant":
            note = "No consonant-root onset now; `w` is treated as a glide that emerges with vowel pairs."
        else:
            note = "Use these as sound-taste probes, not fixed lexical entries."
        lines.append(f"| {entry['manner']} | {onsets} | {examples} | {note} |")

    lines.extend(
        [
            "",
            "## Operation Gloss",
            "",
            "| Neo operation | Phonetic feel |",
            "|---|---|",
            "| Opposition | two articulatory pressures meet or block each other |",
            "| Anchor | closure is held long enough to become a state |",
            "| Propel | pressure releases as directed motion |",
            "| Fracture | closure breaks instead of smoothly opening |",
            "| Dampen | flow is resisted, narrowed, or muffled |",
            "| Distort | flow is shaped by noise or asymmetry |",
            "| Turbulence | airflow becomes unstable, mixed, or hissed |",
            "| Gate | an obstruction controls where sound can pass |",
            "| Stream | sound passes smoothly through an open contour |",
            "",
            "## Design Implication",
            "",
            "This gives the simulator a stronger middle layer: phonetic manner can become a rule-bearing function before the formal alphabet exists. Consonants set the event posture; vowels then determine whether that posture holds, releases, flows, or mutates.",
        ]
    )
    return "\n".join(lines)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")


def build_outputs() -> None:
    roots = load_json(DATA_DIR / "roots.seed.json")["roots"]
    phonology = load_json(DATA_DIR / "phonology.json")
    later_alphabet = load_json(DATA_DIR / "later_alphabet.json")
    phrase_probes = load_json(DATA_DIR / "phrase_probes.json")
    errors = validate_roots(roots)
    if errors:
        raise SystemExit("Validation failed:\n" + "\n".join(f"- {error}" for error in errors))

    write_text(OUTPUT_DIR / "root_ledger.md", render_root_ledger(roots, phonology))
    write_text(OUTPUT_DIR / "name_candidates.md", render_name_candidates(roots, phonology))
    write_text(OUTPUT_DIR / "proto_neo_bridge.md", render_proto_neo_bridge(roots))
    write_text(OUTPUT_DIR / "root_quality_report.md", render_root_quality_report(roots))
    write_text(OUTPUT_DIR / "sound_taste_report.md", render_sound_taste_report(roots, phonology))
    write_text(OUTPUT_DIR / "phrase_samples.md", render_phrase_samples(roots, phonology, phrase_probes))
    write_text(OUTPUT_DIR / "evolution_fastforward.md", render_evolution_fastforward(roots, phonology))
    alphabet_entries = provisional_alphabet_entries(roots, phonology)
    proto_words = generate_proto_words(roots, phonology)
    write_text(OUTPUT_DIR / "provisional_alphabet.md", render_provisional_alphabet(roots, phonology))
    write_text(OUTPUT_DIR / "proto_words.md", render_proto_words(proto_words, phonology))
    write_text(OUTPUT_DIR / "proto_word_collapse.md", render_proto_word_collapse(proto_words, alphabet_entries, phonology))
    stable_letter_entries = stable_letter_name_entries(roots, proto_words, phonology)
    write_text(OUTPUT_DIR / "stable_letter_names_experiment.md", render_stable_letter_names_experiment(roots, proto_words, phonology))
    vowel_grid_onsets = current_beginning_consonants(roots)
    vowel_grid_combos = vowel_combinations(phonology)
    write_text(OUTPUT_DIR / "vowel_combination_grid.md", render_vowel_consonant_grid(roots, phonology))
    sound_function_entries_list = sound_function_entries(roots)
    write_text(OUTPUT_DIR / "phonetic_function_matrix.md", render_phonetic_function_matrix(roots))
    phonetic_analogy_entries_list = phonetic_analogy_entries(roots)
    write_text(OUTPUT_DIR / "neo_phonetic_analogy_matrix.md", render_neo_phonetic_analogy_matrix(roots))
    alphabet_coverage = later_alphabet_coverage(roots, later_alphabet)
    write_text(OUTPUT_DIR / "later_alphabet_compression_audit.md", render_later_alphabet_compression(roots, later_alphabet))
    complete_alphabet = complete_alphabet_entries(later_alphabet)
    write_text(OUTPUT_DIR / "complete_later_alphabet.md", render_complete_later_alphabet(later_alphabet))
    first_lexicon_entries = lexicon_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    write_text(OUTPUT_DIR / "word_combination_ruleset.md", render_word_combination_ruleset())
    write_text(OUTPUT_DIR / "lexicon_first_batch.md", render_lexicon_first_batch(roots, proto_words, phonology, phrase_probes, later_alphabet))
    review_entries = lexicon_review_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
    write_text(OUTPUT_DIR / "lexicon_review.md", render_lexicon_review(roots, proto_words, phonology, phrase_probes, later_alphabet))
    write_text(OUTPUT_DIR / "lexicon_expansion_report.md", render_lexicon_expansion_report(roots, proto_words, phonology, phrase_probes, later_alphabet))
    clusters = alphabet_clusters(roots)

    manifest = {
        "root_count": len(roots),
        "proto_word_count": len(proto_words),
        "name_candidate_count": len(roots) * len(phonology["name_routes"]),
        "name_route_count": len(phonology["name_routes"]),
        "phrase_probe_count": len(phrase_probes["probes"]),
        "alphabet_attractor_count": len(clusters),
        "provisional_letter_count": len(alphabet_entries),
        "stable_letter_name_count": len(stable_letter_entries),
        "vowel_grid_onset_count": len(vowel_grid_onsets),
        "vowel_grid_probe_count": len(vowel_grid_onsets) * len(vowel_grid_combos),
        "phonetic_function_onset_count": len(sound_function_entries_list),
        "phonetic_analogy_count": len(phonetic_analogy_entries_list),
        "later_consonant_family_count": len(later_alphabet["consonant_families"]),
        "later_vowel_family_count": len(later_alphabet["vowel_families"]),
        "complete_later_alphabet_letter_count": len(complete_alphabet),
        "lexicon_first_batch_entry_count": len(first_lexicon_entries),
        "lexicon_review_status_counts": dict(Counter(entry["review_status"] for entry in review_entries)),
        "later_missing_consonant_families": alphabet_coverage["missing_consonants"],
        "later_missing_vowel_families": alphabet_coverage["missing_vowels"],
        "growth_plan": phonology["growth_plan"],
        "outputs": [
            "root_ledger.md",
            "name_candidates.md",
            "proto_neo_bridge.md",
            "root_quality_report.md",
            "sound_taste_report.md",
            "phrase_samples.md",
            "evolution_fastforward.md",
            "provisional_alphabet.md",
            "proto_words.md",
            "proto_word_collapse.md",
            "stable_letter_names_experiment.md",
            "vowel_combination_grid.md",
            "phonetic_function_matrix.md",
            "neo_phonetic_analogy_matrix.md",
            "later_alphabet_compression_audit.md",
            "complete_later_alphabet.md",
            "word_combination_ruleset.md",
            "lexicon_first_batch.md",
            "lexicon_review.md",
            "lexicon_expansion_report.md",
        ],
    }
    write_text(OUTPUT_DIR / "manifest.json", json.dumps(manifest, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic IW language simulator reports.")
    parser.parse_args()
    build_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
