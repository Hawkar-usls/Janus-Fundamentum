#!/usr/bin/env python3
"""UFR-001: bounded, sound literal-preserving variable-renaming for SAT/Exact-One.

This is NOT Feigenbaum scaling, a polynomial-time graph-isomorphism algorithm,
or a change to C023's exact-residual certificate calculus. A matching key is
only a candidate: verify_renaming independently rechecks the actual formula.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from math import factorial
from typing import Iterable, Mapping

Rows = tuple[tuple[int, ...], ...]
Kind = str


def normalize(rows: Iterable[Iterable[int]]) -> Rows:
    out: list[tuple[int, ...]] = []
    for row in rows:
        literals = tuple(row)
        if any(type(lit) is not int or lit == 0 for lit in literals):
            raise ValueError("literals must be nonzero integers")
        # Preserve multiplicity: repeated literals affect EXACT_ONE semantics.
        out.append(tuple(sorted(literals, key=lambda x: (abs(x), x < 0))))
    return tuple(sorted(out))


def check_kind(kind: Kind) -> None:
    if kind not in ("SAT", "EXACT_ONE"):
        raise ValueError(f"unsupported constraint kind: {kind}")


def variables(rows: Rows) -> tuple[int, ...]:
    return tuple(sorted({abs(lit) for row in rows for lit in row}))


def rename(rows: Rows, mapping: Mapping[int, int]) -> Rows:
    return normalize(
        ((1 if lit > 0 else -1) * mapping[abs(lit)] for lit in row)
        for row in rows
    )


@dataclass(frozen=True)
class Canonical:
    kind: Kind
    key: Rows
    forward: tuple[tuple[int, int], ...]  # original -> canonical
    exhaustive: bool
    candidates: int

    def mapping(self) -> dict[int, int]:
        return dict(self.forward)


def canonicalize(
    rows: Iterable[Iterable[int]], kind: Kind = "SAT", *,
    max_variables: int = 12, max_candidates: int = 720,
) -> Canonical:
    """Sound candidate key; only complete for allowed signature-permutation budget.

    A fallback key is still sound, but may miss equivalent instances. Runtime
    can be factorial; max_variables/max_candidates limit this expenditure.
    """
    check_kind(kind)
    source = normalize(rows)
    vs = variables(source)
    # One incidence pass instead of scanning every literal for every variable.
    # Keep signatures and ordering *identical* to the UFR-001 reference.
    incidence: dict[int, dict[tuple[int, int], int]] = {v: {} for v in vs}
    for row in source:
        width = len(row)
        for lit in row:
            counts = incidence[abs(lit)]
            tag = (width, 1 if lit > 0 else -1)
            counts[tag] = counts.get(tag, 0) + 1
    features = {
        v: tuple((width, sign, count) for (width, sign), count
                 in sorted(incidence[v].items()))
        for v in vs
    }
    groups = [tuple(v for v in vs if features[v] == feature)
              for feature in sorted(set(features.values()))]
    candidate_count = 1
    for group in groups:
        candidate_count *= factorial(len(group))
    exhaustive = len(vs) <= max_variables and candidate_count <= max_candidates
    orders = (product(*(permutations(g) for g in groups)) if exhaustive
              else [tuple(groups)])
    best_key: Rows | None = None
    best_forward: tuple[tuple[int, int], ...] = ()
    checked = 0
    for chunks in orders:
        ordered = tuple(v for chunk in chunks for v in chunk)
        mapping = {v: i + 1 for i, v in enumerate(ordered)}
        key = rename(source, mapping)
        checked += 1
        if best_key is None or key < best_key:
            best_key = key
            best_forward = tuple(sorted(mapping.items()))
    assert best_key is not None
    assert rename(source, dict(best_forward)) == best_key
    return Canonical(kind, best_key, best_forward, exhaustive, checked)


def verify_renaming(
    left: Iterable[Iterable[int]], right: Iterable[Iterable[int]],
    mapping: Mapping[int, int], kind: Kind = "SAT",
) -> bool:
    """Independent exact check, including surjectivity and literal signs."""
    check_kind(kind)
    a, b = normalize(left), normalize(right)
    va, vb = set(variables(a)), set(variables(b))
    if (set(mapping) != va or set(mapping.values()) != vb
            or len(mapping.values()) != len(set(mapping.values()))):
        return False
    return rename(a, mapping) == b


def find_verified_match(
    left: Iterable[Iterable[int]], right: Iterable[Iterable[int]],
    kind: Kind = "SAT", *, max_variables: int = 12,
    max_candidates: int = 720,
) -> dict[int, int] | None:
    a = canonicalize(left, kind, max_variables=max_variables,
                     max_candidates=max_candidates)
    b = canonicalize(right, kind, max_variables=max_variables,
                     max_candidates=max_candidates)
    if a.key != b.key:
        return None
    inverse = {c: old for old, c in b.forward}
    mapping = {old: inverse[c] for old, c in a.forward}
    return mapping if verify_renaming(left, right, mapping, kind) else None


def verify_model(rows: Iterable[Iterable[int]], assignment: Mapping[int, bool],
                 kind: Kind = "SAT") -> bool:
    check_kind(kind)
    source = normalize(rows)
    if any(v not in assignment for v in variables(source)):
        return False
    for row in source:
        true_count = sum(assignment[abs(lit)] == (lit > 0) for lit in row)
        if (kind == "SAT" and true_count == 0) or (kind == "EXACT_ONE" and true_count != 1):
            return False
    return True


def transport_model(assignment: Mapping[int, bool],
                    mapping: Mapping[int, int]) -> dict[int, bool]:
    """For a verified left->right map, transport left-model to right-model."""
    if not set(mapping).issubset(assignment):
        raise ValueError("incomplete source assignment")
    return {new: bool(assignment[old]) for old, new in mapping.items()}
