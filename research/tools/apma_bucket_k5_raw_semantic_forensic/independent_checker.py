from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-K5-RAW-REACHABILITY-SEMANTIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC"
CANDIDATE = Path("research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py")
CANDIDATE_BLOB = "4128f0db77dfc1391b6ec539f201250bfb3d8b6e"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_DEPTH_CAP_RAW_REACHABILITY_AND_SEMANTIC_NONTRIVIALITY_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "f40332052fccf28d774a3bfbc8d056c1edb390cb"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_obj(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "candidate_frozen": blob(r / CANDIDATE) == CANDIDATE_BLOB,
        "prereg_frozen": blob(r / PREREG) == PREREG_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def exact_two_rows() -> list[tuple[int, int, int, int]]:
    out = []
    for n in range(16):
        bits = tuple((n >> (3 - i)) & 1 for i in range(4))
        if sum(bits) == 2:
            out.append(bits)
    return out


def reconstruct_probe(mode: str) -> dict:
    raw = copy.deepcopy(cc_v1.filtered_still_overbudget_control())
    names = [f"sticky_{i}" for i in range(5)]
    targets = [next(row for row in raw["constraints"] if row["id"] == name) for name in names]
    fresh = list(range(max(raw["variables"]) + 1, max(raw["variables"]) + 11))
    raw["variables"] += fresh
    edge_index: dict[frozenset[int], int] = {}
    k = 0
    for i in range(5):
        for j in range(i + 1, 5):
            edge_index[frozenset((i, j))] = fresh[k]
            k += 1
    patterns = [tuple(bits) for bits in itertools.product((0, 1), repeat=4)] if mode == "FULL_CUBE" else exact_two_rows()
    for i, rel in enumerate(targets):
        old_scope = list(rel["scope"])
        core_scope = old_scope[: len(old_scope) - 2]
        core_rows = sorted(set(tuple(int(x) for x in row[: len(row) - 2]) for row in rel["allowed"]))
        incidence = sorted(edge_index[frozenset((i, j))] for j in range(5) if j != i)
        rel["scope"] = core_scope + incidence
        rel["allowed"] = [list(c) + list(p) for c in core_rows for p in patterns]
    return raw


def projected(f: dict, core: list[int]) -> tuple[list[int], set[tuple[int, ...]]]:
    cset = set(core)
    scope = list(map(int, f["scope"]))
    residual = [v for v in scope if v not in cset]
    pos = {v: i for i, v in enumerate(scope)}
    rows = set(tuple(int(r[pos[v]]) for v in residual) for r in f["rows"])
    return residual, rows


def bfs_components(factors: list[dict], core: list[int], removed_vars: set[int] | None = None) -> list[list[int]]:
    removed_vars = removed_vars or set()
    scopes = []
    for f in factors:
        rs, _ = projected(f, core)
        scopes.append(set(rs) - removed_vars)
    unseen = set(range(len(factors)))
    out = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        queue = [start]
        comp = []
        while queue:
            i = queue.pop(0)
            comp.append(i)
            add = sorted(j for j in unseen if scopes[i] & scopes[j])
            for j in add:
                unseen.remove(j)
                queue.append(j)
        out.append(sorted(comp))
    return sorted(out, key=lambda x: (x[0], len(x), x))


def graph_receipt(factors: list[dict], core: list[int], comp: list[int]) -> dict:
    scopes = {i: set(projected(factors[i], core)[0]) for i in comp}
    edges = []
    for p, i in enumerate(comp):
        for j in comp[p + 1:]:
            shared = tuple(sorted(scopes[i] & scopes[j]))
            if shared:
                edges.append((i, j, shared))
    return {
        "nodes": len(comp),
        "edges": len(edges),
        "complete": len(edges) == len(comp) * (len(comp) - 1) // 2,
        "single_variable_edges": all(len(shared) == 1 for _, _, shared in edges),
        "edge_variables": sorted(shared[0] for _, _, shared in edges if len(shared) == 1),
    }


def relation_fingerprint_independent(rel: set[tuple[int, ...]]) -> dict[str, bool]:
    if not rel:
        raise AssertionError("EMPTY_RELATION_OUT_OF_SCOPE")
    arity = len(next(iter(rel)))
    zero = tuple(0 for _ in range(arity)) in rel
    one = tuple(1 for _ in range(arity)) in rel
    horn = all(tuple(a & b for a, b in zip(x, y)) in rel for x in rel for y in rel)
    dual = all(tuple(a | b for a, b in zip(x, y)) in rel for x in rel for y in rel)
    bij = all(tuple(1 if a + b + c >= 2 else 0 for a, b, c in zip(x, y, z)) in rel for x in rel for y in rel for z in rel)
    affine = all(tuple(a ^ b ^ c for a, b, c in zip(x, y, z)) in rel for x in rel for y in rel for z in rel)
    return {"ZERO_VALID": zero, "ONE_VALID": one, "HORN": horn, "DUAL_HORN": dual, "BIJUNCTIVE": bij, "AFFINE": affine}


def is_universal(rows: set[tuple[int, ...]], arity: int) -> bool:
    expected = set(tuple((n >> (arity - 1 - i)) & 1 for i in range(arity)) for n in range(1 << arity))
    return rows == expected


def normalize(factors: list[dict], core: list[int]) -> tuple[list[dict], list[str]]:
    kept = []
    removed = []
    for f in factors:
        rs, rows = projected(f, core)
        if is_universal(rows, len(rs)):
            removed.append(str(f["id"]))
        else:
            kept.append(f)
    return kept, sorted(removed)


def unique_k5_component(factors: list[dict], core: list[int]) -> tuple[list[int] | None, dict | None]:
    comps = bfs_components(factors, core)
    candidates = []
    for c in comps:
        if len(c) == 5:
            g = graph_receipt(factors, core, c)
            if g["complete"] and g["edges"] == 10 and g["single_variable_edges"]:
                candidates.append((c, g))
    return candidates[0] if len(candidates) == 1 else (None, None)


def both_single_values_survive(factors: list[dict], core: list[int], comp: list[int], edge_vars: list[int]) -> bool:
    comp_set = set(comp)
    for v in edge_vars:
        for value in (0, 1):
            for i, f in enumerate(factors):
                if i not in comp_set:
                    continue
                rs, rows = projected(f, core)
                if v not in rs:
                    continue
                p = rs.index(v)
                if not any(row[p] == value for row in rows):
                    return False
    return True


def all_up_to_three_removals_connected(factors: list[dict], core: list[int], comp: list[int], edge_vars: list[int]) -> bool:
    local = [factors[i] for i in comp]
    for k in (1, 2, 3):
        for rem in itertools.combinations(edge_vars, k):
            cs = bfs_components(local, core, set(rem))
            if len(cs) != 1 or len(cs[0]) != 5:
                return False
    return True


def inspect(mode: str) -> dict:
    raw = reconstruct_probe(mode)
    canonical = raw_basis.canonicalize_raw(raw)
    prep = v38._prepare(raw)
    result = {"mode": mode, "raw_sha256": sha256_obj(canonical), "prepare_status": prep.get("status")}
    if prep.get("status") != "READY":
        return result
    factors = prep["conditioned"]
    core = prep["core"]
    comp, graph = unique_k5_component(factors, core)
    sem = []
    for f in factors:
        rs, rows = projected(f, core)
        sem.append({
            "id": str(f["id"]),
            "arity": len(rs),
            "tuple_count": len(rows),
            "universal": is_universal(rows, len(rs)),
            "fingerprint": relation_fingerprint_independent(rows),
        })
    kept, removed = normalize(factors, core)
    comp2, graph2 = unique_k5_component(kept, core) if kept else (None, None)
    if comp is not None and graph is not None:
        edge_vars = graph["edge_variables"]
        single_survive = both_single_values_survive(factors, core, comp, edge_vars)
        up3 = all_up_to_three_removals_connected(factors, core, comp, edge_vars)
    else:
        edge_vars = []
        single_survive = False
        up3 = False
    if comp2 is not None and graph2 is not None:
        edge_vars2 = graph2["edge_variables"]
        single_survive2 = both_single_values_survive(kept, core, comp2, edge_vars2)
        up3_2 = all_up_to_three_removals_connected(kept, core, comp2, edge_vars2)
    else:
        single_survive2 = False
        up3_2 = False
    result.update({
        "component_sizes_before": [len(c) for c in bfs_components(factors, core)],
        "k5_before": graph,
        "semantics": sem,
        "removed_universal_factor_ids": removed,
        "component_sizes_after": [len(c) for c in bfs_components(kept, core)] if kept else [],
        "k5_after": graph2,
        "fixed_depth_open_independent_before": bool(comp is not None and single_survive and up3),
        "fixed_depth_open_independent_after": bool(comp2 is not None and single_survive2 and up3_2),
    })
    return result


def main() -> None:
    guard = source_guard()
    if not guard["ok"]:
        print(json.dumps({"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard}, sort_keys=True))
        return
    full = inspect("FULL_CUBE")
    exact2 = inspect("EXACT_2_OF_4")
    exact2_sem = [s for s in exact2.get("semantics", []) if s["arity"] == 4 and s["tuple_count"] == 6]
    full_sem = [s for s in full.get("semantics", []) if s["arity"] == 4 and s["tuple_count"] == 16]
    checks = {
        "A_prepare_ready": full.get("prepare_status") == "READY",
        "A_k5_before": bool(full.get("k5_before")),
        "A_five_universal_k5_relations": len(full_sem) == 5 and all(s["universal"] for s in full_sem),
        "A_k5_removed": full.get("k5_after") is None,
        "B_prepare_ready": exact2.get("prepare_status") == "READY",
        "B_k5_before": bool(exact2.get("k5_before")),
        "B_five_exact2_non_schaefer": len(exact2_sem) == 5 and all(not any(s["fingerprint"].values()) for s in exact2_sem),
        "B_k5_survives": bool(exact2.get("k5_after")),
        "B_fixed_depth_open_before": exact2.get("fixed_depth_open_independent_before") is True,
        "B_fixed_depth_open_after": exact2.get("fixed_depth_open_independent_after") is True,
    }
    out = {
        "artifact_id": ARTIFACT_ID,
        "verdict": VERDICT if all(checks.values()) else "FAIL_DIAGNOSTIC_EXPECTED_INVARIANT",
        "source_guard": guard,
        "checks": checks,
        "raw_k5_full_cube": full,
        "raw_k5_exact_two_of_four": exact2,
        "resource_receipt": {
            "size4_boolean_branches_executed": 0,
            "solver_calls": 0,
            "carrier_calls": 0,
            "unbounded_recursive_calls": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "candidate_fixture_helpers_used": False,
            "candidate_topology_helpers_used": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "SIZE4_BRANCHING_LICENSED": False,
            "GENERAL_RAW_K5_FREQUENCY_OR_NECESSITY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
