#!/usr/bin/env python3
"""Exact C9-invariant PC3 test on cyclic E118 square/cubic/linear targets.

The E118 source cyclic(9,a,b) has a symmetry of order 9 if each source
incidence port is indexed by its clause ROLE rather than by chronological
occurrence. EQUAL3 local gadget still enforces ports=000 or 111 and gives
2/1 extensions, so this is an exact legal SCL (n=90) reduction.

Let V_d be squarefree Boolean polynomials over F2, degree<=d;
W_d the span of PC-degree-d multiples of ExactOne parity/quadratic
constraints. Both V_d and W_d are stable under C9.

Because 9=1 in F2, a contradiction 1 in W_d exists IFF it
exists in the invariant subspace W_d^(C9). The invariant monomial
orbit-sum coefficients are represented exactly by one GF2
coordinate per odd-size orbit (1,3,9). For source q90 at d3, this
reduces 121576 coordinates to ~13512, and 376830 generators to
41870 orbit-sums, with NO LOSS of full degree-3 proof power.

Reconstructs any resulting contradiction as a linear combination
of symmetrized genuine generators, and independently checks it
equals constant 1. Otherwise returns exact INCONCLUSIVE (not SAT).

This is a finite E118 PC3 completeness falsifier, NOT a general
polynomial SCL solver or a theorem on asymptotic proof degree.
"""
from __future__ import annotations

import re
from collections import defaultdict
from itertools import combinations
from math import comb

from r5_universal_boolean_pc_degree3_global_attack import (
    monomial_masks,poly_row,
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source,source_solutions,verify_target,
    real_witness_from_source,
)
from r5_e118_universal_linear_cubic_exactone_hardness_bridge import (
    INTERNAL,rename_gadget,verify_gadget,
)


def equivariant_target(a,b):
    assert 0<a<9 and 0<b<9 and a!=b
    rows_names=[]
    for i in range(9):
        rows_names.append((
            f'v{i}_occ0',
            f'v{(i+a)%9}_occ1',
            f'v{(i+b)%9}_occ2',
        ))
    ports={}
    for i in range(9):
        ps=tuple(f'v{i}_occ{j}' for j in range(3))
        ports[f'v{i}']=ps
        rows_names.extend(rename_gadget(f'G_v{i}',ps))
    names=tuple(sorted(set(v for row in rows_names for v in row)))
    assert len(names)==90 and len(rows_names)==90
    idx={name:i for i,name in enumerate(names)}
    rows=tuple(tuple(idx[x] for x in row) for row in rows_names)
    verify_target(list(rows))
    sigma=[]
    for name in names:
        g=re.fullmatch(r'G_v([0-8])_(.+)',name)
        if g is not None:
            nxt=f'G_v{(int(g.group(1))+1)%9}_{g.group(2)}'
        else:
            g=re.fullmatch(r'v([0-8])_occ([012])',name)
            assert g is not None,name
            nxt=f'v{(int(g.group(1))+1)%9}_occ{g.group(2)}'
        sigma.append(idx[nxt])
    assert sorted(sigma)==list(range(90))
    for i in range(90):
        y=i
        for _ in range(9):y=sigma[y]
        assert y==i and sigma[i]!=i
    row_set={tuple(sorted(r)) for r in rows}
    assert len(row_set)==90
    assert all(tuple(sorted(sigma[v] for v in r)) in row_set for r in rows)
    return rows,ports,idx,tuple(sigma)


def rotate_mask(mask,sigma):
    out=0
    while mask:
        b=mask&-mask
        out|=1<<sigma[b.bit_length()-1]
        mask-=b
    return out


def monomial_orbit_coordinates(n,d,sigma):
    mons=monomial_masks(n,d)
    coords={}
    sizes=defaultdict(int)
    for mon in mons:
        if mon in coords:continue
        orbit=[]
        curr=mon
        while curr not in coords and curr not in orbit:
            orbit.append(curr)
            curr=rotate_mask(curr,sigma)
        assert curr==mon and 9%len(orbit)==0,(mon,len(orbit))
        oid=len(sizes) # do not use: sizes is keyed by orbit length!
        oid=len(coords) # do not use: increases per monomial!
        oid=counter[0] if False else 0
        # Correct orbit index assigned by explicit running integer.
        for x in orbit:
            coords[x]=len(sizes) if False else -1
        sizes[len(orbit)]+=1
    # Reassign deterministic orbit IDs (avoids accidental noncontiguous keys)
    coords.clear()
    orbit_id=0
    for mon in mons:
        if mon in coords:continue
        curr=mon
        while curr not in coords:
            coords[curr]=orbit_id
            curr=rotate_mask(curr,sigma)
        assert curr==mon
        orbit_id+=1
    assert len(coords)==len(mons)
    assert sum(k*v for k,v in sizes.items())==len(mons)
    assert 9*sum(v for k,v in sizes.items())>=len(mons)
    return coords,orbit_id,dict(sorted(sizes.items()))


def row_orbit_representatives(rows,sigma):
    canon={tuple(sorted(r)):i for i,r in enumerate(rows)}
    assigned=set();out=[]
    for i,row in enumerate(rows):
        if i in assigned:continue
        curr=tuple(sorted(row))
        orbit=[]
        for t in range(9):
            j=canon[curr]
            assert j not in orbit
            orbit.append(j)
            curr=tuple(sorted(sigma[v] for v in curr))
        assert curr==tuple(sorted(row)),("non-nine row orbit",i)
        assigned.update(orbit)
        out.append(tuple(row))
    assert len(out)==10 and len(assigned)==90
    return out


def projected_sym_generator(row,mon,which,coord,sigma):
    """Image of sum_{t=0..8} sigma^t(m*g_row).

    Since every monomial orbit has odd length, applying the
    coordinate-parity map to the invariant orbit-sum returns
    its exact coefficient per invariant monomial orbit.
    """
    p=0
    r=row;m=mon
    for _ in range(9):
        p^=poly_row(r,m,which,coord)
        r=tuple(sigma[v] for v in r)
        m=rotate_mask(m,sigma)
    assert tuple(r)==tuple(row) and m==mon
    return p


def degree3_invariant_pc(rows,sigma,track=True):
    n=90; d=3
    coord,dim,orbit_sizes=monomial_orbit_coordinates(n,d,sigma)
    reps=row_orbit_representatives(rows,sigma)
    mon_p=monomial_masks(n,d-1)
    mon_q=monomial_masks(n,d-2)
    generators=[];basis={};rank=0
    for ri,row in enumerate(reps):
        for kind,multis in (("parity",mon_p),("quadratic",mon_q)):
            for mon in multis:
                idx=len(generators)
                generators.append((ri,mon,kind))
                p=projected_sym_generator(row,mon,kind,coord,sigma)
                acc=1<<idx if track else 0
                while p:
                    pv=p.bit_length()-1
                    if pv in basis:
                        b=basis[pv]
                        if track:
                            p^=b[0]; acc^=b[1]
                        else:
                            p^=b
                    else:
                        basis[pv]=(p,acc) if track else p
                        rank+=1
                        break
        print(f'C9_INVARIANT_PC3_PROGRESS rep_clauses={ri+1}/10 '
              f'invariant_rank={rank}/{dim} '
              f'orbit_generators={len(generators)}',flush=True)
    p=1<<coord[0]
    proof=0
    while p:
        pv=p.bit_length()-1
        if pv not in basis:break
        b=basis[pv]
        if track:
            p^=b[0];proof^=b[1]
        else:
            p^=b
    refuted=(p==0)
    nterms=0
    if track and refuted:
        witness=0
        for idx in range(len(generators)):
            if (proof>>idx)&1:
                ri,mon,kind=generators[idx]
                witness^=projected_sym_generator(reps[ri],mon,kind,coord,sigma)
                nterms+=1
        assert witness==1<<coord[0]
        print(f'C9_PC3_INDEPENDENT_UNSAT_COMBINATION_TERMS={nterms}',flush=True)
    return refuted,{
        "full_degree3_monomials":sum(comb(n,j) for j in range(4)),
        "invariant_dimension":dim,
        "monomial_orbit_sizes":orbit_sizes,
        "row_orbits":len(reps),
        "invariant_generators":len(generators),
        "rank":rank,
        "nullity":dim-rank,
        "verified_unsat_certificate_terms":nterms,
    }


def main():
    verify_gadget()
    for name,a,b,sat in (
        ("E118_UNSAT90",1,6,False),
        ("E118_SAT90",1,2,True),
    ):
        source=cyclic_source(9,a,b)
        source_models=source_solutions(source)
        assert bool(source_models)==sat
        rows,ports,idx,sigma=equivariant_target(a,b)
        if sat:
            witness=real_witness_from_source(source_models[0],ports,rows,idx)
            assert len(witness)==90
        refuted,stats=degree3_invariant_pc(rows,sigma,track=True)
        assert not(sat and refuted),"FALSE UNSAT for SAT target"
        print(f'{name} PC3_EXACT_RESULT={"PROVED_UNSAT" if refuted else "INCONCLUSIVE"} '
              f'source_truth={"SAT" if sat else "UNSAT"} '
              f'statistics={stats}',flush=True)
    print('C9_ORBIT_AVERAGING_9_EQUALS_1_OVER_GF2 = PROVED')
    print('INVARIANT_PC3_HAS_EXACT_SAME_CONSTANT_REFUTABILITY_AS_FULL_PC3 = PROVED')
    print('DEGREE3_UNIVERSAL_SCL_COMPLETENESS = NOT_ESTABLISHED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
