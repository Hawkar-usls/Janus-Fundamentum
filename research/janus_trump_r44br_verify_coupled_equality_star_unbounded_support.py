#!/usr/bin/env python3
from itertools import permutations, product

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
ROOTS = (1, 3, 4, 5, 6)
PIVOT = 2
PI = {1: -3, 3: -5, 4: 6, 5: -1, 6: -4}


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
    return sorted({abs(lit) for clause in formula for lit in clause})


def max_matching_size(formula):
    vars_list = vars_of(formula)
    match_var = {}

    def augment(ci, seen):
        for v in {abs(lit) for lit in formula[ci]}:
            if v in seen:
                continue
            seen.add(v)
            if v not in match_var or augment(match_var[v], seen):
                match_var[v] = ci
                return True
        return False

    matched = 0
    for ci in range(len(formula)):
        if augment(ci, set()):
            matched += 1
    return matched


def maxdef(formula):
    # Hall-deficiency identity for the clause-variable incidence graph:
    # delta*(F)=|C(F)|-nu(I(F)).
    return len(formula) - max_matching_size(formula)


def critical(formula):
    k = maxdef(formula)
    # Since delta* is monotone under adding clauses, it is enough to check
    # all one-clause deletions.
    return all(maxdef(formula[:i] + formula[i + 1 :]) < k for i in range(len(formula)))


def pi_clause(clause, pi):
    out = set()
    for lit in clause:
        image = pi[abs(lit)]
        out.add(image if lit > 0 else -image)
    return out


def transport_valid(target, source, pi):
    for clause in target:
        image = pi_clause(clause, pi)
        if not any(set(d).issubset(image) for d in source):
            return False
    return True


def all_signed_permutations(variables):
    variables = tuple(variables)
    for perm in permutations(variables):
        for signs in product((1, -1), repeat=len(variables)):
            yield {v: sign * w for v, w, sign in zip(variables, perm, signs)}


def support(pi):
    return {v for v, image in pi.items() if image != v}


def leaf_id(root, j):
    root_index = ROOTS.index(root) + 1
    return 1000 * root_index + j


def extend_with_stars(formula, L):
    out = [list(c) for c in formula]
    for root in ROOTS:
        for j in range(1, L + 1):
            z = leaf_id(root, j)
            out.append([-root, z])
            out.append([root, -z])
    return out


def extended_pi(L):
    out = dict(PI)
    for root in ROOTS:
        image = PI[root]
        sign = 1 if image > 0 else -1
        target_root = abs(image)
        for j in range(1, L + 1):
            out[leaf_id(root, j)] = sign * leaf_id(target_root, j)
    return out


def binary_degrees(formula):
    deg = {v: 0 for v in vars_of(formula)}
    for c in formula:
        if len(c) == 2:
            for v in {abs(x) for x in c}:
                deg[v] += 1
    return deg


def main():
    A = simplify(BASE, PIVOT, False)
    B = simplify(BASE, PIVOT, True)

    assert maxdef(BASE) == 2
    assert maxdef(A) == 1
    assert maxdef(B) == 1
    assert critical(BASE)
    assert critical(A)
    assert critical(B)

    # Full five-root signed-permutation theorem from R44BQ, replayed directly.
    forward = []
    reverse = []
    for pi in all_signed_permutations(ROOTS):
        if transport_valid(A, B, pi):
            forward.append(pi)
        if transport_valid(B, A, pi):
            reverse.append(pi)
    assert forward
    assert min(len(support(pi)) for pi in forward) == 5
    assert transport_valid(A, B, PI)
    assert not reverse

    for L in (2, 3):
        GL = extend_with_stars(BASE, L)
        AL = simplify(GL, PIVOT, False)
        BL = simplify(GL, PIVOT, True)

        assert maxdef(GL) == 2 + 5 * L
        assert maxdef(AL) == 1 + 5 * L
        assert maxdef(BL) == 1 + 5 * L
        assert critical(GL)
        assert critical(AL)
        assert critical(BL)

        degA = binary_degrees(AL)
        leafs = {leaf_id(root, j) for root in ROOTS for j in range(1, L + 1)}
        assert all(degA[v] == 2 for v in leafs)
        assert all(degA[v] >= 2 * L for v in ROOTS)
        assert min(degA[v] for v in ROOTS) >= 4

        epi = extended_pi(L)
        assert transport_valid(AL, BL, epi)
        assert len(support(epi)) == 5 * (L + 1)

    print("R44BR EXACT CONSTRUCTION REPLAY PASS")
    print("base_parent_delta*=2")
    print("base_siblings_delta*=1,1")
    print("base_forward_min_signed_support=5")
    print("base_reverse_signed_transport=NONE")
    print("criticality_extension=checked_L2_L3")
    print("rank_family=2+5L -> 1+5L")
    print("constructed_transport_support=5(L+1)")
    print("general_lower_bound=PROVED_IN_MARKDOWN")
    print("universal_constant_K_signed_transport_coverage=REFUTED")
    print("unbounded_support_polynomial_discovery=OPEN")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
