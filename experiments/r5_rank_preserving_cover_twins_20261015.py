#!/usr/bin/env python3
"""R5 E4.4 — RANK_PRESERVING_COVER_TWINS, exact finite controls.

All-n theorems:
(1) SAT base => EVERY graph cover SAT via copy-constant assignment.
(2) SAT in SOME legal 2-lift <=> an integer ternary witness y in
    {0,1,2}^n with A*y=2*one. A witness directly constructs signs.
(3) A0+A1=A over GF2, lift(A0)=[[A0,A1],[A1,A0]]:
    rank(lift)=2*rank(A)+rank(L^T A0 K),
    where right/left null bases of A are K,L.
(4) Edge flip delta with L^T delta K=0 keeps full obstruction
    matrix and therefore lift rank. Gauge delta_(i,j)=p_i+q_j
    is a trivial sheet relabeling; connected graph gauge dim 2n-1.
    ker(Phi)/gauge dim = n+1-rank(Phi).

All statements concern graph *incidence* covers and exact SCL
constraints, not arbitrary matrix entry modifications.
Potential UNSAT for a changed covering is established ONLY by
exhaustive small-d GF2 affine enumeration; UNKNOWN is never UNSAT.
"""
from collections import Counter
from itertools import product
import argparse,json,random

from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,valid_witness,gf2_affine,fingerprint,fixtures
)
from r5_connected_coverage_breaker_20261015 import (
    make_connected,connected_scl_components
)
from r5_joint_spectral_anchor_twins_20261015 import (
    unrestricted_connected_mutation,classify_affine
)
from r5_local_codeword_anchors_20261015 import (
    linear_validate_and_incidence,local_codewords
)


def gf2_reduce_vectors(vectors):
    pivots={}
    independent=[]
    for original in vectors:
        rem=original
        while rem:
            top=rem.bit_length()-1
            if top not in pivots:
                pivots[top]=rem
                independent.append(original)
                break
            rem^=pivots[top]
    return independent


def gf2_rank(masks):
    return len(gf2_reduce_vectors(masks))


def gf2_nullspace(rows,width):
    pivots={}
    for row in rows:
        mask=int(row)
        while mask:
            k=mask.bit_length()-1
            if k not in pivots:
                pivots[k]=mask
                break
            mask^=pivots[k]
    free=[v for v in range(width) if v not in pivots]
    basis=[]
    for free_v in free:
        word=1<<free_v
        for pivot in sorted(pivots):
            mask=pivots[pivot]
            if ((mask&word).bit_count()&1):
                word|=1<<pivot
        basis.append(word)
    assert len(basis)==width-len(pivots)
    assert all(all((word&row).bit_count()%2==0 for row in rows)
               for word in basis)
    return tuple(basis)


def source_bitrows(rows):
    rows=validate_scl(rows)
    return tuple(sum(1<<v for v in r) for r in rows)


def transpose_bits(bitrows,n):
    return tuple(sum(1<<i for i,row in enumerate(bitrows)
                     if (row>>v)&1) for v in range(n))


def edge_list(rows):
    rows=validate_scl(rows)
    return tuple((i,j) for i,r in enumerate(rows) for j in r)


def phi_data(rows):
    """Phi: GF2^(3n) -> GF2^(d*d), using rank-preserving obstructions."""
    rows=validate_scl(rows)
    n=len(rows)
    bits=source_bitrows(rows)
    right=gf2_nullspace(bits,n)
    left=gf2_nullspace(transpose_bits(bits,n),n)
    d=len(right)
    assert len(left)==d
    edges=edge_list(rows)
    images=[]
    for i,j in edges:
        lo=sum(1<<a for a,vec in enumerate(left) if (vec>>i)&1)
        ri=sum(1<<b for b,vec in enumerate(right) if (vec>>j)&1)
        out=0
        for a in range(d):
            if (lo>>a)&1:
                out^=ri<<(a*d)
        images.append(out)
    phi_rank=gf2_rank(images)
    assert len(images)==3*n
    eqs=tuple(sum(1<<idx for idx,out in enumerate(images)
                  if (out>>coordinate)&1)
              for coordinate in range(d*d))
    ker=gf2_nullspace(eqs,3*n)
    gauge=[]
    for i in range(n):
        gauge.append(sum(1<<q for q,(r,j) in enumerate(edges) if r==i))
    for v in range(n):
        gauge.append(sum(1<<q for q,(r,j) in enumerate(edges) if j==v))
    gr=gf2_rank(gauge)
    assert gr==2*n-1
    assert all(phi_apply(images,g)==0 for g in gauge)
    echelon=list(gauge)
    non_gauge=[]
    for k in ker:
        if gf2_rank(echelon+[k])>gf2_rank(echelon):
            non_gauge.append(k)
            echelon.append(k)
    qdim=n+1-phi_rank
    assert len(non_gauge)==qdim
    return {"n":n,"d":d,"edges":edges,
            "right":right,"left":left,
            "rankA":n-d,"images":images,"phi_rank":phi_rank,
            "gauge_rank":gr,"ker_dim":len(ker),
            "quotient_dim":qdim,
            "non_gauge_basis":tuple(non_gauge)}


def phi_apply(images,delta):
    value=0
    while delta:
        bit=delta&-delta
        delta^=bit
        value^=images[bit.bit_length()-1]
    return value


def signmask_from_signs(edges,signs):
    return sum(1<<i for i,e in enumerate(edges) if signs.get(e,0))


def lift_rows(rows,signs):
    rows=validate_scl(rows)
    n=len(rows)
    built=[]
    for sheet in (0,1):
        for i,row in enumerate(rows):
            built.append(tuple(j+n*(sheet^signs.get((i,j),0))
                               for j in row))
    return validate_scl(built)


def delta_to_signs(edges,sat_signs,delta):
    return {e:sat_signs.get(e,0)^((delta>>q)&1)
            for q,e in enumerate(edges)}


def check_rank_formula(rows,signs,data=None):
    data=phi_data(rows) if data is None else data
    edges=data["edges"]
    signs_mask=signmask_from_signs(edges,signs)
    # WARNING: rank-of-COLUMNS is NOT rank of XOR-AGGREGATED Phi(signs).
    # Correct obstruction matrix is a SINGLE d*d bit-vector, with
    # rank over GF2 after interpreting its d rows.
    word=phi_apply(data["images"],signs_mask)
    d=data["d"]
    obstruction_rows=[(word>>(a*d))&((1<<d)-1) for a in range(d)]
    t=gf2_rank(obstruction_rows)
    lift=lift_rows(rows,signs)
    actual=gf2_rank(source_bitrows(lift))
    predicted=2*data["rankA"]+t
    assert actual==predicted,(actual,predicted,d)
    return {"base_rank":data["rankA"],"obstruction_rank":t,
            "lift_rank":actual,"lift_nullity":2*len(rows)-actual}


def integer_two_cover_witness(rows,node_budget=12000):
    """Exhaustive ternary domain propagation with honest bounded UNKNOWN.

    Each original clause y_i+y_j+y_k=2 has precisely 6 triples:
    permutations of (2,0,0) and (1,1,0).
    """
    rows=validate_scl(rows)
    n=len(rows)
    if (2*n)%3:
        return {"status":"UNSAT","reason":"3 sum(y)=2n contradiction",
                "nodes":0}
    triples=((2,0,0),(0,2,0),(0,0,2),
             (0,1,1),(1,0,1),(1,1,0))
    calls=0
    budget_hit=False
    def dfs(domains):
        nonlocal calls,budget_hit
        if calls>=node_budget:
            budget_hit=True
            return None
        calls+=1
        D=list(domains)
        while True:
            changed=False
            for i,j,k in rows:
                legal=[t for t in triples if
                       ((D[i]>>t[0])&1) and
                       ((D[j]>>t[1])&1) and
                       ((D[k]>>t[2])&1)]
                if not legal:return None
                for v,index in ((i,0),(j,1),(k,2)):
                    mask=0
                    for t in legal:mask|=1<<t[index]
                    new=D[v]&mask
                    if not new:return None
                    if new!=D[v]:
                        changed=True
                        D[v]=new
            if not changed:break
        if all(d.bit_count()==1 for d in D):
            y=tuple(d.bit_length()-1 for d in D)
            assert all(sum(y[v] for v in row)==2 for row in rows)
            return y
        options=[(d.bit_count(),v) for v,d in enumerate(D)
                 if d.bit_count()>1]
        _,idx=min(options)
        for value in range(3):
            if (D[idx]>>value)&1:
                trial=D[:]
                trial[idx]=1<<value
                result=dfs(tuple(trial))
                if result is not None:return result
                if budget_hit:return None
        return None
    y=dfs((0b111,)*n)
    if y is not None:
        return {"status":"SAT_TERNARY_WITNESS",
                "y":y,"nodes":calls,
                "proof":"independent integer per-row sum 2"}
    return {"status":"UNKNOWN_RESOURCE_LIMIT" if budget_hit else
            "UNSAT_EXHAUSTIVE_TERNARY_DFS",
            "nodes":calls}


def sat_cover_from_y(rows,y):
    rows=validate_scl(rows)
    n=len(rows)
    if (len(y)!=n or any(v not in (0,1,2) for v in y) or
        any(sum(y[j] for j in row)!=2 for row in rows)):
        raise ValueError("invalid Ay=2 witness")
    signs={}
    for i,row in enumerate(rows):
        positives=[j for j in row if y[j]==1]
        twos=[j for j in row if y[j]==2]
        if len(twos)==1:
            assert not positives
        else:
            assert len(twos)==0 and len(positives)==2
            signs[(i,positives[0])]=0
            signs[(i,positives[1])]=1
    witness=sum((1<<j if v>=1 else 0)|(1<<(n+j) if v==2 else 0)
                for j,v in enumerate(y))
    lift=lift_rows(rows,signs)
    assert valid_witness(lift,witness)
    return signs,witness,lift


def search_unsat_base(seed=20261015,attempts=20):
    original,_,_=make_connected(2,seed)
    rng=random.Random(seed)
    for t in range(attempts):
        trial,moves=unrestricted_connected_mutation(
            original,rng,steps=4+(t%11))
        check=classify_affine(trial,cap=1<<12)
        if check["verdict"]=="UNSAT":
            return trial,{"trial":t,"source_sha":fingerprint(trial),
                          "nullity":check["d"],
                          "oracle_words":check["checked"],
                          "unsat_proof":"complete 2^d GF2-affine enumeration"}
    return None,{"status":"NO_EXACT_UNSAT_IN_FINITE_ATTEMPTS"}


def run_gate():
    # Positive universal SAT-lift lemma on a legal SAT source.
    sat=fixtures()["HolyerK4_SAT"]
    x=classify_affine(sat,cap=1<<12)["witness_bits"]
    assert x is not None
    arbitrary={(i,j):(i*13+j*7+1)%2 for i,row in enumerate(sat)
               for j in row}
    lifted=lift_rows(sat,arbitrary)
    lifted_x=sum(((1<<j)|(1<<(len(sat)+j)))
                 for j in range(len(sat)) if (x>>j)&1)
    assert valid_witness(lifted,lifted_x)
    proof=phi_data(sat)
    formula=check_rank_formula(sat,arbitrary,proof)

    unsat,source=search_unsat_base()
    if unsat is None:
        return {"gate":"RANK_PRESERVING_COVER_TWINS",
                "SAT_LIFT_ALL_SIGNS":"PASS",
                "SAT_lemma_formula":formula,
                "source":source,
                "status":"NO_UNSAT_BASE_FOUND_IN_BUDGET",
                "P_vs_NP":"OPEN"}
    ternary=integer_two_cover_witness(unsat,node_budget=18000)
    result={"gate":"RANK_PRESERVING_COVER_TWINS",
            "SAT_LIFT_ALL_SIGNS":"PASS",
            "SAT_lemma_formula":formula,
            "UNSAT_base":source,
            "ternary_nodes":ternary["nodes"],
            "ternary_status":ternary["status"]}
    if ternary["status"]!="SAT_TERNARY_WITNESS":
        result["status"]="TWO_COVER_FEASIBILITY_NOT_CERTIFIED"
        result["P_vs_NP"]="OPEN"
        return result
    y=ternary["y"]
    signs,witness,lift=sat_cover_from_y(unsat,y)
    assert len(connected_scl_components(lift))==1
    frame=phi_data(unsat)
    initial=check_rank_formula(unsat,signs,frame)
    d_lift=initial["lift_nullity"]
    assert d_lift>=0
    result.update({"SAT_2lift_witness":witness,
                   "SAT_2lift_verified":True,
                   "base_ternary_witness":y,
                   "SAT_2lift_connected":True,
                   "base_phi_rank":frame["phi_rank"],
                   "gauge_dim":frame["gauge_rank"],
                   "rank_preserving_quotient_dim":frame["quotient_dim"],
                   "initial_cover":initial})
    rng=random.Random(20261015)
    basis=frame["non_gauge_basis"]
    tested=0
    counts=Counter()
    opposite=None
    for idx in range(min(30,len(basis)+16)):
        if idx<len(basis):
            delta=basis[idx]
        else:
            picks=rng.sample(basis,min(3,len(basis)))
            delta=0
            for v in picks:delta^=v
        assert phi_apply(frame["images"],delta)==0
        successor=delta_to_signs(frame["edges"],signs,delta)
        # algebraic: rank of obstruction matrix exactly invariant
        assert phi_apply(frame["images"],signmask_from_signs(
            frame["edges"],successor))==phi_apply(
            frame["images"],signmask_from_signs(frame["edges"],signs))
        trial=lift_rows(unsat,successor)
        estimate=check_rank_formula(unsat,successor,frame)
        assert estimate["lift_rank"]==initial["lift_rank"]
        assert estimate["lift_nullity"]==d_lift
        assert len(connected_scl_components(trial))==1
        verdict=classify_affine(trial,cap=1<<12)
        counts[verdict["verdict"]]+=1
        tested+=1
        if verdict["verdict"]=="UNSAT":
            opposite={
                "rank_preserving_non_gauge_delta":delta,
                "edge_flip_count":delta.bit_count(),
                "SAT_witness":witness,
                "UNSAT_GF2_nullity":verdict["d"],
                "UNSAT_checked":verdict["checked"],
                "SAT_cover_sha":fingerprint(lift),
                "UNSAT_cover_sha":fingerprint(trial),
                "both_connected":True,
                "same_rank":True,
                "spectral_twins":"NOT_YET_ESTABLISHED"
            }
            break
    result.update({"rank_preserving_candidates_checked":tested,
                   "candidate_verdicts":dict(counts),
                   "opposite_status_same_rank":opposite,
                   "status":"FOUND_SAT_UNSAT_SAME_LIFT_RANK" if opposite else
                            "NO_OPPOSITE_LIFT_IN_TESTED_BASIS",
                   "universal_poly_SCL":"NOT_CONSTRUCTED",
                   "P_vs_NP":"OPEN"})
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:p.error("--self-test")
    print(json.dumps(run_gate(),sort_keys=True,indent=2))
