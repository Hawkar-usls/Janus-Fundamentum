#!/usr/bin/env python3
"""BABEL-20 finite rank survey, frozen legal cover instances."""
import argparse,json
from pathlib import Path
import crossbase_rank2,crossbase_verify,full_kerT_sparse
CASES={"SCL63":(0,1,7,23,38),"SCL126_flip16":(5,14,20,29,37),"SCL126_flip68":(0,16,20,28,47)}
def survey(base):
    crossbase_rank2.P=65521
    full_kerT_sparse.P=65521
    results=[]
    for seed in CASES[base]:
        result=crossbase_rank2.audit(seed,passes=4,base_name=base)
        verified=crossbase_verify.verify(Path(result["pivot_witness"]))
        assert verified["rational_rank_lower_bound"]==result["final_rank_lower_bound_over_Q"]
        entry={"base":base,"seed":seed,"anti_dimension":result["target_antisector_dimension"],
         "certified_Q_rank_lower_bound":verified["rational_rank_lower_bound"],
         "residual_upper_bound":result["final_co_kernel_dimension_at_most"],
         "full_Q_rank":verified["full_rational_rank_proved"],
         "source_zero_generators_per_pass":result["all_kerT_generators_per_pass"],
         "pivot_sha256":result["pivot_witness_sha256"],
         "nonfull_status":"NOT_DECIDED"}
        results.append(entry)
        print("BABEL20_CASE",json.dumps(entry,sort_keys=True),flush=True)
    summary={"base":base,"cases":results,"full_rank_count":sum(x["full_Q_rank"] for x in results),"scope":"15 selected frozen covers only"}
    Path(f"babel20_{base}_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("BABEL20_SUMMARY",json.dumps({"base":base,"full_rank_count":summary["full_rank_count"]},sort_keys=True),flush=True)
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--base",choices=list(CASES),required=True)
    survey(ap.parse_args().base)
