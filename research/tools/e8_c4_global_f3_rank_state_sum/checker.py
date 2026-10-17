#!/usr/bin/env python3
"""Exact v8.5.3 checker: global F3 current -> partition-constrained rank-state sum."""

from collections import Counter
from itertools import permutations

VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)


def mod3(x):
    return x % 3


def wire_state(c, s, q):
    # Canonical exposed-port order: L0,L2,L3,R0,R2,R3.
    return (
        mod3(c + s),
        mod3(c + s * q),
        mod3(c),
        mod3(c + s * q),
        mod3(c - s * (1 + q)),
        mod3(c + s * (q - 1)),
    )


WIRE6 = sorted(
    {
        wire_state(c, s, q)
        for c in range(3)
        for s in (1, 2)
        for q in (1, 2)
    }
)
assert len(WIRE6) == 12


def gf3_rank(rows, ncols):
    """Exact Gaussian rank over F3, no external algebra package."""
    a = [[x % 3 for x in row] for row in rows if any(x % 3 for x in row)]
    r = 0
    c = 0
    while r < len(a) and c < ncols:
        pivot = next((i for i in range(r, len(a)) if a[i][c] % 3), None)
        if pivot is None:
            c += 1
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = 1 if a[r][c] == 1 else 2
        a[r] = [(inv * x) % 3 for x in a[r]]
        for i in range(len(a)):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [(x - f * y) % 3 for x, y in zip(a[i], a[r])]
        r += 1
        c += 1
    return r


def direct_closed_count(pi):
    z = 0
    for x in WIRE6:
        for y in WIRE6:
            if all(x[j] != y[pi[j]] for j in range(6)):
                z += 1
    return z


def rank_state_sum_two(pi):
    """Evaluate the v8.5.3 rank-state expansion for two closed quotient wires.

    Variables are the six oriented splice currents k_0,...,k_5 from wire 1 to wire 2.
    Base rows are the two wire-conservation equations.  The second is dependent in
    this two-wire closure, but we retain it deliberately and let GF(3) rank handle it.

    Edge expansion: h(k_e)=3*delta[k_e=0]-1.
    Vertex expansion: A_v=3*delta[l_+=0]+3*delta[l_-=0]-2.
    Therefore each rank-state is an edge subset S and one local symbol in {0,+,-}
    per wire; the number of currents satisfying its selected linear constraints is
    exactly 3^(6-rank).
    """
    n = 6
    base_rows = [[1] * n, [2] * n]

    lp1 = list(VP)
    lm1 = list(VM)
    # If k_j enters wire 1 at canonical port j then it enters wire 2 with sign -1
    # at canonical port pi[j].  Express both wire-2 forms in the k_j coordinates.
    lp2 = [(-VP[pi[j]]) % 3 for j in range(n)]
    lm2 = [(-VM[pi[j]]) % 3 for j in range(n)]

    total = 0
    states = 0
    rank_profile = Counter()

    for mask in range(1 << n):
        edge_rows = [row[:] for row in base_rows]
        selected_edges = mask.bit_count()
        for e in range(n):
            if (mask >> e) & 1:
                row = [0] * n
                row[e] = 1
                edge_rows.append(row)

        edge_coeff = (3 ** selected_edges) * ((-1) ** (n - selected_edges))

        for t1 in range(3):
            for t2 in range(3):
                rows = [row[:] for row in edge_rows]
                coeff = edge_coeff

                for t, lp, lm in ((t1, lp1, lm1), (t2, lp2, lm2)):
                    if t == 0:
                        coeff *= -2
                    elif t == 1:
                        coeff *= 3
                        rows.append(lp)
                    else:
                        coeff *= 3
                        rows.append(lm)

                rank = gf3_rank(rows, n)
                rank_profile[rank] += 1
                total += coeff * (3 ** (n - rank))
                states += 1

    assert states == (2 ** 6) * (3 ** 2) == 576
    assert total % (3 ** 4) == 0
    return total // (3 ** 4), rank_profile


count_profile = Counter()
aggregate_rank_profile = Counter()
for pi in permutations(range(6)):
    direct = direct_closed_count(pi)
    ranked, rp = rank_state_sum_two(pi)
    assert ranked == direct
    count_profile[direct] += 1
    aggregate_rank_profile.update(rp)

assert sum(count_profile.values()) == 720
assert count_profile == Counter({0: 96, 6: 180, 12: 168, 18: 168, 24: 80, 30: 20, 36: 8})
assert sum(aggregate_rank_profile.values()) == 720 * 576

print("PASS: h(t)=3*delta[t=0]-1 and A_v=3*delta[l_plus=0]+3*delta[l_minus=0]-2 expanded exactly")
print("PASS: every expansion term is counted by one GF(3) Gaussian rank")
print("PASS: two-wire rank-state sum has exactly 2^6*3^2=576 states per closure")
print("PASS: rank-state evaluation matches direct 12-state counting for all 6!=720 port matchings")
print("DIRECT_COUNT_PROFILE=0:96,6:180,12:168,18:168,24:80,30:20,36:8")
print("RANK_STATE_COUNT=414720")
print("VERDICT: EXACT_PARTITION_CONSTRAINED_TERNARY_RANK_STATE_SUM_ESTABLISHED")
print("FRONTIER: COMPRESS_THE_24^m_RANK_STATE_SUM_WITHOUT_LOSING_HAMILTONIAN_PORT_ORDER_OR_WITNESS_RECONSTRUCTION")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
