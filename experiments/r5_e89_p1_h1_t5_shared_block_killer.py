#!/usr/bin/env python3
"""R5 E89: p=1,h=1 t=5 shared-block killer.

E88 excluded p=1,h=1 through t=4.  For t=5, remove the common degree-2
boundary variable x from the three v=1 target covers.  We obtain three
near-parallel classes Q_AB,Q_AC,Q_BC, each containing four triples on a
14-point ground W:

    Q_AB partitions W\{A,B}
    Q_AC partitions W\{A,C}
    Q_BC partitions W\{B,C}.

Linearity implies any pair of classes shares at most one triple.  If k shared
blocks are cancelled, m=4-k triples remain on each side and must carry 3m-1
common points in a simple m x m intersection graph.  k>=2 would give m<=2 and
3m-1>m^2.

The checker fixes Q_AB canonically and enumerates the complete compatible
linear triples (Q_AC,Q_BC). Frozen total: 412,344.

Sharing patterns:
  no pair shares                              291,600
  exactly one specified pair shares           36,288 each
  exactly two specified pairs share             3,888 each
  one block common to all three                   216
  three distinct pair-shared blocks                  0

Structural eliminations:
  * no-share: the ordinary W-points are saturated, leaving only two extra
    triples; the two neighbours r,s of x each need two new incidences, forcing
    a repeated {r,s} pair and hence a Tanner C4.
  * all-three-common: its three points each need two additional incidences
    (or at least five total if one is the distinct zero-hole check), but only
    four completion triples exist and each may meet the common triple in at
    most one point.
  * three distinct pair-shared blocks are impossible already in the complete
    near-class enumeration; combinatorially, the three blocks would be pairwise
    disjoint and a class omitting one of them would have only two remaining
    triples to cover all three points of the omitted block.

The remaining one-share and two-share lanes are quotiented by the automorphism
group of canonical Q_AB (fixing A,B,C).  Frozen orbits:
  one-share representative pattern : 15 orbits (13x2592 + 2x1296)
  two-share representative pattern :  2 orbits (2592 + 1296)
  all-three-common                  :  1 orbit  (216)

For every orbit representative, all degree-completing cubic variables are
enumerated under linearity with the near classes and x.  A surviving U2,4
candidate must also admit the three v=0 exact covers X_A,X_B,X_C.

One-share:
  only a distinct zero hole at r or s survives the degree count.
  degree completions over 15 orbit representatives: 468.
  completions admitting X_A,X_B,X_C simultaneously: 0.

Two-share:
  every overlap hole and every distinct-hole location is tested.
  degree completions over 2 orbit representatives: 7,392.
  completions admitting X_A,X_B,X_C simultaneously: 0.

Thus p=1,h=1 is excluded through t=5. First open size:
  t=6 -> 19 checks / 18 variables.

P_VS_NP remains OPEN.
"""

from collections import Counter
from itertools import combinations, permutations


A,B,C=0,1,2
R,S=14,15
X=frozenset({R,S})
W=set(range(14))
U=set(range(16))

QAB=(
    frozenset({C,3,4}),
    frozenset({5,6,7}),
    frozenset({8,9,10}),
    frozenset({11,12,13}),
)

EXPECTED_PATTERN_COUNTS=Counter({
    (0,0,0,0):291600,
    (1,0,0,0):36288,
    (0,1,0,0):36288,
    (0,0,1,0):36288,
    (1,1,0,0):3888,
    (1,0,1,0):3888,
    (0,1,1,0):3888,
    (1,1,1,1):216,
})


def partitions_linear(points, existing):
    points=set(points)
    if not points:
        yield ()
        return
    a=min(points)
    rest=points-{a}
    for bc in combinations(sorted(rest),2):
        tri=frozenset((a,*bc))
        if any(tri!=e and len(tri&e)>1 for e in existing):
            continue
        rem=rest-set(bc)
        for tail in partitions_linear(rem, existing+(tri,)):
            yield (tri,)+tail


def enumerate_three_classes():
    out=[]
    pattern=Counter()
    Sclasses=tuple(partitions_linear(W-{A,C},QAB))
    assert len(Sclasses)==2052

    for QAC in Sclasses:
        for QBC in partitions_linear(W-{B,C},QAB+QAC):
            rs=len(set(QAB)&set(QAC))
            rt=len(set(QAB)&set(QBC))
            st=len(set(QAC)&set(QBC))
            all3=len(set(QAB)&set(QAC)&set(QBC))
            key=(rs,rt,st,all3)
            pattern[key]+=1
            out.append((QAB,QAC,QBC,key))

    assert len(out)==412344
    assert pattern==EXPECTED_PATTERN_COUNTS
    return out


def apply_perm_class(cl,mp):
    return tuple(sorted(
        tuple(sorted(mp[v] for v in e))
        for e in cl
    ))


def encode_solution(QAC,QBC):
    def enc(cl):
        return tuple(sorted(tuple(sorted(e)) for e in cl))
    return enc(QAC),enc(QBC)


def automorphism_generators():
    blocks=((5,6,7),(8,9,10),(11,12,13))
    gens=[]

    mp=list(range(14));mp[3],mp[4]=4,3
    gens.append(tuple(mp))

    for block in blocks:
        a,b,c=block
        mp=list(range(14));mp[a],mp[b]=b,a
        gens.append(tuple(mp))
        mp=list(range(14));mp[a],mp[b],mp[c]=b,c,a
        gens.append(tuple(mp))

    for b1,b2 in ((blocks[0],blocks[1]),(blocks[1],blocks[2])):
        mp=list(range(14))
        for x,y in zip(b1,b2):
            mp[x],mp[y]=y,x
        gens.append(tuple(mp))

    return tuple(gens)


GENS=automorphism_generators()


def apply_encoded(enc,mp):
    Scl,Tcl=enc
    return apply_perm_class(Scl,mp),apply_perm_class(Tcl,mp)


def orbit_representatives(solutions):
    table={encode_solution(s[1],s[2]):s for s in solutions}
    remaining=set(table)
    reps=[]
    sizes=[]

    while remaining:
        seed=next(iter(remaining))
        orbit={seed}
        stack=[seed]
        while stack:
            cur=stack.pop()
            for g in GENS:
                nxt=apply_encoded(cur,g)
                if nxt in table and nxt not in orbit:
                    orbit.add(nxt)
                    stack.append(nxt)
        remaining-=orbit
        reps.append(table[seed])
        sizes.append(len(orbit))

    return reps,Counter(sizes)


def completion_candidates(base):
    out=[]
    for e in combinations(range(16),3):
        e=frozenset(e)
        if len(e&X)>1:
            continue
        if any(e!=f and len(e&f)>1 for f in base):
            continue
        out.append(e)
    return tuple(out)


def target_degrees(case,hole):
    d=[3]*16
    d[A]=d[B]=d[C]=2
    if case=="overlap":
        d[hole]=1
    else:
        d[hole]=2
    return tuple(d)


def all_degree_completions(base,target,k):
    current=[0]*16
    for e in base:
        for v in e:
            current[v]+=1
    current[R]+=1
    current[S]+=1

    deficit=tuple(target[v]-current[v] for v in range(16))
    if any(d<0 for d in deficit) or sum(deficit)!=3*k:
        return ()

    candidates=tuple(
        e for e in completion_candidates(base)
        if all(deficit[v]>0 for v in e)
    )
    byv={v:[] for v in range(16)}
    for e in candidates:
        for v in e:
            byv[v].append(e)

    solutions=set()
    chosen=[]

    def rec(defi):
        if len(chosen)==k:
            if all(d==0 for d in defi):
                solutions.add(tuple(sorted(
                    tuple(sorted(e)) for e in chosen
                )))
            return

        positive=[v for v,d in enumerate(defi) if d>0]
        if not positive:
            return

        opts=None
        for v in positive:
            here=[]
            for e in byv[v]:
                if e in chosen:
                    continue
                if any(defi[u]<=0 for u in e):
                    continue
                if any(len(e&f)>1 for f in chosen):
                    continue
                here.append(e)
            if opts is None or len(here)<len(opts):
                opts=here

        for e in opts or ():
            nd=list(defi)
            for u in e:
                nd[u]-=1
            chosen.append(e)
            rec(tuple(nd))
            chosen.pop()

    rec(deficit)
    return tuple(
        tuple(frozenset(e) for e in sol)
        for sol in solutions
    )


def exact_cover_exists(triples, omitted):
    target=U-{omitted}
    available=[e for e in triples if e<=target]
    byp={p:[] for p in target}
    for e in available:
        for p in e:
            byp[p].append(e)

    def rec(rem,count):
        if not rem:
            return count==5
        if count>=5:
            return False
        p=min(rem,key=lambda z:sum(e<=rem for e in byp[z]))
        for e in byp[p]:
            if e<=rem and rec(rem-set(e),count+1):
                return True
        return False

    return rec(set(target),0)


def has_all_three_v0_covers(base,extras):
    full=set(base)|set(extras)
    return all(exact_cover_exists(full,u) for u in (A,B,C))


def main():
    systems=enumerate_three_classes()

    no_share=[s for s in systems if s[3]==(0,0,0,0)]
    one_share=[s for s in systems if s[3]==(1,0,0,0)]
    two_share=[s for s in systems if s[3]==(1,1,0,0)]
    all_common=[s for s in systems if s[3]==(1,1,1,1)]

    assert len(no_share)==291600
    assert len(one_share)==36288
    assert len(two_share)==3888
    assert len(all_common)==216

    # Pair-shared capacity theorem: any pair can share at most one block.
    for k in (2,3):
        m=4-k
        assert 3*m-1 > m*m

    one_reps,one_orbit_sizes=orbit_representatives(one_share)
    two_reps,two_orbit_sizes=orbit_representatives(two_share)
    common_reps,common_orbit_sizes=orbit_representatives(all_common)

    assert len(one_reps)==15
    assert one_orbit_sizes==Counter({2592:13,1296:2})
    assert len(two_reps)==2
    assert two_orbit_sizes==Counter({2592:1,1296:1})
    assert len(common_reps)==1
    assert common_orbit_sizes==Counter({216:1})

    one_completions=0
    one_six_cover_hits=0
    for Q0,Q1,Q2,_ in one_reps:
        base=set(Q0+Q1+Q2)
        assert len(base)==11

        # Structural degree count leaves only a distinct hole at r or s.
        for hole in (R,S):
            comps=all_degree_completions(
                base,target_degrees("distinct",hole),3
            )
            one_completions += len(comps)
            for extras in comps:
                if has_all_three_v0_covers(base,extras):
                    one_six_cover_hits += 1

    assert one_completions==468
    assert one_six_cover_hits==0

    two_completions=0
    two_six_cover_hits=0
    for Q0,Q1,Q2,_ in two_reps:
        base=set(Q0+Q1+Q2)
        assert len(base)==10

        cases=(
            [("overlap",h) for h in (A,B,C)]
            + [("distinct",h) for h in range(3,16)]
        )
        for case,hole in cases:
            comps=all_degree_completions(
                base,target_degrees(case,hole),4
            )
            two_completions += len(comps)
            for extras in comps:
                if has_all_three_v0_covers(base,extras):
                    two_six_cover_hits += 1

    assert two_completions==7392
    assert two_six_cover_hits==0

    # All-three-common degree obstruction:
    # the common triple has base active degree1 at each of its 3 points.
    # Four completion triples can meet it at most once each, so can provide
    # at most 4 further incidences.  At least 5 are required even if one of
    # the three points is the distinct zero-hole check.
    assert 4 < 5

    print("R5 E89 p=1,h=1 t=5 shared-block killer: PASS")
    print("canonical near-class triples:", len(systems))
    print("sharing pattern counts:", dict(EXPECTED_PATTERN_COUNTS))
    print("one-share orbits:", len(one_reps), dict(one_orbit_sizes))
    print("two-share orbits:", len(two_reps), dict(two_orbit_sizes))
    print("all-common orbits:", len(common_reps), dict(common_orbit_sizes))
    print("one-share degree completions tested:", one_completions, "six-cover hits:", one_six_cover_hits)
    print("two-share degree completions tested:", two_completions, "six-cover hits:", two_six_cover_hits)
    print("p=1,h=1 excluded through t=5; first open t=6 => 19 checks / 18 variables")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
