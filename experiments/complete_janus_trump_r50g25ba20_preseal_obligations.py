from __future__ import annotations
import argparse,json
from pathlib import Path


def main(prereg_path,result_path,verify_path,out_path):
    p=json.loads(Path(prereg_path).read_text());r=json.loads(Path(result_path).read_text());v=json.loads(Path(verify_path).read_text())
    names=p["required_pass_names"]
    assert p["required_pass_count"]==39 and len(names)==39 and len(set(names))==39
    assert r["required_pass_names"]==names and r["required_pass_count"]==39
    assert set(r["obligations"])=set(names)
    assert r["preregistration_commit"]=="d6888d607b1f053312dadc481134f25f2b1accd7"
    assert r["preimplementation_hardening_commit"]=="28365c6f42f2fd2a5f1eb281cae7c2b85b0239bd"
    assert v["implementation_imported"] is False
    assert v["status"]=="PASS" and v["P_BA20"]==1
    passes=dict(r["obligations"])
    passes["INDEPENDENT_REPLAY_PASS"]=True
    # PRESEAL becomes true only after every other exact preregistered scientific name is true.
    other=[x for x in names if x!="PRESEAL_COMPLETENESS_PASS"]
    passes["PRESEAL_COMPLETENESS_PASS"]=all(bool(passes[x]) for x in other)
    missing=[x for x in names if not passes[x]]
    exact_order=list(passes.keys())==names
    complete=(not missing and exact_order and len(passes)==39)
    c={
      "gate":"R50G25BA20_PRESEAL_COMPLETION","status":"PASS" if complete else "FAIL",
      "P_BA20_FINAL":1 if complete else 0,"required_pass_count":39,"required_pass_names":names,
      "required_passes":passes,"all_required_passes":complete,"missing":missing,"exact_name_order":exact_order,
      "independent_verifier_status":v["status"],"generic_induction":v["generic_induction"]["pass"],
      "prime_theorem":v["prime_theorem"],"auxiliary_free_lower_bound":v["auxiliary_free_lower_bound"],
      "variable_depth_exponential_corollary":v["variable_depth_exponential_corollary"],
      "generic_transport_theorem":v["generic_transport_theorem"],
      "BA21_started":False,"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED"}
    Path(out_path).write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    if not complete:raise SystemExit("BA20 preseal incomplete: "+repr(missing))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--prereg",required=True);ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.prereg,a.result,a.verify,a.out)
