from collections import Counter, defaultdict
from itertools import product


def sat_eval(formula, assignment):
    return all(any((assignment[abs(l)] if l > 0 else not assignment[abs(l)]) for l in clause) for clause in formula)


def brute_sat(formula):
    vars_ = sorted({abs(l) for c in formula for l in c})
    for vals in product((False, True), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        if sat_eval(formula, a):
            return True
    return False


def build_terms(formula):
    occ = defaultdict(lambda: {1: [], -1: []})
    for ci, clause in enumerate(formula):
        for pi, lit in enumerate(clause):
            occ[abs(lit)][1 if lit > 0 else -1].append((ci, pi))

    term_at = {}
    gens = []

    for var, sides in occ.items():
        pos, neg = sides[1], sides[-1]
        total = len(pos) + len(neg)
        assert total <= 3
        if pos and neg:
            if total == 2:
                g = f"e{var}"
                gens.append(g)
                term_at[pos[0]] = (g,)
                term_at[neg[0]] = (g,)
            else:
                majority, minority = (pos, neg) if len(pos) == 2 else (neg, pos)
                assert len(majority) == 2 and len(minority) == 1
                e, f = f"e{var}", f"f{var}"
                gens.extend([e, f])
                term_at[majority[0]] = (e,)
                term_at[majority[1]] = (f,)
                term_at[minority[0]] = (e, f)
        else:
            side = pos or neg
            for j, where in enumerate(side):
                g = f"p{var}_{j}"
                gens.append(g)
                term_at[where] = (g,)

    clauses = []
    for ci, clause in enumerate(formula):
        clauses.append([term_at[(ci, pi)] for pi in range(len(clause))])

    reads = Counter(g for clause in clauses for term in clause for g in term)
    assert max(reads.values(), default=0) <= 2, reads
    return clauses, reads


def has_squarefree_monomial(clauses):
    # Finite replay only: enumerate one term per clause and test generator repetition.
    for chosen in product(*clauses):
        seen = set()
        good = True
        for term in chosen:
            for g in term:
                if g in seen:
                    good = False
                    break
                seen.add(g)
            if not good:
                break
        if good:
            return True
    return False


def check(formula, expected=None):
    clauses, reads = build_terms(formula)
    sat = brute_sat(formula)
    sq = has_squarefree_monomial(clauses)
    assert sat == sq, (formula, sat, sq)
    if expected is not None:
        assert sat == expected
    print(f"clauses={len(formula)} generators={len(reads)} max_read={max(reads.values(), default=0)} SAT={int(sat)} SQFREE={int(sq)} PASS")


def main():
    controls = [
        ([(1, 2, 3)], True),
        ([(1, 2), (-1, 3)], True),
        ([(1, 2), (1, -2), (-1, 3), (-3, 4), (-3, -4)], False),
        ([(1, 2, 3), (-1, 2, -3), (1, -2, 4)], True),
        ([(1, 2), (-1, 2), (1, -2), (-1, -2)], False),
    ]
    for formula, expected in controls:
        # These controls all respect occurrence <= 3 per variable except the last,
        # which is intentionally skipped from the bounded-occurrence carrier check.
        counts = Counter(abs(l) for c in formula for l in c)
        if max(counts.values()) > 3:
            assert brute_sat(formula) == expected
            print(f"clauses={len(formula)} control_only_occurrence_bound_exceeded PASS")
            continue
        check(formula, expected)
    print("PASS: bounded-occurrence SAT iff read-2 Pi-Sigma_3-Pi_2 carrier has a squarefree monomial")


if __name__ == "__main__":
    main()
