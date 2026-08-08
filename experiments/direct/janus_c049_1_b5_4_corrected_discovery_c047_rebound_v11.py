from __future__ import annotations

import argparse
from pathlib import Path

import janus_c049_1_b5_4_corrected_discovery_c047_rebound as base
from janus_c049_fpt_integration_solver import solve_phase_a as historical_solve_phase_a
from janus_c049_fpt_integration_verifier import verify as historical_verify_phase_a


def solve_phase_a_keyword_adapter(factors, dimension, capability, transcript):
    """Adapt the v1 B5.4 call site to the frozen historical keyword-only API."""
    return historical_solve_phase_a(
        factors,
        dimension,
        k=capability.k,
        constructor_transcript=transcript,
        discovery_cap=capability.discovery_cap,
        work_cap=capability.work_cap,
        certificate_cap=capability.certificate_cap,
        trellis_work_cap=capability.trellis_work_cap,
        trellis_certificate_cap=capability.trellis_certificate_cap,
    )


def strict_historical_verify(factors, dimension, certificate):
    """The frozen verifier returns bool; B5.4 may promote only literal True."""
    ok = historical_verify_phase_a(factors, dimension, certificate)
    if ok is not True:
        raise AssertionError("historical Phase-A verifier returned false")
    return True


def build(spec, raw, b5_1, carrier, b52, caps):
    original_solve = base.solve_phase_a
    original_verify = base.verify_phase_a
    try:
        base.solve_phase_a = solve_phase_a_keyword_adapter
        base.verify_phase_a = strict_historical_verify
        return base.build(spec, raw, b5_1, carrier, b52, caps)
    finally:
        base.solve_phase_a = original_solve
        base.verify_phase_a = original_verify


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--carrier", type=Path)
    parser.add_argument("--b5-2b-artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--discovery-cap", type=int)
    parser.add_argument("--work-cap", type=int)
    parser.add_argument("--certificate-cap", type=int)
    parser.add_argument("--trellis-work-cap", type=int)
    parser.add_argument("--trellis-certificate-cap", type=int)
    args = parser.parse_args()
    caps = {
        "discovery_cap": args.discovery_cap,
        "work_cap": args.work_cap,
        "certificate_cap": args.certificate_cap,
        "trellis_work_cap": args.trellis_work_cap,
        "trellis_certificate_cap": args.trellis_certificate_cap,
    }
    artifact = build(
        base.load(args.spec),
        base.load(args.input),
        base.load(args.b5_1_artifact),
        base.load(args.carrier),
        base.load(args.b5_2b_artifact),
        caps,
    )
    base.save(artifact, args.output)
    p = artifact["proof_payload"]
    print("JANUS_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_V1_1 = PASS")
    print("REBOUND_STATUS =", p["rebound_status"])
    print("AFFINE_BINDING_STATUS =", p["affine_binding_status"])
    print("C047_RESULT =", p["c047_result"])
    print("HISTORICAL_PHASE_A_VERIFIER_PASS =", str(p["historical_phase_a_verifier_pass"]).upper())
    print("HISTORICAL_PHASE_A_CALL_ADAPTER = KEYWORD_ONLY_FROZEN_API")
    print("HISTORICAL_PHASE_A_VERIFIER_RETURN = REQUIRED_TRUE")
    print("B5_3_NO_LAYOUT_USED_AS_C047_UNSAT_PREMISE = FALSE")
    print("AFFINE_INSTANCE_SAT_OR_UNSAT_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
