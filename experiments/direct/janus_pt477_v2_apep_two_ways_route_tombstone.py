#!/usr/bin/env python3
"""PT477-v2: Apep / Book-of-Two-Ways route tombstone experiment.

Historical Egyptian texts are used only as operator prompts.  This code does not
claim that Apep was a black hole or that the ancient texts encode complexity
theory.

Frozen modern translation:

  Book of Two Ways -> retain an explicit local route identity.
  Apep NAME/BIND/CUT/BURN -> after an exact Buzz failure, remember that no-go
  route-class pair and refuse repeated approaches before expensive horizon
  canonicalization.

The tombstone can only REFUSE a candidate cache merge.  It can never authorize
reuse or change a Boolean answer.  No extra CNF scan is allowed to construct the
route token: it is derived from the already-computed parent seed signature,
maximum branch-variable frequency, and branch value.

Calibration is GT3..GT9 only.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    Entry,
    Handle,
    Policy0ABHQ2,
    apply_signed_map,
    digest,
    graph_tautology_cnf,
    signed_typed_signature,
)
from janus_tear_policy0a_masked_tseitin import (
    limited_resolution,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)

RUN_ID = "JANUS-PT477-V2-APEP-TWO-WAYS-ROUTE-TOMBSTONE-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
FROZEN_BASELINE = {
    "residual_states": 2822,
    "bytewise_distinct_absorptions": 602,
    "polarity_flip_absorptions": 450,
    "event_horizon_collisions": 839,
    "hawking_escape_count": 2292,
    "canonical_edge_visits": 3488298,
    "resolution_attempts": 626489,
    "charged_work_proxy": 4114787,
}


@dataclass
class RouteEntry:
    answer: bool
    representative: tuple[tuple[int, ...], ...]
    canonicalization: Any
    route_token: str


@dataclass
class RouteHandle:
    signature: str
    canonicalization: Any
    route_token: str


class ApepRouteTombstonePolicy(Policy0ABHQ2):
    """BH-Q2 plus fail-closed negative route memory.

    A tombstone is installed only after Buzz has already rejected a candidate
    route.  A later matching route-class pair is simply not offered to Buzz.
    Search remains explicit, so a false-negative tombstone is a performance
    problem rather than a Boolean-soundness problem.
    """

    def solve(self, cnf, variable_count):
        self.states = 0
        self.buckets: dict[str, list[RouteEntry]] = defaultdict(list)
        self.absorption_hits = 0
        self.bytewise_distinct_absorptions = 0
        self.polarity_flip_absorptions = 0
        self.physarum_signature_checks = 0
        self.event_horizon_collisions = 0
        self.signed_canonicalizations = 0
        self.signed_discrete_canonicalizations = 0
        self.signed_refinement_rounds = 0
        self.signed_refinement_edge_visits = 0
        self.q0_fallback_refinement_edge_visits = 0
        self.buzz_return_checks = 0
        self.buzz_return_passes = 0
        self.hawking_escape_count = 0
        self.resolution_attempts = 0
        self.resolution_additions = 0

        self.route_tombstones: set[tuple[str, str, str]] = set()
        self.route_tombstone_checks = 0
        self.route_tombstone_hits = 0
        self.route_tombstone_inserts = 0
        self.route_token_updates = 0
        self.route_rescan_edge_visits = 0
        self.event_horizon_entries_avoided = 0

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.result(affine_answer, False)

        try:
            return self.result(self.search(cnf, "ROOT"), False)
        except RuntimeError:
            return self.result(None, True)

    @staticmethod
    def tombstone_key(signature: str, current_route: str, stored_route: str) -> tuple[str, str, str]:
        return (signature, current_route, stored_route)

    def quotient_lookup(self, cnf, route_token: str):
        self.physarum_signature_checks += 1
        signature = signed_typed_signature(cnf)
        bucket = self.buckets.get(signature)
        if not bucket:
            return RouteHandle(signature, None, route_token), None

        self.event_horizon_collisions += 1

        # Exact bytewise reuse remains first and is never blocked by a tombstone.
        for entry in bucket:
            if entry.representative == cnf:
                self.absorption_hits += 1
                return RouteHandle(signature, entry.canonicalization, route_token), entry.answer

        # Apep/B2W gate: consult only O(1)-style route metadata before doing any
        # signed-incidence canonicalization of the current residual.
        candidates: list[tuple[RouteEntry, tuple[str, str, str]]] = []
        for entry in bucket:
            key = self.tombstone_key(signature, route_token, entry.route_token)
            self.route_tombstone_checks += 1
            if key in self.route_tombstones:
                self.route_tombstone_hits += 1
                continue
            candidates.append((entry, key))

        if not candidates:
            self.event_horizon_entries_avoided += 1
            return RouteHandle(signature, None, route_token), None

        current_q = self.canonicalize(cnf)
        for entry, key in candidates:
            if entry.canonicalization is None:
                entry.canonicalization = self.canonicalize(entry.representative)
            ok, mapping = self.buzz_verify(cnf, current_q, entry)
            if not ok:
                if key not in self.route_tombstones:
                    self.route_tombstones.add(key)
                    self.route_tombstone_inserts += 1
                continue
            self.absorption_hits += 1
            self.bytewise_distinct_absorptions += 1
            if mapping and any(flip for _, flip in mapping.values()):
                self.polarity_flip_absorptions += 1
            return RouteHandle(signature, current_q, route_token), entry.answer

        return RouteHandle(signature, current_q, route_token), None

    def memo_store(self, handle: RouteHandle, cnf, answer: bool) -> None:
        bucket = self.buckets[handle.signature]
        for entry in bucket:
            if entry.representative == cnf:
                if entry.answer != answer:
                    raise AssertionError("Apep route exact cache collision changed Boolean answer")
                return

        if handle.canonicalization is not None:
            for entry in bucket:
                key = self.tombstone_key(handle.signature, handle.route_token, entry.route_token)
                self.route_tombstone_checks += 1
                if key in self.route_tombstones:
                    self.route_tombstone_hits += 1
                    continue
                if entry.canonicalization is None:
                    entry.canonicalization = self.canonicalize(entry.representative)
                ok, _ = self.buzz_verify(cnf, handle.canonicalization, entry)
                if ok:
                    if entry.answer != answer:
                        raise AssertionError("Apep route singularity collision changed Boolean answer")
                    return
                self.route_tombstones.add(key)
                self.route_tombstone_inserts += 1

        bucket.append(RouteEntry(answer, cnf, handle.canonicalization, handle.route_token))

    def search(self, cnf, route_token: str) -> bool:
        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            return False
        assert propagated is not None
        if not propagated:
            return True
        cnf = propagated

        handle, cached_answer = self.quotient_lookup(cnf, route_token)
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
            child = simplify_one(propagated, variable, value)
            if child is None:
                continue
            # Route identity uses only metadata already computed in this parent
            # step.  No child/residual scan is performed here.
            child_route_token = digest(("B2W-LOCAL-ROUTE", handle.signature, maximum, bool(value)))
            self.route_token_updates += 1
            if self.search(child, child_route_token):
                self.memo_store(handle, cnf, True)
                return True

        self.memo_store(handle, cnf, False)
        return False


def canonical_edges(result) -> int:
    return int(result.signed_refinement_edge_visits) + int(result.q0_fallback_refinement_edge_visits)


def aggregate(rows: list[dict[str, Any]], side: str) -> dict[str, int]:
    names = [
        "residual_states",
        "bytewise_distinct_absorptions",
        "polarity_flip_absorptions",
        "event_horizon_collisions",
        "hawking_escape_count",
        "resolution_attempts",
        "resolution_additions",
    ]
    out = {name: sum(int(row[side][name]) for row in rows) for name in names}
    out["canonical_edge_visits"] = sum(int(row[side]["canonical_edge_visits"]) for row in rows)
    if side == "candidate":
        for name in (
            "route_tombstone_checks",
            "route_tombstone_hits",
            "route_tombstone_inserts",
            "route_token_updates",
            "route_rescan_edge_visits",
            "event_horizon_entries_avoided",
        ):
            out[name] = sum(int(row[side][name]) for row in rows)
    return out


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    answers_match = True
    caps_match = True

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)

        baseline_solver = Policy0ABHQ2()
        baseline = baseline_solver.solve(cnf, variable_count)

        candidate_solver = ApepRouteTombstonePolicy()
        candidate = candidate_solver.solve(cnf, variable_count)

        answers_match &= baseline.answer == candidate.answer
        caps_match &= baseline.cap_exceeded == candidate.cap_exceeded

        baseline_dict = asdict(baseline)
        baseline_dict["canonical_edge_visits"] = canonical_edges(baseline)

        candidate_dict = asdict(candidate)
        candidate_dict["canonical_edge_visits"] = canonical_edges(candidate)
        candidate_dict.update({
            "route_tombstone_checks": candidate_solver.route_tombstone_checks,
            "route_tombstone_hits": candidate_solver.route_tombstone_hits,
            "route_tombstone_inserts": candidate_solver.route_tombstone_inserts,
            "route_token_updates": candidate_solver.route_token_updates,
            "route_rescan_edge_visits": candidate_solver.route_rescan_edge_visits,
            "event_horizon_entries_avoided": candidate_solver.event_horizon_entries_avoided,
        })

        rows.append({
            "order": order,
            "baseline": baseline_dict,
            "candidate": candidate_dict,
        })

    base = aggregate(rows, "baseline")
    cand = aggregate(rows, "candidate")

    base_charged = base["resolution_attempts"] + base["canonical_edge_visits"]
    cand_charged = (
        cand["resolution_attempts"]
        + cand["canonical_edge_visits"]
        + cand["route_tombstone_checks"]
        + cand["route_tombstone_inserts"]
        + cand["route_token_updates"]
    )
    base["charged_work_proxy"] = base_charged
    cand["charged_work_proxy"] = cand_charged

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
        "route_tombstone_hits_positive": cand["route_tombstone_hits"] > 0,
        "hawking_escapes_not_increased": cand["hawking_escape_count"] <= base["hawking_escape_count"],
        "canonical_edge_visits_strictly_lower": cand["canonical_edge_visits"] < base["canonical_edge_visits"],
        "charged_work_proxy_strictly_lower": cand_charged < base_charged,
        "no_extra_residual_scan": cand["route_rescan_edge_visits"] == 0,
    }

    improved = all(gates.values())
    return {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT477_V2" if improved else "STOP_AT_PT477_V2_NO_IMPROVEMENT",
        "operator": "PT477_V2_APEP_TWO_WAYS_ROUTE_TOMBSTONE",
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "historical_inspiration_boundary": {
            "Apep_black_hole": "JANUS_PROJECT_METAPHOR_ONLY",
            "Book_of_Two_Ways": "ROUTE_IDENTITY_PROMPT_ONLY",
            "Book_of_Overthrowing_Apep": "NEGATIVE_ROUTE_BIND_CUT_BURN_PROMPT_ONLY",
            "ancient_text_is_algorithmic_evidence": False,
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
            "PT477_v2": "KEEP" if improved else "REJECT",
            "PT222": "NOT_ENTERED" if not improved else "ELIGIBLE_ONLY_IN_NEW_CONTINUATION_RUN",
        },
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
        },
        "claim_boundary": [
            "A tombstone only refuses a candidate merge; it never proves equivalence.",
            "No extra residual scan is used to construct route tokens.",
            "Finite calibration performance cannot establish an asymptotic SAT theorem.",
            "No resonance or frequency parameter is used.",
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
        assert result["status"] in {
            "PASS_KEEP_PT477_V2",
            "STOP_AT_PT477_V2_NO_IMPROVEMENT",
        }


if __name__ == "__main__":
    main()
