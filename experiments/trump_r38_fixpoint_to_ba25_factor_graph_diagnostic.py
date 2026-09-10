from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r38_portfolio_fixpoint_freeze_structure_intake as r38
import janus_trump_r50g25ba25 as ba25

SEED = 36001
N = 28
RATIO = 4.2
EXPECTED_R38_HASH = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
EXPECTED_INITIAL_CLV = [118, 354, 28]
EXPECTED_RESIDUAL_CLV = [45, 105, 13]
BA25_FINAL_META_COMMIT = "ea0a5ae518da97ebab0695a6c427706b452d02d2"
R37B_SEAL = "a5ddd0bc7aa637df08f9cd6e3f480c8aabd85896"
R38_SEAL = "0b941a484143aa130bad9f7bdf9ca94fbbff79cb"


def remap_formula(formula):
    orig_vars = sorted(r33.variables(formula))
    to_x = {v: f"x{i}" for i, v in enumerate(orig_vars)}
    clauses = [
        [(to_x[abs(int(lit))], 1 if int(lit) > 0 else -1) for lit in clause]
        for clause in formula
    ]
    return orig_vars, to_x, clauses


def graph_dict(vertices, edges):
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def min_fill_verified_td(vertices, edges):
    adj = graph_dict(vertices, edges)
    order = []
    bags = {}
    later = {}
    width = -1
    while adj:
        def score(v):
            nb = sorted(adj[v])
            fill = 0
            for i, a in enumerate(nb):
                for b in nb[i + 1:]:
                    if b not in adj[a]:
                        fill += 1
            return (fill, len(nb), str(v))
        v = min(adj, key=score)
        nb = sorted(adj[v])
        order.append(v)
        later[v] = tuple(nb)
        bags[v] = frozenset([v, *nb])
        width = max(width, len(nb))
        for i, a in enumerate(nb):
            for b in nb[i + 1:]:
                adj[a].add(b)
                adj[b].add(a)
        for u in nb:
            adj[u].discard(v)
        del adj[v]

    pos = {v: i for i, v in enumerate(order)}
    td_edges = []
    roots = []
    for v in order:
        ln = list(later[v])
        if ln:
            parent = min(ln, key=lambda u: pos[u])
            td_edges.append((f"t:{v}", f"t:{parent}"))
        else:
            roots.append(f"t:{v}")
    for a, b in zip(roots, roots[1:]):
        td_edges.append((a, b))
    td_bags = {f"t:{v}": bag for v, bag in bags.items()}
    ok, receipt = validate_graph_td(set(vertices), set(edges), td_bags, tuple(td_edges))
    if not ok:
        raise AssertionError(("candidate TD failed independent validation", receipt))
    if receipt["width"] != width:
        raise AssertionError(("width drift", width, receipt))
    return {
        "bags": td_bags,
        "edges": tuple(td_edges),
        "order": tuple(order),
        "width": width,
        "validation": receipt,
        "heuristic_role": "MIN_FILL_GENERATES_CANDIDATE_ORDER_ONLY",
        "scientific_role": "INDEPENDENTLY_VERIFIED_TREE_DECOMPOSITION_WIDTH_UPPER_BOUND",
        "exact_treewidth_claimed": False,
    }


def validate_graph_td(vertices, edges, bags, td_edges):
    nodes = set(bags)
    if not nodes:
        return (not vertices), {"width": -1, "tree": True, "vertex_coverage": not vertices, "edge_coverage": not edges, "running_intersection": True}
    adj = {n: set() for n in nodes}
    for a, b in td_edges:
        if a not in nodes or b not in nodes or a == b:
            return False, {"why": "bad_td_edge", "edge": [a, b]}
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    stack = [next(iter(nodes))]
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(adj[x] - seen)
    tree_ok = seen == nodes and len(td_edges) == len(nodes) - 1
    if not tree_ok:
        return False, {"why": "not_tree", "seen": len(seen), "nodes": len(nodes), "edges": len(td_edges)}
    cover = set().union(*bags.values()) if bags else set()
    if cover != vertices:
        return False, {"why": "vertex_coverage", "missing": sorted(vertices - cover), "extra": sorted(cover - vertices)}
    for a, b in edges:
        if not any(a in bag and b in bag for bag in bags.values()):
            return False, {"why": "edge_coverage", "edge": [a, b]}
    for v in vertices:
        holders = {n for n, bag in bags.items() if v in bag}
        reach = set()
        st = [next(iter(holders))]
        while st:
            x = st.pop()
            if x in reach:
                continue
            reach.add(x)
            st.extend((adj[x] & holders) - reach)
        if reach != holders:
            return False, {"why": "running_intersection", "vertex": v}
    width = max(len(b) - 1 for b in bags.values())
    return True, {
        "width": width,
        "tree": True,
        "vertex_coverage": True,
        "edge_coverage": True,
        "running_intersection": True,
        "bag_count": len(bags),
        "td_edge_count": len(td_edges),
    }


def degeneracy_lower_bound(vertices, edges):
    adj = graph_dict(vertices, edges)
    bound = 0
    order = []
    while adj:
        v = min(adj, key=lambda x: (len(adj[x]), str(x)))
        d = len(adj[v])
        bound = max(bound, d)
        order.append({"vertex": v, "degree_at_deletion": d})
        for u in list(adj[v]):
            adj[u].discard(v)
        del adj[v]
    return bound, order


def minor_min_width_lower_bound(vertices, edges):
    adj = graph_dict(vertices, edges)
    lb = 0
    contractions = []
    while adj:
        v = min(adj, key=lambda x: (len(adj[x]), str(x)))
        d = len(adj[v])
        lb = max(lb, d)
        if d == 0:
            contractions.append({"operation": "DELETE_ISOLATED", "v": v, "minimum_degree": d})
            del adj[v]
            continue
        u = min(adj[v], key=lambda x: (len(adj[x]), str(x)))
        contractions.append({"operation": "CONTRACT", "v": v, "into": u, "minimum_degree": d})
        nv = (adj[v] | adj[u]) - {v, u}
        for w in list(adj[v]):
            adj[w].discard(v)
        for w in list(adj[u]):
            adj[w].discard(u)
        del adj[v]
        adj[u] = set(nv)
        for w in nv:
            adj[w].add(u)
    return lb, contractions


def structural_certificate(formula, label):
    orig_vars, _, clauses = remap_formula(formula)
    vertices, edges = ba25.incidence_graph(len(orig_vars), clauses)
    td = min_fill_verified_td(vertices, edges)
    deg, deg_order = degeneracy_lower_bound(vertices, edges)
    mmw, contractions = minor_min_width_lower_bound(vertices, edges)
    lower = max(deg, mmw)
    upper = td["width"]
    return {
        "label": label,
        "C_L_V": list(r33.measure(formula)),
        "variable_count": len(orig_vars),
        "clause_count": len(formula),
        "incidence_vertex_count": len(vertices),
        "incidence_edge_count": len(edges),
        "verified_td_upper_bound": upper,
        "treewidth_lower_bound": lower,
        "lower_bound_components": {"degeneracy": deg, "minor_min_width": mmw},
        "treewidth_interval": [lower, upper],
        "exact_treewidth": upper if lower == upper else None,
        "exact_treewidth_certified": lower == upper,
        "candidate_order_method": "DETERMINISTIC_MIN_FILL",
        "candidate_order_is_exact_treewidth_authority": False,
        "td_validation": td["validation"],
        "elimination_order": list(td["order"]),
        "degeneracy_certificate": deg_order,
        "minor_min_width_certificate": contractions,
        "_td": td,
        "_clauses": clauses,
        "_orig_vars": orig_vars,
    }


def extend_incidence_td_to_ba25(td_info, n, clause_count):
    def map_node(q):
        if q.startswith("x"):
            return f"v:{q}"
        if q.startswith("c"):
            return f"C:{int(q[1:])}"
        raise AssertionError(q)

    bags = {name: frozenset(map_node(v) for v in bag) for name, bag in td_info["bags"].items()}
    edges = list(td_info["edges"])
    for i in range(n):
        vn = f"v:x{i}"
        holders = sorted(name for name, bag in bags.items() if vn in bag)
        if not holders:
            raise AssertionError(("missing variable holder", vn))
        leaf = f"block_leaf:{i}"
        bags[leaf] = frozenset({vn, f"B:{i+1}"})
        edges.append((holders[0], leaf))

    z_block = "z:block"
    z_clause = "z:clause"
    bags[z_block] = frozenset({"B:0", "v:z"})
    bags[z_clause] = frozenset({"v:z", f"C:{clause_count}"})
    edges.append((z_block, z_clause))
    if td_info["bags"]:
        edges.append((sorted(td_info["bags"])[0], z_block))
    return ba25.TD(bags=bags, edges=tuple(edges))


def brute_force_formula(formula):
    vs = sorted(r33.variables(formula))
    count = 0
    witness = None
    for bits in itertools.product((0, 1), repeat=len(vs)):
        a = dict(zip(vs, bits))
        ok = True
        for clause in formula:
            if not any((lit > 0 and a[abs(lit)] == 1) or (lit < 0 and a[abs(lit)] == 0) for lit in clause):
                ok = False
                break
        if ok:
            count += 1
            if witness is None:
                witness = dict(a)
    return count, witness


def direct_clause_replay(formula, witness):
    rows = []
    failures = []
    for j, clause in enumerate(formula):
        hit = None
        for lit in clause:
            val = witness[abs(lit)]
            if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                hit = int(lit)
                break
        passed = hit is not None
        rows.append({"clause_index": j, "clause": list(clause), "pass": passed, "satisfied_literal": hit})
        if not passed:
            failures.append(j)
    return rows, failures


def strip_private(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def run():
    initial = r33.canonical_formula(r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO))
    if list(r33.measure(initial)) != EXPECTED_INITIAL_CLV:
        raise AssertionError(("initial CLV drift", r33.measure(initial)))

    frozen = r38.materialize_r37b_fixpoint()
    residual = frozen["formula"]
    if frozen["hash"] != EXPECTED_R38_HASH or list(r33.measure(residual)) != EXPECTED_RESIDUAL_CLV:
        raise AssertionError(("R38 drift", frozen["hash"], r33.measure(residual)))
    if len(residual) != 45:
        raise AssertionError(("R38 clause count", len(residual)))

    before = structural_certificate(initial, "R37B_CONTROLLER_INPUT")
    after = structural_certificate(residual, "R38_SEALED_FIXPOINT")

    orig_vars = after["_orig_vars"]
    clauses = after["_clauses"]
    inst = ba25.embed_cnf(len(orig_vars), clauses)
    factor_vertices, factor_edges = ba25.factor_graph(inst)
    factor_td = extend_incidence_td_to_ba25(after["_td"], len(orig_vars), len(clauses))
    td_ok, td_receipt = ba25.validate_td(factor_vertices, factor_edges, factor_td, claimed_tau=after["verified_td_upper_bound"])
    if not td_ok:
        raise AssertionError(("BA25 factor TD validation failed", td_receipt))

    dp = ba25.run_dp(inst, factor_td, proof=False)
    wr = ba25.witness_receipt(inst, dp["witness"])
    if not wr["direct_verify"]:
        raise AssertionError("BA25 witness receipt failed")

    brute_count, brute_witness = brute_force_formula(residual)
    if brute_witness is None or brute_count <= 0:
        raise AssertionError("R38 residual unexpectedly UNSAT under exact enumeration")
    if dp["count"] != brute_count or not dp["sat"]:
        raise AssertionError(("BA25 vs brute mismatch", dp["count"], brute_count, dp["sat"]))

    ba25_to_orig = {f"x{i}": orig_vars[i] for i in range(len(orig_vars))}
    original_witness = {ba25_to_orig[x]: int(dp["witness"][x]) for x in ba25_to_orig}
    replay_rows, replay_failures = direct_clause_replay(residual, original_witness)
    if replay_failures:
        raise AssertionError(("direct original R38 replay failure", replay_failures))

    upper_drop = before["verified_td_upper_bound"] - after["verified_td_upper_bound"]
    exact_decrease = before["treewidth_lower_bound"] > after["verified_td_upper_bound"]
    exact_nonincrease = before["treewidth_lower_bound"] >= after["verified_td_upper_bound"]

    result = {
        "diagnostic": "TRUMP_R38_FIXPOINT_TO_BA25_FACTOR_GRAPH_DIAGNOSTIC",
        "date": "2026-09-10",
        "status": "PASS",
        "scientific_parent": {
            "R37B_sealed_commit": R37B_SEAL,
            "R38_sealed_commit": R38_SEAL,
            "R38_residual_sha256": EXPECTED_R38_HASH,
            "BA25_final_meta_commit": BA25_FINAL_META_COMMIT,
        },
        "R37_firewall": "POLYNOMIAL_TERMINATION != DECISION_COMPLETENESS",
        "structural_width": {
            "before_exact_reductions": strip_private(before),
            "after_exact_reductions": strip_private(after),
            "verified_td_upper_bound_change_before_minus_after": upper_drop,
            "true_treewidth_strict_decrease_certified": exact_decrease,
            "true_treewidth_nonincrease_certified_from_bounds": exact_nonincrease,
            "interpretation": "Verified decomposition widths are rigorous upper bounds. Min-fill is not exact-treewidth authority. Exact treewidth is emitted only if an independent lower bound meets the verified upper bound."
        },
        "BA25_factor_graph": {
            "semantic_embedding": "R38_CNF -> singleton-DBO arbitrary-CNF calibration embedding",
            "factor_vertex_count": len(factor_vertices),
            "factor_edge_count": len(factor_edges),
            "supplied_td_validation": td_receipt,
            "tau_used_by_BA25": dp["tau"],
            "tau_authority": "WIDTH_OF_INDEPENDENTLY_VERIFIED_SUPPLIED_TD; NOT_CLAIMED_OPTIMAL_UNLESS_BOUNDS_MEET",
            "state_bound": dp["state_bound"],
            "peak_table_states": dp["max_states"],
            "nice_node_count": dp["nice_nodes"],
        },
        "exact_semantics": {
            "SAT": dp["sat"],
            "exact_model_count": dp["count"],
            "brute_force_exact_model_count": brute_count,
            "BA25_equals_bruteforce": dp["count"] == brute_count,
            "witness": original_witness,
            "BA25_witness_receipt_direct_verify": wr["direct_verify"],
            "direct_original_R38_clause_replay_count": len(replay_rows),
            "direct_original_R38_clause_replay_failures": replay_failures,
            "direct_original_R38_clause_replay": replay_rows,
        },
        "R37B_reduction_receipt": {
            "initial_CLV": EXPECTED_INITIAL_CLV,
            "terminal_CLV": EXPECTED_RESIDUAL_CLV,
            "successful_transformations": frozen["successful_transformations"],
            "restarts": frozen["restart_count"],
            "terminal_hash": frozen["hash"],
        },
        "master_hypothesis_impact": {
            "H1": "SINGLE_R38_DATA_POINT_ONLY; CANNOT_PROVE_FORALL_F",
            "H2": "R38_STILL_REQUIRES_FIXED_TRACTABLE_CLASS_AUDITS_INCLUDING_QHORN; BA25_LOW_WIDTH_ROUTE_NOW_MEASURED",
            "H3": "NOT_ESTABLISHED_BY_ONE_INSTANCE",
            "primary_blocker": "UNIVERSAL_RESIDUAL_STRUCTURAL_FUNNEL_THEOREM",
        },
        "firewalls": {
            "heuristic_min_fill_promoted_to_exact_treewidth": False,
            "single_R38_instance_promoted_to_universal_H1": False,
            "BA26_STARTED": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/TRUMP_R38_FIXPOINT_TO_BA25_FACTOR_GRAPH_DIAGNOSTIC_2026-09-10.json")
    args = ap.parse_args()
    out = run()
    p = Path(args.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": out["status"],
        "before_tw_interval": out["structural_width"]["before_exact_reductions"]["treewidth_interval"],
        "after_tw_interval": out["structural_width"]["after_exact_reductions"]["treewidth_interval"],
        "tau_used": out["BA25_factor_graph"]["tau_used_by_BA25"],
        "peak_states": out["BA25_factor_graph"]["peak_table_states"],
        "model_count": out["exact_semantics"]["exact_model_count"],
        "replay_failures": out["exact_semantics"]["direct_original_R38_clause_replay_failures"],
        "SAT_IN_P": out["firewalls"]["SAT_IN_P"],
        "P_VS_NP": out["firewalls"]["P_VS_NP"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
