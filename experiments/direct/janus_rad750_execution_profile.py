#!/usr/bin/env python3
"""RAD750-oriented execution profile for JANUS C025.

This module does NOT alter SAT/UNSAT/OPEN semantics and does NOT implement a new
solver primitive.  It translates an already-canonical exact proof state into a
small deterministic "flight manifest" suitable for later C/PowerPC 750 porting.

The theorem-side state cap remains defined by the C025 root input.  RAD750 cache,
word-size, checkpoint and watchdog policies only control how exact work is
scheduled and serialized.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base


PROFILE_SCHEMA = "JANUS/C025/RAD750-FLIGHT-MANIFEST/v1"
WORD_BITS = 32
L1_I_BYTES = 32 * 1024
L1_D_BYTES = 32 * 1024
HOT_I_TARGET_BYTES = 24 * 1024
HOT_D_TARGET_BYTES = 24 * 1024


RAD750_PUBLIC_PROFILE = {
    "architecture_base": "PowerPC 750",
    "integer_word_bits": WORD_BITS,
    "l1_instruction_cache_bytes": L1_I_BYTES,
    "l1_data_cache_bytes": L1_D_BYTES,
    "hot_instruction_target_bytes": HOT_I_TARGET_BYTES,
    "hot_data_chunk_target_bytes": HOT_D_TARGET_BYTES,
    "semantic_truth_may_depend_on_hardware_profile": False,
    "floating_point_allowed_in_semantic_verifier": False,
    "dynamic_recursion_allowed_in_flight_kernel": False,
    "canonical_serialization_byte_order": "big-endian",
    "fail_closed": True,
}


class FlightProfileError(ValueError):
    pass


def _require_i32(value: int) -> int:
    value = int(value)
    if value < -(2**31) or value > 2**31 - 1:
        raise FlightProfileError(f"signed 32-bit literal overflow: {value}")
    return value


def serialize_cnf_v1(cnf: base.CNF) -> bytes:
    """Canonical fixed-width serialization for cross-machine replay.

    Layout, all big-endian unsigned/signed 32-bit words:
      magic 'JCF1'
      clause_count
      repeated: clause_length, signed literals...

    The input is canonicalized again so host ordering cannot alter the digest.
    """
    canonical = base.canon_cnf(cnf)
    out = bytearray(b"JCF1")
    out.extend(struct.pack(">I", len(canonical)))
    for clause in canonical:
        out.extend(struct.pack(">I", len(clause)))
        for literal in clause:
            out.extend(struct.pack(">i", _require_i32(literal)))
    return bytes(out)


def digest_cnf_v1(cnf: base.CNF) -> str:
    return sha256(serialize_cnf_v1(cnf)).hexdigest()


def _ledger_projection(ledger: Mapping[str, Any] | None) -> dict[str, int]:
    if ledger is None:
        return {}
    allowed = (
        "proposal_work",
        "certificate_discovery_work",
        "verification_work",
        "max_state_units",
        "proof_bytes",
        "extension_definition_bytes",
        "extension_count",
        "residual_state_count",
        "residual_cache_hits",
        "question_count",
        "elimination_pair_work",
        "recompression_work",
        "witness_recovery_work",
        "bounded_width_resolution_work",
        "two_sat_work",
        "gf2_work",
    )
    projected: dict[str, int] = {}
    for key in allowed:
        if key not in ledger:
            continue
        value = int(ledger[key])
        if value < 0:
            raise FlightProfileError(f"negative ledger counter: {key}")
        projected[key] = value
    return projected


def build_flight_manifest(
    cnf: base.CNF,
    *,
    root_N: int | None = None,
    cap_exponent: int = 2,
    progress_phi: int | None = None,
    ledger: Mapping[str, Any] | None = None,
    transition_kind: str = "CHECKPOINT_ONLY",
) -> dict[str, Any]:
    canonical = base.canon_cnf(cnf)
    derived_N = base.input_size_units(canonical)
    if root_N is None:
        root_N = derived_N
    root_N = int(root_N)
    cap_exponent = int(cap_exponent)
    if root_N < 2:
        raise FlightProfileError("root_N must be >= 2")
    if cap_exponent < 1:
        raise FlightProfileError("cap_exponent must be >= 1")

    semantic_cap = root_N**cap_exponent
    units = base.state_units(canonical)
    wire = serialize_cnf_v1(canonical)
    wire_bytes = len(wire)
    chunks = max(1, math.ceil(wire_bytes / HOT_D_TARGET_BYTES))

    manifest = {
        "schema": PROFILE_SCHEMA,
        "status": "RAD750_FLIGHT_PROFILE_ONLY__SEMANTICS_UNCHANGED",
        "transition_kind": str(transition_kind),
        "root_N": root_N,
        "cap_exponent": cap_exponent,
        "semantic_state_cap": semantic_cap,
        "state_units": units,
        "state_within_semantic_cap": units <= semantic_cap,
        "canonical_engine_fingerprint": base.fingerprint(canonical),
        "canonical_flight_sha256": sha256(wire).hexdigest(),
        "canonical_wire_bytes": wire_bytes,
        "hot_data_chunk_target_bytes": HOT_D_TARGET_BYTES,
        "stream_chunks_required": chunks,
        "streaming_required": chunks > 1,
        "progress_phi": None if progress_phi is None else int(progress_phi),
        "ledger": _ledger_projection(ledger),
        "verification_policy": {
            "exact_integer_replay": True,
            "floating_point_truth_decision": False,
            "heuristic_truth_decision": False,
            "dual_independent_verifier_target": True,
            "mismatch_action": "OPEN_OR_SAFE_ERROR",
        },
        "hardware_policy": RAD750_PUBLIC_PROFILE,
        "scientific_boundary": {
            "hardware_profile_changes_theorem": False,
            "hardware_profile_proves_polynomiality": False,
            "arbitrary_CNF": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    return manifest


def verify_flight_manifest(cnf: base.CNF, manifest: Mapping[str, Any]) -> bool:
    """Independent manifest replay; never trusts stored digests or sizes."""
    try:
        rebuilt = build_flight_manifest(
            cnf,
            root_N=int(manifest["root_N"]),
            cap_exponent=int(manifest["cap_exponent"]),
            progress_phi=manifest.get("progress_phi"),
            ledger=manifest.get("ledger", {}),
            transition_kind=str(manifest.get("transition_kind", "CHECKPOINT_ONLY")),
        )
    except (KeyError, TypeError, ValueError, FlightProfileError):
        return False

    keys = (
        "schema",
        "transition_kind",
        "root_N",
        "cap_exponent",
        "semantic_state_cap",
        "state_units",
        "state_within_semantic_cap",
        "canonical_engine_fingerprint",
        "canonical_flight_sha256",
        "canonical_wire_bytes",
        "hot_data_chunk_target_bytes",
        "stream_chunks_required",
        "streaming_required",
        "progress_phi",
        "ledger",
    )
    return all(manifest.get(key) == rebuilt.get(key) for key in keys)


def _self_test() -> dict[str, Any]:
    cnf = base.canon_cnf(
        (
            (1, 2, -3),
            (-1, 3),
            (-2, 3),
            (1, -2),
        )
    )
    manifest = build_flight_manifest(
        cnf,
        cap_exponent=2,
        progress_phi=17,
        ledger={
            "proposal_work": 11,
            "verification_work": 7,
            "proof_bytes": 128,
        },
        transition_kind="SELF_TEST",
    )
    if not verify_flight_manifest(cnf, manifest):
        raise AssertionError("RAD750_MANIFEST_REPLAY_FAILED")

    tampered = json.loads(json.dumps(manifest))
    tampered["canonical_flight_sha256"] = "00" * 32
    if verify_flight_manifest(cnf, tampered):
        raise AssertionError("RAD750_MANIFEST_TAMPER_NOT_REJECTED")

    reordered = tuple(reversed(cnf))
    if digest_cnf_v1(reordered) != digest_cnf_v1(cnf):
        raise AssertionError("CANONICAL_SERIALIZATION_DEPENDS_ON_INPUT_ORDER")

    return {
        "schema": "JANUS/C025/RAD750-FLIGHT-PROFILE-SELF-TEST/v1",
        "status": "PASS",
        "manifest": manifest,
        "tamper_rejected": True,
        "reordered_input_same_digest": True,
        "P_VS_NP": "OPEN",
    }


def main() -> int:
    print(json.dumps(_self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
