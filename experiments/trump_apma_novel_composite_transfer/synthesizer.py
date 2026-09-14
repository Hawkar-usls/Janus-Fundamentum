from __future__ import annotations
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import transfer_core as tc

def main():
    cal=json.loads((ROOT/'calibration.json').read_text(encoding='utf-8'))
    results=[]
    for rule in tc.RULE_CANDIDATES:
        exact=0; admitted=0; records=[]
        for case in cal['cases']:
            z=tc.solve_formula(case['cnf'],rule)
            ok=z.get('admitted') and z.get('decision')==case['truth']
            exact+=int(ok); admitted+=int(bool(z.get('admitted')))
            records.append({'id':case['id'],'truth':case['truth'],'admitted':bool(z.get('admitted')),'decision':z.get('decision'),'exact':bool(ok),'reason':z.get('reason'),'leaf_count':z.get('leaf_count')})
        results.append({'rule':rule,'rule_hash':tc.rule_hash(rule),'exact':exact,'admitted':admitted,'total':len(cal['cases']),'records':records})
    winners=[r for r in results if r['exact']==len(cal['cases'])]
    if not winners:
        out={'verdict':'FAIL_NO_TRANSFER_RULE','candidates':results}
    else:
        winners.sort(key=lambda r:(r['rule']['max_separator_width'],r['rule']['id']))
        sel=winners[0]
        payload={'artifact':'JANUS-TRUMP-APMA-FROZEN-RHO-2026-09-14-v1.0','verdict':'RHO_FROZEN','selected_rule':sel['rule'],'selected_rule_hash':sel['rule_hash'],'operations':tc.RULE_OPS,'lower_primitives':list(tc.LOWER_PRIMITIVES),'candidate_count':len(tc.RULE_CANDIDATES),'calibration_exact':sel['exact'],'calibration_total':sel['total'],'candidate_results':results,'blind_files_read':[],'scientific_firewall':{'UNIVERSAL_DISCOVERY':'NOT_CLAIMED','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN'}}
        raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); payload['bundle_sha256']=hashlib.sha256(raw).hexdigest(); out=payload
    (ROOT/'FROZEN_RHO.json').write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'verdict':out['verdict'],'selected':out.get('selected_rule'),'hash':out.get('selected_rule_hash'),'candidate_exact':{x['rule']['id']:x['exact'] for x in results}},sort_keys=True))
if __name__=='__main__': main()
