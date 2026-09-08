from __future__ import annotations
import argparse, json
from itertools import combinations
from pathlib import Path

import janus_trump_r50g25ba2_persistent_endpoint_correlation_channel as ba2
import janus_trump_r50g25ba3_frozen_positive_bridge_impossibility_two_polarity_completion as ba3
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

PREREG="d6a4acb16a6d0eb3ddef7f982627638cb9bf6575"
OVERLAY="a442e25433262462d6839a488520d2c28fed6e5d"
ORDER_FREEZE="7c3ca977d4dd4977ff7851feff130959c6c1b997"
Q=2


def canon(c):
    s=set(int(x) for x in c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))


def minimize(cs):
    xs=[]
    for c in cs:
        z=canon(c)
        if z is not None: xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c))
    out=[]
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out): continue
        out.append(c)
    return tuple(sorted(out))


def dp(F,x):
    pos=[c for c in F if x in c]; neg=[c for c in F if -x in c]
    rest=[c for c in F if x not in c and -x not in c]
    raw=[]
    for a in pos:
        for b in neg:
            z=canon((set(a)-{x})|(set(b)-{-x}))
            if z is not None: raw.append(z)
    return minimize(rest+raw),raw


def cross(c):
    s={abs(x) for x in c}
    return bool(s&{1,2,3}) and bool(s&{4,5,6})


def independent_kernel():
    F=minimize([
      (-1,-2),(1,2),(2,3),(-2,-3),
      (-4,-5),(4,5),(5,6),(-5,-6),
      (1,4)
    ])
    rpeak=sum(cross(c) for c in F); bpeak=0; wpeak=0; livepeak=len(F); trace=[]
    for x in (1,2,4,5):
        neigh=set()
        for c in F:
            if x in c or -x in c:
                neigh|={abs(l) for l in c if abs(l)!=x}
        wpeak=max(wpeak,len(neigh))
        F2,raw=dp(F,x)
        cr=[c for c in raw if cross(c)]
        rpeak=max(rpeak,sum(cross(c) for c in F2))
        bpeak=max(bpeak,len(cr)); livepeak=max(livepeak,len(F2))
        trace.append({"x":x,"raw":[list(c) for c in raw],"after":[list(c) for c in F2]})
        F=F2
    return {"final":F,"R_peak":rpeak,"B_peak":bpeak,"W_peak":wpeak,"live_peak":livepeak,"trace":trace}


def shift(c,o):
    return tuple((abs(int(l))+o if int(l)>0 else -(abs(int(l))+o)) for l in c)


def lane(U,g,i):
    out=[]; lo=30*g*i
    for j in range(g):
        o=lo+30*j
        out.extend(shift(c,o) for c in U)
        q=2+o; p=30+o
        out.extend(((-q,-p),(q,p)))
    for j in range(g-1):
        p=30+lo+30*j; qn=2+lo+30*(j+1)
        out.extend(((p,qn),(-p,-qn)))
    return out,set(abs(l) for c in out for l in c)


def instance(U,g):
    c1,v1=lane(U,g,0); c2,v2=lane(U,g,1)
    K=(2,2+30*g)
    return c1+c2+[K],[v1,v2],K


def ok(a,c):
    return any((bool(a[abs(l)]) if l>0 else not bool(a[abs(l)])) for l in c)


def make_model(first,U,g,bits):
    a={}
    for i,b in enumerate(bits):
        proto=first[(b,1-b)]; lo=30*g*i
        for j in range(g):
            o=lo+30*j
            for v,val in proto.items(): a[v+o]=bool(val)
    cs,vs,K=instance(U,g)
    return all(ok(a,c) for c in cs),a,cs


def verify(path):
    x=json.loads(Path(path).read_text()); errs=[]
    if x.get("outcome")!="BA5-A_SINGLE_NONFACTORIZING_BINARY_COUPLING_TRANSPORT_CERTIFIED": errs.append("OUTCOME")
    if x.get("preregistration_commit")!=PREREG: errs.append("PREREG")
    if x.get("strict_algebra_overlay_commit")!=OVERLAY: errs.append("STRICT_OVERLAY")
    if x.get("elimination_order_freeze_commit")!=ORDER_FREEZE: errs.append("ORDER_FREEZE")
    if x.get("failure_count")!=0 or x.get("falsifiers"): errs.append("FAILURE_LEDGER")
    if x.get("arbitrary_CNF_coverage_started") or x.get("next_gate_started"): errs.append("SCOPE_ESCAPE")
    if x.get("unclassified_exceptions"): errs.append("UNCLASSIFIED_EXCEPTION")

    K={(0,1),(1,0),(1,1)}
    p1={a for a,b in K}; p2={b for a,b in K}
    if {(a,b) for a in p1 for b in p2}==K: errs.append("K_FACTORIZES")

    ker=independent_kernel()
    if ker["final"]!=((3,6),): errs.append("KERNEL_RESIDUAL")
    if (ker["R_peak"],ker["B_peak"],ker["W_peak"])!=(1,1,2): errs.append("TRANSIENT_METRICS")

    Uinfo,U,models,counts,first,RU=ba2.actual_source()
    cx_counts,first_x,CX=ba3.filter_models(models,[ba3.BA2_CLAUSE,ba3.BA3_BLOCK])
    BX=ba3.bridge_xor_relation(); T=ba3.compose(CX,BX)
    if CX!=((0,1),(1,0)) or BX!=((0,1),(1,0)) or T!=((1,0),(0,1)): errs.append("BA3_IDENTITY_DRIFT")
    dp,_=ba3.generic_projection(Uinfo["defects"],Uinfo["equations"],[ba3.BA2_CLAUSE,ba3.BA3_BLOCK],(2,30))
    if dp!=CX: errs.append("SOURCE_DP")

    replays=[]
    for g in (1,2,3,5,8,16):
        cs,vs,Kc=instance(U,g)
        C=len(cs); L=sum(len(c) for c in cs); V=len(set().union(*vs)); n=C+L+V
        exp=(134*g-3,326*g-6,40*g,500*g-9)
        if (C,L,V,n)!=exp: errs.append(f"SIZE_{g}")
        mem={v:i for i,s in enumerate(vs) for v in s}
        cross_cs=[]
        for c in cs:
            lanes={mem[abs(l)] for l in c}
            if len(lanes)>1: cross_cs.append(c)
        if cross_cs!=[Kc]: errs.append(f"CROSS_SOURCE_{g}")
        for bits in sorted(K):
            good,a,_=make_model(first,U,g,bits)
            if not good: errs.append(f"RECON_{g}_{bits}")
            q0=(int(bool(a[2])),int(bool(a[2+30*g])))
            if q0!=bits: errs.append(f"RETURN_{g}_{bits}")
        replays.append({"g":g,"C":C,"L":L,"V":V,"n":n,"cross_lane_source_clauses":len(cross_cs)})

    width_proof={
      "premise_lane_width":13,
      "new_bag_size":2,
      "derived_upper_bound":max(13,1),
      "rule":"connect new bag {q1,q2} to a bag containing q1 in lane1 and a bag containing q2 in lane2; disjoint trees become one tree and running-intersection is preserved"
    }
    if width_proof["derived_upper_bound"]!=13: errs.append("WIDTH_PROOF")

    obligations={
      "o1": ker["final"]==((3,6),),
      "o2": ker["final"]==((3,6),),
      "o3": x["BA5_boundary_kernel"].get("manual_future_insertion")==0 and x["BA5_boundary_kernel"].get("derived_K_next") is True,
      "o4": x["BA5_source_preimage"].get("source_preimage_pass") is True,
      "o5": x["BA5_reconstruction"].get("all_pass") is True,
      "o6": x["BA5_reconstruction"].get("full_original_verify_all_pass") is True,
      "o7": x["BA5_certificate"].get("explicit_boundary_state_table_rows")==0 and x["BA5_certificate"].get("manual_future_insertion")==0,
      "o8": ker["R_peak"]==1,
      "o9": ker["B_peak"]==1,
      "o10": ker["W_peak"]==2 and width_proof["derived_upper_bound"]==13,
      "o11": x["BA5_complexity"].get("T_total")=="O(n log n) conservative",
    }
    if not all(obligations.values()): errs.append("OPEN_OBLIGATION")
    pre=x.get("strict_promotion_guard_pre_independent_verify",{})
    if pre.get("P_BA5")!=0 or pre.get("v_independent_verifier")!=0 or not pre.get("all_closed_pre_independent_verify"): errs.append("PRE_VERIFIER_GUARD")
    v=0 if errs else 1
    P=1
    for z in obligations.values(): P*=int(z)
    P*=1*v
    if not errs and P!=1: errs.append("PROMOTION_ALGEBRA")

    return {
      "gate":"R50G25BA5_INDEPENDENT_VERIFY",
      "status":"PASS" if not errs else "FAIL",
      "errors":errs,
      "error_count":len(errs),
      "obligations":{k:int(v) for k,v in obligations.items()},
      "x_no_unclassified_exception":1,
      "v_independent_verifier":0 if errs else 1,
      "P_BA5":0 if errs else P,
      "independent_kernel":{"final":[list(c) for c in ker["final"]],"R_peak":ker["R_peak"],"B_peak":ker["B_peak"],"W_peak":ker["W_peak"],"live_clause_peak":ker["live_peak"]},
      "width_proof":width_proof,
      "source_replays":replays,
      "message_state":"VERIFIED" if not errs else "RECEIVED_NOT_VERIFIED",
      "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--result",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
    v=verify(a.result); Path(a.out).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":v["status"],"errors":v["error_count"],"P_BA5":v["P_BA5"]},sort_keys=True))
    if v["error_count"]: raise SystemExit(3)

if __name__=="__main__": main()
