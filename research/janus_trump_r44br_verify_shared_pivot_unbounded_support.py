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
PIVOT = 2
NONPIVOT = [1, 3, 4, 5, 6]
PI_B_TO_A = {1: -3, 3: -5, 4: 6, 5: -1, 6: -4}


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = -10**9
    for mask in range(1 << len(formula)):
        sub = [formula[i] for i in range(len(formula)) if (mask >> i) & 1]
        best = max(best, deficiency(sub))
    return best


def simplify(formula, var, value):
    sat_lit = var if value else -var
    false_lit = -var if value else var
    out = []
    for clause in formula:
        if sat_lit in clause:
            continue
        out.append([lit for lit in clause if lit != false_lit])
    return out


def pi_clause(clause, pi):
    return {
        (pi[abs(lit)] if lit > 0 else -pi[abs(lit)])
        for lit in clause
    }


def transport_valid(target, source, pi):
    for clause in target:
        image = pi_clause(clause, pi)
        if not any(set(d).issubset(image) for d in source):
            return False
    return True


def shared_pivot_family(k):
    out = []
    for block in range(k):
        mapping = {PIVOT: PIVOT}
        for j, v in enumerate(NONPIVOT):
            mapping[v] = 10 * (block + 1) + j + 1
        for clause in BASE:
            out.append([
                (1 if lit > 0 else -1) * mapping[abs(lit)]
                for lit in clause
            ])
    return out


def local_profile_set():
    """All (d,p,full) profiles of one base-block clause subset."""
    prof = set()
    m = len(BASE)
    for mask in range(1 << m):
        sub = [BASE[i] for i in range(m) if (mask >> i) & 1]
        p = int(PIVOT in vars_of(sub))
        d = deficiency(sub)
        prof.add((d, p, mask == (1 << m) - 1))
    return prof


def dp_family_maxdef(k):
    """Exact block-profile DP for the shared-pivot construction."""
    profiles = [(d, p) for d, p, _ in local_profile_set()]
    states = {(0, 0)}  # (sum d, sum p)
    for _ in range(k):
        nxt = set()
        for sd, sp in states:
            for d, p in profiles:
                nxt.add((sd + d, sp + p))
        states = nxt
    return max(sd + sp - (1 if sp > 0 else 0) for sd, sp in states)


def main():
    A = simplify(BASE, PIVOT, False)
    B = simplify(BASE, PIVOT, True)

    # Exact inherited finite premises.
    assert maximal_deficiency(BASE) == 2
    assert maximal_deficiency(A) == 1
    assert maximal_deficiency(B) == 1

    full_mask = (1 << len(BASE)) - 1
    max_proper = max(
        deficiency([BASE[i] for i in range(len(BASE)) if (mask >> i) & 1])
        for mask in range(full_mask)
    )
    assert max_proper == 1

    identity = {v: v for v in NONPIVOT}
    assert not transport_valid(A, B, identity)
    assert not transport_valid(B, A, identity)
    assert transport_valid(A, B, PI_B_TO_A)

    # Exact algebraic/profile replay for several family sizes.
    for k in range(1, 9):
        Fk = shared_pivot_family(k)
        assert len(Fk) == 8 * k
        assert len(vars_of(Fk)) == 5 * k + 1
        assert deficiency(Fk) == 3 * k - 1
        assert dp_family_maxdef(k) == 3 * k - 1

    # Direct exhaustive cross-check where total clause count is still small.
    F2 = shared_pivot_family(2)
    assert maximal_deficiency(F2) == 5
    A2 = simplify(F2, PIVOT, False)
    B2 = simplify(F2, PIVOT, True)
    assert maximal_deficiency(A2) == 2
    assert maximal_deficiency(B2) == 2

    print("R44BR EXACT PREMISE REPLAY PASS")
    print("base_parent_maxdef=2")
    print("base_children_maxdef=1,1")
    print("base_max_proper_deficiency=1")
    print("identity_transport_both_directions=FALSE")
    print("known_B_to_A_transport=TRUE")
    print("shared_parent_rank_formula=3k-1")
    print("shared_children_rank_formula=k")
    print("support_lower_bound_proof=symbolic_block_argument_in_proof_note")
    print("universal_constant_K_signed_transport=REFUTED_FOR_THIS_CLASS")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
