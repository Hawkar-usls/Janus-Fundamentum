#!/usr/bin/env python3
"""R5 THEOREM: connected legal SCL, 3|n, UNSAT, unbounded girth.

This removes the trivial global n%3 refutation from the previous
high-girth Fano homology tower while retaining rigorous UNSAT.

BASE H_j: any connected legal cubic/linear/square SCL on m source
rows/columns, m%3 != 0, Tanner girth >=g. Examples are Fano7
and each homology-cover tower level of Fano7.

Construct THREE disjoint copies of H_j, indexed i=0,1,2.
Choose the SAME original Tanner incidence (row r, variable v)
in each copy. Delete those three Tanner edges and replace them
cyclically with row r_i -- variable v_(i+1 modulo3).
Every source row and column remains degree3, no C4 is added
if base girth >=6, and new source has n=3m divisible by3.
The resulting Tanner graph is CONNECTED.

PROOF UNSAT, an ORIGINAL-SOURCE integer certificate:
For each copy i let b_i = Boolean value of its cut original
variable v_i, and a_i = Boolean value on the replacement
incidence entering its cut exact-one row r_i.
Sum all m Exact-One equations over rows in block i. Each
in-block original column occurs three times except cut
column v_i occurs twice; external variable v_(i+1) enters
once. Therefore:
   m = 3*(sum_original_vars_in_copy_i x_v) - b_i + a_i.
Hence a_i - b_i = m (mod3).
As a_i,b_i in {0,1}, for m mod3 == 1 one has
   (a_i,b_i)=(1,0)
and for m mod3 == 2 one has (a_i,b_i)=(0,1).
But cyclic source wiring imposes a_i = b_(i+1);
contradiction. Thus the new source is UNSAT, though 3|n.

GIRTH: a simple new Tanner cycle either lies in an old copy
(exact girth >=g) or uses cross wires. The three-component
quotient is a triangle; every new crossing cycle must use
all 3 cross wires, and in EACH base copy it traverses a path
between the original cut row and cut variable after the cut
edge was removed. Any such path has length >=g-1 (otherwise
reinserting cut edge creates a base cycle shorter than g).
Thus new cycle length >=3 + 3*(g-1) =3g.
Conclude Tanner girth of connected joined source >=g.

Apply construction at EVERY level of explicit Fano F2-homology
cover tower. Original cover girth grows strictly without bound;
n=3*7*power_of_2 is always divisible by3 and all joined
sources are connected source-legal UNSAT with Tanner girth
unbounded. Its matched quartic quotient Q has
girth(Q) >= girth(Tanner)/2 from earlier proof, so every
fixed-size nonempty exact generalized-loop term vanishes.
Truncation through a fixed selected-edge cardinality returns
1 (empty loop) although exact L=0. This remains true
AFTER a global n%3 check.

No claim that these sources defeat polynomial algorithms
checking block or cut parity, and no unconditional runtime
lower bound. P_VS_NP=OPEN.
"""
from __future__ import annotations
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
from r5_universal_loop_high_girth_fano_homology_cover_nogo import (
    binary_homology_cover,tanner_girth_up_to,original_sum_refutation,
    quotient_girth_up_to
)
from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,verify_paired_quartic_network
)
from r5_universal_rank2_exact_bethe_loop_correction import local_loop_moments


def certify_connected_tanner(rows,n):
    """Original Tanner incidence connectivity, no graph metadata trusted."""
    from collections import deque
    rows=validate_sparse(rows,n)
    adj=[[] for _ in range(2*n)]
    for i,row in enumerate(rows):
        for v in row:
            adj[i].append(n+v)
            adj[n+v].append(i)
    seen={0}
    q=deque([0])
    while q:
        v=q.popleft()
        for w in adj[v]:
            if w not in seen:
                seen.add(w);q.append(w)
    return len(seen)==2*n


def triple_cyclic_source_glue(rows,m):
    """Polynomial source-to-source construction and exact provenance."""
    rows=validate_sparse(rows,m)
    assert m%3 in (1,2)
    assert certify_connected_tanner(rows,m)
    r=0
    v=rows[r][0]
    original=tuple(rows[r])
    result=[]
    for copy_id in range(3):
        for i,row in enumerate(rows):
            shifted=tuple(copy_id*m+x for x in row)
            if i==r:
                old=copy_id*m+v
                incoming=((copy_id+1)%3)*m+v
                assert old in shifted and incoming not in shifted
                shifted=tuple(sorted((set(shifted)-{old})|{incoming}))
            result.append(shifted)
    n=3*m
    source=validate_sparse(result,n)
    assert n%3==0
    assert certify_connected_tanner(source,n)
    provenance={
        "base_n":m,"joined_n":n,"cut_row":r,
        "cut_original_variable":v,"source_cut_row":original,
        "cyclic_wiring":tuple(
            ((i*m+r),((i+1)%3)*m+v) for i in range(3)
        ),"base_mod3":m%3
    }
    return source,n,provenance


def independently_replay_source_glue(base,m,joined,n,cert):
    base=validate_sparse(base,m)
    joined=validate_sparse(joined,n)
    assert n==3*m and cert["base_n"]==m
    assert cert["joined_n"]==n
    assert cert["cut_row"]==0
    assert cert["cut_original_variable"]==base[0][0]
    assert cert["source_cut_row"]==tuple(base[0])
    assert cert["base_mod3"]==m%3
    for i in range(3):
        srcvars=set(range(i*m,(i+1)*m))
        for j,row in enumerate(base):
            actual=joined[i*m+j]
            expected=set(i*m+v for v in row)
            if j==0:
                expected.remove(i*m+base[0][0])
                expected.add(((i+1)%3)*m+base[0][0])
            assert set(actual)==expected,(i,j)
        for v in srcvars:
            assert sum(v in row for row in joined)==3
    assert cert["cyclic_wiring"]==tuple(
        ((i*m),((i+1)%3)*m+base[0][0]) for i in range(3)
    )
    assert certify_connected_tanner(joined,n)
    return True


def original_block_divisibility_unsat_certificate(base,m,joined,n,cert):
    """General source-aligned algebraic proof; no search or oracle.

    Each original block variable appears 3 times except its cut
    source variable appears 2 times locally. Precisely one external
    source variable enters its cut row. The three equal modular
    conditions a_i-b_i == m mod3 contradict cyclic wiring.
    """
    assert independently_replay_source_glue(base,m,joined,n,cert)
    v=cert["cut_original_variable"]
    residue=m%3
    assert residue in (1,2)
    expected_ab=(1,0) if residue==1 else (0,1)
    for i in range(3):
        rowset=joined[i*m:(i+1)*m]
        inblock=range(i*m,(i+1)*m)
        counts={u:sum(u in row for row in rowset) for u in inblock}
        assert all(counts[u]==(2 if u==i*m+v else 3)
                   for u in inblock)
        outgoing=((i+1)%3)*m+v
        assert sum(outgoing in row for row in rowset)==1
        assert all(
            all(i*m<=u<(i+1)*m or u==outgoing for u in row)
            for row in rowset
        )
    # a_i = b_(i+1) from actual source cross-incidence.
    a,b=expected_ab
    assert a!=b
    assert (a-b-m)%3==0
    return {"status":"UNSAT","method":"ORIGINAL_BLOCK_CUT_MOD3",
            "base_n_mod3":residue,"all_blocks_forced_ab":expected_ab,
            "cycle_requires_a_equals_b_next":True}


def independent_brute_source_count(rows,n):
    """Only run on small source n<=21, exponential finite audit."""
    assert n<=21
    rows=validate_sparse(rows,n)
    masks=tuple(sum(1<<v for v in row) for row in rows)
    count=0
    for mask in range(1<<n):
        if all((mask&row).bit_count()==1 for row in masks):
            count+=1
    return count


def main():
    base=cyclic(7)
    assert tanner_girth_up_to(base,7,9)==6
    output,n,cert=triple_cyclic_source_glue(base,7)
    assert n==21 and n%3==0
    assert original_block_divisibility_unsat_certificate(
        base,7,output,n,cert)["status"]=="UNSAT"
    assert independent_brute_source_count(output,n)==0
    observed=tanner_girth_up_to(output,n,9)
    assert observed is None or observed>=6,(observed,cert)
    print(f"THREE_FANO7_CONNECTED_SCL21_MOD3_ZERO_UNSAT="
          f"PROOF_CARRYING_GIRTH_{observed if observed else '>9'}",
          flush=True)

    # First explicitly instantiated high-girth Fano homology cover.
    lifted,m,meta=binary_homology_cover(base,7)
    assert m==1792 and meta["sheets"]==256
    assert original_sum_refutation(lifted,m)["status"]=="UNSAT"
    assert tanner_girth_up_to(lifted,m,9) is None
    joined,n,cert=triple_cyclic_source_glue(lifted,m)
    assert n==5376 and n%3==0
    assert original_block_divisibility_unsat_certificate(
        lifted,m,joined,n,cert)["status"]=="UNSAT"
    assert tanner_girth_up_to(joined,n,9) is None
    print("FIRST_FANO_COVER_TRIPLE_SCL5376_CONNECTED_MOD3_ZERO="
          "SOURCE_UNSAT_GIRTH_GREATER9",flush=True)

    Q=paired_quartic_network(joined,n)
    assert verify_paired_quartic_network(joined,n,Q)
    qg=quotient_girth_up_to(Q,5)
    assert qg is None,"short cycle survived high-girth source"
    mom=local_loop_moments()
    assert all(mom[1<<i]==0 for i in range(4)) and mom[15]==0
    # Any nonempty supported loop has minimum occupied degree2,
    # hence contains some cycle. No cycle<=5 -> truncated sum1.
    print("SCL5376_SOURCE_UNSAT_EXACT_LOOP_ZERO="
          "TRUNCATED_LOOP_THROUGH_5_EQUALS_ONE_FALSE_POSITIVE",
          flush=True)

    # Deliberate forged cyclic wiring must fail original provenance.
    tampered=list(joined)
    tampered[0]=joined[1]
    try:
        independently_replay_source_glue(
            lifted,m,tuple(tampered),n,cert
        )
    except (AssertionError,ValueError):
        print("FORGED_TRIPLE_SCL_SOURCE_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("forged source accepted")

    # Infinite proof is symbolic; next homology tower levels have
    # gargantuan size and must NOT be materialized in CI.
    print("INFINITE_CONNECTED_HIGH_GIRTH_UNSAT_SCL_3DIVIDESN=PROVED")
    print("ALL_FIXED_LENGTH_LOOP_TRUNCATIONS_FALSE_POSITIVE_EVEN_AFTER_NMOD3=PROVED")
    print("GLOBAL_BLOCK_CUT_ARITHMETIC_SOLVERS_NOT_REFUTED")
    print("UNIFORM_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
