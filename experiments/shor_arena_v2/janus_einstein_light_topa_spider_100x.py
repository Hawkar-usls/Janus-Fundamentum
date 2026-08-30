#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CORPUS=ROOT/'research/JANUS_EINSTEIN_LIGHT_RADIATION_CORPUS_2026-08-30.json'
PREREG=ROOT/'research/JANUS_EINSTEIN_LIGHT_TOPA_SPIDER_100X_PREREGISTRATION_2026-08-30.json'
PASSES=100

CONCEPTS={
 'REPRESENTATION_MISMATCH':['representation mismatch','formal distinction','continuous','discrete'],
 'DUAL_REPRESENTATION':['dual representation','wave particle','wave-particle','wave and particle'],
 'LOCALIZATION':['localized','localization','light quanta','energy quanta'],
 'TIME_REVERSAL':['time reversed','time-reversed','inverse elementary','replay'],
 'TRANSITION_CLOSURE':['transition closure','emission','absorption','stimulated emission','operator grammar'],
 'INVARIANT_BOUNDARY':['invariant boundary','light speed','relativity','boundary'],
 'INTERNAL_VARIABLE_ELIMINATION':['internal variable elimination','eliminate internal','projection','factor_or_lift','elimination'],
 'FLUCTUATION_DECOMPOSITION':['fluctuation','independent evidence','decomposition'],
 'CERTIFICATE_PORTFOLIO':['certificate portfolio','portfolio','proof language','message language'],
 'SHARED_PROOF_DAG':['shared proof dag','content-addressed','hash-cons','dag'],
 'INTERFACE_WIDTH':['interface width','live interface','cut width','boundary message','interface profile'],
 'CERTIFICATE_DISCOVERY':['certificate discovery','discovery complexity','collision certificate','order certificate'],
 'EXACT_PROJECTION':['exact projection','context projection','project','projection utility'],
 'REPRESENTATION_BLOWUP':['representation blow','serialized or-forest','open_representation_volume','width lower','exponential blow'],
 'OPEN_DISCIPLINE':['open_','unknown','silence != negative','timeout != negative'],
 'PIPPI':['pippi','plateau','next_epoch'],
 'KEYMASTER':['keymaster','selector'],
 'M2R':['m2r','exact retrieval','capability replay'],
 'SPIDER':['spider','association != proof','advisory_only'],
 'P_VS_NP':['p_vs_np','p vs np','p=np','p = np'],
 'RESOLUTION':['resolution','resolvent','clause learning','davis-putnam'],
 'POLYNOMIAL_BOUND':['polynomial bound','poly(','polytime','polynomial-time','polynomial time'],
 'COUNTEREXAMPLE':['counterexample','refuted','witness 39100','dead path','graveyard'],
}

BRIDGES={
 'B1_REPRESENTATION_DUALITY':('REPRESENTATION_MISMATCH','CERTIFICATE_PORTFOLIO'),
 'B2_LOCALIZATION_TO_TYPED_STATE':('LOCALIZATION','SHARED_PROOF_DAG'),
 'B3_TIME_REVERSAL_REPLAY':('TIME_REVERSAL','M2R'),
 'B4_TRANSITION_OPERATOR_CLOSURE':('TRANSITION_CLOSURE','CERTIFICATE_DISCOVERY'),
 'B5_INVARIANT_LIVE_BOUNDARY':('INVARIANT_BOUNDARY','INTERFACE_WIDTH'),
 'B6_MAXWELL_ELIMINATION_PROJECTION':('INTERNAL_VARIABLE_ELIMINATION','EXACT_PROJECTION'),
 'B7_FLUCTUATION_EVIDENCE_DECOMP':('FLUCTUATION_DECOMPOSITION','CERTIFICATE_PORTFOLIO'),
 'B8_ELIMINATION_BLOWUP_RISK':('INTERNAL_VARIABLE_ELIMINATION','REPRESENTATION_BLOWUP'),
 'B9_DISCOVERY_WIDTH_COUPLING':('CERTIFICATE_DISCOVERY','INTERFACE_WIDTH'),
 'B10_EXACT_STATE_OPEN_FRONTIER':('SHARED_PROOF_DAG','OPEN_DISCIPLINE'),
}

def norm(s):
 return re.sub(r'\s+',' ',s.lower().replace('_',' ').replace('-',' '))

def digest(x):
 return hashlib.sha256(x if isinstance(x,bytes) else str(x).encode()).hexdigest()

def tag(text):
 t=norm(text); out=[]
 for c,keys in CONCEPTS.items():
  if any(norm(k) in t for k in keys): out.append(c)
 return sorted(set(out))

def load_docs():
 docs=[]
 corp=json.loads(CORPUS.read_text())
 docs.append({'id':'EINSTEIN_CORPUS','path':str(CORPUS.relative_to(ROOT)),'text':json.dumps(corp,ensure_ascii=False,sort_keys=True),'kind':'EINSTEIN'})
 for p in sorted((ROOT/'research').glob('*.json')):
  if p in (CORPUS,PREREG): continue
  try: txt=p.read_text(errors='ignore')
  except Exception: continue
  docs.append({'id':p.name,'path':str(p.relative_to(ROOT)),'text':txt,'kind':'JANUS_RESEARCH'})
 for p in sorted((ROOT/'experiments/shor_arena_v2').glob('*.py')):
  if p.name==Path(__file__).name: continue
  try: txt=p.read_text(errors='ignore')
  except Exception: continue
  docs.append({'id':p.name,'path':str(p.relative_to(ROOT)),'text':txt,'kind':'JANUS_CODE'})
 for d in docs: d['tags']=tag(d['text']); d['sha256']=digest(d['text'])
 return docs

def base_graph(docs):
 edge=defaultdict(float); freq=Counter()
 for d in docs:
  ts=d['tags']
  for x in ts: freq[x]+=1
  for i,a in enumerate(ts):
   for b in ts[i+1:]:
    edge[tuple(sorted((a,b)))]+=1.0
 return edge,freq

def edgev(edge,a,b): return edge.get(tuple(sorted((a,b))),0.0)

def bridge_score(edge,freq,a,b):
 direct=edgev(edge,a,b)
 two=0.0
 for m in CONCEPTS:
  if m in (a,b): continue
  x=edgev(edge,a,m); y=edgev(edge,m,b)
  if x and y: two += min(x,y)/(1.0+math.log2(2+freq[m]))
 return direct+0.35*two

def spiral(docs,edge,freq,journal):
 stable={}; prev_scores={k:0.0 for k in BRIDGES}
 for pno in range(1,PASSES+1):
  forward=pno%2==1; ordered=docs if forward else list(reversed(docs))
  directional=defaultdict(float)
  prior=None
  for d in ordered:
   ts=d['tags'] if forward else list(reversed(d['tags']))
   for i,a in enumerate(ts):
    for b in ts[i+1:]: directional[(a,b)]+=1.0
   if prior:
    for a in prior['tags']:
     for b in d['tags']:
      if a!=b: directional[(a,b)]+=0.05
   prior=d
  for (a,b),v in directional.items():
   edge[tuple(sorted((a,b)))]+=v/(PASSES*4.0)
  scores={k:bridge_score(edge,freq,*ab) for k,ab in BRIDGES.items()}
  deltas={k:scores[k]-prev_scores[k] for k in scores}
  newly=[]
  for k,s in scores.items():
   if s>0 and abs(deltas[k])<0.03:
    stable[k]=stable.get(k,0)+1
    if stable[k]==3:newly.append(k)
   else: stable[k]=0
  entry={'pass':pno,'direction':'FORWARD' if forward else 'REVERSE','top_bridges':sorted(scores.items(),key=lambda x:(-x[1],x[0]))[:5],'newly_stable':newly,'max_abs_delta':max(abs(x) for x in deltas.values()),'graph_digest':digest(json.dumps(sorted((str(k),v) for k,v in edge.items()),sort_keys=True))}
  journal.append(entry); prev_scores=scores
 return prev_scores

def theorem_candidate(scores):
 # A deliberately explicit candidate: useful only if the universal polynomial-width theorem is proved.
 return {
  'name':'BOUNDARY_CERTIFICATE_ELIMINATION_GRAMMAR','status':'THEOREM_CANDIDATE_ONLY',
  'core_state':['exact_constraint_DAG','typed_certificate_portfolio','live_interface_boundary','resource_ledger'],
  'operator_cycle':['DISCOVER_CERTIFICATE_CHAIN','VERIFY_EACH_CERTIFICATE','COMPOSE_ON_SHARED_INTERNAL_VARIABLE','ELIMINATE_INTERNAL_VARIABLE','CANONICALIZE_PROJECTED_BOUNDARY_MESSAGE','UPDATE_LIVE_INTERFACE','REPLAY_OR_FALLBACK'],
  'maxwell_analogy':'Faraday + Ampere-Maxwell + Gauss compose to eliminate an internal field and yield a closed wave equation. JANUS candidate asks whether exact SAT certificates can analogously eliminate internal variables while keeping the live interface polynomial.',
  'required_unproved_lemma':'For every arbitrary CNF of input length n, there exists a discoverable exact elimination chain whose total discovery, representation, interface and verification volume is poly(n).',
  'known_obstruction':'Resolution/variable-elimination width and size can blow up exponentially; the required lemma is precisely where the current candidate is unsupported.',
  'bridge_scores':dict(sorted(scores.items(),key=lambda x:(-x[1],x[0]))),
 }

def proof_gate(candidate,docs):
 checks={
  'explicit_deterministic_algorithm':True,
  'local_projection_soundness_framework':True,
  'arbitrary_CNF_completeness_with_polynomial_only_steps':False,
  'worst_case_runtime_poly_input_bits':False,
  'worst_case_representation_poly_input_bits':False,
  'worst_case_certificate_discovery_poly_input_bits':False,
  'no_hidden_solution_or_oracle':True,
  'known_counterexample_lineage_present':any('COUNTEREXAMPLE' in d['tags'] for d in docs),
  'universal_MAD_LAB_pass':False,
  'claim_scope_arbitrary_SAT_proved':False,
 }
 ok=all(checks.values())
 return {'passed':ok,'checks':checks,'verdict':'P_EQUALS_NP_PROVED' if ok else 'P_VS_NP_OPEN__THEOREM_CANDIDATE_ONLY'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);a=ap.parse_args()
 pre=json.loads(PREREG.read_text()); assert pre['status']=='FROZEN_BEFORE_100X_RESULT_INSPECTION' and pre['passes']==100
 docs=load_docs(); edge,freq=base_graph(docs); journal=[]; scores=spiral(docs,edge,freq,journal)
 cand=theorem_candidate(scores); gate=proof_gate(cand,docs)
 result={
  'schema':'JANUS/EINSTEIN-LIGHT/TOPA-SPIDER-100X/RESULT/v1.0','status':'COMPLETE','passes':100,'documents':len(docs),'corpus_bytes':sum(len(d['text'].encode()) for d in docs),
  'document_class_counts':dict(Counter(d['kind'] for d in docs)),'concept_frequency':dict(freq),
  'top_bridges':sorted(scores.items(),key=lambda x:(-x[1],x[0])),'theorem_candidate':cand,'proof_gate':gate,
  'activation_route':{'authoritative_repo':'Hawkar-usls/Janus-Fundamentum','activator_home':'Hawkar-usls/Hawkar-usls','promotion':'BLOCKED_UNTIL_FORMAL_PROOF' if not gate['passed'] else 'ELIGIBLE_FOR_SEALED_PROOF_POINTER'},
  'scientific_boundary':{'association_is_not_proof':True,'physics_analogy_is_not_complexity_proof':True,'P_VS_NP':'OPEN' if not gate['passed'] else 'P_EQUALS_NP_PROVED_BY_RECEIPT'}
 }
 Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 with Path(a.journal).open('w',encoding='utf-8') as f:
  for x in journal:f.write(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
 print(json.dumps({'passes':100,'documents':len(docs),'top_bridges':result['top_bridges'][:6],'candidate':cand['name'],'proof_gate':gate,'activation':result['activation_route']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
