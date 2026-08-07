#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_6_3_corrected_node9_parent_frontier_structural_compression as base

SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
PARENT='e31c05c7e85ecda2ebf79aebb504f42f9d14009a'
LEFT_N,RIGHT_N,PAIR_N,REF_N=8676,36,312336,98319408
SOURCE_CLASSES,DOMAIN_N=20,80
RIGHT_BASIS=(5,); PARENT_BOUNDARY=(1,); AMBIENT=3
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'; SEED='0xC049119'

def cj(x): return base.cj(x)
def dg(x): return base.dg(x)
def rr(rows): return base.rr(rows,AMBIENT)
def span(rows):
    out={0}
    for r in rows: out|={x^int(r) for x in tuple(out)}
    return out
def ssum(a,b): return rr((*a,*b))
def inter(a,b): return rr(sorted(span(a)&span(b)))
def coord(space,basis):
    rows=[]
    for mask in space:
        v=0
        for i,q in enumerate(basis):
            if (int(mask)>>i)&1: v^=int(q)
        rows.append(v)
    return rr(rows)

def seg(tr):
    sk=[]; runs=[]; scal=[]
    for s in tr:
        g=(tuple(map(int,s['left'])),tuple(map(int,s['right']))); v=int(s['value'])
        if not sk or sk[-1]!=g: sk.append(g); runs.append(1); scal.append([v])
        else: runs[-1]+=1; scal[-1].append(v)
    return tuple(sk),tuple(runs),tuple(tuple(x) for x in scal)
def encsk(sk): return [{'left':list(a),'right':list(b)} for a,b in sk]
def amb(sk,basis=None):
    return tuple((coord(a,basis),coord(b,basis)) if basis else (rr(a),rr(b)) for a,b in sk)
def ordered(xs,mode):
    xs=list(xs)
    if mode=='ORIGINAL': return xs
    if mode=='REVERSED': return list(reversed(xs))
    if mode=='SEEDED_SHUFFLE':
        seed=bytes.fromhex(SEED[2:].zfill(8))
        return sorted(xs,key=lambda x:hashlib.sha256(seed+cj(x)).digest())
    raise AssertionError('ENTRY_ORDER_MODE')
def paths(m,n):
    out=[]
    def rec(i,j,p):
        if (i,j)==(m-1,n-1): out.append(tuple(p)); return
        if i+1<m: p.append((i+1,j)); rec(i+1,j,p); p.pop()
        if j+1<n: p.append((i,j+1)); rec(i,j+1,p); p.pop()
    rec(0,0,[(0,0)]); return sorted(out)
def smap(runs): return tuple(i for i,n in enumerate(runs) for _ in range(int(n)))
def lift_count(lruns,rruns,q):
    lm,rm=smap(lruns),smap(rruns); allow=set(q); m,n=len(lm),len(rm); dp=[[0]*n for _ in range(m)]
    dp[0][0]=1
    for i in range(m):
        for j in range(n):
            if (i,j)==(0,0): continue
            if (lm[i],rm[j]) not in allow: continue
            dp[i][j]=(dp[i-1][j] if i else 0)+(dp[i][j-1] if j else 0)
    return dp[-1][-1]
def hv(m,n): return math.comb(int(m)+int(n)-2,int(m)-1)
def hist(es,sk):
    c=Counter()
    for e in es:
        got,r,_=seg(e['trajectory'])
        if got!=sk: raise AssertionError('SKELETON_DRIFT')
        c[r]+=1
    return c
def ench(c): return [{'run_lengths':list(r),'entry_count':int(c[r])} for r in sorted(c)]
def scalar_digest(es,sk):
    a=[]
    for e in es:
        got,r,s=seg(e['trajectory'])
        if got!=sk: raise AssertionError('SCALAR_SKELETON_DRIFT')
        a.append({'entry_digest':dg(e),'geometry_run_lengths':list(r),'scalar_segment_patterns':[list(x) for x in s]})
    return dg(sorted(a,key=cj))
def geometry_receipt(lsk,rsk,q):
    initial=inter(lsk[0][1],rsk[0][1]); jv=[]; sv=[]; projected=[]
    for i,j in q:
        l,r=lsk[i],rsk[j]; jl,jr=ssum(l[0],r[0]),ssum(l[1],r[1])
        jc=len(initial)-len(inter(ssum(l[0],l[1]),ssum(r[0],r[1])))
        lr=inter(jl,jr); pl,pr=inter(jl,PARENT_BOUNDARY),inter(jr,PARENT_BOUNDARY)
        sc=len(lr)-len(inter(lr,PARENT_BOUNDARY))
        if jc<0 or sc<0: raise AssertionError('NEGATIVE_CORRECTION')
        jv.append(jc); sv.append(sc); projected.append({'left':list(pl),'right':list(pr),'lambda_floor':jc+sc,'left_segment_index':i,'right_segment_index':j})
    normalized=[{'left':x['left'],'right':x['right'],'lambda_floor':x['lambda_floor']} for x in projected]
    return jv,sv,projected,dg({'join':jv,'shrink':sv,'projected':normalized})
def domain_receipt(cid,q,lh,rh):
    h=hashlib.sha256(); total=0; n=0
    for lr in sorted(lh):
        for rr0 in sorted(rh):
            c=lift_count(lr,rr0,q); w=int(lh[lr])*int(rh[rr0])*c
            rec={'left_run_lengths':list(lr),'left_entry_count':int(lh[lr]),'right_run_lengths':list(rr0),'right_entry_count':int(rh[rr0]),'fine_lifts_to_domain':c,'weighted_fine_lifts':w}
            h.update(cj(rec)+b'\n'); total+=w; n+=1
    x={'method':'RUN_PROFILE_DP_QUOTIENT_PATH_V1','domain_scope':'FINE_REFINEMENT_KEYS=(left_entry,right_entry,ordinary_hv_fine_path)','source_class_id':cid,'quotient_path':[list(z) for z in q],'left_run_profile_histogram_digest':dg(ench(lh)),'right_run_profile_histogram_digest':dg(ench(rh)),'contribution_record_count':n,'contribution_stream_sha256':h.hexdigest(),'fine_lift_multiplicity':total}
    x['fine_lift_domain_digest']=dg(x); return x

def build(spec_path,n8_path,l5_path,out_path,mode):
    spec=base.load(spec_path); base.check_spec(spec)
    base.load_n8(n8_path)
    raw=base.load(n8_path); left=ordered(raw['proof_payload']['reachable_closure']['entries'],mode); right=ordered(base.load_l5(l5_path),mode)
    retained=raw['proof_payload']['preorder_hardening']['retained_generators']
    byret={x['class_id']:x for x in retained}
    if len(byret)!=SOURCE_CLASSES: raise AssertionError('SOURCE_CLASS_COUNT')
    by=defaultdict(list)
    for e in left: by[e['source_class_id']].append(e)
    if set(by)!=set(byret): raise AssertionError('SOURCE_CLASS_COVERAGE')
    rskset={seg(e['trajectory'])[0] for e in right}
    if len(rskset)!=1: raise AssertionError('LEAF_SKELETON')
    rskc=next(iter(rskset)); rsk=amb(rskc,RIGHT_BASIS); rh=hist(right,rskc); rscalar=scalar_digest(right,rskc)
    leaf={'skeleton_length':len(rsk),'skeleton_coordinate':encsk(rskc),'skeleton_ambient':encsk(rsk),'skeleton_ambient_digest':dg(encsk(rsk)),'entry_count':len(right),'geometry_run_profile_histogram':ench(rh),'geometry_run_profile_histogram_digest':dg(ench(rh)),'scalar_segment_profile_catalog_digest':rscalar}
    sources=[]; data={}
    for cid in sorted(byret):
        sk0,_,_=seg(byret[cid]['generator']); lh=hist(by[cid],sk0); sk=amb(sk0)
        rec={'source_class_id':cid,'retained_generator_digest':byret[cid]['generator_digest'],'skeleton_length':len(sk),'skeleton_ambient':encsk(sk),'skeleton_digest':dg(encsk(sk)),'entry_count':len(by[cid]),'geometry_run_profile_histogram':ench(lh),'geometry_run_profile_histogram_digest':dg(ench(lh)),'scalar_segment_profile_catalog_digest':scalar_digest(by[cid],sk0)}
        sources.append(rec); data[cid]=(rec,sk,lh)
    pairs=sum(x['entry_count']*len(right) for x in sources)
    if pairs!=PAIR_N: raise AssertionError('PAIR_COUNT')
    domains=[]; total=0; checks=0; corr=Counter()
    for cid in sorted(data):
        rec,lsk,lh=data[cid]; qs=paths(len(lsk),len(rsk)); source_exact=0
        for lr,lc in lh.items():
            for rr0,rc in rh.items():
                exact=hv(sum(lr),sum(rr0)); qsum=sum(lift_count(lr,rr0,q) for q in qs)
                if qsum!=exact: raise AssertionError('RUN_PROFILE_QUOTIENT_PARTITION')
                checks+=1; source_exact+=int(lc)*int(rc)*exact
        source_sum=0
        for qi,q in enumerate(qs):
            jv,sv,proj,csig=geometry_receipt(lsk,rsk,q); f=domain_receipt(cid,q,lh,rh); mult=f['fine_lift_multiplicity']; source_sum+=mult; total+=mult; corr[csig]+=1
            basis={'source_class_id':cid,'local_quotient_path_index':qi,'quotient_path':[list(z) for z in q],'source_skeleton_digest':rec['skeleton_digest'],'leaf_skeleton_digest':leaf['skeleton_ambient_digest']}
            domains.append({'domain_id':'CN9Q-'+dg(basis)[:20],'source_class_id':cid,'local_quotient_path_index':qi,'quotient_path':[list(z) for z in q],'ordinary_hv_steps':[[b[0]-a[0],b[1]-a[1]] for a,b in zip(q,q[1:])],'join_correction_vector':jv,'shrink_correction_vector':sv,'projected_geometry':proj,'correction_signature_digest':csig,'fine_lift_multiplicity':mult,'fine_lift_domain_digest':f['fine_lift_domain_digest'],'factorization_receipt':f,'child_pair_projection_count':rec['entry_count']*len(right),'scalar_segment_interface':{'status':'UNRESOLVED_FINE_SCALAR_STABILITY','left_scalar_segment_profile_catalog_digest':rec['scalar_segment_profile_catalog_digest'],'right_scalar_segment_profile_catalog_digest':rscalar,'quotient_cell_segment_pairs':[list(z) for z in q],'post_shrink_compactification_uniformity_proved':False,'width_outcome_uniformity_proved':False},'classification':'UNRESOLVED','success_witness':None,'failure_witness':None})
        if source_sum!=source_exact: raise AssertionError('SOURCE_CONSERVATION')
    domains.sort(key=lambda x:x['domain_id'])
    if len(domains)!=DOMAIN_N or len({x['domain_id'] for x in domains})!=DOMAIN_N or total!=REF_N: raise AssertionError('DOMAIN_CONSERVATION')
    lhist=Counter(len(e['trajectory']) for e in left); rhist=Counter(len(e['trajectory']) for e in right)
    analytic=sum(a*b*hv(m,n) for m,a in lhist.items() for n,b in rhist.items())
    if analytic!=REF_N: raise AssertionError('ANALYTIC_WORKLOAD')
    slh=Counter(x['skeleton_length'] for x in sources)
    if slh!=Counter({3:4,4:12,5:4}): raise AssertionError('SKELETON_HISTOGRAM')
    p={'candidate_phase':'QUOTIENT_SKELETON_STABILITY_ANALYSIS','candidate_status':'EXECUTABLE_DRAFT','admitted':False,
       'source':{'frozen_spec_file_sha256':base.fh(spec_path),'frozen_spec_schema':base.SPEC_SCHEMA,'parent_subject_commit':base.BASE,'previous_discovery_subject':PARENT,'node8_artifact_sha256':base.N8_SHA,'node8_semantic_digest':base.N8_SEM,'leaf5_artifact_sha256':base.L5_SHA,'leaf5_semantic_digest':base.L5_SEM},
       'geometry':{'ambient_dim':3,'left_boundary_ambient_rref':[4,1],'right_boundary_ambient_rref':[5],'common_boundary_ambient_rref':[4,1],'parent_boundary_ambient_rref':[1],'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]],'extension_preorder_diagonal_preserved':True},
       'factorization_basis':{'node8_retained_source_class_count':len(sources),'node8_source_skeleton_length_histogram':{str(k):slh[k] for k in sorted(slh)},'node8_source_classes':sources,'leaf5':leaf,'quotient_path_count':len(domains),'expected_class_count_from_spec_used':False,'historical_node9_counts_used':False},
       'quotient_domains':domains,
       'correction_diagnostics':{'distinct_correction_signature_count':len(corr),'distinct_correction_signature_count_is_oracle':False,'domains_with_nonzero_join_correction':sum(any(x['join_correction_vector']) for x in domains),'domains_with_nonzero_shrink_correction':sum(any(x['shrink_correction_vector']) for x in domains)},
       'conservation_ledger':{'left_entry_count':len(left),'right_entry_count':len(right),'child_pair_count':pairs,'ordinary_hv_refinement_count_analytic':analytic,'sum_fine_lift_multiplicities':total,'expected_ordinary_hv_refinements':REF_N,'fine_refinement_domain_count':len(domains),'fine_refinement_domain_partition_method':'UNIQUE_SEGMENT_QUOTIENT_OF_EACH_HV_FINE_PATH','fine_refinement_domains_pairwise_disjoint_under_quotient_map':True,'fine_refinement_domain_union_complete_by_per_profile_dp_partition':True,'run_profile_pair_partition_checks':checks,'omitted_fine_refinement_multiplicity':0,'duplicated_fine_refinement_multiplicity':0,'child_pair_projection_is_partition':False,'child_pair_projections_overlap_across_quotient_paths':True,'conservation_holds':True},
       'materialization':{'child_pair_records_materialized':0,'fine_hv_path_records_materialized':0,'quotient_domain_records_materialized':len(domains),'fine_lift_counts_computed_by_dynamic_programming':True},
       'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':SEED,'canonical_domain_order':True,'input_order_mode_not_serialized':True},
       'classification_boundary':{'all_domains_unresolved':True,'successful_domain_count':0,'failed_domain_count':0,'unresolved_domain_count':len(domains),'exact_join_correction_replayed_on_quotient_geometry':True,'exact_shrink_correction_replayed_on_quotient_geometry':True,'fine_scalar_interleaving_uniformity_proved':False,'post_shrink_compactification_uniformity_proved':False,'width_outcome_uniformity_proved':False,'direct_success_witnesses_complete':False,'explicit_failure_witnesses_complete':False},
       'strict_boundary':{'node9_frontier_spec_frozen':True,'node9_frontier_executable_draft':'QUOTIENT_SKELETON_STABILITY_ANALYSIS','node9_frontier_candidate_complete':False,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'formal_admission':'BLOCKED','next_gate':'CLOSED','root_reached':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'},
       'result':'HONEST_UNRESOLVED_80_QUOTIENT_HV_DOMAINS_AT_CORRECTED_NODE9_PARENT_FRONTIER'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':p,'semantic_digest':dg(p)}; base.save(art,out_path); return art

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--node8-artifact',type=Path,required=True); ap.add_argument('--leaf5-artifact',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); a=ap.parse_args()
    x=build(a.spec,a.node8_artifact,a.leaf5_artifact,a.output,a.order_mode); p=x['proof_payload']; c=p['conservation_ledger']
    print('JANUS_C049_1_B4_6_3_NODE9_QUOTIENT_SKELETON_STABILITY_ANALYSIS = PASS'); print('NODE8_SOURCE_CLASSES =',p['factorization_basis']['node8_retained_source_class_count']); print('QUOTIENT_HV_DOMAINS =',p['factorization_basis']['quotient_path_count']); print('SUM_FINE_LIFT_MULTIPLICITIES =',c['sum_fine_lift_multiplicities']); print('RUN_PROFILE_PAIR_PARTITION_CHECKS =',c['run_profile_pair_partition_checks']); print('CHILD_PAIR_PROJECTION_IS_PARTITION =',c['child_pair_projection_is_partition']); print('ALL_DOMAINS_UNRESOLVED =',p['classification_boundary']['all_domains_unresolved']); print('SEMANTIC_DIGEST =',x['semantic_digest']); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
