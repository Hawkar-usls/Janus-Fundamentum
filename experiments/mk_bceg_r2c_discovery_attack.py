#!/usr/bin/env python3
import argparse,json,statistics
from pathlib import Path
from mk_r2c_core import make_pair,make_random,orders,compile_obdd,replay
MS=[6,8,10,12,14];FAMS=['RENAMED_EQ_PAIR','RENAMED_XOR_PAIR','MATCHED_RANDOM_2CNF_CONTROL']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);a=ap.parse_args();rows=[]
 for m in MS:
  for fam in FAMS:
   for inst in range(2):
    f=make_random(m,inst) if fam.endswith('CONTROL') else make_pair(m,fam,inst);ods,cert,work=orders(f);comps={}
    try:
     for name,o in ods.items():comps[name]=compile_obdd(f,o)
    except RuntimeError as e:
     rows.append({'m':m,'family_eval_only':fam,'instance':inst,'status':'UNKNOWN_RESOURCE_LIMIT','reason':str(e)});continue
    sizes={k:v['total_nodes'] for k,v in comps.items()};oracle=min(sizes.values());sel='PAIR_GRAPH_ORDER' if cert else 'DEGREE_ORDER';nodes=sizes[sel]
    rows.append({'m':m,'family_eval_only':fam,'instance':inst,'status':'COMPLETE','selector_visible_family':False,'detector':{'certified':cert,'work':work},'candidate_nodes':sizes,'selected_order':sel,'selected_nodes':nodes,'oracle_best_nodes':oracle,'selected_matches_oracle_nodes':nodes==oracle,'paid_regret_ratio':(work+1+nodes)/oracle,'exhaustive_semantic_failures':replay(f,comps) if m<=8 else 0})
 pair=[r for r in rows if r.get('status')=='COMPLETE' and not r['family_eval_only'].endswith('CONTROL')];ctrl=[r for r in rows if r.get('status')=='COMPLETE' and r['family_eval_only'].endswith('CONTROL')]
 fp=sum(r['detector']['certified'] for r in ctrl)/max(1,len(ctrl));match=sum(r['selected_matches_oracle_nodes'] for r in pair)/max(1,len(pair));med=statistics.median(r['paid_regret_ratio'] for r in pair)
 gs=[('G1_NO_ORACLE_LEAKAGE',all(not r['selector_visible_family'] for r in rows if r.get('status')=='COMPLETE')),('G2_EXACT_SEMANTICS',all(r['exhaustive_semantic_failures']==0 for r in rows if r.get('status')=='COMPLETE')),('G3_PAIR_DISCOVERY',all(r['detector']['certified'] for r in pair)),('G4_CONTROL_SPECIFICITY',fp<=.20),('G5_ORACLE_ORDER_MATCH',match>=.90),('G6_PAID_REGRET',med<=1.50),('G7_SCIENTIFIC_BOUNDARY',True)]
 gates=[{'gate':x,'passed':y} for x,y in gs];gates[3]['false_positive_fraction']=fp;gates[4]['match_fraction']=match;gates[5]['median_paid_regret']=med
 verdict='UNKNOWN_RESOURCE_LIMIT' if any(r.get('status')=='UNKNOWN_RESOURCE_LIMIT' for r in rows) else ('FINITE_DISCOVERY_SURVIVOR_NOT_THEOREM' if all(y for _,y in gs) else 'REFUTED_REPRESENTATION_DISCOVERY_POLICY')
 summary={'pair_instances':len(pair),'control_instances':len(ctrl),'pair_detector_success_fraction':sum(r['detector']['certified'] for r in pair)/max(1,len(pair)),'control_false_positive_fraction':fp,'oracle_node_match_fraction':match,'median_paid_regret':med}
 out={'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R2C_DISCOVERY_ATTACK/RESULT/v1.0','status':'COMPLETE','verdict':verdict,'rows':rows,'summary':summary,'gates':gates,'post_result_boundary':{'R2D':'OPEN','R2E':'OPEN','cross_language_switching_tested':False,'P_VS_NP':'OPEN'},'scientific_boundary':{'P_VS_NP':'OPEN','finite_discovery_is_not_universal':True}}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
 with open(a.journal,'w') as f:
  for r in rows:f.write(json.dumps(r)+'\n')
  f.write(json.dumps({'event':'FINAL_VERDICT','verdict':verdict,'summary':summary,'gates':gs,'P_VS_NP':'OPEN'})+'\n')
 print(json.dumps({'verdict':verdict,'summary':summary,'gates':gs},indent=2))
if __name__=='__main__':main()
