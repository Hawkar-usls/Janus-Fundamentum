#!/usr/bin/env python3
"""S𓂸ḥ ribbon-state mechanic: ORIGIN -> EXPERIENCE -> RETURN -> ORIGIN_PRIME.

This layer changes state semantics without changing SAT semantics.  A full
Tranception traversal may return to the same canonical technical POSITION, but it
must not overwrite the original STATE.  Instead it emits a new typed
ORIGIN_PRIME commitment that binds the immutable ORIGIN, the ordered six-direction
history, and the verified return position.

BACK is verification, not erasure.  FORWARD_AGAIN is reproducibility of POSITION,
not identity of STATE.  Historical text is not consumed by solver correctness.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import copy
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import s_phallus_h_gate_0_articulation_decomposition_strict as gate0

CONTRACT = "S_PHALLUS_H_ORIGIN_PRIME_RIBBON_STATE_FROZEN_CONTRACT.json"
RUN_ID = "S-PHALLUS-H-ORIGIN-PRIME-RIBBON-STATE-2026-08-18-v1"
PARENT_SHA = "f5299edb21c72b2f32fcc54862af1910d45d4c34"
PARENT_RESULT_SHA = "343cfa6a5727d898def5eea2d0b43e6c39eb1c39331b6f1c2d3bf31daf7a1ef7"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]


class HashLedger:
    def __init__(self) -> None:
        self.hash_operations = 0

    def digest(self, value: Any) -> str:
        self.hash_operations += 1
        raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return sha256(raw.encode("utf-8")).hexdigest()


def stable_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def mutate_hex(value: str) -> str:
    if not value:
        return value
    first = "0" if value[0] != "0" else "1"
    return first + value[1:]


def technical_position(parent: dict[str, Any], ledger: HashLedger) -> dict[str, Any]:
    primary = parent["FORWARD"]["primary"]
    core = {
        "formula_hash": primary["formula_hash"],
        "technical_verdict": parent["FORWARD"]["status"],
        "lane": parent["FORWARD"]["lane"],
        "forward_again_position_verified": bool(parent["gates"]["FORWARD_AGAIN_exact_projection"]),
        "parent_gate_identity": parent["gate_identity"],
        "parent_subgate": parent["subgate"],
    }
    return {**core, "position_commitment": ledger.digest(core)}


def direction_history(parent: dict[str, Any], ledger: HashLedger) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, direction in enumerate(DIRECTIONS):
        payload = parent[direction]
        rows.append({
            "index": index,
            "direction": direction,
            "payload_digest": ledger.digest(payload),
        })
    return rows


def make_origin(position_commitment: str, parent_integrity: str, ledger: HashLedger) -> dict[str, Any]:
    core = {
        "state_type": "ORIGIN",
        "generation": 0,
        "position_commitment": position_commitment,
        "parent_gate_integrity": parent_integrity,
        "previous_state_commitment": None,
        "path_history_digest": None,
    }
    return {**core, "state_commitment": ledger.digest(core)}


def make_origin_prime(
    previous_state_commitment: str,
    generation: int,
    position_commitment: str,
    history_digest: str,
    return_commitment: str,
    ledger: HashLedger,
) -> dict[str, Any]:
    core = {
        "state_type": "ORIGIN_PRIME",
        "generation": generation,
        "position_commitment": position_commitment,
        "previous_state_commitment": previous_state_commitment,
        "path_history_digest": history_digest,
        "return_commitment": return_commitment,
    }
    return {**core, "state_commitment": ledger.digest(core)}


def verify_origin_prime(
    record: dict[str, Any],
    previous_state_commitment: str,
    generation: int,
    position_commitment: str,
    history_digest: str,
    return_commitment: str,
    ledger: HashLedger,
) -> bool:
    if record.get("state_type") != "ORIGIN_PRIME":
        return False
    expected = {
        "state_type": "ORIGIN_PRIME",
        "generation": generation,
        "position_commitment": position_commitment,
        "previous_state_commitment": previous_state_commitment,
        "path_history_digest": history_digest,
        "return_commitment": return_commitment,
    }
    return all(record.get(k) == v for k, v in expected.items()) and record.get("state_commitment") == ledger.digest(expected)


def build_ribbon(parent: dict[str, Any], previous_state: dict[str, Any] | None = None, generation: int = 1) -> dict[str, Any]:
    ledger = HashLedger()
    position = technical_position(parent, ledger)
    history = direction_history(parent, ledger)
    history_digest = ledger.digest(history)
    parent_integrity = parent["integrity_sha256"]

    if previous_state is None:
        origin = make_origin(position["position_commitment"], parent_integrity, ledger)
        previous_state = origin
    else:
        origin = None

    return_core = {
        "state_type": "RETURN",
        "position_commitment": position["position_commitment"],
        "path_history_digest": history_digest,
        "back_verified": bool(parent["BACK"]["passed"]),
        "forward_again_position_verified": bool(parent["gates"]["FORWARD_AGAIN_exact_projection"]),
        "back_again_verified": bool(parent["BACK_AGAIN"]["passed"]),
        "legacy_same_as_reference": bool(parent["BACK_AGAIN"].get("same_as_reference")),
        "legacy_same_as_reference_interpretation": "POSITION_EQUIVALENCE_ONLY",
    }
    return_commitment = ledger.digest(return_core)
    return_state = {**return_core, "return_commitment": return_commitment}

    origin_prime = make_origin_prime(
        previous_state["state_commitment"],
        generation,
        position["position_commitment"],
        history_digest,
        return_commitment,
        ledger,
    )
    verified = verify_origin_prime(
        origin_prime,
        previous_state["state_commitment"],
        generation,
        position["position_commitment"],
        history_digest,
        return_commitment,
        ledger,
    )

    return {
        "position": position,
        "origin": origin,
        "experience": {
            "ordered_directions": DIRECTIONS,
            "history": history,
            "path_history_digest": history_digest,
        },
        "return": return_state,
        "origin_prime": origin_prime,
        "verified": verified,
        "cost": {
            "hash_operations": ledger.hash_operations,
            "serialized_history_bytes": len(stable_bytes(history)),
            "heterogeneous_units_not_summed_as_runtime": True,
        },
    }


def negative_controls(ribbon: dict[str, Any]) -> dict[str, Any]:
    base = ribbon["origin_prime"]
    previous = base["previous_state_commitment"]
    generation = base["generation"]
    position = base["position_commitment"]
    history = base["path_history_digest"]
    ret = base["return_commitment"]

    def verify(candidate: dict[str, Any], *, prev: str = previous, gen: int = generation,
               pos: str = position, hist: str = history, r: str = ret) -> bool:
        ledger = HashLedger()
        return verify_origin_prime(candidate, prev, gen, pos, hist, r, ledger)

    history_bitflip = copy.deepcopy(base)
    history_bitflip["path_history_digest"] = mutate_hex(history_bitflip["path_history_digest"])

    history_erasure = copy.deepcopy(base)
    history_erasure["path_history_digest"] = None

    forced_origin_reuse = copy.deepcopy(base)
    forced_origin_reuse["state_type"] = "ORIGIN"
    forced_origin_reuse["generation"] = 0
    forced_origin_reuse["state_commitment"] = ribbon["origin"]["state_commitment"]

    position_mutation = copy.deepcopy(base)
    position_mutation["position_commitment"] = mutate_hex(position_mutation["position_commitment"])

    return {
        "history_bitflip_rejected": not verify(history_bitflip),
        "history_erasure_rejected": not verify(history_erasure),
        "forced_origin_state_reuse_rejected": not verify(forced_origin_reuse),
        "return_position_mutation_rejected": not verify(position_mutation),
    }


def run() -> dict[str, Any]:
    contract_path = Path(__file__).with_name(CONTRACT)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    assert contract["parent"]["sha"] == PARENT_SHA
    assert contract["parent"]["result_integrity_sha256"] == PARENT_RESULT_SHA
    assert contract["mechanic"]["new_path"] == ["ORIGIN", "EXPERIENCE", "RETURN", "ORIGIN_PRIME"]
    assert contract["tranception"]["direction_order"] == DIRECTIONS

    parent = gate0.run()
    parent_pass = bool(parent["status"].startswith("PASS_KEEP") and parent["integrity_sha256"] == PARENT_RESULT_SHA)

    first = build_ribbon(parent, previous_state=None, generation=1)
    second = build_ribbon(parent, previous_state=first["origin_prime"], generation=2)
    controls = negative_controls(first)

    origin = first["origin"]
    prime1 = first["origin_prime"]
    prime2 = second["origin_prime"]

    position_same = bool(
        first["position"]["position_commitment"] == second["position"]["position_commitment"]
        and origin["position_commitment"] == prime1["position_commitment"] == prime2["position_commitment"]
    )
    state_changes = bool(
        origin["state_commitment"] != prime1["state_commitment"]
        and prime1["state_commitment"] != prime2["state_commitment"]
        and origin["state_commitment"] != prime2["state_commitment"]
    )
    lineage_exact = bool(
        prime1["previous_state_commitment"] == origin["state_commitment"]
        and prime2["previous_state_commitment"] == prime1["state_commitment"]
        and prime1["generation"] == 1 and prime2["generation"] == 2
    )
    technical_unchanged = bool(
        first["position"]["technical_verdict"] == parent["FORWARD"]["status"]
        and second["position"]["technical_verdict"] == parent["FORWARD"]["status"]
        and parent["gates"]["FORWARD_AGAIN_exact_projection"]
    )

    gates = {
        "parent_gate0_must_pass_unchanged": parent_pass,
        "position_commitment_return_equals_origin": position_same,
        "origin_prime_state_commitment_differs_from_origin": state_changes,
        "origin_prime_binds_exact_origin_state": lineage_exact,
        "origin_prime_binds_exact_ordered_history": bool(first["verified"] and second["verified"]),
        "origin_prime_binds_exact_return_position": bool(first["verified"] and position_same),
        "history_bitflip_must_reject": controls["history_bitflip_rejected"],
        "history_erasure_must_reject": controls["history_erasure_rejected"],
        "forced_origin_state_reuse_must_reject": controls["forced_origin_state_reuse_rejected"],
        "return_position_mutation_must_reject": controls["return_position_mutation_rejected"],
        "second_identical_traversal_must_preserve_position_and_advance_state_generation": bool(position_same and lineage_exact and state_changes),
        "technical_sat_verdict_must_not_change": technical_unchanged,
        "P_VS_NP_OPEN": True,
    }
    passed = all(gates.values())

    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_ORIGIN_PRIME_RIBBON_STATE" if passed else "STOP_ORIGIN_PRIME_RIBBON_STATE_GATE_FAILURE",
        "parent": {"sha": PARENT_SHA, "result_integrity_sha256": PARENT_RESULT_SHA},
        "mechanic": "ORIGIN -> EXPERIENCE -> RETURN -> ORIGIN_PRIME",
        "legacy_cycle": "A -> B -> C -> A",
        "legacy_cycle_status": "REJECTED_AS_STATE_MODEL",
        "law": {
            "POSITION_APPROX_ORIGIN": position_same,
            "STATE_NOT_EQUAL_ORIGINAL_STATE": state_changes,
            "BACK_IS_VERIFICATION_NOT_ERASURE": True,
            "FORWARD_AGAIN_IS_POSITION_REPRODUCIBILITY_NOT_STATE_RESET": True,
        },
        "first_traversal": first,
        "second_traversal": second,
        "negative_controls": controls,
        "gates": gates,
        "technical_verdict": parent["FORWARD"]["status"],
        "scientific_boundary": contract["scientific_boundary"],
    }
    integrity = sha256(stable_bytes(result)).hexdigest()
    result["integrity_sha256"] = integrity
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
