#!/usr/bin/env python3
"""Finite mechanics for Policy-0B.1 execution -> Resolution compilation.

Checks one symbolic branch: each child conflict lifts to a blocking unit clause,
then the two blocking units resolve to empty.  The asymptotic PHP lower-bound
transfer is analytical/literature-backed, not established by this finite probe.
"""
from __future__ import annotations

Clause = tuple[int, ...]


def resolve(left: Clause, right: Clause, pivot: int) -> Clause:
    assert pivot in left and -pivot in right
    s = (set(left) - {pivot}) | (set(right) - {-pivot})
    assert not any(-l in s for l in s)
    return tuple(sorted(s, key=lambda l: (abs(l), l < 0)))


def main() -> None:
    # Branch variable x=1.
    # Under x=0, (x OR y) and (x OR ~y) restrict to y and ~y, so conflict
    # lifts directly to the blocking clause (x).
    left0 = (1, 2)
    left1 = (1, -2)
    block_false = resolve(left0, left1, 2)
    assert block_false == (1,)

    # Under x=1, (~x OR z) and (~x OR ~z) restrict to z and ~z, so conflict
    # lifts to the blocking clause (~x).
    right0 = (-1, 3)
    right1 = (-1, -3)
    block_true = resolve(right0, right1, 3)
    assert block_true == (-1,)

    # Branch composition.
    root_conflict = resolve(block_false, block_true, 1)
    assert root_conflict == ()

    print("C025_POLICY0B1_RES_COMPILER_FALSE_CHILD_BLOCK = PASS")
    print("C025_POLICY0B1_RES_COMPILER_TRUE_CHILD_BLOCK = PASS")
    print("C025_POLICY0B1_RES_COMPILER_BRANCH_COMPOSITION = PASS")
    print("C025_POLICY0B1_EXECUTION_TO_RESOLUTION = ANALYTICAL_GENERAL_THEOREM")
    print("C025_POLICY0B1_PHP_RUNTIME_LOWER_BOUND = LITERATURE_TRANSFER_NOT_CI")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
