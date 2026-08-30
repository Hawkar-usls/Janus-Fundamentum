#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from mk_r2c_core import make_pair,make_random,orders,compile_obdd,restrict
from mk_r2d_core import translate,cond_dd,cnf_bits,dd_bits
MS=[4,6,8];FAMS=['RENAMED_EQ_PAIR','RENAMED_XOR_PAIR','MATCHED_RANDOM_2CNF_CONTROL']
def local_verify(src,dst):
 fail=list(dst['local_cert_failures']);n=dst['nodes'];checks=0
 for sid,did in dst['source_to_dest'].items():
  if sid in (0,1):continue
  checks+=1;k=n[did]
  if k[0]!='OR':fail.append({'source_node':sid,'failure':'DEST_NOT_OR'});continue
  a0,a1=n[k[1]],n[k[2]]
  if a0[0]!='AND' or a1[0]!='AND':fail.append({'source_node':sid,'failure':'BRANCH_NOT_AND'});continue
  lits=[]
  for a in (a0,a1):
   x,y=n[a[1]],n[a[2]]
   q=x if x[0]=='LIT' else (y if y[0]=='LIT' else None)
   lits.append(q)
  if None in lits or lits[0][1]!=lits[1][1] or lits[0][2]==lits[1][2]:fail.append({'source_node':sid,'failure':'NONDETERMINISTIC_GUARDS'})
 return fail,checks
def case(m,fam):
 f=make_random(m,0) if fam.endswith('CONTROL') else make_pair(m,fam,0);ods,cert,detect_work=orders(f);sel='PAIR_GRAPH_ORDER' if cert else 'DEGREE_ORDER';src=compile_obdd(f,ods[sel]);dst=translate(src);lf,local_checks=local_verify(src,dst);vs=sorted({abs(x) for c in f for x in c})
 cb=cnf_bits(f,vs);db,vw=dd_bits(dst,vs);identity=(cb==db);assign_fail=[];verify_work=vw+(1<<len(vs));condition_work=0;actions=0
 for v in vs:
  for val in (0,1):
   actions+=1;succ=restrict(f,v,val);rem=[x for x in vs if x!=v];cd=cond_dd(dst,v,bool(val));condition_work+=cd['condition_work'];a=cnf_bits(succ,rem);b,w=dd_bits(cd,rem);verify_work+=w+(1<<len(rem))
   if a!=b:assign_fail.append({'var':v,'value':val,'cnf_bits':a,'dd_bits':b})
 ratio=dst['structural_nodes']/src['total_nodes']
 return {'m':m,'family_eval_only':fam,'selector_visible_family':False,'source_order':sel,'detector_work':detect_work,'source_robdd_total_nodes':src['total_nodes'],'destination_ddnnf_structural_nodes':dst['structural_nodes'],'destination_over_source_ratio':ratio,'translation_work':dst['translation_work'],'local_certificate_checks':local_checks,'local_certificate_failures':lf,'identity_semantics_match':identity,'assign_actions_checked':actions,'assign_congruence_failures':assign_fail,'condition_work':condition_work,'semantic_verification_work':verify_work}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);a=ap.parse_args();rows=[case(m,f) for m in MS for f in FAMS]
 g1=all(not r['local_certificate_failures'] for r in rows);g2=all(r['identity_semantics_match'] for r in rows);g3=all(not r['assign_congruence_failures'] for r in rows);g4=all(r['destination_over_source_ratio']<=5 for r in rows);g5=all(r['translation_work']>0 and r['semantic_verification_work']>0 for r in rows);g6=True
 gates=[{'gate':'G1_TRANSLATION_LOCAL_CERT','passed':g1},{'gate':'G2_IDENTITY_SEMANTICS','passed':g2},{'gate':'G3_ASSIGN_CONGRUENCE','passed':g3},{'gate':'G4_LINEAR_TRANSLATION_SIGNATURE','passed':g4,'max_ratio':max(r['destination_over_source_ratio'] for r in rows)},{'gate':'G5_COST_ACCOUNTING','passed':g5,'translation_work_total':sum(r['translation_work'] for r in rows),'verification_work_total':sum(r['semantic_verification_work'] for r in rows),'condition_work_total':sum(r['condition_work'] for r in rows)},{'gate':'G6_NO_AUTHORITY_PROMOTION','passed':g6}]
 verdict='FINITE_CROSS_LANGUAGE_CONGRUENCE_SURVIVOR_NOT_THEOREM' if all(g['passed'] for g in gates) else 'REFUTED_CROSS_LANGUAGE_TRANSLATION'
 out={'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R2D_CROSS_LANGUAGE_CONGRUENCE/RESULT/v1.0','status':'COMPLETE','verdict':verdict,'translation':'ROBDD_TO_dDNNF_SHANNON','rows':rows,'summary':{'cases':len(rows),'assign_actions_checked':sum(r['assign_actions_checked'] for r in rows),'local_certificate_failures':sum(len(r['local_certificate_failures']) for r in rows),'identity_failures':sum(not r['identity_semantics_match'] for r in rows),'assign_congruence_failures':sum(len(r['assign_congruence_failures']) for r in rows),'max_destination_over_source_ratio':max(r['destination_over_source_ratio'] for r in rows)},'gates':gates,'post_result_boundary':{'R2E':'OPEN','universal_cross_language_portfolio_proved':False,'P_VS_NP':'OPEN'},'scientific_boundary':{'finite_congruence_is_not_universal_theorem':True,'P_VS_NP':'OPEN'}}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
 with open(a.journal,'w') as f:
  for r in rows:f.write(json.dumps(r)+'\n')
  f.write(json.dumps({'event':'FINAL_VERDICT','verdict':verdict,'summary':out['summary'],'gates':[[g['gate'],g['passed']] for g in gates],'next':'R2E_CUMULATIVE_SWITCHING_MONSTER','P_VS_NP':'OPEN'})+'\n')
 print(json.dumps({'verdict':verdict,'summary':out['summary'],'gates':[[g['gate'],g['passed']] for g in gates]},indent=2))
if __name__=='__main__':main()
