#!/usr/bin/env python3
import itertools
import json
from pathlib import Path

JSON_PATH = Path(__file__).with_name("JANUS_TRUMP_R44BU_K4_POLYNOMIAL_SUBSTITUTION_DISCOVERY_2026-09-03.json")

BASE = [
    [2,-3,6], [2,-4,-5], [1,-2,4], [1,-4,6],
    [3,-4,5], [-2,5,6], [-2,-3,-6], [-1,5,-6]
]
PIVOT = 2
K = 4


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def simplify(formula, var, value):
    sat = var if value else -var
    false = -sat
    out = []
    for clause in formula:
        if sat in clause:
            continue
        out.append([lit for lit in clause if lit != false])
    return out


def image_clause(clause, phi):
    out = set()
    for lit in clause:
        mapped = phi[abs(lit)]
        out.add(mapped if lit > 0 else -mapped)
    return out


def transport_valid(target, source, phi):
    source_sets = [set(c) for c in source]
    for clause in target:
        img = image_clause(clause, phi)
        if any(-lit in img for lit in img):
            continue
        if not any(d.issubset(img) for d in source_sets):
            return False
    return True


def k_deviation_search(target, source, K):
    variables = tuple(sorted(vars_of(target) | vars_of(source)))
    source_lits = tuple(v for x in variables for v in (x, -x))
    tested = 0
    for s in range(K + 1):
        for support in itertools.combinations(variables, s):
            for images in itertools.product(source_lits, repeat=s):
                phi = {v: v for v in variables}
                for v, image in zip(support, images):
                    phi[v] = image
                if any(phi[v] == v for v in support):
                    continue
                tested += 1
                if transport_valid(target, source, phi):
                    actual = {v for v in variables if phi[v] != v}
                    return phi, actual, tested
    return None, None, tested


def rename_formula(formula, offset):
    return [[(abs(lit)+offset) * (1 if lit > 0 else -1) for lit in clause] for clause in formula]


def disjoint_union_copies(t, stride=10):
    out = []
    for i in range(t):
        out.extend(rename_formula(BASE, i*stride))
    return out


def lift_phi(phi_local, t, stride=10):
    variables = set()
    for i in range(t):
        off = i*stride
        variables.update(abs(lit) for clause in rename_formula(BASE, off) for lit in clause)
    # distinguished first pivot disappears after simplification; leaving an identity
    # entry for it is harmless because it never occurs in a sibling clause.
    phi = {v: v for v in variables}
    phi.update(phi_local)
    return phi


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = -10**9
    for mask in range(1 << len(formula)):
        sub = [formula[i] for i in range(len(formula)) if (mask >> i) & 1]
        best = max(best, deficiency(sub))
    return best


def main():
    data = json.loads(JSON_PATH.read_text())
    expected = {int(k): v for k, v in data["K4_instance"]["valid_phi"].items()}

    A = simplify(BASE, PIVOT, False)
    B = simplify(BASE, PIVOT, True)
    found, support, tested = k_deviation_search(A, B, K)
    assert found is not None
    assert len(support) <= 4
    assert transport_valid(A, B, found)
    assert transport_valid(A, B, expected)
    assert {v for v in expected if expected[v] != v} == set(data["K4_instance"]["deviation_support"])

    # Exact rank replay for the base pair.
    assert maximal_deficiency(BASE) == 2
    assert maximal_deficiency(A) == 0
    assert maximal_deficiency(B) == 1

    # Replay the stated infinite-family mechanism on several finite lifts.
    for t in range(1, 5):
        F = disjoint_union_copies(t)
        At = simplify(F, PIVOT, False)
        Bt = simplify(F, PIVOT, True)
        phi = lift_phi(expected, t)
        assert transport_valid(At, Bt, phi)
        assert len({v for v in phi if phi[v] != v}) == 4

    print("R44BU K4 DISCOVERY REPLAY PASS")
    print(f"base_candidates_until_first_valid={tested}")
    print(f"found_support={len(support)}")
    print("expected_support=4")
    print("discovery_bound=O(n^8 * poly(input))")
    print("finite_lifts_checked=1..4")
    print("universal_critical_coverage=OPEN")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
