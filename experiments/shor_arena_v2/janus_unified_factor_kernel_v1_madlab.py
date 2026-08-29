#!/usr/bin/env python3
import json
from janus_unified_factor_kernel_v1_core import DAG,Limit,Spider,M2R,Selector,Pippi,C,H,capability,project,join,open_receipt,fp,CAPS

def attack(name,fn):
 try:
  detail=fn();return {'attack':name,'passed':True,'detail':detail}
 except Exception as e:return {'attack':name,'passed':False,'error':type(e).__name__+': '+str(e)}

def run():
 cap=capability();out=[]
 def false_merge():
  D=DAG();a,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':21,'x':5,'y':0,'epsilon':4},{'r':'a'});b,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':45,'x':7,'y':0,'epsilon':4},{'r':'b'});assert a!=b;return {'same_epsilon':4,'distinct_nodes':True}
 out.append(attack('SAME_LABEL_OR_EPSILON_FALSE_MERGE',false_merge))
 def prov_storm():
  D=DAG({**CAPS,'max_serialized_certificate_bytes':600});term=None
  for k in range(50):
   try:D.add('MODULAR_POWER_EQUALITY','MODULAR_EQUALITY',{'N':15,'a':2,'e':4,'residue':1},{'k':k,'padding':'x'*40})
   except Limit as e:term=str(e);break
  assert term=='OPEN_REPRESENTATION_VOLUME' and D.L.unique<600 and D.L.serialized>600;return {'terminal':term,'unique':D.L.unique,'serialized':D.L.serialized,'provenance':D.L.prov}
 out.append(attack('PROVENANCE_STORM',prov_storm))
 def payload_storm():
  D=DAG({**CAPS,'max_unique_payload_bytes':120});term=None
  try:D.add('X','Y',{'blob':'z'*500},{'r':'x'})
  except Limit as e:term=str(e)
  assert term=='OPEN_REPRESENTATION_VOLUME';return {'terminal':term}
 out.append(attack('UNIQUE_PAYLOAD_STORM',payload_storm))
 def stale_m2r():
  D=DAG();n,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':21,'x':5,'y':0,'epsilon':4},{'r':'x'});m=M2R(cap);m.remember(n,D.n[n].lang,H(C(D.n[n].payload)));bad=capability({'successor':1});assert m.get(n,bad)['status']=='CAPABILITY_MISMATCH' and m.get(n,cap)['status']=='EXACT_RETRIEVAL_CANDIDATE';return {'stale_rejected':True}
 out.append(attack('STALE_M2R_CAPABILITY_REUSE',stale_m2r))
 def forged_collision():
  D=DAG();n,_=D.add('RESIDUE_COLLISION_ORDER_MULTIPLE','RESIDUE_COLLISION',{'N':15,'a':2,'i':1,'j':5,'ri':2,'rj':3},{'r':'forge'});r=project(D,n,{'N':15});assert r['status']=='CERTIFICATE_FAILURE';return r
 out.append(attack('FORGED_RESIDUE_COLLISION',forged_collision))
 def forged_order():
  D=DAG();n,_=D.add('EXACT_MULTIPLICATIVE_ORDER','EXACT_ORDER',{'N':15,'a':2,'r':2},{'r':'forge'});r=project(D,n,{'N':15});assert r['status']=='CERTIFICATE_FAILURE';return r
 out.append(attack('FORGED_EXACT_ORDER',forged_order))
 def no_join_cert():
  D=DAG();a,_=D.add('A','PRODUCT',{'x':1},{'r':'a'});b,_=D.add('B','POWER',{'x':2},{'r':'b'});r=join(D,a,b);assert r['status']=='OPEN_NO_CERTIFIED_BOUNDARY_JOIN';return r
 out.append(attack('CROSS_LANGUAGE_JOIN_WITHOUT_CERT',no_join_cert))
 def forged_boundary():
  D=DAG();a,_=D.add('A','PRODUCT',{'x':1},{'r':'a'});b,_=D.add('B','POWER',{'x':2},{'r':'b'});c,_=D.add('BOUNDARY_GATED_COMPOSITION','CONSISTENCY_CERT',{'left':a,'right':b,'verified':False},{'r':'forge'});r=join(D,a,b,c);assert r['status']=='CERTIFICATE_FAILURE';return r
 out.append(attack('FORGED_BOUNDARY_CERT',forged_boundary))
 def spider_injection():
  S=Spider();S.add('heuristic_factor','terminal_factor',1.0);assert not S.certifies('heuristic_factor');return {'authority':'ADVISORY_ONLY'}
 out.append(attack('SPIDER_AUTHORITY_INJECTION',spider_injection))
 def same_episode_keymaster():
  S=Selector(['L1','L2']);before=S.rank();S.log('L2',999,7);assert S.rank()==before;S.close(7);assert S.rank()==before;return {'ranking_unchanged_same_epoch':True,'scope':S.rank()}
 out.append(attack('SAME_EPISODE_KEYMASTER_PROMOTION',same_episode_keymaster))
 def current_pippi():
  P=Pippi();[P.record(e,'L1',10,5,6,'OPEN_DISCOVERY_BUDGET') for e in (1,2,3)];assert P.next_switch(3)=='NO_SIGNAL' and P.next_switch(4)=='NEXT_EPOCH_LANGUAGE_SWITCH_CANDIDATE';return {'same_epoch':'NO_SIGNAL','next_epoch':'CANDIDATE'}
 out.append(attack('CURRENT_EPISODE_PIPPI_SWITCH',current_pippi))
 def fingerprint_identity():
  D1=DAG();a,_=D1.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':21,'x':5,'y':0,'epsilon':4},{'r':'a'});D1.set_front([a]);D2=DAG();b,_=D2.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':45,'x':7,'y':0,'epsilon':4},{'r':'b'});D2.set_front([b]);assert fp(D1.profile())==fp(D2.profile()) and a!=b;D=DAG();x,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':21,'x':5,'y':0,'epsilon':4},{'r':'a'});y,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':45,'x':7,'y':0,'epsilon':4},{'r':'b'});assert join(D,x,y)['status']=='OPEN_NO_CERTIFIED_BOUNDARY_JOIN';return {'same_fingerprint':True,'exact_nodes_distinct':True}
 out.append(attack('FINGERPRINT_EQUALITY_FALSE_IDENTITY',fingerprint_identity))
 def open_drift():
  D=DAG();a,_=D.add('A','PRODUCT',{'x':1},{'r':'a'});b,_=D.add('B','POWER',{'x':2},{'r':'b'});D.set_front([a]);r=open_receipt(D,'OPEN_NO_TRACTABLE_PROJECTION',cap,'frozen');D.set_front([b]);assert r['frontier_node_ids']==[a] and D.front==[b] and r['immutable'];return {'receipt_frontier_frozen':True}
 out.append(attack('OPEN_FRONTIER_WITNESS_DRIFT',open_drift))
 def frontier_overflow():
  D=DAG({**CAPS,'max_frontier_bytes':150});ids=[D.add('L','PRODUCT',{'x':i},{'r':i})[0] for i in range(3)];term=None
  try:D.set_front(ids)
  except Limit as e:term=str(e)
  assert term=='OPEN_INTERFACE_VOLUME';return {'terminal':term}
 out.append(attack('INTERFACE_VOLUME_OVERFLOW',frontier_overflow))
 def canonical_overflow():
  D=DAG({**CAPS,'max_canonicalization_bytes':80});term=None
  try:D.add('L','PRODUCT',{'blob':'q'*200},{'r':'x'})
  except Limit as e:term=str(e)
  assert term=='OPEN_CANONICALIZATION_BUDGET';return {'terminal':term}
 out.append(attack('CANONICALIZATION_BUDGET_OVERFLOW',canonical_overflow))
 def open_negative():
  D=DAG();a,_=D.add('A','PRODUCT',{'x':1},{'r':'a'});D.set_front([a]);r=open_receipt(D,'OPEN_NO_TRACTABLE_PROJECTION',cap,'unknown');assert r['terminal'].startswith('OPEN_') and 'NO_FACTOR' not in r['terminal'] and 'HARD' not in r['terminal'];return {'terminal':r['terminal'],'negative_claim':False}
 out.append(attack('OPEN_TO_NEGATIVE_EVIDENCE_PROMOTION',open_negative))
 hard=[x for x in out if not x['passed']]
 return {'schema':'JANUS/UFK-V1/MAD-LAB/RESULT/v1.0','status':'PASS' if not hard else 'FAIL','attacks':out,'attack_count':len(out),'passed':len(out)-len(hard),'failed':len(hard),'capability_digest':cap,'scientific_boundary':{'polynomial_time_factoring':False,'P_VS_NP':'OPEN'}}
if __name__=='__main__':print(json.dumps(run(),indent=2))
