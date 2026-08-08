#!/usr/bin/env python3
"""v1.1 corpus-authority wrapper for the multidirectional frontier producer.

The v1 search used live filesystem enumeration. v1.1 freezes the search corpus
to Git-tracked files via `git ls-files`, then delegates all report semantics to
the v1 producer. The theorem ceiling is unchanged.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import janus_fundamentum_multidirectional_frontier_v1 as base


def tracked_iter_text_files(root: Path):
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    rels = sorted(x.decode("utf-8") for x in raw.split(b"\0") if x)
    for rel in rels:
        if rel.startswith("research_targets/"):
            continue
        path = root / rel
        if path.suffix.lower() not in base.ALLOWED_SUFFIXES:
            continue
        if not path.is_file():
            continue
        if path.stat().st_size > base.MAX_FILE_BYTES:
            continue
        yield path


base.iter_text_files = tracked_iter_text_files


if __name__ == "__main__":
    base.main()
