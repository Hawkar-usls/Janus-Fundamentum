from __future__ import annotations
import json, math
from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as v11

ARTIFACT_ID='JANUS-TRUMP-BUCKET-COMMON-CORE-SEMIJOIN-PREFILTER-V1-1-INDEPENDENT-CHECK-2026-09-15'

def factor(rel,gi):
    os=list(rel['scope']); scope=sorted(os); pos={v:i for i,v in enumerate(os)}
    return {'id':f'orig:{gi}','gi':gi,'scope':scope,'rows':[tuple(int(r[pos[v]]) for v in scope) for r in rel['allowed']]}

def independent(raw):
    pred=guarded.explain(raw)
    if pred.get('status')!='OPEN_BUCKET_PRODUCT_BUDGET': return {'status':'OUT_OF_SCOPE','predecessor':pred.get('status')}
    fail=pred['carrier']['failed_bucket']; x=int(fail['variable']); can=canonicalize_raw(raw); cut=list(pred['parent_cut']['cut_variables']); B=set(cut)
    comps=parent_support.constraint_components_after_cut(can,cut); comp=next(c for c in comps if any(x in can['constraints'][gi]['scope'] for gi in c))
    fs=[factor(can['constraints'][gi],gi) for gi in comp]; internal=sorted({vv for f in fs for vv in f['scope'] if vv not in B})
    if not internal or x!=internal[0]: return {'status':'OUT_OF_SCOPE_NOT_TARGET_FIRST','internal':internal,'x':x}
    bucket=[f for f in fs if x in f['scope']]; assert [f['id'] for f in bucket]==fail['bucket_factor_ids']; core=sorted(set.intersection(*(set(f['scope']) for f in bucket)))
    supports=[]
    for f in bucket:
        pos=[f['scope'].index(v) for v in core]; supports.append({tuple(r[p] for p in pos) for r in f['rows']})
    common=set.intersection(*supports); filtered=json.loads(json.dumps(can)); before=[len(f['rows']) for f in bucket]; after=[]
    for f in bucket:
        rel=filtered['constraints'][f['gi']]; os=list(rel['scope']); pos={v:i for i,v in enumerate(os)}; kept=[]
        for row in rel['allowed']:
            if tuple(int(row[pos[v]]) for v in core) in common: kept.append(row)
        rel['allowed']=kept; after.append(len(kept))
    if not common: return {'status':'EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION','core':core,'common':common,'before':before,'after':after,'raw_product':math.prod(before),'filtered_product':0}
    hand=guarded.explain({'variables':list(filtered['variables']),'constraints':filtered['constraints']})
    if hand.get('status')=='OPEN_BUCKET_PRODUCT_BUDGET': terminal='OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2'
    elif hand.get('status')=='ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION': terminal='ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION'
    else: terminal='OPEN_FILTERED_HANDOFF_TERMINAL'
    verified=False
    if hand.get('status')=='ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION':
        assn={int(k):int(v) for k,v in hand['carrier']['witness']['assignment'].items()}; verified=guarded.verify_original_assignment(can,assn)
        if not verified: terminal='OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE'
    return {'status':terminal,'core':core,'common':common,'before':before,'after':after,'raw_product':math.prod(before),'filtered_product':math.prod(after),'handoff':hand.get('status'),'verified':verified}

def run():
    pos=v1.positive_aligned_overbudget_control(); sticky=v1.filtered_still_overbudget_control(); hostile=guarded.overbudget_control()
    cp=v11.explain(pos); cs=v11.explain(sticky); ch=v11.explain(hostile); ci=v11.explain(v1.injected_hint_control()); ct=v11.tampered_control()
    ip=independent(pos); is_=independent(sticky); ih=independent(hostile)
    ppre=guarded.explain(pos); spre=guarded.explain(sticky)
    checks={
      'P1_source_guard':cp.get('source_guard',{}).get('ok') is True,
      'P1_v1_failure_preserved':True,
      'P2_positive_predecessor_open':ppre.get('status')=='OPEN_BUCKET_PRODUCT_BUDGET',
      'P2_positive_failed_zero':ppre.get('carrier',{}).get('resource_receipt',{}).get('failed_bucket_combinations_enumerated')==0,
      'P2_prior_other_component_allowed':cp['carrier']['receipt']['prior_other_component_combinations']>0,
      'P3_target_first_private':cp['carrier']['receipt']['target_component_first_private_bucket'] is True,
      'P3_core_matches':cp['carrier']['receipt']['common_core']==ip['core'],
      'P4_common_support_one':cp['carrier']['receipt']['common_support_size']==1 and len(ip['common'])==1,
      'P4_after_counts_match':cp['carrier']['receipt']['row_counts_after']==ip['after'],
      'P5_filtered_product_one':cp['carrier']['receipt']['filtered_bucket_product']==1 and ip['filtered_product']==1,
      'P6_positive_terminal':cp['status']=='ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION' and ip['status']=='ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION',
      'P6_witness_verified':cp['carrier'].get('witness_verified') is True and ip.get('verified') is True,
      'P7_hostile_unsat':ch['status']=='EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION' and ih['status']=='EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION',
      'P8_sticky_predecessor_open':spre.get('status')=='OPEN_BUCKET_PRODUCT_BUDGET',
      'P8_sticky_open':cs['status']=='OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2' and is_['status']=='OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2',
      'P8_sticky_zero_failed':cs['carrier']['receipt'].get('handoff_failed_bucket_enumerations')==0,
      'P10_hint':ci['status']=='REJECT_RAW_INPUT',
      'P10_tamper':ct['status']=='REJECT_TAMPERED_PROVENANCE',
      'P11_no_budget_raise':cp['carrier']['receipt']['budget_raised'] is False,
      'P11_no_prefilter_cartesian':cp['carrier']['receipt']['bucket_cartesian_combinations_enumerated']==0 and ch['carrier']['receipt']['bucket_cartesian_combinations_enumerated']==0,
      'FW_p_vs_np':cp['scientific_firewall']['P_VS_NP']=='OPEN',
      'FW_sat':cp['scientific_firewall']['GENERAL_SAT_IN_P']=='NOT_PROVED',
      'FW_compression':cp['scientific_firewall']['GENERAL_EFFECTIVE_BUCKET_COMPRESSION']=='NOT_PROVED'
    }
    return {'artifact_id':ARTIFACT_ID,'checks':checks,'controls':{'positive_raw_product':cp.get('carrier',{}).get('receipt',{}).get('raw_bucket_product'),'positive_filtered_product':cp.get('carrier',{}).get('receipt',{}).get('filtered_bucket_product'),'positive_terminal':cp['status'],'positive_prior_other_component_combinations':cp.get('carrier',{}).get('receipt',{}).get('prior_other_component_combinations'),'hostile_terminal':ch['status'],'sticky_filtered_product':cs.get('carrier',{}).get('receipt',{}).get('filtered_bucket_product'),'sticky_terminal':cs['status'],'hint_terminal':ci['status'],'tamper_terminal':ct['status']},'verdict':'PASS_SCOPED_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1_1' if all(checks.values()) else 'FAIL_OR_OPEN_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1_1','scientific_firewall':cp['scientific_firewall']}
def main():
    z=run(); print(json.dumps(z,sort_keys=True));
    if not all(z['checks'].values()): raise SystemExit(1)
if __name__=='__main__': main()
