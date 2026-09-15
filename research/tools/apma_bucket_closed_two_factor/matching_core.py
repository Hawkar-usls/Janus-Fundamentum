from __future__ import annotations

from collections import deque
from typing import Any, Iterable


class MatchingInputError(ValueError):
    pass


def _canonical_graph(vertices: Iterable[int], edges: Iterable[tuple[int, int]]) -> tuple[list[int], list[tuple[int, int]]]:
    verts = sorted({int(v) for v in vertices})
    vset = set(verts)
    out: set[tuple[int, int]] = set()
    for raw_a, raw_b in edges:
        a, b = int(raw_a), int(raw_b)
        if a not in vset or b not in vset:
            raise MatchingInputError("EDGE_ENDPOINT_OUTSIDE_VERTEX_SET")
        if a == b:
            raise MatchingInputError("SELF_LOOP_NOT_SUPPORTED_IN_MATCHING_GADGET")
        if a > b:
            a, b = b, a
        out.add((a, b))
    return verts, sorted(out)


def maximum_matching(vertices: Iterable[int], edges: Iterable[tuple[int, int]]) -> dict[str, Any]:
    """Deterministic unweighted Edmonds blossom maximum-cardinality matching.

    The implementation is intentionally self-contained. Vertex labels are arbitrary ints;
    internal indices follow sorted canonical vertex order. Neighbor scans are sorted.
    """
    verts, canon_edges = _canonical_graph(vertices, edges)
    index = {v: i for i, v in enumerate(verts)}
    n = len(verts)
    adjacency_sets = [set() for _ in range(n)]
    for a, b in canon_edges:
        ia, ib = index[a], index[b]
        adjacency_sets[ia].add(ib)
        adjacency_sets[ib].add(ia)
    adjacency = [sorted(xs) for xs in adjacency_sets]

    match = [-1] * n
    parent = [-1] * n
    base = list(range(n))
    used = [False] * n
    blossom = [False] * n

    counters = {
        "find_path_calls": 0,
        "queue_pops": 0,
        "neighbor_scans": 0,
        "lca_calls": 0,
        "blossom_contractions": 0,
        "augmentations": 0,
    }

    def lca(a: int, b: int) -> int:
        counters["lca_calls"] += 1
        seen = [False] * n
        while True:
            a = base[a]
            seen[a] = True
            if match[a] == -1:
                break
            a = parent[match[a]]
        while True:
            b = base[b]
            if seen[b]:
                return b
            b = parent[match[b]]

    def mark_path(v: int, b: int, child: int) -> None:
        while base[v] != b:
            blossom[base[v]] = True
            blossom[base[match[v]]] = True
            parent[v] = child
            child = match[v]
            v = parent[match[v]]

    def find_augmenting_path(root: int) -> bool:
        nonlocal parent, base, used, blossom
        counters["find_path_calls"] += 1
        used = [False] * n
        parent = [-1] * n
        base = list(range(n))
        queue: deque[int] = deque([root])
        used[root] = True

        while queue:
            v = queue.popleft()
            counters["queue_pops"] += 1
            for u in adjacency[v]:
                counters["neighbor_scans"] += 1
                if base[v] == base[u] or match[v] == u:
                    continue
                if u == root or (match[u] != -1 and parent[match[u]] != -1):
                    current_base = lca(v, u)
                    blossom = [False] * n
                    mark_path(v, current_base, u)
                    mark_path(u, current_base, v)
                    counters["blossom_contractions"] += 1
                    for i in range(n):
                        if blossom[base[i]]:
                            base[i] = current_base
                            if not used[i]:
                                used[i] = True
                                queue.append(i)
                elif parent[u] == -1:
                    parent[u] = v
                    if match[u] == -1:
                        current = u
                        while current != -1:
                            previous = parent[current]
                            next_current = match[previous] if previous != -1 else -1
                            match[current] = previous
                            if previous != -1:
                                match[previous] = current
                            current = next_current
                        counters["augmentations"] += 1
                        return True
                    matched_u = match[u]
                    if not used[matched_u]:
                        used[matched_u] = True
                        queue.append(matched_u)
        return False

    for i in range(n):
        if match[i] == -1:
            find_augmenting_path(i)

    pairs: list[tuple[int, int]] = []
    for i, j in enumerate(match):
        if j != -1 and i < j:
            a, b = verts[i], verts[j]
            pairs.append((a, b) if a < b else (b, a))
    pairs.sort()

    return {
        "matching": pairs,
        "cardinality": len(pairs),
        "perfect": 2 * len(pairs) == n,
        "vertex_count": n,
        "edge_count": len(canon_edges),
        "counters": counters,
    }


def verify_perfect_matching(
    vertices: Iterable[int],
    edges: Iterable[tuple[int, int]],
    matching_edges: Iterable[tuple[int, int]],
) -> dict[str, Any]:
    verts, canon_edges = _canonical_graph(vertices, edges)
    edge_set = set(canon_edges)
    used: set[int] = set()
    canonical_matching: list[tuple[int, int]] = []
    for raw_a, raw_b in matching_edges:
        a, b = int(raw_a), int(raw_b)
        if a > b:
            a, b = b, a
        if (a, b) not in edge_set:
            return {"ok": False, "reason": "MATCHING_EDGE_NOT_IN_GRAPH", "edge": [a, b]}
        if a in used or b in used:
            return {"ok": False, "reason": "MATCHING_VERTEX_REUSED", "edge": [a, b]}
        used.add(a)
        used.add(b)
        canonical_matching.append((a, b))
    if used != set(verts):
        return {
            "ok": False,
            "reason": "MATCHING_NOT_PERFECT",
            "covered_vertex_count": len(used),
            "vertex_count": len(verts),
        }
    return {
        "ok": True,
        "reason": "STATIC_PERFECT_MATCHING_VERIFIED",
        "matching": [list(e) for e in sorted(canonical_matching)],
        "vertex_count": len(verts),
    }


def components_after_delete(
    vertices: Iterable[int],
    edges: Iterable[tuple[int, int]],
    deleted: Iterable[int],
) -> list[list[int]]:
    verts, canon_edges = _canonical_graph(vertices, edges)
    removed = {int(v) for v in deleted}
    if not removed.issubset(set(verts)):
        raise MatchingInputError("TUTTE_SET_OUTSIDE_VERTEX_SET")
    kept = [v for v in verts if v not in removed]
    kept_set = set(kept)
    adjacency: dict[int, list[int]] = {v: [] for v in kept}
    for a, b in canon_edges:
        if a in kept_set and b in kept_set:
            adjacency[a].append(b)
            adjacency[b].append(a)
    for v in adjacency:
        adjacency[v].sort()

    seen: set[int] = set()
    components: list[list[int]] = []
    for start in kept:
        if start in seen:
            continue
        seen.add(start)
        todo = [start]
        component: list[int] = []
        while todo:
            v = todo.pop()
            component.append(v)
            for w in reversed(adjacency[v]):
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        components.append(sorted(component))
    components.sort(key=lambda xs: (xs[0] if xs else -1, len(xs), xs))
    return components


def verify_tutte_obstruction(
    vertices: Iterable[int],
    edges: Iterable[tuple[int, int]],
    obstruction_u: Iterable[int],
) -> dict[str, Any]:
    verts, canon_edges = _canonical_graph(vertices, edges)
    u = sorted({int(v) for v in obstruction_u})
    if not set(u).issubset(set(verts)):
        return {"ok": False, "reason": "TUTTE_SET_OUTSIDE_VERTEX_SET"}
    components = components_after_delete(verts, canon_edges, u)
    odd_components = [comp for comp in components if len(comp) % 2 == 1]
    q = len(odd_components)
    ok = q > len(u)
    return {
        "ok": ok,
        "reason": "STATIC_TUTTE_OBSTRUCTION_VERIFIED" if ok else "TUTTE_INEQUALITY_NOT_VIOLATED",
        "U": u,
        "U_size": len(u),
        "component_sizes": [len(c) for c in components],
        "odd_component_count": q,
        "deficiency_lower_bound": q - len(u),
    }


def derive_tutte_obstruction(
    vertices: Iterable[int],
    edges: Iterable[tuple[int, int]],
) -> dict[str, Any]:
    """Polynomial Gallai-Edmonds candidate derivation, followed by static verification.

    D = {v : nu(H-v) = nu(H)}; A = N(D) \\ D. For a graph without a
    perfect matching, Gallai-Edmonds implies A is a Tutte barrier. Scientific
    UNSAT authority comes only from verify_tutte_obstruction, never from this
    derivation alone.
    """
    verts, canon_edges = _canonical_graph(vertices, edges)
    base_result = maximum_matching(verts, canon_edges)
    if base_result["perfect"]:
        return {
            "status": "NOT_APPLICABLE_PERFECT_MATCHING_EXISTS",
            "matching_number": base_result["cardinality"],
            "maximum_matching_calls": 1,
        }

    nu = int(base_result["cardinality"])
    d_set: set[int] = set()
    calls = 1
    for v in verts:
        reduced_vertices = [x for x in verts if x != v]
        reduced = maximum_matching(reduced_vertices, canon_edges)
        calls += 1
        if int(reduced["cardinality"]) == nu:
            d_set.add(v)

    neighbors_of_d: set[int] = set()
    for a, b in canon_edges:
        if a in d_set and b not in d_set:
            neighbors_of_d.add(b)
        if b in d_set and a not in d_set:
            neighbors_of_d.add(a)
    a_set = sorted(neighbors_of_d - d_set)
    static = verify_tutte_obstruction(verts, canon_edges, a_set)
    if not static["ok"]:
        return {
            "status": "OPEN_DERIVED_TUTTE_SET_FAILED_STATIC_VERIFICATION",
            "matching_number": nu,
            "D": sorted(d_set),
            "A": a_set,
            "maximum_matching_calls": calls,
            "static_verification": static,
        }
    return {
        "status": "VERIFIED_TUTTE_OBSTRUCTION",
        "matching_number": nu,
        "D": sorted(d_set),
        "A": a_set,
        "U": a_set,
        "maximum_matching_calls": calls,
        "static_verification": static,
    }
