from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8

GATE = "JANUS_TRUMP_R50G9_EXPLICIT_LOCAL_WIDE_FIXPOINT_COUNTEREXAMPLE"
WIDTH_CAP = 4
PIVOT = 1
SHIFT = 100
N_VERTICES = 12
POS_PARENT = (1, -101, -102, -103)
NEG_PARENT = (-1, -104, -107)
EXPECTED_WIDE = (-101, -102, -103, -104, -107)


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def even_prism_tseitin(n_vertices: int = N_VERTICES):
    if n_vertices < 8 or n_vertices % 2:
        raise ValueError("R50G9_PRISM_REQUIRES_EVEN_N_GE_8")
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
            raise AssertionError("R50G9_PRISM_NOT_3_REGULAR")
        # target parity = 0 at every vertex.  As in frozen R33/R34, include
        # exactly the falsifying odd-parity assignments as clauses.
        for bits in itertools.product((0, 1), repeat=3):
            if sum(bits) % 2 == 0:
                continue
            clauses.append(tuple(x if bit == 0 else -x for x, bit in zip(xs, bits)))
    return canon(clauses)


def shift_formula(formula, offset: int = SHIFT):
    return canon(
        tuple((1 if lit > 0 else -1) * (abs(int(lit)) + offset) for lit in clause)
        for clause in canon(formula)
    )


def source_formula():
    core = even_prism_tseitin()
    shifted = shift_formula(core)
    source = canon(list(shifted) + [POS_PARENT, NEG_PARENT])
    return core, shifted, source


def verify_incidence_necessary_condition(final_formula):
    """Mechanical check of the R50G9 fixed-point incidence lemma.

    For each bipolar variable y in an R33 fixed formula H, let p,n be the
    polarity clause counts and R the unique non-tautological DP resolvent count.
    If R < p+n, frozen BVE must strictly reduce clause count, contradicting the
    fixed-point assumption.  This function checks the necessary inequality on
    the concrete witness and records the extremal rows.
    """
    f = canon(final_formula)
    rows = []
    for y in r33.variables(f):
        pos = [c for c in f if y in c]
        neg = [c for c in f if -y in c]
        if not pos or not neg:
            continue
        resolvents = set()
        for p in pos:
            for n in neg:
                rr = (set(p) - {y}) | (set(n) - {-y})
                if any(-lit in rr for lit in rr):
                    continue
                resolvents.add(r33.canonical_clause(rr))
        if len(resolvents) < len(pos) + len(neg):
            raise AssertionError(("R50G9_FIXED_POINT_INCIDENCE_INEQUALITY_FAIL", y, len(pos), len(neg), len(resolvents)))
        if len(pos) < 2 or len(neg) < 2:
            raise AssertionError(("R50G9_FIXED_POINT_POLARITY_DEGREE_FAIL", y, len(pos), len(neg)))
        rows.append({
            "var": int(y),
            "positive_parent_count": len(pos),
            "negative_parent_count": len(neg),
            "unique_nontaut_resolvent_count": len(resolvents),
            "required_lower_bound": len(pos) + len(neg),
        })
    return rows


def run():
    core, shifted, source = source_formula()

    # Core is a satisfiable complete affine CNF; all-false is an explicit model.
    core_affine = r34.recognize_complete_affine_cnf(core)
    if not core_affine["recognized"]:
        raise AssertionError(("R50G9_EVEN_PRISM_NOT_AFFINE", core_affine))
    core_solution = r34.solve_gf2_with_certificate(core_affine["equations"])
    core_verify = r34.verify_affine_certificate(core, core_affine, core_solution)
    if not core_solution["sat"] or not core_verify["pass"]:
        raise AssertionError(("R50G9_EVEN_PRISM_NOT_CERTIFIED_SAT", core_solution, core_verify))

    if max_width(source) != WIDTH_CAP:
        raise AssertionError(("R50G9_SOURCE_WIDTH_NOT_4", max_width(source)))
    if not r50g8.pre_bve_clean(source):
        raise AssertionError("R50G9_SOURCE_NOT_PRE_BVE_CLEAN")

    micro = r50g4.micro_r33_status(source)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        raise AssertionError(("R50G9_NOT_IMMEDIATE_BVE_ESCAPE", micro))
    direct = r50g4.first_r33_micro_candidate(source)
    if direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct.get("var", -1)) != PIVOT:
        raise AssertionError(("R50G9_FIRST_RULE_NOT_PIVOT1_BVE", direct))
    post_dp = canon(direct["after"])
    if EXPECTED_WIDE not in post_dp:
        raise AssertionError(("R50G9_EXPECTED_WIDTH5_RESOLVENT_MISSING", direct.get("resolvents")))
    if max_width(post_dp) <= WIDTH_CAP:
        raise AssertionError("R50G9_DP_DID_NOT_ESCAPE_W4")

    candidate = r47j.macro_candidate_fixpoint(source, PIVOT)
    if candidate is None:
        raise AssertionError("R50G9_SAME_PIVOT_R47J_MISSING")
    replay = r47j.independent_fixpoint_macro_replay(source, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G9_INDEPENDENT_REPLAY_FAIL", replay))

    norm = candidate["normalization"]
    final = canon(norm["final_formula"])
    if norm["terminal"] is not None:
        raise AssertionError(("R50G9_WITNESS_UNEXPECTEDLY_TERMINAL", norm["terminal"]))
    if max_width(final) <= WIDTH_CAP:
        raise AssertionError(("R50G9_WITNESS_REENTERED_W4", max_width(final)))
    if EXPECTED_WIDE not in final:
        raise AssertionError("R50G9_EXPECTED_WIDE_CLAUSE_DID_NOT_SURVIVE")

    # The intended witness is stronger than merely ending wide: no normalizer
    # changes the post-DP state at all.
    if final != post_dp:
        raise AssertionError(("R50G9_FINAL_DIFFERS_FROM_POST_DP", r50g4.fhash(post_dp), r50g4.fhash(final)))

    final_r33 = r33.simplify(final)
    if final_r33["history"] or final_r33["terminal"] != "STALLED_STACK_LEAN_CORE":
        raise AssertionError(("R50G9_FINAL_NOT_R33_FIXED", final_r33))
    final_affine = r34.recognize_complete_affine_cnf(final)
    if final_affine["recognized"]:
        raise AssertionError("R50G9_FINAL_UNEXPECTEDLY_COMPLETE_AFFINE")
    final_rup = r35b.run_candidate(final)
    if final_rup["status"] != "STALLED_RUP_CORE" or canon(final_rup["final_formula"]) != final:
        raise AssertionError(("R50G9_FINAL_NOT_RUP_FIXED", final_rup["status"]))
    if r33.bve_candidate(final) is not None:
        raise AssertionError("R50G9_FINAL_NOT_BVE_FIXED")

    supports = r50g8.nonblocking_supports_for_clause(final, EXPECTED_WIDE)
    if supports is None or len(supports) != len(EXPECTED_WIDE):
        raise AssertionError(("R50G9_WIDE_SUPPORT_CERTIFICATE_FAIL", supports))

    inspection = r50g8.inspect_immediate_bve_state(source)
    cert = inspection.get("wide_fixpoint_certificate")
    if not inspection.get("final_nonterminal_wide") or not cert:
        raise AssertionError(("R50G9_R50G8_CLASSIFIER_DID_NOT_CERTIFY_WIDE_FIXPOINT", inspection))
    if cert["kind"] != "DIRECT_DP_WIDE_SURVIVOR_TO_FIXPOINT":
        raise AssertionError(("R50G9_UNEXPECTED_ANCESTRY_KIND", cert["kind"]))

    # Explicit semantic model: every shifted core variable is false; pivot can
    # also be false.  This is not transition authority, only a witness sanity check.
    explicit_model = {v: False for v in r33.variables(source)}
    if not r33.eval_formula(source, explicit_model):
        raise AssertionError("R50G9_EXPLICIT_SOURCE_MODEL_FAIL")
    if not r33.eval_formula(final, {v: False for v in r33.variables(final)}):
        raise AssertionError("R50G9_EXPLICIT_FINAL_MODEL_FAIL")

    incidence = verify_incidence_necessary_condition(final)

    return {
        "gate": GATE,
        "mode": "EXACT_DETERMINISTIC_CONSTRUCTIVE_COUNTEREXAMPLE",
        "witness": {
            "core_kind": "EVEN_CHARGE_3_REGULAR_PRISM_TSEITIN_12",
            "core_measure": list(r33.measure(core)),
            "core_affine_certified_sat": True,
            "shift": SHIFT,
            "source_hash": r50g4.fhash(source),
            "source_measure": list(r33.measure(source)),
            "source_max_width": max_width(source),
            "source_pre_bve_clean": True,
            "pivot": PIVOT,
            "positive_parent": list(POS_PARENT),
            "negative_parent": list(NEG_PARENT),
            "expected_width5_resolvent": list(EXPECTED_WIDE),
            "post_DP_hash": r50g4.fhash(post_dp),
            "post_DP_measure": list(r33.measure(post_dp)),
            "post_DP_width": max_width(post_dp),
            "normalization_round_count": int(norm["round_count"]),
            "normalization_restart_count": int(norm["restart_count"]),
            "final_hash": r50g4.fhash(final),
            "final_measure": list(r33.measure(final)),
            "final_width": max_width(final),
            "terminal": None,
            "R33_fixed": True,
            "affine_negative": True,
            "RUP_fixed": True,
            "BVE_fixed": True,
            "same_pivot_machine_safe": False,
            "independent_replay_pass": True,
            "ancestry_kind": cert["kind"],
            "wide_support_count": len(supports),
            "wide_supports": [
                {"literal": int(lit), "witness_clause": list(clause)}
                for lit, clause in sorted(supports.items(), key=lambda kv: r33.lit_key(kv[0]))
            ],
            "explicit_sat_model_verified": True
        },
        "fixed_point_incidence_rows": incidence,
        "verdict": "LOCAL_WIDE_ANCESTRY_IMPOSSIBILITY_AND_LOCAL_SAME_PIVOT_W4_SAFETY_REFUTED_BY_EXACT_CONSTRUCTIVE_WITNESS__REACHABILITY_NOT_ESTABLISHED",
        "critical_next_obligation": "NO_U_MU_REACHABLE_PRE_BVE_CLEAN_W4_SOURCE_CAN_GENERATE_A_WIDE_ANCESTRY_CERTIFICATE_ENDING_AT_A_NONTERMINAL_CERTIFIED_NORMALIZATION_FIXPOINT__OR_EXPLICITLY_REACH_THE_FROZEN_R50G9_WITNESS",
        "firewall": {
            "HEURISTIC_AUTHORITY": False,
            "LEARNED_SELECTOR": False,
            "PROBABILISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "LOCAL_WIDE_ANCESTRY_IMPOSSIBILITY_THEOREM": "REFUTED",
            "LOCAL_SAME_PIVOT_W4_SAFETY": "REFUTED",
            "REACHABILITY_OF_WITNESS": "NOT_ESTABLISHED",
            "REACHABLE_SAME_PIVOT_W4_SAFETY": "OPEN",
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
