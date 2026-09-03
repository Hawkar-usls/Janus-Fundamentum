#!/usr/bin/env python3

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
PIVOT = 2
ROOTS = (1, 3, 4, 5, 6)
BASE_PI = {1: -3, 3: -5, 4: 6, 5: -1, 6: -4}


def simplify(formula, var, value):
    sat = var if value else -var
    false = -var if value else var
    out = []
    for c in formula:
        if sat in c:
            continue
        out.append([x for x in c if x != false])
    return out


def vars_of(formula):
    return {abs(x) for c in formula for x in c}


def max_matching_size(formula):
    match = {}
    def aug(ci, seen):
        for v in {abs(x) for x in formula[ci]}:
            if v in seen:
                continue
            seen.add(v)
            if v not in match or aug(match[v], seen):
                match[v] = ci
                return True
        return False
    ans = 0
    for ci in range(len(formula)):
        if aug(ci, set()):
            ans += 1
    return ans


def maxdef(formula):
    return len(formula) - max_matching_size(formula)


def critical(formula):
    k = maxdef(formula)
    return all(maxdef(formula[:i] + formula[i+1:]) < k for i in range(len(formula)))


def sub_image(clause, phi):
    image = set()
    for lit in clause:
        y = phi[abs(lit)]
        y = y if lit > 0 else -y
        if -y in image:
            return True, image
        image.add(y)
    return False, image


def substitution_valid(target, source, phi):
    for c in target:
        taut, image = sub_image(c, phi)
        if taut:
            continue
        if not any(set(d).issubset(image) for d in source):
            return False
    return True


def identity_valid(target, source):
    phi = {v: v for v in vars_of(target)}
    return substitution_valid(target, source, phi)


def block_var(block, local, stride=10):
    if local == PIVOT:
        return PIVOT
    return block * stride + local


def shared_pivot_family(k, stride=10):
    out = []
    for b in range(k):
        for c in BASE:
            nc = []
            for lit in c:
                local = abs(lit)
                v = block_var(b, local, stride)
                nc.append(v if lit > 0 else -v)
            out.append(nc)
    return out


def blockwise_pi(k, stride=10):
    phi = {}
    for b in range(k):
        for r in ROOTS:
            src = block_var(b, r, stride)
            image_local = BASE_PI[r]
            dst = block_var(b, abs(image_local), stride)
            phi[src] = dst if image_local > 0 else -dst
    return phi


def main():
    A = simplify(BASE, PIVOT, False)
    B = simplify(BASE, PIVOT, True)
    assert not identity_valid(A, B)
    assert not identity_valid(B, A)
    assert substitution_valid(A, B, BASE_PI)

    for k in (1, 2, 3):
        G = shared_pivot_family(k)
        A_k = simplify(G, PIVOT, False)
        B_k = simplify(G, PIVOT, True)
        assert maxdef(G) == 3 * k - 1
        assert critical(G)
        assert maxdef(A_k) == k
        assert maxdef(B_k) == k
        phi = blockwise_pi(k)
        assert substitution_valid(A_k, B_k, phi)
        assert sum(phi[v] != v for v in phi) == 5 * k

    print("R44BV EXACT REPLAY PASS")
    print("identity_local_transport_both_directions=FALSE")
    print("parent_rank=3k-1")
    print("sibling_ranks=k,k")
    print("parent_criticality=checked_k1_k2_k3")
    print("blockwise_substitution_upper_bound=5k")
    print("general_deviation_support_lower_bound=k_PROVED_IN_MARKDOWN")
    print("universal_constant_K_many_to_one_substitution_coverage=REFUTED")
    print("critical_unbounded_support_discovery=OPEN")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == '__main__':
    main()
