#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
IDS=tuple(f'R19-W{i:02d}' for i in range(1,11))
def aggregate(d):
    rows=[]
    for wid in IDS:
        p=d/f'JANUS_TRUMP_R19_{wid}_RESULT_2026-09-02.json'
        if not p.exists():return {'overall_verdict':'FAIL_INTEGRITY','reason':f'MISSING:{wid}','P_VS_NP':'OPEN'}
        x=json.loads(p.read_text());c=x.get('candidate',{});q=x.get('comparison',{});rows.append({'id':wid,'suite':x['source']['suite'],'n':x['source']['n'],'bridge':x['source']['bridge_variable_count'],'frame_sha256':x['source']['frame_sha256'],'verdict':x['verdict'],'candidate_status':c.get('status'),'elapsed_seconds':c.get('elapsed_seconds'),'final_active_nodes':c.get('final_active_nodes'),'maximum_nodes_seen':c.get('maximum_nodes_seen_before_gc'),'nodes_created_total':c.get('nodes_created_total'),'restrict_calls_total':c.get('restrict_calls_total'),'hashcons_hits':c.get('hashcons_hits'),'gc_removed_total':c.get('gc_removed_total'),'original_allowed':q.get('original_allowed'),'candidate_allowed':q.get('candidate_allowed'),'false_positive':q.get('false_positive_count'),'false_negative':q.get('false_negative_count'),'truth_hash':q.get('original_truth_table_sha256')})
    c=Counter(r['verdict'] for r in rows)
    if c['FAIL_INTEGRITY']:overall='FAIL_INTEGRITY'
    elif c['MISMATCH_FRESH_UNSEEN']:overall='R19_FRESH_UNSEEN_SEMANTIC_MISMATCH'
    elif c['OPEN_CANDIDATE_RESOURCE_LIMIT']:overall='R19_FRESH_UNSEEN_RESOURCE_OPEN'
    elif c['PASS_EXACT_FRESH_UNSEEN']==10:overall='R19_PASS_EXACT_FRESH_UNSEEN_10_OF_10'
    else:overall='FAIL_INTEGRITY'
    terminal=[r for r in rows if r['verdict'] in ('PASS_EXACT_FRESH_UNSEEN','MISMATCH_FRESH_UNSEEN')]
    scaling={'n_values':sorted({r['n'] for r in rows}),'terminal_worlds':len(terminal),'max_elapsed_seconds':max((r['elapsed_seconds'] or 0 for r in terminal),default=None),'max_final_active_nodes':max((r['final_active_nodes'] or 0 for r in terminal),default=None),'max_maximum_nodes_seen':max((r['maximum_nodes_seen'] or 0 for r in terminal),default=None),'max_nodes_created_total':max((r['nodes_created_total'] or 0 for r in terminal),default=None),'max_restrict_calls_total':max((r['restrict_calls_total'] or 0 for r in terminal),default=None),'interpretation':'Finite n=24..56 ladder only; no asymptotic polynomial theorem.'}
    next_gate={'R19_PASS_EXACT_FRESH_UNSEEN_10_OF_10':'R20_ADVERSARIAL_AND_SCALING_KILLER_TEST','R19_FRESH_UNSEEN_SEMANTIC_MISMATCH':'R20_COUNTEREXAMPLE_FORENSICS__DO_NOT_TUNE_R18_IN_PLACE','R19_FRESH_UNSEEN_RESOURCE_OPEN':'R20_DAG_RESOURCE_GROWTH_FORENSICS','FAIL_INTEGRITY':'STOP_AND_REPAIR_INTEGRITY'}[overall]
    return {'schema':'JANUS/TRUMP/R19/FRESH_PROSPECTIVE_UNSEEN_SHANNON_DAG_HOLDOUT/AGGREGATE_RESULT/v1.0','created_date':'2026-09-02','overall_verdict':overall,'verdict_counts':dict(c),'world_count':len(rows),'worlds':rows,'scaling_observation':scaling,'scientific_interpretation':'R19 is the first genuinely fresh structural unseen holdout for the byte-frozen R18 shared-DAG mechanism. PASS is finite scoped evidence; mismatch is a counterexample; resource OPEN is not semantic negative evidence.','next_gate':next_gate,'claim_ceiling':'No global polynomial bound, arbitrary-CNF totality, SAT-in-P, P=NP, or P!=NP conclusion from this finite holdout.','seal':'CAPTAIN_OBVIOUS_SAYS__THE_REAL_FIELD_TEST_COUNTS_ONLY_IF_THE_MAP_WAS_FRESH_AND_THE_HERO_WAS_FROZEN','P_VS_NP':'OPEN'}
def main():
    a=argparse.ArgumentParser();a.add_argument('--input-dir',required=True);a.add_argument('--output',required=True);z=a.parse_args();out=aggregate(Path(z.input_dir));Path(z.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'overall_verdict':out['overall_verdict'],'verdict_counts':out.get('verdict_counts'),'scaling':out.get('scaling_observation'),'P_VS_NP':'OPEN'},indent=2,sort_keys=True));return 2 if out['overall_verdict']=='FAIL_INTEGRITY' else 0
if __name__=='__main__':raise SystemExit(main())
