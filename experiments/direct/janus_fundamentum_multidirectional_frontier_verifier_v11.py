#!/usr/bin/env python3
"""v1.1 Git-index corpus wrapper for the independent frontier verifier.

This wrapper does not import the producer. It replaces only the v1 verifier's
live-filesystem corpus enumeration with an independent `git ls-files` replay.
All semantic checks and repaired-digest tamper attacks remain in the base
independent verifier.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import janus_fundamentum_multidirectional_frontier_verifier_v1 as base


def tracked_corpus(root: Path):
    rows = []
    digest = hashlib.sha256()
    raw_listing = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    rels = sorted(x.decode("utf-8") for x in raw_listing.split(b"\0") if x)
    for rel in rels:
        if rel.startswith("research_targets/"):
            continue
        path = root / rel
        if path.suffix.lower() not in base.SUFFIXES:
            continue
        if not path.is_file():
            continue
        if path.stat().st_size > base.MAX_BYTES:
            continue
        try:
            file_bytes = path.read_bytes()
            text = file_bytes.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rows.append((rel, text))
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(file_bytes).digest())
    return rows, digest.hexdigest()


base.corpus = tracked_corpus


if __name__ == "__main__":
    base.main()
