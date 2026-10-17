#!/usr/bin/env python3
"""Exact controls for optimal-face blossom-parity DP."""

from __future__ import annotations

import itertools
import json
import random

SEED = 9379992


def all_perfect_matchings(vertices, edges):
    vertices = tuple(sorted(vertices))
    inc = {v: [] for v in vertices}
    for i, (u, v) in enumerate(edges):
        inc[u].append((i, v))
        inc[v].append((i, u))

    def rec(rem):
        if not rem:
            yield ()
            return
        a = min(rem)
        for ei, b in inc[a]:
            if b not in rem:
                continue
            nxt = set(rem)
            nxt.remove(a)
            nxt.remove(b)
            for tail in rec(nxt):
                yield (ei,) + tail

    return list(rec(set(vertices)))


def laminar_children(root, family):
    allsets = [root] + list(family)
    children = {}
    for s in allsets:
        contained = [t for t in family if t < s]
        children[s] = [
            t for t in contained
            if not any(t < u < s for u in contained)
        ]
    return children


def atom_of(v, children):
    for child in children:
        if v in child:
            return child
    return frozenset((v,))


def parity_matching(verts, variants):
    verts = tuple(verts)
    if not verts:
        return {0}
    if len(verts) % 2:
        return set()

    a = verts[0]
    out = set()
    for j in range(1, len(verts)):
        b = verts[j]
        colors = variants.get(frozenset((a, b)), set())
        if not colors:
            continue
        rest = verts[1:j] + verts[j + 1 :]
        sub = parity_matching(rest, variants)
        for x in colors:
            for y in sub:
                out.add(x ^ y)
    return out


def blossom_dp(n, edges, red, tight, family):
    root = frozenset(range(n))
    children = laminar_children(root, family)
    pi = {}

    for s in sorted(family, key=len):
        ch = children[s]
        atoms = ch + [
            frozenset((v,))
            for v in s
            if not any(v in t for t in ch)
        ]
        idx = {a: i for i, a in enumerate(atoms)}

        crossing = [
            ei
            for ei, (u, v) in enumerate(edges)
            if tight[ei] and ((u in s) ^ (v in s))
        ]

        for p in crossing:
            u, v = edges[p]
            inside = u if u in s else v
            exposed = atom_of(inside, ch)
            exposed_i = idx[exposed]

            if exposed in ch:
                offset = pi.get((exposed, p), set())
            else:
                offset = {0}

            variants = {}
            for q, (a, b) in enumerate(edges):
                if not tight[q] or a not in s or b not in s:
                    continue
                aa = atom_of(a, ch)
                bb = atom_of(b, ch)
                if aa == bb:
                    continue

                left = pi.get((aa, q), set()) if aa in ch else {0}
                right = pi.get((bb, q), set()) if bb in ch else {0}
                colors = {
                    red[q] ^ x ^ y
                    for x in left
                    for y in right
                }
                if colors:
                    variants.setdefault(
                        frozenset((idx[aa], idx[bb])), set()
                    ).update(colors)

            remaining = [
                i for i in range(len(atoms)) if i != exposed_i
            ]
            sk = parity_matching(remaining, variants)
            pi[(s, p)] = {x ^ y for x in offset for y in sk}

    ch = children[root]
    atoms = ch + [
        frozenset((v,))
        for v in root
        if not any(v in t for t in ch)
    ]
    idx = {a: i for i, a in enumerate(atoms)}
    variants = {}

    for q, (a, b) in enumerate(edges):
        if not tight[q]:
            continue
        aa = atom_of(a, ch)
        bb = atom_of(b, ch)
        if aa == bb:
            continue

        left = pi.get((aa, q), set()) if aa in ch else {0}
        right = pi.get((bb, q), set()) if bb in ch else {0}
        colors = {
            red[q] ^ x ^ y
            for x in left
            for y in right
        }
        if colors:
            variants.setdefault(
                frozenset((idx[aa], idx[bb])), set()
            ).update(colors)

    return parity_matching(range(len(atoms)), variants)


def is_laminar_with(s, family):
    return all(s <= t or t <= s or s.isdisjoint(t) for t in family)


def random_laminar(n, rng, limit):
    candidates = [
        frozenset(c)
        for k in range(3, n, 2)
        for c in itertools.combinations(range(n), k)
    ]
    rng.shuffle(candidates)
    family = []
    for s in candidates:
        if len(family) >= limit:
            break
        if is_laminar_with(s, family):
            family.append(s)
    return family


def run_controls(trials=600):
    rng = random.Random(SEED)
    feasible = 0
    nested = 0

    for _ in range(trials):
        n = rng.choice((6, 8))
        edges = list(itertools.combinations(range(n), 2))
        family = random_laminar(n, rng, rng.randint(0, 4))

        if any(t < s for s in family for t in family):
            nested += 1

        z = {s: rng.randint(1, 4) for s in family}
        slack = [
            0 if rng.random() < 0.78 else rng.randint(1, 3)
            for _ in edges
        ]
        red = [rng.randrange(2) for _ in edges]

        weights = []
        for ei, (u, v) in enumerate(edges):
            weights.append(
                slack[ei]
                + sum(
                    z[s]
                    for s in family
                    if ((u in s) ^ (v in s))
                )
            )

        pms = all_perfect_matchings(range(n), edges)
        costs = [
            sum(weights[ei] for ei in pm)
            for pm in pms
        ]
        optimum = min(costs)
        dual_lower_bound = sum(z.values())

        # Keep only cases where the constructed laminar dual certificate is
        # exact: some PM uses only tight edges and crosses each odd set once.
        if optimum != dual_lower_bound:
            continue

        exact_parities = {
            sum(red[ei] for ei in pm) & 1
            for pm, cost in zip(pms, costs)
            if cost == optimum
        }
        dp_parities = blossom_dp(
            n,
            edges,
            red,
            [s == 0 for s in slack],
            family,
        )

        assert dp_parities == exact_parities, {
            "n": n,
            "family": [sorted(s) for s in family],
            "exact": sorted(exact_parities),
            "dp": sorted(dp_parities),
        }
        feasible += 1

    assert feasible >= 450
    return {
        "trials": trials,
        "certified_feasible_faces": feasible,
        "generated_nested_family_trials": nested,
    }


def explicit_nested_control():
    n = 8
    edges = list(itertools.combinations(range(n), 2))
    family = [
        frozenset((0, 1, 2)),
        frozenset((0, 1, 2, 3, 4)),
    ]
    z = {family[0]: 2, family[1]: 3}
    red = [
        ((u * 7 + v * 11 + 3) & 1)
        for u, v in edges
    ]
    # All edges tight: every optimum is characterized purely by the two
    # nested odd-cut equalities.
    slack = [0] * len(edges)
    weights = [
        sum(
            z[s]
            for s in family
            if ((u in s) ^ (v in s))
        )
        for u, v in edges
    ]

    pms = all_perfect_matchings(range(n), edges)
    costs = [sum(weights[i] for i in pm) for pm in pms]
    opt = min(costs)
    exact = {
        sum(red[i] for i in pm) & 1
        for pm, c in zip(pms, costs)
        if c == opt
    }
    dp = blossom_dp(n, edges, red, [True] * len(edges), family)
    assert dp == exact
    assert opt == sum(z.values())
    return {
        "family": [sorted(s) for s in family],
        "optimum": opt,
        "parities": sorted(exact),
    }


def main():
    random_receipt = run_controls()
    nested_receipt = explicit_nested_control()
    print(json.dumps({
        "status": "PASS",
        "random_controls": random_receipt,
        "explicit_nested_control": nested_receipt,
        "verified_identity": (
            "recursive_two_state_blossom_DP_parities"
            " == exact_minimum_weight_PM_parities"
        ),
        "claim_ceiling": (
            "OPTIMAL_FACE_PARITY_ONLY__NO_GENERAL_BCPM_"
            "OR_EXACT_MATCHING_CLAIM"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
