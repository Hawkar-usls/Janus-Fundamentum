#!/usr/bin/env python3
"""Search for abstract wider origins of a fresh bridge under Resolution.

This is a red-team test for the arbitrary-n binary-origin reduction.  It drops
GT reachability and enumerates signed clauses on small quotient vertex sets.
We seek parents A,B and literals l,p such that:

- l occurs with the same orientation in both parents;
- p occurs in A and -p in B;
- A is component-spanning;
- B contains a directed cycle;
- l is non-bridge in both parent underlying graphs;
- the non-tautological resolvent is component-spanning and l becomes a bridge;
- at least three quotient vertices remain.

Any witness proves that binary-origin localization is not a general graph-
Resolution theorem and must exploit GT residual reachability.
"""

from __future__ import annotations

from itertools import product

Literal = tuple[int, int]
Clause = tuple[Literal, ...]


def pairs(m: int):
    return tuple((u, v) for u in range(m) for v in range(u + 1, m))


def oriented(pair, sign: int) -> Literal:
    u, v = pair
    return (u, v) if sign > 0 else (v, u)


def variable(literal: Literal):
    return tuple(sorted(literal))


def sign_of(literal: Literal):
    u, v = literal
    return 1 if u < v else -1


def complement(literal: Literal):
    return (literal[1], literal[0])


def undirected_edges(clause: Clause):
    return tuple(variable(literal) for literal in clause)


def connected(m: int, clause: Clause) -> bool:
    if m <= 1:
        return True
    adjacency = {v: set() for v in range(m)}
    for u, v in undirected_edges(clause):
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen = {0}
    agenda = [0]
    while agenda:
        u = agenda.pop()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                agenda.append(v)
    return len(seen) == m


def endpoints_connected_without(
    m: int,
    clause: Clause,
    removed: Literal,
) -> bool:
    source, target = removed
    adjacency = {v: set() for v in range(m)}
    removed_once = False
    for literal in clause:
        if literal == removed and not removed_once:
            removed_once = True
            continue
        u, v = variable(literal)
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen = {source}
    agenda = [source]
    while agenda:
        u = agenda.pop()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                agenda.append(v)
    return target in seen


def is_bridge(m: int, clause: Clause, literal: Literal) -> bool:
    return not endpoints_connected_without(m, clause, literal)


def has_directed_cycle(m: int, clause: Clause) -> bool:
    adjacency = {v: set() for v in range(m)}
    for u, v in clause:
        adjacency[u].add(v)
    colour = {v: 0 for v in range(m)}

    def dfs(u: int) -> bool:
        colour[u] = 1
        for v in adjacency[u]:
            if colour[v] == 1:
                return True
            if colour[v] == 0 and dfs(v):
                return True
        colour[u] = 2
        return False

    return any(colour[v] == 0 and dfs(v) for v in range(m))


def clause_key(clause: Clause):
    return tuple(sorted(clause))


def enumerate_clauses(m: int):
    edge_pairs = pairs(m)
    for choices in product((-1, 0, 1), repeat=len(edge_pairs)):
        if all(choice == 0 for choice in choices):
            continue
        clause = tuple(
            oriented(pair, choice)
            for pair, choice in zip(edge_pairs, choices)
            if choice
        )
        yield clause_key(clause)


def resolve(left: Clause, right: Clause, pivot: Literal):
    opposite = complement(pivot)
    if pivot not in left or opposite not in right:
        return None
    result = set(left)
    result.remove(pivot)
    result.update(right)
    result.remove(opposite)
    for literal in tuple(result):
        if complement(literal) in result:
            return None
    return clause_key(tuple(result))


def search(m: int):
    clauses = tuple(enumerate_clauses(m))
    spanning = tuple(clause for clause in clauses if connected(m, clause))
    directed = tuple(clause for clause in clauses if has_directed_cycle(m, clause))
    best = None

    for left in spanning:
        for right in directed:
            common = set(left).intersection(right)
            if not common:
                continue
            for bad in common:
                if is_bridge(m, left, bad) or is_bridge(m, right, bad):
                    continue
                for pivot in left:
                    if pivot == bad or complement(pivot) not in right:
                        continue
                    result = resolve(left, right, pivot)
                    if result is None or bad not in result:
                        continue
                    if not connected(m, result):
                        continue
                    if not is_bridge(m, result, bad):
                        continue
                    record = {
                        "m": m,
                        "left": left,
                        "right": right,
                        "pivot": pivot,
                        "bad": bad,
                        "resolvent": result,
                        "left_width": len(left),
                        "right_width": len(right),
                        "resolvent_width": len(result),
                        "left_directed_cycle": has_directed_cycle(m, left),
                        "right_directed_cycle": has_directed_cycle(m, right),
                    }
                    score = (
                        len(left) + len(right),
                        len(result),
                        len(left),
                        len(right),
                        repr(record),
                    )
                    if best is None or score < best[0]:
                        best = (score, record)
    return {
        "m": m,
        "clause_count": len(clauses),
        "spanning_count": len(spanning),
        "directed_cycle_count": len(directed),
        "witness": None if best is None else best[1],
    }


def self_test() -> None:
    results = []
    for m in (3, 4):
        data = search(m)
        results.append(data)
        print(f"M = {m}")
        print(f"  clause_count = {data['clause_count']}")
        print(f"  spanning_count = {data['spanning_count']}")
        print(f"  directed_cycle_count = {data['directed_cycle_count']}")
        print(f"  witness = {data['witness']}")
        if data["witness"] is not None:
            break

    witness = next(
        (data["witness"] for data in results if data["witness"] is not None),
        None,
    )
    print("JANUS_GT_ABSTRACT_MERGED_TAIL_ORIGIN_SEARCH = PASS")
    print(f"MINIMUM_WITNESS = {witness}")
    print(
        "claim_boundary = exhaustive abstract signed-clause search on the "
        "reported quotient sizes; GT reachability is intentionally ignored"
    )


if __name__ == "__main__":
    self_test()
