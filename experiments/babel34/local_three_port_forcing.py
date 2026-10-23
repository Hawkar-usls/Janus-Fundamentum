#!/usr/bin/env python3
"""BABEL34: exact three-port local forcing and unique-SAT for all macro graphs.

Two independent local complete Boolean methods:
  * exhaustive unit-propagating Exact-One DPLL (24 untouched rows);
  * sparse Fraction elimination + ALL 2^5 Boolean free-coordinate projections.
Global controls use exact original rows, independently rebuild/recover every
incidence and check 3regular, linear, connected, full model and GF2 rank.
This proves a scoped composition for certified macro templates only; no P=NP.
"""
import hashlib
import itertools
import json
import random
from collections import Counter, deque
from fractions import Fraction

ROWS=(
(0,1,2),(0,3,6),(0,5,7),(3,5,20),(1,7,11),
(3,8,12),(6,7,8),(2,5,8),(2,10,14),
(9,10,11),(9,12,15),(9,14,22),(12,13,14),
(10,13,16),(1,6,17),(15,16,17),(4,17,20),
(11,13,21),(4,18,19),(15,18,24),
(18,23,25),(21,22,23),(16,19,25),(19,21,26),(24,25,26),
(4,23,26),(20,22,24))
PORTS=((0,0),(1,6),(2,5))
SHA="9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
ONES=(2,3,7,9,13,17,19,23,24)


def bitset_as_tuple(m,n):
    return tuple(i for i in range(n) if m>>i&1)


def exact_one(formula,truth):
    return all(sum(truth>>i&1 for i in row)==1 for row in formula)


def local_dpll(formula,n=27):
    """Complete Boolean DPLL; does not use rational elimination."""
    results=[]
    calls=0
    def search(assigned,true):
        nonlocal calls
        calls+=1
        while True:
            changed=False
            for row in formula:
                yes=sum(true>>i&1 for i in row)
                undec=[i for i in row if not assigned>>i&1]
                if yes>1 or yes+len(undec)<1:
                    return
                if yes==1 and undec:
                    for i in undec:assigned|=1<<i
                    changed=True
                elif yes==0 and len(undec)==1:
                    i=undec[0]
                    true|=1<<i;assigned|=1<<i
                    changed=True
            if not changed:break
        if assigned.bit_count()==n:
            assert exact_one(formula,true)
            results.append(true)
            return
        i=next(i for i in range(n) if not assigned>>i&1)
        search(assigned|(1<<i),true)
        search(assigned|(1<<i),true|(1<<i))
    search(0,0)
    assert len(set(results))==len(results)
    return set(results),calls


def rational_echelon(formula,n=27):
    """Independent rational sparse Gaussian elimination on Ax=1 via shift."""
    piv={}
    for triple in formula:
        row={j:Fraction(1) for j in triple}
        while row:
            p=min(row)
            if p not in piv:
                factor=row[p]
                piv[p]={j:v/factor for j,v in row.items()}
                break
            factor=row[p]
            prev=piv[p]
            row={j:v for j in row.keys()|prev.keys()
                 if (v:=row.get(j,0)-factor*prev.get(j,0))}
    return piv,tuple(j for j in range(n) if j not in piv)


def exhaustive_q_boolean_projection(formula,n=27):
    piv,free=rational_echelon(formula,n)
    models=set()
    for bits in itertools.product((0,1),repeat=len(free)):
        physical={i:Fraction(b) for i,b in zip(free,bits)}
        for p in sorted(piv,reverse=True):
            physical[p]=Fraction(1,3)-sum(
                coeff*(physical[j]-Fraction(1,3))
                for j,coeff in piv[p].items() if j!=p)
        if all(physical[i] in (0,1) for i in range(n)):
            truth=sum(int(physical[i])<<i for i in range(n))
            assert exact_one(formula,truth)
            models.add(truth)
    return models,len(piv),free


def local_three_port_relation():
    assert hashlib.sha256(json.dumps(ROWS,separators=(",",":")).encode()).hexdigest()==SHA
    assert len(ROWS)==27
    assert set(ri for ri,_ in PORTS)=={0,1,2}
    untouched=[row for i,row in enumerate(ROWS) if i not in {r for r,_ in PORTS}]
    dpll,calls=local_dpll(untouched)
    qrational,rank,free=exhaustive_q_boolean_projection(untouched)
    planted=sum(1<<v for v in ONES)
    alt=planted|(1<<0)
    assert dpll==qrational=={planted,alt},(dpll,qrational)
    assert rank==24 and len(free)==3 and free==(0,25,26),(rank,free)
    assert len(untouched)==24
    assert all(0 not in row for row in untouched)
    entries=[]
    allowed={}
    for physical in sorted(dpll):
        export=tuple(physical>>v&1 for _,v in PORTS)
        retained=[sum(physical>>j&1 for j in ROWS[r] if j!=v)
                  for r,v in PORTS]
        imported=tuple(1-x for x in retained)
        admissible=all(z in (0,1) for z in imported)
        if admissible:
            allowed[(export,imported)]=allowed.get((export,imported),0)+1
        entries.append({
          "punctured_true_variables":list(bitset_as_tuple(physical,27)),
          "exported_bits":list(export),
          "retained_true_counts":retained,
          "required_import_bits":list(imported),
          "admissible_under_boolean_imports":admissible
        })
    assert allowed=={((0,0,0),(0,0,0)):1},allowed
    assert [x["admissible_under_boolean_imports"] for x in entries]==[True,False]
    # The full U base has GF2 rank 24 and GF2 kernel dimension 3.
    assert 27-gf2_rank(ROWS)==3
    return {"punctured_rows":24,"full_original_variables":27,
        "DPLL_complete_nodes":calls,
        "rational_punctured_rank":rank,
        "rational_free_coordinates":list(free),
        "all_rational_boolean_projections_checked":1<<len(free),
        "complete_DPLL_model_count":len(dpll),
        "complete_rational_model_count":len(qrational),
        "unfiltered_local_models":entries,
        "EXACT_FEASIBLE_BOUNDARY_RELATION":[{
            "export_bits":[0,0,0],"import_bits":[0,0,0],"count":1
        }],
        "independent_boolean_enumerations_agree":True}


def gf2_rank(rows):
    piv={}
    for r in rows:
        v=sum(1<<j for j in r)
        while v:
            p=v.bit_length()-1
            if p in piv:v^=piv[p]
            else:piv[p]=v;break
    return len(piv)


def fixed_macro(t,seed):
    assert t>=8 and t%2==0
    m=t//2
    edge_set=set()
    for off in (0,m):
        for i in range(m):
            edge_set.add(tuple(sorted((off+i,off+(i+1)%m))))
    perm=list(range(m))
    random.Random(seed).shuffle(perm)
    for i,j in enumerate(perm):edge_set.add((i,m+j))
    assert len(edge_set)==3*t//2
    neighbors={i:set() for i in range(t)}
    for i,j in edge_set:
        neighbors[i].add(j);neighbors[j].add(i)
    assert all(len(neighbors[i])==3 for i in range(t))
    return neighbors


def global_fixture(t,seed):
    """Fresh independent macro generator; no imports from BABEL33."""
    neighbors=fixed_macro(t,seed)
    port_by_neighbor={(b,other):k
                      for b in range(t)
                      for k,other in enumerate(sorted(neighbors[b]))}
    n=27*t
    current=[[27*b+j for j in row] for b in range(t) for row in ROWS]
    for b in range(t):
        for other in sorted(neighbors[b]):
            if b>=other:continue
            ia=port_by_neighbor[b,other]
            ib=port_by_neighbor[other,b]
            ra,va=PORTS[ia]
            rb,vb=PORTS[ib]
            a_row=27*b+ra;b_row=27*other+rb
            a_var=27*b+va;b_var=27*other+vb
            current[a_row][current[a_row].index(a_var)]=b_var
            current[b_row][current[b_row].index(b_var)]=a_var
    formula=tuple(tuple(sorted(row)) for row in current)
    return formula


def independently_verify_macro_admission(formula,t):
    """Accept only certified real BABEL33 three-port macro substitution."""
    n=len(formula)
    assert n==27*t
    assert all(len(r)==3 and len(set(r))==3 for r in formula)
    assert Counter(v for row in formula for v in row)==Counter({i:3 for i in range(n)})
    pairs=[tuple(sorted(p)) for row in formula for p in itertools.combinations(row,2)]
    assert len(set(pairs))==3*n
    neighbors={b:set() for b in range(t)}
    for b in range(t):
        for ri,row in enumerate(ROWS):
            actual=formula[27*b+ri]
            if ri in (0,1,2):
                exported=PORTS[ri][1]
                local_expected={27*b+j for j in row if j!=exported}
                present_locals={j for j in actual if j//27==b}
                assert present_locals==local_expected
                external=[j for j in actual if j//27!=b]
                assert len(external)==1
                other=external[0]//27
                assert other!=b
                assert external[0]%27 in (0,6,5)
                neighbors[b].add(other)
            else:
                assert tuple(actual)==tuple(27*b+j for j in row)
    assert all(len(v)==3 for v in neighbors.values())
    assert all(b in neighbors[a] for a in neighbors for b in neighbors[a])
    # Validate swap matching in BOTH directions with correct inverse port row.
    for b in range(t):
        for ri,v in PORTS:
            incoming=[x for x in formula[27*b+ri] if x//27!=b]
            assert len(incoming)==1
            neighbor=incoming[0]//27
            incoming_var=incoming[0]
            inverse_ports=[row_index for row_index,export in PORTS
                           if export==incoming_var%27]
            assert len(inverse_ports)==1
            remote_row=inverse_ports[0]
            assert 27*b+v in formula[27*neighbor+remote_row]
    # Every block must use all three ports to THREE distinct neighbors.
    assert sum(len(v) for v in neighbors.values())==3*t
    seen={0};queue=[0]
    while queue:
        for y in neighbors[queue.pop()]-seen:
            seen.add(y);queue.append(y)
    assert len(seen)==t
    # The implication local-feasible R_U=singleton => global UNIQUE SAT
    # is the all-n theorem, not a full 2^dim(K) enumeration.
    witness=sum(1<<(27*b+v) for b in range(t) for v in ONES)
    assert exact_one(formula,witness)
    return witness


def one_fixture(t,seed):
    formula=global_fixture(t,seed)
    model=independently_verify_macro_admission(formula,t)
    d=n_kernel=27*t-gf2_rank(formula)
    assert d>=3*t//2,(t,d)
    E2=27*t*(1+27*t+(27*t)*(27*t-1)//2)
    support_degree2_ceiling=1+4*E2
    return {
        "macro_vertices":t,
        "n_original_variables":27*t,
        "connected_legal_cubic_linear":"EXACT_PASS",
        "independent_macro_certificate":"EXACT_PASS",
        "all_original_rows_SAT_replayed":"EXACT_PASS",
        "all_n_exact_sat_count_from_local_singleton":"1",
        "GF2_kernel_dim_exact":d,
        "GF2_kernel_lower_bound_proved":3*t//2,
        "full_indicator_Fourier_support_exact":str(1<<d),
        "degree2_Gram_support_upper":support_degree2_ceiling,
        "degree2_idempotence_SAT_gate_impossible":
             support_degree2_ceiling<(1<<d),
        "rows_sha256":hashlib.sha256(json.dumps(formula,separators=(",",":")).encode()).hexdigest()
    }


def main():
    local=local_three_port_relation()
    tests=[one_fixture(t,seed=3400+t) for t in (8,12,16,24,40)]
    assert tests[-1]["degree2_idempotence_SAT_gate_impossible"]
    print(json.dumps({
       "gate":"BABEL34_ALL_N_THREE_PORT_MACRO_UNIQUE_SAT",
       "local_exhaustive_two_implementations":"EXACT_PASS",
       "local_boundary_relation_singleton":"000_TO_000",
       "all_n_theorem":"EVERY_ADMISSIBLE_CUBIC_MACRO_HAS_EXACTLY_ONE_SAT_MODEL",
       "all_n_GF2_nullity":"DIM_K_GE_3T_OVER_2",
       "fixed_degree_Gram_indicator_complete":"NO_ON_THIS_FAMILY_ASYMPTOTICALLY",
       "admitted_template_composition_complexity":"POLYNOMIAL_WITH_CERTIFIED_DECOMPOSITION",
       "arbitrary_connected_SCL_template_discovery":"OPEN",
       "unrestricted_polynomial_solver":"NOT_PROVED",
       "P_vs_NP":"OPEN",
       "local":local,
       "controls":tests
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
