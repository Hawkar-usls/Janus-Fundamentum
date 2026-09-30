#!/usr/bin/env python3
from itertools import product

COLORS = (0, 1, 2)

def third(a, b):
    assert a != b
    return (-a - b) % 3

def alldiff(a, b, c):
    return len({a, b, c}) == 3

def brute_extends(nh, edges_h, boundary_inc, bcols):
    """Does fixed boundary colouring extend to H? boundary_inc: list[(h_vertex,boundary_index)]."""
    for hc in product(COLORS, repeat=nh):
        ok = True
        for u, v in edges_h:
            if hc[u] == hc[v]:
                ok = False
                break
        if not ok:
            continue
        for v, j in boundary_inc:
            if hc[v] == bcols[j]:
                ok = False
                break
        if ok:
            return True
    return False

def check_case(name, nh, edges_h, boundary_inc, bad_pred):
    nb = 1 + max((j for _, j in boundary_inc), default=-1)
    total = 0
    for bcols in product(COLORS, repeat=nb):
        extends = brute_extends(nh, edges_h, boundary_inc, bcols)
        bad = bad_pred(bcols)
        if extends == bad:
            raise AssertionError((name, bcols, extends, bad))
        total += 1
    print(f"PASS {name}: {total} boundary colourings")
    return total

# H=K1, three outside neighbours. Failure iff all three boundary colours are distinct.
def bad_k1(c):
    return alldiff(c[0], c[1], c[2])

# H=K2, each endpoint has two outside neighbours. One shared K2 palette sigma must be
# the missing colour of both boundary pairs.
def bad_k2(c):
    a,b,d,e = c
    if a == b or d == e:
        return False
    return third(a,b) == third(d,e)

# H=P3, endpoints have two outside neighbours; middle has one outside neighbour.
# Let sigma01, sigma12 be K2 labels. Failure iff endpoint pairs force the labels and
# ALLDIFF(sigma01,sigma12,middle_boundary).
def bad_p3(c):
    a,b,m,d,e = c
    if a == b or d == e:
        return False
    s01 = third(a,b)
    s12 = third(d,e)
    return alldiff(s01, s12, m)

# H=K1,3. Each leaf has two outside neighbours; the three forced K2 labels must be all distinct.
def bad_claw(c):
    labels = []
    for i in range(0, 6, 2):
        if c[i] == c[i+1]:
            return False
        labels.append(third(c[i], c[i+1]))
    return alldiff(*labels)

# H=C3 or C5. Every H vertex has one outside neighbour. A bad odd-cycle degree-list assignment
# has one common missing colour mu, hence all boundary colours are equal.
def bad_odd_cycle(c):
    return len(set(c)) == 1

# Triangle 0-1-2-0 plus bridge 0-3. Noncut triangle vertices 1,2 each have one outside neighbour;
# bridge leaf 3 has two. Badness: triangle boundary colours agree (=mu), leaf pair is distinct and
# its missing colour sigma equals mu.
def bad_triangle_bridge(c):
    t1,t2,a,b = c
    if t1 != t2 or a == b:
        return False
    return third(a,b) == t1


def main():
    total = 0
    total += check_case(
        "isolated_degree3_vertex",
        1, [], [(0,0),(0,1),(0,2)], bad_k1)
    total += check_case(
        "K2_component",
        2, [(0,1)], [(0,0),(0,1),(1,2),(1,3)], bad_k2)
    total += check_case(
        "P3_component",
        3, [(0,1),(1,2)], [(0,0),(0,1),(1,2),(2,3),(2,4)], bad_p3)
    total += check_case(
        "claw_component",
        4, [(0,1),(0,2),(0,3)],
        [(1,0),(1,1),(2,2),(2,3),(3,4),(3,5)], bad_claw)
    total += check_case(
        "triangle_component",
        3, [(0,1),(1,2),(2,0)], [(0,0),(1,1),(2,2)], bad_odd_cycle)
    total += check_case(
        "C5_component",
        5, [(0,1),(1,2),(2,3),(3,4),(4,0)],
        [(0,0),(1,1),(2,2),(3,3),(4,4)], bad_odd_cycle)
    total += check_case(
        "triangle_plus_bridge",
        4, [(0,1),(1,2),(2,0),(0,3)],
        [(1,0),(2,1),(3,2),(3,3)], bad_triangle_bridge)

    # Algebraic control: ALLDIFF iff sum=0 mod3 and first two differ.
    for a,b,c in product(COLORS, repeat=3):
        lhs = alldiff(a,b,c)
        rhs = ((a+b+c) % 3 == 0 and a != b)
        if lhs != rhs:
            raise AssertionError(("alldiff_linearization", a,b,c,lhs,rhs))
    print("PASS ALLDIFF_3 affine linearization: 27 triples")
    print(f"PASS total boundary assignments replayed: {total}")

if __name__ == "__main__":
    main()
