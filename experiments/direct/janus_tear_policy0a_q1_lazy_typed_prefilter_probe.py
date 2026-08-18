#!/usr/bin/env python3
"""Q1 lazy typed-prefilter probe for JANUS-FC_local.

Q1 keeps Q0's proof-preserving merge rule unchanged, but postpones expensive
signed-incidence gauge refinement until a cheap permutation-invariant typed
signature collides with an already completed residual.

The cheap signature is only a filter. It NEVER authorizes reuse. Reuse still
requires Q0 canonical equality plus the explicit variable-permutation replay.
Thus a false-positive cheap collision costs time but cannot change the Boolean
answer. A false-negative would be serious, so the signature is deliberately
constructed from invariants already present in Q0's initial coloring:
  * multiset of clause widths;
  * multiset of each variable's positive/negative occurrence counts by width.
Any variable-renaming equivalence admitted by Q0 must preserve these values.

Calibration only. No new untouched holdout is inspected here. P_VS_NP remains
OPEN regardless of finite performance.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256

from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    limited_resolution,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)
from janus_tear_policy0a_q0_typed_anchor_gauge_probe import (
    Q0Canonicalization,
    apply_permutation,
    q0_canonicalize,
)


def digest(value: object) -> str:
    return sha256(repr(value).encode("utf-8")).hexdigest()


def cheap_typed_signature(cnf: CNF) -> str:
    """Permutation-invariant prefilter; never a proof of equivalence."""
    variables = sorted({abs(lit) for clause in cnf for lit in clause})
    widths = sorted({len(clause) for clause in cnf})
    width_index = {width: i for i, width in enumerate(widths)}
    pos = {v: [0] * len(widths) for v in variables}
    neg = {v: [0] * len(widths) for v in variables}
    clause_widths = []

    for clause in cnf:
        clause_widths.append(len(clause))
        slot = width_index[len(clause)]
        for lit in clause:
            target = pos if lit > 0 else neg
            target[abs(lit)][slot] += 1

    variable_profiles = sorted(
        (tuple(pos[v]), tuple(neg[v])) for v in variables
    )
    return digest((tuple(sorted(clause_widths)), tuple(variable_profiles)))


@dataclass
class Entry:
    answer: bool
    representative: CNF
    q0: Q0Canonicalization | None


@dataclass
class Handle:
    signature: str
    q0: Q0Canonicalization | None


@dataclass
class Q1Result:
    answer: bool | None
    cap_exceeded: bool
    residual_states: int
    quotient_entries: int
    quotient_hits: int
    bytewise_distinct_hits: int
    cheap_signature_checks: int
    cheap_bucket_collisions: int
    q0_canonicalizations: int
    q0_discrete_canonicalizations: int
    q0_fallback_canonicalizations: int
    refinement_rounds: int
    refinement_edge_visits: int
    resolution_attempts: int
    resolution_additions: int
    affine_equations: int


class Policy0AQ1Lazy:
    def __init__(self, state_cap: int | None = None):
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> Q1Result:
        self.states = 0
        self.buckets: dict[str, list[Entry]] = defaultdict(list)
        self.quotient_hits = 0
        self.bytewise_distinct_hits = 0
        self.cheap_signature_checks = 0
        self.cheap_bucket_collisions = 0
        self.q0_canonicalizations = 0
        self.q0_discrete_canonicalizations = 0
        self.q0_fallback_canonicalizations = 0
        self.refinement_rounds = 0
        self.refinement_edge_visits = 0
        self.resolution_attempts = 0
        self.resolution_additions = 0

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.result(affine_answer, False)

        try:
            return self.result(self.search(cnf), False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> Q1Result:
        return Q1Result(
            answer=answer,
            cap_exceeded=cap_exceeded,
            residual_states=self.states,
            quotient_entries=sum(len(items) for items in self.buckets.values()),
            quotient_hits=self.quotient_hits,
            bytewise_distinct_hits=self.bytewise_distinct_hits,
            cheap_signature_checks=self.cheap_signature_checks,
            cheap_bucket_collisions=self.cheap_bucket_collisions,
            q0_canonicalizations=self.q0_canonicalizations,
            q0_discrete_canonicalizations=self.q0_discrete_canonicalizations,
            q0_fallback_canonicalizations=self.q0_fallback_canonicalizations,
            refinement_rounds=self.refinement_rounds,
            refinement_edge_visits=self.refinement_edge_visits,
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
            affine_equations=self.affine_equation_count,
        )

    def canonicalize(self, cnf: CNF) -> Q0Canonicalization:
        q = q0_canonicalize(cnf)
        self.q0_canonicalizations += 1
        self.refinement_rounds += q.refinement_rounds
        self.refinement_edge_visits += q.refinement_edge_visits
        if q.discrete:
            self.q0_discrete_canonicalizations += 1
        else:
            self.q0_fallback_canonicalizations += 1
        return q

    @staticmethod
    def verify_q0_equivalence(
        current: CNF,
        current_q: Q0Canonicalization,
        stored: Entry,
    ) -> bool:
        assert stored.q0 is not None
        if current_q.key != stored.q0.key:
            return False

        if current_q.key.mode == "RAW":
            return current == stored.representative

        representative_inverse = {
            canonical: old
            for old, canonical in stored.q0.old_to_canonical.items()
        }
        permutation = {
            current_old: representative_inverse[canonical]
            for current_old, canonical in current_q.old_to_canonical.items()
        }
        return apply_permutation(current, permutation) == stored.representative

    def quotient_lookup(self, cnf: CNF) -> tuple[Handle, bool | None]:
        self.cheap_signature_checks += 1
        signature = cheap_typed_signature(cnf)
        bucket = self.buckets.get(signature)
        if not bucket:
            return Handle(signature, None), None

        self.cheap_bucket_collisions += 1

        # Exact bytewise hit is always safe and requires no gauge refinement.
        for entry in bucket:
            if entry.representative == cnf:
                self.quotient_hits += 1
                return Handle(signature, entry.q0), entry.answer

        current_q = self.canonicalize(cnf)
        for entry in bucket:
            if entry.q0 is None:
                entry.q0 = self.canonicalize(entry.representative)
            if self.verify_q0_equivalence(cnf, current_q, entry):
                self.quotient_hits += 1
                self.bytewise_distinct_hits += 1
                return Handle(signature, current_q), entry.answer

        return Handle(signature, current_q), None

    def memo_store(self, handle: Handle, cnf: CNF, answer: bool) -> None:
        bucket = self.buckets[handle.signature]
        for entry in bucket:
            if entry.representative == cnf:
                if entry.answer != answer:
                    raise AssertionError("Q1 exact cache collision changed Boolean answer")
                return

        # If a Q0 key is already known for this residual, ensure no contradictory
        # answer can hide behind the same certified quotient class.
        if handle.q0 is not None:
            for entry in bucket:
                if entry.q0 is None:
                    entry.q0 = self.canonicalize(entry.representative)
                if entry.q0.key == handle.q0.key:
                    if not self.verify_q0_equivalence(cnf, handle.q0, entry):
                        raise AssertionError("Q1 equal Q0 key failed permutation replay")
                    if entry.answer != answer:
                        raise AssertionError("Q1 quotient collision changed Boolean answer")
                    return

        bucket.append(Entry(answer, cnf, handle.q0))

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
            child = simplify_one(propagated, variable, value)
            if child is not None and self.search(child):
                self.memo_store(handle, cnf, True)
                return True

        self.memo_store(handle, cnf, False)
        return False


def run_order(order: int, state_cap: int | None) -> Q1Result:
    cnf, variable_count = graph_tautology_cnf(order)
    result = Policy0AQ1Lazy(state_cap=state_cap).solve(cnf, variable_count)
    encoding_units = variable_count + len(cnf) + sum(len(c) for c in cnf)
    print(f"ORDER_SIZE = {order}")
    print(f"  encoding_units = {encoding_units}")
    for name in (
        "answer", "cap_exceeded", "residual_states", "quotient_entries",
        "quotient_hits", "bytewise_distinct_hits", "cheap_signature_checks",
        "cheap_bucket_collisions", "q0_canonicalizations",
        "q0_discrete_canonicalizations", "q0_fallback_canonicalizations",
        "refinement_rounds", "refinement_edge_visits", "resolution_attempts",
        "resolution_additions",
    ):
        print(f"  {name} = {getattr(result, name)}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", default="3,4,5,6,7,8,9,10,11")
    parser.add_argument("--state-cap", type=int, default=None)
    args = parser.parse_args()

    for raw in args.orders.split(","):
        if raw:
            run_order(int(raw), args.state_cap)

    print("JANUS_Q1_LAZY_TYPED_PREFILTER_PROBE = COMPLETE")
    print("claim_boundary = calibration/replay only; no new holdout; P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
