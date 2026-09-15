from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_mixed_carrier_barrier.check_schaefer_barrier import (
    is_0_valid,
    is_1_valid,
    is_horn,
    is_dual_horn,
    is_bijunctive,
    is_affine,
)
from research.tools.apma_unseen_basis.raw_relation_basis import (
    induce_basis,
    raw_or2,
    raw_even_xor3,
    raw_mixed,
    permuted,
    label_injected,
)

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_RAW_RELATION_SCHAEFER_BASIS_INDUCTION_PREREGISTRATION_2026-09-15.json"
CANDIDATE = ROOT / "research/tools/apma_unseen_basis/raw_relation_basis.py"
SEALED = ROOT / "research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py"

PREREG_SHA1 = "92c6e6978f171a800db82bd6ae2e3c7112d65e22"
CANDIDATE_SHA1 = "63490c05ef3e91a4f682f75da26ff2af811839a6"
SEALED_SHA1 = "11fcacd5f0c550543f96648a7965734308509d22"
PRIORITY = ("AFFINE", "BIJUNCTIVE", "HORN", "DUAL_HORN", "ZERO_VALID", "ONE_VALID")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def independent_fp(language: list[set[tuple[int, ...]]]) -> dict[str, bool]:
    return {
        "ZERO_VALID": is_0_valid(language),
        "ONE_VALID": is_1_valid(language),
        "HORN": is_horn(language),
        "DUAL_HORN": is_dual_horn(language),
        "BIJUNCTIVE": is_bijunctive(language),
        "AFFINE": is_affine(language),
    }


def selected(fp: dict[str, bool]) -> str | None:
    return next((x for x in PRIORITY if fp[x]), None)


def relation_set(words: list[str]) -> set[tuple[int, ...]]:
    return {tuple(int(ch) for ch in w) for w in words}


def expected_from_raw(raw: dict) -> tuple[dict[str, bool], str | None]:
    seen: dict[tuple[int, tuple[str, ...]], set[tuple[int, ...]]] = {}
    for row in raw["constraints"]:
        allowed = {tuple(int(x) for x in t) for t in row["allowed"]}
        words = tuple(sorted("".join(str(x) for x in t) for t in allowed))
        seen[(len(row["scope"]), words)] = allowed
    language = [seen[k] for k in sorted(seen)]
    fp = independent_fp(language)
    return fp, selected(fp)


def certificate_valid(raw: dict, cert: dict) -> bool:
    if cert.get("status") != "ADMIT_EXACT_SCHAEFER_BASIS":
        return False
    fp, sel = expected_from_raw(raw)
    return cert.get("language_fingerprint") == fp and cert.get("selected_basis") == sel and bool(sel)


def raw_single_relation(arity: int, mask: int, rid: str) -> dict:
    tuples = []
    for word in range(1 << arity):
        if (mask >> word) & 1:
            tuples.append([(word >> i) & 1 for i in range(arity)])
    if not tuples:
        raise ValueError("mask must be nonzero")
    return {
        "variables": list(range(arity)),
        "constraints": [{"id": rid, "scope": list(range(arity)), "allowed": tuples}],
    }


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    candidate_source = CANDIDATE.read_text(encoding="utf-8")

    c1_raw = raw_or2()
    c2_raw = raw_even_xor3()
    c3_raw = raw_mixed()
    c1 = induce_basis(c1_raw)
    c2 = induce_basis(c2_raw)
    c3 = induce_basis(c3_raw)
    c4 = induce_basis(permuted(c3_raw))
    c6 = induce_basis(label_injected())

    c1_fp, c1_sel = expected_from_raw(c1_raw)
    c2_fp, c2_sel = expected_from_raw(c2_raw)
    c3_fp, c3_sel = expected_from_raw(c3_raw)

    exhaustive_arity2 = []
    for mask in range(1, 1 << (1 << 2)):
        raw = raw_single_relation(2, mask, f"opaque_{mask}")
        got = induce_basis(raw)
        fp, sel = expected_from_raw(raw)
        exhaustive_arity2.append(
            got.get("language_fingerprint") == fp
            and got.get("selected_basis") == sel
            and got.get("status") == ("ADMIT_EXACT_SCHAEFER_BASIS" if sel else "OPEN_NO_SCHAEFER_BASIS")
        )

    arity3_masks = [
        0x01,
        0x03,
        0x0F,
        0x17,
        0x33,
        0x55,
        0x69,
        0x96,
        0xAA,
        0xC3,
        0xE8,
        0xFF,
    ]
    sampled_arity3 = []
    for mask in arity3_masks:
        raw = raw_single_relation(3, mask, f"opaque3_{mask}")
        got = induce_basis(raw)
        fp, sel = expected_from_raw(raw)
        sampled_arity3.append(
            got.get("language_fingerprint") == fp
            and got.get("selected_basis") == sel
            and got.get("status") == ("ADMIT_EXACT_SCHAEFER_BASIS" if sel else "OPEN_NO_SCHAEFER_BASIS")
        )

    tampered = dict(c1)
    tampered["selected_basis"] = "AFFINE"

    mixed_metrics = c3.get("metrics", {})
    checks = {
        "P1_prereg_blob": git_blob_sha1(PREREG) == PREREG_SHA1,
        "P1_candidate_blob": git_blob_sha1(CANDIDATE) == CANDIDATE_SHA1,
        "P1_sealed_primitive_blob": git_blob_sha1(SEALED) == SEALED_SHA1,
        "P1_prereg_status_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "P2_label_injection_rejected": c6.get("status") == "REJECT_RAW_INPUT" and c6.get("reason") == "FORBIDDEN_TRUSTED_CONSTRAINT_FIELD",
        "P2_label_rejection_no_execution": c6.get("metrics", {}).get("solver_invocations") == 0 and c6.get("metrics", {}).get("carrier_executions") == 0,
        "P3_or2_fingerprint_independent": c1.get("language_fingerprint") == c1_fp,
        "P3_or2_selected_independent": c1.get("selected_basis") == c1_sel == "BIJUNCTIVE",
        "P3_xor_fingerprint_independent": c2.get("language_fingerprint") == c2_fp,
        "P3_xor_selected_independent": c2.get("selected_basis") == c2_sel == "AFFINE",
        "P3_exhaustive_all_15_nonempty_binary_relations": all(exhaustive_arity2) and len(exhaustive_arity2) == 15,
        "P3_sampled_arity3_relations": all(sampled_arity3) and len(sampled_arity3) == len(arity3_masks),
        "P4_positive_abstraction_adequacy": c1.get("abstraction_adequacy") == "PASS_COMPLETE_SURFACE_CLOSURE" and c2.get("abstraction_adequacy") == "PASS_COMPLETE_SURFACE_CLOSURE",
        "P4_tampered_certificate_rejected": certificate_valid(c1_raw, tampered) is False,
        "P4_untampered_certificate_accepted": certificate_valid(c1_raw, c1) is True,
        "P5_mixed_all_six_false": c3_fp == {"ZERO_VALID": False, "ONE_VALID": False, "HORN": False, "DUAL_HORN": False, "BIJUNCTIVE": False, "AFFINE": False},
        "P5_mixed_fails_closed": c3.get("status") == "OPEN_NO_SCHAEFER_BASIS" and c3_sel is None,
        "P5_mixed_execution_unauthorized": c3.get("execution_authorized") is False,
        "P5_mixed_zero_solver_invocations": mixed_metrics.get("solver_invocations") == 0 and mixed_metrics.get("carrier_executions") == 0,
        "P6_surface_permutation_same_surface_hash": c3.get("semantic_surface_sha256") == c4.get("semantic_surface_sha256"),
        "P6_surface_permutation_same_fingerprint": c3.get("language_fingerprint") == c4.get("language_fingerprint"),
        "P6_surface_permutation_same_selected_basis": c3.get("selected_basis") == c4.get("selected_basis"),
        "P7_candidate_source_no_itertools": "import itertools" not in candidate_source,
        "P7_candidate_source_no_full_cube_pattern": "range(1 <<" not in candidate_source and "product([0, 1]" not in candidate_source and "product((0, 1)" not in candidate_source,
        "P7_reported_full_variable_cube_zero": all(x.get("metrics", {}).get("full_variable_assignments_enumerated", 0) == 0 for x in (c1, c2, c3)),
        "P7_reported_solver_invocations_zero": all(x.get("metrics", {}).get("solver_invocations", 0) == 0 for x in (c1, c2, c3)),
        "P8_p_vs_np_open": c1.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "P8_general_sat_not_proved": c1.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "P8_arbitrary_discovery_not_proved": c1.get("scientific_firewall", {}).get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_RAW_RELATION_SCHAEFER_BASIS_INDUCTION" if all(checks.values()) else "FAIL_OR_OPEN_RAW_RELATION_BASIS_INDUCTION"
    out = {
        "artifact_id": "JANUS-TRUMP-RAW-RELATION-SCHAEFER-BASIS-INDUCTION-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "raw_or2": {"fingerprint": c1.get("language_fingerprint"), "selected": c1.get("selected_basis")},
            "raw_even_xor3": {"fingerprint": c2.get("language_fingerprint"), "selected": c2.get("selected_basis")},
            "mixed": {"fingerprint": c3.get("language_fingerprint"), "status": c3.get("status")},
            "exhaustive_binary_relations_checked": len(exhaustive_arity2),
            "sampled_arity3_relations_checked": len(sampled_arity3),
        },
        "complexity": {
            "discovery": "O(sum_R s_R^3 a_R) over explicit allowed-tuple input",
            "certificate_replay": "same polynomial closure checks over the complete bound relation surface",
            "full_variable_cube": "FORBIDDEN_AND_NOT_USED",
            "solver_execution": "ZERO_IN_THIS_BASIS_INDUCTION_GATE",
        },
        "interpretation": "The mechanism discovers membership in the frozen six Boolean Schaefer basis classes from raw explicit relation semantics without trusted class labels. This is a scoped basis-induction result, not arbitrary invariant discovery.",
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW"
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
