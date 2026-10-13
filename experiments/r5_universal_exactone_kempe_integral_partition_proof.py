#!/usr/bin/env python3
"""Pure Python exact all-state Kempe-hypercube partition challenge.

A stronger necessary condition than one-step existential Kempe closure
is that a fixed arbitrary colour-pair (A,B) partitions complete proper
interior edge-colourings into orbits of independently switchable paths.
If the boundary colouring multiplicity is chosen identically 1 for
EVERY target physical exact-one state, then the 108 boundary states
must admit an exact partition into admissible Kempe hypercubes for
each of the three pairs of colours. Our earlier exact rational LP
found w_s=1 feasible; this tests an integer exact-cover strengthening.

Uses no numpy/scipy. If a pure combinatorial partition is found,
the selected hypercubes are independently checked as an exact 108
state cover, each with a concrete 2-colour perfect matching witness.
Failure within a search guard is UNKNOWN, not a universal obstruction.
"""
from itertools import product
from collections import Counter
import hashlib
import json

PAIRS=((0,1),(0,2),(1,2))
TARGET={(1,0,0),(0,1,0),(0,0,1)}
STATES=tuple(s for s in product(range(3),repeat=6)
        if all(s.count(c)%2==0 for c in range(3))
        and tuple(int(s[i]==s[i+3]) for i in range(3)) in TARGET)
assert len(STATES)==108
IDX={s:i for i,s in enumerate(STATES)}
FULL=(1<<len(STATES))-1


def matchings(vertices):
    if not vertices:
        yield ()
        return
    first,*rest=vertices
    for i,other in enumerate(rest):
        for tail in matchings(rest[:i]+rest[i+1:]):
            yield ((first,other),)+tail


def orbit(s,a,b,pairs):
    out=set()
    for mask in range(1<<len(pairs)):
        x=list(s)
        for j,block in enumerate(pairs):
            if mask & (1<<j):
                for i in block:
                    x[i]=b if x[i]==a else a
        out.add(tuple(x))
    assert len(out)==1<<len(pairs)
    return frozenset(out)


def candidate_orbits(a,b):
    raw={}
    for s in STATES:
        inds=tuple(i for i,v in enumerate(s) if v in (a,b))
        for M in matchings(inds):
            O=orbit(s,a,b,M)
            if O<=IDX.keys():
                mask=sum(1<<IDX[t] for t in O)
                raw.setdefault(mask,(s,M))
    assert len(raw)==42,len(raw)
    return tuple(sorted(raw.items(),key=lambda x:(x[0].bit_count(),x[0])))


def exact_cover(orbits):
    allm=[x[0] for x in orbits]
    touches=[[] for _ in range(108)]
    for i,m in enumerate(allm):
        for v in range(108):
            if m>>v & 1:
                touches[v].append(i)
    explored=[0]
    exhausted=set()
    def rec(uncovered):
        explored[0]+=1
        if explored[0]>250000:
            raise RuntimeError("UNKNOWN_RESOURCE_LIMIT exact cover DFS")
        if uncovered==0:
            return []
        if uncovered in exhausted:
            return None
        best=None
        for s in range(108):
            if not (uncovered>>s & 1):
                continue
            choices=[j for j in touches[s]
                     if allm[j] & uncovered == allm[j]]
            if not choices:
                exhausted.add(uncovered)
                return None
            if best is None or len(choices)<len(best):
                best=choices
                if len(choices)==1:
                    break
        for j in best:
            remainder=uncovered ^ allm[j]
            sol=rec(remainder)
            if sol is not None:
                return [j]+sol
        exhausted.add(uncovered)
        return None
    chosen=rec(FULL)
    return chosen,explored[0]


def check_part(a,b,orbits,indices):
    assert indices is not None
    covered=0
    size_counts=Counter()
    for j in indices:
        bitset,(s,M)=orbits[j]
        assert not covered&bitset
        covered |= bitset
        O=orbit(s,a,b,M)
        assert set(IDX[t] for t in O)==set(i for i in range(108) if bitset>>i &1)
        size_counts[len(O)]+=1
    assert covered==FULL
    return size_counts


def main():
    solution=[]
    for a,b in PAIRS:
        orbits=candidate_orbits(a,b)
        selected,visits=exact_cover(orbits)
        if selected is None:
            print("INTEGER_ORBIT_PARTITION=NOT_FOUND",a,b,
                  "visited",visits)
            print("Do not infer impossibility of sixpole; rational cone still feasible")
            continue
        histogram=check_part(a,b,orbits,selected)
        print("EXACT_INTEGER_PARTITION_PASS",{"colors":(a,b),
              "orbits_total":len(orbits),
              "selected":len(selected),"sizes":dict(histogram),
              "dfs_nodes":visits},flush=True)
        # The indices and orbit defs reconstruct exact toggling witnesses.
        indices=sorted(selected)
        solution.append({"colors":[a,b],"selected":indices})
        print("SELECTED_ORBIT_INDICES",a,b,indices,flush=True)
    if len(solution)==3:
        data=json.dumps(solution,sort_keys=True,separators=(",",":")).encode()
        print("ALL_THREE_COLOUR_PAIRS_UNIT_COUNTS_EXACT_PARTITION=PASS")
        print("ORBIT_PARTITION_CERT_SHA256",hashlib.sha256(data).hexdigest())
    else:
        print("ALL_THREE_INTEGER_PARTITION_STATUS=UNRESOLVED")
    print("GADGET_EXISTENCE=OPEN; UNIVERSAL_PC_BACKSIM=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
