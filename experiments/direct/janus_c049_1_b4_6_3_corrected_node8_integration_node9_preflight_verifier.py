#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json, math
from collections import Counter
from pathlib import Path

ART_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-INTEGRATION-NODE9-PREFLIGHT-v1'
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

class VError(AssertionError):
    pass

def fail(code):
    raise VError(code)
def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rr(rows,d):
    p=[]
    for raw in rows:
        x=int(raw)
        if not 0 <= x < (1<<d): fail('VECTOR_RANGE')
        for q in p: x=min(x,x^q)
        if x:
            b=x.bit_length()-1
            p=[q^x if (q>>b)&1 else q for q in p]+[x]; p.sort(reverse=True)
    return tuple(p)

def span(rows,d):
    b=rr(rows,d); vals=set()
    for mask in range(1<<len(b)):
        x=0
        for i,v in enumerate(b):
            if mask>>i & 1: x^=v
        vals.add(x)
    return vals

def inter(a,b,d): return rr(sorted(span(a,d)&span(b,d)),d)
def vcoord(v,basis):
    t=len(basis)
    for c in range(1<<t):
        z=0
        for i,q in enumerate(basis):
            if c & (1<<(t-1-i)): z^=int(q)
        if z==int(v): return c
    fail('COORDINATE_OUTSIDE_BOUNDARY')
def subcoord(rows,basis): return list(rr([vcoord(v,basis) for v in rows],len(basis)))
def trcoord(t,basis): return [{'left':subcoord(s['left'],basis),'right':subcoord(s['right'],basis),'value':int(s['value'])} for s in t]
def histogram(entries): return {str(k):v for k,v in sorted(Counter(len(e['trajectory']) for e in entries).items())}
def stream(entries):
    h=hashlib.sha256()
    for e in entries: h.update(cj(e['trajectory'])+b'\n')
    return h.hexdigest()
def hvc(lh,rh): return sum(int(a)*int(b)*math.comb(int(m)+int(n)-2,int(m)-1) for m,a in lh.items() for n,b in rh.items())

def scalar_reduce(v):
    a=list(v)
    while True:
        for i in range(1,len(a)):
            if a[i-1]==a[i]: del a[i]; break
        else:
            hit=False
            for i in range(len(a)):
                for j in range(i+2,len(a)):
                    z=a[i:j+1]
                    if (z[0]<=z[-1] and all(z[0]<=q<=z[-1] for q in z[1:-1])) or (z[0]>=z[-1] and all(z[0]>=q>=z[-1] for q in z[1:-1])):
                        del a[i+1:j]; hit=True; break
                if hit: break
            if not hit: return tuple(a)
            continue
        continue

def reconstruct_patterns():
    found=set()
    for n in range(1,16):
        for v in itertools.product((0,1),repeat=n):
            if scalar_reduce(v)==v: found.add(v)
    return tuple(sorted(found))

def reconstruct_leaf():
    pats=reconstruct_patterns()
    expected=((0,),(0,1),(0,1,0),(1,),(1,0),(1,0,1))
    if pats!=expected: fail('LEAF_SCALAR_PATTERNS')
    out=[]
    for a in pats:
        for b in pats:
            t=[{'left':[],'right':[1],'value':v} for v in a]+[{'left':[1],'right':[],'value':v} for v in b]
            out.append({'trajectory':t,'source_run_patterns':[list(a),list(b)]})
    out.sort(key=lambda e:cj(e['trajectory']))
    return out

def load_json(path,sha,schema,scope,code):
    if fh(path)!=sha: fail(code+'_SHA')
    x=json.load(open(path))
    if x.get('schema')!=schema or x.get('semantic_digest_scope')!=scope: fail(code+'_SCHEMA')
    key='spec_payload' if scope=='spec_payload' else 'leaf_payload'
    if x.get('semantic_digest')!=dg(x[key]): fail(code+'_SEMANTIC')
    return x

def replay(source_path,spec_path,leaf_path):
    spec=load_json(spec_path,SPEC_SHA,SPEC_SCHEMA,'spec_payload','SPEC'); sp=spec['spec_payload']
    leaf=load_json(leaf_path,LEAF_SHA,LEAF_SCHEMA,'leaf_payload','LEAF'); lp=leaf['leaf_payload']
    expected_leaf=reconstruct_leaf()
    if lp.get('entries')!=expected_leaf or lp.get('entry_count')!=36 or lp.get('entries_digest')!=dg(expected_leaf): fail('RIGHT_LEAF_RECONSTRUCTION')
    if lp.get('trajectory_length_histogram')!=histogram(expected_leaf) or lp.get('trajectory_stream_sha256')!=stream(expected_leaf): fail('RIGHT_LEAF_RECEIPT')
    if (lp.get('factor_index_zero_based'),lp.get('leaf_ordinal_one_based'),lp.get('block_ambient_rref'))!=(4,5,[5]): fail('RIGHT_LEAF_BINDING')
    if fh(source_path)!=SOURCE_SHA: fail('SOURCE_ARTIFACT_SHA')
    src=json.load(open(source_path))
    if src.get('schema')!=SOURCE_SCHEMA or src.get('semantic_digest')!=SOURCE_SEM: fail('SOURCE_SEMANTIC_DIGEST')
    if src.get('semantic_digest')!=dg(src['proof_payload']): fail('SOURCE_SEMANTIC_REPLAY')
    c=src['proof_payload']['reachable_closure']; raw=c['entries']
    if len(raw)!=8676: fail('SOURCE_ENTRY_COUNT')
    if dg(raw)!=SOURCE_ENTRIES or c.get('reachable_entries_digest')!=SOURCE_ENTRIES or c.get('reachable_stream_sha256')!=SOURCE_STREAM: fail('SOURCE_CLOSURE_RECEIPT')
    basis=(4,1); converted=[]
    for e in raw:
        z=copy.deepcopy(e); z['trajectory']=trcoord(e['trajectory'],basis); converted.append(z)
    converted.sort(key=cj)
    if dg(converted)!=COORD_ENTRIES or stream(converted)!=COORD_STREAM: fail('COORDINATE_ENTRIES_DIGEST')
    lh=histogram(converted); rh=histogram(expected_leaf)
    if lh!=sp['source_node8']['left_trajectory_length_histogram']: fail('LEFT_LENGTH_HISTOGRAM')
    if rh!=sp['right_leaf']['trajectory_length_histogram']: fail('RIGHT_LENGTH_HISTOGRAM')
    pairs=len(converted)*len(expected_leaf); refs=hvc(lh,rh)
    blocks=[tuple(x) for x in sp['scaffold']['whole_factor_blocks']]
    common=rr((4,1,5),3); parent=inter([q for i in range(5) for q in blocks[i]],blocks[5],3)
    if (common,parent)!=((4,1),(1,)): fail('GEOMETRY')
    return {'spec':spec,'leaf':leaf,'left_hist':lh,'right_hist':rh,'pairs':pairs,'refs':refs}

def verify(art,r):
    if art.get('schema')!=ART_SCHEMA or art.get('semantic_digest_scope')!='proof_payload': fail('ARTIFACT_SCHEMA')
    p=art.get('proof_payload')
    if not isinstance(p,dict) or art.get('semantic_digest')!=dg(p): fail('ARTIFACT_SEMANTIC')
    if p.get('candidate_status')!='CONSTRUCTIVE_CANDIDATE' or p.get('admitted') is not False: fail('CANDIDATE_STATUS')
    if p['source'].get('artifact_sha256')!=SOURCE_SHA: fail('SOURCE_ARTIFACT_SHA')
    if p['source'].get('semantic_digest')!=SOURCE_SEM: fail('SOURCE_SEMANTIC_DIGEST')
    if p['source'].get('entry_count')!=8676: fail('SOURCE_ENTRY_COUNT')
    h=p['node8_integration_handoff']
    if h.get('coordinate_entries_digest')!=COORD_ENTRIES or h.get('coordinate_stream_sha256')!=COORD_STREAM: fail('COORDINATE_ENTRIES_DIGEST')
    if h.get('trajectory_length_histogram')!=r['left_hist'] or h.get('entry_count')!=8676: fail('LEFT_LENGTH_HISTOGRAM')
    leaf=p['right_leaf']
    if leaf.get('artifact_sha256')!=LEAF_SHA: fail('RIGHT_LEAF_SHA')
    if leaf.get('entry_count')!=36 or leaf.get('trajectory_length_histogram')!=r['right_hist']: fail('RIGHT_LEAF_ENTRY_COUNT')
    if p.get('ordinary_join_domain')!={'steps':[[1,0],[0,1]],'diagonal_allowed':False,'path_count_formula':'C(m+n-2,m-1)'}: fail('JOIN_DOMAIN')
    q=p['preflight']
    if q.get('child_pairs')!=312336 or q.get('child_pairs')!=r['pairs']: fail('CHILD_PAIR_COUNT')
    if q.get('ordinary_hv_refinements')!=98319408 or q.get('ordinary_hv_refinements')!=r['refs']: fail('HV_REFINEMENT_COUNT')
    if (q.get('pair_cap'),q.get('refinement_cap'),q.get('stop_reason'))!=(10000,2000000,'CHILD_PAIR_CAP_EXCEEDED'): fail('CAP_STOP_REASON')
    if q.get('pair_records_emitted')!=0 or q.get('refinement_records_emitted')!=0: fail('RECORD_MATERIALIZATION')
    iv=p.get('invariant_vector'); expected={f'CN9P-INV-{i:02d}':'PASS' for i in range(1,13)}
    if iv!=expected: fail('INVARIANT_VECTOR')
    b=p.get('strict_boundary',{})
    expected_b={'pr116_exact_head_ci_green':False,'pr116_admitted':False,'corrected_node8_parent_up_k_candidate_complete':True,'corrected_node8_parent_up_k_complete':False,'corrected_node8_up_k_admitted':False,'node8_integration_candidate_complete':True,'node8_integrated_into_bottom_up_executor':False,'node9_parent_preflight_candidate_complete':True,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'root_reached':False,'root_full_set_computed':False,'root_empty_proved':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','current_global_terminal':TERM,'p_vs_np':'OPEN'}
    if b!=expected_b: fail('FALSE_ADMISSION_OR_ROOT_CLAIM')
    if p.get('result')!='HONEST_OPEN_AT_CORRECTED_NODE9_PARENT_REFINEMENT_CAPABILITY' or p.get('next_gate_status')!='CLOSED_PENDING_PR116_EXACT_HEAD_CI_AND_SEMANTIC_ADMISSION': fail('BOUNDARY_RESULT')

def static_check(producer_path):
    text=Path(producer_path).read_text(); ast.parse(text)
    forbidden=('itertools.product(','pair_records.append(','refinement_records.append(','for left_entry in','for right_entry in')
    if any(x in text for x in forbidden): fail('STATIC_ANALYTIC_ONLY')
    if 'math.comb' not in text or 'hv_count' not in text: fail('STATIC_ANALYTIC_ONLY')
    print('STATIC_ANALYTIC_ONLY_NO_CHILD_CARTESIAN_OR_REFINEMENT_MATERIALIZATION = PASS')

def tamper(art,r):
    tests=[]
    def setv(o,k,v): old=o[k]; o[k]=v; return lambda:o.__setitem__(k,old)
    p=art['proof_payload']
    tests=[
      ('T01_SOURCE_ARTIFACT_SHA','SOURCE_ARTIFACT_SHA',lambda:setv(p['source'],'artifact_sha256','0'*64)),
      ('T02_SOURCE_SEMANTIC_DIGEST','SOURCE_SEMANTIC_DIGEST',lambda:setv(p['source'],'semantic_digest','0'*64)),
      ('T03_SOURCE_ENTRY_COUNT','SOURCE_ENTRY_COUNT',lambda:setv(p['source'],'entry_count',8675)),
      ('T04_COORDINATE_ENTRIES_DIGEST','COORDINATE_ENTRIES_DIGEST',lambda:setv(p['node8_integration_handoff'],'coordinate_entries_digest','0'*64)),
      ('T05_RIGHT_LEAF_SHA','RIGHT_LEAF_SHA',lambda:setv(p['right_leaf'],'artifact_sha256','0'*64)),
      ('T06_RIGHT_LEAF_ENTRY_COUNT','RIGHT_LEAF_ENTRY_COUNT',lambda:setv(p['right_leaf'],'entry_count',35)),
      ('T07_LEFT_LENGTH_HISTOGRAM','LEFT_LENGTH_HISTOGRAM',lambda:setv(p['node8_integration_handoff'],'trajectory_length_histogram',{'3':8676})),
      ('T08_CHILD_PAIR_COUNT','CHILD_PAIR_COUNT',lambda:setv(p['preflight'],'child_pairs',312335)),
      ('T09_HV_REFINEMENT_COUNT','HV_REFINEMENT_COUNT',lambda:setv(p['preflight'],'ordinary_hv_refinements',98319407)),
      ('T10_CAP_STOP_REASON','CAP_STOP_REASON',lambda:setv(p['preflight'],'stop_reason','REFINEMENT_CAP_EXCEEDED')),
      ('T11_RECORD_MATERIALIZATION','RECORD_MATERIALIZATION',lambda:setv(p['preflight'],'refinement_records_emitted',1)),
      ('T12_FALSE_ADMISSION_OR_ROOT_CLAIM','FALSE_ADMISSION_OR_ROOT_CLAIM',lambda:setv(p['strict_boundary'],'root_reached',True)),
    ]
    old=art['semantic_digest']; passed=[]
    for tid,expect,mut in tests:
        undo=mut(); art['semantic_digest']=dg(p)
        try:
            verify(art,r)
        except VError as e:
            if str(e)!=expect: raise AssertionError(f'{tid}: expected {expect}, got {e}')
            passed.append((tid,expect))
        else:
            raise AssertionError(f'{tid}: tamper accepted')
        finally:
            undo(); art['semantic_digest']=old
    if len(passed)!=12: raise AssertionError('tamper count')
    for tid,code in passed: print(f'TAMPER_REJECTED {tid} -> {code}')
    print('DIGEST_REPAIRED_TAMPERS_REJECTED = 12/12')

def main():
    a=argparse.ArgumentParser(); a.add_argument('source'); a.add_argument('spec'); a.add_argument('leaf'); a.add_argument('artifact'); a.add_argument('--producer-source',required=True); a.add_argument('--tamper-self-test',action='store_true'); z=a.parse_args()
    static_check(z.producer_source); r=replay(z.source,z.spec,z.leaf); art=json.load(open(z.artifact)); verify(art,r)
    if z.tamper_self_test: tamper(art,r)
    print('JANUS_C049_1_B4_6_3_CORRECTED_NODE9_PREFLIGHT_VERIFIER = PASS')
    print('INVARIANTS = 12/12'); print('NODE9_CHILD_PAIRS = 312336'); print('NODE9_ORDINARY_HV_REFINEMENTS = 98319408'); print('ADMITTED = FALSE'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
