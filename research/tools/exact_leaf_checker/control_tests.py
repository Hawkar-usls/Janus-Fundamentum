import copy, json, subprocess, sys, tempfile
from pathlib import Path

CERT="d7831123307ee6d2fc6efff231815706335b4ac794db0fb1bea204b13b8e4b74"
MANIFEST="9179ffa25c2b52707dc3c039aee3f71821637856c77dce1b1d7c477843d3ad20"
CONSTITUTION="d6b069a6e070d51573b9b84576d19d1074fc0054d8672c3a6801b1ea984d30eb"
PAIR="507bd2437afc6de3a060b6fb6899454206b7fce2"

def state(vec):
    return {"schema":"TRUMP_CANONICAL_RESIDUAL_STATE_V1","version":"1.0","certificate_digest":CERT,"compressed_manifest_sha256":MANIFEST,"exact_only_constitution_sha256":CONSTITUTION,"assignment_vector":list(vec)}

def proof(nodes,root):
    return {"schema":"TRUMP_EXACT_PROOF_DAG_V1","version":"1.0","certificate_digest":CERT,"compressed_manifest_sha256":MANIFEST,"exact_only_constitution_sha256":CONSTITUTION,"pair_order_preregistration_commit":PAIR,"nodes":nodes,"root_node_id":root}

def leaf(nid,s):
    return {"node_id":nid,"type":"UNSAT_EXACT_WORD_LEVEL_CONTRADICTION","state":s,"derivation_kind":"A_LEX_LT_B_VIOLATION"}

def partition_control():
    v=[0]*560; v[0]=5; v[280]=3; v[1]=-1
    parent=state(v); nodes=[]; children=[]
    for value in range(24):
        w=list(v); w[1]=value; nodes.append(leaf(value,state(w))); children.append({"value":value,"node_id":value})
    nodes.append({"node_id":24,"type":"INTERNAL_24_WAY_PARTITION","state":parent,"branch_rank":1,"children":children})
    return proof(nodes,24)

def memo_control():
    v=[0]*560; v[0]=5; v[280]=3; s=state(v)
    return proof([leaf(0,s),{"node_id":1,"type":"UNSAT_EXACT_MEMOIZED_RESIDUAL_REUSE","state":copy.deepcopy(s),"target_unsat_node_id":0}],1)

def run(checker,obj,tmp,name,expect_pass=False):
    p=tmp/(name+".json"); p.write_text(json.dumps(obj,sort_keys=True,separators=(",",":")),encoding="utf-8",newline="\n")
    r=subprocess.run([sys.executable,str(checker),"--proof",str(p)],capture_output=True,text=True)
    ok=(r.returncode==0) if expect_pass else (r.returncode!=0)
    return {"test":name,"ok":ok,"returncode":r.returncode,"stdout":r.stdout.strip(),"stderr_tail":r.stderr.strip()[-240:]}

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--checker",required=True); a=ap.parse_args(); checker=Path(a.checker)
    out=[]
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td); good=partition_control(); memo=memo_control()
        out.append(run(checker,good,tmp,"VALID_24_WAY_PARTITION",True))
        out.append(run(checker,memo,tmp,"VALID_BYTE_IDENTICAL_MEMO",True))
        x=copy.deepcopy(good); x["pair_order_preregistration_commit"]="0"*40; out.append(run(checker,x,tmp,"PAIR_ORDER_BINDING_DRIFT"))
        x=copy.deepcopy(good); x["compressed_manifest_sha256"]="0"*64; out.append(run(checker,x,tmp,"MANIFEST_BINDING_DRIFT"))
        x=copy.deepcopy(good); x["exact_only_constitution_sha256"]="0"*64; out.append(run(checker,x,tmp,"CONSTITUTION_BINDING_DRIFT"))
        x=copy.deepcopy(good); x["nodes"][0]["state"]["assignment_vector"]=x["nodes"][0]["state"]["assignment_vector"][:-1]; out.append(run(checker,x,tmp,"STATE_LENGTH_559"))
        x=copy.deepcopy(good); x["nodes"][0]["state"]["assignment_vector"][2]=24; out.append(run(checker,x,tmp,"STATE_VALUE_24"))
        x=copy.deepcopy(good); x["nodes"][24]["branch_rank"]=2; out.append(run(checker,x,tmp,"NONMINIMAL_BRANCH_RANK"))
        x=copy.deepcopy(good); x["nodes"][24]["children"]=x["nodes"][24]["children"][:-1]; out.append(run(checker,x,tmp,"MISSING_CHILD"))
        x=copy.deepcopy(good); x["nodes"][24]["children"][1]["value"]=0; out.append(run(checker,x,tmp,"DUPLICATE_CHILD_VALUE"))
        x=copy.deepcopy(good); x["nodes"][24]["children"]=list(reversed(x["nodes"][24]["children"])); out.append(run(checker,x,tmp,"NONCANONICAL_CHILD_ORDER"))
        x=copy.deepcopy(good); x["nodes"][0]["state"]["assignment_vector"][2]=1; out.append(run(checker,x,tmp,"CHILD_MUTATES_TWO_RANKS"))
        x=copy.deepcopy(good); x["nodes"][0]["type"]="UNKNOWN_LEAF"; out.append(run(checker,x,tmp,"UNKNOWN_LEAF_TYPE"))
        x=proof([leaf(0,state([0]*560))],0); x["nodes"][0]["state"]["assignment_vector"][0]=2; x["nodes"][0]["state"]["assignment_vector"][280]=3; out.append(run(checker,x,tmp,"FAKE_LEX_CONTRADICTION"))
        x=copy.deepcopy(memo); x["nodes"][1]["state"]["assignment_vector"][2]=1; out.append(run(checker,x,tmp,"MEMO_STATE_NOT_IDENTICAL"))
        x=copy.deepcopy(good); x["nodes"][0]["heuristic_score"]=1; out.append(run(checker,x,tmp,"HEURISTIC_FIELD_SMUGGLE"))
        x=copy.deepcopy(good); x["nodes"][0]["random_seed"]=7; out.append(run(checker,x,tmp,"RANDOMNESS_FIELD_SMUGGLE"))
        s=state([0]*560); x=proof([{"node_id":0,"type":"SAT_COMPLETE_ASSIGNMENT_REPLAY","state":s}],0); out.append(run(checker,x,tmp,"SAT_REPLAY_UNSUPPORTED"))
        x=proof([{"node_id":0,"type":"UNSAT_CERTIFIED_BOUND_CONTRADICTION","state":s}],0); out.append(run(checker,x,tmp,"BOUND_LEAF_UNSUPPORTED"))
    result={"schema":"TRUMP_EXACT_LEAF_CHECKER_CONTROL_TESTS_V1","all_pass":all(r["ok"] for r in out),"test_count":len(out),"results":out}
    print(json.dumps(result,sort_keys=True)); return 0 if result["all_pass"] else 1

if __name__=="__main__": raise SystemExit(main())
