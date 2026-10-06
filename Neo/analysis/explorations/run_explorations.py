#!/usr/bin/env python3
"""Neo signature explorations.

Runs five investigations on top of `neo_batch_signatures`:

    1. Translation invariance audit      -> 01_translation_invariance.{md,csv}
    2. Phase Shift / Turbulence probes   -> 02_phase_turbulence.{md,csv}
    3. Semantic-category mapping study   -> 03_semantic_categories.{md,csv}
    4. Chord-space clustering of corpus  -> 04_chord_clusters.{md,csv}
    5. Chord-space visualizations        -> 05_chord_visualizations.{html,csv}
    6. Controlled syntax tests           -> 06_controlled_syntax.{md,csv}
    7. Minimal pair studies              -> 07_minimal_pairs.{md,csv}

A consolidated REPORT.md ties the sections together. All outputs land in
this script's directory.
"""

from __future__ import annotations

import csv
import html
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev

SCRIPT_DIR = Path(__file__).resolve().parent
NEO_DIR = SCRIPT_DIR.parent.parent  # .../Neo
sys.path.insert(0, str(NEO_DIR))

from neo_batch_signatures import analyze_phrase  # noqa: E402

OUT_DIR = SCRIPT_DIR
CORPUS_CSV = NEO_DIR / "corpora" / "neo_phrase_corpus.csv"
ANALYSIS_MISSING_MODE = "canonical"
NATURAL_COLLECTIONS = {"seed", "expanded", "translation_added"}
LANG_ORDER = {"EN": 0, "LA": 1, "GA": 2, "NEO": 3}
CHORD_KEYS = ("action_net", "structure", "flow", "transform")
GROUP_KEYS = ("right", "left", "cross", "diagonal", "backslash")
ALL_INTERACTIONS = (
    "Reinforce", "Opposition", "Anchor", "Propel", "Distort",
    "Dampen", "Invert", "Crystalize", "Gate", "Fracture",
    "Stream", "Turbulence", "Phase Shift",
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def chord(sig: dict) -> dict:
    return sig["chord"]["word_aware"]["normalized"]


def raw_chord(sig: dict) -> dict:
    return sig["chord"]["word_aware"]["raw"]


def cosine(a: dict, b: dict) -> float:
    num = sum(a[k] * b[k] for k in CHORD_KEYS)
    da = math.sqrt(sum(a[k] * a[k] for k in CHORD_KEYS))
    db = math.sqrt(sum(b[k] * b[k] for k in CHORD_KEYS))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def euclid(a: dict, b: dict) -> float:
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in CHORD_KEYS))


def chord_str(c: dict) -> str:
    return ", ".join(f"{k}={c[k]:+.3f}" for k in CHORD_KEYS)


def group_share(sig: dict) -> dict:
    counts = sig["group_counts"]
    total = sum(counts.values()) or 1
    return {k: counts.get(k, 0) / total for k in GROUP_KEYS}


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_corpus_rows(
    *,
    collection: str | None = None,
    item_type: str | None = None,
    concept_id: str | None = None,
) -> list[dict]:
    with CORPUS_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if collection is not None:
        rows = [row for row in rows if row.get("collection") == collection]
    if item_type is not None:
        rows = [row for row in rows if row.get("item_type") == item_type]
    if concept_id is not None:
        rows = [row for row in rows if row.get("concept_id") == concept_id]
    return rows


def analyze_corpus_row(row: dict, *, missing_mode: str = ANALYSIS_MISSING_MODE) -> dict:
    sig = analyze_phrase(
        row["phrase"],
        source=row.get("corpus_id") or row.get("phrase"),
        missing_mode=missing_mode,
        metadata=row,
    )
    sig["_corpus_id"] = row.get("corpus_id", "")
    sig["_collection"] = row.get("collection", "")
    sig["_item_type"] = row.get("item_type", "")
    sig["_concept_id"] = row.get("concept_id", "")
    sig["_concept"] = row.get("concept", "")
    sig["_lang"] = row.get("language", "")
    sig["_provenance"] = row.get("provenance", "")
    sig["_status"] = row.get("status", "")
    sig["_notes"] = row.get("notes", "")
    return sig


def translation_groups() -> list[dict]:
    rows = [
        row for row in load_corpus_rows(item_type="phrase")
        if row.get("collection") in NATURAL_COLLECTIONS
    ]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("language") in {"EN", "LA", "GA"}:
            grouped[row["concept_id"]].append(row)

    groups = []
    for concept_id, members in grouped.items():
        languages = {row.get("language") for row in members}
        if len(languages) < 2:
            continue
        members.sort(key=lambda row: (LANG_ORDER.get(row.get("language", ""), 99), row.get("corpus_id", "")))
        groups.append(
            {
                "label": concept_id,
                "concept": members[0].get("concept") or concept_id,
                "members": members,
            }
        )
    return sorted(groups, key=lambda group: group["label"])


def probe_rows() -> list[dict]:
    return load_corpus_rows(collection="forfeda_probe", item_type="probe")


def semantic_category_rows() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in load_corpus_rows(collection="semantic_category", item_type="phrase"):
        grouped[row["concept_id"]].append(row)
    return {
        category: sorted(rows, key=lambda row: row.get("corpus_id", ""))
        for category, rows in sorted(grouped.items())
    }


def cluster_corpus_rows() -> list[dict]:
    rows = [
        row for row in load_corpus_rows(item_type="phrase")
        if row.get("collection") in NATURAL_COLLECTIONS
    ]
    return sorted(rows, key=lambda row: row.get("corpus_id", ""))


def controlled_syntax_rows() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in load_corpus_rows(collection="controlled_syntax", item_type="phrase"):
        grouped[row["concept_id"]].append(row)
    return {
        frame: sorted(rows, key=lambda row: row.get("corpus_id", ""))
        for frame, rows in sorted(grouped.items())
    }


def minimal_pair_rows() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in load_corpus_rows(collection="minimal_pair"):
        grouped[row["concept_id"]].append(row)
    return {
        family: sorted(rows, key=lambda row: row.get("corpus_id", ""))
        for family, rows in sorted(grouped.items())
    }


def note_value(row: dict, key: str) -> str:
    parts = (row.get("notes") or "").split()
    for index, part in enumerate(parts):
        if part == key and index + 1 < len(parts):
            return parts[index + 1]
    return ""


# ---------------------------------------------------------------------------
# Task 1: Translation invariance audit
# ---------------------------------------------------------------------------

# Each entry: label, concept, members[(language, phrase, provenance)]
# provenance "corpus" = already in sample_phrases.txt, "added" = freshly added
# for this audit and not vetted by a native speaker.
TRIPLETS = [
    {
        "label": "war_breaks_gate",
        "concept": "war breaks the gate",
        "members": [
            ("EN", "WAR BREAKS THE GATE", "corpus"),
            ("LA", "BELLUM PORTA FRANGIT", "corpus"),
            ("GA", "BRISEANN COGADH AN GEATA", "corpus"),
        ],
    },
    {
        "label": "memory_holds_stone",
        "concept": "memory holds the stone / river remembers",
        "members": [
            ("EN", "THE RIVER REMEMBERS THE STONE", "corpus"),
            ("LA", "MEMORIA LAPIDEM TENET", "corpus"),
            ("GA", "IS CUIMHIN LEIS AN ABHAINN", "corpus"),
        ],
    },
    {
        "label": "memory_opens_gate",
        "concept": "memory opens the gate",
        "members": [
            ("EN", "MEMORY OPENS A HIDDEN GATE", "corpus"),
            ("LA", "MEMORIA PORTAM ABDITAM APERIT", "added"),
            ("GA", "OSCLAIONN CUIMHNE AN GEATA", "corpus"),
        ],
    },
    {
        "label": "freedom_opens_door",
        "concept": "freedom opens the door",
        "members": [
            ("EN", "FREEDOM OPENS THE DOOR", "added"),
            ("LA", "LIBERTAS PORTAM APERIT", "corpus"),
            ("GA", "OSCLAIONN SAOIRSE AN DORAS", "added"),
        ],
    },
    {
        "label": "light_breaks_darkness",
        "concept": "light breaks the darkness",
        "members": [
            ("EN", "LIGHT BREAKS THE DARKNESS", "added"),
            ("LA", "LUX TENEBRAS FRANGIT", "added"),
            ("GA", "BRISEANN SOLAS AN DORCHADAS", "corpus"),
        ],
    },
    {
        "label": "care_bends_friction",
        "concept": "care bends friction towards freedom",
        "members": [
            ("EN", "CARE BENDS FRICTION TOWARDS FREEDOM", "corpus"),
            ("LA", "CURA FRICTIONEM AD LIBERTATEM FLECTIT", "corpus"),
        ],
    },
    {
        "label": "water_teaches_fire",
        "concept": "water/fire teaching pair (subjects flipped)",
        "members": [
            ("EN", "FIRE TEACHES WATER TO TURN", "corpus"),
            ("LA", "AQUA IGNEM DOCET", "corpus"),
        ],
    },
]


def task1_translation_invariance() -> dict:
    rows: list[dict] = []
    triplet_summaries: list[dict] = []

    for triplet in translation_groups():
        signatures = []
        for row in triplet["members"]:
            sig = analyze_corpus_row(row, missing_mode=ANALYSIS_MISSING_MODE)
            signatures.append(sig)

        # Pairwise distances across the triplet
        pair_distances = []
        for i, a in enumerate(signatures):
            for b in signatures[i + 1 :]:
                pair_distances.append(
                    {
                        "label": triplet["label"],
                        "a_lang": a["_lang"],
                        "b_lang": b["_lang"],
                        "a_dominant": a["dominant_interaction"],
                        "b_dominant": b["dominant_interaction"],
                        "dominant_match": a["dominant_interaction"] == b["dominant_interaction"],
                        "cosine": round(cosine(chord(a), chord(b)), 4),
                        "euclid": round(euclid(chord(a), chord(b)), 4),
                        "entropy_delta": round(abs(a["interaction_entropy"] - b["interaction_entropy"]), 4),
                        "disrupt_delta": abs(a["disruptive_event_count"] - b["disruptive_event_count"]),
                    }
                )

        # Per-member rows
        for sig in signatures:
            c = chord(sig)
            grp = group_share(sig)
            rows.append(
                {
                    "concept": triplet["label"],
                    "language": sig["_lang"],
                    "provenance": sig["_provenance"],
                    "phrase": sig["phrase"],
                    "glyph_count": sig["glyph_count"],
                    "dominant": sig["dominant_interaction"],
                    "dominant_count": sig["dominant_interaction_count"],
                    "disruptive_events": sig["disruptive_event_count"],
                    "entropy": sig["interaction_entropy"],
                    "chord_action_net": round(c["action_net"], 4),
                    "chord_structure": round(c["structure"], 4),
                    "chord_flow": round(c["flow"], 4),
                    "chord_transform": round(c["transform"], 4),
                    "group_right": round(grp["right"], 3),
                    "group_left": round(grp["left"], 3),
                    "group_cross": round(grp["cross"], 3),
                    "group_diagonal": round(grp["diagonal"], 3),
                    "group_backslash": round(grp["backslash"], 3),
                }
            )

        # Triplet summary
        avg_cos = mean(p["cosine"] for p in pair_distances) if pair_distances else 0.0
        avg_euc = mean(p["euclid"] for p in pair_distances) if pair_distances else 0.0
        dom_unique = len({p["b_dominant"] for p in pair_distances} | {p["a_dominant"] for p in pair_distances})
        triplet_summaries.append(
            {
                "label": triplet["label"],
                "concept": triplet["concept"],
                "n_members": len(signatures),
                "avg_cosine": round(avg_cos, 4),
                "avg_euclid": round(avg_euc, 4),
                "distinct_dominants": dom_unique,
                "pairs": pair_distances,
                "signatures": signatures,
            }
        )

    # CSV
    csv_path = OUT_DIR / "01_translation_invariance.csv"
    write_csv(
        csv_path,
        rows,
        fieldnames=list(rows[0].keys()),
    )

    # Markdown
    md_lines = [
        "# Task 1: Translation Invariance Audit",
        "",
        "How similar are signatures of the same concept across English (EN), Latin (LA), and Irish (GA)?",
        "",
        "Cosine similarity is computed over the normalized word-aware chord vector "
        "`(action_net, structure, flow, transform)`. 1.0 = identical direction, "
        "0.0 = orthogonal, negative = opposite direction.",
        "",
        f"Groups are read from `{CORPUS_CSV.name}`. Rows marked `experimental` have not "
        "been vetted by a native speaker; they are usable for orthography-driven "
        "signature analysis but should not be cited as canonical translations.",
        "",
        "## Per-triplet summary (sorted least to most invariant by avg cosine)",
        "",
        "| Concept | Members | Avg cosine | Avg Euclid | Distinct dominants |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for summary in sorted(triplet_summaries, key=lambda s: s["avg_cosine"]):
        md_lines.append(
            f"| {summary['concept']} | {summary['n_members']} | "
            f"{summary['avg_cosine']:+.3f} | {summary['avg_euclid']:.3f} | "
            f"{summary['distinct_dominants']} |"
        )

    md_lines.extend(["", "## Per-triplet detail", ""])
    for summary in triplet_summaries:
        md_lines.append(f"### {summary['concept']}")
        md_lines.append("")
        md_lines.append("| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for sig in summary["signatures"]:
            c = chord(sig)
            md_lines.append(
                f"| {sig['_lang']} | {sig['phrase']} | {sig['dominant_interaction']} ({sig['dominant_interaction_count']}) | "
                f"{sig['disruptive_event_count']} | {sig['interaction_entropy']:.2f} | "
                f"({c['action_net']:+.2f}, {c['structure']:+.2f}, {c['flow']:+.2f}, {c['transform']:+.2f}) |"
            )
        md_lines.append("")
        md_lines.append("Pairs:")
        md_lines.append("")
        for pair in summary["pairs"]:
            tag = "MATCH" if pair["dominant_match"] else "DIVERGE"
            md_lines.append(
                f"- {pair['a_lang']} vs {pair['b_lang']}: cosine={pair['cosine']:+.3f}, "
                f"euclid={pair['euclid']:.3f}, dominants `{pair['a_dominant']}`/`{pair['b_dominant']}` ({tag})"
            )
        md_lines.append("")

    # Aggregate findings
    domain_match_rate = mean(
        1.0 if p["dominant_match"] else 0.0
        for s in triplet_summaries for p in s["pairs"]
    )
    avg_cos_all = mean(p["cosine"] for s in triplet_summaries for p in s["pairs"])
    avg_euc_all = mean(p["euclid"] for s in triplet_summaries for p in s["pairs"])

    md_lines.extend([
        "## Aggregate",
        "",
        f"- Triplets/pairs analyzed: {len(triplet_summaries)}",
        f"- Total cross-language pairs: {sum(len(s['pairs']) for s in triplet_summaries)}",
        f"- Mean cosine across all pairs: {avg_cos_all:+.3f}",
        f"- Mean Euclidean distance: {avg_euc_all:.3f}",
        f"- Dominant-interaction match rate: {domain_match_rate*100:.1f}%",
        "",
    ])

    (OUT_DIR / "01_translation_invariance.md").write_text("\n".join(md_lines), encoding="utf-8")

    return {
        "summaries": triplet_summaries,
        "avg_cosine": avg_cos_all,
        "avg_euclid": avg_euc_all,
        "match_rate": domain_match_rate,
    }


# ---------------------------------------------------------------------------
# Task 2: Phase Shift / Turbulence probes
# ---------------------------------------------------------------------------

# Probes: synthetic phrases designed to fire the rare interaction cells.
# Comments next to each probe describe the intended glyph parse (greedy
# 2-char first per `transliterate_neo_text`).
PROBES = [
    # ---- Pure Phase Shift (Backslash + Backslash) ----
    ("AEUI",       "phase_shift_min", "AE -> UI : single Phase Shift event"),
    ("AEAEAE",     "phase_shift_chain", "AE -> AE -> AE : 2 Phase Shifts in a row"),
    ("UIEAIO",     "phase_shift_climb", "UI -> EA -> IO : 2 Phase Shifts ascending magnitude"),
    ("OIAEUIEA",   "phase_shift_walk", "OI -> AE -> UI -> EA : 3 consecutive Phase Shifts"),
    # ---- Pure Turbulence (Diagonal + Backslash) ----
    ("AEA",        "turbulence_min", "AE -> A : Backslash->Diagonal = Turbulence"),
    ("AAE",        "turbulence_min_rev", "A -> AE : Diagonal->Backslash = Turbulence"),
    ("IEAU",       "turbulence_chain", "I -> EA -> U : Turbulence x2"),
    ("OIOOIO",     "turbulence_oscillate", "OI -> O -> OI -> O : alternating pairs (Turbulence + Turbulence + Turbulence)"),
    # ---- Mixed: structure-breaking phrases ----
    ("FAEUIEA",    "distort_then_phase", "F -> AE -> UI -> EA : Distort then Phase Shift x2"),
    ("RAEIO",      "fracture_then_phase", "R -> AE -> IO : Fracture then Phase Shift"),
    ("MIOAE",      "fracture_then_turb_phase", "M -> IO -> AE : Fracture, Phase Shift"),
    ("BEAOIIO",    "distort_chain", "B -> EA -> OI -> IO : Distort, Phase Shift x2"),
    # ---- Natural-ish multi-word probes ----
    ("AEUI EAIO OIAE",       "phase_shift_phrase", "Three short tokens, each Phase-Shift dense"),
    ("TAE OIO UIEA",         "mixed_natural", "Looks word-like but heavy Forfeda load"),
    ("AOEAIOU",              "vowel_storm", "Pure vowels, mixes Diag and Backslash heavily"),
]


def task2_phase_turbulence() -> dict:
    rows: list[dict] = []
    detail_blocks: list[str] = []

    cell_totals = Counter()

    for row in probe_rows():
        phrase = row["phrase"]
        probe_id = row["concept_id"]
        intent = row.get("notes") or row.get("concept") or probe_id
        sig = analyze_corpus_row(row, missing_mode="strict")

        interactions = sig["interaction_counts"]
        for k, v in interactions.items():
            cell_totals[k] += v

        rows.append(
            {
                "probe_id": probe_id,
                "phrase": phrase,
                "intent": intent,
                "glyph_sequence": " ".join(sig["glyph_sequence"]),
                "glyph_count": sig["glyph_count"],
                "phase_shift": interactions.get("Phase Shift", 0),
                "turbulence": interactions.get("Turbulence", 0),
                "fracture": interactions.get("Fracture", 0),
                "distort": interactions.get("Distort", 0),
                "invert": interactions.get("Invert", 0),
                "all_interactions": "; ".join(
                    f"{k}={v}" for k, v in sorted(interactions.items())
                ),
                "dominant": sig["dominant_interaction"],
                "entropy": sig["interaction_entropy"],
                "chord_transform": round(chord(sig)["transform"], 4),
                "chord_flow": round(chord(sig)["flow"], 4),
            }
        )

        detail_blocks.append(
            "\n".join([
                f"### `{phrase}`  ({probe_id})",
                "",
                f"- Intent: {intent}",
                f"- Glyph parse: `{' '.join(sig['glyph_sequence'])}`",
                f"- Pair events: " + ", ".join(
                    f"`{e['pair']}`={e['interaction']}" for e in sig["pair_events"]
                ),
                f"- Interaction counts: " + ", ".join(
                    f"{k}={v}" for k, v in sorted(interactions.items())
                ),
                f"- Chord: {chord_str(chord(sig))}",
                "",
            ])
        )

    write_csv(
        OUT_DIR / "02_phase_turbulence.csv",
        rows,
        fieldnames=list(rows[0].keys()),
    )

    md_lines = [
        "# Task 2: Phase Shift / Turbulence Probes",
        "",
        "Phase Shift (Backslash + Backslash) and Turbulence (Diagonal + Backslash) "
        "are sparse in natural corpus rows. This task reads synthetic probes from "
        f"`{CORPUS_CSV.name}`, confirms those matrix cells are reachable, and observes "
        "what kind of chord the Forfeda glyphs produce when concentrated.",
        "",
        "Probes use `--missing strict` (no transliteration), so the parse is unambiguous.",
        "",
        "## Hits per interaction across all probes",
        "",
    ]
    for k in ALL_INTERACTIONS:
        md_lines.append(f"- {k}: {cell_totals.get(k, 0)}")
    md_lines.extend([
        "",
        "## Per-probe detail",
        "",
    ])
    md_lines.extend(detail_blocks)

    # Reachability check
    phase_total = cell_totals.get("Phase Shift", 0)
    turb_total = cell_totals.get("Turbulence", 0)
    md_lines.extend([
        "## Reachability conclusion",
        "",
        f"- Phase Shift events fired: **{phase_total}**",
        f"- Turbulence events fired: **{turb_total}**",
        "",
        "Both rare cells are reachable from the existing transliteration pipeline once "
        "Forfeda digraphs (AE/OI/UI/EA/IO) are introduced. They are effectively absent "
        "from natural English/Latin/Irish prose because the digraphs only appear sparsely "
        "and almost never adjacent. This means the matrix cells are sound but live in a "
        "'ritual register' of intentional Forfeda-heavy inscription.",
        "",
    ])

    (OUT_DIR / "02_phase_turbulence.md").write_text("\n".join(md_lines), encoding="utf-8")

    return {
        "totals": cell_totals,
        "probes": rows,
    }


# ---------------------------------------------------------------------------
# Task 5: Semantic-category mapping study
# ---------------------------------------------------------------------------

CATEGORIES = {
    "motion": [
        "THE BIRD FLIES SOUTH",
        "THE RIVER RUNS TO THE SEA",
        "THE ARROW SEEKS THE TREE",
        "THE WOLF CHASES THE DEER",
        "THE WIND CARRIES THE SEED",
    ],
    "containment": [
        "THE JAR HOLDS THE HONEY",
        "THE NEST CRADLES THE EGG",
        "THE WALL KEEPS THE GARDEN",
        "THE CUP RECEIVES THE WINE",
        "THE CAVE HIDES THE BEAR",
    ],
    "breakage": [
        "THE GLASS SHATTERS ON THE FLOOR",
        "THE BONE SNAPS UNDER WEIGHT",
        "THE BRIDGE COLLAPSES IN THE STORM",
        "THE ICE CRACKS BENEATH THE BOOT",
        "THE WALL CRUMBLES INTO DUST",
    ],
    "waiting": [
        "THE OWL WAITS FOR THE NIGHT",
        "THE STONE LIES ON THE PATH",
        "THE CANDLE REMAINS UNLIT",
        "THE HOUSE SLEEPS AT DAWN",
        "THE LETTER RESTS ON THE TABLE",
    ],
    "opening": [
        "THE DOOR OPENS TO THE GARDEN",
        "THE BOOK REVEALS A SECRET",
        "THE EYE OPENS TO THE SKY",
        "THE MAP UNFOLDS THE WORLD",
        "THE FLOWER OPENS AT MORNING",
    ],
}


def random_cohesion_baseline(corpus_chords: list[dict], subset_size: int, n_samples: int = 500, seed: int = 13) -> dict:
    """Mean within-subset cosine for random subsets of given size; serves as a 'noise floor'
    for judging whether semantic-category cohesion is meaningfully above the corpus baseline.
    """
    import random

    rng = random.Random(seed)
    sample_means: list[float] = []
    for _ in range(n_samples):
        subset = rng.sample(corpus_chords, subset_size)
        pair_cos: list[float] = []
        for i, a in enumerate(subset):
            for b in subset[i + 1 :]:
                pair_cos.append(cosine(a, b))
        if pair_cos:
            sample_means.append(mean(pair_cos))
    return {
        "mean": mean(sample_means),
        "stdev": pstdev(sample_means),
        "p05": sorted(sample_means)[int(n_samples * 0.05)],
        "p95": sorted(sample_means)[int(n_samples * 0.95)],
    }


def task5_semantic_categories(corpus_chords: list[dict] | None = None) -> dict:
    rows: list[dict] = []
    category_blocks: list[str] = []
    category_summaries: list[dict] = []

    # Compute noise floor for baseline if corpus chords supplied
    noise_floor = None
    if corpus_chords:
        noise_floor = random_cohesion_baseline(corpus_chords, subset_size=5, n_samples=500)

    categories = semantic_category_rows()

    for category, rows_for_category in categories.items():
        signatures = [
            analyze_corpus_row(row, missing_mode=ANALYSIS_MISSING_MODE)
            for row in rows_for_category
        ]

        # Per-phrase rows
        for sig in signatures:
            c = chord(sig)
            rows.append(
                {
                    "category": category,
                    "phrase": sig["phrase"],
                    "glyph_count": sig["glyph_count"],
                    "dominant": sig["dominant_interaction"],
                    "dominant_count": sig["dominant_interaction_count"],
                    "disruptive_events": sig["disruptive_event_count"],
                    "entropy": sig["interaction_entropy"],
                    "chord_action_net": round(c["action_net"], 4),
                    "chord_structure": round(c["structure"], 4),
                    "chord_flow": round(c["flow"], 4),
                    "chord_transform": round(c["transform"], 4),
                }
            )

        # Within-category metrics
        chords = [chord(s) for s in signatures]
        means = {k: mean(c[k] for c in chords) for k in CHORD_KEYS}
        stds = {k: pstdev(c[k] for c in chords) for k in CHORD_KEYS}

        # Within-category cosine similarity (mean over all pairs)
        pair_cos = []
        for i, a in enumerate(chords):
            for b in chords[i + 1 :]:
                pair_cos.append(cosine(a, b))
        avg_cos = mean(pair_cos) if pair_cos else 1.0

        dominant_counter = Counter(s["dominant_interaction"] for s in signatures)
        most_common_dom, dom_count = dominant_counter.most_common(1)[0]

        category_summaries.append(
            {
                "category": category,
                "members": len(signatures),
                "mean_chord": means,
                "std_chord": stds,
                "within_avg_cosine": avg_cos,
                "dominant_consensus": most_common_dom,
                "dominant_consensus_count": dom_count,
                "dominant_distribution": dominant_counter,
            }
        )

        # Markdown block
        category_blocks.append(
            "\n".join([
                f"### {category}",
                "",
                "| Phrase | Dominant | Disrupt | Entropy | Chord |",
                "| :--- | :--- | :--- | :--- | :--- |",
                *[
                    f"| {s['phrase']} | {s['dominant_interaction']} ({s['dominant_interaction_count']}) | "
                    f"{s['disruptive_event_count']} | {s['interaction_entropy']:.2f} | "
                    f"({chord(s)['action_net']:+.2f}, {chord(s)['structure']:+.2f}, "
                    f"{chord(s)['flow']:+.2f}, {chord(s)['transform']:+.2f}) |"
                    for s in signatures
                ],
                "",
                f"- Mean chord: {chord_str(means)}",
                f"- Std-dev:    {chord_str(stds)}",
                f"- Within-category avg cosine similarity: {avg_cos:+.3f}",
                f"- Dominant interaction consensus: `{most_common_dom}` ({dom_count}/{len(signatures)})",
                f"- Dominant distribution: " + ", ".join(f"{k}={v}" for k, v in dominant_counter.most_common()),
                "",
            ])
        )

    write_csv(
        OUT_DIR / "03_semantic_categories.csv",
        rows,
        fieldnames=list(rows[0].keys()),
    )

    # Cross-category centroids
    centroid_rows = []
    for summary in category_summaries:
        centroid_rows.append(
            {
                "category": summary["category"],
                **{f"mean_{k}": round(summary["mean_chord"][k], 4) for k in CHORD_KEYS},
                **{f"std_{k}": round(summary["std_chord"][k], 4) for k in CHORD_KEYS},
                "within_avg_cosine": round(summary["within_avg_cosine"], 4),
                "dominant_consensus": summary["dominant_consensus"],
                "dominant_consensus_count": summary["dominant_consensus_count"],
            }
        )
    write_csv(
        OUT_DIR / "03_semantic_categories_centroids.csv",
        centroid_rows,
        fieldnames=list(centroid_rows[0].keys()),
    )

    # Cross-centroid cosine
    cat_names = [s["category"] for s in category_summaries]
    cross_lines = ["| | " + " | ".join(cat_names) + " |", "| :--- |" + " :--- |" * len(cat_names)]
    for i, a in enumerate(category_summaries):
        cells = []
        for j, b in enumerate(category_summaries):
            cells.append(f"{cosine(a['mean_chord'], b['mean_chord']):+.2f}")
        cross_lines.append(f"| **{a['category']}** | " + " | ".join(cells) + " |")

    md_lines = [
        "# Task 5: Semantic-Category Mapping Study",
        "",
        f"{len(categories)} hand-authored categories "
        f"({sum(len(rows) for rows in categories.values())} phrases total) test whether Neo "
        "signatures cluster by *meaning*. For each category we report mean chord, "
        "std-dev, within-category cosine similarity, and dominant-interaction consensus.",
        "",
        f"All phrases run with `--missing {ANALYSIS_MISSING_MODE}`.",
        "",
    ]

    if noise_floor is not None:
        md_lines.extend([
            "## Noise floor",
            "",
            "To judge whether category cohesion is meaningful, we draw 500 random 5-phrase "
            "subsets from the structured natural/translation corpus and compute their within-subset "
            "cosine similarity. This is the *baseline* a category must beat to count as "
            "semantically cohesive in chord space.",
            "",
            f"- Random 5-subset cosine: mean **{noise_floor['mean']:+.3f}** "
            f"(stdev {noise_floor['stdev']:.3f}; 5th percentile {noise_floor['p05']:+.3f}; "
            f"95th percentile {noise_floor['p95']:+.3f})",
            "",
            "Read the consistency table below in light of this baseline: a category with "
            f"within-avg cosine close to **{noise_floor['mean']:+.3f}** is no more cohesive "
            "than a random handful of phrases.",
            "",
        ])

    md_lines.extend([
        "## Cross-category centroid cosine matrix",
        "",
        *cross_lines,
        "",
        "If categories truly differed by meaning, this matrix would have low off-diagonal "
        "values. In practice the off-diagonal values sit in the **+0.95 to +1.00** band, "
        "showing that all five category centroids point in essentially the same direction "
        "in chord space.",
        "",
        "## Per-category detail",
        "",
        *category_blocks,
        "",
        "## Consistency ranking (highest within-category cosine = most internally coherent)",
        "",
        "| Category | Within-avg cosine | Above noise floor? | Dominant consensus | Std (action,struct,flow,transform) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for s in sorted(category_summaries, key=lambda x: -x["within_avg_cosine"]):
        std_str = "(" + ", ".join(f"{s['std_chord'][k]:.2f}" for k in CHORD_KEYS) + ")"
        if noise_floor is not None:
            above = s["within_avg_cosine"] - noise_floor["mean"]
            note = f"{above:+.3f} vs baseline"
        else:
            note = "n/a"
        md_lines.append(
            f"| {s['category']} | {s['within_avg_cosine']:+.3f} | {note} | "
            f"`{s['dominant_consensus']}` ({s['dominant_consensus_count']}/{s['members']}) | {std_str} |"
        )

    (OUT_DIR / "03_semantic_categories.md").write_text("\n".join(md_lines), encoding="utf-8")

    return {"summaries": category_summaries, "noise_floor": noise_floor}


# ---------------------------------------------------------------------------
# Task 6: Chord-space clustering of the structured phrase corpus
# ---------------------------------------------------------------------------


def load_corpus_signatures() -> list[dict]:
    return [
        analyze_corpus_row(row, missing_mode="sensitivity")
        for row in cluster_corpus_rows()
    ]


def kmeans(points: list[list[float]], k: int, max_iter: int = 200, seed: int = 13) -> tuple[list[int], list[list[float]]]:
    """Tiny stdlib K-means for low-dimensional points."""
    import random

    rng = random.Random(seed)
    if not points:
        return [], []

    # K-means++ seeding
    centers = [list(points[rng.randrange(len(points))])]
    while len(centers) < k:
        d2 = [min(sum((p[i] - c[i]) ** 2 for i in range(len(p))) for c in centers) for p in points]
        total = sum(d2) or 1.0
        r = rng.random() * total
        cum = 0.0
        for idx, w in enumerate(d2):
            cum += w
            if cum >= r:
                centers.append(list(points[idx]))
                break

    assignments = [0] * len(points)
    for _ in range(max_iter):
        # Assignment step
        new_assign = []
        for p in points:
            best = 0
            best_d = float("inf")
            for ci, c in enumerate(centers):
                d = sum((p[i] - c[i]) ** 2 for i in range(len(p)))
                if d < best_d:
                    best_d = d
                    best = ci
            new_assign.append(best)
        if new_assign == assignments:
            break
        assignments = new_assign

        # Update step
        new_centers = []
        for ci in range(k):
            members = [points[i] for i in range(len(points)) if assignments[i] == ci]
            if not members:
                new_centers.append(list(points[rng.randrange(len(points))]))
            else:
                new_centers.append([
                    sum(m[d] for m in members) / len(members) for d in range(len(members[0]))
                ])
        centers = new_centers

    return assignments, centers


def task6_chord_clusters() -> dict:
    signatures = load_corpus_signatures()
    points = [[chord(s)[k] for k in CHORD_KEYS] for s in signatures]

    # Corpus centroid
    centroid = {k: mean(chord(s)[k] for s in signatures) for k in CHORD_KEYS}

    # K=4 cluster (one per chord dimension hypothesis)
    assignments, centers = kmeans(points, k=4)

    # Build cluster summaries
    clusters: dict[int, list[dict]] = defaultdict(list)
    for sig, cluster_id in zip(signatures, assignments):
        clusters[cluster_id].append(sig)

    # Per-cluster mean
    cluster_summaries = []
    for cid in sorted(clusters):
        members = clusters[cid]
        ms = [chord(s) for s in members]
        means = {k: mean(c[k] for c in ms) for k in CHORD_KEYS}
        # Label cluster by largest *deviation* from corpus centroid (more informative
        # than absolute coordinates because the whole corpus is flow-positive).
        deltas = {k: means[k] - centroid[k] for k in CHORD_KEYS}
        ordered = sorted(deltas.items(), key=lambda kv: abs(kv[1]), reverse=True)
        sign = "+" if ordered[0][1] >= 0 else "-"
        label = f"{sign}d_{ordered[0][0]}"
        # Secondary descriptor: language tilt of cluster members
        lang_counts = Counter()
        for sig in members:
            lang_counts[sig.get("_lang", "") or "UNKNOWN"] += 1
        cluster_summaries.append(
            {
                "id": cid,
                "label": label,
                "size": len(members),
                "mean_chord": means,
                "delta": deltas,
                "lang_mix": lang_counts,
                "members": members,
            }
        )

    # Sort phrases by each axis
    by_axis = {}
    for k in CHORD_KEYS:
        ranked = sorted(signatures, key=lambda s: chord(s)[k])
        by_axis[k] = {
            "low5": [(round(chord(s)[k], 4), s["phrase"]) for s in ranked[:5]],
            "high5": [(round(chord(s)[k], 4), s["phrase"]) for s in ranked[-5:][::-1]],
        }

    by_centroid = sorted(
        signatures, key=lambda s: euclid(chord(s), centroid)
    )
    closest = [(round(euclid(chord(s), centroid), 4), s["phrase"]) for s in by_centroid[:5]]
    farthest = [(round(euclid(chord(s), centroid), 4), s["phrase"]) for s in by_centroid[-5:][::-1]]

    # Nearest neighbors (cosine) for every phrase
    neighbor_rows = []
    for sig in signatures:
        scored = [
            (cosine(chord(sig), chord(other)), other["phrase"])
            for other in signatures if other is not sig
        ]
        scored.sort(reverse=True)
        neighbors = scored[:3]
        neighbor_rows.append(
            {
                "corpus_id": sig.get("_corpus_id", ""),
                "collection": sig.get("_collection", ""),
                "concept_id": sig.get("_concept_id", ""),
                "language": sig.get("_lang", ""),
                "phrase": sig["phrase"],
                "neighbor_1": neighbors[0][1] if neighbors else "",
                "neighbor_1_cos": round(neighbors[0][0], 4) if neighbors else 0.0,
                "neighbor_2": neighbors[1][1] if len(neighbors) > 1 else "",
                "neighbor_2_cos": round(neighbors[1][0], 4) if len(neighbors) > 1 else 0.0,
                "neighbor_3": neighbors[2][1] if len(neighbors) > 2 else "",
                "neighbor_3_cos": round(neighbors[2][0], 4) if len(neighbors) > 2 else 0.0,
            }
        )
    write_csv(
        OUT_DIR / "04_chord_neighbors.csv",
        neighbor_rows,
        fieldnames=list(neighbor_rows[0].keys()),
    )

    # Cluster CSV
    cluster_rows = []
    for c in cluster_summaries:
        for sig in c["members"]:
            ch = chord(sig)
            cluster_rows.append(
                {
                    "cluster_id": c["id"],
                    "cluster_label": c["label"],
                    "corpus_id": sig.get("_corpus_id", ""),
                    "collection": sig.get("_collection", ""),
                    "concept_id": sig.get("_concept_id", ""),
                    "language": sig.get("_lang", ""),
                    "phrase": sig["phrase"],
                    "dominant": sig["dominant_interaction"],
                    "chord_action_net": round(ch["action_net"], 4),
                    "chord_structure": round(ch["structure"], 4),
                    "chord_flow": round(ch["flow"], 4),
                    "chord_transform": round(ch["transform"], 4),
                    "distance_to_centroid": round(
                        math.sqrt(sum((ch[k] - c["mean_chord"][k]) ** 2 for k in CHORD_KEYS)), 4
                    ),
                }
            )
    write_csv(
        OUT_DIR / "04_chord_clusters.csv",
        cluster_rows,
        fieldnames=list(cluster_rows[0].keys()),
    )

    # Markdown
    md_lines = [
        "# Task 6: Chord-Space Clustering",
        "",
        f"K-means (K=4) on the normalized word-aware chord vectors of the "
        f"{len(signatures)}-phrase structured natural/translation corpus, "
        "plus per-axis rankings and centroid-distance extremes.",
        "",
        "## Corpus centroid",
        "",
        f"- {chord_str(centroid)}",
        "",
        "## K-means clusters (K=4)",
        "",
    ]
    for c in cluster_summaries:
        lang_str = ", ".join(f"{k}={v}" for k, v in c["lang_mix"].most_common())
        md_lines.append(f"### Cluster {c['id']}: `{c['label']}` ({c['size']} members; lang mix {lang_str})")
        md_lines.append(f"- Mean chord: {chord_str(c['mean_chord'])}")
        md_lines.append(f"- Delta vs corpus centroid: {chord_str(c['delta'])}")
        md_lines.append("")
        md_lines.append("| Phrase | Dominant | Chord |")
        md_lines.append("| :--- | :--- | :--- |")
        for sig in sorted(c["members"], key=lambda s: -chord(s)["flow"]):
            ch = chord(sig)
            md_lines.append(
                f"| {sig['phrase']} | {sig['dominant_interaction']} | "
                f"({ch['action_net']:+.2f}, {ch['structure']:+.2f}, "
                f"{ch['flow']:+.2f}, {ch['transform']:+.2f}) |"
            )
        md_lines.append("")

    md_lines.extend([
        "## Per-axis extremes",
        "",
    ])
    for k in CHORD_KEYS:
        md_lines.append(f"### {k}")
        md_lines.append("")
        md_lines.append("Lowest:")
        for v, p in by_axis[k]["low5"]:
            md_lines.append(f"- {v:+.3f} {p}")
        md_lines.append("")
        md_lines.append("Highest:")
        for v, p in by_axis[k]["high5"]:
            md_lines.append(f"- {v:+.3f} {p}")
        md_lines.append("")

    md_lines.extend([
        "## Centroid distance",
        "",
        "Phrases closest to the corpus centroid (most 'average'):",
        "",
    ])
    for v, p in closest:
        md_lines.append(f"- {v:.3f} {p}")
    md_lines.extend([
        "",
        "Phrases farthest from the corpus centroid (most extreme):",
        "",
    ])
    for v, p in farthest:
        md_lines.append(f"- {v:.3f} {p}")
    md_lines.append("")

    (OUT_DIR / "04_chord_clusters.md").write_text("\n".join(md_lines), encoding="utf-8")

    return {
        "clusters": cluster_summaries,
        "centroid": centroid,
        "closest": closest,
        "farthest": farthest,
        "by_axis": by_axis,
        "corpus_size": len(signatures),
    }


# ---------------------------------------------------------------------------
# Task 7: Chord-space visualizations
# ---------------------------------------------------------------------------

LANG_COLORS = {
    "EN": "#2563eb",
    "LA": "#c2410c",
    "GA": "#15803d",
    "NEO": "#7c3aed",
    "UNKNOWN": "#64748b",
}


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def mat_vec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [dot(row, vector) for row in matrix]


def normalize_vec(vector: list[float]) -> list[float]:
    length = math.sqrt(sum(v * v for v in vector))
    if length == 0:
        return [0.0 for _ in vector]
    return [v / length for v in vector]


def principal_component(matrix: list[list[float]], seed_vector: list[float]) -> tuple[list[float], float]:
    vector = normalize_vec(seed_vector)
    for _ in range(80):
        next_vector = normalize_vec(mat_vec(matrix, vector))
        if euclid_dict_like(vector, next_vector) < 1e-10:
            break
        vector = next_vector
    eigenvalue = dot(vector, mat_vec(matrix, vector))
    return vector, eigenvalue


def euclid_dict_like(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def pca2(points: list[list[float]]) -> list[tuple[float, float]]:
    if not points:
        return []
    dims = len(points[0])
    means = [mean(row[i] for row in points) for i in range(dims)]
    centered = [[row[i] - means[i] for i in range(dims)] for row in points]
    denom = max(len(points) - 1, 1)
    cov = [
        [sum(row[i] * row[j] for row in centered) / denom for j in range(dims)]
        for i in range(dims)
    ]

    pc1, eig1 = principal_component(cov, [1.0, 0.3, 0.2, 0.1])
    cov2 = [
        [cov[i][j] - eig1 * pc1[i] * pc1[j] for j in range(dims)]
        for i in range(dims)
    ]
    pc2, _ = principal_component(cov2, [0.1, 1.0, 0.2, 0.3])
    return [(dot(row, pc1), dot(row, pc2)) for row in centered]


def scale(value: float, lo: float, hi: float, out_lo: float, out_hi: float) -> float:
    if abs(hi - lo) < 1e-12:
        return (out_lo + out_hi) / 2
    return out_lo + (value - lo) * (out_hi - out_lo) / (hi - lo)


def scatter_svg(
    title: str,
    rows: list[dict],
    x_key: str,
    y_key: str,
    x_label: str,
    y_label: str,
) -> str:
    width = 720
    height = 480
    pad_left = 78
    pad_right = 28
    pad_top = 54
    pad_bottom = 70
    xs = [row[x_key] for row in rows]
    ys = [row[y_key] for row in rows]
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)
    x_margin = (x_hi - x_lo) * 0.08 or 0.1
    y_margin = (y_hi - y_lo) * 0.08 or 0.1
    x_lo -= x_margin
    x_hi += x_margin
    y_lo -= y_margin
    y_hi += y_margin

    parts = [
        f'<section class="chart"><h2>{html.escape(title)}</h2>',
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f'<rect class="plot-bg" x="{pad_left}" y="{pad_top}" '
        f'width="{width - pad_left - pad_right}" height="{height - pad_top - pad_bottom}" />',
    ]

    for i in range(6):
        tx = pad_left + i * (width - pad_left - pad_right) / 5
        ty = pad_top + i * (height - pad_top - pad_bottom) / 5
        x_val = x_lo + i * (x_hi - x_lo) / 5
        y_val = y_hi - i * (y_hi - y_lo) / 5
        parts.append(f'<line class="grid" x1="{tx:.1f}" y1="{pad_top}" x2="{tx:.1f}" y2="{height - pad_bottom}" />')
        parts.append(f'<line class="grid" x1="{pad_left}" y1="{ty:.1f}" x2="{width - pad_right}" y2="{ty:.1f}" />')
        parts.append(f'<text class="tick x" x="{tx:.1f}" y="{height - pad_bottom + 22}">{x_val:+.2f}</text>')
        parts.append(f'<text class="tick y" x="{pad_left - 12}" y="{ty + 4:.1f}">{y_val:+.2f}</text>')

    parts.append(f'<line class="axis" x1="{pad_left}" y1="{height - pad_bottom}" x2="{width - pad_right}" y2="{height - pad_bottom}" />')
    parts.append(f'<line class="axis" x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height - pad_bottom}" />')
    parts.append(f'<text class="axis-label x-label" x="{width / 2}" y="{height - 22}">{html.escape(x_label)}</text>')
    parts.append(
        f'<text class="axis-label y-label" transform="translate(24 {height / 2}) rotate(-90)">'
        f'{html.escape(y_label)}</text>'
    )

    for row in rows:
        cx = scale(row[x_key], x_lo, x_hi, pad_left, width - pad_right)
        cy = scale(row[y_key], y_lo, y_hi, height - pad_bottom, pad_top)
        color = LANG_COLORS.get(row["language"], LANG_COLORS["UNKNOWN"])
        radius = 7 if row["language"] == "NEO" else 5
        title_text = (
            f"{row['phrase']} | {row['language']} | {row['dominant']} | "
            f"{x_label}={row[x_key]:+.3f}, {y_label}={row[y_key]:+.3f}"
        )
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius}" fill="{color}" '
            f'stroke="#0f172a" stroke-width="0.7" opacity="0.88"><title>'
            f'{html.escape(title_text)}</title></circle>'
        )

    parts.append("</svg></section>")
    return "\n".join(parts)


def task7_chord_visualizations() -> dict:
    signatures = load_corpus_signatures()
    pca_points = pca2([[chord(sig)[k] for k in CHORD_KEYS] for sig in signatures])
    rows = []
    for sig, (pca_1, pca_2) in zip(signatures, pca_points):
        c = chord(sig)
        rows.append(
            {
                "corpus_id": sig.get("_corpus_id", ""),
                "collection": sig.get("_collection", ""),
                "concept_id": sig.get("_concept_id", ""),
                "language": sig.get("_lang", "") or "UNKNOWN",
                "phrase": sig["phrase"],
                "dominant": sig["dominant_interaction"],
                "action_net": c["action_net"],
                "structure": c["structure"],
                "flow": c["flow"],
                "transform": c["transform"],
                "pca_1": pca_1,
                "pca_2": pca_2,
            }
        )

    write_csv(
        OUT_DIR / "05_chord_visualizations.csv",
        [
            {
                **row,
                "action_net": round(row["action_net"], 6),
                "structure": round(row["structure"], 6),
                "flow": round(row["flow"], 6),
                "transform": round(row["transform"], 6),
                "pca_1": round(row["pca_1"], 6),
                "pca_2": round(row["pca_2"], 6),
            }
            for row in rows
        ],
        fieldnames=[
            "corpus_id", "collection", "concept_id", "language", "phrase",
            "dominant", "action_net", "structure", "flow", "transform",
            "pca_1", "pca_2",
        ],
    )

    legend = "\n".join(
        f'<span><i style="background:{color}"></i>{html.escape(lang)}</span>'
        for lang, color in LANG_COLORS.items()
        if lang == "UNKNOWN" or any(row["language"] == lang for row in rows)
    )
    charts = [
        scatter_svg("Flow vs Action", rows, "flow", "action_net", "flow", "action_net"),
        scatter_svg("Flow vs Structure", rows, "flow", "structure", "flow", "structure"),
        scatter_svg("Structure vs Transform", rows, "structure", "transform", "structure", "transform"),
        scatter_svg("PCA Of Chord Vectors", rows, "pca_1", "pca_2", "PCA 1", "PCA 2"),
    ]
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Neo Chord Visualizations</title>
<style>
body {{
  margin: 0;
  font-family: Segoe UI, Arial, sans-serif;
  color: #172033;
  background: #f6f8fb;
}}
main {{
  max-width: 1160px;
  margin: 0 auto;
  padding: 34px 24px 48px;
}}
h1 {{ font-size: 30px; margin: 0 0 8px; }}
p {{ max-width: 850px; line-height: 1.55; }}
.legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin: 18px 0 26px;
  font-size: 14px;
}}
.legend span {{ display: inline-flex; align-items: center; gap: 7px; }}
.legend i {{
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid #0f172a;
}}
.grid-wrap {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(430px, 1fr));
  gap: 22px;
}}
.chart {{
  background: #ffffff;
  border: 1px solid #d7deea;
  border-radius: 8px;
  padding: 16px 16px 10px;
}}
h2 {{ font-size: 17px; margin: 0 0 8px; }}
svg {{ width: 100%; height: auto; display: block; }}
.plot-bg {{ fill: #fbfdff; stroke: #d5deec; }}
.grid {{ stroke: #e4eaf3; stroke-width: 1; }}
.axis {{ stroke: #334155; stroke-width: 1.4; }}
.tick {{ fill: #64748b; font-size: 12px; }}
.tick.x {{ text-anchor: middle; }}
.tick.y {{ text-anchor: end; }}
.axis-label {{ fill: #334155; font-weight: 600; font-size: 13px; text-anchor: middle; }}
</style>
</head>
<body>
<main>
<h1>Neo Chord Visualizations</h1>
<p>Generated from <code>{html.escape(CORPUS_CSV.name)}</code> using the current structured natural/translation corpus ({len(rows)} phrases). Points are colored by language; hover a point to see phrase, dominant interaction, and coordinates.</p>
<div class="legend">{legend}</div>
<div class="grid-wrap">
{''.join(charts)}
</div>
</main>
</body>
</html>
"""
    (OUT_DIR / "05_chord_visualizations.html").write_text(html_text, encoding="utf-8")
    return {"rows": rows, "path": OUT_DIR / "05_chord_visualizations.html"}


# ---------------------------------------------------------------------------
# Task 8: Controlled syntax tests
# ---------------------------------------------------------------------------


def mean_chord(signatures: list[dict]) -> dict:
    return {key: mean(chord(sig)[key] for sig in signatures) for key in CHORD_KEYS}


def within_avg_cosine(signatures: list[dict]) -> float:
    values = []
    for i, a in enumerate(signatures):
        for b in signatures[i + 1:]:
            values.append(cosine(chord(a), chord(b)))
    return mean(values) if values else 1.0


def task8_controlled_syntax() -> dict:
    frames = controlled_syntax_rows()
    phrase_rows = []
    frame_summaries = []

    for frame, rows_for_frame in frames.items():
        signatures = [analyze_corpus_row(row, missing_mode=ANALYSIS_MISSING_MODE) for row in rows_for_frame]
        centroid = mean_chord(signatures)
        dominant_counter = Counter(sig["dominant_interaction"] for sig in signatures)
        common_dom, common_count = dominant_counter.most_common(1)[0]
        frame_summaries.append(
            {
                "frame": frame,
                "members": len(signatures),
                "centroid": centroid,
                "within_avg_cosine": within_avg_cosine(signatures),
                "dominant_consensus": common_dom,
                "dominant_consensus_count": common_count,
                "dominant_distribution": dominant_counter,
                "signatures": signatures,
            }
        )

        for sig in signatures:
            c = chord(sig)
            phrase_rows.append(
                {
                    "frame": frame,
                    "noun_pair": note_value(sig.get("metadata", {}), "noun_pair"),
                    "phrase": sig["phrase"],
                    "dominant": sig["dominant_interaction"],
                    "disruptive_events": sig["disruptive_event_count"],
                    "entropy": sig["interaction_entropy"],
                    "chord_action_net": round(c["action_net"], 4),
                    "chord_structure": round(c["structure"], 4),
                    "chord_flow": round(c["flow"], 4),
                    "chord_transform": round(c["transform"], 4),
                }
            )

    write_csv(OUT_DIR / "06_controlled_syntax.csv", phrase_rows, fieldnames=list(phrase_rows[0].keys()))

    centroid_rows = []
    for summary in frame_summaries:
        centroid_rows.append(
            {
                "frame": summary["frame"],
                "members": summary["members"],
                "within_avg_cosine": round(summary["within_avg_cosine"], 4),
                "dominant_consensus": summary["dominant_consensus"],
                "dominant_consensus_count": summary["dominant_consensus_count"],
                **{f"centroid_{key}": round(summary["centroid"][key], 4) for key in CHORD_KEYS},
            }
        )
    write_csv(OUT_DIR / "06_controlled_syntax_centroids.csv", centroid_rows, fieldnames=list(centroid_rows[0].keys()))

    frame_names = [summary["frame"] for summary in frame_summaries]
    cross_lines = ["| | " + " | ".join(frame_names) + " |", "| :--- |" + " :--- |" * len(frame_names)]
    for a in frame_summaries:
        cells = [f"{cosine(a['centroid'], b['centroid']):+.2f}" for b in frame_summaries]
        cross_lines.append(f"| **{a['frame']}** | " + " | ".join(cells) + " |")

    noun_pair_groups: dict[str, list[dict]] = defaultdict(list)
    for summary in frame_summaries:
        for sig in summary["signatures"]:
            noun_pair_groups[note_value(sig.get("metadata", {}), "noun_pair")].append(sig)

    noun_pair_rows = []
    for noun_pair, signatures in sorted(noun_pair_groups.items()):
        noun_pair_rows.append(
            {
                "noun_pair": noun_pair,
                "frames": len(signatures),
                "cross_frame_avg_cosine": round(within_avg_cosine(signatures), 4),
                "phrases": " | ".join(sig["phrase"] for sig in signatures),
            }
        )
    write_csv(OUT_DIR / "06_controlled_syntax_noun_pairs.csv", noun_pair_rows, fieldnames=list(noun_pair_rows[0].keys()))

    md_lines = [
        "# Task 6: Controlled Syntax Tests",
        "",
        "These rows hold syntax almost fixed while swapping the central frame: "
        "`THE X OPENS THE Y`, `THE X HOLDS THE Y`, `THE X BREAKS THE Y`, and "
        "`THE X WAITS NEAR THE Y`. Each frame uses the same five noun pairs.",
        "",
        f"All phrases run with `--missing {ANALYSIS_MISSING_MODE}`.",
        "",
        "## Frame Cohesion",
        "",
        "| Frame | Members | Within-avg cosine | Dominant consensus | Centroid |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for summary in sorted(frame_summaries, key=lambda item: -item["within_avg_cosine"]):
        md_lines.append(
            f"| {summary['frame']} | {summary['members']} | "
            f"{summary['within_avg_cosine']:+.3f} | "
            f"`{summary['dominant_consensus']}` "
            f"({summary['dominant_consensus_count']}/{summary['members']}) | "
            f"{chord_str(summary['centroid'])} |"
        )

    md_lines.extend([
        "",
        "## Cross-Frame Centroid Cosine",
        "",
        *cross_lines,
        "",
        "High off-diagonal values mean the fixed sentence shell is stronger than the "
        "verb/frame distinction. Lower values suggest the frame itself is moving the "
        "signature.",
        "",
        "## Noun-Pair Stability Across Frames",
        "",
        "| Noun pair | Cross-frame avg cosine |",
        "| :--- | :--- |",
    ])
    for row in sorted(noun_pair_rows, key=lambda item: item["cross_frame_avg_cosine"]):
        md_lines.append(f"| {row['noun_pair']} | {row['cross_frame_avg_cosine']:+.3f} |")

    md_lines.extend(["", "## Per-Frame Detail", ""])
    for summary in frame_summaries:
        md_lines.append(f"### {summary['frame']}")
        md_lines.append("")
        md_lines.append("| Phrase | Dominant | Disrupt | Chord |")
        md_lines.append("| :--- | :--- | :--- | :--- |")
        for sig in summary["signatures"]:
            c = chord(sig)
            md_lines.append(
                f"| {sig['phrase']} | {sig['dominant_interaction']} | "
                f"{sig['disruptive_event_count']} | "
                f"({c['action_net']:+.2f}, {c['structure']:+.2f}, "
                f"{c['flow']:+.2f}, {c['transform']:+.2f}) |"
            )
        md_lines.append("")

    (OUT_DIR / "06_controlled_syntax.md").write_text("\n".join(md_lines), encoding="utf-8")
    return {"summaries": frame_summaries, "noun_pairs": noun_pair_rows}


# ---------------------------------------------------------------------------
# Task 9: Minimal pair studies
# ---------------------------------------------------------------------------


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            curr.append(min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if ca == cb else 1),
            ))
        prev = curr
    return prev[-1]


def task9_minimal_pairs() -> dict:
    families = minimal_pair_rows()
    word_rows = []
    pair_rows = []
    family_summaries = []

    for family, rows_for_family in families.items():
        signatures = [analyze_corpus_row(row, missing_mode=ANALYSIS_MISSING_MODE) for row in rows_for_family]
        base = signatures[0]
        pair_cosines = []
        pair_euclids = []

        for sig in signatures:
            c = chord(sig)
            word_rows.append(
                {
                    "family": family,
                    "word": sig["phrase"],
                    "distance_from_base": edit_distance(base["phrase"], sig["phrase"]),
                    "cosine_from_base": round(cosine(chord(base), c), 4),
                    "euclid_from_base": round(euclid(chord(base), c), 4),
                    "dominant": sig["dominant_interaction"],
                    "chord_action_net": round(c["action_net"], 4),
                    "chord_structure": round(c["structure"], 4),
                    "chord_flow": round(c["flow"], 4),
                    "chord_transform": round(c["transform"], 4),
                }
            )

        for i, a in enumerate(signatures):
            for b in signatures[i + 1:]:
                cos = cosine(chord(a), chord(b))
                dist = euclid(chord(a), chord(b))
                pair_cosines.append(cos)
                pair_euclids.append(dist)
                pair_rows.append(
                    {
                        "family": family,
                        "word_a": a["phrase"],
                        "word_b": b["phrase"],
                        "edit_distance": edit_distance(a["phrase"], b["phrase"]),
                        "cosine": round(cos, 4),
                        "euclid": round(dist, 4),
                        "dominant_a": a["dominant_interaction"],
                        "dominant_b": b["dominant_interaction"],
                        "dominant_match": a["dominant_interaction"] == b["dominant_interaction"],
                    }
                )

        family_summaries.append(
            {
                "family": family,
                "base": base["phrase"],
                "members": len(signatures),
                "avg_pair_cosine": mean(pair_cosines) if pair_cosines else 1.0,
                "avg_pair_euclid": mean(pair_euclids) if pair_euclids else 0.0,
                "max_from_base": max(
                    word_rows[-len(signatures):],
                    key=lambda row: row["euclid_from_base"],
                ),
                "signatures": signatures,
            }
        )

    write_csv(OUT_DIR / "07_minimal_pairs.csv", word_rows, fieldnames=list(word_rows[0].keys()))
    write_csv(OUT_DIR / "07_minimal_pair_distances.csv", pair_rows, fieldnames=list(pair_rows[0].keys()))

    edit1_pairs = [row for row in pair_rows if row["edit_distance"] == 1]
    edit1_avg = mean(row["euclid"] for row in edit1_pairs) if edit1_pairs else 0.0

    md_lines = [
        "# Task 7: Minimal Pair Studies",
        "",
        "Minimal-pair word families test how sharply small spelling changes move a Neo "
        "signature. This is the microscope pass after the broader controlled syntax test.",
        "",
        f"All words run with `--missing {ANALYSIS_MISSING_MODE}`.",
        "",
        "## Family Summary",
        "",
        "| Family | Base | Members | Avg pair cosine | Avg pair Euclid | Most moved from base |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for summary in sorted(family_summaries, key=lambda item: -item["avg_pair_euclid"]):
        moved = summary["max_from_base"]
        md_lines.append(
            f"| {summary['family']} | {summary['base']} | {summary['members']} | "
            f"{summary['avg_pair_cosine']:+.3f} | {summary['avg_pair_euclid']:.3f} | "
            f"{moved['word']} ({moved['euclid_from_base']:.3f}) |"
        )

    md_lines.extend([
        "",
        f"Mean Euclidean movement for one-edit pairs: **{edit1_avg:.3f}**",
        "",
        "## Per-Family Detail",
        "",
    ])
    for summary in family_summaries:
        md_lines.append(f"### {summary['family']}")
        md_lines.append("")
        md_lines.append("| Word | Edit from base | Cos from base | Euclid from base | Dominant | Chord |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        rows_for_family = [row for row in word_rows if row["family"] == summary["family"]]
        for row in rows_for_family:
            md_lines.append(
                f"| {row['word']} | {row['distance_from_base']} | "
                f"{row['cosine_from_base']:+.3f} | {row['euclid_from_base']:.3f} | "
                f"`{row['dominant']}` | "
                f"({row['chord_action_net']:+.2f}, {row['chord_structure']:+.2f}, "
                f"{row['chord_flow']:+.2f}, {row['chord_transform']:+.2f}) |"
            )
        md_lines.append("")

    (OUT_DIR / "07_minimal_pairs.md").write_text("\n".join(md_lines), encoding="utf-8")
    return {"summaries": family_summaries, "pair_rows": pair_rows, "edit1_avg_euclid": edit1_avg}


# ---------------------------------------------------------------------------
# Synthesis report
# ---------------------------------------------------------------------------


def write_report(t1, t2, t5, t6, t8, t9) -> None:
    lines = [
        "# Neo Explorations: Synthesis Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Seven investigations driven by the structured corpus in `{CORPUS_CSV.name}`. "
        "Detailed results live in the per-task files alongside this report. A visual "
        "scatterplot companion is available in `05_chord_visualizations.html`.",
        "",
        "## 1. Translation Invariance (`01_translation_invariance.md`)",
        "",
        f"- Triplets/pairs analyzed: **{len(t1['summaries'])}**",
        f"- Mean cosine across all cross-language pairs: **{t1['avg_cosine']:+.3f}**",
        f"- Mean Euclidean distance: **{t1['avg_euclid']:.3f}**",
        f"- Dominant-interaction match rate across pairs: **{t1['match_rate']*100:.1f}%**",
        "",
        "Most-invariant concept (highest avg cosine):",
    ]
    sorted_concepts = sorted(t1["summaries"], key=lambda s: -s["avg_cosine"])
    for s in sorted_concepts[:2]:
        lines.append(f"  - `{s['concept']}` (cos={s['avg_cosine']:+.3f})")
    lines.append("Least-invariant concept (lowest avg cosine):")
    for s in sorted_concepts[-2:]:
        lines.append(f"  - `{s['concept']}` (cos={s['avg_cosine']:+.3f})")

    lines.extend([
        "",
        "## 2. Phase Shift / Turbulence Reachability (`02_phase_turbulence.md`)",
        "",
        f"- Phase Shift events fired across probes: **{t2['totals'].get('Phase Shift', 0)}**",
        f"- Turbulence events fired across probes: **{t2['totals'].get('Turbulence', 0)}**",
        f"- Probes run: {len(t2['probes'])}",
        "",
        "Conclusion: both rare cells are reachable. They simply do not appear in natural "
        "Latin-alphabet prose because the Forfeda digraphs (AE/OI/UI/EA/IO) only arise "
        "from Irish orthography or transliteration, and almost never adjacent. They are "
        "available as a 'ritual register' for deliberate Forfeda-heavy inscription.",
        "",
        "## 3. Semantic Category Consistency (`03_semantic_categories.md`)",
        "",
    ])

    sorted_cats = sorted(t5["summaries"], key=lambda s: -s["within_avg_cosine"])
    nf = t5.get("noise_floor")
    nf_mean = nf["mean"] if nf else None
    lines.append("| Category | Within-avg cosine | vs random baseline | Dominant consensus |")
    lines.append("| :--- | :--- | :--- | :--- |")
    for s in sorted_cats:
        delta = (s["within_avg_cosine"] - nf_mean) if nf_mean is not None else None
        delta_str = f"{delta:+.3f}" if delta is not None else "n/a"
        lines.append(
            f"| {s['category']} | {s['within_avg_cosine']:+.3f} | {delta_str} | "
            f"`{s['dominant_consensus']}` ({s['dominant_consensus_count']}/{s['members']}) |"
        )
    if nf_mean is not None:
        lines.append("")
        lines.append(
            f"Random-subset noise floor (500 random 5-phrase subsets of the "
            f"{t6['corpus_size']}-phrase structured natural/translation corpus): "
            f"mean cosine **{nf_mean:+.3f}**, 95th percentile **{nf['p95']:+.3f}**."
        )
    lines.append("")
    lines.append(f"Most consistent semantic category: **{sorted_cats[0]['category']}** "
                 f"(within-cosine {sorted_cats[0]['within_avg_cosine']:+.3f})")
    lines.append(f"Least consistent: **{sorted_cats[-1]['category']}** "
                 f"(within-cosine {sorted_cats[-1]['within_avg_cosine']:+.3f})")
    lines.append("")

    lines.extend([
        "## 4. Chord-Space Clusters (`04_chord_clusters.md`)",
        "",
        f"- Corpus rows clustered: **{t6['corpus_size']}**",
        f"- Corpus centroid: {chord_str(t6['centroid'])}",
        "",
        "K-means K=4 cluster summary (label = largest deviation from corpus centroid):",
        "",
        "| Cluster | Label | Size | Lang mix |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for c in t6["clusters"]:
        lang_str = ", ".join(f"{k}={v}" for k, v in c["lang_mix"].most_common())
        lines.append(f"| {c['id']} | `{c['label']}` | {c['size']} | {lang_str} |")
    lines.append("")
    lines.append("Most-average phrases (closest to centroid):")
    for v, p in t6["closest"][:3]:
        lines.append(f"- {v:.3f} {p}")
    lines.append("")
    lines.append("Most-extreme phrases (farthest from centroid):")
    for v, p in t6["farthest"][:3]:
        lines.append(f"- {v:.3f} {p}")
    lines.append("")

    lines.extend([
        "## 5. Chord Visualizations (`05_chord_visualizations.html`)",
        "",
        "The visualization report plots flow/action, flow/structure, "
        "structure/transform, and a two-axis PCA projection of the chord vectors. "
        "Points are colored by language so the language fingerprint can be inspected "
        "visually rather than only inferred from tables.",
        "",
    ])

    controlled_rank = sorted(t8["summaries"], key=lambda s: -s["within_avg_cosine"])
    lines.extend([
        "## 6. Controlled Syntax (`06_controlled_syntax.md`)",
        "",
        "Controlled syntax rows hold the noun pairs steady while swapping the frame: "
        "`opens`, `holds`, `breaks`, and `waits_near`.",
        "",
        "| Frame | Within-avg cosine | Dominant consensus |",
        "| :--- | :--- | :--- |",
    ])
    for summary in controlled_rank:
        lines.append(
            f"| {summary['frame']} | {summary['within_avg_cosine']:+.3f} | "
            f"`{summary['dominant_consensus']}` "
            f"({summary['dominant_consensus_count']}/{summary['members']}) |"
        )
    lines.append("")

    minimal_rank = sorted(t9["summaries"], key=lambda s: -s["avg_pair_euclid"])
    lines.extend([
        "## 7. Minimal Pairs (`07_minimal_pairs.md`)",
        "",
        f"Mean Euclidean movement for one-edit word pairs: **{t9['edit1_avg_euclid']:.3f}**",
        "",
        "| Family | Avg pair cosine | Avg pair Euclid | Most moved from base |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for summary in minimal_rank:
        moved = summary["max_from_base"]
        lines.append(
            f"| {summary['family']} | {summary['avg_pair_cosine']:+.3f} | "
            f"{summary['avg_pair_euclid']:.3f} | {moved['word']} "
            f"({moved['euclid_from_base']:.3f}) |"
        )
    lines.append("")

    # Compose cross-cutting observations using actual measurements
    most_invariant = sorted_concepts[0]
    least_invariant = sorted_concepts[-1]
    obs_lines = [
        "## Cross-cutting observations",
        "",
        "**Translation invariance is real but uneven.** Mean cross-language cosine sits "
        f"at **{t1['avg_cosine']:+.3f}**, well above orthogonality. Same-concept phrases "
        "*do* point in similar directions in chord space. But the dominant-interaction "
        f"label only matches **{t1['match_rate']*100:.0f}%** of the time. So the *vector* "
        "is preserved across languages while the *peak interaction cell* gets relabeled "
        "by orthography. The most stable concept is "
        f"`{most_invariant['concept']}` (cos {most_invariant['avg_cosine']:+.3f}), the "
        f"least is `{least_invariant['concept']}` ({least_invariant['avg_cosine']:+.3f}).",
        "",
        "**Forfeda is a 'ritual register'.** Phase Shift and Turbulence are sparse "
        "in natural prose but trivially producible once Forfeda digraphs are clustered "
        "intentionally. The pure Phase-Shift probes `AEUI`, `AEAEAE`, `UIEAIO` all "
        "collapse to chord vector `(0, 0, 0, 1)` - pure transform. This means the Forfeda "
        "axis is currently a *binary* indicator (present / absent) rather than a "
        "continuous signal in observed text. It functions as an opt-in 'magic register'.",
        "",
    ]

    if nf_mean is not None:
        best_above = sorted_cats[0]["within_avg_cosine"] - nf_mean
        worst_above = sorted_cats[-1]["within_avg_cosine"] - nf_mean
        obs_lines.extend([
            f"**Semantic categories barely beat random.** Random 5-phrase subsets of the "
            f"{t6['corpus_size']}-phrase structured natural/translation corpus already "
            f"average **{nf_mean:+.3f}** within-cosine - meaning "
            "the entire corpus lives in a single tight chord neighborhood. The most "
            f"cohesive category (`{sorted_cats[0]['category']}`) beats the noise floor by "
            f"only **{best_above:+.3f}**, the least by **{worst_above:+.3f}**. The "
            "cross-category centroid cosine matrix is uniformly +0.95 to +1.00. "
            "Translation: chord-space clustering currently captures English-prose "
            "letter statistics, not semantic content.",
            "",
        ])

    controlled_best = max(t8["summaries"], key=lambda s: s["within_avg_cosine"])
    controlled_worst = min(t8["summaries"], key=lambda s: s["within_avg_cosine"])
    minimal_most_sensitive = max(t9["summaries"], key=lambda s: s["avg_pair_euclid"])
    obs_lines.extend([
        "**Controlled frames are the next stress test.** The most internally stable "
        f"frame is `{controlled_best['frame']}` "
        f"({controlled_best['within_avg_cosine']:+.3f}); the loosest is "
        f"`{controlled_worst['frame']}` ({controlled_worst['within_avg_cosine']:+.3f}). "
        "If these values stay high while cross-frame centroids remain close, Neo is "
        "mostly hearing the shared sentence shell. If the frame centroids pull apart, "
        "the verb/action field is measurable.",
        "",
        "**Minimal pairs expose the instrument's gain.** The most sensitive family in "
        f"this run is `{minimal_most_sensitive['family']}` "
        f"(avg Euclid {minimal_most_sensitive['avg_pair_euclid']:.3f}); one-edit pairs "
        f"move by {t9['edit1_avg_euclid']:.3f} on average. This gives us a concrete "
        "scale for deciding whether a phrase-level difference is large or just normal "
        "orthographic jitter.",
        "",
    ])

    # Find clusters that over-represent each language relative to the whole corpus.
    corpus_lang_mix = Counter()
    for c in t6["clusters"]:
        corpus_lang_mix.update(c["lang_mix"])

    def lang_lift(cluster: dict, lang: str) -> float:
        corpus_total = sum(corpus_lang_mix.values()) or 1
        cluster_total = sum(cluster["lang_mix"].values()) or 1
        return (
            cluster["lang_mix"].get(lang, 0) / cluster_total
            - corpus_lang_mix.get(lang, 0) / corpus_total
        )

    la_clust = max(t6["clusters"], key=lambda c: lang_lift(c, "LA"))
    ga_clust = max(t6["clusters"], key=lambda c: lang_lift(c, "GA"))
    en_clust = max(t6["clusters"], key=lambda c: lang_lift(c, "EN"))
    obs_lines.extend([
        "**Clusters track *language*, not just *meaning*.** Once K-means clusters are "
        f"relabeled by deviation from the corpus centroid, the four groups have "
        "distinct linguistic tilts:",
        "",
        f"- Cluster {la_clust['id']} `{la_clust['label']}` over-represents Latin "
        f"(LA={la_clust['lang_mix'].get('LA', 0)}, "
        f"GA={la_clust['lang_mix'].get('GA', 0)}, "
        f"EN={la_clust['lang_mix'].get('EN', 0)})",
        f"- Cluster {ga_clust['id']} `{ga_clust['label']}` over-represents Irish "
        f"(GA={ga_clust['lang_mix'].get('GA', 0)}, "
        f"LA={ga_clust['lang_mix'].get('LA', 0)}, "
        f"EN={ga_clust['lang_mix'].get('EN', 0)})",
        f"- Cluster {en_clust['id']} `{en_clust['label']}` over-represents English "
        f"(EN={en_clust['lang_mix'].get('EN', 0)}, "
        f"LA={en_clust['lang_mix'].get('LA', 0)}, "
        f"GA={en_clust['lang_mix'].get('GA', 0)})",
        "",
        "The chord vector currently carries a **language fingerprint** as its primary "
        "signal. Latin currently over-represents in the positive-action cluster, Irish "
        "in the low-flow / high-transform pocket, and English in the high-structure "
        "and negative-action clusters. Concept identity is a secondary, weaker "
        "layer on top.",
        "",
        "**Implication for the Name = Form thesis.** Two genuine outcomes are "
        "compatible with these results: (a) Neo correctly captures that 'the same idea "
        "expressed in different languages is a different inscription' - meaningful and "
        "intended, or (b) Neo currently confuses orthography with meaning and a "
        "phoneme-level or lemma-level normalization layer is needed before chord "
        "vectors. This audit doesn't pick between the two; it simply makes the "
        "trade-off visible and quantifies it.",
        "",
    ])
    lines.extend(obs_lines)

    (OUT_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    print("[1/7] Translation invariance audit ...")
    t1 = task1_translation_invariance()
    print(f"      avg cosine={t1['avg_cosine']:+.3f}, dominant-match={t1['match_rate']*100:.1f}%")

    print("[2/7] Phase Shift / Turbulence probes ...")
    t2 = task2_phase_turbulence()
    print(f"      Phase Shift hits={t2['totals'].get('Phase Shift', 0)}, "
          f"Turbulence hits={t2['totals'].get('Turbulence', 0)}")

    print("[3/7] Chord-space clustering ...")
    t6 = task6_chord_clusters()
    for c in t6["clusters"]:
        lang_str = ", ".join(f"{k}={v}" for k, v in c["lang_mix"].most_common())
        print(f"      cluster {c['id']} `{c['label']}`: {c['size']} members  ({lang_str})")

    print("[4/7] Semantic-category mapping ...")
    corpus_chords = [chord(sig) for sig in load_corpus_signatures()]
    t5 = task5_semantic_categories(corpus_chords=corpus_chords)
    if t5["noise_floor"]:
        print(f"      noise floor (random 5-subsets): "
              f"mean={t5['noise_floor']['mean']:+.3f}  p95={t5['noise_floor']['p95']:+.3f}")
    for s in t5["summaries"]:
        print(f"      {s['category']:>11s}: within-cos={s['within_avg_cosine']:+.3f}, "
              f"consensus={s['dominant_consensus']} ({s['dominant_consensus_count']}/{s['members']})")

    print("[5/7] Chord visualizations ...")
    t7 = task7_chord_visualizations()
    print(f"      wrote {t7['path']}")

    print("[6/7] Controlled syntax tests ...")
    t8 = task8_controlled_syntax()
    for s in t8["summaries"]:
        print(f"      {s['frame']:>10s}: within-cos={s['within_avg_cosine']:+.3f}, "
              f"consensus={s['dominant_consensus']} ({s['dominant_consensus_count']}/{s['members']})")

    print("[7/7] Minimal pair studies ...")
    t9 = task9_minimal_pairs()
    print(f"      one-edit avg Euclid={t9['edit1_avg_euclid']:.3f}")
    for s in t9["summaries"]:
        print(f"      {s['family']:>12s}: avg-pair-euclid={s['avg_pair_euclid']:.3f}")

    write_report(t1, t2, t5, t6, t8, t9)
    print(f"Wrote outputs to: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
