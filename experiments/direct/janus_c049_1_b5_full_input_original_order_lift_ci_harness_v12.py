from __future__ import annotations

import sys

import janus_c049_1_b5_full_input_original_order_lift_ci_harness_v11 as h


def build_chain_v12(name: str, original: dict):
    raw = h.TMP / f"{name}.original.json"
    pre = h.TMP / f"{name}.pre.json"
    reduced = h.TMP / f"{name}.reduced.json"
    b51 = h.TMP / f"{name}.b51.json"
    carrier = h.TMP / f"{name}.carrier.json"
    b52 = h.TMP / f"{name}.b52.json"
    lift = h.TMP / f"{name}.lift.json"
    h.write(raw, original)

    h.run([sys.executable, str(h.PRE_PRODUCER), "--spec", str(h.PRE_SPEC), "--input", str(raw), "--output", str(pre)], h.TMP / f"{name}.pre.log")
    h.run([sys.executable, str(h.PRE_VERIFIER), "--spec", str(h.PRE_SPEC), "--input", str(raw), "--candidate", str(pre)], h.TMP / f"{name}.prev.log")
    pre_obj = h.load(pre)
    if pre_obj["proof_payload"]["preprocessing_branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        raise AssertionError(name + " did not reach positive preprocessing branch")
    h.write(reduced, h.make_reduced_raw(original, pre_obj))

    h.run([sys.executable, str(h.B51_PRODUCER), "--spec", str(h.B51_SPEC), "--input", str(reduced), "--output", str(b51)], h.TMP / f"{name}.b51.log")
    b51log = h.run([sys.executable, str(h.B51_VERIFIER), "--spec", str(h.B51_SPEC), "--input", str(reduced), "--candidate", str(b51)], h.TMP / f"{name}.b51v.log")
    if "RUNTIME_RESULT = CLOSED_COMPLETE_TRACE" not in b51log:
        raise AssertionError(name + " B5.1 not independently verified CLOSED")

    h.run([sys.executable, str(h.B52A_PRODUCER), "--spec", str(h.B52A_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--output", str(carrier)], h.TMP / f"{name}.carrier.log")
    cverify = h.run([sys.executable, str(h.B52A_VERIFIER), "--spec", str(h.B52A_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--candidate", str(carrier)], h.TMP / f"{name}.carrierv.log")
    if "JANUS_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_V1_1_INDEPENDENT_VERIFIER = PASS" not in cverify:
        raise AssertionError(name + " B5.2A verify")

    h.run([sys.executable, str(h.B52B_PRODUCER), "--spec", str(h.B52B_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--output", str(b52)], h.TMP / f"{name}.b52.log")
    b52verify = h.run([sys.executable, str(h.B52B_VERIFIER), "--spec", str(h.B52B_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--candidate", str(b52)], h.TMP / f"{name}.b52v.log")
    if "JANUS_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_INDEPENDENT_VERIFIER_V1_1 = PASS" not in b52verify:
        raise AssertionError(name + " B5.2B verify")

    h.run([sys.executable, str(h.PRODUCER), "--spec", str(h.SPEC), "--original-input", str(raw), "--preprocessing", str(pre), "--reduced-input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--b5-2b-artifact", str(b52), "--output", str(lift)], h.TMP / f"{name}.lift.log")
    lverify = h.run([
        sys.executable, str(h.VERIFIER), "--spec", str(h.SPEC), "--preprocessing-spec", str(h.PRE_SPEC), "--b5-1-spec", str(h.B51_SPEC), "--b5-2a-spec", str(h.B52A_SPEC), "--b5-2b-spec", str(h.B52B_SPEC),
        "--original-input", str(raw), "--preprocessing", str(pre), "--reduced-input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--b5-2b-artifact", str(b52), "--candidate", str(lift)
    ], h.TMP / f"{name}.liftv.log")
    if "JANUS_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_INDEPENDENT_VERIFIER = PASS" not in lverify:
        raise AssertionError(name + " lift verify")
    return {"raw": raw, "pre": pre, "reduced": reduced, "b51": b51, "carrier": carrier, "b52": b52, "lift": lift}


def main() -> None:
    h.build_chain = build_chain_v12
    h.main()


if __name__ == "__main__":
    main()
