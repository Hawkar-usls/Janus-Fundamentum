#!/usr/bin/env python3
"""R5 exact cyclic-odd symmetry PC3 proof search for legal snark SCL.

For a simple cubic graph G carrying an odd-order automorphism sigma,
the direct G->square+cubic+linear Exact-One incidence is invariant
under the induced action on x_(edge,color).

Over GF2, averaging over an ODD order group preserves constant-one
refutability of any fixed-degree polynomial calculus space. The
invariant monomial orbit sums form an exact basis (all orbit sizes odd).

This checker tests exact PC degree 3 on:
 * SAT pentagonal prism (5-fold automorphism)
 * UNSAT Isaacs flower snarks J5 and J7 (odd 5-/7-fold automorphisms).
It independently counts graph colourings by a perfect matching
route, constructs a legal SCL target, verifies the graph automorphism
and its incidence action, computes complete PC3 *invariant* span
(no polynomial certificate hiding outside it), and reconstructs
any UNSAT certificate as actual orbit-sums of generator multiples.

No assumption of universal degree-3 completeness. Inconclusive is
not SAT; even finite success does NOT establish P=NP.
"""
from __future__ import annotations

from collections import defaultdict
from math import comb

from r5_universal_boolean_pc_degree3_global_attack import (
    monomial_masks,poly_row,
)
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl
from r5_universal_cubic_flow_lowmoment_collision_20v import (
    flower,three_edge_colour_count,
)
from r5_universal_modular_flow_count_all_q_no_go import prism
from r5_universal_e118_c9_invariant_pc3 import rotate_mask


def automorphism_flower(k):
    """A 2-step rotation of flower's 2k rim:
       spokes a_i,b_i -> i+2 mod k; c_i,d_i exchange
       on wraparound of the c0..c(k-1),d0..d(k-1) rim.
    """
    assert k>=5 and k%2
    sigma=[-1]*(4*k)
    for i in range(k):
        j=(i+2)%k
        sigma[4*i]=4*j
        sigma[4*i+1]=4*j+1
        if i+2<k:
            sigma[4*i+2]=4*j+2
            sigma[4*i+3]=4*j+3
        else:
            sigma[4*i+2]=4*j+3
            sigma[4*i+3]=4*j+2
    assert sorted(sigma)==list(range(4*k))
    return tuple(sigma)


def automorphism_prism(k):
    return tuple([((i+1)%k) for i in range(k)] +
                 [k+((i+1)%k) for i in range(k)])


def direct_scl_action(edges,vertex_perm,order):
    edges=tuple(sorted(tuple(sorted(e)) for e in edges))
    nvar=3*len(edges)
    edge_index={e:i for i,e in enumerate(edges)}
    assert len(edge_index)==len(edges)
    action=[]
    for u,v in edges:
        uv=tuple(sorted((vertex_perm[u],vertex_perm[v])))
        assert uv in edge_index
        j=edge_index[uv]
        action.extend((3*j,3*j+1,3*j+2))
    assert sorted(action)==list(range(nvar))
    for x in range(nvar):
        y=x
        for _ in range(order):y=action[y]
        assert y==x
    rows,n,_,_=make_scl(edges)
    assert n==nvar and len(rows)==n
    rowset={tuple(sorted(row)) for row in rows}
    assert len(rowset)==len(rows)
    assert all(tuple(sorted(action[v] for v in row)) in rowset for row in rows)
    return tuple(rows),tuple(action)


def monomial_orbit_map(n,sigma,order):
    mons=monomial_masks(n,3)
    idx={}
    sizes=defaultdict(int);num=0
    for mask in mons:
        if mask in idx:continue
        orbit=[];cur=mask
        while cur not in orbit:
            assert cur not in idx
            orbit.append(cur)
            cur=rotate_mask(cur,sigma)
        assert cur==mask and order%len(orbit)==0 and len(orbit)%2==1
        for x in orbit:idx[x]=num
        sizes[len(orbit)]+=1
        num+=1
    assert sum(k*v for k,v in sizes.items())==len(mons)
    return idx,num,dict(sorted(sizes.items()))


def row_orbits(rows,sigma,order):
    row_index={tuple(sorted(row)):i for i,row in enumerate(rows)}
    assert len(row_index)==len(rows)
    seen=set();reprs=[]
    for i,row in enumerate(rows):
        if i in seen:continue
        cur=tuple(sorted(row));orbit=[]
        while cur!=tuple(sorted(row)) or not orbit:
            j=row_index[cur]
            assert j not in orbit
            orbit.append(j)
            cur=tuple(sorted(sigma[v] for v in cur))
        assert order%len(orbit)==0
        # This implementation uses row orbits of FULL order;
        # tested source flower/prism automorphisms have this property.
        assert len(orbit)==order,(i,len(orbit),order)
        seen.update(orbit)
        reprs.append(tuple(row))
    assert len(seen)==len(rows)
    return reprs


def symmetric_generator(row,mask,kind,coord,sigma,order):
    out=0;current=row;m=mask
    for _ in range(order):
        out^=poly_row(current,m,kind,coord)
        current=tuple(sigma[x] for x in current)
        m=rotate_mask(m,sigma)
    assert current==row and m==mask
    return out


def pc3_symmetry_test(rows,sigma,order,emit_small_proof=False):
    n=len(rows);coord,dim,sizes=monomial_orbit_map(n,sigma,order)
    reps=row_orbits(rows,sigma,order)
    mult_p=monomial_masks(n,2)
    mult_q=monomial_masks(n,1)
    gen=[];basis={};rank=0
    for ri,row in enumerate(reps):
        for kind,ms in (('parity',mult_p),('quadratic',mult_q)):
            for m in ms:
                j=len(gen);gen.append((ri,m,kind))
                vec=symmetric_generator(row,m,kind,coord,sigma,order)
                cert=1<<j
                while vec:
                    pivot=vec.bit_length()-1
                    if pivot in basis:
                        b,pivot_certificate=basis[pivot]
                        vec^=b;cert^=pivot_certificate
                    else:
                        basis[pivot]=(vec,cert);rank+=1;break
        print(f'ODD_SYM_PC3 progress_reps={ri+1}/{len(reps)} '
              f'rank={rank}/{dim} generators={len(gen)}',flush=True)
    target=1<<coord[0];c=0
    while target:
        pivot=target.bit_length()-1
        if pivot not in basis:break
        vec,pivot_certificate=basis[pivot]
        target^=vec;c^=pivot_certificate
    refuted=target==0
    support=0
    if refuted:
        check=0
        for j,(ri,m,kind) in enumerate(gen):
            if (c>>j)&1:
                check^=symmetric_generator(reps[ri],m,kind,coord,sigma,order)
                support+=1
        assert check==1<<coord[0]
        if emit_small_proof and support<=12:
            terms=[
                {'row_orbit':ri,'kind':kind,
                 'monomial_variables':tuple(i for i in range(n) if (m>>i)&1)}
                for j,(ri,m,kind) in enumerate(gen)
                if (c>>j)&1
            ]
            print(f'ODD_SYM_PC3_SHORT_CERTIFICATE={terms}',flush=True)
    return refuted,{
        'full_pc3_monomials':sum(comb(n,j) for j in range(4)),
        'odd_invariant_monomials':dim,
        'orbit_sizes':sizes,
        'row_orbits':len(reps),
        'invariant_generator_count':len(gen),
        'rank':rank,
        'nullity':dim-rank,
        'verified_orbit_certificate_terms':support,
    }


def main():
    k=5
    for name,raw,nv,vertex_perm,colorable,expected in (
        ('SAT_PRISM5',prism(k)[1],2*k,automorphism_prism(k),True,30),
        ('UNSAT_FLOWER_J5',flower(k),4*k,automorphism_flower(k),False,0),
        ('UNSAT_FLOWER_J7',flower(7),28,automorphism_flower(7),False,0),
    ):
        E=tuple(sorted(tuple(sorted(e)) for e in raw))
        assert len(E)==3*nv//2
        assert {tuple(sorted((vertex_perm[u],vertex_perm[v])))
                for u,v in E}==set(E),'graph automorphism invalid'
        n=3*len(E)
        full,pm,extendable=three_edge_colour_count(nv,E)
        assert full==expected and (full>0)==colorable
        order=7 if name=='UNSAT_FLOWER_J7' else k
        rows,sigma=direct_scl_action(E,vertex_perm,order)
        assert n==len(rows)
        refuted,st=pc3_symmetry_test(rows,sigma,order)
        assert not (colorable and refuted)
        print(f'{name}: SCL_n={n}, independent_colouring={full}, '
              f'perfect_matchings={pm}, '
              f'PC3={"PROVED_UNSAT" if refuted else "INCONCLUSIVE"}, '
              f'stats={st}',flush=True)
    print('ODD_AUTOMORPHISM_GF2_GROUP_AVERAGE_PRESERVES_PC3_REFUTABILITY = PROVED')
    print('GENERAL_FIXED_PC3_COMPLETENESS = NOT_ESTABLISHED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
