#!/usr/bin/env python3
"""JANUS PIPPI adaptive ladder v1.2 — floor endurance recovery extension.

Preserves v1.1 exact bootstrap correction and all v1.0 race semantics.  The only
controller extension is at the 3:3 racing floor: if a rollback has reached 3:3
without satisfying the strict recovery target, PIPPI is allowed up to four
additional fresh 3:3 recovery laps, with a full pit-stop between each.  This
implements "until performance recovers" without pretending the symmetric 1:1
and 2:2 formation laps provide a useful racing signal.

If the target still is not reached, the frontier is frozen. P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import time
from pathlib import Path
import torch

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_pitstop_ladder_v1_1 as v11
from experiments.mad_lab import keymaster_50x50_cycle1_teacher_slime as c1

P_VS_NP="OPEN"
SCHEMA="JANUS/PIPPI/ADAPTIVE-PITSTOP-LADDER/v1.2.0"


def main()->int:
    v1.exact_root_episode=v11.exact_root_episode_v1_1
    ap=argparse.ArgumentParser()
    ap.add_argument('--topa-dir',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--max-d',type=int,default=32)
    ap.add_argument('--formulas-per-stage',type=int,default=6)
    ap.add_argument('--max-stages',type=int,default=72)
    ap.add_argument('--time-budget-seconds',type=float,default=780.0)
    ap.add_argument('--recovery-margin',type=float,default=3.0)
    ap.add_argument('--max-floor-recovery-laps',type=int,default=4)
    args=ap.parse_args()
    random.seed(20260828); torch.manual_seed(20260828); torch.set_num_threads(2)
    out=args.out_dir; out.mkdir(parents=True,exist_ok=True); journal=out/'pippi-journal.jsonl'
    start=time.perf_counter(); used:set[str]=set()

    memory,boot=v1.bootstrap_50(used)
    teacher=c1.JGPTPivotTeacher(); teacher_opt=torch.optim.AdamW(teacher.parameters(),lr=0.004,weight_decay=0.002)
    student=c1.PivotSlimeStudent()
    attention_state=None; rejected:set[str]=set(); focus_patterns:set[str]=set(); fusion={'JGPT':0.5,'SLIME':0.25,'M2R':0.25,'SPIDER':0.0}
    train_pool=[e for e in memory if v1.split_name(e['fingerprint'])=='TRAIN']; calib_pool=[e for e in memory if v1.split_name(e['fingerprint'])=='CALIBRATION']
    initial_train=v1.train_models(teacher,teacher_opt,student,train_pool,set())
    edge=out/'edge-state-pit0.jsonl'; er=v1.build_relation_edges(train_pool,{e['fingerprint'] for e in memory},edge)
    attention_state,spider=v1.run_spider(args.topa_dir,edge,None,out,0)
    detective=v1.detective_calibration_gate(train_pool,calib_pool); rejected=set(detective['rejected_patterns'])
    prior=v1.spider_prior_map(attention_state,rejected); fusion,fcal=v1.choose_fusion(teacher,student,train_pool,calib_pool,prior)
    focus_patterns={x['node_id'] for x in spider['focus'] if str(x.get('node_id','')).startswith('pattern:')}
    v1.append_jsonl(journal,{'kind':'PITSTOP','pit':0,'phase':'PRE_RACE_BOOTSTRAP','bootstrap':boot,'train':initial_train,'spider':spider,'detective':detective,'fusion_weights':fusion,'fusion_calibration':fcal,'P_VS_NP':P_VS_NP})

    history=[]; pit=0; stage_serial=0; current_d=1; highest_accepted=0; prev_accepted_score=None
    rollback=None; floor_recovery_laps=0; stop_reason=None
    while stage_serial<args.max_stages and current_d<=args.max_d:
        if time.perf_counter()-start > args.time_budget_seconds:
            stop_reason='TIME_BUDGET'; break
        stage_serial+=1
        stage_eps=v1.make_track_stage(current_d,stage_serial,args.formulas_per_stage,used)
        prior=v1.spider_prior_map(attention_state,rejected)
        qstudent=copy.deepcopy(student); qaudit=c1.quantize_int8_inplace(qstudent)
        scored=v1.stage_score(stage_eps,teacher,qstudent,train_pool,prior,fusion)
        score=float(scored['performance_index'])
        state='FORMATION' if current_d<3 else ('ROLLBACK' if rollback else 'RACING')
        event={'kind':'STAGE','stage_serial':stage_serial,'difficulty':f'{current_d}:{current_d}','d':current_d,'state':state,'score_before_learning_from_this_stage':score,'metrics':scored,'fusion_weights_used':fusion,'int8_tensor_count':qaudit['tensor_count'],'fresh_fingerprints':[e['fingerprint'] for e in stage_eps],'elapsed_seconds':time.perf_counter()-start,'P_VS_NP':P_VS_NP}
        v1.append_jsonl(journal,event); history.append(event)

        decision={'action':'CONTINUE'}
        if current_d>=3:
            if rollback is None:
                if prev_accepted_score is None:
                    prev_accepted_score=score; highest_accepted=max(highest_accepted,current_d); decision={'action':'ACCEPT_FIRST_RACING_REFERENCE'}
                elif score>=prev_accepted_score:
                    prev_accepted_score=score; highest_accepted=max(highest_accepted,current_d); floor_recovery_laps=0; decision={'action':'ACCEPT_AND_INCREASE'}
                else:
                    drop=prev_accepted_score-score; target=prev_accepted_score+args.recovery_margin
                    rollback={'failed_d':current_d,'failed_score':score,'previous_accepted_score':prev_accepted_score,'drop':drop,'recovery_target':target,'rollback_from':current_d}
                    floor_recovery_laps=0; decision={'action':'REGRESSION_ROLLBACK','drop':drop,'recovery_target':target}
            else:
                if score>=rollback['recovery_target']:
                    decision={'action':'RECOVERY_CONFIRMED_RETRY_FAILED','recovery_target':rollback['recovery_target'],'rebound_from_failed':score-rollback['failed_score'],'floor_recovery_laps_used':floor_recovery_laps}
                elif current_d<=3:
                    if floor_recovery_laps<args.max_floor_recovery_laps:
                        floor_recovery_laps+=1
                        decision={'action':'FLOOR_RECOVERY_PIT_LOOP','recovery_target':rollback['recovery_target'],'floor_recovery_lap':floor_recovery_laps,'max_floor_recovery_laps':args.max_floor_recovery_laps}
                    else:
                        decision={'action':'STOP_RECOVERY_NOT_REACHED_AFTER_FLOOR_ENDURANCE','recovery_target':rollback['recovery_target'],'floor_recovery_laps_used':floor_recovery_laps}
                else:
                    decision={'action':'ROLL_BACK_ONE_MORE_LEVEL','recovery_target':rollback['recovery_target']}
        v1.append_jsonl(journal,{'kind':'CONTROLLER','stage_serial':stage_serial,'d':current_d,**decision,'P_VS_NP':P_VS_NP})

        memory.extend(stage_eps); new_fps={e['fingerprint'] for e in stage_eps}
        train_pool=[e for e in memory if v1.split_name(e['fingerprint'])=='TRAIN']; calib_pool=[e for e in memory if v1.split_name(e['fingerprint'])=='CALIBRATION']
        pit+=1
        train_audit=v1.train_models(teacher,teacher_opt,student,train_pool,focus_patterns)
        edge=out/f'edge-state-pit{pit}.jsonl'; edge_audit=v1.build_relation_edges(train_pool,new_fps,edge)
        attention_state,spider=v1.run_spider(args.topa_dir,edge,attention_state,out,pit)
        detective=v1.detective_calibration_gate(train_pool,calib_pool); rejected=set(detective['rejected_patterns'])
        prior=v1.spider_prior_map(attention_state,rejected)
        fusion,fcal=v1.choose_fusion(teacher,student,train_pool,calib_pool,prior)
        focus_patterns={x['node_id'] for x in spider['focus'] if str(x.get('node_id','')).startswith('pattern:')}
        mirror={'kind':'PITSTOP','pit':pit,'after_stage':stage_serial,'d':current_d,'new_exact_receipts':len(stage_eps),'memory_formulas':len(memory),'train_formulas':len(train_pool),'calibration_formulas':len(calib_pool),'training':train_audit,'relation_edges':edge_audit,'spider_focus':spider['focus'],'detective':detective,'next_fusion_weights':fusion,'fusion_calibration':fcal,'controller_decision':decision,'performance_history':[{'stage':h['stage_serial'],'d':h['d'],'score':h['score_before_learning_from_this_stage'],'state':h['state']} for h in history],'P_VS_NP':P_VS_NP}
        v1.append_jsonl(journal,mirror); (out/f'pippi-mirror-pit{pit}.json').write_text(json.dumps(mirror,indent=2,sort_keys=True)+'\n')

        act=decision['action']
        if act in {'CONTINUE','ACCEPT_FIRST_RACING_REFERENCE','ACCEPT_AND_INCREASE'}: current_d+=1
        elif act=='REGRESSION_ROLLBACK': current_d=max(3,current_d-1)
        elif act=='ROLL_BACK_ONE_MORE_LEVEL': current_d=max(3,current_d-1)
        elif act=='FLOOR_RECOVERY_PIT_LOOP': current_d=3
        elif act=='RECOVERY_CONFIRMED_RETRY_FAILED': current_d=int(rollback['failed_d']); rollback=None; floor_recovery_laps=0
        elif act=='STOP_RECOVERY_NOT_REACHED_AFTER_FLOOR_ENDURANCE': stop_reason='RECOVERY_NOT_REACHED_AFTER_3x3_ENDURANCE'; break
        else: current_d+=1

    if stop_reason is None:
        if current_d>args.max_d: stop_reason='MAX_D_REACHED'
        elif stage_serial>=args.max_stages: stop_reason='MAX_STAGES_REACHED'
        else: stop_reason='ENDED'
    racing=[h for h in history if h['d']>=3]; best=max(racing,key=lambda h:h['score_before_learning_from_this_stage']) if racing else None
    result={
      'schema':SCHEMA,'status':'ADAPTIVE_RACE_COMPLETE__EXACT_TRANSITIONS_VERIFIED','P_VS_NP':P_VS_NP,
      'rules':{'start':'1:1','formation_laps':['1:1','2:2'],'difficulty_step':1,'pitstop_before_every_next_stage':True,'regression_trigger':'score < previous accepted racing score','recovery_rule':'fresh rollback score >= previous accepted score + 3.0 points','recovery_margin_points':args.recovery_margin,'rollback_floor':'3:3','max_floor_recovery_laps':args.max_floor_recovery_laps},
      'scope':{'formula_family':'balanced inconsistent XOR 2-CNF','exact_2sat_shortcut_available':True,'exact_2sat_shortcut_used_for_race_runtime':False,'race_runtime':'capped exact elimination navigation','general_sat_hardness_claim':False},
      'bootstrap':boot,'stages_completed':len(history),'pitstops_completed':pit,'highest_accepted_d':highest_accepted,'frontier':f'{highest_accepted}:{highest_accepted}' if highest_accepted else None,'stop_reason':stop_reason,
      'best_observed_racing_stage':None if best is None else {'stage':best['stage_serial'],'d':best['d'],'score':best['score_before_learning_from_this_stage']},
      'history':[{'stage':h['stage_serial'],'d':h['d'],'state':h['state'],'score':h['score_before_learning_from_this_stage'],'top1':h['metrics']['top1_best_recall'],'mean_rank':h['metrics']['mean_best_rank'],'static':h['metrics']['aggregate']['STATIC'],'keymaster':h['metrics']['aggregate']['KEYMASTER'],'oracle':h['metrics']['aggregate']['ORACLE']} for h in history],
      'final_fusion_weights':fusion,'final_detective_rejected_patterns':sorted(rejected),'elapsed_seconds':time.perf_counter()-start,
      'resource_accounting':{'symbolic_runtime_metrics_logged_separately':True,'model_training_walltime_not_added_to_pair_work':True,'spider_walltime_not_added_to_pair_work':True,'GLOBAL_RESOURCE_POSITIVE':'UNKNOWN'},
      'scientific_firewall':{'FRESH_STAGE_SCORED_BEFORE_LEARNING_FROM_IT':True,'ROLLBACK_USES_FRESH_FINGERPRINTS':True,'PIVOT_NUMERIC_ID_IS_NOT_MODEL_FEATURE':True,'EXACT_RAW_UNITS_ARE_LABELS_NOT_MODEL_INPUTS':True,'ATTENTION_WEIGHT_IS_NOT_EVIDENCE_WEIGHT':True,'SPIDER_EDGE_IS_NOT_CAUSATION':True,'MODEL_PREDICTION_IS_NOT_PROOF':True,'KEYMASTER_ONLY_REORDERS_EXACT_CHECKS':True,'EVERY_ACCEPTED_TRANSITION_EXACT_VERIFIED':True,'NO_SAME_RUN_THEOREM_PROMOTION':True,'P_VS_NP':P_VS_NP}}
    (out/'adaptive-race-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'frontier':result['frontier'],'stages':result['stages_completed'],'pitstops':result['pitstops_completed'],'stop_reason':stop_reason,'best_stage':result['best_observed_racing_stage'],'final_weights':fusion,'P_VS_NP':P_VS_NP},indent=2,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
