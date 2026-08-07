from __future__ import annotations
import argparse, hashlib, json, math, random
from pathlib import Path

SCHEMA='janus.c049_1.corrected_root_full_refinement_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_root_full_refinement_spec.v1'
UPK_SCHEMA='janus.c049_1.corrected_node9_residual_up_k_candidate.v1'
SPEC_BLOB='401c4856de261f6048d313ca62fa43598ea449e0'
UPK_SHA='33aa00a538818b90ccaa0506071d579cf02ca49177b7875833c9625356ffc27f'
UPK_SEM='24de29ece76fe7aa2243c8227619ac74ff587f12ff8b199fb700cc6f29775c36'
SEED=0xC049122
K=1
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
PATTERNS=((0,),(0,1),(0,1,0),(1,),(1,0),(1,0,1))

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

def enc(g): return [{'left':list(a),'right':list(b),'value':int(v)} for a,b,v in g]
def dec(raw): return tuple((tuple(map(int,x['left'])),tuple(map(int,x['right'])),int(x['value'])) for x in raw)
def tr_id(prefix,g): return prefix+'-'+dg(enc(g))[:24]
def sub_sum(a,b): return (1,) if a or b else ()
def sub_inter(a,b): return (1,) if a and b else ()
def dim(s): return len(s)
def contains(big,small): return (not small) or big==(1,)
def valid_trajectory(g):
    if not g or g[0][1]!=g[-1][0]: return False
    return all(contains(b[0],a[0]) and contains(a[1],b[1]) for a,b in zip(g,g[1:]))
def interval(g,i,j):
    if j-i<=1 or (g[i][0],g[i][1])!=(g[j][0],g[j][1]): return False
    a,b=g[i][2],g[j][2]; q=[x[2] for x in g[i+1:j]]
    return (a<=b and all(a<=x<=b for x in q)) or (a>=b and all(a>=x>=b for x in q))
def compact(g):
    s=list(g); trace=[]
    while True:
        changed=False
        for i in range(1,len(s)):
            if s[i-1]==s[i]:
                before=len(s); rem=s[i]; del s[i]
                trace.append({'rule':'duplicate','start':i-1,'end':i,'before_length':before,'after_length':len(s),'removed':enc((rem,))})
                changed=True; break
        if changed: continue
        hit=None
        for i in range(len(s)):
            for j in range(i+2,len(s)):
                if interval(s,i,j): hit=(i,j); break
            if hit: break
        if hit:
            i,j=hit; before=len(s); rem=tuple(s[i+1:j]); del s[i+1:j]
            trace.append({'rule':'interval','start':i,'end':j,'before_length':before,'after_length':len(s),'removed':enc(rem)})
            continue
        return tuple(s),trace
def right_leaf():
    out=[]
    for p in PATTERNS:
        for q in PATTERNS:
            g=tuple([((),(1,),v) for v in p]+[((1,),(),v) for v in q])
            if not valid_trajectory(g) or compact(g)[0]!=g: raise AssertionError('leaf normal form')
            out.append({'leaf_id':tr_id('RL6',g),'source_patterns':[list(p),list(q)],'trajectory':enc(g),'trajectory_digest':dg(enc(g))})
    return sorted(out,key=lambda x:x['leaf_id'])
def hv_paths(m,n):
    path=[(0,0)]
    def rec(i,j):
        if i==m-1 and j==n-1:
            yield tuple(path); return
        if i<m-1:
            path.append((i+1,j)); yield from rec(i+1,j); path.pop()
        if j<n-1:
            path.append((i,j+1)); yield from rec(i,j+1); path.pop()
    yield from rec(0,0)
def path_steps(path):
    return ''.join('H' if b[0]-a[0]==1 else 'V' for a,b in zip(path,path[1:]))
def replay_join(g1,g2,path):
    init=sub_inter(g1[0][1],g2[0][1]); raw=[]; corrections=[]
    for i,j in path:
        a,b=g1[i],g2[j]; left=sub_sum(a[0],b[0]); right=sub_sum(a[1],b[1])
        ar=sub_sum(a[0],a[1]); br=sub_sum(b[0],b[1]); cur=sub_inter(ar,br); corr=dim(init)-dim(cur)
        if corr<0: raise AssertionError('negative join correction')
        raw.append((left,right,a[2]+b[2]+corr)); corrections.append(corr)
    comp,trace=compact(tuple(raw))
    if not valid_trajectory(comp): raise AssertionError('invalid compact join')
    return tuple(raw),tuple(corrections),comp,trace
def replay_shrink(joined):
    pre=[]; corrections=[]
    for l,r,v in joined:
        corr=dim(sub_inter(l,r)); pre.append(((),(),v+corr)); corrections.append(corr)
    final,trace=compact(tuple(pre))
    if not valid_trajectory(final): raise AssertionError('invalid root shrink')
    return tuple(pre),tuple(corrections),final,trace
def check_spec(p):
    if gb(p)!=SPEC_BLOB: raise AssertionError('spec blob')
    s=load(p)
    if s.get('schema')!=SPEC_SCHEMA or s.get('status')!='SPEC_FROZEN' or s.get('admission') is not False: raise AssertionError('spec')
    e=s['expected_values_policy']
    if any(e[k] is not None for k in ('expected_child_pairs','expected_ordinary_hv_refinements','expected_successful_refinements','expected_failed_refinements','expected_final_compact_outputs')): raise AssertionError('result oracle')
    if e['historical_or_local_values_may_seed_expected_values'] is not False: raise AssertionError('oracle policy')
    if s['canonical_semantics']['corrected_join_api']['ordinary_steps']!=[[1,0],[0,1]]: raise AssertionError('ordinary join domain')
    return s
def bind_upk(p):
    if fh(p)!=UPK_SHA: raise AssertionError('upk sha')
    a=load(p)
    if a.get('schema')!=UPK_SCHEMA or not sem_ok(a) or a.get('semantic_digest')!=UPK_SEM: raise AssertionError('upk semantic')
    return a
def build(specp,upkp,outp,mode):
    spec=check_spec(specp); upk=bind_upk(upkp)
    left_entries=upk['proof_payload']['closure']['retained_generator_entries']
    left=[]
    for e in left_entries:
        g=dec(e['trajectory'])
        if not valid_trajectory(g) or compact(g)[0]!=g or max(x[2] for x in g)>K: raise AssertionError('left full-set entry')
        left.append({'trajectory_id':e['trajectory_id'],'trajectory':e['trajectory'],'trajectory_digest':dg(e['trajectory'])})
    left=sorted(left,key=lambda x:x['trajectory_id']); right=right_leaf()
    left_order=ordered(left,mode,'LEFT'); right_order=ordered(right,mode,'RIGHT')
    pair_records=[]; refinements=[]; successful=[]; failed=[]
    for lrow in left_order:
        g1=dec(lrow['trajectory'])
        for rrow in right_order:
            g2=dec(rrow['trajectory']); pair_id='PAIR-'+dg([lrow['trajectory_id'],rrow['leaf_id']])[:24]; pair_ref=[]
            paths=list(hv_paths(len(g1),len(g2))); paths=ordered(paths,mode,pair_id)
            for path in paths:
                steps=path_steps(path)
                if set(steps)-{'H','V'}: raise AssertionError('diagonal ordinary path')
                raw,jcorr,jcomp,jtrace=replay_join(g1,g2,path); spre,scorr,final,strace=replay_shrink(jcomp); width=max(x[2] for x in final); classification='SUCCESS' if width<=K else 'FAILED'
                provenance={'pair_id':pair_id,'left_trajectory_id':lrow['trajectory_id'],'right_leaf_id':rrow['leaf_id'],'path':[[i,j] for i,j in path],'steps':steps}
                rid='REF-'+dg(provenance)[:24]
                rec={'refinement_id':rid,'pair_id':pair_id,'left_trajectory_id':lrow['trajectory_id'],'right_leaf_id':rrow['leaf_id'],'ordinary_hv_path':[[i,j] for i,j in path],'ordinary_hv_steps':steps,'join_raw':enc(raw),'join_correction_vector':list(jcorr),'join_compact':enc(jcomp),'join_compactification_trace':jtrace,'shrink_precompact':enc(spre),'shrink_correction_vector':list(scorr),'final_compact':enc(final),'final_compact_digest':dg(enc(final)),'final_width':width,'classification':classification}
                rec['record_digest']=dg(rec); refinements.append(rec); pair_ref.append(rid)
                (successful if classification=='SUCCESS' else failed).append(rid)
            pair_records.append({'pair_id':pair_id,'left_trajectory_id':lrow['trajectory_id'],'right_leaf_id':rrow['leaf_id'],'left_length':len(g1),'right_length':len(g2),'ordinary_hv_refinement_count':len(paths),'refinement_ids_digest':dg(sorted(pair_ref))})
    pair_records.sort(key=lambda x:x['pair_id']); refinements.sort(key=lambda x:x['refinement_id']); successful.sort(); failed.sort()
    expected_total=sum(math.comb(x['left_length']+x['right_length']-2,x['left_length']-1) for x in pair_records)
    if len(refinements)!=expected_total or len(refinements)!=len(successful)+len(failed): raise AssertionError('conservation')
    outputs={}
    for rec in refinements:
        if rec['classification']=='SUCCESS': outputs.setdefault(rec['final_compact_digest'],rec['final_compact'])
    output_rows=[{'trajectory_digest':k,'trajectory':outputs[k]} for k in sorted(outputs)]
    proof={'candidate_phase':'CORRECTED_ROOT_FULL_REFINEMENT','candidate_status':'PRODUCER_DERIVED_CANDIDATE','admitted':False,
      'spec_binding':{'spec_git_blob':SPEC_BLOB,'parent_up_k_head':spec['parent_up_k_admission']['head_subject'],'parent_up_k_review_id':spec['parent_up_k_admission']['review_id']},
      'source_binding':{'up_k_sha256':UPK_SHA,'up_k_semantic_digest':UPK_SEM},
      'geometry':spec['geometry'],'ordinary_join_domain':{'steps':[[1,0],[0,1]],'diagonal_allowed':False},
      'left_full_set':{'entry_count':len(left),'entries':left,'catalog_digest':dg(left),'expected_count_used':False},
      'right_leaf':{'entry_count':len(right),'entries':right,'catalog_digest':dg(right),'typical_patterns':[list(x) for x in PATTERNS],'expected_count_used':False},
      'child_pairs':{'pair_count':len(pair_records),'records':pair_records,'catalog_digest':dg(pair_records),'expected_count_used':False},
      'refinements':{'ordinary_hv_refinement_count':len(refinements),'records':refinements,'catalog_digest':dg(refinements),'successful_refinement_count':len(successful),'failed_refinement_count':len(failed),'successful_refinement_ids_digest':dg(successful),'failed_refinement_ids_digest':dg(failed),'expected_counts_used':False},
      'successful_generator_frontier':{'distinct_output_count':len(output_rows),'outputs':output_rows,'catalog_digest':dg(output_rows),'expected_count_used':False},
      'conservation_ledger':{'child_pairs':len(pair_records),'ordinary_hv_refinements':len(refinements),'analytic_hv_refinements':expected_total,'successful_refinements':len(successful),'failed_refinements':len(failed),'omitted_child_pairs':0,'duplicated_child_pairs':0,'omitted_refinements':0,'duplicated_refinements':0,'ordinary_diagonal_steps':0,'all_failed_records_materialized':len(failed)==sum(1 for r in refinements if r['classification']=='FAILED')},
      'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':'0xC049122','input_order_mode_not_serialized':True,'canonical_pair_order':True,'canonical_refinement_order':True,'byte_identical_output_required':True},
      'strict_boundary':{'node9_parent_up_k_complete':True,'node9_integrated_into_bottom_up_executor':False,'root_reached':False,'root_parent_refinement_complete':False,'root_parent_up_k_complete':False,'root_full_set_computed':False,'root_empty_proved':False,'repository_failed_domains':0,'repository_successful_domains':0,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'},
      'result':'PRODUCER_DERIVED_ROOT_REFINEMENT_WITHOUT_ADMISSION'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; art['semantic_digest']=dg(proof); save(art,outp); return art
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--up-k-artifact',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); a=ap.parse_args(); art=build(a.spec,a.up_k_artifact,a.output,a.order_mode); p=art['proof_payload']
    print('JANUS_CORRECTED_ROOT_FULL_REFINEMENT_PRODUCER = PASS'); print('LEFT_FULL_SET_ENTRIES =',p['left_full_set']['entry_count']); print('RIGHT_LEAF_ENTRIES =',p['right_leaf']['entry_count']); print('CHILD_PAIRS =',p['child_pairs']['pair_count']); print('ORDINARY_HV_REFINEMENTS =',p['refinements']['ordinary_hv_refinement_count']); print('SUCCESSFUL_REFINEMENTS =',p['refinements']['successful_refinement_count']); print('FAILED_REFINEMENTS =',p['refinements']['failed_refinement_count']); print('DISTINCT_SUCCESS_OUTPUTS =',p['successful_generator_frontier']['distinct_output_count']); print('SEMANTIC_DIGEST =',art['semantic_digest']); print('ROOT_PARENT_REFINEMENT_COMPLETE = FALSE'); print('ROOT_EMPTY_PROVED = FALSE'); print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
