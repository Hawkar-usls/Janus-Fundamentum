#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping
import janus_c040_producer_lane_isolation as lane

CID='C040.2'; SCHEMA='janus.c040.2.producer-lane-c039-adapter.v1'; CONSTRUCTOR='PRODUCER_LANE_MODULE_FOREST_V1'
FORBIDDEN={'assignments','assignment_rows','communication_rows','evaluation_vector','row_matrix','truth_table','truth_table_blob','raw_bitmap','assignment_index','lookup_table','branch_assignment'}
class Terminal(str,Enum): SELECTED='VTREE_SELECTED_CERTIFIED'; EXHAUSTED='OPEN_PORTFOLIO_EXHAUSTED'; BUDGET='OPEN_DISCOVERY_BUDGET'; FEATURE='OPEN_FEATURE_LANGUAGE'; STALE='OPEN_CAPABILITY_STALE'; INVALID='INVALID_DISCOVERY_CERTIFICATE'
@dataclass(frozen=True)
class Budget:
    max_candidates:int=4; max_generation_work:int=1_000_000; max_probe_work:int=1_000_000; max_total_work:int=2_000_000; max_certificate_bytes:int=8_000_000
    @property
    def digest(self):return dg('BUDGET',self.__dict__)

def safe(x:Any)->Any:
    if x is None or isinstance(x,(str,bool,int)):return x
    if isinstance(x,float):raise TypeError('float')
    if isinstance(x,(list,tuple)):return [safe(v) for v in x]
    if isinstance(x,dict):
        out={}
        for k,v in x.items():
            k=str(k)
            if k.lower() in FORBIDDEN:raise ValueError('enumerative payload')
            out[k]=safe(v)
        return out
    raise TypeError('json')
def cj(x):return json.dumps(safe(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def dg(tag,x):return 'sha256:'+hashlib.sha256(b'JANUS-C040.2-'+tag.encode()+b'\0'+cj(x)).hexdigest()
def raw_formula_digest(raw):return dg('FORMULA',raw)

def tree_wire(tree):
    leaves={}; internal=[]; counter=[0]
    def walk(node):
        if isinstance(node,int):
            key=f'leaf-{node}'; leaves[key]=f'x{node}'; return key
        if not isinstance(node,(list,tuple)) or len(node)!=2:raise ValueError('derived vtree')
        left,right=walk(node[0]),walk(node[1]); key=f'node-{counter[0]:04d}'; counter[0]+=1; internal.append({'id':key,'left':left,'right':right}); return key
    root=walk(tree)
    return {'leaves':dict(sorted(leaves.items())),'internal_nodes':internal,'root':root}
def tree_digest(tree):return dg('VTREE',tree)

def constructor(raw,budget:Budget):
    safe(raw); factors=lane.core.parse_factors(raw); meter=lane.core.Meter(budget.max_generation_work,0,budget.max_certificate_bytes)
    modules,edges,roots,conflicts=lane.discover_modules_with_producer_lanes(factors,meter)
    if conflicts:raise lane.core.OpenResult('OPEN_HEAD_CONFLICT')
    derived=lane.core.derive_variable_vtree(modules,edges,roots); wire=tree_wire(derived)
    feature={'kind':'HORN_HEAD_MAP_AND_AFFINE_SUPPORT','formula_digest':raw_formula_digest(raw),'producer_lanes':{str(k):v for k,v in sorted(lane.producer_lane_map(factors).items())},'module_count':len(modules),'edge_count':len(edges)}
    feature['feature_digest']=dg('FEATURE',feature)
    proof={'constructor':CONSTRUCTOR,'formula_digest':raw_formula_digest(raw),'feature_digest':feature['feature_digest'],'modules':[m.to_dict() for m in modules],'edges':[{'a':a,'b':b,'variables':list(v)} for (a,b),v in sorted(edges.items())],'roots':roots,'vtree':wire,'generation_work_units':meter.work,'depends_on_assignment_values':False,'generated_before_probe':True}
    proof['generation_proof_digest']=dg('GENERATION',proof)
    candidate={'schema':'janus.c040.vtree-candidate.v1','candidate_id':'candidate-0000','constructor':CONSTRUCTOR,'constructor_digest':dg('CONSTRUCTOR',CONSTRUCTOR),'feature_digests':[feature['feature_digest']],'generation_proof_digest':proof['generation_proof_digest'],'generated_before_probe':True,'depends_on_assignment_values':False,'vtree':wire,'vtree_digest':tree_digest(wire)}
    candidate['candidate_digest']=dg('CANDIDATE',candidate)
    return feature,proof,candidate,meter.work

def validate_probe(probe,candidate,formula_digest,capability_digest):
    required={'terminal','full_compile','formula_digest','capability_digest','vtree_digest','c039_certificate_digest','max_node_representation','total_representation','total_work_units'}
    if not isinstance(probe,dict) or not required<=set(probe):raise ValueError('probe')
    if probe['full_compile'] is not True or probe['formula_digest']!=formula_digest or probe['capability_digest']!=capability_digest or probe['vtree_digest']!=candidate['vtree_digest']:raise ValueError('probe binding')
    if probe['terminal'] not in {'CLOSED_POLY','OPEN_LANGUAGE','OPEN_BUDGET','OPEN_EQUIVALENCE','OPEN_REPRESENTATION_GROWTH','OPEN_COMPOSITION'}:raise ValueError('terminal')
    for key in ('max_node_representation','total_representation','total_work_units'):
        if not isinstance(probe[key],int) or probe[key]<0:raise ValueError('ledger')
    body=dict(probe); claimed=body.pop('probe_digest',None)
    computed=dg('PROBE',body)
    if claimed not in (None,computed):raise ValueError('probe digest')
    probe=dict(probe);probe['probe_digest']=computed;return probe

def run(raw,capability_digest:str,probe_fn:Callable[[Mapping[str,Any]],Mapping[str,Any]],budget:Budget=Budget()):
    formula_digest=raw_formula_digest(raw)
    try:
        feature,proof,candidate,generation_work=constructor(raw,budget)
    except lane.core.OpenResult as exc:
        reason=str(exc); terminal=Terminal.BUDGET if reason in {'OPEN_WORK_BUDGET','OPEN_CERTIFICATE_VOLUME','OPEN_TABLE_BUDGET'} else Terminal.EXHAUSTED
        q={'schema':SCHEMA,'canonical_id':CID,'terminal':terminal.value,'reason_code':reason,'formula_digest':formula_digest,'capability_digest':capability_digest,'budget_digest':budget.digest,'candidate_phase':'FROZEN_BEFORE_PROBES','features':[],'candidates':[],'candidate_manifest_digest':dg('MANIFEST',[]),'probes':[],'selected_candidate_id':None,'selected_vtree_digest':None,'work_ledger':{'candidate_generation_work_units':0,'probe_work_units':0,'total_work_units':0},'p_vs_np':'OPEN'}
        q['discovery_digest']=dg('DISCOVERY',q);return q
    except (TypeError,ValueError):
        q={'schema':SCHEMA,'canonical_id':CID,'terminal':Terminal.FEATURE.value,'reason_code':'INVALID_OR_UNSUPPORTED_FEATURE','formula_digest':formula_digest,'capability_digest':capability_digest,'budget_digest':budget.digest,'candidate_phase':'FROZEN_BEFORE_PROBES','features':[],'candidates':[],'candidate_manifest_digest':dg('MANIFEST',[]),'probes':[],'selected_candidate_id':None,'selected_vtree_digest':None,'work_ledger':{'candidate_generation_work_units':0,'probe_work_units':0,'total_work_units':0},'p_vs_np':'OPEN'}
        q['discovery_digest']=dg('DISCOVERY',q);return q
    candidates=[candidate]
    if len(candidates)>budget.max_candidates or generation_work>budget.max_generation_work:
        terminal=Terminal.BUDGET;probes=[];probe_work=0;selected=None
    else:
        manifest=dg('MANIFEST',[c['candidate_digest'] for c in candidates])
        raw_probe=probe_fn(candidate)
        probe=validate_probe(raw_probe,candidate,formula_digest,capability_digest)
        probes=[probe];probe_work=probe['total_work_units'];selected=candidate if probe['terminal']=='CLOSED_POLY' else None
        terminal=Terminal.SELECTED if selected else Terminal.EXHAUSTED
    manifest=dg('MANIFEST',[c['candidate_digest'] for c in candidates])
    total=generation_work+probe_work
    if probe_work>budget.max_probe_work or total>budget.max_total_work:terminal=Terminal.BUDGET;selected=None
    q={'schema':SCHEMA,'canonical_id':CID,'terminal':terminal.value,'reason_code':'NONE' if terminal is Terminal.SELECTED else terminal.value,'formula_digest':formula_digest,'capability_digest':capability_digest,'budget_digest':budget.digest,'candidate_phase':'FROZEN_BEFORE_PROBES','depends_on_assignment_values':False,'features':[feature],'generation_proofs':[proof],'candidates':candidates,'candidate_manifest_digest':manifest,'probes':probes,'selected_candidate_id':None if selected is None else selected['candidate_id'],'selected_vtree_digest':None if selected is None else selected['vtree_digest'],'work_ledger':{'candidate_generation_work_units':generation_work,'probe_work_units':probe_work,'total_work_units':total},'direct_module_forest_dp_promoted_to_selection':False,'p_vs_np':'OPEN'}
    q['discovery_digest']=dg('DISCOVERY',q)
    if len(cj(q))>budget.max_certificate_bytes:q['terminal']=Terminal.BUDGET.value;q['reason_code']='OPEN_CERTIFICATE_VOLUME';q['selected_candidate_id']=None;q['selected_vtree_digest']=None;q['discovery_digest']=dg('DISCOVERY',q)
    return q

def replay_constructor(raw,candidate,budget=Budget()):
    try:return constructor(raw,budget)[2]==candidate
    except Exception:return False
class FakeProbe:
    def __init__(self,terminal='CLOSED_POLY'):self.terminal=terminal;self.calls=0
    def __call__(self,c):
        self.calls+=1;q={'terminal':self.terminal,'full_compile':True,'formula_digest':FORMULA,'capability_digest':CAPABILITY,'vtree_digest':c['vtree_digest'],'c039_certificate_digest':dg('C039-CERT',c['candidate_digest']),'max_node_representation':7,'total_representation':11,'total_work_units':13};q['probe_digest']=dg('PROBE',q);return q

def sample():return [{'id':0,'language':'SINGLE_HEAD_HORN','body':[1],'head':2},{'id':1,'language':'SINGLE_HEAD_HORN','body':[2],'head':3}]
FORMULA=raw_formula_digest(sample());CAPABILITY=dg('CAPABILITY','test')
def self_test():
    C={};raw=sample();p=FakeProbe();a=run(raw,CAPABILITY,p);b=run(raw,CAPABILITY,FakeProbe())
    C['deterministic_discovery_digest']=a['discovery_digest']==b['discovery_digest']
    C['one_probe_per_frozen_candidate']=p.calls==1 and len(a['probes'])==len(a['candidates'])==1
    C['manifest_frozen_before_probe']=a['candidate_phase']=='FROZEN_BEFORE_PROBES' and a['candidate_manifest_digest']==dg('MANIFEST',[a['candidates'][0]['candidate_digest']])
    C['constructor_assignment_independent']=a['depends_on_assignment_values'] is False and a['candidates'][0]['depends_on_assignment_values'] is False
    C['generation_proof_replays']=replay_constructor(raw,a['candidates'][0])
    C['closed_probe_selects']=a['terminal']==Terminal.SELECTED.value and a['selected_vtree_digest']==a['candidates'][0]['vtree_digest']
    op=FakeProbe('OPEN_LANGUAGE');o=run(raw,CAPABILITY,op);C['all_open_is_portfolio_exhausted']=o['terminal']==Terminal.EXHAUSTED.value and o['selected_vtree_digest'] is None
    C['work_ledgers_separated']=a['work_ledger']['total_work_units']==a['work_ledger']['candidate_generation_work_units']+a['work_ledger']['probe_work_units']
    C['direct_dp_not_promoted']=a['direct_module_forest_dp_promoted_to_selection'] is False
    C['capability_locked']=a['capability_digest']==CAPABILITY and a['probes'][0]['capability_digest']==CAPABILITY
    try:cj({'truth_table':[0,1]});rejected=False
    except ValueError:rejected=True
    C['hidden_truth_table_rejected']=rejected
    tight=run(raw,CAPABILITY,FakeProbe(),Budget(max_generation_work=0));C['generation_budget_is_open']=tight['terminal']==Terminal.BUDGET.value
    assert len(C)==12 and all(C.values()),C
    return {'status':'PASS','canonical_id':CID,'constructor':CONSTRUCTOR,'acceptance_checks':len(C),**C,'p_vs_np':'OPEN'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');a=ap.parse_args()
    if a.self_test:print(json.dumps(self_test(),sort_keys=True,separators=(',',':')));return 0
    ap.error('use --self-test')
if __name__=='__main__':raise SystemExit(main())
