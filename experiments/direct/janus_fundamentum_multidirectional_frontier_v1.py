#!/usr/bin/env python3
"""Fundamentum multidirectional frontier search v1.

This is a route/evidence-surface search, NOT a theorem prover.  It scans the
checked-out repository for committed surfaces relevant to each frozen target,
computes explicit implication reachability, and emits a deterministic report.
No corpus hit or implication path is promoted to a mathematical terminal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SCHEMA = "janus.fundamentum.multidirectional_frontier_report.v1"
ALLOWED_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}
SKIP_PREFIXES = ("research_targets/",)
MAX_FILE_BYTES = 2_000_000

RELATION_WEIGHT = {
    "MAIN": 100,
    "VERY_HIGH": 80,
    "HIGH": 65,
    "DIRECT_CONTINUATION": 85,
    "VERY_INTERESTING": 60,
    "MEDIUM": 40,
    "MEDIUM_FAR": 25,
    "ARCHITECTURALLY_POSSIBLE_MATHEMATICALLY_FAR": 5,
}


def canonical_json_bytes(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj: object) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(SKIP_PREFIXES) or any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def scan_corpus(root: Path) -> Tuple[List[Tuple[str, str]], str]:
    corpus: List[Tuple[str, str]] = []
    digest = hashlib.sha256()
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            data = path.read_bytes()
            text = data.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        corpus.append((rel, text))
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
    return corpus, digest.hexdigest()


def implication_closure(edges: List[List[str]], start: str) -> List[str]:
    adjacency: Dict[str, List[str]] = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
    seen = {start}
    queue = [start]
    order: List[str] = []
    while queue:
        cur = queue.pop(0)
        for nxt in sorted(adjacency.get(cur, [])):
            if nxt in seen:
                continue
            seen.add(nxt)
            order.append(nxt)
            queue.append(nxt)
    return order


def classify(target: dict, marker_hits: int) -> str:
    if target["fundamentum_status"] == "DOMAIN_BRIDGE_NOT_ESTABLISHED":
        return "DOMAIN_BRIDGE_REQUIRED"
    if marker_hits == 0:
        return "NO_REPOSITORY_ROUTE_SURFACE_FOUND"
    if target["relation"] == "DIRECT_CONTINUATION":
        return "ACTIVE_STRUCTURAL_ROUTE"
    return "ROUTE_SURFACE_FOUND_REQUIRES_THEOREM"


def build_report(root: Path, registry: dict) -> dict:
    corpus, corpus_digest = scan_corpus(root)
    edges = registry.get("explicit_implications", [])
    target_reports = []

    for target in registry["targets"]:
        marker_rows = []
        all_paths = set()
        total_occurrences = 0
        for marker in target["search_markers"]:
            needle = marker.casefold()
            paths = []
            occurrences = 0
            for rel, text in corpus:
                hay = text.casefold()
                count = hay.count(needle)
                if count:
                    paths.append(rel)
                    occurrences += count
                    all_paths.add(rel)
            marker_rows.append({
                "marker": marker,
                "occurrences": occurrences,
                "surface_count": len(paths),
                "surfaces": paths[:10],
            })
            total_occurrences += occurrences

        pos_closure = implication_closure(edges, target["positive_terminal"])
        neg_closure = implication_closure(edges, target["negative_terminal"])
        score = (
            RELATION_WEIGHT.get(target["relation"], 0)
            + min(len(all_paths), 20) * 3
            + min(total_occurrences, 50)
            + (20 if "P_NOT_EQUALS_NP" in pos_closure or "P_NOT_EQUALS_NP" in neg_closure else 0)
        )
        target_reports.append({
            "id": target["id"],
            "level": target["level"],
            "question": target["question"],
            "positive_terminal": target["positive_terminal"],
            "negative_terminal": target["negative_terminal"],
            "relation": target["relation"],
            "fundamentum_status": target["fundamentum_status"],
            "route_classification": classify(target, len(all_paths)),
            "marker_occurrences": total_occurrences,
            "repository_surface_count": len(all_paths),
            "repository_surfaces": sorted(all_paths)[:20],
            "marker_results": marker_rows,
            "positive_implication_closure": pos_closure,
            "negative_implication_closure": neg_closure,
            "can_reach_p_not_np_by_explicit_implication": (
                "P_NOT_EQUALS_NP" in pos_closure or "P_NOT_EQUALS_NP" in neg_closure
            ),
            "frontier_score": score,
            "next_bridge": target["next_bridge"],
            "proof_status": "NOT_PROVED_BY_THIS_SEARCH",
        })

    ranked = sorted(target_reports, key=lambda row: (-row["frontier_score"], row["id"]))
    level_counts: Dict[str, int] = {}
    route_counts: Dict[str, int] = {}
    for row in target_reports:
        level_counts[row["level"]] = level_counts.get(row["level"], 0) + 1
        route_counts[row["route_classification"]] = route_counts.get(row["route_classification"], 0) + 1

    body = {
        "schema": SCHEMA,
        "registry_schema": registry["schema"],
        "registry_semantic_sha256": sha256_obj(registry),
        "base_binding": registry["base_binding"],
        "search_policy": {
            "route_search_is_not_proof": True,
            "preferred_outcome": None,
            "resource_exhaustion_means_open": True,
            "corpus_scope": "UTF-8 committed text surfaces <= 2 MB, excluding research_targets to prevent self-hit inflation",
        },
        "corpus_semantic_sha256": corpus_digest,
        "scanned_surface_count": len(corpus),
        "target_count": len(target_reports),
        "level_counts": dict(sorted(level_counts.items())),
        "route_counts": dict(sorted(route_counts.items())),
        "targets": target_reports,
        "ranked_frontier": [row["id"] for row in ranked],
        "global_terminal": "OPEN",
        "forbidden_promotions_preserved": registry["global_forbidden_claims"],
    }
    body["report_semantic_sha256"] = sha256_obj(body)
    return body


def validate_registry(registry: dict) -> None:
    assert registry["schema"] == "janus.fundamentum.research_target_registry.v1"
    assert registry["policy"]["preferred_outcome"] is None
    assert registry["policy"]["route_search_is_not_proof"] is True
    targets = registry["targets"]
    assert len(targets) == 23, len(targets)
    ids = [t["id"] for t in targets]
    assert len(ids) == len(set(ids))
    assert ids[0] == "A0_P_VS_NP"
    assert {t["level"] for t in targets} == {"A0", "A1", "A2", "A3", "A4"}
    for target in targets:
        for key in (
            "id", "level", "question", "positive_terminal", "negative_terminal",
            "relation", "fundamentum_status", "search_markers", "next_bridge"
        ):
            assert target.get(key), (target.get("id"), key)
        assert target["positive_terminal"] != target["negative_terminal"]
        assert len(target["search_markers"]) >= 3
    edges = registry["explicit_implications"]
    assert ["NP_NOT_SUBSETEQ_PPOLY", "P_NOT_EQUALS_NP"] in edges
    assert ["NP_NOT_EQUALS_CONP", "P_NOT_EQUALS_NP"] in edges
    assert ["ETH_TRUE", "P_NOT_EQUALS_NP"] in edges
    assert ["SETH_TRUE", "ETH_TRUE"] in edges
    assert registry["base_binding"]["current_ceiling"]["P_VS_NP"] == "OPEN"
    assert registry["base_binding"]["current_ceiling"]["B5_COMPLETE"] is False


def self_test() -> None:
    # Pure policy/graph tests; repository-dependent search is exercised by CI generation+verifier.
    sample = {
        "schema": "janus.fundamentum.research_target_registry.v1",
        "policy": {"preferred_outcome": None, "route_search_is_not_proof": True},
        "base_binding": {"current_ceiling": {"P_VS_NP": "OPEN", "B5_COMPLETE": False}},
        "targets": [],
        "explicit_implications": [
            ["SETH_TRUE", "ETH_TRUE"],
            ["ETH_TRUE", "P_NOT_EQUALS_NP"],
        ],
    }
    assert implication_closure(sample["explicit_implications"], "SETH_TRUE") == ["ETH_TRUE", "P_NOT_EQUALS_NP"]
    assert implication_closure(sample["explicit_implications"], "P_EQUALS_NP") == []
    assert classify({"fundamentum_status": "DOMAIN_BRIDGE_NOT_ESTABLISHED", "relation": "MEDIUM"}, 100) == "DOMAIN_BRIDGE_REQUIRED"
    assert classify({"fundamentum_status": "OPEN", "relation": "DIRECT_CONTINUATION"}, 1) == "ACTIVE_STRUCTURAL_ROUTE"
    assert classify({"fundamentum_status": "OPEN", "relation": "HIGH"}, 0) == "NO_REPOSITORY_ROUTE_SURFACE_FOUND"
    assert classify({"fundamentum_status": "OPEN", "relation": "HIGH"}, 1) == "ROUTE_SURFACE_FOUND_REQUIRES_THEOREM"
    print("MULTIDIRECTIONAL_FRONTIER_SELF_TEST = PASS")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--registry", default="research_targets/FUNDAMENTUM_RESEARCH_TARGET_REGISTRY_V1.json")
    ap.add_argument("--output", default="artifacts/fundamentum_multidirectional_frontier_v1.json")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    root = Path(args.root).resolve()
    registry_path = (root / args.registry).resolve()
    registry = load_json(registry_path)
    validate_registry(registry)
    report = build_report(root, registry)
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"TARGET_COUNT = {report['target_count']}")
    print(f"SCANNED_SURFACE_COUNT = {report['scanned_surface_count']}")
    print(f"GLOBAL_TERMINAL = {report['global_terminal']}")
    print("TOP_FRONTIER = " + ",".join(report["ranked_frontier"][:10]))
    for row in sorted(report["targets"], key=lambda x: x["id"]):
        print(
            f"TARGET {row['id']} | {row['route_classification']} | "
            f"surfaces={row['repository_surface_count']} | occurrences={row['marker_occurrences']} | "
            f"score={row['frontier_score']}"
        )
    print(f"REPORT_SEMANTIC_SHA256 = {report['report_semantic_sha256']}")


if __name__ == "__main__":
    main()
