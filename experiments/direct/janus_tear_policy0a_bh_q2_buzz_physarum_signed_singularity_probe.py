#!/usr/bin/env python3
"""BH-Q2 Buzz/Physarum proof-carrying signed-singularity calibration probe.

PHYSARUM = cheap signed-invariant attraction to candidate singularity buckets.
BUZZ     = exact signed-permutation replay plus inverse/round-trip guard.

No similarity score authorizes reuse. A bytewise-distinct residual is absorbed
only after an explicit bijective signed variable map sends it exactly to the
stored representative and the inverse sends the representative exactly back.

The signed quotient is stronger than Q0 variable renaming because an individual
source variable may map to either x_j or NOT x_j. SAT is preserved and Boolean
witnesses have an explicit reversible coordinate transform.

Frozen calibration only. P_VS_NP remains OPEN.
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
from janus_tear_policy0a_q0_typed_anchor_gauge_probe import q0_canonicalize


def digest(value: object) -> str:
    return sha256(repr(value).encode("utf-8")).hexdigest()


SignedMap = dict[int, tuple[int, bool]]


def apply_signed_map(cnf: CNF, mapping: SignedMap) -> CNF:
    """Apply x_src -> x_dst when flip=False, x_src -> NOT x_dst when flip=True."""
    transformed = []
    for clause in cnf:
        out = []
        for literal in clause:
            source = abs(literal)
            target, flip = mapping[source]
            source_positive = literal > 0
            target_positive = bool(source_positive) ^ bool(flip)
            out.append(target if target_positive else -target)
        transformed.append(tuple(out))
    return canonical_cnf(transformed)


def invert_signed_map(mapping: SignedMap) -> SignedMap:
    inverse: SignedMap = {}
    for source, (target, flip) in mapping.items():
        if target in inverse:
            raise AssertionError("signed map is not injective")
        inverse[target] = (source, bool(flip))
    if len(inverse) != len(mapping):
        raise AssertionError("signed map inverse lost a variable")
    return inverse


def compose_current_to_representative(
    current_to_canonical: SignedMap,
    representative_to_canonical: SignedMap,
) -> SignedMap:
    rep_by_canonical: dict[int, tuple[int, bool]] = {}
    for rep_var, (canonical_var, rep_flip) in representative_to_canonical.items():
        if canonical_var in rep_by_canonical:
            raise AssertionError("representative canonical map is not bijective")
        rep_by_canonical[canonical_var] = (rep_var, bool(rep_flip))

    mapping: SignedMap = {}
    for current_var, (canonical_var, current_flip) in current_to_canonical.items():
        if canonical_var not in rep_by_canonical:
            raise AssertionError("canonical coordinate missing in representative")
        rep_var, rep_flip = rep_by_canonical[canonical_var]
        mapping[current_var] = (rep_var, bool(current_flip) ^ bool(rep_flip))
    return mapping


def signed_map_roundtrip_ok(mapping: SignedMap) -> bool:
    try:
        inverse = invert_signed_map(mapping)
    except AssertionError:
        return False
    if set(mapping) != set(inverse.values() if False else mapping):
        # Deliberately no clever shortcut: explicit literal checks below are the gate.
        pass
    for source, (target, flip) in mapping.items():
        if target not in inverse:
            return False
        back_source, back_flip = inverse[target]
        if back_source != source or bool(back_flip) != bool(flip):
            return False
        for source_positive in (False, True):
            target_positive = bool(source_positive) ^ bool(flip)
            restored_positive = bool(target_positive) ^ bool(back_flip)
            if restored_positive != source_positive:
                return False
    return True


def signed_typed_signature(cnf: CNF) -> str:
    """Cheap signed-permutation invariant. Attraction only; never a proof."""
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

    variable_profiles = []
    for variable in variables:
        pair = sorted((tuple(pos[variable]), tuple(neg[variable])))
        variable_profiles.append(tuple(pair))

    return digest((tuple(sorted(clause_widths)), tuple(sorted(variable_profiles))))


@dataclass(frozen=True)
class SingularityKey:
    mode: str
    canonical: CNF


@dataclass
class SingularityCanonicalization:
    key: SingularityKey
    old_to_canonical: SignedMap
    signed_discrete: bool
    signed_refinement_rounds: int
    signed_refinement_edge_visits: int
    q0_fallback_edge_visits: int


def signed_incidence_canonicalize(cnf: CNF) -> SingularityCanonicalization:
    """Canonicalize only when signed literal/clause refinement is fully oriented.

    If the signed partition stays ambiguous, fall back to Q0; if Q0 is RAW, exact
    byte equality remains the only merge rule.
    """
    variables = sorted({abs(lit) for clause in cnf for lit in clause})
    if not variables:
        return SingularityCanonicalization(
            SingularityKey("BH2", cnf), {}, True, 0, 0, 0
        )

    widths = sorted({len(clause) for clause in cnf})
    width_index = {width: i for i, width in enumerate(widths)}

    literal_incidence: dict[tuple[int, int], list[int]] = defaultdict(list)
    clause_literals: dict[int, list[tuple[int, int]]] = defaultdict(list)
    literal_width_counts: dict[tuple[int, int], list[int]] = {
        (v, sign): [0] * len(widths)
        for v in variables
        for sign in (-1, 1)
    }

    for clause_index, clause in enumerate(cnf):
        slot = width_index[len(clause)]
        for lit in clause:
            node = (abs(lit), 1 if lit > 0 else -1)
            literal_incidence[node].append(clause_index)
            clause_literals[clause_index].append(node)
            literal_width_counts[node][slot] += 1

    literal_colors = {
        node: digest(("L", tuple(literal_width_counts[node])))
        for node in literal_width_counts
    }
    clause_colors = {
        index: digest(("C", len(clause)))
        for index, clause in enumerate(cnf)
    }

    previous_partition_size = -1
    rounds = 0
    edge_visits = 0
    max_rounds = 2 * len(variables) + len(cnf) + 1

    for _ in range(max_rounds):
        partition_size = len(set(literal_colors.values())) + len(set(clause_colors.values()))
        if partition_size == previous_partition_size:
            break
        previous_partition_size = partition_size
        rounds += 1

        new_literal_colors: dict[tuple[int, int], str] = {}
        for node in literal_colors:
            variable, sign = node
            complement = (variable, -sign)
            neighborhood = []
            for clause_index in literal_incidence[node]:
                neighborhood.append(clause_colors[clause_index])
                edge_visits += 1
            new_literal_colors[node] = digest(
                (
                    "L",
                    literal_colors[node],
                    literal_colors[complement],
                    tuple(sorted(neighborhood)),
                )
            )

        new_clause_colors: dict[int, str] = {}
        for clause_index, clause in enumerate(cnf):
            neighborhood = []
            for node in clause_literals[clause_index]:
                neighborhood.append(literal_colors[node])
                edge_visits += 1
            new_clause_colors[clause_index] = digest(
                ("C", clause_colors[clause_index], len(clause), tuple(sorted(neighborhood)))
            )

        literal_colors = new_literal_colors
        clause_colors = new_clause_colors

    pair_rows = []
    oriented = True
    for variable in variables:
        pos_color = literal_colors[(variable, 1)]
        neg_color = literal_colors[(variable, -1)]
        if pos_color == neg_color:
            oriented = False
            break
        pair_rows.append((tuple(sorted((pos_color, neg_color))), variable, pos_color, neg_color))

    if oriented and len({row[0] for row in pair_rows}) == len(variables):
        pair_rows.sort(key=lambda row: row[0])
        mapping: SignedMap = {}
        for canonical_variable, (_, old_variable, pos_color, neg_color) in enumerate(pair_rows, start=1):
            # The smaller literal color becomes canonical positive orientation.
            flip = not (pos_color < neg_color)
            mapping[old_variable] = (canonical_variable, flip)
        canonical = apply_signed_map(cnf, mapping)
        return SingularityCanonicalization(
            SingularityKey("BH2", canonical),
            mapping,
            True,
            rounds,
            edge_visits,
            0,
        )

    q0 = q0_canonicalize(cnf)
    q0_map: SignedMap = {
        old: (canonical, False)
        for old, canonical in q0.old_to_canonical.items()
    }
    return SingularityCanonicalization(
        SingularityKey(q0.key.mode, q0.key.canonical),
        q0_map,
        False,
        rounds,
        edge_visits,
        q0.refinement_edge_visits,
    )


@dataclass
class Entry:
    answer: bool
    representative: CNF
    canonicalization: SingularityCanonicalization | None


@dataclass
class Handle:
    signature: str
    canonicalization: SingularityCanonicalization | None


@dataclass
class BHQ2Result:
    answer: bool | None
    cap_exceeded: bool
    residual_states: int
    singularity_entries: int
    absorption_hits: int
    bytewise_distinct_absorptions: int
    polarity_flip_absorptions: int
    physarum_signature_checks: int
    event_horizon_collisions: int
    signed_canonicalizations: int
    signed_discrete_canonicalizations: int
    signed_refinement_rounds: int
    signed_refinement_edge_visits: int
    q0_fallback_refinement_edge_visits: int
    buzz_return_checks: int
    buzz_return_passes: int
    hawking_escape_count: int
    resolution_attempts: int
    resolution_additions: int
    affine_equations: int


class Policy0ABHQ2:
    def __init__(self, state_cap: int | None = None):
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> BHQ2Result:
        self.states = 0
        self.buckets: dict[str, list[Entry]] = defaultdict(list)
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

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.result(affine_answer, False)

        try:
            return self.result(self.search(cnf), False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> BHQ2Result:
        return BHQ2Result(
            answer=answer,
            cap_exceeded=cap_exceeded,
            residual_states=self.states,
            singularity_entries=sum(len(entries) for entries in self.buckets.values()),
            absorption_hits=self.absorption_hits,
            bytewise_distinct_absorptions=self.bytewise_distinct_absorptions,
            polarity_flip_absorptions=self.polarity_flip_absorptions,
            physarum_signature_checks=self.physarum_signature_checks,
            event_horizon_collisions=self.event_horizon_collisions,
            signed_canonicalizations=self.signed_canonicalizations,
            signed_discrete_canonicalizations=self.signed_discrete_canonicalizations,
            signed_refinement_rounds=self.signed_refinement_rounds,
            signed_refinement_edge_visits=self.signed_refinement_edge_visits,
            q0_fallback_refinement_edge_visits=self.q0_fallback_refinement_edge_visits,
            buzz_return_checks=self.buzz_return_checks,
            buzz_return_passes=self.buzz_return_passes,
            hawking_escape_count=self.hawking_escape_count,
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
            affine_equations=self.affine_equation_count,
        )

    def canonicalize(self, cnf: CNF) -> SingularityCanonicalization:
        q = signed_incidence_canonicalize(cnf)
        self.signed_canonicalizations += 1
        self.signed_refinement_rounds += q.signed_refinement_rounds
        self.signed_refinement_edge_visits += q.signed_refinement_edge_visits
        self.q0_fallback_refinement_edge_visits += q.q0_fallback_edge_visits
        if q.signed_discrete:
            self.signed_discrete_canonicalizations += 1
        return q

    def buzz_verify(
        self,
        current: CNF,
        current_q: SingularityCanonicalization,
        stored: Entry,
    ) -> tuple[bool, SignedMap | None]:
        self.buzz_return_checks += 1
        if stored.canonicalization is None:
            self.hawking_escape_count += 1
            return False, None
        if current_q.key != stored.canonicalization.key:
            self.hawking_escape_count += 1
            return False, None

        if current_q.key.mode == "RAW":
            ok = current == stored.representative
            if ok:
                self.buzz_return_passes += 1
                return True, {v: (v, False) for v in {abs(l) for c in current for l in c}}
            self.hawking_escape_count += 1
            return False, None

        try:
            mapping = compose_current_to_representative(
                current_q.old_to_canonical,
                stored.canonicalization.old_to_canonical,
            )
            inverse = invert_signed_map(mapping)
        except AssertionError:
            self.hawking_escape_count += 1
            return False, None

        if not signed_map_roundtrip_ok(mapping):
            self.hawking_escape_count += 1
            return False, None
        if apply_signed_map(current, mapping) != stored.representative:
            self.hawking_escape_count += 1
            return False, None
        if apply_signed_map(stored.representative, inverse) != current:
            self.hawking_escape_count += 1
            return False, None

        self.buzz_return_passes += 1
        return True, mapping

    def quotient_lookup(self, cnf: CNF) -> tuple[Handle, bool | None]:
        self.physarum_signature_checks += 1
        signature = signed_typed_signature(cnf)
        bucket = self.buckets.get(signature)
        if not bucket:
            return Handle(signature, None), None

        self.event_horizon_collisions += 1

        # Exact same residual: safe without entering the event horizon.
        for entry in bucket:
            if entry.representative == cnf:
                self.absorption_hits += 1
                return Handle(signature, entry.canonicalization), entry.answer

        current_q = self.canonicalize(cnf)
        for entry in bucket:
            if entry.canonicalization is None:
                entry.canonicalization = self.canonicalize(entry.representative)
            ok, mapping = self.buzz_verify(cnf, current_q, entry)
            if not ok:
                continue
            self.absorption_hits += 1
            self.bytewise_distinct_absorptions += 1
            if mapping and any(flip for _, flip in mapping.values()):
                self.polarity_flip_absorptions += 1
            return Handle(signature, current_q), entry.answer

        return Handle(signature, current_q), None

    def memo_store(self, handle: Handle, cnf: CNF, answer: bool) -> None:
        bucket = self.buckets[handle.signature]
        for entry in bucket:
            if entry.representative == cnf:
                if entry.answer != answer:
                    raise AssertionError("BH-Q2 exact cache collision changed Boolean answer")
                return

        if handle.canonicalization is not None:
            for entry in bucket:
                if entry.canonicalization is None:
                    entry.canonicalization = self.canonicalize(entry.representative)
                ok, _ = self.buzz_verify(cnf, handle.canonicalization, entry)
                if ok:
                    if entry.answer != answer:
                        raise AssertionError("BH-Q2 singularity collision changed Boolean answer")
                    return

        bucket.append(Entry(answer, cnf, handle.canonicalization))

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


def run_order(order: int, state_cap: int | None) -> BHQ2Result:
    cnf, variable_count = graph_tautology_cnf(order)
    result = Policy0ABHQ2(state_cap=state_cap).solve(cnf, variable_count)
    encoding_units = variable_count + len(cnf) + sum(len(c) for c in cnf)
    print(f"ORDER_SIZE = {order}")
    print(f"  encoding_units = {encoding_units}")
    for name in (
        "answer",
        "cap_exceeded",
        "residual_states",
        "singularity_entries",
        "absorption_hits",
        "bytewise_distinct_absorptions",
        "polarity_flip_absorptions",
        "physarum_signature_checks",
        "event_horizon_collisions",
        "signed_canonicalizations",
        "signed_discrete_canonicalizations",
        "signed_refinement_rounds",
        "signed_refinement_edge_visits",
        "q0_fallback_refinement_edge_visits",
        "buzz_return_checks",
        "buzz_return_passes",
        "hawking_escape_count",
        "resolution_attempts",
        "resolution_additions",
    ):
        print(f"  {name} = {getattr(result, name)}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", default="3,4,5,6,7,8,9")
    parser.add_argument("--state-cap", type=int, default=None)
    args = parser.parse_args()

    for raw in args.orders.split(","):
        if raw:
            run_order(int(raw), args.state_cap)

    print("JANUS_BH_Q2_BUZZ_PHYSARUM_SIGNED_SINGULARITY = COMPLETE")
    print("canonical_law = NO RETURN PATH => NO ABSORPTION")
    print("claim_boundary = frozen calibration only; P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
