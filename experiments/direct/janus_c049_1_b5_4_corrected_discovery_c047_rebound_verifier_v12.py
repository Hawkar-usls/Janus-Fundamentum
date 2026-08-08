from __future__ import annotations

import copy

import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v11 as v11


def _repair_b52(candidate: dict) -> dict:
    candidate["semantic_digest"] = v11.base.dg(candidate["proof_payload"])
    return candidate


def _reject_upstream_b52_tamper(
    name: str,
    sat: dict,
    spec: dict,
    carrier_spec: dict,
    b52_spec: dict,
    r52: dict,
    r53: dict,
    mutation,
) -> int:
    b52 = copy.deepcopy(sat["b52"])
    mutation(b52["proof_payload"])
    _repair_b52(b52)
    try:
        v11.verify(
            copy.deepcopy(sat["candidate"]),
            spec,
            sat["raw"],
            sat["b51"],
            sat.get("carrier"),
            b52,
            carrier_spec,
            b52_spec,
            r52,
            r53,
            sat["caps"],
        )
    except Exception:
        print(name + " = REJECTED")
        return 1
    raise AssertionError(name + " survived")


def tamper_suite(subjects, spec, carrier_spec, b52_spec, r52, r53, caps):
    rejected, total = v11.tamper_suite(subjects, spec, carrier_spec, b52_spec, r52, r53, caps)
    if (rejected, total) != (25, 25):
        raise AssertionError("B5.4 v1.1 tamper suite changed")

    sat = subjects["sat"]
    rejected += _reject_upstream_b52_tamper(
        "T26_REPAIRED_UPSTREAM_B52_CUT_WIDTH",
        sat,
        spec,
        carrier_spec,
        b52_spec,
        r52,
        r53,
        lambda p: p["cut_certificates"][0].__setitem__("width", 999),
    )
    total += 1
    rejected += _reject_upstream_b52_tamper(
        "T27_REPAIRED_UPSTREAM_B52_CUT_BASIS",
        sat,
        spec,
        carrier_spec,
        b52_spec,
        r52,
        r53,
        lambda p: p["cut_certificates"][0].__setitem__("boundary_rref", [999]),
    )
    total += 1
    return rejected, total
