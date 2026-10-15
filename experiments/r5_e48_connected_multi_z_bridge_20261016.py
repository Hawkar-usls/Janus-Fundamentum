#!/usr/bin/env python3
"""E4.8 CROSS_COMPONENT_EDGE_SWAP_MULTI_Z: constructive connected UNSAT base.

All-n theorem:
Given UNSAT legal connected cubic linear SCL A and SAT legal
connected cubic linear SCL B, choose two distinct B SAT witnesses
x1,x2 with same bit t on variable b; choose a in A such that
the *ternary* AyA=2 witness obeys yA[a]=1-t. Swap exactly the
incidences (r,a) in A and (s,b) in B, where r/s contain a/b.
The source C remains legal cubic linear, becomes connected, and
is UNSAT: for any putative C Boolean exact-one x,
sum over A rows gives nA=3*sum(x_A)-x_a+x_b,
so x_a=x_b mod3 (nA divisible by3). Since x bits are Boolean
x_a=x_b, the switch can be undone without changing row sums,
and x_A would solve A, contradiction.
Each y_i=(yA,1-x_i^B) solves integer C*y=2, because
yA[a]=1-x_i^B[b]. Their distinct parity z_i=y_i mod2
are in Z(C), so |Z(C)|>=2.

Cross-switch uses two cross-edges: it creates an explicit
size-two EDGE cut, not a hard/expanding source. The construction
proves base Z feasibility only; it does not guarantee all z
can be activated by one signed 2-lift.

Extra: solve a single GF2 linear system for sheet voltages
sigma_(row,col) and a separate sheet label lambda_(i,col)
for each required ternary witness y_i. Every source row of
type (1,1,0) imposes
lambda_j+lambda_k+sigma_(row,j)+sigma_(row,k)=1.
If this system has a solution, build a SAT 2-lift realizing
ALL specified z simultaneously, with explicit 90-bit witnesses.
This joint result is only claimed after integer Exact-One
verification. No P=NP claim or timeouts-as-UNSAT.
"""
import argparse
import hashlib
import json
from collections import Counter,deque
from itertools import combinations
from pathlib import Path

from r5_cooperative_scl_coverage_20261015 import (
    fixtures,validate_scl,valid_witness,fingerprint
)
from r5_e47_base_z_rational_audit_20261016 import (
    low_pivot_kernel,residual_two_ways,rational_rref
)
from r5_e46_clean_room_verify_20261016 import (
    affine_exact_oracle
)


def exact_sat_words(rows,cap=1<<15):
    n=len(rows)
    r,basis=low_pivot_kernel([sum(1<<v for v in row)
                              for row in rows],n)
    d=len(basis)
    if 1<<d>cap:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","d":d}
    full=(1<<n)-1
    sat=[]
    for seed in range(1<<d):
        v=0
        for i,b in enumerate(basis):
            if (seed>>i)&1:v^=b
        x=v^full
        if all(sum((x>>j)&1 for j in row)==1 for row in rows):
            assert valid_witness(rows,x)
            sat.append(x)
    return {"status":"EXACT","rank":r,"d":d,
            "checked":1<<d,"count":len(sat),"witnesses":sat}


def incidence_component_sizes(rows):
    n=len(rows)
    neighbors=[[] for _ in range(2*n)]
    for i,row in enumerate(rows):
        for v in row:
            neighbors[i].append(n+v)
            neighbors[n+v].append(i)
    remaining=set(range(2*n))
    components=[]
    while remaining:
        start=min(remaining)
        queue=[start]
        remaining.remove(start)
        seen=[]
        while queue:
            u=queue.pop()
            seen.append(u)
            for v in neighbors[u]:
                if v in remaining:
                    remaining.remove(v);queue.append(v)
        components.append(tuple(sorted(seen)))
    return components


def select_shared_solutions(B,min_group):
    sat=exact_sat_words(B)
    assert sat["status"]=="EXACT"
    groups=[]
    for b in range(len(B)):
        for t in (0,1):
            agreeing=[x for x in sat["witnesses"] if ((x>>b)&1)==t]
            groups.append((len(agreeing),b,t,agreeing))
    maxcount=max(g[0] for g in groups)
    picked=next(g for g in groups if g[0]==maxcount)
    assert picked[0]>=min_group
    return sat,picked


def bridge(A,B,yA,min_common):
    nA=len(A)
    assert len(yA)==nA
    assert all(v in (0,1,2) for v in yA)
    assert all(sum(yA[v] for v in row)==2 for row in A)
    assert len(incidence_component_sizes(A))==1
    assert len(incidence_component_sizes(B))==1
    Aoracle=exact_sat_words(A)
    assert Aoracle["status"]=="EXACT" and Aoracle["count"]==0
    Bsat,(cnt,b,t,agreeing)=select_shared_solutions(B,min_common)
    a=next(j for j,value in enumerate(yA) if value==1-t)
    r=next(i for i,row in enumerate(A) if a in row)
    s=next(i for i,row in enumerate(B) if b in row)
    nB=len(B);n=nA+nB
    expanded=[list(row) for row in A]+[
        [nA+j for j in row] for row in B]
    expanded[r].remove(a);expanded[r].append(nA+b)
    expanded[nA+s].remove(nA+b);expanded[nA+s].append(a)
    C=validate_scl(expanded)
    assert len(C)==n
    assert len(incidence_component_sizes(C))==1
    # A's row labels were shuffled by validate_scl(C):
    # preserve a LEGAL deterministic original ordering for
    # exact voltage/witness construction and divide by source.
    C_ordered=tuple(tuple(sorted(row)) for row in expanded)
    assert validate_scl(C_ordered)==C
    crossedges=[]
    for i,row in enumerate(C_ordered):
        for v in row:
            if (i<nA)!=(v<nA):crossedges.append((i,v))
    assert len(crossedges)==2
    graph=incidence_component_sizes(C_ordered)
    assert len(graph)==1
    # The cut is exact: after removing the two crossedges the
    # bipartite incidence graph has components of 2*nA,2*nB.
    assert no_cross_subgraphs_connected(C_ordered,nA)
    Y=[]
    for x in agreeing:
        yi=list(yA)+[1-((x>>j)&1) for j in range(nB)]
        assert len(yi)==n
        assert yi[a]==yi[nA+b]==1-t
        assert all(sum(yi[j] for j in row)==2 for row in C_ordered)
        z=sum(1<<j for j,val in enumerate(yi) if val&1)
        assert z!=0 and all((sum((z>>j)&1 for j in row)%2)==0
                               for row in C_ordered)
        Y.append({"B_SAT_bits":x,"y":yi,"z":z})
    assert len(set(item["z"] for item in Y))==len(Y)>=min_common
    result={
        "n":n,"base_A_n":nA,"base_B_n":nB,
        "base_A_UNSAT_parity_checked":Aoracle["checked"],
        "B_exact_SAT_count":Bsat["count"],
        "B_exact_affine_checked":Bsat["checked"],
        "B_shared_coordinate":b,"B_shared_bit":t,
        "matching_A_column":a,
        "switched_A_row":r,"switched_B_row_local":s,
        "cross_edges":crossedges,
        "connected":True,"linear_cubic":True,
        "two_edge_cut_components":[2*nA,2*nB],
        "certified_constructed_distinct_z":len(Y),
        "constructed_z":[str(item["z"]) for item in Y],
        "constructed_z_weights":[item["z"].bit_count() for item in Y],
        "constructed_ternary_y":Y,
        "proof_of_UNSAT":"mod3 sum A rows forces x_a=x_b; undo switch implies SAT base A",
        "base_C_rows":[list(row) for row in C_ordered],
        "C_sha256":fingerprint(C)
    }
    return C_ordered,Y,result


def no_cross_subgraphs_connected(C,nA):
    n=len(C)
    for row_selector, col_selector in (
        (list(range(nA)),set(range(nA))),
        (list(range(nA,n)),set(range(nA,n)))
    ):
        # Strip crossedges. Every original component
        # loses ONE incidence; the removed edge is no
        # bridge in a 3-regular bipartite component.
        col_list=sorted(col_selector)
        adj={("r",i):[] for i in row_selector}
        adj.update({("c",j):[] for j in col_list})
        for i in row_selector:
            for j in C[i]:
                if j in col_selector:
                    adj[("r",i)].append(("c",j))
                    adj[("c",j)].append(("r",i))
        first=("r",row_selector[0])
        visited={first};q=[first]
        while q:
            u=q.pop()
            for v in adj[u]:
                if v not in visited:visited.add(v);q.append(v)
        if len(visited)!=len(adj):
            return False
    return True


def affine_solver(equations,width):
    # Every equation is (mask, rhs); use low pivot
    # GF2 integer echelon with an augmented right bit.
    mat=[mask | ((rhs&1)<<width) for mask,rhs in equations]
    rank=0
    for col in range(width):
        pivot=next((j for j in range(rank,len(mat))
                    if (mat[j]>>col)&1),None)
        if pivot is None:continue
        mat[rank],mat[pivot]=mat[pivot],mat[rank]
        for j in range(len(mat)):
            if j!=rank and ((mat[j]>>col)&1):
                mat[j]^=mat[rank]
        rank+=1
    if any((word&((1<<width)-1))==0 and
           ((word>>width)&1) for word in mat):
        return None,rank
    # LOW-pivot echelon: free variables ZERO; each
    # leading row has its pivot column with bit1,
    # so RHS assigned to pivot yields a solution.
    v=0
    for i in range(rank):
        row=mat[i]
        pivot=(row&-row).bit_length()-1
        if (row>>width)&1:v|=1<<pivot
    assert all(((mask&v).bit_count()&1)==rhs
               for mask,rhs in equations)
    return v,rank


def joint_cover(C,Y):
    n=len(C)
    E=[(i,v) for i,row in enumerate(C) for v in row]
    lookup={e:k for k,e in enumerate(E)}
    W=len(E)
    lam={}
    for k,item in enumerate(Y):
        for v,value in enumerate(item["y"]):
            if value==1:
                lam[(k,v)]=W+len(lam)
    equations=[]
    for k,item in enumerate(Y):
        y=item["y"]
        for i,row in enumerate(C):
            two=[v for v in row if y[v]==1]
            doubles=[v for v in row if y[v]==2]
            if doubles:
                assert len(doubles)==1 and not two
            else:
                assert len(two)==2
                j,h=two
                mask=((1<<lookup[(i,j)])|(1<<lookup[(i,h)])|
                      (1<<lam[(k,j)])|(1<<lam[(k,h)]))
                equations.append((mask,1))
    solution,r=affine_solver(equations,W+len(lam))
    if solution is None:
        return {"status":"JOINT_GF2_VOLTAGE_INCONSISTENT",
                "equations":len(equations),"rank":r},None
    sigma=solution&((1<<W)-1)
    rows=[]
    for sheet in (0,1):
        for i,row in enumerate(C):
            rows.append(tuple(v+n*(sheet^((sigma>>lookup[(i,v)])&1))
                              for v in row))
    lifted=validate_scl(rows)
    assert len(incidence_component_sizes(rows))==1
    witnesses=[]
    for k,item in enumerate(Y):
        bits=0
        for v,val in enumerate(item["y"]):
            if val==2:
                bits|=(1<<v)|(1<<(n+v))
            elif val==1:
                sheet=(solution>>lam[(k,v)])&1
                bits|=1<<(v+n*sheet)
        assert valid_witness(rows,bits)
        witnesses.append(bits)
    assert len(set(witnesses))==len(Y)
    full=(1<<n)-1
    swapped=[((w&full)<<n)|(w>>n) for w in witnesses]
    for k,(w,w2) in enumerate(zip(witnesses,swapped)):
        assert w!=w2 and valid_witness(rows,w2)
        assert (((w&full)^(w>>n))==Y[k]["z"])
        assert (((w2&full)^(w2>>n))==Y[k]["z"])
    assert len(set(witnesses+swapped))==2*len(Y)
    return {
        "status":"JOINT_SAT_2LIFT_WITNESSES_VERIFIED",
        "linear_GF2_equations":len(equations),
        "linear_GF2_rank":r,
        "sign_bitmask_decimal":str(sigma),
        "2lift_sha256":fingerprint(lifted),
        "2lift_connected":True,
        "witness_bits_decimal":[str(x) for x in witnesses],
        "witness_sheet_XOR":[str(item["z"]) for item in Y],
        "distinct_valid_SAT_witnesses":len(witnesses),
        "directly_verified_sheet_swap_witnesses":2*len(Y),
        "sheet_swapped_witness_bits_decimal":[str(w) for w in swapped],
        "2lift_rows":[list(row) for row in rows]
    },rows


def run():
    data=json.loads(Path(__file__).with_name(
        "r5_e46_frozen_fixture_20261016.json").read_text())
    A=tuple(tuple(row) for row in data["base_rows"])
    assert fingerprint(validate_scl(A))==data["source_sha256"]
    yA=tuple(data["ternary_y"])
    results={}
    for name,expected in (("AffinePlane9_SAT",2),("HolyerK4_SAT",3)):
        B=fixtures()[name]
        C,Y,report=bridge(A,B,yA,expected)
        oracle=exact_sat_words(C,1<<15)
        assert oracle["status"]=="EXACT" and oracle["count"]==0
        report["C_UNSAT_full_GF2_oracle"]={
            "rank":oracle["rank"],"nullity":oracle["d"],
            "checked":oracle["checked"],"exact_SAT_count":oracle["count"]}
        AR=[[int(j in row) for j in range(len(C))] for row in C]
        rational_rank,*_=rational_rref(AR)
        assert len(C)-rational_rank>=2
        report["rational_rank"]=rational_rank
        report["rational_nullity"]=len(C)-rational_rank
        # Further exact base-only audit when GF2 d is small.
        if oracle["d"]<=13:
            _,basis=low_pivot_kernel(
                [sum(1<<v for v in row) for row in C],len(C))
            zs=[0]
            for b in basis:zs.extend([z^b for z in tuple(zs)])
            feasible=[]
            Ytot=0
            for z in sorted(zs):
                if not z:continue
                f=residual_two_ways(C,z)
                if f["Y_count"]:
                    feasible.append({"z_decimal":str(z),
                                     "Y_count":f["Y_count"],
                                     "w":z.bit_count()})
                    Ytot+=f["Y_count"]
            report["complete_Z_A"]={
                "all_nonzero_z_checked":len(zs)-1,
                "feasible_z":feasible,"Z_size":len(feasible),
                "all_Y_totals":Ytot}
            assert len(feasible)>=expected
        cover,rows=joint_cover(C,Y[:expected])
        report["JOINT_COVER"]=cover
        results[name]=report
    return {
        "gate":"E4_8_CROSS_COMPONENT_EDGE_SWAP_MULTI_Z",
        "proof_all_n":"mod3 preserved UNSAT and identical edge-value preserves ternary Ay=2",
        "source_connected_UNSAT_certificate":"frozen SCL36 64-word GF2 oracle",
        "controls":results,
        "independent_graph_hardness":"NO; explicit two-edge cut",
        "depth1_spectral_SAT_UNSAT_twins":"NOT_ESTABLISHED",
        "universal_poly_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.parse_args()
    print(json.dumps(run(),indent=2,sort_keys=True))
