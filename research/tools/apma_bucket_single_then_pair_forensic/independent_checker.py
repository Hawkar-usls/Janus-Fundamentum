from __future__ import annotations

import hashlib
import itertools
import json
from collections import deque
from pathlib import Path

from research.tools.apma_bucket_single_then_pair_forensic import single_then_pair_forensic as cand
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-CONDITION-THEN-PAIR-ADMISSIBILITY-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_CONDITION_THEN_PAIR_ADMISSIBILITY_FORENSIC"
CAND = Path("research/tools/apma_bucket_single_then_pair_forensic/single_then_pair_forensic.py")
CAND_BLOB = "72e48e12afb67a7df12af872748991ddd81a8a22"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def rscope(f: dict, core: list[int]) -> set[int]:
    cc = set(int(v) for v in core)
    return {int(v) for v in f["scope"] if int(v) not in cc}


def bfs_components(scopes: list[set[int]]) -> list[list[int]]:
    n = len(scopes)
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if scopes[i] & scopes[j]:
                adj[i].append(j)
                adj[j].append(i)
    seen = set()
    out = []
    for s in range(n):
        if s in seen:
            continue
        seen.add(s)
        q = deque([s])
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        out.append(sorted(comp))
    return sorted(out, key=lambda x: (x[0], len(x), x))


def restrict_assignment(f: dict, assignment: dict[int, int]) -> dict | None:
    scope = [int(v) for v in f["scope"]]
    rows = [tuple(int(x) for x in r) for r in f["rows"]]
    indexed = [(i, v) for i, v in enumerate(scope) if v in assignment]
    keep = [i for i, v in enumerate(scope) if v not in assignment]
    survivors = set()
    for row in rows:
        if all(row[i] == assignment[v] for i, v in indexed):
            survivors.add(tuple(row[i] for i in keep))
    if not survivors:
        return None
    return {**f, "scope": [scope[i] for i in keep], "rows": sorted(survivors)}


def disconnects(fs: list[dict], core: list[int], pair: tuple[int, int]) -> bool:
    scopes = [rscope(f, core) for f in fs]
    return len(bfs_components([s - set(pair) for s in scopes])) > len(bfs_components(scopes))


def branch(fs: list[dict], core: list[int], pair: tuple[int, int], vals: tuple[int, int]) -> tuple[str, tuple[int, ...]]:
    assignment = {pair[0]: vals[0], pair[1]: vals[1]}
    rf = []
    for f in fs:
        z = restrict_assignment(f, assignment)
        if z is None:
            return "EXACT_EMPTY_UNSAT", ()
        rf.append(z)
    sizes = tuple(len(c) for c in bfs_components([rscope(f, core) for f in rf]))
    return ("STRUCTURAL_LE2" if all(x <= 2 for x in sizes) else "STRUCTURAL_GT2"), sizes


def pair_scan(fs: list[dict], core: list[int]) -> dict:
    variables = sorted(set().union(*(rscope(f, core) for f in fs)) if fs else set())
    cuts = []
    admissible = []
    for pair in itertools.combinations(variables, 2):
        if not disconnects(fs, core, pair):
            continue
        br = [branch(fs, core, pair, vals) for vals in ((0,0),(0,1),(1,0),(1,1))]
        rec = {
            "pair": list(pair),
            "branch_statuses": [x[0] for x in br],
            "branch_component_sizes": [list(x[1]) for x in br],
        }
        cuts.append(rec)
        if all(x[0] in {"EXACT_EMPTY_UNSAT", "STRUCTURAL_LE2"} for x in br):
            admissible.append(rec)
    return {
        "pair_cut_count": len(cuts),
        "pair_cuts": cuts,
        "admissible_pair_count": len(admissible),
        "admissible_pairs": admissible,
        "lexicographic_first_admissible_pair": admissible[0]["pair"] if admissible else None,
    }


def normalize_scan(scan: dict) -> tuple:
    return (
        scan["pair_cut_count"],
        tuple((tuple(x["pair"]), tuple(x["branch_statuses"]), tuple(tuple(z) for z in x["branch_component_sizes"])) for x in scan["pair_cuts"]),
        scan["admissible_pair_count"],
        tuple((tuple(x["pair"]), tuple(x["branch_statuses"]), tuple(tuple(z) for z in x["branch_component_sizes"])) for x in scan["admissible_pairs"]),
        None if scan["lexicographic_first_admissible_pair"] is None else tuple(scan["lexicographic_first_admissible_pair"]),
    )


def run() -> dict:
    candidate = cand.run()
    raw = pair_v310.no_pair_k4_control()
    parent = pair_v310.explain(raw)
    prep = v38._prepare(raw)
    checks = {
        "G1_candidate_blob": blob(root() / CAND) == CAND_BLOB,
        "G1_candidate_guard": candidate.get("source_guard", {}).get("ok") is True,
        "G2_candidate_verdict": candidate.get("status") == VERDICT,
        "G2_parent_open": parent.get("status") == "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR",
    }
    if prep.get("status") != "READY":
        return {"artifact_id": ARTIFACT_ID, "verdict": "FAIL_INDEPENDENT_PREP", "checks": checks}

    target = next(c for c in prep["residual_components"] if len(c) > 2)
    fs0 = [prep["conditioned"][i] for i in target]
    variables = sorted(set().union(*(rscope(f, prep["core"]) for f in fs0)))
    independent = []
    for variable in variables:
        for value in (0, 1):
            fs = []
            empty = False
            for f in fs0:
                z = restrict_assignment(f, {variable: value})
                if z is None:
                    empty = True
                    break
                fs.append(z)
            if empty:
                independent.append({"variable": variable, "value": value, "single_exact_empty_unsat": True})
                continue
            independent.append({
                "variable": variable,
                "value": value,
                "single_exact_empty_unsat": False,
                "post_single_component_sizes": [len(c) for c in bfs_components([rscope(f, prep["core"]) for f in fs])],
                "pair_scan": pair_scan(fs, prep["core"]),
            })

    cand_records = {(r["variable"], r["value"]): r for r in candidate["records"]}
    ind_records = {(r["variable"], r["value"]): r for r in independent}
    checks.update({
        "G3_twelve_conditions_candidate": len(cand_records) == 12,
        "G3_twelve_conditions_independent": len(ind_records) == 12,
        "G4_condition_keys_match": sorted(cand_records) == sorted(ind_records),
        "G5_all_single_nonempty_match": all(cand_records[k].get("single_exact_empty_unsat") == ind_records[k].get("single_exact_empty_unsat") for k in cand_records),
        "G6_component_sizes_match": all(cand_records[k].get("post_single_component_sizes") == ind_records[k].get("post_single_component_sizes") for k in cand_records),
        "G7_pair_scans_match": all(normalize_scan(cand_records[k]["pair_scan"]) == normalize_scan(ind_records[k]["pair_scan"]) for k in cand_records if not cand_records[k].get("single_exact_empty_unsat", False)),
        "G8_candidate_zero_pair_carrier_exec": candidate["resource_receipt"]["pair_carrier_executions"] == 0,
        "G8_candidate_zero_solver": candidate["resource_receipt"]["solver_executions"] == 0,
        "G8_candidate_zero_3plus_join": candidate["resource_receipt"]["three_plus_join_chains_materialized"] == 0,
        "G8_candidate_zero_global_product": candidate["resource_receipt"]["global_residual_cartesian_products_materialized"] == 0,
        "FW_p_vs_np": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "FW_general_sat": candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
    })

    def compact(records: dict) -> list:
        out = []
        for k in sorted(records):
            r = records[k]
            if r.get("single_exact_empty_unsat"):
                out.append([k[0], k[1], "EMPTY"])
            else:
                s = r["pair_scan"]
                out.append([k[0], k[1], s["pair_cut_count"], s["admissible_pair_count"], s["lexicographic_first_admissible_pair"]])
        return out

    verdict = VERDICT if all(checks.values()) else "FAIL_INDEPENDENT_MISMATCH"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__DIAGNOSTIC_ONLY",
        "verdict": verdict,
        "checks": checks,
        "candidate_compact": compact(cand_records),
        "independent_compact": compact(ind_records),
        "conditions_with_admissible_pair": candidate["summary"]["conditions_with_admissible_pair"],
        "conditions_without_admissible_pair": candidate["summary"]["conditions_without_admissible_pair"],
        "independent_methods": {
            "componentization": "BFS",
            "single_restriction": "INDEPENDENT_ASSIGNMENT_FILTER_PROJECT",
            "pair_scan": "INDEPENDENT_UNORDERED_PAIR_SCAN",
            "pair_restriction": "INDEPENDENT_TWO_VARIABLE_ASSIGNMENT_FILTER_PROJECT",
            "candidate_pair_helpers_used": False,
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
