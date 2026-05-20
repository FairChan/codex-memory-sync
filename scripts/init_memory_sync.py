#!/usr/bin/env python3
"""Backward-compatible entrypoint for Codex memory sync initialization."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from memory_sync import main as memory_sync_main  # noqa: E402


def translate_args(argv: list[str]) -> list[str]:
    translated = ["init"]
    for arg in argv:
        if arg == "--force":
            print("notice: --force is deprecated and does not overwrite existing memory files; use --replace-existing explicitly.", file=sys.stderr)
            continue
        translated.append(arg)
    return translated


if __name__ == "__main__":
    raise SystemExit(memory_sync_main(translate_args(sys.argv[1:])))
