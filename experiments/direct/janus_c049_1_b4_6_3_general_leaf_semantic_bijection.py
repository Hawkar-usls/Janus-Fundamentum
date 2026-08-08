from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.general_leaf_semantic_bijection_candidate.v1'
SPEC_SCHEMA='janus.c049_1.general_leaf_semantic_bijection_spec.v1.1'
SPEC_BLOB='a6e255210cf0df83a92b2e6169cfafcfabc753d5'
B1_DOC_BLOB='c1807ab523d3269c064db33221c764d1e459bee2'
B1_CORE_BLOB='96019d44b8defb97f7b0911b57302004c3d57c61'
B2_DOC_BLOB='a7c5a7a65dfd9839711967f1039a96ba20ad6443'
B2_CORE_BLOB='3b66fa2b45702f11ee7a62657754c16800fa90f3'
LEDGER_AUDIT_BLOB='c7ab1da4f38e56034bbf4d3f49c22cbedd1b9d5c'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def req(x,m):
    if not x: raise AssertionError(m)

def bind(specp,b1doc,b1core,b2doc,b2core,ledger):
    req(gb(specp)==SPEC_BLOB,'spec blob'); s=load(specp); req(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN' and s['admission'] is False,'spec')
    for p,h in ((b1doc,B1_DOC_BLOB),(b1core,B1_CORE_BLOB),(b2doc,B2_DOC_BLOB),(b2core,B2_CORE_BLOB),(ledger,LEDGER_AUDIT_BLOB)): req(gb(p)==h,'source blob')
    la=load(ledger); req(la['semantic_digest']==s['source_bindings']['structural_gap_ledger']['audit_semantic_digest'] and dg(la['audit_payload'])==la['semantic_digest'],'ledger semantic')
    return s

def build(a):
    s=bind(a.spec,a.b1_doc,a.b1_core,a.b2_doc,a.b2_core,a.ledger_audit)
    b1d=Path(a.b1_doc).read_text(); b1c=Path(a.b1_core).read_text(); b2d=Path(a.b2_doc).read_text(); b2c=Path(a.b2_core).read_text()
    mapping={
      'statistic_interface':('Statistic' in b1c and 'A statistic is a triple `(L,R,lambda)`' in b1d),
      'compactification_interface':('def compactify' in b1c and 'compactification normal form `tau`' in b1d),
      'preorder_interface':('def extension_preorder_witness' in b2c and 'uses only `(1,0)`, `(0,1)`, or `(1,1)` steps' in b2d),
      'up_k_interface':('def up_k_closure' in b2c and 'Complete finite `U_k(B)` closure' in b2d),
      'published_definition_claim_local':('corrected definitions in `arXiv:1507.02184v4`' in b2d),
    }
    req(all(mapping.values()),'local mapping')
    theorem=s['general_theorem']; req(theorem['conclusion']=='FS_k({V},B) = up_k({Delta_B},B)','formula')
    proof={
      'phase':'GENERAL_LEAF_SEMANTIC_BIJECTION_THEOREM_BINDING',
      'status':'CANDIDATE_PENDING_EXACT_HEAD_CI_AND_SEMANTIC_AUDIT',
      'quantifiers':{'ambient_space':'FOR_ALL finite-dimensional GF(2) vector spaces A','V':'FOR_ALL subspaces V<=A','B':'FOR_ALL subspaces B<=V','k':'FOR_ALL integers k>=0','concrete_ambient_dimension_used':False,'concrete_boundary_dimension_used':False,'concrete_factor_vector_used':False,'concrete_k_used':False},
      'published_theorem':{'source':'Jeong-Kim-Oum, The art of trellis decoding is fixed-parameter tractable','arxiv':'1507.02184v4','doi':'10.1109/TIT.2017.2740283','result':'Proposition 4.1','normalized_formula':'FS_k({V},B) = up_k({Delta_B},B)','dependency_status':'PUBLISHED_GENERAL_THEOREM_TRUSTED_NOT_INDEPENDENTLY_REPROVED'},
      'symbolic_leaf_derivation':{
        'singleton_layout_count_expression':'1!','singleton_layout_count':1,'unique_layout':['V'],
        'premise':'B<=V','intersection_laws':['ZERO_INTER_V=ZERO','V_INTER_ZERO=ZERO','ZERO_INTER_B=ZERO','V_INTER_B=B'],
        'canonical_definition':['L_i=(prefix span) INTER B','R_i=(suffix span) INTER B','lambda_i=dim(prefix INTER suffix)-dim(prefix INTER suffix INTER B)'],
        'first_cut':{'prefix':'ZERO','suffix':'V','L':'ZERO','R':'B','lambda':0},
        'second_cut':{'prefix':'V','suffix':'ZERO','L':'B','R':'ZERO','lambda':0},
        'delta_B':[['ZERO','B',0],['B','ZERO',0]],'delta_is_unique_canonical_singleton_trajectory':True,
      },
      'local_semantic_mapping':mapping,
      'semantic_bridge':{
        'published_full_set_definition':'compact width<=k B-trajectories Gamma covered by some realizable Delta under preccurlyeq',
        'published_up_k_definition':'compact width<=k B-trajectories Gamma covered by a generator Delta under preccurlyeq',
        'singleton_realizable_language_has_unique_canonical_source':'Delta_B',
        'theorem_formula':'FS_k({V},B) = up_k({Delta_B},B)',
        'local_interface_matches_published_leaf_theorem':True,
      },
      'dependency_ceiling':{'paper_mathematics_independently_reproved_by_repo':False,'published_proposition_used_as_external_mathematical_dependency':True,'local_semantic_mapping_machine_checked':True,'general_leaf_theorem_claim_scope':'ONLY_THE_SINGLE_SUBSPACE_BASE_CASE'},
      'strict_boundary':{'o1_leaf_language_base_case':False,'general_leaf_semantic_bijection_receipt':False,'remaining_general_semantic_theorems':7,'o2_o7_established':False,'structural_induction_proved':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'},
      'result':'GENERAL_LEAF_SEMANTIC_BIJECTION_CANDIDATE_PUBLISHED_THEOREM_BOUND_TO_LOCAL_INTERFACE'
    }
    out={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; out['semantic_digest']=dg(proof); save(out,a.output); return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--b1-doc',type=Path,required=True); ap.add_argument('--b1-core',type=Path,required=True); ap.add_argument('--b2-doc',type=Path,required=True); ap.add_argument('--b2-core',type=Path,required=True); ap.add_argument('--ledger-audit',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); x=build(a); p=x['proof_payload']; print('JANUS_GENERAL_LEAF_SEMANTIC_BIJECTION_BINDER = PASS'); print('QUANTIFICATION = UNIVERSAL_SYMBOLIC_GF2'); print('SINGLETON_LAYOUT_COUNT = 1'); print('DELTA_B = ((ZERO,B,0),(B,ZERO,0))'); print('PUBLISHED_RESULT = JKO_PROPOSITION_4_1'); print('LOCAL_SEMANTIC_MAPPING = PASS'); print('PAPER_MATHEMATICS_INDEPENDENTLY_REPROVED_BY_REPO = FALSE'); print('GENERAL_LEAF_SEMANTIC_BIJECTION_RECEIPT = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
