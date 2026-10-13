#!/usr/bin/env python3
"""All n=14 simple connected sixpole EXPOSED EXACT-ONE candidates: exact proof scan.

Unlike the earlier full colour-relation n<=12 classifier, this script
allows rigorous early REJECTION. For each of the 15 boundary pairings,
ONE actual proper colouring with a forbidden bit tuple suffices to
exclude exact relation {100,010,001}; if no such witness is found, all
remaining 3-edge-colourings are exhaustively searched and missing
required 100/010/001 states are checked.

The first internal edge can be fixed to colour zero WLOG, because a
global colour permutation maps every 3-edge-colouring to such an
assignment and all equality-bit predicates are colour-invariant.
Thus anchored enumeration is complete for the target bit projection.
All 6 open ports are physical, distinct; two missing port colours at
a degree-one internal vertex get BOTH permutations.

Input: nauty-geng -cq -d1 -D3 14 18 (all connected simple graphs
of n=14 internal vertices, m=18 interior edges, up to isomorphism).
Streaming generation avoids large memory usage. All 15 pairings are
checked for every graph. A found candidate prints graph6, physical
port IDs, matching and all observed target bit states; independently
recheck with a full (non-anchored) source original colouring.
"""
import hashlib
import itertools
import shutil
import subprocess
import sys
from collections import Counter

ONEHOT_MASK=(1<<1)|(1<<2)|(1<<4)
ALL_MASK=(1<<8)-1


def all_pairings(items):
    if not items:
        yield ()
        return
    first,*remaining=items
    for j,other in enumerate(remaining):
        for tail in all_pairings(remaining[:j]+remaining[j+1:]):
            yield ((first,other),)+tail


PAIRINGS=tuple(all_pairings(list(range(6))))
assert len(PAIRINGS)==15
# Tiny static lookup: boundary base3 tuple to 3-bit encoded equalities.
SIGNATURE_BITS=[]
for digits in itertools.product(range(3),repeat=6):
    SIGNATURE_BITS.append(tuple(
        (int(digits[a]==digits[b])*4 +
         int(digits[c]==digits[d])*2 +
         int(digits[e]==digits[f]))
        for ((a,b),(c,d),(e,f)) in PAIRINGS))
assert len(SIGNATURE_BITS)==729


def graph6_decode(line):
    chars=[ord(x)-63 for x in line.strip()]
    assert chars and chars[0]==14,("not n14 graph6",line)
    bits=[]
    for x in chars[1:]:
        bits.extend((x>>s)&1 for s in (5,4,3,2,1,0))
    edges=[]
    j=0
    for v in range(1,14):
        for u in range(v):
            if bits[j]:
                edges.append((u,v))
            j+=1
    assert len(edges)==18
    return tuple(edges)


def code_base3(digits):
    # itertools.product enumerates lexicographically: first is most significant.
    acc=0
    for d in digits:
        acc=3*acc+d
    return acc


def graph_test(edges):
    n=14
    inc=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    assert all(1<=len(a)<=3 for a in inc)
    assert sum(3-len(a) for a in inc)==6
    port_slots=tuple((v,j) for v in range(n)
                     for j in range(3-len(inc[v])))
    assert len(port_slots)==6
    # 3^6 bounded per-node expansions due to missing-colour order at
    # degree1 vertices; no allocation proportional to graph count.
    colour=[-1]*len(edges)
    colour[0]=0
    mask=[0]*15
    witnessed_bad=[None]*15
    checked_assignments=0
    checked_port_tuples=0
    stopped_early=False

    def add_colour_state(port_tuple):
        nonlocal checked_port_tuples,stopped_early
        checked_port_tuples+=1
        sig=code_base3(port_tuple)
        bits=SIGNATURE_BITS[sig]
        for j,b in enumerate(bits):
            if witnessed_bad[j] is not None:
                continue
            mask[j]|=1<<b
            if b not in (1,2,4):
                witnessed_bad[j]=port_tuple
        if all(x is not None for x in witnessed_bad):
            stopped_early=True

    def recurse(i):
        nonlocal checked_assignments
        if stopped_early:
            return
        if i==len(edges):
            checked_assignments+=1
            choices=[]
            for ids in inc:
                free=tuple(c for c in range(3)
                           if c not in [colour[j] for j in ids])
                assert len(free)==3-len(ids)
                if free:
                    choices.append(tuple(itertools.permutations(free)))
            for chunks in itertools.product(*choices):
                boundary=tuple(x for chunk in chunks for x in chunk)
                assert len(boundary)==6
                add_colour_state(boundary)
                if stopped_early:
                    break
            return
        if colour[i]>=0:
            recurse(i+1)
            return
        u,v=edges[i]
        for c in (0,1,2):
            if any(colour[j]==c for w in (u,v)
                   for j in inc[w] if j<i):
                continue
            colour[i]=c
            recurse(i+1)
            colour[i]=-1
            if stopped_early:
                break

    recurse(0)
    if not checked_assignments:
        assert not stopped_early
        return "uncolourable",port_slots,None,checked_assignments,checked_port_tuples

    exact=[j for j in range(15)
           if witnessed_bad[j] is None and mask[j]==ONEHOT_MASK]
    if exact:
        assert not stopped_early
        return "candidate",port_slots,exact,checked_assignments,checked_port_tuples
    # If an interface has no forbidden witness, then all anchored
    # colourings were enumerated, and a required onehot bit was
    # absent. If some forbidden witness was seen, that alone rejects.
    for j in range(15):
        assert witnessed_bad[j] is not None or mask[j]!=ONEHOT_MASK
    return "rejected",port_slots,None,checked_assignments,checked_port_tuples


def main():
    command=shutil.which("nauty-geng") or shutil.which("geng")
    if not command:
        raise RuntimeError("Missing nauty-geng: exact n14 classification UNKNOWN")
    command=[command,"-c","-q","-d1","-D3","14","18"]
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,text=True)
    counts=Counter()
    dig=hashlib.sha256()
    candidates=[]
    for line in proc.stdout:
        if not line.strip() or line.startswith(">>"):
            continue
        g6=line.strip()
        dig.update((g6+"\n").encode("ascii"))
        edges=graph6_decode(g6)
        result,ports,matching,assignments,port_tuples=graph_test(edges)
        counts["graphs"]+=1
        counts["status_"+result]+=1
        counts["anchored_full_assignments_seen"]+=assignments
        counts["boundary_tuples_seen"]+=port_tuples
        if result=="candidate":
            candidates.append((g6,edges,ports,matching))
            print("N14_EXACTONE_CANDIDATE",candidates[-1],flush=True)
        if counts["graphs"]%10000==0:
            print("PROGRESS",dict(counts),flush=True)
    stderr=proc.stderr.read()
    assert proc.wait()==0,("nauty failed",stderr)
    assert counts["graphs"]>0 and counts["graphs"]==(
           counts["status_uncolourable"]+counts["status_candidate"]+
           counts["status_rejected"])
    print("N14_SUMMARY",dict(counts),flush=True)
    print("N14_GRAPH6_SHA256",dig.hexdigest(),flush=True)
    print("N14_CANDIDATE_COUNT",len(candidates),flush=True)
    for candidate in candidates[:15]:
        print("SOURCE_CANDIDATE",candidate,flush=True)
    if candidates:
        print("REQUIRES_INDEPENDENT_FULL_PHYSICAL_SIGNATURE_REPLAY")
        print("REQUIRES_CLOSED_NATIVE_SCL_SOURCE_AND_PC_BACKSIM")
    else:
        print("NO_OPEN_EXACTONE_N14_EXHAUSTIVE_FINITE_CENSUS")
    print("ANY_N_UNIVERSAL_NONEXISTENCE=OPEN")
    print("UNBOUNDED_NATIVE_PC_DEGREE=OPEN; SolveLinearCubicXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
