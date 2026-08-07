#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, math
from collections import Counter
from pathlib import Path

SPEC_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-SPEC-v1'
ART_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-CANDIDATE-v1'
N8_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
L5_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-RIGHT-LEAF5-CANDIDATE-v1'
BASE='c354d56bf3ac0bb77136b96e869dc95a6b9ba07f'
N8_SHA='80b74b500ae82639e51568a9a6dc70a72668f32991add42bc5ffac05b3f9537f'
N8_SEM='e0017e4e5de933e520c6ea374ef291c07bbbb373478c6f9952911cc376380622'
N8_ENT='c6beadf320cf886765d5c8a804887cbf14d854b8f96fc6997058fd0cf0afe480'
N8_STREAM='c109730b8f3608d59059ff07a2235d42510be5cbcb5bac991eeb51a7991c7400'
N8_CENT='464093b979c947f64de3598172b0d276e8b546151660e5f2ac228aff371c74ee'
N8_CSTREAM='856abcc9dbc1f37b0dfb210ed669c98b775dce560ce6012560a6027a633d0000'
L5_SHA='6e4bbd67747405846b63a87633e34d41b0f720d33a6f55e877717b5463c01882'
L5_SEM='d5dcbaf64366a93420691fd667776f0f577bb0afd0feb588421139c69eb42d65'
L5_ENT='22dae6cd5455319b8139c3bf59970c978c885323ccd1ad49290c305939d2e437'
L5_STREAM='d4025b99e32c187e7d4bd61404df715fa86990e3fb351aac8e7fb9b9622f94a4'
LEFT_N,RIGHT_N,PAIR_N,REF_N=8676,36,312336,98319408
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'; SEED='0xC049119'

def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(x,p): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_bytes(cj(x)+b'\n')

def rr(rows,d):
    piv=[]
    for raw in rows:
        x=int(raw)
        if not 0<=x<(1<<d): raise AssertionError('VECTOR_RANGE')
        for q in piv: x=min(x,x^q)
        if x:
            b=x.bit_length()-1
            piv=[q^x if (q>>b)&1 else q for q in piv]+[x]; piv.sort(reverse=True)
    return tuple(piv)

def vcoord(v,basis):
    t=len(basis)
    for c in range(1<<t):
        z=0
        for i,q in enumerate(basis):
            if c&(1<<(t-1-i)): z^=int(q)
        if z==int(v): return c
    raise AssertionError('COORDINATE_OUTSIDE_BOUNDARY')

def subcoord(rows,basis): return list(rr((vcoord(v,basis) for v in rows),len(basis)))
def trcoord(tr,basis): return [{'left':subcoord(s['left'],basis),'right':subcoord(s['right'],basis),'value':int(s['value'])} for s in tr]

def stream(entries):
    h=hashlib.sha256()
    for e in entries: h.update(cj(e['trajectory'])+b'\n')
    return h.hexdigest()

def typical(vals):
    a=[int(v) for v in vals]
    while True:
        hit=False
        for i in range(1,len(a)):
            if a[i-1]==a[i]: del a[i]; hit=True; break
        if hit: continue
        for i in range(len(a)):
            for j in range(i+2,len(a)):
                z=a[i:j+1]
                inc=z[0]<=z[-1] and all(z[0]<=q<=z[-1] for q in z[1:-1])
                dec=z[0]>=z[-1] and all(z[0]>=q>=z[-1] for q in z[1:-1])
                if inc or dec: del a[i+1:j]; hit=True; break
            if hit: break
        if not hit: return tuple(a)

def skeleton(tr):
    out=[]
    for s in tr:
        x=(tuple(int(v) for v in s['left']),tuple(int(v) for v in s['right']))
        if not out or out[-1]!=x: out.append(x)
    return tuple(out)

def run_profile(vals):
    out=[]
    for raw in vals:
        v=int(raw)
        if out and out[-1][0]==v: out[-1][1]+=1
        else: out.append([v,1])
    return out

def signature(tr):
    return {'geometric_skeleton':[{'left':list(a),'right':list(b)} for a,b in skeleton(tr)],
            'scalar_typical_pattern':list(typical([s['value'] for s in tr]))}

def order(entries,mode):
    a=list(entries)
    if mode=='ORIGINAL': return a
    if mode=='REVERSED': return list(reversed(a))
    if mode=='SEEDED_SHUFFLE':
        seed=bytes.fromhex(SEED[2:].zfill(8))
        return sorted(a,key=lambda x:hashlib.sha256(seed+cj(x)).digest())
    raise ValueError(mode)

def lenhist(entries): return {str(k):v for k,v in sorted(Counter(len(e['trajectory']) for e in entries).items())}
def runhist(entries):
    c=Counter(cj(run_profile([s['value'] for s in e['trajectory']])).decode() for e in entries)
    return [{'profile':json.loads(k),'count':v} for k,v in sorted(c.items())]
def domain_digest(entries): return dg(sorted(dg(e) for e in entries))
def hv(lh,rh): return sum(int(a)*int(b)*math.comb(int(m)+int(n)-2,int(m)-1) for m,a in lh.items() for n,b in rh.items())

def check_spec(s):
    if s.get('schema')!=SPEC_SCHEMA: raise AssertionError('SPEC_SCHEMA')
    if s.get('baseline',{}).get('parent_subject_commit')!=BASE: raise AssertionError('PARENT_SUBJECT_BINDING')
    w=s.get('exact_workload',{})
    if (w.get('child_pairs'),w.get('ordinary_hv_refinements'),w.get('fine_workload_materialized'))!=(PAIR_N,REF_N,False): raise AssertionError('SPEC_WORKLOAD')
    g=s.get('geometry',{})
    req={'left_boundary_ambient_rref':[4,1],'right_boundary_ambient_rref':[5],'common_boundary_ambient_rref':[4,1],'parent_boundary_ambient_rref':[1],'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]],'extension_preorder_diagonal_preserved':True}
    if any(g.get(k)!=v for k,v in req.items()): raise AssertionError('SPEC_GEOMETRY')
    m=s.get('materialization_policy',{})
    if m.get('full_child_cartesian_materialization_forbidden') is not True or m.get('fine_hv_path_enumeration_forbidden') is not True: raise AssertionError('SPEC_MATERIALIZATION')
    o=s.get('objective',{})
    if any(o.get(k) is not None for k in ('expected_class_count','expected_successful_class_count','expected_failed_class_count')): raise AssertionError('EXPECTED_CLASS_LEAK')

def load_n8(path):
    if fh(path)!=N8_SHA: raise AssertionError('SOURCE_NODE8_SHA')
    a=load(path)
    if a.get('schema')!=N8_SCHEMA or a.get('semantic_digest')!=N8_SEM or a.get('semantic_digest')!=dg(a['proof_payload']): raise AssertionError('SOURCE_NODE8_SEMANTIC')
    c=a['proof_payload']['reachable_closure']; raw=c['entries']
    if len(raw)!=LEFT_N or dg(raw)!=N8_ENT or c.get('reachable_entries_digest')!=N8_ENT or c.get('reachable_stream_sha256')!=N8_STREAM: raise AssertionError('SOURCE_NODE8_RECEIPT')
    out=[]
    for e in raw:
        z=copy.deepcopy(e); z['trajectory']=trcoord(e['trajectory'],(4,1)); out.append(z)
    out.sort(key=cj)
    if dg(out)!=N8_CENT or stream(out)!=N8_CSTREAM: raise AssertionError('SOURCE_NODE8_COORDINATES')
    return out

def load_l5(path):
    if fh(path)!=L5_SHA: raise AssertionError('RIGHT_LEAF5_SHA')
    a=load(path)
    if a.get('schema')!=L5_SCHEMA or a.get('semantic_digest')!=L5_SEM or a.get('semantic_digest')!=dg(a['leaf_payload']): raise AssertionError('RIGHT_LEAF5_SEMANTIC')
    p=a['leaf_payload']; e=p['entries']
    if (p.get('factor_index_zero_based'),p.get('leaf_ordinal_one_based'),p.get('block_ambient_rref'),len(e))!=(4,5,[5],RIGHT_N): raise AssertionError('RIGHT_LEAF5_BINDING')
    if dg(e)!=L5_ENT or p.get('entries_digest')!=L5_ENT or p.get('trajectory_stream_sha256')!=L5_STREAM: raise AssertionError('RIGHT_LEAF5_RECEIPT')
    return e

def groups(entries,mode):
    d={}
    for e in order(entries,mode):
        sig=signature(e['trajectory']); key=dg(sig)
        b=d.setdefault(key,{'signature':sig,'members':[]})
        if b['signature']!=sig: raise AssertionError('SIGNATURE_DIGEST_COLLISION')
        b['members'].append(e)
    out=[]
    for key,b in d.items():
        m=b['members']
        out.append({'signature_digest':key,'signature':b['signature'],'member_count':len(m),'member_domain_digest':domain_digest(m),'trajectory_length_histogram':lenhist(m),'scalar_run_profile_histogram':runhist(m),'representative_entry_digest':min(dg(x) for x in m)})
    return sorted(out,key=lambda x:(x['signature_digest'],cj(x['signature'])))

def build(spec_path,n8_path,l5_path,out_path,mode):
    spec=load(spec_path); check_spec(spec)
    lg=groups(load_n8(n8_path),mode); rg=groups(load_l5(l5_path),mode)
    classes=[]; ids=set()
    for l in lg:
        for r in rg:
            dom={'left_group_digest':l['signature_digest'],'left_member_domain_digest':l['member_domain_digest'],'right_group_digest':r['signature_digest'],'right_member_domain_digest':r['member_domain_digest']}
            dd=dg(dom); cid='CN9F-DISC-'+dd[:16]
            if cid in ids: raise AssertionError('CLASS_ID_COLLISION')
            ids.add(cid)
            classes.append({'class_id':cid,'source_domain_digest':dd,'source_domain':dom,'left_structural_signature_digest':l['signature_digest'],'right_structural_signature_digest':r['signature_digest'],'child_pair_multiplicity':l['member_count']*r['member_count'],'refinement_multiplicity':hv(l['trajectory_length_histogram'],r['trajectory_length_histogram']),'classification':'UNRESOLVED','success_witness':None,'failure_witness':None,'post_shrink_class_digest':None,'collision_contribution':None})
    classes.sort(key=lambda x:x['class_id'])
    le=sum(x['member_count'] for x in lg); re=sum(x['member_count'] for x in rg)
    pairs=sum(x['child_pair_multiplicity'] for x in classes); refs=sum(x['refinement_multiplicity'] for x in classes)
    if (le,re,pairs,refs)!=(LEFT_N,RIGHT_N,PAIR_N,REF_N): raise AssertionError('CONSERVATION')
    if len({x['source_domain_digest'] for x in classes})!=len(classes): raise AssertionError('SOURCE_DOMAIN_DUPLICATION')
    p={'candidate_phase':'STRUCTURAL_DISCOVERY_PARTITION_ONLY','candidate_status':'EXECUTABLE_DRAFT','admitted':False,
       'source':{'spec_file_sha256':fh(spec_path),'spec_schema':SPEC_SCHEMA,'parent_subject_commit':BASE,'node8_artifact_sha256':N8_SHA,'node8_semantic_digest':N8_SEM,'node8_coordinate_entries_digest':N8_CENT,'leaf5_artifact_sha256':L5_SHA,'leaf5_semantic_digest':L5_SEM,'leaf5_binding':{'factor_index_zero_based':4,'leaf_ordinal_one_based':5,'block_ambient_rref':[5]}},
       'join_domain':{'ordinary_steps':[[1,0],[0,1]],'ordinary_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]]},
       'geometry':{'left_boundary_ambient_rref':[4,1],'right_boundary_ambient_rref':[5],'common_boundary_ambient_rref':[4,1],'parent_boundary_ambient_rref':[1],'left_expand_identity':True,'right_expand_identity':False,'shrink_identity':False},
       'discovery_partition':{'structural_signature_definition':{'geometric_skeleton':'consecutive duplicate child geometry removed; scalar values excluded','scalar_typical_pattern':'canonical scalar typical reduction derived from trajectory values','scalar_run_profiles':'stored as per-group histograms; not used as success/failure oracle'},'left_group_count':len(lg),'right_group_count':len(rg),'structural_class_count':len(classes),'successful_class_count':0,'failed_class_count':0,'unresolved_class_count':len(classes),'left_groups':lg,'right_groups':rg,'classes':classes},
       'conservation_ledger':{'left_entry_count':le,'right_entry_count':re,'child_pair_count':pairs,'ordinary_hv_refinement_count':refs,'expected_child_pair_count':PAIR_N,'expected_ordinary_hv_refinement_count':REF_N,'source_domain_class_key_count':len(classes),'source_domain_class_keys_unique':True,'aggregate_group_partition_complete':True,'aggregate_group_partition_pairwise_disjoint':True,'omitted_child_pair_multiplicity':0,'duplicated_child_pair_multiplicity':0,'omitted_refinement_multiplicity':0,'duplicated_refinement_multiplicity':0,'conservation_holds':True},
       'materialization':{'child_pair_records_materialized':0,'fine_hv_paths_materialized':0,'aggregate_structural_class_records_materialized':len(classes)},
       'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'canonical_group_order':True,'canonical_class_order':True,'seed_hex':SEED,'artifact_is_order_mode_independent_by_construction':True},
       'classification_boundary':{'success_claims_made':0,'failure_claims_made':0,'all_classes_unresolved':True,'join_correction_replayed':False,'shrink_correction_replayed':False,'post_shrink_compactification_replayed':False,'width_classification_replayed':False,'direct_success_witnesses_complete':False,'explicit_failure_witnesses_complete':False},
       'strict_boundary':{'node9_frontier_spec_frozen':True,'node9_frontier_executable_draft':'DISCOVERY_PARTITION_ONLY','node9_frontier_candidate_complete':False,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'formal_admission':'BLOCKED','next_gate':'CLOSED','root_reached':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'},
       'result':'HONEST_UNRESOLVED_STRUCTURAL_PARTITION_AT_CORRECTED_NODE9_PARENT_FRONTIER'}
    art={'schema':ART_SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':p,'semantic_digest':dg(p)}; save(art,out_path); return art

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--node8-artifact',type=Path,required=True); ap.add_argument('--leaf5-artifact',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--order',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); a=ap.parse_args()
    art=build(a.spec,a.node8_artifact,a.leaf5_artifact,a.output,a.order); p=art['proof_payload']; d=p['discovery_partition']; l=p['conservation_ledger']
    print('NODE9_FRONTIER_PRODUCER = EXECUTABLE_DRAFT_DISCOVERY_ONLY'); print('LEFT_STRUCTURAL_GROUPS =',d['left_group_count']); print('RIGHT_STRUCTURAL_GROUPS =',d['right_group_count']); print('DISCOVERED_CLASSES =',d['structural_class_count']); print('SUCCESS = 0'); print('FAILED = 0'); print('UNRESOLVED =',d['unresolved_class_count']); print('CHILD_PAIRS =',l['child_pair_count']); print('ORDINARY_HV_REFINEMENTS =',l['ordinary_hv_refinement_count']); print('CONSERVATION = PASS'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
