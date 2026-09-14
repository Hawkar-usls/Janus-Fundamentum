from __future__ import annotations
from pathlib import Path
import json, time, importlib.util
ROOT=Path(__file__).resolve().parent

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
cand=load('cand_scale',ROOT/'candidate.py'); gen=load('gen_scale',ROOT/'make_population.py')
makers=[gen.make_slot0,gen.make_slot1,gen.make_slot2,gen.make_slot3]
rows=[]
for n in [16,32,64,128]:
    for slot,maker in enumerate(makers):
        for sat in [True,False]:
            seed=gen.stable(f'scaling:{slot}:{n}:{sat}')
            base=maker(n,seed,sat);raw=gen.surface_v1(base,seed^0x5151)
            case={'case_id':f'S{slot}_{n}_{int(sat)}','cnf':raw}
            t=time.perf_counter();r=cand.process_case(case);wall=(time.perf_counter()-t)*1000
            rows.append({'slot':slot,'n_parameter':n,'truth':'SAT' if sat else 'UNSAT','candidate':r['candidate'],'decision':r['decision'],'root_replay':r['root_replay'],'raw_nvars':len({abs(x) for c in raw for x in c}),'raw_nclauses':len(raw),'t_normalize_ms':r['t_normalize_ms'],'t_discovery_ms':r['t_discovery_ms'],'t_carrier_certificate_reconstruct_ms':r['t_carrier_ms'],'t_root_verify_ms':r['t_root_verify_ms'],'wall_ms':wall})
print(json.dumps({'artifact':'APMA_BLINDED_MULTI_FAMILY_ROUTING_EMPIRICAL_SCALING','note':'empirical corroboration only; not an asymptotic proof','sizes':[16,32,64,128],'rows':rows},sort_keys=True,separators=(',',':')))
