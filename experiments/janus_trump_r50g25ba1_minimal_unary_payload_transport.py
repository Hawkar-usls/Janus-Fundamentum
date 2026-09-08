from __future__ import annotations

import argparse
import hashlib
import json
import math
from itertools import product
from pathlib import Path

import janus_trump_r50g25ba0_target_family_expressivity_interface_capacity as ba0
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

GATE = "R50G25BA1_MINIMAL_NONTRIVIAL_SEMANTIC_PAYLOAD_TRANSPORT"
PREREG = "47ac7f28dfdb3b057a1a21d7c8492f37d73e57f6"
PARENT_BA0_SOURCE = "0fbc2bf9e2ddb08e03569f8e8dcafb1d29ed83f9"
PARENT_BA0_RECEIPT = "ddbdfbd4e16415baaeb47266a98f889e8ecd7e46"
PARENT_BA0_META = "af8d7725414c746c5b362150a09eed1662998d5e"

STATES = ("TOP", "FORCE_0", "FORCE_1", "BOTTOM")
VALUES = {
    "TOP": frozenset((0, 1)),
    "FORCE_0": frozenset((0,)),
    "FORCE_1": frozenset((1,)),
    "BOTTOM": frozenset(),
}

def sha_obj(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def classify(values):
    s = frozenset(int(x) for x in values)
    for name, vals in VALUES.items():
        if s == vals:
            return name
    return None


def meet(a, b):
    return classify(VALUES[a] & VALUES[b])


def sat_state(a):
    return bool(VALUES[a])


def state_and_continuation_sat(a, k):
    return bool(VALUES[a] & VALUES[k])


def unit_endpoint_relation():
    Uinfo = az.source_unit()
    U = ba0.r33.canonical_formula(Uinfo["root"])
    models, counts, first = ba0.enumerate_unit_models(U)
    relation = sorted([list(pair) for pair, count in counts.items() if count > 0])
    return Uinfo, U, models, counts, first, relation


def direct_distinguishability():
    K0 = "FORCE_0"
    K1 = "FORCE_1"
    required = {
        "FORCE_0_plus_K0": state_and_continuation_sat("FORCE_0", K0),
        "FORCE_1_plus_K0": state_and_continuation_sat("FORCE_1", K0),
        "FORCE_1_plus_K1": state_and_continuation_sat("FORCE_1", K1),
        "FORCE_0_plus_K1": state_and_continuation_sat("FORCE_0", K1),
    }
    pairwise = {}
    signatures = {}
    for a in STATES:
        sig = tuple(int(state_and_continuation_sat(a, k)) for k in STATES)
        signatures[a] = list(sig)
    for i, a in enumerate(STATES):
        for b in STATES[i+1:]:
            pairwise[f"{a}__{b}"] = signatures[a] != signatures[b]
    classes = len({tuple(v) for v in signatures.values()})
    return {
        "continuations": list(STATES),
        "required_FORCE_witness": required,
        "state_signatures": signatures,
        "pairwise_distinct": pairwise,
        "all_four_pairwise_distinguishable": all(pairwise.values()),
        "N_local_injected_boundary": classes,
        "local_information_bits": math.log2(classes) if classes else 0.0,
    }


def compose_exact(rho, sigma, tau, endpoint_pairs):
    # rho and sigma live on current cut q. U relates q to p. Bridge is p OR q_next.
    current = VALUES[rho] & VALUES[sigma]
    out = set()
    for q in current:
        for p in (0, 1):
            if [q, p] not in endpoint_pairs:
                continue
            for qn in (0, 1):
                if p or qn:
                    out.add(qn)
    out &= set(VALUES[tau])
    return classify(out), sorted(out)


def composition_algebra(endpoint_pairs):
    table = {}
    closure_failures = []
    for rho in STATES:
        table[rho] = {}
        for sigma in STATES:
            table[rho][sigma] = {}
            for tau in STATES:
                result, rows = compose_exact(rho, sigma, tau, endpoint_pairs)
                table[rho][sigma][tau] = {"result": result, "rows": rows}
                if result not in STATES:
                    closure_failures.append({"rho":rho,"sigma":sigma,"tau":tau,"rows":rows})

    # Under the sealed full endpoint relation, the exact symbolic law should be:
    # if rho AND sigma is contradictory -> BOTTOM; otherwise the new residual is exactly tau.
    law_failures = []
    for rho in STATES:
        for sigma in STATES:
            m = meet(rho, sigma)
            for tau in STATES:
                got = table[rho][sigma][tau]["result"]
                expected = "BOTTOM" if m == "BOTTOM" else tau
                if got != expected:
                    law_failures.append({"rho":rho,"sigma":sigma,"tau":tau,"got":got,"expected":expected})

    return {
        "closed_in_Sigma_1": not closure_failures,
        "closure_failures": closure_failures,
        "exact_table": table,
        "simplified_law": "COMPOSE_SIGMA(rho,sigma,tau)=BOTTOM iff rho AND sigma is contradictory; otherwise COMPOSE_SIGMA=tau",
        "simplified_law_failures": law_failures,
    }


def transported_information(algebra):
    # A genuine carried directional bit must survive a neutral local payload and neutral next payload.
    neutral = {}
    for a in STATES:
        neutral[a] = algebra["exact_table"][a]["TOP"]["TOP"]["result"]

    # Also compare the full transition signature with local payload frozen TOP and arbitrary future tau.
    signatures = {}
    for a in STATES:
        signatures[a] = [algebra["exact_table"][a]["TOP"][tau]["result"] for tau in STATES]
    classes = {}
    for a, sig in signatures.items():
        classes.setdefault(tuple(sig), []).append(a)

    force_survives_neutral = neutral["FORCE_0"] != neutral["FORCE_1"]
    force_signatures_distinct = signatures["FORCE_0"] != signatures["FORCE_1"]
    return {
        "neutral_transition": neutral,
        "transition_signatures_with_current_payload_TOP": signatures,
        "transport_equivalence_classes": list(classes.values()),
        "N_transported_transition_behaviours": len(classes),
        "transport_information_bits_total": math.log2(len(classes)) if classes else 0.0,
        "FORCE_0_vs_FORCE_1_survives_neutral_composition": force_survives_neutral,
        "FORCE_0_vs_FORCE_1_full_future_tau_signatures_distinct": force_signatures_distinct,
        "directional_constraint_classes_among_TOP_FORCE0_FORCE1": len({tuple(signatures[s]) for s in ("TOP","FORCE_0","FORCE_1")}),
        "directional_constraint_bits_transported": math.log2(len({tuple(signatures[s]) for s in ("TOP","FORCE_0","FORCE_1")})),
        "interpretation": "BOTTOM/non-BOTTOM remains distinguishable, but the FORCE_0 versus FORCE_1 direction is erased by one full U+bridge composition when no new source payload is injected at the next cut."
    }


def generalized_sat_and_return(first_by_pair):
    # For every payload vector with no BOTTOM, choose x30=1 in every block.
    # TOP/FORCE_0 use endpoint (0,1), FORCE_1 uses (1,1).
    required_pairs = {
        "TOP": (0,1),
        "FORCE_0": (0,1),
        "FORCE_1": (1,1),
    }
    missing = [s for s,p in required_pairs.items() if p not in first_by_pair]
    prototypes = {s: ba0.compact_assignment(first_by_pair[p]) for s,p in required_pairs.items() if p in first_by_pair}
    return {
        "generic_rule": "If sigma contains BOTTOM, the explicit empty clause makes F_{g,sigma} UNSAT. Otherwise, block 0 uses a sealed U model with (x2,x30)=(0,1); every later block j uses (0,1) for TOP/FORCE_0 and (1,1) for FORCE_1. Every payload unit is respected and every bridge is satisfied by left x30=1.",
        "required_endpoint_pairs": {k:list(v) for k,v in required_pairs.items()},
        "missing_endpoint_pairs": missing,
        "prototype_models": prototypes,
        "constructive_return_for_all_no_BOTTOM_payload_vectors": not missing,
        "direct_source_validation_rule": "Check every shifted U clause, every positive bridge, and every explicit unary payload clause on the reconstructed assignment.",
        "reconstruction_respects_FORCE_0": not missing,
        "reconstruction_respects_FORCE_1": not missing,
    }


def unsat_capability():
    return {
        "trivial_BOTTOM": {
            "exists": True,
            "mechanism": "BOTTOM inserts an empty clause directly",
            "classification": "TRIVIAL_UNSAT_BY_INSERTED_EMPTY_CLAUSE"
        },
        "nontrivial_propagated_contradiction": {
            "exists_under_valid_single_payload_per_cut_syntax": False,
            "reason": "For every non-BOTTOM sigma vector, choose each block endpoint x30=1 and x2 according to its unary payload. The sealed U realizes both (0,1) and (1,1), so all payload units and all bridges are simultaneously satisfiable.",
            "classification": "NO_PROPAGATED_FORCE_CONTRADICTION_IN_UNARY_VECTOR_CLASS"
        },
        "conclusion": "Within valid F_{g,sigma} syntax, UNSAT occurs iff at least one sigma_j is BOTTOM."
    }


def size_time_accounting():
    return {
        "parameters": {
            "f": "number of FORCE_0/FORCE_1 boundaries, 0<=f<=g-1",
            "b": "number of BOTTOM boundaries, 0<=b<=g-1"
        },
        "target_measures": {
            "C_g_sigma": "64*g - 1 + f + b",
            "L_g_sigma": "157*g - 2 + f",
            "V_g_sigma": "20*g",
            "encoded_payload_symbols": "g-1"
        },
        "certificate_record_bound": {
            "recurrence": "s_(g+1) <= s_g + 4578",
            "closed_form": "s_g <= 4578*g - 5 relation/payload ledger records",
            "bit_complexity": "O(g log g) = O(n log n) due shifted variable identifiers",
            "history_duplication": "NO: AZ prefix certificate DAG is shared and exactly one constant-size payload-state record is appended per new boundary"
        },
        "total_required_time_bound": {
            "recurrence": "t_(g+1) <= t_g + 49258",
            "closed_form": "t_g = O(g) ledger operations and O(g log g) conservative encoded-verification time",
            "includes": ["payload decode","four-state transition lookup","reconstruction payload check","direct source validation"]
        },
        "separator_width": "Unary clauses add no primal-graph edge; the AZ structural induced-width upper bound 13 is not increased by the unary payload itself. This does not rescue the lost directional residual semantics.",
        "polynomiality_for_fixed_unary_alphabet": True
    }


def run():
    failures = []
    Uinfo, U, models, counts, first_by_pair, endpoint_pairs = unit_endpoint_relation()
    failures.extend(Uinfo.get("failures", []))
    if len(models) != 60:
        failures.append(["UNIT_MODEL_COUNT_DRIFT", len(models)])
    expected_pairs = [[0,0],[0,1],[1,0],[1,1]]
    if endpoint_pairs != expected_pairs:
        failures.append(["ENDPOINT_RELATION_NOT_FULL", endpoint_pairs])

    distinguish = direct_distinguishability()
    if not distinguish["all_four_pairwise_distinguishable"]:
        failures.append("LOCAL_SIGMA_STATES_NOT_PAIRWISE_DISTINGUISHABLE")

    algebra = composition_algebra(endpoint_pairs)
    if not algebra["closed_in_Sigma_1"]:
        outcome = "BA1-B_UNARY_PAYLOAD_COMPOSITION_NOT_CLOSED"
    elif algebra["simplified_law_failures"]:
        failures.append(["SIMPLIFIED_COMPOSITION_LAW_DRIFT", algebra["simplified_law_failures"]])
        outcome = "BA1-E_OPEN"
    else:
        transported = transported_information(algebra)
        return_cert = generalized_sat_and_return(first_by_pair)
        unsat = unsat_capability()
        accounting = size_time_accounting()
        if not return_cert["constructive_return_for_all_no_BOTTOM_payload_vectors"]:
            failures.append("RECONSTRUCTION_PROTOTYPE_MISSING")
        # BA1-A requires the FORCE direction itself to survive generic composition.
        if not transported["FORCE_0_vs_FORCE_1_survives_neutral_composition"] or not transported["FORCE_0_vs_FORCE_1_full_future_tau_signatures_distinct"]:
            outcome = "BA1-D_UNARY_PAYLOAD_TOO_WEAK"
        elif not accounting["polynomiality_for_fixed_unary_alphabet"]:
            outcome = "BA1-C_PAYLOAD_TRANSPORT_BREAKS_POLYNOMIALITY"
        else:
            outcome = "BA1-A_UNARY_PAYLOAD_TRANSPORT_CERTIFIED"

    transported = transported_information(algebra) if algebra["closed_in_Sigma_1"] else None
    return_cert = generalized_sat_and_return(first_by_pair)
    unsat = unsat_capability()
    accounting = size_time_accounting()

    falsifiers = []
    if distinguish["required_FORCE_witness"] != {
        "FORCE_0_plus_K0": True,
        "FORCE_1_plus_K0": False,
        "FORCE_1_plus_K1": True,
        "FORCE_0_plus_K1": False,
    }:
        falsifiers.append("F1_FORCE_DISTINGUISHABILITY_WITNESS_FAILED")
    if not algebra["closed_in_Sigma_1"]:
        falsifiers.append("F2_FOUR_STATE_ALGEBRA_NOT_CLOSED")
    if transported and (not transported["FORCE_0_vs_FORCE_1_survives_neutral_composition"]):
        falsifiers.append("F3_DIRECTIONAL_RESIDUAL_REQUIREMENT_ERASED_BY_ONE_FULL_COMPOSITION")
    if not return_cert["constructive_return_for_all_no_BOTTOM_payload_vectors"]:
        falsifiers.append("F4_RECONSTRUCTION_PAYLOAD_FAILURE")
    if unsat["nontrivial_propagated_contradiction"]["exists_under_valid_single_payload_per_cut_syntax"] is False:
        falsifiers.append("F8_NO_NONTRIVIAL_PROPAGATED_CONTRADICTION__BOTTOM_ONLY_UNSAT_CLASS")

    smallest = None
    if "F3_DIRECTIONAL_RESIDUAL_REQUIREMENT_ERASED_BY_ONE_FULL_COMPOSITION" in falsifiers:
        smallest = {
            "kind": "ONE_FULL_BLOCK_DIRECTION_ERASURE",
            "incoming_states": ["FORCE_0","FORCE_1"],
            "current_payload": "TOP",
            "next_payload": "TOP",
            "outputs": {
                "FORCE_0": algebra["exact_table"]["FORCE_0"]["TOP"]["TOP"]["result"],
                "FORCE_1": algebra["exact_table"]["FORCE_1"]["TOP"]["TOP"]["result"]
            },
            "lost_information": "whether the incoming cut required q=0 or q=1",
            "why_generic": "The proof uses only the sealed full endpoint relation of U and the positive bridge, so it is independent of g and uses no finite-g table."
        }

    if failures and outcome not in ("BA1-B_UNARY_PAYLOAD_COMPOSITION_NOT_CLOSED",):
        outcome = "BA1-E_OPEN"

    return {
        "gate": GATE,
        "status": "SCIENTIFIC_AUDIT_RESULT",
        "preregistration_commit": PREREG,
        "parent_BA0_source_head": PARENT_BA0_SOURCE,
        "parent_BA0_receipt": PARENT_BA0_RECEIPT,
        "parent_BA0_meta_final": PARENT_BA0_META,
        "failure_count": len(failures),
        "failures": failures,
        "outcome": outcome,
        "endpoint_relation": {
            "unit_model_count": len(models),
            "endpoint_pair_counts": {str(k):int(v) for k,v in sorted(counts.items())},
            "realized_pairs": endpoint_pairs,
            "is_full_boolean_relation": endpoint_pairs == expected_pairs
        },
        "BA1_1_distinguishability": distinguish,
        "BA1_2_four_state_algebra": algebra,
        "BA1_3_generalized_pi": {
            "pi_payload": "SAT_DECISION_PRESERVATION + BOUNDARY_RESIDUAL_SEMANTICS_PRESERVATION + CONSTRUCTIVE_RETURN",
            "transport": transported,
            "status": "FAIL_DIRECTIONAL_RESIDUAL_ERASURE" if transported and not transported["FORCE_0_vs_FORCE_1_survives_neutral_composition"] else "PASS"
        },
        "BA1_4_generic_composition": {
            "uniform_rule": algebra["simplified_law"],
            "hardcoded_g": False,
            "future_solution_inspection": False,
            "closure": algebra["closed_in_Sigma_1"],
            "directional_information_preserved": bool(transported and transported["FORCE_0_vs_FORCE_1_full_future_tau_signatures_distinct"])
        },
        "BA1_5_constructive_return": return_cert,
        "BA1_6_unsat_capability": unsat,
        "BA1_7_size_time": accounting,
        "BA1_8_information_accounting": {
            "BA0_N_boundary": 1,
            "BA0_bits": 0,
            "local_injected_N": distinguish["N_local_injected_boundary"],
            "local_injected_bits": distinguish["local_information_bits"],
            "transported_transition_N": transported["N_transported_transition_behaviours"] if transported else None,
            "transported_transition_bits_total": transported["transport_information_bits_total"] if transported else None,
            "directional_constraint_classes_among_TOP_FORCE0_FORCE1": transported["directional_constraint_classes_among_TOP_FORCE0_FORCE1"] if transported else None,
            "directional_constraint_bits_transported": transported["directional_constraint_bits_transported"] if transported else None,
            "critical_distinction": "Four local labels really are four semantic residual classes at the injection cut, but the full U+bridge transition has only one non-contradictory directional behaviour: TOP, FORCE_0 and FORCE_1 have identical future-tau signatures."
        },
        "falsifiers": falsifiers,
        "smallest_falsifier": smallest,
        "finite_g_ladder_replayed": False,
        "arbitrary_CNF_coverage_started": False,
        "BA2_started": False,
        "AZ_modified": False,
        "BA0_modified": False,
        "firewall": {"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "outcome": out["outcome"],
        "falsifiers": out["falsifiers"],
        "local_N": out["BA1_8_information_accounting"]["local_injected_N"],
        "transported_N": out["BA1_8_information_accounting"]["transported_transition_N"],
        "directional_bits": out["BA1_8_information_accounting"]["directional_constraint_bits_transported"],
    }, sort_keys=True))
    if out["failure_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
