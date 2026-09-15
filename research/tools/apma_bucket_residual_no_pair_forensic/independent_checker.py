from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, deque
from pathlib import Path

from research.tools.apma_bucket_residual_no_pair_forensic import no_pair_forensic as cand
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-NO-PAIR-SEPARATOR-STRUCTURE-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_PAIR_SEPARATOR_STRUCTURE_FORENSIC"
CAND = Path("research/tools/apma_bucket_residual_no_pair_forensic/no_pair_forensic.py")
CAND_BLOB = "cb32d5e37ad4ab424e56853421365e213ee7d163"
CAP = 3


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def rscope(f: dict, core: list[int]) -> set[int]:
    c = set(int(v) for v in core)
    return {int(v) for v in f["scope"] if int(v) not in c}


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
    for start in range(n):
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
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


def disconnected_by(scopes: list[set[int]], cut: tuple[int, ...]) -> bool:
    return len(bfs_components([s - set(cut) for s in scopes])) > len(bfs_components(scopes))


def scan_cuts(scopes: list[set[int]], cap: int = CAP) -> dict:
    vs = sorted(set().union(*scopes) if scopes else set())
    examined = {}
    by_size = {}
    minimum = None
    minimum_cuts = []
    for k in range(1, min(cap, len(vs)) + 1):
        hits = []
        count = 0
        for subset in itertools.combinations(vs, k):
            count += 1
            if disconnected_by(scopes, subset):
                hits.append(list(subset))
        examined[str(k)] = count
        by_size[str(k)] = hits
        if hits:
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


def overlap_edges(scopes: list[set[int]]) -> list[dict]:
    out = []
    for i in range(len(scopes)):
        for j in range(i + 1, len(scopes)):
            ov = sorted(scopes[i] & scopes[j])
            if ov:
                out.append({"i": i, "j": j, "overlap": ov, "overlap_cardinality": len(ov)})
    return out


def prim_tree(scopes: list[set[int]], es: list[dict]) -> list[dict]:
    if not scopes:
        return []
    edge_map = {(e["i"], e["j"]): e for e in es}
    edge_map.update({(e["j"], e["i"]): {**e, "i": e["j"], "j": e["i"]} for e in es})
    used = {0}
    out = []
    while len(used) < len(scopes):
        choices = []
        for u in sorted(used):
            for v in range(len(scopes)):
                if v in used or (u, v) not in edge_map:
                    continue
                e = edge_map[(u, v)]
                choices.append((-e["overlap_cardinality"], min(u, v), max(u, v), e))
        if not choices:
            break
        _, _, _, e = min(choices, key=lambda x: (x[0], x[1], x[2], x[3]["overlap"]))
        v = e["j"] if e["i"] in used else e["i"]
        used.add(v)
        a, b = sorted((e["i"], e["j"]))
        out.append({"i": a, "j": b, "overlap": sorted(scopes[a] & scopes[b]), "overlap_cardinality": len(scopes[a] & scopes[b])})
    return out


def ri(scopes: list[set[int]], tree: list[dict]) -> dict:
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
        q = deque([nodes[0]])
        seen = {nodes[0]}
        while q:
            u = q.popleft()
            for w in adj[u]:
                if w in allowed and w not in seen:
                    seen.add(w)
                    q.append(w)
        if seen != allowed:
            failures.append(v)
    return {"ok": not failures, "failure_variables": failures}


def hash_compat(fs: list[dict], es: list[dict]) -> list[dict]:
    out = []
    for e in es:
        a, b = fs[e["i"]], fs[e["j"]]
        ov = e["overlap"]
        posa = [list(map(int, a["scope"])).index(v) for v in ov]
        posb = [list(map(int, b["scope"])).index(v) for v in ov]
        ca = Counter(tuple(int(r[p]) for p in posa) for r in a["rows"])
        cb = Counter(tuple(int(r[p]) for p in posb) for r in b["rows"])
        count = sum(n * cb.get(sig, 0) for sig, n in ca.items())
        out.append({**e, "left_rows": len(a["rows"]), "right_rows": len(b["rows"]), "compatible_pairs": count})
    return out


def restrict_independent(f: dict, variable: int, value: int) -> dict | None:
    scope = [int(v) for v in f["scope"]]
    if variable not in scope:
        return {**f, "scope": scope, "rows": [tuple(int(x) for x in r) for r in f["rows"]]}
    pos = scope.index(variable)
    new_scope = [v for i, v in enumerate(scope) if i != pos]
    rows = set()
    for row in f["rows"]:
        rr = tuple(int(x) for x in row)
        if rr[pos] == value:
            rows.add(tuple(x for i, x in enumerate(rr) if i != pos))
    if not rows:
        return None
    return {**f, "scope": new_scope, "rows": sorted(rows)}


def condition_profiles(fs: list[dict], core: list[int]) -> list[dict]:
    vs = sorted(set().union(*(rscope(f, core) for f in fs)) if fs else set())
    out = []
    for v in vs:
        branches = []
        for bit in (0, 1):
            rf = []
            empty = False
            for f in fs:
                z = restrict_independent(f, v, bit)
                if z is None:
                    empty = True
                    break
                rf.append(z)
            if empty:
                branches.append({"value": bit, "exact_empty_unsat": True})
                continue
            scopes = [rscope(f, core) for f in rf]
            cp = scan_cuts(scopes, CAP)
            branches.append({
                "value": bit,
                "exact_empty_unsat": False,
                "component_sizes": [len(c) for c in bfs_components(scopes)],
                "cut_profile": cp,
                "pair_cut_present": cp["minimum_size_up_to_cap"] == 2,
            })
        out.append({"variable": v, "branches": branches})
    return out


def norm_compat(rows: list[dict]) -> list[tuple]:
    return sorted((r["i"], r["j"], tuple(r["overlap"]), r["left_rows"], r["right_rows"], r["compatible_pairs"]) for r in rows)


def branch_minima(rows: list[dict]) -> list[tuple]:
    out = []
    for rec in rows:
        for b in rec["branches"]:
            out.append((rec["variable"], b["value"], b.get("exact_empty_unsat", False), None if b.get("exact_empty_unsat") else b["cut_profile"]["minimum_size_up_to_cap"], False if b.get("exact_empty_unsat") else b["pair_cut_present"]))
    return sorted(out)


def run() -> dict:
    candidate = cand.run()
    raw = pair_v310.no_pair_k4_control()
    parent = pair_v310.explain(raw)
    prep = v38._prepare(raw)
    checks = {
        "G1_candidate_blob": blob(root() / CAND) == CAND_BLOB,
        "G1_candidate_source_guard": candidate.get("source_guard", {}).get("ok") is True,
        "G2_candidate_diagnostic_pass": candidate.get("status") == VERDICT,
        "G2_parent_open": parent.get("status") == "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR",
    }
    if prep.get("status") != "READY":
        return {"artifact_id": ARTIFACT_ID, "verdict": "FAIL_DIAGNOSTIC_INDEPENDENT_PREP", "checks": checks, "prep": prep.get("status")}

    target = next(c for c in prep["residual_components"] if len(c) > 2)
    fs = [prep["conditioned"][i] for i in target]
    scopes = [rscope(f, prep["core"]) for f in fs]
    es = overlap_edges(scopes)
    cp = scan_cuts(scopes, CAP)
    tree = prim_tree(scopes, es)
    rip = ri(scopes, tree)
    compat = hash_compat(fs, es)
    branches = condition_profiles(fs, prep["core"])
    prof = candidate["profile"]

    checks.update({
        "G3_scopes_match": prof["residual_scopes"] == [sorted(s) for s in scopes],
        "G3_overlap_edges_match": [(x["i"], x["j"], x["overlap"]) for x in prof["overlap_edges"]] == [(x["i"], x["j"], x["overlap"]) for x in es],
        "G4_cut_minimum_matches": prof["cut_profile"]["minimum_size_up_to_cap"] == cp["minimum_size_up_to_cap"],
        "G4_minimum_cuts_match": prof["cut_profile"]["minimum_cuts"] == cp["minimum_cuts"],
        "G5_running_intersection_boolean_matches": prof["running_intersection"]["ok"] == rip["ok"],
        "G6_pairwise_compatibility_matches": norm_compat(prof["pairwise_compatibility"]) == norm_compat(compat),
        "G7_single_condition_cut_minima_match": branch_minima(prof["single_condition_profiles"]) == branch_minima(branches),
        "G8_candidate_zero_3plus_join": prof["resource_receipt"]["three_plus_join_chains_materialized"] == 0,
        "G8_candidate_zero_global_product": prof["resource_receipt"]["global_residual_cartesian_products_materialized"] == 0,
        "G8_candidate_zero_sat_separator_assignments": prof["resource_receipt"]["sat_separator_assignments_executed"] == 0,
        "FW_p_vs_np": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "FW_general_sat": candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
    })
    verdict = VERDICT if all(checks.values()) else "FAIL_DIAGNOSTIC_INDEPENDENT_MISMATCH"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__DIAGNOSTIC_ONLY",
        "verdict": verdict,
        "checks": checks,
        "candidate_summary": {
            "cut_minimum": prof["cut_profile"]["minimum_size_up_to_cap"],
            "minimum_cuts": prof["cut_profile"]["minimum_cuts"],
            "running_intersection": prof["running_intersection"],
            "single_condition_minima": branch_minima(prof["single_condition_profiles"]),
        },
        "independent_summary": {
            "cut_minimum": cp["minimum_size_up_to_cap"],
            "minimum_cuts": cp["minimum_cuts"],
            "prim_tree": tree,
            "running_intersection": rip,
            "single_condition_minima": branch_minima(branches),
        },
        "independent_methods": {
            "componentization": "BFS",
            "cut_scan": "FIXED_CAP_SUBSET_SCAN",
            "spanning_tree": "PRIM",
            "compatibility": "HASH_SIGNATURE_COUNTS",
            "restriction": "INDEPENDENT_ROW_FILTER_AND_PROJECT",
            "candidate_cut_tree_or_compatibility_helpers_used": False,
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
