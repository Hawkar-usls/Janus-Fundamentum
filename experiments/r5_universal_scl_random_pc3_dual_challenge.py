#!/usr/bin/env python3
"""Adversarial ALL-SCL (not just cubic-graph) PC3 completeness test.

Generate exact legal square+cubic+linear (C4-free) positive 1-in-3
SAT matrices A=I+P+Q from deterministic random permutations.
For each candidate:
 (1) exact complete, independently written branch-and-propagate solver;
 (2) full GF2 degree-3 Polynomial Calculus row-span test;
 (3) on a TRUE UNSAT where PC3 is INCONCLUSIVE, construct a DUAL
     degree-3 pseudoexpectation y, and verify y(1)=1 and
     y(m*p_clause)=y(m*q_clause)=0 for every tested generator.

Such a witness is a finite certificate that PC3 cannot refute this
specific UNSAT *legal SCL* instance; it does NOT imply a general
lower bound for arbitrary algorithms and does NOT solve P vs NP.

All counters can run on graph-unstructured LEGAL SCL matrices,
not only the Holyer 3-edge-colouring image.
"""
from __future__ import annotations
import json,random,hashlib
from collections import Counter
from functools import lru_cache
from itertools import combinations
from math import comb

from r5_universal_boolean_pc_degree3_global_attack import (
    monomial_masks,poly_row,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def legal_matrix(n,seed):
    rng=random.Random(seed+1000003*n)
    p=list(range(n));q=list(range(n))
    rng.shuffle(p);rng.shuffle(q)
    rows=[]
    seen=set()
    for i in range(n):
        clause=tuple(sorted((i,p[i],q[i])))
        if len(set(clause))<3:return None
        for pair in combinations(clause,2):
            if pair in seen:return None
            seen.add(pair)
        rows.append(clause)
    # ensure connected primal graph (exclude trivial component padding)
    adj=[set() for _ in range(n)]
    for a,b,c in rows:
        adj[a].update((b,c))
        adj[b].update((a,c))
        adj[c].update((a,b))
    seen_v={0};stack=[0]
    while stack:
        for v in adj[stack.pop()]:
            if v not in seen_v:
                seen_v.add(v);stack.append(v)
    if len(seen_v)!=n:return None
    normalized=tuple(tuple(r) for r in validate_sparse(rows,n))
    assert len(normalized)==n
    return normalized


def exact_boolean_support(rows,n):
    """Complete exact cover search; the finite ground truth oracle is
    exponential worst-case. Caches labelled selected-clause masks."""
    covering=[0]*n
    for ci,row in enumerate(rows):
        for v in row:covering[v]|=1<<ci
    assert all(x.bit_count()==3 for x in covering)
    full=(1<<n)-1
    visited=[0]
    @lru_cache(maxsize=None)
    def rec(done):
        visited[0]+=1
        if done==full:return ()
        best=None
        for ci,row in enumerate(rows):
            if (done>>ci)&1:continue
            avail=tuple(v for v in row if not (covering[v]&done))
            if not avail:return None
            if best is None or len(avail)<len(best):
                best=avail
                if len(best)==1:break
        assert best is not None
        for v in best:
            tail=rec(done|covering[v])
            if tail is not None:return (v,)+tail
        return None
    witness=rec(0)
    if witness is not None:
        selected=set(witness)
        assert len(selected)==n//3 and all(sum(v in selected for v in row)==1 for row in rows)
    return witness,visited[0]


def pc3_rank_and_dual(rows,n):
    d=3
    mons=monomial_masks(n,d)
    pos={mon:i for i,mon in enumerate(mons)}
    pm=monomial_masks(n,d-1)
    qm=monomial_masks(n,d-2)
    basis={}
    generators=0
    for row in rows:
        for kind,ms in (("parity",pm),("quadratic",qm)):
            for m in ms:
                generators+=1
                vec=poly_row(row,m,kind,pos)
                while vec:
                    pivot=vec.bit_length()-1
                    if pivot in basis: vec^=basis[pivot]
                    else:
                        basis[pivot]=vec
                        break
    refuted=0 in basis
    stats={"n":n,"degree":d,"monomials":len(mons),
           "rank":len(basis),"generators":generators,
           "zero_polynomial_in_span":refuted}
    if refuted:return True,None,stats
    # Fully independent dual *non-refutation* certificate:
    # choose free coefficient y[constant]=1 and all other free
    # coordinates 0; recursively solve each pivot equation.
    dual=1
    for p in sorted(basis):
        assert p!=0
        if (basis[p]&dual).bit_count()%2:dual|=1<<p
    assert dual&1
    assert all((v&dual).bit_count()%2==0 for v in basis.values())
    # Independently re-evaluate EVERY original generator with dual.
    audited=0
    for row in rows:
        for kind,ms in (("parity",pm),("quadratic",qm)):
            for m in ms:
                vec=poly_row(row,m,kind,pos)
                assert (vec&dual).bit_count()%2==0
                audited+=1
    assert audited==generators
    stats["dual_weight"]=dual.bit_count()
    stats["dual_sha256"]=hashlib.sha256(
        dual.to_bytes((dual.bit_length()+7)//8,"little")
    ).hexdigest()
    return False,dual,stats


def main():
    observations=Counter()
    accepted=0
    searched=0
    best=None
    # First probe n=24,30,36; no subclass assumption.
    for n,need in ((24,12),(30,20),(36,15)):
        count=0
        for seed in range(150000):
            searched+=1
            rows=legal_matrix(n,seed)
            if rows is None:continue
            count+=1;accepted+=1
            witness,states=exact_boolean_support(rows,n)
            truth="SAT" if witness is not None else "UNSAT"
            observations[(n,truth)]+=1
            if witness is None:
                refuted,dual,stats=pc3_rank_and_dual(rows,n)
                pc3status="REFUTED" if refuted else "INCONCLUSIVE"
                observations[(n,pc3status)]+=1
                print(f'ADVERSARIAL_SCL n={n} seed={seed} truth={truth} '
                      f'pc3={pc3status} exact_states={states} stats={stats}',
                      flush=True)
                if not refuted:
                    best=(n,seed,rows,dual,stats)
                    break
            elif count<=2:
                print(f'ADVERSARIAL_SCL n={n} seed={seed} truth=SAT '
                      f'exact_states={states}',flush=True)
            if count>=need:break
        if best is not None:break
        assert count>=need,(n,count)
    print(f'ADVERSARIAL_COUNTS searched={searched} accepted={accepted} '
          f'observations={dict((str(k),v) for k,v in observations.items())}',
          flush=True)
    if best is not None:
        n,seed,rows,dual,stats=best
        fixture={
            "schema":"JANUS-R5-SCL-PC3-DUAL-NONREFUTATION-v1",
            "n":n,"seed":seed,"rows":[list(r) for r in rows],
            "degree":3,"dual_bits_le_hex":hex(dual),
            "dual_weight":dual.bit_count(),"verified":True,
            "scientific_status":"TRUE_UNSAT_AND_PC3_INCONCLUSIVE",
            "solver_status":"UNIVERSAL_POLY_NOT_CONSTRUCTED",
        }
        print("EXACT_PC3_LEGAL_SCL_COUNTEREXAMPLE_JSON="+json.dumps(
            fixture,sort_keys=True,separators=(',',':')),flush=True)
        print('UNIVERSAL_FIXED_DEGREE_3_PC_COMPLETENESS = REFUTED_FINITE_CERT',
              flush=True)
    else:
        print('UNIVERSAL_FIXED_DEGREE_3_PC_COMPLETENESS = UNRESOLVED_NO_COUNTEREXAMPLE_IN_SAMPLE',
              flush=True)
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
