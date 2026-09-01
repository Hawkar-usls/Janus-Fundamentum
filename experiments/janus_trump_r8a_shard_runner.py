#!/usr/bin/env python3
"""Infrastructure-only sharded carrier for the frozen R8A experiment."""
from __future__ import annotations
import argparse, json
from hashlib import sha256
from pathlib import Path
import janus_trump_r8a_unseen_natural_holdout as base


def run_shard(shard_index: int, shard_count: int):
    all_rows = base.frozen_residuals()
    selected = [x for i, x in enumerate(all_rows) if i % shard_count == shard_index]
    rows = []
    for global_index, item in [(i,x) for i,x in enumerate(all_rows) if i % shard_count == shard_index]:
        cnf=item['cnf']
        pre={'global_index':global_index,'source':item['source'],'root_sha256':item['root_sha256'],'pivot':item['pivot'],'branch_value':item['branch_value'],'stage':item['stage'],'formula_sha256':item['formula_sha256'],'truth':None,'candidate':None}
        seal=sha256(json.dumps(pre,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        cand=base.r7d.r7d_candidate(cnf)
        oracle=base.direct.dpll(cnf)
        truth=None if oracle['status']!='EXACT' else ('SAT' if oracle['sat'] else 'UNSAT')
        terminal_match=cand.terminal=='OPEN' or (truth is not None and cand.terminal==truth)
        sat_replay=cand.terminal!='SAT' or (cand.witness is not None and base.r7d.r7b.verify_sat(cnf,cand.witness))
        rows.append({**pre,'preverification_seal_sha256':seal,'candidate':cand.as_dict(),'shadow_verification':{'oracle':oracle,'truth':truth,'terminal_match':terminal_match,'sat_replay':sat_replay}})
    fw=base.candidate_firewall()
    terminal=[r for r in rows if r['candidate']['terminal'] in ('SAT','UNSAT')]
    opens=[r for r in rows if r['candidate']['terminal']=='OPEN']
    false_terms=[r for r in terminal if not r['shadow_verification']['terminal_match']]
    replay_fail=[r for r in terminal if not r['shadow_verification']['sat_replay']]
    unknown=[r for r in rows if r['shadow_verification']['truth'] is None]
    gates={'G1_TWO_FROZEN_INDICES':len(rows)==2,'G2_PRETRUTH':all(r['truth'] is None for r in rows),'G3_FIREWALL':fw['pass'],'G4_FALSE_TERMINALS_ZERO':not false_terms,'G5_REPLAY_FAILURES_ZERO':not replay_fail,'G6_NO_THEOREM_INFLATION':True}
    return {'schema':'JANUS/TRUMP/R8A/SHARDED_EVIDENCE/v1.0','status':'FROZEN_SHARD_RESULT','shard_index':shard_index,'shard_count':shard_count,'indices':[r['global_index'] for r in rows],'summary':{'rows':len(rows),'terminal':len(terminal),'open':len(opens),'shadow_unknown':len(unknown),'false_terminals':len(false_terms),'sat_replay_failures':len(replay_fail),'candidate_total_charged_ops':sum(int(r['candidate']['charged_ops']) for r in rows),'shadow_dpll_total_work':sum(int(r['shadow_verification']['oracle'].get('work',0)) for r in rows)},'gates':gates,'candidate_source_firewall':fw,'P_VS_NP':'OPEN','rows':rows}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--shard-index',type=int,required=True); ap.add_argument('--shard-count',type=int,default=8); ap.add_argument('--output',required=True); a=ap.parse_args()
    d=run_shard(a.shard_index,a.shard_count); Path(a.output).write_text(json.dumps(d,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps({'shard':a.shard_index,'indices':d['indices'],'summary':d['summary'],'gates':d['gates']},indent=2)); return 0 if all(d['gates'].values()) else 2
if __name__=='__main__': raise SystemExit(main())
