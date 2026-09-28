#!/usr/bin/env python3
"""Exact finite counterexample to the PolaritySAT forced-assignment lemma.

Scientific role: donor falsifier only.  This does not address P vs NP directly.
"""
from itertools import product

NAMES = ("u", "v", "w", "a", "z")
IDX = {name: i for i, name in enumerate(NAMES)}

# Literal = (variable-name, polarity-True-for-positive)
CLAUSES = (
    (("u", True), ("v", True)),
    (("v", False), ("w", True)),
    (("w", False), ("a", True)),
    (("w", False), ("a", False)),
    (("u", False), ("z", True)),
    (("z", False), ("u", True)),
)

# Declared descending order u > v > w > a > z.
ORDER = {name: len(NAMES) - i for i, name in enumerate(NAMES)}


def sat_clause(clause, assignment):
    return any(bool(assignment[IDX[v]]) == pol for v, pol in clause)


def sat_formula(assignment):
    return all(sat_clause(c, assignment) for c in CLAUSES)


def models():
    return [bits for bits in product((0, 1), repeat=len(NAMES)) if sat_formula(bits)]


def globally_unified_polarities(v):
    """Implement the donor definition literally.

    A polarity p qualifies iff for every higher u with at least one current
    clause containing both u and v, every occurrence of v in those clauses has p.
    """
    candidates = []
    for p in (False, True):
        ok = True
        for u in NAMES:
            if ORDER[u] <= ORDER[v]:
                continue
            joint = [c for c in CLAUSES if any(x == u for x, _ in c) and any(x == v for x, _ in c)]
            if not joint:
                continue
            for c in joint:
                vpols = [pol for x, pol in c if x == v]
                if any(pol != p for pol in vpols):
                    ok = False
        if ok:
            candidates.append(p)
    return candidates


def main():
    ms = models()
    assert ms == [(1, 0, 0, 0, 1), (1, 0, 0, 1, 1)], ms

    # No unit clauses and no pure variable.
    assert all(len(c) >= 2 for c in CLAUSES)
    for v in NAMES:
        pols = {pol for c in CLAUSES for x, pol in c if x == v}
        assert pols == {False, True}, (v, pols)

    # v is uniquely globally-unified positive under the published definition.
    assert globally_unified_polarities("v") == [True]

    # Yet no satisfying model has v=True.
    assert not any(m[IDX["v"]] == 1 for m in ms)

    print("PASS: formula is SAT but globally-unified-positive v cannot be set True")
    print("models:", ms)


if __name__ == "__main__":
    main()
