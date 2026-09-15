from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as v310
from research.tools.apma_bucket_fixed_depth_122 import fixed_depth_122 as fixed

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-K5-RAW-REACHABILITY-SEMANTIC-FORENSIC-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_DEPTH_CAP_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "f40332052fccf28d774a3bfbc8d056c1edb390cb"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.15.json")
PARENT_BLOB = "30c714e4a35565d7fdacbb1d12c9be7098e7fb70"
CC = Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py")
CC_BLOB = "f103bf9b14e3b208200f429b75d0858c4963fa7c"
V36 = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
V36_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"
V38 = Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
V38_BLOB = "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"
V310 = Path("research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py")
V310_BLOB = "0853ebb9a3e273fdaeca172dbe2502cc7214cf61"
FIXED = Path("research/tools/apma_bucket_fixed_depth_122/fixed_depth_122.py")
FIXED_BLOB = "2e02bac1d78b751d22df2c50a01980ae06bd2751"
RAW_BASIS = Path("research/tools/apma_unseen_basis/raw_relation_basis.py")
RAW_BASIS_BLOB = "63490c05ef3e91a4f682f75da26ff2af811839a6"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "parent_v3_15_blob": blob(r / PARENT) == PARENT_BLOB,
        "common_core_v1_blob": blob(r / CC) == CC_BLOB,
        "residual_le2_v3_6_blob": blob(r / V36) == V36_BLOB,
        "single_v3_8_blob": blob(r / V38) == V38_BLOB,
        "pair_v3_10_blob": blob(r / V310) == V310_BLOB,
        "fixed_depth_v3_14_blob": blob(r / FIXED) == FIXED_BLOB,
        "raw_basis_blob": blob(r / RAW_BASIS) == RAW_BASIS_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GENERAL_RAW_K5_FREQUENCY_OR_NECESSITY": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        "SIZE4_BRANCHING_LICENSED": False,
        "NATURAL_BENCHMARK_FREQUENCY_EVIDENCE": False,
    }


def exact_two_of_four() -> list[tuple[int, int, int, int]]:
    return [tuple(int(x) for x in bits) for bits in itertools.product((0, 1), repeat=4) if sum(bits) == 2]


def build_raw_k5(mode: str) -> dict:
    if mode not in {"FULL_CUBE", "EXACT_2_OF_4"}:
        raise ValueError("UNKNOWN_K5_MODE")
    raw = copy.deepcopy(cc_v1.filtered_still_overbudget_control())
    targets = [next(r for r in raw["constraints"] if r["id"] == f"sticky_{i}") for i in range(5)]
    start = max(int(v) for v in raw["variables"]) + 1
    edge_var: dict[tuple[int, int], int] = {}
    nxt = start
    for i in range(5):
        for j in range(i + 1, 5):
            edge_var[(i, j)] = nxt
            nxt += 1
    raw["variables"].extend(range(start, nxt))
    patterns = list(itertools.product((0, 1), repeat=4)) if mode == "FULL_CUBE" else exact_two_of_four()
    for i, rel in enumerate(targets):
        old_scope = [int(v) for v in rel["scope"]]
        old_payload_arity = 2
        core_scope = old_scope[:-old_payload_arity]
        core_rows = sorted({tuple(int(x) for x in row[:-old_payload_arity]) for row in rel["allowed"]})
        incident = sorted(edge_var[tuple(sorted((i, j)))] for j in range(5) if j != i)
        rel["scope"] = core_scope + incident
        rel["allowed"] = [list(core) + list(bits) for core in core_rows for bits in patterns]
    return raw


def residual_relation(factor: dict, core: list[int]) -> tuple[list[int], set[tuple[int, ...]]]:
    cset = set(int(v) for v in core)
    scope = [int(v) for v in factor["scope"]]
    residual_scope = [v for v in scope if v not in cset]
    pos = {v: i for i, v in enumerate(scope)}
    rows = {
        tuple(int(row[pos[v]]) for v in residual_scope)
        for row in factor["rows"]
    }
    return residual_scope, rows


def factor_semantics(factor: dict, core: list[int]) -> dict:
    scope, rows = residual_relation(factor, core)
    cube = set(itertools.product((0, 1), repeat=len(scope)))
    fp = raw_basis.classify_language([rows])
    return {
        "factor_id": str(factor["id"]),
        "residual_scope": scope,
        "residual_arity": len(scope),
        "tuple_count": len(rows),
        "full_cube_tuple_count": len(cube),
        "universal": rows == cube,
        "fingerprint": fp,
        "relation_sha256": sha256_obj({"scope": scope, "rows": sorted(rows)}),
    }


def components(factors: list[dict], core: list[int]) -> list[list[int]]:
    scopes = [set(residual_relation(f, core)[0]) for f in factors]
    n = len(scopes)
    seen: set[int] = set()
    out: list[list[int]] = []
    for s in range(n):
        if s in seen:
            continue
        todo = [s]
        seen.add(s)
        comp: list[int] = []
        while todo:
            i = todo.pop(0)
            comp.append(i)
            for j in range(n):
                if j not in seen and scopes[i] & scopes[j]:
                    seen.add(j)
                    todo.append(j)
        out.append(sorted(comp))
    return sorted(out, key=lambda xs: (xs[0], len(xs), xs))


def component_graph(factors: list[dict], core: list[int], comp: list[int]) -> dict:
    scopes = {i: set(residual_relation(factors[i], core)[0]) for i in comp}
    edges = []
    for ai, i in enumerate(comp):
        for j in comp[ai + 1:]:
            shared = sorted(scopes[i] & scopes[j])
            if shared:
                edges.append({"a": str(factors[i]["id"]), "b": str(factors[j]["id"]), "shared": shared})
    return {
        "factor_ids": [str(factors[i]["id"]) for i in comp],
        "node_count": len(comp),
        "edge_count": len(edges),
        "edges": edges,
        "complete_graph": len(edges) == len(comp) * (len(comp) - 1) // 2,
        "all_pair_overlaps_single_variable": all(len(e["shared"]) == 1 for e in edges),
    }


def exact_universal_normalize(factors: list[dict], core: list[int]) -> dict:
    kept = []
    removed = []
    for f in factors:
        sem = factor_semantics(f, core)
        if sem["universal"]:
            removed.append(str(f["id"]))
        else:
            kept.append(f)
    return {"kept": kept, "removed_factor_ids": sorted(removed)}


def fixed_depth_structural_status(factors: list[dict], core: list[int]) -> dict:
    cs = components(factors, core)
    gt = [c for c in cs if len(c) > 2]
    if not gt:
        return {"status": "OUT_OF_SCOPE_NO_RESIDUAL_COMPONENT_GT2", "component_sizes": [len(c) for c in cs]}
    if len(gt) != 1:
        return {"status": "OUT_OF_SCOPE_MULTIPLE_GT2_COMPONENTS", "component_sizes": [len(c) for c in cs]}
    prep = {"conditioned": factors, "core": core, "residual_components": cs}
    direct = v310.pair_candidates(prep)
    if any(c["structural_ok"] for c in direct):
        return {"status": "OUT_OF_SCOPE_DIRECT_V3_10_PAIR_ALREADY_ADMISSIBLE", "component_sizes": [len(c) for c in cs]}
    plan = fixed.discover_plan_from_factors(fixed.seed_root_provenance(factors), core)
    return {
        "status": "OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND" if plan is None else "FIXED_DEPTH_1_2_2_PLAN_FOUND",
        "component_sizes": [len(c) for c in cs],
        "plan": plan,
    }


def profile_raw(raw: dict, name: str) -> dict:
    canonical = raw_basis.canonicalize_raw(raw)
    prep = v38._prepare(raw)
    out: dict[str, Any] = {
        "name": name,
        "raw_sha256": sha256_obj(canonical),
        "prepare_status": prep.get("status"),
    }
    if prep.get("status") != "READY":
        return out
    factors = prep["conditioned"]
    core = prep["core"]
    cs = components(factors, core)
    semantics = [factor_semantics(f, core) for f in factors]
    gt = [c for c in cs if len(c) > 2]
    graphs = [component_graph(factors, core, c) for c in gt]
    before_status = fixed_depth_structural_status(factors, core)
    norm = exact_universal_normalize(factors, core)
    after_cs = components(norm["kept"], core) if norm["kept"] else []
    after_gt = [c for c in after_cs if len(c) > 2]
    after_graphs = [component_graph(norm["kept"], core, c) for c in after_gt]
    after_status = fixed_depth_structural_status(norm["kept"], core)
    out.update({
        "common_core": list(core),
        "unique_common_state": list(prep["state"]),
        "conditioned_factor_count": len(factors),
        "residual_component_sizes_before": [len(c) for c in cs],
        "gt2_graphs_before": graphs,
        "factor_semantics": semantics,
        "universal_factor_ids": sorted(s["factor_id"] for s in semantics if s["universal"]),
        "nonuniversal_factor_ids": sorted(s["factor_id"] for s in semantics if not s["universal"]),
        "fixed_depth_before": before_status,
        "normalization": {
            "removed_universal_factor_ids": norm["removed_factor_ids"],
            "kept_factor_ids": [str(f["id"]) for f in norm["kept"]],
            "residual_component_sizes_after": [len(c) for c in after_cs],
            "gt2_graphs_after": after_graphs,
            "fixed_depth_after": after_status,
        },
    })
    return out


def frozen_control_census() -> list[dict]:
    raw_cases = [
        ("CC_V1_FILTERED_STILL_OVERBUDGET_CONTROL", cc_v1.filtered_still_overbudget_control()),
        ("V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", v36.residual_component_gt2_control()),
        ("V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", v38.no_single_variable_articulation_control()),
        ("V3_8_BRANCH_STILL_GT2_CONTROL", v38.branch_still_gt2_control()),
        ("V3_10_NO_PAIR_K4_CONTROL", v310.no_pair_k4_control()),
        ("V3_14_POSITIVE_K4_CONTROL", fixed.positive_k4_control()),
    ]
    out = []
    for name, raw in raw_cases:
        prep = v38._prepare(raw)
        row = {"name": name, "prepare_status": prep.get("status")}
        if prep.get("status") == "READY":
            cs = components(prep["conditioned"], prep["core"])
            gt = [c for c in cs if len(c) > 2]
            row["residual_component_sizes"] = [len(c) for c in cs]
            row["gt2_graphs"] = [component_graph(prep["conditioned"], prep["core"], c) for c in gt]
        out.append(row)
    unit = fixed.depth_cap_unit_control()
    out.append({
        "name": "V3_14_UNIT_ONLY_K5_DEPTH_CAP_CONTROL",
        "status": unit["status"],
        "factor_count": unit["factor_count"],
        "residual_variable_count": unit["residual_variable_count"],
        "unit_test_only": unit["unit_test_only"],
        "raw_reachability_authority": unit["raw_reachability_authority"],
    })
    return out


def exact_two_non_schaefer(profile: dict) -> bool:
    k5 = [s for s in profile.get("factor_semantics", []) if s["factor_id"] in {f"orig:{i}" for i in range(5)}]
    # Canonical ordering may change orig indices; identify the five arity-four, six-row non-universal K5 factors instead.
    k5 = [s for s in profile.get("factor_semantics", []) if s["residual_arity"] == 4 and s["tuple_count"] == 6 and not s["universal"]]
    return len(k5) == 5 and all(not any(s["fingerprint"].values()) for s in k5)


def k5_graph_present(profile: dict, after: bool = False) -> bool:
    graphs = profile.get("normalization", {}).get("gt2_graphs_after", []) if after else profile.get("gt2_graphs_before", [])
    return any(g["node_count"] == 5 and g["edge_count"] == 10 and g["complete_graph"] and g["all_pair_overlaps_single_variable"] for g in graphs)


def main() -> None:
    guard = source_guard()
    if not guard["ok"]:
        print(json.dumps({"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}, sort_keys=True))
        return
    full = profile_raw(build_raw_k5("FULL_CUBE"), "RAW_K5_FULL_CUBE")
    exact2 = profile_raw(build_raw_k5("EXACT_2_OF_4"), "RAW_K5_EXACT_2_OF_4")
    census = frozen_control_census()
    full_target_sem = [s for s in full.get("factor_semantics", []) if s["residual_arity"] == 4 and s["tuple_count"] == 16]
    checks = {
        "A_prepare_ready": full.get("prepare_status") == "READY",
        "A_k5_before": k5_graph_present(full, False),
        "A_five_k5_factors_universal": len(full_target_sem) == 5 and all(s["universal"] for s in full_target_sem),
        "A_k5_removed_by_exact_universal_normalization": not k5_graph_present(full, True),
        "B_prepare_ready": exact2.get("prepare_status") == "READY",
        "B_k5_before": k5_graph_present(exact2, False),
        "B_exact_two_non_schaefer": exact_two_non_schaefer(exact2),
        "B_k5_survives_universal_normalization": k5_graph_present(exact2, True),
        "B_fixed_depth_open_before": exact2.get("fixed_depth_before", {}).get("status") == "OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND",
        "B_fixed_depth_open_after": exact2.get("normalization", {}).get("fixed_depth_after", {}).get("status") == "OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND",
        "unit_k5_not_raw_authority": any(x.get("name") == "V3_14_UNIT_ONLY_K5_DEPTH_CAP_CONTROL" and x.get("unit_test_only") is True and x.get("raw_reachability_authority") is False for x in census),
    }
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": VERDICT if all(checks.values()) else "FAIL_DIAGNOSTIC_EXPECTED_INVARIANT",
        "source_guard": guard,
        "checks": checks,
        "frozen_control_census": census,
        "raw_k5_full_cube": full,
        "raw_k5_exact_two_of_four": exact2,
        "resource_receipt": {
            "raw_probe_family_count": 2,
            "size4_boolean_branches_executed": 0,
            "separator_sets_size_ge_3_executed_as_boolean_branches": 0,
            "solver_calls": 0,
            "carrier_calls": 0,
            "unbounded_recursive_calls": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raise": False,
        },
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
