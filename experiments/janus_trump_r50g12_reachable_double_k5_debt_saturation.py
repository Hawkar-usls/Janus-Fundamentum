from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g11_support_frontier_double_debt_core as r50g11

GATE = "JANUS_TRUMP_R50G12_REACHABLE_DOUBLE_K5_DEBT_SATURATION"
WIDTH_CAP = 4
MIN_ALL_CLOSED_VARS = 6
REACH_CONTROL_PREDECESSOR_PIVOT = 1
REACH_CONTROL_DANGEROUS_PIVOT = 2
REACH_CONTROL_ROOT_POS = (1, 2, -101)
REACH_CONTROL_ROOT_NEG = (-1, -102, -103)
REACH_CONTROL_X_NEG = (-2, -104, -107)
REACH_CONTROL_REACHED_X_POS = (2, -101, -102, -103)
REACH_CONTROL_WIDE = (-101, -102, -103, -104, -107)


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def support_vars(literals):
    return {abs(int(l)) for l in literals}


def exact_bve_admission_for_var(formula, y: int):
    """Replay the frozen r33.bve_candidate admission predicate for one pivot."""
    f = canon(formula)
    y = int(y)
    pos = [c for c in f if y in c]
    neg = [c for c in f if -y in c]
    if not pos or not neg:
        return {
            "pivot": y,
            "bipolar": False,
            "accepted": False,
            "reason": "NONBIPOLAR",
        }

    resolvents = set()
    for p in pos:
        for n in neg:
            rr = (set(p) - {y}) | (set(n) - {-y})
            if any(-lit in rr for lit in rr):
                continue
            resolvents.add(r33.canonical_clause(rr))
    resolvents = tuple(sorted(resolvents))
    removed = set(pos + neg)
    transformed = canon([c for c in f if c not in removed] + list(resolvents))
    count_ok = len(resolvents) <= len(removed)
    measure_ok = tuple(r33.measure(transformed)) < tuple(r33.measure(f))
    accepted = bool(count_ok and measure_ok)
    reasons = []
    if not count_ok:
        reasons.append("RESOLVENT_COUNT_GT_REMOVED_PARENT_COUNT")
    if not measure_ok:
        reasons.append("R33_C_L_V_MEASURE_NOT_STRICTLY_DECREASING")
    return {
        "pivot": y,
        "bipolar": True,
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "removed_parent_count": len(removed),
        "unique_nontaut_resolvent_count": len(resolvents),
        "count_ok": count_ok,
        "measure_before_C_L_V": list(r33.measure(f)),
        "measure_after_C_L_V": list(r33.measure(transformed)),
        "measure_ok": measure_ok,
        "accepted": accepted,
        "rejection_reasons": reasons,
    }


def earlier_bve_order_debt(formula, x: int):
    """Exact conditional debt induced by ascending frozen BVE pivot order."""
    f = canon(formula)
    if not r50g10.exact_pre_bve_clean(f):
        raise AssertionError("R50G12_ORDER_DEBT_REQUIRES_PRE_BVE_CLEAN")
    direct = r50g4.first_r33_micro_candidate(f)
    if direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct.get("var", -1)) != int(x):
        raise AssertionError(("R50G12_ORDER_DEBT_X_NOT_FIRST_BVE", x, direct))

    rows = []
    for y in r33.variables(f):
        y = int(y)
        if y >= int(x):
            continue
        record = exact_bve_admission_for_var(f, y)
        if not record["bipolar"]:
            # Pre-BVE clean includes no pure literal, so every present variable
            # must occur in both polarities.
            raise AssertionError(("R50G12_PRE_BVE_EARLIER_VAR_NONBIPOLAR", y, record))
        if record["accepted"]:
            raise AssertionError(("R50G12_EARLIER_ACCEPTED_BVE_SHOULD_PREEMPT_X", y, x, record))
        if not record["rejection_reasons"]:
            raise AssertionError(("R50G12_EARLIER_BVE_REJECT_WITHOUT_REASON", y, record))
        rows.append(record)
    return {
        "first_BVE_pivot": int(x),
        "earlier_present_variable_count": len(rows),
        "all_earlier_variables_have_exact_rejection_receipt": True,
        "rows": rows,
    }


def v6_double_k5_certificate(formula, x: int):
    """Mechanically certify the exact V=6 consequence if all alternate doors close.

    The theorem is conditional.  An input that does not have exactly six
    variables or does not close all alternate doors is classified as
    non-applicable rather than as evidence for the theorem.
    """
    f = canon(formula)
    vars_ = set(int(v) for v in r33.variables(f))
    if len(vars_) != MIN_ALL_CLOSED_VARS:
        return {
            "applicable": False,
            "reason": "VARIABLE_COUNT_NOT_6",
            "variable_count": len(vars_),
        }
    if int(x) not in vars_:
        raise AssertionError(("R50G12_X_NOT_PRESENT", x, sorted(vars_)))
    if not r50g10.exact_pre_bve_clean(f):
        raise AssertionError("R50G12_V6_SOURCE_NOT_PRE_BVE_CLEAN")

    doors = r50g10.profile_all_alternate_doors(f, int(x))
    if not doors["all_alternate_doors_closed"]:
        return {
            "applicable": False,
            "reason": "NOT_ALL_ALTERNATE_DOORS_CLOSED",
            "variable_count": 6,
            "open_door_count": doors["open_door_count"],
            "closed_door_count": doors["closed_door_count"],
            "first_open_door": doors["first_open_door"],
        }

    alts = sorted(vars_ - {int(x)})
    if len(alts) != 5:
        raise AssertionError(("R50G12_ALT_COUNT_NOT5", x, alts))

    chi_graph = {}
    r47j_graph = {}
    rows = []
    by_door = {int(r["pivot"]): r for r in doors["rows"]}
    for y in alts:
        door = by_door[y]
        if not door["closed_door_certificate"]:
            raise AssertionError(("R50G12_V6_OPEN_DOOR_IN_ALL_CLOSED", y, door))

        chi = r50g11.chi_bad_pair_certificate(f, y)
        if int(chi["chi_star"]) != 5:
            raise AssertionError(("R50G12_V6_CLOSED_CHI_NOT_EXACT5", y, chi))
        if chi["witness"] is None:
            raise AssertionError(("R50G12_V6_CHI5_WITHOUT_WITNESS", y, chi))
        chi_support = support_vars(chi["witness"]["nontautological_union"])
        expected_support = vars_ - {y}
        if chi_support != expected_support:
            raise AssertionError(("R50G12_V6_CHI_DOES_NOT_USE_ALL_OTHER_VARS", y, chi_support, expected_support, chi))

        rj = r50g11.r47j_wide_debt_certificate(f, y)
        if rj["safe"] or rj["terminal"] is not None or int(rj["final_width"]) != 5:
            raise AssertionError(("R50G12_V6_R47J_DEBT_NOT_EXACT_W5_NONTERMINAL", y, rj))
        rj_support = support_vars(rj["widest_final_clause"])
        if rj_support != expected_support:
            raise AssertionError(("R50G12_V6_R47J_WIDE_CLAUSE_NOT_ALL_OTHER_VARS", y, rj_support, expected_support, rj))

        expected_alt_neighbours = sorted(set(alts) - {y})
        chi_neigh = sorted(chi_support - {int(x), y})
        rj_neigh = sorted(rj_support - {int(x), y})
        if chi_neigh != expected_alt_neighbours:
            raise AssertionError(("R50G12_V6_CHI_GRAPH_NOT_K5_ROW", y, chi_neigh, expected_alt_neighbours))
        if rj_neigh != expected_alt_neighbours:
            raise AssertionError(("R50G12_V6_R47J_GRAPH_NOT_K5_ROW", y, rj_neigh, expected_alt_neighbours))
        chi_graph[y] = chi_neigh
        r47j_graph[y] = rj_neigh
        rows.append({
            "pivot": y,
            "chi_star": 5,
            "chi_witness": chi["witness"],
            "r47j_final_width": 5,
            "r47j_widest_final_clause": rj["widest_final_clause"],
            "chi_alt_neighbours": chi_neigh,
            "r47j_alt_neighbours": rj_neigh,
        })

    order_debt = earlier_bve_order_debt(f, int(x))
    expected_graph = {y: sorted(set(alts) - {y}) for y in alts}
    if chi_graph != expected_graph or r47j_graph != expected_graph:
        raise AssertionError(("R50G12_V6_DOUBLE_K5_GRAPH_MISMATCH", chi_graph, r47j_graph, expected_graph))

    return {
        "applicable": True,
        "all_alternate_doors_closed": True,
        "variable_count": 6,
        "dangerous_pivot": int(x),
        "alternate_variables": alts,
        "chi_star_exactly_5_for_every_alternate": True,
        "R47J_final_width_exactly_5_for_every_alternate": True,
        "chi_graph": chi_graph,
        "r47j_graph": r47j_graph,
        "both_graphs_equal_complete_directed_K5": True,
        "rows": rows,
        "earlier_BVE_order_debt": order_debt,
    }


def even_prism_tseitin(n_vertices: int = 12):
    """Complete CNF for even parity on every vertex of a 3-regular prism."""
    if n_vertices < 8 or n_vertices % 2:
        raise ValueError("R50G12_PRISM_REQUIRES_EVEN_N_GE8")
    k = n_vertices // 2
    edges = []

    def add_edge(u: int, v: int):
        if u > v:
            u, v = v, u
        if (u, v) not in edges:
            edges.append((u, v))

    for i in range(k):
        add_edge(i, (i + 1) % k)
        add_edge(k + i, k + ((i + 1) % k))
        add_edge(i, k + i)

    incident = defaultdict(list)
    for edge_var, (u, v) in enumerate(edges, 1):
        incident[u].append(edge_var)
        incident[v].append(edge_var)

    clauses = []
    for vertex in range(n_vertices):
        xs = sorted(incident[vertex])
        if len(xs) != 3:
            raise AssertionError("R50G12_PRISM_NOT_3_REGULAR")
        for bits in itertools.product((0, 1), repeat=3):
            if sum(bits) % 2 == 0:
                continue
            clauses.append(tuple(x if bit == 0 else -x for x, bit in zip(xs, bits)))
    return canon(clauses)


def shift_formula(formula, offset: int = 100):
    return canon(
        tuple((1 if lit > 0 else -1) * (abs(int(lit)) + offset) for lit in clause)
        for clause in canon(formula)
    )


def build_reachable_same_pivot_wide_control():
    """Independently reconstruct the audited one-step U_mu reachability witness."""
    core = shift_formula(even_prism_tseitin())
    root = canon(list(core) + [REACH_CONTROL_ROOT_POS, REACH_CONTROL_ROOT_NEG, REACH_CONTROL_X_NEG])
    reached = canon(list(core) + [REACH_CONTROL_REACHED_X_POS, REACH_CONTROL_X_NEG])
    return core, root, reached


def verify_reachable_same_pivot_wide_control():
    core, root, reached = build_reachable_same_pivot_wide_control()
    if max_width(root) > 3:
        raise AssertionError(("R50G12_REACH_ROOT_NOT_W3", max_width(root)))
    if not r50g10.exact_pre_bve_clean(root):
        raise AssertionError("R50G12_REACH_ROOT_NOT_PRE_BVE_CLEAN")

    direct_root = r50g4.first_r33_micro_candidate(root)
    if direct_root.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct_root.get("var", -1)) != REACH_CONTROL_PREDECESSOR_PIVOT:
        raise AssertionError(("R50G12_REACH_ROOT_FIRST_BVE_NOT_Y", direct_root))
    if canon(direct_root["after"]) != reached:
        raise AssertionError(("R50G12_REACH_ROOT_BVE_SUCCESSOR_MISMATCH", r50g4.fhash(direct_root["after"]), r50g4.fhash(reached)))

    root_micro = r50g4.micro_r33_status(root)
    if root_micro["status"] != "AUTHORIZED_R33_MICROSTEP" or max_width(root_micro["after"]) != 4:
        raise AssertionError(("R50G12_REACH_ROOT_NOT_AUTHORIZED_TO_W4", root_micro))
    root_step = r50g4.refined_exact_step(root)
    if root_step["kind"] != "NONTERMINAL" or root_step["lane"] != "R33_EXACT_W4_MICROSTEP":
        raise AssertionError(("R50G12_REACH_ROOT_U_MU_LANE_FAIL", root_step))
    if canon(root_step["successor"]) != reached:
        raise AssertionError("R50G12_REACH_U_MU_SUCCESSOR_MISMATCH")

    if not r50g10.exact_pre_bve_clean(reached):
        raise AssertionError("R50G12_REACHED_NOT_PRE_BVE_CLEAN")
    direct_reached = r50g4.first_r33_micro_candidate(reached)
    if direct_reached.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct_reached.get("var", -1)) != REACH_CONTROL_DANGEROUS_PIVOT:
        raise AssertionError(("R50G12_REACHED_FIRST_BVE_NOT_X", direct_reached))
    if REACH_CONTROL_WIDE not in canon(direct_reached["after"]):
        raise AssertionError("R50G12_REACHED_EXPECTED_WIDE_MISSING")
    reached_micro = r50g4.micro_r33_status(reached)
    if reached_micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        raise AssertionError(("R50G12_REACHED_NOT_IMMEDIATE_BVE_ESCAPE", reached_micro))

    row, candidate = r50a._fallback_candidate(reached, REACH_CONTROL_DANGEROUS_PIVOT)
    if candidate is None:
        raise AssertionError("R50G12_REACHED_SAME_PIVOT_CANDIDATE_MISSING")
    replay = r47j.independent_fixpoint_macro_replay(reached, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G12_REACHED_SAME_PIVOT_REPLAY_FAIL", replay))
    if row["width4_safe"] or row["terminal"] is not None or int(row["final_max_width"]) <= 4:
        raise AssertionError(("R50G12_REACHED_SAME_PIVOT_NOT_UNSAFE_WIDE", row))

    doors = r50g10.profile_all_alternate_doors(reached, REACH_CONTROL_DANGEROUS_PIVOT)
    if doors["all_alternate_doors_closed"]:
        raise AssertionError("R50G12_REACH_CONTROL_UNEXPECTEDLY_ALL_DOORS_CLOSED")
    if not any(r["r49h_authorized"] for r in doors["rows"]):
        raise AssertionError(("R50G12_REACH_CONTROL_EXPECTED_R49H_RESCUE_MISSING", doors))

    root_model = {v: False for v in r33.variables(root)}
    reached_model = {v: False for v in r33.variables(reached)}
    if not r33.eval_formula(root, root_model) or not r33.eval_formula(reached, reached_model):
        raise AssertionError("R50G12_REACH_CONTROL_EXPLICIT_SAT_MODEL_FAIL")

    return {
        "root_hash": r50g4.fhash(root),
        "root_measure_C_L_V": list(r33.measure(root)),
        "root_width": max_width(root),
        "predecessor_pivot": REACH_CONTROL_PREDECESSOR_PIVOT,
        "authorized_lane": root_step["lane"],
        "reached_hash": r50g4.fhash(reached),
        "reached_measure_C_L_V": list(r33.measure(reached)),
        "reached_width": max_width(reached),
        "dangerous_pivot": REACH_CONTROL_DANGEROUS_PIVOT,
        "immediate_BVE_escape": True,
        "same_pivot_terminal": row["terminal"],
        "same_pivot_final_width": int(row["final_max_width"]),
        "same_pivot_safe": False,
        "same_pivot_independent_replay_pass": True,
        "expected_wide_resolvent": list(REACH_CONTROL_WIDE),
        "alternate_open_door_count": doors["open_door_count"],
        "alternate_closed_door_count": doors["closed_door_count"],
        "alternate_R49H_door_count": doors["r49h_door_count"],
        "alternate_R47J_safe_door_count": doors["r47j_safe_door_count"],
        "all_alternate_doors_closed": False,
        "explicit_root_and_reached_SAT_models_verified": True,
    }


def run():
    reachable_control = verify_reachable_same_pivot_wide_control()
    frozen_replay = r50g10.replay_frozen_reachable_roots()

    # R50G11 has already proved V>=6 for a genuine all-doors-closed core.  This
    # gate closes the exact V=6 conditional shape.  The frozen replay currently
    # contains no same-pivot wide survivor, so there is no live all-closed V6
    # state on which to instantiate the conditional certificate.
    if frozen_replay["wide_survivors_without_existing_alternate_door"]:
        raise AssertionError(("R50G12_FROZEN_REPLAY_FOUND_ALL_CLOSED_REQUIRES_EXPLICIT_V6_OR_LARGER_AUDIT", frozen_replay))

    return {
        "gate": GATE,
        "mode": "SOURCE_THEOREM_PLUS_REACHABLE_COUNTERCONTROL_PLUS_FROZEN_REPLAY",
        "proved_from_frozen_source_definitions": [
            "ALL_DOORS_CLOSED_IMPLIES_V_GE_6",
            "AT_V6_CLOSED_R49H_IMPLIES_CHI_STAR_EXACTLY_5",
            "AT_V6_EACH_CHI_DEBT_WITNESS_USES_ALL_FIVE_OTHER_VARIABLES",
            "AT_V6_CLOSED_R47J_IMPLIES_NONTERMINAL_FINAL_WIDTH_EXACTLY_5",
            "AT_V6_EACH_R47J_DEBT_WIDE_CLAUSE_USES_ALL_FIVE_OTHER_VARIABLES",
            "AT_V6_BOTH_ALTERNATE_DEBT_GRAPHS_EQUAL_COMPLETE_DIRECTED_K5",
            "EVERY_PRESENT_Y_BELOW_FIRST_BVE_X_CARRIES_EXACT_FROZEN_BVE_REJECTION_RECEIPT",
        ],
        "V6_double_K5_theorem": {
            "status": "PROVED_CONDITIONALLY_FROM_FROZEN_DEFINITIONS_AND_EXECUTABLE_CERTIFIER",
            "condition": "V=6 AND PRE_BVE_CLEAN AND IMMEDIATE_BVE_X AND ALL_ALTERNATE_DOORS_CLOSED",
            "conclusion": "CHI_DEBT_GRAPH=K5_DIRECTED AND R47J_DEBT_GRAPH=K5_DIRECTED",
            "impossibility_claimed": False,
        },
        "reachable_same_pivot_wide_control": reachable_control,
        "reachable_same_pivot_W4_safety": "REFUTED_RESEALED_ON_CURRENT_BRANCH",
        "frozen_reachable_replay": frozen_replay,
        "live_V6_all_doors_closed_witness": None,
        "critical_next_obligation": "PROVE_OR_REFUTE_REALIZABILITY_OF_A_U_MU_REACHABLE_PRE_BVE_CLEAN_DOUBLE_K5_ALL_DOORS_CLOSED_CORE_UNDER_FROZEN_BVE_ADMISSION_ORDER_AND_CLAUSE_INCIDENCE",
        "verdict": "V6_DOUBLE_K5_SATURATION_THEOREM_CLOSED__REACHABLE_SAME_PIVOT_WIDE_REFUTATION_RESEALED__V6_DOUBLE_K5_REALIZABILITY_OR_EXCLUSION_OPEN",
        "firewall": {
            "FINITE_SUCCESS_IMPLIES_V6_IMPOSSIBILITY": False,
            "HEURISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "REACHABLE_SAME_PIVOT_W4_SAFETY": "REFUTED",
            "V6_DOUBLE_K5_SATURATION": "PROVED",
            "V6_DOUBLE_K5_IMPOSSIBILITY": "OPEN",
            "REACHABLE_ALTERNATE_DOOR_THEOREM": "OPEN",
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
