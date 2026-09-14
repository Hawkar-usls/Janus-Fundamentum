from __future__ import annotations
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import core,make_population as pop

def rank(cases):
    rows=[]
    for idx,p in enumerate(core.grammar()):
        exact=admitted=0;t=0.0
        for case in cases:
            z=core.run_program(case['cnf'],p);t+=sum(z['timing'].values())
            if z['admitted']:
                admitted+=1;exact+=z['decision']==case['truth']
        rows.append((-exact,-admitted,idx,p,t))
    rows.sort(key=lambda x:(x[0],x[1],x[2]));return rows[0]

def main():
    frozen=json.loads((ROOT/'SYNTHESIZED_CANDIDATES.json').read_text());rows=[]
    for n in [8,16,32,64,128]:
        for slot,f in enumerate('ABCD'):
            cases=[]
            for j,sat in enumerate([True,False,True,False]):
                cnf=pop.make(slot,n+(j//2),sat,700000+slot*10000+n*10+j,'hold')
                cases.append({'cnf':cnf,'truth':'SAT' if sat else 'UNSAT'})
            t0=time.perf_counter();best=rank(cases);t1=time.perf_counter()
            p=frozen['folds'][f]['selected_program'];exec_ms=0.0;ok=True
            for c in cases:
                z=core.run_program(c['cnf'],p);exec_ms+=sum(z['timing'].values());ok &= z['admitted'] and z['decision']==c['truth']
            rows.append({'n':n,'fold':f,'ranking_program':best[3]['id'],'frozen_program':p['id'],'synthesis_wall_ms':(t1-t0)*1000,'candidate_stage_sum_ms':best[4],'frozen_execution_ms':exec_ms,'all_exact':bool(ok)})
    out={'artifact':'APMA_COMPOSITIONAL_SYNTHESIS_SCALING_CORROBORATION','firewall':'EMPIRICAL_ONLY_NOT_ASYMPTOTIC_PROOF','rows':rows}
    (ROOT/'scaling_raw.json').write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    summary={}
    for n in [8,16,32,64,128]:
        rr=[x for x in rows if x['n']==n];summary[n]={'max_synthesis_wall_ms':max(x['synthesis_wall_ms'] for x in rr),'sum_execution_ms':sum(x['frozen_execution_ms'] for x in rr),'all_exact':all(x['all_exact'] for x in rr),'rank_matches':all(x['ranking_program']==x['frozen_program'] for x in rr)}
    print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
