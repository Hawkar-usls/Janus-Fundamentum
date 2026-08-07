from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import deque
from pathlib import Path

SCHEMA='janus.c049_1.corrected_node9_residual_up_k_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_node9_residual_up_k_spec.v1'
RESIDUAL_SCHEMA='janus.c049_1.corrected_node9_residual_compact_frontier_candidate.v1'
SPEC_BLOB='f661107212acdca4019dc2d038610e2cdd3beb40'
RESIDUAL_SHA='4d81196e48b75d0f138e97fc2c72ef8984581cb0bb42ea0fd187dcb881a0b62f'
RESIDUAL_SEM='d70faf0fb15023671b4c0441a2d5191ff2e144b0a10151d4c4308355a61cd64e'
SEED=0xC049121
AMBIENT_DIM=1
K=1
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def sem_ok(a): return a.get('semantic_digest_scope')=='proof_payload' and dg(a.get('proof_payload'))==a.get('semantic_digest')
def ordered(xs,mode,tag):
    out=list(xs)
    if mode=='REVERSED': out.reverse()
    elif mode=='SEEDED_SHUFFLE':
        salt=int(hashlib.sha256(tag.encode()).hexdigest()[:16],16); random.Random(SEED^salt).shuffle(out)
    return out

def check_spec(p):
    if gb(p)!=SPEC_BLOB: raise AssertionError('SPEC_BLOB')
    s=load(p)
    if s.get('schema')!=SPEC_SCHEMA or s.get('status')!='SPEC_FROZEN' or s.get('admission') is not False: raise AssertionError('SPEC')
    e=s['expected_values_policy']
    if any(e[k] is not None for k in ('expected_input_generator_count','expected_ordered_relation_count','expected_retained_generator_count','expected_universe_size','expected_closure_entry_count')): raise AssertionError('OUTPUT_ORACLE')
    if e['historical_or_local_values_may_seed_expected_values'] is not False: raise AssertionError('ORACLE_POLICY')
    c=s['canonical_semantics']
    if c['ambient_dim']!=AMBIENT_DIM or c['k']!=K or c['extension_preorder_steps']!=[[1,0],[0,1],[1,1]]: raise AssertionError('SEMANTICS')
    return s

def bind_residual(p):
    if fh(p)!=RESIDUAL_SHA: raise AssertionError('RESIDUAL_SHA')
    a=load(p)
    if a.get('schema')!=RESIDUAL_SCHEMA or not sem_ok(a) or a.get('semantic_digest')!=RESIDUAL_SEM: raise AssertionError('RESIDUAL_SEM')
    return a

def enc(g): return [{'left':list(a),'right':list(b),'value':int(v)} for a,b,v in g]
def dec(raw): return tuple((tuple(map(int,x['left'])),tuple(map(int,x['right'])),int(x['value'])) for x in raw)
def tkey(g): return tuple(g)
def tid(g): return 'UKT-'+dg(enc(g))[:24]
def span(big,small): return (not small) or big==(1,)
def valid(g):
    if not g or g[0][1]!=g[-1][0]: return False
    return all(span(b[0],a[0]) and span(a[1],b[1]) for a,b in zip(g,g[1:]))
def interval(g,i,j):
    if j-i<=1 or (g[i][0],g[i][1])!=(g[j][0],g[j][1]): return False
    a,b=g[i][2],g[j][2]; inner=[x[2] for x in g[i+1:j]]
    return (a<=b and all(a<=x<=b for x in inner)) or (a>=b and all(a>=x>=b for x in inner))
def compact(g):
    s=list(g)
    if not s: raise ValueError('empty')
    while True:
        for i in range(1,len(s)):
            if s[i-1]==s[i]: del s[i]; break
        else:
            hit=None
            for i in range(len(s)):
                for j in range(i+2,len(s)):
                    if interval(s,i,j): hit=(i,j); break
                if hit: break
            if hit:
                i,j=hit; del s[i+1:j]
            else: return tuple(s)
def is_compact(g): return compact(g)==tuple(g)
def stat_leq(a,b): return a[0]==b[0] and a[1]==b[1] and a[2]<=b[2]
def preorder_witness(lower,upper):
    m,n=len(lower),len(upper); parent={}
    for i in range(m):
        for j in range(n):
            if not stat_leq(lower[i],upper[j]): continue
            if i==0 and j==0: parent[(i,j)]=None; continue
            for prev in ((i-1,j-1),(i-1,j),(i,j-1)):
                if prev in parent: parent[(i,j)]=prev; break
    end=(m-1,n-1)
    if end not in parent:return None
    path=[]; cur=end
    while cur is not None: path.append(cur); cur=parent[cur]
    path.reverse(); return path
def witness_obj(path): return {'path':[[i,j] for i,j in path],'path_length':len(path)}
def relation_catalog(gens):
    out=[]; rel={}
    for lower in gens:
        for upper in gens:
            p=preorder_witness(lower,upper)
            if p is not None:
                rel[(tid(lower),tid(upper))]=p
                out.append({'lower_id':tid(lower),'upper_id':tid(upper),'witness':witness_obj(p)})
    return sorted(out,key=lambda x:(x['lower_id'],x['upper_id'])),rel
def minimize(gens,rel):
    gens=tuple(sorted(set(gens),key=tkey)); ids=[tid(g) for g in gens]
    retained=[]
    for j,g in enumerate(gens):
        gid=ids[j]
        strict=[i for i,h in enumerate(gens) if i!=j and (ids[i],gid) in rel and (gid,ids[i]) not in rel]
        equiv_earlier=[i for i in range(j) if (ids[i],gid) in rel and (gid,ids[i]) in rel]
        if not strict and not equiv_earlier: retained.append(g)
    retids={tid(g) for g in retained}; removals=[]
    for g in gens:
        if tid(g) in retids: continue
        candidates=[h for h in retained if (tid(h),tid(g)) in rel]
        if not candidates: raise AssertionError('NO_DIRECT_RETAINED_PREDECESSOR')
        h=min(candidates,key=tkey); p=rel[(tid(h),tid(g))]
        removals.append({'removed_id':tid(g),'retained_id':tid(h),'reason':'STRICTLY_COVERED' if (tid(g),tid(h)) not in rel else 'EQUIVALENT_CANONICAL_REPRESENTATIVE','witness':witness_obj(p)})
    return tuple(sorted(retained,key=tkey)),sorted(removals,key=lambda x:x['removed_id'])
def enumerate_universe(mode):
    subs=[(),(1,)]; states=[(l,r,v) for l in subs for r in subs for v in range(K+1)]
    states=ordered(states,mode,'UNIVERSE_STATES'); maxlen=(2*AMBIENT_DIM+1)*(2*K+1); emitted={}
    def dfs(seq,target):
        last=seq[-1]
        if last[0]==target: emitted[tkey(seq)]=seq
        if len(seq)>=maxlen:return
        for nxt in states:
            if not span(nxt[0],last[0]) or not span(last[1],nxt[1]) or not span(target,nxt[0]): continue
            cand=seq+(nxt,)
            if not is_compact(cand): continue
            dfs(cand,target)
    for first in states:
        if not span(first[1],first[0]): continue
        dfs((first,),first[1])
    return tuple(emitted[k] for k in sorted(emitted))
def closure_entries(gens,universe):
    gens=tuple(sorted(gens,key=tkey)); out=[]
    for cand in universe:
        chosen=None
        for source in gens:
            p=preorder_witness(source,cand)
            if p is not None: chosen=(source,p); break
        if chosen:
            out.append({'trajectory_id':tid(cand),'trajectory':enc(cand),'source_generator_id':tid(chosen[0]),'witness':witness_obj(chosen[1])})
    return sorted(out,key=lambda x:x['trajectory_id'])
def catalog(gens): return [{'trajectory_id':tid(g),'trajectory':enc(g),'trajectory_digest':dg(enc(g)),'length':len(g),'width':max(x[2] for x in g)} for g in sorted(gens,key=tkey)]
def derive_input(residual,mode):
    outs=residual['proof_payload']['global_compact_frontier']['outcomes']
    raw=ordered(outs,mode,'INPUT_FRONTIER'); gens=[]
    for o in raw:
        g=dec(o['trajectory'])
        if not valid(g) or not is_compact(g) or max(x[2] for x in g)>K: raise AssertionError('BAD_INPUT_GENERATOR')
        if o['compact_trajectory_id']!='CT-'+dg(o['trajectory'])[:24]: raise AssertionError('RESIDUAL_TRAJECTORY_ID')
        gens.append(g)
    if len(set(gens))!=len(gens): raise AssertionError('DUP_INPUT')
    return tuple(gens)
def build(specp,residualp,outp,mode):
    spec=check_spec(specp); residual=bind_residual(residualp); inputs=derive_input(residual,mode)
    canonical_inputs=tuple(sorted(inputs,key=tkey)); relcat,rel=relation_catalog(canonical_inputs); retained,removals=minimize(canonical_inputs,rel)
    universe=enumerate_universe(mode)
    universe_cat=catalog(universe)
    original_entries=closure_entries(canonical_inputs,universe); retained_entries=closure_entries(retained,universe)
    if [x['trajectory_id'] for x in original_entries] != [x['trajectory_id'] for x in retained_entries]: raise AssertionError('MINIMIZATION_CHANGED_CLOSURE')
    first_closure=tuple(dec(x['trajectory']) for x in retained_entries)
    second_relcat,second_rel=relation_catalog(tuple(sorted(first_closure,key=tkey)))
    second_retained,_=minimize(first_closure,second_rel)
    second_entries=closure_entries(second_retained,universe)
    if [x['trajectory_id'] for x in second_entries] != [x['trajectory_id'] for x in retained_entries]: raise AssertionError('NOT_IDEMPOTENT')
    proof={
      'candidate_phase':'RESIDUAL_UP_K','candidate_status':'PRODUCER_DERIVED_CANDIDATE','admitted':False,
      'spec_binding':{'spec_schema':SPEC_SCHEMA,'spec_git_blob':SPEC_BLOB,'parent_residual_head':spec['parent_residual_admission']['head_subject'],'parent_residual_review_id':spec['parent_residual_admission']['review_id']},
      'source_binding_receipt':{'residual_sha256':RESIDUAL_SHA,'residual_semantic_digest':RESIDUAL_SEM,'residual_global_frontier_digest':residual['proof_payload']['global_compact_frontier']['frontier_catalog_digest']},
      'semantics':{'ambient_dim':AMBIENT_DIM,'k':K,'b1_subject':spec['canonical_semantics']['b1_core']['subject'],'b1_blob':spec['canonical_semantics']['b1_core']['blob'],'b2_subject':spec['canonical_semantics']['b2_core']['subject'],'b2_blob':spec['canonical_semantics']['b2_core']['blob'],'extension_preorder_steps':[[1,0],[0,1],[1,1]]},
      'input_generators':catalog(canonical_inputs),'input_generator_catalog_digest':dg(catalog(canonical_inputs)),'expected_input_count_used':False,
      'ordered_extension_relation':{'edge_count':len(relcat),'edges':relcat,'edge_catalog_digest':dg(relcat),'expected_edge_count_used':False},
      'minimization':{'retained_generators':catalog(retained),'retained_catalog_digest':dg(catalog(retained)),'removals':removals,'removal_catalog_digest':dg(removals),'expected_retained_count_used':False,'all_removals_directly_witnessed':True,'transitive_only_removal_witnesses':0},
      'complete_universe':{'ambient_dim':AMBIENT_DIM,'k':K,'max_length_bound':(2*AMBIENT_DIM+1)*(2*K+1),'entry_count':len(universe_cat),'entries':universe_cat,'catalog_digest':dg(universe_cat),'expected_universe_size_used':False,'supplied_universe_used':False},
      'closure':{'original_generator_entries':original_entries,'retained_generator_entries':retained_entries,'original_entry_catalog_digest':dg(original_entries),'retained_entry_catalog_digest':dg(retained_entries),'entry_count':len(retained_entries),'closures_equal':True,'expected_entry_count_used':False,'every_entry_directly_witnessed':True},
      'idempotence':{'second_input_entry_count':len(first_closure),'second_relation_edge_count':len(second_relcat),'second_retained_generators':catalog(second_retained),'second_closure_entries':second_entries,'second_closure_digest':dg(second_entries),'first_second_closure_equal':True},
      'work_ledger':{'input_generators_materialized':len(canonical_inputs),'ordered_generator_pairs_tested':len(canonical_inputs)**2,'relation_edges_retained':len(relcat),'complete_universe_entries_materialized':len(universe_cat),'closure_candidate_tests_original':len(universe_cat),'closure_candidate_tests_retained':len(universe_cat),'second_input_generator_pairs_tested':len(first_closure)**2,'supplied_universe_entries_consumed':0},
      'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':'0xC049121','input_order_mode_not_serialized':True,'canonical_input_order':True,'canonical_relation_order':True,'canonical_universe_order':True,'canonical_closure_order':True,'byte_identical_output_required':True},
      'strict_boundary':{'node9_frontier_candidate_complete':True,'node9_parent_refinement_complete':True,'node9_residual_up_k_spec_frozen':True,'node9_residual_up_k_producer_created':True,'node9_residual_up_k_verifier_created':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'repository_failed_domains':0,'repository_successful_domains':0,'root_reached':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'},
      'result':'PRODUCER_DERIVED_RESIDUAL_UP_K_WITHOUT_ADMISSION'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; art['semantic_digest']=dg(proof); save(art,outp); return art

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--residual-artifact',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); a=ap.parse_args()
    art=build(a.spec,a.residual_artifact,a.output,a.order_mode); p=art['proof_payload']
    print('JANUS_NODE9_RESIDUAL_UP_K_PRODUCER = PASS')
    print('INPUT_GENERATORS =',len(p['input_generators']))
    print('ORDERED_EXTENSION_RELATIONS =',p['ordered_extension_relation']['edge_count'])
    print('RETAINED_GENERATORS =',len(p['minimization']['retained_generators']))
    print('COMPLETE_UNIVERSE_SIZE =',p['complete_universe']['entry_count'])
    print('UP_K_CLOSURE_ENTRIES =',p['closure']['entry_count'])
    print('IDEMPOTENT =',p['idempotence']['first_second_closure_equal'])
    print('SEMANTIC_DIGEST =',art['semantic_digest'])
    print('NODE9_PARENT_UP_K_COMPLETE = FALSE')
    print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
