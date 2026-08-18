#!/usr/bin/env python3
"""Q0 typed anchor-gauge quotient probe for JANUS-FC_local.

Q0 is deliberately conservative.  It uses deterministic signed-incidence color
refinement to derive a canonical variable order only when every residual
variable receives a unique final color.  If the partition remains ambiguous,
Q0 falls back to the existing byte-for-byte residual key.

A quotient cache hit across bytewise-distinct residuals is accepted only after
an explicit variable-permutation check maps the current residual exactly onto
its stored representative.  No statistical similarity score is a reuse rule.

This is a finite experiment, not a polynomial-time SAT theorem and not a result
about P versus NP.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256

from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    canonical_cnf,
    limited_resolution,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)


def digest_signature(value: object) -> str:
    return sha256(repr(value).encode("utf-8")).hexdigest()


def apply_permutation(cnf: CNF, permutation: dict[int, int]) -> CNF:
    return canonical_cnf(
        tuple(
            (permutation[abs(literal)] if literal > 0 else -permutation[abs(literal)])
            for literal in clause
        )
        for clause in cnf
    )


@dataclass(frozen=True)
class Q0Key:
    mode: str
    canonical: CNF


@dataclass
class Q0Canonicalization:
    key: Q0Key
    old_to_canonical: dict[int, int]
    discrete: bool
    refinement_rounds: int
    refinement_edge_visits: int


def q0_canonicalize(cnf: CNF) -> Q0Canonicalization:
    variables = sorted({abs(literal) for clause in cnf for literal in clause})
    if not variables:
        return Q0Canonicalization(Q0Key("Q0", cnf), {}, True, 0, 0)

    var_incidence: dict[int, list[tuple[int, int]]] = defaultdict(list)
    clause_literals: dict[int, list[tuple[int, int]]] = defaultdict(list)

    width_domain = sorted({len(clause) for clause in cnf})
    width_index = {width: index for index, width in enumerate(width_domain)}

    positive_width_counts: dict[int, list[int]] = {
        variable: [0] * len(width_domain) for variable in variables
    }
    negative_width_counts: dict[int, list[int]] = {
        variable: [0] * len(width_domain) for variable in variables
    }

    for clause_index, clause in enumerate(cnf):
        width_slot = width_index[len(clause)]
        for literal in clause:
            variable = abs(literal)
            sign = 1 if literal > 0 else -1
            var_incidence[variable].append((clause_index, sign))
            clause_literals[clause_index].append((variable, sign))
            target = positive_width_counts if sign > 0 else negative_width_counts
            target[variable][width_slot] += 1

    var_colors = {
        variable: digest_signature(
            (
                "V",
                tuple(positive_width_counts[variable]),
                tuple(negative_width_counts[variable]),
            )
        )
        for variable in variables
    }
    clause_colors = {
        clause_index: digest_signature(("C", len(clause)))
        for clause_index, clause in enumerate(cnf)
    }

    edge_visits = 0
    rounds = 0
    previous_partition_size = -1
    max_rounds = len(variables) + len(cnf) + 1

    for _ in range(max_rounds):
        partition_size = len(set(var_colors.values())) + len(set(clause_colors.values()))
        if partition_size == previous_partition_size:
            break
        previous_partition_size = partition_size
        rounds += 1

        new_var_colors: dict[int, str] = {}
        for variable in variables:
            neighborhood = []
            for clause_index, sign in var_incidence[variable]:
                neighborhood.append((sign, clause_colors[clause_index]))
                edge_visits += 1
            new_var_colors[variable] = digest_signature(
                ("V", var_colors[variable], tuple(sorted(neighborhood)))
            )

        new_clause_colors: dict[int, str] = {}
        for clause_index, clause in enumerate(cnf):
            neighborhood = []
            for variable, sign in clause_literals[clause_index]:
                neighborhood.append((sign, var_colors[variable]))
                edge_visits += 1
            new_clause_colors[clause_index] = digest_signature(
                (
                    "C",
                    clause_colors[clause_index],
                    len(clause),
                    tuple(sorted(neighborhood)),
                )
            )

        var_colors = new_var_colors
        clause_colors = new_clause_colors

    discrete = len(set(var_colors.values())) == len(variables)
    if not discrete:
        return Q0Canonicalization(
            key=Q0Key("RAW", cnf),
            old_to_canonical={variable: variable for variable in variables},
            discrete=False,
            refinement_rounds=rounds,
            refinement_edge_visits=edge_visits,
        )

    ordered_variables = sorted(variables, key=lambda variable: var_colors[variable])
    old_to_canonical = {
        variable: index + 1 for index, variable in enumerate(ordered_variables)
    }
    canonical = apply_permutation(cnf, old_to_canonical)
    return Q0Canonicalization(
        key=Q0Key("Q0", canonical),
        old_to_canonical=old_to_canonical,
        discrete=True,
        refinement_rounds=rounds,
        refinement_edge_visits=edge_visits,
    )


@dataclass
class Q0Result:
    answer: bool | None
    cap_exceeded: bool
    residual_states: int
    quotient_entries: int
    quotient_hits: int
    bytewise_distinct_hits: int
    discrete_states: int
    fallback_states: int
    refinement_rounds: int
    refinement_edge_visits: int
    resolution_attempts: int
    resolution_additions: int
    affine_equations: int


class Policy0AQ0:
    def __init__(self, state_cap: int | None = None):
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> Q0Result:
        self.states = 0
        self.memo: dict[Q0Key, tuple[bool, CNF, dict[int, int]]] = {}
        self.quotient_hits = 0
        self.bytewise_distinct_hits = 0
        self.discrete_states = 0
        self.fallback_states = 0
        self.refinement_rounds = 0
        self.refinement_edge_visits = 0
        self.resolution_attempts = 0
        self.resolution_additions = 0

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.result(affine_answer, False)

        try:
            answer = self.search(cnf)
            return self.result(answer, False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> Q0Result:
        return Q0Result(
            answer=answer,
            cap_exceeded=cap_exceeded,
            residual_states=self.states,
            quotient_entries=len(self.memo),
            quotient_hits=self.quotient_hits,
            bytewise_distinct_hits=self.bytewise_distinct_hits,
            discrete_states=self.discrete_states,
            fallback_states=self.fallback_states,
            refinement_rounds=self.refinement_rounds,
            refinement_edge_visits=self.refinement_edge_visits,
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
            affine_equations=self.affine_equation_count,
        )

    def quotient_lookup(self, cnf: CNF):
        q = q0_canonicalize(cnf)
        self.refinement_rounds += q.refinement_rounds
        self.refinement_edge_visits += q.refinement_edge_visits
        if q.discrete:
            self.discrete_states += 1
        else:
            self.fallback_states += 1

        stored = self.memo.get(q.key)
        if stored is None:
            return q, None

        answer, representative, representative_map = stored
        self.quotient_hits += 1
        if representative != cnf:
            self.bytewise_distinct_hits += 1

        if q.key.mode == "Q0":
            representative_inverse = {
                canonical: old for old, canonical in representative_map.items()
            }
            permutation = {
                current_old: representative_inverse[canonical]
                for current_old, canonical in q.old_to_canonical.items()
            }
            if apply_permutation(cnf, permutation) != representative:
                raise AssertionError("Q0 permutation verification failed")
        else:
            if representative != cnf:
                raise AssertionError("RAW fallback key cannot merge distinct residuals")

        return q, answer

    def memo_store(self, q: Q0Canonicalization, cnf: CNF, answer: bool) -> None:
        existing = self.memo.get(q.key)
        if existing is None:
            self.memo[q.key] = (answer, cnf, dict(q.old_to_canonical))
        elif existing[0] != answer:
            raise AssertionError("Q0 cache collision changed Boolean answer")

    def search(self, cnf: CNF) -> bool:
        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            return False
        assert propagated is not None
        if not propagated:
            return True
        cnf = propagated

        q, cached_answer = self.quotient_lookup(cnf)
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
            self.memo_store(q, cnf, False)
            return False

        propagated, contradiction = unit_propagate(saturated)
        if contradiction:
            self.memo_store(q, cnf, False)
            return False
        assert propagated is not None
        if not propagated:
            self.memo_store(q, cnf, True)
            return True

        frequencies = Counter(
            abs(literal) for clause in propagated for literal in clause
        )
        maximum = max(frequencies.values())
        variable = min(
            candidate
            for candidate, frequency in frequencies.items()
            if frequency == maximum
        )

        for value in (False, True):
            child = simplify_one(propagated, variable, value)
            if child is not None and self.search(child):
                self.memo_store(q, cnf, True)
                return True

        self.memo_store(q, cnf, False)
        return False


def run_order(order: int, state_cap: int | None) -> Q0Result:
    cnf, variable_count = graph_tautology_cnf(order)
    result = Policy0AQ0(state_cap=state_cap).solve(cnf, variable_count)
    literal_occurrences = sum(len(clause) for clause in cnf)
    encoding_units = variable_count + len(cnf) + literal_occurrences

    print(f"ORDER_SIZE = {order}")
    print(f"  encoding_units = {encoding_units}")
    print(f"  answer = {result.answer}")
    print(f"  cap_exceeded = {str(result.cap_exceeded).lower()}")
    print(f"  residual_states = {result.residual_states}")
    print(f"  quotient_entries = {result.quotient_entries}")
    print(f"  quotient_hits = {result.quotient_hits}")
    print(f"  bytewise_distinct_hits = {result.bytewise_distinct_hits}")
    print(f"  discrete_states = {result.discrete_states}")
    print(f"  fallback_states = {result.fallback_states}")
    print(f"  refinement_rounds = {result.refinement_rounds}")
    print(f"  refinement_edge_visits = {result.refinement_edge_visits}")
    print(f"  resolution_attempts = {result.resolution_attempts}")
    print(f"  resolution_additions = {result.resolution_additions}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", default="3,4,5,6,7,8,9")
    parser.add_argument("--state-cap", type=int, default=None)
    args = parser.parse_args()

    orders = [int(item) for item in args.orders.split(",") if item]
    for order in orders:
        run_order(order, args.state_cap)

    print("JANUS_Q0_TYPED_ANCHOR_GAUGE_PROBE = COMPLETE")
    print("claim_boundary = finite quotient probe; P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
