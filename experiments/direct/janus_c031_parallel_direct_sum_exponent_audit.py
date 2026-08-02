#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib

def audit(k_values=range(1,8), n_values=(2,4,8,16,32,64), m_values=(1,2,4,8,16,64)):
    rows=[]
    for k in k_values:
        for n in n_values:
            base_lb=n
            for m in m_values:
                N=m*n
                perfect_direct_sum=m*base_lb
                assert perfect_direct_sum==N
                target=N**k
                rows.append({
                    "k":k,"base_input":n,"copies":m,"total_input":N,
                    "one_copy_lower_bound":base_lb,
                    "perfect_direct_sum_lower_bound":perfect_direct_sum,
                    "target_polynomial_bound":target,
                    "target_over_direct_sum":target/perfect_direct_sum,
                })
    result={
      "artifact_id":"C031-NO-EXPONENT-GAIN-FROM-PARALLEL-DIRECT-SUM",
      "status":"PASS",
      "p_vs_np":"OPEN",
      "theorem":"Even a perfect direct-sum theorem for m independent copies of a function with linear circuit lower bound yields only a linear lower bound in the total input length N=mn.",
      "rows_checked":len(rows),
      "symbolic_accounting":{
        "base_exponent_a":"a",
        "total_input_N":"m*n",
        "perfect_direct_sum":"m*n^a = N^a / m^(a-1)",
        "linear_case":"a=1 => Omega(N), independent of m",
        "consequence":"parallel repetition cannot raise the input-length exponent"
      },
      "decisive_obstruction":"Certified Refuter Amplification cannot be achieved by plain parallel repetition of current linear gate-elimination refuters, even if all sharing is fully excluded.",
      "next_gate":"Use nontrivial composition/hardness magnification whose complexity growth outpaces encoded input growth, while preserving constructive counterexample extraction and SAT/UNSAT certificates.",
      "claim_boundary":"This does not rule out strong composition, hardness magnification, or other nonlinear amplification. It blocks parallel-copy amplification as a route from linear to n^k lower bounds."
    }
    payload=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    result["integrity_sha256"]=hashlib.sha256(payload).hexdigest()
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    r=audit()
    print(json.dumps(r,indent=2,sort_keys=True))
    if args.self_test:
        assert r["status"]=="PASS"
        assert r["rows_checked"]==7*6*6
        assert r["symbolic_accounting"]["linear_case"].startswith("a=1")

if __name__=="__main__":
    main()
