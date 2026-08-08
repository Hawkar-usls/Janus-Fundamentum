from __future__ import annotations
import argparse, ast, copy, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.general_b2_semantic_language_preservation_candidate.v1'
SPEC_SCHEMA='janus.c049_1.general_b2_semantic_language_preservation_spec.v1'
class VError(Exception):
    def __init__(self,inv,msg): super().__init__(f'{inv}:{msg}'); self.inv=inv
def req(x,inv,msg):
    if not x: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def txt(p): return Path(p).read_text()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def imports(p):
    t=ast.parse(Path(p).read_text()); out=[]
    for n in ast.walk(t):
        if isinstance(n,ast.Import): out.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): out.append(n.module or '')
    return out
def fn(tree,name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name: return ast.unparse(n)
    raise VError('INV03','missing '+name)

def abstract_preorder_controls():
    preorder_count=0; cofinal_checks=0; idempotence_checks=0
    for n in range(1,5):
        pairs=[(i,j) for i in range(n) for j in range(n)]
        for mask in range(1<<(n*n)):
            rel={(i,j) for bit,(i,j) in enumerate(pairs) if (mask>>bit)&1}
            if any((i,i) not in rel for i in range(n)): continue
            trans=True
            for i in range(n):
                for j in range(n):
                    if (i,j) not in rel: continue
                    for k in range(n):
                        if (j,k) in rel and (i,k) not in rel:
                            trans=False; break
                    if not trans: break
                if not trans: break
            if not trans: continue
            preorder_count+=1
            def up(S): return {t for t in range(n) if any((s,t) in rel for s in S)}
            for rmask in range(1<<n):
                R={i for i in range(n) if (rmask>>i)&1}
                U=up(R); req(up(U)==U,'INV07','abstract idempotence'); idempotence_checks+=1
                for mmask in range(1<<n):
                    M={i for i in range(n) if (mmask>>i)&1}
                    if not M.issubset(R): continue
                    cofinal=all(any((m,r) in rel for m in M) for r in R)
                    if not cofinal: continue
                    req(up(M)==U,'INV04','abstract cofinal equality'); cofinal_checks+=1
    req(preorder_count>0 and cofinal_checks>0 and idempotence_checks>0,'INV05','controls empty')
    return {'preorders':preorder_count,'cofinal_equalities':cofinal_checks,'idempotence_equalities':idempotence_checks}

def derive(spec,a):
    src=spec['source_bindings']
    for key,path in {'b1_core':a.b1_core,'b2_core':a.b2_core,'b2_doc':a.b2_doc}.items(): req(gb(path)==src[key]['git_blob'],'INV01',key)
    o5=load(a.o5_audit); q=src['o5_admission']
    req(gb(a.o5_audit)==q['audit_git_blob'],'INV01','o5 audit blob')
    req(o5['semantic_digest']==q['audit_semantic_digest'] and dg(o5['audit_payload'])==q['audit_semantic_digest'],'INV01','o5 audit semantic')
    pub=spec['published_source']; th=spec['derived_theorems']; ceiling=spec['interpretation_ceiling']
    req(pub['lattice_characterization'].startswith('Lemma 3.5'),'INV02','lemma3.5')
    req(pub['preorder_transitivity']=='Lemma 3.6: preccurlyeq is transitive.','INV02','lemma3.6')
    req(pub['compactification_equivalence']=='Corollary 3.8: tau(Gamma) is preorder-equivalent to Gamma.','INV02','cor3.8')
    req('some Delta in R' in pub['up_k_definition'] and 'width<=k' in pub['up_k_definition'],'INV02','up_k')
    req(th['cofinal_minimization']['preconditions']==['M SUBSET R','FOR_EVERY Delta IN R EXISTS Gamma IN M WITH Gamma preccurlyeq Delta','preccurlyeq IS TRANSITIVE'],'INV04','cofinal premises')
    req(th['up_k_idempotence']['conclusion']=='up_k(up_k(R,B),B)=up_k(R,B)','INV07','idempotence theorem')

    b1=txt(a.b1_core); b2=txt(a.b2_core); b2d=txt(a.b2_doc); tree=ast.parse(b2)
    pre=fn(tree,'extension_preorder_witness'); mini=fn(tree,'minimize_generators'); up=fn(tree,'up_k_closure')
    req('(i - 1, j - 1)' in pre and '(i - 1, j)' in pre and '(i, j - 1)' in pre,'INV03','preorder path')
    req('unique_map' in mini and 'retained_indices' in mini,'INV03','dedup/minimize')
    req('candidates = [i for i in retained_indices if (i, j) in relation]' in mini,'INV03','direct predecessor')
    req("'retained': encode(ordered[i])" in mini and "relation[i, j]['path']" in mini,'INV03','removal receipt')
    req('retained, removals = minimize_generators' in up and 'for source in retained' in up,'INV03','up uses retained')
    req('def compactify' in b1,'INV02','B1')
    req('up_k(original generators) = up_k(retained generators)' in b2d,'INV03','B2 documented equality')
    req(ceiling['source_family_requirement'].startswith('R must already be semantically complete'),'INV08','source family premise')
    sb=spec['strict_boundary']
    req(sb['retained_generator_minimization_creates_new_realizability'] is False and sb['upstream_o2_o5_caller_preconditions_automatically_established'] is False,'INV08','ceiling')
    req(sb['o1_leaf_language_base_case'] is True and sb['o2_expand_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION' and sb['o3_join_interleaving_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION' and sb['o4_shrink_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_BOUND_SUBSPACE_CONTAINMENT' and sb['o5_width_filter_soundness_and_reflection']=='TRUE_CONDITIONALLY_ON_COMPLETE_COMPOSITION_SOURCE_FAMILY_AND_BOUND_O2_O4_CALLER_PRECONDITIONS','INV09','prior')

    symbolic={'cofinal_forward_chain':'Gamma_M preccurlyeq Delta_R preccurlyeq Theta => Gamma_M preccurlyeq Theta','cofinal_reverse_subset':'M SUBSET R => every M witness is an R witness','duplicate_multiplicity_irrelevant_under_existential_membership':True,'preorder_reflexive_from_identity_extensions':True,'preorder_transitive_bound_to_lemma_3_6':True,'up_k_idempotence_forward_by_transitivity':True,'up_k_idempotence_reverse_by_reflexivity':True}
    checks={'o5_admission_bound':True,'published_lemma_3_5_bound':True,'published_lemma_3_6_bound':True,'published_corollary_3_8_bound':True,'local_extension_preorder_matches':True,'local_duplicate_dedup_present':True,'local_retained_subset_constructed_from_original':True,'direct_retained_predecessor_for_every_removal':True,'local_up_k_uses_retained_sources':True,'source_family_must_be_semantically_complete_and_cap_filtered':True,'minimization_does_not_create_realizability':True,'upstream_premises_not_auto_established':True}
    expected={
      'gate':spec['gate'],'status':'CANDIDATE_PENDING_ADMISSION','published_dependency':pub,'derived_theorems':th,'symbolic_preservation_proof':symbolic,'source_checks':checks,
      'b2_preservation_contract':{'duplicate_deletion_preserves_up_k':True,'direct_predecessor_minimization_preserves_up_k':True,'up_k_idempotent':True,'semantic_language_preserved_if_source_family_semantically_complete':True,'semantic_language_reflected_if_source_family_semantically_complete':True,'retained_generator_minimization_creates_new_realizability':False,'upstream_o2_o5_caller_preconditions_automatically_established':False,'concrete_fixture_oracle_used':False},
      'prior_obligations':{'o1_leaf_language_base_case':True,'o2_expand_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION','o3_join_interleaving_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION','o4_shrink_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_SUBSPACE_CONTAINMENT','o5_width_filter_soundness_and_reflection':'TRUE_CONDITIONALLY_ON_COMPLETE_COMPOSITION_SOURCE_FAMILY_AND_BOUND_O2_O4_CALLER_PRECONDITIONS'},
      'candidate_promotion':{'o6_b2_semantic_language_preservation_and_reflection':False,'general_b2_semantic_language_preservation_receipt':False,'receipt_wording_if_admitted':spec['admission_boundary']['receipt_wording']},
      'general_semantic_theorems_established':5,'remaining_general_semantic_theorems':2,'first_required_next_receipt':'GENERAL_B2_SEMANTIC_LANGUAGE_PRESERVATION_RECEIPT','strict_boundary':sb,
    }
    return expected

def verify(c,spec,a,run_controls=True):
    req(c.get('schema')==SCHEMA,'INV01','schema'); req(c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest'),'INV01','digest')
    exp=derive(spec,a); req(c['proof_payload']==exp,'INV01','derived candidate'); p=c['proof_payload']
    req(len(p['source_checks'])==12 and all(p['source_checks'].values()),'INV01','checks')
    req(p['b2_preservation_contract']['duplicate_deletion_preserves_up_k'] is True,'INV06','duplicates')
    req(p['b2_preservation_contract']['direct_predecessor_minimization_preserves_up_k'] is True,'INV04','minimization')
    req(p['b2_preservation_contract']['up_k_idempotent'] is True,'INV07','idempotence')
    req(p['b2_preservation_contract']['retained_generator_minimization_creates_new_realizability'] is False,'INV08','realizability')
    req(p['b2_preservation_contract']['upstream_o2_o5_caller_preconditions_automatically_established'] is False,'INV08','premises')
    if run_controls: abstract_preorder_controls()
    b=p['strict_boundary']; req(b['o6_b2_semantic_language_preservation_and_reflection'] is False and b['o7_empty_root_specialization_established'] is False,'INV12','obligations')
    req(b['structural_induction_proved'] is False and b['terminal_completeness_proved'] is False and b['global_engine_no_layout_at_cap']=='FORBIDDEN' and b['found_layout']=='FORBIDDEN' and b['formal_admission']=='BLOCKED' and b['next_gate']=='CLOSED' and b['p_vs_np']=='OPEN','INV12','boundary')

def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tampers(c,spec,a):
    ok=[]
    def atk(name,mut):
        x=copy.deepcopy(c); mut(x); seal(x)
        try: verify(x,spec,a,False)
        except VError as e: ok.append((name,e.inv)); return
        raise AssertionError('survived '+name)
    atk('T01_TRANSITIVITY',lambda x:x['proof_payload']['published_dependency'].__setitem__('preorder_transitivity','Lemma 3.6: preccurlyeq is not transitive.'))
    atk('T02_SUBSET',lambda x:x['proof_payload']['derived_theorems']['cofinal_minimization'].__setitem__('preconditions',['FOR_EVERY Delta IN R EXISTS Gamma IN M WITH Gamma preccurlyeq Delta','preccurlyeq IS TRANSITIVE']))
    atk('T03_COFINAL',lambda x:x['proof_payload']['b2_preservation_contract'].__setitem__('direct_predecessor_minimization_preserves_up_k',False))
    atk('T04_EXISTENTIAL',lambda x:x['proof_payload']['published_dependency'].__setitem__('up_k_definition','up_k requires every Delta in R to dominate Gamma.'))
    atk('T05_DUPLICATE',lambda x:x['proof_payload']['b2_preservation_contract'].__setitem__('duplicate_deletion_preserves_up_k',False))
    atk('T06_IDEMPOTENCE',lambda x:x['proof_payload']['b2_preservation_contract'].__setitem__('up_k_idempotent',False))
    atk('T07_DIRECT_WITNESS',lambda x:x['proof_payload']['source_checks'].__setitem__('direct_retained_predecessor_for_every_removal',False))
    atk('T08_REALIZABILITY',lambda x:x['proof_payload']['b2_preservation_contract'].__setitem__('retained_generator_minimization_creates_new_realizability',True))
    atk('T09_AUTO_PREMISES',lambda x:x['proof_payload']['b2_preservation_contract'].__setitem__('upstream_o2_o5_caller_preconditions_automatically_established',True))
    atk('T10_O7',lambda x:x['proof_payload']['strict_boundary'].__setitem__('o7_empty_root_specialization_established',True))
    atk('T11_TERMINAL',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True))
    atk('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    req(len(ok)==12,'INV11','tamper count'); return ok

def main():
    p=argparse.ArgumentParser()
    for f in ('spec','producer-source','o5-audit','b1-core','b2-core','b2-doc','candidate-original','candidate-reordered'): p.add_argument('--'+f,type=Path,required=True)
    p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args(); spec=load(a.spec)
    req(spec['schema']==SPEC_SCHEMA and spec['status']=='SPEC_FROZEN','INV01','spec')
    req(not any(x.endswith('janus_c049_1_b4_6_3_general_b2_semantic_language_preservation') for x in imports(a.producer_source)),'INV01','producer import')
    req(a.candidate_original.read_bytes()==a.candidate_reordered.read_bytes(),'INV10','byte identity')
    c=load(a.candidate_original); verify(c,spec,a,True); ctrls=abstract_preorder_controls(); ts=tampers(c,spec,a) if a.tamper_suite else []
    print('JANUS_GENERAL_B2_SEMANTIC_LANGUAGE_PRESERVATION_INDEPENDENT_VERIFIER = PASS')
    print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED')
    print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN')
    print('ABSTRACT_PREORDER_CONTROLS =',ctrls['preorders']); print('ABSTRACT_COFINAL_EQUALITIES =',ctrls['cofinal_equalities']); print('ABSTRACT_IDEMPOTENCE_EQUALITIES =',ctrls['idempotence_equalities'])
    print('COFINAL_MINIMIZATION_UP_K_EQUALITY = PASS_AS_DERIVED_CANDIDATE'); print('DUPLICATE_DELETION_UP_K_PRESERVATION = PASS_AS_DERIVED_CANDIDATE'); print('UP_K_IDEMPOTENCE = PASS_AS_DERIVED_CANDIDATE')
    print('RETAINED_GENERATOR_MINIMIZATION_CREATES_NEW_REALIZABILITY = FALSE'); print('UPSTREAM_O2_O5_CALLER_PRECONDITIONS_AUTOMATICALLY_ESTABLISHED = FALSE')
    print('GENERAL_SEMANTIC_THEOREMS_ESTABLISHED = 5'); print('REMAINING_GENERAL_SEMANTIC_THEOREMS = 2'); print('FIRST_REQUIRED_NEXT_RECEIPT = GENERAL_B2_SEMANTIC_LANGUAGE_PRESERVATION_RECEIPT')
    print('STRUCTURAL_INDUCTION_PROVED = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
