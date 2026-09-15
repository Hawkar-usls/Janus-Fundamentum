from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as parent

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-NO-SINGLE-SEPARATOR-STRUCTURE-FORENSIC-2026-09-15-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "f0173d6a4871e0068093e85a6c1a9e7e81061513"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.8.json")
PARENT_STATE_BLOB = "1fb0635807f03167ba5c33c4cb2c52c49243b515"
PARENT_CANDIDATE = Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
PARENT_CANDIDATE_BLOB = "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"
CUT_CAP = 2


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    r = root()
    p = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": p.get("status") == "FROZEN_BEFORE_DIAGNOSTIC_IMPLEMENTATION",
        "cut_cap_two": p.get("cut_definition", {}).get("maximum_cut_size") == CUT_CAP,
        "parent_state_blob": blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_candidate_blob": blob(r / PARENT_CANDIDATE) == PARENT_CANDIDATE_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GENERAL_PARTIAL_OVERLAP_FACTORIZATION": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
    }


def residual_scope(f: dict, core: list[int]) -> list[int]:
    c = set(int(x) for x in core)
    return [int(v) for v in f["scope"] if int(v) not in c]


def components_from_scopes(scopes: list[set[int]], removed: set[int] | None = None) -> list[list[int]]:
    removed = removed or set()
    reduced = [set(s) - removed for s in scopes]
    n = len(reduced)
    parent_idx = list(range(n))

    def find(x: int) -> int:
        while parent_idx[x] != x:
            parent_idx[x] = parent_idx[parent_idx[x]]
            x = parent_idx[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra > rb:
                ra, rb = rb, ra
            parent_idx[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if reduced[i] & reduced[j]:
                union(i, j)
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted((sorted(v) for v in groups.values()), key=lambda x: (x[0], len(x), x))


def minimum_cut(scopes: list[set[int]], cap: int = CUT_CAP) -> dict:
    variables = sorted(set().union(*scopes) if scopes else set())
    base = components_from_scopes(scopes)
    if all(len(c) <= 2 for c in base):
        return {"minimum_cut_size": 0, "minimum_cuts": [[]], "tested_subsets": 0, "base_component_sizes": [len(c) for c in base]}
    tested = 0
    for size in range(1, cap + 1):
        winners: list[list[int]] = []
        for combo in itertools.combinations(variables, size):
            tested += 1
            comps = components_from_scopes(scopes, set(combo))
            if all(len(c) <= 2 for c in comps):
                winners.append(list(combo))
        if winners:
            return {"minimum_cut_size": size, "minimum_cuts": winners, "tested_subsets": tested, "base_component_sizes": [len(c) for c in base]}
    return {"minimum_cut_size": None, "minimum_cuts": [], "tested_subsets": tested, "base_component_sizes": [len(c) for c in base], "cap": cap}


def edges(factors: list[dict], core: list[int]) -> list[dict]:
    scopes = [set(residual_scope(f, core)) for f in factors]
    out = []
    for i in range(len(factors)):
        for j in range(i + 1, len(factors)):
            overlap = sorted(scopes[i] & scopes[j])
            if overlap:
                out.append({"i": i, "j": j, "left": factors[i]["id"], "right": factors[j]["id"], "overlap": overlap, "overlap_cardinality": len(overlap)})
    return out


def kruskal_tree(n: int, es: list[dict]) -> list[dict]:
    p = list(range(n))
    def find(x: int) -> int:
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x
    out = []
    for e in sorted(es, key=lambda x: (-x["overlap_cardinality"], x["left"], x["right"], x["i"], x["j"])):
        a, b = find(e["i"]), find(e["j"])
        if a == b:
            continue
        if a > b:
            a, b = b, a
        p[b] = a
        out.append(e)
        if len(out) == n - 1:
            break
    return out


def running_intersection(factors: list[dict], core: list[int], tree: list[dict]) -> dict:
    scopes = [set(residual_scope(f, core)) for f in factors]
    adj = {i: [] for i in range(len(factors))}
    for e in tree:
        adj[e["i"]].append(e["j"])
        adj[e["j"]].append(e["i"])
    failures = []
    for variable in sorted(set().union(*scopes) if scopes else set()):
        nodes = [i for i, s in enumerate(scopes) if variable in s]
        if len(nodes) <= 1:
            continue
        allowed = set(nodes)
        seen = {nodes[0]}
        stack = [nodes[0]]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v in allowed and v not in seen:
                    seen.add(v)
                    stack.append(v)
        if seen != allowed:
            failures.append({"variable": variable, "nodes": nodes, "connected_nodes": sorted(seen)})
    return {"ok": not failures, "failures": failures}


def row_map(f: dict, row: tuple[int, ...]) -> dict[int, int]:
    return {int(v): int(bit) for v, bit in zip(f["scope"], row)}


def pairwise_compatibility(factors: list[dict], es: list[dict]) -> list[dict]:
    out = []
    for e in es:
        left, right = factors[e["i"]], factors[e["j"]]
        compatible = 0
        comparisons = 0
        for lr in left["rows"]:
            lm = row_map(left, tuple(lr))
            for rr in right["rows"]:
                comparisons += 1
                rm = row_map(right, tuple(rr))
                if all(lm[v] == rm[v] for v in e["overlap"]):
                    compatible += 1
        out.append({**e, "left_rows": len(left["rows"]), "right_rows": len(right["rows"]), "row_pair_comparisons": comparisons, "compatible_pairs": compatible})
    return out


def restrict_factors(factors: list[dict], variable: int, value: int) -> dict:
    restricted = []
    for f in factors:
        scope = [int(v) for v in f["scope"]]
        rows = [tuple(int(x) for x in r) for r in f["rows"]]
        if variable not in scope:
            restricted.append({**f, "scope": scope, "rows": rows})
            continue
        pos = scope.index(variable)
        new_scope = scope[:pos] + scope[pos + 1:]
        new_rows = sorted({r[:pos] + r[pos + 1:] for r in rows if int(r[pos]) == int(value)})
        if not new_rows:
            return {"status": "EMPTY_BRANCH", "factor_id": f["id"]}
        restricted.append({**f, "scope": new_scope, "rows": new_rows})
    return {"status": "READY", "factors": restricted}


def target_data(raw: dict) -> dict:
    parent_result = parent.explain(raw)
    prep = parent._prepare(raw)
    if prep.get("status") != "READY":
        return {"status": "HALT_PARENT_PREP_NOT_READY", "parent_terminal": parent_result.get("status"), "prep_terminal": prep.get("status")}
    targets = [c for c in prep["residual_components"] if len(c) >= 3]
    if not targets:
        return {"status": "HALT_NO_GT2_COMPONENT", "parent_terminal": parent_result.get("status")}
    target = sorted(targets, key=lambda c: (-len(c), c))[0]
    factors = [prep["conditioned"][i] for i in target]
    return {"status": "READY", "parent_terminal": parent_result.get("status"), "prep": prep, "target": target, "factors": factors}


def branch_profiles(factors: list[dict], core: list[int]) -> list[dict]:
    scopes = [set(residual_scope(f, core)) for f in factors]
    variables = sorted(set().union(*scopes) if scopes else set())
    out = []
    for variable in variables:
        for value in (0, 1):
            r = restrict_factors(factors, variable, value)
            if r["status"] != "READY":
                out.append({"variable": variable, "value": value, "status": r["status"], "empty_factor_id": r.get("factor_id")})
                continue
            rs = [set(residual_scope(f, core)) for f in r["factors"]]
            comps = components_from_scopes(rs)
            out.append({
                "variable": variable,
                "value": value,
                "status": "READY",
                "component_sizes": [len(c) for c in comps],
                "minimum_cut_up_to_two": minimum_cut(rs),
            })
    return out


def profile(name: str, raw: dict) -> dict:
    d = target_data(raw)
    if d.get("status") != "READY":
        return {"name": name, **d}
    prep, factors = d["prep"], d["factors"]
    core = [int(v) for v in prep["core"]]
    scopes = [set(residual_scope(f, core)) for f in factors]
    es = edges(factors, core)
    tree = kruskal_tree(len(factors), es)
    return {
        "name": name,
        "status": "PROFILED",
        "parent_terminal": d["parent_terminal"],
        "common_core": core,
        "unique_common_state": list(prep["state"]),
        "target_component_indices": list(d["target"]),
        "target_factor_ids": [f["id"] for f in factors],
        "residual_scopes": [sorted(s) for s in scopes],
        "edges": es,
        "minimum_raw_variable_cut_up_to_two": minimum_cut(scopes),
        "kruskal_max_overlap_tree": tree,
        "running_intersection": running_intersection(factors, core, tree),
        "pairwise_compatibility": pairwise_compatibility(factors, es),
        "branch_profiles_after_one_condition": branch_profiles(factors, core),
        "resource_receipt": {
            "cut_cap": CUT_CAP,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "solver_calls": 0,
            "theorem_promotions": 0,
        },
    }


def run() -> dict:
    g = source_guard()
    if not g["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": g, "scientific_firewall": firewall()}
    controls = {
        "no_single_articulation": profile("no_single_articulation", parent.no_single_variable_articulation_control()),
        "branch_still_gt2": profile("branch_still_gt2", parent.branch_still_gt2_control()),
    }
    ok = all(x.get("status") == "PROFILED" and x.get("parent_terminal") == "OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR" for x in controls.values())
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC" if ok else "FAIL_DIAGNOSTIC_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC",
        "source_guard": g,
        "controls": controls,
        "scientific_firewall": firewall(),
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
