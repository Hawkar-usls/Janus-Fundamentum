from __future__ import annotations

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

EXPECTED_BLOBS = {
    PREREG: "7cee9892b79eb3c66af9c214564064b990f0db51",
    REVIEW: "265b35006973eea51676c248de3e2b045882202b",
    WL_RESULT: "b2f84ed9e8e1bd97c42852e02f9abd2c88f74320",
    HISTORICAL: "3704a2bfd4edac8885cf78fc345bb20912cf21a5",
    SOURCE_REGISTRY: "0886fe4b41652e52f76e862a752acab0832a5302",
    RAW_BASIS: "63490c05ef3e91a4f682f75da26ff2af811839a6",
}


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def raw_sha(raw: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(raw_basis.canonicalize_raw(raw))).hexdigest()


def relation_signature(c: dict[str, Any]) -> str:
    rows = sorted("".join(str(int(bit)) for bit in row) for row in c["allowed"])
    return f"a{len(c['scope'])}:" + "/".join(rows)


def node_key(node: tuple[str, Any]) -> tuple[str, str]:
    return node[0], str(node[1])


def canonical_rank(signatures: dict[Any, Any]) -> dict[Any, int]:
    unique = sorted(set(signatures.values()), key=repr)
    rank = {value: i for i, value in enumerate(unique)}
    return {key: rank[value] for key, value in signatures.items()}


def incidence_structure(raw: dict[str, Any]):
    nodes: list[tuple[str, Any]] = []
    adjacency: dict[tuple[str, Any], set[tuple[str, Any]]] = defaultdict(set)
    labels: dict[tuple[str, Any], str] = {}
    for v in sorted(int(x) for x in raw["variables"]):
        node = ("v", v)
        nodes.append(node)
        adjacency[node]
        labels[node] = "V"
    for c in raw["constraints"]:
        cn = ("c", str(c["id"]))
        nodes.append(cn)
        adjacency[cn]
        labels[cn] = "C:" + relation_signature(c)
        for v in sorted({int(x) for x in c["scope"]}):
            vn = ("v", v)
            adjacency[cn].add(vn)
            adjacency[vn].add(cn)
    return sorted(nodes, key=node_key), adjacency, labels


def wl1(nodes, adjacency, labels):
    colors = canonical_rank({n: (labels[n],) for n in nodes})
    rounds = 0
    while True:
        signatures = {
            n: (colors[n], tuple(sorted(colors[x] for x in adjacency[n])))
            for n in nodes
        }
        new = canonical_rank(signatures)
        rounds += 1
        if len(set(new.values())) == len(set(colors.values())):
            return new, rounds
        colors = new


def wl2(nodes, adjacency, labels):
    vertex_colors = canonical_rank({n: (labels[n],) for n in nodes})
    pairs = list(itertools.product(nodes, nodes))
    colors = canonical_rank({
        (u, v): (vertex_colors[u], vertex_colors[v], int(u == v), int(v in adjacency[u]))
        for u, v in pairs
    })
    rounds = 0
    while True:
        signatures = {}
        for u, v in pairs:
            multiset = tuple(sorted((colors[(u, w)], colors[(w, v)]) for w in nodes))
            signatures[(u, v)] = (colors[(u, v)], multiset)
        new = canonical_rank(signatures)
        rounds += 1
        if len(set(new.values())) == len(set(colors.values())):
            return new, rounds
        colors = new


def class_sizes(colors, keys) -> list[int]:
    counts = Counter(colors[k] for k in keys)
    return sorted(counts.values())


def wl_features(raw: dict[str, Any]) -> dict[str, Any]:
    nodes, adjacency, labels = incidence_structure(raw)
    variables = [n for n in nodes if n[0] == "v"]
    colors1, rounds1 = wl1(nodes, adjacency, labels)
    colors2, rounds2 = wl2(nodes, adjacency, labels)
    sizes1 = class_sizes(colors1, variables)
    sizes2 = class_sizes(colors2, [(v, v) for v in variables])
    return {
        "WL1_MAX_VARIABLE_COLOR_CLASS_SIZE": max(sizes1),
        "WL1_VARIABLE_PARTITION_IS_DISCRETE": all(x == 1 for x in sizes1),
        "WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE": max(sizes2),
        "WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE": all(x == 1 for x in sizes2),
        "_receipt": {
            "variable_count": len(variables),
            "constraint_count": sum(1 for n in nodes if n[0] == "c"),
            "incidence_vertex_count": len(nodes),
            "incidence_edge_count": sum(len(adjacency[n]) for n in nodes) // 2,
            "wl1_rounds": rounds1,
            "wl2_rounds": rounds2,
        },
    }


def reconstruct_unique_raws():
    guard = source_registry.source_guard()
    if not guard.get("ok"):
        raise RuntimeError("FROZEN_SOURCE_REGISTRY_GUARD_FAILURE")
    entries = source_registry.fixture_defs()
    if len(entries) != 26:
        raise RuntimeError(f"SOURCE_ENTRY_COUNT_MISMATCH:{len(entries)}")
    unique: dict[str, dict[str, Any]] = {}
    for entry in entries:
        canonical = raw_basis.canonicalize_raw(entry["raw"])
        sha = hashlib.sha256(canonical_bytes(canonical)).hexdigest()
        if sha not in unique:
            unique[sha] = {
                "raw": canonical,
                "aliases": [],
                "source_classes": [],
                "constructors": [],
                "first_ordinal": int(entry["ordinal"]),
            }
        unique[sha]["aliases"].append(str(entry["name"]))
        unique[sha]["source_classes"].append(str(entry["source_class"]))
        unique[sha]["constructors"].append(str(entry["constructor"]))
    if len(unique) != 23:
        raise RuntimeError(f"UNIQUE_RAW_COUNT_MISMATCH:{len(unique)}")
    return unique, guard


def main() -> dict[str, Any]:
    authority_bindings = {str(p.relative_to(ROOT)): git_blob(p) == h for p, h in EXPECTED_BLOBS.items()}
    if not all(authority_bindings.values()):
        return {"verdict": "FAIL_AUTHORITY_BINDING", "authority_bindings": authority_bindings}

    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    if review.get("review_verdict") != "PASS_CLEAN_BLIND_HISTORICAL_FALSIFIER_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE":
        return {"verdict": "FAIL_REVIEW_NOT_AUTHORIZED"}

    blocker_values = prereg["frozen_candidate_features_and_blocker_values"]
    panel = prereg["frozen_historical_closed_control_panel"]
    panel_shas = [row["raw_sha256"] for row in panel]
    if len(panel_shas) != 6 or len(set(panel_shas)) != 6:
        return {"verdict": "FAIL_FROZEN_PANEL_CONTRACT"}

    unique, source_guard = reconstruct_unique_raws()
    missing = [sha for sha in panel_shas if sha not in unique]
    if missing:
        return {"verdict": "FAIL_FROZEN_CONTROL_RECONSTRUCTION", "missing_sha256": missing}

    rows = []
    witnesses = {feature: [] for feature in sorted(blocker_values)}
    for panel_row in panel:
        sha = panel_row["raw_sha256"]
        rec = unique[sha]
        observed_aliases = sorted(set(rec["aliases"]))
        required_aliases = sorted(panel_row["aliases"])
        aliases_ok = all(alias in observed_aliases for alias in required_aliases)
        feature_values = wl_features(rec["raw"])
        matches = {}
        for feature, blocker_value in sorted(blocker_values.items()):
            match = feature_values[feature] == blocker_value
            matches[feature] = match
            if match:
                witnesses[feature].append({
                    "raw_sha256": sha,
                    "aliases": required_aliases,
                    "closing_mechanism": panel_row["closing_mechanism"],
                    "observed_value": feature_values[feature],
                })
        rows.append({
            "raw_sha256": sha,
            "required_aliases": required_aliases,
            "observed_aliases": observed_aliases,
            "aliases_ok": aliases_ok,
            "closing_mechanism": panel_row["closing_mechanism"],
            "feature_values": feature_values,
            "matches_blocker_value": matches,
        })

    if not all(row["aliases_ok"] for row in rows):
        return {"verdict": "FAIL_FROZEN_CONTROL_ALIAS_BINDING", "control_rows": rows}

    survivors = sorted(feature for feature, hits in witnesses.items() if not hits)
    falsified = sorted(feature for feature, hits in witnesses.items() if hits)
    verdict = (
        "ALL_WL_CANDIDATES_FALSIFIED_BY_HISTORICAL_CLOSED_CONTROLS"
        if not survivors
        else "WL_CANDIDATE_SURVIVOR_SET_FOUND__INDEPENDENT_REPLICATION_REQUIRED"
    )
    return {
        "artifact_id": "JANUS-TRUMP-UF20-WL-POLYTIME-HISTORICAL-CLOSED-CONTROL-FALSIFIER-CANDIDATE-2026-09-17-v1.0",
        "gate": "TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_GATE",
        "authority": "BLIND_NEGATIVE_CONTROL_FALSIFIER_ONLY__NO_REDUCTION_OR_SOLVER_DESIGN",
        "verdict": verdict,
        "authority_bindings": authority_bindings,
        "source_registry_guard_ok": bool(source_guard.get("ok")),
        "source_entry_count": 26,
        "unique_raw_count": 23,
        "frozen_control_count": len(rows),
        "frozen_candidate_count": len(blocker_values),
        "test_matrix_size": len(rows) * len(blocker_values),
        "candidate_blocker_values": blocker_values,
        "control_rows": rows,
        "falsifier_witnesses_by_feature": witnesses,
        "falsified_candidate_features": falsified,
        "surviving_candidate_features": survivors,
        "blindness_receipt": {
            "fresh_holdout_values_read_or_computed": 0,
            "controls_dropped_after_unblinding": 0,
            "candidate_features_modified_after_unblinding": 0,
            "candidate_blocker_values_modified_after_unblinding": 0,
            "thresholds_conjunctions_or_disjunctions_tested": 0,
        },
        "resource_receipt": {
            "solver_invocations": 0,
            "automorphism_or_group_searches": 0,
            "new_solver_rules": 0,
            "new_action_rules": 0,
            "new_carrier_mechanisms": 0,
            "new_reduction_mechanisms": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
