from __future__ import annotations

import copy

import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v11 as v11


def _repair_b52(candidate: dict) -> dict:
    candidate["semantic_digest"] = v11.base.dg(candidate["proof_payload"])
    return candidate


def _repair_b54(candidate: dict) -> dict:
    candidate["semantic_digest"] = v11.base.dg(candidate["proof_payload"])
    return candidate


def _reject_nontrivial_upstream_b52_tamper(
    name: str,
    sat: dict,
    spec: dict,
    carrier_spec: dict,
    b52_spec: dict,
    r52: dict,
    r53: dict,
    mutation,
) -> int:
    # Mutate the upstream B5.2B proof and repair its own semantic digest.
    b52 = copy.deepcopy(sat["b52"])
    mutation(b52["proof_payload"])
    _repair_b52(b52)
    if b52["semantic_digest"] == sat["b52"]["semantic_digest"]:
        raise AssertionError(name + " is a no-op B5.2B mutation")

    # Also repair the outer B5.4 subject binding so rejection cannot be caused
    # merely by old-subject-digest != repaired-upstream-digest.
    candidate = copy.deepcopy(sat["candidate"])
    candidate["proof_payload"]["subject"]["b5_2b_semantic_digest"] = b52["semantic_digest"]
    _repair_b54(candidate)
    if candidate["proof_payload"]["subject"]["b5_2b_semantic_digest"] != b52["semantic_digest"]:
        raise AssertionError(name + " failed to rebind repaired upstream digest")
    if candidate["semantic_digest"] == sat["candidate"]["semantic_digest"]:
        raise AssertionError(name + " failed to repair outer B5.4 digest")

    # Prove the intended rejection source explicitly: the bound independent
    # B5.2B verifier must reject the repaired upstream semantic mutation.
    upstream_rejected = False
    try:
        v11.base.b52b_verifier.verify(
            b52,
            b52_spec,
            sat["raw"],
            sat["b51"],
            sat["carrier"],
        )
    except Exception:
        upstream_rejected = True
    if not upstream_rejected:
        raise AssertionError(name + " survived direct independent B5.2B replay")

    # And the full B5.4 verifier must reject the same repaired-and-rebound
    # upstream subject before any C047 promotion can be accepted.
    try:
        v11.verify(
            candidate,
            spec,
            sat["raw"],
            sat["b51"],
            sat["carrier"],
            b52,
            carrier_spec,
            b52_spec,
            r52,
            r53,
            sat["caps"],
        )
    except Exception:
        print(name + " = REJECTED_AFTER_OUTER_SUBJECT_REBIND")
        return 1
    raise AssertionError(name + " survived full B5.4 replay")


def tamper_suite(subjects, spec, carrier_spec, b52_spec, r52, r53, caps):
    rejected, total = v11.tamper_suite(subjects, spec, carrier_spec, b52_spec, r52, r53, caps)
    if (rejected, total) != (25, 25):
        raise AssertionError("B5.4 v1.1 tamper suite changed")

    sat = subjects["sat"]
    rejected += _reject_nontrivial_upstream_b52_tamper(
        "T26_REPAIRED_REBOUND_UPSTREAM_B52_CUT_WIDTH",
        sat,
        spec,
        carrier_spec,
        b52_spec,
        r52,
        r53,
        lambda p: p["cut_certificates"][0].__setitem__("width", 999),
    )
    total += 1
    rejected += _reject_nontrivial_upstream_b52_tamper(
        "T27_REPAIRED_REBOUND_UPSTREAM_B52_CUT_BASIS",
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
