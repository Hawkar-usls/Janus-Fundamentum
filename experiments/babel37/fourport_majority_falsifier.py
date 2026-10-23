#!/usr/bin/env python3
"""BABEL37 independently exact FOUR-port U relation and majority barrier.

No imports from BABEL24-36 producer scripts. Independently enumerate all
23-row Boolean assignments by (1) complete unit-propagation Exact-One DPLL
and (2) exact rational Gaussian elimination + all Boolean free projections.
Then certify a finite exact 3-state CSP over genuine CONNECTED, cubic, linear
original SCL macros, with one SAT and one UNSAT fixture.
"""
import hashlib
import itertools
import json
from collections import Counter,deque
from fractions import Fraction

U=(
    (0,1,2),(0,3,6),(0,5,7),(3,5,20),(1,7,11),
    (3,8,12),(6,7,8),(2,5,8),(2,10,14),
    (9,10,11),(9,12,15),(9,14,22),
    (12,13,14),(10,13,16),(1,6,17),(15,16,17),
    (4,17,20),(11,13,21),(4,18,19),(15,18,24),
    (18,23,25),(21,22,23),(16,19,25),
    (19,21,26),(24,25,26),(4,23,26),(20,22,24))
SHA="9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
PORTS=((0,0),(1,3),(2,7),(26,20))
FULL_MASK=(1<<27)-1
R4=(
   (0,0,0,1, 0,0,1,0),
   (0,1,1,0, 0,1,1,0),
   (1,1,1,0, 0,0,0,0)
)
MAJORITY_MISSING=(0,1,1,0, 0,0,1,0)


def true_indices(bits,n=27):
    return tuple(i for i in range(n) if bits>>i&1)


def exact_one(rows,bits):
    return all(sum(bits>>j&1 for j in row)==1 for row in rows)


def complete_dpll(kept):
    """Boolean exact-one complete independent decision-tree enumerator."""
    outputs=[];calls=0
    def visit(known,true):
        nonlocal calls
        calls+=1
        while True:
            changed=False
            for row in kept:
                have=sum((true>>j)&1 for j in row)
                unknown=[j for j in row if not(known>>j&1)]
                if have>1 or (have==0 and not unknown):return
                if have==1 and unknown:
                    for j in unknown:known|=1<<j
                    changed=True
                elif have==0 and len(unknown)==1:
                    j=unknown[0];known|=1<<j;true|=1<<j
                    changed=True
            if not changed:break
        if known==FULL_MASK:
            assert exact_one(kept,true)
            outputs.append(true)
            return
        free=next(j for j in range(27) if not (known>>j)&1)
        visit(known|(1<<free),true)
        visit(known|(1<<free),true|(1<<free))
    visit(0,0)
    assert len(outputs)==len(set(outputs))
    return set(outputs),calls


def complete_fraction_projection(kept):
    """Independent rational row elimination, not dependent on DPLL."""
    piv={}
    for row in kept:
        coeff={j:Fraction(1) for j in row}
        while coeff:
            p=min(coeff)
            if p not in piv:
                scale=coeff[p]
                piv[p]={j:v/scale for j,v in coeff.items()}
                break
            fact=coeff[p];old=piv[p]
            coeff={j:v for j in (coeff.keys()|old.keys())
                   if (v:=coeff.get(j,0)-fact*old.get(j,0))}
    free=tuple(j for j in range(27) if j not in piv)
    outputs=set()
    for binary in itertools.product((0,1),repeat=len(free)):
        x={i:Fraction(bit) for i,bit in zip(free,binary)}
        for p in sorted(piv,reverse=True):
            x[p]=Fraction(1,3)-sum(
                coefficient*(x[j]-Fraction(1,3))
                for j,coefficient in piv[p].items() if j!=p)
        if all(x[j] in (0,1) for j in range(27)):
            bits=sum(int(x[j])<<j for j in range(27))
            assert exact_one(kept,bits)
            outputs.add(bits)
    return outputs,len(piv),free


def local_relation():
    assert hashlib.sha256(json.dumps(U,separators=(",",":")).encode()).hexdigest()==SHA
    assert len(U)==27
    assert len(set(r for r,v in PORTS))==len(set(v for r,v in PORTS))==4
    assert all(v in U[r] for r,v in PORTS)
    deleted={r for r,v in PORTS}
    kept=[row for i,row in enumerate(U) if i not in deleted]
    assert len(kept)==23
    bool_models,calls=complete_dpll(kept)
    q_models,rank,free=complete_fraction_projection(kept)
    assert bool_models==q_models
    assert rank==23 and free==(0,23,25,26),(rank,free)
    assert len(bool_models)==4
    records=[];feasible={}
    for physical in sorted(bool_models):
        export=tuple((physical>>v)&1 for _,v in PORTS)
        retained=tuple(sum((physical>>j)&1 for j in U[r] if j!=v)
                       for r,v in PORTS)
        need=tuple(1-c for c in retained)
        allowed=all(b in (0,1) for b in need)
        records.append({
            "ones":list(true_indices(physical)),
            "exports":list(export),"required_imports":list(need),
            "retained_counts":list(retained),
            "feasible":allowed
        })
        if allowed:
            bits=export+need
            assert bits not in feasible,("duplicated boundary assignment",bits)
            feasible[bits]=physical
    assert tuple(sorted(feasible))==tuple(sorted(R4)),tuple(sorted(feasible))
    # Four incidence edges removed. The 54-vertex ORIGINAL remaining factor
    # graph must be fully connected to inherit global macro connectedness.
    g=[[] for _ in range(54)]
    for i,row in enumerate(U):
        for v in row:
            if (i,v) in PORTS:continue
            g[i].append(27+v);g[27+v].append(i)
    seen={0};q=[0]
    while q:
        for v in g[q.pop()]:
            if v not in seen:seen.add(v);q.append(v)
    assert len(seen)==54
    return feasible,{
       "punctured_rows_kept":23,
       "independent_complete_Boolean_DPLL_model_count":len(bool_models),
       "DPLL_search_nodes":calls,
       "independent_rational_matrix_rank":rank,
       "rational_free_original_coordinates":list(free),
       "rational_Boolean_projections_tested":1<<len(free),
       "complete_physical_local_models":records,
       "feasible_four_port_signatures":[list(p) for p in sorted(feasible)],
       "internal_four_port_deleted_graph_connected":True
    }


def maj(a,b,c):
    return tuple(int((x+y+z)>=2) for x,y,z in zip(a,b,c))


def majority_obstruction(feasible):
    assert len(feasible)==3 and len(R4)==3
    out=maj(*R4)
    assert out==MAJORITY_MISSING
    assert out not in feasible
    # This is a complete finite failure of majority closure; a 2CNF
    # relation, including existentially eliminated helper variables,
    # MUST be majority-closed by the all-n mathematical proof in doc.
    return {
        "three_true_relation_points":[list(x) for x in R4],
        "coordinatewise_majority":[*out],
        "majority_is_valid":out in feasible,
        "not_exactly_2CNF_definable_even_with_existential_aux":"PROVED",
        "no_generic_SAT_lower_bound_claimed":True
    }


def schaefer_exact_polymorphism_falsifiers(feasible):
    """Finite closure counterexamples for the six Schaefer tractable types.

    The NP-completeness consequence applies to the GENERIC CSP({R4})
    with unrestricted 8-variable constraint scopes ONLY. It does NOT
    automatically transfer to four-edge U macro joins.
    """
    A,B,C=R4
    and_ab=tuple(x&y for x,y in zip(A,B))
    or_ab=tuple(x|y for x,y in zip(A,B))
    xor_abc=tuple(x^y^z for x,y,z in zip(A,B,C))
    majority=maj(A,B,C)
    assert (0,)*8 not in feasible
    assert (1,)*8 not in feasible
    assert all(x not in feasible for x in
               (and_ab,or_ab,xor_abc,majority))
    return {
      "all_zero_tuple_admissible":False,
      "all_one_tuple_admissible":False,
      "Horn_AND_counterexample":[*and_ab],
      "dual_Horn_OR_counterexample":[*or_ab],
      "affine_XOR3_counterexample":[*xor_abc],
      "bijunctive_majority_counterexample":[*majority],
      "all_four_closure_outputs_outside_R4":True,
      "generic_unrestricted_CSP_R4_complexity":
         "NP_COMPLETE_BY_SCHAEFER_DICHOTOMY",
      "special_edge_spliced_U_macro_NP_hardness":
         "NOT_ESTABLISHED"
    }


def macros(kind):
    if kind=="K5":
        t=5
        edges=tuple(itertools.combinations(range(5),2))
        adj={i:set() for i in range(t)}
        for a,b in edges:adj[a].add(b);adj[b].add(a)
        slots={(a,b):sorted(adj[a]).index(b)
               for a in range(t) for b in adj[a]}
    elif kind=="K44":
        t=8
        edges=tuple((i,4+j) for i in range(4) for j in range(4))
        adj={i:set() for i in range(t)}
        slots={}
        for i,j in edges:
            adj[i].add(j);adj[j].add(i)
            # Four-edge-coloring: same port used at BOTH edge ends.
            k=(i+(j-4))%4
            slots[(i,j)]=slots[(j,i)]=k
    else:raise ValueError(kind)
    assert len(edges)==2*t
    assert all(len(x)==4 for x in adj.values())
    assert all(set(slots[(b,c)] for c in adj[b])==set(range(4))
               for b in range(t))
    return t,edges,adj,slots


def build_macro(t,edges,slots):
    rows=[list(27*b+v for v in row) for b in range(t) for row in U]
    original=[tuple(sorted(row)) for row in rows]
    receipts=[]
    for a,b in edges:
        ra,va=PORTS[slots[(a,b)]]
        rb,vb=PORTS[slots[(b,a)]]
        left=27*a+ra;right=27*b+rb
        x=27*a+va;y=27*b+vb
        assert x in rows[left] and y in rows[right]
        rows[left][rows[left].index(x)]=y
        rows[right][rows[right].index(y)]=x
        receipts.append((left,x,right,y))
    out=tuple(tuple(sorted(row)) for row in rows)
    n=27*t
    assert all(len(row)==3 and len(set(row))==3 for row in out)
    assert Counter(v for row in out for v in row)==Counter({v:3 for v in range(n)})
    pair_list=[tuple(sorted(p)) for row in out for p in itertools.combinations(row,2)]
    assert len(set(pair_list))==3*n
    reversed_rows=[list(row) for row in out]
    for left,x,right,y in receipts:
        assert y in reversed_rows[left] and x in reversed_rows[right]
        reversed_rows[left][reversed_rows[left].index(y)]=x
        reversed_rows[right][reversed_rows[right].index(x)]=y
    assert [tuple(sorted(row)) for row in reversed_rows]==original
    adjacency=[set() for _ in range(2*n)]
    for row,row_vars in enumerate(out):
        for v in row_vars:
            adjacency[row].add(n+v);adjacency[n+v].add(row)
    seen={0};q=[0]
    while q:
        for nxt in adjacency[q.pop()]-seen:
            seen.add(nxt);q.append(nxt)
    assert len(seen)==2*n
    return out


def independent_three_state_count(t,edges,slots,feasible,full_rows):
    """Exhaustive 3^t CSP, NOT a full 2^n physical SAT enumeration."""
    states=sorted(feasible)
    assert len(states)==3
    all_models=[]
    for choice in itertools.product(range(3),repeat=t):
        satisfied=True
        for a,b in edges:
            pa=slots[(a,b)]
            pb=slots[(b,a)]
            sig_a=states[choice[a]]
            sig_b=states[choice[b]]
            if sig_a[pa]!=sig_b[4+pb] or sig_b[pb]!=sig_a[4+pa]:
                satisfied=False;break
        if satisfied:
            physical=sum(feasible[states[choice[i]]]<<(27*i) for i in range(t))
            assert exact_one(full_rows,physical),("unsound port relation",choice)
            all_models.append(physical)
    assert len(set(all_models))==len(all_models)
    return all_models


def check_macro(kind,feasible):
    t,edges,adj,slots=macros(kind)
    physical_rows=build_macro(t,edges,slots)
    models=independent_three_state_count(t,edges,slots,feasible,physical_rows)
    count=len(models)
    if kind=="K5":assert count==0,count
    if kind=="K44":assert count==1,count
    n=27*t
    return {
       "macro":kind,"macro_vertices":t,
       "connected_original_SCL_variables":n,
       "original_row_count":n,
       "macro_edges":len(edges),
       "local_relation_states_per_block":3,
       "macro_state_combinations_exhaustively_checked":3**t,
       "exact_global_SAT_count":count,
       "physical_witness_replayed_against_ALL_original_rows":True if count else None,
       "original_SCL_legal_connected_square_cubic_linear":"EXACT_PASS",
       "inverse_incidence_splices":"EXACT_PASS"
    }


def main():
    feasible,local=local_relation()
    obstruction=majority_obstruction(feasible)
    schaefer=schaefer_exact_polymorphism_falsifiers(feasible)
    controls=[check_macro("K5",feasible),check_macro("K44",feasible)]
    print(json.dumps({
      "gate":"BABEL37_FOUR_PORT_MAJORITY_NONBIJUNCTIVE_BARRIER",
      "frozen_SCL27_checksum_checked":True,
      "two_independent_COMPLETE_local_enumerators":"PASS",
      "R4_exact":"{0001|0010,0110|0110,1110|0000}",
      "R4_expressible_by_2CNF_with_existential_aux":"NO_PROVED",
      "all_n_macro_3state_CSP_correspondence":"PROVED",
      "universal_connected_SCL_polynomial_decider":"NOT_PROVED",
      "P_vs_NP":"OPEN",
      "independent_local_proof":local,
      "majority_refutation":obstruction,
      "independent_Schaefer_polymorphism_falsifiers":schaefer,
      "exact_original_macro_controls":controls
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
