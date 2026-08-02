#!/usr/bin/env python3
"""Show that the cache-diamond speedup is not a Resolution separation.

The diamond family contains the complete contradiction on four shifted core
variables.  Resolution can ignore every selector and private clause, eliminate
the four core variables, and derive the empty clause in 31 lines for every
selector count.  Exact caching still gives an exponential speedup over the
specific no-cache execution, but not over ordinary Resolution on this family.
"""

from __future__ import annotations

from dataclasses import dataclass

from janus_tear_policy0a_context_obstruction import cache_diamond_cnf
from janus_tear_policy0a_masked_tseitin import canonical_cnf
from janus_tear_policy0t_no_cache import Policy0T

Clause = tuple[int, ...]


@dataclass(frozen=True)
class Line:
    clause: Clause
    left: int | None = None
    right: int | None = None
    pivot: int | None = None


def canonical_clause(raw) -> Clause:
    literals = set(raw)
    assert not any(-literal in literals for literal in literals)
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def resolve(left: Clause, right: Clause, pivot: int) -> Clause:
    if pivot in left and -pivot in right:
        raw = (set(left) - {pivot}) | (set(right) - {-pivot})
    elif -pivot in left and pivot in right:
        raw = (set(left) - {-pivot}) | (set(right) - {pivot})
    else:
        raise AssertionError("non-complementary pivot")
    return canonical_clause(raw)


def core_refutation(selector_count: int, full_cnf) -> tuple[list[Line], int]:
    core_variables = tuple(selector_count + index for index in range(1, 5))
    core_set = {
        clause
        for clause in full_cnf
        if set(map(abs, clause)) == set(core_variables) and len(clause) == 4
    }
    assert len(core_set) == 16

    lines = [Line(clause) for clause in sorted(core_set)]
    current = {line.clause: index for index, line in enumerate(lines)}

    for pivot in reversed(core_variables):
        next_level: dict[Clause, int] = {}
        for clause, left_index in sorted(current.items()):
            if pivot not in clause:
                continue
            partner = canonical_clause((set(clause) - {pivot}) | {-pivot})
            assert partner in current
            right_index = current[partner]
            resolvent = resolve(clause, partner, pivot)
            if resolvent in next_level:
                continue
            line_index = len(lines)
            lines.append(Line(resolvent, left_index, right_index, pivot))
            next_level[resolvent] = line_index
        assert len(next_level) * 2 == len(current)
        current = next_level

    assert set(current) == {()}
    return lines, current[()]


def verify(full_cnf, lines: list[Line], final_index: int) -> tuple[int, int]:
    axioms = set(canonical_cnf(full_cnf))
    clauses: list[Clause] = []
    depths: list[int] = []

    for index, line in enumerate(lines):
        if line.left is None:
            assert line.right is None and line.pivot is None
            assert line.clause in axioms
            depth = 0
        else:
            assert line.right is not None and line.pivot is not None
            assert 0 <= line.left < index
            assert 0 <= line.right < index
            assert resolve(
                clauses[line.left], clauses[line.right], line.pivot
            ) == line.clause
            depth = 1 + max(depths[line.left], depths[line.right])
        clauses.append(line.clause)
        depths.append(depth)

    assert clauses[final_index] == ()
    return max(map(len, clauses)), depths[final_index]


def self_test() -> None:
    rows = []
    for selector_count in range(0, 8):
        cnf, variable_count = cache_diamond_cnf(selector_count)
        lines, final_index = core_refutation(selector_count, cnf)
        maximum_width, proof_depth = verify(cnf, lines, final_index)
        tree = Policy0T().solve(cnf, variable_count)
        assert tree.answer is False and not tree.cap_exceeded
        assert len(lines) == 31
        assert maximum_width == 4
        assert proof_depth == 4
        rows.append((selector_count, tree.recursive_calls, len(lines)))

    assert rows[-1][1] >= 2 ** (rows[-1][0] + 1) - 1
    assert all(proof_lines == 31 for _, _, proof_lines in rows)

    print("JANUS_POLICY0A_DIAMOND_RESOLUTION_BYPASS = PASS")
    print(f"rows = {tuple(rows)}")
    print("resolution_axioms = 16")
    print("resolution_steps = 15")
    print("proof_lines = 31")
    print("proof_depth = 4")
    print("maximum_width = 4")
    print("selectors_used_by_proof = 0")
    print("private_clauses_used_by_proof = 0")
    print("verdict = diamond separates cached and no-cache executions, not Formula Caching and Resolution")


if __name__ == "__main__":
    self_test()
