#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math
from collections import Counter, defaultdict, deque
from functools import lru_cache
from pathlib import Path

SCHEMA='janus.c049_1.corrected_node9_scalar_symbolic_automaton_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_node9_scalar_symbolic_automaton_spec.v1.2'
SPEC_SUBJECT='0b6a472d43096d4508a217c938a2988a3315bddc'
SPEC_SHA='44b43927eebfb8145942d7f28f4ada3e85a0aaf4cd9a001d6546f08b8c8c5a9a'
SEED='0xC049119'; SEED_B=bytes.fromhex(SEED[2:].zfill(8))
N8_SHA='80b74b500ae82639e51568a9a6dc70a72668f32991add42bc5ffac05b3f9537f'; N8_SEM='e0017e4e5de933e520c6ea374ef291c07bbbb373478c6f9952911cc376380622'; N8_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
L5_SHA='6e4bbd67747405846b63a87633e34d41b0f720d33a6f55e877717b5463c01882'; L5_SEM='d5dcbaf64366a93420691fd667776f0f577bb0afd0feb588421139c69eb42d65'; L5_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-RIGHT-LEAF5-CANDIDATE-v1'
Q80_SHA='fa21c129ad7c03cad0f46c5a5baeb3941d0c94baadea54718d8059652f3a3375'; Q80_SEM='1463974e2378c60ca6f2ebba961c5366a98c59f9efc65603851e87239229f4a1'; Q80_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
REF_N=98319408; TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(x,p): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_bytes(cj(x)+b'\n')
def order(xs,m):
    xs=list(xs)
    if m=='ORIGINAL': return xs
    if m=='REVERSED': return list(reversed(xs))
    if m=='SEEDED_SHUFFLE': return sorted(xs,key=lambda x:hashlib.sha256(SEED_B+cj(x)).digest())
    raise AssertionError('ORDER_MODE')

def bind(path,sha,sem,schema,pkey,label):
    if fh(path)!=sha: raise AssertionError(label+'_FILE_SHA')
    a=load(path)
    if a.get('schema')!=schema or a.get('semantic_digest_scope')!=pkey or a.get('semantic_digest')!=sem or dg(a[pkey])!=sem: raise AssertionError(label+'_BINDING')
    return a[pkey]

def check_spec(path):
    if fh(path)!=SPEC_SHA: raise AssertionError('SPEC_SHA')
    s=load(path)
    if s.get('schema')!=SPEC_SCHEMA or s.get('version')!='1.2' or s.get('status')!='SPEC_FROZEN': raise AssertionError('SPEC_BIND')
    if s.get('admission') is not False or s.get('next_gate')!='CLOSED' or not s['strict_boundary']['node9_scalar_automaton_spec_frozen']: raise AssertionError('SPEC_BOUNDARY')
    if s['upstream']['research_head']!='97a57154b4fdeed8cbc7ba40fa71b2008757c8f1': raise AssertionError('SPEC_HEAD')
    if s['determinism']!={'modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':SEED,'fixed_seed_required':True,'byte_identical_required':True}: raise AssertionError('SPEC_DETERMINISM')
    e=s['expected_values_policy']
    if any(e[k] is not None for k in ('expected_zero_language_domains','expected_mixed_domains','expected_all_accepting_domains','expected_surviving_fine_lifts')) or e['historical_or_local_counts_may_seed_expected_values'] is not False: raise AssertionError('OUTPUT_ORACLE')
    return s

def skeleton(e):
    out=[]; last=None
    for x in e['trajectory']:
        g=(tuple(map(int,x['left'])),tuple(map(int,x['right'])))
        if g!=last: out.append(g); last=g
    return tuple(out)
def profile(e):
    out=[]; last=None
    for x in e['trajectory']:
        g=(tuple(map(int,x['left'])),tuple(map(int,x['right']))); v=int(x['value'])
        if g!=last: out.append([v]); last=g
        else: out[-1].append(v)
    return tuple(tuple(w) for w in out)
def ew(w): return list(map(int,w))
def wid(w): return 'SW-'+dg(ew(w))[:16]
def lrec(lang):
    words=[ew(w) for w in lang]; return {'language_id':'SL-'+dg(words)[:16],'word_count':len(words),'words':words,'language_digest':dg(words)}

def factor(entries,label):
    ss={skeleton(e) for e in entries}
    if len(ss)!=1: raise AssertionError(label+'_SKELETON')
    sk=next(iter(ss)); ps=[profile(e) for e in entries]
    if any(len(p)!=len(sk) for p in ps): raise AssertionError(label+'_SEGMENTS')
    langs=tuple(tuple(sorted({p[i] for p in ps})) for i in range(len(sk))); unique=set(ps); prod=math.prod(map(len,langs))
    if len(unique)!=len(ps) or len(unique)!=prod: raise AssertionError(label+'_NOT_PRODUCT')
    cat=[[ew(w) for w in p] for p in sorted(unique)]
    r={'label':label,'entry_count':len(entries),'segment_count':len(sk),'skeleton_digest':dg([{'left':list(a),'right':list(b)} for a,b in sk]),'segment_languages':[lrec(x) for x in langs],'unique_profile_count':len(unique),'cartesian_product_cardinality':prod,'no_duplicate_profiles':True,'all_profiles_coordinatewise_in_derived_languages':True,'profile_catalog_digest':dg(cat),'cartesian_factorization_complete':True,'product_materialized_for_proof':False}
    r['factorization_receipt_digest']=dg(r); return langs,r

def sid(s,d):
    qi,lp,rp,li,ri=s; a,b=map(int,d['quotient_path'][qi]); lam=int(lp[li])+int(rp[ri])+int(d['join_correction_vector'][qi])+int(d['shrink_correction_vector'][qi])
    r={'quotient_cell_index':qi,'left_segment_index':a,'right_segment_index':b,'active_left_word_id':wid(lp),'active_right_word_id':wid(rp),'left_offset':li,'right_offset':ri,'lambda':lam}; r['state_id']='SA-'+dg(r)[:20]; return r

def succ(s,q,L,R):
    qi,lp,rp,li,ri=s; a,b=q[qi]; out=[]
    if li+1<len(lp): out.append(('H_INTERNAL',(qi,lp,rp,li+1,ri)))
    elif qi+1<len(q) and q[qi+1]==(a+1,b): out += [('H_CELL',(qi+1,nlp,rp,0,ri)) for nlp in L[a+1]]
    if ri+1<len(rp): out.append(('V_INTERNAL',(qi,lp,rp,li,ri+1)))
    elif qi+1<len(q) and q[qi+1]==(a,b+1): out += [('V_CELL',(qi+1,lp,nrp,li,0)) for nrp in R[b+1]]
    return sorted(out,key=lambda z:(z[0],z[1]))
def terminal(s,q,L,R):
    qi,lp,rp,li,ri=s; a,b=q[qi]
    return qi==len(q)-1 and a==len(L)-1 and b==len(R)-1 and li==len(lp)-1 and ri==len(rp)-1

def automaton(d,L,R,filtered,graph):
    q=tuple(tuple(map(int,x)) for x in d['quotient_path'])
    if not q or q[0]!=(0,0) or q[-1]!=(len(L)-1,len(R)-1): raise AssertionError('QPATH_ENDPOINT')
    if len(d['join_correction_vector'])!=len(q) or len(d['shrink_correction_vector'])!=len(q): raise AssertionError('CORR_LEN')
    corr=tuple(int(a)+int(b) for a,b in zip(d['join_correction_vector'],d['shrink_correction_vector']))
    def ok(s):
        qi,lp,rp,li,ri=s; return (not filtered) or int(lp[li])+int(rp[ri])+corr[qi]<=1
    starts=[(0,lp,rp,0,0) for lp in L[0] for rp in R[0]]; dq=deque(starts); queued=set(starts); seen=set(); edges=defaultdict(list); rejected=0
    while dq:
        s=dq.popleft()
        if s in seen: continue
        seen.add(s)
        if not ok(s): rejected+=1; continue
        for step,t in succ(s,q,L,R):
            edges[s].append((step,t))
            if t not in queued: queued.add(t); dq.append(t)
    @lru_cache(None)
    def count(s):
        if not ok(s): return 0
        if terminal(s,q,L,R): return 1
        return sum(count(t) for _,t in edges.get(s,()))
    runs=sum(count(s) for s in starts); live={s for s in seen if ok(s) and count(s)>0}
    rank=lambda s:(s[0],s[3]+s[4],s[3],wid(s[1]),wid(s[2])); fw=defaultdict(int)
    for s in starts:
        if s in live: fw[s]+=1
    for s in sorted(live,key=rank):
        for _,t in edges.get(s,()):
            if t in live: fw[t]+=fw[s]
    tm=sum(fw[s] for s in live if terminal(s,q,L,R))
    if tm!=runs: raise AssertionError('FORWARD_BACKWARD')
    valid_states=sorted((sid(s,d) for s in seen if ok(s)),key=lambda x:x['state_id']); valid_edges=[]
    for s in sorted(seen,key=rank):
        if not ok(s): continue
        a=sid(s,d)['state_id']
        for step,t in edges.get(s,()):
            if ok(t): valid_edges.append({'from':a,'step':step,'to':sid(t,d)['state_id']})
    valid_edges.sort(key=lambda x:(x['from'],x['step'],x['to']))
    out={'run_multiplicity':runs,'start_state_count':len(starts),'visited_state_count_including_guard_rejections':len(seen),'guard_rejected_state_count':rejected,'guard_valid_state_count':sum(ok(s) for s in seen),'coaccessible_state_count':len(live),'guard_valid_transition_count':sum(len(edges.get(s,())) for s in seen if ok(s)),'coaccessible_transition_count':sum(t in live for s in live for _,t in edges.get(s,())),'terminal_state_count':sum(terminal(s,q,L,R) for s in live),'terminal_prefix_multiplicity':tm,'reachable_graph_digest':dg({'states':valid_states,'edges':valid_edges})}
    if graph:
        states=[]; es=[]
        for s in sorted(live,key=rank):
            r=sid(s,d); r.update(prefix_multiplicity=int(fw[s]),accepting_suffix_multiplicity=int(count(s)),terminal=bool(terminal(s,q,L,R))); states.append(r)
        states.sort(key=lambda x:x['state_id'])
        for s in live:
            for step,t in edges.get(s,()):
                if t in live: es.append({'from':sid(s,d)['state_id'],'step':step,'to':sid(t,d)['state_id']})
        es.sort(key=lambda x:(x['from'],x['step'],x['to'])); g={'states':states,'edges':es,'start_state_ids':sorted({sid(s,d)['state_id'] for s in starts if s in live}),'state_catalog_digest':dg(states),'edge_catalog_digest':dg(es)}; g['graph_digest']=dg(g); out['accepted_symbolic_state_graph']=g
    return out

def compact_iface():
    x={'compact_state_memoization_used':False,'right_congruence_required_for_this_run':False,'width_filter_statement':'AUTOMATON_ACCEPTS(L) iff FINAL_POST_SHRINK_COMPACT_WIDTH(L) <= 1','precompact_lambda_max_preservation_basis':[{'rule':'DUPLICATE_STATE_REMOVAL','reason':'Removing one of two identical consecutive states preserves the maximum lambda.'},{'rule':'MONOTONE_INTERVAL_INTERIOR_REMOVAL','reason':'Every removed interior scalar value lies between retained endpoint scalar values, so no removed value can exceed the retained endpoint maximum.'}],'producer_claim':'MAX_LAMBDA_PRECOMPACT_EQUALS_MAX_LAMBDA_POSTCOMPACT','independent_verifier_proof_required':True}; x['certificate_interface_digest']=dg(x); return x

def build(spec_path,n8_path,l5_path,q80_path,out_path,mode):
    spec=check_spec(spec_path); n8=bind(n8_path,N8_SHA,N8_SEM,N8_SCHEMA,'proof_payload','NODE8'); leaf=bind(l5_path,L5_SHA,L5_SEM,L5_SCHEMA,'leaf_payload','LEAF5'); q80=bind(q80_path,Q80_SHA,Q80_SEM,Q80_SCHEMA,'proof_payload','Q80')
    left=order(n8['reachable_closure']['entries'],mode); right=order(leaf['entries'],mode); domains=order(q80['quotient_domains'],mode)
    if len(left)!=8676 or len(right)!=36 or len(domains)!=80: raise AssertionError('SOURCE_COUNTS')
    led=q80['conservation_ledger']
    if led['sum_fine_lift_multiplicities']!=REF_N or led['omitted_fine_refinement_multiplicity'] or led['duplicated_fine_refinement_multiplicity']: raise AssertionError('Q80_CONSERVATION')
    if any(d['classification']!='UNRESOLVED' or d['success_witness'] is not None or d['failure_witness'] is not None for d in domains): raise AssertionError('Q80_BOUNDARY')
    by=defaultdict(list)
    for e in left: by[e['source_class_id']].append(e)
    if len(by)!=20: raise AssertionError('CLASS_COUNT')
    L={}; receipts=[]
    for cid in sorted(by):
        L[cid],r=factor(by[cid],'NODE8:'+cid); r['source_class_id']=cid; receipts.append(r)
    R,leaf_r=factor(right,'LEAF5')
    words=sorted({w for langs in list(L.values())+[R] for lang in langs for w in lang}); wc=[{'word_id':wid(w),'word':ew(w),'word_digest':dg(ew(w))} for w in words]; wc.sort(key=lambda x:x['word_id'])
    iface=compact_iface(); rows=[]; cls=Counter(); total=good=0; us=fs=live=edges=0; rby={r['source_class_id']:r for r in receipts}
    for d in domains:
        cid=d['source_class_id']; u=automaton(d,L[cid],R,False,False); f=automaton(d,L[cid],R,True,True); n=int(d['fine_lift_multiplicity'])
        if u['run_multiplicity']!=n: raise AssertionError(('DOMAIN_MULTIPLICITY',d['domain_id']))
        g=int(f['run_multiplicity']); typ='ZERO_LANGUAGE' if g==0 else ('ALL_ACCEPTING' if g==n else 'MIXED'); cls[typ]+=1
        post={'projected_geometry_digest':dg(d['projected_geometry']),'join_correction_vector_digest':dg(d['join_correction_vector']),'shrink_correction_vector_digest':dg(d['shrink_correction_vector']),'lambda_formula':'left_scalar_value + right_scalar_value + join_correction + shrink_correction'}
        rec={'domain_id':d['domain_id'],'source_class_id':cid,'quotient_path':d['quotient_path'],'q80_fine_lift_multiplicity':n,'q80_fine_lift_domain_digest':d['fine_lift_domain_digest'],'q80_correction_signature_digest':d['correction_signature_digest'],'join_correction_vector':d['join_correction_vector'],'shrink_correction_vector':d['shrink_correction_vector'],'source_factorization_receipt_digest':rby[cid]['factorization_receipt_digest'],'leaf_factorization_receipt_digest':leaf_r['factorization_receipt_digest'],'classification':typ,'repository_success_promoted':False,'repository_failure_promoted':False,'unrestricted_automaton':u,'width_filtered_automaton':{k:v for k,v in f.items() if k!='accepted_symbolic_state_graph'},'post_shrink_interface':post,'compactification_interface':iface}
        graph=f['accepted_symbolic_state_graph']
        if typ=='ZERO_LANGUAGE':
            if graph['states'] or graph['edges'] or graph['start_state_ids']: raise AssertionError('ZERO_GRAPH')
            z={'certificate_kind':'ZERO_ACCEPTING_LANGUAGE_CANDIDATE','unrestricted_run_multiplicity':n,'accepted_run_multiplicity':0,'width_filtered_reachable_graph_digest':f['reachable_graph_digest'],'width_filter_soundness_and_completeness_status':'PRODUCER_CERTIFICATE_INTERFACE_PENDING_INDEPENDENT_VERIFIER','interpretation_after_independent_verification':'FOR_ALL_FINE_LIFTS: FINAL_POST_SHRINK_COMPACT_WIDTH > 1'}; z['zero_language_certificate_digest']=dg(z); rec['zero_language_certificate']=z; rec['accepted_language']=None
        else:
            a={'accepted_symbolic_state_graph':graph,'accepted_run_multiplicity':g,'post_shrink_interface':post,'compactification_interface':iface}; a['accepted_language_digest']=dg(a); rec['accepted_language']=a; rec['zero_language_certificate']=None
        rec['domain_record_digest']=dg(rec); rows.append(rec); total+=n; good+=g; us+=u['visited_state_count_including_guard_rejections']; fs+=f['visited_state_count_including_guard_rejections']; live+=f['coaccessible_state_count']; edges+=f['coaccessible_transition_count']
    rows.sort(key=lambda x:x['domain_id'])
    if total!=REF_N or sum(cls.values())!=80: raise AssertionError('GLOBAL_CONSERVATION')
    langs={}
    for r in receipts+[leaf_r]:
        for x in r['segment_languages']: langs[x['language_id']]=x
    langs=[langs[k] for k in sorted(langs)]
    src={'spec_subject':SPEC_SUBJECT,'spec_file_sha256':SPEC_SHA,'node8':{'artifact_sha256':N8_SHA,'semantic_digest':N8_SEM,'exact_bound_artifact_validated':True,'reconstruction_contract':spec['input_reconstruction_policy']['node8_source'],'reconstruction_execution':'EXTERNAL_TO_THIS_PRODUCER_RUN_AND_REQUIRED_FOR_EXACT_HEAD_CI'},'leaf5':{'artifact_sha256':L5_SHA,'semantic_digest':L5_SEM,'exact_bound_artifact_validated':True,'reconstruction_contract':spec['input_reconstruction_policy']['leaf5']},'q80':{'artifact_sha256':Q80_SHA,'semantic_digest':Q80_SEM,'exact_bound_artifact_validated':True,'reconstruction_contract':spec['input_reconstruction_policy']['q80'],'reconstruction_execution':'EXTERNAL_TO_THIS_PRODUCER_RUN_AND_REQUIRED_FOR_EXACT_HEAD_CI'},'all_exact_artifact_and_semantic_bindings_pass':True,'unbound_artifact_substitution_allowed':False}; src['source_binding_receipt_digest']=dg(src)
    work={'node8_entries_processed':len(left),'node8_source_classes_factorized':len(L),'leaf5_entries_processed':len(right),'q80_domains_processed':len(rows),'source_scalar_profiles_checked':sum(r['entry_count'] for r in receipts),'leaf_scalar_profiles_checked':leaf_r['entry_count'],'derived_distinct_scalar_words':len(wc),'derived_distinct_segment_languages':len(langs),'unrestricted_symbolic_states_visited':us,'width_filtered_symbolic_states_visited_including_guard_rejections':fs,'width_filtered_coaccessible_states':live,'width_filtered_coaccessible_transitions':edges,'fine_hv_path_records_materialized':0,'child_cartesian_records_materialized':0}
    proof={'candidate_phase':'SCALAR_SYMBOLIC_AUTOMATON','candidate_status':'PRODUCER_DERIVED_CANDIDATE','admitted':False,'spec_binding':{'spec_subject':SPEC_SUBJECT,'spec_schema':SPEC_SCHEMA,'spec_file_sha256':SPEC_SHA,'parent_structural_spec_subject':spec['parent_structural_spec']['subject'],'parent_relation':spec['parent_structural_spec']['relation']},'source_binding_receipt':src,'scalar_factorization':{'derivation_policy':'DERIVE_FROM_BOUND_SOURCE_ONLY','historical_or_local_catalog_used_as_seed':False,'expected_language_catalog_used':False,'node8_source_class_receipts':sorted(receipts,key=lambda r:r['source_class_id']),'leaf5_receipt':leaf_r,'derived_segment_language_catalog':langs,'derived_scalar_word_catalog':wc,'derived_language_catalog_digest':dg(langs)},'symbolic_automaton_contract':{'state_fields':['quotient_cell_index','active_left_scalar_word','active_right_scalar_word','left_offset','right_offset'],'lambda_formula':'left_scalar_value + right_scalar_value + join_correction + shrink_correction','accept_condition':'lambda <= 1','fine_lift_bijection_claim':'DERIVED_BY_COMPLETE_SYMBOLIC_TRANSITION_DAG_PENDING_INDEPENDENT_VERIFIER','compact_state_memoization_used':False,'fine_path_materialization_used':False,'child_cartesian_materialization_used':False},'domain_records':rows,'classification_summary':{'zero_language_domain_count':int(cls['ZERO_LANGUAGE']),'mixed_domain_count':int(cls['MIXED']),'all_accepting_domain_count':int(cls['ALL_ACCEPTING']),'repository_successful_domain_count':0,'repository_failed_domain_count':0,'classification_promoted_to_repository_success_or_failure':False,'expected_classification_counts_used':False},'conservation_ledger':{'q80_domain_count':len(rows),'q80_bound_fine_refinement_total':REF_N,'derived_unrestricted_symbolic_run_total':total,'derived_width_le_1_run_total':good,'derived_width_gt_1_run_total':total-good,'all_domain_unrestricted_counts_match_q80_fine_lift_multiplicity':True,'omitted_fine_refinement_multiplicity':0,'duplicated_fine_refinement_multiplicity':0,'fine_refinement_conservation':True},'width_filter_certificate_interface':iface,'work_ledger':work,'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':SEED,'input_order_mode_not_serialized':True,'canonical_domain_order':True,'byte_identical_output_required':True},'strict_boundary':{'node9_scalar_automaton_spec_frozen':True,'node9_scalar_automaton_producer_created':True,'node9_scalar_automaton_verifier_created':False,'node9_scalar_automaton_candidate_complete':False,'node9_frontier_candidate_complete':False,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'root_reached':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'},'result':'PRODUCER_DERIVED_SCALAR_SYMBOLIC_AUTOMATON_WITHOUT_ADMISSION'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof,'semantic_digest':dg(proof)}; save(art,out_path); return art

def main():
    a=argparse.ArgumentParser(); a.add_argument('--spec',type=Path,required=True); a.add_argument('--node8-artifact',type=Path,required=True); a.add_argument('--leaf5-artifact',type=Path,required=True); a.add_argument('--q80-artifact',type=Path,required=True); a.add_argument('--output',type=Path,required=True); a.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); z=a.parse_args(); x=build(z.spec,z.node8_artifact,z.leaf5_artifact,z.q80_artifact,z.output,z.order_mode); p=x['proof_payload']; c=p['classification_summary']; l=p['conservation_ledger']; print('JANUS_NODE9_SCALAR_SYMBOLIC_AUTOMATON_PRODUCER = PASS'); print('ZERO_LANGUAGE_DOMAINS =',c['zero_language_domain_count']); print('MIXED_DOMAINS =',c['mixed_domain_count']); print('ALL_ACCEPTING_DOMAINS =',c['all_accepting_domain_count']); print('FINE_REFINEMENTS =',l['derived_unrestricted_symbolic_run_total']); print('WIDTH_LE_1_MULTIPLICITY =',l['derived_width_le_1_run_total']); print('WIDTH_GT_1_MULTIPLICITY =',l['derived_width_gt_1_run_total']); print('SEMANTIC_DIGEST =',x['semantic_digest']); print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
