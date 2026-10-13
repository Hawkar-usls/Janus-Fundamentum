#!/usr/bin/env python3
"""Adversarial structured near-SAT legal SCL versus degree-three PC.

Start from an infinitely extendible SAT cubic-linear square family,
with three explicit residue-class satisfying assignments.
Exchange ONE incidence (column position) between two distinct rows,
preserving every column/row degree. Reject any exchange that violates
pairwise linearity/C4-free or Levi connectivity.

For EVERY accepted adversarial input, independently run exact
Boolean selected-column covering (sound+complete, exponential)
and then (if UNSAT) all-input GF(2) degree-3 PC span. On a true
UNSAT surviving PC3, compute and independently verify a DUAL
pseudoexpectation y with y(1)=1 and y(generator)=0.

Either return a small reproducible counterexample to the
UNIVERSAL CONSTANT-DEGREE-THREE COMPLETENESS THESIS, or report
an explicit NO-COUNTEREXAMPLE-IN-TESTS (NOT a theorem).
"""
from __future__ import annotations
import json
from itertools import combinations

from r5_universal_scl_random_pc3_dual_challenge import (
    exact_boolean_support,pc3_rank_and_dual,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def toroidal(L):
    assert L>=6 and L%3==0
    n=L*L
    rows=[]
    for i in range(L):
        for j in range(L):
            def site(a,b):return (a%L)*L+(b%L)
            rows.append(tuple(sorted((
                site(i,j),site(i+1,j),site(i,j+1)
            ))))
    witness={i*L+j for i in range(L) for j in range(L)
             if (i-j)%3==0}
    return n,tuple(rows),witness


def cyclic(n,a=1,b=5):
    assert n>=15 and n%3==0 and a%3==1 and b%3==2
    rows=tuple(tuple(sorted((i,(i+a)%n,(i+b)%n))) for i in range(n))
    return n,rows,{v for v in range(n) if v%3==0}


def connected(rows,n):
    adj=[set() for _ in range(n)]
    for a,b,c in rows:
        adj[a].update((b,c));adj[b].update((a,c));adj[c].update((a,b))
    seen={0};todo=[0]
    while todo:
        for v in adj[todo.pop()]:
            if v not in seen:seen.add(v);todo.append(v)
    return len(seen)==n


def checked_matrix(rows,n):
    if len(rows)!=n:return None
    seen=set()
    for row in rows:
        if len(row)!=3 or len(set(row))!=3:return None
        for pair in combinations(row,2):
            if pair in seen:return None
            seen.add(pair)
    if len(seen)!=3*n:return None
    if not connected(rows,n):return None
    return tuple(validate_sparse(rows,n))


def swaps(rows,n):
    """Deterministic single-incidence 2-switch preserving degrees."""
    for r,s in combinations(range(n),2):
        for a in rows[r]:
            for b in rows[s]:
                if a==b or a in rows[s] or b in rows[r]:continue
                nextrows=list(rows)
                nextrows[r]=tuple(sorted((set(rows[r])-{a})|{b}))
                nextrows[s]=tuple(sorted((set(rows[s])-{b})|{a}))
                # avoid the duplicate of reverse row and column choice
                if nextrows[r]==rows[r] or nextrows[s]==rows[s]:continue
                cand=checked_matrix(tuple(nextrows),n)
                if cand is not None:
                    yield (r,s,a,b),cand


def main():
    examined=0;legal=0;hard=0
    challenge_families=[
        ("TORUS_L6",toroidal(6),60),
        ("CYCLIC_N27",cyclic(27),60),
        ("CYCLIC_N33",cyclic(33),60),
    ]
    for name,(n,rows,known_witness),budget in challenge_families:
        rows=checked_matrix(rows,n)
        assert rows is not None
        assert len(known_witness)==n//3
        assert all(sum(v in known_witness for v in row)==1 for row in rows)
        print(f'{name}_BASE = SAT_WITH_EXPLICIT_WITNESS n={n}',flush=True)
        examined_family=0;unsat_family=0
        for mutation,challenger in swaps(rows,n):
            legal+=1
            witness,states=exact_boolean_support(challenger,n)
            examined+=1;examined_family+=1
            if witness is None:
                unsat_family+=1;hard+=1
                pc_refuted,dual,stats=pc3_rank_and_dual(challenger,n)
                print(f'NEAR_SAT_{name}: mutation={mutation}, '
                      f'UNSAT=True, PC3={"REFUTED" if pc_refuted else "INCONCLUSIVE"}, '
                      f'exact_states={states},rank={stats["rank"]}, '
                      f'dimension={stats["monomials"]}',flush=True)
                if not pc_refuted:
                    cert={
                      "schema":"JANUS-R5-PC3-STRUCTURED-UNSAT-DUAL-v1",
                      "n":n,"source":name,"mutation":list(mutation),
                      "rows":[list(r) for r in challenger],
                      "degree":3,"dual_bits_hex":hex(dual),
                      "dual_weight":dual.bit_count(),
                      "truth":"UNSAT_BY_EXACT_EXHAUSTION",
                      "pc3":"EXACT_INCONCLUSIVE_WITH_DUAL_CERTIFICATE",
                    }
                    print("PC3_STRUCTURED_COUNTEREXAMPLE_JSON="+json.dumps(
                        cert,sort_keys=True,separators=(',',':')),flush=True)
                    print('UNIVERSAL_FIXED_PC3_COMPLETENESS = REFUTED_FINITE_CERT',
                          flush=True)
                    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
                    print('P_VS_NP = OPEN')
                    return
                if unsat_family>=budget:break
            if examined_family>=max(budget*5,500):break
        print(f'{name}_AUDIT: legal_tested={examined_family}, '
              f'UNSAT_tested={unsat_family}, all_UNSAT_PC3_refuted=True',
              flush=True)
    print(f'NO_STRUCTURED_PC3_COUNTEREXAMPLE_FOUND: legal={legal} '
          f'full_oracle_queries={examined} UNSAT_pc3_refuted={hard}',flush=True)
    print('UNIVERSAL_FIXED_PC3_COMPLETENESS = STILL_OPEN')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
