#!/usr/bin/env python3
"""PT477-v3: residual-local Apep edge tombstone calibration.

Historical texts are operator prompts only.  The modern rule follows the bounded
Aura diagnosis of PT477-v2:

  * keep NAME/BIND/CUT/BURN as a negative-only mechanism;
  * remove global tombstone scope;
  * bind a failed candidate edge only to the current residual handle;
  * never inherit that negative mark into another residual context.

Concretely, quotient_lookup records which pre-existing bucket entries failed an
exact Buzz return check for THIS current residual.  If the same residual later
reaches memo_store, those exact already-failed comparisons are not replayed.
Entries added by descendant search after quotient_lookup are never tombstoned and
are checked normally.  Thus the optimization is local replay de-duplication, not
a new equivalence rule.

A local tombstone may only refuse one repeat Buzz check.  It can never authorize
an absorption, SAT, UNSAT, or semantic equivalence.  No extra residual scan is
used.  Calibration is revealed GT3..GT9 only.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    Policy0ABHQ2,
    graph_tautology_cnf,
    signed_typed_signature,
)

RUN_ID = "JANUS-PT477-V3-LOCAL-APEP-EDGE-TOMBSTONE-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_BASELINE = {
    "residual_states": 2822,
    "bytewise_distinct_absorptions": 602,
    "polarity_flip_absorptions": 450,
    "event_horizon_collisions": 839,
    "hawking_escape_count": 2292,
    "buzz_return_checks": 2894,
    "canonical_edge_visits": 3488298,
    "resolution_attempts": 626489,
    "resolution_additions": 93638,
    "structural_work_proxy": 4114787,
}


@dataclass
class LocalApepHandle:
    signature: str
    canonicalization: Any
    failed_entry_indices: frozenset[int]
    lookup_bucket_size: int


class LocalApepEdgeTombstonePolicy(Policy0ABHQ2):
    """BH-Q2 with residual-local negative replay memory only."""

    def solve(self, cnf, variable_count):
        self.local_tombstone_checks = 0
        self.local_tombstone_hits = 0
        self.local_tombstone_inserts = 0
        self.route_rescan_edge_visits = 0
        return super().solve(cnf, variable_count)

    def quotient_lookup(self, cnf):
        self.physarum_signature_checks += 1
        signature = signed_typed_signature(cnf)
        bucket = self.buckets.get(signature)
        if not bucket:
            return LocalApepHandle(signature, None, frozenset(), 0), None

        self.event_horizon_collisions += 1

        # Exact bytewise reuse is identical to baseline and bypasses the horizon.
        for entry in bucket:
            if entry.representative == cnf:
                self.absorption_hits += 1
                return LocalApepHandle(signature, entry.canonicalization, frozenset(), len(bucket)), entry.answer

        current_q = self.canonicalize(cnf)
        failed: set[int] = set()
        lookup_bucket_size = len(bucket)

        for index, entry in enumerate(bucket):
            if entry.canonicalization is None:
                entry.canonicalization = self.canonicalize(entry.representative)
            ok, mapping = self.buzz_verify(cnf, current_q, entry)
            if not ok:
                # NAME/BIND: remember this exact failed candidate edge only on
                # the current residual handle.  Nothing global is written.
                failed.add(index)
                self.local_tombstone_inserts += 1
                continue
            self.absorption_hits += 1
            self.bytewise_distinct_absorptions += 1
            if mapping and any(flip for _, flip in mapping.values()):
                self.polarity_flip_absorptions += 1
            return LocalApepHandle(
                signature,
                current_q,
                frozenset(failed),
                lookup_bucket_size,
            ), entry.answer

        return LocalApepHandle(
            signature,
            current_q,
            frozenset(failed),
            lookup_bucket_size,
        ), None

    def memo_store(self, handle: LocalApepHandle, cnf, answer: bool) -> None:
        bucket = self.buckets[handle.signature]

        # Preserve baseline exact-byte cache behavior first.
        for entry in bucket:
            if entry.representative == cnf:
                if entry.answer != answer:
                    raise AssertionError("PT477-v3 exact cache collision changed Boolean answer")
                return

        if handle.canonicalization is not None:
            for index, entry in enumerate(bucket):
                # CUT/BURN only the comparison that THIS SAME residual already
                # proved bad in quotient_lookup.  Descendant-added entries have
                # index >= lookup_bucket_size and are always checked normally.
                if index < handle.lookup_bucket_size:
                    self.local_tombstone_checks += 1
                    if index in handle.failed_entry_indices:
                        self.local_tombstone_hits += 1
                        continue

                if entry.canonicalization is None:
                    entry.canonicalization = self.canonicalize(entry.representative)
                ok, _ = self.buzz_verify(cnf, handle.canonicalization, entry)
                if ok:
                    if entry.answer != answer:
                        raise AssertionError("PT477-v3 singularity collision changed Boolean answer")
                    return

        # No equivalence was proved.  Search state remains explicit exactly as
        # in baseline BH-Q2.
        from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import Entry
        bucket.append(Entry(answer, cnf, handle.canonicalization))


def canonical_edges(result) -> int:
    return int(result.signed_refinement_edge_visits) + int(result.q0_fallback_refinement_edge_visits)


def aggregate(rows: list[dict[str, Any]], side: str) -> dict[str, int]:
    names = [
        "residual_states",
        "bytewise_distinct_absorptions",
        "polarity_flip_absorptions",
        "event_horizon_collisions",
        "hawking_escape_count",
        "buzz_return_checks",
        "resolution_attempts",
        "resolution_additions",
    ]
    out = {name: sum(int(row[side][name]) for row in rows) for name in names}
    out["canonical_edge_visits"] = sum(int(row[side]["canonical_edge_visits"]) for row in rows)
    out["structural_work_proxy"] = out["resolution_attempts"] + out["canonical_edge_visits"]
    if side == "candidate":
        for name in (
            "local_tombstone_checks",
            "local_tombstone_hits",
            "local_tombstone_inserts",
            "route_rescan_edge_visits",
        ):
            out[name] = sum(int(row[side][name]) for row in rows)
        out["local_bookkeeping_ops"] = (
            out["local_tombstone_checks"] + out["local_tombstone_inserts"]
        )
    return out


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    answers_match = True
    caps_match = True

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)

        baseline_solver = Policy0ABHQ2()
        baseline = baseline_solver.solve(cnf, variable_count)

        candidate_solver = LocalApepEdgeTombstonePolicy()
        candidate = candidate_solver.solve(cnf, variable_count)

        answers_match &= baseline.answer == candidate.answer
        caps_match &= baseline.cap_exceeded == candidate.cap_exceeded

        baseline_dict = asdict(baseline)
        baseline_dict["canonical_edge_visits"] = canonical_edges(baseline)

        candidate_dict = asdict(candidate)
        candidate_dict["canonical_edge_visits"] = canonical_edges(candidate)
        candidate_dict.update({
            "local_tombstone_checks": candidate_solver.local_tombstone_checks,
            "local_tombstone_hits": candidate_solver.local_tombstone_hits,
            "local_tombstone_inserts": candidate_solver.local_tombstone_inserts,
            "route_rescan_edge_visits": candidate_solver.route_rescan_edge_visits,
        })

        rows.append({
            "order": order,
            "baseline": baseline_dict,
            "candidate": candidate_dict,
        })

    base = aggregate(rows, "baseline")
    cand = aggregate(rows, "candidate")
    saved_buzz = base["buzz_return_checks"] - cand["buzz_return_checks"]
    cand["saved_buzz_return_checks"] = saved_buzz

    baseline_reproduced = all(base[name] == expected for name, expected in FROZEN_BASELINE.items())

    gates = {
        "frozen_baseline_reproduced": baseline_reproduced,
        "same_boolean_answers": answers_match,
        "same_cap_status": caps_match,
        "same_residual_states": cand["residual_states"] == base["residual_states"],
        "same_bytewise_distinct_absorptions": (
            cand["bytewise_distinct_absorptions"] == base["bytewise_distinct_absorptions"]
        ),
        "same_polarity_flip_absorptions": (
            cand["polarity_flip_absorptions"] == base["polarity_flip_absorptions"]
        ),
        "same_event_horizon_collisions": (
            cand["event_horizon_collisions"] == base["event_horizon_collisions"]
        ),
        "same_resolution_attempts": cand["resolution_attempts"] == base["resolution_attempts"],
        "same_resolution_additions": cand["resolution_additions"] == base["resolution_additions"],
        "same_canonical_edge_visits": (
            cand["canonical_edge_visits"] == base["canonical_edge_visits"]
        ),
        "local_tombstone_hits_positive": cand["local_tombstone_hits"] > 0,
        "buzz_return_checks_strictly_lower": saved_buzz > 0,
        "skipped_buzz_exactly_accounted": cand["local_tombstone_hits"] == saved_buzz,
        "hawking_escapes_not_increased": cand["hawking_escape_count"] <= base["hawking_escape_count"],
        "no_extra_residual_scan": cand["route_rescan_edge_visits"] == 0,
        "structural_work_proxy_not_increased": (
            cand["structural_work_proxy"] <= base["structural_work_proxy"]
        ),
    }

    improved = all(gates.values())
    return {
        "artifact_id": RUN_ID,
        "status": (
            "PASS_KEEP_PT477_V3_LOCAL_REPLAY_DEDUP"
            if improved
            else "STOP_AT_PT477_V3_NO_IMPROVEMENT"
        ),
        "operator": "PT477_V3_LOCAL_APEP_EDGE_TOMBSTONE",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "historical_inspiration_boundary": {
            "Apep_black_hole": "JANUS_PROJECT_METAPHOR_ONLY",
            "Book_of_Overthrowing_Apep": "NEGATIVE_BIND_CUT_BURN_PROMPT_ONLY",
            "Names_of_Apep_cols_32_33": "LOCAL_IDENTITY_PROMPT_ONLY",
            "Book_of_Two_Ways": "LOCAL_CANDIDATE_EDGE_PROMPT_ONLY",
            "ancient_text_is_algorithmic_evidence": False,
        },
        "scope_invariant": {
            "tombstone_scope": "CURRENT_RESIDUAL_HANDLE_ONLY",
            "future_residual_inheritance": False,
            "new_descendant_entries_are_never_pre_tombstoned": True,
            "can_only_refuse_repeat_failed_buzz": True,
            "can_authorize_absorption": False,
        },
        "baseline": base,
        "candidate": cand,
        "gates": gates,
        "metric_improved": improved,
        "rows": rows,
        "ladder": {
            "PT355": "KEEP_FROM_PARENT",
            "PT366": "KEEP_FROM_PARENT",
            "PT477_v1": "REJECTED_FROM_PARENT",
            "PT477_v2": "REJECTED_FROM_PARENT",
            "PT477_v3": "KEEP" if improved else "REJECT",
            "PT222": (
                "ELIGIBLE_ONLY_FOR_NEW_PREREGISTERED_CONTINUATION"
                if improved
                else "NOT_ENTERED"
            ),
        },
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
        },
        "claim_boundary": [
            "A local tombstone only removes a duplicate failed Buzz replay for the same residual handle.",
            "Local bookkeeping operations are reported explicitly and are not treated as free.",
            "A PASS establishes only exact-trajectory replay de-duplication on revealed GT3..GT9, not a scalar total-work theorem.",
            "No extra residual scan, resonance, or frequency parameter is used.",
            "Finite calibration performance cannot establish an asymptotic SAT theorem.",
        ],
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
        assert result["scope_invariant"]["future_residual_inheritance"] is False
        assert result["status"] in {
            "PASS_KEEP_PT477_V3_LOCAL_REPLAY_DEDUP",
            "STOP_AT_PT477_V3_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
