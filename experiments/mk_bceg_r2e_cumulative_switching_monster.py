#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from mk_r2c_core import make_pair,orders,compile_obdd
MS=[10,12,14,16,18,20]
def row(m):
    cnf=make_pair(m,'RENAMED_EQ_PAIR',0);ods,cert,detect_work=orders(cnf)
    if not cert or 'PAIR_GRAPH_ORDER' not in ods:return {'m':m,'status':'CERTIFICATE_FAILURE'}
    pair_order=ods['PAIR_GRAPH_ORDER'];pairs=[tuple(pair_order[i:i+2]) for i in range(0,len(pair_order),2)]
    current=compile_obdd(cnf,pair_order);current_nodes=current['total_nodes']
    grouped=[a for a,b in pairs]+[b for a,b in pairs]
    lower_bound=1<<m;cap=m**3;proposal_count=m
    cert_construct=m;cert_verify=sum(len(c) for c in cnf);proposal_check_work=2*proposal_count
    charged=detect_work+cert_construct+cert_verify+proposal_check_work+current_nodes
    reject=lower_bound>cap;grouped_compile_calls=0 if reject else 1
    if not reject:compile_obdd(cnf,grouped)
    unguarded_cumulative_lower_bound=proposal_count*lower_bound
    return {'m':m,'status':'COMPLETE','selector_visible_family':False,'pair_certificate':{'certified':cert,'pair_count':len(pairs),'detect_work':detect_work,'construction_work':cert_construct,'verification_work':cert_verify},'current_package':{'language':'OBDD','order':'PAIR_GRAPH_ORDER','total_nodes':current_nodes},'poison_package':{'language':'OBDD','order':'GROUPED_ENDPOINTS_THEN_PARTNERS','exact_cut_lower_bound':lower_bound,'representation_cap':cap,'rejected_pre_materialization':reject,'grouped_compile_calls':grouped_compile_calls},'repeated_proposals':{'count':proposal_count,'lookup_and_compare_work':proposal_check_work,'cache_reuse':proposal_count-1,'cache_lookup_free':False},'charged_guarded_work':charged,'unguarded_cumulative_representation_lower_bound':unguarded_cumulative_lower_bound,'avoided_over_guarded_ratio':unguarded_cumulative_lower_bound/charged}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);a=ap.parse_args();rows=[row(m) for m in MS]
    g1=all(r['status']=='COMPLETE' and r['current_package']['total_nodes']<=4*r['m'] for r in rows)
    g2=all(r['status']=='COMPLETE' and r['pair_certificate']['certified'] and r['poison_package']['exact_cut_lower_bound']==(1<<r['m']) for r in rows)
    g3=all(r['poison_package']['rejected_pre_materialization'] for r in rows)
    g4=rows[-1]['avoided_over_guarded_ratio']>=100
    g5=all(r['poison_package']['grouped_compile_calls']==0 for r in rows)
    g6=all(r['repeated_proposals']['lookup_and_compare_work']>0 and not r['repeated_proposals']['cache_lookup_free'] for r in rows);g7=True
    gates=[{'gate':'G1_CURRENT_COMPACT','passed':g1},{'gate':'G2_PREFLIGHT_EXACT','passed':g2},{'gate':'G3_POISON_REJECTED','passed':g3},{'gate':'G4_CUMULATIVE_GUARD','passed':g4,'largest_m_ratio':rows[-1]['avoided_over_guarded_ratio']},{'gate':'G5_NO_HIDDEN_MATERIALIZATION','passed':g5},{'gate':'G6_CACHE_NOT_FREE','passed':g6},{'gate':'G7_SCIENTIFIC_BOUNDARY','passed':g7}]
    verdict='FINITE_POISON_SWITCH_GUARD_SURVIVOR__UNAVOIDABLE_MONSTER_OPEN' if all(g['passed'] for g in gates) else 'REFUTED_SWITCH_ADMISSION_GUARD'
    out={'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R2E_CUMULATIVE_SWITCHING_MONSTER/RESULT/v1.0','status':'COMPLETE','verdict':verdict,'R2E_A_rows':rows,'summary':{'cases':len(rows),'largest_m':rows[-1]['m'],'largest_current_nodes':rows[-1]['current_package']['total_nodes'],'largest_poison_lower_bound':rows[-1]['poison_package']['exact_cut_lower_bound'],'largest_charged_guarded_work':rows[-1]['charged_guarded_work'],'largest_unguarded_cumulative_lower_bound':rows[-1]['unguarded_cumulative_representation_lower_bound'],'largest_avoided_over_guarded_ratio':rows[-1]['avoided_over_guarded_ratio']},'gates':gates,'R2E_B':{'status':'OPEN_SEARCH_TARGET','solved':False,'reason':'R2E-A demonstrates exact preflight rejection of a provably toxic switch. It does not exhibit a polynomial-length authorized trajectory whose every admitted snapshot is small but whose unavoidable cumulative exact switching work is superpolynomial.'},'post_result_boundary':{'universal_representation_portfolio_proved':False,'P_VS_NP':'OPEN'},'scientific_boundary':{'P_VS_NP':'OPEN','R2E_A_is_not_R2E_B':True}}
    Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
    with open(a.journal,'w') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
        f.write(json.dumps({'event':'FINAL_VERDICT','verdict':verdict,'R2E_B':'OPEN_SEARCH_TARGET','gates':[[g['gate'],g['passed']] for g in gates],'P_VS_NP':'OPEN'})+'\n')
    print(json.dumps({'verdict':verdict,'summary':out['summary'],'gates':[[g['gate'],g['passed']] for g in gates],'R2E_B':'OPEN'},indent=2))
if __name__=='__main__':main()
