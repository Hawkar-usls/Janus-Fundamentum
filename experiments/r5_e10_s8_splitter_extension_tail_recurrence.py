#!/usr/bin/env python3
"""Exact controls for the S8 rank-saturated extension-tail recurrence."""

from __future__ import annotations

import json

INF = 10**9


def gf2_rank(cols: list[int], rank_bound: int) -> int:
    basis = [0] * rank_bound
    rank = 0
    for x in cols:
        y = x
        while y:
            i = y.bit_length() - 1
            if basis[i]:
                y ^= basis[i]
            else:
                basis[i] = y
                rank += 1
                break
    return rank


def is_3connected(cols: list[int], rank_bound: int) -> bool:
    m = len(cols)
    full_rank = gf2_rank(cols, rank_bound)
    for mask in range(1, 1 << m):
        left_size = mask.bit_count()
        if left_size < 2 or m - left_size < 2:
            continue
        left = [cols[i] for i in range(m) if (mask >> i) & 1]
        right = [cols[i] for i in range(m) if not ((mask >> i) & 1)]
        lam = (
            gf2_rank(left, rank_bound)
            + gf2_rank(right, rank_bound)
            - full_rank
        )
        if lam < 2:
            return False
    return True


def syndrome_distances(cols: list[int], rank_bound: int) -> list[int]:
    d = [INF] * (1 << rank_bound)
    d[0] = 0
    for v in cols:
        old = d[:]
        for syndrome, cost in enumerate(old):
            if cost < INF:
                d[syndrome ^ v] = min(d[syndrome ^ v], cost + 1)
    return d


def extension_update(d: list[int], v: int) -> list[int]:
    old = d[:]
    return [min(old[s], 1 + old[s ^ v]) for s in range(len(old))]


def tail_formula(base_d: list[int], tail: list[int]) -> list[int]:
    out = [INF] * len(base_d)
    for mask in range(1 << len(tail)):
        shift = 0
        cost = 0
        for i, v in enumerate(tail):
            if (mask >> i) & 1:
                shift ^= v
                cost += 1
        for s in range(len(base_d)):
            out[s] = min(out[s], cost + base_d[s ^ shift])
    return out


def test_recurrence() -> None:
    controls = [
        (4, [1, 2, 4, 8, 14, 13, 11], [3, 5, 6]),
        (5, [1, 2, 4, 8, 16, 7, 25, 30], [3, 5, 9]),
        (4, [1, 4, 10], [3, 6]),
    ]
    for rank_bound, base, tail in controls:
        d = syndrome_distances(base, rank_bound)
        cols = base[:]
        for v in tail:
            d = extension_update(d, v)
            cols.append(v)
            assert d == syndrome_distances(cols, rank_bound)

        assert tail_formula(
            syndrome_distances(base, rank_bound), tail
        ) == syndrome_distances(base + tail, rank_bound)


def scalar_signature_countercontrol() -> dict[str, object]:
    rank_bound = 4
    f = 15
    v = 3
    b1 = [1, 2, 12]
    b2 = [1, 4, 10]
    d1 = syndrome_distances(b1, rank_bound)
    d2 = syndrome_distances(b2, rank_bound)

    assert d1[f] == d2[f] == 3
    assert d1[f ^ v] == 1
    assert d2[f ^ v] == INF

    d1_after = extension_update(d1, v)
    d2_after = extension_update(d2, v)
    assert d1_after[f] == 2
    assert d2_after[f] == 3

    return {
        "rank": rank_bound,
        "f": f,
        "extension": v,
        "prefix_1": b1,
        "prefix_2": b2,
        "same_pre_extension_target_cost": 3,
        "post_extension_target_costs": [2, 3],
    }


def s8_rank_saturated_tail() -> list[dict[str, object]]:
    # Sage catalog representation:
    # [I4 | 0111,1011,1101,1111], up to row/bit convention.
    s8 = [1, 2, 4, 8, 14, 13, 11, 15]
    tail = [3, 5, 6, 7, 9, 10, 12]

    assert gf2_rank(s8, 4) == 4
    assert is_3connected(s8, 4)

    cur = s8[:]
    receipt = []
    for v in tail:
        assert v not in cur
        cur.append(v)
        assert gf2_rank(cur, 4) == 4
        assert is_3connected(cur, 4)
        receipt.append(
            {
                "added": v,
                "size": len(cur),
                "rank": 4,
                "three_connected": True,
            }
        )

    assert sorted(cur) == list(range(1, 16))
    return receipt


def main() -> int:
    test_recurrence()
    scalar = scalar_signature_countercontrol()
    tail = s8_rank_saturated_tail()

    print(
        json.dumps(
            {
                "status": "PASS",
                "single_extension_recurrence": "VERIFIED",
                "multi_extension_subset_shift_formula": "VERIFIED",
                "scalar_target_only_signature": (
                    "FALSIFIED_IN_UNRESTRICTED_BINARY_CONTROL"
                ),
                "s8_rank4_extension_tail": "VERIFIED_7_STEP_TO_PG_3_2",
                "scalar_control": scalar,
                "s8_tail": tail,
                "claim_ceiling": (
                    "NO_POLYNOMIAL_SIGNATURE_LOWER_BOUND_CLAIMED"
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
