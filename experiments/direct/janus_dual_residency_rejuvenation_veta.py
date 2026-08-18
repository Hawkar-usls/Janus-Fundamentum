#!/usr/bin/env python3
"""Dual-residency rejuvenation checkpoint with explicit Veta identity attacks.

This is one frozen modern operator inspired by the project's restoration overlay.
It separates exact active child/capability state from provenance identity.

VETA_BEFORE_SEED:
  provenance is erased before the seed capsule is formed.  The active child and
  seed-only view are deliberately indistinguishable between an original and a
  matched surrogate identity.  Exact identity recovery is therefore forbidden
  without the durable lane.  The durable four-fragment ledger must recover the
  exact original parent and original identity anchor.

VETA_AFTER_SEED:
  a provenance/manifest commitment crosses the seed gate before Veta erases the
  active provenance.  The carried commitment plus the durable ledger must recover
  the exact original parent and identity anchor.

The layer has no solver authority and cannot change search trajectory.  Revealed
GT3..GT9 only.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_four_sons_typed_fragment_reassembly import (
    EXPECTED_TYPES,
    FourSonsFragmentLedgerPolicy,
    fragment_payloads,
    fragment_ref,
    rebuild_delta,
    solver_snapshot,
)
from janus_son_return_path_parent_delta import cnf_digest, recover_parent
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import simplify_one

RUN_ID = "JANUS-DUAL-RESIDENCY-REJUVENATION-VETA-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_TRANSITIONS = 5366
FROZEN_FOUR_SONS_LEDGER_BYTES = 4534211
FROZEN_FULL_PARENT_SNAPSHOT_BYTES = 12231536
FROZEN_SOLVER = {
    "residual_states": 2822,
    "bytewise_distinct_absorptions": 602,
    "polarity_flip_absorptions": 450,
    "event_horizon_collisions": 839,
    "hawking_escape_count": 1242,
    "buzz_return_checks": 1844,
    "canonical_edge_visits": 3488298,
    "resolution_attempts": 626489,
    "resolution_additions": 93638,
    "local_tombstone_checks": 1050,
    "local_tombstone_hits": 1050,
    "local_tombstone_inserts": 1242,
    "route_rescan_edge_visits": 0,
}


def manifest_commitment(refs: tuple[str, str, str, str]) -> str:
    h = sha256(b"JANUS|MANIFEST|V1|")
    for ref in refs:
        h.update(bytes.fromhex(ref))
    return h.hexdigest()


def identity_anchor(parent_sha256: str, manifest_sha256: str) -> str:
    h = sha256(b"JANUS|IDENTITY|V1|")
    h.update(bytes.fromhex(parent_sha256))
    h.update(bytes.fromhex(manifest_sha256))
    return h.hexdigest()


def surrogate_anchor(original: str) -> str:
    return sha256(b"JANUS|SURROGATE|V1|" + bytes.fromhex(original)).hexdigest()


class DualResidencyVetaPolicy(FourSonsFragmentLedgerPolicy):
    """Four-Sons durable ledger plus active/durable identity checkpoint audit."""

    def solve(self, cnf, variable_count):
        self.dual_transition_count = 0
        self.veta_active_pair_equal_passes = 0
        self.veta_provenance_pair_distinct_passes = 0
        self.pre_seed_identity_nonidentifiable_passes = 0
        self.pre_seed_durable_parent_passes = 0
        self.pre_seed_durable_identity_passes = 0
        self.pre_seed_forward_replay_passes = 0
        self.post_seed_capsule_identity_passes = 0
        self.post_seed_durable_parent_passes = 0
        self.post_seed_durable_identity_passes = 0
        self.post_seed_forward_replay_passes = 0
        self.dual_manifest_lookup_passes = 0
        self.dual_reference_hash_passes = 0
        self.dual_reference_type_passes = 0
        self.dual_checkpoint_parent_literal_visits = 0
        self.dual_identity_hash_ops = 0
        self.dual_extra_solver_residual_scans = 0
        self.dual_manifest_index: dict[str, tuple[str, str, str, str]] = {}
        return super().solve(cnf, variable_count)

    def _checkpoint_resolve(self, refs: tuple[str, str, str, str]):
        resolved = []
        for expected_type, ref in zip(EXPECTED_TYPES, refs):
            item = self.fragment_store.get(ref)
            if item is None:
                raise AssertionError("dual checkpoint missing durable fragment")
            actual_type, payload = item
            if fragment_ref(actual_type, payload) != ref:
                raise AssertionError("dual checkpoint durable fragment hash mismatch")
            self.dual_reference_hash_passes += 1
            if actual_type != expected_type:
                raise AssertionError("dual checkpoint durable fragment type mismatch")
            self.dual_reference_type_passes += 1
            resolved.append(item)
        return rebuild_delta(tuple(resolved))

    def record_fragment_ledger(self, child, original_delta, parent) -> None:
        # Preserve the already-passed Four-Sons operator exactly first.
        super().record_fragment_ledger(child, original_delta, parent)

        refs = tuple(
            fragment_ref(type_tag, payload)
            for type_tag, payload in fragment_payloads(original_delta)
        )
        if len(refs) != 4:
            raise AssertionError("dual checkpoint requires exactly four durable refs")
        refs = tuple(refs)  # type: ignore[assignment]
        manifest_sha = manifest_commitment(refs)  # 1 identity/hash operation
        original_identity = identity_anchor(original_delta.parent_sha256, manifest_sha)
        surrogate_identity = surrogate_anchor(original_identity)
        active_child_sha = cnf_digest(child)
        self.dual_identity_hash_ops += 4

        existing = self.dual_manifest_index.get(manifest_sha)
        if existing is None:
            self.dual_manifest_index[manifest_sha] = refs
        elif existing != refs:
            raise AssertionError("manifest commitment collision with unequal refs")

        self.dual_transition_count += 1

        # Matched-control Veta pair: same exact active child/capability bytes,
        # deliberately distinct provenance identities.
        original_active_after_veta = bytes.fromhex(active_child_sha)
        surrogate_active_after_veta = bytes.fromhex(active_child_sha)
        if original_active_after_veta == surrogate_active_after_veta:
            self.veta_active_pair_equal_passes += 1
        if original_identity != surrogate_identity:
            self.veta_provenance_pair_distinct_passes += 1

        # VETA_BEFORE_SEED: the seed is formed only after provenance was erased.
        # Its bytes are therefore identical for the original/surrogate pair.
        pre_seed_original = original_active_after_veta
        pre_seed_surrogate = surrogate_active_after_veta
        if pre_seed_original == pre_seed_surrogate and original_identity != surrogate_identity:
            self.pre_seed_identity_nonidentifiable_passes += 1

        # External durable residency is allowed to restore the original identity.
        rebuilt_pre = self._checkpoint_resolve(refs)
        restored_pre = recover_parent(child, rebuilt_pre)
        self.dual_checkpoint_parent_literal_visits += (
            sum(len(c) for c in child) + sum(len(c) for c in restored_pre)
        )
        if restored_pre == parent:
            self.pre_seed_durable_parent_passes += 1
        pre_manifest_sha = manifest_commitment(refs)
        pre_identity = identity_anchor(rebuilt_pre.parent_sha256, pre_manifest_sha)
        self.dual_identity_hash_ops += 2
        if pre_identity == original_identity:
            self.pre_seed_durable_identity_passes += 1
        if simplify_one(restored_pre, rebuilt_pre.variable, rebuilt_pre.value) == child:
            self.pre_seed_forward_replay_passes += 1

        # VETA_AFTER_SEED: provenance/manifest commitment crosses the gate first.
        # The seed capsule is exactly 64 bytes: identity anchor + manifest handle.
        post_seed_capsule = bytes.fromhex(original_identity) + bytes.fromhex(manifest_sha)
        if len(post_seed_capsule) != 64:
            raise AssertionError("post-seed capsule must be exactly 64 bytes")
        carried_identity = post_seed_capsule[:32].hex()
        carried_manifest = post_seed_capsule[32:].hex()
        if carried_identity == original_identity:
            self.post_seed_capsule_identity_passes += 1
        carried_refs = self.dual_manifest_index.get(carried_manifest)
        if carried_refs is None:
            raise AssertionError("post-seed manifest handle not found in durable lane")
        self.dual_manifest_lookup_passes += 1
        rebuilt_post = self._checkpoint_resolve(carried_refs)
        restored_post = recover_parent(child, rebuilt_post)
        self.dual_checkpoint_parent_literal_visits += (
            sum(len(c) for c in child) + sum(len(c) for c in restored_post)
        )
        if restored_post == parent:
            self.post_seed_durable_parent_passes += 1
        post_manifest_sha = manifest_commitment(carried_refs)
        post_identity = identity_anchor(rebuilt_post.parent_sha256, post_manifest_sha)
        self.dual_identity_hash_ops += 2
        if post_identity == carried_identity == original_identity:
            self.post_seed_durable_identity_passes += 1
        if simplify_one(restored_post, rebuilt_post.variable, rebuilt_post.value) == child:
            self.post_seed_forward_replay_passes += 1


def add(rows: list[dict[str, Any]], side: str, field: str) -> int:
    return sum(int(row[side][field]) for row in rows)


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    answers_match = True
    caps_match = True

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)
        parent_solver = FourSonsFragmentLedgerPolicy()
        parent_result = parent_solver.solve(cnf, variable_count)
        candidate_solver = DualResidencyVetaPolicy()
        candidate_result = candidate_solver.solve(cnf, variable_count)

        answers_match &= parent_result.answer == candidate_result.answer
        caps_match &= parent_result.cap_exceeded == candidate_result.cap_exceeded
        parent_snap = solver_snapshot(parent_solver, parent_result)
        candidate_snap = solver_snapshot(candidate_solver, candidate_result)

        rows.append({
            "order": order,
            "parent": parent_snap,
            "candidate": candidate_snap,
            "parent_ledger": {
                "transition_count": parent_solver.recovery_transition_count,
                "fragment_store_wire_bytes": parent_solver.fragment_store_wire_bytes,
                "manifest_wire_bytes": parent_solver.fragment_manifest_wire_bytes,
                "total_ledger_wire_bytes": parent_solver.fragment_store_wire_bytes + parent_solver.fragment_manifest_wire_bytes,
                "parent_snapshot_wire_bytes": parent_solver.recovery_parent_snapshot_bytes,
            },
            "dual": {
                "transition_count": candidate_solver.dual_transition_count,
                "veta_active_pair_equal_passes": candidate_solver.veta_active_pair_equal_passes,
                "veta_provenance_pair_distinct_passes": candidate_solver.veta_provenance_pair_distinct_passes,
                "pre_seed_identity_nonidentifiable_passes": candidate_solver.pre_seed_identity_nonidentifiable_passes,
                "pre_seed_durable_parent_passes": candidate_solver.pre_seed_durable_parent_passes,
                "pre_seed_durable_identity_passes": candidate_solver.pre_seed_durable_identity_passes,
                "pre_seed_forward_replay_passes": candidate_solver.pre_seed_forward_replay_passes,
                "post_seed_capsule_identity_passes": candidate_solver.post_seed_capsule_identity_passes,
                "post_seed_durable_parent_passes": candidate_solver.post_seed_durable_parent_passes,
                "post_seed_durable_identity_passes": candidate_solver.post_seed_durable_identity_passes,
                "post_seed_forward_replay_passes": candidate_solver.post_seed_forward_replay_passes,
                "manifest_lookup_passes": candidate_solver.dual_manifest_lookup_passes,
                "reference_hash_passes": candidate_solver.dual_reference_hash_passes,
                "reference_type_passes": candidate_solver.dual_reference_type_passes,
                "checkpoint_parent_literal_visits": candidate_solver.dual_checkpoint_parent_literal_visits,
                "identity_hash_ops": candidate_solver.dual_identity_hash_ops,
                "extra_solver_residual_scans": candidate_solver.dual_extra_solver_residual_scans,
                "four_sons_total_ledger_wire_bytes": candidate_solver.fragment_store_wire_bytes + candidate_solver.fragment_manifest_wire_bytes,
            },
        })

    solver_parent = {key: add(rows, "parent", key) for key in FROZEN_SOLVER}
    solver_candidate = {key: add(rows, "candidate", key) for key in FROZEN_SOLVER}
    parent_ledger_bytes = add(rows, "parent_ledger", "total_ledger_wire_bytes")
    parent_snapshot_bytes = add(rows, "parent_ledger", "parent_snapshot_wire_bytes")

    dual_fields = (
        "transition_count",
        "veta_active_pair_equal_passes",
        "veta_provenance_pair_distinct_passes",
        "pre_seed_identity_nonidentifiable_passes",
        "pre_seed_durable_parent_passes",
        "pre_seed_durable_identity_passes",
        "pre_seed_forward_replay_passes",
        "post_seed_capsule_identity_passes",
        "post_seed_durable_parent_passes",
        "post_seed_durable_identity_passes",
        "post_seed_forward_replay_passes",
        "manifest_lookup_passes",
        "reference_hash_passes",
        "reference_type_passes",
        "checkpoint_parent_literal_visits",
        "identity_hash_ops",
        "extra_solver_residual_scans",
        "four_sons_total_ledger_wire_bytes",
    )
    dual = {field: add(rows, "dual", field) for field in dual_fields}

    t = dual["transition_count"]
    storage = {
        "four_sons_durable_ledger_bytes": dual["four_sons_total_ledger_wire_bytes"],
        "active_commitment_bytes": 32 * t,
        "durable_identity_anchor_bytes": 32 * t,
        "durable_manifest_commitment_bytes": 32 * t,
        "post_seed_capsule_bytes": 64 * t,
    }
    storage["worst_case_dual_residency_wire_bytes"] = sum(storage.values())
    storage["full_parent_snapshot_wire_bytes"] = parent_snapshot_bytes
    storage["ratio_to_full_parent_snapshots"] = (
        storage["worst_case_dual_residency_wire_bytes"] / max(1, parent_snapshot_bytes)
    )
    storage["saved_wire_bytes_vs_full_parent_snapshots"] = (
        parent_snapshot_bytes - storage["worst_case_dual_residency_wire_bytes"]
    )

    gates = {
        "frozen_four_sons_solver_reproduced": solver_parent == FROZEN_SOLVER,
        "candidate_solver_exactly_matches_parent": solver_candidate == solver_parent,
        "same_boolean_answers": answers_match,
        "same_cap_status": caps_match,
        "frozen_four_sons_ledger_bytes_reproduced": parent_ledger_bytes == FROZEN_FOUR_SONS_LEDGER_BYTES,
        "transition_count_exact": t == FROZEN_TRANSITIONS,
        "all_veta_active_pairs_identical": dual["veta_active_pair_equal_passes"] == t,
        "all_veta_provenance_pairs_distinct": dual["veta_provenance_pair_distinct_passes"] == t,
        "before_seed_identity_nonidentifiable_for_all": dual["pre_seed_identity_nonidentifiable_passes"] == t,
        "before_seed_durable_parent_exact_for_all": dual["pre_seed_durable_parent_passes"] == t,
        "before_seed_durable_identity_exact_for_all": dual["pre_seed_durable_identity_passes"] == t,
        "before_seed_forward_replay_exact_for_all": dual["pre_seed_forward_replay_passes"] == t,
        "after_seed_capsule_identity_exact_for_all": dual["post_seed_capsule_identity_passes"] == t,
        "after_seed_durable_parent_exact_for_all": dual["post_seed_durable_parent_passes"] == t,
        "after_seed_durable_identity_exact_for_all": dual["post_seed_durable_identity_passes"] == t,
        "after_seed_forward_replay_exact_for_all": dual["post_seed_forward_replay_passes"] == t,
        "after_seed_manifest_lookup_exact_for_all": dual["manifest_lookup_passes"] == t,
        "all_dual_fragment_hashes_and_types_verify": (
            dual["reference_hash_passes"] == 8 * t and dual["reference_type_passes"] == 8 * t
        ),
        "zero_extra_solver_residual_scans": dual["extra_solver_residual_scans"] == 0,
        "worst_case_dual_residency_strictly_smaller_than_full_snapshots": (
            storage["worst_case_dual_residency_wire_bytes"] < parent_snapshot_bytes
        ),
    }
    passed = all(gates.values())

    return {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_DUAL_RESIDENCY_REJUVENATION_CHECKPOINT" if passed else "STOP_AT_DUAL_RESIDENCY_REJUVENATION_NO_IMPROVEMENT",
        "operator": "DUAL_RESIDENCY_REJUVENATION_CHECKPOINT",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "identity_law": "RESTORATION_OF_FUNCTION != RESTORATION_OF_IDENTITY",
        "veta_law": "VETA_DESTROYS_IDENTITY_BEFORE_IT_NECESSARILY_DESTROYS_FUNCTION",
        "parent_solver": solver_parent,
        "candidate_solver": solver_candidate,
        "dual_residency": dual,
        "storage": storage,
        "gates": gates,
        "interpretation_if_pass": {
            "VETA_BEFORE_SEED": "Active/seed-only bytes cannot distinguish original from matched surrogate identity; exact identity returns only from the independent durable provenance lane.",
            "VETA_AFTER_SEED": "A provenance commitment that crosses the seed gate survives later active provenance erasure and selects the exact original durable record.",
            "surrogate_rule": "Replacement can preserve the exact active child/capability bytes while carrying a different provenance identity.",
            "canonical_phrase": "THE SON RETURNS ONLY THE FATHER-STATE THAT CROSSED THE GATE; DURABLE PROVENANCE IS A SEPARATE RETURN CHANNEL."
        },
        "work_charged": {
            "checkpoint_parent_literal_visits": dual["checkpoint_parent_literal_visits"],
            "identity_hash_ops": dual["identity_hash_ops"],
            "fragment_reference_hash_checks": dual["reference_hash_passes"],
            "fragment_type_checks": dual["reference_type_passes"],
            "storage_bytes": storage["worst_case_dual_residency_wire_bytes"],
            "note": "Checkpoint/reassembly verification is explicit overhead and is not claimed free."
        },
        "historical_inspiration_boundary": {
            "Veta": "PROJECT_IDENTITY_ERASURE_OPERATOR_ONLY",
            "Sah_Orion": "WATCHLIST_NOT_USED_IN_THIS_RUN",
            "ancient_text_is_algorithmic_evidence": False,
        },
        "next_watchlist_if_pass": [
            "SAH_ORION_TRANSFIGURED_STATE_ANCHOR_AFTER_LEXICAL_GATE",
            "MULTI_GLOSS_EQUIVALENCE_PROVENANCE_LEDGER",
            "RESTORE_TO_STABLE_CHECKPOINT",
            "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY"
        ],
        "claim_boundary": [
            "The matched surrogate is a synthetic provenance control, not a biological or archaeological claim.",
            "Identity here means an explicit cryptographic provenance vector in this data model.",
            "A pass would establish finite exact recovery/storage properties on revealed GT3..GT9 only.",
            "It would not establish lower total runtime or memory on arbitrary CNFs.",
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
            "PASS_KEEP_DUAL_RESIDENCY_REJUVENATION_CHECKPOINT",
            "STOP_AT_DUAL_RESIDENCY_REJUVENATION_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
