#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, math, random
from collections import Counter
from pathlib import Path

SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-INTEGRATION-NODE9-PREFLIGHT-v1'
SPEC_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-PREFLIGHT-SPEC-v1'
LEAF_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-RIGHT-LEAF5-CANDIDATE-v1'
SOURCE_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
SPEC_SHA='9b779324828d48d8fc54ca20cf3e7dfaeecae061f73dfe7205aa438f2985fe74'
LEAF_SHA='6e4bbd67747405846b63a87633e34d41b0f720d33a6f55e877717b5463c01882'
SOURCE_SHA='80b74b500ae82639e51568a9a6dc70a72668f32991add42bc5ffac05b3f9537f'
SOURCE_SEM='e0017e4e5de933e520c6ea374ef291c07bbbb373478c6f9952911cc376380622'
SOURCE_ENTRIES='c6beadf320cf886765d5c8a804887cbf14d854b8f96fc6997058fd0cf0afe480'
SOURCE_STREAM='c109730b8f3608d59059ff07a2235d42510be5cbcb5bac991eeb51a7991c7400'
COORD_ENTRIES='464093b979c947f64de3598172b0d276e8b546151660e5f2ac228aff371c74ee'
COORD_STREAM='856abcc9dbc1f37b0dfb210ed669c98b775dce560ce6012560a6027a633d0000'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
SEED=0xC049119

def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rref(rows,d):
    piv=[]
    for raw in rows:
        x=int(raw)
        if not 0 <= x < (1<<d): raise AssertionError('vector range')
        for r in piv: x=min(x,x^r)
        if x:
            b=x.bit_length()-1
            piv=[r^x if (r>>b)&1 else r for r in piv]+[x]
            piv.sort(reverse=True)
    return tuple(piv)

def span_set(rows,d):
    b=rref(rows,d); out=set()
    for mask in range(1<<len(b)):
        x=0
        for i,v in enumerate(b):
            if mask>>i & 1: x^=v
        out.add(x)
    return out

def intersection_basis(a,b,d):
    vals=sorted(span_set(a,d)&span_set(b,d))
    return rref(vals,d)

def vec_to_coord(v,parent):
    theta=len(parent)
    for c in range(1<<theta):
        a=0
        for i,b in enumerate(parent):
            if c & (1<<(theta-1-i)): a^=int(b)
        if a==int(v): return c
    raise AssertionError('vector outside parent boundary')

def coord_sub(rows,parent):
    return list(rref([vec_to_coord(v,parent) for v in rows],len(parent)))

def coord_traj(raw,parent):
    return [{'left':coord_sub(q['left'],parent),'right':coord_sub(q['right'],parent),'value':int(q['value'])} for q in raw]

def hist(entries):
    return {str(k):v for k,v in sorted(Counter(len(e['trajectory']) for e in entries).items())}

def stream(entries):
    h=hashlib.sha256()
    for e in entries: h.update(cj(e['trajectory'])+b'\n')
    return h.hexdigest()

def hv_count(lh,rh):
    return sum(int(lc)*int(rc)*math.comb(int(m)+int(n)-2,int(m)-1) for m,lc in lh.items() for n,rc in rh.items())

def load_bound(path,sha,schema,scope):
    if fh(path)!=sha: raise AssertionError('bound file sha')
    x=json.load(open(path))
    if x.get('schema')!=schema or x.get('semantic_digest_scope')!=scope: raise AssertionError('bound schema')
    key={'spec_payload':'spec_payload','leaf_payload':'leaf_payload'}[scope]
    if x.get('semantic_digest')!=dg(x[key]): raise AssertionError('bound semantic')
    return x

def build(source_path,spec_path,leaf_path,out_path,mode):
    spec=load_bound(spec_path,SPEC_SHA,SPEC_SCHEMA,'spec_payload'); sp=spec['spec_payload']
    leaf=load_bound(leaf_path,LEAF_SHA,LEAF_SCHEMA,'leaf_payload'); lp=leaf['leaf_payload']
    if fh(source_path)!=SOURCE_SHA: raise AssertionError('source sha')
    src=json.load(open(source_path))
    if src.get('schema')!=SOURCE_SCHEMA or src.get('semantic_digest')!=SOURCE_SEM: raise AssertionError('source bind')
    proof=src['proof_payload']; closure=proof['reachable_closure']; raw=closure['entries']
    if len(raw)!=8676 or dg(raw)!=SOURCE_ENTRIES or closure.get('reachable_stream_sha256')!=SOURCE_STREAM: raise AssertionError('source closure')
    if sp['source_node8']['artifact_sha256']!=SOURCE_SHA or sp['right_leaf']['artifact_sha256']!=LEAF_SHA: raise AssertionError('spec binding')
    ordered=copy.deepcopy(raw)
    if mode=='reversed': ordered.reverse()
    elif mode=='seeded-shuffle': random.Random(SEED).shuffle(ordered)
    elif mode!='original': raise AssertionError('mode')
    parent=tuple(sp['source_node8']['parent_boundary_ambient_rref'])
    converted=[]
    for e in ordered:
        z=copy.deepcopy(e); z['trajectory']=coord_traj(e['trajectory'],parent); converted.append(z)
    converted.sort(key=cj)
    if dg(converted)!=COORD_ENTRIES or stream(converted)!=COORD_STREAM: raise AssertionError('coordinate handoff')
    lh=hist(converted); rh=hist(lp['entries'])
    if lh!=sp['source_node8']['left_trajectory_length_histogram'] or rh!=sp['right_leaf']['trajectory_length_histogram']: raise AssertionError('histogram')
    pairs=len(converted)*len(lp['entries']); refs=hv_count(lh,rh)
    exp=sp['expected_preflight']
    if (pairs,refs)!=(exp['child_pairs'],exp['ordinary_hv_refinements']): raise AssertionError('analytic counts')
    blocks=[tuple(x) for x in sp['scaffold']['whole_factor_blocks']]
    left=tuple(sp['geometry']['left_boundary_ambient_rref']); right=tuple(sp['geometry']['right_boundary_ambient_rref'])
    common=rref((*left,*right),3); parent_boundary=intersection_basis([v for i in range(5) for v in blocks[i]],blocks[5],3)
    if (left,right,common,parent_boundary)!=((4,1),(5,),(4,1),(1,)): raise AssertionError('geometry')
    caps=sp['cap_policy']; pair_exceeded=pairs>int(caps['pair_cap']); ref_exceeded=refs>int(caps['refinement_cap'])
    stop='CHILD_PAIR_CAP_EXCEEDED' if pair_exceeded else ('REFINEMENT_CAP_EXCEEDED' if ref_exceeded else None)
    if stop!=caps['expected_stop_reason']: raise AssertionError('cap policy')
    payload={
      'candidate_status':'CONSTRUCTIVE_CANDIDATE','admitted':False,'gate':sp['gate'],
      'source':{'subject_commit':sp['source_node8']['subject_commit'],'artifact_sha256':SOURCE_SHA,'semantic_digest':SOURCE_SEM,'reachable_entries_digest':SOURCE_ENTRIES,'entry_count':8676},
      'spec':{'artifact_sha256':SPEC_SHA,'semantic_digest':spec['semantic_digest']},
      'node8_integration_handoff':{'parent_boundary_ambient_rref':list(parent),'coordinate_dimension':2,'entry_count':8676,'coordinate_entries_digest':COORD_ENTRIES,'coordinate_stream_sha256':COORD_STREAM,'trajectory_length_histogram':lh,'all_source_subspaces_in_parent_boundary':True},
      'right_leaf':{'factor_index_zero_based':4,'leaf_ordinal_one_based':5,'block_ambient_rref':[5],'artifact_sha256':LEAF_SHA,'semantic_digest':leaf['semantic_digest'],'entry_count':36,'entries_digest':lp['entries_digest'],'trajectory_stream_sha256':lp['trajectory_stream_sha256'],'trajectory_length_histogram':rh},
      'geometry':copy.deepcopy(sp['geometry']),
      'ordinary_join_domain':copy.deepcopy(sp['ordinary_join_domain']),
      'preflight':{'left_entries':8676,'right_entries':36,'child_pairs':pairs,'ordinary_hv_refinements':refs,'pair_cap':int(caps['pair_cap']),'refinement_cap':int(caps['refinement_cap']),'pair_cap_exceeded':pair_exceeded,'refinement_cap_exceeded':ref_exceeded,'stop_reason':stop,'pair_records_emitted':0,'refinement_records_emitted':0,'counting_method':'LENGTH_HISTOGRAM_X_BINOMIAL_HV_FORMULA'},
      'invariant_vector':{f'CN9P-INV-{i:02d}':'PASS' for i in range(1,13)},
      'strict_boundary':{'pr116_exact_head_ci_green':False,'pr116_admitted':False,'corrected_node8_parent_up_k_candidate_complete':True,'corrected_node8_parent_up_k_complete':False,'corrected_node8_up_k_admitted':False,'node8_integration_candidate_complete':True,'node8_integrated_into_bottom_up_executor':False,'node9_parent_preflight_candidate_complete':True,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'root_reached':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'},
      'result':'HONEST_OPEN_AT_CORRECTED_NODE9_PARENT_REFINEMENT_CAPABILITY','next_gate_status':'CLOSED_PENDING_PR116_EXACT_HEAD_CI_AND_SEMANTIC_ADMISSION'
    }
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':payload,'semantic_digest':dg(payload)}
    Path(out_path).write_bytes(cj(art)+b'\n')
    print('JANUS_C049_1_B4_6_3_CORRECTED_NODE9_PREFLIGHT = PASS')
    print('NODE9_CHILD_PAIRS =',pairs); print('NODE9_ORDINARY_HV_REFINEMENTS =',refs)
    print('PAIR_RECORDS_EMITTED = 0'); print('REFINEMENT_RECORDS_EMITTED = 0')
    print('STOP_REASON =',stop); print('ADMITTED = FALSE'); print('P_VS_NP = OPEN')
    return art

def main():
    p=argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('spec'); p.add_argument('leaf'); p.add_argument('--output',required=True); p.add_argument('--entry-order',choices=('original','reversed','seeded-shuffle'),default='original'); a=p.parse_args(); build(a.source,a.spec,a.leaf,a.output,a.entry_order)
if __name__=='__main__': main()
