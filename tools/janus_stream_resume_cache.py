#!/usr/bin/env python3
"""Durable JANUS P-vs-NP stream-resume checkpoint utility.

Purpose:
- survive UI/stream cache loss by keeping the exact research resume state in Git;
- fail closed on scientific promotion;
- never rewind a live branch to the cached source head.

This tool does not control ChatGPT's UI cache. It makes recovery deterministic
after a stream failure.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / ".janus" / "P_VS_NP_STREAM_CACHE_CURRENT.json"
HISTORY = ROOT / ".janus" / "stream_cache_history"
SCHEMA = "JANUS-P-VS-NP-STREAM-RESUME-CACHE-v1"

DENY_KEY = re.compile(r"(password|passwd|token|secret|credential|private[_-]?key|api[_-]?key)", re.I)
DENY_TEXT = re.compile(r"(ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


class CacheError(RuntimeError):
    pass


def canonical_payload(obj: dict) -> bytes:
    body = copy.deepcopy(obj)
    body.pop("integrity", None)
    return json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(obj: dict) -> str:
    return hashlib.sha256(canonical_payload(obj)).hexdigest()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CacheError(f"missing cache file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CacheError(f"invalid JSON in {path}: {exc}") from exc


def git(*args: str, check: bool = True) -> str:
    p = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and p.returncode:
        raise CacheError(p.stderr.strip() or f"git {' '.join(args)} failed")
    return p.stdout.strip()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scan_secrets(value, path="$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            if DENY_KEY.search(str(k)):
                hits.append(f"{path}.{k}: forbidden key")
            hits.extend(scan_secrets(v, f"{path}.{k}"))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            hits.extend(scan_secrets(v, f"{path}[{i}]"))
    elif isinstance(value, str) and DENY_TEXT.search(value):
        hits.append(f"{path}: secret-like text")
    return hits


def validate(obj: dict, verify_digest: bool = True) -> None:
    if obj.get("schema") != SCHEMA:
        raise CacheError(f"schema mismatch: {obj.get('schema')!r}")
    required = [
        "repository",
        "branch",
        "source_scientific_head",
        "scientific_boundary",
        "current_research_state",
        "resume_policy",
    ]
    missing = [k for k in required if k not in obj]
    if missing:
        raise CacheError(f"missing required keys: {missing}")

    hits = scan_secrets(obj)
    if hits:
        raise CacheError("secret scan failed:\n  " + "\n  ".join(hits))

    boundary = obj["scientific_boundary"]
    pnp = boundary.get("P_VS_NP")
    if pnp != "OPEN" and not obj.get("promotion_receipt"):
        raise CacheError(
            "fail-closed: P_VS_NP may leave OPEN only with promotion_receipt"
        )

    if verify_digest:
        got = obj.get("integrity", {}).get("sha256")
        want = digest(obj)
        if got != want:
            raise CacheError(f"digest mismatch: stored={got!r} computed={want}")


def source_head_relation(source: str, live: str) -> str:
    if source == live:
        return "EXACT"
    p = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", source, live],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p.returncode == 0:
        return "LIVE_DESCENDS_FROM_CACHE"
    p2 = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", live, source],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p2.returncode == 0:
        return "CACHE_AHEAD_OF_LIVE"
    return "DIVERGED_OR_SOURCE_MISSING"


def cmd_verify(_: argparse.Namespace) -> int:
    obj = read_json(CURRENT)
    validate(obj)
    print(json.dumps({
        "status": "PASS_STREAM_CACHE_VERIFY",
        "schema": obj["schema"],
        "source_scientific_head": obj["source_scientific_head"],
        "frontier": obj["current_research_state"].get("frontier_name"),
        "P_VS_NP": obj["scientific_boundary"].get("P_VS_NP"),
        "sha256": obj["integrity"]["sha256"],
    }, sort_keys=True))
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    obj = read_json(CURRENT)
    validate(obj)
    live = git("rev-parse", "HEAD")
    relation = source_head_relation(obj["source_scientific_head"], live)
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    safe = relation in {"EXACT", "LIVE_DESCENDS_FROM_CACHE"}
    print(json.dumps({
        "status": "PASS" if safe else "STOP_WRITE_AND_RECONCILE",
        "live_head": live,
        "live_branch": branch,
        "cached_source_head": obj["source_scientific_head"],
        "relation": relation,
        "frontier": obj["current_research_state"].get("frontier_name"),
        "next_attack": obj["current_research_state"].get("next_attack", []),
        "P_VS_NP": obj["scientific_boundary"].get("P_VS_NP"),
    }, ensure_ascii=False, sort_keys=True))
    return 0 if safe else 2


def cmd_resume(_: argparse.Namespace) -> int:
    obj = read_json(CURRENT)
    validate(obj)
    state = obj["current_research_state"]
    out = {
        "repository": obj["repository"],
        "branch": obj["branch"],
        "source_scientific_head": obj["source_scientific_head"],
        "scientific_boundary": obj["scientific_boundary"],
        "frontier_name": state.get("frontier_name"),
        "carrier": state.get("carrier"),
        "established": state.get("established", []),
        "live_split": state.get("live_split", {}),
        "next_attack": state.get("next_attack", []),
        "anti_loop": obj.get("anti_loop", {}),
        "transport_hazards": obj.get("transport_hazards", []),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def archive_current() -> Path | None:
    if not CURRENT.exists():
        return None
    old = read_json(CURRENT)
    validate(old)
    HISTORY.mkdir(parents=True, exist_ok=True)
    stamp = old.get("updated_at_utc", "unknown").replace(":", "").replace("-", "")
    short = old["integrity"]["sha256"][:16]
    dst = HISTORY / f"{stamp}__{short}.json"
    if dst.exists():
        if dst.read_bytes() != CURRENT.read_bytes():
            raise CacheError(f"history collision with different bytes: {dst}")
    else:
        dst.write_bytes(CURRENT.read_bytes())
    return dst


def cmd_write(args: argparse.Namespace) -> int:
    incoming = read_json(Path(args.from_json))
    incoming["schema"] = SCHEMA
    incoming["updated_at_utc"] = utc_now()

    if args.source_head:
        incoming["source_scientific_head"] = args.source_head
    else:
        incoming["source_scientific_head"] = git("rev-parse", "HEAD")

    incoming["integrity"] = {
        "algorithm": "sha256(canonical-json-without-integrity)",
        "sha256": digest(incoming),
    }
    validate(incoming)

    archived = archive_current()
    CURRENT.parent.mkdir(parents=True, exist_ok=True)
    tmp = CURRENT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(incoming, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, CURRENT)

    print(json.dumps({
        "status": "PASS_STREAM_CACHE_WRITE",
        "current": str(CURRENT.relative_to(ROOT)),
        "archived": str(archived.relative_to(ROOT)) if archived else None,
        "source_scientific_head": incoming["source_scientific_head"],
        "sha256": incoming["integrity"]["sha256"],
    }, sort_keys=True))
    return 0


def cmd_archive(_: argparse.Namespace) -> int:
    archived = archive_current()
    print(json.dumps({
        "status": "PASS_STREAM_CACHE_ARCHIVE",
        "archived": str(archived.relative_to(ROOT)) if archived else None,
    }, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("resume").set_defaults(fn=cmd_resume)
    w = sub.add_parser("write")
    w.add_argument("--from-json", required=True)
    w.add_argument("--source-head")
    w.set_defaults(fn=cmd_write)
    sub.add_parser("archive").set_defaults(fn=cmd_archive)
    return p


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.fn(args)
    except CacheError as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
