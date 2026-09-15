from __future__ import annotations

import itertools
import json
from collections import deque

from research.tools.apma_bucket_residual_no_single_forensic import no_single_separator_forensic as prof
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as parent

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-NO-SINGLE-SEPARATOR-STRUCTURE-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC"


def rscope(f: dict, core: list[int]) -> set[int]:
    c = set(int(x) for x in core)
    return {int(v) for v in f["scope"] if int(v) not in c}


def bfs_components(scopes: list[set[int]], removed: set[int] | None = None) -> list[list[int]]:
    removed = removed or set()
    s = [set(x) - removed for x in scopes]
    adj = {i: [] for i in range(len(s))}
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if s[i] & s[j]:
                adj[i].append(j)
                adj[j].append(i)
    seen = set()
    out = []
    for start in range(len(s)):
        if start in seen:
            continue
        q = deque([start]); seen.add(start); comp = []
        while q:
            u = q.popleft(); comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); q.append(v)
        out.append(sorted(comp))
    return sorted(out, key=lambda x: (x[0], len(x), x))


def min_cut(scopes: list[set[int]], cap: int = 2) -> dict:
    variables = sorted(set().union(*scopes) if scopes else set())
    base = bfs_components(scopes)
    if all(len(c) <= 2 for c in base):
        return {"minimum_cut_size": 0, "minimum_cuts": [[]], "base_component_sizes": [len(c) for c in base]}
    for size in range(1, cap + 1):
        wins = []
        for combo in itertools.combinations(variables, size):
            if all(len(c) <= 2 for c in bfs_components(scopes, set(combo))):
                wins.append(list(combo))
        if wins:
            return {"minimum_cut_size": size, "minimum_cuts": wins, "base_component_sizes": [len(c) for c in base]}
    return {"minimum_cut_size": None, "minimum_cuts": [], "base_component_sizes": [len(c) for c in base], "cap": cap}


def edge_list(factors: list[dict], core: list[int]) -> list[dict]:
    scopes = [rscope(f, core) for f in factors]
    out = []
    for i in range(len(scopes)):
        for j in range(i + 1, len(scopes)):
            ov = sorted(scopes[i] & scopes[j])
            if ov:
                out.append({"i": i, "j": j, "left": factors[i]["id"], "right": factors[j]["id"], "overlap": ov, "overlap_cardinality": len(ov)})
    return out


def prim_tree(n: int, edges: list[dict]) -> list[dict]:
    if n <= 1:
        return []
    used = {0}; out = []
    while len(used) < n:
        candidates = [e for e in edges if (e["i"] in used) ^ (e["j"] in used)]
        if not candidates:
            break
        e = sorted(candidates, key=lambda x: (-x["overlap_cardinality"], x["left"], x["right"], x["i"], x["j"]))[0]
        out.append(e)
        used.add(e["i"]); used.add(e["j"])
    return out


def ri_check(factors: list[dict], core: list[int], tree: list[dict]) -> dict:
    scopes = [rscope(f, core) for f in factors]
    adj = {i: [] for i in range(len(factors))}
    for e in tree:
        adj[e["i"]].append(e["j"]); adj[e["j"]].append(e["i"])
    failures = []
    for var in sorted(set().union(*scopes) if scopes else set()):
        nodes = [i for i, s in enumerate(scopes) if var in s]
        if len(nodes) <= 1:
            continue
        allowed = set(nodes); seen = {nodes[0]}; q = deque([nodes[0]])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v in allowed and v not in seen:
                    seen.add(v); q.append(v)
        if seen != allowed:
            failures.append(var)
    return {"ok": not failures, "failure_variables": failures}


def compatibility_hash(factors: list[dict], edges: list[dict]) -> list[dict]:
    out = []
    for e in edges:
        left, right = factors[e["i"]], factors[e["j"]]
        lpos = {int(v): k for k, v in enumerate(left["scope"])}
        rpos = {int(v): k for k, v in enumerate(right["scope"])}
        counts: dict[tuple[int, ...], int] = {}
        for row in right["rows"]:
            key = tuple(int(row[rpos[v]]) for v in e["overlap"])
            counts[key] = counts.get(key, 0) + 1
        compatible = 0
        for row in left["rows"]:
            key = tuple(int(row[lpos[v]]) for v in e["overlap"])
            compatible += counts.get(key, 0)
        out.append({**e, "left_rows": len(left["rows"]), "right_rows": len(right["rows"]), "compatible_pairs": compatible})
    return out


def restrict_raw(factors: list[dict], variable: int, value: int) -> dict:
    out = []
    for f in factors:
        scope = [int(v) for v in f["scope"]]
        rows = [tuple(int(x) for x in r) for r in f["rows"]]
        if variable not in scope:
            out.append({**f, "scope": scope, "rows": rows}); continue
        p = scope.index(variable)
        nr = sorted({r[:p] + r[p + 1:] for r in rows if int(r[p]) == int(value)})
        if not nr:
            return {"status": "EMPTY_BRANCH"}
        out.append({**f, "scope": scope[:p] + scope[p + 1:], "rows": nr})
    return {"status": "READY", "factors": out}


def independent_profile(raw: dict) -> dict:
    p = parent._prepare(raw)
    terminal = parent.explain(raw).get("status")
    if p.get("status") != "READY":
        return {"status": "HALT", "parent_terminal": terminal}
    targets = [c for c in p["residual_components"] if len(c) >= 3]
    target = sorted(targets, key=lambda c: (-len(c), c))[0]
    factors = [p["conditioned"][i] for i in target]
    core = [int(v) for v in p["core"]]
    scopes = [rscope(f, core) for f in factors]
    es = edge_list(factors, core)
    tree = prim_tree(len(factors), es)
    variables = sorted(set().union(*scopes) if scopes else set())
    branches = []
    for var in variables:
        for value in (0, 1):
            r = restrict_raw(factors, var, value)
            if r["status"] != "READY":
                branches.append({"variable": var, "value": value, "status": "EMPTY_BRANCH"}); continue
            rs = [rscope(f, core) for f in r["factors"]]
            branches.append({"variable": var, "value": value, "status": "READY", "component_sizes": [len(c) for c in bfs_components(rs)], "minimum_cut_up_to_two": min_cut(rs)})
    return {
        "parent_terminal": terminal,
        "target_factor_ids": [f["id"] for f in factors],
        "residual_scopes": [sorted(s) for s in scopes],
        "edges": es,
        "minimum_cut": min_cut(scopes),
        "running_intersection": ri_check(factors, core, tree),
        "pairwise": compatibility_hash(factors, es),
        "branches": branches,
    }


def normalize_pairs(rows: list[dict]) -> list[tuple]:
    return sorted((r["left"], r["right"], tuple(r["overlap"]), int(r["compatible_pairs"])) for r in rows)


def essential_branch(rows: list[dict]) -> list[tuple]:
    out = []
    for r in rows:
        mc = r.get("minimum_cut_up_to_two", {})
        out.append((r["variable"], r["value"], r["status"], tuple(r.get("component_sizes", [])), mc.get("minimum_cut_size"), tuple(tuple(x) for x in mc.get("minimum_cuts", []))))
    return sorted(out)


def run() -> dict:
    candidate = prof.run()
    indep = {
        "no_single_articulation": independent_profile(parent.no_single_variable_articulation_control()),
        "branch_still_gt2": independent_profile(parent.branch_still_gt2_control()),
    }
    checks = {"source_guard": candidate.get("source_guard", {}).get("ok") is True, "candidate_diagnostic_pass": candidate.get("status") == VERDICT}
    for name in ("no_single_articulation", "branch_still_gt2"):
        c = candidate["controls"][name]; i = indep[name]
        checks[f"{name}_parent_open"] = c.get("parent_terminal") == i.get("parent_terminal") == "OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR"
        checks[f"{name}_factor_ids"] = c.get("target_factor_ids") == i.get("target_factor_ids")
        checks[f"{name}_scopes"] = c.get("residual_scopes") == i.get("residual_scopes")
        checks[f"{name}_edges"] = [(e["left"], e["right"], e["overlap"]) for e in c.get("edges", [])] == [(e["left"], e["right"], e["overlap"]) for e in i.get("edges", [])]
        cm = c.get("minimum_raw_variable_cut_up_to_two", {}); im = i.get("minimum_cut", {})
        checks[f"{name}_minimum_cut"] = cm.get("minimum_cut_size") == im.get("minimum_cut_size") and cm.get("minimum_cuts") == im.get("minimum_cuts")
        checks[f"{name}_running_intersection"] = c.get("running_intersection", {}).get("ok") == i.get("running_intersection", {}).get("ok")
        checks[f"{name}_pairwise"] = normalize_pairs(c.get("pairwise_compatibility", [])) == normalize_pairs(i.get("pairwise", []))
        checks[f"{name}_branch_profiles"] = essential_branch(c.get("branch_profiles_after_one_condition", [])) == essential_branch(i.get("branches", []))
        checks[f"{name}_zero_join_chain"] = c.get("resource_receipt", {}).get("three_plus_join_chains_materialized") == 0
        checks[f"{name}_zero_cartesian"] = c.get("resource_receipt", {}).get("global_residual_cartesian_products_materialized") == 0
        checks[f"{name}_zero_solver"] = c.get("resource_receipt", {}).get("solver_calls") == 0
    checks["FW_p_vs_np"] = candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN"
    checks["FW_sat"] = candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED"
    verdict = VERDICT if all(checks.values()) else "FAIL_DIAGNOSTIC_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC"
    return {"artifact_id": ARTIFACT_ID, "authority": "INDEPENDENT_DIAGNOSTIC_CHECKER", "checks": checks, "candidate": candidate, "independent": indep, "verdict": verdict, "scientific_firewall": candidate.get("scientific_firewall")}


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
