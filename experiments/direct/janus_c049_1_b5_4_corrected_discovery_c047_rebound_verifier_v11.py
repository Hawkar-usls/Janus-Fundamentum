from __future__ import annotations

import argparse
import copy
from pathlib import Path

import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier as base
from janus_c049_fpt_integration_verifier import verify as historical_verify_phase_a


def verify(candidate, spec, raw, b51, carrier, b52, carrier_spec, b52_spec, r52, r53, caps):
    out = base.verify(candidate, spec, raw, b51, carrier, b52, carrier_spec, b52_spec, r52, r53, caps)
    p = candidate["proof_payload"]
    if p.get("historical_phase_a_verifier_pass") is True:
        factors = p.get("phase_a_factors")
        certificate = p.get("phase_a_certificate")
        if not isinstance(factors, list) or not isinstance(certificate, dict):
            raise AssertionError("historical verifier flag without replay material")
        if historical_verify_phase_a(factors, int(p["ambient_dim"]), certificate) is not True:
            raise AssertionError("historical Phase-A verifier returned false")
    return out


def repair(candidate):
    candidate["semantic_digest"] = base.dg(candidate["proof_payload"])
    return candidate


def tamper_suite(subjects, spec, carrier_spec, b52_spec, r52, r53, caps):
    rejected, total = base.tamper_suite(subjects, spec, carrier_spec, b52_spec, r52, r53, caps)
    if (rejected, total) != (24, 24):
        raise AssertionError("base B5.4 tamper suite changed")

    sat = subjects["sat"]
    candidate = copy.deepcopy(sat["candidate"])
    cert = candidate["proof_payload"].get("phase_a_certificate")
    if not isinstance(cert, dict) or "integrity_sha256" not in cert:
        raise AssertionError("T25 fixture missing Phase-A integrity digest")
    cert["integrity_sha256"] = "0" * 64
    candidate = repair(candidate)
    try:
        verify(
            candidate,
            spec,
            sat["raw"],
            sat["b51"],
            sat.get("carrier"),
            sat.get("b52"),
            carrier_spec,
            b52_spec,
            r52,
            r53,
            sat.get("caps", caps),
        )
    except Exception:
        return rejected + 1, total + 1
    raise AssertionError("T25_PHASE_A_CERTIFICATE_FALSE_RETURN survived")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--carrier-spec", type=Path, required=True)
    p.add_argument("--b5-2b-spec", type=Path, required=True)
    p.add_argument("--b5-2b-admission", type=Path, required=True)
    p.add_argument("--b5-3-admission", type=Path, required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--b5-1-artifact", type=Path, required=True)
    p.add_argument("--carrier", type=Path)
    p.add_argument("--b5-2b-artifact", type=Path)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--discovery-cap", type=int)
    p.add_argument("--work-cap", type=int)
    p.add_argument("--certificate-cap", type=int)
    p.add_argument("--trellis-work-cap", type=int)
    p.add_argument("--trellis-certificate-cap", type=int)
    a = p.parse_args()
    caps = {
        "discovery_cap": a.discovery_cap,
        "work_cap": a.work_cap,
        "certificate_cap": a.certificate_cap,
        "trellis_work_cap": a.trellis_work_cap,
        "trellis_certificate_cap": a.trellis_certificate_cap,
    }
    out = verify(
        base.load(a.candidate),
        base.load(a.spec),
        base.load(a.input),
        base.load(a.b5_1_artifact),
        base.load(a.carrier),
        base.load(a.b5_2b_artifact),
        base.load(a.carrier_spec),
        base.load(a.b5_2b_spec),
        base.load(a.b5_2b_admission),
        base.load(a.b5_3_admission),
        caps,
    )
    print("JANUS_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_INDEPENDENT_VERIFIER_V1_1 = PASS")
    print("REBOUND_STATUS =", out["rebound_status"])
    print("AFFINE_BINDING_STATUS =", out["affine_binding_status"])
    print("C047_RESULT =", out["c047_result"])
    print("HISTORICAL_PHASE_A_VERIFIER_RETURN = REQUIRED_TRUE")
    print("B5_3_NO_LAYOUT_USED_AS_C047_UNSAT_PREMISE = FALSE")
    print("AFFINE_INSTANCE_SAT_OR_UNSAT_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
