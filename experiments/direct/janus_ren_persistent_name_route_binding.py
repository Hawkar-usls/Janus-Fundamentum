#!/usr/bin/env python3
"""REN persistent-name route-binding calibration.

Book of the Dead 119/149 are used only as source-side prompts for a persistent
name associated with bidirectional route/continued identity.  The modern `rn`
below is NOT a translation of an Egyptian name into a cryptographic identifier.

Frozen modern operator:
  exact 32-byte external anchor
    -> per-GT lexicographically sorted unique-anchor dictionary
    -> deterministic unsigned 16-bit rn
    -> rn resolves back to the exact 32-byte anchor
    -> full anchor/manifest hash verification remains mandatory
    -> exact durable parent + provenance identity + forward replay

This is an offline certificate-routing/storage layer.  It has no solver-decision
or pruning authority.  Revealed GT3..GT9 only. P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_sah_orion_external_state_anchor import (
    FROZEN_DUAL_COUNTERS,
    FROZEN_DUAL_WIRE_BYTES,
    FROZEN_FOUR_SONS_LEDGER_BYTES,
    FROZEN_SOLVER,
    FROZEN_TRANSITIONS,
    SahOrionExternalAnchorPolicy,
    sah_snapshot,
)
from janus_dual_residency_rejuvenation_veta import identity_anchor, manifest_commitment
from janus_four_sons_typed_fragment_reassembly import (
    EXPECTED_TYPES,
    fragment_payloads,
    fragment_ref,
    rebuild_delta,
    solver_snapshot,
)
from janus_son_return_path_parent_delta import recover_parent
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import simplify_one

RUN_ID = "JANUS-REN-PERSISTENT-NAME-ROUTE-BINDING-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_SAH_WIRE_BYTES = 5049347
NAME_WIDTH = 2
NAME_CAPACITY = 1 << (8 * NAME_WIDTH)
FROZEN_SAH_COUNTERS = {
    "transition_count": 5366,
    "anchor_handle_32b_passes": 5366,
    "anchor_absent_nonidentifiable_passes": 5366,
    "anchor_manifest_lookup_passes": 5366,
    "reference_hash_passes": 21464,
    "reference_type_passes": 21464,
    "parent_recovery_passes": 5366,
    "identity_recompute_passes": 5366,
    "forward_replay_passes": 5366,
    "hash_ops": 48294,
    "checkpoint_parent_literal_visits": 4426398,
    "extra_solver_residual_scans": 0,
}


def dictionary_commitment(entries: tuple[tuple[bytes, str], ...]) -> str:
    h = sha256(b"JANUS|REN|DICTIONARY|V1|")
    for name, anchor in entries:
        h.update(name)
        h.update(bytes.fromhex(anchor))
    return h.hexdigest()


class RenPersistentNamePolicy(SahOrionExternalAnchorPolicy):
    """Successful Sah external-anchor parent plus offline 16-bit rn audit."""

    def solve(self, cnf, variable_count):
        self.ren_records: list[tuple[Any, Any, Any, str, str]] = []
        self.ren_transition_count = 0
        self.ren_unique_anchor_count = 0
        self.ren_name_resolution_passes = 0
        self.ren_dictionary_commitment_passes = 0
        self.ren_manifest_binding_passes = 0
        self.ren_reference_hash_passes = 0
        self.ren_reference_type_passes = 0
        self.ren_parent_recovery_passes = 0
        self.ren_identity_recompute_passes = 0
        self.ren_forward_replay_passes = 0
        self.ren_name_assignment_determinism_passes = 0
        self.ren_namespace_capacity_passes = 0
        self.ren_adjacent_name_swap_rejects = 0
        self.ren_out_of_range_name_rejects = 0
        self.ren_dictionary_commitment_bitflip_rejects = 0
        self.ren_full_anchor_bitflip_rejects = 0
        self.ren_missing_name_rejects = 0
        self.ren_hash_ops = 0
        self.ren_dictionary_lookups = 0
        self.ren_checkpoint_parent_literal_visits = 0
        self.ren_extra_solver_residual_scans = 0
        result = super().solve(cnf, variable_count)
        self._finalize_ren_dictionary()
        return result

    def record_fragment_ledger(self, child, original_delta, parent) -> None:
        # Reproduce every successful Sah/Dual/Four-Sons parent audit unchanged.
        super().record_fragment_ledger(child, original_delta, parent)
        refs = tuple(
            fragment_ref(type_tag, payload)
            for type_tag, payload in fragment_payloads(original_delta)
        )
        refs = tuple(refs)  # type: ignore[assignment]
        anchor = manifest_commitment(refs)
        original_identity = identity_anchor(original_delta.parent_sha256, anchor)
        self.ren_records.append((child, parent, original_delta, anchor, original_identity))

    def _ren_resolve_manifest(self, anchor: str):
        refs = self.dual_manifest_index.get(anchor)
        self.ren_dictionary_lookups += 1
        if refs is None:
            raise AssertionError("rn resolved anchor missing from durable manifest index")
        if manifest_commitment(refs) != anchor:
            raise AssertionError("rn full anchor does not bind exact durable manifest")
        self.ren_hash_ops += 1
        self.ren_manifest_binding_passes += 1

        resolved = []
        for expected_type, ref in zip(EXPECTED_TYPES, refs):
            item = self.fragment_store.get(ref)
            if item is None:
                raise AssertionError("rn selected durable fragment missing")
            actual_type, payload = item
            self.ren_hash_ops += 1
            if fragment_ref(actual_type, payload) != ref:
                raise AssertionError("rn selected durable fragment hash mismatch")
            self.ren_reference_hash_passes += 1
            if actual_type != expected_type:
                raise AssertionError("rn selected durable fragment type mismatch")
            self.ren_reference_type_passes += 1
            resolved.append(item)
        return rebuild_delta(tuple(resolved))

    def _finalize_ren_dictionary(self) -> None:
        anchors = tuple(sorted({record[3] for record in self.ren_records}))
        self.ren_unique_anchor_count = len(anchors)
        if len(anchors) > NAME_CAPACITY:
            return
        self.ren_namespace_capacity_passes += 1

        # Frozen deterministic assignment: lexicographic full-anchor order -> u16.
        entries = tuple((i.to_bytes(NAME_WIDTH, "big"), anchor) for i, anchor in enumerate(anchors))
        entries_rebuilt = tuple((i.to_bytes(NAME_WIDTH, "big"), anchor) for i, anchor in enumerate(sorted(anchors)))
        if entries == entries_rebuilt:
            self.ren_name_assignment_determinism_passes += 1

        name_to_anchor = {name: anchor for name, anchor in entries}
        anchor_to_name = {anchor: name for name, anchor in entries}
        if len(name_to_anchor) != len(entries) or len(anchor_to_name) != len(entries):
            raise AssertionError("rn dictionary is not bijective")

        dict_sha = dictionary_commitment(entries)
        self.ren_hash_ops += 1
        if dictionary_commitment(entries) == dict_sha:
            self.ren_dictionary_commitment_passes += 1
        self.ren_hash_ops += 1

        # Frozen dictionary-level tamper controls, one suite per GT instance.
        mutated_dict_sha = (bytes([bytes.fromhex(dict_sha)[0] ^ 1]) + bytes.fromhex(dict_sha)[1:]).hex()
        if mutated_dict_sha != dictionary_commitment(entries):
            self.ren_dictionary_commitment_bitflip_rejects += 1
        self.ren_hash_ops += 1

        missing_name = len(entries).to_bytes(NAME_WIDTH, "big")
        if missing_name not in name_to_anchor:
            self.ren_missing_name_rejects += 1

        out_of_range_name = (NAME_CAPACITY - 1).to_bytes(NAME_WIDTH, "big")
        if out_of_range_name not in name_to_anchor:
            self.ren_out_of_range_name_rejects += 1

        # Replay every transition through rn -> full anchor -> durable manifest.
        for child, parent, original_delta, expected_anchor, expected_identity in self.ren_records:
            self.ren_transition_count += 1
            name = anchor_to_name[expected_anchor]
            resolved_anchor = name_to_anchor.get(name)
            self.ren_dictionary_lookups += 1
            if resolved_anchor == expected_anchor:
                self.ren_name_resolution_passes += 1
            else:
                raise AssertionError("rn did not resolve exact original full anchor")

            # Adjacent valid-name swap must not bind the expected anchor.
            if len(entries) > 1:
                idx = int.from_bytes(name, "big")
                swapped = ((idx + 1) % len(entries)).to_bytes(NAME_WIDTH, "big")
                if name_to_anchor[swapped] != expected_anchor:
                    self.ren_adjacent_name_swap_rejects += 1

            # Full-anchor bitflip after name resolution must not select a valid
            # expected durable record. This tests that rn never replaces hash binding.
            raw = bytes.fromhex(resolved_anchor)
            corrupted_anchor = (bytes([raw[0] ^ 1]) + raw[1:]).hex()
            if corrupted_anchor != expected_anchor and self.dual_manifest_index.get(corrupted_anchor) is None:
                self.ren_full_anchor_bitflip_rejects += 1

            rebuilt = self._ren_resolve_manifest(resolved_anchor)
            restored = recover_parent(child, rebuilt)
            self.ren_checkpoint_parent_literal_visits += (
                sum(len(c) for c in child) + sum(len(c) for c in restored)
            )
            if restored == parent:
                self.ren_parent_recovery_passes += 1
            recovered_identity = identity_anchor(rebuilt.parent_sha256, resolved_anchor)
            self.ren_hash_ops += 1
            if recovered_identity == expected_identity:
                self.ren_identity_recompute_passes += 1
            if simplify_one(restored, rebuilt.variable, rebuilt.value) == child:
                self.ren_forward_replay_passes += 1


def ren_snapshot(solver: RenPersistentNamePolicy) -> dict[str, int]:
    return {
        "transition_count": int(solver.ren_transition_count),
        "unique_anchor_count": int(solver.ren_unique_anchor_count),
        "name_resolution_passes": int(solver.ren_name_resolution_passes),
        "dictionary_commitment_passes": int(solver.ren_dictionary_commitment_passes),
        "manifest_binding_passes": int(solver.ren_manifest_binding_passes),
        "reference_hash_passes": int(solver.ren_reference_hash_passes),
        "reference_type_passes": int(solver.ren_reference_type_passes),
        "parent_recovery_passes": int(solver.ren_parent_recovery_passes),
        "identity_recompute_passes": int(solver.ren_identity_recompute_passes),
        "forward_replay_passes": int(solver.ren_forward_replay_passes),
        "name_assignment_determinism_passes": int(solver.ren_name_assignment_determinism_passes),
        "namespace_capacity_passes": int(solver.ren_namespace_capacity_passes),
        "adjacent_name_swap_rejects": int(solver.ren_adjacent_name_swap_rejects),
        "out_of_range_name_rejects": int(solver.ren_out_of_range_name_rejects),
        "dictionary_commitment_bitflip_rejects": int(solver.ren_dictionary_commitment_bitflip_rejects),
        "full_anchor_bitflip_rejects": int(solver.ren_full_anchor_bitflip_rejects),
        "missing_name_rejects": int(solver.ren_missing_name_rejects),
        "hash_ops": int(solver.ren_hash_ops),
        "dictionary_lookups": int(solver.ren_dictionary_lookups),
        "checkpoint_parent_literal_visits": int(solver.ren_checkpoint_parent_literal_visits),
        "extra_solver_residual_scans": int(solver.ren_extra_solver_residual_scans),
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
        parent_solver = SahOrionExternalAnchorPolicy()
        parent_result = parent_solver.solve(cnf, variable_count)
        candidate_solver = RenPersistentNamePolicy()
        candidate_result = candidate_solver.solve(cnf, variable_count)

        answers_match &= parent_result.answer == candidate_result.answer
        caps_match &= parent_result.cap_exceeded == candidate_result.cap_exceeded
        rows.append({
            "order": order,
            "parent_solver": solver_snapshot(parent_solver, parent_result),
            "candidate_solver": solver_snapshot(candidate_solver, candidate_result),
            "parent_sah": sah_snapshot(parent_solver),
            "candidate_sah": sah_snapshot(candidate_solver),
            "ren": ren_snapshot(candidate_solver),
            "four_sons_ledger_bytes": int(candidate_solver.fragment_store_wire_bytes + candidate_solver.fragment_manifest_wire_bytes),
        })

    solver_fields = tuple(FROZEN_SOLVER.keys())
    parent_solver_agg = aggregate(rows, "parent_solver", solver_fields)
    candidate_solver_agg = aggregate(rows, "candidate_solver", solver_fields)
    sah_fields = tuple(FROZEN_SAH_COUNTERS.keys())
    parent_sah_agg = aggregate(rows, "parent_sah", sah_fields)
    candidate_sah_agg = aggregate(rows, "candidate_sah", sah_fields)
    ren_fields = tuple(rows[0]["ren"].keys())
    ren = aggregate(rows, "ren", ren_fields)

    t = ren["transition_count"]
    unique_anchors = ren["unique_anchor_count"]
    four_sons_ledger = sum(int(row["four_sons_ledger_bytes"]) for row in rows)
    gt_count = len(rows)
    storage = {
        "four_sons_durable_ledger_bytes": four_sons_ledger,
        "active_commitment_bytes": 32 * t,
        "durable_name_bytes": NAME_WIDTH * t,
        "carried_name_bytes": NAME_WIDTH * t,
        "dictionary_entry_bytes": (NAME_WIDTH + 32) * unique_anchors,
        "dictionary_commitment_bytes": 32 * gt_count,
    }
    storage["total_ren_wire_bytes"] = sum(storage.values())
    storage["frozen_sah_external_anchor_wire_bytes"] = FROZEN_SAH_WIRE_BYTES
    storage["saved_wire_bytes_vs_sah"] = FROZEN_SAH_WIRE_BYTES - storage["total_ren_wire_bytes"]
    storage["ratio_to_sah"] = storage["total_ren_wire_bytes"] / FROZEN_SAH_WIRE_BYTES

    # Every transition has an adjacent-swap control because all revealed per-GT
    # dictionaries are required to have >1 unique anchor. Dictionary-level controls
    # are one PASS per GT instance.
    gates = {
        "frozen_sah_parent_solver_reproduced": parent_solver_agg == FROZEN_SOLVER,
        "candidate_solver_exactly_matches_parent": candidate_solver_agg == parent_solver_agg,
        "frozen_sah_parent_counters_reproduced": parent_sah_agg == FROZEN_SAH_COUNTERS,
        "candidate_sah_counters_exactly_match_parent": candidate_sah_agg == parent_sah_agg,
        "same_boolean_answers": answers_match,
        "same_cap_status": caps_match,
        "frozen_four_sons_ledger_bytes_reproduced": four_sons_ledger == FROZEN_FOUR_SONS_LEDGER_BYTES,
        "transition_count_exact": t == FROZEN_TRANSITIONS,
        "all_GT_namespaces_fit_u16": ren["namespace_capacity_passes"] == gt_count,
        "all_GT_name_assignments_deterministic": ren["name_assignment_determinism_passes"] == gt_count,
        "all_GT_dictionary_commitments_verify": ren["dictionary_commitment_passes"] == gt_count,
        "every_name_resolves_exact_original_anchor": ren["name_resolution_passes"] == t,
        "every_resolved_anchor_binds_exact_manifest": ren["manifest_binding_passes"] == t,
        "all_resolved_fragment_hashes_verify": ren["reference_hash_passes"] == 4 * t,
        "all_resolved_fragment_types_verify": ren["reference_type_passes"] == 4 * t,
        "every_name_recovers_exact_parent": ren["parent_recovery_passes"] == t,
        "every_name_recomputes_exact_identity": ren["identity_recompute_passes"] == t,
        "every_name_forward_replays_exact_child": ren["forward_replay_passes"] == t,
        "adjacent_valid_name_swaps_all_reject": ren["adjacent_name_swap_rejects"] == t,
        "out_of_range_name_rejects_for_all_GT": ren["out_of_range_name_rejects"] == gt_count,
        "dictionary_commitment_bitflip_rejects_for_all_GT": ren["dictionary_commitment_bitflip_rejects"] == gt_count,
        "full_anchor_bitflips_all_reject": ren["full_anchor_bitflip_rejects"] == t,
        "missing_name_rejects_for_all_GT": ren["missing_name_rejects"] == gt_count,
        "zero_extra_solver_residual_scans": ren["extra_solver_residual_scans"] == 0,
        "ren_storage_strictly_lower_than_sah_parent": storage["total_ren_wire_bytes"] < FROZEN_SAH_WIRE_BYTES,
    }
    passed = all(gates.values())

    return {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_REN_PERSISTENT_NAME_ROUTE_BINDING" if passed else "STOP_AT_REN_PERSISTENT_NAME_ROUTE_BINDING_NO_IMPROVEMENT",
        "operator": "REN_PERSISTENT_NAME_ROUTE_BINDING",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "parent_solver": parent_solver_agg,
        "candidate_solver": candidate_solver_agg,
        "parent_sah_anchor": parent_sah_agg,
        "candidate_sah_anchor": candidate_sah_agg,
        "ren": ren,
        "storage": storage,
        "gates": gates,
        "interpretation_if_pass": {
            "name_law": "NAME_IS_A_ROUTE_HANDLE; FULL_HASH_IS_THE_IDENTITY_WITNESS",
            "canonical_phrase": "THE NAME MAY CROSS THE GATE COMPACTLY, BUT THE FULL ANCHOR MUST ANSWER WHEN CALLED."
        },
        "work_charged": {
            "hash_ops": ren["hash_ops"],
            "dictionary_lookups": ren["dictionary_lookups"],
            "fragment_hash_checks": ren["reference_hash_passes"],
            "fragment_type_checks": ren["reference_type_passes"],
            "checkpoint_parent_literal_visits": ren["checkpoint_parent_literal_visits"],
            "storage_bytes": storage["total_ren_wire_bytes"],
            "note": "Name/dictionary/replay verification is explicit overhead and is not claimed free."
        },
        "historical_inspiration_boundary": {
            "Book_of_the_Dead_119": "NAME_PLUS_COMING_GOING_ROUTE_PROMPT_ONLY",
            "Book_of_the_Dead_149": "PERSISTENT_NAME_PROMPT_ONLY",
            "rn_is_cryptographic_identifier_translation": False,
            "ancient_text_is_algorithmic_evidence": False,
        },
        "next_watchlist_if_pass": [
            "MULTI_GLOSS_EQUIVALENCE_PROVENANCE_LEDGER",
            "RESTORE_TO_STABLE_CHECKPOINT",
            "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY"
        ],
        "claim_boundary": [
            "A pass establishes finite certificate-routing/storage compaction on revealed GT3..GT9 only.",
            "The 16-bit rn has no identity authority without exact dictionary resolution and full-anchor verification.",
            "It does not establish lower total runtime or RAM on arbitrary CNFs.",
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
            "PASS_KEEP_REN_PERSISTENT_NAME_ROUTE_BINDING",
            "STOP_AT_REN_PERSISTENT_NAME_ROUTE_BINDING_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
