#!/usr/bin/env python3
"""R5 E118 — universal linear-cubic ExactOne hardness bridge replay.

This checker is deliberately finite and exact.  It validates the EQUAL3 gadget
truth relation and the structural invariants used by the occurrence-splitting
reduction.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product


PORTS = ("x", "y", "z")
INTERNAL = ("a", "b", "c", "d", "e", "f", "g")
GADGET_CLAUSES = (
    ("d", "f", "g"),
    ("z", "c", "e"),
    ("y", "e", "f"),
    ("x", "b", "f"),
    ("z", "a", "b"),
    ("a", "e", "g"),
    ("x", "a", "d"),
    ("y", "c", "d"),
    ("b", "c", "g"),
)


def exact_one(clause: tuple[str, ...], assignment: dict[str, int]) -> bool:
    return sum(assignment[v] for v in clause) == 1


def verify_gadget() -> None:
    variables = PORTS + INTERNAL
    satisfying: list[dict[str, int]] = []

    for bits in product((0, 1), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if all(exact_one(c, assignment) for c in GADGET_CLAUSES):
            satisfying.append(assignment)

    assert len(satisfying) == 3, len(satisfying)

    projections = Counter(tuple(s[p] for p in PORTS) for s in satisfying)
    assert projections == Counter({(0, 0, 0): 2, (1, 1, 1): 1}), projections

    # Check the closed-form linear solution on every Boolean model.
    for s in satisfying:
        t = s["f"]
        z = s["z"]
        assert s["x"] == s["y"] == s["z"] == s["g"]
        assert s["a"] == s["c"] == s["f"] == t
        assert s["b"] == s["d"] == s["e"] == 1 - t - z

    degree = Counter(v for c in GADGET_CLAUSES for v in c)
    for p in PORTS:
        assert degree[p] == 2, (p, degree[p])
    for v in INTERNAL:
        assert degree[v] == 3, (v, degree[v])

    for c1, c2 in combinations(GADGET_CLAUSES, 2):
        assert len(set(c1) & set(c2)) <= 1, (c1, c2)


def rename_gadget(prefix: str, ports: tuple[str, str, str]) -> list[tuple[str, ...]]:
    mapping = {
        "x": ports[0],
        "y": ports[1],
        "z": ports[2],
        **{v: f"{prefix}_{v}" for v in INTERNAL},
    }
    return [tuple(mapping[v] for v in c) for c in GADGET_CLAUSES]


def split_occurrences(
    source_clauses: tuple[tuple[str, str, str], ...]
) -> tuple[list[tuple[str, ...]], dict[str, tuple[str, str, str]]]:
    occurrences: dict[str, list[str]] = {}
    transformed_source: list[tuple[str, ...]] = []

    for ci, clause in enumerate(source_clauses):
        new_clause = []
        for v in clause:
            idx = len(occurrences.setdefault(v, []))
            port = f"{v}_occ{idx}"
            occurrences[v].append(port)
            new_clause.append(port)
        transformed_source.append(tuple(new_clause))

    for v, occs in occurrences.items():
        assert len(occs) == 3, (v, occs)

    port_map = {v: tuple(occs) for v, occs in occurrences.items()}
    return transformed_source, port_map


def verify_reduction_skeleton() -> None:
    # K4 triples: 4 variables, 4 clauses, every variable has degree 3.
    # This source is intentionally non-linear: distinct clauses share 2 variables.
    source = (
        ("u1", "u2", "u3"),
        ("u1", "u2", "u4"),
        ("u1", "u3", "u4"),
        ("u2", "u3", "u4"),
    )
    n = 4

    source_degree = Counter(v for c in source for v in c)
    assert all(source_degree[v] == 3 for v in source_degree)
    assert all(len(c) == 3 and len(set(c)) == 3 for c in source)

    split_source, ports = split_occurrences(source)
    target = list(split_source)
    for v, ps in ports.items():
        target.extend(rename_gadget(f"G_{v}", ps))

    variables = sorted({v for c in target for v in c})

    assert len(target) == 10 * n, len(target)
    assert len(variables) == 10 * n, len(variables)
    assert all(len(c) == 3 and len(set(c)) == 3 for c in target)

    target_degree = Counter(v for c in target for v in c)
    assert set(target_degree.values()) == {3}, target_degree

    for c1, c2 in combinations(target, 2):
        assert len(set(c1) & set(c2)) <= 1, (c1, c2)

    # Forward logical replay on every source assignment.
    source_variables = sorted(source_degree)
    for bits in product((0, 1), repeat=len(source_variables)):
        assignment = dict(zip(source_variables, bits))
        source_sat = all(sum(assignment[v] for v in c) == 1 for c in source)

        port_assignment: dict[str, int] = {}
        for v, ps in ports.items():
            for p in ps:
                port_assignment[p] = assignment[v]

        split_sat = all(
            sum(port_assignment[p] for p in c) == 1 for c in split_source
        )
        assert split_sat == source_sat

        # Every equal port triple has at least one gadget extension.
        for v, ps in ports.items():
            value = assignment[v]
            ext_count = 0
            for internal_bits in product((0, 1), repeat=len(INTERNAL)):
                local = dict(zip(INTERNAL, internal_bits))
                local.update({"x": value, "y": value, "z": value})
                if all(exact_one(c, local) for c in GADGET_CLAUSES):
                    ext_count += 1
            assert ext_count == (1 if value else 2), (v, value, ext_count)


def main() -> None:
    verify_gadget()
    verify_reduction_skeleton()

    print("R5 E118 PASS")
    print("EQUAL3 satisfying assignments: 3")
    print("port projections: 000 x2, 111 x1")
    print("internal degrees: 3; port internal degrees: 2")
    print("gadget and transformed reduction skeleton: 3-uniform, 3-regular, linear")
    print("4-variable cubic source -> 40 variables, 40 clauses")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
