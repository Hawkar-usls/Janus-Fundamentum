from __future__ import annotations

import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as reference_census
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate

ROOT=Path(__file__).resolve().parents[3]
TRAINING={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','8ff66183320ed0516fb0573b0cbe76aa4c0717af8f0bf83d69813a1c837fe37f'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','cf91266425d38475c03dfae3547e809b7c8fdf1ed55ab5f4548785d5acf7b70a'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','3f26b47e41720f2acca5e6fb5444a8b17db566d650e73e911a78969f67975c27'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','f41ebed66be06fc7d22ca64a988aefee00a6d46a1831d2636dcee94e2f5036e2')}
HOLDOUT={
 'UF20_011':(ROOT/'research/source_data/SATLIB_UF20_011_2026-09-17.cnf','d693e2c019a1ceb7abe1bf1c29ffd57d25cde01b','dc043cb67fef03567bcbae82f82a66ee53c476f5d2d91bb5606aa56f9213a7e7'),
 'UF20_012':(ROOT/'research/source_data/SATLIB_UF20_012_2026-09-17.cnf','745e26942701ca6bcb3f9708e9306d7e6385ecdc','6c7750381472768e5f889be53a682316585ea09149b13d8da4070287b9dab705'),
 'UF20_013':(ROOT/'research/source_data/SATLIB_UF20_013_2026-09-17.cnf','62349f4152b5ce1576e380242e7d62bbe2099907','bf4b24d389929b0d3fe8ed25f34077283c745d9fdcc713c57827a7cec272ce42'),
 'UF20_014':(ROOT/'research/source_data/SATLIB_UF20_014_2026-09-17.cnf','9d2c03f1bd246ebcf0892722b522b82bbe07452f','2a39fdba19a928a5d950661f58dfff6a77a36eea0d94907ffc79847a7c87a8ad'),
 'UF20_015':(ROOT/'research/source_data/SATLIB_UF20_015_2026-09-17.cnf','09e4581c3281d62390731e553c2eab48c421166c','0caeb45235dda56ef74f87f9d8b0454ae68fbf8ed5e252d0695c571803c7277b')}
FEATURES=('WL1_MAX_VARIABLE_COLOR_CLASS_SIZE','WL1_VARIABLE_PARTITION_IS_DISCRETE','WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE','WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE');BLOCK={FEATURES[0]:1,FEATURES[1]:True,FEATURES[2]:1,FEATURES[3]:True};CLOSED_ORBIT={'ADMIT_ORBIT_COUNT_QUOTIENT_SAT','ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'}
def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(p):
 cs=[];buf=[];head=None
 for line in p.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):q=s.split();head=(int(q[2]),int(q[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(v) for v in buf})==3;cs.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert head==(20,91) and len(cs)==91 and not buf
 can=''.join(' '.join(map(str,c))+' 0\n' for c in cs).encode();return cs,hashlib.sha256(can).hexdigest()
def reduce_once(raw):
 deg=Counter(v for c in raw['constraints'] for v in set(map(int,c['scope'])));D={int(v) for v in raw['variables'] if deg[int(v)]==1};T={c['id'] for c in raw['constraints'] if D & set(map(int,c['scope']))};red={'variables':[int(v) for v in raw['variables'] if int(v) not in D],'constraints':[c for c in raw['constraints'] if c['id'] not in T]};assert not any(D & set(map(int,c['scope'])) for c in red['constraints']);return red,sorted(D),sorted(T)
def project(src,p):return projection_identity.normalize_projection(src,parse(p)[0])[0]
def regression():
 out={}
 for s,(p,b,h) in TRAINING.items():
  if blob(p)!=b:return False,{s:{'source_blob_ok':False}}
  raw=project(s,p);red,D,T=reduce_once(raw);sha=csha(red);out[s]={'source_blob_ok':True,'projected_sha256':csha(raw),'degree1_variables':D,'target_constraints':T,'reduced_sha256':sha,'expected_reduced_sha256':h,'match':sha==h}
 return all(x['match'] for x in out.values()),out
def rank(d):
 vals=sorted(set(d.values()),key=repr);m={v:i for i,v in enumerate(vals)};return {k:m[v] for k,v in d.items()}
def rel(c):return (len(c['scope']),tuple(sorted(tuple(map(int,r)) for r in c['allowed'])))
def wl(raw):
 ns=[];adj=defaultdict(set);lab={}
 for v in sorted(map(int,raw['variables'])):n=('v',v);ns.append(n);lab[n]=('V',);adj[n]
 for c in raw['constraints']:
  n=('c',str(c['id']));ns.append(n);lab[n]=('C',rel(c));adj[n]
  for v in sorted(set(map(int,c['scope']))):vn=('v',v);adj[n].add(vn);adj[vn].add(n)
 ns=sorted(ns,key=lambda x:(x[0],str(x[1])));vs=[n for n in ns if n[0]=='v'];c1=rank(lab);r1=0
 while True:
  n1=rank({u:(c1[u],tuple(sorted(c1[v] for v in adj[u]))) for u in ns});r1+=1
  if len(set(n1.values()))==len(set(c1.values())):c1=n1;break
  c1=n1
 vc=rank(lab);pairs=list(itertools.product(ns,ns));c2=rank({(u,v):(vc[u],vc[v],u==v,v in adj[u]) for u,v in pairs});r2=0
 while True:
  n2=rank({(u,v):(c2[(u,v)],tuple(sorted((c2[(u,w)],c2[(w,v)]) for w in ns))) for u,v in pairs});r2+=1
  if len(set(n2.values()))==len(set(c2.values())):c2=n2;break
  c2=n2
 s1=sorted(Counter(c1[v] for v in vs).values());s2=sorted(Counter(c2[(v,v)] for v in vs).values());return {FEATURES[0]:max(s1),FEATURES[1]:all(x==1 for x in s1),FEATURES[2]:max(s2),FEATURES[3]:all(x==1 for x in s2),'_receipt':{'variable_count':len(vs),'constraint_count':sum(n[0]=='c' for n in ns),'incidence_vertex_count':len(ns),'incidence_edge_count':sum(len(adj[n]) for n in ns)//2,'wl1_rounds':r1,'wl2_rounds':r2}}
def route(red):
 e=reference_census.eligibility(red);c=compositional_basis.induce_compositional_basis(red);bases=list(e.get('global_candidate_bases') or []);bc=bool(bases) or c.get('status')=='ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO';o={'E1':{'global_candidate_bases':bases,'compositional_status':c.get('status'),'closed_or_admitted':bc}};cl=None
 if bc:cl={'route':'EXISTING_SCHAEFER_OR_COMPOSITIONAL_BASIS','status':c.get('status'),'solver_authority':False};o['E2']={'executed':False};o['E3']={'executed':False}
 else:
  la=reference_census.replay_log_alien(red);o['E2']=la
  if la.get('closed'):win=la.get('winning_attempt') or {};cl={'route':'SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER','status':win.get('status'),'solver_authority':True};o['E3']={'executed':False}
  else:
   q=orbit_candidate.run_candidate(red);o['E3']={'executed':True,'status':q.get('status'),'solver_authority':q.get('solver_authority'),'raw_semantic_sha256':q.get('raw_semantic_sha256'),'cells':q.get('cells'),'generator_edges':q.get('generator_edges'),'quotient_states_Q':q.get('quotient_states_Q'),'resource_receipt':q.get('resource_receipt',{}),'certificate_type':(q.get('certificate') or {}).get('type')}
   if q.get('status') in CLOSED_ORBIT and q.get('solver_authority') is True:cl={'route':'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT','status':q.get('status'),'solver_authority':True}
 o['closure']=cl;o['label']='PORTFOLIO_CLOSED' if cl else 'PORTFOLIO_OPEN';o['signed_route']='NOT_EXECUTED_SOURCE_BOUND_IDENTITY_CONTRACT';return o
def main(cp):
 cand=json.loads(cp.read_text());ok,tr=regression()
 if cand.get('verdict')=='HALT_PREUNBLINDING_TRAINING_REGRESSION_FAILURE':
  good=(not ok and cand.get('training_regression')==tr and cand.get('holdout_formula_reads')==0);return {'verdict':'PASS_INDEPENDENT_PREUNBLINDING_HALT' if good else 'FAIL_INDEPENDENT_PREUNBLINDING_HALT','candidate_imported':False,'holdout_formula_reads':0,'training_regression':tr}
 if not ok:return {'verdict':'FAIL_INDEPENDENT_TRAINING_REGRESSION_DISAGREEMENT','candidate_imported':False,'holdout_formula_reads':0,'training_regression':tr}
 rows=[]
 for s,(p,b,h) in HOLDOUT.items():
  bb=blob(p);cs,fh=parse(p);assert bb==b and fh==h;raw=projection_identity.normalize_projection(s,cs)[0];red,D,T=reduce_once(raw);w=wl(red);r=route(red);rows.append({'source':s,'source_git_blob':bb,'canonical_formula_sha256':fh,'projected_raw_sha256':csha(raw),'projected_variables':len(raw['variables']),'projected_constraints':len(raw['constraints']),'degree1_variables':D,'target_constraints':T,'reduced_raw_sha256':csha(red),'reduced_variables':len(red['variables']),'reduced_constraints':len(red['constraints']),'wl_features':{f:w[f] for f in FEATURES},'wl_receipt':w['_receipt'],'existing_portfolio':r})
 scores={}
 for f in FEATURES:
  ts=[{'source':x['source'],'feature_value':x['wl_features'][f],'blocker_value':BLOCK[f],'is_blocker':x['wl_features'][f]==BLOCK[f],'route_label':x['existing_portfolio']['label'],'matches_prediction':(x['wl_features'][f]==BLOCK[f])==(x['existing_portfolio']['label']=='PORTFOLIO_OPEN')} for x in rows];scores[f]={'tests':ts,'matches':sum(t['matches_prediction'] for t in ts),'survives':all(t['matches_prediction'] for t in ts)}
 sv=sorted(f for f in FEATURES if scores[f]['survives']);labels=sorted({x['existing_portfolio']['label'] for x in rows})
 expected=('FRESH_REPLICATION_ALL_FOUR_SURVIVE_WITH_BOTH_ROUTE_CLASSES' if len(sv)==4 and len(labels)==2 else 'FRESH_REPLICATION_ALL_FOUR_SURVIVE_ONE_ROUTE_CLASS_ONLY__LIMITED' if len(sv)==4 else 'FRESH_REPLICATION_PARTIAL_FEATURE_SURVIVOR_SET' if sv else 'FRESH_REPLICATION_ALL_FOUR_FALSIFIED')
 checks={'training_exact':cand.get('training_regression')==tr,'holdout_rows_exact':cand.get('holdout_rows')==rows,'scores_exact':cand.get('per_feature_scores')==scores,'survivors_exact':cand.get('surviving_features')==sv,'route_coverage_exact':cand.get('route_class_coverage')==labels,'verdict_exact':cand.get('verdict')==expected,'no_retuning':cand.get('resource_receipt',{}).get('posthoc_thresholds_or_combinations')==0,'no_iteration_or_new_route':cand.get('resource_receipt',{}).get('iterated_peeling_rounds')==0 and cand.get('resource_receipt',{}).get('new_routes')==0 and cand.get('resource_receipt',{}).get('signed_route_invocations')==0,'firewall':cand.get('scientific_firewall',{}).get('P_VS_NP')=='OPEN' and cand.get('scientific_firewall',{}).get('GENERAL_SAT_IN_P')=='NOT_PROVED'}
 return {'artifact_id':'JANUS-TRUMP-UF20-011-015-FRESH-GENERIC-PENDANT-WL-REPLICATION-INDEPENDENT-CHECK-2026-09-17-v1.0','verdict':'PASS_INDEPENDENT_FRESH_REPLICATION_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_FRESH_REPLICATION_VERIFICATION','checks':checks,'independent_holdout_rows':rows,'independent_scores':scores,'independent_surviving_features':sv,'expected_candidate_verdict':expected,'candidate_imported':False,'holdout_formula_reads':5,'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED'}}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);a=p.parse_args();r=main(Path(a.candidate));print(json.dumps(r,sort_keys=True,separators=(',',':')));raise SystemExit(0 if r['verdict'].startswith('PASS_') else 1)
