from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47k_extended_normalization_closure_one_swap_falsifier as r47k
import janus_trump_r47r_targeted_two_swap_depth2_rescue_disruption as r47r
import janus_trump_r47w_fixed_depth3_rescue_or_certified_lower_bound as r47w

GATE = "JANUS_TRUMP_R47X2_COMMUTING_UNLOCK_SET_ATLAS"
EXPECTED_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_CLV = (76, 203, 22)
EXPECTED_DEPTH2_COUNT = 462
EXPECTED_DEPTH2_LEDGER_HASH = "72416db56bcff832efed776c902e8d2e158cc706139bfac44e6c5366ab8340ed"
KNOWN_EDGE = (11, 12, 15)


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def fhash(formula):
    return r47f.formula_hash(canon(formula))


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def terminal_kind(candidate):
    term = candidate["normalization"]["terminal"]
    if term is None:
        return None
    if isinstance(term, dict):
        return term.get("kind") or term.get("status") or str(term)
    return str(term)


def tarjan_scc(graph):
    index = 0
    stack = []
    on_stack = set()
    indices = {}
    low = {}
    comps = []

    def visit(v):
        nonlocal index
        indices[v] = low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in sorted(graph.get(v, ())):
            if w not in indices:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            comp = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            comps.append(sorted(comp))

    for v in sorted(graph):
        if v not in indices:
            visit(v)
    return sorted(comps, key=lambda c: (min(c), len(c), c))


def condensation_metrics(graph, sccs):
    comp_of = {}
    for i, comp in enumerate(sccs):
        for v in comp:
            comp_of[v] = i
    dag = {i: set() for i in range(len(sccs))}
    for u, outs in graph.items():
        for v in outs:
            cu, cv = comp_of[u], comp_of[v]
            if cu != cv:
                dag[cu].add(cv)
    memo = {}

    def depth(c):
        if c in memo:
            return memo[c]
        memo[c] = 1 + max((depth(n) for n in dag[c]), default=0)
        return memo[c]

    longest = max((depth(c) for c in dag), default=0)
    edges = sorted((u, v) for u, outs in dag.items() for v in outs)
    return {"SCC_count": len(sccs), "condensation_edge_count": len(edges), "condensation_depth": longest}


def run(output: Path | None = None):
    _, original = r47w.load_witness()
    if fhash(original) != EXPECTED_HASH or clv(original) != EXPECTED_CLV:
        raise AssertionError("R47X2_INPUT_DRIFT")

    depth1 = r47k.first_extended_accept(original)
    if depth1["covered"]:
        raise AssertionError(("R47X2_DEPTH1_DRIFT", depth1["selected_var"]))
    depth2 = r47r.depth2_scan(original, keep_all_failures=True)
    if depth2["covered"]:
        raise AssertionError(("R47X2_DEPTH2_DRIFT", depth2["selected_pair"]))
    failures = depth2["all_failures"]
    if len(failures) != EXPECTED_DEPTH2_COUNT:
        raise AssertionError(("R47X2_DEPTH2_COUNT_DRIFT", len(failures)))
    ledger_hash = canonical_hash(failures)
    if ledger_hash != EXPECTED_DEPTH2_LEDGER_HASH:
        raise AssertionError(("R47X2_DEPTH2_LEDGER_DRIFT", ledger_hash))

    # Because every legal depth-1 and depth-2 sequence is dead, every accepted
    # depth-3 sequence is automatically minimal with a two-key prerequisite.
    pair_rows = sorted(failures, key=lambda r: (int(r["first_var"]), int(r["second_var"])))
    triple_digest = hashlib.sha256()
    tested = 0
    accepted_sequences = []
    hyper = {}

    for pair_row in pair_rows:
        a = int(pair_row["first_var"])
        b = int(pair_row["second_var"])
        first, g1, second, g2 = r47w.recompute_pair(original, a, b)
        prefix_hash = fhash(g2)
        prefix_clv = list(clv(g2))
        for c in sorted(r33.variables(g2)):
            third = r47j.macro_candidate_fixpoint(g2, int(c))
            if third is None:
                continue
            r47w.replay_layer(g2, third, (a, b, int(c)))
            g3 = canon(third["normalization"]["final_formula"])
            accepted = third["normalization"]["terminal"] is not None or clv(g3) < clv(original)
            tested += 1
            digest_row = {
                "sequence": [a, b, int(c)],
                "prefix_hash": prefix_hash,
                "prefix_CLV": prefix_clv,
                "final_hash": fhash(g3),
                "final_CLV": list(clv(g3)),
                "terminal": terminal_kind(third),
                "accepted": bool(accepted),
            }
            triple_digest.update((json.dumps(digest_row, sort_keys=True, separators=(",", ":")) + "\n").encode())
            if not accepted:
                continue
            composed = r47w.verify_terminal_sat_composition(original, first, g1, second, g2, third)
            if not composed["pass"]:
                raise AssertionError(("R47X2_TERMINAL_SAT_COMPOSITION_FAIL", digest_row, composed))
            accepted_sequences.append(digest_row)
            x, y = sorted((a, b))
            key = (x, y, int(c))
            edge = hyper.setdefault(key, {
                "keys": [x, y],
                "target": int(c),
                "orders": {},
            })
            edge["orders"][f"{a},{b}"] = {
                "accepted": True,
                "prefix_hash": prefix_hash,
                "prefix_CLV": prefix_clv,
                "final_hash": fhash(g3),
                "final_CLV": list(clv(g3)),
                "terminal": terminal_kind(third),
            }

    edges = []
    order_sensitive = 0
    order_insensitive = 0
    convergent = 0
    nonconvergent = 0
    graph = {}

    for key in sorted(hyper):
        edge = hyper[key]
        x, y = edge["keys"]
        c = edge["target"]
        o1 = edge["orders"].get(f"{x},{y}")
        o2 = edge["orders"].get(f"{y},{x}")
        both = o1 is not None and o2 is not None
        convergence = bool(both and o1["prefix_hash"] == o2["prefix_hash"])
        edge["order_sensitive"] = not both
        edge["both_orders_accepted"] = both
        edge["prefixes_converge"] = convergence
        edge["accepted_order_count"] = int(o1 is not None) + int(o2 is not None)
        if both:
            order_insensitive += 1
            if convergence:
                convergent += 1
            else:
                nonconvergent += 1
        else:
            order_sensitive += 1
        edges.append(edge)
        graph.setdefault(x, set()).add(c)
        graph.setdefault(y, set()).add(c)
        graph.setdefault(c, set())

    known = next((e for e in edges if e["keys"] == [11, 12] and e["target"] == 15), None)
    if known is None or not known["both_orders_accepted"] or not known["prefixes_converge"]:
        raise AssertionError(("R47X2_KNOWN_EDGE_DRIFT", known))

    sccs = tarjan_scc(graph)
    cm = condensation_metrics(graph, sccs)
    involved_nodes = sorted(graph)
    largest_scc = max((len(c) for c in sccs), default=0)

    if len(edges) == 1:
        classification = "NO_ADDITIONAL_MINIMAL_TWO_KEY_UNLOCKS_BEYOND_SEALED_EDGE"
    elif order_sensitive > 0 and order_insensitive == 0:
        classification = "RIGID_ORDER_SENSITIVE_SERIAL_SIGNAL"
    elif order_sensitive > 0 and order_insensitive > 0:
        classification = "MIXED_ORDER_SENSITIVE_AND_COMMUTING_UNLOCK_STRUCTURE"
    elif cm["condensation_depth"] <= 2 or largest_scc == len(involved_nodes):
        classification = "COMMUTING_UNLOCK_HYPERGRAPH_RAPIDLY_COLLAPSES"
    else:
        classification = "COMMUTING_UNLOCK_HYPERGRAPH_WITH_NONTRIVIAL_CAUSAL_DEPTH"

    target_min_prereq = {}
    for e in edges:
        t = str(e["target"])
        target_min_prereq[t] = 2

    out = {
        "gate": GATE,
        "parent_R47X_result_commit": "3779026bc213e1fcee1f6727a3c89b1c24a330f0",
        "input_hash": EXPECTED_HASH,
        "input_CLV": list(EXPECTED_CLV),
        "depth1_reconfirmed_dead": True,
        "depth2_reconfirmed_dead": True,
        "depth2_failed_pair_count": len(failures),
        "depth2_failed_pair_ledger_sha256": ledger_hash,
        "complete_depth3_scan": True,
        "depth3_tested_candidate_count": tested,
        "depth3_complete_digest_sha256": triple_digest.hexdigest(),
        "accepted_depth3_sequence_count": len(accepted_sequences),
        "accepted_depth3_sequences_sha256": canonical_hash(accepted_sequences),
        "minimal_two_key_unlock_hyperedge_count": len(edges),
        "minimal_two_key_unlock_hyperedges": edges,
        "target_minimum_prerequisite_size_within_tested_bound": target_min_prereq,
        "order_statistics": {
            "order_sensitive_hyperedge_count": order_sensitive,
            "order_insensitive_hyperedge_count": order_insensitive,
            "convergent_commuting_hyperedge_count": convergent,
            "nonconvergent_order_insensitive_hyperedge_count": nonconvergent,
        },
        "causal_incidence": {
            "involved_nodes": involved_nodes,
            "involved_node_count": len(involved_nodes),
            "directed_edge_count": sum(len(v) for v in graph.values()),
            "SCCs": sccs,
            "largest_SCC_size": largest_scc,
            **cm,
        },
        "classification": classification,
        "interpretation": {
            "finite_witness_only": True,
            "unbounded_unlock_rank_proved": False,
            "universal_constant_K_proved": False,
            "next_theorem_front": "COUPLED_UNLOCK_SET_RANK_AMPLIFICATION_OR_ROOT_INDEPENDENT_CAUSAL_DIAMETER_BOUND",
        },
        "firewall": {
            "UNBOUNDED_UNLOCK_SET_RANK": "NOT_PROVED",
            "UNBOUNDED_DEPTH_FAMILY_EXISTS": "NOT_PROVED",
            "UNIVERSAL_CONSTANT_K_EXISTS": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    summary = {k: out[k] for k in (
        "gate", "depth3_tested_candidate_count", "accepted_depth3_sequence_count",
        "minimal_two_key_unlock_hyperedge_count", "order_statistics", "causal_incidence", "classification"
    )}
    print(json.dumps(summary, sort_keys=True))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
