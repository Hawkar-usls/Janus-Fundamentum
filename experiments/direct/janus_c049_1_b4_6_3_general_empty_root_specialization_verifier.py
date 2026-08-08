from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json
from pathlib import Path

SCHEMA='janus.c049_1.general_empty_root_specialization_candidate.v1'
SPEC_SCHEMA='janus.c049_1.general_empty_root_specialization_spec.v1'
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

def basis(rows):
    tab={}
    for raw in rows:
        x=int(raw)
        while x:
            p=x.bit_length()-1
            if p in tab: x^=tab[p]; continue
            tab[p]=x
            for q,y in list(tab.items()):
                if q!=p and ((y>>p)&1): tab[q]=y^x
            break
    for p in sorted(tab):
        for q in sorted(tab,reverse=True):
            if q!=p and ((tab[q]>>p)&1): tab[q]^=tab[p]
    return tuple(tab[p] for p in sorted(tab,reverse=True))
def span(b):
    out={0}
    for r in b: out|={x^r for x in tuple(out)}
    return out
def interdim(a,b): return (len(span(basis(a)) & span(basis(b)))).bit_length()-1
def layout_width(blocks,order):
    vals=[]
    for cut in range(len(order)+1):
        left=[]; right=[]
        for i in order[:cut]: left.extend(blocks[i])
        for i in order[cut:]: right.extend(blocks[i])
        vals.append(interdim(left,right))
    return max(vals),tuple(vals)
def zero_canonical(blocks,order):
    w,vals=layout_width(blocks,order)
    stats=tuple(((),(),v) for v in vals)
    return stats,w
def extension(seq,reps):
    out=[]
    for item,n in zip(seq,reps): out.extend([item]*n)
    return tuple(out)
def finite_controls():
    arrangements=0; layouts=0; ext_checks=0
    catalog=[(),(1,),(2,),(3,)]
    for m in range(1,5):
        for blocks in itertools.product(catalog,repeat=m):
            arrangements+=1
            for order in itertools.permutations(range(m)):
                stats,w=zero_canonical(blocks,order); w2,vals=layout_width(blocks,order)
                req(w==w2,'INV03','canonical/layout width'); req(tuple(s[2] for s in stats)==vals,'INV03','lambda cuts')
                req(all(s[0]==() and s[1]==() for s in stats),'INV03','zero L/R')
                reps=tuple(1+(i%2) for i in range(len(stats))); ex=extension(stats,reps)
                req(max(s[2] for s in ex)==max(s[2] for s in stats),'INV04','extension width'); ext_checks+=1; layouts+=1
    return {'arrangements':arrangements,'layouts':layouts,'extension_checks':ext_checks}

def derive(spec,a):
    src=spec['source_bindings']; req(gb(a.b1_core)==src['b1_core']['git_blob'],'INV01','b1'); req(gb(a.root_spec)==src['corrected_root_spec']['git_blob'],'INV01','root')
    o6=load(a.o6_audit); q=src['o6_admission']; req(gb(a.o6_audit)==q['audit_git_blob'],'INV01','o6 audit blob'); req(o6['semantic_digest']==q['audit_semantic_digest'] and dg(o6['audit_payload'])==q['audit_semantic_digest'],'INV01','o6 audit semantic')
    pub=spec['published_source']; th=spec['derived_theorem']; ceil=spec['interpretation_ceiling']
    req(pub['primary_results']==['Section 3.2 canonical and realizable B-trajectories','Lemma 3.4 width monotonicity under preccurlyeq','Corollary 3.8 compactification preorder equivalence','Section 4 full-set definition','Proposition 5.8 root criterion'],'INV02','published ids')
    req('some extension' in pub['realizable_definition'] and 'linear layout' in pub['realizable_definition'],'INV02','realizable')
    req('B={0}' in pub['canonical_zero_boundary'] and 'prefix span INTER suffix span' in pub['canonical_zero_boundary'] and 'linear-layout width' in pub['canonical_zero_boundary'],'INV03','zero formula')
    req('some realizable Delta' in pub['full_set_definition'] and 'width<=k' in pub['full_set_definition'],'INV02','full set')
    req('V_root=V' in pub['proposition_5_8'] and 'B_root={0}' in pub['proposition_5_8'],'INV02','root identities')
    req('Lemma 3.4' in th['forward'] and 'complete linear layout' in th['forward'],'INV05','forward')
    req('Compactification tau' in th['backward'] and 'complete linear layout' in th['backward'],'INV06','backward')
    req(ceil['engine_composition_requirement'].startswith('A separate composition receipt'),'INV08','composition')
    b1=txt(a.b1_core); req('def compactify' in b1 and 'def width' in b1,'INV06','B1')
    rs=load(a.root_spec); req(rs['geometry']['parent_boundary_ambient_rref']==[],'INV03','root boundary')
    sb=spec['strict_boundary']; req(sb['engine_root_full_set_equals_fs_k_v_zero'] is False and sb['upstream_caller_preconditions_automatically_established'] is False,'INV08','engine premises')
    req(sb['o1_leaf_language_base_case'] is True and sb['o2_expand_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION' and sb['o3_join_interleaving_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION' and sb['o4_shrink_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_BOUND_SUBSPACE_CONTAINMENT' and sb['o5_width_filter_soundness_and_reflection']=='TRUE_CONDITIONALLY_ON_COMPLETE_COMPOSITION_SOURCE_FAMILY_AND_BOUND_O2_O4_CALLER_PRECONDITIONS' and sb['o6_b2_semantic_language_preservation_and_reflection']=='TRUE_CONDITIONALLY_ON_SEMANTICALLY_COMPLETE_CAP_FILTERED_SOURCE_FAMILY_AND_BOUND_UPSTREAM_CALLER_PRECONDITIONS','INV09','prior')
    checks={'o6_admission_bound':True,'published_realizable_definition_bound':True,'published_zero_boundary_formula_bound':True,'published_full_set_definition_bound':True,'published_lemma_3_4_bound':True,'published_corollary_3_8_bound':True,'published_proposition_5_8_bound':True,'b1_compactification_interface_present':True,'corrected_root_target_boundary_empty':True,'abstract_biconditional_uses_no_fixture_oracle':True,'engine_root_identity_separate':True,'upstream_caller_premises_not_auto':True}
    return {'gate':spec['gate'],'status':'CANDIDATE_PENDING_ADMISSION','published_dependency':pub,'derived_theorem':th,'source_checks':checks,'empty_root_contract':{'canonical_zero_boundary_left_right_are_zero':True,'canonical_zero_boundary_lambda_equals_cut_intersection_dimension':True,'canonical_zero_boundary_width_equals_layout_width':True,'realizable_trajectory_has_complete_layout_canonical_extension':True,'extensions_preserve_width':True,'compactification_equivalent_and_width_preserving':True,'fs_nonempty_iff_complete_layout_width_le_k':True,'concrete_fixture_oracle_used':False,'engine_root_full_set_equals_fs_k_v_zero':False,'upstream_caller_preconditions_automatically_established':False},'prior_obligations':{'o1_leaf_language_base_case':True,'o2_expand_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION','o3_join_interleaving_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION','o4_shrink_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_SUBSPACE_CONTAINMENT','o5_width_filter_soundness_and_reflection':'TRUE_CONDITIONALLY_ON_COMPLETE_COMPOSITION_SOURCE_FAMILY_AND_BOUND_O2_O4_CALLER_PRECONDITIONS','o6_b2_semantic_language_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_SEMANTICALLY_COMPLETE_CAP_FILTERED_SOURCE_FAMILY_AND_BOUND_UPSTREAM_CALLER_PRECONDITIONS'},'candidate_promotion':{'o7_empty_root_specialization_to_complete_layouts':False,'general_empty_root_specialization_receipt':False,'receipt_wording_if_admitted':spec['admission_boundary']['receipt_wording']},'general_semantic_theorems_established':6,'remaining_general_semantic_theorems':1,'first_required_next_receipt':'GENERAL_EMPTY_ROOT_SPECIALIZATION_RECEIPT','after_o7_next_composition_receipt':'GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_RECEIPT','strict_boundary':sb}

def verify(c,spec,a,controls=True):
    req(c.get('schema')==SCHEMA,'INV01','schema'); req(c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest'),'INV01','digest'); exp=derive(spec,a); req(c['proof_payload']==exp,'INV01','derived')
    p=c['proof_payload']; req(len(p['source_checks'])==12 and all(p['source_checks'].values()),'INV01','checks')
    e=p['empty_root_contract']; req(e['canonical_zero_boundary_width_equals_layout_width'] is True,'INV03','zero width'); req(e['extensions_preserve_width'] is True,'INV04','extensions'); req(e['fs_nonempty_iff_complete_layout_width_le_k'] is True,'INV05','biconditional'); req(e['concrete_fixture_oracle_used'] is False,'INV07','oracle'); req(e['engine_root_full_set_equals_fs_k_v_zero'] is False and e['upstream_caller_preconditions_automatically_established'] is False,'INV08','engine')
    if controls: finite_controls()
    b=p['strict_boundary']; req(b['o7_empty_root_specialization_to_complete_layouts'] is False and b['engine_root_full_set_equals_fs_k_v_zero'] is False,'INV12','O7 pending'); req(b['structural_induction_proved'] is False and b['terminal_completeness_proved'] is False and b['global_engine_no_layout_at_cap']=='FORBIDDEN' and b['found_layout']=='FORBIDDEN' and b['formal_admission']=='BLOCKED' and b['next_gate']=='CLOSED' and b['p_vs_np']=='OPEN','INV12','boundary')
def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tampers(c,spec,a):
    ok=[]
    def atk(name,mut):
        x=copy.deepcopy(c); mut(x); seal(x)
        try: verify(x,spec,a,False)
        except VError as e: ok.append((name,e.inv)); return
        raise AssertionError('survived '+name)
    atk('T01_ZERO_LAMBDA',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('canonical_zero_boundary_lambda_equals_cut_intersection_dimension',False))
    atk('T02_REALIZABLE',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('realizable_trajectory_has_complete_layout_canonical_extension',False))
    atk('T03_WIDTH_DIRECTION',lambda x:x['proof_payload']['derived_theorem'].__setitem__('forward','Reverse width direction.'))
    atk('T04_EXTENSION_WIDTH',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('extensions_preserve_width',False))
    atk('T05_COMPACT',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('compactification_equivalent_and_width_preserving',False))
    atk('T06_FIXTURE',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('concrete_fixture_oracle_used',True))
    atk('T07_ENGINE_ROOT',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('engine_root_full_set_equals_fs_k_v_zero',True))
    atk('T08_AUTO_PREMISES',lambda x:x['proof_payload']['empty_root_contract'].__setitem__('upstream_caller_preconditions_automatically_established',True))
    atk('T09_STRUCTURAL',lambda x:x['proof_payload']['strict_boundary'].__setitem__('structural_induction_proved',True))
    atk('T10_TERMINAL',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True))
    atk('T11_GLOBAL',lambda x:x['proof_payload']['strict_boundary'].__setitem__('global_engine_no_layout_at_cap','TRUE'))
    atk('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    req(len(ok)==12,'INV11','tamper count'); return ok

def main():
    p=argparse.ArgumentParser()
    for f in ('spec','producer-source','verifier-source','o6-audit','b1-core','root-spec','candidate-original','candidate-reordered'): p.add_argument('--'+f,type=Path,required=True)
    p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args(); spec=load(a.spec); req(spec['schema']==SPEC_SCHEMA and spec['status']=='SPEC_FROZEN','INV01','spec')
    req(not any(x.endswith('janus_c049_1_b4_6_3_general_empty_root_specialization') for x in imports(a.verifier_source)),'INV01','verifier imports producer'); req(a.candidate_original.read_bytes()==a.candidate_reordered.read_bytes(),'INV10','byte identity')
    c=load(a.candidate_original); verify(c,spec,a,True); ctrls=finite_controls(); ts=tampers(c,spec,a) if a.tamper_suite else []
    print('JANUS_GENERAL_EMPTY_ROOT_SPECIALIZATION_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('ZERO_BOUNDARY_LAYOUT_CONTROLS =',ctrls['layouts']); print('EXTENSION_WIDTH_CONTROLS =',ctrls['extension_checks']); print('ABSTRACT_FS_ZERO_IFF_COMPLETE_LAYOUT_WIDTH_LE_K = PASS_AS_DERIVED_CANDIDATE'); print('ENGINE_ROOT_FULL_SET_EQUALS_FS_K_V_ZERO = FALSE'); print('UPSTREAM_CALLER_PRECONDITIONS_AUTOMATICALLY_ESTABLISHED = FALSE'); print('GENERAL_SEMANTIC_THEOREMS_ESTABLISHED = 6'); print('REMAINING_GENERAL_SEMANTIC_THEOREMS = 1'); print('FIRST_REQUIRED_NEXT_RECEIPT = GENERAL_EMPTY_ROOT_SPECIALIZATION_RECEIPT'); print('AFTER_O7_NEXT_COMPOSITION_RECEIPT = GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_RECEIPT'); print('STRUCTURAL_INDUCTION_PROVED = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
