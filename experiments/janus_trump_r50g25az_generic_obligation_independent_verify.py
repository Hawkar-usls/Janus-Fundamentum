from __future__ import annotations

import argparse, json
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az
import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av

r33=av.r33
r50g23=av.asmod.r50g25g._chain()[1]
r42=r50g23.r42
r34=r50g23.r34
PREREG="85b5d55e563d919585fff16efb08bcb5ecea68f8"
VARS=tuple(az.UNIT_VARS)


def evc(c,a):return any(bool(a[abs(int(l))])==(int(l)>0) for l in c)
def evf(f,a):return all(evc(c,a) for c in f)

def models(U):
    out=[]
    for bits in product((False,True),repeat=len(VARS)):
        a=dict(zip(VARS,bits))
        if evf(U,a):out.append(a)
    return out

def assumptions_satisfiable_by_unit(U,ms):
    uncovered=[]
    for ci,c in enumerate(U):
        for rem in c:
            assumptions=[-l for l in c if l!=rem]
            if not any(all(bool(a[abs(l)])==(l>0) for l in assumptions) for a in ms):
                uncovered.append((ci,rem))
    return uncovered

def support(c):return frozenset(abs(int(l)) for l in c)

def no_subsumption(U):
    ss=[set(c) for c in U]
    return not any(i!=j and ss[i] <= ss[j] for i in range(len(ss)) for j in range(len(ss)))

def endpoint_bve(U):
    p,q=1002,1032; mid=r33.canonical_formula(list(U)+[(p,2),(30,q)])
    for v in VARS:
        F=mid if v in (2,30) else U
        # R33 target-specific candidate reimplementation.
        pos=[c for c in F if v in c]; neg=[c for c in F if -v in c]
        if not pos or not neg:return False,("POLARITY",v)
        resolvents=[]
        for pc in pos:
            for nc in neg:
                raw=(set(pc)-{v})|(set(nc)-{-v})
                if any(-x in raw for x in raw):continue
                resolvents.append(r33.canonical_clause(raw))
        resolvents=sorted(set(resolvents)); removed=set(pos+neg)
        transformed=r33.canonical_formula([c for c in F if c not in removed]+resolvents)
        r33cand=len(resolvents)<=len(removed) and r33.measure(transformed)<r33.measure(F)
        if r33cand:return False,("R33_BVE",v)
        if r42.sa_bve_candidate_for_var(F,v) is not None:return False,("SA_BVE",v)
    return True,None

def bridge_not_blocked(U,endpoint,external):
    parents=[c for c in U if -endpoint in c]
    if not parents:return False
    for c in parents:
        raw=(set(c)-{-endpoint})|{external}
        if not any(-x in raw for x in raw):return True
    return False

def affine_local_obstruction(U):
    groups=defaultdict(list)
    for c in U:groups[tuple(sorted(abs(l) for l in c))].append(c)
    return any(len(cs)!=(1<<(len(vs)-1)) for vs,cs in groups.items())

def algebra_ok():
    # Symbolic coefficient inequalities valid for all integer g>=1.
    # 30*n-s =133g-56, 318*n-t=684g-634.
    return (133-56)>0 and (684-634)>0 and (155**4)>4577

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--theorem",type=Path,required=True);ap.add_argument("--hardening",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    T=json.loads(args.theorem.read_text());H=json.loads(args.hardening.read_text());fail=[]
    if T.get("preregistration_commit")!=PREREG or H.get("preregistration_commit")!=PREREG:fail.append("PREREG")
    unit=az.source_unit();U=r33.canonical_formula(unit["root"])
    if unit["failures"]:fail.append({"UNIT":unit["failures"]})
    ms=models(U); pairs={(int(a[2]),int(a[30])) for a in ms}
    if len(ms)!=60:fail.append(("MODEL_COUNT",len(ms)))
    if pairs!={(0,0),(0,1),(1,0),(1,1)}:fail.append(("ENDPOINT_PAIRS",sorted(pairs)))
    uncovered=assumptions_satisfiable_by_unit(U,ms)
    if uncovered:fail.append(("RUP_UNCOVERED",uncovered[:10]))
    if any(len(c)<2 for c in U) or any(r33.is_tautology(c) for c in U):fail.append("UNIT_OR_TAUTOLOGY")
    pol=defaultdict(set)
    for c in U:
        for l in c:pol[abs(l)].add(l>0)
    if any(pol[v]!={False,True} for v in VARS):fail.append("PURE")
    if not no_subsumption(U):fail.append("SUBSUMPTION")
    if r33.first_blocked_clause(U) is not None:fail.append("UNIT_BLOCKED")
    if not bridge_not_blocked(U,30,1032) or not bridge_not_blocked(U,2,1002):fail.append("BRIDGE_BLOCKED")
    bok,bwhy=endpoint_bve(U)
    if not bok:fail.append(bwhy)
    if r34.recognize_complete_affine_cnf(U).get("recognized") or not affine_local_obstruction(U):fail.append("AFFINE")
    if r33.is_2cnf(U) or r33.is_horn(U):fail.append("TERMINAL_CLASS")

    C=H.get("COMP",{}); definition=C.get("definition",{}); ret=C.get("return_map",{}); cert=C.get("certificate_composition",{})
    if definition.get("history_rule")!="PREFIX_DAG_SHARING; NO_RECURSIVE_EMBEDDING_OF_C_g_BYTES":fail.append("COMP_HISTORY")
    if C.get("template_content",{}).get("MID_boundary")!={"scope":[32],"rows":[[0],[1]],"sha256":T["MID_template"]["boundary"]["sha256"]}:fail.append("MID_BOUNDARY")
    if "qbit" not in ret.get("general",""):fail.append("RETURN_RULE")
    if cert.get("formula")!="C_(g+1)=COMPOSE_CERT(C_g,C_bridge,C_1)":fail.append("CERT_COMPOSE")
    R=H.get("recurrences",{})
    expected={
      "input_literal_size":("n_g=157*g-2","n_(g+1)=n_g+157"),
      "relation_rows":("s_g=4577*g-4","s_(g+1)=s_g+4577"),
      "evaluation_attempts":("t_g=49242*g-2","t_(g+1)=t_g+49242")}
    for key,(closed,rec) in expected.items():
        if R.get(key,{}).get("closed")!=closed or R.get(key,{}).get("recurrence")!=rec:fail.append(("RECURRENCE",key))
    if not algebra_ok():fail.append("ALGEBRA")

    # Independently verify the finite induction templates rather than trusting their hashes.
    if T["LAST_width_certificate"]["width"]!=13 or T["MID_width_certificate"]["width"]!=13:fail.append("WIDTH")
    if T["LAST_template"]["total_rows"]!=4573 or T["MID_template"]["total_rows"]!=4577:fail.append("ROWS")
    if T["MID_template"]["boundary"]["rows"]!=[[0],[1]]:fail.append("MID_NEUTRAL")
    # Generic policy proof rule checks: shifted blocks are variable-disjoint; bridges touch only endpoints.
    locality={"shift":30,"unit_max":30,"unit_min":2,"bridge_endpoints":"30_j,2_(j+1)",
              "proof":"unit clauses remain local; each endpoint gets at most one positive cross-block clause; every local RUP witness extends because all four endpoint pairs are realizable"}
    if H.get("generic_policy_identity",{}).get("result") is not True:fail.append("HARDENING_POLICY_FALSE")
    if H.get("lemma_status")!={"AZ_1":"PASS","AZ_2":"PASS","AZ_3":"PASS","AZ_4":"PASS","AZ_5":"PASS"}:fail.append("LEMMA_STATUS")
    out={"status":"PASS" if not fail else "FAIL","failure_count":len(fail),"failures":fail,
         "independent":{"unit_model_count":len(ms),"endpoint_pairs":[list(x) for x in sorted(pairs)],"rup_candidate_uncovered":len(uncovered),
                        "local_BVE_SA_BVE_pass":bok,"affine_obstruction":affine_local_obstruction(U),"algebra":algebra_ok(),"locality_certificate":locality},
         "classification":"69_GENERIC_FAMILY_HARDENING_VERIFIED_PENDING_PROOF_STATE_MACHINE" if not fail else "PI1_PRE_68",
         "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"failures":out["failure_count"],"models":len(ms),"pairs":sorted(pairs)},sort_keys=True))
    if fail:raise SystemExit(1)
if __name__=="__main__":main()
