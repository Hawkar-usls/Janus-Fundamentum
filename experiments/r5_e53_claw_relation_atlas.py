#!/usr/bin/env python3
"""Exhaustive local claw-relation atlas for R5 E53.

A conflict vertex has three source-pairs of neighbors.  A claw chooses one endpoint
from each pair, hence is a bit vector in {0,1}^3.  There are 12 possible cross-pair
edges; each forbids one 2-bit pattern.  Exhaust all 2^12 local cross-edge graphs,
collect distinct claw families, impose the post-E52 coordinate-surjectivity condition,
and quotient by cube symmetries (S3 coordinate permutations and independent bit flips).

Expected exact counts:
  166 distinct claw families total;
  103 post-E52 coordinate-surjective families;
  8 cube-symmetry orbits with sizes 2,3,4,4,4,5,6,8.
"""
import itertools
from collections import Counter, defaultdict

ASSIGN=list(itertools.product([0,1], repeat=3))
EDGES=[]
for i,j in itertools.combinations(range(3),2):
    for a in (0,1):
        for b in (0,1):
            EDGES.append(((i,a),(j,b)))


def family(mask):
    out=[]
    for z in ASSIGN:
        ok=True
        for k,((i,a),(j,b)) in enumerate(EDGES):
            if (mask>>k)&1 and z[i]==a and z[j]==b:
                ok=False; break
        if ok:
            out.append(z)
    return tuple(out)


def surjective(F):
    return bool(F) and all({z[i] for z in F}=={0,1} for i in range(3))


def transform(z,p,flip):
    return tuple(z[p[i]] ^ flip[i] for i in range(3))


def canonical(F):
    images=[]
    for p in itertools.permutations(range(3)):
        for flip in itertools.product([0,1], repeat=3):
            images.append(tuple(sorted(transform(z,p,flip) for z in F)))
    return min(images)


def main():
    fams={family(mask) for mask in range(1<<12)}
    assert len(fams)==166
    dist=Counter(map(len,fams))
    assert dist==Counter({3:48,4:44,2:28,5:24,6:12,1:8,8:1,0:1})

    post=[F for F in fams if surjective(F)]
    assert len(post)==103
    orbits=defaultdict(list)
    for F in post:
        orbits[canonical(F)].append(F)
    assert len(orbits)==8
    sizes=sorted(len(rep) for rep in orbits)
    assert sizes==[2,3,4,4,4,5,6,8]

    reps=sorted(orbits, key=lambda F:(len(F),F))
    print("R5 E53 claw-relation atlas: PASS")
    print("distinct_families=166")
    print("post_E52_families=103")
    print("cube_symmetry_orbits=8")
    for F in reps:
        print(f"size={len(F)} rep={F}")


if __name__=="__main__":
    main()
