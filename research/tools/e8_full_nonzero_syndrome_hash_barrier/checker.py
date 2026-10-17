from itertools import product

FORMULA = [(1,2),(1,-2),(-1,3),(-3,4),(-3,-4)]


def build_occurrences():
    occ = []
    groups = {}
    for ci, clause in enumerate(FORMULA):
        for li, lit in enumerate(clause):
            o = len(occ)
            occ.append((ci, li, lit))
            groups.setdefault(abs(lit), []).append(o)
    return occ, groups


def soft_ok(occ, bits):
    for ci, _clause in enumerate(FORMULA):
        vals = []
        for o, (cci, _li, lit) in enumerate(occ):
            if cci != ci:
                continue
            y = bits[o]
            vals.append(y if lit > 0 else 1 - y)
        if not any(vals):
            return False
    return True


def syndrome(groups, bits):
    out = []
    for v in sorted(groups):
        os = groups[v]
        out.extend(bits[os[j]] ^ bits[os[j+1]] for j in range(len(os)-1))
    return tuple(out)


def original_unsat():
    vars_ = [1,2,3,4]
    for vals in product((0,1), repeat=4):
        a = dict(zip(vars_, vals))
        if all(any((a[abs(l)] if l > 0 else 1-a[abs(l)]) for l in c) for c in FORMULA):
            return False
    return True


def main():
    assert original_unsat()
    occ, groups = build_occurrences()
    assert groups == {1:[0,2,4], 2:[1,3], 3:[5,6,8], 4:[7,9]}
    syndromes = []
    soft_count = 0
    for bits in product((0,1), repeat=len(occ)):
        if soft_ok(occ, bits):
            soft_count += 1
            syndromes.append(syndrome(groups, bits))

    S = set(syndromes)
    universe = set(product((0,1), repeat=6))
    zero = (0,0,0,0,0,0)
    assert soft_count == 243, soft_count
    assert len(S) == 63, len(S)
    assert zero not in S
    assert S == universe - {zero}

    # Hence every proper linear compression H:F2^6->F2^r has a nonzero
    # kernel vector, and that vector is realized by a soft feasible factor.
    basis = [tuple(1 if i == j else 0 for i in range(6)) for j in range(6)]
    assert all(e in S for e in basis)
    print('soft_count=243 distinct_syndromes=63 zero_absent=1 all_nonzero_present=1 PASS')
    print('PASS: every dimension-reducing linear zero-hash has a false positive on the frozen UNSAT witness')


if __name__ == '__main__':
    main()
