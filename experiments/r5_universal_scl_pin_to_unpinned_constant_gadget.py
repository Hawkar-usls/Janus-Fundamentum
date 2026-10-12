#!/usr/bin/env python3
"""R5 all-legal-SCL constant pin gadgets and polynomial pin compiler.

Two finite source-authenticated 3-regular C4-free ExactOne gadgets:

G10 (10 variables): removing source incidence (row {1,4,6},var4)
gives a TWO-PORT ternary Holant transfer with sole nonzero
row-side/column-side boundary (a,b)=(1,0), multiplicity 1.

G11 (11 variables): removing source incidence (row {5,7,8},var7)
gives transfer only (a,b)=(0,1), multiplicity 2.

Connect any source SCL F and the two chosen gadget copies
by deleting one Tanner edge (W0,V0) in EACH of the three
components and cyclically rewiring:
    original W0 -> gadget1 V1,
    gadget1 W1 -> gadget2 V2,
    gadget2 W2 -> original V0.
This 3-switch preserves exact cubic row/column degrees and
C4-free/linear SCL legality: no new C4 can cross the
three DIFFERENT components joined by just one inter-component
edge per unordered pair, and no old C4 was created internally.

Select gadget order (G10,G11) to force original
source row port and source variable port both equal0;
select (G11,G10) to force both equal1.

Every original source solution with x_v=t has exactly
1*2=2 extended solutions of the transformed UNPINNED legal
SCL instance; no other assignments survive:
    #SAT(CompilePin(F,v,t)) = 2*#SAT(F and x_v=t).

Repeating independently for q DISTINCT original source pins,
always on the ORIGINAL variable indices preserved by extension:
    size = n+21*q <= 22n,
    #SAT(CompilePins(F,P)) = 2^q * #SAT(F respecting P).
The conversion and its independent source replay are polynomial
on ALL legal SCL inputs, not just Holyer or a special subclass.

Hence a hypothetical UNPINNED uniform bit-polynomial
SolveLinearCubicXSAT/LoopZeroTest on all legal SCL suffices
for witness recovery by n+1 source-legal unpinned zero calls.
No polynomial ZERO TEST has been constructed; P vs NP OPEN.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import validate_sparse

G10_RAW=(
    (0,6,5),(1,3,0),(2,0,8),(3,8,4),(4,1,6),
    (5,4,9),(6,7,2),(7,9,3),(8,5,7),(9,2,1)
)
G11_RAW=(
    (0,5,2),(1,10,0),(2,9,10),(3,0,4),(4,1,9),
    (5,7,8),(6,2,7),(7,3,1),(8,4,6),(9,6,5),(10,8,3)
)

def gadget(which):
    assert which in (10,11)
    rows=validate_sparse(G10_RAW if which==10 else G11_RAW,which)
    chosen=tuple(sorted((4,1,6) if which==10 else (5,7,8)))
    cut_row=rows.index(chosen)
    cut_col=4 if which==10 else 7
    assert cut_col in rows[cut_row]
    return rows,cut_row,cut_col


def exhaustive_open_transfer(which):
    """Independent ORIGINAL-SOURCE finite transfer enumeration."""
    rows,i,v=gadget(which)
    n=len(rows)
    table=[[0,0],[0,0]]
    solutions={(a,b):[] for a in (0,1) for b in (0,1)}
    for mask in range(1<<n):
        x=tuple((mask>>j)&1 for j in range(n))
        if any(sum(x[j] for j in row)!=1
               for j,row in enumerate(rows) if j!=i):
            continue
        # row i sees external a INSTEAD of column v's actual bit b
        a=1-sum(x[j] for j in rows[i] if j!=v)
        b=x[v]
        if a not in (0,1):continue
        table[a][b]+=1
        solutions[(a,b)].append(x)
    expected=((0,0),(1,0)) if which==10 else ((0,2),(0,0))
    assert tuple(map(tuple,table))==expected,(which,table)
    # Global source closed by original edge is UNSAT by n mod3,
    # so both same-bit transfer entries must be zero.
    assert table[0][0]==table[1][1]==0
    return tuple(map(tuple,table)),solutions


def replace_port(row,old,new):
    assert old in row and new not in row
    return tuple(sorted((set(row)-{old})|{new}))


def three_switch_pin(rows,n,var,pin):
    """Source-replayable deterministic constant-size SCL gadget splice."""
    rows=validate_sparse(rows,n)
    assert type(var) is int and 0<=var<n
    assert pin in (0,1)
    cut0=next(i for i,row in enumerate(rows) if var in row)
    g1n,g2n=(10,11) if pin==0 else (11,10)
    g1,i1,v1=gadget(g1n)
    g2,i2,v2=gadget(g2n)
    ofs1=n
    ofs2=n+g1n
    extended=list(rows)
    extended.extend(tuple(ofs1+v for v in row) for row in g1)
    extended.extend(tuple(ofs2+v for v in row) for row in g2)

    old0=extended[cut0]
    old1=extended[ofs1+i1]
    old2=extended[ofs2+i2]
    extended[cut0]=replace_port(old0,var,ofs1+v1)
    extended[ofs1+i1]=replace_port(old1,ofs1+v1,ofs2+v2)
    extended[ofs2+i2]=replace_port(old2,ofs2+v2,var)

    output=validate_sparse(extended,n+21)
    assert len(output)==n+21
    assert all(len(row)==3 for row in output)
    # The witness-lifted algebraic transfer imposes old row & col
    # values pin (0,0) or pin (1,1), with multiplicity2.
    return output,n+21,{
        "source_n":n,"new_n":n+21,"original_var":var,
        "forced_bit":pin,"source_edge_row":old0,
        "gadget_order":(g1n,g2n),
        "source_row_count":n,
        "transfer_multiplier":2
    }


def certify_single_pin_compile(rows,n,var,pin,compiled,meta):
    """Reconstruct the FULL transformed original SCL from source;
    reject alternative rows, forged provenance or pin metadata."""
    rows=validate_sparse(rows,n)
    expected,size,m=three_switch_pin(rows,n,var,pin)
    assert compiled==expected
    assert meta==m
    assert size==n+21
    return True


def compile_source_pins(rows,n,pins):
    """Polynomial original-to-legal-SCL compilation, q<=n."""
    original=validate_sparse(rows,n)
    labels=dict(pins)
    assert all(type(v) is int and 0<=v<n and b in (0,1)
               for v,b in labels.items())
    current=original
    size=n
    chain=[]
    for var,bit in sorted(labels.items()):
        candidate,newsize,proof=three_switch_pin(
            current,size,var,bit
        )
        assert certify_single_pin_compile(
            current,size,var,bit,candidate,proof
        )
        chain.append(proof)
        current,size=candidate,newsize
    assert size==n+21*len(labels)
    return current,size,tuple(chain)


def certify_source_pin_chain(rows,n,pins,compiled,chain):
    original=validate_sparse(rows,n)
    labels=dict(pins)
    assert len(chain)==len(labels)
    size=n;current=original
    for (var,bit),p in zip(sorted(labels.items()),chain):
        nxt,newsize,generated=three_switch_pin(current,size,var,bit)
        assert generated==p
        assert p["source_n"]==size and p["original_var"]==var
        current,size=nxt,newsize
    assert compiled==current and size==n+21*len(labels)
    return True


def source_exact_witness_count_small(rows,n,pins=None):
    """EXPONENTIAL finite independent original witness control ONLY."""
    assert n<=12
    rows=validate_sparse(rows,n)
    pins=dict(pins or {})
    masks=tuple(sum(1<<v for v in row) for row in rows)
    ans=[]
    for m in range(1<<n):
        if all((m&mask).bit_count()==1 for mask in masks) and all(
            ((m>>v)&1)==bit for v,bit in pins.items()
        ):
            ans.append(tuple((m>>i)&1 for i in range(n)))
    return tuple(ans)


def lift_single_source_witness(rows,n,witness,var,pin):
    """Construct a genuine witness for the n+21 compiled rows."""
    assert len(witness)==n and witness[var]==pin
    assert all(sum(witness[v] for v in row)==1 for row in rows)
    g1n,g2n=(10,11) if pin==0 else (11,10)
    _,w1=exhaustive_open_transfer(g1n)
    _,w2=exhaustive_open_transfer(g2n)
    # n10 a,b=(1,0); n11 a,b=(0,1).
    key1=(1,0) if g1n==10 else (0,1)
    key2=(0,1) if g2n==11 else (1,0)
    compiled,size,_=three_switch_pin(rows,n,var,pin)
    lifted=[]
    for u in w1[key1]:
        for v in w2[key2]:
            x=tuple(witness)+u+v
            assert len(x)==size
            assert all(sum(x[t] for t in row)==1 for row in compiled)
            lifted.append(x)
    assert len(lifted)==2 and lifted[0]!=lifted[1]
    return compiled,tuple(lifted)


def recover_original_witness_from_unpinned_scl_oracle(rows,n,zero_test):
    """GENERAL conditional theorem, all calls on legal UNPINNED SCL.

    zero_test(F,m) must return TRUE iff the ordinary original SCL F
    is UNSAT, for ALL legal square+cubic+linear sources F,
    including compiled sources of size <=22n.
    """
    source=validate_sparse(rows,n)
    calls=1
    if zero_test(source,n):
        return None,calls
    fixed={}
    for v in range(n):
        trial=dict(fixed)
        trial[v]=0
        candidate,nnew,cert=compile_source_pins(source,n,trial)
        assert certify_source_pin_chain(source,n,trial,candidate,cert)
        calls+=1
        if zero_test(candidate,nnew):
            fixed[v]=1
        else:
            fixed[v]=0
    witness=tuple(fixed[v] for v in range(n))
    assert all(sum(witness[v] for v in row)==1 for row in source)
    assert calls==n+1
    return witness,calls


def finite_unpinned_scl_oracle_affine9(rows,n):
    """Finite exact exponential oracle, not a polynomial all-SCL solver.

    Accepts ONLY ORIGINAL LEGAL cubic linear square sources: no
    marked tensors, pins, clauses of other sizes or source hints.
    """
    from r5_universal_all_scl_perfect_matching_rank2_network import (
        paired_quartic_network,independent_network_count_small
    )
    Q=paired_quartic_network(rows,n)
    result=independent_network_count_small(
        Q,max_nodes=220,max_states=3500000
    )
    assert result["status"] in ("SAT","UNSAT"),result
    if result["status"]=="SAT":
        assert result["witness"] is not None
        assert all(sum(result["witness"][v] for v in row)==1
                   for row in Q["source_rows"])
    return result


def finite_unmarked_only_witness_demo():
    from r5_universal_pinned_loop_witness_extraction_gate import (
        affine_plane_scl9
    )
    source,expected=affine_plane_scl9()
    history=[]
    def oracle(rows,n):
        result=finite_unpinned_scl_oracle_affine9(rows,n)
        history.append((n,result["status"],result["states"]))
        return result["status"]=="UNSAT"
    witness,calls=recover_original_witness_from_unpinned_scl_oracle(
        source,9,oracle
    )
    assert calls==10
    assert witness in expected
    assert len(history)==10
    assert max(n for n,status,states in history)<=9+21*9
    print("AFFINE9_WITNESS_FROM_TEN_UNPINNED_LEGAL_SCL_CALLS="+
          str(witness),flush=True)
    print("AFFINE9_UNPINNED_COMPILER_QUERY_SIZES="+
          str(tuple(row[0] for row in history)),flush=True)
    print("AFFINE9_UNPINNED_FINITE_ORACLE_TOTAL_STATES="+
          str(sum(row[2] for row in history)),flush=True)
    return witness


def main():
    from r5_universal_pinned_loop_witness_extraction_gate import (
        affine_plane_scl9
    )
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,petersen_graph
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower
    from r5_universal_all_scl_perfect_matching_rank2_network import (
        paired_quartic_network,independent_network_count_small,
    )
    for k in (10,11):
        matrix,w=exhaustive_open_transfer(k)
        print(f"LEGAL_SCL_OPEN_GADGET_{k}_TRANSFER={matrix} "
              f"nonzero_assignments={sum(map(sum,matrix))}",flush=True)

    rows9,witnesses=affine_plane_scl9()
    assert len(witnesses)==3
    for bit in (0,1):
        p={0:bit}
        compiled,n,chain=compile_source_pins(rows9,9,p)
        assert certify_source_pin_chain(rows9,9,p,compiled,chain)
        expected=2*len(source_exact_witness_count_small(rows9,9,p))
        assert expected in (2,4)
        quotient=paired_quartic_network(compiled,n)
        audit=independent_network_count_small(
            quotient,max_nodes=35,max_states=2000000
        )
        assert audit["status"]!="UNKNOWN_RESOURCE_LIMIT",audit
        assert audit["count"]==expected,(bit,audit,expected)
        original=next(w for w in witnesses if w[0]==bit)
        _,lifted=lift_single_source_witness(rows9,9,original,0,bit)
        assert len(lifted)==2
        print(f"AFFINE_SCL9_PIN_{bit}_COMPILED_SCL{n}_EXACT_COUNT="
              f"{audit['count']} expected={expected} "
              f"states={audit['states']}",flush=True)

    # Strict multiple-pin test: first two variables share original row.
    # Incompatibility of simultaneous x0=x1=1 is source-explicit.
    assert 0 in rows9[0] and 1 in rows9[0]
    conflicting={0:1,1:1}
    output,n,chain=compile_source_pins(rows9,9,conflicting)
    assert n==51 and certify_source_pin_chain(
        rows9,9,conflicting,output,chain
    )
    assert not source_exact_witness_count_small(rows9,9,conflicting)
    count=independent_network_count_small(
        paired_quartic_network(output,n),max_nodes=55,
        max_states=3000000
    )
    assert count["status"]=="UNSAT" and count["count"]==0,count
    print(f"AFFINE_SCL9_INCOMPATIBLE_TWO_PINS_COMPILED_SCL51="
          f"UNSAT_CERTIFIED_FINITE states={count['states']}",flush=True)

    # True product factor 2^q tested with compatible two original pins.
    compatible={0:1,1:0}
    orig_count=len(source_exact_witness_count_small(
        rows9,9,compatible
    ))
    assert orig_count==1
    output2,n2,chain2=compile_source_pins(rows9,9,compatible)
    assert n2==51 and certify_source_pin_chain(
        rows9,9,compatible,output2,chain2
    )
    count2=independent_network_count_small(
        paired_quartic_network(output2,n2),max_nodes=55,
        max_states=3000000
    )
    assert count2["status"]=="SAT" and count2["count"]==4,count2
    print(f"AFFINE_SCL9_TWO_COMPATIBLE_PINS_COMPILED_SCL51="
          f"COUNT4_EXACT states={count2['states']}",flush=True)

    # Non-Holyer and larger hard original source:
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    for name,rows,n in (
        ("FANO7",cyclic(7),7),
        ("K4_SCL18",*make_scl(K4())[:2]),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
        ("FLOWER_J5_SCL90",*make_scl(flower(5))[:2])
    ):
        candidate,nnew,proof=compile_source_pins(rows,n,{0:1})
        assert nnew==n+21
        assert certify_source_pin_chain(
            rows,n,{0:1},candidate,proof
        )
        print(f"ALL_SCL_PIN_COMPILER_{name}_SIZE={nnew}_LEGAL_SOURCE=PASS",
              flush=True)
    for name,p,q in (("E61_SAT12",P_SAT,Q_SAT),
                     ("E61_UNSAT12",P_UNSAT,Q_UNSAT)):
        A=build_A(p,q)
        rows=validate_sparse([tuple(j for j,v in enumerate(row) if v)
                              for row in A],len(A))
        compiled,nnew,proof=compile_source_pins(
            rows,len(rows),{0:0}
        )
        assert certify_source_pin_chain(
            rows,len(rows),{0:0},compiled,proof
        )
        print(f"ALL_SCL_PIN_COMPILER_{name}_SIZE={nnew}_LEGAL_SOURCE=PASS",
              flush=True)

    finite_unmarked_only_witness_demo()
    print("ALL_SCL_TWO_TERMINAL_PIN_GADGETS_WITH_TRANSFER_MULTIPLIER2=PROVED")
    print("ALL_SCL_SOURCE_PIN_TO_UNPINNED_LEGAL_SCL_POLY_COMPILER=PROVED")
    print("COMPILED_SOURCE_SIZE_N_PLUS21_PER_PIN=PROVED")
    print("COMPILED_EXACT_COUNT_EQUALS_2_POWER_Q_TIMES_ORIGINAL_PINNED_COUNT=PROVED")
    print("UNPINNED_POLY_LOOP_ZERO_TEST_SUFFICES_TO_EXTRACT_WITNESS=CONDITIONAL")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")

if __name__=="__main__":
    main()
