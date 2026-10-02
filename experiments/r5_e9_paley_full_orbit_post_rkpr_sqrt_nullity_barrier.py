#!/usr/bin/env python3
"""Finite exact controls for the Paley full-orbit post-RKPR sqrt-nullity theorem.

Prime-field controls q=19,31,43 are enough to regression-test the construction.
The infinite-family statement itself is proved in the companion markdown theorem.
"""

from __future__ import annotations

from collections import defaultdict, deque
from itertools import combinations

import numpy as np


def quadratic_residues(q: int) -> list[int]:
    return sorted({(x * x) % q for x in range(1, q)})


def paley_data(q: int):
    Q = quadratic_residues(q)
    Qset = set(Q)
    arcs = [(u, v) for u in range(q) for v in range(q) if u != v and (v - u) % q in Qset]
    arc_set = set(arcs)
    arc_index = {e: i for i, e in enumerate(arcs)}

    triangles = []
    for a, b, c in combinations(range(q), 3):
        outdeg = {a: 0, b: 0, c: 0}
        edges = []
        for u, v in ((a, b), (a, c), (b, c)):
            e = (u, v) if (u, v) in arc_set else (v, u)
            edges.append(e)
            outdeg[e[0]] += 1
        if sorted(outdeg.values()) == [1, 1, 1]:
            triangles.append(tuple(edges))

    def translate(T, k):
        return tuple(sorted((((u + k) % q, (v + k) % q) for u, v in T)))

    def canon_translation(T):
        return min(translate(T, k) for k in range(q))

    translation_classes = defaultdict(list)
    for T in triangles:
        translation_classes[canon_translation(T)].append(T)

    reps = sorted(translation_classes)
    rep_index = {rep: i for i, rep in enumerate(reps)}

    def multiplicative_orbit(i: int):
        rep = reps[i]
        orbit = set()
        for r in Q:
            scaled = tuple(sorted((((r * u) % q, (r * v) % q) for u, v in rep)))
            orbit.add(rep_index[canon_translation(scaled)])
        return tuple(sorted(orbit))

    mult_orbits = sorted(
        {multiplicative_orbit(i) for i in range(len(reps))},
        key=lambda x: (len(x), x),
    )

    return Q, arcs, arc_index, translation_classes, reps, mult_orbits


def build_source(q: int, full_orbit, arcs, arc_index, classes, reps):
    faces = []
    for i in full_orbit:
        faces.extend(classes[reps[i]])

    n = len(arcs)
    assert len(faces) == n

    coldeg = [0] * n
    pair_seen = set()
    rows = []
    for T in faces:
        idx = sorted(arc_index[e] for e in T)
        assert len(idx) == 3
        rows.append(idx)
        for j in idx:
            coldeg[j] += 1
        for a, b in combinations(idx, 2):
            pair = (a, b)
            assert pair not in pair_seen, "two distinct rows share two columns: non-linear source"
            pair_seen.add(pair)

    assert set(coldeg) == {3}
    return faces, rows


def gradient_signatures(q: int, arcs):
    # Fix p(0)=0.  Each arc coordinate restricts to the functional p(v)-p(u)
    # on the (q-1)-dimensional gradient subspace.
    sigs = []
    for u, v in arcs:
        vec = [0] * (q - 1)
        if v != 0:
            vec[v - 1] += 1
        if u != 0:
            vec[u - 1] -= 1
        assert any(vec)
        # Canonical projective representative over Q. Values are in {-1,0,1},
        # so only a sign normalization is needed.
        first = next(x for x in vec if x)
        if first < 0:
            vec = [-x for x in vec]
        sigs.append(tuple(vec))
    assert len(set(sigs)) == len(arcs), "RKPR collision already visible on gradient subspace"
    return sigs


def rank_mod_prime(rows, n: int, p: int = 101) -> int:
    A = np.zeros((len(rows), n), dtype=np.int64)
    for i, row in enumerate(rows):
        A[i, row] = 1
    A %= p

    r = 0
    m = A.shape[0]
    for c in range(n):
        nz = np.flatnonzero(A[r:, c])
        if nz.size == 0:
            continue
        pivot = r + int(nz[0])
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]
        A[r] = (A[r] * pow(int(A[r, c]), -1, p)) % p
        idx = np.flatnonzero(A[:, c])
        idx = idx[idx != r]
        if idx.size:
            factors = A[idx, c].copy()
            A[idx] = (A[idx] - factors[:, None] * A[r]) % p
        r += 1
        if r == m:
            break
    return r


def levi_component_count(n: int, rows) -> int:
    adj = [[] for _ in range(2 * n)]
    for i, row in enumerate(rows):
        rv = n + i
        for c in row:
            adj[rv].append(c)
            adj[c].append(rv)

    seen = set()
    components = 0
    for s in range(2 * n):
        if s in seen:
            continue
        components += 1
        dq = deque([s])
        seen.add(s)
        while dq:
            u = dq.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
    return components


def check_q(q: int):
    assert q % 12 == 7 and q > 7
    Q, arcs, arc_index, classes, reps, mult_orbits = paley_data(q)
    m = (q - 1) // 2
    n = q * (q - 1) // 2

    assert len(Q) == m
    assert len(arcs) == n
    assert len(reps) == (q * q - 1) // 24

    full = [O for O in mult_orbits if len(O) == m]
    assert full, "the theorem predicts at least one trivial-stabilizer/full Q-orbit"

    # Every full orbit must give a square linear cubic source and be RKPR-clean
    # already on the explicit gradient subspace.
    gradient_signatures(q, arcs)

    best_rank = -1
    connected = 0
    orbit_summaries = []
    for O in full:
        faces, rows = build_source(q, O, arcs, arc_index, classes, reps)
        rank101 = rank_mod_prime(rows, n, 101)
        best_rank = max(best_rank, rank101)
        comps = levi_component_count(n, rows)
        connected += int(comps == 1)
        orbit_summaries.append((len(O), rank101, n - rank101, comps))

    # The explicit gradient space has dimension q-1, so rank_Q <= n-(q-1).
    # If rank modulo 101 reaches that upper bound, rational rank is pinned exactly.
    target_rank = n - (q - 1)
    assert best_rank == target_rank
    assert connected >= 1

    return {
        "q": q,
        "n": n,
        "translation_classes": len(reps),
        "full_orbits": len(full),
        "target_gradient_dim": q - 1,
        "best_rank_mod_101": best_rank,
        "best_nullity_mod_101": n - best_rank,
        "connected_full_orbits": connected,
        "orbits": orbit_summaries,
    }


def main():
    results = [check_q(q) for q in (19, 31, 43)]
    for r in results:
        print(r)
    print("PASS: Paley full-orbit post-RKPR sqrt-nullity finite controls")


if __name__ == "__main__":
    main()
