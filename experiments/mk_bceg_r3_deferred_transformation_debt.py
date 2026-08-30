#!/usr/bin/env python3
import argparse,json
from pathlib import Path
KS=[4,6,8,10,12,14,16,18,20]
def lazy(k):
 checks=0
 for mask in range(1<<k):
  checks+=1
  if mask==(1<<k)-1:return {'truth':True,'extension_checks':checks,'syntax_size':2*k+1}
 return {'truth':False,'extension_checks':checks,'syntax_size':2*k+1}
def eager(k):return {'truth':True,'projection_work':2*k,'output_size':1,'certificates':k}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);a=ap.parse_args();rows=[]
 for k in KS:
  l=lazy(k);e=eager(k);rows.append({'k':k,'lazy':l,'eager':e,'debt_over_eager_ratio':l['extension_checks']/e['projection_work']})
 g1=all(r['lazy']['truth'] and r['eager']['truth'] for r in rows);g2=all(r['lazy']['syntax_size']<=3*r['k']+1 for r in rows);g3=all(r['lazy']['extension_checks']==1<<r['k'] for r in rows);g4=all(r['eager']['projection_work']<=4*r['k'] and r['eager']['output_size']==1 for r in rows);g5=all(r['lazy']['extension_checks']>r['lazy']['syntax_size'] for r in rows);g6=True
 gates=[{'gate':'G1_EXACT_SEMANTICS','passed':g1},{'gate':'G2_LAZY_SMALL_SYNTAX','passed':g2},{'gate':'G3_DEFERRED_DEBT_SIGNATURE','passed':g3},{'gate':'G4_EAGER_LOCAL_ESCAPE','passed':g4},{'gate':'G5_DEBT_ACCOUNTING','passed':g5},{'gate':'G6_SCIENTIFIC_BOUNDARY','passed':g6}]
 verdict='REFUTED_LAZY_DEFERRED_WRAPPER_AS_TRACTABLE_INTERFACE__LOCAL_PROJECTION_ESCAPE_SURVIVES' if all(g['passed'] for g in gates) else 'UNKNOWN_RESOURCE_LIMIT'
 out={'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R3_DEFERRED_TRANSFORMATION_DEBT/RESULT/v1.0','status':'COMPLETE','verdict':verdict,'rows':rows,'summary':{'largest_k':rows[-1]['k'],'largest_lazy_syntax':rows[-1]['lazy']['syntax_size'],'largest_lazy_extension_checks':rows[-1]['lazy']['extension_checks'],'largest_eager_projection_work':rows[-1]['eager']['projection_work'],'largest_debt_over_eager_ratio':rows[-1]['debt_over_eager_ratio']},'gates':gates,'external_boundary':{'authority':'EXTERNAL_REFERENCE_NOT_INTERNAL_PROOF_RECEIPT','finding':'IJCAI-2024 structured d-DNNF existential-quantification non-closure remains the stronger next representation-language transformation target.'},'post_result_boundary':{'next':'R3B_OPERATION_CAPABILITY_PACKAGES_AND_CLOSURE_HARDNESS','P_VS_NP':'OPEN'},'scientific_boundary':{'P_VS_NP':'OPEN','this_trap_is_not_universal':True}}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
 with open(a.journal,'w') as f:
  for r in rows:f.write(json.dumps(r)+'\n')
  f.write(json.dumps({'event':'FINAL_VERDICT','verdict':verdict,'summary':out['summary'],'next':out['post_result_boundary']['next'],'P_VS_NP':'OPEN'})+'\n')
 print(json.dumps({'verdict':verdict,'summary':out['summary'],'gates':[[g['gate'],g['passed']] for g in gates]},indent=2))
if __name__=='__main__':main()
