#!/usr/bin/env python3
"""Independent verifier for Fundamentum multidirectional frontier report v1.

The verifier does not import the producer. It independently rescans the
repository, recomputes marker counts, implication closure, classifications,
ranking, corpus digest, and semantic report hash. It also enforces the theorem
ceiling: every target produced by this search remains NOT_PROVED_BY_THIS_SEARCH.

Amendment v1.2 independently enforces case-insensitive literal matching with
ASCII identifier boundaries, rejecting substring-inflated short-token counts.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPORT_SCHEMA = "janus.fundamentum.multidirectional_frontier_report.v1"
REGISTRY_SCHEMA = "janus.fundamentum.research_target_registry.v1"
SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt"}
IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}
MAX_BYTES = 2_000_000

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


def cbytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def obj_hash(value: object) -> str:
    return hashlib.sha256(cbytes(value)).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def literal_marker_count(text: str, marker: str) -> int:
    rx = re.compile(
        r"(?<![A-Za-z0-9_])" + re.escape(marker) + r"(?![A-Za-z0-9_])",
        flags=re.IGNORECASE,
    )
    return len(rx.findall(text))


def corpus(root: Path) -> Tuple[List[Tuple[str, str]], str]:
    rows: List[Tuple[str, str]] = []
    h = hashlib.sha256()
    candidates = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in SUFFIXES:
            continue
        rel = p.relative_to(root).as_posix()
        if rel.startswith("research_targets/"):
            continue
        if any(part in IGNORED_PARTS for part in p.parts):
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        candidates.append((rel, p))
    for rel, p in sorted(candidates, key=lambda item: item[0]):
        try:
            raw = p.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rows.append((rel, text))
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(raw).digest())
    return rows, h.hexdigest()


def closure(edges: List[List[str]], start: str) -> List[str]:
    graph: Dict[str, List[str]] = {}
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise AssertionError("bad implication edge")
        graph.setdefault(edge[0], []).append(edge[1])
    seen = {start}
    pending = [start]
    out: List[str] = []
    while pending:
        node = pending.pop(0)
        for nxt in sorted(graph.get(node, [])):
            if nxt not in seen:
                seen.add(nxt)
                out.append(nxt)
                pending.append(nxt)
    return out


def expected_class(target: dict, surface_count: int) -> str:
    if target["fundamentum_status"] == "DOMAIN_BRIDGE_NOT_ESTABLISHED":
        return "DOMAIN_BRIDGE_REQUIRED"
    if surface_count == 0:
        return "NO_REPOSITORY_ROUTE_SURFACE_FOUND"
    if target["relation"] == "DIRECT_CONTINUATION":
        return "ACTIVE_STRUCTURAL_ROUTE"
    return "ROUTE_SURFACE_FOUND_REQUIRES_THEOREM"


def verify_matching_semantics() -> None:
    assert literal_marker_count("NC NCX XNC _NC nc", "NC") == 2
    assert literal_marker_count("alpha PH beta ph2", "PH") == 1
    assert literal_marker_count("PIT pitfall PIT_2", "PIT") == 1
    assert literal_marker_count("P/poly and NP subseteq P/poly", "P/poly") == 2


def verify_registry(registry: dict) -> None:
    assert registry["schema"] == REGISTRY_SCHEMA
    policy = registry["policy"]
    assert policy["preferred_outcome"] is None
    assert policy["route_search_is_not_proof"] is True
    assert policy["resource_exhaustion_means_open"] is True
    assert policy["forbid_cross_target_promotion_without_explicit_implication"] is True
    targets = registry["targets"]
    assert len(targets) == 23
    ids = [t["id"] for t in targets]
    assert len(set(ids)) == 23
    assert sum(t["level"] == "A0" for t in targets) == 1
    assert sum(t["level"] == "A1" for t in targets) == 5
    assert sum(t["level"] == "A2" for t in targets) == 9
    assert sum(t["level"] == "A3" for t in targets) == 3
    assert sum(t["level"] == "A4" for t in targets) == 5
    a0 = next(t for t in targets if t["id"] == "A0_P_VS_NP")
    assert a0["positive_terminal"] == "P_EQUALS_NP"
    assert a0["negative_terminal"] == "P_NOT_EQUALS_NP"
    assert a0["fundamentum_status"] == "OPEN"
    assert registry["base_binding"]["b5_4_evidence_head"] == "e7663ed9be87ebd37bfa51c01501e74c9d5b2603"
    assert registry["base_binding"]["b5_4_proof_head"] == "135740e9ee06030ad0d029cc65cbace95af82cc1"
    ceiling = registry["base_binding"]["current_ceiling"]
    assert ceiling["ALL_INPUT_TERMINATION"] == "NOT_ESTABLISHED"
    assert ceiling["POLYNOMIAL_RUNTIME"] == "NOT_ESTABLISHED"
    assert ceiling["B5_COMPLETE"] is False
    assert ceiling["P_VS_NP"] == "OPEN"
    required_edges = {
        ("NP_NOT_SUBSETEQ_PPOLY", "P_NOT_EQUALS_NP"),
        ("NP_NOT_EQUALS_CONP", "P_NOT_EQUALS_NP"),
        ("ETH_TRUE", "P_NOT_EQUALS_NP"),
        ("SETH_TRUE", "ETH_TRUE"),
        ("PH_DOES_NOT_COLLAPSE", "P_NOT_EQUALS_NP"),
    }
    assert required_edges.issubset({tuple(e) for e in registry["explicit_implications"]})
    for target in targets:
        assert target["positive_terminal"] != target["negative_terminal"]
        assert len(target["search_markers"]) >= 3
        assert target["next_bridge"]


def verify_report(root: Path, registry: dict, report: dict) -> None:
    verify_matching_semantics()
    verify_registry(registry)
    assert report["schema"] == REPORT_SCHEMA
    assert report["registry_schema"] == REGISTRY_SCHEMA
    assert report["registry_semantic_sha256"] == obj_hash(registry)
    assert report["base_binding"] == registry["base_binding"]
    assert report["search_policy"]["route_search_is_not_proof"] is True
    assert report["search_policy"]["preferred_outcome"] is None
    assert report["search_policy"]["resource_exhaustion_means_open"] is True
    assert report["search_policy"]["marker_matching"] == "case-insensitive literal with ASCII identifier boundaries on both sides"
    assert report["global_terminal"] == "OPEN"
    assert report["forbidden_promotions_preserved"] == registry["global_forbidden_claims"]

    expected_hash_input = copy.deepcopy(report)
    supplied_report_hash = expected_hash_input.pop("report_semantic_sha256")
    assert supplied_report_hash == obj_hash(expected_hash_input)

    rows, corpus_hash = corpus(root)
    assert report["corpus_semantic_sha256"] == corpus_hash
    assert report["scanned_surface_count"] == len(rows)
    assert report["target_count"] == 23

    report_by_id = {row["id"]: row for row in report["targets"]}
    assert len(report_by_id) == 23
    edges = registry["explicit_implications"]
    expected_rank_rows = []
    level_counts: Dict[str, int] = {}
    route_counts: Dict[str, int] = {}

    for target in registry["targets"]:
        row = report_by_id[target["id"]]
        for key in ("level", "question", "positive_terminal", "negative_terminal", "relation", "fundamentum_status", "next_bridge"):
            assert row[key] == target[key], (target["id"], key)
        assert row["proof_status"] == "NOT_PROVED_BY_THIS_SEARCH"

        all_surfaces = set()
        total_occurrences = 0
        expected_marker_rows = []
        for marker in target["search_markers"]:
            surfaces = []
            occurrences = 0
            for rel, text in rows:
                count = literal_marker_count(text, marker)
                if count:
                    occurrences += count
                    surfaces.append(rel)
                    all_surfaces.add(rel)
            expected_marker_rows.append({
                "marker": marker,
                "occurrences": occurrences,
                "surface_count": len(surfaces),
                "surfaces": surfaces[:10],
            })
            total_occurrences += occurrences

        assert row["marker_results"] == expected_marker_rows
        assert row["marker_occurrences"] == total_occurrences
        assert row["repository_surface_count"] == len(all_surfaces)
        assert row["repository_surfaces"] == sorted(all_surfaces)[:20]
        assert row["route_classification"] == expected_class(target, len(all_surfaces))

        pos = closure(edges, target["positive_terminal"])
        neg = closure(edges, target["negative_terminal"])
        assert row["positive_implication_closure"] == pos
        assert row["negative_implication_closure"] == neg
        can_pneqnp = "P_NOT_EQUALS_NP" in pos or "P_NOT_EQUALS_NP" in neg
        assert row["can_reach_p_not_np_by_explicit_implication"] is can_pneqnp

        expected_score = (
            RELATION_WEIGHT.get(target["relation"], 0)
            + min(len(all_surfaces), 20) * 3
            + min(total_occurrences, 50)
            + (20 if can_pneqnp else 0)
        )
        assert row["frontier_score"] == expected_score
        expected_rank_rows.append((target["id"], expected_score))
        level_counts[target["level"]] = level_counts.get(target["level"], 0) + 1
        route_counts[row["route_classification"]] = route_counts.get(row["route_classification"], 0) + 1

    expected_ranking = [item[0] for item in sorted(expected_rank_rows, key=lambda item: (-item[1], item[0]))]
    assert report["ranked_frontier"] == expected_ranking
    assert report["level_counts"] == dict(sorted(level_counts.items()))
    assert report["route_counts"] == dict(sorted(route_counts.items()))


def expect_reject(root: Path, registry: dict, report: dict, mutate) -> None:
    bad = copy.deepcopy(report)
    mutate(bad)
    unhashed = copy.deepcopy(bad)
    unhashed.pop("report_semantic_sha256", None)
    bad["report_semantic_sha256"] = obj_hash(unhashed)
    try:
        verify_report(root, registry, bad)
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("tamper unexpectedly accepted")


def tamper_suite(root: Path, registry: dict, report: dict) -> int:
    attacks = [
        lambda r: r.__setitem__("global_terminal", "P_EQUALS_NP"),
        lambda r: r["targets"][0].__setitem__("proof_status", "PROVED"),
        lambda r: r["targets"][0].__setitem__("positive_terminal", "P_NOT_EQUALS_NP"),
        lambda r: r["targets"][0].__setitem__("route_classification", "PROVED"),
        lambda r: r["targets"][0].__setitem__("marker_occurrences", r["targets"][0]["marker_occurrences"] + 1),
        lambda r: r["targets"][0].__setitem__("repository_surface_count", r["targets"][0]["repository_surface_count"] + 1),
        lambda r: r["targets"][0].__setitem__("frontier_score", r["targets"][0]["frontier_score"] + 1000),
        lambda r: r["ranked_frontier"].reverse(),
        lambda r: r.__setitem__("corpus_semantic_sha256", "0" * 64),
        lambda r: r.__setitem__("registry_semantic_sha256", "f" * 64),
        lambda r: r["base_binding"]["current_ceiling"].__setitem__("POLYNOMIAL_RUNTIME", "ESTABLISHED"),
        lambda r: r["base_binding"]["current_ceiling"].__setitem__("B5_COMPLETE", True),
        lambda r: r["targets"][1].__setitem__("can_reach_p_not_np_by_explicit_implication", False),
        lambda r: r["targets"][3].__setitem__("negative_implication_closure", []),
        lambda r: r["targets"][-1].__setitem__("route_classification", "ACTIVE_STRUCTURAL_ROUTE"),
        lambda r: r["search_policy"].__setitem__("route_search_is_not_proof", False),
        lambda r: r["search_policy"].__setitem__("marker_matching", "substring"),
    ]
    for attack in attacks:
        expect_reject(root, registry, report, attack)
    return len(attacks)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--registry", default="research_targets/FUNDAMENTUM_RESEARCH_TARGET_REGISTRY_V1.json")
    ap.add_argument("--report", default="artifacts/fundamentum_multidirectional_frontier_v1.json")
    ap.add_argument("--tamper-test", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    registry = read_json((root / args.registry).resolve())
    report = read_json((root / args.report).resolve())
    verify_report(root, registry, report)
    print("INDEPENDENT_FRONTIER_REPLAY = PASS")
    print("BOUNDARY_AWARE_MARKER_MATCHING = PASS")
    print(f"VERIFIED_TARGET_COUNT = {report['target_count']}")
    print(f"GLOBAL_TERMINAL = {report['global_terminal']}")
    if args.tamper_test:
        n = tamper_suite(root, registry, report)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {n}/{n}")


if __name__ == "__main__":
    main()
