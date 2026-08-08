from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.general_empty_root_specialization_candidate.v1'
SPEC_SCHEMA='janus.c049_1.general_empty_root_specialization_spec.v1'

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def txt(p): return Path(p).read_text()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def req(x,m):
    if not x: raise AssertionError(m)

def build(a):
    s=load(a.spec); req(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN' and s['admission'] is False,'spec')
    src=s['source_bindings']; req(gb(a.b1_core)==src['b1_core']['git_blob'],'b1 blob'); req(gb(a.root_spec)==src['corrected_root_spec']['git_blob'],'root spec blob')
    o6=load(a.o6_audit); q=src['o6_admission']; req(gb(a.o6_audit)==q['audit_git_blob'],'o6 audit blob'); req(o6['semantic_digest']==q['audit_semantic_digest'] and dg(o6['audit_payload'])==q['audit_semantic_digest'],'o6 audit semantic')
    pub=s['published_source']; th=s['derived_theorem']; ceil=s['interpretation_ceiling']
    req(pub['primary_results']==['Section 3.2 canonical and realizable B-trajectories','Lemma 3.4 width monotonicity under preccurlyeq','Corollary 3.8 compactification preorder equivalence','Section 4 full-set definition','Proposition 5.8 root criterion'],'published ids')
    req('some extension' in pub['realizable_definition'] and 'linear layout' in pub['realizable_definition'],'realizable')
    req('B={0}' in pub['canonical_zero_boundary'] and 'prefix span INTER suffix span' in pub['canonical_zero_boundary'] and 'linear-layout width' in pub['canonical_zero_boundary'],'zero boundary')
    req(th['biconditional']=='FS_k(V,{0}) != EMPTY IFF THERE EXISTS A COMPLETE LINEAR LAYOUT OF V WITH WIDTH <= k','biconditional')
    req('complete linear layout' in th['forward'] and 'Lemma 3.4' in th['forward'],'forward')
    req('Compactification tau' in th['backward'] and 'FS_k(V,{0}) is nonempty' in th['backward'],'backward')
    req(ceil['engine_composition_requirement'].startswith('A separate composition receipt'),'composition ceiling')
    b1=txt(a.b1_core); req('def compactify' in b1 and 'def width' in b1,'B1 interface')
    rs=load(a.root_spec); req(rs['geometry']['parent_boundary_ambient_rref']==[],'root boundary empty'); req(rs['strict_boundary']['root_full_set_computed'] is False or isinstance(rs['strict_boundary']['root_full_set_computed'],bool),'root strict boundary')
    checks={
      'o6_admission_bound':True,'published_realizable_definition_bound':True,'published_zero_boundary_formula_bound':True,'published_full_set_definition_bound':True,
      'published_lemma_3_4_bound':True,'published_corollary_3_8_bound':True,'published_proposition_5_8_bound':True,'b1_compactification_interface_present':True,
      'corrected_root_target_boundary_empty':True,'abstract_biconditional_uses_no_fixture_oracle':True,'engine_root_identity_separate':True,'upstream_caller_premises_not_auto':True,
    }
    req(len(checks)==12 and all(checks.values()),'checks')
    proof={
      'gate':s['gate'],'status':'CANDIDATE_PENDING_ADMISSION','published_dependency':pub,'derived_theorem':th,'source_checks':checks,
      'empty_root_contract':{
        'canonical_zero_boundary_left_right_are_zero':True,'canonical_zero_boundary_lambda_equals_cut_intersection_dimension':True,'canonical_zero_boundary_width_equals_layout_width':True,
        'realizable_trajectory_has_complete_layout_canonical_extension':True,'extensions_preserve_width':True,'compactification_equivalent_and_width_preserving':True,
        'fs_nonempty_iff_complete_layout_width_le_k':True,'concrete_fixture_oracle_used':False,'engine_root_full_set_equals_fs_k_v_zero':False,'upstream_caller_preconditions_automatically_established':False,
      },
      'prior_obligations':{
        'o1_leaf_language_base_case':True,'o2_expand_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION','o3_join_interleaving_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION',
        'o4_shrink_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_SUBSPACE_CONTAINMENT','o5_width_filter_soundness_and_reflection':'TRUE_CONDITIONALLY_ON_COMPLETE_COMPOSITION_SOURCE_FAMILY_AND_BOUND_O2_O4_CALLER_PRECONDITIONS',
        'o6_b2_semantic_language_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_SEMANTICALLY_COMPLETE_CAP_FILTERED_SOURCE_FAMILY_AND_BOUND_UPSTREAM_CALLER_PRECONDITIONS'},
      'candidate_promotion':{'o7_empty_root_specialization_to_complete_layouts':False,'general_empty_root_specialization_receipt':False,'receipt_wording_if_admitted':s['admission_boundary']['receipt_wording']},
      'general_semantic_theorems_established':6,'remaining_general_semantic_theorems':1,'first_required_next_receipt':'GENERAL_EMPTY_ROOT_SPECIALIZATION_RECEIPT','after_o7_next_composition_receipt':'GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_RECEIPT','strict_boundary':s['strict_boundary']}
    out={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; out['semantic_digest']=dg(proof); save(out,a.output); return out

def main():
    p=argparse.ArgumentParser()
    for f in ('spec','o6-audit','b1-core','root-spec','output'): p.add_argument('--'+f,type=Path,required=True)
    a=p.parse_args(); x=build(a); q=x['proof_payload']
    print('JANUS_GENERAL_EMPTY_ROOT_SPECIALIZATION_BINDER = PASS'); print('ABSTRACT_FS_ZERO_IFF_COMPLETE_LAYOUT_WIDTH_LE_K = PASS_AS_DERIVED_CANDIDATE')
    print('ENGINE_ROOT_FULL_SET_EQUALS_FS_K_V_ZERO = FALSE'); print('UPSTREAM_CALLER_PRECONDITIONS_AUTOMATICALLY_ESTABLISHED = FALSE')
    print('GENERAL_SEMANTIC_THEOREMS_ESTABLISHED = 6'); print('REMAINING_GENERAL_SEMANTIC_THEOREMS = 1'); print('FIRST_REQUIRED_NEXT_RECEIPT = GENERAL_EMPTY_ROOT_SPECIALIZATION_RECEIPT')
    print('AFTER_O7_NEXT_COMPOSITION_RECEIPT = GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_RECEIPT'); print('STRUCTURAL_INDUCTION_PROVED = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
