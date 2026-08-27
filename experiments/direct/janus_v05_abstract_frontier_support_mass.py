#!/usr/bin/env python3
"""Exact finite abstract frontier verifier for JANUS v0.5 ordinary elimination.

This checker proves a FINITE cap-availability statement over an explicit
integer overapproximation of normalized unit-free canonical CNF states.
It is not a SAT solver and does not prove unbounded totality or P=NP.

Abstract state: (n,m,L)
  n = live variables
  m = canonical clauses
  L = literal occurrences

The transfer is sound but intentionally overapproximating.  A PASS therefore
proves the checked finite-N cap statement from the frozen lemmas.  A FAIL means
only that the current abstraction/bounds are insufficient; it is NOT an actual
CNF counterexample unless separately realized.
"""

from __future__ import annotations

from functools import lru_cache
from math import comb

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"
BASE_FINITE_FRONTIER = 54
TAIL_N = 6


def degree_interval(n: int, m: int, L: int) -> tuple[int, int]:
    """Necessary interval for the minimum incidence degree d.

    If one variable has degree d and all other n-1 variables have degree in
    [d,m], then nd<=L<=d+(n-1)m.
    """
    return max(1, L - (n - 1) * m), min(m, L // n)


@lru_cache(maxsize=None)
def wmax(r: int, R: int) -> int:
    """Maximum width sum of R distinct signed clauses over r variables."""
    if R <= 0:
        return 0
    rem = R
    total = 0
    for w in range(r, -1, -1):
        count = comb(r, w) * (2 ** w)
        take = min(rem, count)
        total += take * w
        rem -= take
        if rem == 0:
            return total
    raise AssertionError((r, R, "R exceeds signed-clause universe"))


@lru_cache(maxsize=None)
def omission_product_max(p: int, q: int, o: int) -> int:
    best = 0
    for a in range(min(p, o) + 1):
        b = min(q, o - a)
        best = max(best, a * b)
    return best


@lru_cache(maxsize=None)
def support_resolvent_ceiling(n: int, m: int, d: int, p: int, q: int) -> int:
    if p == 0 or q == 0:
        return 0
    r = n - 1
    c = m - d
    pq = p * q
    o = min(d, c)
    smin = r * (pq - omission_product_max(p, q, o))
    lo, hi = 0, min(pq, 3 ** r)
    # F(R)=Wmax(r,R)+(pq-R)r is nonincreasing.
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if wmax(r, mid) + (pq - mid) * r >= smin:
            lo = mid
        else:
            hi = mid - 1
    return lo


def near_full_resolvent_ceiling(m: int, p: int, q: int) -> int:
    """d=m-1 theorem: distinct resolvents <= max(1,pq-min(p,q)+1)."""
    if p == 0 or q == 0:
        return 0
    a = min(p, q)
    return max(1, p * q - a + 1)


@lru_cache(maxsize=None)
def transfer_bounds(n: int, m: int, L: int, d: int, p: int, q: int) -> tuple[int, int, int, int]:
    """Return (raw_units_cap, m_out_cap, L_out_cap, R_resolvent_cap)."""
    assert p + q == d
    r = n - 1
    c = m - d

    # Every pivot-parent clause is unit-free, hence has >=1 tail literal.
    # Retained literal mass is also at most c*r by width.
    retained_L_cap = min(c * r, max(0, L - 2 * d))

    if p == 0 or q == 0:
        raw = 1 + c + retained_L_cap
        return raw, c, retained_L_cap, 0

    R = support_resolvent_ceiling(n, m, d, p, q)
    if d == m:
        # General full-width-collapse theorem.
        R = min(R, min(p, q))
    elif d == m - 1:
        # General near-full-collapse theorem.
        R = min(R, near_full_resolvent_ceiling(m, p, q))

    m_out = c + R
    k = max(p, q)

    # General low-degree literal-transport theorem.
    L_transport = k * (L - d) - 2 * (k - 1) * c
    # Support ceiling also bounds distinct-resolvent total width.
    L_support = retained_L_cap + wmax(r, R)
    L_out = max(0, min(L_transport, L_support, m_out * r))

    # Two independent raw-set bounds; take their minimum.
    raw_support = 1 + c + retained_L_cap + R + wmax(r, R)
    raw_transport = 1 + c + p * q + max(0, L_transport)
    raw = min(raw_support, raw_transport)
    return raw, m_out, L_out, R


def add_pareto_rectangle(rects: list[tuple[int, int]], M: int, L: int) -> None:
    """Union rectangles [m<=M,L<=Lcap], keeping only Pareto maxima."""
    if M < 7 or L < 14:
        return
    if any(a >= M and b >= L for a, b in rects):
        return
    rects[:] = [(a, b) for a, b in rects if not (M >= a and L >= b)]
    rects.append((M, L))


def hard_roots(N: int) -> dict[int, set[tuple[int, int]]]:
    """Roots not already closed by m<=6, n<=6, or L<3n reroot."""
    roots: dict[int, set[tuple[int, int]]] = {}
    max_n = (N - 8) // 4  # m>=7 and L>=3n imply N>=8+4n
    for n in range(7, max_n + 1):
        rows: set[tuple[int, int]] = set()
        for m in range(7, N):
            L = N - 1 - n - m
            if L < 3 * n or L < 2 * m or L > n * m:
                continue
            dlo, dhi = degree_interval(n, m, L)
            if dlo <= dhi:
                rows.add((m, L))
        if rows:
            roots[n] = rows
    return roots


def verify_N(N: int, previous_frontier: int) -> dict:
    assert previous_frontier == N - 1
    assert previous_frontier >= BASE_FINITE_FRONTIER
    cap = N * N
    roots = hard_roots(N)
    max_n = max(roots, default=TAIL_N)
    rectangles: dict[int, list[tuple[int, int]]] = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}

    checked_states = 0
    checked_transitions = 0
    worst_raw = -1
    worst_witness = None
    layer_counts: dict[int, int] = {}

    # n strictly decreases under ordinary elimination, so descending layers
    # form a finite acyclic abstract proof graph.
    for n in range(max_n, 6, -1):
        candidates = set(rootsets.get(n, set()))
        rects = rectangles[n]
        max_M = max((M for M, _ in rects), default=0)

        # Materialize the union of Pareto rectangles only once per n-layer.
        for m in range(7, max_M + 1):
            Lcap = max((Lb for M, Lb in rects if M >= m), default=-1)
            if Lcap < 0:
                continue
            # Strong-induction gate: local input size 1+n+m+L > previous_frontier.
            # Smaller local states are already covered by the previous finite theorem,
            # and their smaller cap is no larger than the current N^2 cap.
            Llo = max(2 * m, n, previous_frontier - n - m)
            Lhi = min(Lcap, n * m, cap - 1 - m)
            if Llo > Lhi:
                continue
            for L in range(Llo, Lhi + 1):
                dlo, dhi = degree_interval(n, m, L)
                if dlo <= dhi:
                    candidates.add((m, L))

        layer_counts[n] = len(candidates)
        for m, L in sorted(candidates):
            checked_states += 1
            dlo, dhi = degree_interval(n, m, L)
            for d in range(dlo, dhi + 1):
                # p<->q is symmetric for every bound used here.
                for p in range(0, d // 2 + 1):
                    q = d - p
                    checked_transitions += 1
                    raw, m_out, L_out, R = transfer_bounds(n, m, L, d, p, q)
                    if raw > worst_raw:
                        worst_raw = raw
                        worst_witness = {
                            "state": [n, m, L],
                            "d": d,
                            "p": p,
                            "q": q,
                            "raw_bound": raw,
                            "m_out_bound": m_out,
                            "L_out_bound": L_out,
                            "distinct_resolvent_bound": R,
                        }
                    if raw > cap:
                        return {
                            "N": N,
                            "status": "ABSTRACT_BOUND_OPEN",
                            "cap": cap,
                            "checked_states": checked_states,
                            "checked_transitions": checked_transitions,
                            "layer_counts": layer_counts,
                            "first_open": worst_witness,
                            "claim_ceiling": "ABSTRACTION_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE",
                            "P_VS_NP": "OPEN",
                        }

                    # Unit propagation/canonicalization can only lower n,m,L.
                    # m<=6 closes by the proved invariant; n<=6 closes by Uraw(6).
                    for n2 in range(7, n):
                        add_pareto_rectangle(rectangles[n2], m_out, L_out)

    return {
        "N": N,
        "status": "PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_ABSTRACT_OVERAPPROX",
        "cap": cap,
        "root_states": sum(len(v) for v in roots.values()),
        "checked_states": checked_states,
        "checked_transitions": checked_transitions,
        "layer_counts": layer_counts,
        "pareto_rectangle_counts": {str(n): len(rectangles[n]) for n in rectangles},
        "worst_raw_bound": worst_raw,
        "worst_witness": worst_witness,
        "claim_ceiling": "FINITE_N_ORDINARY_ELIMINATION_CAP_AVAILABILITY_ONLY",
        "P_VS_NP": "OPEN",
    }


def selftest() -> None:
    # Frozen support-mass arithmetic specimen.
    assert support_resolvent_ceiling(7, 59, 43, 18, 25) == 352
    assert wmax(6, 352) == 1728

    previous = BASE_FINITE_FRONTIER
    for N in (55, 56, 57):
        result = verify_N(N, previous)
        print(f"ABSTRACT_N{N}_STATUS={result['status']}")
        print(f"ABSTRACT_N{N}_CHECKED_STATES={result['checked_states']}")
        print(f"ABSTRACT_N{N}_CHECKED_TRANSITIONS={result['checked_transitions']}")
        if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_ABSTRACT_OVERAPPROX':
            print(f"ABSTRACT_N{N}_FIRST_OPEN={result['first_open']}")
            raise AssertionError(result)
        print(f"ABSTRACT_N{N}_WORST_RAW_BOUND={result['worst_raw_bound']}")
        assert result['worst_raw_bound'] <= N * N
        previous = N

    print('V05_ABSTRACT_FRONTIER_N55_TO_N57=PASS')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('ABSTRACT_FAIL_WOULD_BE_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
