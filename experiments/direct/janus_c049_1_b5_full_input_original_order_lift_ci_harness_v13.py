from __future__ import annotations

import time

import janus_c049_1_b5_full_input_original_order_lift_ci_harness_v11 as h
import janus_c049_1_b5_full_input_original_order_lift_ci_harness_v12 as h12
import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier_v11 as liftv11
import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier_v12 as liftv12


def timed_run(args, log=None):
    label = args[1] if len(args) > 1 else args[0]
    started = time.monotonic()
    print(f"V1_3_SUBPROCESS_START = {label}", flush=True)
    out = ORIGINAL_RUN(args, log)
    print(f"V1_3_SUBPROCESS_SECONDS = {time.monotonic() - started:.3f} :: {label}", flush=True)
    return out


def tamper_strict_shrink_v13(files):
    subject = {
        "raw_original": h.load(files["raw"]),
        "preprocessing": h.load(files["pre"]),
        "reduced_raw": h.load(files["reduced"]),
        "b51": h.load(files["b51"]),
        "carrier": h.load(files["carrier"]),
        "b52": h.load(files["b52"]),
        "candidate": h.load(files["lift"]),
        "caps": {
            "discovery_cap": None,
            "work_cap": None,
            "certificate_cap": None,
            "trellis_work_cap": None,
            "trellis_certificate_cap": None,
        },
    }
    spec = h.load(h.SPEC)
    prep_spec = h.load(h.PRE_SPEC)
    b51_spec = h.load(h.B51_SPEC)
    b52a_spec = h.load(h.B52A_SPEC)
    b52b_spec = h.load(h.B52B_SPEC)

    baseline = liftv12.verify(
        subject["candidate"],
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
    print("V1_2_FAIL_FAST_WRAPPER_VALID_DELEGATED_REPLAY = PASS", flush=True)
    print("V1_2_FAIL_FAST_WRAPPER_BASELINE_BRANCH =", baseline["branch"], flush=True)

    old_verify = liftv11.verify
    liftv11.verify = liftv12.verify
    try:
        started = time.monotonic()
        result = liftv11.tamper_suite(subject, spec, prep_spec, b51_spec, b52a_spec, b52b_spec)
        print(f"V1_2_FAIL_FAST_29_ATTACK_SECONDS = {time.monotonic() - started:.3f}", flush=True)
        return result
    finally:
        liftv11.verify = old_verify


def main() -> None:
    global ORIGINAL_RUN
    ORIGINAL_RUN = h.run
    h.run = timed_run
    h.build_chain = h12.build_chain_v12
    h.tamper_strict_shrink = tamper_strict_shrink_v13
    print("B5_ORIGINAL_ORDER_LIFT_CI_RUNTIME_HARDENING = ACTIVE_V1_3", flush=True)
    print("FAIL_FAST_SEMANTICS = REJECTION_ONLY_FULL_REPLAY_MANDATORY_ON_PREFLIGHT_PASS", flush=True)
    h.main()


if __name__ == "__main__":
    main()
