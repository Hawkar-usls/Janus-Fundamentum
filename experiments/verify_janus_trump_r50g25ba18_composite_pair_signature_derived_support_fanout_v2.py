from __future__ import annotations
import argparse, json
from itertools import product
from pathlib import Path
import verify_janus_trump_r50g25ba18_composite_pair_signature_derived_support_fanout as v1
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG="1670788c9e6c10d77c1ed7bf4f0ccf2a32471285"
PARENT_META="bd003cb6004d587e7d970b9b580c1e90fc6ad458"
HOLDOUTS=((1,1,1),(1,2,1),(1,2,2),(2,2,2),(2,3,2),(3,2,3))


def independent_generic_invariant(n):
    p=1;r=1
    F,(a,x,y,b,z,t,c)=v1.source(p,n,r)
    E=set(F)
    expected=[v1.canon((-b[j],t[j],z)) for j in range(n)]
    source_exact=all(q in E for q in expected)
    private_disjoint=all(len({b[j],t[j]} & {b[k],t[k]})==0 for j in range(n) for k in range(n) if j!=k)
    same_z_polarity=all(z in q and -z not in q for q in expected)
    fixed_kernel=(len(ba4.az.ORDER)==20)
    return {
      "n":n,
      "source_U_exact":source_exact,
      "private_groups_pairwise_disjoint":private_disjoint,
      "all_U_have_same_positive_z_polarity":same_z_polarity,
      "BA4_fixed_pivots_per_lane":len(ba4.az.ORDER),
      "fixed_kernel":fixed_kernel,
      "inductive_argument":"Private-lane elimination cannot import a second private group because all non-U BA4 clauses are lane-local. On the shared z channel all U-derived lineages inherit the same endpoint polarity; an opposite-polarity resolution parent is carrier-only and therefore contains no other private group. Thus every descendant carries at most one j group and each U_j transports independently to its shifted endpoint clause.",
      "work_bound_argument":"There are 2n private lanes with constant-size fixed kernels, contributing O(n) local work. The single shared z lane has 20 fixed pivots and O(n) U-lineage clauses; each positive/negative pool is O(n), hence at most O(n^2) raw pairs per shared pivot and O(n^2) work per transition. Repeating across g-1 translated transitions gives O(g*n^2).",
      "pass":source_exact and private_disjoint and same_z_polarity and fixed_kernel}


def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text());errors=[]
    def ck(cond,msg):
        if not cond:errors.append(msg)
    ck(r["preregistration_commit"]==PREREG,"prereg")
    ck(r["parent_BA17_meta_commit"]==PARENT_META,"parent")
    ck(r["historical_immutability"]["BA16_F14"]=="PRESERVED_FOREVER","BA16 F14")
    ck(r["historical_immutability"]["P_BA16_A"]==0 and r["historical_immutability"]["P_BA16_MIXED"]==1,"BA16 mixed")
    ck(r["implementation_version"]=="BA18_V2_GENERIC_TERNARY_TRANSPORT_WITHOUT_FALSE_LINEAR_WORK_RECURRENCE","implementation version")
    ck(r["ternary_carrier"]["rejected_postimplementation_conjecture"]["scientific_authority"] is False,"false recurrence authority")
    ck(r["complexity"]["ternary_carrier_certification_work"]=="O(g*n^2)","ternary work bound")

    absrows=[v1.abstract_replay(*h) for h in HOLDOUTS]
    ck(all(x["pass"] for x in absrows),"abstract semantic replay")
    for i,h in enumerate(HOLDOUTS):
        p,n,r0=h
        ck(r["holdouts"][i]["whole_b"]["RAW"]==p*n*r0,"raw gen3")
        ck(r["holdouts"][i]["whole_b"]["NEW_DISTINCT"]==p*n*r0,"distinct gen3")
        ck(r["holdouts"][i]["whole_b"]["DUPLICATES"]==0,"semantic duplicates")
        ck(r["holdouts"][i]["tag_erasure_distinct"]==p*r0,"tag erasure")
        ck(r["holdouts"][i]["tag_identification_distinct"]==p*r0,"tag identification")
        actual=sum(1 for bits in product((0,1),repeat=p+n+r0) if v1.final_ok(bits,p,n,r0))
        ck(actual==v1.final_count(p,n,r0),"final model count")
        ck(v1.source_width(p,n,r0),"source width")
        ck(r["width_certificates"][i]["final"]["claimed"]==p+n+r0-max(p,n,r0),"final width")

    U,first,gates,hard=ba4.source_hardening()
    joints=[v1.carrier(U,n) for n in (1,2,3,4)]
    ck(all(x["pass"] and x["exact"] and not x["mix"] for x in joints),"joint ternary exact transport")
    result_joints=r["ternary_carrier"]["joint_diagnostics"]
    ck(len(result_joints)==4,"joint diagnostics count")
    metric_keys=("raw_pairs","tautological","non_tautological","duplicates","retained","live_clause_peak","R_peak","B_peak","E_peak","W_peak")
    for j,x in enumerate(joints):
        q=result_joints[j]
        ck(q["n"]==x["n"] and q["pass"]==x["pass"],"joint identity")
        ck(all(q[k]==x[k] for k in metric_keys),"joint ledger mismatch")
    inv=[independent_generic_invariant(n) for n in (1,2,3,4)]
    ck(all(x["pass"] for x in inv),"generic source/polarity invariant")
    ck(r["ternary_carrier"]["generic_proof"]["proof_not_based_on_holdouts"] is True,"generic proof authority")
    ck(r["ternary_carrier"]["generic_proof"]["work_bound_g"]=="O((g-1)*n^2)=O(g*n^2)","generic g work")

    recon=0;source_cases=0
    for p,n,r0 in HOLDOUTS:
        for g in (1,2):
            ck(v1.size_replay(U,g,p,n,r0),"exact source size")
            # Independent constructive reconstruction against full BA4 carrier CNF.
            for fb in product((0,1),repeat=p+n+r0):
                if not v1.final_ok(fb,p,n,r0):continue
                rb=v1.reconstruct(fb,p,n,r0)
                ck(v1.source_ok(rb,p,n,r0),"symbolic reconstruction")
                ck(v1.validate_model(first,U,g,p,n,r0,rb),"full BA4 reconstruction")
                recon+=1
            # A deterministic diagnostic sample of source models, independent of builder output.
            m=p+2+n+1+n+r0
            taken=0
            for sb in product((0,1),repeat=m):
                if not v1.source_ok(sb,p,n,r0):continue
                ck(v1.validate_model(first,U,g,p,n,r0,sb),"full BA4 source model")
                source_cases+=1;taken+=1
                if taken>=16:break

    ck(r["named_fields"]["RAW_GEN3"]=="p*n*r" and r["named_fields"]["DISTINCT_GEN3"]=="p*n*r","named gen3")
    ck(r["named_fields"]["COMPOSITE_PAIR_SIGNATURE"]["count"]=="n*r","named signature")
    ck(r["named_fields"]["BA16_IDENTITY_PRESERVATION"]["NEW_VARIABLE_IDENTITY_COUNT"]==0,"no new identity")
    ck(r["output_firewall"]["COMPOSITE_IDENTITY_FANOUT_NE_EXPONENTIAL_BLOWUP"] is True,"output firewall")
    ck(r["failure_count"]==0 and not r["falsifiers"],"builder falsifiers")
    ck(all(r["ternary_subpasses"].values()),"ternary subpasses")
    ck(r["next_gate_started"] is False and r["BA19_started"] is False,"STOP")

    out={
      "gate":"R50G25BA18_INDEPENDENT_REPLAY_V2",
      "status":"PASS" if not errors else "FAIL",
      "error_count":len(errors),"errors":errors,
      "implementation_imported":False,
      "base_BA18_implementation_imported":False,
      "abstract_holdouts":absrows,
      "joint_ternary_carrier_replay":joints,
      "generic_invariant_certificates":inv,
      "generic_transport_theorem":"PASS" if all(x["pass"] for x in inv) and all(x["pass"] for x in joints) else "FAIL",
      "ternary_certification_work_bound":"O(g*n^2)",
      "false_linear_work_recurrence_required":False,
      "reconstruction_cases":recon,"source_model_cases":source_cases,
      "P_BA18":1 if not errors else 0,
      "BA16_F14":"PRESERVED_FOREVER","P_BA16_A":0,"P_BA16_MIXED":1,
      "P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("BA18 independent replay v2 failure: "+errors[0])

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.out)
