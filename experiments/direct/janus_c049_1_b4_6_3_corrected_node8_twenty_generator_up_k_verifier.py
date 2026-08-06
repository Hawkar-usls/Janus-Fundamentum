#!/usr/bin/env python3
import argparse,ast,hashlib,itertools,json
from dataclasses import dataclass
from pathlib import Path

SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
SRC_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE7-INTEGRATION-NODE8-PARENT-REFINEMENT-v1'
SRC_SHA='30329bdb77802016ef3479d37a29fdb8e1fc95c5d534484fc179916a0cfdbb0a'
SRC_SEM='41df529e471aa4fb1c0ce1192cd4e0fa8ae8de2eb230c38343bbf04abf7f6708'
SRC_CLASSES='9d5a420647f69454ae6deb8114435f433973ae7262f46d6e716e929acde1616c'
SRC_HEAD='ee3ca0c90aff2aaca3b3f3a820dc94c2f3c94539'
GATE='C049.1_B4.6.3_CORRECTED_NODE8_TWENTY_GENERATOR_UP_K_HARDENING'
NEXT='C049.1_B4.6.3_CORRECTED_NODE8_UP_K_INTEGRATION_AND_NODE9_PARENT_REFINEMENT'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
PATS=((0,),(0,1),(0,1,0),(1,),(1,0),(1,0,1))
LEDGER={'binary_scalar_sequences_tested':65534,'direct_witnesses':8716,'generator_pair_tests':400,'lattice_cells':378244,'lattice_path_vertices':74945,'lattice_predecessor_tests':142216,'preorder_calls':9112,'reachable_candidates_constructed':8676}
def cj(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x):return hashlib.sha256(cj(x)).hexdigest()
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
@dataclass(frozen=True,order=True)
class P:left:tuple;right:tuple;v:int

def rb(rows,d=3):
 p=[]
 for raw in rows:
  x=int(raw)
  if not 0<=x<(1<<d):raise AssertionError('range')
  for r in p:x=min(x,x^r)
  if x:
   b=x.bit_length()-1;p=[r^x if (r>>b)&1 else r for r in p]+[x];p.sort(reverse=True)
 return tuple(p)
def sub(big,small):
 for raw in small:
  x=int(raw)
  for r in big:x=min(x,x^r)
  if x:return False
 return True
def red(g):
 a=list(g)
 while 1:
  for i in range(1,len(a)):
   if a[i-1]==a[i]:del a[i];break
  else:
   hit=False
   for i in range(len(a)):
    for j in range(i+2,len(a)):
     if (a[i].left,a[i].right)!=(a[j].left,a[j].right):continue
     v=[q.v for q in a[i:j+1]]
     if (v[0]<=v[-1] and all(v[0]<=z<=v[-1] for z in v[1:-1])) or (v[0]>=v[-1] and all(v[0]>=z>=v[-1] for z in v[1:-1])):
      del a[i+1:j];hit=True;break
    if hit:break
   if not hit:return tuple(a)
   continue
  continue
def ser(g):return [{'left':list(x.left),'right':list(x.right),'value':x.v} for x in g]
def ky(g):return tuple((x.left,x.right,x.v) for x in g)
def parse(raw):
 g=tuple(P(rb(x['left']),rb(x['right']),int(x['value'])) for x in raw)
 if any(x.v not in (0,1) for x in g) or g[0].right!=g[-1].left:raise AssertionError('trajectory')
 for a,b in zip(g,g[1:]):
  if not sub(b.left,a.left) or not sub(a.right,b.right):raise AssertionError('mono')
 if red(g)!=g:raise AssertionError('compact')
 return g
def runs(g):
 sk=[];ps=[]
 for x in g:
  z=(x.left,x.right)
  if not sk or sk[-1]!=z:sk.append(z);ps.append([x.v])
  else:ps[-1].append(x.v)
 ps=tuple(tuple(x) for x in ps)
 if any(x not in PATS for x in ps) or len(set(sk))!=len(sk):raise AssertionError('runs')
 return tuple(sk),ps
def le(a,b):return a.left==b.left and a.right==b.right and a.v<=b.v

def pw(lo,up,L=None):
 if L is not None:L['preorder_calls']=L.get('preorder_calls',0)+1
 par={}
 for i,a in enumerate(lo):
  for j,b in enumerate(up):
   if L is not None:L['lattice_cells']=L.get('lattice_cells',0)+1
   if not le(a,b):continue
   if (i,j)==(0,0):par[(i,j)]=None;continue
   for q in ((i-1,j-1),(i-1,j),(i,j-1)):
    if L is not None:L['lattice_predecessor_tests']=L.get('lattice_predecessor_tests',0)+1
    if q in par:par[(i,j)]=q;break
 e=(len(lo)-1,len(up)-1)
 if e not in par:return None
 out=[];q=e
 while q is not None:out.append(q);q=par[q]
 out.reverse()
 if L is not None:L['direct_witnesses']=L.get('direct_witnesses',0)+1;L['lattice_path_vertices']=L.get('lattice_path_vertices',0)+len(out)
 return {'path':[[i,j] for i,j in out],'path_length':len(out)}
def wok(lo,up,w):
 p=w.get('path')
 if not isinstance(p,list) or not p:return False
 try:p=[(int(i),int(j)) for i,j in p]
 except:return False
 return p[0]==(0,0) and p[-1]==(len(lo)-1,len(up)-1) and all((b[0]-a[0],b[1]-a[1]) in ((1,0),(0,1),(1,1)) for a,b in zip(p,p[1:])) and all(0<=i<len(lo) and 0<=j<len(up) and le(lo[i],up[j]) for i,j in p) and w.get('path_length')==len(p)

def src(path):
 if fh(path)!=SRC_SHA:raise AssertionError('source sha')
 x=json.load(open(path))
 if x.get('schema')!=SRC_SCHEMA or x.get('semantic_digest')!=SRC_SEM or x.get('next_gate')!=GATE:raise AssertionError('source bind')
 if len(x.get('invariant_vector',{}))!=12 or set(x['invariant_vector'].values())!={'PASS'}:raise AssertionError('source inv')
 if x.get('corrected_path_domain')!={'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]],'extension_preorder_diagonal_preserved':True,'legacy_delannoy_node8_frontier_consumed':False}:raise AssertionError('domain')
 q=x['node8_parent_refinement']['quotient_frontier'];cs=q['classes']
 if q.get('class_catalog_digest')!=SRC_CLASSES or len(cs)!=20 or q.get('post_shrink_class_count')!=20 or q.get('local_direct_assignment_tests')!=17424 or any(c.get('length')!=5 or c.get('width')!=1 for c in cs):raise AssertionError('classes')
 return cs

def replay(path):
 L={};found=set()
 for n in range(1,16):
  for v in itertools.product((0,1),repeat=n):
   L['binary_scalar_sequences_tested']=L.get('binary_scalar_sequences_tested',0)+1;g=tuple(P((),(),x) for x in v)
   if red(g)==g:found.add(v)
 if tuple(sorted(found))!=PATS:raise AssertionError('patterns')
 edges=[];allow={}
 for a in PATS:
  lo=tuple(P((),(),x) for x in a);allow[a]=[]
  for b in PATS:
   up=tuple(P((),(),x) for x in b);w=pw(lo,up,L)
   if w:allow[a].append(b);edges.append({'lower':list(a),'upper':list(b),'direct_witness':w})
  allow[a].sort()
 edges.sort(key=cj)
 rec=[]
 for c in src(path):
  g=parse(c['canonical_generator'])
  if dg(ser(g))!=c['generator_digest']:raise AssertionError('digest')
  sk,ps=runs(g);rec.append({'class_id':c['class_id'],'g':g,'sk':sk,'ps':ps})
 rec.sort(key=lambda r:(ky(r['g']),r['class_id']))
 if len({ky(r['g']) for r in rec})!=20:raise AssertionError('unique')
 rel={}
 for i,a in enumerate(rec):
  for j,b in enumerate(rec):
   L['generator_pair_tests']=L.get('generator_pair_tests',0)+1;w=pw(a['g'],b['g'],L)
   if w:rel[(i,j)]=w
 rs={'ordered_pair_tests':400,'relation_edges':len(rel),'self_relation_edges':sum((i,i) in rel for i in range(20)),'cross_relation_edges':sum(i!=j for i,j in rel),'strict_cross_relation_edges':sum(i!=j and (j,i) not in rel for i,j in rel),'equivalent_cross_relation_pairs':sum(i<j and (i,j) in rel and (j,i) in rel for i in range(20) for j in range(20))}
 if rs!={'ordered_pair_tests':400,'relation_edges':20,'self_relation_edges':20,'cross_relation_edges':0,'strict_cross_relation_edges':0,'equivalent_cross_relation_pairs':0}:raise AssertionError('relation')
 entries=[];seen=set()
 for si,r in enumerate(rec):
  for ass in itertools.product(*(tuple(allow[p]) for p in r['ps'])):
   g=tuple(P(l,rr,int(v)) for (l,rr),vals in zip(r['sk'],ass) for v in vals);L['reachable_candidates_constructed']=L.get('reachable_candidates_constructed',0)+1
   if red(g)!=g or ky(g) in seen:raise AssertionError('closure')
   seen.add(ky(g));w=pw(r['g'],g,L)
   if not w or not wok(r['g'],g,w):raise AssertionError('witness')
   entries.append({'trajectory':ser(g),'source_generator_index':si,'source_class_id':r['class_id'],'source_run_patterns':[list(p) for p in r['ps']],'upper_run_patterns':[list(p) for p in ass],'direct_witness':w,'witness_kind':'EXTENSION_PREORDER_DIRECT'})
 entries.sort(key=lambda e:cj(e['trajectory']))
 if len(entries)!=8676 or dict(sorted(L.items()))!=LEDGER:raise AssertionError('receipts')
 checks=0
 for r in rec:
  for p in r['ps']:
   first=set(allow[p])
   for m in allow[p]:checks+=len(allow[m]);assert set(allow[m]).issubset(first)
 inp=[{'class_id':r['class_id'],'generator':ser(r['g']),'generator_digest':dg(ser(r['g']))} for r in rec]
 ret=[{'class_id':r['class_id'],'generator':ser(r['g']),'generator_digest':dg(ser(r['g'])),'skeleton_length':len(r['sk']),'run_patterns':[list(p) for p in r['ps']]} for r in rec]
 sh=hashlib.sha256()
 for e in entries:sh.update(cj(e['trajectory'])+b'\n')
 return {'inp':inp,'ret':ret,'rs':rs,'edges':edges,'allow':{''.join(map(str,a)):[''.join(map(str,b)) for b in allow[a]] for a in PATS},'entries':entries,'stream':sh.hexdigest(),'checks':checks}

def verify(a,r):
 if a.get('schema')!=SCHEMA or a.get('semantic_digest_scope')!='proof_payload':raise AssertionError('schema')
 p=a.get('proof_payload');
 if not isinstance(p,dict) or a.get('semantic_digest')!=dg(p):raise AssertionError('semantic')
 if p.get('candidate_status')!='CONSTRUCTIVE_CANDIDATE' or p.get('admitted') is not False:raise AssertionError('admission')
 if p.get('source')!={'parent_pr':114,'admitted_exact_head':SRC_HEAD,'artifact_sha256':SRC_SHA,'semantic_digest':SRC_SEM,'schema':SRC_SCHEMA,'class_catalog_digest':SRC_CLASSES,'post_shrink_class_count':20,'local_direct_assignment_tests':17424,'ordinary_join_diagonal_allowed':False}:raise AssertionError('source')
 if p.get('input_family')!={'generator_count':20,'family_digest':dg(r['inp']),'generators':r['inp']}:raise AssertionError('input')
 q=p['preorder_hardening']
 for k,v in r['rs'].items():
  if q.get(k)!=v:raise AssertionError('relation field')
 if q.get('retained_generator_count')!=20 or q.get('direct_removal_count')!=0 or q.get('retained_family_digest')!=dg(r['ret']) or q.get('retained_generators')!=r['ret'] or q.get('removals')!=[] or q.get('pairwise_incomparable') is not True or q.get('all_removals_direct') is not True or q.get('transitive_closure_used') is not False:raise AssertionError('hardening')
 s=p['scalar_typical_catalog']
 if s.get('patterns')!=[list(x) for x in PATS] or s.get('relation_edges')!=r['edges'] or s.get('relation_edge_count')!=20 or s.get('allowed_upper_patterns')!=r['allow']:raise AssertionError('scalar')
 c=p['reachable_closure']
 if c.get('complete_reachable_catalog')!=8676 or c.get('reachable_entry_count')!=8676 or c.get('entries')!=r['entries'] or c.get('reachable_entries_digest')!=dg(r['entries']) or c.get('reachable_stream_sha256')!=r['stream'] or c.get('all_entries_have_direct_witness') is not True or c.get('transitive_closure_used') is not False or c.get('global_compact_universe_enumerated') is not False or c.get('global_universe_entries_enumerated')!=0:raise AssertionError('closure')
 if p.get('idempotence')!={'proved':True,'method':'BLOCKWISE_UPWARD_SET_TRANSITIVITY','scalar_transitivity_checks':r['checks'],'global_repeated_geometry_blocks':0} or p.get('work_ledger')!=LEDGER:raise AssertionError('idempotence')
 if p.get('invariant_vector')!={f'CN8U-INV-{i:02d}':'PASS' for i in range(1,13)}:raise AssertionError('invariants')
 b={'pr114_exact_head_ci_green':True,'pr114_node8_refinement_admitted':True,'corrected_node8_parent_generator_frontier_complete':True,'corrected_node8_parent_refinement_complete':True,'corrected_node8_parent_up_k_candidate_complete':True,'corrected_node8_parent_up_k_complete':False,'corrected_node8_up_k_admitted':False,'corrected_node8_integrated_into_bottom_up_executor':False,'corrected_node9_parent_refinement_started':False,'corrected_bottom_up_replay_complete':False,'root_parent_refinement_complete':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'}
 if p.get('strict_boundary')!=b or p.get('next_gate_after_admission')!=NEXT or p.get('next_gate_status')!='CLOSED_PENDING_EXACT_HEAD_CI_AND_ADMISSION':raise AssertionError('boundary')

def static(path):
 t=Path(path).read_text();tree=ast.parse(t)
 bad={'enumerate_compact_trajectories','enumerate_global_compact_universe','global_compact_universe'}
 if any(isinstance(n,ast.Name) and n.id in bad or isinstance(n,ast.Attribute) and n.attr in bad for n in ast.walk(tree)) or 'itertools.product(*(' not in t:raise AssertionError('static')
 print('STATIC_NO_GLOBAL_COMPACT_UNIVERSE_ENUMERATION = PASS')
def tamper(a,r):
 p=a['proof_payload'];tests=[]
 def setv(o,k,v):old=o[k];o[k]=v;return lambda:o.__setitem__(k,old)
 def popv(x):v=x.pop();return lambda:x.append(v)
 def rev(x):x.reverse();return lambda:x.reverse()
 def app(x,v):x.append(v);return lambda:x.pop()
 tests=[lambda:setv(p['source'],'artifact_sha256','0'*64),lambda:setv(p['source'],'admitted_exact_head','0'*40),lambda:setv(p['input_family']['generators'][0]['generator'][0],'value',1),lambda:popv(p['preorder_hardening']['retained_generators']),lambda:app(p['preorder_hardening']['removals'],{'fake':True}),lambda:popv(p['reachable_closure']['entries']),lambda:setv(p['reachable_closure']['entries'][0],'source_class_id','FAKE'),lambda:rev(p['reachable_closure']['entries']),lambda:popv(p['scalar_typical_catalog']['patterns']),lambda:setv(p['idempotence'],'proved',False),lambda:setv(p['strict_boundary'],'corrected_node8_parent_up_k_complete',True),lambda:setv(p['strict_boundary'],'root_empty_proved',True)]
 old=a['semantic_digest'];n=0
 for f in tests:
  undo=f();a['semantic_digest']=dg(p)
  try:verify(a,r)
  except:n+=1
  else:raise AssertionError('tamper accepted')
  finally:undo();a['semantic_digest']=old
 if n!=12:raise AssertionError('tamper count')
 print('DIGEST_REPAIRED_TAMPERS_REJECTED = 12/12')
def main():
 z=argparse.ArgumentParser();z.add_argument('source');z.add_argument('artifact');z.add_argument('--producer-source',required=True);z.add_argument('--tamper-self-test',action='store_true');a=z.parse_args();static(a.producer_source);r=replay(a.source);x=json.load(open(a.artifact));verify(x,r);tamper(x,r) if a.tamper_self_test else None
 print('JANUS_C049_1_B4_6_3_CORRECTED_NODE8_TWENTY_GENERATOR_UP_K_VERIFIER = PASS');print('INVARIANTS = 12/12');print('INPUT_GENERATORS = 20');print('RETAINED_GENERATORS = 20');print('DIRECT_REMOVALS = 0');print('PAIRWISE_INCOMPARABLE = TRUE');print('REACHABLE_ENTRIES = 8676');print('CANDIDATE_STATUS = CONSTRUCTIVE_CANDIDATE');print('ADMITTED = FALSE');print('CURRENT_GLOBAL_TERMINAL =',TERM)
if __name__=='__main__':main()
