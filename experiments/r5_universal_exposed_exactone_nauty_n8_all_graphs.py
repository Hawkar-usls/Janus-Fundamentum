#!/usr/bin/env python3
"""Exact non-isomorphic simple connected 8-vertex open-sixpole survey.

Input graphs generated exhaustively by Brendan McKay's nauty geng:
    nauty-geng -cq -d1 -D3 8 9
(where m=(3*n-6)/2). Isomorphism-free interior graph generation;
for EACH representative, enumerate all proper 3-edge-colourings,
all missing-colour orientations at degree-1 vertices, ALL 15
labelled ways to partition six external semiedges into pairs.
A graph is skipped ONLY if its full port relation is empty;
no positives are assumed. Source full boundary labels matter.

The exact bit relation sought is {100,010,001}, where each bit
is 1 iff corresponding pair's physical 3-edge colours are equal.
Positive candidates are printed with graph6, edges, pairing
and all port-colour signatures for independently checking.
"""
import itertools
import shutil
import subprocess
from collections import Counter

TARGET=frozenset(((1,0,0),(0,1,0),(0,0,1)))


def pairings(items):
    if not items:
        yield ()
        return
    first=items[0]
    for j in range(1,len(items)):
        second=items[j]
        for tail in pairings(items[1:j]+items[j+1:]):
            yield ((first,second),)+tail


PAIRS=tuple(pairings(tuple(range(6))))
assert len(PAIRS)==15


def graph6_edges(line):
    line=line.strip()
    assert line and not line.startswith(">>")
    nums=[ord(c)-63 for c in line]
    n=nums[0]
    assert 2<=n<=12
    bits=[]
    for x in nums[1:]:
        bits.extend(((x>>s)&1 for s in (5,4,3,2,1,0)))
    edges=[]
    k=0
    # graph6 uses upper-triangle COLUMN order:
    # (0,1),(0,2),(1,2),(0,3),(1,3),(2,3), ...
    for w in range(1,n):
        for v in range(w):
            if bits[k]:
                edges.append((v,w))
            k+=1
    return n,tuple(edges)


def enumerate_port_signatures(n,edges):
    inc=[[] for _ in range(n)]
    for i,(v,w) in enumerate(edges):
        inc[v].append(i)
        inc[w].append(i)
    assert all(1<=len(row)<=3 for row in inc)
    assert sum(3-len(row) for row in inc)==6
    # Canonical port IDs are (vertex, local port slot).
    ports=tuple((v,j) for v in range(n)
                for j in range(3-len(inc[v])))
    assert len(ports)==6
    signatures=set()
    colouring=[-1]*len(edges)
    assignments=0
    def rec(i):
        nonlocal assignments
        if i==len(edges):
            assignments+=1
            choices=[]
            for v in range(n):
                chosen={colouring[j] for j in inc[v]}
                missing=tuple(c for c in range(3) if c not in chosen)
                assert len(missing)==3-len(inc[v])
                if missing:
                    choices.append(tuple(itertools.permutations(missing)))
            for blocks in itertools.product(*choices):
                signatures.add(tuple(c for block in blocks for c in block))
            return
        v,w=edges[i]
        for c in range(3):
            if any(colouring[j]==c for z in (v,w)
                   for j in inc[z] if j<i):
                continue
            colouring[i]=c
            rec(i+1)
            colouring[i]=-1
    rec(0)
    return ports,frozenset(signatures),assignments


def evaluate_pairings(signatures):
    relation_types=Counter()
    exact=[]
    for pairing in PAIRS:
        rel=frozenset(tuple(int(s[u]==s[v]) for u,v in pairing)
                      for s in signatures)
        relation_types[tuple(sorted(rel))]+=1
        if rel==TARGET:
            exact.append(pairing)
    return relation_types,exact


def run_case(n):
    m=(3*n-6)//2
    command=shutil.which("nauty-geng") or shutil.which("geng")
    if command is None:
        raise RuntimeError("nauty-geng absent: cannot certify exhaustive n=8")
    result=subprocess.run([command,"-c","-q","-d1","-D3",str(n),str(m)],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          check=True,text=True)
    graph_lines=[s for s in result.stdout.splitlines() if s and not s.startswith(">>")]
    assert len(graph_lines)==len(set(graph_lines)), "geng duplicate graph6"
    tally=Counter()
    relation_tally=Counter()
    examples=[]
    candidates=[]
    for g6 in graph_lines:
        nn,edges=graph6_edges(g6)
        assert nn==n and len(edges)==m
        deg=Counter(v for e in edges for v in e)
        assert all(1<=deg[v]<=3 for v in range(n))
        ports,signatures,assignments=enumerate_port_signatures(n,edges)
        tally["graphs"]+=1
        if not signatures:
            tally["uncolourable"]+=1
            continue
        tally["colourable"]+=1
        tally["proper_inner_assignments"]+=assignments
        rt,ex=evaluate_pairings(signatures)
        tally["tested_pairings"]+=15
        relation_tally.update(rt)
        if ex:
            for pairing in ex:
                candidates.append((g6,edges,ports,pairing,len(signatures),tuple(sorted(signatures))))
            print("EXACT_ONE_FOUND",n,g6,edges,ports,ex,flush=True)
        if len(examples)<3:
            examples.append((g6,edges,len(signatures),assignments))
    assert tally["graphs"]==len(graph_lines)
    assert tally["tested_pairings"]==15*tally["colourable"]
    assert sum(relation_tally.values())==tally["tested_pairings"]
    print("NAUTY_EXACT",{"n":n,"m":m,**tally},flush=True)
    print("RELATION_TYPES",{"count":len(relation_tally),
          "histogram":[(str(k),v) for k,v in relation_tally.most_common(25)]},flush=True)
    print("EXAMPLES",examples,flush=True)
    print("EXACT_ONE_COUNT",len(candidates),flush=True)
    for candidate in candidates[:5]:
        print("WITNESS",candidate,flush=True)
    return candidates,tally


def main():
    if not (shutil.which("nauty-geng") or shutil.which("geng")):
        raise RuntimeError("EXHAUSTIVE STATUS UNKNOWN: nauty-geng missing")
    # 4/6 sanity checks; this verifies graph6 parser, nauty enumeration.
    n4,_=run_case(4)
    n6,_=run_case(6)
    assert not n4 and not n6, "Contradicts previously frozen exhaustive n<=6"
    n8,_=run_case(8)
    if n8:
        print("OPEN_EXACTONE_8_FOUND: inspect frozen color-level witness")
    else:
        print("OPEN_EXACTONE_N<=8_NO_CANDIDATE: exact nauty classification")
    n10,_=run_case(10)
    if n10:
        print("OPEN_EXACTONE_N10_FOUND: needs independent certificate and native PC simulation")
    else:
        print("OPEN_EXACTONE_N<=10_NO_CANDIDATE: exact nauty classification")
    n12,_=run_case(12)
    if n12:
        print("OPEN_EXACTONE_N12_FOUND: needs independent certificate and native PC simulation")
    else:
        print("OPEN_EXACTONE_N<=12_NO_CANDIDATE: exact nauty classification")
    print("UNBOUNDED_NATIVE_GF3_PC_DEGREE=OPEN")
    print("UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
