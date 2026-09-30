#!/usr/bin/env python3
from itertools import product

F3 = (0, 1, 2)


def proper_cycle(c):
    return all(c[i] != c[(i + 1) % len(c)] for i in range(len(c)))


def all_cycle_colorings(k):
    return [c for c in product(F3, repeat=k) if proper_cycle(c)]


def sigma_types(k):
    return [c for c in all_cycle_colorings(k) if c[0] == 0]


def integrate_tension(t):
    c = [0]
    for d in t[:-1]:
        c.append((c[-1] + d) % 3)
    return tuple(c)


def main():
    for k in range(3, 9):
        cols = all_cycle_colorings(k)
        sigmas = sigma_types(k)
        expected = (2**k + 2*((-1)**k)) // 3
        assert len(sigmas) == expected

        # Unique translation decomposition c = u + sigma.
        for c in cols:
            u = c[0]
            sigma = tuple((x - u) % 3 for x in c)
            assert sigma in sigmas
            assert tuple((u + x) % 3 for x in sigma) == c

        # Sigma <-> nowhere-zero cycle tension bijection.
        tensions = set()
        for s in sigmas:
            t = tuple((s[(i + 1) % k] - s[i]) % 3 for i in range(k))
            assert all(d in (1, 2) for d in t)
            assert sum(t) % 3 == 0
            assert integrate_tension(t) == s
            tensions.add(t)
        assert len(tensions) == len(sigmas)

    sigma4 = sigma_types(4)
    expected4 = {
        (0,1,0,1), (0,1,0,2), (0,1,2,1),
        (0,2,0,1), (0,2,0,2), (0,2,1,2),
    }
    assert set(sigma4) == expected4
    for s in sigma4:
        t = [((s[(i + 1) % 4] - s[i]) % 3) for i in range(4)]
        assert t.count(1) == 2 and t.count(2) == 2

    # Edge equivalence: actual endpoint inequality iff translation difference avoids one gain.
    for sx in sigma4:
        for sy in sigma4:
            for p in range(4):
                for q in range(4):
                    f = (sx[p] - sy[q]) % 3
                    for ux in F3:
                        for uy in F3:
                            cx = (ux + sx[p]) % 3
                            cy = (uy + sy[q]) % 3
                            assert (cx != cy) == (((uy - ux) % 3) != f)

    # Switching identity on one edge.
    for f in F3:
        for ux in F3:
            for uy in F3:
                for sx in F3:
                    for sy in F3:
                        fp = (f + sy - sx) % 3
                        upx = (ux + sx) % 3
                        upy = (uy + sy) % 3
                        assert (((uy - ux) % 3) != f) == (((upy - upx) % 3) != fp)

    print("PASS: normalized cycle types and Z3 gain constraints")
    print("|Sigma_3|=2, |Sigma_4|=6")
    print("C4 normalized types are exactly the six 2-plus/2-minus tensions")
    print("edge properness equals one forbidden Z3 relative-difference residue")


if __name__ == '__main__':
    main()
