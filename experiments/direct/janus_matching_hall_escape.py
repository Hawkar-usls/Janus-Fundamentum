#!/usr/bin/env python3
"""Exact matching/Hall escape for a syntactically recognized injective-assignment CNF.

Accepted raw CNF shape:
  * every clause is either all-positive (one left-demand clause) or binary all-negative;
  * every variable occurs in exactly one positive demand clause;
  * negative clauses whose endpoints belong to the same demand are admitted as
    intra-demand AMO constraints (the theorem-matched PHP encoding may contain them);
  * after removing those intra-demand edges, the cross-demand conflict graph is
    a disjoint union of cliques;
  * each cross-demand conflict clique contains at most one variable from each demand.

Each cross-demand conflict clique (including singleton variables) is one right-side
resource/hole. The CNF is SAT iff the resulting bipartite graph has a matching
covering every left demand. Intra-demand negative clauses cannot invalidate the
matching witness because that witness selects exactly one variable per demand.
Ambiguous or nonconforming inputs return OPEN.

This lane is exact and family-specific. It does not claim arbitrary-CNF coverage
or P=NP.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, Optional

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


def recognize_injective_assignment(raw_clauses: Iterable[Iterable[int]]) -> Optional[dict]:
    cnf = base.canon_cnf(raw_clauses)
    if not cnf or () in cnf:
        return None

    positive = []
    negative = []
    for clause in cnf:
        if clause and all(lit > 0 for lit in clause):
            positive.append(clause)
        elif len(clause) == 2 and all(lit < 0 for lit in clause):
            negative.append(clause)
        else:
            return None

    if not positive:
        return None

    # Positive clauses must form a partition of all variables into left demands.
    var_to_left: Dict[int, int] = {}
    for left, clause in enumerate(positive):
        for var in clause:
            if var in var_to_left:
                return None
            var_to_left[var] = left

    all_vars = set(base.vars_of(cnf))
    if all_vars != set(var_to_left):
        return None

    # Separate harmless intra-demand AMO edges from the cross-demand exclusion
    # relation that defines right-side resources.
    cross_conflict: Dict[int, set[int]] = {v: set() for v in sorted(all_vars)}
    intra_demand_edges: list[tuple[int, int]] = []
    cross_edges: set[tuple[int, int]] = set()
    seen_edges: set[tuple[int, int]] = set()

    for clause in negative:
        u, v = sorted((abs(clause[0]), abs(clause[1])))
        if u == v or u not in var_to_left or v not in var_to_left:
            return None
        edge = (u, v)
        if edge in seen_edges:
            return None
        seen_edges.add(edge)

        if var_to_left[u] == var_to_left[v]:
            intra_demand_edges.append(edge)
            continue

        cross_edges.add(edge)
        cross_conflict[u].add(v)
        cross_conflict[v].add(u)

    # The cross-demand conflict relation must be exactly an equivalence-by-resource:
    # connected components are cliques, and each component contains at most one
    # variable from any left demand. Isolated variables are singleton resources.
    components: list[tuple[int, ...]] = []
    unseen = set(all_vars)
    while unseen:
        root = min(unseen)
        stack = [root]
        comp = set()
        unseen.remove(root)
        while stack:
            u = stack.pop()
            comp.add(u)
            for v in sorted(cross_conflict[u]):
                if v in unseen:
                    unseen.remove(v)
                    stack.append(v)

        ordered = tuple(sorted(comp))
        lefts = [var_to_left[v] for v in ordered]
        if len(lefts) != len(set(lefts)):
            return None

        for i, u in enumerate(ordered):
            for v in ordered[i + 1 :]:
                if v not in cross_conflict[u]:
                    return None
        components.append(ordered)

    components.sort(key=lambda comp: comp)
    var_to_right = {
        var: right
        for right, comp in enumerate(components)
        for var in comp
    }

    edges: Dict[int, list[tuple[int, int]]] = {left: [] for left in range(len(positive))}
    for var, left in sorted(var_to_left.items()):
        edges[left].append((var_to_right[var], var))
    for left in edges:
        edges[left].sort()
        if not edges[left]:
            return None

    return {
        "cnf": cnf,
        "fingerprint": base.fingerprint(cnf),
        "left_count": len(positive),
        "right_count": len(components),
        "positive_clauses": positive,
        "right_components": components,
        "intra_demand_negative_edges": tuple(sorted(intra_demand_edges)),
        "cross_demand_negative_edges": tuple(sorted(cross_edges)),
        "var_to_left": var_to_left,
        "var_to_right": var_to_right,
        "edges": edges,
    }


def _maximum_matching(model: dict) -> tuple[dict[int, int], dict[int, int]]:
    edges = model["edges"]
    match_right: Dict[int, int] = {}
    match_left: Dict[int, int] = {}

    def augment(left: int, seen_right: set[int]) -> bool:
        for right, _var in edges[left]:
            if right in seen_right:
                continue
            seen_right.add(right)
            old_left = match_right.get(right)
            if old_left is None or augment(old_left, seen_right):
                match_right[right] = left
                match_left[left] = right
                return True
        return False

    for left in range(model["left_count"]):
        augment(left, set())
    return match_left, match_right


def _hall_deficiency(model: dict, match_left: dict[int, int], match_right: dict[int, int]) -> tuple[list[int], list[int]]:
    edges = model["edges"]
    z_left = {left for left in range(model["left_count"]) if left not in match_left}
    z_right: set[int] = set()
    queue = deque(sorted(z_left))

    while queue:
        left = queue.popleft()
        matched_right = match_left.get(left)
        for right, _var in edges[left]:
            # Alternating reachability: L -> R through unmatched edges.
            if right == matched_right:
                continue
            if right in z_right:
                continue
            z_right.add(right)
            # R -> L through the matched edge, if any.
            other_left = match_right.get(right)
            if other_left is not None and other_left not in z_left:
                z_left.add(other_left)
                queue.append(other_left)

    neighbors = {
        right
        for left in z_left
        for right, _var in edges[left]
    }
    if len(neighbors) >= len(z_left):
        raise AssertionError("MAX_MATCHING_FAILED_TO_PRODUCE_HALL_DEFICIENCY")
    return sorted(z_left), sorted(neighbors)


def solve_matching_hall_escape(raw_clauses: Iterable[Iterable[int]]) -> dict:
    model = recognize_injective_assignment(raw_clauses)
    if model is None:
        return {
            "kind": "JANUS_MATCHING_HALL_ESCAPE",
            "status": "OPEN",
            "recognized_family": False,
            "P_VS_NP": P_VS_NP,
        }

    match_left, match_right = _maximum_matching(model)
    if len(match_left) == model["left_count"]:
        assignment = {var: 0 for var in model["var_to_left"]}
        selected = []
        for left, right in sorted(match_left.items()):
            candidates = [var for candidate_right, var in model["edges"][left] if candidate_right == right]
            if len(candidates) != 1:
                raise AssertionError("NON_UNIQUE_EDGE_VARIABLE_FOR_MATCHED_PAIR")
            var = candidates[0]
            assignment[var] = 1
            selected.append({"left": left, "right": right, "variable": var})
        if not base.verify_total_assignment(model["cnf"], assignment):
            raise AssertionError("MATCHING_WITNESS_FAILED_CNF_REPLAY")
        return {
            "kind": "JANUS_MATCHING_HALL_ESCAPE",
            "status": "SAT",
            "recognized_family": True,
            "fingerprint": model["fingerprint"],
            "left_count": model["left_count"],
            "right_count": model["right_count"],
            "matching_size": len(match_left),
            "selected_edges": selected,
            "assignment": assignment,
            "certificate": "COVERING_BIPARTITE_MATCHING",
            "P_VS_NP": P_VS_NP,
        }

    hall_left, hall_neighbors = _hall_deficiency(model, match_left, match_right)
    return {
        "kind": "JANUS_MATCHING_HALL_ESCAPE",
        "status": "UNSAT",
        "recognized_family": True,
        "fingerprint": model["fingerprint"],
        "left_count": model["left_count"],
        "right_count": model["right_count"],
        "matching_size": len(match_left),
        "hall_left": hall_left,
        "hall_neighbors": hall_neighbors,
        "hall_deficiency": len(hall_left) - len(hall_neighbors),
        "certificate": "HALL_DEFICIENT_LEFT_SET",
        "P_VS_NP": P_VS_NP,
    }


def verify_matching_hall_escape(raw_clauses: Iterable[Iterable[int]], result: dict) -> bool:
    model = recognize_injective_assignment(raw_clauses)
    if model is None or result.get("recognized_family") is not True:
        return False
    if result.get("fingerprint") != model["fingerprint"]:
        return False

    if result.get("status") == "SAT":
        raw_assignment = result.get("assignment", {})
        assignment = {int(var): int(bit) for var, bit in raw_assignment.items()}
        return (
            set(assignment) == set(model["var_to_left"])
            and all(bit in (0, 1) for bit in assignment.values())
            and base.verify_total_assignment(model["cnf"], assignment)
        )

    if result.get("status") == "UNSAT":
        hall_left = sorted({int(x) for x in result.get("hall_left", [])})
        if not hall_left or any(left < 0 or left >= model["left_count"] for left in hall_left):
            return False
        neighbors = sorted({
            right
            for left in hall_left
            for right, _var in model["edges"][left]
        })
        advertised = sorted({int(x) for x in result.get("hall_neighbors", [])})
        return advertised == neighbors and len(neighbors) < len(hall_left)

    return False


def _php(m: int, n: int, *, row_amo: bool = False):
    def var(p: int, h: int) -> int:
        return 1 + p * n + h

    clauses = []
    # Every pigeon/left demand chooses at least one hole/right resource.
    for p in range(m):
        clauses.append(tuple(var(p, h) for h in range(n)))

    # Optional theorem-matched exactly-one row constraints.
    if row_amo:
        for p in range(m):
            for h in range(n):
                for k in range(h + 1, n):
                    clauses.append((-var(p, h), -var(p, k)))

    # Every hole/right resource has capacity one across distinct pigeons.
    for h in range(n):
        for p in range(m):
            for q in range(p + 1, m):
                clauses.append((-var(p, h), -var(q, h)))
    return clauses


def self_test() -> None:
    # Minimal pairwise PHP form: row ALO + column AMO.
    unsat = _php(5, 4)
    result = solve_matching_hall_escape(unsat)
    assert result["status"] == "UNSAT"
    assert result["hall_deficiency"] >= 1
    assert verify_matching_hall_escape(unsat, result)

    sat = _php(4, 4)
    result = solve_matching_hall_escape(sat)
    assert result["status"] == "SAT"
    assert verify_matching_hall_escape(sat, result)

    # Historical theorem-matched holdout shape from the frozen PHP_8_7 artifact:
    # 8 row ALO + 8*C(7,2) row AMO + 7*C(8,2) column AMO = 372 clauses.
    php87_exact_one = _php(8, 7, row_amo=True)
    assert len(php87_exact_one) == 372
    model = recognize_injective_assignment(php87_exact_one)
    assert model is not None
    assert model["left_count"] == 8
    assert model["right_count"] == 7
    result = solve_matching_hall_escape(php87_exact_one)
    assert result["status"] == "UNSAT"
    assert result["matching_size"] == 7
    assert result["hall_deficiency"] >= 1
    assert verify_matching_hall_escape(php87_exact_one, result)

    unrelated = ((1, 2, 3), (-1, -2, -3))
    assert solve_matching_hall_escape(unrelated)["status"] == "OPEN"


if __name__ == "__main__":
    self_test()
    print("MATCHING_HALL_ESCAPE_SELF_TEST=PASS")
    print("THEOREM_MATCHED_PHP8_7_REGRESSION=PASS")
    print("P_VS_NP=OPEN")
