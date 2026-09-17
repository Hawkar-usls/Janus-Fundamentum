from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF20_02_04_05_COMMON_INVARIANT_DIFFERENTIAL_PROFILING_PREREGISTRATION_2026-09-17_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF20_02_04_05_COMMON_INVARIANT_DIFFERENTIAL_PROFILING_REVIEW_2026-09-17_v1.0.json"
REDUCTION = ROOT / "research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json"
PROJECTION = ROOT / "research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
EXPECTED_BLOBS = {
    PREREG: "253da0ce5aa987dcb4bc4bfd84165166315d8348",
    REVIEW: "5b4eaa77a0bc2cd442f160f4eaaa40c0623c9f2e",
    REDUCTION: "d91cb675e3d06fed92f97d96d6b3a0733f8be5df",
    PROJECTION: "2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
}
SOURCES = {
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}
ORDER = ("UF20_02", "UF20_03", "UF20_04", "UF20_05")
BLOCKERS = ("UF20_02", "UF20_04", "UF20_05")
CONTROL = "UF20_03"
ELIGIBLE = (
    "ARTICULATION_AND_BICONNECTED_BLOCK_COUNTS",
    "CONSTRAINT_ARITY_MULTISET",
    "CONSTRAINT_COUNT",
    "EXACT_LOCAL_RELATION_TABLE_SIGNATURES",
    "INCIDENCE_CONNECTEDNESS",
    "INCIDENCE_CYCLE_RANK",
    "PAIRWISE_VARIABLE_COOCCURRENCE_COUNTS",
    "VARIABLE_COUNT",
    "VARIABLE_DEGREE_MULTISET",
)


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def csha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def graph(raw):
    adj = defaultdict(set)
    for v in raw["variables"]:
        adj[("v", int(v))]
    for c in raw["constraints"]:
        cn = ("c", str(c["id"]))
        adj[cn]
        for v in sorted({int(x) for x in c["scope"]}):
            vn = ("v", v)
            adj[vn].add(cn)
            adj[cn].add(vn)
    return adj


def nkey(x):
    return (x[0], str(x[1]))


def components(adj):
    seen = set()
    out = 0
    for s in sorted(adj, key=nkey):
        if s in seen:
            continue
        out += 1
        todo = [s]
        seen.add(s)
        while todo:
            u = todo.pop()
            for v in sorted(adj[u], key=nkey):
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
    return out


def tarjan_counts(adj):
    disc, low, parent = {}, {}, {}
    arts, edges = set(), []
    tick = 0
    block_count = 0

    def visit(u):
        nonlocal tick, block_count
        tick += 1
        disc[u] = low[u] = tick
        children = 0
        for v in sorted(adj[u], key=nkey):
            if v not in disc:
                parent[v] = u
                children += 1
                edges.append((u, v))
                visit(v)
                low[u] = min(low[u], low[v])
                root = u not in parent
                if (root and children > 1) or ((not root) and low[v] >= disc[u]):
                    arts.add(u)
                if low[v] >= disc[u]:
                    block_count += 1
                    while edges:
                        e = edges.pop()
                        if e == (u, v):
                            break
            elif parent.get(u) != v and disc[v] < disc[u]:
                low[u] = min(low[u], disc[v])
                edges.append((u, v))

    for s in sorted(adj, key=nkey):
        if s not in disc:
            visit(s)
            if edges:
                block_count += 1
                edges.clear()
    return [len(arts), block_count]


def sig(c):
    a = len({int(v) for v in c["scope"]})
    rows = sorted("".join(str(int(b)) for b in row) for row in c["allowed"])
    return f"arity={a}|allowed={'/'.join(rows)}"


def compute(raw):
    variables = sorted({int(v) for v in raw["variables"]})
    deg = {v: 0 for v in variables}
    pairs = {(a, b): 0 for a, b in itertools.combinations(variables, 2)}
    arities = []
    e = 0
    for c in raw["constraints"]:
        scope = sorted({int(v) for v in c["scope"]})
        arities.append(len(scope))
        e += len(scope)
        for v in scope:
            deg[v] += 1
        for p in itertools.combinations(scope, 2):
            pairs[p] += 1
    adj = graph(raw)
    cc = components(adj)
    return {
        "VARIABLE_COUNT": len(variables),
        "CONSTRAINT_COUNT": len(raw["constraints"]),
        "INCIDENCE_CONNECTEDNESS": cc == 1,
        "VARIABLE_DEGREE_MULTISET": sorted(deg.values()),
        "CONSTRAINT_ARITY_MULTISET": sorted(arities),
        "PAIRWISE_VARIABLE_COOCCURRENCE_COUNTS": sorted(pairs.values()),
        "INCIDENCE_CYCLE_RANK": e - len(adj) + cc,
        "ARTICULATION_AND_BICONNECTED_BLOCK_COUNTS": tarjan_counts(adj),
        "EXACT_LOCAL_RELATION_TABLE_SIGNATURES": sorted(sig(c) for c in raw["constraints"]),
        "AUTOMORPHISM_ORBIT_PARTITION_IF_COMPUTED_EXACTLY": "NOT_COMPUTED_NO_PREEXISTING_BOUNDED_EXACT_IMPLEMENTATION_SELECTED",
        "FROZEN_ROUTE_APPLICABILITY_BITS_FOR_EXISTING_ROUTES_ONLY": "CALIBRATION_EXCLUDED_FROM_CANDIDATE_SELECTION",
    }


def reconstruct():
    reduction = json.loads(REDUCTION.read_text())
    receipts = {r["source"]: r for r in reduction["source_receipts"]}
    out, guards = {}, {}
    for name in ORDER:
        path, source_blob = SOURCES[name]
        original, _ = projection_identity.normalize_projection(name, projection_identity.parse(path))
        r = receipts[name]
        rm_c = set(r["removed_constraint_ids"])
        rm_v = {int(v) for v in r["removed_leaves"]}
        reduced = {
            "variables": [int(v) for v in original["variables"] if int(v) not in rm_v],
            "constraints": [c for c in original["constraints"] if c["id"] not in rm_c],
        }
        checks = {
            "source_blob_ok": blob(path) == source_blob,
            "original_sha_ok": csha(original) == r["original_projected_raw"]["sha256"],
            "reduced_sha_ok": csha(reduced) == r["reduced_raw"]["sha256"],
            "reduced_variables_ok": len(reduced["variables"]) == r["reduced_raw"]["variables"],
            "reduced_constraints_ok": len(reduced["constraints"]) == r["reduced_raw"]["constraints"],
        }
        checks["all_ok"] = all(checks.values())
        if not checks["all_ok"]:
            raise RuntimeError(f"independent identity guard failure {name}: {checks}")
        guards[name] = checks
        out[name] = reduced
    return out, guards


def main(candidate_path: Path):
    candidate = json.loads(candidate_path.read_text())
    auth = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED_BLOBS.items()}
    raws, guards = reconstruct()
    rows = {name: compute(raws[name]) for name in ORDER}
    chosen = []
    for f in ELIGIBLE:
        vals = [rows[s][f] for s in BLOCKERS]
        if vals[0] == vals[1] == vals[2] and vals[0] != rows[CONTROL][f]:
            chosen.append(f)
    chosen.sort()
    expected_verdict = "COMMON_PRIMITIVE_INVARIANT_CANDIDATE_SET_FOUND__BLIND_FALSIFIER_REQUIRED" if chosen else "NO_COMMON_INVARIANT_FOUND_ON_FROZEN_PRIMITIVE_FEATURE_BASIS"
    checks = {
        "authority_bindings": all(auth.values()),
        "identity_guards": all(g["all_ok"] for g in guards.values()),
        "feature_rows_exact": candidate.get("feature_rows") == rows,
        "candidate_set_exact": candidate.get("candidate_invariant_set") == chosen,
        "verdict_exact": candidate.get("verdict") == expected_verdict,
        "historical_controls_unread": candidate.get("blindness_receipt", {}).get("historical_control_feature_values_read") == 0,
        "fresh_holdouts_unread": candidate.get("blindness_receipt", {}).get("fresh_holdout_values_read") == 0,
        "no_feature_combinations": all(candidate.get("blindness_receipt", {}).get(k) == 0 for k in ("feature_conjunctions_tested", "feature_disjunctions_tested", "fitted_thresholds_tested", "weighted_combinations_tested")),
        "no_new_mechanisms": all(candidate.get("resource_receipt", {}).get(k) == 0 for k in ("solver_invocations", "new_solver_rules", "new_action_rules", "new_carrier_mechanisms", "new_reduction_mechanisms", "synthetic_blockers_generated")),
        "firewall_p_vs_np": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "firewall_general_sat": candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
    }
    return {
        "artifact_id": "JANUS-TRUMP-UF20-02-04-05-COMMON-INVARIANT-DIFFERENTIAL-PROFILING-INDEPENDENT-CHECK-2026-09-17-v1.0",
        "verdict": "PASS_INDEPENDENT_DIFFERENTIAL_PROFILE_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_DIFFERENTIAL_PROFILE_VERIFICATION",
        "checks": checks,
        "authority_bindings": auth,
        "identity_guards": guards,
        "independent_feature_rows": rows,
        "independent_candidate_invariant_set": chosen,
        "expected_candidate_verdict": expected_verdict,
        "candidate_imported": False,
        "historical_control_feature_values_read": 0,
        "scientific_firewall": {"P_VS_NP": "OPEN", "GENERAL_SAT_IN_P": "NOT_PROVED"},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()
    result = main(Path(args.candidate))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    if not result["verdict"].startswith("PASS_"):
        raise SystemExit(1)
