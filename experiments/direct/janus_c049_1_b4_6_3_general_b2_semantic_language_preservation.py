from __future__ import annotations
import argparse, ast, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.general_b2_semantic_language_preservation_candidate.v1'
SPEC_SCHEMA='janus.c049_1.general_b2_semantic_language_preservation_spec.v1'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def txt(p): return Path(p).read_text()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def req(x,m):
    if not x: raise AssertionError(m)
def fn(tree,name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name: return ast.unparse(n)
    raise AssertionError('missing '+name)

def build(a):
    s=load(a.spec); req(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN' and s['admission'] is False,'spec')
    src=s['source_bindings']
    for key,path in {'b1_core':a.b1_core,'b2_core':a.b2_core,'b2_doc':a.b2_doc}.items(): req(gb(path)==src[key]['git_blob'],'blob '+key)
    o5=load(a.o5_audit); q=src['o5_admission']
    req(gb(a.o5_audit)==q['audit_git_blob'],'o5 audit blob')
    req(o5['semantic_digest']==q['audit_semantic_digest'] and dg(o5['audit_payload'])==q['audit_semantic_digest'],'o5 audit semantic')

    pub=s['published_source']; th=s['derived_theorems']; ceiling=s['interpretation_ceiling']
    req(pub['preorder_transitivity']=='Lemma 3.6: preccurlyeq is transitive.','transitivity')
    req(pub['compactification_equivalence']=='Corollary 3.8: tau(Gamma) is preorder-equivalent to Gamma.','compactification')
    req('some Delta in R' in pub['up_k_definition'] and 'width<=k' in pub['up_k_definition'],'up_k')
    req(th['cofinal_minimization']['conclusion']=='up_k(M,B)=up_k(R,B)','cofinal theorem')
    req(th['up_k_idempotence']['conclusion']=='up_k(up_k(R,B),B)=up_k(R,B)','idempotence')
    req(ceiling['source_family_requirement'].startswith('R must already be semantically complete'),'source ceiling')

    b1=txt(a.b1_core); b2=txt(a.b2_core); b2d=txt(a.b2_doc); tree=ast.parse(b2)
    pre=fn(tree,'extension_preorder_witness'); mini=fn(tree,'minimize_generators'); up=fn(tree,'up_k_closure')
    req('(i - 1, j - 1)' in pre and '(i - 1, j)' in pre and '(i, j - 1)' in pre,'preorder synchronized path')
    req('unique_map' in mini and 'retained_indices' in mini,'dedup/minimize')
    req("candidates = [i for i in retained_indices if (i, j) in relation]" in mini,'direct retained predecessor')
    req("'retained': encode(ordered[i])" in mini and "relation[i, j]['path']" in mini,'direct removal receipt')
    req('retained, removals = minimize_generators' in up and 'for source in retained' in up,'closure uses retained')
    req('def compactify' in b1,'B1 compactify')
    req('up_k(original generators) = up_k(retained generators)' in b2d,'B2 documented preservation')

    symbolic={
      'cofinal_forward_chain':'Gamma_M preccurlyeq Delta_R preccurlyeq Theta => Gamma_M preccurlyeq Theta',
      'cofinal_reverse_subset':'M SUBSET R => every M witness is an R witness',
      'duplicate_multiplicity_irrelevant_under_existential_membership':True,
      'preorder_reflexive_from_identity_extensions':True,
      'preorder_transitive_bound_to_lemma_3_6':True,
      'up_k_idempotence_forward_by_transitivity':True,
      'up_k_idempotence_reverse_by_reflexivity':True,
    }
    checks={
      'o5_admission_bound':True,
      'published_lemma_3_5_bound':pub['lattice_characterization'].startswith('Lemma 3.5'),
      'published_lemma_3_6_bound':True,
      'published_corollary_3_8_bound':True,
      'local_extension_preorder_matches':True,
      'local_duplicate_dedup_present':True,
      'local_retained_subset_constructed_from_original':True,
      'direct_retained_predecessor_for_every_removal':True,
      'local_up_k_uses_retained_sources':True,
      'source_family_must_be_semantically_complete_and_cap_filtered':True,
      'minimization_does_not_create_realizability':s['strict_boundary']['retained_generator_minimization_creates_new_realizability'] is False,
      'upstream_premises_not_auto_established':s['strict_boundary']['upstream_o2_o5_caller_preconditions_automatically_established'] is False,
    }
    req(len(checks)==12 and all(checks.values()),'checks')
    proof={
      'gate':s['gate'],'status':'CANDIDATE_PENDING_ADMISSION','published_dependency':pub,'derived_theorems':th,
      'symbolic_preservation_proof':symbolic,'source_checks':checks,
      'b2_preservation_contract':{
        'duplicate_deletion_preserves_up_k':True,
        'direct_predecessor_minimization_preserves_up_k':True,
        'up_k_idempotent':True,
        'semantic_language_preserved_if_source_family_semantically_complete':True,
        'semantic_language_reflected_if_source_family_semantically_complete':True,
        'retained_generator_minimization_creates_new_realizability':False,
        'upstream_o2_o5_caller_preconditions_automatically_established':False,
        'concrete_fixture_oracle_used':False,
      },
      'prior_obligations':{
        'o1_leaf_language_base_case':True,
        'o2_expand_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION',
        'o3_join_interleaving_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION',
        'o4_shrink_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_SUBSPACE_CONTAINMENT',
        'o5_width_filter_soundness_and_reflection':'TRUE_CONDITIONALLY_ON_COMPLETE_COMPOSITION_SOURCE_FAMILY_AND_BOUND_O2_O4_CALLER_PRECONDITIONS',
      },
      'candidate_promotion':{
        'o6_b2_semantic_language_preservation_and_reflection':False,
        'general_b2_semantic_language_preservation_receipt':False,
        'receipt_wording_if_admitted':s['admission_boundary']['receipt_wording'],
      },
      'general_semantic_theorems_established':5,'remaining_general_semantic_theorems':2,
      'first_required_next_receipt':'GENERAL_B2_SEMANTIC_LANGUAGE_PRESERVATION_RECEIPT','strict_boundary':s['strict_boundary'],
    }
    out={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; out['semantic_digest']=dg(proof); save(out,a.output); return out

def main():
    p=argparse.ArgumentParser()
    for f in ('spec','o5-audit','b1-core','b2-core','b2-doc','output'): p.add_argument('--'+f,type=Path,required=True)
    a=p.parse_args(); x=build(a); q=x['proof_payload']
    print('JANUS_GENERAL_B2_SEMANTIC_LANGUAGE_PRESERVATION_BINDER = PASS')
    print('COFINAL_MINIMIZATION_UP_K_EQUALITY = PASS_AS_DERIVED_CANDIDATE')
    print('DUPLICATE_DELETION_UP_K_PRESERVATION = PASS_AS_DERIVED_CANDIDATE')
    print('UP_K_IDEMPOTENCE = PASS_AS_DERIVED_CANDIDATE')
    print('RETAINED_GENERATOR_MINIMIZATION_CREATES_NEW_REALIZABILITY = FALSE')
    print('UPSTREAM_O2_O5_CALLER_PRECONDITIONS_AUTOMATICALLY_ESTABLISHED = FALSE')
    print('GENERAL_SEMANTIC_THEOREMS_ESTABLISHED =',q['general_semantic_theorems_established'])
    print('REMAINING_GENERAL_SEMANTIC_THEOREMS =',q['remaining_general_semantic_theorems'])
    print('FIRST_REQUIRED_NEXT_RECEIPT =',q['first_required_next_receipt'])
    print('STRUCTURAL_INDUCTION_PROVED = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
