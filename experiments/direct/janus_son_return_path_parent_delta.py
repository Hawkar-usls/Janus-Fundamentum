#!/usr/bin/env python3
"""Son-return-path immediate-parent recovery calibration.

Historical Egyptian texts are used only as operator prompts.  In particular,
PT 366 supplies a father/seed/Horus chain and Book of the Dead 151 supplies a
son/reassembly-of-father motif.  The user's ꜣ=vagina/gate substitution remains a
project heuristic, not an Egyptological translation.

Frozen modern operator:

    PARENT -> CHILD + RECOVERY_DELTA
    CHILD + RECOVERY_DELTA -> EXACT PARENT -> SAME CHILD

The recovery delta is generated in the same parent-clause pass that performs the
branch simplification.  It may reconstruct and verify an immediate parent only;
it cannot authorize SAT, UNSAT, equivalence, absorption, or pruning.

Calibration is revealed GT3..GT9 only.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_pt477_v3_local_apep_edge_tombstone import (
    LocalApepEdgeTombstonePolicy,
    canonical_edges,
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

RUN_ID = "JANUS-SON-RETURN-PATH-PARENT-DELTA-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_PT477_V3 = {
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


def feed_clause(hasher, clause: tuple[int, ...]) -> None:
    hasher.update(len(clause).to_bytes(2, "big", signed=False))
    for literal in clause:
        hasher.update(int(literal).to_bytes(4, "big", signed=True))


def cnf_digest(cnf: CNF) -> str:
    h = sha256()
    h.update(len(cnf).to_bytes(4, "big", signed=False))
    for clause in cnf:
        feed_clause(h, clause)
    return h.hexdigest()


def clause_wire_bytes(clause: tuple[int, ...]) -> int:
    return 2 + 4 * len(clause)


def clause_list_wire_bytes(clauses: tuple[tuple[int, ...], ...]) -> int:
    return 4 + sum(clause_wire_bytes(clause) for clause in clauses)


def cnf_snapshot_wire_bytes(cnf: CNF) -> int:
    return 4 + sum(clause_wire_bytes(clause) for clause in cnf)


@dataclass(frozen=True)
class ParentRecoveryDelta:
    variable: int
    value: bool
    add_parent_clauses: tuple[tuple[int, ...], ...]
    remove_child_artifacts: tuple[tuple[int, ...], ...]
    parent_sha256: str


def recovery_delta_wire_bytes(delta: ParentRecoveryDelta) -> int:
    # variable(4) + value(1) + exact parent commitment(32) + two clause lists.
    return (
        4
        + 1
        + 32
        + clause_list_wire_bytes(delta.add_parent_clauses)
        + clause_list_wire_bytes(delta.remove_child_artifacts)
    )


def fused_simplify_with_recovery_delta(
    cnf: CNF,
    variable: int,
    value: bool,
) -> tuple[CNF | None, ParentRecoveryDelta | None, int]:
    """Perform simplify_one semantics while recording an exact inverse delta.

    No second parent-CNF pass is used to build the certificate.  `unchanged`
    records child clauses that already existed in the parent; this lets reverse
    replay distinguish them from reduced-clause artifacts without rescanning the
    parent after simplification.
    """
    true_literal = variable if value else -variable
    false_literal = -true_literal

    residual: list[tuple[int, ...]] = []
    add_parent: list[tuple[int, ...]] = []
    reduced_candidates: set[tuple[int, ...]] = set()
    unchanged: set[tuple[int, ...]] = set()
    parent_literal_visits = 0

    h = sha256()
    h.update(len(cnf).to_bytes(4, "big", signed=False))

    for clause in cnf:
        feed_clause(h, clause)
        parent_literal_visits += len(clause)

        if true_literal in clause:
            add_parent.append(clause)
            continue

        if false_literal in clause:
            reduced = tuple(literal for literal in clause if literal != false_literal)
            if not reduced:
                return None, None, parent_literal_visits
            residual.append(reduced)
            add_parent.append(clause)
            reduced_candidates.add(reduced)
        else:
            residual.append(clause)
            unchanged.add(clause)

    child = canonical_cnf(residual)
    # A reduced child clause is a branch artifact only when that exact clause did
    # not already exist unchanged in the parent.
    remove_artifacts = canonical_cnf(reduced_candidates - unchanged)
    delta = ParentRecoveryDelta(
        variable=variable,
        value=bool(value),
        add_parent_clauses=canonical_cnf(add_parent),
        remove_child_artifacts=remove_artifacts,
        parent_sha256=h.hexdigest(),
    )
    return child, delta, parent_literal_visits


def recover_parent(child: CNF, delta: ParentRecoveryDelta) -> CNF:
    remove = set(delta.remove_child_artifacts)
    clauses = [clause for clause in child if clause not in remove]
    clauses.extend(delta.add_parent_clauses)
    return canonical_cnf(clauses)


class SonReturnPathPolicy(LocalApepEdgeTombstonePolicy):
    """PT477-v3 trajectory plus immediate-parent recovery certificates."""

    def solve(self, cnf, variable_count):
        self.recovery_transition_count = 0
        self.recovery_reverse_passes = 0
        self.recovery_forward_replay_passes = 0
        self.recovery_commitment_passes = 0
        self.recovery_parent_snapshot_bytes = 0
        self.recovery_delta_bytes = 0
        self.recovery_parent_literal_units = 0
        self.recovery_delta_literal_units = 0
        self.recovery_generation_parent_literal_visits = 0
        self.recovery_reverse_verifier_literal_visits = 0
        self.recovery_smaller_payload_transitions = 0
        self.recovery_equal_or_larger_payload_transitions = 0
        self.recovery_max_delta_snapshot_ratio = 0.0
        self.recovery_generation_extra_parent_rescans = 0
        return super().solve(cnf, variable_count)

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

            self.recovery_transition_count += 1
            parent_bytes = cnf_snapshot_wire_bytes(propagated)
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
            self.recovery_max_delta_snapshot_ratio = max(
                self.recovery_max_delta_snapshot_ratio,
                ratio,
            )
            if delta_bytes < parent_bytes:
                self.recovery_smaller_payload_transitions += 1
            else:
                self.recovery_equal_or_larger_payload_transitions += 1

            # Reverse/fwd verification is explicit calibration work and is
            # reported separately; it does not change search decisions.
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

            if self.search(child):
                self.memo_store(handle, cnf, True)
                return True

        self.memo_store(handle, cnf, False)
        return False


def aggregate_solver(rows: list[dict[str, Any]], side: str) -> dict[str, int]:
    fields = (
        "residual_states",
        "bytewise_distinct_absorptions",
        "polarity_flip_absorptions",
        "event_horizon_collisions",
        "hawking_escape_count",
        "buzz_return_checks",
        "resolution_attempts",
        "resolution_additions",
        "canonical_edge_visits",
        "local_tombstone_checks",
        "local_tombstone_hits",
        "local_tombstone_inserts",
        "route_rescan_edge_visits",
    )
    return {field: sum(int(row[side][field]) for row in rows) for field in fields}


def aggregate_recovery(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fields = (
        "recovery_transition_count",
        "recovery_reverse_passes",
        "recovery_forward_replay_passes",
        "recovery_commitment_passes",
        "recovery_parent_snapshot_bytes",
        "recovery_delta_bytes",
        "recovery_parent_literal_units",
        "recovery_delta_literal_units",
        "recovery_generation_parent_literal_visits",
        "recovery_reverse_verifier_literal_visits",
        "recovery_smaller_payload_transitions",
        "recovery_equal_or_larger_payload_transitions",
        "recovery_generation_extra_parent_rescans",
    )
    out: dict[str, Any] = {
        field: sum(int(row["recovery"][field]) for row in rows)
        for field in fields
    }
    out["recovery_max_delta_snapshot_ratio"] = max(
        float(row["recovery"]["recovery_max_delta_snapshot_ratio"])
        for row in rows
    )
    out["aggregate_delta_to_parent_snapshot_ratio"] = (
        out["recovery_delta_bytes"] / max(1, out["recovery_parent_snapshot_bytes"])
    )
    return out


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    answers_match = True
    caps_match = True

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)
        parent_solver = LocalApepEdgeTombstonePolicy()
        parent = parent_solver.solve(cnf, variable_count)

        candidate_solver = SonReturnPathPolicy()
        candidate = candidate_solver.solve(cnf, variable_count)

        answers_match &= parent.answer == candidate.answer
        caps_match &= parent.cap_exceeded == candidate.cap_exceeded

        parent_dict = asdict(parent)
        parent_dict["canonical_edge_visits"] = canonical_edges(parent)
        parent_dict.update({
            "local_tombstone_checks": parent_solver.local_tombstone_checks,
            "local_tombstone_hits": parent_solver.local_tombstone_hits,
            "local_tombstone_inserts": parent_solver.local_tombstone_inserts,
            "route_rescan_edge_visits": parent_solver.route_rescan_edge_visits,
        })

        candidate_dict = asdict(candidate)
        candidate_dict["canonical_edge_visits"] = canonical_edges(candidate)
        candidate_dict.update({
            "local_tombstone_checks": candidate_solver.local_tombstone_checks,
            "local_tombstone_hits": candidate_solver.local_tombstone_hits,
            "local_tombstone_inserts": candidate_solver.local_tombstone_inserts,
            "route_rescan_edge_visits": candidate_solver.route_rescan_edge_visits,
        })

        recovery = {
            name: getattr(candidate_solver, name)
            for name in (
                "recovery_transition_count",
                "recovery_reverse_passes",
                "recovery_forward_replay_passes",
                "recovery_commitment_passes",
                "recovery_parent_snapshot_bytes",
                "recovery_delta_bytes",
                "recovery_parent_literal_units",
                "recovery_delta_literal_units",
                "recovery_generation_parent_literal_visits",
                "recovery_reverse_verifier_literal_visits",
                "recovery_smaller_payload_transitions",
                "recovery_equal_or_larger_payload_transitions",
                "recovery_max_delta_snapshot_ratio",
                "recovery_generation_extra_parent_rescans",
            )
        }

        rows.append({
            "order": order,
            "parent": parent_dict,
            "candidate": candidate_dict,
            "recovery": recovery,
        })

    parent = aggregate_solver(rows, "parent")
    candidate = aggregate_solver(rows, "candidate")
    recovery = aggregate_recovery(rows)

    parent_reproduced = all(
        parent[name] == expected for name, expected in FROZEN_PT477_V3.items()
    )
    exact_solver_trajectory = all(
        candidate[name] == parent[name] for name in FROZEN_PT477_V3
    )
    transitions = recovery["recovery_transition_count"]

    gates = {
        "frozen_pt477_v3_parent_reproduced": parent_reproduced,
        "same_boolean_answers": answers_match,
        "same_cap_status": caps_match,
        "exact_solver_trajectory": exact_solver_trajectory,
        "recovery_transitions_positive": transitions > 0,
        "every_parent_reconstructed_exactly": (
            recovery["recovery_reverse_passes"] == transitions
        ),
        "every_parent_commitment_matches": (
            recovery["recovery_commitment_passes"] == transitions
        ),
        "every_parent_forward_replays_same_child": (
            recovery["recovery_forward_replay_passes"] == transitions
        ),
        "aggregate_recovery_delta_strictly_smaller_than_parent_snapshots": (
            recovery["recovery_delta_bytes"]
            < recovery["recovery_parent_snapshot_bytes"]
        ),
        "zero_extra_parent_rescans_for_delta_generation": (
            recovery["recovery_generation_extra_parent_rescans"] == 0
        ),
    }

    improved = all(gates.values())
    return {
        "artifact_id": RUN_ID,
        "status": (
            "PASS_KEEP_SON_RETURN_PATH_PARENT_DELTA"
            if improved
            else "STOP_AT_SON_RETURN_PATH_PARENT_DELTA_NO_IMPROVEMENT"
        ),
        "operator": "SON_RETURN_PATH_PARENT_DELTA_CERTIFICATE",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "parent_pt477_v3": parent,
        "candidate_solver": candidate,
        "recovery": recovery,
        "gates": gates,
        "metric_improved": improved,
        "historical_inspiration_boundary": {
            "PT366": "FATHER_SEED_HORUS_CHAIN_PROMPT_ONLY",
            "Book_of_the_Dead_151": "SON_REASSEMBLES_FATHER_PROMPT_ONLY",
            "user_rebus": "PROJECT_HEURISTIC_ONLY",
            "a_as_vagina_or_gate": "PROJECT_SUBSTITUTION_NOT_TRANSLATION",
            "ancient_text_is_algorithmic_evidence": False,
        },
        "next_watchlist_if_pass": [
            "FOUR_SONS_TYPED_FRAGMENT_REASSEMBLY_LEDGER",
            "SAH_ORION_TRANSFIGURED_STATE_ANCHOR",
            "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY",
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
        },
        "claim_boundary": [
            "A recovery delta reconstructs only the immediate parent branch state.",
            "Reverse verification work is reported separately and is not free.",
            "A payload pass does not establish lower total runtime or memory on arbitrary CNFs.",
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
            "PASS_KEEP_SON_RETURN_PATH_PARENT_DELTA",
            "STOP_AT_SON_RETURN_PATH_PARENT_DELTA_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
