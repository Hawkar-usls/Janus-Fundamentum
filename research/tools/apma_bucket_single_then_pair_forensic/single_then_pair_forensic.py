from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-CONDITION-THEN-PAIR-ADMISSIBILITY-FORENSIC-2026-09-15-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_CONDITION_THEN_PAIR_ADMISSIBILITY_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "85c39099ac2c6f320b7ad3af34e12a4d2e862399"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.11.json")
PAIR = Path("research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py")
PAIR_BLOB = "0853ebb9a3e273fdaeca172dbe2502cc7214cf61"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "parent_exists": (r / PARENT).exists(),
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
    out: dict[int, list[int]] = {}
    for i in range(n):
        out.setdefault(find(i), []).append(i)
    return sorted((sorted(c) for c in out.values()), key=lambda x: (x[0], len(x), x))


def restrict_one(f: dict, variable: int, value: int) -> dict | None:
    scope = [int(v) for v in f["scope"]]
    rows = [tuple(int(x) for x in r) for r in f["rows"]]
    if variable not in scope:
        return {**f, "scope": scope, "rows": rows}
    pos = scope.index(variable)
    keep = [i for i in range(len(scope)) if i != pos]
    kept = sorted({tuple(r[i] for i in keep) for r in rows if r[pos] == value})
    if not kept:
        return None
    return {**f, "scope": [scope[i] for i in keep], "rows": kept}


def restrict_pair(f: dict, pair: tuple[int, int], values: tuple[int, int]) -> dict | None:
    scope = [int(v) for v in f["scope"]]
    rows = [tuple(int(x) for x in r) for r in f["rows"]]
    wanted = dict(zip(pair, values))
    positions = {v: scope.index(v) for v in pair if v in scope}
    keep = [i for i, v in enumerate(scope) if v not in wanted]
    kept = []
    for r in rows:
        if all(r[p] == wanted[v] for v, p in positions.items()):
            kept.append(tuple(r[i] for i in keep))
    kept = sorted(set(kept))
    if not kept:
        return None
    return {**f, "scope": [scope[i] for i in keep], "rows": kept}


def pair_disconnects(fs: list[dict], core: list[int], pair: tuple[int, int]) -> bool:
    before = [rscope(f, core) for f in fs]
    after = [s - set(pair) for s in before]
    return len(components(after)) > len(components(before))


def pair_branch_structure(fs: list[dict], core: list[int], pair: tuple[int, int], values: tuple[int, int]) -> dict:
    restricted = []
    for f in fs:
        z = restrict_pair(f, pair, values)
        if z is None:
            return {"values": list(values), "status": "EXACT_EMPTY_UNSAT", "component_sizes": []}
        restricted.append(z)
    cs = components([rscope(f, core) for f in restricted])
    sizes = [len(c) for c in cs]
    return {
        "values": list(values),
        "status": "STRUCTURAL_LE2" if all(x <= 2 for x in sizes) else "STRUCTURAL_GT2",
        "component_sizes": sizes,
    }


def scan_pairs(fs: list[dict], core: list[int]) -> dict:
    variables = sorted(set().union(*(rscope(f, core) for f in fs)) if fs else set())
    pair_cuts = []
    admissible = []
    for pair in itertools.combinations(variables, 2):
        if not pair_disconnects(fs, core, pair):
            continue
        branches = [pair_branch_structure(fs, core, pair, vals) for vals in ((0,0),(0,1),(1,0),(1,1))]
        rec = {
            "pair": list(pair),
            "branch_statuses": [b["status"] for b in branches],
            "branch_component_sizes": [b["component_sizes"] for b in branches],
        }
        pair_cuts.append(rec)
        if all(b["status"] in {"EXACT_EMPTY_UNSAT", "STRUCTURAL_LE2"} for b in branches):
            admissible.append(rec)
    return {
        "variables": variables,
        "pair_cut_count": len(pair_cuts),
        "pair_cuts": pair_cuts,
        "admissible_pair_count": len(admissible),
        "admissible_pairs": admissible,
        "lexicographic_first_admissible_pair": admissible[0]["pair"] if admissible else None,
    }


def run() -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard}

    raw = pair_v310.no_pair_k4_control()
    parent = pair_v310.explain(raw)
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"artifact_id": ARTIFACT_ID, "status": "FAIL_PARENT_PREP", "parent": parent.get("status"), "prep": prep.get("status")}

    target = next(c for c in prep["residual_components"] if len(c) > 2)
    fs0 = [prep["conditioned"][i] for i in target]
    variables = sorted(set().union(*(rscope(f, prep["core"]) for f in fs0)))
    records = []
    for variable in variables:
        for value in (0, 1):
            fs = []
            empty = False
            for f in fs0:
                z = restrict_one(f, variable, value)
                if z is None:
                    empty = True
                    break
                fs.append(z)
            if empty:
                records.append({"variable": variable, "value": value, "single_exact_empty_unsat": True})
                continue
            scan = scan_pairs(fs, prep["core"])
            records.append({
                "variable": variable,
                "value": value,
                "single_exact_empty_unsat": False,
                "post_single_component_sizes": [len(c) for c in components([rscope(f, prep["core"]) for f in fs])],
                "pair_scan": scan,
            })

    all_twelve = len(records) == 12
    all_nonempty = all(not r.get("single_exact_empty_unsat", False) for r in records)
    all_have_pair_cut = all(r.get("pair_scan", {}).get("pair_cut_count", 0) > 0 for r in records if not r.get("single_exact_empty_unsat", False))
    summary = {
        "single_condition_count": len(records),
        "all_single_conditions_nonempty": all_nonempty,
        "all_single_conditions_have_raw_pair_cut": all_have_pair_cut,
        "conditions_with_admissible_pair": [
            {"variable": r["variable"], "value": r["value"], "first_pair": r["pair_scan"]["lexicographic_first_admissible_pair"]}
            for r in records if not r.get("single_exact_empty_unsat", False) and r["pair_scan"]["admissible_pair_count"] > 0
        ],
        "conditions_without_admissible_pair": [
            [r["variable"], r["value"]]
            for r in records if not r.get("single_exact_empty_unsat", False) and r["pair_scan"]["admissible_pair_count"] == 0
        ],
    }
    ok = (
        parent.get("status") == "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR"
        and all_twelve and all_nonempty and all_have_pair_cut
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_CONDITION_THEN_PAIR_ADMISSIBILITY_FORENSIC" if ok else "FAIL_DIAGNOSTIC",
        "source_guard": guard,
        "parent_terminal": parent.get("status"),
        "records": records,
        "summary": summary,
        "resource_receipt": {
            "single_condition_count": len(records),
            "pair_carrier_executions": 0,
            "solver_executions": 0,
            "separator_sets_size_ge_3_executed_for_sat": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raised": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
