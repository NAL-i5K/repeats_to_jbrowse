#!/usr/bin/env python3
"""Copy staged JBrowse output into an optional destination directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_entry(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        return
    shutil.copy2(source, destination)


def publish_directory(source_directory: Path, destination_directory: Path | None) -> None:
    if destination_directory is None:
        return

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
    publish_directory(args.source_directory, args.destination_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())