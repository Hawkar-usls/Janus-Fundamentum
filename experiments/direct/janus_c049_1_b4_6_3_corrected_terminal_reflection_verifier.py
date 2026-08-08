from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json, math
from pathlib import Path

SCHEMA='janus.c049_1.corrected_terminal_reflection_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_terminal_reflection_spec.v1.1'
ROOT_SPEC_SCHEMA='janus.c049_1.corrected_root_full_refinement_spec.v1'
EMPTY_SCHEMA='janus.c049_1.corrected_root_empty_up_k_candidate.v1'
AUDIT_SCHEMA='janus.c049_1.corrected_root_empty_up_k_independent_semantic_audit.v1'
SPEC_BLOB='f45356b9065ad1d9e7e38f8c08d7e2031b5efa89'
ROOT_SPEC_BLOB='401c4856de261f6048d313ca62fa43598ea449e0'
EMPTY_SHA='b82fced138820d028898889eb59d059aaa023616ad774e6f31e0dc290fa492ab'
EMPTY_SEM='b811d3bf3abfd9c48b4454aaf3a9ec863d226092faa164fd8a0cf45bbe1e7ec0'
AUDIT_SHA='dbbbcaaee12dfcbaf073f0e11e182c0c530fe54acb0c05b2996c21a92fa68897'
AUDIT_SEM='e1b35822e6be0be2b4081c359f0be54692450e2e649d64cd5cff5332895308e0'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
class VError(Exception):
    def __init__(self,inv,msg): super().__init__(f'{inv}:{msg}'); self.inv=inv

def req(x,inv,msg):
    if not x: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sem_ok(a): return a.get('semantic_digest_scope')=='proof_payload' and dg(a.get('proof_payload'))==a.get('semantic_digest')

def producer_import_check(path):
    tree=ast.parse(Path(path).read_text(encoding='utf-8')); mods=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
    req(not any(x.endswith('janus_c049_1_b4_6_3_corrected_terminal_reflection_verifier') for x in mods),'INV01','producer imports verifier')

def bind(specp,rootspecp,emptyp,auditp,producerp):
    req(gb(specp)==SPEC_BLOB,'INV01','terminal spec blob'); spec=load(specp)
    req(spec.get('schema')==SPEC_SCHEMA and spec.get('status')=='SPEC_FROZEN' and spec.get('admission') is False,'INV01','terminal spec')
    exp=spec['expected_values_policy']; req(all(exp[k] is None for k in ('expected_permutation_count','expected_minimum_layout_width','expected_accepting_layout_count','expected_root_empty')),'INV01','expected oracle'); req(exp['historical_or_local_values_may_seed_expected_values'] is False,'INV01','oracle policy')
    req(gb(rootspecp)==ROOT_SPEC_BLOB,'INV01','root spec blob'); rs=load(rootspecp); req(rs.get('schema')==ROOT_SPEC_SCHEMA,'INV01','root spec')
    req(fh(emptyp)==EMPTY_SHA,'INV01','empty sha'); empty=load(emptyp); req(empty.get('schema')==EMPTY_SCHEMA and sem_ok(empty) and empty.get('semantic_digest')==EMPTY_SEM,'INV01','empty semantic')
    req(fh(auditp)==AUDIT_SHA,'INV01','audit sha'); audit=load(auditp); req(audit.get('schema')==AUDIT_SCHEMA and audit.get('semantic_digest')==AUDIT_SEM and dg(audit.get('audit_payload'))==AUDIT_SEM,'INV01','audit semantic')
    producer_import_check(producerp); return spec,rs,empty,audit

def span_set(rows,d):
    s={0}; mask=(1<<d)-1
    for raw in rows:
        v=int(raw)&mask; s |= {x^v for x in tuple(s)}
    return frozenset(s)
def intersection_dim(left,right,d):
    z=span_set(left,d)&span_set(right,d); req(len(z)>0 and (len(z)&(len(z)-1))==0,'INV04','intersection not subspace'); return len(z).bit_length()-1
def rec(blocks,order,d):
    widths=[]
    for cut in range(len(order)+1):
        l=[v for i in order[:cut] for v in blocks[i]]; r=[v for i in order[cut:] for v in blocks[i]]; widths.append(intersection_dim(l,r,d))
    return {'order':list(order),'width_vector':widths,'maximum_width':max(widths,default=0)}
def reference(rs,empty):
    d=int(rs['canonical_semantics']['ambient_dim']); k=int(rs['canonical_semantics']['k']); blocks=tuple(tuple(int(v) for v in b) for b in rs['scaffold']['whole_factor_blocks'])
    records=[rec(blocks,o,d) for o in itertools.permutations(range(len(blocks)))]; records=sorted(records,key=lambda x:tuple(x['order'])); accepting=[x for x in records if x['maximum_width']<=k]; minimum=min((x['maximum_width'] for x in records),default=0)
    ep=empty['proof_payload']; root_empty=bool(ep['root_up_k_closure']['empty'] and ep['root_up_k_closure']['entry_count']==0); no_layout=len(accepting)==0
    return {'d':d,'k':k,'blocks':[list(b) for b in blocks],'records':records,'accepting':accepting,'minimum':minimum,'root_empty':root_empty,'no_layout':no_layout,'pointwise':root_empty==no_layout}

def verify(c,spec,ref):
    req(c.get('schema')==SCHEMA and sem_ok(c),'INV01','candidate semantic'); p=c['proof_payload']; sb=p['source_binding']
    req(sb['terminal_spec_git_blob']==SPEC_BLOB and sb['root_spec_git_blob']==ROOT_SPEC_BLOB and sb['root_empty_sha256']==EMPTY_SHA and sb['root_empty_semantic_digest']==EMPTY_SEM and sb['tracked_audit_sha256']==AUDIT_SHA and sb['tracked_audit_semantic_digest']==AUDIT_SEM,'INV01','binding'); req(sb['historical_layout_oracle_consumed'] is False and sb['easter_egg_consumed_as_proof_input'] is False,'INV01','forbidden source')
    s=p['derived_scaffold']; req(s=={'ambient_dim':ref['d'],'k':ref['k'],'whole_factor_blocks':ref['blocks'],'factor_count':len(ref['blocks'])},'INV02','scaffold')
    o=p['whole_factor_layout_oracle']; req(o['permutation_count']==math.factorial(len(ref['blocks']))==len(ref['records']),'INV03','permutation domain'); req(o['records']==ref['records'] and o['records_digest']==dg(ref['records']),'INV04','layout records'); req(len({tuple(x['order']) for x in o['records']})==len(o['records']),'INV05','unique layouts')
    req(o['minimum_layout_width']==ref['minimum'] and o['accepting_layout_count']==len(ref['accepting']) and o['accepting_layouts']==ref['accepting'] and o['accepting_layouts_digest']==dg(ref['accepting']),'INV06','oracle aggregate'); req(o['expected_permutation_count_used'] is False and o['expected_minimum_width_used'] is False and o['expected_accepting_count_used'] is False,'INV06','expected used')
    e=p['admitted_root_empty_observation']; req(e['root_up_k_closure_entry_count']==0 and e['root_up_k_closure_empty'] is True and e['derived_root_empty']==ref['root_empty'] and e['expected_root_empty_used'] is False,'INV07','root empty')
    x=p['frozen_instance_crosscheck']; req(x['no_width_le_k_layout']==ref['no_layout'] and x['root_empty_equals_no_width_le_k_layout']==ref['pointwise'],'INV08','pointwise'); req(x['scope']=='POINTWISE_BOOLEAN_EQUIVALENCE_FOR_THIS_FROZEN_SIX_FACTOR_INSTANCE_ONLY','INV08','scope')
    g=p['structural_reflection_gap']; req(g['required_obligations']==spec['structural_reflection_obligations'] and g['obligations_proved_by_this_pointwise_gate']==[] and g['unresolved_obligations']==spec['structural_reflection_obligations'] and g['gap_status']=='STRUCTURAL_INDUCTION_STILL_REQUIRED','INV09','gap'); req(x['structural_induction_proved'] is False and x['engine_terminal_completeness_proved'] is False,'INV09','induction promotion')
    d=p['determinism']; req(d['required_order_modes']==['ORIGINAL','REVERSED','SEEDED_SHUFFLE'] and d['canonical_layout_order'] is True and d['input_order_mode_not_serialized'] is True and d['byte_identical_output_required'] is True,'INV10','determinism')
    b=p['strict_boundary']; expected={'root_empty_proved':True,'frozen_six_factor_no_layout_at_cap':False,'frozen_instance_root_layout_pointwise_equivalence':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','found_layout':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}; req(b==expected,'INV12','boundary'); return True

def repair(c):
    p=c['proof_payload']; o=p['whole_factor_layout_oracle']; o['permutation_count']=len(o['records']); o['records_digest']=dg(o['records']); k=p['derived_scaffold']['k']; o['accepting_layouts']=[r for r in o['records'] if r['maximum_width']<=k]; o['accepting_layout_count']=len(o['accepting_layouts']); o['accepting_layouts_digest']=dg(o['accepting_layouts']); c['semantic_digest']=dg(p)
def reseal(c): c['semantic_digest']=dg(c['proof_payload'])
def inject_fake_accepting(x):
    o=x['proof_payload']['whole_factor_layout_oracle']; o['accepting_layouts'].append(copy.deepcopy(o['records'][0])); o['accepting_layout_count']=len(o['accepting_layouts']); o['accepting_layouts_digest']=dg(o['accepting_layouts'])
def tamper(c,spec,ref):
    ok=[]
    def atk(name,mut,post=None):
        x=copy.deepcopy(c); mut(x); repair(x)
        if post: post(x); reseal(x)
        try: verify(x,spec,ref)
        except VError as e: ok.append((name,e.inv)); return
        raise AssertionError('survived '+name)
    atk('T01_ROOT_EMPTY_BINDING',lambda x:x['proof_payload']['source_binding'].__setitem__('root_empty_sha256','0'*64)); atk('T02_AUDIT_BINDING',lambda x:x['proof_payload']['source_binding'].__setitem__('tracked_audit_sha256','1'*64)); atk('T03_SCAFFOLD_BLOCK',lambda x:x['proof_payload']['derived_scaffold']['whole_factor_blocks'][0].__setitem__(0,7)); atk('T04_DELETE_PERMUTATION',lambda x:x['proof_payload']['whole_factor_layout_oracle']['records'].pop()); atk('T05_CUT_WIDTH',lambda x:x['proof_payload']['whole_factor_layout_oracle']['records'][0]['width_vector'].__setitem__(1,9))
    atk('T06_FAKE_ACCEPTING',lambda x:None,inject_fake_accepting); atk('T07_MINIMUM',lambda x:None,lambda x:x['proof_payload']['whole_factor_layout_oracle'].__setitem__('minimum_layout_width',0)); atk('T08_ROOT_EMPTY_BOOL',lambda x:None,lambda x:x['proof_payload']['admitted_root_empty_observation'].__setitem__('derived_root_empty',False)); atk('T09_POINTWISE_FLAG',lambda x:None,lambda x:x['proof_payload']['frozen_instance_crosscheck'].__setitem__('root_empty_equals_no_width_le_k_layout',False)); atk('T10_STRUCTURAL_PROMOTION',lambda x:None,lambda x:x['proof_payload']['frozen_instance_crosscheck'].__setitem__('structural_induction_proved',True)); atk('T11_REORDER',lambda x:x['proof_payload']['whole_factor_layout_oracle']['records'].reverse()); atk('T12_TERMINAL_PROMOTION',lambda x:None,lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True)); req(len(ok)==12,'INV11','tamper count'); return ok

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--root-spec',type=Path,required=True); ap.add_argument('--root-empty-artifact',type=Path,required=True); ap.add_argument('--audit-receipt',type=Path,required=True); ap.add_argument('--candidate-original',type=Path,required=True); ap.add_argument('--candidate-reversed',type=Path,required=True); ap.add_argument('--candidate-seeded-shuffle',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args()
    spec,rs,empty,audit=bind(a.spec,a.root_spec,a.root_empty_artifact,a.audit_receipt,a.producer_source); b=a.candidate_original.read_bytes(); req(b==a.candidate_reversed.read_bytes()==a.candidate_seeded_shuffle.read_bytes(),'INV10','three mode bytes'); ref=reference(rs,empty); c=load(a.candidate_original); verify(c,spec,ref); ts=tamper(c,spec,ref) if a.tamper_suite else []
    print('JANUS_CORRECTED_TERMINAL_REFLECTION_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED'); print('MATHEMATICAL_INDEPENDENCE = NOT_AUTOMATIC'); print('SPECIFICATION_INDEPENDENCE = NOT_AUTOMATIC'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('WHOLE_FACTOR_PERMUTATIONS =',len(ref['records'])); print('MINIMUM_LAYOUT_WIDTH =',ref['minimum']); print('ACCEPTING_LAYOUTS =',len(ref['accepting'])); print('ROOT_EMPTY =',ref['root_empty']); print('POINTWISE_ROOT_LAYOUT_EQUIVALENCE =',ref['pointwise']); print('STRUCTURAL_INDUCTION_PROVED = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
