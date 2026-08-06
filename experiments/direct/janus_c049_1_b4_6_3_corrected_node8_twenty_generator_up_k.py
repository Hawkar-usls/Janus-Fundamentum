#!/usr/bin/env python3
import argparse,copy,hashlib,itertools,json,random
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

def cj(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x):return hashlib.sha256(cj(x)).hexdigest()
def fh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
@dataclass(frozen=True,order=True)
class S:left:tuple;right:tuple;value:int

def basis(rows,d=3):
 p=[]
 for raw in rows:
  x=int(raw)
  if not 0<=x<(1<<d):raise AssertionError('vector range')
  for r in p:x=min(x,x^r)
  if x:
   b=x.bit_length()-1;p=[r^x if (r>>b)&1 else r for r in p]+[x];p.sort(reverse=True)
 return tuple(p)
def contains(big,small):
 for raw in small:
  x=int(raw)
  for r in big:x=min(x,x^r)
  if x:return False
 return True
def compact(g):
 a=list(g)
 while 1:
  for i in range(1,len(a)):
   if a[i-1]==a[i]:del a[i];break
  else:
   hit=False
   for i in range(len(a)):
    for j in range(i+2,len(a)):
     if (a[i].left,a[i].right)!=(a[j].left,a[j].right):continue
     v=[q.value for q in a[i:j+1]]
     if (v[0]<=v[-1] and all(v[0]<=z<=v[-1] for z in v[1:-1])) or (v[0]>=v[-1] and all(v[0]>=z>=v[-1] for z in v[1:-1])):
      del a[i+1:j];hit=True;break
    if hit:break
   if not hit:return tuple(a)
   continue
  continue
def enc(g):return [{'left':list(x.left),'right':list(x.right),'value':x.value} for x in g]
def key(g):return tuple((x.left,x.right,x.value) for x in g)
def parse(raw):
 g=tuple(S(basis(x['left']),basis(x['right']),int(x['value'])) for x in raw)
 if any(x.value not in (0,1) for x in g) or g[0].right!=g[-1].left:raise AssertionError('trajectory')
 for a,b in zip(g,g[1:]):
  if not contains(b.left,a.left) or not contains(a.right,b.right):raise AssertionError('monotonicity')
 if compact(g)!=g:raise AssertionError('noncompact')
 return g
def runs(g):
 sk=[];ps=[]
 for x in g:
  z=(x.left,x.right)
  if not sk or sk[-1]!=z:sk.append(z);ps.append([x.value])
  else:ps[-1].append(x.value)
 ps=tuple(tuple(x) for x in ps)
 if any(x not in PATS for x in ps) or len(set(sk))!=len(sk):raise AssertionError('runs')
 return tuple(sk),ps
def leq(a,b):return a.left==b.left and a.right==b.right and a.value<=b.value

def wit(lo,up,L=None):
 if L is not None:L['preorder_calls']=L.get('preorder_calls',0)+1
 par={}
 for i,a in enumerate(lo):
  for j,b in enumerate(up):
   if L is not None:L['lattice_cells']=L.get('lattice_cells',0)+1
   if not leq(a,b):continue
   if (i,j)==(0,0):par[(i,j)]=None;continue
   for q in ((i-1,j-1),(i-1,j),(i,j-1)):
    if L is not None:L['lattice_predecessor_tests']=L.get('lattice_predecessor_tests',0)+1
    if q in par:par[(i,j)]=q;break
 end=(len(lo)-1,len(up)-1)
 if end not in par:return None
 out=[];q=end
 while q is not None:out.append(q);q=par[q]
 out.reverse()
 if L is not None:
  L['direct_witnesses']=L.get('direct_witnesses',0)+1;L['lattice_path_vertices']=L.get('lattice_path_vertices',0)+len(out)
 return {'path':[[i,j] for i,j in out],'path_length':len(out)}
def wok(lo,up,w):
 p=w.get('path')
 if not isinstance(p,list) or not p:return False
 try:p=[(int(i),int(j)) for i,j in p]
 except:return False
 if p[0]!=(0,0) or p[-1]!=(len(lo)-1,len(up)-1):return False
 if any((b[0]-a[0],b[1]-a[1]) not in ((1,0),(0,1),(1,1)) for a,b in zip(p,p[1:])):return False
 return all(0<=i<len(lo) and 0<=j<len(up) and leq(lo[i],up[j]) for i,j in p) and w.get('path_length')==len(p)

def scalar(L):
 found=set()
 for n in range(1,16):
  for v in itertools.product((0,1),repeat=n):
   L['binary_scalar_sequences_tested']=L.get('binary_scalar_sequences_tested',0)+1
   g=tuple(S((),(),x) for x in v)
   if compact(g)==g:found.add(v)
 if tuple(sorted(found))!=PATS:raise AssertionError('patterns')
 edges=[];allow={}
 for a in PATS:
  lo=tuple(S((),(),x) for x in a);allow[a]=[]
  for b in PATS:
   up=tuple(S((),(),x) for x in b);w=wit(lo,up,L)
   if w:allow[a].append(b);edges.append({'lower':list(a),'upper':list(b),'direct_witness':w})
  allow[a].sort()
 edges.sort(key=cj)
 return {'patterns':[list(x) for x in PATS],'relation_edges':edges,'relation_edge_count':len(edges),'allowed_upper_patterns':{''.join(map(str,a)):[''.join(map(str,b)) for b in allow[a]] for a in PATS}}
def order(items,mode):
 a=copy.deepcopy(list(items))
 if mode=='reversed':a.reverse()
 elif mode=='seeded-shuffle':random.Random(0xC04911620).shuffle(a)
 elif mode!='original':raise AssertionError('order')
 return a
def source(path):
 if fh(path)!=SRC_SHA:raise AssertionError('source sha')
 x=json.load(open(path))
 if x.get('schema')!=SRC_SCHEMA or x.get('semantic_digest')!=SRC_SEM or x.get('next_gate')!=GATE:raise AssertionError('source bind')
 if len(x.get('invariant_vector',{}))!=12 or set(x['invariant_vector'].values())!={'PASS'}:raise AssertionError('source invariants')
 if x.get('corrected_path_domain')!={'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]],'extension_preorder_diagonal_preserved':True,'legacy_delannoy_node8_frontier_consumed':False}:raise AssertionError('path domain')
 q=x['node8_parent_refinement']['quotient_frontier'];cs=q['classes']
 if q.get('class_catalog_digest')!=SRC_CLASSES or len(cs)!=20 or q.get('post_shrink_class_count')!=20 or q.get('local_direct_assignment_tests')!=17424:raise AssertionError('source classes')
 if any(c.get('length')!=5 or c.get('width')!=1 for c in cs):raise AssertionError('source shape')
 return x,cs

def build(src,out,mode='original'):
 x,cs=source(src);L={};sc=scalar(L);recs=[]
 for pos,c in enumerate(order(cs,mode)):
  g=parse(c['canonical_generator'])
  if dg(enc(g))!=c['generator_digest']:raise AssertionError('generator digest')
  sk,ps=runs(g);recs.append({'class_id':c['class_id'],'source_index':pos,'g':g,'sk':sk,'ps':ps})
 recs.sort(key=lambda r:(key(r['g']),r['class_id']))
 if len({key(r['g']) for r in recs})!=20:raise AssertionError('duplicates')
 rel={}
 for i,a in enumerate(recs):
  for j,b in enumerate(recs):
   L['generator_pair_tests']=L.get('generator_pair_tests',0)+1;w=wit(a['g'],b['g'],L)
   if w:rel[(i,j)]=w
 summary={'ordered_pair_tests':400,'relation_edges':len(rel),'self_relation_edges':sum((i,i) in rel for i in range(20)),'cross_relation_edges':sum(i!=j for i,j in rel),'strict_cross_relation_edges':sum(i!=j and (j,i) not in rel for i,j in rel),'equivalent_cross_relation_pairs':sum(i<j and (i,j) in rel and (j,i) in rel for i in range(20) for j in range(20))}
 if summary!={'ordered_pair_tests':400,'relation_edges':20,'self_relation_edges':20,'cross_relation_edges':0,'strict_cross_relation_edges':0,'equivalent_cross_relation_pairs':0}:raise AssertionError('relation')
 retained=recs;rem=[]
 codes={''.join(map(str,p)):p for p in PATS};allow={codes[a]:tuple(codes[b] for b in bs) for a,bs in sc['allowed_upper_patterns'].items()}
 entries=[];seen=set()
 for si,r in enumerate(retained):
  for ass in itertools.product(*(allow[p] for p in r['ps'])):
   g=tuple(S(l,rr,int(v)) for (l,rr),vals in zip(r['sk'],ass) for v in vals);L['reachable_candidates_constructed']=L.get('reachable_candidates_constructed',0)+1
   if compact(g)!=g or key(g) in seen:raise AssertionError('closure')
   seen.add(key(g));w=wit(r['g'],g,L)
   if not w or not wok(r['g'],g,w):raise AssertionError('witness')
   entries.append({'trajectory':enc(g),'source_generator_index':si,'source_class_id':r['class_id'],'source_run_patterns':[list(p) for p in r['ps']],'upper_run_patterns':[list(p) for p in ass],'direct_witness':w,'witness_kind':'EXTENSION_PREORDER_DIRECT'})
 entries.sort(key=lambda e:cj(e['trajectory']))
 if len(entries)!=8676:raise AssertionError('closure count')
 checks=0
 for r in retained:
  for p in r['ps']:
   first=set(allow[p])
   for mid in allow[p]:checks+=len(allow[mid]);assert set(allow[mid]).issubset(first)
 inp=[{'class_id':r['class_id'],'generator':enc(r['g']),'generator_digest':dg(enc(r['g']))} for r in recs]
 ret=[{'class_id':r['class_id'],'generator':enc(r['g']),'generator_digest':dg(enc(r['g'])),'skeleton_length':len(r['sk']),'run_patterns':[list(p) for p in r['ps']]} for r in retained]
 sh=hashlib.sha256()
 for e in entries:sh.update(cj(e['trajectory'])+b'\n')
 proof={'candidate_status':'CONSTRUCTIVE_CANDIDATE','admitted':False,'node_id':8,'ambient_dim':3,'k':1,'source':{'parent_pr':114,'admitted_exact_head':SRC_HEAD,'artifact_sha256':SRC_SHA,'semantic_digest':SRC_SEM,'schema':SRC_SCHEMA,'class_catalog_digest':SRC_CLASSES,'post_shrink_class_count':20,'local_direct_assignment_tests':17424,'ordinary_join_diagonal_allowed':False},'input_family':{'generator_count':20,'family_digest':dg(inp),'generators':inp},'preorder_hardening':{**summary,'retained_generator_count':20,'direct_removal_count':0,'retained_family_digest':dg(ret),'retained_generators':ret,'removals':rem,'pairwise_incomparable':True,'all_removals_direct':True,'transitive_closure_used':False},'scalar_typical_catalog':sc,'reachable_closure':{'complete_reachable_catalog':8676,'reachable_entry_count':8676,'reachable_entries_digest':dg(entries),'reachable_stream_sha256':sh.hexdigest(),'entries':entries,'all_entries_have_direct_witness':True,'transitive_closure_used':False,'global_compact_universe_enumerated':False,'global_universe_entries_enumerated':0},'idempotence':{'proved':True,'method':'BLOCKWISE_UPWARD_SET_TRANSITIVITY','scalar_transitivity_checks':checks,'global_repeated_geometry_blocks':0},'work_ledger':dict(sorted(L.items())),'invariant_vector':{f'CN8U-INV-{i:02d}':'PASS' for i in range(1,13)},'strict_boundary':{'pr114_exact_head_ci_green':True,'pr114_node8_refinement_admitted':True,'corrected_node8_parent_generator_frontier_complete':True,'corrected_node8_parent_refinement_complete':True,'corrected_node8_parent_up_k_candidate_complete':True,'corrected_node8_parent_up_k_complete':False,'corrected_node8_up_k_admitted':False,'corrected_node8_integrated_into_bottom_up_executor':False,'corrected_node9_parent_refinement_started':False,'corrected_bottom_up_replay_complete':False,'root_parent_refinement_complete':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'},'next_gate_after_admission':NEXT,'next_gate_status':'CLOSED_PENDING_EXACT_HEAD_CI_AND_ADMISSION'}
 art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof,'semantic_digest':dg(proof)};Path(out).write_bytes(cj(art)+b'\n');return art

def main():
 a=argparse.ArgumentParser();a.add_argument('source');a.add_argument('--output',required=True);a.add_argument('--entry-order',choices=('original','reversed','seeded-shuffle'),default='original');z=a.parse_args();x=build(z.source,z.output,z.entry_order);p=x['proof_payload']
 print('JANUS_C049_1_B4_6_3_CORRECTED_NODE8_TWENTY_GENERATOR_UP_K = PASS');print('INPUT_GENERATORS = 20');print('RETAINED_GENERATORS = 20');print('DIRECT_REMOVALS = 0');print('RELATION_EDGES = 20');print('PAIRWISE_INCOMPARABLE = True');print('COMPLETE_REACHABLE_CATALOG = 8676');print('IDEMPOTENT = True');print('CANDIDATE_STATUS = CONSTRUCTIVE_CANDIDATE');print('ADMITTED = False');print('SEMANTIC_DIGEST =',x['semantic_digest']);print('CURRENT_GLOBAL_TERMINAL =',TERM)
if __name__=='__main__':main()
