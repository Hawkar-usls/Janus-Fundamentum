import argparse, copy, json, subprocess, sys, tempfile
from pathlib import Path
from control_tests import partition_control, memo_control

def run(checker,obj,tmp,name):
    p=tmp/(name+'.json'); p.write_text(json.dumps(obj,sort_keys=True,separators=(',',':')),encoding='utf-8',newline='\n')
    r=subprocess.run([sys.executable,str(checker),'--proof',str(p)],capture_output=True,text=True)
    return {'test':name,'rejected':r.returncode!=0,'stderr_tail':r.stderr.strip()[-220:]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checker',required=True); a=ap.parse_args(); checker=Path(a.checker)
    good=partition_control(); memo=memo_control(); out=[]
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        for key,name,value in [('learned_selector','LEARNED_SELECTOR_SMUGGLE','model'),('probabilistic_guidance','PROBABILISTIC_GUIDANCE_SMUGGLE',0.7),('approximate_pruning','APPROXIMATE_PRUNING_SMUGGLE',True),('scored_ranking','SCORED_RANKING_SMUGGLE',1.0)]:
            x=copy.deepcopy(good); x['nodes'][0][key]=value; out.append(run(checker,x,tmp,name))
        x=copy.deepcopy(memo); x['nodes'][1].pop('target_unsat_node_id'); x['nodes'][1]['target_state_sha256']='0'*64
        out.append(run(checker,x,tmp,'HASH_ONLY_MEMOIZED_REUSE'))
    result={'schema':'TRUMP_EXACT_LEAF_CHECKER_SUPPLEMENTARY_REDTEAM_V1','all_pass':all(x['rejected'] for x in out),'test_count':len(out),'results':out}
    print(json.dumps(result,sort_keys=True)); return 0 if result['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
