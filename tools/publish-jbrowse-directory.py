#!/usr/bin/env python3
"""Copy staged JBrowse output into an optional destination directory."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def track_identifier(track: object) -> str | None:
    if not isinstance(track, dict):
        return None
    for key in ("label", "key", "name"):
        value = track.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def merge_track_lists(source: Path, destination: Path) -> None:
    source_data = json.loads(source.read_text(encoding="utf-8"))
    if not destination.exists():
        destination.write_text(json.dumps(source_data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        return

    destination_data = json.loads(destination.read_text(encoding="utf-8"))
    if not isinstance(source_data, dict) or not isinstance(destination_data, dict):
        shutil.copy2(source, destination)
        return

    merged_data = dict(destination_data)
    source_tracks = source_data.get("tracks")
    destination_tracks = destination_data.get("tracks")
    if isinstance(source_tracks, list) and isinstance(destination_tracks, list):
        merged_tracks = list(destination_tracks)
        index_by_identifier = {}
        for index, track in enumerate(merged_tracks):
            identifier = track_identifier(track)
            if identifier is not None:
                index_by_identifier[identifier] = index

        for track in source_tracks:
            identifier = track_identifier(track)
            if identifier is not None and identifier in index_by_identifier:
                merged_tracks[index_by_identifier[identifier]] = track
            else:
                merged_tracks.append(track)

        merged_data["tracks"] = merged_tracks
    else:
        merged_data.update(source_data)

    for key, value in source_data.items():
        if key == "tracks":
            continue
        merged_data.setdefault(key, value)

    destination.write_text(json.dumps(merged_data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def copy_entry(source: Path, destination: Path) -> None:
    if source.name == "trackList.json":
        merge_track_lists(source, destination)
        return
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        return
    shutil.copy2(source, destination)


def publish_directory(source_directory: Path, destination_directory: Path | None) -> None:
    if destination_directory is None:
        return

    if not destination_directory.is_absolute():
        raise ValueError(
            "jbrowse_directory must be an absolute path. "
            f"Received relative path: {destination_directory}"
        )

    destination_directory.mkdir(parents=True, exist_ok=True)
    for entry in source_directory.iterdir():
        copy_entry(entry, destination_directory / entry.name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Copy JBrowse output into an optional destination directory.")
    parser.add_argument("source_directory", type=Path, help="Staged JBrowse output directory")
    parser.add_argument("destination_directory", nargs="?", type=Path, help="Optional JBrowse destination directory")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        publish_directory(args.source_directory, args.destination_directory)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())