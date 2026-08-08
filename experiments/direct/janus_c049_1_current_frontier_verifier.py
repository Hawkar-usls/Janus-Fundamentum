from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.current_frontier.v1_1'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def verify(x,a):
    if x.get('schema')!=SCHEMA: raise AssertionError('schema')
    if x.get('status')!='FROZEN_NEGATIVE_TERMINAL_ADMITTED_B5_GENERAL_INTEGRATION_PENDING': raise AssertionError('status')
    if x.get('canonical_evidence_head')!='d02c0895a3fff82ad81aa6ea90a5fb8cf683daca': raise AssertionError('evidence head')
    actual=load(a.actual_receipt); term=load(a.terminal_receipt)
    if gb(a.actual_receipt)!='05478ffe8dee2f658297d12e2cbc3fc8ae15d917': raise AssertionError('actual blob')
    if gb(a.terminal_receipt)!='a37b11483f17e746c42f0f27bcedeb88e4125240': raise AssertionError('terminal blob')
    ap=actual['audit_payload']; tp=term['audit_payload']
    if ap['admission_review_id']!=4888144889 or ap['exact_proof_head']!='bef8134fe9bffd5f7b694803a866aad4927d96ed': raise AssertionError('actual authority')
    if ap['semantic_conclusion']['engine_root_full_set_equals_fs_k_v_zero'] is not True: raise AssertionError('actual root identity')
    if tp['admission_review_id']!=4888184352 or tp['exact_proof_head']!='1e4444d8a545888fbeaccf6e1b1fc503182c5471': raise AssertionError('terminal authority')
    tc=tp['semantic_conclusion']
    if tc['no_layout_at_cap']!='TRUE_FOR_FROZEN_SIX_FACTOR_TARGET_AT_K_1' or tc['arbitrary_input_global_engine_theorem']!='NOT_ESTABLISHED' or tc['p_vs_np']!='OPEN': raise AssertionError('terminal scope')
    al=x['admitted_layers']
    if al['actual_corrected_engine_trace_mapping']['receipt_git_blob']!=gb(a.actual_receipt) or al['actual_corrected_engine_trace_mapping']['review_id']!=4888144889: raise AssertionError('frontier actual binding')
    if al['frozen_negative_terminal']['receipt_git_blob']!=gb(a.terminal_receipt) or al['frozen_negative_terminal']['review_id']!=4888184352: raise AssertionError('frontier terminal binding')
    if al['frozen_negative_terminal']['target_layout_enumeration_used_as_premise'] is not False: raise AssertionError('oracle regression')

    phase_a=x['implemented_but_not_rebound_to_b5']['phase_a_verified_layout_to_c047']
    if gb(a.phase_a_solver)!='70c06752890e797bdf3a7c87c2cb41703fade163': raise AssertionError('phase-a solver blob')
    if phase_a['solver_git_blob']!=gb(a.phase_a_solver) or phase_a['subject']!='8cf39d35fc0fd03191b5ab28905637a5c842b2cf': raise AssertionError('phase-a solver binding')
    if phase_a['status']!='IMPLEMENTED_AND_PHASE_A_CI_AUDITED_NOT_REVIEWER_BOUND_TO_CORRECTED_GENERIC_DISCOVERY_HANDOFF': raise AssertionError('phase-a status')
    if phase_a['bare_no_layout_transcript_rejected'] is not True: raise AssertionError('bare negative transcript policy')
    solver=Path(a.phase_a_solver).read_text(encoding='utf-8')
    required_solver_tokens=(
      'def compile_order_probe(',
      'if sorted(order_positions) != list(range(len(normalized))):',
      'if terminal == "NO_LAYOUT_AT_CAP":',
      'OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT',
      'if terminal != "FOUND_LAYOUT":',
      'original_layout = layout_data_from_spaces(spaces, order_positions, dimension, meter)',
      'trellis = compile_order_probe(',
      '"reason": "FOUND_LAYOUT_VERIFIED_AND_C047_COMPILED"')
    if not all(t in solver for t in required_solver_tokens): raise AssertionError('phase-a C047 semantics')

    pos=x['historical_positive_reconstruction']
    if pos['generic_corrected_found_layout_reconstruction_admitted'] is not False: raise AssertionError('positive overclaim')
    seams=x['open_generalization_seams']
    expected={
      'generic_corrected_algorithm1_runtime_trace_mapping':'NOT_ESTABLISHED',
      'generic_positive_root_to_found_layout_reconstruction':'NOT_ESTABLISHED',
      'generic_negative_terminal_over_arbitrary_bound_inputs':'NOT_ESTABLISHED',
      'corrected_generic_discovery_to_phase_a_c047_handoff':'NOT_REBOUND_OR_ADMITTED',
      'arbitrary_input_global_engine_theorem':'NOT_ESTABLISHED'}
    if seams!=expected: raise AssertionError('generalization seam')
    if gb(a.b5_plan)!='a776887c258da5c92414fa3d548beeec6ebcee83': raise AssertionError('b5 plan blob')
    plan=Path(a.b5_plan).read_text(encoding='utf-8')
    for token in ('B5 — terminal integration with C047','replayable `FOUND_LAYOUT` and `NO_LAYOUT_AT_CAP`','exact C047 SAT/UNSAT composition'):
        if token not in plan: raise AssertionError('b5 plan semantics')
    snaps={s['path']:s for s in x['superseded_status_snapshots']}
    for path,attr,blob,next_gate in [
      ('registry/c049.1-phase-b-status.json','phase_b','71c35490252ed9bb7f3755753e73e7fbf39c435b','C049.1_PHASE_B4_COMPLETE_BRANCH_DECOMPOSITION_REFINEMENT'),
      ('registry/c049.1-phase-b4.6-status.json','b46','f4141eca14d62f1f94cf76227f86e0afeb1cc1a4','C049.1_B4.6.2_FULL_ITERATIVE_COMPRESSION_CYCLE'),
      ('registry/c049.1-phase-b4.6.2-status.json','b462','c78a834bee039d4a84a68d9bf18581cf32c32e38','C049.1_B4.6.3_TERMINAL_COMPLETENESS')]:
        p=getattr(a,attr)
        if gb(p)!=blob or snaps[path]['git_blob']!=blob: raise AssertionError('snapshot blob '+path)
        if load(p)['next_gate']!=next_gate or snaps[path]['historical_next_gate']!=next_gate: raise AssertionError('snapshot next gate '+path)
    if x['next_gate']!='C049.1_B5_GENERAL_RUNTIME_AND_TERMINAL_INTEGRATION_CONTRACT': raise AssertionError('next gate')
    ns=x['next_gate_scope']
    required_scope=('must_first_freeze','must_not_assume_generic_runtime_from_frozen_six_factor_trace','must_not_assume_found_layout_from_historical_positive_fixtures','must_bind_whole_factor_partition','must_preserve_affine_offsets_for_c047','must_rebind_corrected_generic_discovery_to_phase_a_c047_interface','must_keep_capability_refusals_explicit')
    if not all(ns[k] is True for k in required_scope): raise AssertionError('next scope')
    sb=x['strict_boundary']
    expected_boundary={'frozen_target_no_layout_at_cap':True,'phase_a_verified_layout_to_c047_implemented':True,'corrected_generic_discovery_to_c047_handoff_admitted':False,'generic_no_layout_at_cap_enabled':False,'generic_found_layout_enabled':False,'b5_complete':False,'global_formal_admission':'BLOCKED','p_vs_np':'OPEN'}
    if sb!=expected_boundary: raise AssertionError('boundary')

def attacks(base,a):
    muts=[]
    def add(name,fn): y=copy.deepcopy(base); fn(y); muts.append((name,y))
    add('T01_GENERIC_RUNTIME',lambda x:x['open_generalization_seams'].__setitem__('generic_corrected_algorithm1_runtime_trace_mapping','ESTABLISHED'))
    add('T02_GENERIC_FOUND',lambda x:x['strict_boundary'].__setitem__('generic_found_layout_enabled',True))
    add('T03_GENERIC_NO_LAYOUT',lambda x:x['strict_boundary'].__setitem__('generic_no_layout_at_cap_enabled',True))
    add('T04_B5_COMPLETE',lambda x:x['strict_boundary'].__setitem__('b5_complete',True))
    add('T05_P_VS_NP',lambda x:x['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    add('T06_STALE_NEXT_GATE',lambda x:x.__setitem__('next_gate','C049.1_B4.6.2_FULL_ITERATIVE_COMPRESSION_CYCLE'))
    add('T07_FOUND_FROM_FIXTURE',lambda x:x['historical_positive_reconstruction'].__setitem__('generic_corrected_found_layout_reconstruction_admitted',True))
    add('T08_ORACLE_REGRESSION',lambda x:x['admitted_layers']['frozen_negative_terminal'].__setitem__('target_layout_enumeration_used_as_premise',True))
    add('T09_FALSE_C047_REBOUND',lambda x:x['strict_boundary'].__setitem__('corrected_generic_discovery_to_c047_handoff_admitted',True))
    add('T10_ERASE_EXISTING_PHASE_A_C047',lambda x:x['strict_boundary'].__setitem__('phase_a_verified_layout_to_c047_implemented',False))
    rejected=0
    for name,y in muts:
        try: verify(y,a)
        except Exception: rejected+=1; continue
        raise AssertionError(name+' survived')
    return rejected,len(muts)

def main():
    p=argparse.ArgumentParser()
    for n in ('frontier','actual-receipt','terminal-receipt','phase-a-solver','b5-plan','phase-b','b46','b462'):
        p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args()
    x=load(a.frontier); verify(x,a)
    print('JANUS_C049_1_CURRENT_FRONTIER_INDEPENDENT_VERIFIER = PASS')
    print('FROZEN_NEGATIVE_TERMINAL_AUTHORITY = PASS')
    print('PHASE_A_VERIFIED_LAYOUT_TO_C047_IMPLEMENTED = TRUE')
    print('CORRECTED_GENERIC_DISCOVERY_TO_C047_HANDOFF_ADMITTED = FALSE')
    print('HISTORICAL_STATUS_SNAPSHOTS_CLASSIFIED = 3/3')
    print('OPEN_GENERALIZATION_SEAMS = 5/5')
    print('NEXT_GATE = C049.1_B5_GENERAL_RUNTIME_AND_TERMINAL_INTEGRATION_CONTRACT')
    print('GENERIC_FOUND_LAYOUT_ENABLED = FALSE')
    print('GENERIC_NO_LAYOUT_AT_CAP_ENABLED = FALSE')
    print('B5_COMPLETE = FALSE')
    print('P_VS_NP = OPEN')
    if a.tamper_suite:
        r,t=attacks(x,a); print(f'DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}')
if __name__=='__main__': main()
