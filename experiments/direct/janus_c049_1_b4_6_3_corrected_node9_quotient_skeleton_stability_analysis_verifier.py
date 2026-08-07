#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, copy, hashlib, json, math, tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

SPEC_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-SPEC-v1'
ART_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
N8_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
L5_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-RIGHT-LEAF5-CANDIDATE-v1'
BASE='c354d56bf3ac0bb77136b96e869dc95a6b9ba07f'
LAYER_SUBJECT='1ee3e6ed7e70ee2031fdf1b9c35907f6df22bda8'
N8_SHA='80b74b500ae82639e51568a9a6dc70a72668f32991add42bc5ffac05b3f9537f'
N8_SEM='e0017e4e5de933e520c6ea374ef291c07bbbb373478c6f9952911cc376380622'
N8_ENT='c6beadf320cf886765d5c8a804887cbf14d854b8f96fc6997058fd0cf0afe480'
N8_STREAM='c109730b8f3608d59059ff07a2235d42510be5cbcb5bac991eeb51a7991c7400'
L5_SHA='6e4bbd67747405846b63a87633e34d41b0f720d33a6f55e877717b5463c01882'
L5_SEM='d5dcbaf64366a93420691fd667776f0f577bb0afd0feb588421139c69eb42d65'
L5_ENT='22dae6cd5455319b8139c3bf59970c978c885323ccd1ad49290c305939d2e437'
L5_STREAM='d4025b99e32c187e7d4bd61404df715fa86990e3fb351aac8e7fb9b9622f94a4'
LEFT_N,RIGHT_N,PAIR_N,REF_N=8676,36,312336,98319408
SOURCE_N,DOMAIN_N=20,80
AMBIENT=3; RIGHT_BASIS=(5,); PARENT=(1,); TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

class VError(AssertionError): pass
def fail(code): raise VError(code)
def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def rr(rows:Iterable[int],d=AMBIENT):
    vals=[]
    for raw in rows:
        x=int(raw)
        if not 0<=x<(1<<d): fail('GEOMETRY_CORRECTION')
        if x and x not in vals: vals.append(x)
    vals.sort(reverse=True); t=0
    for col in range(d-1,-1,-1):
        s=next((i for i in range(t,len(vals)) if (vals[i]>>col)&1),None)
        if s is None: continue
        vals[t],vals[s]=vals[s],vals[t]; p=vals[t]
        for i in range(len(vals)):
            if i!=t and ((vals[i]>>col)&1): vals[i]^=p
        t+=1
    out=[x for x in vals if x]; out.sort(key=lambda x:x.bit_length(),reverse=True); return tuple(out)
def span(rows):
    o={0}
    for r in rows: o|={x^int(r) for x in tuple(o)}
    return o
def add(a,b): return rr((*a,*b))
def meet(a,b): return rr(sorted(span(a)&span(b)))
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
def amb(sk,basis=None): return tuple((coord(a,basis),coord(b,basis)) if basis else (rr(a),rr(b)) for a,b in sk)
def paths(m,n):
    o=[]
    def rec(i,j,p):
        if (i,j)==(m-1,n-1): o.append(tuple(p)); return
        if i+1<m: p.append((i+1,j)); rec(i+1,j,p); p.pop()
        if j+1<n: p.append((i,j+1)); rec(i,j+1,p); p.pop()
    rec(0,0,[(0,0)]); return sorted(o)
def smap(runs): return tuple(i for i,n in enumerate(runs) for _ in range(int(n)))
def qcount(lruns,rruns,q):
    lm,rm=smap(lruns),smap(rruns); allowed=set(q); a=[[0]*len(rm) for _ in lm]; a[0][0]=1
    for i in range(len(lm)):
        for j in range(len(rm)):
            if i==j==0: continue
            if (lm[i],rm[j]) not in allowed: continue
            a[i][j]=(a[i-1][j] if i else 0)+(a[i][j-1] if j else 0)
    return a[-1][-1]
def hv(m,n): return math.comb(m+n-2,m-1)
def ench(c): return [{'run_lengths':list(r),'entry_count':int(c[r])} for r in sorted(c)]
def hist(es,sk):
    c=Counter()
    for e in es:
        got,r,_=seg(e['trajectory'])
        if got!=sk: fail('CLASS_SOURCE_KEYS')
        c[r]+=1
    return c
def scalar_digest(es,sk):
    rows=[]
    for e in es:
        got,r,s=seg(e['trajectory'])
        if got!=sk: fail('CLASS_SOURCE_KEYS')
        rows.append({'entry_digest':dg(e),'geometry_run_lengths':list(r),'scalar_segment_patterns':[list(x) for x in s]})
    return dg(sorted(rows,key=cj))
def geom(lsk,rsk,q):
    initial=meet(lsk[0][1],rsk[0][1]); jv=[]; sv=[]; proj=[]
    for i,j in q:
        l,r=lsk[i],rsk[j]; jl,jr=add(l[0],r[0]),add(l[1],r[1])
        jc=len(initial)-len(meet(add(l[0],l[1]),add(r[0],r[1])))
        lr=meet(jl,jr); pl,pr=meet(jl,PARENT),meet(jr,PARENT); sc=len(lr)-len(meet(lr,PARENT))
        if jc<0 or sc<0: fail('GEOMETRY_CORRECTION')
        jv.append(jc); sv.append(sc); proj.append({'left':list(pl),'right':list(pr),'lambda_floor':jc+sc,'left_segment_index':i,'right_segment_index':j})
    norm=[{'left':x['left'],'right':x['right'],'lambda_floor':x['lambda_floor']} for x in proj]
    return jv,sv,proj,dg({'join':jv,'shrink':sv,'projected':norm})
def freceipt(cid,q,lh,rh):
    h=hashlib.sha256(); total=0; n=0
    for lr in sorted(lh):
        for rr0 in sorted(rh):
            c=qcount(lr,rr0,q); w=int(lh[lr])*int(rh[rr0])*c
            row={'left_run_lengths':list(lr),'left_entry_count':int(lh[lr]),'right_run_lengths':list(rr0),'right_entry_count':int(rh[rr0]),'fine_lifts_to_domain':c,'weighted_fine_lifts':w}
            h.update(cj(row)+b'\n'); total+=w; n+=1
    x={'method':'RUN_PROFILE_DP_QUOTIENT_PATH_V1','domain_scope':'FINE_REFINEMENT_KEYS=(left_entry,right_entry,ordinary_hv_fine_path)','source_class_id':cid,'quotient_path':[list(z) for z in q],'left_run_profile_histogram_digest':dg(ench(lh)),'right_run_profile_histogram_digest':dg(ench(rh)),'contribution_record_count':n,'contribution_stream_sha256':h.hexdigest(),'fine_lift_multiplicity':total}
    x['fine_lift_domain_digest']=dg(x); return x

def check_spec(s):
    if s.get('schema')!=SPEC_SCHEMA or s.get('baseline',{}).get('parent_subject_commit')!=BASE: fail('PARENT_SUBJECT_BINDING')
    w=s.get('exact_workload',{})
    if (w.get('child_pairs'),w.get('ordinary_hv_refinements'),w.get('fine_workload_materialized'))!=(PAIR_N,REF_N,False): fail('ANALYTIC_WORKLOAD')
    g=s.get('geometry',{})
    req={'left_boundary_ambient_rref':[4,1],'right_boundary_ambient_rref':[5],'common_boundary_ambient_rref':[4,1],'parent_boundary_ambient_rref':[1],'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]],'extension_preorder_diagonal_preserved':True}
    if any(g.get(k)!=v for k,v in req.items()): fail('ILLEGAL_DIAGONAL_JOIN')

def source_data(n8_path,l5_path):
    if fh(n8_path)!=N8_SHA: fail('SOURCE_NODE8_BINDING')
    n8=load(n8_path)
    if n8.get('schema')!=N8_SCHEMA or n8.get('semantic_digest')!=N8_SEM or n8.get('semantic_digest')!=dg(n8['proof_payload']): fail('SOURCE_NODE8_BINDING')
    cl=n8['proof_payload']['reachable_closure']; left=cl['entries']
    if len(left)!=LEFT_N or dg(left)!=N8_ENT or cl.get('reachable_entries_digest')!=N8_ENT or cl.get('reachable_stream_sha256')!=N8_STREAM: fail('SOURCE_NODE8_BINDING')
    ret=n8['proof_payload']['preorder_hardening']['retained_generators']; byret={x['class_id']:x for x in ret}
    if len(byret)!=SOURCE_N: fail('SOURCE_NODE8_BINDING')
    if fh(l5_path)!=L5_SHA: fail('RIGHT_LEAF5_BINDING')
    l5=load(l5_path)
    if l5.get('schema')!=L5_SCHEMA or l5.get('semantic_digest')!=L5_SEM or l5.get('semantic_digest')!=dg(l5['leaf_payload']): fail('RIGHT_LEAF5_BINDING')
    lp=l5['leaf_payload']; right=lp['entries']
    if (lp.get('factor_index_zero_based'),lp.get('leaf_ordinal_one_based'),lp.get('block_ambient_rref'),len(right))!=(4,5,[5],RIGHT_N): fail('RIGHT_LEAF5_BINDING')
    if dg(right)!=L5_ENT or lp.get('entries_digest')!=L5_ENT or lp.get('trajectory_stream_sha256')!=L5_STREAM: fail('RIGHT_LEAF5_BINDING')
    return left,right,byret

def expected_model(left,right,byret):
    by=defaultdict(list)
    for e in left:
        if e.get('source_class_id') not in byret: fail('CLASS_SOURCE_KEYS')
        by[e['source_class_id']].append(e)
    if set(by)!=set(byret): fail('CLASS_SOURCE_KEYS')
    rset={seg(e['trajectory'])[0] for e in right}
    if len(rset)!=1: fail('RIGHT_LEAF5_BINDING')
    rsk0=next(iter(rset)); rsk=amb(rsk0,RIGHT_BASIS); rh=hist(right,rsk0); rsd=scalar_digest(right,rsk0)
    leaf={'skeleton_length':2,'skeleton_coordinate':encsk(rsk0),'skeleton_ambient':encsk(rsk),'skeleton_ambient_digest':dg(encsk(rsk)),'entry_count':RIGHT_N,'geometry_run_profile_histogram':ench(rh),'geometry_run_profile_histogram_digest':dg(ench(rh)),'scalar_segment_profile_catalog_digest':rsd}
    src=[]; dat={}; slh=Counter()
    for cid in sorted(byret):
        sk0,_,_=seg(byret[cid]['generator']); lh=hist(by[cid],sk0); sk=amb(sk0); slh[len(sk)]+=1
        rec={'source_class_id':cid,'retained_generator_digest':byret[cid]['generator_digest'],'skeleton_length':len(sk),'skeleton_ambient':encsk(sk),'skeleton_digest':dg(encsk(sk)),'entry_count':len(by[cid]),'geometry_run_profile_histogram':ench(lh),'geometry_run_profile_histogram_digest':dg(ench(lh)),'scalar_segment_profile_catalog_digest':scalar_digest(by[cid],sk0)}
        src.append(rec); dat[cid]=(rec,sk,lh)
    if slh!=Counter({3:4,4:12,5:4}): fail('CLASS_SOURCE_KEYS')
    domains=[]; total=0; checks=0; corr=Counter()
    for cid in sorted(dat):
        rec,lsk,lh=dat[cid]; qs=paths(len(lsk),2); source_total=0; source_exact=0
        for lr,lc in lh.items():
            for rr0,rc in rh.items():
                exact=hv(sum(lr),sum(rr0)); qsum=sum(qcount(lr,rr0,q) for q in qs)
                if qsum!=exact: fail('PARTITION_COVERAGE')
                checks+=1; source_exact+=int(lc)*int(rc)*exact
        for qi,q in enumerate(qs):
            jv,sv,proj,csig=geom(lsk,rsk,q); f=freceipt(cid,q,lh,rh); mult=f['fine_lift_multiplicity']; source_total+=mult; total+=mult; corr[csig]+=1
            basis={'source_class_id':cid,'local_quotient_path_index':qi,'quotient_path':[list(z) for z in q],'source_skeleton_digest':rec['skeleton_digest'],'leaf_skeleton_digest':leaf['skeleton_ambient_digest']}
            domains.append({'domain_id':'CN9Q-'+dg(basis)[:20],'source_class_id':cid,'local_quotient_path_index':qi,'quotient_path':[list(z) for z in q],'ordinary_hv_steps':[[b[0]-a[0],b[1]-a[1]] for a,b in zip(q,q[1:])],'join_correction_vector':jv,'shrink_correction_vector':sv,'projected_geometry':proj,'correction_signature_digest':csig,'fine_lift_multiplicity':mult,'fine_lift_domain_digest':f['fine_lift_domain_digest'],'factorization_receipt':f,'child_pair_projection_count':rec['entry_count']*RIGHT_N,'scalar_segment_interface':{'status':'UNRESOLVED_FINE_SCALAR_STABILITY','left_scalar_segment_profile_catalog_digest':rec['scalar_segment_profile_catalog_digest'],'right_scalar_segment_profile_catalog_digest':rsd,'quotient_cell_segment_pairs':[list(z) for z in q],'post_shrink_compactification_uniformity_proved':False,'width_outcome_uniformity_proved':False},'classification':'UNRESOLVED','success_witness':None,'failure_witness':None})
        if source_total!=source_exact: fail('PARTITION_COVERAGE')
    domains.sort(key=lambda x:x['domain_id'])
    if len(domains)!=DOMAIN_N or total!=REF_N: fail('PARTITION_COVERAGE')
    return src,leaf,domains,total,checks,corr

def static_check(path):
    text=Path(path).read_text(encoding='utf-8'); ast.parse(text)
    if 'itertools.product' in text or 'fine_hv_paths_materialized' in text: fail('MATERIALIZATION_POLICY')
    if "paths(len(lsk),len(rsk))" not in text or 'lift_count' not in text: fail('MATERIALIZATION_POLICY')
    return True

def verify(spec_path,n8_path,l5_path,artifact_path,producer_path=None,peer_paths=()):
    spec=load(spec_path); check_spec(spec); left,right,byret=source_data(n8_path,l5_path)
    art=load(artifact_path)
    if art.get('schema')!=ART_SCHEMA or art.get('semantic_digest_scope')!='proof_payload' or art.get('semantic_digest')!=dg(art.get('proof_payload')): fail('ARTIFACT_SEMANTIC')
    p=art['proof_payload']
    if p.get('candidate_phase')!='QUOTIENT_SKELETON_STABILITY_ANALYSIS' or p.get('candidate_status')!='EXECUTABLE_DRAFT' or p.get('admitted') is not False: fail('FALSE_ADMISSION_OR_ROOT_CLAIM')
    if p.get('source',{}).get('parent_subject_commit')!=BASE: fail('PARENT_SUBJECT_BINDING')
    if p.get('source',{}).get('node8_artifact_sha256')!=N8_SHA or p.get('source',{}).get('node8_semantic_digest')!=N8_SEM: fail('SOURCE_NODE8_BINDING')
    if p.get('source',{}).get('leaf5_artifact_sha256')!=L5_SHA or p.get('source',{}).get('leaf5_semantic_digest')!=L5_SEM: fail('RIGHT_LEAF5_BINDING')
    g=p.get('geometry',{})
    if g.get('ordinary_join_steps')!=[[1,0],[0,1]] or g.get('ordinary_join_diagonal_allowed') is not False: fail('ILLEGAL_DIAGONAL_JOIN')
    src,leaf,expected,total,checks,corr=expected_model(left,right,byret)
    fb=p.get('factorization_basis',{})
    if fb.get('node8_source_classes')!=src or fb.get('leaf5')!=leaf or fb.get('quotient_path_count')!=DOMAIN_N: fail('CLASS_SOURCE_KEYS')
    obs=p.get('quotient_domains')
    if not isinstance(obs,list) or len(obs)!=DOMAIN_N: fail('PARTITION_COVERAGE')
    if obs!=sorted(obs,key=lambda x:x.get('domain_id','')): fail('CANONICAL_ORDER')
    for o,e in zip(obs,expected):
        if o.get('classification')=='SUCCESS' or o.get('success_witness') is not None: fail('DIRECT_SUCCESS_WITNESS')
        if o.get('classification')=='FAILED' or o.get('failure_witness') is not None: fail('FAILURE_WITNESS')
        for k in ('join_correction_vector','shrink_correction_vector','projected_geometry','correction_signature_digest'):
            if o.get(k)!=e.get(k): fail('GEOMETRY_CORRECTION')
        for k in ('domain_id','source_class_id','local_quotient_path_index','quotient_path','ordinary_hv_steps','fine_lift_multiplicity','fine_lift_domain_digest','factorization_receipt','child_pair_projection_count','scalar_segment_interface'):
            if o.get(k)!=e.get(k): fail('CLASS_SOURCE_KEYS')
    c=p.get('conservation_ledger',{})
    if (c.get('child_pair_count'),c.get('ordinary_hv_refinement_count_analytic'),c.get('sum_fine_lift_multiplicities'))!=(PAIR_N,REF_N,REF_N): fail('ANALYTIC_WORKLOAD')
    if c.get('run_profile_pair_partition_checks')!=checks or c.get('fine_refinement_domain_count')!=DOMAIN_N or c.get('omitted_fine_refinement_multiplicity')!=0 or c.get('duplicated_fine_refinement_multiplicity')!=0 or c.get('conservation_holds') is not True: fail('PARTITION_COVERAGE')
    if c.get('child_pair_projection_is_partition') is not False or c.get('child_pair_projections_overlap_across_quotient_paths') is not True: fail('PARTITION_COVERAGE')
    if c.get('fine_refinement_domains_pairwise_disjoint_under_quotient_map') is not True or c.get('fine_refinement_domain_union_complete_by_per_profile_dp_partition') is not True: fail('PARTITION_COVERAGE')
    m=p.get('materialization',{})
    if m.get('child_pair_records_materialized')!=0 or m.get('fine_hv_path_records_materialized')!=0 or m.get('quotient_domain_records_materialized')!=DOMAIN_N: fail('MATERIALIZATION_POLICY')
    cb=p.get('classification_boundary',{})
    if cb.get('all_domains_unresolved') is not True or (cb.get('successful_domain_count'),cb.get('failed_domain_count'),cb.get('unresolved_domain_count'))!=(0,0,DOMAIN_N): fail('DIRECT_SUCCESS_WITNESS')
    if cb.get('fine_scalar_interleaving_uniformity_proved') is not False or cb.get('post_shrink_compactification_uniformity_proved') is not False or cb.get('width_outcome_uniformity_proved') is not False: fail('DIRECT_SUCCESS_WITNESS')
    b=p.get('strict_boundary',{})
    required={'node9_frontier_candidate_complete':False,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'formal_admission':'BLOCKED','next_gate':'CLOSED','root_reached':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'}
    if any(b.get(k)!=v for k,v in required.items()): fail('FALSE_ADMISSION_OR_ROOT_CLAIM')
    if producer_path is not None: static_check(producer_path)
    raw=Path(artifact_path).read_bytes()
    for peer in peer_paths:
        if Path(peer).read_bytes()!=raw: fail('CANONICAL_ORDER')
    inv={f'CN9Q-INV-{i:02d}':'PASS' for i in range(1,13)}
    return {'invariant_vector':inv,'domain_count':DOMAIN_N,'fine_refinements':total,'run_profile_partition_checks':checks,'distinct_correction_signatures_diagnostic':len(corr)}

def repaired(art):
    art['semantic_digest']=dg(art['proof_payload']); return art

def tamper_suite(spec,n8,l5,artifact,producer):
    base_art=load(artifact); out=[]
    def run_art(tid,code,mut):
        a=copy.deepcopy(base_art); mut(a['proof_payload']); repaired(a)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.json'; p.write_bytes(cj(a)+b'\n')
            try: verify(spec,n8,l5,p,producer,())
            except VError as e:
                if str(e)!=code: raise AssertionError(f'{tid}: expected {code}, got {e}')
                out.append((tid,code)); return
            raise AssertionError(tid+' accepted')
    run_art('T01_PARENT_SUBJECT_BINDING','PARENT_SUBJECT_BINDING',lambda p:p['source'].__setitem__('parent_subject_commit','0'*40))
    with tempfile.TemporaryDirectory() as td:
        x=load(n8); x['proof_payload']['reachable_closure']['entries'][0]['trajectory'][0]['value']^=1
        cl=x['proof_payload']['reachable_closure']; cl['reachable_entries_digest']=dg(cl['entries']); x['semantic_digest']=dg(x['proof_payload'])
        q=Path(td)/'n8.json'; q.write_bytes(cj(x)+b'\n')
        try: verify(spec,q,l5,artifact,producer,())
        except VError as e:
            if str(e)!='SOURCE_NODE8_BINDING': raise
            out.append(('T02_SOURCE_NODE8_BINDING',str(e)))
        else: raise AssertionError('T02 accepted')
    with tempfile.TemporaryDirectory() as td:
        x=load(l5); x['leaf_payload']['factor_index_zero_based']=3; x['semantic_digest']=dg(x['leaf_payload'])
        q=Path(td)/'l5.json'; q.write_bytes(cj(x)+b'\n')
        try: verify(spec,n8,q,artifact,producer,())
        except VError as e:
            if str(e)!='RIGHT_LEAF5_BINDING': raise
            out.append(('T03_RIGHT_LEAF5_BINDING',str(e)))
        else: raise AssertionError('T03 accepted')
    run_art('T04_ILLEGAL_DIAGONAL_JOIN','ILLEGAL_DIAGONAL_JOIN',lambda p:p['geometry'].__setitem__('ordinary_join_steps',[[1,0],[0,1],[1,1]]))
    run_art('T05_ANALYTIC_WORKLOAD','ANALYTIC_WORKLOAD',lambda p:p['conservation_ledger'].__setitem__('sum_fine_lift_multiplicities',REF_N-1))
    run_art('T06_PARTITION_COVERAGE','PARTITION_COVERAGE',lambda p:p['quotient_domains'].pop())
    run_art('T07_CLASS_SOURCE_KEYS','CLASS_SOURCE_KEYS',lambda p:p['quotient_domains'][0].__setitem__('source_class_id','CN8-SXX'))
    run_art('T08_GEOMETRY_CORRECTION','GEOMETRY_CORRECTION',lambda p:p['quotient_domains'][0]['join_correction_vector'].__setitem__(0,1-p['quotient_domains'][0]['join_correction_vector'][0]))
    def t9(p): p['quotient_domains'][0]['classification']='SUCCESS'; p['quotient_domains'][0]['success_witness']={'fake':True}
    run_art('T09_FAKE_SUCCESS_WITNESS','DIRECT_SUCCESS_WITNESS',t9)
    def t10(p): p['quotient_domains'][0]['classification']='FAILED'; p['quotient_domains'][0]['failure_witness']={'fake':True}
    run_art('T10_FAILURE_WITNESS','FAILURE_WITNESS',t10)
    run_art('T11_CANONICAL_ORDER','CANONICAL_ORDER',lambda p:p['quotient_domains'].reverse())
    run_art('T12_FALSE_ADMISSION_OR_ROOT','FALSE_ADMISSION_OR_ROOT_CLAIM',lambda p:p['strict_boundary'].__setitem__('formal_admission','ADMITTED'))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--node8-artifact',type=Path,required=True); ap.add_argument('--leaf5-artifact',type=Path,required=True); ap.add_argument('--artifact',type=Path,required=True); ap.add_argument('--producer-source',type=Path); ap.add_argument('--peer-artifact',type=Path,action='append',default=[]); ap.add_argument('--tamper',action='store_true'); a=ap.parse_args()
    r=verify(a.spec,a.node8_artifact,a.leaf5_artifact,a.artifact,a.producer_source,a.peer_artifact)
    print('JANUS_NODE9_Q80_INDEPENDENT_VERIFIER = PASS'); print('INVARIANTS = 12/12'); print('QUOTIENT_DOMAINS =',r['domain_count']); print('FINE_REFINEMENTS =',r['fine_refinements']); print('RUN_PROFILE_PAIR_PARTITION_CHECKS =',r['run_profile_partition_checks']); print('DISTINCT_CORRECTION_SIGNATURES_DIAGNOSTIC =',r['distinct_correction_signatures_diagnostic'])
    if a.tamper:
        t=tamper_suite(a.spec,a.node8_artifact,a.leaf5_artifact,a.artifact,a.producer_source)
        print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(t)}/12')
    print('NODE9_FRONTIER_CANDIDATE_COMPLETE = FALSE'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
