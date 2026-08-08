from __future__ import annotations

import argparse
import copy
from pathlib import Path

import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier as basev


def nontrivial_lift(payload: dict, stage: str) -> dict:
    matches = [
        cert for cert in payload["paper_faithful_lift_certificates"]
        if cert["stage"] == stage
        and "compactification_lift" in cert
        and cert["compactification_lift"]["compactification_trace"]
        and cert["lower_trajectory_digest"] != cert["compactification_lift"]["runtime_compact_source_digest"]
    ]
    if not matches:
        raise AssertionError("INSUFFICIENT_TAMPER_FIXTURE_NO_NONTRIVIAL_" + stage)
    return matches[0]


def hardened_tamper_suite(
    nonempty: dict,
    empty: dict,
    spec: dict,
    nonempty_subject: tuple[dict, dict, dict],
    empty_subject: tuple[dict, dict, dict],
) -> tuple[int, int]:
    attacks: list[tuple[str, dict, tuple[dict, dict, dict]]] = []

    def add(name: str, source: dict, subject: tuple[dict, dict, dict], mutation) -> None:
        candidate = copy.deepcopy(source)
        mutation(candidate["proof_payload"])
        attacks.append((name, basev.repair(candidate), subject))

    def cert_by_stage(payload: dict, stage: str) -> dict:
        return next(x for x in payload["paper_faithful_lift_certificates"] if x["stage"] == stage)

    def first_event(payload: dict, kind: str) -> dict:
        return next(x for x in payload["printorder_event_trace"] if x["kind"] == kind)

    # Prove before generating the attacks that the compactification fixtures are
    # semantically nontrivial.  A no-op mutation is a harness failure, not a rejection.
    nontrivial_lift(nonempty["proof_payload"], "FINAL_UP_FROM_PAPER_SHRINK")
    nontrivial_lift(nonempty["proof_payload"], "JOINED_UP_FROM_RAW_HV_JOIN")

    add("T01_NONMIN_ROOT", nonempty, nonempty_subject, lambda p: p.__setitem__("selected_root_entry_index", 1 if p["selected_root_entry_index"] == 0 else 0))
    add("T02_ROOT_TIE_BREAK", nonempty, nonempty_subject, lambda p: p["root_selection_key"].__setitem__(1, "0" * 64))
    add("T03_FINAL_LIFT_WITNESS", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "FINAL_UP_FROM_PAPER_SHRINK")["extension_preorder_witness"]["path"].__setitem__(0, [999, 999]))
    add("T04_FINAL_X", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "FINAL_UP_FROM_PAPER_SHRINK")["algorithm2_x_sequence_zero_based"].__setitem__(0, 999))

    def t05(payload: dict) -> None:
        cert = nontrivial_lift(payload, "FINAL_UP_FROM_PAPER_SHRINK")
        replacement = cert["compactification_lift"]["runtime_compact_source_digest"]
        if replacement == cert["lower_trajectory_digest"]:
            raise AssertionError("T05_NOOP")
        cert["lower_trajectory_digest"] = replacement
    add("T05_COMPACT_SHRINK_AS_PAPER_NODE", nonempty, nonempty_subject, t05)

    add("T06_SHRINK_INDEX", nonempty, nonempty_subject, lambda p: first_event(p, "SHRINK_IDENTITY_DISPATCH").__setitem__("joined_child_interval", 999))
    add("T07_JOIN_LIFT_WITNESS", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "JOINED_UP_FROM_RAW_HV_JOIN")["extension_preorder_witness"]["path"].__setitem__(0, [999, 999]))
    add("T08_JOIN_X", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "JOINED_UP_FROM_RAW_HV_JOIN")["algorithm2_x_sequence_zero_based"].__setitem__(0, 999))

    def t09(payload: dict) -> None:
        cert = nontrivial_lift(payload, "JOINED_UP_FROM_RAW_HV_JOIN")
        replacement = cert["compactification_lift"]["runtime_compact_source_digest"]
        if replacement == cert["lower_trajectory_digest"]:
            raise AssertionError("T09_NOOP")
        cert["lower_trajectory_digest"] = replacement
    add("T09_COMPACT_JOIN_AS_HV_NODE", nonempty, nonempty_subject, t09)

    dispatch_kind = "JOIN_DISPATCH_LEFT" if any(e["kind"] == "JOIN_DISPATCH_LEFT" for e in nonempty["proof_payload"]["printorder_event_trace"]) else "JOIN_DISPATCH_RIGHT"
    reverse_kind = "JOIN_DISPATCH_RIGHT" if dispatch_kind == "JOIN_DISPATCH_LEFT" else "JOIN_DISPATCH_LEFT"
    add("T10_DIAGONAL_JOIN_DISPATCH", nonempty, nonempty_subject, lambda p: first_event(p, dispatch_kind).__setitem__("kind", "JOIN_DISPATCH_DIAGONAL"))
    add("T11_REVERSE_JOIN_DISPATCH", nonempty, nonempty_subject, lambda p: first_event(p, dispatch_kind).__setitem__("kind", reverse_kind))
    add("T12_EXPANDED_X", nonempty, nonempty_subject, lambda p: next(x for x in p["paper_faithful_lift_certificates"] if "EXPANDED_CHILD_UP" in x["stage"])["algorithm2_x_sequence_zero_based"].__setitem__(0, 999))
    add("T13_CHILD_ANCESTRY", nonempty, nonempty_subject, lambda p: first_event(p, "TRANSPORT_IDENTITY_DISPATCH").__setitem__("child_output_interval", 999))
    add("T14_DUPLICATE_FACTOR", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].__setitem__(-1, p["factor_order_ids"][0]))
    add("T15_OMIT_FACTOR", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].pop())
    add("T16_UNKNOWN_FACTOR", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].__setitem__(0, "__unknown_factor__"))
    add("T17_SPLIT_REPLACE_FACTOR", nonempty, nonempty_subject, lambda p: p["layout_records"][0].__setitem__("normal_space", []))
    add("T18_AFFINE_OFFSET", nonempty, nonempty_subject, lambda p: p["layout_records"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T19_CUT_BOUNDARY", nonempty, nonempty_subject, lambda p: p["cut_certificates"][1].__setitem__("boundary_rref", [999]))
    add("T20_MAX_WIDTH", nonempty, nonempty_subject, lambda p: p.__setitem__("maximum_cut_width", 0 if p["maximum_cut_width"] != 0 else 999))
    add("T21_ORDER_REPLAY", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].__setitem__(slice(0, 2), list(reversed(p["factor_order_ids"][:2]))))
    add("T22_EMPTY_ROOT_FAKE_ORDER", empty, empty_subject, lambda p: p.update({"factor_order_ids": ["fake"], "layout_records": [{"factor_id": "fake"}], "candidate_found_layout": True}))
    add("T23_PREMATURE_FOUND_LAYOUT", nonempty, nonempty_subject, lambda p: p.__setitem__("found_layout_promotion", "TRUE"))
    add("T24_GLOBAL_PROMOTION", nonempty, nonempty_subject, lambda p: p["strict_boundary"].update({"generic_no_layout_at_cap": "TRUE", "polynomial_runtime": "TRUE", "b5_complete": True, "p_vs_np": "CLOSED"}))

    rejected = 0
    for name, candidate, subject in attacks:
        raw, b5, carrier = subject
        try:
            basev.verify(candidate, spec, raw, b5, carrier)
        except Exception:
            rejected += 1
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--carrier", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--tamper-suite", action="store_true")
    parser.add_argument("--empty-input", type=Path)
    parser.add_argument("--empty-b5-1-artifact", type=Path)
    parser.add_argument("--empty-carrier", type=Path)
    parser.add_argument("--empty-candidate", type=Path)
    args = parser.parse_args()

    spec = basev.load(args.spec)
    raw = basev.load(args.input)
    b5 = basev.load(args.b5_1_artifact)
    carrier = basev.load(args.carrier)
    candidate = basev.load(args.candidate)
    expected = basev.verify(candidate, spec, raw, b5, carrier)

    print("JANUS_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_INDEPENDENT_VERIFIER_V1_1 = PASS")
    print("RECONSTRUCTION_STATUS =", "NOT_APPLICABLE_EMPTY_ROOT" if expected["empty"] else "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW")
    print("INDEPENDENT_ROOT_SELECTION = PASS")
    print("PAPER_RAW_JOIN_LIFT = PASS")
    print("PAPER_PRECOMPACT_SHRINK_LIFT = PASS")
    print("ALGORITHM2_X_SEQUENCE_REPLAY = PASS")
    print("B5_2A_SLACK_METADATA_USED_BY_PRINTORDER = FALSE")
    print("INDEPENDENT_PRINTORDER_REPLAY = PASS")
    print("WHOLE_FACTOR_PERMUTATION =", "N/A_EMPTY_ROOT" if expected["empty"] else "PASS")
    print("INDEPENDENT_CUT_WIDTH_RECOMPUTATION =", "N/A_EMPTY_ROOT" if expected["empty"] else "PASS")
    print("MAXIMUM_CUT_WIDTH =", expected["max_width"])
    print("NONTRIVIAL_COMPACTIFICATION_TAMPER_FIXTURES = REQUIRED")
    print("GENERIC_FOUND_LAYOUT = FORBIDDEN_PENDING_REVIEW")
    print("GENERIC_NO_LAYOUT_AT_CAP = FORBIDDEN_PENDING_B5_3")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")

    if args.tamper_suite:
        required = [args.empty_input, args.empty_b5_1_artifact, args.empty_carrier, args.empty_candidate]
        if any(x is None for x in required):
            raise AssertionError("tamper suite requires empty-root subject")
        empty_subject = (
            basev.load(args.empty_input),
            basev.load(args.empty_b5_1_artifact),
            basev.load(args.empty_carrier),
        )
        rejected, total = hardened_tamper_suite(
            candidate,
            basev.load(args.empty_candidate),
            spec,
            (raw, b5, carrier),
            empty_subject,
        )
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
