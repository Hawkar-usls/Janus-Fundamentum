#!/usr/bin/env python3
"""Exact sixpole <=> triple heterochromatic single-pair closures plus no 000.

A 6-pole M has labelled ports 0..5, partitioned into 3 couples.
Bit_i = 1 iff the two semiedges of couple_i have SAME physical colour.
Cubic sixpole parity forbids exactly two true bits (110,101,011).

Theorem, ALL SIZES:
Exact physical projected relation {100,010,001} iff:
  (A) for each i, colourings with couple_i equal are NONEMPTY,
      and in ALL such colourings both other couples are different.
      Equivalently, the 4-pole after joining the semiedges of
      couple_i into a single edge is colourable and HETEROCHROMATIC
      with respect to the other two port pairs; AND
  (B) no 3-edge-colouring of M has pair-equality triple 000.
This equivalence is elementary and does NOT provide an existence proof.

This script exhausts *all* six-port physical colour tuples of all
nonisomorphic simple connected interiors of 4,6,8,10,12 vertices,
and every 15 pairing. Count cases with all three independently
heterochromatic closures, and classify 000/111 completions. Uses
nauty-geng exactly; no hidden sampling; n14 is tested independently.
"""
from collections import Counter
from itertools import combinations
import shutil
import subprocess

from r5_universal_exposed_exactone_nauty_n8_all_graphs import (
    graph6_edges,enumerate_port_signatures,PAIRS,
)

ONEHOT={(1,0,0),(0,1,0),(0,0,1)}
EXACT_BIT_RESTRICTED=ONEHOT|{(0,0,0)}


def signed_bits(ports,pairs):
    return tuple(int(ports[a]==ports[b]) for a,b in pairs)


def evaluate_boundary(S,pairs):
    R={signed_bits(s,pairs) for s in S}
    # Check parity restriction as a source-independent invariant.
    assert not any(sum(b)==2 for b in R)
    closures=[]
    for i in range(3):
        # The one-edge joining glue is legal precisely when paired
        # terminal colours are identical.
        fiber={b for b in R if b[i]==1}
        closures.append(bool(fiber) and all(
            all(b[j]==0 for j in range(3) if j!=i)
            for b in fiber
        ))
    triples=all(closures)
    nozero=(0,0,0) not in R
    assert (R==ONEHOT)==(triples and nozero),(
        "all-size closure lemma violated",pairs,R,triples,nozero)
    return R, triples, nozero


def check_size(n):
    geng=shutil.which("nauty-geng") or shutil.which("geng")
    if geng is None:
        raise RuntimeError("nauty-geng missing: exhaustive status UNKNOWN")
    m=(3*n-6)//2
    p=subprocess.run([geng,"-c","-q","-d1","-D3",str(n),str(m)],
                    check=True,capture_output=True,text=True)
    ctr=Counter()
    for line in p.stdout.splitlines():
        if not line or line.startswith(">>"):
            continue
        nn,E=graph6_edges(line)
        assert nn==n and len(E)==m
        _,states,assignments=enumerate_port_signatures(n,E)
        ctr["graphs"]+=1
        if not states:
            ctr["uncolourable"]+=1
            continue
        for pairs in PAIRS:
            R, triple, nozero=evaluate_boundary(states,pairs)
            ctr["examined_pairings"]+=1
            if triple:
                ctr["triple_heterochromatic_closures"]+=1
                assert ONEHOT <= R and (1,1,1) not in R
                if (0,0,0) in R:
                    ctr["triple_closures_but_zero_remains"]+=1
                if nozero:
                    ctr["EXACTONE"]+=1
            if nozero:
                ctr["no_000"]+=1
    assert ctr["examined_pairings"]==15*(
        ctr["graphs"]-ctr["uncolourable"])
    assert ctr["triple_heterochromatic_closures"]==(
        ctr["triple_closures_but_zero_remains"]+ctr["EXACTONE"])
    assert ctr["EXACTONE"]==0,("FOUND GADGET",n,ctr)
    print("EXACT_SINGLE_CLOSE",n,dict(ctr),flush=True)
    return ctr


def main():
    total=Counter()
    for n in (4,6,8,10,12):
        z=check_size(n)
        total.update(z)
    assert total["graphs"]==6366, total
    assert total["examined_pairings"]==94065, total
    print("ALL_N<=12",dict(total),flush=True)
    print("PROVED_ALL_N: EXACTONE <=> 3 HETEROCHROMATIC")
    print(" SINGLE-EDGE COUPLE CLOSURES + NO_000")
    print("NO EXACTONE N<=12 is FINITE; all-size existence OPEN")
    print("No PC transfer or universal solver constructed; P vs NP OPEN")


if __name__=="__main__":
    main()
