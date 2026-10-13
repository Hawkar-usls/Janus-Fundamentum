#!/usr/bin/env python3
"""R5 all-size fixed-port GF(2)^2 LINEAR ENVELOPE for colour fibres.

For any connected cubic sixpole with six DISTINCT semiedge roots, fix
an ordered physical port colour tuple s, and suppose at least one full
proper 3-edge-colouring c0 extending s is given.

For any other full proper colouring c extending exactly s, the
difference D_e = code(c_e) XOR code(c0_e), with code 0->1, 1->2,
2->3 in F2^2, belongs to the polynomial-time computable linear space:

Z_s = {D over F2^2 on ordinary interior edges :
       partial D = 0 at every cubic vertex,
       D_e in span_F2(code(s_i)) for each port-root incident edge e }.

At a semiedge root two ordinary incident edges have equal D by
partial D=0. Since the fixed semiedge colour is a, the only possible
swaps of the other two colours are identity or their interchange;
therefore D on either ordinary edge is 0 or code(a).

The map c -> (c XOR c0) injects the colour fibre into Z_s, so
|Fibre(s)| <= 2^(dim Z_s).
The dimension is obtained by Gaussian elimination over F2 on O(n)
variables and equations, in polynomial time. This is ONLY an upper
bound conditional on a witness; it is not a polynomial algorithm for
finding the witness or counting the fibre.

Independent exhaustive n=8 check (fixed ordered ports 001212):
1472 labelled simple connected reference colourings, with
dim(Z_s)=0 for 1072 (all fibre size 1), dim(Z_s)=1 for 400
(240 fibre size 1, 160 fibre size 2).
No n>=18 theorem or P=NP result follows.
"""
from collections import Counter
from itertools import product
from r5_kempe_physical_fiveloop_gf4_flow_witness import (
    COLOURS, PORTS, REFERENCE_C,
    WITNESS_EDGES, GIRTH6_EDGES,
    matching, connected, check_colouring, fibre_at_fixed_ports,
)


def binary_rank(rows):
    pivots = {}
    for r in rows:
        while r:
            j = r.bit_length()-1
            if j in pivots:
                r ^= pivots[j]
            else:
                pivots[j] = r
                break
    return len(pivots)


def linear_envelope(edges, port_roots, port_colours):
    """Return (dimension, constraint bitsets), independent of c0."""
    assert len(port_roots) == len(port_colours) == 6
    assert len(set(port_roots)) == 6
    assert len(set(edges)) == len(edges)
    V = sorted(set(port_roots) | {w for edge in edges for w in edge})
    assert V == list(range(len(V))), "normalise vertices to 0..n-1"
    n, m = len(V),len(edges)
    assert 2*m + 6 == 3*n
    incident=[[] for _ in V]
    for k,(u,v) in enumerate(edges):
        assert 0<=u<v<n
        incident[u].append(k);incident[v].append(k)
    for v in V:
        assert len(incident[v]) + int(v in port_roots) == 3
    # F2^2 divergence zero: one row for each vertex and each bit.
    rows=[]
    for v in V:
        for coord in (0,1):
            rows.append(sum(1<<(2*j+coord) for j in incident[v]))
    # At each root an additional one-dimensional-line constraint:
    # a=0 (code 01) -> D coord1 = 0; a=1 (code 10) -> coord0=0;
    # a=2 (code 11) -> coord0 xor coord1 =0.
    for v,c in zip(port_roots,port_colours):
        e=incident[v][0]
        if c==0:
            rows.append(1 << (2*e+1))
        elif c==1:
            rows.append(1 << (2*e))
        else:
            assert c==2
            rows.append((1<<(2*e)) | (1<<(2*e+1)))
    dimension=2*m-binary_rank(rows)
    assert 0<=dimension<=n-4
    return dimension, rows


def verify_difference(rows, first, other):
    codes=(1,2,3)
    D=[codes[a]^codes[b] for a,b in zip(first,other)]
    encoded=sum((d & 1)<<(2*j) | ((d>>1)&1)<<(2*j+1)
                for j,d in enumerate(D))
    assert all((encoded & row).bit_count()%2==0 for row in rows)
    return encoded


def test():
    reference_roots=tuple(range(6))
    assert linear_envelope(WITNESS_EDGES,reference_roots,PORTS)[0]==1
    assert linear_envelope(GIRTH6_EDGES,reference_roots,PORTS)[0]==1
    match_by_colour={
        c:tuple(matching(tuple(v for v in range(8)
                 if v>=6 or PORTS[v]!=c)))
        for c in COLOURS
    }
    assert all(len(x)==15 for x in match_by_colour.values())
    counts=Counter()
    for a,b,c in product(match_by_colour[0],match_by_colour[1],
                         match_by_colour[2]):
        edges=a+b+c
        if len(set(edges))<9 or not connected(edges):
            continue
        check_colouring(edges,REFERENCE_C,PORTS)
        d,rows=linear_envelope(edges,reference_roots,PORTS)
        fibre=fibre_at_fixed_ports(edges,PORTS)
        assert REFERENCE_C in fibre
        assert 1<=len(fibre)<=2**d
        for full in fibre:
            verify_difference(rows,REFERENCE_C,full)
        if d==0: assert fibre==[REFERENCE_C]
        counts[(d,len(fibre))]+=1
    assert counts==Counter({(0,1):1072,(1,1):240,(1,2):160}),counts
    print('N8_GF4_FIXED_PORT_LINEAR_ENVELOPE',dict(sorted(counts.items())),flush=True)
    print('THEOREM: SAME_BOUNDARY_COLOURINGS_INJECT_TO_POLYTIME_COMPUTABLE_Z_s')
    print('BOUND: |Fibre(s)| <= 2**dim(Z_s) <= 2**(n-4)')
    print('DIM0_PLUS_REFERENCE_WITNESS_IS_SINGLETON_NOT_GENERIC_SAT')
    print('SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN')


if __name__=='__main__':
    test()
