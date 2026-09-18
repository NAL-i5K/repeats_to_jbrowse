#!/usr/bin/env python3
"""Run flatfile-to-json.pl with score-based color bins derived from a GFF."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


COLOR_BINS = [
    ("#000080", "navy"),
    ("#4B0082", "indigo"),
    ("#800080", "purple"),
    ("#008000", "green"),
    ("#00FF00", "light green"),
    ("#FFFF00", "yellow"),
    ("#FFA500", "orange"),
    ("#FF4500", "orange-red"),
    ("#FF0000", "red"),
    ("#8B0000", "dark red"),
]
DEFAULT_COLOR = "#808080"
TYPE_COLOR_BINS = [
    ("LINE", "#3399ff", "blue"),
    ("SINE", "#800080", "purple"),
    ("DNA", "#ff6666", "salmon"),
    ("LTR", "#00cc44", "green"),
    ("RC", "#ff6600", "orange"),
    ("Low_complexity", "#d1d1e0", "grey/blue"),
    ("Satellite", "#ff99ff", "pink"),
    ("Simple_repeat", "#8686ac", "dark grey/blue"),
    ("Unknown", "#f2f2f2", "grey"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute score bins from a GFF file and run flatfile-to-json.pl."
    )
    parser.add_argument("in_annotation_source", help="Annotation source metadata")
    parser.add_argument("singularity_image", help="Singularity image containing flatfile-to-json.pl")
    parser.add_argument("in_gff", type=Path, help="Input GFF file")
    parser.add_argument("in_track_label", help="Track label")
    parser.add_argument("in_json_directory", help="Output JBrowse JSON directory")
    parser.add_argument("in_track_key", help="Track key")
    parser.add_argument("in_data_provider", help="Data provider metadata")
    parser.add_argument("in_data_source", help="Data source metadata")
    parser.add_argument("in_data_description", help="Data description metadata")
    parser.add_argument("in_materials_and_methods", help="Methods metadata")
    parser.add_argument("in_publication_status", help="Publication status metadata")
    return parser


def collect_scores(gff_path: Path) -> list[float]:
    scores: list[float] = []
    with gff_path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 6:
                continue
            raw_score = fields[5].strip()
            if raw_score in {"", "."}:
                continue
            try:
                score = float(raw_score)
            except ValueError:
                continue
            if math.isfinite(score):
                scores.append(score)
    return scores


def format_score(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    if not text or text == "-0":
        return "0"
    return text


def round_score(value: float) -> int:
    return int(round(value))


def compute_score_bins(scores: list[float]) -> dict[str, object] | None:
    if not scores:
        return None

    min_score = min(scores)
    max_score = max(scores)
    if math.isclose(min_score, max_score):
        rounded_score = round_score(min_score)
        return {
            "min_score": min_score,
            "max_score": max_score,
            "cutoffs": [rounded_score] * (len(COLOR_BINS) - 1),
            "constant": True,
        }

    step = (max_score - min_score) / len(COLOR_BINS)
    cutoffs = [round_score(min_score + (step * index)) for index in range(1, len(COLOR_BINS))]
    return {
        "min_score": min_score,
        "max_score": max_score,
        "cutoffs": cutoffs,
        "constant": False,
    }


def build_color_function(score_bins: dict[str, object] | None) -> str:
    if score_bins is None:
        return (
            "function(feature) { "
            "var score = parseFloat(feature.get('score')); "
            f"return isNaN(score) ? '{DEFAULT_COLOR}' : '{COLOR_BINS[0][0]}'; "
            "}"
        )

    if score_bins["constant"]:
        return (
            "function(feature) { "
            "var score = parseFloat(feature.get('score')); "
            f"return isNaN(score) ? '{DEFAULT_COLOR}' : '{COLOR_BINS[0][0]}'; "
            "}"
        )

    cutoffs_json = json.dumps(score_bins["cutoffs"])
    colors_json = json.dumps([color for color, _ in COLOR_BINS])
    return (
        "function(feature) { "
        "var score = parseFloat(feature.get('score')); "
        f"var cutoffs = {cutoffs_json}; "
        f"var colors = {colors_json}; "
        f"if (isNaN(score)) return '{DEFAULT_COLOR}'; "
        "for (var index = 0; index < cutoffs.length; index += 1) { "
        "if (score < cutoffs[index]) return colors[index]; "
        "} "
        "return colors[colors.length - 1]; "
        "}"
    )


def build_type_color_function() -> str:
    type_map = {name: color for name, color, _label in TYPE_COLOR_BINS}
    type_map["repeat_region"] = type_map["Unknown"]
    return (
        "function(feature) { "
        "var typeValue = feature.get('type') || feature.get('Type') || ''; "
        "var prefix = typeValue.split('/')[0]; "
        f"var typeColors = {json.dumps(type_map)}; "
        f"return typeColors[prefix] || typeColors.Unknown || '{DEFAULT_COLOR}'; "
        "}"
    )


def build_track_legend(score_bins: dict[str, object] | None) -> str:
    if score_bins is None:
        return "No numeric score values were found in column 6, so numeric features use the default navy color and features without a numeric score are gray."

    min_score = score_bins["min_score"]
    max_score = score_bins["max_score"]
    if score_bins["constant"]:
        formatted_score = format_score(min_score)
        return (
            "All numeric score values in column 6 are "
            f"{formatted_score}, so scored features are shown in navy and features without a numeric score are gray."
        )

    cutoffs = score_bins["cutoffs"]
    ranges: list[str] = []
    lower_bound = min_score
    for index, (_, color_name) in enumerate(COLOR_BINS):
        if index < len(cutoffs):
            upper_bound = cutoffs[index]
            ranges.append(
                f"{format_score(lower_bound)} to < {format_score(upper_bound)} are {color_name}"
            )
            lower_bound = upper_bound
        else:
            ranges.append(
                f"{format_score(lower_bound)} to {format_score(max_score)} are {color_name}"
            )

    return (
        "Higher scores are represented by warmer colors: "
        + "; ".join(ranges)
        + ". Features without a numeric score are gray."
    )


def build_type_legend() -> str:
    ranges = [f"{name} are {description} ({color})" for name, color, description in TYPE_COLOR_BINS]
    return (
        "EarlGrey features are colored by the type prefix before any '/'; repeat_region and any other unmapped types are grey. "
        + "; ".join(ranges)
        + "."
    )


def normalize_annotation_source(value: str) -> str:
    normalized = value.strip().lower()
    if normalized == "repeatmodeler":
        return "RepeatModeler"
    return "EarlGrey"


def build_command(args: argparse.Namespace) -> list[str]:
    annotation_source = normalize_annotation_source(args.in_annotation_source)
    score_bins = compute_score_bins(collect_scores(args.in_gff)) if annotation_source == "RepeatModeler" else None
    client_config = {
        "label": "target,name,id",
        "description": "score,note,description",
        "color": build_color_function(score_bins) if annotation_source == "RepeatModeler" else build_type_color_function(),
    }
    config = {
        "category": "Repeat Sequence Analysis/Transposable Elements",
        "metadata": {
            "Data description": args.in_data_description,
            "Data provider": args.in_data_provider,
            "Data source": args.in_data_source,
            "Annotation source": annotation_source,
            "Methods": args.in_materials_and_methods,
            "Publication status": args.in_publication_status,
            "Track legend": build_track_legend(score_bins) if annotation_source == "RepeatModeler" else build_type_legend(),
        },
    }

    return [
        "singularity",
        "exec",
        args.singularity_image,
        "flatfile-to-json.pl",
        "--trackType",
        "CanvasFeatures",
        "--gff",
        str(args.in_gff),
        "--trackLabel",
        args.in_track_label,
        "--out",
        args.in_json_directory,
        "--key",
        args.in_track_key,
        "--clientConfig",
        json.dumps(client_config, separators=(",", ":")),
        "--config",
        json.dumps(config, separators=(",", ":")),
    ]


def main() -> int:
    args = build_parser().parse_args()
    try:
        completed = subprocess.run(build_command(args), check=False)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())