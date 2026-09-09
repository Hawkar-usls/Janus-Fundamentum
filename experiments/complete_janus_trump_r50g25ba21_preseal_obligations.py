from __future__ import annotations
import argparse,json
from pathlib import Path

EXPECTED_PREREG="26f582d9050369719d92be22d498f649c0a932c9"
EXPECTED_HARDENING="bd49ba59b12ab344ed3800b285d3009364064257"

def main(prereg_path,result_path,verify_path,out_path):
    p=json.loads(Path(prereg_path).read_text());r=json.loads(Path(result_path).read_text());v=json.loads(Path(verify_path).read_text())
    names=p["required_pass_names"];errors=[]
    def ck(c,m):
        if not c:errors.append(m)
    ck(p["required_pass_count"]==29 and len(names)==29 and len(set(names))==29,"prereg names")
    ck(r["required_pass_names"]==names and r["required_pass_count"]==29,"result names")
    ck(set(r["obligations"])==set(names),"result obligation set")
    ck(r["preregistration_commit"]==EXPECTED_PREREG,"prereg commit")
    ck(r["preimplementation_hardening_commit"]==EXPECTED_HARDENING,"hardening commit")
    for k in names:
        if k not in ("INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"):
            ck(r["obligations"][k] is True,"builder "+k)
    ck(v["status"]=="PASS" and v["P_BA21"]==1 and v["implementation_imported"] is False,"independent verifier")
    nm=r["no_materialization"]
    ck(nm["EXPLICIT_PRIME_IMPLICATE_RECORDS"]==0 and nm["EXPLICIT_CARTESIAN_OUTPUT_TUPLES"]==0 and nm["EXPLICIT_SUPPORT_PRODUCT_RECORDS"]==0 and nm["expand_then_compress"] is False,"no materialization")
    ck(r["large_depth_diagnostic"]["DBO_blocks"]==65 and r["large_depth_diagnostic"]["variable_references"]==129,"large diagnostic")
    ck(v["large_depth"]["blocks"]==65 and v["large_depth"]["refs"]==129 and v["large_depth"]["explicit_prime_records"]==0,"large independent")
    ck(v["BA20_lower_bound_preserved"] is True,"BA20 lower bound")
    passes={k:bool(r["obligations"][k]) for k in names}
    passes["INDEPENDENT_REPLAY_PASS"]=not errors
    other=[k for k in names if k!="PRESEAL_COMPLETENESS_PASS"]
    passes["PRESEAL_COMPLETENESS_PASS"]=all(passes[k] for k in other) and not errors
    missing=[k for k in names if not passes[k]]
    complete=not errors and not missing
    out={"gate":"R50G25BA21_PRESEAL_COMPLETION","status":"PASS" if complete else "FAIL","P_BA21_FINAL":1 if complete else 0,
         "errors":errors,"missing":missing,"required_pass_count":29,"required_pass_names":names,"required_passes":passes,
         "all_required_passes":complete,"independent_verifier_status":v["status"],"no_materialization":nm,"large_depth":v["large_depth"],
         "BA20_lower_bound_preserved":True,"BA22_started":False,"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED"}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if not complete:raise SystemExit("BA21 preseal incomplete: "+repr(out))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--prereg",required=True);ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.prereg,a.result,a.verify,a.out)
