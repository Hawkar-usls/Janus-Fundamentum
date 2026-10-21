#!/usr/bin/env python3
"""BABEL21: exact complete-source Fourier coordinate matching.

Check whether a residual source functional on ALL row/multiplier columns
equals the coordinate functional e_f^T A for a *nonzero* source frequency f.
In that case every existing source degree2 certificate has zero response,
so transfer to cover exists using verified rational rank modulo syzygies.

This DOES NOT establish existence of the source degree2 certificate itself.
"""
import argparse,gzip,json,hashlib
from pathlib import Path
from janus_babel6_transfer import xor_labels
from janus_babel10_degree_scan import frozen_instances

def verify(base,seed):
    inp=Path(f"babel21_{base}_seed{seed}_source_phi.json.gz")
    with gzip.open(inp,"rt",encoding="utf-8") as f:doc=json.load(f)
    rows=frozen_instances()[base]
    labels,Q,d=xor_labels(rows)
    assert doc["source_degree2_multiplier_count"]==len(rows)*len(Q)
    answers=[]
    for item in doc["annihilator_representatives"]:
        phi={(r,p):v for r,p,v in item["source_phi_response"]}
        assert len(phi)==item["source_phi_nnz"] and phi
        (r,p),one=next(iter(phi.items()))
        candidates={p,*(p^labels[j] for j in rows[r])}
        accepted=[]
        for freq in candidates:
            if freq==0:continue
            mismatches=[]
            verified=0
            for i,row in enumerate(rows):
                a,b,c=[labels[j] for j in row]
                for u in sorted(Q):
                    predicted=sum(x==freq for x in (u,u^a,u^b,u^c))
                    observed=phi.get((i,u),0)
                    if predicted!=observed:
                        mismatches.append((i,u,predicted,observed))
                        break
                    verified+=1
                if mismatches:break
            if not mismatches:
                assert verified==len(rows)*len(Q)
                accepted.append(freq)
        result={"component":item["component"],
                "nonzero_source_frequency_matches":accepted,
                "exact_source_columns_verified":len(rows)*len(Q) if accepted else 0,
                "source_response_nnz":len(phi),
                "target_compatible_under_existing_source_identity":bool(accepted),
                "no_extra_source_syzygy_required_if_match":bool(accepted)}
        print("BABEL21_FREQUENCY_MATCH",base,seed,json.dumps(result,sort_keys=True),flush=True)
        answers.append(result)
    report={"gate":"BABEL21_EXACT_SOURCE_FREQUENCY_TARGET_COMPATIBILITY",
        "base":base,"seed":seed,
        "all_remaining_functionals_identified_as_nonzero_source_frequencies":
           all(x["target_compatible_under_existing_source_identity"] for x in answers),
        "full_source_degree2_certificate_verified_in_this_run":False,
        "source_certificate_needed_for_cover_existence":True,
        "frequency_checks":answers,
        "source_phi_sha256":hashlib.sha256(inp.read_bytes()).hexdigest(),
        "P_vs_NP_proved":False}
    Path(f"babel21_{base}_seed{seed}_frequency_match.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("BABEL21_FREQUENCY_FINAL",json.dumps({k:v for k,v in report.items() if k!="frequency_checks"},sort_keys=True),flush=True)
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--base",default="SCL126_flip16");a.add_argument("--seed",type=int,default=20)
    args=a.parse_args();verify(args.base,args.seed)
