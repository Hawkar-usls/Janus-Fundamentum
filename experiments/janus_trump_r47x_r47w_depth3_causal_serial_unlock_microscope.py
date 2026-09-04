from __future__ import annotations

import hashlib
import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47k_extended_normalization_closure_one_swap_falsifier as r47k
import janus_trump_r47r_targeted_two_swap_depth2_rescue_disruption as r47r
import janus_trump_r47w_fixed_depth3_rescue_or_certified_lower_bound as r47w

EXPECTED_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_CLV = (76, 203, 22)
EXPECTED_DEPTH2_COUNT = 462
EXPECTED_DEPTH2_LEDGER_HASH = "72416db56bcff832efed776c902e8d2e158cc706139bfac44e6c5366ab8340ed"
TARGET = (11, 12, 15)


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def canonical_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def clause_key(clause):
    return tuple(sorted((int(x) for x in clause), key=lambda x: (abs(x), x)))


def pivot_skeleton(formula, pivot):
    f = r33.canonical_formula(formula)
    v = int(pivot)
    pos = sorted((clause_key(c) for c in f if v in c))
    neg = sorted((clause_key(c) for c in f if -v in c))
    background = sorted((clause_key(c) for c in f if v not in c and -v not in c))
    resolvents = set()
    tautological_pairs = 0
    for p in pos:
        for n in neg:
            merged = (set(p) - {v}) | (set(n) - {-v})
            if any(-lit in merged for lit in merged):
                tautological_pairs += 1
                continue
            resolvents.add(clause_key(merged))
    resolvents_sorted = sorted(resolvents)
    return {
        "pivot": v,
        "formula_CLV": list(clv(f)),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "parent_pair_product": len(pos) * len(neg),
        "positive_parents_sha256": canonical_hash(pos),
        "negative_parents_sha256": canonical_hash(neg),
        "parent_union_sha256": canonical_hash([pos, neg]),
        "distinct_nontaut_resolvent_count": len(resolvents_sorted),
        "resolvents_sha256": canonical_hash(resolvents_sorted),
        "tautological_parent_pair_count": tautological_pairs,
        "background_clause_count": len(background),
        "background_sha256": canonical_hash(background),
    }


def skeleton_delta(a, b):
    return {
        "parents_equal": a["parent_union_sha256"] == b["parent_union_sha256"],
        "resolvents_equal": a["resolvents_sha256"] == b["resolvents_sha256"],
        "background_equal": a["background_sha256"] == b["background_sha256"],
        "positive_parent_delta": b["positive_parent_count"] - a["positive_parent_count"],
        "negative_parent_delta": b["negative_parent_count"] - a["negative_parent_count"],
        "resolvent_count_delta": b["distinct_nontaut_resolvent_count"] - a["distinct_nontaut_resolvent_count"],
        "background_clause_delta": b["background_clause_count"] - a["background_clause_count"],
    }


def apply_sequence(original, sequence):
    base = r33.canonical_formula(original)
    base_clv = clv(base)
    state = base
    layers = []
    for index, pivot in enumerate(sequence, start=1):
        candidate = r47j.macro_candidate_fixpoint(state, int(pivot))
        if candidate is None:
            return {
                "sequence": [int(v) for v in sequence],
                "exists": False,
                "missing_at_layer": index,
                "accepted_relative_to_F0": False,
                "layers": layers,
                "final_formula": state,
                "final_CLV": list(clv(state)),
            }
        replay = r47j.independent_fixpoint_macro_replay(state, candidate)
        if not replay["pass"]:
            raise AssertionError(("R47X_INDEPENDENT_REPLAY_FAIL", tuple(sequence), index, pivot, replay))
        next_state = r33.canonical_formula(candidate["normalization"]["final_formula"])
        layer = {
            "index": index,
            "pivot": int(pivot),
            "input_CLV": list(clv(state)),
            "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
            "final_CLV": list(clv(next_state)),
            "terminal": candidate["normalization"]["terminal"],
            "restart_count": int(candidate["normalization"]["restart_count"]),
            "round_count": int(candidate["normalization"]["round_count"]),
            "independent_replay_pass": True,
        }
        layers.append(layer)
        state = next_state
    accepted = bool(layers and (layers[-1]["terminal"] is not None or clv(state) < base_clv))
    return {
        "sequence": [int(v) for v in sequence],
        "exists": True,
        "accepted_relative_to_F0": accepted,
        "layers": layers,
        "final_formula": state,
        "final_CLV": list(clv(state)),
    }


def public_sequence_receipt(row):
    return {k: v for k, v in row.items() if k != "final_formula"}


def run():
    parent, original = r47w.load_witness()
    if r47w.r47f.formula_hash(original) != EXPECTED_HASH or clv(original) != EXPECTED_CLV:
        raise AssertionError("R47X_WITNESS_DRIFT")

    depth1 = r47k.first_extended_accept(original)
    if depth1["covered"]:
        raise AssertionError(("R47X_DEPTH1_DRIFT", depth1["selected_var"]))
    depth2 = r47r.depth2_scan(original, keep_all_failures=True)
    if depth2["covered"]:
        raise AssertionError(("R47X_DEPTH2_DRIFT", depth2["selected_pair"]))
    failures = depth2["all_failures"]
    if len(failures) != EXPECTED_DEPTH2_COUNT:
        raise AssertionError(("R47X_DEPTH2_COUNT_DRIFT", len(failures)))
    if canonical_hash(failures) != EXPECTED_DEPTH2_LEDGER_HASH:
        raise AssertionError("R47X_DEPTH2_LEDGER_DRIFT")

    seq_15 = apply_sequence(original, (15,))
    seq_11_15 = apply_sequence(original, (11, 15))
    seq_12_15 = apply_sequence(original, (12, 15))
    seq_11_12 = apply_sequence(original, (11, 12))
    seq_12_11 = apply_sequence(original, (12, 11))
    seq_target = apply_sequence(original, TARGET)
    seq_reverse = apply_sequence(original, (12, 11, 15))

    if seq_15["accepted_relative_to_F0"] or seq_11_15["accepted_relative_to_F0"] or seq_12_15["accepted_relative_to_F0"]:
        raise AssertionError("R47X_SHORT_TARGET_BYPASS_DRIFT")
    if not seq_target["accepted_relative_to_F0"]:
        raise AssertionError("R47X_TARGET_TRIPLE_NO_LONGER_ACCEPTED")
    if tuple(seq_target["final_CLV"]) != (75, 206, 19):
        raise AssertionError(("R47X_TARGET_FINAL_CLV_DRIFT", seq_target["final_CLV"]))

    f0 = r33.canonical_formula(original)
    g11 = r33.canonical_formula(apply_sequence(original, (11,))["final_formula"])
    g12 = r33.canonical_formula(apply_sequence(original, (12,))["final_formula"])
    g11_12 = r33.canonical_formula(seq_11_12["final_formula"])
    g12_11 = r33.canonical_formula(seq_12_11["final_formula"])

    s12_f0 = pivot_skeleton(f0, 12)
    s12_g11 = pivot_skeleton(g11, 12)
    s15_f0 = pivot_skeleton(f0, 15)
    s15_g11 = pivot_skeleton(g11, 15)
    s15_g12 = pivot_skeleton(g12, 15)
    s15_g11_12 = pivot_skeleton(g11_12, 15)
    s15_g12_11 = pivot_skeleton(g12_11, 15)

    stage12_delta = skeleton_delta(s12_f0, s12_g11)
    target_deltas = {
        "F0_to_after_11": skeleton_delta(s15_f0, s15_g11),
        "F0_to_after_12": skeleton_delta(s15_f0, s15_g12),
        "F0_to_after_11_12": skeleton_delta(s15_f0, s15_g11_12),
        "after_11_to_after_11_12": skeleton_delta(s15_g11, s15_g11_12),
        "F0_to_after_12_11": skeleton_delta(s15_f0, s15_g12_11),
    }

    stage12_context_only = stage12_delta["parents_equal"] and stage12_delta["resolvents_equal"]
    target_context_only = all(
        target_deltas[key]["parents_equal"] and target_deltas[key]["resolvents_equal"]
        for key in ("F0_to_after_11", "F0_to_after_12", "F0_to_after_11_12")
    )
    order_sensitive = not seq_reverse["accepted_relative_to_F0"]

    causal_prerequisites = (
        not seq_15["accepted_relative_to_F0"]
        and not seq_11_15["accepted_relative_to_F0"]
        and not seq_12_15["accepted_relative_to_F0"]
        and seq_target["accepted_relative_to_F0"]
    )
    if not causal_prerequisites:
        classification = "STRUCTURAL_SHORTCUT_OR_CAUSAL_MODEL_MISMATCH"
    elif stage12_context_only and target_context_only:
        classification = (
            "CONTEXT_ONLY_ORDER_SENSITIVE_SERIAL_UNLOCK"
            if order_sensitive
            else "CONTEXT_ONLY_ORDER_INSENSITIVE_DEPTH3_UNLOCK"
        )
    elif (not stage12_context_only) and (not target_context_only):
        classification = (
            "LOCAL_SKELETON_MEDIATED_ORDER_SENSITIVE_SERIAL_UNLOCK"
            if order_sensitive
            else "LOCAL_SKELETON_MEDIATED_ORDER_INSENSITIVE_DEPTH3_UNLOCK"
        )
    else:
        classification = "MIXED_CONTEXT_AND_SKELETON_SERIAL_UNLOCK"

    out = {
        "gate": "JANUS_TRUMP_R47X_R47W_DEPTH3_CAUSAL_SERIAL_UNLOCK_MICROSCOPE",
        "parent_commit": "5163b3e0e1080a423a5dd6b96c0ab5e80760aa81",
        "R47U_theorem_context_commit": "b7d056cbe67903fa35014232aff8bb4feea8b931",
        "input_hash": EXPECTED_HASH,
        "input_CLV": list(EXPECTED_CLV),
        "sealed_depth_statement": "d(F)=3_FOR_THIS_FINITE_REACHABLE_WITNESS",
        "depth1_reconfirmed_dead": True,
        "depth2_reconfirmed_dead": True,
        "depth2_failed_pair_count": len(failures),
        "depth2_failed_pair_ledger_sha256": canonical_hash(failures),
        "causal_key": {
            "pivot15_alone_accepted": seq_15["accepted_relative_to_F0"],
            "11_then_15_accepted": seq_11_15["accepted_relative_to_F0"],
            "12_then_15_accepted": seq_12_15["accepted_relative_to_F0"],
            "11_then_12_then_15_accepted": seq_target["accepted_relative_to_F0"],
            "12_then_11_then_15_accepted": seq_reverse["accepted_relative_to_F0"],
            "target_requires_two_layer_prefix_against_single_key_controls": causal_prerequisites,
            "prefix_order_sensitive_for_pivot15": order_sensitive,
        },
        "sequence_receipts": {
            "15": public_sequence_receipt(seq_15),
            "11_15": public_sequence_receipt(seq_11_15),
            "12_15": public_sequence_receipt(seq_12_15),
            "11_12": public_sequence_receipt(seq_11_12),
            "12_11": public_sequence_receipt(seq_12_11),
            "11_12_15": public_sequence_receipt(seq_target),
            "12_11_15": public_sequence_receipt(seq_reverse),
        },
        "pivot12_stage_delta_after_11": stage12_delta,
        "pivot15_skeletons": {
            "F0": s15_f0,
            "after_11": s15_g11,
            "after_12": s15_g12,
            "after_11_12": s15_g11_12,
            "after_12_11": s15_g12_11,
        },
        "pivot15_deltas": target_deltas,
        "stage12_context_only": stage12_context_only,
        "pivot15_context_only_through_target_prefix": target_context_only,
        "classification": classification,
        "interpretation": {
            "finite_result_only": True,
            "serial_family_constructed": False,
            "universal_fixed_K_proved": False,
            "next_if_serial_signal": "SYNTHESIZE_COUPLED_3_STAGE_GADGET_FROM_MEASURED_INTERFACE_DELTAS_AND_TEST_BYPASS_RESISTANCE",
            "next_if_skeleton_or_mixed": "ISOLATE_MINIMAL_PARENT_RESOLVENT_OR_BACKGROUND_DELTA_NEEDED_FOR_THIRD_STAGE_ACCEPTANCE",
            "next_if_order_insensitive": "SEARCH_FOR_COMMUTING_UNLOCK_EQUIVALENCE_AND_CAUSAL_DIAMETER_COLLAPSE",
        },
        "firewall": {
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
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
