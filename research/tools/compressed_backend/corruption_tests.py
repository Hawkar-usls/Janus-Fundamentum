import argparse, copy, json, subprocess, sys, tempfile
from pathlib import Path

def run(checker,cert,obj,tmp,name):
    p=tmp/(name+".json")
    p.write_text(json.dumps(obj,sort_keys=True,separators=(",",":")),encoding="utf-8",newline="\n")
    r=subprocess.run([sys.executable,str(checker),"--cert",str(cert),"--backend",str(p)],capture_output=True,text=True)
    return {"test":name,"rejected":r.returncode!=0,"stdout":r.stdout.strip(),"stderr_tail":r.stderr.strip()[-300:]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checker",required=True)
    ap.add_argument("--cert",required=True)
    ap.add_argument("--backend",required=True)
    a=ap.parse_args()
    checker=Path(a.checker); cert=Path(a.cert); base=json.loads(Path(a.backend).read_text(encoding="utf-8"))
    results=[]
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        x=copy.deepcopy(base); x["input_certificate_digest"]="0"*64
        results.append(run(checker,cert,x,tmp,"CERTIFICATE_DIGEST_DRIFT"))
        x=copy.deepcopy(base); x["groups"][10]["source_last_id"]+=1
        results.append(run(checker,cert,x,tmp,"STAGE_RANGE_CORRUPTION"))
        x=copy.deepcopy(base); x["branch_codes"]=list(range(23))
        results.append(run(checker,cert,x,tmp,"INCOMPLETE_24_WAY_COVERAGE"))
        x=copy.deepcopy(base); x["heuristics_present"]=True
        results.append(run(checker,cert,x,tmp,"HEURISTIC_MECHANISM_SMUGGLE"))
        x=copy.deepcopy(base); x["branch_coordinate_rule"]="SCORED_BEST_FIRST"
        results.append(run(checker,cert,x,tmp,"NONCANONICAL_BRANCH_SELECTOR"))
        x=copy.deepcopy(base); x["branch_value_order"]=list(reversed(range(24)))
        results.append(run(checker,cert,x,tmp,"NONCANONICAL_BRANCH_VALUE_ORDER"))
        x=copy.deepcopy(base); x["randomness_present"]=True
        results.append(run(checker,cert,x,tmp,"RANDOMNESS_SMUGGLE"))
        x=copy.deepcopy(base); x["learned_selector_present"]=True
        results.append(run(checker,cert,x,tmp,"LEARNED_SELECTOR_SMUGGLE"))
        x=copy.deepcopy(base); x["probabilistic_guidance_present"]=True
        results.append(run(checker,cert,x,tmp,"PROBABILISTIC_GUIDANCE_SMUGGLE"))
        x=copy.deepcopy(base); x["approximate_pruning_present"]=True
        results.append(run(checker,cert,x,tmp,"APPROXIMATE_PRUNING_SMUGGLE"))
        x=copy.deepcopy(base); x["scored_ranking_present"]=True
        results.append(run(checker,cert,x,tmp,"SCORED_RANKING_SMUGGLE"))
        x=copy.deepcopy(base); x["TRUMP_EXACT_ALGEBRA_ONLY"]=False
        results.append(run(checker,cert,x,tmp,"EXACT_ALGEBRA_ONLY_CONSTITUTION_DISABLED"))
        x=copy.deepcopy(base); x["heuristics_forbidden"]=False
        results.append(run(checker,cert,x,tmp,"HEURISTICS_FORBIDDEN_FLAG_DISABLED"))
    all_pass=all(r["rejected"] for r in results)
    out={"schema":"TRUMP_COMPRESSED_BACKEND_CORRUPTION_TESTS_V1_1_EXACT_ONLY","all_pass":all_pass,"results":results}
    print(json.dumps(out,sort_keys=True))
    return 0 if all_pass else 1

if __name__=="__main__":
    raise SystemExit(main())
