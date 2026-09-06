from __future__ import annotations
import json
from pathlib import Path
p=Path('research/JANUS_TRUMP_R50G25_CHAIN_JOURNAL.json')
x=json.loads(p.read_text())
entries=[e for e in x['entries'] if e.get('gate') not in {'R50G25X','R50G25Y'}]
entries.extend([
  {
    'gate':'R50G25X','status':'SUCCESS_WITH_COUNTEREXAMPLE','branch':'research/r50g25x-universal-door-obligation-adversarial-stall-search-2026-09-06','preregistration_commit':'558a528863e33ff5bf3cef28af03257158fe753f','run_head_commit':'9f49c37abdd31e5523a6cc7a9623ef81611da39f','result_receipt_commit':'30cbe3f2fd3b07fbffb1210bcd5d00c232a2945c','run_id':34044941068,'artifact':{'name':'janus-trump-r50g25x-adversarial-stall-search','id':9992845123,'zip_sha256':'32232b076165663a0f699adf34b237d0b755e6e1be06a8c0c2974f13741e1069'},'verdict':'W_POLICY_COUNTEREXAMPLE_FOUND','evaluated_unique_count':58,'residual_fixpoint_count':15,'assertion_failure_count':0,'reconstruction_failure_count':0,'canonical_Y_target':{'hash':'c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb','CLV':[63,155,20],'RUP':0,'SA_BVE':0},'next_gate':'R50G25Y_MINIMAL_W_POLICY_COUNTEREXAMPLE_FORENSICS'
  },
  {
    'gate':'R50G25Y','status':'SUCCESS','branch':'research/r50g25y-minimal-w-policy-counterexample-forensics-2026-09-06','preregistration_commit':'92b93a34cd582800fc925e961196607ff8d27ee0','run_head_commit':'63e4aa3d87d5673eed1fd1537cfa83a157ff10eb','result_receipt_commit':'3398edec2c648cc59f366b179a61a895829eacb2','run_id':34045760892,'artifact':{'name':'janus-trump-r50g25y-minimal-w-policy-counterexample-forensics','id':9993039773,'zip_sha256':'89b273964ca8e96e1bf263b1596bb54d8ce5f358ff0b168d2022c3fc67ec4a70'},'verdict':'MINIMAL_STALL_HAS_ONLY_NONDESCENDING_DP_DOORS','minimization':{'source_CLV':[63,155,20],'minimized_CLV':[27,66,17],'residual_core_CLV':[23,60,13],'accepted_edits':41,'attempts':946,'truth_blind':True},'exact_DP_pivot_count':13,'exact_DP_relation_histogram':{'GROWTH':13},'downstream_nonresidual_pivot_count':12,'minimum_nonresidual_DP_door':{'var':10,'CLV_before':[23,60,13],'CLV_after':[23,61,12],'downstream_terminal':'EMPTY_CNF_SAT'},'next_gate':'R50G25Z_CONTROLLED_GROWTH_DP_DOOR_OR_LOWER_BOUND_OBSTRUCTION'
  }
])
x['entries']=entries
x['version']='2.1'
x.setdefault('policy',{})['P_VS_NP']='OPEN'; x['policy']['SAT_IN_P']='NOT_PROVED'; x['policy']['TRUMP_finished']=False; x['policy']['finite_success_is_not_universal_coverage']=True
p.write_text(json.dumps(x,indent=2,sort_keys=False)+'\n')
print('JOURNAL_V21_OK',len(entries),[e['gate'] for e in entries[-3:]])
