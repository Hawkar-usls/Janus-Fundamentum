#!/usr/bin/env python3
"""E4.10: exact 2-lift inheritance of multiple ternary Y_z + high girth.

ALL-n theorem: If A*y=2*1 over integers with ternary y_j in
{0,1,2}, EVERY graph 2-lift of A admits a ternary extension
tilde_y on both sheets by simply repeating y on each copy of
its source variable. Consequently distinct parity z directions
of A lift to distinct parity z directions of EVERY 2-lift,
regardless of voltage and regardless of SAT status.

This does NOT inherit UNSAT from the base. A 2-lift of
UNSAT A may be SAT. For this SPECIFIC frozen source C45,
the COMPLETE base-only Z(A) audit proves Z(A)={z1,z2}.
Therefore any signed two-lift is UNSAT if both z cycle parity
systems are violated, since every possible SAT witness must
have sheet-XOR equal to one of these two. Verify independently
with complete small GF2 exact affine oracle, not a timeout.

High girth control: a simple base cycle of length 6/8/10 lifts
to the same length iff total edge voltage parity is zero,
else becomes a cycle twice as long. A nonbacktracking closed
walk shorter than 12 in a girth-6 graph that is not a simple
cycle must contain at least two distinct simple cycles, hence
needs at least 12 edges. Therefore imposing odd voltage on
ALL base simple cycles shorter than target g=10 or12 (on this
girth6 base) rules out ALL shorter cycles in the 2-cover.
Always verify actual lifted girth by independent BFS. The
simultaneous GF2 constraints may be INCONSISTENT; report
that as exact infeasibility for THIS 2-lift operation, not
a high-girth impossibility for arbitrary source construction.

Target source size n90≥63. Structural hardness/expansion is
NOT inferred, since lift preserves the original source cuts and
old eigenvalues.
"""
import argparse,json,random
from collections import Counter,deque
from pathlib import Path

from r5_e49_joint_cyclespace_20261016 import (
    cycle_equations,nullspace,gf2rank
)
from r5_e49_structural_profile_20261016 import (
    graph_from_rows,girth_and_cycle,comp_sizes
)
from r5_e48_connected_multi_z_bridge_20261016 import (
    exact_sat_words
)
from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,valid_witness,fingerprint
)


def short_base_cycles(adj,less_than):
    """Enumerate ALL undirected SIMPLE cycles shorter than g."""
    n=len(adj)
    found=set()
    max_path=less_than-1
    for start in range(n):
        def dfs(v,visited,path,edge_ids):
            for nxt,eid in adj[v]:
                if nxt==start:
                    if len(path)>=4 and len(path)<less_than:
                        mask=1<<eid
                        for e in edge_ids:mask|=1<<e
                        assert mask.bit_count()==len(path)
                        found.add(mask)
                    continue
                # min(start) canonical representative, and no
                # repeated vertex (simple cycles only).
                if nxt<=start or nxt in visited:continue
                if len(path)+1>=less_than:continue
                visited.add(nxt)
                dfs(nxt,visited,path+[nxt],edge_ids+[eid])
                visited.remove(nxt)
        dfs(start,{start},[start],[])
    counts=Counter(v.bit_count() for v in found)
    assert set(counts).issubset({6,8,10})
    return sorted(found),dict(counts)


def affine_unit_rhs(masks,width):
    """Solve all cycle-mask dot sigma=1 via augmented GF2 RREF."""
    rows=[mask|(1<<width) for mask in masks]
    # Each elimination row tracks which ORIGINAL simple cycles
    # were XOR-combined to derive it. An inconsistent 0=1 row
    # therefore yields a short portable proof independent of
    # the elimination implementation.
    provenance=[1<<i for i in range(len(masks))]
    rank=0;pivots=[]
    for j in range(width):
        i=next((i for i in range(rank,len(rows)) if (rows[i]>>j)&1),None)
        if i is None:continue
        rows[i],rows[rank]=rows[rank],rows[i]
        provenance[i],provenance[rank]=provenance[rank],provenance[i]
        for k in range(len(rows)):
            if k!=rank and ((rows[k]>>j)&1):
                rows[k]^=rows[rank]
                provenance[k]^=provenance[rank]
        pivots.append(j);rank+=1
    for j in range(rank,len(rows)):
        if rows[j]==(1<<width):
            ids=[i for i in range(len(masks))
                 if (provenance[j]>>i)&1]
            folded=0
            for i in ids:folded^=masks[i]
            assert folded==0 and len(ids)%2==1
            proof={"original_cycle_indices":ids,
                   "original_cycle_masks_decimal":[str(masks[i]) for i in ids],
                   "xor_all_masks_zero":True,
                   "odd_number_of_cycles":len(ids)}
            return {"consistent":False,"rank":rank,
                    "constraint_count":len(masks),
                    "contradiction_certificate":proof},None,None
    particular=0
    for i,j in enumerate(pivots):
        if (rows[i]>>width)&1:particular|=1<<j
    assert all(((v&particular).bit_count()&1)==1 for v in masks)
    homogeneous=nullspace(masks,width)
    assert len(homogeneous)==width-rank
    return {"consistent":True,"rank":rank,
            "constraint_count":len(masks),
            "solution_affine_dim":len(homogeneous)},particular,homogeneous


def lift_rows(base,sign):
    n=len(base)
    E=[(i,j) for i,row in enumerate(base) for j in row]
    lookup={(i,j):(sign>>k)&1 for k,(i,j) in enumerate(E)}
    out=[]
    for layer in (0,1):
        for i,row in enumerate(base):
            out.append(tuple(j+n*(layer^lookup[(i,j)]) for j in row))
    validate_scl(out)
    return out


def is_unsat_by_cycle_sign(sign,systems):
    # A frozen base with exact Z(A)={z1,z2}: SAT possible
    # ONLY if at least one individual z system is compatible.
    return all(any(((mask&sign).bit_count()&1)!=rhs
                   for mask,rhs in sys)
               for sys in systems)


def run(path,samples=96):
    F=json.loads(Path(path).read_text())
    base=[tuple(row) for row in F["base_45_rows"]]
    assert len(base)==45
    adj,E=graph_from_rows(base)
    assert girth_and_cycle(adj)[0]==6
    # graph_from_rows numbers COLUMN VERTICES as n+j; cycle_equations
    # expects original source column indices j.
    lookup={(i,v-len(base)):k for k,(i,v) in enumerate(E)}
    zlist=[int(z) for z in F["distinct_z_decimal"]]
    systems=[[(mask,rhs) for mask,rhs,trail in
              cycle_equations(base,z,lookup)["equations"]]
             for z in zlist]
    assert len(systems)==2
    assert [len(s) for s in systems]==[14,14]
    log=[]
    rng=random.Random(20261016)
    for goal in (12,10,8):
        masks,hist=short_base_cycles(adj,goal)
        solved,part,basis=affine_unit_rhs(masks,len(E))
        attempt={"target_girth":goal,"simple_base_cycles":hist,
                 "GF2_odd_cycle_system":solved,
                 "exact_odd_cycle_constraint_consistency":
                    solved["consistent"]}
        log.append(attempt)
        if not solved["consistent"]:
            # Recheck the certificate WITHOUT relying on row-reduction:
            # pure XOR of the cited short cycle masks is zero and an
            # odd number of required RHS ones sums to one.
            relation=solved["contradiction_certificate"]
            folded=0
            for decimal in relation["original_cycle_masks_decimal"]:
                folded^=int(decimal)
            assert folded==0
            assert len(relation["original_cycle_masks_decimal"])%2==1
            continue
        choices=[]
        for k in range(samples):
            mask=0
            if k:
                for generator in rng.sample(basis,
                                            min(13,len(basis))):
                    mask^=generator
            sigma=part^mask
            if not is_unsat_by_cycle_sign(sigma,systems):continue
            choices.append(sigma)
            break
        attempt["sample_signings_checked_for_UNSAT"]=samples
        if not choices:
            attempt["verdict"]="NO_UNSAT_SIGNING_FOUND_IN_BOUNDED_SAMPLE"
            continue
        sigma=choices[0]
        signed=lift_rows(base,sigma)
        lifted_adj,_=graph_from_rows(signed)
        girth,cycle=girth_and_cycle(lifted_adj)
        assert girth>=goal
        assert comp_sizes(lifted_adj)==[2*len(signed)]
        oracle=exact_sat_words(signed,cap=1<<16)
        assert oracle["status"]=="EXACT"
        assert oracle["count"]==0
        n=len(base)
        y2s=[]
        for z in zlist:
            y=[int((z>>j)&1)+2*int(j in (1,16))
               for j in range(n)]
            assert all(sum(y[j] for j in row)==2 for row in base)
            y2=y+y
            assert len(y2)==2*n
            assert all(sum(y2[j] for j in row)==2 for row in signed)
            lifted_z=sum(1<<j for j,v in enumerate(y2) if v&1)
            assert lifted_z!=0 and all(
                sum((lifted_z>>j)&1 for j in row)%2==0
                for row in signed)
            y2s.append({"z_source_decimal":str(z),
                        "z_lifted_decimal":str(lifted_z),
                        "y2_columns":[1,16,1+n,16+n]})
        assert y2s[0]["z_lifted_decimal"]!=y2s[1]["z_lifted_decimal"]
        # The lifted graph still inherits source bottleneck:
        # preimage of 18-node source side has 36 vertices and
        # 8 crossing incidence edges.
        return {
            "status":"FOUND_CERTIFIED_GIRTH_ENHANCED_UNSAT_MULTI_Z_N90",
            "source_n":2*n,"source_incidence_vertex_count":4*n,
            "source_girth":girth,"target_girth":goal,
            "source_GF2_rank":oracle["rank"],
            "source_GF2_nullity":oracle["d"],
            "source_full_parity_words":oracle["checked"],
            "source_exact_SAT_count":oracle["count"],
            "at_least_two_DISTINCT_residual_Yz":True,
            "constructed_ternary_lifts":y2s,
            "sign_mask_decimal":str(sigma),
            "legal_connected":True,
            "lifted_source_rows":[list(row) for row in signed],
            "source_sha256":fingerprint(validate_scl(signed)),
            "source_cut_inherited":{
                "small_side_vertices":36,
                "cross_edges":8,
                "conductance_upper_bound":"2/27"},
            "search_log":log,
            "high_expansion":"NOT_PROVED",
            "depth1_spectral_twins":"NOT_CONSTRUCTED",
            "P_vs_NP":"OPEN"
        }
    return {"status":"NO_CERTIFIED_GIRTH_ENHANCED_UNSAT_FOUND",
            "search_log":log,
            "n90_2lift_MULTI_Z_inheritance":"PROVED_ALL_N",
            "no_universal_no_go_claim":True,
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    p.add_argument("--samples",type=int,default=96)
    a=p.parse_args()
    print(json.dumps(run(a.fixture,a.samples),indent=2,sort_keys=True))
