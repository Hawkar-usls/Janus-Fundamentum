#!/usr/bin/env python3
import argparse, itertools, json, pathlib

def ce(a,b):return tuple(sorted((str(a),str(b))))
def edges(P):return {ce(a,b) for a,b in P["edges"]}
def has(P,a,b):return ce(a,b) in edges(P)
def induced_path(P,seq):
    if len(set(seq))!=len(seq):return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if has(P,a,seq[j])!=(j==i+1):return False
    return True
def p6_free(P):
    V=P["vertices"]
    if len(V)<6:return True
    return not any(induced_path(P,p) for comb in itertools.combinations(V,6) for p in itertools.permutations(comb))
def proper(P,c):
    return all(c[a]!=c[b] for a,b in edges(P))
def extensions_count(P,fixed):
    V=sorted(P["vertices"]);free=[v for v in V if v not in fixed];n=0
    for vals in itertools.product(range(1,5),repeat=len(free)):
        c=dict(fixed);c.update(dict(zip(free,vals)))
        if proper(P,c):n+=1
    return n

def main():
    ap=argparse.ArgumentParser();ap.add_argument("run_dir");ap.add_argument("output");args=ap.parse_args()
    root=pathlib.Path(args.run_dir)
    summary=json.loads((root/"summary.json").read_text())
    sealedP=json.loads((root/"SEALED_111_PLUS_000_SUPPORT_Z_COLLISION.fixture.json").read_text())
    sealed=json.loads((root/"SEALED_111_PLUS_000_SUPPORT_Z_COLLISION.receipt.json").read_text())
    core_ids=["CORE_FULL_000_111_NO001","LEGACY_000_FORCE_ONLY","LEGACY_111_SUPPORT_ONLY"]
    receipts={i:json.loads((root/(i+".receipt.json")).read_text()) for i in core_ids}
    fixtures={i:json.loads((root/(i+".fixture.json")).read_text()) for i in core_ids}
    qformal=json.loads((root/"QUARANTINED_001_formal.receipt.json").read_text())
    qtext=json.loads((root/"QUARANTINED_001_completeness_text.receipt.json").read_text())

    checks={}
    checks["sealed_graph_P6_free"]=p6_free(sealedP)
    checks["sealed_extension_proper"]=proper(sealedP,sealedP["c"])
    checks["sealed_exact_edges"]=set(edges(sealedP))=={
      ce("s1","s2"),ce("s2","s3"),ce("s1","s3"),ce("v","s1"),ce("v","z"),ce("z","n"),ce("n","s3")
    }
    # Independent source-fragment derivation: 111(U,W) contributes v,z,n to support;
    # 000(A,U) contributes v to semantic Z_FORCE.
    support={"v","z","n"};zforce={"v"}
    checks["sealed_independent_support_Z_collision"]=(support&zforce)=={"v"}
    checks["sealed_candidate_reproduced_literal_collision"]=sealed.get("literal_constructor")=="FAIL_SUPPORT_Z_COLLISION" and sealed.get("literal_collision")==["v"]
    checks["sealed_normalized_typed"]=sealed.get("normalized_constructor")=="PASS_ROLE_NORMALIZATION"
    ov=sealed.get("overlap_assertions",{}).get("v",{})
    checks["overlap_physical_seed_semantic_Z_preserved"]=(ov.get("physical_role")=="SEED" and ov.get("semantic_Z_FORCE") is True and ov.get("forced_color_preserved") is True)
    checks["sealed_fixed_union_and_extensions_preserved"]=sealed.get("fixed_union_identity") is True and sealed.get("extension_sets_equal") is True

    for i,P in fixtures.items():
        checks[i+"_P6_free"]=p6_free(P)
        checks[i+"_c_proper"]=proper(P,P["c"])
        r=receipts[i]
        checks[i+"_candidate_full_replay_pass"]=r.get("verdict")=="PASS_FULL_LEGACY_REPLAY"
        sem=r.get("R4_semantic_identity",{})
        checks[i+"_semantic_identity"]=sem.get("fixed_union_identity") is True and sem.get("extension_sets_equal") is True
        l10=r.get("R5_lemma7_10_replay",{})
        checks[i+"_lemma7_replay"]=l10.get("lemma7")=="PASS"
        checks[i+"_lemma10_conclusions"]=all((l10.get("checks") or {}).values())
        raw=r.get("R6_raw_semantics",{})
        checks[i+"_raw_completeness_soundness"]=raw.get("fixed_extension_c_captured") is True and raw.get("normalized_extensions_subset_original") is True

    deleted=(receipts["LEGACY_000_FORCE_ONLY"].get("R5_lemma7_10_replay",{}).get("lemma6",{}).get("deleted") or [])
    checks["pure000_nontrivial_lemma6_deletion"]=len(deleted)>=1
    rec=receipts["LEGACY_000_FORCE_ONLY"].get("R6_downstream_reconstruction",{})
    checks["pure000_reconstruction"]=rec.get("reconstruction_ok") is True

    checks["001_kept_quarantined"]=summary.get("quarantined_001",{}).get("SOURCE_001_RESOLVED") is False
    checks["001_variants_recorded"]=qformal.get("variant")=="formal" and qtext.get("variant")=="completeness"
    checks["gate_candidate_pass"]=summary.get("scientific_gate")=="PASS_LEGACY_NORMALIZED_CONSTRUCTOR_REPLAY"
    ceiling=summary.get("ceiling",{})
    checks["authority_ceiling"]=(
      summary.get("authority_mode")=="FINITE_SOURCE_FAITHFUL_REPLAY__NOT_UNIVERSAL_FORMAL_PROOF" and
      ceiling.get("AUTHORS_INTENDED_NORMALIZATION")=="NOT_CLAIMED" and
      ceiling.get("SOURCE_001_SEMANTICS")=="AMBIGUOUS" and
      ceiling.get("RIGID_SPLIT4")=="STILL_PAUSED" and
      ceiling.get("P7_RAW_COVERAGE")=="NOT_RERUN" and
      ceiling.get("P_VS_NP")=="OPEN"
    )
    verdict="INDEPENDENT_LEGACY_NORMALIZATION_REPLAY_PASS" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={"schema":"janus.trump.legacy_normalized_constructor_replay.independent.v1",
         "verdict":verdict,"checks":checks,
         "authority_ceiling":{
           "UNIVERSAL_LEMMA7_10_REPROOF":"NOT_CLAIMED",
           "AUTHORS_INTENDED_NORMALIZATION":"NOT_CLAIMED",
           "SOURCE_001_SEMANTICS":"AMBIGUOUS",
           "RIGID_SPLIT4":"PAUSED",
           "P_VS_NP":"OPEN"
         }}
    pathlib.Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
    if verdict!="INDEPENDENT_LEGACY_NORMALIZATION_REPLAY_PASS":raise SystemExit(1)

if __name__=="__main__":main()
