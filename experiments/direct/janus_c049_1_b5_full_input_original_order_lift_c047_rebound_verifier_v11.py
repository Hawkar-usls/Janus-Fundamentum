from __future__ import annotations

import copy

import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier as base

verify = base.verify
load = base.load
dg = base.dg
cb = base.cb


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(subject: dict, spec: dict, prep_spec: dict, b51_spec: dict, b52a_spec: dict, b52b_spec: dict) -> tuple[int, int]:
    attacks: list[tuple[str, dict]] = []

    def add(name: str, mutation) -> None:
        candidate = copy.deepcopy(subject["candidate"])
        before = cb(candidate)
        mutation(candidate["proof_payload"])
        repair(candidate)
        if cb(candidate) == before:
            raise AssertionError(name + " is a no-op")
        attacks.append((name, candidate))

    add("T01_PREPROCESSING_SUBJECT_DIGEST", lambda p: p.__setitem__("preprocessing_semantic_digest", "0" * 64))
    add("T02_ORIGINAL_FACTOR_ID", lambda p: p["original_layout_records"][0].__setitem__("factor_id", "__fake__"))
    add("T03_ORIGINAL_NORMAL_SPACE", lambda p: p["original_layout_records"][0].__setitem__("normal_space", []))
    add("T04_ORIGINAL_AFFINE_OFFSET", lambda p: p["original_layout_records"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T05_REDUCED_B5_2B_SUBJECT_DIGEST", lambda p: p.__setitem__("reduced_b5_2b_semantic_digest", "0" * 64))
    add("T06_REDUCED_ORDER_DUPLICATE", lambda p: p["factor_order_ids"].__setitem__(-1, p["factor_order_ids"][0]))
    add("T07_REDUCED_ORDER_OMISSION", lambda p: p["factor_order_ids"].pop())
    add("T08_REDUCED_ORDER_UNKNOWN_FACTOR", lambda p: p["factor_order_ids"].__setitem__(0, "__unknown__"))
    add("T09_ORIGINAL_ORDER_REORDERED_AFTER_B5_2B", lambda p: p["factor_order_ids"].__setitem__(slice(0, 2), list(reversed(p["factor_order_ids"][:2]))))
    add("T10_ORIGINAL_CUT_WIDTH", lambda p: p["original_layout_replay"]["cut_widths"].__setitem__(1, 999))
    add("T11_ORIGINAL_CUT_BASIS", lambda p: p["original_layout_replay"]["cut_bases"].__setitem__(1, [999]))
    add("T12_REDUCED_ORIGINAL_CUT_BRIDGE", lambda p: p["reduced_to_original_cut_bridge"][1].__setitem__("width", 999))
    add("T13_ORIGINAL_MAX_WIDTH_GT_K_ACCEPTED", lambda p: p["original_layout_replay"].__setitem__("maximum_width", 999))
    add("T14_PHASE_A_NUMERIC_ID_COLLISION", lambda p: p["phase_a_factor_bijection"][1].__setitem__("phase_a_input_position", 0))
    add("T15_PHASE_A_ORDER_POSITION", lambda p: p["phase_a_order_positions"].__setitem__(0, 999))
    add("T16_AFFINE_BETA", lambda p: p["phase_a_factors"][0]["equations"][0].__setitem__(1, 1 - p["phase_a_factors"][0]["equations"][0][1]))
    add("T17_AFFINE_MASK", lambda p: p["phase_a_factors"][0]["equations"][0].__setitem__(0, 0 if p["phase_a_factors"][0]["equations"][0][0] != 0 else 1))
    add("T18_PHASE_A_TRANSCRIPT", lambda p: p["phase_a_transcript"]["order"].__setitem__(0, 999))
    add("T19_C047_RESULT_DISAGREEMENT", lambda p: p.__setitem__("c047_result", "UNSAT" if p["c047_result"] == "SAT" else "SAT"))
    add("T20_HISTORICAL_CERTIFICATE_TERMINAL_FLIP", lambda p: p["phase_a_certificate"].__setitem__("status", "UNSAT" if p["phase_a_certificate"]["status"] == "SAT" else "SAT"))
    add("T21_HISTORICAL_VERIFIER_PASS_FLAG", lambda p: p.__setitem__("historical_phase_a_verifier_pass", False))
    add("T22_DIRECT_REDUCED_B5_4_PROMOTION", lambda p: p["authority_policy"].__setitem__("direct_b5_4_on_reduced_catalog", True))
    add("T23_STRICT_PREFIX_PROMOTION", lambda p: p["authority_policy"].__setitem__("strict_prefix_c047", True))
    add("T24_B5_3_NO_LAYOUT_TO_C047_UNSAT", lambda p: p["authority_policy"].__setitem__("b5_3_no_layout_used_as_c047_unsat_premise", True))
    add("T25_ORIGINAL_ORDER_LIFT_WITHOUT_PREPROCESSING_EQUIVALENCE", lambda p: p["authority_policy"].__setitem__("original_geometry_required_for_final_width_and_affine_rebound", False))
    add("T26_ALL_INPUT_TERMINATION_PROMOTION", lambda p: p["strict_boundary"].__setitem__("all_input_termination", "ESTABLISHED"))
    add("T27_POLYNOMIAL_RUNTIME_PROMOTION", lambda p: p["strict_boundary"].__setitem__("polynomial_runtime", "ESTABLISHED"))
    add("T28_B5_COMPLETE_PROMOTION", lambda p: p["strict_boundary"].__setitem__("b5_complete", True))
    add("T29_P_VS_NP_PROMOTION", lambda p: p["strict_boundary"].__setitem__("p_vs_np", "CLOSED"))

    rejected = 0
    for name, candidate in attacks:
        try:
            verify(
                candidate,
                spec,
                subject["raw_original"],
                subject["preprocessing"],
                subject["reduced_raw"],
                subject["b51"],
                subject["carrier"],
                subject["b52"],
                prep_spec,
                b51_spec,
                b52a_spec,
                b52b_spec,
                subject["caps"],
            )
        except Exception:
            rejected += 1
            print(name + " = REJECTED")
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)
