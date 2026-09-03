#!/usr/bin/env python3
from itertools import combinations, permutations, product

BASE = [
    [2, 3, -4],
    [-1, 2, 4],
    [-2, -5, -6],
    [1, -3, -4],
    [1, -5, 6],
    [-3, 5, -6],
    [-2, 3, 6],
    [-1, 4, 5],
]
BASE_VARS = [1, 3, 4, 5, 6]
BASE_ALL_VARS = [1, 2, 3, 4, 5, 6]
PIVOT = 2
EXPECTED_PI = {1: -3, 3: -5, 4: 6, 5: -1, 6: -4}
K = 5


def simplify(formula, var, value):
    sat_lit = var if value else -var
    false_lit = -var if value else var
    out = []
    for clause in formula:
        if sat_lit in clause:
            continue
        out.append([lit for lit in clause if lit != false_lit])
    return out


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = None
    for mask in range(1 << len(formula)):
        sub = [formula[i] for i in range(len(formula)) if (mask >> i) & 1]
        d = deficiency(sub)
        if best is None or d > best:
            best = d
    return best


def pi_clause(clause, pi):
    out = set()
    for lit in clause:
        image = pi[abs(lit)]
        out.add(image if lit > 0 else -image)
    return out


def transport_valid(target, source, pi):
    # source -> target
    for clause in target:
        image = pi_clause(clause, pi)
        if not any(set(d).issubset(image) for d in source):
            return False
    return True


def bounded_support_search(target, source, variables, K):
    """Return first signed permutation with support contained in <=K vars."""
    tested = 0
    variables = tuple(sorted(variables))
    for s in range(K + 1):
        for support in combinations(variables, s):
            for perm in permutations(support):
                rho = dict(zip(support, perm))
                for signs in product([1, -1], repeat=s):
                    pi = {v: v for v in variables}
                    for v, sign in zip(support, signs):
                        pi[v] = sign * rho[v]
                    # Signed permutation must be bijective on underlying vars.
                    if len({abs(x) for x in pi.values()}) != len(variables):
                        continue
                    tested += 1
                    if transport_valid(target, source, pi):
                        actual_support = {v for v in variables if pi[v] != v}
                        return pi, actual_support, tested
    return None, None, tested


def rename_formula(formula, offset):
    out = []
    for clause in formula:
        out.append([(abs(lit) + offset) * (1 if lit > 0 else -1) for lit in clause])
    return out


def disjoint_union_copies(k, stride=10):
    out = []
    for i in range(k):
        out.extend(rename_formula(BASE, i * stride))
    return out


def lift_pi_to_k(pi_local, k, stride=10):
    # Include every variable of every untouched copy, including each copy's
    # pivot variable. Only the distinguished first copy has x2 simplified away.
    variables = set()
    for i in range(k):
        off = i * stride
        variables.update(v + off for v in BASE_ALL_VARS)
    pi = {v: v for v in variables}
    for v, image in pi_local.items():
        pi[v] = image
    return pi


def main():
    A = simplify(BASE, PIVOT, False)
    B = simplify(BASE, PIVOT, True)

    assert maximal_deficiency(BASE) == 2
    assert maximal_deficiency(A) == 1
    assert maximal_deficiency(B) == 1

    # Exact deterministic discovery, not a hardcoded acceptance.
    found, support, tested = bounded_support_search(A, B, BASE_VARS, K)
    assert found == EXPECTED_PI
    assert support == set(BASE_VARS)
    assert len(support) == 5
    assert tested == 3799

    # No transport in the same direction exists with support <=4.
    found4, _, _ = bounded_support_search(A, B, BASE_VARS, 4)
    assert found4 is None

    # Reverse direction has no K5 certificate on this fixed instance.
    reverse, _, reverse_tested = bounded_support_search(B, A, BASE_VARS, K)
    assert reverse is None
    assert reverse_tested == 6331

    # Exact rank-additivity sanity replay for two variable-disjoint copies.
    F2 = disjoint_union_copies(2)
    A2 = simplify(F2, PIVOT, False)
    B2 = simplify(F2, PIVOT, True)
    assert maximal_deficiency(F2) == 4
    assert maximal_deficiency(A2) == 3
    assert maximal_deficiency(B2) == 3

    # The same support-5 permutation, identity outside the distinguished copy,
    # remains a valid transport for arbitrarily many disjoint common copies.
    # Finite replay below checks several sizes; the JSON proof gives the general argument.
    for k in range(1, 6):
        Fk = disjoint_union_copies(k)
        Ak = simplify(Fk, PIVOT, False)
        Bk = simplify(Fk, PIVOT, True)
        pik = lift_pi_to_k(EXPECTED_PI, k)
        assert transport_valid(Ak, Bk, pik)
        assert len({v for v in pik if pik[v] != v}) == 5

    print("R44BQ EXACT REPLAY PASS")
    print("K=5")
    print("base_first_valid_candidate=3799")
    print("base_min_support=5")
    print("reverse_K5_transport=NONE")
    print("discovery_bound=O(n^5*m_A*m_B*w)")
    print("base_rank_effect=2->1")
    print("two_copy_rank_effect=4->3")
    print("support_remains_5_under_disjoint_lift")
    print("universal_critical_sibling_coverage=OPEN")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == '__main__':
    main()
