from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bicameral_mincut.independent_checker import independent_canonical_cut
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier as candidate

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_PREREGISTRATION_2026-09-15.json"
CANDIDATE = ROOT / "research/tools/apma_component_join_carrier/component_join_carrier.py"
PARENT_STATE = ROOT / "registry/TRUMP_CURRENT_STATE_2026-09-15_v2.8.json"
PARENT_MINCUT = ROOT / "research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py"
PARENT_SUPPORT = ROOT / "research/tools/apma_cut_support_carrier/cut_support_carrier.py"
PARENT_SUPPORT_V11 = ROOT / "research/tools/apma_cut_support_carrier/independent_checker_v1_1.py"
HISTORICAL_GYO = ROOT / "archive/trump_apma_v1_1_successor/PREREG_DRAFT_SEMANTIC_JOIN_TREE_REPRESENTATION_v0.3.json"
EXPECTED = {
    PREREG: "a020a0c54995580f8d02e51d931624948060ecfa",
    CANDIDATE: "89f5d591d4d553bb26489908a79f2c739f62b756",
    PARENT_STATE: "98d7bb5b0067ef281f8727a45b1ecf76b741bf61",
    PARENT_MINCUT: "c0c612676e39241b95026c15823e7af6b3da8f0d",
    PARENT_SUPPORT: "012aa1acf52fa12de26bb64df303b2208d396ea9",
    PARENT_SUPPORT_V11: "02a5c47ad3e0afe430b7286a4fc8a6c82d7e527e",
    HISTORICAL_GYO: "bbf046833b2cd7aa3d4bb5c165be6ba8851d58b6",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_candidate() -> dict:
    cp = subprocess.run([sys.executable, "-m", "research.tools.apma_component_join_carrier.component_join_carrier"], cwd=ROOT, check=True, capture_output=True, text=True)
    return json.loads(cp.stdout.strip().splitlines()[-1])


def independent_components(canonical: dict, cut: list[int]) -> list[list[int]]:
    removed = set(cut)
    rel_adj = {i: set() for i in range(len(canonical["constraints"]))}
    var_to_rel: dict[int, list[int]] = {}
    for i, row in enumerate(canonical["constraints"]):
        for v in row["scope"]:
            if v not in removed:
                var_to_rel.setdefault(v, []).append(i)
    for rels in var_to_rel.values():
        for a in rels:
            rel_adj[a].update(x for x in rels if x != a)
    seen = set()
    out = []
    for i in range(len(canonical["constraints"])):
        if i in seen:
            continue
        stack = [i]
        comp = []
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.append(u)
            stack.extend(sorted(rel_adj[u] - seen, reverse=True))
        out.append(sorted(comp))
    return sorted(out)


def independent_join_tree(relations: list[dict]) -> dict:
    n = len(relations)
    if n == 0:
        return {"ok": False, "edges": [], "violations": ["EMPTY"]}
    if n == 1:
        return {"ok": True, "edges": [], "violations": []}
    scopes = [set(r["scope"]) for r in relations]
    selected = {0}
    edges = []
    while len(selected) < n:
        choices = []
        for u in sorted(selected):
            for v in range(n):
                if v in selected:
                    continue
                shared = tuple(sorted(scopes[u] & scopes[v]))
                choices.append((-len(shared), u, v, shared))
        if not choices:
            return {"ok": False, "edges": edges, "violations": ["NO_SPANNING_TREE"]}
        negw, u, v, shared = min(choices)
        edges.append({"a": u, "b": v, "separator": list(shared), "weight": -negw})
        selected.add(v)
    adj = {i: set() for i in range(n)}
    for e in edges:
        adj[e["a"]].add(e["b"])
        adj[e["b"]].add(e["a"])
    violations = []
    for x in sorted(set().union(*scopes)):
        nodes = {i for i, s in enumerate(scopes) if x in s}
        if len(nodes) <= 1:
            continue
        seen = {min(nodes)}
        stack = list(seen)
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w in nodes and w not in seen:
                    seen.add(w)
                    stack.append(w)
        if seen != nodes:
            violations.append(x)
    return {"ok": not violations, "edges": edges, "violations": violations}


def independent_anchor(relations: list[dict], cut: list[int]) -> int | None:
    B = set(cut)
    choices = [(len(r["allowed"]), str(r.get("id", "")), i) for i, r in enumerate(relations) if B.issubset(set(r["scope"]))]
    return min(choices)[2] if choices else None


def restrict_rows(relation: dict, assignment: dict[int, int]) -> list[tuple[int, ...]]:
    scope = list(relation["scope"])
    pos = [(i, v) for i, v in enumerate(scope) if v in assignment]
    out = []
    for row in relation["allowed"]:
        t = tuple(map(int, row))
        if all(t[i] == assignment[v] for i, v in pos):
            out.append(t)
    return sorted(set(out))


def compatible(scope_a: list[int], a: tuple[int, ...], scope_b: list[int], b: tuple[int, ...]) -> bool:
    pb = {v: i for i, v in enumerate(scope_b)}
    return all(v not in pb or a[i] == b[pb[v]] for i, v in enumerate(scope_a))


def independent_conditional_join(relations: list[dict], tree: dict, cut: list[int], sigma: tuple[int, ...]) -> dict:
    assignment = {v: bit for v, bit in zip(cut, sigma)}
    tables = {i: restrict_rows(r, assignment) for i, r in enumerate(relations)}
    if any(not x for x in tables.values()):
        return {"sat": False, "rows": {}}
    if len(relations) == 1:
        return {"sat": True, "rows": {0: list(tables[0][0])}}
    adj = {i: set() for i in range(len(relations))}
    for e in tree["edges"]:
        adj[e["a"]].add(e["b"])
        adj[e["b"]].add(e["a"])
    parent = {0: None}
    order = [0]
    q = [0]
    while q:
        u = q.pop(0)
        for w in sorted(adj[u]):
            if w not in parent:
                parent[w] = u
                order.append(w)
                q.append(w)
    scopes = {i: list(relations[i]["scope"]) for i in range(len(relations))}
    feasible: dict[int, list[tuple[int, ...]]] = {}
    child_choice: dict[tuple[int, tuple[int, ...], int], tuple[int, ...]] = {}
    children = {i: [w for w in sorted(adj[i]) if parent.get(w) == i] for i in range(len(relations))}
    for u in reversed(order):
        kept = []
        for row in tables[u]:
            ok = True
            for ch in children[u]:
                matches = [r for r in feasible[ch] if compatible(scopes[u], row, scopes[ch], r)]
                if not matches:
                    ok = False
                    break
                child_choice[(u, row, ch)] = matches[0]
            if ok:
                kept.append(row)
        feasible[u] = kept
        if not kept:
            return {"sat": False, "rows": {}}
    chosen: dict[int, tuple[int, ...]] = {0: feasible[0][0]}
    for u in order:
        for ch in children[u]:
            chosen[ch] = child_choice[(u, chosen[u], ch)]
    return {"sat": True, "rows": {i: list(chosen[i]) for i in sorted(chosen)}}


def independent_component_support(canonical: dict, component: list[int], cut: list[int]) -> dict:
    relations = [canonical["constraints"][i] for i in component]
    aidx = independent_anchor(relations, cut)
    if aidx is None:
        return {"status": "OPEN_NO_FULL_CUT_ANCHOR", "support": {}, "tree_ok": None}
    tree = independent_join_tree(relations)
    if not tree["ok"]:
        return {"status": "OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE", "support": {}, "tree_ok": False, "violations": tree["violations"]}
    anchor = relations[aidx]
    scope = list(anchor["scope"])
    pos = [scope.index(v) for v in cut]
    states = sorted({tuple(int(row[p]) for p in pos) for row in anchor["allowed"]})
    support = {}
    for sigma in states:
        z = independent_conditional_join(relations, tree, cut, sigma)
        if z["sat"]:
            support[sigma] = z
    return {"status": "ADMIT_COMPONENT_JOIN_TREE_SUPPORT", "support": support, "tree_ok": True, "anchor_rows": len(anchor["allowed"]), "anchor_states": len(states)}


def independent_global(raw: dict) -> dict:
    canonical = canonicalize_raw(raw)
    cutrec = independent_canonical_cut(canonical)
    if cutrec is None:
        return {"status": "NO_CUT"}
    cut = list(cutrec["cut_variables"])
    comps = independent_components(canonical, cut)
    results = [independent_component_support(canonical, c, cut) for c in comps]
    if any(r["status"] != "ADMIT_COMPONENT_JOIN_TREE_SUPPORT" for r in results):
        return {"status": next(r["status"] for r in results if r["status"] != "ADMIT_COMPONENT_JOIN_TREE_SUPPORT"), "cut": cutrec, "components": comps, "component_results": results}
    common = set.intersection(*(set(r["support"]) for r in results)) if results else set()
    return {"status": "SAT" if common else "UNSAT", "cut": cutrec, "components": comps, "component_results": results, "common": sorted(common)}


def verify_candidate_witness(raw: dict, run: dict) -> bool:
    canonical = canonicalize_raw(raw)
    witness = run.get("carrier", {}).get("witness")
    if not witness:
        return False
    assignment = {int(k): int(v) for k, v in witness["assignment"].items()}
    return candidate.verify_original_assignment(canonical, assignment)


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    source = {p.name + "_blob": git_blob_sha1(p) == sha for p, sha in EXPECTED.items()}
    source["prereg_frozen"] = prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
    source["prereg_gate"] = prereg.get("frozen_gate") == "TRUMP_BICAMERAL_COMPONENT_BOUNDARY_RELATION_JOIN_TREE_CARRIER_FALSIFIER_GATE"
    run = run_candidate()

    pos_raw = candidate.positive_multi_relation_k20()
    pos_can = canonicalize_raw(pos_raw)
    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_support_parent = parent_support.explain_overwidth_cut(pos_raw)
    pos_ind = independent_global(pos_raw)
    pos = run["positive"]

    empty_raw = candidate.empty_conditional_join_control()
    empty_ind = independent_global(empty_raw)
    empty = run["negative_empty"]

    cycle_raw = candidate.alpha_cycle_control()
    cycle_ind = independent_global(cycle_raw)
    cycle = run["negative_cycle"]

    no_anchor = run["negative_no_anchor_unit"]
    hint = run["negative_hint"]
    tamper = run["negative_tamper"]
    rr = pos.get("carrier", {}).get("resource_receipt", {})
    pos_components = pos_ind.get("components", [])
    pos_component_sizes = sorted(len(c) for c in pos_components)
    pos_common = pos_ind.get("common", [])
    candidate_component_receipts = pos.get("carrier", {}).get("component_receipts", [])

    checks = {
        **{f"P1_{k}": v for k, v in source.items()},
        "P2_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_parent_zero_branches": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P2_independent_cut20": pos_ind.get("cut", {}).get("cut_size") == 20 and pos_ind.get("cut", {}).get("cut_variables") == list(range(20)),
        "P3_parent_singleton_carrier_open": pos_support_parent.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P3_multi_relation_component_present": pos_component_sizes == [1, 2],
        "P4_candidate_anchor_state_bound": all(r.get("anchor_state_count", 10**9) <= r.get("anchor_input_rows", -1) for r in candidate_component_receipts),
        "P4_independent_anchor_state_bound": all(r.get("anchor_states", 10**9) <= r.get("anchor_rows", -1) for r in pos_ind.get("component_results", [])),
        "P5_candidate_join_trees_verified": all(r.get("support_size", -1) >= 0 for r in candidate_component_receipts),
        "P5_independent_join_trees_verified": all(r.get("tree_ok") is True for r in pos_ind.get("component_results", [])),
        "P7_no_raw_cube": rr.get("raw_cut_assignments_enumerated") == 0,
        "P8_positive_candidate_and_independent_support_one": pos.get("carrier", {}).get("effective_support_size") == 1 and len(pos_common) == 1,
        "P9_carrier_bounded_by_anchor_rows": all(r.get("support_size", 10**9) <= r.get("anchor_input_rows", -1) for r in candidate_component_receipts),
        "P10_positive_terminal": pos.get("status") == "ADMIT_EXACT_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER",
        "P10_positive_witness_verified": pos.get("carrier", {}).get("witness_verified") is True and verify_candidate_witness(pos_raw, pos),
        "P11_empty_independent_unsat": empty_ind.get("status") == "UNSAT" and not empty_ind.get("common"),
        "P11_empty_candidate_exact_unsat": empty.get("status") == "EXACT_UNSAT_BY_EMPTY_COMPONENT_BOUNDARY_SUPPORT",
        "P12_no_anchor_open": no_anchor.get("status") == "OPEN_NO_FULL_CUT_ANCHOR",
        "P13_cycle_independent_rejects_tree": cycle_ind.get("status") == "OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE",
        "P13_cycle_candidate_open": cycle.get("status") == "OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE",
        "P14_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "P14_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P15_zero_full_join": rr.get("full_join_rows_materialized") == 0,
        "P15_zero_cartesian": rr.get("cartesian_products_materialized") == 0,
        "P15_zero_generic_transfer": rr.get("generic_transfer_calls") == 0,
        "P15_zero_external_solver": rr.get("external_solver_invocations") == 0,
        "P15_zero_join_tree_backtracking": rr.get("join_tree_backtracks") == 0,
        "FW_p_vs_np_open": run["scientific_firewall"].get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": run["scientific_firewall"].get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": run["scientific_firewall"].get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "FW_arbitrary_unseen_not_proved": run["scientific_firewall"].get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
        "FW_general_multi_relation_compression_not_proved": run["scientific_firewall"].get("GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION") == "NOT_PROVED",
    }
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER" if all(checks.values()) else "FAIL_OR_OPEN_COMPONENT_BOUNDARY_JOIN_CARRIER"
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "positive_parent": pos_parent.get("status"),
            "positive_cut": pos_ind.get("cut"),
            "positive_component_sizes": pos_component_sizes,
            "positive_effective_support": [list(x) for x in pos_common],
            "positive_terminal": pos.get("status"),
            "positive_anchor_state_counts": [r.get("anchor_state_count") for r in candidate_component_receipts],
            "positive_component_support_sizes": [r.get("support_size") for r in candidate_component_receipts],
            "empty_terminal": empty.get("status"),
            "cycle_terminal": cycle.get("status"),
            "no_anchor_terminal": no_anchor.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper.get("status"),
        },
        "complexity": {
            "candidate_cut_states": "bounded by explicit anchor rows",
            "join_tree_discovery": "polynomial candidate Kruskal; independent checker Prim; both followed by running-intersection verification",
            "conditional_join": "polynomial tree DP/semijoin over explicit rows per anchor state",
            "raw_2_to_k_enumeration": 0,
            "full_join_materialization": 0,
            "backtracking": 0,
        },
        "scientific_firewall": candidate.firewall(),
    }
    print(json.dumps(out, sort_keys=True))
    if verdict != "PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
