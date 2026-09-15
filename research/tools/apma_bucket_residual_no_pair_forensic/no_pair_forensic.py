from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-NO-PAIR-SEPARATOR-STRUCTURE-FORENSIC-2026-09-15-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_PAIR_SEPARATOR_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "2601a67309bf38ff9acb19ffb1797573c097375e"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.10.json")
PARENT_BLOB = "6de3adf858ae83a25b32bd0dfd4262c525e0fb55"
PAIR = Path("research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py")
PAIR_BLOB = "0853ebb9a3e273fdaeca172dbe2502cc7214cf61"
CAP = 3


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "parent_v3_10_blob": blob(r / PARENT) == PARENT_BLOB,
        "pair_v3_10_blob": blob(r / PAIR) == PAIR_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def rscope(f: dict, core: list[int]) -> set[int]:
    c = set(int(v) for v in core)
    return {int(v) for v in f["scope"] if int(v) not in c}


def components(scopes: list[set[int]]) -> list[list[int]]:
    n = len(scopes)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for i in range(n):
        for j in range(i + 1, n):
            if scopes[i] & scopes[j]:
                union(i, j)
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted((sorted(v) for v in groups.values()), key=lambda x: (x[0], len(x), x))


def edges(scopes: list[set[int]]) -> list[dict]:
    out = []
    for i in range(len(scopes)):
        for j in range(i + 1, len(scopes)):
            ov = sorted(scopes[i] & scopes[j])
            if ov:
                out.append({"i": i, "j": j, "overlap": ov, "overlap_cardinality": len(ov)})
    return out


def disconnects(scopes: list[set[int]], cut: tuple[int, ...]) -> bool:
    return len(components([s - set(cut) for s in scopes])) > len(components(scopes))


def cut_profile(scopes: list[set[int]], cap: int = CAP) -> dict:
    vs = sorted(set().union(*scopes) if scopes else set())
    by_size: dict[str, list[list[int]]] = {}
    examined: dict[str, int] = {}
    minimum = None
    minimum_cuts: list[list[int]] = []
    for k in range(1, min(cap, len(vs)) + 1):
        combos = list(itertools.combinations(vs, k))
        examined[str(k)] = len(combos)
        hits = [list(c) for c in combos if disconnects(scopes, c)]
        by_size[str(k)] = hits
        if hits and minimum is None:
            minimum = k
            minimum_cuts = hits
            break
    return {
        "variables": vs,
        "cap": cap,
        "minimum_size_up_to_cap": minimum,
        "minimum_cuts": minimum_cuts,
        "cuts_by_size_until_minimum": by_size,
        "candidate_sets_examined": examined,
    }


def kruskal_tree(scopes: list[set[int]], es: list[dict]) -> list[dict]:
    parent = list(range(len(scopes)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    out = []
    for e in sorted(es, key=lambda z: (-z["overlap_cardinality"], z["i"], z["j"], z["overlap"])):
        a, b = find(e["i"]), find(e["j"])
        if a == b:
            continue
        parent[max(a, b)] = min(a, b)
        out.append(e)
        if len(out) == len(scopes) - 1:
            break
    return out


def running_intersection(scopes: list[set[int]], tree: list[dict]) -> dict:
    adj = {i: [] for i in range(len(scopes))}
    for e in tree:
        adj[e["i"]].append(e["j"])
        adj[e["j"]].append(e["i"])
    failures = []
    for v in sorted(set().union(*scopes) if scopes else set()):
        nodes = [i for i, s in enumerate(scopes) if v in s]
        if len(nodes) <= 1:
            continue
        allowed = set(nodes)
        seen = {nodes[0]}
        stack = [nodes[0]]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w in allowed and w not in seen:
                    seen.add(w)
                    stack.append(w)
        if seen != allowed:
            failures.append(v)
    return {"ok": not failures, "failure_variables": failures}


def amap(f: dict, row: tuple[int, ...] | list[int]) -> dict[int, int]:
    return {int(v): int(b) for v, b in zip(f["scope"], row)}


def pairwise_compatibility(fs: list[dict], es: list[dict]) -> list[dict]:
    out = []
    for e in es:
        a, b = fs[e["i"]], fs[e["j"]]
        ov = e["overlap"]
        count = 0
        for x in a["rows"]:
            ax = amap(a, x)
            for y in b["rows"]:
                ay = amap(b, y)
                if all(ax[v] == ay[v] for v in ov):
                    count += 1
        out.append({**e, "left_rows": len(a["rows"]), "right_rows": len(b["rows"]), "compatible_pairs": count})
    return out


def restrict_one(f: dict, variable: int, value: int) -> dict | None:
    scope = [int(v) for v in f["scope"]]
    if variable not in scope:
        return {**f, "scope": scope, "rows": [tuple(int(x) for x in r) for r in f["rows"]]}
    pos = scope.index(variable)
    keep = [i for i in range(len(scope)) if i != pos]
    rows = []
    for row in f["rows"]:
        r = tuple(int(x) for x in row)
        if r[pos] == value:
            rows.append(tuple(r[i] for i in keep))
    rows = sorted(set(rows))
    if not rows:
        return None
    return {**f, "scope": [scope[i] for i in keep], "rows": rows}


def single_condition_profiles(fs: list[dict], core: list[int]) -> list[dict]:
    vs = sorted(set().union(*(rscope(f, core) for f in fs)) if fs else set())
    out = []
    for v in vs:
        branches = []
        for bit in (0, 1):
            rf = []
            empty = False
            for f in fs:
                z = restrict_one(f, v, bit)
                if z is None:
                    empty = True
                    break
                rf.append(z)
            if empty:
                branches.append({"value": bit, "exact_empty_unsat": True})
                continue
            scopes = [rscope(f, core) for f in rf]
            cp = cut_profile(scopes, CAP)
            branches.append({
                "value": bit,
                "exact_empty_unsat": False,
                "component_sizes": [len(c) for c in components(scopes)],
                "cut_profile": cp,
                "pair_cut_present": cp["minimum_size_up_to_cap"] == 2,
            })
        out.append({"variable": v, "branches": branches})
    return out


def run() -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard}

    raw = pair_v310.no_pair_k4_control()
    parent = pair_v310.explain(raw)
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"artifact_id": ARTIFACT_ID, "status": "FAIL_DIAGNOSTIC_PARENT_PREP", "parent": parent.get("status"), "prep": prep.get("status")}

    target = next(c for c in prep["residual_components"] if len(c) > 2)
    fs = [prep["conditioned"][i] for i in target]
    scopes = [rscope(f, prep["core"]) for f in fs]
    es = edges(scopes)
    tree = kruskal_tree(scopes, es)
    cp = cut_profile(scopes, CAP)
    profile = {
        "label": "K4_DISTINCT_EDGE_VARIABLES",
        "parent_terminal": parent.get("status"),
        "target_factor_indices": target,
        "factor_ids": [f["id"] for f in fs],
        "core": list(prep["core"]),
        "core_state": list(prep["state"]),
        "residual_scopes": [sorted(s) for s in scopes],
        "overlap_edges": es,
        "cut_profile": cp,
        "kruskal_tree": tree,
        "running_intersection": running_intersection(scopes, tree),
        "pairwise_compatibility": pairwise_compatibility(fs, es),
        "single_condition_profiles": single_condition_profiles(fs, prep["core"]),
        "resource_receipt": {
            "diagnostic_cap": CAP,
            "sat_separator_assignments_executed": 0,
            "separator_sets_size_ge_4_enumerated": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "external_solver_calls": 0,
            "budget_raised": False,
        },
    }
    ok = (
        profile["parent_terminal"] == "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR"
        and cp["minimum_size_up_to_cap"] is not None
        and profile["resource_receipt"]["three_plus_join_chains_materialized"] == 0
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_PAIR_SEPARATOR_STRUCTURE_FORENSIC" if ok else "FAIL_DIAGNOSTIC",
        "source_guard": guard,
        "profile": profile,
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
