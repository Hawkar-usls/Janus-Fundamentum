#!/usr/bin/env python3
"""Build the canonical externalized JANUS working-context snapshot.

Two layers are intentionally combined:
1. `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` is the explicit semantic research
   checkpoint (frontier, established facts, anti-loop, next attacks).
2. This tool is the automatic live Git continuity/index layer around it.  It
   records the current non-cache HEAD, determines whether the semantic checkpoint
   is an ancestor of that HEAD, indexes newer commits/artifacts, and snapshots
   transport/governance state.

This persists explicit reproducible project/scientific state. It intentionally
cannot and does not persist private model chain-of-thought, hidden runtime cache,
credentials, or secrets.
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
    "P_VS_NP", "P_EQ_NP", "E8_D1", "UNIVERSAL_SELECTOR", "D1 =", "D1=",
    "STATUS", "AUTHORITY", "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7",
    "REPRESENTATION_CHANGE", "FRONTIER", "OPEN", "CLOSED", "PROVED",
    "CANDIDATE", "MATERIALIZED",
)
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt"}


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if check and proc.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config() -> dict[str, Any]:
    return load_json(CONFIG_PATH)


def resolve_ref(candidates: list[str]) -> str | None:
    for candidate in candidates:
        if git("rev-parse", "--verify", candidate, check=False):
            return candidate
    return None


def canonical_source_head() -> str:
    """Return latest commit that is not an auto-generated context-cache commit."""
    head = git("rev-parse", "HEAD")
    while True:
        subject = git("show", "-s", "--format=%s", head)
        if not subject.startswith(CACHE_COMMIT_PREFIX):
            return head
        head = git("rev-parse", f"{head}^")


def source_commit_time(head: str) -> str:
    return git("show", "-s", "--format=%cI", head)


def current_branch(config: dict[str, Any]) -> str:
    return (
        git("branch", "--show-current", check=False)
        or os.environ.get("GITHUB_REF_NAME")
        or config["canonical_branch"]
    )


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
        if marker.endswith("/") and path.startswith(marker):
            return True
        if path == marker:
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
    text = path.read_text(encoding="utf-8", errors="replace")
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


def commit_rows(revision: str, limit: int, reverse: bool = False) -> list[dict[str, str]]:
    fmt = "%H%x09%cI%x09%s"
    args = ["log", revision, f"-n{limit}", f"--pretty=format:{fmt}"]
    if reverse:
        args.append("--reverse")
    raw = git(*args, check=False)
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


def ancestor_relation(old: str | None, live: str) -> str:
    if not old:
        return "SEMANTIC_SOURCE_MISSING"
    if old == live:
        return "EXACT"
    if subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", old, live],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0:
        return "LIVE_DESCENDS_FROM_SEMANTIC_CACHE"
    if subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", live, old],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0:
        return "SEMANTIC_CACHE_AHEAD_OF_LIVE"
    return "DIVERGED_OR_SOURCE_MISSING"


def load_semantic_checkpoint(config: dict[str, Any], source_head: str) -> dict[str, Any]:
    rel = config.get("semantic_resume_cache")
    if not rel:
        return {"exists": False, "relation": "UNCONFIGURED"}
    path = ROOT / rel
    if not path.exists():
        return {"exists": False, "path": rel, "relation": "MISSING"}

    obj = load_json(path)
    semantic_source = obj.get("source_scientific_head")
    relation = ancestor_relation(semantic_source, source_head)

    boundary = obj.get("scientific_boundary", {})
    config_fw = config["scientific_firewall"]
    for key in ("P_VS_NP", "E8_D1"):
        if key in boundary and boundary[key] != config_fw.get(key):
            raise RuntimeError(
                f"scientific firewall disagreement for {key}: "
                f"semantic={boundary[key]!r} config={config_fw.get(key)!r}"
            )

    newer: list[dict[str, str]] = []
    if relation == "LIVE_DESCENDS_FROM_SEMANTIC_CACHE":
        newer = commit_rows(f"{semantic_source}..{source_head}", 200, reverse=True)

    return {
        "exists": True,
        "path": rel,
        "sha256": file_sha256(path),
        "semantic_source_head": semantic_source,
        "relation_to_live_source_head": relation,
        "commits_after_semantic_checkpoint": newer,
        "checkpoint": obj,
    }


def working_tree_state() -> dict[str, Any]:
    raw = git("status", "--porcelain", check=False)
    rows = [line for line in raw.splitlines() if line]
    return {"clean": not rows, "porcelain": rows[:200], "truncated": len(rows) > 200}


def build_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    source_head = canonical_source_head()
    base_ref = resolve_ref(config.get("base_refs", []))
    all_changed = changed_paths(base_ref, source_head)
    scientific = [
        p for p in all_changed
        if scientific_path(p, config) and not generated_path(p, config)
    ]
    index = [path_record(p) for p in scientific]
    limit = int(config.get("status_scan_limit_per_file", 100))
    must_read = [path_record(p, limit) for p in config.get("must_read", [])]
    transport = [path_record(p) for p in config.get("tracked_transport_paths", [])]
    semantic = load_semantic_checkpoint(config, source_head)

    declared: list[dict[str, Any]] = []
    for rec in must_read:
        if rec.get("status_tokens"):
            declared.append({"path": rec["path"], "tokens": rec["status_tokens"]})

    if semantic.get("exists"):
        live_frontier = semantic["checkpoint"].get("current_research_state", {})
    else:
        live_frontier = config.get("frontier_seed_fallback_only", {})

    return {
        "schema_version": "JANUS_CONTEXT_CACHE_v1.1",
        "generated_from_source_commit_time": source_commit_time(source_head),
        "scope": config["scope"],
        "repository": config["repository"],
        "canonical_pr": config["canonical_pr"],
        "branch": current_branch(config),
        "source_head": source_head,
        "base_ref": base_ref,
        "active_goal": config["active_goal"],
        "scientific_firewall": config["scientific_firewall"],
        "semantic_resume_state": semantic,
        "live_frontier": live_frontier,
        "transport_state": transport,
        "must_read_artifacts": must_read,
        "declared_status_evidence": declared,
        "recent_commits": commit_rows(
            source_head, int(config.get("recent_commit_limit", 100))
        ),
        "changed_scientific_artifact_count": len(index),
        "changed_scientific_artifact_index": index,
        "working_tree": working_tree_state(),
        "resume_protocol": [
            "Read JANUS_CONTEXT_CACHE_START_HERE.md.",
            "Read docs/JANUS_CONTEXT_CACHE_CURRENT.md.",
            "Treat .janus/P_VS_NP_STREAM_CACHE_CURRENT.json as the semantic frontier/next-action checkpoint and registry/JANUS_CONTEXT_CACHE_CURRENT.json as the automatic live Git continuity/index layer.",
            "If relation_to_live_source_head is LIVE_DESCENDS_FROM_SEMANTIC_CACHE, ingest every listed newer non-cache commit before continuing mathematics.",
            "If the relation is DIVERGED_OR_SOURCE_MISSING or SEMANTIC_CACHE_AHEAD_OF_LIVE, stop writes and reconcile Git history.",
            "Fetch must-read/critical artifacts and run anti-duplication/source checks before a new theorem or experiment.",
            "Never promote P_VS_NP, E8_D1, or a PA/NM identifier from cache text alone; promotion requires governance/checker/CI."
        ],
    }


def render_markdown(snapshot: dict[str, Any]) -> str:
    fw = snapshot["scientific_firewall"]
    semantic = snapshot["semantic_resume_state"]
    frontier = snapshot["live_frontier"]
    transport = snapshot["transport_state"]
    must_read = snapshot["must_read_artifacts"]
    commits = snapshot["recent_commits"][:25]

    lines = [
        "# JANUS Context Cache — CURRENT",
        "",
        "> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.",
        "",
        f"- **Repository:** `{snapshot['repository']}`",
        f"- **PR:** `#{snapshot['canonical_pr']}`",
        f"- **Branch:** `{snapshot['branch']}`",
        f"- **Live source HEAD:** `{snapshot['source_head']}`",
        f"- **Source commit time:** `{snapshot['generated_from_source_commit_time']}`",
        f"- **Indexed changed scientific artifacts:** `{snapshot['changed_scientific_artifact_count']}`",
        "",
        "## Continuity status",
        "",
    ]
    if semantic.get("exists"):
        lines += [
            f"- Semantic cache: `{semantic['path']}`",
            f"- Semantic source HEAD: `{semantic.get('semantic_source_head')}`",
            f"- Relation: **`{semantic.get('relation_to_live_source_head')}`**",
            f"- Commits after semantic checkpoint: `{len(semantic.get('commits_after_semantic_checkpoint', []))}`",
        ]
    else:
        lines.append(f"- Semantic cache unavailable: **{semantic.get('relation')}**")

    lines += [
        "",
        "## Scientific firewall",
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
        "## Semantic live frontier",
        "",
    ]

    if frontier.get("frontier_name"):
        lines.append(f"- **Frontier:** `{frontier['frontier_name']}`")
    if frontier.get("carrier"):
        lines.append(f"- **Carrier:** {frontier['carrier']}")
    for item in frontier.get("established", []):
        lines.append(f"- Established: {item}")
    if frontier.get("live_split"):
        lines += ["", "### Live split", "", "```json", json.dumps(frontier["live_split"], indent=2, ensure_ascii=False), "```"]
    if frontier.get("next_attack"):
        lines += ["", "### Next attack", ""]
        for i, item in enumerate(frontier["next_attack"], 1):
            lines.append(f"{i}. {item}")
    if not frontier.get("frontier_name"):
        for key, value in frontier.items():
            lines.append(f"- `{key}` — {value}")

    newer = semantic.get("commits_after_semantic_checkpoint", []) if semantic.get("exists") else []
    if newer:
        lines += ["", "## Commits newer than semantic checkpoint — MUST INGEST", ""]
        for row in newer[-80:]:
            lines.append(f"- `{row['sha'][:12]}` — {row['committed_at']} — {row['subject']}")

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
        lines.append(f"- `{row['sha'][:12]}` — {row['committed_at']} — {row['subject']}")

    lines += ["", "## Resume protocol", ""]
    for i, item in enumerate(snapshot["resume_protocol"], 1):
        lines.append(f"{i}. {item}")

    lines += [
        "",
        "## Scope boundary",
        "",
        "This repository cache stores explicit scientific/project context only. It deliberately excludes private model chain-of-thought, hidden runtime cache, credentials, and secrets.",
        "",
        "## Machine-readable companion",
        "",
        "`registry/JANUS_CONTEXT_CACHE_CURRENT.json` contains the complete live index and the embedded semantic checkpoint. History is append-only under `registry/context_cache/history/<source-head>.json`.",
        "",
    ]
    return "\n".join(lines)


def canonical_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def check_equal(path: Path, expected: str) -> bool:
    if not path.exists():
        print(f"STALE: missing {relative(path)}")
        return False
    if path.read_text(encoding="utf-8") != expected:
        print(f"STALE: {relative(path)} differs from generated snapshot")
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--no-history", action="store_true")
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
            raise RuntimeError(f"history collision: {relative(history_path)}")
        history_path.write_text(json_text, encoding="utf-8")

    print(
        "JANUS_CONTEXT_CACHE_UPDATE=PASS "
        f"source_head={snapshot['source_head']} "
        f"semantic_relation={snapshot['semantic_resume_state'].get('relation_to_live_source_head', snapshot['semantic_resume_state'].get('relation'))} "
        f"scientific_artifacts={snapshot['changed_scientific_artifact_count']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
