from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_raw_predecessor_nonunique_reachability_acquisition_census import census as source_registry
from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_PREREGISTRATION_2026-09-17_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_REVIEW_2026-09-17_v1.0.json"
WL_RESULT = ROOT / "research/TRUMP_UF20_02_04_05_WL_POLYTIME_STRUCTURAL_INVARIANT_RESULT_2026-09-17_v1.0.json"
HISTORICAL = ROOT / "research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_RESULT_2026-09-16.json"
SOURCE_REGISTRY = ROOT / "research/tools/apma_bucket_raw_predecessor_nonunique_reachability_acquisition_census/census.py"
RAW_BASIS = ROOT / "research/tools/apma_unseen_basis/raw_relation_basis.py"
EXPECTED = {
    PREREG: "7cee9892b79eb3c66af9c214564064b990f0db51",
    REVIEW: "265b35006973eea51676c248de3e2b045882202b",
    WL_RESULT: "b2f84ed9e8e1bd97c42852e02f9abd2c88f74320",
    HISTORICAL: "3704a2bfd4edac8885cf78fc345bb20912cf21a5",
    SOURCE_REGISTRY: "0886fe4b41652e52f76e862a752acab0832a5302",
    RAW_BASIS: "63490c05ef3e91a4f682f75da26ff2af811839a6",
}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def encoded(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def rsignature(c):
    words = sorted("".join(str(int(x)) for x in row) for row in c["allowed"])
    return (len(c["scope"]), tuple(words))


def nsort(x):
    return x[0], str(x[1])


def recolor(signatures):
    dictionary = {signature: i for i, signature in enumerate(sorted(set(signatures.values()), key=repr))}
    return {obj: dictionary[signature] for obj, signature in signatures.items()}


def build(raw):
    graph = defaultdict(set)
    label = {}
    vertices = []
    for variable in sorted(int(v) for v in raw["variables"]):
        node = ("v", variable)
        vertices.append(node)
        graph[node]
        label[node] = ("V",)
    for constraint in raw["constraints"]:
        node = ("c", str(constraint["id"]))
        vertices.append(node)
        graph[node]
        label[node] = ("C", rsignature(constraint))
        for variable in sorted({int(v) for v in constraint["scope"]}):
            vn = ("v", variable)
            graph[node].add(vn)
            graph[vn].add(node)
    return sorted(vertices, key=nsort), graph, label


def refine_one(vertices, graph, label):
    colors = recolor(label)
    rounds = 0
    while True:
        signatures = {}
        for u in vertices:
            signatures[u] = (colors[u], tuple(sorted(colors[v] for v in graph[u])))
        updated = recolor(signatures)
        rounds += 1
        if len(set(updated.values())) == len(set(colors.values())):
            return updated, rounds
        colors = updated


def refine_two(vertices, graph, label):
    vertex_colors = recolor(label)
    ordered = [(u, v) for u in vertices for v in vertices]
    colors = recolor({
        (u, v): (vertex_colors[u], vertex_colors[v], u == v, v in graph[u])
        for u, v in ordered
    })
    rounds = 0
    while True:
        signatures = {}
        for u, v in ordered:
            middle = tuple(sorted((colors[(u, w)], colors[(w, v)]) for w in vertices))
            signatures[(u, v)] = (colors[(u, v)], middle)
        updated = recolor(signatures)
        rounds += 1
        if len(set(updated.values())) == len(set(colors.values())):
            return updated, rounds
        colors = updated


def sizes(colors, domain):
    return sorted(Counter(colors[item] for item in domain).values())


def evaluate(raw):
    vertices, graph, label = build(raw)
    variable_vertices = [v for v in vertices if v[0] == "v"]
    c1, r1 = refine_one(vertices, graph, label)
    c2, r2 = refine_two(vertices, graph, label)
    s1 = sizes(c1, variable_vertices)
    s2 = sizes(c2, [(v, v) for v in variable_vertices])
    return {
        "WL1_MAX_VARIABLE_COLOR_CLASS_SIZE": max(s1),
        "WL1_VARIABLE_PARTITION_IS_DISCRETE": all(n == 1 for n in s1),
        "WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE": max(s2),
        "WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE": all(n == 1 for n in s2),
        "_receipt": {
            "variable_count": len(variable_vertices),
            "constraint_count": len(vertices) - len(variable_vertices),
            "incidence_vertex_count": len(vertices),
            "incidence_edge_count": sum(len(graph[v]) for v in vertices) // 2,
            "wl1_rounds": r1,
            "wl2_rounds": r2,
        },
    }


def reconstruct():
    guard = source_registry.source_guard()
    assert guard.get("ok")
    entries = source_registry.fixture_defs()
    assert len(entries) == 26
    unique = {}
    for entry in entries:
        raw = raw_basis.canonicalize_raw(entry["raw"])
        sha = hashlib.sha256(encoded(raw)).hexdigest()
        if sha not in unique:
            unique[sha] = {"raw": raw, "aliases": []}
        unique[sha]["aliases"].append(str(entry["name"]))
    assert len(unique) == 23
    return unique, guard


def main(candidate_path: Path):
    candidate = json.loads(candidate_path.read_text())
    prereg = json.loads(PREREG.read_text())
    bindings = {str(p.relative_to(ROOT)): blob(p) == expected for p, expected in EXPECTED.items()}
    unique, source_guard = reconstruct()
    blocker_values = prereg["frozen_candidate_features_and_blocker_values"]
    panel = prereg["frozen_historical_closed_control_panel"]

    rows = []
    witness = {name: [] for name in sorted(blocker_values)}
    for expected_control in panel:
        sha = expected_control["raw_sha256"]
        assert sha in unique
        values = evaluate(unique[sha]["raw"])
        alias_ok = all(a in set(unique[sha]["aliases"]) for a in expected_control["aliases"])
        matches = {}
        for name, blocker in sorted(blocker_values.items()):
            same = values[name] == blocker
            matches[name] = same
            if same:
                witness[name].append({
                    "raw_sha256": sha,
                    "aliases": sorted(expected_control["aliases"]),
                    "closing_mechanism": expected_control["closing_mechanism"],
                    "observed_value": values[name],
                })
        rows.append({
            "raw_sha256": sha,
            "required_aliases": sorted(expected_control["aliases"]),
            "observed_aliases": sorted(set(unique[sha]["aliases"])),
            "aliases_ok": alias_ok,
            "closing_mechanism": expected_control["closing_mechanism"],
            "feature_values": values,
            "matches_blocker_value": matches,
        })

    falsified = sorted(name for name, hits in witness.items() if hits)
    survivors = sorted(name for name, hits in witness.items() if not hits)
    expected_verdict = "ALL_WL_CANDIDATES_FALSIFIED_BY_HISTORICAL_CLOSED_CONTROLS" if not survivors else "WL_CANDIDATE_SURVIVOR_SET_FOUND__INDEPENDENT_REPLICATION_REQUIRED"
    checks = {
        "authority_bindings": all(bindings.values()),
        "source_registry_guard": bool(source_guard.get("ok")),
        "all_six_controls_evaluated": len(rows) == 6 and len({row["raw_sha256"] for row in rows}) == 6,
        "all_alias_bindings": all(row["aliases_ok"] for row in rows),
        "test_matrix_size_24": len(rows) * len(blocker_values) == 24,
        "control_rows_exact": candidate.get("control_rows") == rows,
        "falsifier_witnesses_exact": candidate.get("falsifier_witnesses_by_feature") == witness,
        "falsified_set_exact": candidate.get("falsified_candidate_features") == falsified,
        "survivor_set_exact": candidate.get("surviving_candidate_features") == survivors,
        "verdict_exact": candidate.get("verdict") == expected_verdict,
        "fresh_holdouts_unread": candidate.get("blindness_receipt", {}).get("fresh_holdout_values_read_or_computed") == 0,
        "no_control_drop": candidate.get("blindness_receipt", {}).get("controls_dropped_after_unblinding") == 0,
        "no_candidate_mutation": candidate.get("blindness_receipt", {}).get("candidate_features_modified_after_unblinding") == 0 and candidate.get("blindness_receipt", {}).get("candidate_blocker_values_modified_after_unblinding") == 0,
        "no_posthoc_combinations": candidate.get("blindness_receipt", {}).get("thresholds_conjunctions_or_disjunctions_tested") == 0,
        "no_solver_or_group_search": candidate.get("resource_receipt", {}).get("solver_invocations") == 0 and candidate.get("resource_receipt", {}).get("automorphism_or_group_searches") == 0,
        "firewall": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN" and candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
    }
    return {
        "artifact_id": "JANUS-TRUMP-UF20-WL-HISTORICAL-CLOSED-CONTROL-FALSIFIER-INDEPENDENT-CHECK-2026-09-17-v1.0",
        "verdict": "PASS_INDEPENDENT_HISTORICAL_FALSIFIER_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_HISTORICAL_FALSIFIER_VERIFICATION",
        "checks": checks,
        "independent_control_rows": rows,
        "independent_falsifier_witnesses_by_feature": witness,
        "independent_falsified_candidate_features": falsified,
        "independent_surviving_candidate_features": survivors,
        "expected_candidate_verdict": expected_verdict,
        "candidate_imported": False,
        "fresh_holdout_values_read_or_computed": 0,
        "scientific_firewall": {"P_VS_NP": "OPEN", "GENERAL_SAT_IN_P": "NOT_PROVED"},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    result = main(Path(args.candidate))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if result["verdict"].startswith("PASS_") else 1)
