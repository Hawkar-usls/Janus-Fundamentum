#!/usr/bin/env python3
import argparse,itertools,json,pathlib
COL={1,2,3,4}
def ce(a,b):return tuple(sorted((str(a),str(b))))
def E(P):return {ce(a,b) for a,b in P['edges']}
def has(P,a,b):return ce(a,b) in E(P)
def nbr(P,v):return {u for u in P['vertices'] if u!=v and has(P,u,v)}
def Nset(P,A):
 A=set(A);return (set().union(*(nbr(P,v) for v in A))-A) if A else set()
def conn(P,A):
 A=set(A)
 if not A:return False
 st=[next(iter(A))];seen=set()
 while st:
  v=st.pop()
  if v in seen:continue
  seen.add(v);st.extend((nbr(P,v)&A)-seen)
 return seen==A
def proper(P,c):return all((a not in c or b not in c or c[a]!=c[b]) for a,b in E(P))
def indpath(P,seq):
 return len(set(seq))==len(seq) and all(has(P,seq[i],seq[j])==(j==i+1) for i in range(len(seq)) for j in range(i+1,len(seq)))
def p7free(P):
 if len(P['vertices'])<7:return True
 return not any(indpath(P,p) for comb in itertools.combinations(P['vertices'],7) for p in itertools.permutations(comb))
def lset(P,v):return COL-{P['f'][s] for s in nbr(P,v)&set(P['S'])} if v not in P['S'] and v not in P['X0'] else {P['f'][v]}
def input_ok(P):
 V=set(P['vertices']);S=set(P['S']);X0=set(P['X0']);X=set(P['X']);Y0=set(P['Y0']);Y=set(P['Y']);parts=[S,X0,X,Y0,Y]
 if set().union(*parts)!=V or sum(map(len,parts))!=len(V):return False
 if set(P['f'])!=S|X0 or not proper(P,P['f']):return False
 if not conn(P,V-X0) or not conn(P,S) or any(S<=nbr(P,v) for v in V-S):return False
 if Y0!=V-(Nset(P,S)|X0|S):return False
 for a,b in E(P):
  if a in Y0 and b in Y0:
   for v in V-(Y0|X0):
    if has(P,v,a)!=has(P,v,b):return False
 for v in V-S:
  if v not in {1:X0,2:X,3:Y,4:Y0}[len(lset(P,v))]:return False
 return p7free(P)
def typev(P,v):return tuple(sorted(nbr(P,v)&set(P['S'])))
def fT(P,T):return {P['f'][x] for x in T}
def YT(P,T):return {v for v in P['Y'] if typev(P,v)==tuple(T)}
def ny0(P):return Nset(P,P['Y0'])
def pairs(P):
 ts=[];S=sorted(P['S'])
 for r in range(1,len(S)+1):
  for T in itertools.combinations(S,r):
   if len(fT(P,T))==1:ts.append(T)
 return [(a,b) for a in ts for b in ts if fT(P,a)!=fT(P,b)]
def choose(P,c,T,Tp):
 a=next(iter(fT(P,T)));b=next(iter(fT(P,Tp)));L=sorted(YT(P,T)&ny0(P));R=sorted(YT(P,Tp)&ny0(P))
 bad=[(p,n) for p in L for n in R if not has(P,p,n) and c[p] not in {a,b} and c[n] not in {a,b}]
 if bad:
  p,n=bad[0];common=sorted(z for z in P['Y0'] if has(P,p,z) and has(P,n,z))
  if common:return ('A1_111',{'mode':'111','T':T,'Tp':Tp,'p':p,'m':common[0],'n':n})
  A=sorted(z for z in P['Y0'] if has(P,p,z));B=sorted(z for z in P['Y0'] if has(P,n,z));aa,bb=A[0],B[0]
  if has(P,p,bb) or has(P,aa,n) or has(P,aa,bb):return ('FAIL',None)
  return ('A2_SPLIT4',{'mode':'SPLIT4','T':T,'Tp':Tp,'p':p,'a':aa,'b':bb,'n':n})
 cand=[n for n in R if c[n]!=a]
 if cand:return ('B_001',{'mode':'001','T':T,'Tp':Tp,'n':cand[0]})
 return ('C_000',{'mode':'000','T':T,'Tp':Tp})
def supp(st):
 return set() if st['mode']=='000' else ({st['n']} if st['mode']=='001' else ({st['p'],st['m'],st['n']} if st['mode']=='111' else {st['p'],st['a'],st['b'],st['n']}))
def zloc(P,st,var):
 T,Tp=st['T'],st['Tp'];m=st['mode']
 if m=='000':return YT(P,Tp)&ny0(P)
 if m=='001':return ((YT(P,Tp) if var=='formal' else YT(P,T))&ny0(P))-nbr(P,st['n'])
 return set()
def force(P,st,var):
 if st['mode']=='000':return next(iter(fT(P,st['T'])))
 if st['mode']=='001':return next(iter(fT(P,st['T'] if var=='formal' else st['Tp'])))
 return None
def branch_record(P,c,var):
 sts=[];br=[]
 for T,Tp in pairs(P):
  b,s=choose(P,c,T,Tp);br.append((T,Tp,b));sts.append(s)
 A=set().union(*(supp(s) for s in sts)); Z=set().union(*(zloc(P,s,var) for s in sts))
 fmap={}
 for s in sts:
  fc=force(P,s,var)
  if fc is not None:
   for v in zloc(P,s,var):fmap.setdefault(v,set()).add(fc)
 conflict={v:sorted(x) for v,x in fmap.items() if len(x)>1}
 fp={v:c[v] for v in A|Z}
 adm=not conflict and all(fp[v]==next(iter(cs)) for v,cs in fmap.items())
 S2=set(P['S'])|A;X02=set(P['X0'])|(Z-A)
 return {'branches':br,'A':A,'Z':Z,'overlap':A&Z,'forcing':{v:sorted(x) for v,x in fmap.items()},'conflict':conflict,'admissible':adm,'S2':S2,'X02':X02}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('out');a=ap.parse_args();root=pathlib.Path(a.run)
 summ=json.load(open(root/'summary.json'));P=json.load(open(root/'AUTH_SPLIT4_SUPPORT_LEGACY_ZFORCE_OVERLAP.fixture.json'))
 q=json.load(open(root/'QUARANTINED_001_TEXT_DISCREPANCY.receipt.json'));neg=json.load(open(root/'NEG_Z_FORCE_COLOR_CONFLICT.receipt.json'));leg=json.load(open(root/'LEGACY_111_PLUS_000_NORMALIZED_REGRESSION.receipt.json'))
 checks={}
 checks['input_P7_free_axioms']=input_ok(P);checks['c_proper']=proper(P,P['c'])
 r=branch_record(P,P['c'],'formal')
 bm={str((tuple(T),tuple(Tp))):b for T,Tp,b in r['branches']}
 exp={str((('s1',),('s2',))):'A2_SPLIT4',str((('s2',),('s1',))):'A2_SPLIT4',str((('s1',),('s3',))):'C_000',str((('s3',),('s1',))):'C_000',str((('s2',),('s3',))):'A1_111',str((('s3',),('s2',))):'A1_111'}
 checks['frozen_decision_tree']=bm==exp
 checks['mandatory_A']=r['A']=={'p','n','w','a','b'};checks['mandatory_Z']=r['Z']=={'p','w'};checks['mandatory_overlap']=r['overlap']=={'p','w'}
 checks['forcing_preserved']=r['forcing'].get('p')==[3] and r['forcing'].get('w')==[1] and r['admissible']
 checks['physical_seed_semantic_Z']=r['overlap']<=r['S2'] and not (r['overlap']&r['X02'])
 checks['normalized_seed_connected']=conn(P,r['S2']);checks['normalized_fixed_proper']=proper(P,{**P['f'],**{v:P['c'][v] for v in r['A']|r['Z']}})
 exts=json.load(open(root/'main_all_extensions.json'))
 checks['all_extension_records_have_two_variants']=all('formal_definition' in x and 'completeness_text' in x and 'variant_invariant' in x and 'affects_main_authority' in x for x in exts)
 checks['authority_firewall_records']=all((x['affects_main_authority'] is False) for x in exts if not x['authoritative'])
 checks['candidate_counts_match_records']=(summ['exhaustive_main_extensions']['total']==len(exts) and summ['exhaustive_main_extensions']['authoritative']==sum(x['authoritative'] for x in exts) and summ['exhaustive_main_extensions']['quarantined_001']==sum(not x['authoritative'] for x in exts))
 checks['all_authoritative_variants_pass']=all(x['formal_definition']['verdict']=='PASS_VARIANT' for x in exts if x['authoritative'])
 checks['candidate_soundness_exhaustive_pass']=summ['authoritative_candidate_soundness']['pass'] is True and summ['authoritative_candidate_soundness']['checked_global_Q']>0 and summ['authoritative_candidate_soundness']['checked_admissible_functions']>0
 checks['legacy_regression']=leg['expected_old_verdict']=='FAIL_SUPPORT_Z_COLLISION' and leg['verdict']=='PASS_LEGACY_NORMALIZATION_REGRESSION' and leg['overlap_force_preserved'] is True
 checks['negative_conflict_detected']=neg['verdict']=='PASS_NEGATIVE_CONTROL' and neg['detail'].get('reason')=='FAIL_Z_FORCE_COLOR_CONFLICT'
 qq=q['001_quarantine'];checks['explicit_001_quarantine_complete']=all(k in qq for k in ['formal_definition','completeness_text','variant_invariant','affects_main_authority']) and qq['affects_main_authority'] is False
 checks['full_domain_open_if_quarantine']=summ['full_source_domain']=='OPEN_DUE_TO_001_AMBIGUITY' if summ['exhaustive_main_extensions']['quarantined_001'] else True
 ceiling=summ['ceiling'];checks['ceiling']=ceiling=={'SUBGATE_A':'OPEN','LEMMA7_P7_TRANSFER':'NOT_STARTED','LEMMA10_P7_TRANSFER':'NOT_STARTED','BREAK_B':'NOT_STARTED','SUBGATE_B':'NOT_STARTED','LEMMA11_P7_LIFT':'OPEN','P7_FREE_4_COLOR_IN_P':'NOT_PROVED','HARDNESS_LOCALIZED':'NOT_CLAIMED','P_VS_NP':'OPEN'}
 scientific=summ['scientific_gate']
 if scientific=='P7_SPLIT4_NORMALIZED_RAW_EQUIVALENCE_AUTHORITATIVE_CORE_VERIFIED':
  verdict='INDEPENDENT_AUTHORITATIVE_CORE_PASS' if all(checks.values()) else 'INDEPENDENT_REPLAY_FAIL'
 else:
  ff=summ.get('first_failure');checks['failure_witness_present']=isinstance(ff,dict) and ff.get('verdict')==scientific and ff.get('witness') is not None and scientific!='FAIL_SUPPORT_Z_COLLISION'
  verdict='INDEPENDENT_WITNESS_CARRYING_FAIL_RECORDED' if all(checks.values()) else 'INDEPENDENT_REPLAY_FAIL'
 out={'schema':'janus.trump.p7_split4.normalized_raw_rerun.independent.v1','verdict':verdict,'scientific_gate_seen':scientific,'checks':checks,'independent_main':{'branches':[(list(T),list(Tp),b) for T,Tp,b in r['branches']],'A':sorted(r['A']),'Z_FORCE':sorted(r['Z']),'overlap':sorted(r['overlap']),'forcing':r['forcing']},'authority_ceiling':ceiling}
 pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'verdict':verdict,'failed':[k for k,v in checks.items() if not v]},sort_keys=True))
 if verdict=='INDEPENDENT_REPLAY_FAIL':raise SystemExit(1)
if __name__=='__main__':main()
