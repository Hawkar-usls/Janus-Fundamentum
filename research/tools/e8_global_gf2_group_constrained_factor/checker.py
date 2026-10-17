from itertools import product


def occurrence_groups(formula):
    groups = {}
    occ = []
    for ci, clause in enumerate(formula):
        for li, lit in enumerate(clause):
            o = len(occ)
            occ.append((ci, li, lit))
            groups.setdefault(abs(lit), []).append(o)
    return occ, groups


def soft_clause_ok(formula, occ, bits):
    by_clause = [[] for _ in formula]
    for o, (ci, _li, lit) in enumerate(occ):
        y = bits[o]
        truth = y if lit > 0 else 1 - y
        by_clause[ci].append(truth)
    return all(any(vals) for vals in by_clause)


def syndrome(groups, bits):
    out = []
    for v in sorted(groups):
        os = groups[v]
        if len(os) >= 2:
            # This is exactly the alpha / alpha+beta / beta encoding:
            # coordinates are consecutive XORs y_j+y_{j+1}.
            out.extend(bits[os[j]] ^ bits[os[j + 1]] for j in range(len(os) - 1))
    return tuple(out)


def original_sat(formula):
    vars_ = sorted({abs(lit) for c in formula for lit in c})
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        if all(any((a[abs(l)] if l > 0 else 1 - a[abs(l)]) for l in c) for c in formula):
            return True
    return False


def zero_syndrome_soft_factor(formula):
    occ, groups = occurrence_groups(formula)
    q = len(occ)
    found = False
    soft_count = 0
    for bits in product((0, 1), repeat=q):
        if not soft_clause_ok(formula, occ, bits):
            continue
        soft_count += 1
        if all(x == 0 for x in syndrome(groups, bits)):
            found = True
            break
    return found, soft_count


def check(formula):
    sat = original_sat(formula)
    zero, soft_seen = zero_syndrome_soft_factor(formula)
    assert sat == zero, (formula, sat, zero)
    print(f'clauses={len(formula)} SAT={int(sat)} ZERO_SYNDROME_FACTOR={int(zero)} soft_examined={soft_seen} PASS')


def main():
    controls = [
        [(1, 2, 3)],
        [(1, 2), (-1, 3)],
        [(1, 2), (1, -2), (-1, 3)],
        # Frozen v1.5 UNSAT control.
        [(1, 2), (1, -2), (-1, 3), (-3, 4), (-3, -4)],
    ]
    for f in controls:
        check(f)
    print('PASS: normalized SAT iff soft occurrence factor has zero direct-sum GF(2) consistency syndrome')


if __name__ == '__main__':
    main()
