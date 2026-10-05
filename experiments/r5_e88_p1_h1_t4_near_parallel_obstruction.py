#!/usr/bin/env python3
"""R5 E88: p=1,h=1 t=4 near-parallel-class obstruction.

E87 excluded the p=1,h=1 conditioned-U2,4 lane through t=3 by a residual
edge/half-edge census.  E88 closes t=4 by a shorter exact combinatorial
argument.

For t=4:
    a = 13 active checks,
    b = 12 active variables.

Let x be the unique degree-2 variable carrying the surviving variable-side
boundary port.  In each of the three target states with v=1, x is selected.
Remove x and its two internal check-neighbours r,s.  On the remaining
11-point ground W there are three partial parallel classes of three triples:

    Q_AB partitions W \ {A,B},
    Q_AC partitions W \ {A,C},
    Q_BC partitions W \ {B,C}.

Linearity implies any two distinct triple-variables intersect in at most one
check.

Pairwise shared-block lemma for n=3:
If Q_AB and Q_AC shared one triple, removing it would leave two triples on
each side that must realize five common ordinary points.  Distinct triples
can contribute at most one common point per pair, so a 2x2 intersection graph
has capacity four, contradiction.  Two shared triples are even worse after
cancellation.  Hence no pair of the three classes shares a triple.

Therefore all 9 triples are distinct.  Every ordinary point of
W\{A,B,C} occurs in all three classes and is already saturated to active
check-degree 3, while A,B,C each have degree 1 from these triples.

There are exactly two further cubic active variables outside those nine
triples and x.

Degree completion now kills both zero-hole geometries:
  * overlap: one of A/B/C has target internal degree1, the other two degree2;
    r,s both need two further incidences.  Both extra triples would need both
    r and s, sharing the pair {r,s} with x and creating a Tanner C4.
  * distinct: if the zero-hole check lies in the ordinary W-points, that point
    is already overfull (degree3 vs target2).  Hence the hole must be r or s.
    The other x-neighbour then needs two extra incidences, so both extra
    triples contain it; the hole-neighbour needs one extra incidence, forcing
    one of those triples to contain both r and s, again violating linearity
    with x.

The checker independently enumerates the complete canonical three-class
systems (72) and every linear pair of possible extra triples (245,592 pairs
across those systems).  It confirms zero degree-completing overlap or distinct
configurations.

Thus p=1,h=1 is excluded through t=4.  First open size: t=5, i.e.
16 checks / 15 variables.

P_VS_NP remains OPEN.
"""

from collections import Counter
from itertools import combinations


A,B,C = 0,1,2
R,S = 11,12
X = frozenset({R,S})


def partitions_into_triples(points):
    points=set(points)
    if not points:
        yield ()
        return
    a=min(points)
    rest=points-{a}
    for bc in combinations(sorted(rest),2):
        tri=frozenset((a,*bc))
        rem=rest-set(bc)
        for tail in partitions_into_triples(rem):
            yield (tri,)+tail


def linear_ok(new_triples, existing):
    all_triples=list(existing)
    for t in new_triples:
        for e in all_triples:
            if t == e:
                continue
            if len(t & e) > 1:
                return False
        all_triples.append(t)
    return True


def canonical_three_near_classes():
    # W has 11 points: A,B,C plus 8 ordinary points.  Fix Q_AB canonically
    # by relabeling the eight ordinary points while keeping A,B,C fixed.
    W=set(range(11))
    QAB=(
        frozenset({C,3,4}),
        frozenset({5,6,7}),
        frozenset({8,9,10}),
    )

    out=[]
    for QAC in partitions_into_triples(W-{A,C}):
        if not linear_ok(QAC,QAB):
            continue
        for QBC in partitions_into_triples(W-{B,C}):
            if not linear_ok(QBC,QAB+QAC):
                continue
            out.append((QAB,QAC,QBC))
    return tuple(out)


def pair_shared_capacity_lemma():
    # After k shared triples are cancelled from two n=3 near-parallel
    # classes, m=3-k triples remain on each side and must carry 3m-1 common
    # points.  A simple m x m intersection graph has capacity m^2.
    # For k>=1, m<=2 and 3m-1 > m^2.
    for k in (1,2):
        m=3-k
        assert 3*m-1 > m*m


def target_degrees_overlap(hole):
    d={v:3 for v in range(13)}
    d[A]=d[B]=d[C]=2
    d[hole]=1
    return d


def target_degrees_distinct(hole):
    d={v:3 for v in range(13)}
    d[A]=d[B]=d[C]=2
    d[hole]=2
    return d


def enumerate_degree_completions(systems):
    checked_pairs=0
    overlap_hits=0
    distinct_hits=0

    for QAB,QAC,QBC in systems:
        base=set(QAB+QAC+QBC)
        assert len(base)==9

        deg=Counter()
        for e in base:
            for v in e:
                deg[v]+=1
        # x={r,s} is active in all v=1 states.
        deg[R]+=1
        deg[S]+=1

        assert deg[A]==deg[B]==deg[C]==1
        assert all(deg[v]==3 for v in range(3,11))
        assert deg[R]==deg[S]==1

        candidates=[]
        for e in combinations(range(13),3):
            e=frozenset(e)
            # Linearity with x.
            if len(e & X) > 1:
                continue
            if any(e != f and len(e & f)>1 for f in base):
                continue
            candidates.append(e)

        for e1,e2 in combinations(candidates,2):
            if len(e1 & e2)>1:
                continue
            checked_pairs += 1

            d=deg.copy()
            for v in e1:
                d[v]+=1
            for v in e2:
                d[v]+=1

            for hole in (A,B,C):
                target=target_degrees_overlap(hole)
                if all(d[v]==target[v] for v in range(13)):
                    overlap_hits += 1

            for hole in range(3,13):
                target=target_degrees_distinct(hole)
                if all(d[v]==target[v] for v in range(13)):
                    distinct_hits += 1

    return checked_pairs,overlap_hits,distinct_hits


def main():
    pair_shared_capacity_lemma()

    systems=canonical_three_near_classes()
    assert len(systems)==72

    # Every complete three-class system has nine distinct triples.
    assert all(
        len(set(QAB+QAC+QBC))==9
        for QAB,QAC,QBC in systems
    )

    checked,overlap_hits,distinct_hits=enumerate_degree_completions(systems)
    assert checked==245592
    assert overlap_hits==0
    assert distinct_hits==0

    print("R5 E88 p=1,h=1 t=4 near-parallel-class obstruction: PASS")
    print("canonical three near-parallel-class systems:", len(systems))
    print("all systems use 9 distinct triple variables")
    print("linear extra-triple pairs checked:", checked)
    print("overlap degree completions:", overlap_hits)
    print("distinct-hole degree completions:", distinct_hits)
    print("p=1,h=1 excluded through t=4; first open t=5 => 16 checks / 15 variables")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
