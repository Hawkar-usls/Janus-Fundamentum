#!/usr/bin/env python3
"""PIPPI 50:50 cached-resource re-audit with cross-formula cache reuse.

Separates route-equivalent exhaustive work from actual unique-transition work.
The original Cycle0 lru_cache persists across formulas, so this re-audit uses
one shared cache across the ordered TRAIN corpus as well. Distinct root
fingerprints may converge to an identical canonical descendant, allowing exact
verified transitions to be reused across formulas.

Neural training wall time remains a separate unit; GLOBAL_RESOURCE_POSITIVE is
UNKNOWN without a declared common normalized resource unit. P_VS_NP=OPEN.
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
from typing import Any
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import juxtapose_50x50_multiformula_corpus as corpus_mod

P_VS_NP="OPEN"; UNBOUNDED_CAP=10**9; PIVOTS=tuple(range(1,8))

class SharedAudit:
    def __init__(self):
        self.cache:dict[tuple[base.CNF,int,int],tuple[base.CNF|None,dict[str,Any]]]={}
        self.pairs=0; self.raw=0; self.verified=0; self.overflow=0; self.hits=0
    def transition(self,state:base.CNF,pivot:int,cap:int):
        key=(state,pivot,cap)
        if key in self.cache:
            self.hits+=1; return self.cache[key]
        out,st=base.eliminate_var_capped(state,pivot,cap)
        self.pairs+=int(st.get('pairs',0)); self.raw+=int(st.get('raw_units',0))
        if out is None:self.overflow+=1
        else:
            assert base.verify_elimination_transition(state,pivot,out,cap); self.verified+=1
        self.cache[key]=(out,st); return out,st
    def snap(self):return {'transitions':len(self.cache),'pairs':self.pairs,'raw':self.raw,'verified':self.verified,'overflow':self.overflow,'hits':self.hits}

def audit_formula(shared:SharedAudit,seed:int,stress_cap:int)->dict[str,Any]:
    root=corpus_mod.construct(seed); before=shared.snap()
    def replay(order,cap):
        state=root
        for p in order:
            if state==((),):break
            if p not in set(base.vars_of(state)):continue
            out,_=shared.transition(state,p,cap)
            if out is None:return False
            state=out
        return state==((),)
    for order in itertools.permutations(PIVOTS):assert replay(order,UNBOUNDED_CAP)
    safe=sum(int(replay(order,stress_cap)) for order in itertools.permutations(PIVOTS)); assert safe>0
    after=shared.snap()
    return {
      'seed':seed,'stress_cap':stress_cap,'safe_orders_at_stress_cap':safe,
      'new_unique_transition_computations':after['transitions']-before['transitions'],
      'new_unique_transition_pair_work':after['pairs']-before['pairs'],
      'new_unique_transition_raw_units_sum':after['raw']-before['raw'],
      'new_exact_verified_nonoverflow_transitions':after['verified']-before['verified'],
      'new_unique_overflow_transitions':after['overflow']-before['overflow'],
      'cache_hits_during_formula':after['hits']-before['hits']
    }

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--cycle1',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    corpus=json.loads(a.corpus.read_text()); cycle1=json.loads(a.cycle1.read_text())
    train=[f for f in corpus['formulas'] if f['split']=='TRAIN']; assert len(train)==24
    shared=SharedAudit(); rows=[]
    for f in train:rows.append(audit_formula(shared,int(f['seed']),int(f['stress']['cap'])))
    actual_transitions=len(shared.cache); actual_pairs=shared.pairs
    equivalent_pairs=sum(int(f['stress']['exhaustive_pair_work']) for f in train)
    equivalent_checks=sum(int(f['stress']['exhaustive_exact_checks']) for f in train)
    cache_misses_recorded=sum(int(f['stress']['transition_cache']['misses_exact_verified']) for f in train)
    assert actual_transitions==cache_misses_recorded,(actual_transitions,cache_misses_recorded)
    saved_pairs=int(cycle1['PIPPI_DELTA1']['pair_work_saved']); saved_checks=int(cycle1['PIPPI_DELTA1']['exact_checks_saved'])
    model_seconds=float(cycle1['teacher_audit']['training_seconds'])+float(cycle1['student_audit']['training_seconds'])
    pair_net=saved_pairs-actual_pairs
    payload={
      'schema':'JANUS/PIPPI/50x50-CYCLE0-RESOURCE-REAUDIT/v1.1.0','status':'PASS__CROSS_FORMULA_CACHE_REUSE_ACCOUNTED','P_VS_NP':P_VS_NP,
      'scope':'24_TRAIN_FINGERPRINTS_USED_BY_CYCLE1',
      'route_equivalent_counterfactual':{'exhaustive_exact_route_checks':equivalent_checks,'exhaustive_pair_work':equivalent_pairs,'interpretation':'Logical sum over all stressed routes; NOT actual compute after transition caching.'},
      'implemented_cached_generator':{
        'unique_transition_computations':actual_transitions,'exact_verified_nonoverflow_transitions':shared.verified,'unique_overflow_transitions':shared.overflow,
        'actual_unique_transition_pair_work':actual_pairs,'actual_unique_transition_raw_units_sum':shared.raw,'cache_hits':shared.hits,
        'cache_reuse_factor_by_transition_count':equivalent_checks/max(1,actual_transitions),'cache_reuse_factor_by_pair_work':equivalent_pairs/max(1,actual_pairs),
        'cross_formula_cache_reuse_enabled':True,
        'interpretation':'One shared exact cache across ordered formulas; canonical descendants may be reused across distinct root fingerprints.'},
      'cycle1_downstream_holdout_savings_vs_static_numeric_control':{'exact_checks_saved':saved_checks,'pair_work_saved':saved_pairs,'holdout_formulas':8},
      'pair_work_accounting_horizon':{
        'actual_cached_training_pair_work_charge':actual_pairs,'downstream_pair_work_saved_so_far':saved_pairs,'net_pair_work_after_actual_cached_generation_charge':pair_net,
        'PAIR_WORK_RESOURCE_POSITIVE':pair_net>0,
        'estimated_break_even_additional_holdout_like_formulas_if_gain_rate_stays_constant':(actual_pairs-saved_pairs)/max(1e-12,saved_pairs/8.0) if pair_net<0 and saved_pairs>0 else 0.0,
        'warning':'Break-even projection is diagnostic only; gain rate is not assumed constant.'},
      'separate_model_training_resource':{'teacher_plus_student_training_wall_seconds_on_GitHub_runner':model_seconds,'pair_work_conversion_declared':False,'energy_measurement_available':False},
      'global_resource_statement':{'GLOBAL_RESOURCE_POSITIVE':'UNKNOWN','reason':'Pair-work and neural training wall-time/energy are different units; no common normalized resource budget has been declared.'},
      'per_formula_incremental_cache_cost':rows,
      'firewall':{'DO_NOT_CALL_ROUTE_EQUIVALENT_WORK_ACTUAL_COMPUTE':True,'DO_NOT_ADD_PAIR_WORK_AND_SECONDS':True,'CACHE_DOES_NOT_CHANGE_EXACT_SEMANTICS':True,'CROSS_FORMULA_CACHE_REUSE_IS_RESOURCE_REUSE_NOT_LEARNING_PROOF':True,'MODEL_PREDICTION_IS_NOT_PROOF':True,'P_VS_NP':P_VS_NP}}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':payload['status'],'equivalent_pair_work':equivalent_pairs,'actual_cached_pair_work':actual_pairs,'unique_transitions':actual_transitions,'cross_formula_cache_hits':shared.hits,'pair_work_net':pair_net,'global_resource_positive':'UNKNOWN','P_VS_NP':P_VS_NP},indent=2,sort_keys=True)); return 0
if __name__=='__main__':raise SystemExit(main())
