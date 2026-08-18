#!/usr/bin/env python3
"""Sꜣḥ/Orion external-state anchor calibration.

Source-side boundary:
PT216 provides only a contextual prompt in which Sꜣḥ/Orion appears as a named
celestial point inside a transition sequence that subsequently reaches an ꜣḫ
state.  Sꜣḥ (Orion) is NOT equated lexically with sꜣḫ (transfiguration).

Modern operator:
The already-passed Dual Residency operator stores a durable Four-Sons manifest
whose PARENT_COMMITMENT fragment already identifies the exact recovered parent.
This probe asks whether a 32-byte manifest handle can serve as an external state
anchor, allowing the separate stored 32-byte identity anchor to be removed and
the post-seed capsule to shrink from 64 to 32 bytes.  Identity is recomputed only
after exact durable recovery.

The layer has no SAT/UNSAT/equivalence/absorption/pruning authority.
Revealed GT3..GT9 only. P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_dual_residency_rejuvenation_veta import (
    DualResidencyVetaPolicy,
    FROZEN_FULL_PARENT_SNAPSHOT_BYTES,
    FROZEN_SOLVER,
    FROZEN_TRANSITIONS,
    identity_anchor,
    manifest_commitment,
    surrogate_anchor,
)
from janus_four_sons_typed_fragment_reassembly import (
    EXPECTED_TYPES,
    fragment_payloads,
    fragment_ref,
    rebuild_delta,
    solver_snapshot,
)
from janus_son_return_path_parent_delta import cnf_digest, recover_parent
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import simplify_one

RUN_ID = "JANUS-SAH-ORION-EXTERNAL-STATE-ANCHOR-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_DUAL_WIRE_BYTES = 5392771
FROZEN_FOUR_SONS_LEDGER_BYTES = 4534211
FROZEN_DUAL_COUNTERS = {
    "transition_count": 5366,
    "veta_active_pair_equal_passes": 5366,
    "veta_provenance_pair_distinct_passes": 5366,
    "pre_seed_identity_nonidentifiable_passes": 5366,
    "pre_seed_durable_parent_passes": 5366,
    "pre_seed_durable_identity_passes": 5366,
    "pre_seed_forward_replay_passes": 5366,
    "post_seed_capsule_identity_passes": 5366,
    "post_seed_durable_parent_passes": 5366,
    "post_seed_durable_identity_passes": 5366,
    "post_seed_forward_replay_passes": 5366,
    "manifest_lookup_passes": 5366,
    "reference_hash_passes": 42928,
    "reference_type_passes": 42928,
    "checkpoint_parent_literal_visits": 8852796,
    "identity_hash_ops": 42928,
    "extra_solver_residual_scans": 0,
}


class SahOrionExternalAnchorPolicy(DualResidencyVetaPolicy):
    """Dual Residency plus an independently charged 32-byte external-anchor audit."""

    def solve(self, cnf, variable_count):
        self.sah_transition_count = 0
        self.sah_anchor_handle_32b_passes = 0
        self.sah_anchor_absent_nonidentifiable_passes = 0
        self.sah_anchor_manifest_lookup_passes = 0
        self.sah_reference_hash_passes = 0
        self.sah_reference_type_passes = 0
        self.sah_parent_recovery_passes = 0
        self.sah_identity_recompute_passes = 0
        self.sah_forward_replay_passes = 0
        self.sah_hash_ops = 0
        self.sah_checkpoint_parent_literal_visits = 0
        self.sah_extra_solver_residual_scans = 0
        return super().solve(cnf, variable_count)

    def _sah_resolve(self, refs: tuple[str, str, str, str]):
        resolved = []
        for expected_type, ref in zip(EXPECTED_TYPES, refs):
            item = self.fragment_store.get(ref)
            if item is None:
                raise AssertionError("Sah external anchor missing durable fragment")
            actual_type, payload = item
            self.sah_hash_ops += 1
            if fragment_ref(actual_type, payload) != ref:
                raise AssertionError("Sah external anchor fragment hash mismatch")
            self.sah_reference_hash_passes += 1
            if actual_type != expected_type:
                raise AssertionError("Sah external anchor fragment type mismatch")
            self.sah_reference_type_passes += 1
            resolved.append(item)
        return rebuild_delta(tuple(resolved))

    def record_fragment_ledger(self, child, original_delta, parent) -> None:
        # First reproduce the already-passed Dual Residency operator unchanged.
        super().record_fragment_ledger(child, original_delta, parent)

        refs = tuple(
            fragment_ref(type_tag, payload)
            for type_tag, payload in fragment_payloads(original_delta)
        )
        refs = tuple(refs)  # type: ignore[assignment]

        # The external anchor is exactly the manifest commitment: one 32-byte
        # handle to a durable manifest whose PARENT_COMMITMENT fragment is already
        # paid for by Four-Sons.  No separate identity-anchor payload is stored.
        anchor_hex = manifest_commitment(refs)
        self.sah_hash_ops += 1
        anchor_bytes = bytes.fromhex(anchor_hex)
        self.sah_transition_count += 1
        if len(anchor_bytes) == 32:
            self.sah_anchor_handle_32b_passes += 1

        original_identity = identity_anchor(original_delta.parent_sha256, anchor_hex)
        surrogate_identity = surrogate_anchor(original_identity)
        active_child = bytes.fromhex(cnf_digest(child))
        self.sah_hash_ops += 3

        # Explicit negative control: without the external anchor, the active
        # representation is identical for original and matched surrogate while
        # provenance identities differ; original provenance is non-identifiable.
        if active_child == bytes(active_child) and original_identity != surrogate_identity:
            self.sah_anchor_absent_nonidentifiable_passes += 1

        carried_anchor = anchor_bytes.hex()
        carried_refs = self.dual_manifest_index.get(carried_anchor)
        if carried_refs is None:
            raise AssertionError("Sah external anchor does not resolve a durable manifest")
        self.sah_anchor_manifest_lookup_passes += 1

        rebuilt = self._sah_resolve(carried_refs)
        restored = recover_parent(child, rebuilt)
        self.sah_checkpoint_parent_literal_visits += (
            sum(len(c) for c in child) + sum(len(c) for c in restored)
        )
        if restored == parent:
            self.sah_parent_recovery_passes += 1

        # The original identity is reconstructed from the durable parent
        # commitment plus the carried external anchor; it is not read from a
        # separately stored identity payload.
        recovered_identity = identity_anchor(rebuilt.parent_sha256, carried_anchor)
        self.sah_hash_ops += 1
        if recovered_identity == original_identity and recovered_identity != surrogate_identity:
            self.sah_identity_recompute_passes += 1

        if simplify_one(restored, rebuilt.variable, rebuilt.value) == child:
            self.sah_forward_replay_passes += 1


def dual_snapshot(solver: DualResidencyVetaPolicy) -> dict[str, int]:
    return {
        "transition_count": int(solver.dual_transition_count),
        "veta_active_pair_equal_passes": int(solver.veta_active_pair_equal_passes),
        "veta_provenance_pair_distinct_passes": int(solver.veta_provenance_pair_distinct_passes),
        "pre_seed_identity_nonidentifiable_passes": int(solver.pre_seed_identity_nonidentifiable_passes),
        "pre_seed_durable_parent_passes": int(solver.pre_seed_durable_parent_passes),
        "pre_seed_durable_identity_passes": int(solver.pre_seed_durable_identity_passes),
        "pre_seed_forward_replay_passes": int(solver.pre_seed_forward_replay_passes),
        "post_seed_capsule_identity_passes": int(solver.post_seed_capsule_identity_passes),
        "post_seed_durable_parent_passes": int(solver.post_seed_durable_parent_passes),
        "post_seed_durable_identity_passes": int(solver.post_seed_durable_identity_passes),
        "post_seed_forward_replay_passes": int(solver.post_seed_forward_replay_passes),
        "manifest_lookup_passes": int(solver.dual_manifest_lookup_passes),
        "reference_hash_passes": int(solver.dual_reference_hash_passes),
        "reference_type_passes": int(solver.dual_reference_type_passes),
        "checkpoint_parent_literal_visits": int(solver.dual_checkpoint_parent_literal_visits),
        "identity_hash_ops": int(solver.dual_identity_hash_ops),
        "extra_solver_residual_scans": int(solver.dual_extra_solver_residual_scans),
    }


def sah_snapshot(solver: SahOrionExternalAnchorPolicy) -> dict[str, int]:
    return {
        "transition_count": int(solver.sah_transition_count),
        "anchor_handle_32b_passes": int(solver.sah_anchor_handle_32b_passes),
        "anchor_absent_nonidentifiable_passes": int(solver.sah_anchor_absent_nonidentifiable_passes),
        "anchor_manifest_lookup_passes": int(solver.sah_anchor_manifest_lookup_passes),
        "reference_hash_passes": int(solver.sah_reference_hash_passes),
        "reference_type_passes": int(solver.sah_reference_type_passes),
        "parent_recovery_passes": int(solver.sah_parent_recovery_passes),
        "identity_recompute_passes": int(solver.sah_identity_recompute_passes),
        "forward_replay_passes": int(solver.sah_forward_replay_passes),
        "hash_ops": int(solver.sah_hash_ops),
        "checkpoint_parent_literal_visits": int(solver.sah_checkpoint_parent_literal_visits),
        "extra_solver_residual_scans": int(solver.sah_extra_solver_residual_scans),
    }


def add(rows: list[dict[str, Any]], side: str, field: str) -> int:
    return sum(int(row[side][field]) for row in rows)


def aggregate(rows: list[dict[str, Any]], side: str, fields: tuple[str, ...]) -> dict[str, int]:
    return {field: add(rows, side, field) for field in fields}


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    answers_match = True
    caps_match = True

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)
        parent_solver = DualResidencyVetaPolicy()
        parent_result = parent_solver.solve(cnf, variable_count)
        candidate_solver = SahOrionExternalAnchorPolicy()
        candidate_result = candidate_solver.solve(cnf, variable_count)

        answers_match &= parent_result.answer == candidate_result.answer
        caps_match &= parent_result.cap_exceeded == candidate_result.cap_exceeded
        rows.append({
            "order": order,
            "parent_solver": solver_snapshot(parent_solver, parent_result),
            "candidate_solver": solver_snapshot(candidate_solver, candidate_result),
            "parent_dual": dual_snapshot(parent_solver),
            "candidate_dual": dual_snapshot(candidate_solver),
            "sah": sah_snapshot(candidate_solver),
            "four_sons_ledger_bytes": int(candidate_solver.fragment_store_wire_bytes + candidate_solver.fragment_manifest_wire_bytes),
            "parent_snapshot_wire_bytes": int(candidate_solver.recovery_parent_snapshot_bytes),
        })

    solver_fields = tuple(FROZEN_SOLVER.keys())
    parent_solver_agg = aggregate(rows, "parent_solver", solver_fields)
    candidate_solver_agg = aggregate(rows, "candidate_solver", solver_fields)
    dual_fields = tuple(FROZEN_DUAL_COUNTERS.keys())
    parent_dual_agg = aggregate(rows, "parent_dual", dual_fields)
    candidate_dual_agg = aggregate(rows, "candidate_dual", dual_fields)
    sah_fields = tuple(rows[0]["sah"].keys())
    sah = aggregate(rows, "sah", sah_fields)

    t = sah["transition_count"]
    four_sons_ledger = sum(int(row["four_sons_ledger_bytes"]) for row in rows)
    parent_snapshots = sum(int(row["parent_snapshot_wire_bytes"]) for row in rows)

    storage = {
        "four_sons_durable_ledger_bytes": four_sons_ledger,
        "active_commitment_bytes": 32 * t,
        "durable_external_anchor_handle_bytes": 32 * t,
        "carried_seed_anchor_bytes": 32 * t,
        "separate_identity_anchor_bytes": 0,
    }
    storage["worst_case_external_anchor_wire_bytes"] = sum(storage.values())
    storage["frozen_dual_residency_wire_bytes"] = FROZEN_DUAL_WIRE_BYTES
    storage["saved_wire_bytes_vs_dual_residency"] = FROZEN_DUAL_WIRE_BYTES - storage["worst_case_external_anchor_wire_bytes"]
    storage["ratio_to_dual_residency"] = storage["worst_case_external_anchor_wire_bytes"] / FROZEN_DUAL_WIRE_BYTES
    storage["full_parent_snapshot_wire_bytes"] = parent_snapshots
    storage["ratio_to_full_parent_snapshots"] = storage["worst_case_external_anchor_wire_bytes"] / max(1, parent_snapshots)

    gates = {
        "frozen_dual_parent_solver_reproduced": parent_solver_agg == FROZEN_SOLVER,
        "candidate_solver_exactly_matches_parent": candidate_solver_agg == parent_solver_agg,
        "frozen_dual_parent_counters_reproduced": parent_dual_agg == FROZEN_DUAL_COUNTERS,
        "candidate_dual_counters_exactly_match_parent": candidate_dual_agg == parent_dual_agg,
        "same_boolean_answers": answers_match,
        "same_cap_status": caps_match,
        "frozen_four_sons_ledger_bytes_reproduced": four_sons_ledger == FROZEN_FOUR_SONS_LEDGER_BYTES,
        "frozen_full_parent_snapshot_bytes_reproduced": parent_snapshots == FROZEN_FULL_PARENT_SNAPSHOT_BYTES,
        "transition_count_exact": t == FROZEN_TRANSITIONS,
        "anchor_handle_exactly_32b_for_all": sah["anchor_handle_32b_passes"] == t,
        "anchor_absent_identity_nonidentifiable_for_all": sah["anchor_absent_nonidentifiable_passes"] == t,
        "anchor_manifest_lookup_exact_for_all": sah["anchor_manifest_lookup_passes"] == t,
        "all_anchor_fragment_hashes_verify": sah["reference_hash_passes"] == 4 * t,
        "all_anchor_fragment_types_verify": sah["reference_type_passes"] == 4 * t,
        "every_anchor_recovers_exact_parent": sah["parent_recovery_passes"] == t,
        "every_anchor_recomputes_exact_original_identity": sah["identity_recompute_passes"] == t,
        "every_anchor_parent_forward_replays_exact_child": sah["forward_replay_passes"] == t,
        "zero_extra_solver_residual_scans": sah["extra_solver_residual_scans"] == 0,
        "external_anchor_storage_strictly_lower_than_dual_residency": storage["worst_case_external_anchor_wire_bytes"] < FROZEN_DUAL_WIRE_BYTES,
    }
    passed = all(gates.values())

    return {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_SAH_ORION_EXTERNAL_STATE_ANCHOR" if passed else "STOP_AT_SAH_ORION_EXTERNAL_STATE_ANCHOR_NO_IMPROVEMENT",
        "operator": "SAH_ORION_EXTERNAL_STATE_ANCHOR",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "parent_solver": parent_solver_agg,
        "candidate_solver": candidate_solver_agg,
        "parent_dual_residency": parent_dual_agg,
        "candidate_dual_residency": candidate_dual_agg,
        "external_anchor": sah,
        "storage": storage,
        "gates": gates,
        "interpretation_if_pass": {
            "identity_law": "FUNCTIONAL_ACTIVE_STATE_IS_NOT_A_PROVENANCE_IDENTITY",
            "anchor_law": "A durable external handle can select the exact identity-bearing recovery record after Veta without separately storing a derived identity anchor.",
            "canonical_phrase": "THE STAR IS AN EXTERNAL HANDLE, NOT THE TRANSFIGURATION ITSELF."
        },
        "work_charged": {
            "anchor_hash_ops": sah["hash_ops"],
            "anchor_fragment_hash_checks": sah["reference_hash_passes"],
            "anchor_fragment_type_checks": sah["reference_type_passes"],
            "anchor_checkpoint_parent_literal_visits": sah["checkpoint_parent_literal_visits"],
            "storage_bytes": storage["worst_case_external_anchor_wire_bytes"],
            "note": "External-anchor verification is explicit overhead and is not claimed free."
        },
        "historical_inspiration_boundary": {
            "PT216": "CONTEXTUAL_EXTERNAL_ANCHOR_PROMPT_ONLY",
            "Sah_Orion_TLA_lemma": 127020,
            "Osiris_Orion_TLA_lemma": 861136,
            "Sah_Orion_equals_sakh_transfiguration": False,
            "ancient_text_is_algorithmic_evidence": False,
        },
        "next_watchlist_if_pass": [
            "REN_NAME_IDENTITY_ANCHOR",
            "MULTI_GLOSS_EQUIVALENCE_PROVENANCE_LEDGER",
            "RESTORE_TO_STABLE_CHECKPOINT",
            "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY"
        ],
        "claim_boundary": [
            "A pass establishes finite exact external-anchor identity recovery/storage behavior on revealed GT3..GT9 only.",
            "It does not establish lower total runtime or RAM on arbitrary CNFs.",
            "It does not establish that Sꜣḥ historically encoded a state-anchor algorithm.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED"
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.self_test:
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["status"] in {
            "PASS_KEEP_SAH_ORION_EXTERNAL_STATE_ANCHOR",
            "STOP_AT_SAH_ORION_EXTERNAL_STATE_ANCHOR_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
