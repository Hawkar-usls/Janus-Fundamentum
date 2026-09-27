#!/usr/bin/env python3
"""Build the canonical externalized JANUS working-context snapshot.

This tool persists explicit, reproducible project/scientific state in the repo.
It intentionally does NOT and cannot persist private model chain-of-thought or
hidden runtime caches.

Normal mode writes:
  registry/JANUS_CONTEXT_CACHE_CURRENT.json
  docs/JANUS_CONTEXT_CACHE_CURRENT.md
  registry/context_cache/history/<source-head>.json

--check is deterministic for a fixed source HEAD and exits non-zero if the
current JSON/Markdown snapshots are stale.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "registry/JANUS_CONTEXT_CACHE_CONFIG.json"
CURRENT_JSON = ROOT / "registry/JANUS_CONTEXT_CACHE_CURRENT.json"
CURRENT_MD = ROOT / "docs/JANUS_CONTEXT_CACHE_CURRENT.md"
HISTORY_DIR = ROOT / "registry/context_cache/history"
CACHE_COMMIT_PREFIX = "[context-cache]"

STATUS_NEEDLES = (
    "P_VS_NP",
    "P_EQ_NP",
    "E8_D1",
    "UNIVERSAL_SELECTOR",
    "D1 =",
    "D1=",
    "STATUS",
    "AUTHORITY",
    "R0",
    "R1",
    "R2",
    "R3",
    "R4",
    "R5",
    "R6",
    "R7",
    "REPRESENTATION_CHANGE",
    "FRONTIER",
    "OPEN",
    "CLOSED",
    "PROVED",
    "CANDIDATE",
    "MATERIALIZED",
)

TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt"}


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def resolve_ref(candidates: list[str]) -> str | None:
    for candidate in candidates:
        if git("rev-parse", "--verify", candidate, check=False):
            return candidate
    return None


def canonical_source_head() -> str:
    """Return the latest non-generated-cache commit.

    Cache commits use a frozen prefix. This makes --check stable when it is run
    on the cache commit itself: the snapshot still describes its scientific
    parent rather than recursively describing itself.
    """
    head = git("rev-parse", "HEAD")
    while True:
        subject = git("show", "-s", "--format=%s", head)
        if not subject.startswith(CACHE_COMMIT_PREFIX):
            return head
        parent = git("rev-parse", f"{head}^")
        if not parent:
            return head
        head = parent


def source_commit_time(head: str) -> str:
    return git("show", "-s", "--format=%cI", head)


def current_branch(config: dict[str, Any]) -> str:
    branch = git("branch", "--show-current", check=False)
    return branch or os.environ.get("GITHUB_REF_NAME") or config["canonical_branch"]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def generated_path(path: str, config: dict[str, Any]) -> bool:
    for marker in config.get("generated_paths", []):
        if marker.endswith("/"):
            if path.startswith(marker):
                return True
        elif path == marker:
            return True
    return False


def scientific_path(path: str, config: dict[str, Any]) -> bool:
    return any(path.startswith(prefix) for prefix in config["scientific_prefixes"])


def changed_paths(base_ref: str | None, source_head: str) -> list[str]:
    if base_ref:
        out = git("diff", "--name-only", f"{base_ref}...{source_head}")
    else:
        out = git("ls-tree", "-r", "--name-only", source_head)
    return sorted(p for p in out.splitlines() if p)


def status_tokens(path: Path, limit: int) -> list[str]:
    if not path.exists() or path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw.strip())
        if not line or len(line) > 420:
            continue
        upper = line.upper()
        if not any(needle in upper for needle in STATUS_NEEDLES):
            continue
        if line in seen:
            continue
        seen.add(line)
        out.append(line)
        if len(out) >= limit:
            break
    return out


def path_record(path_text: str, status_limit: int = 0) -> dict[str, Any]:
    path = ROOT / path_text
    rec: dict[str, Any] = {"path": path_text, "exists": path.exists()}
    if not path.exists() or not path.is_file():
        return rec
    rec["bytes"] = path.stat().st_size
    rec["sha256"] = file_sha256(path)
    if status_limit:
        rec["status_tokens"] = status_tokens(path, status_limit)
    return rec


def recent_commits(source_head: str, limit: int) -> list[dict[str, str]]:
    fmt = "%H%x09%cI%x09%s"
    raw = git("log", source_head, f"-n{limit}", f"--pretty=format:{fmt}")
    rows: list[dict[str, str]] = []
    for line in raw.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        sha, when, subject = parts
        if subject.startswith(CACHE_COMMIT_PREFIX):
            continue
        rows.append({"sha": sha, "committed_at": when, "subject": subject})
    return rows


def working_tree_state() -> dict[str, Any]:
    raw = git("status", "--porcelain", check=False)
    lines = [line for line in raw.splitlines() if line]
    return {
        "clean": not lines,
        "porcelain": lines[:200],
        "truncated": len(lines) > 200,
    }


def build_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    source_head = canonical_source_head()
    base_ref = resolve_ref(config.get("base_refs", []))
    all_changed = changed_paths(base_ref, source_head)
    scientific = [
        p
        for p in all_changed
        if scientific_path(p, config) and not generated_path(p, config)
    ]

    index = [path_record(p) for p in scientific]
    must_read = [
        path_record(p, int(config.get("status_scan_limit_per_file", 80)))
        for p in config.get("must_read", [])
    ]
    transport = [path_record(p) for p in config.get("tracked_transport_paths", [])]

    # Aggregated declared-state excerpts are deliberately sourced only from the
    # configured must-read artifacts. They are evidence pointers, not a theorem
    # promotion mechanism.
    declared: list[dict[str, Any]] = []
    for rec in must_read:
        tokens = rec.get("status_tokens") or []
        if tokens:
            declared.append({"path": rec["path"], "tokens": tokens})

    return {
        "schema_version": "JANUS_CONTEXT_CACHE_v1.0",
        "generated_from_source_commit_time": source_commit_time(source_head),
        "scope": config["scope"],
        "repository": config["repository"],
        "canonical_pr": config["canonical_pr"],
        "branch": current_branch(config),
        "source_head": source_head,
        "base_ref": base_ref,
        "active_goal": config["active_goal"],
        "scientific_firewall": config["scientific_firewall"],
        "frontier_seed": config["frontier_seed"],
        "transport_state": transport,
        "must_read_artifacts": must_read,
        "declared_status_evidence": declared,
        "recent_commits": recent_commits(
            source_head, int(config.get("recent_commit_limit", 80))
        ),
        "changed_scientific_artifact_count": len(index),
        "changed_scientific_artifact_index": index,
        "working_tree": working_tree_state(),
        "resume_protocol": [
            "Read JANUS_CONTEXT_CACHE_START_HERE.md.",
            "Read docs/JANUS_CONTEXT_CACHE_CURRENT.md for the human checkpoint.",
            "Use registry/JANUS_CONTEXT_CACHE_CURRENT.json as the machine-readable authority for source HEAD, file hashes, transport state, and evidence pointers.",
            "Fetch the listed must-read artifacts before changing scientific status.",
            "Run anti-duplication/source checks before creating a new theorem or experiment.",
            "Never promote P_VS_NP, E8_D1, or a PA/NM identifier from cache text alone; promotion still requires the repository governance/checker path."
        ],
    }


def render_markdown(snapshot: dict[str, Any]) -> str:
    fw = snapshot["scientific_firewall"]
    frontier = snapshot["frontier_seed"]
    transport = snapshot["transport_state"]
    must_read = snapshot["must_read_artifacts"]
    commits = snapshot["recent_commits"][:20]

    lines: list[str] = []
    lines += [
        "# JANUS Context Cache — CURRENT",
        "",
        "> Canonical externalized working checkpoint. Generated from repository state; not from chat memory.",
        "",
        f"- **Repository:** `{snapshot['repository']}`",
        f"- **PR:** `#{snapshot['canonical_pr']}`",
        f"- **Branch:** `{snapshot['branch']}`",
        f"- **Source HEAD:** `{snapshot['source_head']}`",
        f"- **Source commit time:** `{snapshot['generated_from_source_commit_time']}`",
        f"- **Base ref:** `{snapshot['base_ref']}`",
        f"- **Indexed changed scientific artifacts:** `{snapshot['changed_scientific_artifact_count']}`",
        "",
        "## Scope",
        "",
        snapshot["scope"]["purpose"],
        "",
        "This cache deliberately excludes private model chain-of-thought, hidden runtime cache, and secrets. It stores the explicit project/scientific state needed for deterministic resumption.",
        "",
        "## Immutable scientific firewall",
        "",
        "```text",
        f"P_VS_NP = {fw['P_VS_NP']}",
        f"E8_D1 = {fw['E8_D1']}",
        f"UNIVERSAL_SELECTOR = {fw['UNIVERSAL_SELECTOR']}",
        f"TOTAL_PATH = {fw['total_path_requirement']}",
        "FINITE_TESTS != UNIVERSAL_PROOF",
        "EXISTENCE != POLYNOMIAL_CONSTRUCTION",
        "```",
        "",
        "## Active goal",
        "",
        f"**{snapshot['active_goal']['name']}**",
        "",
        snapshot["active_goal"]["target"],
        "",
        "## Live frontier seed",
        "",
    ]
    for key, value in frontier.items():
        lines.append(f"- `{key}` — {value}")

    lines += ["", "## Transport / stale-bootstrap watch", ""]
    for rec in transport:
        marker = "PRESENT" if rec["exists"] else "ABSENT"
        extra = f" — sha256 `{rec['sha256']}`" if rec.get("sha256") else ""
        lines.append(f"- `{rec['path']}`: **{marker}**{extra}")

    lines += ["", "## Must-read authority/evidence artifacts", ""]
    for rec in must_read:
        marker = "OK" if rec["exists"] else "MISSING"
        digest = f" `{rec['sha256'][:16]}…`" if rec.get("sha256") else ""
        lines.append(f"- **{marker}** `{rec['path']}`{digest}")

    lines += ["", "## Recent non-cache commits", ""]
    for row in commits:
        lines.append(
            f"- `{row['sha'][:12]}` — {row['committed_at']} — {row['subject']}"
        )

    lines += [
        "",
        "## Resume protocol",
        "",
    ]
    for i, item in enumerate(snapshot["resume_protocol"], 1):
        lines.append(f"{i}. {item}")

    lines += [
        "",
        "## Machine-readable companion",
        "",
        "`registry/JANUS_CONTEXT_CACHE_CURRENT.json` contains the complete indexed snapshot, evidence excerpts, hashes, and recent commit list.",
        "",
        "Historical snapshots are append-only under `registry/context_cache/history/<source-head>.json`.",
        "",
    ]
    return "\n".join(lines)


def canonical_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def check_equal(path: Path, expected: str) -> bool:
    if not path.exists():
        print(f"STALE: missing {relative(path)}")
        return False
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        print(f"STALE: {relative(path)} differs from generated snapshot")
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; fail if CURRENT JSON/Markdown/history are stale.",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Update current snapshot without writing append-only history.",
    )
    args = parser.parse_args()

    config = load_config()
    snapshot = build_snapshot(config)
    json_text = canonical_json(snapshot)
    md_text = render_markdown(snapshot)
    history_path = HISTORY_DIR / f"{snapshot['source_head']}.json"

    if args.check:
        ok = check_equal(CURRENT_JSON, json_text) and check_equal(CURRENT_MD, md_text)
        if not args.no_history:
            ok = check_equal(history_path, json_text) and ok
        if not ok:
            return 1
        print(f"JANUS_CONTEXT_CACHE_CHECK=PASS source_head={snapshot['source_head']}")
        return 0

    CURRENT_JSON.parent.mkdir(parents=True, exist_ok=True)
    CURRENT_MD.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    CURRENT_JSON.write_text(json_text, encoding="utf-8")
    CURRENT_MD.write_text(md_text, encoding="utf-8")
    if not args.no_history:
        if history_path.exists() and history_path.read_text(encoding="utf-8") != json_text:
            raise RuntimeError(
                f"history collision: {relative(history_path)} already exists with different content"
            )
        history_path.write_text(json_text, encoding="utf-8")

    print(
        "JANUS_CONTEXT_CACHE_UPDATE=PASS "
        f"source_head={snapshot['source_head']} "
        f"scientific_artifacts={snapshot['changed_scientific_artifact_count']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
