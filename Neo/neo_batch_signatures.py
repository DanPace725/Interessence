#!/usr/bin/env python3
"""
Batch signature exporter for Neo / NeOgham phrases.

Reads words or phrases from text, CSV, JSON, or JSONL and exports:
- signatures.json: full structured signatures
- signatures.jsonl: one signature per line
- signatures.csv: flat phrase-level table
- pair_events.csv: every adjacent glyph interaction
- summary.md: quick corpus overview
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from neo_generator import AICME_INTERACTIONS, NEO_ALPHABET, NEO_SIGNALS


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = SCRIPT_DIR / "analysis" / "signature_exports"

GROUP_LABELS = {
    "right": "Right / Action",
    "left": "Left / Resistance",
    "cross": "Cross / Structure",
    "diagonal": "Diagonal / Flow",
    "backslash": "Backslash / Transform",
}

DISRUPTIVE_INTERACTIONS = {
    "Fracture",
    "Distort",
    "Invert",
    "Turbulence",
    "Phase Shift",
}

MISSING_MODES = ("strict", "canonical", "phonetic-lite", "sensitivity")
DEFAULT_MISSING_MODE = "canonical"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", strip_accents(text).lower()).strip("-")
    return slug or "neo-item"


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_for_neo(text: str) -> str:
    text = strip_accents(text).upper()
    return re.sub(r"\s+", " ", text).strip()


def prepare_text(text: str, missing_mode: str) -> dict:
    """Create a Neo-normalized inscription and record any interpretive substitutions."""
    normalized = normalize_for_neo(text)
    if missing_mode == "strict":
        return {
            "original_normalized": normalized,
            "neo_text": normalized,
            "substitutions": [],
            "alternates": [],
        }

    mode_for_rules = "canonical" if missing_mode == "sensitivity" else missing_mode
    substitutions = []
    alternates = []
    output_parts = []

    for match in re.finditer(r"[A-Z]+|[^A-Z]+", normalized):
        token = match.group(0)
        if not token.isalpha():
            output_parts.append(token)
            continue

        for local_index, char in enumerate(token):
            original_index = match.start() + local_index
            replacement, reason, options = replacement_for_missing_letter(
                char=char,
                word=token,
                local_index=local_index,
                mode=mode_for_rules,
            )
            neo_start = sum(len(part) for part in output_parts)
            output_parts.append(replacement)
            neo_end = neo_start + len(replacement)

            if replacement != char:
                substitutions.append(
                    {
                        "index": original_index,
                        "from": char,
                        "to": replacement,
                        "reason": reason,
                        "mode": mode_for_rules,
                    }
                )
            if options:
                alternates.append(
                    {
                        "index": original_index,
                        "neo_start": neo_start,
                        "neo_end": neo_end,
                        "from": char,
                        "primary": replacement,
                        "options": options,
                        "reason": reason,
                    }
                )

    return {
        "original_normalized": normalized,
        "neo_text": "".join(output_parts),
        "substitutions": substitutions,
        "alternates": alternates,
    }


def replacement_for_missing_letter(char: str, word: str, local_index: int, mode: str) -> tuple[str, str, list[str]]:
    if char == "K":
        return "C", "k_hard_to_c", ["C", ""]
    if char == "Q":
        return "CW", "q_to_cw", ["CW", "C", "W", ""]
    if char == "V":
        return "F", "v_to_f", ["F", ""]
    if char == "J":
        return "G", "j_to_g", ["G", ""]
    if char == "X":
        return "CS", "x_to_cs", ["CS", "C", "S", ""]
    if char != "Y":
        return char, "", []
    return "EA", "y_to_ea", ["EA", "I", "E", "AI", ""]


def transliterate_quiet(text: str, missing_mode: str = "strict") -> tuple[list[dict], list[dict]]:
    """Convert text to Neo glyph records while collecting unsupported characters."""
    prepared = prepare_text(text, missing_mode)
    return transliterate_neo_text(prepared["neo_text"])


def transliterate_neo_text(neo_text: str) -> tuple[list[dict], list[dict]]:
    """Convert already-normalized Neo text to glyph records."""
    normalized = normalize_for_neo(neo_text)
    glyphs: list[dict] = []
    skipped: list[dict] = []
    i = 0

    while i < len(normalized):
        ch = normalized[i]
        if not ch.isalpha():
            i += 1
            continue

        if i < len(normalized) - 1:
            two = normalized[i : i + 2]
            if two in NEO_ALPHABET:
                position, marks, name = NEO_ALPHABET[two]
                glyphs.append(make_glyph(two, position, marks, name))
                i += 2
                continue

        if ch in NEO_ALPHABET:
            position, marks, name = NEO_ALPHABET[ch]
            glyphs.append(make_glyph(ch, position, marks, name))
        else:
            skipped.append({"char": ch, "index": i})

        i += 1

    return glyphs, skipped


def make_glyph(code: str, position: str, marks: int, name: str) -> dict:
    signal = NEO_SIGNALS[name]
    return {
        "code": code,
        "name": name,
        "group": position,
        "group_label": GROUP_LABELS[position],
        "marks": marks,
        "fingerprint": signal["fingerprint"],
        "dynamic": signal["dynamic"],
        "closure": signal["closure"],
    }


def magnitude_result(delta: int) -> str:
    if delta == 0:
        return "Resonance"
    if delta == 1:
        return "Modulation"
    return "Dominance"


def calculate_pair(g1: dict, g2: dict, scope: str, index: int) -> dict:
    delta = abs(g1["marks"] - g2["marks"])
    interaction = AICME_INTERACTIONS[g1["group"]][g2["group"]]
    return {
        "index": index,
        "scope": scope,
        "pair": f"{g1['code']}->{g2['code']}",
        "glyph_a": g1["code"],
        "glyph_b": g2["code"],
        "name_a": g1["name"],
        "name_b": g2["name"],
        "group_a": g1["group"],
        "group_b": g2["group"],
        "marks_a": g1["marks"],
        "marks_b": g2["marks"],
        "magnitude_delta": delta,
        "magnitude_result": magnitude_result(delta),
        "interaction": interaction,
        "signal_a": g1["fingerprint"],
        "signal_b": g2["fingerprint"],
        "is_disruptive": interaction in DISRUPTIVE_INTERACTIONS,
    }


def positional_weights(length: int) -> list[float]:
    if length <= 0:
        return []
    if length == 1:
        return [1.0]
    if length == 2:
        return [1.0, 0.9]
    return [1.0, 0.8] + [0.6] * (length - 3) + [0.9]


def add_chord_contribution(vector: dict[str, float], glyph: dict, weight: float) -> None:
    value = glyph["marks"] * weight
    group = glyph["group"]
    if group == "right":
        vector["action_positive"] += value
        vector["action_net"] += value
    elif group == "left":
        vector["action_negative"] += value
        vector["action_net"] -= value
    elif group == "cross":
        vector["structure"] += value
    elif group == "diagonal":
        vector["flow"] += value
    elif group == "backslash":
        vector["transform"] += value


def chord_vector(glyphs: list[dict]) -> dict:
    vector = defaultdict(float)
    for glyph, weight in zip(glyphs, positional_weights(len(glyphs))):
        add_chord_contribution(vector, glyph, weight)
    return finalize_chord(vector)


def word_aware_chord(words: list[str]) -> dict:
    vector = defaultdict(float)
    for word in words:
        glyphs, _ = transliterate_quiet(word)
        for glyph, weight in zip(glyphs, positional_weights(len(glyphs))):
            add_chord_contribution(vector, glyph, weight)
    return finalize_chord(vector)


def finalize_chord(vector: dict[str, float]) -> dict:
    keys = ["action_net", "action_positive", "action_negative", "structure", "flow", "transform"]
    raw = {key: round(vector.get(key, 0.0), 4) for key in keys}
    denominator = sum(abs(raw[key]) for key in ["action_net", "structure", "flow", "transform"])
    if denominator == 0:
        normalized = {key: 0.0 for key in ["action_net", "structure", "flow", "transform"]}
    else:
        normalized = {
            key: round(raw[key] / denominator, 4)
            for key in ["action_net", "structure", "flow", "transform"]
        }
    dominant = sorted(normalized.items(), key=lambda item: abs(item[1]), reverse=True)
    return {"raw": raw, "normalized": normalized, "dominant": dominant[:3]}


def interaction_entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counter.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    return round(entropy, 4)


def analyze_phrase(
    phrase: str,
    source: str = "",
    missing_mode: str = DEFAULT_MISSING_MODE,
    metadata: dict | None = None,
) -> dict:
    prepared = prepare_text(phrase, missing_mode)
    signature = analyze_prepared_phrase(phrase, source, missing_mode, prepared, metadata or {})
    if missing_mode == "sensitivity":
        signature["sensitivity"] = calculate_sensitivity(signature, prepared)
    else:
        signature["sensitivity"] = {
            "enabled": False,
            "variant_count": 0,
            "stable": None,
            "variants": [],
        }
    return signature


def analyze_prepared_phrase(
    phrase: str,
    source: str,
    missing_mode: str,
    prepared: dict,
    metadata: dict | None = None,
) -> dict:
    normalized = prepared["neo_text"]
    words = [word for word in normalized.split(" ") if word]
    glyphs, skipped = transliterate_neo_text(normalized)
    pair_events: list[dict] = []

    for index in range(len(glyphs) - 1):
        pair_events.append(calculate_pair(glyphs[index], glyphs[index + 1], "adjacent", index))

    interaction_counts = Counter(event["interaction"] for event in pair_events)
    magnitude_counts = Counter(event["magnitude_result"] for event in pair_events)
    group_counts = Counter(glyph["group"] for glyph in glyphs)
    mark_counts = Counter(str(glyph["marks"]) for glyph in glyphs)
    signal_counts = Counter(glyph["fingerprint"] for glyph in glyphs)
    glyph_counts = Counter(glyph["code"] for glyph in glyphs)

    dominant_interaction, dominant_count = ("", 0)
    if interaction_counts:
        dominant_interaction, dominant_count = interaction_counts.most_common(1)[0]

    disruptive_events = [event for event in pair_events if event["is_disruptive"]]

    return {
        "id": slugify(phrase),
        "source": source,
        "metadata": metadata or {},
        "phrase": phrase,
        "transliteration_mode": missing_mode,
        "original_normalized_phrase": prepared["original_normalized"],
        "normalized_phrase": normalized,
        "substitutions": prepared["substitutions"],
        "alternates": prepared["alternates"],
        "words": words,
        "word_count": len(words),
        "glyph_count": len(glyphs),
        "skipped": skipped,
        "skipped_chars": "".join(item["char"] for item in skipped),
        "glyph_sequence": [glyph["code"] for glyph in glyphs],
        "glyphs": glyphs,
        "pair_events": pair_events,
        "interaction_counts": dict(sorted(interaction_counts.items())),
        "magnitude_counts": dict(sorted(magnitude_counts.items())),
        "group_counts": dict(sorted(group_counts.items())),
        "mark_counts": dict(sorted(mark_counts.items())),
        "signal_counts": dict(signal_counts.most_common()),
        "glyph_counts": dict(glyph_counts.most_common()),
        "dominant_interaction": dominant_interaction,
        "dominant_interaction_count": dominant_count,
        "disruptive_event_count": len(disruptive_events),
        "disruptive_pairs": [event["pair"] for event in disruptive_events],
        "interaction_entropy": interaction_entropy(interaction_counts),
        "chord": {
            "inscription": chord_vector(glyphs),
            "word_aware": word_aware_chord(words),
        },
    }


def metric_snapshot(signature: dict) -> dict:
    dominant_chord = signature["chord"]["word_aware"]["dominant"]
    dominant_chord_dimension = dominant_chord[0][0] if dominant_chord else ""
    return {
        "glyph_count": signature["glyph_count"],
        "dominant_interaction": signature["dominant_interaction"],
        "dominant_interaction_count": signature["dominant_interaction_count"],
        "disruptive_event_count": signature["disruptive_event_count"],
        "interaction_entropy": signature["interaction_entropy"],
        "chord_dominant_dimension": dominant_chord_dimension,
        "chord_normalized": signature["chord"]["word_aware"]["normalized"],
    }


def calculate_sensitivity(base_signature: dict, prepared: dict) -> dict:
    variants = []
    base_metrics = metric_snapshot(base_signature)
    neo_text = prepared["neo_text"]

    for alternate in prepared["alternates"]:
        for option in alternate["options"]:
            if option == alternate["primary"]:
                continue
            variant_text = neo_text[: alternate["neo_start"]] + option + neo_text[alternate["neo_end"] :]
            variant_prepared = {
                "original_normalized": prepared["original_normalized"],
                "neo_text": variant_text,
                "substitutions": prepared["substitutions"],
                "alternates": prepared["alternates"],
            }
            variant_signature = analyze_prepared_phrase(
                base_signature["phrase"],
                base_signature["source"],
                "sensitivity-variant",
                variant_prepared,
                base_signature.get("metadata", {}),
            )
            variant_metrics = metric_snapshot(variant_signature)
            chord_delta = max_chord_delta(
                base_metrics["chord_normalized"],
                variant_metrics["chord_normalized"],
            )
            variants.append(
                {
                    "index": alternate["index"],
                    "from": alternate["from"],
                    "primary": alternate["primary"],
                    "option": option,
                    "variant_normalized_phrase": variant_text,
                    "dominant_interaction_changed": (
                        base_metrics["dominant_interaction"] != variant_metrics["dominant_interaction"]
                    ),
                    "disruptive_event_count_delta": (
                        variant_metrics["disruptive_event_count"] - base_metrics["disruptive_event_count"]
                    ),
                    "chord_dominant_changed": (
                        base_metrics["chord_dominant_dimension"]
                        != variant_metrics["chord_dominant_dimension"]
                    ),
                    "max_chord_delta": chord_delta,
                    "metrics": variant_metrics,
                }
            )

    stable = all(
        not variant["dominant_interaction_changed"]
        and not variant["chord_dominant_changed"]
        and variant["disruptive_event_count_delta"] == 0
        for variant in variants
    )
    return {
        "enabled": True,
        "variant_count": len(variants),
        "stable": stable,
        "base_metrics": base_metrics,
        "variants": variants,
    }


def max_chord_delta(base: dict, variant: dict) -> float:
    keys = set(base) | set(variant)
    if not keys:
        return 0.0
    return round(max(abs(base.get(key, 0.0) - variant.get(key, 0.0)) for key in keys), 4)


def read_phrases(path: Path, phrase_column: str | None = None) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv_phrases(path, phrase_column)
    if suffix == ".jsonl":
        return read_jsonl_phrases(path, phrase_column)
    if suffix == ".json":
        return read_json_phrases(path, phrase_column)
    return read_text_phrases(path)


def read_text_phrases(path: Path) -> list[dict]:
    phrases = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        phrase = line.strip()
        if not phrase or phrase.startswith("#"):
            continue
        phrases.append({"phrase": phrase, "source": f"{path.name}:{line_number}", "metadata": {}})
    return phrases


def choose_phrase_column(fieldnames: list[str], requested: str | None) -> str:
    if requested:
        if requested not in fieldnames:
            raise ValueError(f"Column '{requested}' not found. Available columns: {', '.join(fieldnames)}")
        return requested
    for candidate in ["phrase", "text", "word", "title", "name"]:
        if candidate in fieldnames:
            return candidate
    return fieldnames[0]


def read_csv_phrases(path: Path, phrase_column: str | None) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        column = choose_phrase_column(reader.fieldnames, phrase_column)
        phrases = []
        for row_number, row in enumerate(reader, start=2):
            phrase = (row.get(column) or "").strip()
            if phrase:
                metadata = {key: value for key, value in row.items() if key != column and value}
                source = metadata.get("corpus_id") or metadata.get("id") or f"{path.name}:{row_number}"
                phrases.append({"phrase": phrase, "source": source, "metadata": metadata})
        return phrases


def read_jsonl_phrases(path: Path, phrase_column: str | None) -> list[dict]:
    phrases = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        phrase = extract_phrase(item, phrase_column)
        if phrase:
            metadata = item if isinstance(item, dict) else {}
            phrases.append({"phrase": phrase, "source": f"{path.name}:{line_number}", "metadata": metadata})
    return phrases


def read_json_phrases(path: Path, phrase_column: str | None) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("phrases") or data.get("items") or []
    else:
        items = []
    phrases = []
    for index, item in enumerate(items, start=1):
        phrase = extract_phrase(item, phrase_column)
        if phrase:
            metadata = item if isinstance(item, dict) else {}
            phrases.append({"phrase": phrase, "source": f"{path.name}:{index}", "metadata": metadata})
    return phrases


def extract_phrase(item, phrase_column: str | None) -> str:
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return ""
    if phrase_column:
        return str(item.get(phrase_column, "")).strip()
    for candidate in ["phrase", "text", "word", "title", "name"]:
        if candidate in item and str(item[candidate]).strip():
            return str(item[candidate]).strip()
    return ""


def flat_signature(signature: dict) -> dict:
    interactions = signature["interaction_counts"]
    groups = signature["group_counts"]
    marks = signature["mark_counts"]
    word_chord = signature["chord"]["word_aware"]["normalized"]
    raw_word_chord = signature["chord"]["word_aware"]["raw"]
    metadata = signature.get("metadata", {})
    return {
        "id": signature["id"],
        "source": signature["source"],
        "corpus_id": metadata.get("corpus_id", metadata.get("id", "")),
        "collection": metadata.get("collection", ""),
        "item_type": metadata.get("item_type", ""),
        "concept_id": metadata.get("concept_id", ""),
        "concept": metadata.get("concept", ""),
        "language": metadata.get("language", ""),
        "provenance": metadata.get("provenance", ""),
        "status": metadata.get("status", ""),
        "notes": metadata.get("notes", ""),
        "phrase": signature["phrase"],
        "transliteration_mode": signature["transliteration_mode"],
        "original_normalized_phrase": signature["original_normalized_phrase"],
        "normalized_phrase": signature["normalized_phrase"],
        "substitution_count": len(signature["substitutions"]),
        "substitutions": " ".join(
            f"{item['from']}->{item['to']}@{item['index']}:{item['reason']}"
            for item in signature["substitutions"]
        ),
        "alternate_count": len(signature["alternates"]),
        "sensitivity_enabled": signature["sensitivity"]["enabled"],
        "sensitivity_variant_count": signature["sensitivity"]["variant_count"],
        "sensitivity_stable": signature["sensitivity"]["stable"],
        "word_count": signature["word_count"],
        "glyph_count": signature["glyph_count"],
        "skipped_chars": signature["skipped_chars"],
        "glyph_sequence": " ".join(signature["glyph_sequence"]),
        "dominant_interaction": signature["dominant_interaction"],
        "dominant_interaction_count": signature["dominant_interaction_count"],
        "disruptive_event_count": signature["disruptive_event_count"],
        "disruptive_pairs": " ".join(signature["disruptive_pairs"]),
        "interaction_entropy": signature["interaction_entropy"],
        "count_anchor": interactions.get("Anchor", 0),
        "count_crystalize": interactions.get("Crystalize", 0),
        "count_dampen": interactions.get("Dampen", 0),
        "count_distort": interactions.get("Distort", 0),
        "count_fracture": interactions.get("Fracture", 0),
        "count_gate": interactions.get("Gate", 0),
        "count_invert": interactions.get("Invert", 0),
        "count_opposition": interactions.get("Opposition", 0),
        "count_phase_shift": interactions.get("Phase Shift", 0),
        "count_propel": interactions.get("Propel", 0),
        "count_reinforce": interactions.get("Reinforce", 0),
        "count_stream": interactions.get("Stream", 0),
        "count_turbulence": interactions.get("Turbulence", 0),
        "group_right": groups.get("right", 0),
        "group_left": groups.get("left", 0),
        "group_cross": groups.get("cross", 0),
        "group_diagonal": groups.get("diagonal", 0),
        "group_backslash": groups.get("backslash", 0),
        "marks_1": marks.get("1", 0),
        "marks_2": marks.get("2", 0),
        "marks_3": marks.get("3", 0),
        "marks_4": marks.get("4", 0),
        "marks_5": marks.get("5", 0),
        "chord_action_net": word_chord.get("action_net", 0.0),
        "chord_structure": word_chord.get("structure", 0.0),
        "chord_flow": word_chord.get("flow", 0.0),
        "chord_transform": word_chord.get("transform", 0.0),
        "raw_action_positive": raw_word_chord.get("action_positive", 0.0),
        "raw_action_negative": raw_word_chord.get("action_negative", 0.0),
        "raw_action_net": raw_word_chord.get("action_net", 0.0),
        "raw_structure": raw_word_chord.get("structure", 0.0),
        "raw_flow": raw_word_chord.get("flow", 0.0),
        "raw_transform": raw_word_chord.get("transform", 0.0),
    }


def write_outputs(signatures: list[dict], out_dir: Path, label: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "signatures.json").write_text(
        json.dumps({"label": label, "count": len(signatures), "signatures": signatures}, indent=2),
        encoding="utf-8",
    )
    with (out_dir / "signatures.jsonl").open("w", encoding="utf-8") as handle:
        for signature in signatures:
            handle.write(json.dumps(signature, ensure_ascii=False) + "\n")

    flat_rows = [flat_signature(signature) for signature in signatures]
    if flat_rows:
        with (out_dir / "signatures.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(flat_rows)

    pair_rows = []
    for signature in signatures:
        for event in signature["pair_events"]:
            metadata = signature.get("metadata", {})
            row = {
                "signature_id": signature["id"],
                "phrase": signature["phrase"],
                "corpus_id": metadata.get("corpus_id", metadata.get("id", "")),
                "collection": metadata.get("collection", ""),
                "concept_id": metadata.get("concept_id", ""),
                "language": metadata.get("language", ""),
                **event,
            }
            pair_rows.append(row)
    if pair_rows:
        with (out_dir / "pair_events.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(pair_rows[0].keys()))
            writer.writeheader()
            writer.writerows(pair_rows)

    (out_dir / "summary.md").write_text(build_summary(signatures, label), encoding="utf-8")


def build_summary(signatures: list[dict], label: str) -> str:
    interaction_totals = Counter()
    group_totals = Counter()
    skipped_totals = Counter()
    glyph_totals = Counter()
    substitution_totals = Counter()
    sensitivity_no_variants = 0
    sensitivity_stable = 0
    sensitivity_unstable = 0
    disruptive_rank = []
    flow_rank = []

    for signature in signatures:
        interaction_totals.update(signature["interaction_counts"])
        group_totals.update(signature["group_counts"])
        glyph_totals.update(signature["glyph_counts"])
        skipped_totals.update(signature["skipped_chars"])
        for substitution in signature["substitutions"]:
            substitution_totals[f"{substitution['from']}->{substitution['to']} ({substitution['reason']})"] += 1
        if signature["sensitivity"]["enabled"]:
            if signature["sensitivity"]["variant_count"] == 0:
                sensitivity_no_variants += 1
            elif signature["sensitivity"]["stable"]:
                sensitivity_stable += 1
            else:
                sensitivity_unstable += 1
        disruptive_rank.append((signature["disruptive_event_count"], signature["phrase"]))
        flow_rank.append((abs(signature["chord"]["word_aware"]["normalized"]["flow"]), signature["phrase"]))

    lines = [
        f"# Neo Batch Signature Summary: {label}",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Items analyzed: {len(signatures)}",
        "",
        "## Corpus Totals",
        "",
        f"- Total glyphs: {sum(signature['glyph_count'] for signature in signatures)}",
        f"- Total pair events: {sum(len(signature['pair_events']) for signature in signatures)}",
        f"- Skipped unsupported characters: {sum(skipped_totals.values())}",
        f"- Transliteration substitutions: {sum(substitution_totals.values())}",
        "",
        "## Top Interactions",
        "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in interaction_totals.most_common())
    lines.extend(["", "## Group Totals", ""])
    lines.extend(f"- {GROUP_LABELS.get(name, name)}: {count}" for name, count in group_totals.most_common())
    lines.extend(["", "## Top Glyphs", ""])
    lines.extend(f"- {name}: {count}" for name, count in glyph_totals.most_common(15))

    if skipped_totals:
        lines.extend(["", "## Unsupported Characters", ""])
        lines.extend(f"- {name}: {count}" for name, count in skipped_totals.most_common())

    if substitution_totals:
        lines.extend(["", "## Transliteration Substitutions", ""])
        lines.extend(f"- {name}: {count}" for name, count in substitution_totals.most_common())

    if sensitivity_no_variants or sensitivity_stable or sensitivity_unstable:
        lines.extend(["", "## Sensitivity", ""])
        lines.append(f"- No ambiguous alternates: {sensitivity_no_variants}")
        lines.append(f"- Tested stable signatures: {sensitivity_stable}")
        lines.append(f"- Transliteration-sensitive signatures: {sensitivity_unstable}")

    lines.extend(["", "## Most Disruptive Signatures", ""])
    for count, phrase in sorted(disruptive_rank, reverse=True)[:10]:
        lines.append(f"- {count}: {phrase}")

    lines.extend(["", "## Strongest Flow Signatures", ""])
    for score, phrase in sorted(flow_rank, reverse=True)[:10]:
        lines.append(f"- {score:.4f}: {phrase}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-export Neo signatures for words or phrases.")
    parser.add_argument("--input", "-i", type=Path, help="Input text, CSV, JSON, or JSONL file.")
    parser.add_argument("--text", "-t", action="append", default=[], help="Phrase to analyze. Can be repeated.")
    parser.add_argument("--phrase-column", help="Column/key containing phrases for CSV/JSON inputs.")
    parser.add_argument("--out-dir", "-o", type=Path, default=DEFAULT_OUT_DIR, help="Output directory.")
    parser.add_argument("--label", default="corpus", help="Human label used in summary output.")
    parser.add_argument(
        "--missing",
        choices=MISSING_MODES,
        default=DEFAULT_MISSING_MODE,
        help=(
            "How to handle letters outside the Neo alphabet. "
            "strict skips them; canonical uses bounded reference mappings "
            "K->C, Q->CW, V->F, J->G, X->CS, Y->EA; "
            "sensitivity uses canonical plus local variants."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    items: list[dict] = []

    if args.input:
        items.extend(read_phrases(args.input, args.phrase_column))
    for index, phrase in enumerate(args.text, start=1):
        items.append({"phrase": phrase, "source": f"--text:{index}"})

    if not items:
        raise SystemExit("No phrases supplied. Use --input or --text.")

    signatures = [
        analyze_phrase(
            item["phrase"],
            item.get("source", ""),
            missing_mode=args.missing,
            metadata=item.get("metadata", {}),
        )
        for item in items
    ]
    write_outputs(signatures, args.out_dir, args.label)

    print(f"Analyzed {len(signatures)} phrase(s).")
    print(f"Wrote: {args.out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
