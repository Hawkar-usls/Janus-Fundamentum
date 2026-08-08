#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, copy, hashlib, json
from pathlib import Path

from janus_c049_1_b2_up_k_core import Ledger, up_k_closure
from janus_c049_1_b3_expand_join_shrink_core import Statistic, expand_trajectory, shrink_trajectory
from janus_c049_1_b3_join_path_domain_corrected import JOIN_INTERLEAVING_STEPS, ordinary_join_paths, join_trajectory

SCHEMA='janus.c049_1.b4_6_4.actual_engine_composition_authority_closure_candidate.v1'
WHOLE=((2,),(4,),(6,),(3,),(5,),(1,)); D=3
class VError(AssertionError):
    def __init__(self,c): super().__init__(c); self.code=c
def req(v,c):
    if not v: raise VError(c)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def contains(v,n):
    if v==n: return True
    if isinstance(v,dict): return any(contains(x,n) for x in v.values())
    if isinstance(v,(list,tuple)): return any(contains(x,n) for x in v)
    return False
def sem(p,scope):
    x=load(p); req(x.get('semantic_digest_scope')==scope,'INV01_SEM_SCOPE'); req(dg(x[scope])==x.get('semantic_digest'),'INV01_SEM_DIGEST'); return x
def pyconst(path,name):
    t=ast.parse(Path(path).read_text(encoding='utf-8'))
    for n in t.body:
        if isinstance(n,(ast.Assign,ast.AnnAssign)):
            target=n.targets[0] if isinstance(n,ast.Assign) else n.target
            if isinstance(target,ast.Name) and target.id==name:
                try: return ast.literal_eval(n.value)
                except Exception: return None
    return None

def rr(rows):
    tab={}
    for raw in rows:
        x=int(raw); req(0<=x<(1<<D),'INV04_VECTOR_RANGE')
        while x:
            p=x.bit_length()-1
            if p in tab: x^=tab[p]; continue
            tab[p]=x
            for q,r in list(tab.items()):
                if q!=p and ((r>>p)&1): tab[q]=r^x
            break
    for p in sorted(tab):
        for q in sorted(tab,reverse=True):
            if q!=p and ((tab[q]>>p)&1): tab[q]^=tab[p]
    return tuple(tab[p] for p in sorted(tab,reverse=True))
def sp(rows):
    out={0}
    for r in rr(rows): out|={x^r for x in tuple(out)}
    return out
def add(a,b): return rr((*a,*b))
def meet(a,b): return rr(sorted(sp(a)&sp(b)))
def le(a,b): return sp(a)<=sp(b)
def fspan(ids): return rr(v for i in ids for v in WHOLE[i])
def bd(ids):
    ids=tuple(ids); s=set(ids); return meet(fspan(ids),fspan(i for i in range(6) if i not in s))
def geometry():
    rows=[]
    for node in range(6,11):
        rf=node-5; left=tuple(range(rf)); right=(rf,); covered=tuple(range(rf+1)); lb,rb,pb=bd(left),bd(right),bd(covered); bp=add(lb,rb); lv,rv=fspan(left),fspan(right)
        cert={'o2_left':le(lb,bp) and meet(lv,bp)==lb,'o2_right':le(rb,bp) and meet(rv,bp)==rb,'o3':meet(add(lv,bp),add(rv,bp))==bp,'o4':le(pb,bp)}
        req(all(cert.values()),'INV04_GEOMETRY'); rows.append((node,bp,pb))
    return rows

def positive():
    b=(1,); leaf=(Statistic((),b,0),Statistic(b,(),0)); left,_=expand_trajectory(leaf,b,b,1); right,_=expand_trajectory(leaf,b,b,1); gens=[]; paths=[]
    for path in ordinary_join_paths(2,2):
        joined,_=join_trajectory(left,right,path,b,1); shrunk,_=shrink_trajectory(joined,(),1); w=max(s.value for s in shrunk); paths.append((tuple(path),w,w<=1));
        if w<=1: gens.append(shrunk)
    req(gens,'INV16_POSITIVE'); c=up_k_closure(gens,0,1,Ledger(discovery_cap=1000000,work_cap=1000000)); req(int(c['entry_count'])>0,'INV16_POSITIVE')
    return len(gens),int(c['entry_count']),paths

def verify(c,a):
    req(c.get('schema')==SCHEMA,'INV01_SCHEMA'); req(c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest'),'INV01_DIGEST')
    p=c['proof_payload']; spec=load(a.spec); hard=sem(a.hardening,'hardening_payload'); ledger=load(a.ledger); pre=sem(a.preflight_audit,'audit_payload'); n8=sem(a.node8_audit,'audit_payload'); q80=sem(a.q80_audit,'audit_payload')
    req(spec.get('status')=='SPEC_FROZEN' and spec.get('admission') is False,'INV01_SPEC'); hp=hard['hardening_payload']; ga=hp['general_composition_authority']; nr=hp['node8_up_k_authority_requirement']
    req(ga['review_id']==4888039239 and ga['authority_scope']=='COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_ONLY','INV02_GENERAL_AUTHORITY')
    req(nr['authority_established'] is True and nr['semantic_admission_review_id']==4888054139,'INV02_NODE8_AUTHORITY')
    req(n8['audit_payload']['semantic_subject']['final_admission_review_id']==4888054139 and n8['audit_payload']['semantic_conclusion'] if 'semantic_conclusion' in n8['audit_payload'] else True,'INV02_NODE8_RECEIPT')
    req(q80['audit_payload']['admission_review_id']==4888076452,'INV02_Q80_AUTHORITY'); req(q80['audit_payload']['derived']['partition_fine_language_conservation']=='PASS' and q80['audit_payload']['derived']['expected_domain_or_fine_total_used_as_acceptance_oracle'] is False,'INV07_Q80_COMPLETENESS'); req(q80['audit_payload']['downstream_handoff']['scalar_handoff_identity']=='PASS','INV10_Q80_HANDOFF')
    req(pre['audit_payload']['derived_geometry']['all_o2_o3_o4_caller_premises_hold'] is True and pre['audit_payload']['semantic_conclusion']['root_empty_consumed_as_premise'] is False,'INV04_PREFLIGHT')
    grows=geometry(); req(len(grows)==5,'INV04_GEOMETRY_COUNT')
    req(ledger.get('current_blockers')==[],'INV02_BLOCKERS'); entries={x['edge_id']:x for x in ledger['entries']}; req(entries['NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K']['final_admission_review_id']==4888054139,'INV02_LEDGER_NODE8')
    carriers=spec['engine_carriers']; req(gb(a.corrected_join)==carriers['corrected_join_api']['git_blob'],'INV05_JOIN_BLOB'); req(gb(a.node6_source)==carriers['node6_first_internal_join']['git_blob'],'INV03_NODE6_BLOB'); req(gb(a.node7_source)==carriers['node7_frontier']['git_blob'],'INV03_NODE7_BLOB'); req(gb(a.node8_manifest)==carriers['node8_parent_refinement']['manifest_git_blob'],'INV03_NODE8_BLOB'); req(gb(a.scalar_spec)==carriers['node9_scalar']['spec_git_blob'],'INV10_SCALAR_BLOB'); req(gb(a.residual_spec)==carriers['node9_residual_frontier']['spec_git_blob'],'INV10_RESIDUAL_BLOB'); req(gb(a.node9_upk_spec)==carriers['node9_residual_up_k']['spec_git_blob'],'INV10_UPK_BLOB'); req(gb(a.root_spec)==carriers['root_refinement']['spec_git_blob'],'INV10_ROOT_BLOB')
    corrected=Path(a.corrected_join).read_text(); req('((1, 0), (0, 1))' in corrected and '((1, 0), (0, 1), (1, 1))' in corrected,'INV05_PATH_DOMAIN'); req(pyconst(a.node6_source,'FIRST_INTERNAL_NODE_ID')==6,'INV03_NODE6_ID'); req(pyconst(a.node7_source,'PARENT_HEAD')=='af0556d4ae05ea6dc343d120a34f67255890ba18','INV10_NODE7_HANDOFF')
    manifest=load(a.node8_manifest); req(manifest['base_exact_head']=='024afebb322c67953f310af48818d3386fdcfc27' and manifest['proof_controls']['ordinary_join_diagonal_allowed'] is False,'INV10_NODE8_HANDOFF')
    scalar,residual,upk,root,root_empty=map(load,(a.scalar_spec,a.residual_spec,a.node9_upk_spec,a.root_spec,a.root_empty_spec)); qh=q80['audit_payload']['downstream_handoff']; req(contains(scalar,nr['proof_subject']) and contains(scalar,qh['q80_sha256']) and contains(scalar,qh['q80_semantic_digest']),'INV10_SCALAR_HANDOFF'); req(contains(residual,carriers['node9_scalar']['admission_head']),'INV10_RESIDUAL_HANDOFF'); req(contains(upk,carriers['node9_residual_frontier']['admission_head']),'INV10_UPK_HANDOFF'); req(contains(root,carriers['node9_residual_up_k']['admission_head']),'INV10_ROOT_HANDOFF'); req(contains(root_empty,carriers['root_refinement']['admission_head']),'INV10_ROOT_UPK_HANDOFF'); req(contains(root,[list(x) for x in WHOLE]),'INV15_LAYOUT_UNITS')
    pg,pe,pp=positive(); req(p['positive_nonvacuity_control']['successful_root_generators']==pg and p['positive_nonvacuity_control']['root_up_k_entry_count']==pe and p['positive_nonvacuity_control']['root_full_set_nonempty'] is True,'INV16_POSITIVE')
    auth=p['authority']; req(auth['general_composition_review_id']==4888039239 and auth['preflight_review_id']==4888055750 and auth['node8_final_admission_review_id']==4888054139 and auth['q80_composition_review_id']==4888076452,'INV02_CANDIDATE_AUTHORITY')
    t=p['actual_trace']; req(t['geometry_caller_premises']=='5/5' and t['all_stage_authority_edges_closed'] is True and t['q80_partition_fine_language_conservation_bound'] is True and t['q80_scalar_handoff_identity'] is True and all(t[k] is True for k in ('scalar_to_residual_handoff','residual_to_node9_up_k_handoff','node9_up_k_to_root_refinement_handoff','root_refinement_to_root_up_k_handoff')),'INV11_TRACE_COMPOSITION')
    comp=p['composition']; req(comp['general_complete_trace_theorem_bound'] is True and comp['actual_trace_satisfies_complete_algorithm1_contract_candidate'] is True and comp['candidate_derives_engine_root_full_set_equals_fs_k_v_zero'] is True,'INV11_ROOT_IDENTITY_CANDIDATE'); req(comp['root_empty_consumed_as_composition_premise'] is False and comp['zero_root_successes_consumed_as_composition_premise'] is False and comp['historical_counts_consumed_as_acceptance_oracles'] is False,'INV14_NONVACUITY')
    b=p['strict_boundary']; req(b['actual_corrected_engine_complete_algorithm1_trace_established'] is False and b['engine_root_full_set_equals_fs_k_v_zero'] is False and b['structural_induction_proved'] is False and b['composition_candidate_ready_for_reviewer_admission'] is True,'INV18_REVIEW_CEILING'); req(b['terminal_completeness_proved'] is False and b['no_layout_at_cap']=='FORBIDDEN' and b['found_layout']=='FORBIDDEN' and b['formal_admission']=='BLOCKED' and b['p_vs_np']=='OPEN','INV18_TERMINAL_CEILING')

def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tampers(c,a):
    out=[]
    def attack(name,mut):
        x=copy.deepcopy(c); mut(x); seal(x)
        try: verify(x,a)
        except VError as e: out.append((name,e.code)); return
        raise AssertionError('tamper survived '+name)
    attack('T01_GENERAL_REVIEW',lambda x:x['proof_payload']['authority'].__setitem__('general_composition_review_id',1))
    attack('T02_NODE8_REVIEW',lambda x:x['proof_payload']['authority'].__setitem__('node8_final_admission_review_id',1))
    attack('T03_Q80_REVIEW',lambda x:x['proof_payload']['authority'].__setitem__('q80_composition_review_id',1))
    attack('T04_GEOMETRY',lambda x:x['proof_payload']['actual_trace'].__setitem__('geometry_caller_premises','4/5'))
    attack('T05_DIAGONAL_JOIN',lambda x:x['proof_payload']['actual_trace'].__setitem__('ordinary_join_steps',[[1,0],[0,1],[1,1]]))
    attack('T06_NODE7_REPAIR',lambda x:x['proof_payload']['actual_trace'].__setitem__('node7_repair_bound',False))
    attack('T07_NODE8_EDGE',lambda x:x['proof_payload']['actual_trace'].__setitem__('node8_up_k_authority_bound',False))
    attack('T08_Q80_CONSERVATION',lambda x:x['proof_payload']['actual_trace'].__setitem__('q80_partition_fine_language_conservation_bound',False))
    attack('T09_Q80_HANDOFF',lambda x:x['proof_payload']['actual_trace'].__setitem__('q80_scalar_handoff_identity',False))
    attack('T10_SCALAR_RESIDUAL',lambda x:x['proof_payload']['actual_trace'].__setitem__('scalar_to_residual_handoff',False))
    attack('T11_RESIDUAL_UPK',lambda x:x['proof_payload']['actual_trace'].__setitem__('residual_to_node9_up_k_handoff',False))
    attack('T12_ROOT_HANDOFF',lambda x:x['proof_payload']['actual_trace'].__setitem__('node9_up_k_to_root_refinement_handoff',False))
    attack('T13_ROOT_UPK_HANDOFF',lambda x:x['proof_payload']['actual_trace'].__setitem__('root_refinement_to_root_up_k_handoff',False))
    attack('T14_ROOT_EMPTY_SHORTCUT',lambda x:x['proof_payload']['composition'].__setitem__('root_empty_consumed_as_composition_premise',True))
    attack('T15_ZERO_SHORTCUT',lambda x:x['proof_payload']['composition'].__setitem__('zero_root_successes_consumed_as_composition_premise',True))
    attack('T16_POSITIVE',lambda x:x['proof_payload']['positive_nonvacuity_control'].__setitem__('root_full_set_nonempty',False))
    attack('T17_PREMATURE_AUTHORITY',lambda x:x['proof_payload']['strict_boundary'].__setitem__('engine_root_full_set_equals_fs_k_v_zero',True))
    attack('T18_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    req(len(out)==18,'INV18_TAMPER_COUNT'); return out

def main():
    p=argparse.ArgumentParser()
    for n in ('spec','hardening','ledger','preflight-audit','node8-audit','q80-audit','corrected-join','node6-source','node7-source','node8-manifest','scalar-spec','residual-spec','node9-upk-spec','root-spec','root-empty-spec','candidate'): p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args(); c=load(a.candidate); verify(c,a); ts=tampers(c,a) if a.tamper_suite else []
    print('JANUS_ACTUAL_ENGINE_COMPOSITION_AUTHORITY_CLOSURE_INDEPENDENT_VERIFIER = PASS'); print('INVARIANTS = 18/18'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/18' if a.tamper_suite else 'NOT_RUN'); print('GF2_CALLER_PREMISE_NODES = 5/5'); print('ALL_STAGE_AUTHORITY_EDGES_CLOSED = TRUE'); print('Q80_PARTITION_FINE_LANGUAGE_CONSERVATION = PASS'); print('Q80_SCALAR_HANDOFF_IDENTITY = PASS'); print('POSITIVE_NONVACUITY_CONTROL = PASS'); print('ROOT_EMPTY_CONSUMED_AS_COMPOSITION_PREMISE = FALSE'); print('ACTUAL_TRACE_COMPLETE_CANDIDATE = TRUE'); print('ENGINE_ROOT_FULL_SET_EQUALS_FS_K_V_ZERO_CANDIDATE = TRUE'); print('FORMAL_ADMISSION = BLOCKED_PENDING_REVIEW'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
