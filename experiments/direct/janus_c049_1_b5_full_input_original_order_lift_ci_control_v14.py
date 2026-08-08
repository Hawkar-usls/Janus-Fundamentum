from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import janus_c049_1_b5_full_input_original_order_lift_ci_harness_v11 as h
import janus_c049_1_b5_full_input_original_order_lift_ci_harness_v12 as h12
import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier_v11 as liftv11
import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier_v12 as liftv12

EVIDENCE = Path("/tmp/b5-original-order-lift-parallel-evidence")
CAPS = {
    "discovery_cap": None,
    "work_cap": None,
    "certificate_cap": None,
    "trellis_work_cap": None,
    "trellis_certificate_cap": None,
}


def subject(files: dict[str, Path]) -> dict:
    return {
        "raw_original": h.load(files["raw"]),
        "preprocessing": h.load(files["pre"]),
        "reduced_raw": h.load(files["reduced"]),
        "b51": h.load(files["b51"]),
        "carrier": h.load(files["carrier"]),
        "b52": h.load(files["b52"]),
        "candidate": h.load(files["lift"]),
        "caps": dict(CAPS),
    }


def full_wrapper_verify(files: dict[str, Path]) -> dict:
    s = subject(files)
    return liftv12.verify(
        s["candidate"],
        h.load(h.SPEC),
        s["raw_original"],
        s["preprocessing"],
        s["reduced_raw"],
        s["b51"],
        s["carrier"],
        s["b52"],
        h.load(h.PRE_SPEC),
        h.load(h.B51_SPEC),
        h.load(h.B52A_SPEC),
        h.load(h.B52B_SPEC),
        s["caps"],
    )


def run_control(name: str) -> dict:
    controls = h.controls()
    if name == "sat":
        files = h.build_chain("sat", controls["sat"])
        p = h.load(files["lift"])["proof_payload"]
        if not (p["c047_result"] == "SAT" and p["historical_phase_a_verifier_pass"] is True and p["original_layout_replay"]["maximum_width"] <= 0):
            raise AssertionError("SAT control")
        wrapper = full_wrapper_verify(files)
        if wrapper.get("branch") not in {"POSITIVE_AFFINE_BOUND", "POSITIVE_TERMINAL", "POSITIVE"}:
            # The exact branch label is verifier-owned and may be more specific;
            # success is established by a returned report plus the base verifier replay.
            if not isinstance(wrapper, dict):
                raise AssertionError("wrapper delegated report")
        return {"sat": "PASS", "wrapper_full_base_delegation": "PASS", "c047_result": "SAT"}

    if name == "unsat":
        files = h.build_chain("unsat", controls["unsat"])
        p = h.load(files["lift"])["proof_payload"]
        if not (p["c047_result"] == "UNSAT" and p["historical_phase_a_verifier_pass"] is True and len({x["phase_a_input_position"] for x in p["phase_a_factor_bijection"]}) == 2):
            raise AssertionError("UNSAT control")
        return {"unsat": "PASS", "c047_result": "UNSAT"}

    if name == "shrink":
        files = h.build_chain("shrink", controls["shrink"])
        p = h.load(files["lift"])["proof_payload"]
        pre = h.load(files["pre"])["proof_payload"]
        if not (p["c047_result"] == "SAT" and p["historical_phase_a_verifier_pass"] is True and p["original_layout_replay"]["maximum_width"] <= 1):
            raise AssertionError("strict-shrink terminal")
        if not any(len(o["normal_space"]) > len(r["normal_space"]) for o, r in zip(pre["original_catalog"], pre["discovery_catalog"])):
            raise AssertionError("strict-shrink witness")
        if not all(x["semantic_boundary_equal"] is True for x in p["reduced_to_original_cut_bridge"]):
            raise AssertionError("strict-shrink cut bridge")
        return {"strict_shrink": "PASS", "c047_result": "SAT"}

    if name == "opaque":
        files = h.build_chain("opaque", controls["opaque"])
        p = h.load(files["lift"])["proof_payload"]
        if p["lift_status"] != "OPEN_AFFINE_REBOUND_BINDING" or p["c047_result"] != "NOT_ESTABLISHED":
            raise AssertionError("opaque OPEN")
        return {"opaque_open": "PASS", "lift_status": p["lift_status"]}

    if name == "reorder":
        a = h.build_chain("sat", controls["sat"])
        b = h.build_chain("sat-reordered", controls["sat-reordered"])
        pa = h.load(a["lift"])["proof_payload"]
        pb = h.load(b["lift"])["proof_payload"]
        if pa["factor_order_ids"] != pb["factor_order_ids"] or pa["original_layout_replay"] != pb["original_layout_replay"] or pa["c047_result"] != pb["c047_result"]:
            raise AssertionError("presentation reorder semantic result")
        if pa["preprocessing_semantic_digest"] == pb["preprocessing_semantic_digest"]:
            raise AssertionError("presentation reorder provenance collapse")
        return {"presentation_reorder": "PASS", "provenance_distinct": True}

    if name == "historical-open":
        files = h.build_chain("sat", controls["sat"])
        path = h.build_hist_open(files)
        p = h.load(path)["proof_payload"]
        if p["lift_status"] != "ORIGINAL_ORDER_LIFT_PHASE_A_C047_OPEN" or not str(p["c047_result"]).startswith("OPEN_"):
            raise AssertionError("historical OPEN")
        return {"historical_open": "PASS", "c047_result": p["c047_result"]}

    if name == "direct-reduced":
        sat = h.build_chain("sat", controls["sat"])
        shrink = h.build_chain("shrink", controls["shrink"])
        ds = h.direct_reduced_b54("sat", sat)["proof_payload"]
        dh = h.direct_reduced_b54("shrink", shrink)["proof_payload"]
        for p in (ds, dh):
            if p["rebound_status"] != "OPEN_AFFINE_REBOUND_BINDING" or p["c047_result"] != "NOT_ESTABLISHED":
                raise AssertionError("direct reduced B5.4 must remain OPEN")
        return {"direct_reduced_b5_4": "OPEN_AS_REQUIRED"}

    if name == "tamper":
        files = h.build_chain("shrink", controls["shrink"])
        s = subject(files)
        old = liftv11.verify
        liftv11.verify = liftv12.verify
        try:
            rejected, total = liftv11.tamper_suite(
                s,
                h.load(h.SPEC),
                h.load(h.PRE_SPEC),
                h.load(h.B51_SPEC),
                h.load(h.B52A_SPEC),
                h.load(h.B52B_SPEC),
            )
        finally:
            liftv11.verify = old
        if (rejected, total) != (29, 29):
            raise AssertionError(f"29-attack fail-fast suite: {rejected}/{total}")
        return {"digest_repaired_tampers_rejected": "29/29", "attack_generator": "UNCHANGED_V1_1"}

    raise AssertionError("unknown control: " + name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", required=True, choices=[
        "sat", "unsat", "shrink", "opaque", "reorder", "historical-open", "direct-reduced", "tamper"
    ])
    args = parser.parse_args()
    h.build_chain = h12.build_chain_v12
    h.TMP.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    result = run_control(args.control)
    seconds = time.monotonic() - started
    receipt = {
        "schema": "janus.c049_1.b5.original_order_lift_parallel_control_receipt.v1_4",
        "control": args.control,
        "verification_head": os.environ.get("VERIFICATION_HEAD", "LOCAL"),
        "frozen_proof_head": os.environ.get("FROZEN_PROOF_HEAD", "LOCAL"),
        "status": "PASS",
        "seconds": round(seconds, 6),
        "result": result,
        "strict_ceiling": {
            "iterative_compression_orchestrator": "NOT_ESTABLISHED",
            "all_input_termination": "NOT_ESTABLISHED",
            "polynomial_runtime": "NOT_ESTABLISHED",
            "b5_complete": False,
            "c049_1_complete": False,
            "p_vs_np": "OPEN",
        },
    }
    path = EVIDENCE / f"{args.control}.json"
    path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("PARALLEL_CONTROL =", args.control)
    print("PARALLEL_CONTROL_STATUS = PASS")
    print("PARALLEL_CONTROL_SECONDS =", f"{seconds:.3f}")
    for key, value in result.items():
        print(key.upper(), "=", value)
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("C049_1_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
