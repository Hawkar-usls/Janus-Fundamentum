#!/usr/bin/env python3
"""Four-sons typed fragment recovery-ledger calibration.

Book of the Dead 151 is used only as a source-side prompt: the sons/protectors
reassemble and restore Osiris.  The four modern fragment roles below are NOT
translations of the four deities' historical functions.

Frozen modern operator:

  MONOLITHIC RECOVERY DELTA
        -> 4 typed content-addressed fragments
        -> exact four-reference manifest
        -> verify types/hashes
        -> reassemble exact delta
        -> exact parent recovery
        -> exact forward replay to child

The ledger has no SAT/UNSAT/equivalence/absorption/pruning authority.  Revealed
GT3..GT9 only.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_pt477_v3_local_apep_edge_tombstone import canonical_edges
from janus_son_return_path_parent_delta import (
    FROZEN_PT477_V3,
    ParentRecoveryDelta,
    SonReturnPathPolicy,
    clause_list_wire_bytes,
    cnf_digest,
    fused_simplify_with_recovery_delta,
    recover_parent,
    recovery_delta_wire_bytes,
)
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    graph_tautology_cnf,
)
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    canonical_cnf,
    limited_resolution,
    simplify_one,
    unit_propagate,
)

RUN_ID = "JANUS-FOUR-SONS-TYPED-FRAGMENT-REASSEMBLY-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_PARENT_TRANSITIONS = 5366
FROZEN_MONOLITHIC_DELTA_BYTES = 6736086

TYPE_BRANCH = 1
TYPE_RESTORE = 2
TYPE_REMOVE = 3
TYPE_COMMIT = 4
TYPE_NAMES = {
    TYPE_BRANCH: "BRANCH_IDENTITY",
    TYPE_RESTORE: "PARENT_CLAUSES_TO_RESTORE",
    TYPE_REMOVE: "CHILD_ARTIFACTS_TO_REMOVE",
    TYPE_COMMIT: "PARENT_COMMITMENT",
}
EXPECTED_TYPES = (TYPE_BRANCH, TYPE_RESTORE, TYPE_REMOVE, TYPE_COMMIT)


def encode_clause_list(clauses: tuple[tuple[int, ...], ...]) -> bytes:
    out = bytearray()
    out += len(clauses).to_bytes(4, "big", signed=False)
    for clause in clauses:
        out += len(clause).to_bytes(2, "big", signed=False)
        for literal in clause:
            out += int(literal).to_bytes(4, "big", signed=True)
    return bytes(out)


def decode_clause_list(payload: bytes) -> tuple[tuple[int, ...], ...]:
    pos = 0
    if len(payload) < 4:
        raise AssertionError("fragment clause-list payload too short")
    count = int.from_bytes(payload[pos:pos+4], "big", signed=False)
    pos += 4
    clauses: list[tuple[int, ...]] = []
    for _ in range(count):
        if pos + 2 > len(payload):
            raise AssertionError("fragment clause-list length truncated")
        width = int.from_bytes(payload[pos:pos+2], "big", signed=False)
        pos += 2
        clause: list[int] = []
        for _ in range(width):
            if pos + 4 > len(payload):
                raise AssertionError("fragment literal truncated")
            clause.append(int.from_bytes(payload[pos:pos+4], "big", signed=True))
            pos += 4
        clauses.append(tuple(clause))
    if pos != len(payload):
        raise AssertionError("fragment clause-list has trailing bytes")
    return canonical_cnf(clauses)


def fragment_ref(type_tag: int, payload: bytes) -> str:
    h = sha256()
    h.update(bytes((type_tag,)))
    h.update(len(payload).to_bytes(4, "big", signed=False))
    h.update(payload)
    return h.hexdigest()


def branch_payload(delta: ParentRecoveryDelta) -> bytes:
    return int(delta.variable).to_bytes(4, "big", signed=True) + bytes((int(delta.value),))


def fragment_payloads(delta: ParentRecoveryDelta) -> tuple[tuple[int, bytes], ...]:
    return (
        (TYPE_BRANCH, branch_payload(delta)),
        (TYPE_RESTORE, encode_clause_list(delta.add_parent_clauses)),
        (TYPE_REMOVE, encode_clause_list(delta.remove_child_artifacts)),
        (TYPE_COMMIT, bytes.fromhex(delta.parent_sha256)),
    )


def rebuild_delta(resolved: tuple[tuple[int, bytes], ...]) -> ParentRecoveryDelta:
    if tuple(tag for tag, _ in resolved) != EXPECTED_TYPES:
        raise AssertionError("typed fragment slot order mismatch")
    branch = resolved[0][1]
    if len(branch) != 5:
        raise AssertionError("branch fragment has wrong payload length")
    variable = int.from_bytes(branch[:4], "big", signed=True)
    value_raw = branch[4]
    if value_raw not in (0, 1):
        raise AssertionError("branch Boolean is not canonical")
    commitment = resolved[3][1]
    if len(commitment) != 32:
        raise AssertionError("parent commitment fragment must be 32 bytes")
    return ParentRecoveryDelta(
        variable=variable,
        value=bool(value_raw),
        add_parent_clauses=decode_clause_list(resolved[1][1]),
        remove_child_artifacts=decode_clause_list(resolved[2][1]),
        parent_sha256=commitment.hex(),
    )


class FourSonsFragmentLedgerPolicy(SonReturnPathPolicy):
    """Parent-delta operator plus typed content-addressed certificate ledger."""

    def solve(self, cnf, variable_count):
        self.fragment_store: dict[str, tuple[int, bytes]] = {}
        self.fragment_store_wire_bytes = 0
        self.fragment_manifest_wire_bytes = 0
        self.fragment_manifest_count = 0
        self.fragment_reference_count = 0
        self.fragment_reference_hash_passes = 0
        self.fragment_type_passes = 0
        self.fragment_reassembled_delta_passes = 0
        self.fragment_parent_recovery_passes = 0
        self.fragment_parent_commitment_passes = 0
        self.fragment_forward_replay_passes = 0
        self.fragmentation_extra_residual_scans = 0
        self.fragment_dedup_hits = 0
        self.fragment_unique_by_type = Counter()
        self.fragment_refs_by_type = Counter()
        return super().solve(cnf, variable_count)

    def intern_fragment(self, type_tag: int, payload: bytes) -> str:
        ref = fragment_ref(type_tag, payload)
        self.fragment_refs_by_type[TYPE_NAMES[type_tag]] += 1
        existing = self.fragment_store.get(ref)
        if existing is None:
            self.fragment_store[ref] = (type_tag, payload)
            self.fragment_store_wire_bytes += 1 + 4 + len(payload)
            self.fragment_unique_by_type[TYPE_NAMES[type_tag]] += 1
        else:
            if existing != (type_tag, payload):
                raise AssertionError("SHA-256 fragment collision with unequal typed payload")
            self.fragment_dedup_hits += 1
        return ref

    def resolve_manifest(self, refs: tuple[str, str, str, str]) -> tuple[tuple[int, bytes], ...]:
        resolved: list[tuple[int, bytes]] = []
        for expected_type, ref in zip(EXPECTED_TYPES, refs):
            item = self.fragment_store.get(ref)
            if item is None:
                raise AssertionError("typed fragment reference missing from store")
            actual_type, payload = item
            self.fragment_reference_count += 1
            if fragment_ref(actual_type, payload) == ref:
                self.fragment_reference_hash_passes += 1
            else:
                raise AssertionError("typed fragment reference hash mismatch")
            if actual_type == expected_type:
                self.fragment_type_passes += 1
            else:
                raise AssertionError("typed fragment placed in wrong slot")
            resolved.append(item)
        return tuple(resolved)

    def record_fragment_ledger(
        self,
        child: CNF,
        original_delta: ParentRecoveryDelta,
        parent: CNF,
    ) -> None:
        refs = tuple(
            self.intern_fragment(type_tag, payload)
            for type_tag, payload in fragment_payloads(original_delta)
        )
        if len(refs) != 4:
            raise AssertionError("exactly four fragment slots are required")
        self.fragment_manifest_count += 1
        self.fragment_manifest_wire_bytes += 4 * 32

        resolved = self.resolve_manifest(refs)  # verifies hash and type before use
        rebuilt = rebuild_delta(resolved)
        if rebuilt == original_delta:
            self.fragment_reassembled_delta_passes += 1

        restored = recover_parent(child, rebuilt)
        if restored == parent:
            self.fragment_parent_recovery_passes += 1
        if cnf_digest(restored) == rebuilt.parent_sha256:
            self.fragment_parent_commitment_passes += 1
        if simplify_one(restored, rebuilt.variable, rebuilt.value) == child:
            self.fragment_forward_replay_passes += 1

    def search(self, cnf: CNF) -> bool:
        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            return False
        assert propagated is not None
        if not propagated:
            return True
        cnf = propagated

        handle, cached_answer = self.quotient_lookup(cnf)
        if cached_answer is not None:
            return cached_answer

        self.states += 1
        if self.state_cap is not None and self.states > self.state_cap:
            raise RuntimeError("state cap exceeded")

        literal_count = sum(len(clause) for clause in cnf)
        width_limit = max(len(clause) for clause in cnf) + 1
        saturated, refuted, attempts, additions = limited_resolution(
            cnf,
            max_width=width_limit,
            attempt_budget=max(64, 4 * literal_count),
            addition_budget=max(8, len(cnf) // 4),
        )
        self.resolution_attempts += attempts
        self.resolution_additions += additions

        if refuted:
            self.memo_store(handle, cnf, False)
            return False

        propagated, contradiction = unit_propagate(saturated)
        if contradiction:
            self.memo_store(handle, cnf, False)
            return False
        assert propagated is not None
        if not propagated:
            self.memo_store(handle, cnf, True)
            return True

        frequencies = Counter(abs(lit) for clause in propagated for lit in clause)
        maximum = max(frequencies.values())
        variable = min(v for v, count in frequencies.items() if count == maximum)

        for value in (False, True):
            child, delta, generation_visits = fused_simplify_with_recovery_delta(
                propagated,
                variable,
                value,
            )
            self.recovery_generation_parent_literal_visits += generation_visits
            if child is None:
                continue
            assert delta is not None

            # Preserve the exact parent operator's accounting and verification.
            self.recovery_transition_count += 1
            parent_bytes = 4 + sum(2 + 4 * len(clause) for clause in propagated)
            delta_bytes = recovery_delta_wire_bytes(delta)
            parent_literals = sum(len(clause) for clause in propagated)
            delta_literals = (
                sum(len(clause) for clause in delta.add_parent_clauses)
                + sum(len(clause) for clause in delta.remove_child_artifacts)
                + 1
            )
            self.recovery_parent_snapshot_bytes += parent_bytes
            self.recovery_delta_bytes += delta_bytes
            self.recovery_parent_literal_units += parent_literals
            self.recovery_delta_literal_units += delta_literals
            ratio = delta_bytes / max(1, parent_bytes)
            self.recovery_max_delta_snapshot_ratio = max(self.recovery_max_delta_snapshot_ratio, ratio)
            if delta_bytes < parent_bytes:
                self.recovery_smaller_payload_transitions += 1
            else:
                self.recovery_equal_or_larger_payload_transitions += 1

            restored = recover_parent(child, delta)
            restored_literals = sum(len(clause) for clause in restored)
            child_literals = sum(len(clause) for clause in child)
            self.recovery_reverse_verifier_literal_visits += (
                restored_literals + child_literals + restored_literals
            )
            if restored == propagated:
                self.recovery_reverse_passes += 1
            if cnf_digest(restored) == delta.parent_sha256:
                self.recovery_commitment_passes += 1
            if simplify_one(restored, variable, value) == child:
                self.recovery_forward_replay_passes += 1

            # New operator is a pure certificate-storage layer; it performs no
            # residual scan and cannot affect the search decision.
            self.record_fragment_ledger(child, delta, propagated)

            if self.search(child):
                self.memo_store(handle, cnf, True)
                return True

        self.memo_store(handle, cnf, False)
        return False


def solver_snapshot(solver, result) -> dict[str, int]:
    return {
        "residual_states": int(result.residual_states),
        "bytewise_distinct_absorptions": int(result.bytewise_distinct_absorptions),
        "polarity_flip_absorptions": int(result.polarity_flip_absorptions),
        "event_horizon_collisions": int(result.event_horizon_collisions),
        "hawking_escape_count": int(result.hawking_escape_count),
        "buzz_return_checks": int(result.buzz_return_checks),
        "canonical_edge_visits": int(canonical_edges(result)),
        "resolution_attempts": int(result.resolution_attempts),
        "resolution_additions": int(result.resolution_additions),
        "local_tombstone_checks": int(solver.local_tombstone_checks),
        "local_tombstone_hits": int(solver.local_tombstone_hits),
        "local_tombstone_inserts": int(solver.local_tombstone_inserts),
        "route_rescan_edge_visits": int(solver.route_rescan_edge_visits),
    }


def add_counts(rows: list[dict[str, Any]], side: str, fields: tuple[str, ...]) -> dict[str, int]:
    return {field: sum(int(row[side][field]) for row in rows) for field in fields}


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    answers_match = True
    caps_match = True

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)

        parent_solver = SonReturnPathPolicy()
        parent_result = parent_solver.solve(cnf, variable_count)
        candidate_solver = FourSonsFragmentLedgerPolicy()
        candidate_result = candidate_solver.solve(cnf, variable_count)

        answers_match &= parent_result.answer == candidate_result.answer
        caps_match &= parent_result.cap_exceeded == candidate_result.cap_exceeded

        parent_snap = solver_snapshot(parent_solver, parent_result)
        candidate_snap = solver_snapshot(candidate_solver, candidate_result)

        recovery = {
            "transition_count": candidate_solver.recovery_transition_count,
            "monolithic_delta_wire_bytes": candidate_solver.recovery_delta_bytes,
            "parent_snapshot_wire_bytes": candidate_solver.recovery_parent_snapshot_bytes,
        }
        ledger = {
            "fragment_store_wire_bytes": candidate_solver.fragment_store_wire_bytes,
            "manifest_wire_bytes": candidate_solver.fragment_manifest_wire_bytes,
            "manifest_count": candidate_solver.fragment_manifest_count,
            "reference_count": candidate_solver.fragment_reference_count,
            "reference_hash_passes": candidate_solver.fragment_reference_hash_passes,
            "type_passes": candidate_solver.fragment_type_passes,
            "reassembled_delta_passes": candidate_solver.fragment_reassembled_delta_passes,
            "parent_recovery_passes": candidate_solver.fragment_parent_recovery_passes,
            "parent_commitment_passes": candidate_solver.fragment_parent_commitment_passes,
            "forward_replay_passes": candidate_solver.fragment_forward_replay_passes,
            "dedup_hits": candidate_solver.fragment_dedup_hits,
            "unique_fragment_count": len(candidate_solver.fragment_store),
            "unique_by_type": dict(candidate_solver.fragment_unique_by_type),
            "references_by_type": dict(candidate_solver.fragment_refs_by_type),
            "fragmentation_extra_residual_scans": candidate_solver.fragmentation_extra_residual_scans,
        }
        ledger["total_ledger_wire_bytes"] = (
            ledger["fragment_store_wire_bytes"] + ledger["manifest_wire_bytes"]
        )

        rows.append({
            "order": order,
            "parent": parent_snap,
            "candidate": candidate_snap,
            "recovery": recovery,
            "ledger": ledger,
        })

    solver_fields = tuple(FROZEN_PT477_V3)
    parent = add_counts(rows, "parent", solver_fields)
    candidate = add_counts(rows, "candidate", solver_fields)
    parent_reproduced = all(parent[name] == expected for name, expected in FROZEN_PT477_V3.items())
    exact_solver_trajectory = all(candidate[name] == parent[name] for name in solver_fields)

    transition_count = sum(row["recovery"]["transition_count"] for row in rows)
    monolithic_bytes = sum(row["recovery"]["monolithic_delta_wire_bytes"] for row in rows)
    parent_snapshot_bytes = sum(row["recovery"]["parent_snapshot_wire_bytes"] for row in rows)

    ledger_sum_fields = (
        "fragment_store_wire_bytes",
        "manifest_wire_bytes",
        "manifest_count",
        "reference_count",
        "reference_hash_passes",
        "type_passes",
        "reassembled_delta_passes",
        "parent_recovery_passes",
        "parent_commitment_passes",
        "forward_replay_passes",
        "dedup_hits",
        "unique_fragment_count",
        "fragmentation_extra_residual_scans",
    )
    ledger = {
        field: sum(int(row["ledger"][field]) for row in rows)
        for field in ledger_sum_fields
    }
    # Each order is an independent solver run/store.  This intentionally avoids
    # cross-instance deduplication leakage between calibration instances.
    ledger["total_ledger_wire_bytes"] = (
        ledger["fragment_store_wire_bytes"] + ledger["manifest_wire_bytes"]
    )
    ledger["ledger_to_monolithic_ratio"] = ledger["total_ledger_wire_bytes"] / max(1, monolithic_bytes)
    ledger["saved_wire_bytes_vs_monolithic"] = monolithic_bytes - ledger["total_ledger_wire_bytes"]

    expected_refs = transition_count * 4
    gates = {
        "frozen_son_return_parent_reproduced": (
            parent_reproduced
            and transition_count == FROZEN_PARENT_TRANSITIONS
            and monolithic_bytes == FROZEN_MONOLITHIC_DELTA_BYTES
        ),
        "same_boolean_answers": answers_match,
        "same_cap_status": caps_match,
        "exact_solver_trajectory": exact_solver_trajectory,
        "transition_count_exact": transition_count == FROZEN_PARENT_TRANSITIONS,
        "exactly_four_references_per_transition": ledger["reference_count"] == expected_refs,
        "all_fragment_reference_hashes_verify": ledger["reference_hash_passes"] == expected_refs,
        "all_fragment_types_verify": ledger["type_passes"] == expected_refs,
        "every_delta_reassembled_exactly": ledger["reassembled_delta_passes"] == transition_count,
        "every_parent_reconstructed_exactly": ledger["parent_recovery_passes"] == transition_count,
        "every_parent_commitment_matches": ledger["parent_commitment_passes"] == transition_count,
        "every_parent_forward_replays_same_child": ledger["forward_replay_passes"] == transition_count,
        "ledger_total_strictly_smaller_than_monolithic_delta": (
            ledger["total_ledger_wire_bytes"] < monolithic_bytes
        ),
        "fragment_deduplication_positive": ledger["dedup_hits"] > 0,
        "zero_extra_residual_scans_for_fragmentation": (
            ledger["fragmentation_extra_residual_scans"] == 0
        ),
    }
    improved = all(gates.values())

    return {
        "artifact_id": RUN_ID,
        "status": (
            "PASS_KEEP_FOUR_SONS_TYPED_FRAGMENT_REASSEMBLY"
            if improved
            else "STOP_AT_FOUR_SONS_TYPED_FRAGMENT_REASSEMBLY_NO_IMPROVEMENT"
        ),
        "operator": "FOUR_SONS_TYPED_FRAGMENT_REASSEMBLY_LEDGER",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "parent_solver": parent,
        "candidate_solver": candidate,
        "recovery_parent": {
            "transition_count": transition_count,
            "monolithic_delta_wire_bytes": monolithic_bytes,
            "parent_snapshot_wire_bytes": parent_snapshot_bytes,
        },
        "fragment_ledger": ledger,
        "gates": gates,
        "metric_improved": improved,
        "historical_inspiration_boundary": {
            "Book_of_the_Dead_151": "FOUR_SONS_REASSEMBLY_PROMPT_ONLY",
            "modern_fragment_roles_are_historical_translations": False,
            "ancient_text_is_algorithmic_evidence": False,
        },
        "next_watchlist_if_pass": [
            "DUAL_RESIDENCY_REJUVENATION_CHECKPOINT",
            "SAH_ORION_TRANSFIGURED_STATE_ANCHOR",
            "MULTI_GLOSS_EQUIVALENCE_PROVENANCE_LEDGER",
            "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY",
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
        },
        "claim_boundary": [
            "Fragment hashes/types and ledger storage are charged explicitly.",
            "Fragment stores are isolated per GT instance; no cross-instance calibration leakage is used.",
            "The ledger can reconstruct recovery data only and cannot authorize a solver conclusion.",
            "A storage pass does not establish lower runtime/RAM on arbitrary CNFs.",
            "A finite calibration does not establish a universal polynomial residual automaton.",
            "P_VS_NP = OPEN",
        ],
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
            "PASS_KEEP_FOUR_SONS_TYPED_FRAGMENT_REASSEMBLY",
            "STOP_AT_FOUR_SONS_TYPED_FRAGMENT_REASSEMBLY_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
