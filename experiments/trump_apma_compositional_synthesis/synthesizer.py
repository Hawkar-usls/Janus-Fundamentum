from __future__ import annotations
from pathlib import Path
import hashlib, json, sys, time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import core

def load_calibration():
    return json.loads((ROOT/'calibration.json').read_text(encoding='utf-8-sig'))

def synthesize():
    data=load_calibration(); programs=core.grammar(); out={'artifact':'APMA_COMPOSITIONAL_SYNTHESIS_CANDIDATES','grammar_count':len(programs),'folds':{}}
    for fold in sorted(data['folds']):
        cases=data['folds'][fold]; rows=[]
        for idx,p in enumerate(programs):
            exact=0; admitted=0; total_ms=0.0
            for case in cases:
                z=core.run_program(case['cnf'],p);total_ms+=sum(z['timing'].values())
                if z['admitted']:
                    admitted+=1
                    if z['decision']==case['truth']:
                        exact+=1
            rows.append({'program':p,'program_hash':core.program_hash(p),'exact':exact,'admitted':admitted,'total':len(cases),'runtime_ms':total_ms,'rank_key':[-exact,-admitted,idx]})
        rows.sort(key=lambda r:tuple(r['rank_key']))
        best=rows[0]
        out['folds'][fold]={'selected_program':best['program'],'selected_program_hash':best['program_hash'],'calibration_exact':best['exact'],'calibration_admitted':best['admitted'],'calibration_total':best['total'],'ranking':rows}
    payload=json.dumps(out,sort_keys=True,separators=(',',':')).encode()
    out['bundle_sha256']=hashlib.sha256(payload).hexdigest()
    return out

if __name__=='__main__':
    result=synthesize()
    text=json.dumps(result,indent=2,sort_keys=True)
    (ROOT/'SYNTHESIZED_CANDIDATES.json').write_text(text,encoding='utf-8')
    print(json.dumps({'bundle_sha256':result['bundle_sha256'],'folds':{k:v['selected_program']['id'] for k,v in result['folds'].items()}},sort_keys=True))
