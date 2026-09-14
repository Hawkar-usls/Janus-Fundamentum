from __future__ import annotations
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import core
import independent_checker as chk

def rank(cases, pool):
    rows=[]
    for idx,p in enumerate(pool):
        exact=admitted=0
        for case in cases:
            z=core.run_program(case['cnf'],p)
            if z['admitted']:
                admitted+=1
                if z['decision']==case['truth']: exact+=1
        rows.append(( -exact,-admitted,p['id'],p,exact,admitted))
    rows.sort(key=lambda x:(x[0],x[1],x[2]))
    return rows[0]

def main():
    cal=json.loads((ROOT/'calibration.json').read_text());adm=json.loads((ROOT/'sealed_admission.json').read_text());hol=json.loads((ROOT/'sealed_holdout.json').read_text());truth=json.loads((ROOT/'sealed_truth.json').read_text());cand=json.loads((ROOT/'SYNTHESIZED_CANDIDATES.json').read_text())
    out={'artifact':'APMA_COMPOSITIONAL_SYNTHESIS_ABLATION_DIAGNOSTIC','authority':'DIAGNOSTIC_ONLY_NOT_PASS_CRITERION','folds':{}}
    for f in 'ABCD':
        slot=ord(f)-65;orig=cand['folds'][f]['selected_program'];fold=[]
        for removed in orig['nodes'][:2]:
            pool=[p for p in core.grammar() if removed not in p['nodes']]
            best=rank(cal['folds'][f],pool);p=best[3];fails=[];okn=0;total=0
            for data in (adm,hol):
                for case in data['folds'][f]:
                    total+=1;z=core.run_program(case['cnf'],p);gt=truth[case['id']]['truth']
                    ok=z['admitted'] and z['decision']==gt and chk.VER[slot](case['cnf'],z)
                    if ok:okn+=1
                    else:fails.append([case['id'],gt,z.get('decision'),z.get('admitted')])
            fold.append({'removed_primitive':removed,'replacement_program':p['id'],'calibration_exact':best[4],'calibration_admitted':best[5],'blind_exact':okn,'blind_total':total,'verdict':'ABLATION_ROBUST' if okn==total else 'ABLATION_CRITICAL_PRIMITIVE','failure_count':len(fails),'sample_failures':fails[:5]})
        out['folds'][f]=fold
    (ROOT/'ablation_raw.json').write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({f:[x['verdict'] for x in xs] for f,xs in out['folds'].items()},sort_keys=True))
if __name__=='__main__':main()
