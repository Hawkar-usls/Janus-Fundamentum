from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path

SCHEMA='janus.c049_1.corrected_root_empty_up_k_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_root_empty_up_k_spec.v1'
ROOT_SCHEMA='janus.c049_1.corrected_root_full_refinement_candidate.v1'
SPEC_BLOB='0715adc3de2b7d206c84971d4538f73f8e5ddf1e'
ROOT_SHA='74b734c8fc64a789dc4f0e40588956f93ad35ac799dea16417b1180ee5a83900'
ROOT_SEM='82a81c053dbd0bf99bb75f534f4e86ffe3794f06d21a359b76bcffd006fe3dc0'
SEED=0xC049123
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

def enc_seq(seq): return [{'left':[],'right':[],'value':int(v)} for v in seq]
def tid(seq): return 'ROOTUK-'+dg(enc_seq(seq))[:24]
def typical(seq):
    s=list(seq)
    while True:
        changed=False
        for i in range(1,len(s)):
            if s[i-1]==s[i]: del s[i]; changed=True; break
        if changed: continue
        hit=None
        for i in range(len(s)):
            for j in range(i+2,len(s)):
                vals=s[i:j+1]; a,b=vals[0],vals[-1]
                if (a<=b and all(a<=x<=b for x in vals[1:-1])) or (a>=b and all(a>=x>=b for x in vals[1:-1])):
                    hit=(i,j); break
            if hit: break
        if hit:
            i,j=hit; del s[i+1:j]; continue
        return tuple(s)
def universe(mode):
    states=ordered((0,1),mode,'ROOT_EMPTY_STATES'); out={}
    def dfs(seq):
        if typical(seq)==seq: out[seq]=seq
        if len(seq)>=3:return
        for v in states:
            cand=seq+(v,)
            if typical(cand)==cand: dfs(cand)
    for v in states: dfs((v,))
    return tuple(out[k] for k in sorted(out))
def preorder(lower,upper):
    m,n=len(lower),len(upper); reach=set()
    for i in range(m):
        for j in range(n):
            if lower[i]>upper[j]: continue
            if (i,j)==(0,0) or any(x in reach for x in ((i-1,j),(i,j-1),(i-1,j-1))): reach.add((i,j))
    return (m-1,n-1) in reach
def check_spec(p):
    if gb(p)!=SPEC_BLOB: raise AssertionError('spec blob')
    s=load(p)
    if s.get('schema')!=SPEC_SCHEMA or s.get('status')!='SPEC_FROZEN' or s.get('admission') is not False: raise AssertionError('spec')
    e=s['expected_values_policy']
    if any(e[k] is not None for k in ('expected_success_generator_count','expected_complete_universe_size','expected_closure_entry_count')): raise AssertionError('oracle')
    if e['historical_or_local_values_may_seed_expected_values'] is not False: raise AssertionError('oracle policy')
    return s
def bind_root(p):
    if fh(p)!=ROOT_SHA: raise AssertionError('root sha')
    a=load(p)
    if a.get('schema')!=ROOT_SCHEMA or not sem_ok(a) or a.get('semantic_digest')!=ROOT_SEM: raise AssertionError('root semantic')
    return a
def derive_sources(root,mode):
    records=ordered(root['proof_payload']['refinements']['records'],mode,'ROOT_RECORDS'); success_ids=[]; outputs={}; inconsistent=[]
    for r in records:
        expected='SUCCESS' if int(r['final_width'])<=K else 'FAILED'
        if r['classification']!=expected: inconsistent.append(r['refinement_id'])
        if expected=='SUCCESS':
            success_ids.append(r['refinement_id'])
            seq=tuple(int(x['value']) for x in r['final_compact'])
            if any(x['left'] or x['right'] for x in r['final_compact']): raise AssertionError('root boundary not empty')
            if typical(seq)!=seq or max(seq)>K: raise AssertionError('bad success generator')
            outputs.setdefault(dg(r['final_compact']),seq)
    if inconsistent: raise AssertionError('classification inconsistency')
    success_ids=sorted(success_ids); gens=tuple(outputs[k] for k in sorted(outputs))
    return success_ids,gens
def catalog(seqs): return [{'trajectory_id':tid(s),'trajectory':enc_seq(s),'trajectory_digest':dg(enc_seq(s)),'length':len(s),'width':max(s)} for s in sorted(seqs)]
def build(specp,rootp,outp,mode):
    spec=check_spec(specp); root=bind_root(rootp); success_ids,gens=derive_sources(root,mode); U=universe(mode)
    closure=[]
    for cand in U:
        sources=[g for g in gens if preorder(g,cand)]
        if sources:
            src=min(sources); closure.append({'trajectory_id':tid(cand),'trajectory':enc_seq(cand),'source_generator_id':tid(src)})
    closure=sorted(closure,key=lambda x:x['trajectory_id']); second_gens=tuple(tuple(x['value'] for x in e['trajectory']) for e in closure); second=[]
    for cand in U:
        sources=[g for g in second_gens if preorder(g,cand)]
        if sources: second.append({'trajectory_id':tid(cand),'trajectory':enc_seq(cand),'source_generator_id':tid(min(sources))})
    second=sorted(second,key=lambda x:x['trajectory_id'])
    if [x['trajectory_id'] for x in closure] != [x['trajectory_id'] for x in second]: raise AssertionError('not idempotent')
    proof={'candidate_phase':'ROOT_EMPTY_UP_K','candidate_status':'PRODUCER_DERIVED_CANDIDATE','admitted':False,
      'spec_binding':{'spec_git_blob':SPEC_BLOB,'parent_root_head':spec['parent_root_refinement_admission']['head_subject'],'parent_root_review_id':spec['parent_root_refinement_admission']['review_id']},
      'source_binding':{'root_refinement_sha256':ROOT_SHA,'root_refinement_semantic_digest':ROOT_SEM},
      'source_scan':{'root_refinement_record_count':len(root['proof_payload']['refinements']['records']),'classification_inconsistencies':0,'successful_refinement_count':len(success_ids),'successful_refinement_ids':success_ids,'successful_refinement_ids_digest':dg(success_ids),'expected_success_count_used':False},
      'successful_generator_family':{'generator_count':len(gens),'generators':catalog(gens),'catalog_digest':dg(catalog(gens)),'expected_count_used':False},
      'complete_empty_boundary_universe':{'entry_count':len(U),'entries':catalog(U),'catalog_digest':dg(catalog(U)),'max_length_bound':3,'expected_universe_size_used':False,'supplied_universe_used':False},
      'root_up_k_closure':{'entry_count':len(closure),'entries':closure,'catalog_digest':dg(closure),'empty':len(closure)==0,'expected_entry_count_used':False,'universe_entries_with_direct_source_witness':len(closure)},
      'idempotence':{'second_input_entry_count':len(closure),'second_closure_entries':second,'second_closure_digest':dg(second),'first_second_equal':closure==second},
      'work_ledger':{'root_refinement_records_scanned':len(root['proof_payload']['refinements']['records']),'successful_generators_materialized':len(gens),'complete_universe_entries_materialized':len(U),'source_to_universe_relation_tests':len(gens)*len(U),'second_source_to_universe_relation_tests':len(closure)*len(U),'supplied_universe_entries_consumed':0},
      'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':'0xC049123','input_order_mode_not_serialized':True,'canonical_source_order':True,'canonical_universe_order':True,'canonical_closure_order':True,'byte_identical_output_required':True},
      'strict_boundary':{'node9_integrated_into_bottom_up_executor':True,'root_reached':True,'root_parent_refinement_complete':True,'root_parent_up_k_complete':False,'root_full_set_computed':False,'root_empty_proved':False,'terminal_completeness_proved':False,'repository_failed_domains':0,'repository_successful_domains':0,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'},
      'result':'PRODUCER_DERIVED_ROOT_UP_K_CLOSURE_WITHOUT_ADMISSION'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; art['semantic_digest']=dg(proof); save(art,outp); return art
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--root-refinement-artifact',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); a=ap.parse_args(); art=build(a.spec,a.root_refinement_artifact,a.output,a.order_mode); p=art['proof_payload']
    print('JANUS_CORRECTED_ROOT_EMPTY_UP_K_PRODUCER = PASS'); print('ROOT_REFINEMENT_RECORDS_SCANNED =',p['source_scan']['root_refinement_record_count']); print('SUCCESS_GENERATORS =',p['successful_generator_family']['generator_count']); print('COMPLETE_EMPTY_BOUNDARY_UNIVERSE =',p['complete_empty_boundary_universe']['entry_count']); print('ROOT_UP_K_CLOSURE_ENTRIES =',p['root_up_k_closure']['entry_count']); print('ROOT_UP_K_CLOSURE_EMPTY =',p['root_up_k_closure']['empty']); print('IDEMPOTENT =',p['idempotence']['first_second_equal']); print('SEMANTIC_DIGEST =',art['semantic_digest']); print('ROOT_EMPTY_PROVED = FALSE'); print('NO_LAYOUT_AT_CAP = FORBIDDEN'); print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
