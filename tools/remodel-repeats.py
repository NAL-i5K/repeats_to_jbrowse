#!/usr/bin/env python3
"""Convert RepeatModeler GFF3 output into a JBrowse1-friendly hierarchy."""

# Created with GPT-5.4 mini.

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

FEATURE_TYPE_INPUTS = {"similarity", "dispersed_repeat"}
FEATURE_TYPE_PARENT = "repeat_region"
FEATURE_TYPE_CHILD = "dispersed_repeat"
TARGET_KEYS = {"%": "%25", " ": "%20", "\t": "%09", "\n": "%0A", "\r": "%0D", ";": "%3B", "=": "%3D", "&": "%26", ",": "%2C"}


def escape_target_id(value: str) -> str:
    """Escape only the characters that are illegal in a GFF3 Target ID."""

    escaped_parts: list[str] = []
    index = 0
    while index < len(value):
        character = value[index]
        if character == "%" and index + 2 < len(value):
            hex_pair = value[index + 1 : index + 3]
            if all(ch in "0123456789abcdefABCDEF" for ch in hex_pair):
                escaped_parts.append(value[index : index + 3])
                index += 3
                continue
        replacement = TARGET_KEYS.get(character)
        if replacement is not None:
            escaped_parts.append(replacement)
        else:
            escaped_parts.append(character)
        index += 1
    return "".join(escaped_parts)


def normalize_target_attribute(raw_value: str) -> str | None:
    """Normalize a RepeatModeler-style Target attribute to GFF3 syntax."""

    value = raw_value.strip()
    if value.startswith("Target"):
        value = value[len("Target") :].lstrip()
    if value.startswith("="):
        value = value[1:].lstrip()

    try:
        tokens = shlex.split(value)
    except ValueError:
        return None

    if len(tokens) < 3:
        return None

    strand = None
    if tokens[-1] in {"+", "-"} and len(tokens) >= 4:
        strand = tokens[-1]
        end = tokens[-2]
        start = tokens[-3]
        target_id_tokens = tokens[:-3]
    else:
        end = tokens[-1]
        start = tokens[-2]
        target_id_tokens = tokens[:-2]

    target_id = " ".join(target_id_tokens).strip()
    if not target_id:
        return None

    normalized = [escape_target_id(target_id), start, end]
    if strand is not None:
        normalized.append(strand)
    return "Target=" + " ".join(normalized)


def clean_attributes(attributes_text: str, remove_keys: set[str]) -> str:
    cleaned_attributes: list[str] = []
    for chunk in attributes_text.split(";"):
        part = chunk.strip()
        if not part:
            continue

        if part == "Target" or part.startswith("Target=") or part.startswith("Target "):
            normalized_target = normalize_target_attribute(part)
            if normalized_target is not None:
                cleaned_attributes.append(normalized_target)
            else:
                cleaned_attributes.append(part.replace('"', ""))
            continue

        key, separator, _value = part.partition("=")
        if separator and key in remove_keys:
            continue

        cleaned_attributes.append(part)

    return ";".join(cleaned_attributes) if cleaned_attributes else "."


def append_attribute(attributes_text: str, attribute: str) -> str:
    if attributes_text == "." or not attributes_text:
        return attribute
    return f"{attributes_text};{attribute}"


def transform_feature_line(line: str, feature_id: int) -> list[str]:
    fields = line.split("\t")
    if len(fields) != 9:
        sys.stderr.write(f"warning: expected 9 tab-delimited columns, leaving line unchanged: {line}\n")
        return [line]

    if fields[2] not in FEATURE_TYPE_INPUTS:
        return [line]

    parent_fields = fields.copy()
    child_fields = fields.copy()

    parent_fields[2] = FEATURE_TYPE_PARENT
    child_fields[2] = FEATURE_TYPE_CHILD

    parent_fields[8] = append_attribute(clean_attributes(fields[8], remove_keys={"ID", "Parent"}), f"ID={feature_id}")
    child_fields[8] = append_attribute(clean_attributes(fields[8], remove_keys={"ID", "Parent"}), f"Parent={feature_id}")

    return ["\t".join(parent_fields), "\t".join(child_fields)]


def process_file(input_path: Path, output_handle) -> tuple[int, int, set[str]]:
    feature_id = 0
    modified_lines = 0
    added_lines = 0
    unhandled_feature_types: set[str] = set()
    with input_path.open("r", encoding="utf-8") as input_handle:
        for raw_line in input_handle:
            line = raw_line.rstrip("\n")
            if not line or line.startswith("#"):
                output_handle.write(raw_line)
                continue

            fields = line.split("\t")
            if len(fields) == 9 and fields[2] not in FEATURE_TYPE_INPUTS:
                unhandled_feature_types.add(fields[2])

            transformed_lines = transform_feature_line(line, feature_id + 1)
            if transformed_lines == [line]:
                output_handle.write(raw_line)
                continue

            feature_id += 1
            modified_lines += 1
            added_lines += len(transformed_lines) - 1
            for transformed_line in transformed_lines:
                output_handle.write(transformed_line + "\n")

    return modified_lines, added_lines, unhandled_feature_types


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert RepeatModeler GFF3 output into parent/child features for JBrowse1."
    )
    parser.add_argument("input", type=Path, help="Input GFF3 file")
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Optional output GFF3 file. Defaults to stdout.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.output is None:
        modified_lines, added_lines, unhandled_feature_types = process_file(args.input, sys.stdout)
        if unhandled_feature_types:
            print(
                "warning: input contains feature types not handled by this script: "
                + ", ".join(sorted(unhandled_feature_types)),
                file=sys.stderr,
            )
        print(
            f"info: modified {modified_lines} lines and added {added_lines} lines.",
            file=sys.stderr,
        )
        return 0

    with args.output.open("w", encoding="utf-8") as output_handle:
        modified_lines, added_lines, unhandled_feature_types = process_file(args.input, output_handle)

    if unhandled_feature_types:
        print(
            "warning: input contains feature types not handled by this script: "
            + ", ".join(sorted(unhandled_feature_types)),
            file=sys.stderr,
        )
    print(
        f"info: modified {modified_lines} lines and added {added_lines} lines.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())