#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.b4_6_4.actual_engine_trace_preflight_candidate.v1'
BLOCKS=((2,),(4,),(6,),(3,),(5,),(1,))
D=3

class VError(AssertionError):
    def __init__(self, code):
        super().__init__(code); self.code=code

def req(v, code):
    if not v: raise VError(code)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def rref(rows):
    rows=[int(x) for x in rows if int(x)]
    out=[]
    for x in rows:
        for r in out: x=min(x,x^r)
        if not x: continue
        p=x.bit_length()-1
        out=[r^x if ((r>>p)&1) else r for r in out]+[x]
        out.sort(reverse=True)
    return tuple(out)
def sp(rows):
    out={0}
    for r in rref(rows): out|={x^r for x in tuple(out)}
    return out
def add(a,b): return rref((*a,*b))
def meet(a,b): return rref(sorted(sp(a)&sp(b)))
def le(a,b): return sp(a)<=sp(b)
def fspan(ids): return rref(v for i in ids for v in BLOCKS[i])
def bd(ids):
    ids=tuple(ids); s=set(ids)
    return meet(fspan(ids),fspan(tuple(i for i in range(6) if i not in s)))
def nrec(node):
    rf=node-5; left=tuple(range(rf)); right=(rf,); covered=tuple(range(rf+1))
    lb,rb,pb=bd(left),bd(right),bd(covered); bp=add(lb,rb); lv,rv=fspan(left),fspan(right)
    return {'node_id':node,'left_factor_indices':list(left),'right_factor_indices':list(right),'covered_factor_indices':list(covered),'left_boundary':list(lb),'right_boundary':list(rb),'join_boundary_bprime':list(bp),'parent_boundary':list(pb),'left_span':list(lv),'right_span':list(rv),'caller_certificates':{'o2_expand_left':le(lb,bp) and meet(lv,bp)==lb,'o2_expand_right':le(rb,bp) and meet(rv,bp)==rb,'o3_join_separation':meet(add(lv,bp),add(rv,bp))==bp,'o4_shrink_containment':le(pb,bp)}}

def expected_node8(n8):
    return {
        'proof_subject':n8['candidate_proof_head'],
        'semantic_audit':n8['semantic_audit'],
        'semantic_audit_review_id':n8['independent_semantic_audit_review_id'],
        'final_admission_review_id':n8['final_admission_review_id'],
        'semantic_admission':n8['semantic_admission'],
        'status':n8['status'],
        'authority_receipt_commit':n8['authority_receipt_commit'],
        'authority_receipt_git_blob':n8['authority_receipt_git_blob'],
        'authority_receipt_file_sha256':n8['authority_receipt_file_sha256'],
        'authority_receipt_semantic_digest':n8['authority_receipt_semantic_digest'],
        'verification_pr':n8['verification_pr'],
        'verification_head':n8['verification_head'],
        'verification_run_id':n8['verification_run_id'],
        'verification_artifact_id':n8['verification_artifact_id'],
        'verification_workflows':n8['verification_workflows'],
    }

def verify(c,ledger,hardening):
    req(c.get('schema')==SCHEMA,'INV01_SCHEMA')
    req(c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest'),'INV01_DIGEST')
    p=c['proof_payload']; hp=hardening['hardening_payload']
    req(hardening.get('semantic_digest_scope')=='hardening_payload' and dg(hp)==hardening.get('semantic_digest'),'INV02_HARDENING_DIGEST')
    req(ledger.get('schema')=='janus.c049_1.b4_6_4.general_structural_induction_authority_gap_ledger.v1','INV02_LEDGER_SCHEMA')
    req(p['target']=={'ambient_dim':3,'k':1,'whole_factor_blocks':[list(x) for x in BLOCKS],'tree':'LEFT_DEEP_6_FACTOR'},'INV03_TARGET')
    exp_leaves=[{'factor_index':i,'boundary':list(bd((i,)))} for i in range(6)]
    req(p['derived_leaf_boundaries']==exp_leaves,'INV04_LEAF_BOUNDARIES')
    exp_nodes=[nrec(n) for n in range(6,11)]
    req(p['derived_internal_nodes']==exp_nodes,'INV05_CALLER_DAG')
    req(all(all(x['caller_certificates'].values()) for x in exp_nodes),'INV06_CALLER_PREMISES')
    req(p['path_domains']=={'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'extension_preorder_steps':[[1,0],[0,1],[1,1]]},'INV07_PATH_DOMAINS')
    entries={x['edge_id']:x for x in ledger['entries']}
    n8=entries['NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K']; q80=entries['NODE8_UP_K_TO_NODE9_Q80']
    req(p['authority']['general_composition_receipt']==hp['general_composition_authority'],'INV08_GENERAL_AUTHORITY')
    req(hp['node8_up_k_authority_requirement']['authority_established'] is True,'INV09_NODE8_AUTHORITY')
    req(hp['node8_up_k_authority_requirement']['semantic_admission_review_id']==4888054139,'INV09_NODE8_AUTHORITY')
    req(hp['node8_up_k_authority_requirement']['authority_receipt_git_blob']=='b04124490df9737c0799ed856fd7819b37477208','INV09_NODE8_AUTHORITY')
    req(p['authority']['node8_up_k']==expected_node8(n8),'INV09_NODE8_AUTHORITY')
    req(n8['status']=='CLOSED_BY_VERIFICATION_ONLY_AUTHORITY_CLOSURE' and n8['semantic_admission']=='ADMITTED_BY_REVIEWER_BOUND_AUTHORITY_CLOSURE','INV09_NODE8_AUTHORITY')
    req(p['authority']['q80']['historical_standalone_admission'] is False and p['authority']['q80']['composition_replay_required'] is True and p['authority']['q80']['status']==q80['status'],'INV10_Q80_REPLAY')
    req(p['blockers']==[] and p['blockers']==sorted(ledger['current_blockers']),'INV10_GAP_LEDGER')
    req(p['required_replays']==sorted(ledger['composition_replays_required'])==['NODE8_UP_K_TO_NODE9_Q80'],'INV10_GAP_LEDGER')
    c0=p['preflight_conclusions']
    req(c0['all_o2_o3_o4_geometry_caller_premises_hold_on_frozen_tree'] is True,'INV06_CALLER_PREMISES')
    req(c0['general_composition_authority_bound'] is True,'INV08_GENERAL_AUTHORITY')
    req(c0['node8_authority_closed'] is True,'INV09_NODE8_AUTHORITY')
    req(c0['q80_composition_replay_complete'] is False,'INV10_Q80_REPLAY')
    req(c0['root_empty_consumed_as_premise'] is False,'INV11_NONVACUITY')
    req(c0['actual_corrected_engine_complete_algorithm1_trace_established'] is False and c0['engine_root_full_set_equals_fs_k_v_zero'] is False and c0['ready_for_composition_admission'] is False,'INV12_CEILING')
    b=p['strict_boundary']; req(b['structural_induction_proved_for_actual_engine'] is False and b['terminal_completeness_proved'] is False and b['no_layout_at_cap']=='FORBIDDEN' and b['found_layout']=='FORBIDDEN' and b['formal_admission']=='BLOCKED' and b['p_vs_np']=='OPEN','INV12_CEILING')

def tamper_suite(c,l,h):
    attacks=[]
    def attack(name,mut):
        x=copy.deepcopy(c); mut(x); x['semantic_digest']=dg(x['proof_payload'])
        try: verify(x,l,h)
        except VError as e: attacks.append((name,e.code)); return
        raise AssertionError('tamper survived '+name)
    attack('T01_BOUNDARY',lambda x:x['proof_payload']['derived_internal_nodes'][2].__setitem__('parent_boundary',[4,2]))
    attack('T02_EXPAND',lambda x:x['proof_payload']['derived_internal_nodes'][0]['caller_certificates'].__setitem__('o2_expand_left',False))
    attack('T03_JOIN',lambda x:x['proof_payload']['derived_internal_nodes'][3]['caller_certificates'].__setitem__('o3_join_separation',False))
    attack('T04_SHRINK',lambda x:x['proof_payload']['derived_internal_nodes'][4]['caller_certificates'].__setitem__('o4_shrink_containment',False))
    attack('T05_DIAGONAL_JOIN',lambda x:x['proof_payload']['path_domains'].__setitem__('ordinary_join_diagonal_allowed',True))
    attack('T06_NODE8_REOPEN',lambda x:x['proof_payload']['preflight_conclusions'].__setitem__('node8_authority_closed',False))
    attack('T07_Q80_CLOSE',lambda x:x['proof_payload']['preflight_conclusions'].__setitem__('q80_composition_replay_complete',True))
    attack('T08_CONSUME_ROOT_EMPTY',lambda x:x['proof_payload']['preflight_conclusions'].__setitem__('root_empty_consumed_as_premise',True))
    attack('T09_ENGINE_TRACE',lambda x:x['proof_payload']['preflight_conclusions'].__setitem__('actual_corrected_engine_complete_algorithm1_trace_established',True))
    attack('T10_ROOT_IDENTITY',lambda x:x['proof_payload']['preflight_conclusions'].__setitem__('engine_root_full_set_equals_fs_k_v_zero',True))
    attack('T11_READY',lambda x:x['proof_payload']['preflight_conclusions'].__setitem__('ready_for_composition_admission',True))
    attack('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    req(len(attacks)==12,'INV12_TAMPER_COUNT'); return attacks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ledger',type=Path,required=True); ap.add_argument('--hardening',type=Path,required=True); ap.add_argument('--candidate',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args()
    l,h,c=load(a.ledger),load(a.hardening),load(a.candidate); verify(c,l,h); ts=tamper_suite(c,l,h) if a.tamper_suite else []
    print('JANUS_ACTUAL_ENGINE_TRACE_PREFLIGHT_INDEPENDENT_VERIFIER = PASS')
    print('INVARIANTS = 12/12')
    print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN')
    print('GF2_CALLER_PREMISE_NODES = 5/5')
    print('NODE8_AUTHORITY_CLOSED = TRUE')
    print('CURRENT_BLOCKERS = 0')
    print('Q80_COMPOSITION_REPLAY_COMPLETE = FALSE')
    print('ROOT_EMPTY_CONSUMED_AS_PREMISE = FALSE')
    print('READY_FOR_COMPOSITION_ADMISSION = FALSE')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
