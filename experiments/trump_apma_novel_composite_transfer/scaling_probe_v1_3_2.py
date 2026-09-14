from __future__ import annotations
from pathlib import Path
import json,sys,time,importlib.util
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import transfer_core as tc

def load_exact(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

gen=load_exact('janus_v12_generator',ROOT/'make_population.py')
chk=load_exact('janus_v13_checker',ROOT/'independent_checker.py')

def main():
    rho=json.loads((ROOT/'FROZEN_RHO.json').read_text(encoding='utf-8')); rule=rho['selected_rule']; rows=[]
    for k in [4,8,16,32]:
        cases,hidden,_=gen.make_pair('hold',900+k,k,'long_path',900000+k); truths={cid:truth for cid,truth,meta,metrics in hidden}
        for case in cases:
            t0=time.perf_counter(); z=tc.solve_formula(case['cnf'],rule); wall=(time.perf_counter()-t0)*1000
            vok,vreason=chk.verify_transfer(case['cnf'],z,rule) if z.get('admitted') else (False,z.get('reason'))
            exact=bool(z.get('admitted') and z.get('decision')==truths[case['id']] and vok)
            cert=z.get('certificate') or {}; rel=cert.get('relations') or []; edges=cert.get('edges') or []
            rows.append({'k':k,'topology':'long_path','id':case['id'],'truth':truths[case['id']],'admitted':bool(z.get('admitted')),'decision':z.get('decision'),'independent_verify':vok,'verify_reason':vreason,'exact':exact,'leaf_count':z.get('leaf_count'),'carrier_edge_count':len(edges),'relation_count':len(rel),'relation_tuple_total':sum(len(r.get('allowed',[]))+len(r.get('forbidden',[])) for r in rel),'timing_ms':z.get('timing'),'wall_ms':wall})
    grouped={}
    for k in [4,8,16,32]:
        rr=[x for x in rows if x['k']==k]; grouped[str(k)]={'cases':len(rr),'exact':sum(x['exact'] for x in rr),'max_wall_ms':max(x['wall_ms'] for x in rr),'sum_wall_ms':sum(x['wall_ms'] for x in rr),'max_leaf_count':max(x['leaf_count'] for x in rr),'max_carrier_edge_count':max(x['carrier_edge_count'] for x in rr),'max_relation_tuple_total':max(x['relation_tuple_total'] for x in rr),'leaf_to_k_ratio_max':max(x['leaf_count']/k for x in rr)}
    out={'artifact':'JANUS-TRUMP-APMA-NOVEL-COMPOSITE-TRANSFER-POSTPASS-SCALING-2026-09-14-v1.3.2','authority':'POST_PASS_DIAGNOSTIC_ONLY','frozen_rho':rule,'frozen_rho_hash':rho['selected_rule_hash'],'sizes':[4,8,16,32],'topology':'long_path','rows':rows,'grouped':grouped,'all_exact':all(x['exact'] for x in rows),'complexity_firewall':{'timings':'EMPIRICAL_CORROBORATION_ONLY','not_asymptotic_proof':True,'theoretical_scope':'selected rho uses fixed separator width 1; generic prereg scope remains w<=3 and relation size <=8 tuples','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN'}}
    (ROOT/'scaling_raw_v1_3_2.json').write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps({'all_exact':out['all_exact'],'grouped':grouped},sort_keys=True))
if __name__=='__main__': main()
