from __future__ import annotations

import argparse
import hashlib
import json
import math
from itertools import product
from pathlib import Path

import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az
import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av

GATE = "R50G25BA0_TARGET_FAMILY_EXPRESSIVITY_INTERFACE_CAPACITY_AUDIT"
PREREG = "d096066e88d2f90240892ff37546c5876732f313"
PARENT_AZ_SOURCE = "aa0a6114c4e9a437a0aa1b60f05df605e4f0cc3d"
AZ_RECEIPT = "6de0ca8283c2289d5a38f8eb1f37e1550b7fda93"
AZ_META_FINAL = "7e7ddf58a5358fbbc9ee1f104cf0b5a411f7a141"
Y_HASH = az.Y_HASH
UNIT_VARS = tuple(az.UNIT_VARS)
ORDER = tuple(az.ORDER)

OUTCOME = "BA0-B_EXACT_F_g_EXPRESSIVITY_BLOCKED"

r33 = av.r33


def sha_obj(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def eval_formula(formula, assignment):
    return all(r33.eval_clause(tuple(c), assignment) for c in formula)


def enumerate_unit_models(U):
    models = []
    endpoint = {(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 0}
    first_by_pair = {}
    for bits in product((False, True), repeat=len(UNIT_VARS)):
        a = dict(zip(UNIT_VARS, bits))
        if eval_formula(U, a):
            models.append(a)
            pair = (int(a[2]), int(a[30]))
            endpoint[pair] += 1
            first_by_pair.setdefault(pair, a)
    return models, endpoint, first_by_pair


def compact_assignment(a):
    return {str(k): int(bool(v)) for k, v in sorted(a.items())}


def exact_target_definition():
    return {
        "parameter_list": ["g: integer >= 1"],
        "additional_free_parameters": [],
        "deterministic_for_fixed_g": True,
        "same_g_can_yield_different_target_under_frozen_contract": False,
        "unit_rule": "U_j = shift(U,30*j), j=0..g-1",
        "bridge_rule": "B_j=(30+30*j,32+30*j), j=0..g-2",
        "formula_rule": "F_g=canonical_union(all U_j, all B_j)",
        "exact_measures": {"C_g": "64*g-1", "L_g": "157*g-2", "V_g": "20*g"},
        "semantic_payload_fields": [],
        "certificate_metadata_is_target_semantics": False,
    }


def generic_sat_certificate(U, first_by_pair):
    # Choose the same local model with (x2,x30)=(0,1) in every shifted block.
    pair = (0,1)
    witness = first_by_pair.get(pair)
    failures = []
    if witness is None:
        failures.append("NO_UNIT_MODEL_WITH_ENDPOINT_PAIR_0_1")
    elif not eval_formula(U, witness):
        failures.append("LOCAL_WITNESS_DOES_NOT_SATISFY_U")
    if witness is not None and (int(witness[2]), int(witness[30])) != pair:
        failures.append("LOCAL_WITNESS_ENDPOINT_DRIFT")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "local_witness_endpoint_pair": list(pair),
        "local_witness": compact_assignment(witness) if witness is not None else None,
        "local_witness_sha256": sha_obj(compact_assignment(witness)) if witness is not None else None,
        "uniform_construction": "For every block j, assign a_g(v+30*j)=a_U(v) using the fixed U-model with a_U(2)=0,a_U(30)=1.",
        "unit_argument": "Variable renaming preserves satisfaction, so every shifted U_j is satisfied.",
        "bridge_argument": "Every B_j=(30+30*j,32+30*j) has its left literal true because a_g(30+30*j)=1; therefore every bridge is satisfied independently of the next block.",
        "generic_conclusion": "FOR_ALL_INTEGER_g_GE_1_SAT(F_g)",
        "uses_finite_g_ladder": False,
    }


def decision_obstruction():
    bottom = r33.canonical_formula([()])
    bottom_sat = eval_formula(bottom, {})
    contradictory_units = r33.canonical_formula([(1,), (-1,)])
    contradictory_sat = any(
        eval_formula(contradictory_units, {1:b}) for b in (False, True)
    )
    return {
        "smallest_preferred_source": {
            "formula": [list(c) for c in bottom],
            "C": len(bottom),
            "L": sum(len(c) for c in bottom),
            "V": len(r33.variables(bottom)),
            "sat": bool(bottom_sat),
            "kind": "ONE_EMPTY_CLAUSE_CNF",
        },
        "fallback_contradictory_units": {
            "formula": [list(c) for c in contradictory_units],
            "sat": bool(contradictory_sat),
        },
        "corollary": "Because every exact F_g is SAT, no total SAT-preserving mapping arbitrary-CNF -> exact F_g can map this UNSAT source while preserving SAT iff SAT.",
        "refutes_AZ": False,
    }


def source_information_capacity():
    return {
        "available_target_semantic_channels": {
            "g": "YES: chain length / target size",
            "unit_choice": "NO: U is frozen",
            "bridge_choice": "NO: positive binary bridge is frozen",
            "clause_or_sign_choice": "NO",
            "boundary_payload": "NO",
            "auxiliary_payload": "NO",
            "certificate_metadata": "NOT TARGET SEMANTICS",
        },
        "only_source_dependent_semantic_choice_possible_without_changing_target_class": "g",
        "literal_budget_count": "If L(F_g)<=B then g<=floor((B+2)/157); therefore at most floor((B+2)/157) exact targets are available.",
        "polynomial_output_consequence": "For B=p(m), only poly(m) choices of g exist, carrying O(log m) syntactic choice bits when p is polynomial.",
        "decision_capacity": "ZERO_BITS_FOR_SAT_VS_UNSAT: all exact targets are SAT",
        "proof_metadata_firewall": "PROOF_METADATA != TARGET_SEMANTICS",
    }


def mid_interface(Uinfo):
    defects = Uinfo["defects"]
    equations = Uinfo["equations"]
    q = 32
    mid = az.partial_bucket(defects, equations, ORDER, q)
    scopes = [tuple(sorted({abs(int(l)) for l in c})) for c in defects] + [tuple(sorted(set(e["vars"]))) for e in equations] + [(30,q)]
    adj = az.primal_graph(tuple(UNIT_VARS)+(q,), scopes)
    width = az.explicit_width(adj, ORDER)
    boundary_scope = mid["boundary"]["scope"]
    rows = mid["boundary"]["rows"]
    if boundary_scope != [q]:
        raise AssertionError(("MID_BOUNDARY_SCOPE_DRIFT", boundary_scope))
    if rows != [[0],[1]]:
        raise AssertionError(("MID_BOUNDARY_TABLE_DRIFT", rows))
    truth_table = {"q=0": True, "q=1": True}
    return {
        "internal_induced_width": int(width["width"]),
        "loose_internal_assignment_bound_2_pow_w": 2 ** int(width["width"]),
        "surviving_boundary_scope": boundary_scope,
        "surviving_boundary_variable_count": len(boundary_scope),
        "surviving_boundary_assignments": rows,
        "surviving_relation_truth_table": truth_table,
        "surviving_relation_boolean_function": "TRUE",
        "possible_unary_boolean_functions_if_table_were_source_variable": 4,
        "actual_frozen_MID_templates_available": 1,
        "N_boundary_actual_pairwise_distinguishable_prefix_behaviours": 1,
        "constraint_bits_transmitted_from_eliminated_prefix": 0,
        "capacity_statement": "The exact frozen prefix always projects to the same constant-TRUE unary factor. Therefore no source-dependent residual distinction is transmitted across a chain cut.",
        "important_distinction": "w<=13 bounds internal generated scope; it does not imply 2^13 useful source-semantic states cross the final MID boundary.",
    }


def source_cut_witness():
    plus = {0: False, 1: True}   # x
    minus = {0: True, 1: False}  # not x
    current = {0: True, 1: True}
    return {
        "boundary_variable": "x",
        "source_residual_family": [
            {"name":"P_PLUS", "cnf":[[1]], "truth_table": {"x=0":False,"x=1":True}},
            {"name":"P_MINUS", "cnf":[[-1]], "truth_table": {"x=0":True,"x=1":False}},
        ],
        "required_pairwise_distinct_behaviours": 2,
        "current_MID_available_behaviours": 1,
        "tables_distinct": plus != minus,
        "neither_equals_current_TRUE": plus != current and minus != current,
        "information_that_cannot_cross": "whether the continuation endpoint is required to be 0 or required to be 1",
        "capacity_obstruction": "2 required residual behaviours > 1 actual frozen MID behaviour",
    }


def extension_contract():
    return {
        "status": "REPRESENTATION_CANDIDATE_ONLY_NOT_A_REDUCTION_THEOREM",
        "name": "F_{g,sigma}_EXPLICIT_SEMANTIC_BOUNDARY_PAYLOAD",
        "definition": "F_{g,sigma}=canonical(F_g union payload_CNF(sigma)); sigma is serialized as target-semantic factors, never certificate-only metadata.",
        "minimal_unary_payload": {
            "boundary": "q_j=2+30*(j+1) for cut j",
            "sigma_j_values": {
                "TOP": "no added clause",
                "FORCE_0": "(-q_j)",
                "FORCE_1": "(q_j)",
                "BOTTOM": "empty clause ()"
            },
            "neutral_sigma": "all sigma_j=TOP",
            "neutral_exactness": "F_{g,TOP,...,TOP}=F_g exactly",
            "semantic_gain": "allows the target instance itself to distinguish TRUE, q, not-q, FALSE on a one-bit boundary",
            "still_not_arbitrary_CNF_capable": True,
        },
        "arbitrary_capacity_requirement": {
            "separator_sets": "A future sigma must be allowed to name explicit B_j of width k_j and structured semantic payload P_j over B_j (and explicitly local auxiliaries if needed).",
            "state_lower_bound": "If N pairwise distinguishable residual source states must cross a state-labelled k_j-bit boundary and no compression theorem identifies them, require k_j >= ceil(log2 N).",
            "dense_table_cost": "An explicit truth table over k_j bits has 2^k_j rows; polynomial sigma therefore forbids hiding exponential tables.",
            "structured_payload": "A circuit/CNF/other compact P_j is allowed only if its semantics and verification are explicit and the solver theorem is re-proved for that representation.",
            "width_debt": "Future induced width must be derived from payload incidence; it is not inherited as <=13 automatically.",
        },
        "future_obligations_before_BA1_success": [
            "poly-time construction phi -> (g,sigma)",
            "SAT(phi) iff SAT(F_{g,sigma})",
            "model reconstruction back to phi",
            "independent source-model validation",
            "polynomial sigma size",
            "polynomial relation/certificate size",
            "polynomial total construction+verification+reconstruction time",
            "no hindsight/oracle choice",
            "explicit separator-width bound for the extended target class",
        ],
        "AZ_reuse": "AZ is recovered exactly at neutral sigma. MID/LAST may be reused only on payload-free portions or after a future proof that the payload-augmented templates preserve their obligations.",
    }


def run():
    failures = []
    Uinfo = az.source_unit()
    failures.extend(Uinfo["failures"])
    U = r33.canonical_formula(Uinfo["root"])
    if az.ay.formula_hash(U) != Y_HASH:
        failures.append("Y_HASH_DRIFT")
    if az.ay.clv(U) != (63,155,20):
        failures.append("UNIT_CLV_DRIFT")

    models, endpoint_counts, first_by_pair = enumerate_unit_models(U)
    if len(models) != 60:
        failures.append(("UNIT_MODEL_COUNT_DRIFT", len(models)))
    if set(k for k,v in endpoint_counts.items() if v>0) != {(0,0),(0,1),(1,0),(1,1)}:
        failures.append(("ENDPOINT_PAIR_COVERAGE_DRIFT", endpoint_counts))

    target = exact_target_definition()
    sat = generic_sat_certificate(U, first_by_pair)
    if sat["status"] != "PASS":
        failures.append({"GENERIC_SAT": sat})
    obstruction = decision_obstruction()
    if obstruction["smallest_preferred_source"]["sat"] is not False:
        failures.append("EMPTY_CLAUSE_NOT_UNSAT_UNDER_REPOSITORY_SEMANTICS")
    info = source_information_capacity()
    interface = mid_interface(Uinfo)
    if interface["internal_induced_width"] != 13:
        failures.append(("MID_WIDTH_DRIFT", interface["internal_induced_width"]))
    if interface["N_boundary_actual_pairwise_distinguishable_prefix_behaviours"] != 1:
        failures.append("ACTUAL_BOUNDARY_CAPACITY_DRIFT")
    witness = source_cut_witness()
    if not witness["tables_distinct"] or witness["required_pairwise_distinct_behaviours"] <= witness["current_MID_available_behaviours"]:
        failures.append("SOURCE_CUT_WITNESS_NOT_OBSTRUCTING")

    extension = extension_contract()
    outcome = OUTCOME if not failures else "BA0-D_OPEN_DUE_TO_AUDIT_FAILURE"
    return {
        "gate": GATE,
        "status": "SCIENTIFIC_AUDIT_RESULT",
        "preregistration_commit": PREREG,
        "parent_AZ_source_head": PARENT_AZ_SOURCE,
        "AZ_receipt": AZ_RECEIPT,
        "AZ_meta_final": AZ_META_FINAL,
        "failure_count": len(failures),
        "failures": failures,
        "outcome": outcome,
        "Q1_exact_target": target,
        "Q2_unit_model_facts": {
            "model_count": len(models),
            "endpoint_pair_counts": {str(k):int(v) for k,v in sorted(endpoint_counts.items())},
            "all_four_endpoint_pairs_realized": all(endpoint_counts[p]>0 for p in endpoint_counts),
        },
        "Q2_generic_SAT": sat,
        "Q2_smallest_decision_obstruction": obstruction,
        "Q3_source_information": info,
        "Q4_exact_MID_interface": interface,
        "Q4_source_cut_obstruction": witness,
        "Q5_constant_width_classification": {
            "class": "B_INSUFFICIENT_UNDER_CURRENT_REPRESENTATION_CONTRACT",
            "reason": "The current exposed MID relation is fixed TRUE, so the eliminated prefix cannot communicate even the one-bit distinction FORCE_0 versus FORCE_1. This is stronger and more specific than merely observing w<=13.",
            "proved_compression_invariant_for_arbitrary_source_behaviours": False,
        },
        "Q6_minimal_extension_candidate": extension,
        "interpretation": {
            "AZ_preserved": True,
            "exact_F_g_is_a_solver_target_with_insufficient_arbitrary_decision_expressivity": not failures,
            "arbitrary_CNF_reduction_started": False,
            "BA1_started": False,
        },
        "firewall": {"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    x = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "outcome": x["outcome"],
        "failures": x["failure_count"],
        "unit_models": x["Q2_unit_model_facts"]["model_count"],
        "endpoint_pairs": x["Q2_unit_model_facts"]["endpoint_pair_counts"],
        "N_boundary": x["Q4_exact_MID_interface"]["N_boundary_actual_pairwise_distinguishable_prefix_behaviours"],
        "internal_width": x["Q4_exact_MID_interface"]["internal_induced_width"],
    }, sort_keys=True))
    if x["failure_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
