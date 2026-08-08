from __future__ import annotations
import argparse, hashlib, itertools, json, random
from pathlib import Path

SCHEMA='janus.c049_1.corrected_terminal_reflection_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_terminal_reflection_spec.v1'
ROOT_SPEC_SCHEMA='janus.c049_1.corrected_root_full_refinement_spec.v1'
EMPTY_SCHEMA='janus.c049_1.corrected_root_empty_up_k_candidate.v1'
AUDIT_SCHEMA='janus.c049_1.corrected_root_empty_up_k_independent_semantic_audit.v1'
SPEC_BLOB='88a229256c239f473d8766c2c43b77b84dd7ecbb'
ROOT_SPEC_BLOB='401c4856de261f6048d313ca62fa43598ea449e0'
EMPTY_SHA='b82fced138820d028898889eb59d059aaa023616ad774e6f31e0dc290fa492ab'
EMPTY_SEM='b811d3bf3abfd9c48b4454aaf3a9ec863d226092faa164fd8a0cf45bbe1e7ec0'
AUDIT_SHA='dbbbcaaee12dfcbaf073f0e11e182c0c530fe54acb0c05b2996c21a92fa68897'
AUDIT_SEM='e1b35822e6be0be2b4081c359f0be54692450e2e649d64cd5cff5332895308e0'
SEED=0xC049124
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
OBLIGATIONS=['LEAF_LANGUAGE_BASE_CASE','EXPAND_PRESERVATION_AND_REFLECTION','JOIN_INTERLEAVING_PRESERVATION_AND_REFLECTION','SHRINK_PRESERVATION_AND_REFLECTION','WIDTH_FILTER_SOUNDNESS_AND_REFLECTION','B2_DELETION_AND_UP_K_LANGUAGE_PRESERVATION_AND_REFLECTION','EMPTY_ROOT_SPECIALIZATION_TO_COMPLETE_LAYOUTS']

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def sem_ok(a): return a.get('semantic_digest_scope')=='proof_payload' and dg(a.get('proof_payload'))==a.get('semantic_digest')

def check_inputs(specp, rootspecp, emptyp, auditp):
    if gb(specp)!=SPEC_BLOB: raise AssertionError('terminal spec blob')
    spec=load(specp)
    if spec.get('schema')!=SPEC_SCHEMA or spec.get('status')!='SPEC_FROZEN' or spec.get('admission') is not False: raise AssertionError('terminal spec')
    exp=spec['expected_values_policy']
    if any(exp[k] is not None for k in ('expected_permutation_count','expected_minimum_layout_width','expected_accepting_layout_count','expected_root_empty')): raise AssertionError('expected oracle')
    if exp['historical_or_local_values_may_seed_expected_values'] is not False: raise AssertionError('oracle policy')
    if gb(rootspecp)!=ROOT_SPEC_BLOB: raise AssertionError('root spec blob')
    rs=load(rootspecp)
    if rs.get('schema')!=ROOT_SPEC_SCHEMA or rs.get('status')!='SPEC_FROZEN': raise AssertionError('root spec')
    if fh(emptyp)!=EMPTY_SHA: raise AssertionError('empty sha')
    empty=load(emptyp)
    if empty.get('schema')!=EMPTY_SCHEMA or not sem_ok(empty) or empty.get('semantic_digest')!=EMPTY_SEM: raise AssertionError('empty semantic')
    if fh(auditp)!=AUDIT_SHA: raise AssertionError('audit sha')
    audit=load(auditp)
    if audit.get('schema')!=AUDIT_SCHEMA or audit.get('semantic_digest')!=AUDIT_SEM or dg(audit.get('audit_payload'))!=AUDIT_SEM: raise AssertionError('audit semantic')
    return spec,rs,empty,audit

def rank(rows,d):
    basis=[0]*d
    for raw in rows:
        x=int(raw)&((1<<d)-1)
        while x:
            bit=x.bit_length()-1
            if basis[bit]: x ^= basis[bit]
            else:
                basis[bit]=x
                for j in range(bit):
                    if basis[j] and ((basis[bit]>>j)&1): basis[bit]^=basis[j]
                for j in range(bit+1,d):
                    if basis[j] and ((basis[j]>>bit)&1): basis[j]^=basis[bit]
                break
    return sum(bool(x) for x in basis)

def intersection_dim(left,right,d): return rank(left,d)+rank(right,d)-rank([*left,*right],d)
def layout_record(blocks,order,d):
    widths=[]
    for cut in range(len(order)+1):
        left=[v for idx in order[:cut] for v in blocks[idx]]
        right=[v for idx in order[cut:] for v in blocks[idx]]
        widths.append(intersection_dim(left,right,d))
    return {'order':list(order),'width_vector':widths,'maximum_width':max(widths,default=0)}
def permutation_order(n,mode):
    xs=list(itertools.permutations(range(n)))
    if mode=='REVERSED': xs.reverse()
    elif mode=='SEEDED_SHUFFLE': random.Random(SEED).shuffle(xs)
    return xs

def build(specp,rootspecp,emptyp,auditp,outp,mode):
    spec,rs,empty,audit=check_inputs(specp,rootspecp,emptyp,auditp)
    d=int(rs['canonical_semantics']['ambient_dim']); k=int(rs['canonical_semantics']['k'])
    blocks=tuple(tuple(int(v) for v in b) for b in rs['scaffold']['whole_factor_blocks'])
    records=[layout_record(blocks,o,d) for o in permutation_order(len(blocks),mode)]
    records=sorted(records,key=lambda r:tuple(r['order']))
    accepting=[r for r in records if r['maximum_width']<=k]
    minimum=min((r['maximum_width'] for r in records),default=0)
    ep=empty['proof_payload']; root_empty=bool(ep['root_up_k_closure']['empty'] and ep['root_up_k_closure']['entry_count']==0)
    no_layout=(len(accepting)==0); pointwise=(root_empty==no_layout)
    proof={'candidate_phase':'CORRECTED_TERMINAL_REFLECTION_POINTWISE_ATTACK','candidate_status':'PRODUCER_DERIVED_CANDIDATE','admitted':False,
      'source_binding':{'terminal_spec_git_blob':SPEC_BLOB,'root_spec_git_blob':ROOT_SPEC_BLOB,'root_empty_sha256':EMPTY_SHA,'root_empty_semantic_digest':EMPTY_SEM,'tracked_audit_sha256':AUDIT_SHA,'tracked_audit_semantic_digest':AUDIT_SEM,'historical_layout_oracle_consumed':False,'easter_egg_consumed_as_proof_input':False},
      'derived_scaffold':{'ambient_dim':d,'k':k,'whole_factor_blocks':[list(b) for b in blocks],'factor_count':len(blocks)},
      'whole_factor_layout_oracle':{'construction':'EXHAUSTIVE_ALL_PERMUTATIONS_WITH_GF2_RANK_IDENTITY','records':records,'permutation_count':len(records),'records_digest':dg(records),'minimum_layout_width':minimum,'accepting_layout_count':len(accepting),'accepting_layouts':accepting,'accepting_layouts_digest':dg(accepting),'expected_permutation_count_used':False,'expected_minimum_width_used':False,'expected_accepting_count_used':False},
      'admitted_root_empty_observation':{'root_up_k_closure_entry_count':int(ep['root_up_k_closure']['entry_count']),'root_up_k_closure_empty':bool(ep['root_up_k_closure']['empty']),'derived_root_empty':root_empty,'expected_root_empty_used':False},
      'frozen_instance_crosscheck':{'no_width_le_k_layout':no_layout,'root_empty_equals_no_width_le_k_layout':pointwise,'scope':'POINTWISE_BOOLEAN_EQUIVALENCE_FOR_THIS_FROZEN_SIX_FACTOR_INSTANCE_ONLY','structural_induction_proved':False,'engine_terminal_completeness_proved':False},
      'structural_reflection_gap':{'required_obligations':OBLIGATIONS,'obligations_proved_by_this_pointwise_gate':[],'unresolved_obligations':OBLIGATIONS,'gap_status':'STRUCTURAL_INDUCTION_STILL_REQUIRED'},
      'determinism':{'required_order_modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':'0xC049124','canonical_layout_order':True,'input_order_mode_not_serialized':True,'byte_identical_output_required':True},
      'strict_boundary':{'root_empty_proved':True,'frozen_six_factor_no_layout_at_cap':False,'frozen_instance_root_layout_pointwise_equivalence':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','found_layout':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'},
      'result':'FROZEN_INSTANCE_POINTWISE_CROSSCHECK_CANDIDATE_WITH_STRUCTURAL_REFLECTION_GAP_OPEN'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; art['semantic_digest']=dg(proof); save(art,outp); return art

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--root-spec',type=Path,required=True); ap.add_argument('--root-empty-artifact',type=Path,required=True); ap.add_argument('--audit-receipt',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL'); a=ap.parse_args()
    art=build(a.spec,a.root_spec,a.root_empty_artifact,a.audit_receipt,a.output,a.order_mode); p=art['proof_payload']; o=p['whole_factor_layout_oracle']; x=p['frozen_instance_crosscheck']
    print('JANUS_CORRECTED_TERMINAL_REFLECTION_PRODUCER = PASS'); print('WHOLE_FACTOR_PERMUTATIONS =',o['permutation_count']); print('MINIMUM_LAYOUT_WIDTH =',o['minimum_layout_width']); print('ACCEPTING_LAYOUTS =',o['accepting_layout_count']); print('ROOT_EMPTY =',p['admitted_root_empty_observation']['derived_root_empty']); print('FROZEN_INSTANCE_NO_WIDTH_LE_K_LAYOUT =',x['no_width_le_k_layout']); print('POINTWISE_ROOT_LAYOUT_EQUIVALENCE =',x['root_empty_equals_no_width_le_k_layout']); print('STRUCTURAL_INDUCTION_PROVED = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
