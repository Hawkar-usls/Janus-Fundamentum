#!/usr/bin/env python3
"""
Finite regression controls for NM-0014 single-root boundary lifting.

The checker works directly with binary cycle/cocycle spaces for:
  * 2-sum,
  * ordinary Delta 3-sum,
  * dual Y 3-sum.

It verifies the exact restriction-image/kernel statements and the derived
support bounds when the real-side image is spanned by support<=3 vectors.
This is a finite control, not the theorem proof.
"""
from __future__ import annotations

import itertools
import json
import random


def wt(x: int) -> int:
    return x.bit_count()


def rank(rows):
    basis = {}
    for x in rows:
        y = x
        while y:
            b = y.bit_length() - 1
            if b in basis:
                y ^= basis[b]
            else:
                basis[b] = y
                break
    return len(basis)


def basis(rows):
    out = []
    r = 0
    for x in rows:
        nr = rank(out + [x])
        if nr > r:
            out.append(x)
            r = nr
    return out


def span(rows):
    b = basis(rows)
    out = {0}
    for x in b:
        out |= {y ^ x for y in list(out)}
    return out


def orthogonal_basis(rows, n):
    s = span(rows)
    vals = []
    for x in range(1 << n):
        if all(wt(x & y) % 2 == 0 for y in s):
            vals.append(x)
    return basis(vals)


def restrict(x, idxs):
    out = 0
    for j, i in enumerate(idxs):
        if (x >> i) & 1:
            out |= 1 << j
    return out


def embed(real, trace, nreal, z):
    return real | (trace << nreal)


def trace(x, nreal, z):
    return (x >> nreal) & ((1 << z) - 1)


def realpart(x, nreal):
    return x & ((1 << nreal) - 1)


def image_real(space_rows, nreal):
    return span([realpart(x, nreal) for x in span(space_rows)])


def kernel_real(space_rows, nreal):
    return {x for x in span(space_rows) if realpart(x, nreal) == 0}


def trace_image(space_rows, nreal, z):
    return {trace(x, nreal, z) for x in span(space_rows)}


def fiber_product(space1, n1, space2, n2, z):
    # Both spaces live on real_i + same z trace.
    vals = []
    S1, S2 = span(space1), span(space2)
    for x in S1:
        tx = trace(x, n1, z)
        for y in S2:
            if trace(y, n2, z) == tx:
                vals.append(realpart(x, n1) | (realpart(y, n2) << n1))
    return basis(vals)


def random_subspace(n, rng, mindim=2):
    rows = [rng.randrange(1, 1 << n) for _ in range(rng.randint(mindim, n - 1))]
    return basis(rows)


def find_delta_component(nreal, rng):
    z = 3
    n = nreal + z
    Z111 = 0b111 << nreal
    for _ in range(5000):
        rows = basis([Z111] + [rng.randrange(1, 1 << n) for _ in range(rng.randint(3, n))])
        S = span(rows)
        # Exact Delta-side conditions used by the proof:
        # trace onto Z is full; vectors supported entirely on Z are {0,111}.
        if trace_image(rows, nreal, z) != set(range(8)):
            continue
        ker = kernel_real(rows, nreal)
        if ker != {0, Z111}:
            continue
        return rows
    raise RuntimeError("failed to find delta component")


def find_2_component(nreal, rng):
    z = 1
    n = nreal + 1
    Ze = 1 << nreal
    for _ in range(5000):
        rows = random_subspace(n, rng)
        if trace_image(rows, nreal, z) != {0, 1}:
            continue
        if kernel_real(rows, nreal) != {0}:  # e not a loop
            continue
        dual = orthogonal_basis(rows, n)
        if trace_image(dual, nreal, z) != {0, 1}:
            continue
        if kernel_real(dual, nreal) != {0}:  # e not a coloop
            continue
        return rows
    raise RuntimeError("failed to find 2-sum component")


def small_real_generators(image):
    vals = [x for x in image if wt(x) <= 3]
    if rank(vals) != rank(image):
        return None
    return basis(vals)


def unique_lifts(space_rows, nreal, x):
    return [v for v in span(space_rows) if realpart(v, nreal) == x]


def check_2sum(rng):
    n1 = n2 = 4
    V1 = find_2_component(n1, rng)
    V2 = find_2_component(n2, rng)
    Pcycles = fiber_product(V1, n1, V2, n2, 1)
    Pcoc = orthogonal_basis(Pcycles, n1 + n2)
    W1 = orthogonal_basis(V1, n1 + 1)

    parent_img = {restrict(v, range(n1)) for v in span(Pcoc)}
    comp_img = image_real(W1, n1)
    assert parent_img == comp_img
    assert kernel_real(W1, n1) == {0}

    small = small_real_generators(parent_img)
    if small is None:
        return None
    lifted = []
    for x in small:
        L = unique_lifts(W1, n1, x)
        assert len(L) == 1
        v = L[0]
        assert wt(v) <= wt(x) + 1 <= 4
        lifted.append(v)
    assert rank(lifted) == rank(W1)
    return {"real_rank": rank(parent_img), "generator_bound": 4}


def check_delta3(rng):
    n1 = n2 = 4
    V1 = find_delta_component(n1, rng)
    V2 = find_delta_component(n2, rng)
    Pcycles = fiber_product(V1, n1, V2, n2, 3)
    Pcoc = orthogonal_basis(Pcycles, n1 + n2)
    W1 = orthogonal_basis(V1, n1 + 3)

    parent_img = {restrict(v, range(n1)) for v in span(Pcoc)}
    comp_img = image_real(W1, n1)
    assert parent_img == comp_img
    assert kernel_real(W1, n1) == {0}

    small = small_real_generators(parent_img)
    if small is None:
        return None
    lifted = []
    for x in small:
        L = unique_lifts(W1, n1, x)
        assert len(L) == 1
        v = L[0]
        t = trace(v, n1, 3)
        assert wt(t) in (0, 2)  # cocycle vs common triangle
        assert wt(v) <= wt(x) + 2 <= 5
        lifted.append(v)
    assert rank(lifted) == rank(W1)
    return {"real_rank": rank(parent_img), "generator_bound": 5}


def check_y3(rng):
    # A Y-sum in the primal is a Delta-sum in the dual.
    # Therefore the COMPONENT COCYCLE spaces themselves satisfy the
    # Delta-side conditions and the PARENT cocycle space is their fiber product.
    n1 = n2 = 4
    W1 = find_delta_component(n1, rng)
    W2 = find_delta_component(n2, rng)
    Pcoc = fiber_product(W1, n1, W2, n2, 3)

    parent_img = {restrict(v, range(n1)) for v in span(Pcoc)}
    comp_img = image_real(W1, n1)
    assert parent_img == comp_img

    Z111 = 0b111 << n1
    assert kernel_real(W1, n1) == {0, Z111}

    small = small_real_generators(parent_img)
    if small is None:
        return None

    lifted = []
    for x in small:
        L = unique_lifts(W1, n1, x)
        assert len(L) == 2
        assert L[0] ^ L[1] == Z111
        v = min(L, key=lambda q: wt(trace(q, n1, 3)))
        assert wt(trace(v, n1, 3)) <= 1
        assert wt(v) <= wt(x) + 1 <= 4
        lifted.append(v)

    # Small chosen lifts span the quotient by the interface triad;
    # adding the interface-only cocycle spans the full component space.
    assert rank(lifted + [Z111]) == rank(W1)
    return {"real_rank": rank(parent_img), "generator_bound": 4, "kernel_generator_bound": 3}


def run_many(fn, rng, target=100):
    out = []
    tries = 0
    while len(out) < target and tries < 10000:
        tries += 1
        r = fn(rng)
        if r is not None:
            out.append(r)
    assert len(out) == target, (fn.__name__, len(out), tries)
    return {"instances": len(out), "max_real_rank": max(x["real_rank"] for x in out)}


def main():
    rng = random.Random(140014)
    result = {
        "status": "PASS_FINITE_SINGLE_ROOT_BOUNDARY_LIFTING_CONTROLS",
        "two_sum": run_many(check_2sum, rng),
        "delta_three_sum": run_many(check_delta3, rng),
        "y_three_sum": run_many(check_y3, rng),
        "bounds": {
            "two_sum_cocycle_generator_support": 4,
            "delta_three_sum_cocycle_generator_support": 5,
            "y_three_sum_lift_generator_support": 4,
            "y_three_sum_interface_kernel_support": 3,
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
