from __future__ import annotations

import hashlib,json
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_REVIEW_2026-09-17_v1.0.json'
SOURCE_FREEZE=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_RESULT_2026-09-17_v1.0.json'
PARENT=ROOT/'research/TRUMP_UF20_024_WL_TO_ORBIT_CAUSAL_BRIDGE_DIAGNOSTIC_RESULT_2026-09-17_v1.0.json'
FRESH=ROOT/'research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py'
WL=ROOT/'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
ORBIT=ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
EXPECTED={PREREG:'d06753061f4f1f06397ecb83188c6a580645ab52',REVIEW:'f3df81e17396d3fbba67346bf95e73df13e2be38',SOURCE_FREEZE:'5be45a07e7455876c2e9ff643350a8eaaf265ef2',PARENT:'3983f9dd90a389deaab3a6a191041f32b3533f77',FRESH:'9ec365ae27a6caa7b936cd33040e542f183ded99',WL:'6b697fd8b3de4c83f8226b06399b6bad99953d4e',ORBIT:'a076cfc56d68aad0348415e313705da1f6b9cdcd'}
ORDER=tuple(f'UF20_{i:03d}' for i in range(26,76))

def blob(path:Path)->str:
    d=path.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def canonical_sha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def classes(colors,keys,value_of):
    groups=defaultdict(list)
    for k in keys:groups[colors[k]].append(int(value_of(k)))
    out=[sorted(v) for v in groups.values() if len(v)>1];out.sort(key=lambda x:(len(x),x));return out
def guard():
    bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()};pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());sf=json.loads(SOURCE_FREEZE.read_text());parent=json.loads(PARENT.read_text())
    receipts=sf.get('source_receipts',[])
    checks={'bindings':all(bindings.values()),'prereg_status':pre.get('status')=='FROZEN_AFTER_SOURCE_FREEZE__BEFORE_FIRST_WL_CLASS_MEMBERSHIP_OR_E3_WITNESS_COMPUTATION_ON_THE_FIFTY_SOURCE_PANEL','review_authorized':review.get('review_verdict')=='PASS_CLEAN_PROSPECTIVE_FIFTY_SOURCE_WL_ORBIT_BRIDGE_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','source_freeze_pass':sf.get('verdict')=='PASS_UF20_026_075_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE','source_count':len(receipts)==50,'source_order':tuple(r.get('source') for r in receipts)==ORDER,'sources_independent':all(r.get('independent_verified') is True and r.get('status')=='SOURCE_FROZEN' for r in receipts),'parent_bridge_pass':parent.get('scientific_outcome')=='PASS_WL_DERIVES_SEALED_E3_TRANSPOSITION_AND_DIRECT_EXACT_SWAP_VERIFIES'}
    return {'ok':all(checks.values()),'checks':checks,'bindings':bindings}
def prediction(reduced):
    nodes,adj,labels=wl_ref.incidence_structure(reduced);variables=[n for n in nodes if n[0]=='v'];c1,r1=wl_ref.wl1(nodes,adj,labels);c2,r2=wl_ref.wl2(nodes,adj,labels);cl1=classes(c1,variables,lambda n:n[1]);diag=[(v,v) for v in variables];cl2=classes(c2,diag,lambda p:p[0][1]);pair=None;exact=None;checks=0
    if len(cl1)==1 and len(cl1[0])==2 and len(cl2)==1 and cl2[0]==cl1[0]:
        pair=cl1[0];formula=orbit.validate_and_normalize(reduced);checks=1;exact=orbit.is_exact_transposition_automorphism(formula,pair[0],pair[1])
    return {'wl1_nontrivial_variable_classes':cl1,'wl2_nontrivial_diagonal_variable_classes':cl2,'wl_rounds':{'wl1':r1,'wl2':r2},'wl_derived_pair':pair,'direct_exact_transposition_automorphism':exact,'prediction_positive':bool(pair is not None and exact is True),'direct_checks':checks}
def main():
    g=guard()
    if not g['ok']:return {'verdict':'HALT_AUTHORITY_OR_SOURCE_BINDING_FAILURE','authority_guard':g,'new_panel_structural_reads':0}
    training_ok,training=frozen.training_regression()
    if not training_ok:return {'verdict':'HALT_PREUNBLINDING_TRAINING_REGRESSION_FAILURE','training_regression':training,'new_panel_structural_reads':0}
    sf=json.loads(SOURCE_FREEZE.read_text());metadata={r['source']:r for r in sf['source_receipts']};predictions=[];prepared=[];direct_checks=0
    for source in ORDER:
        meta=metadata[source];path=ROOT/meta['committed_copy_path'];source_blob=frozen.blob(path);clauses,formula_hash=frozen.parse_and_formula_hash(path)
        if source_blob!=meta['committed_git_blob'] or formula_hash!=meta['canonical_formula_sha256']:return {'verdict':'HALT_AUTHORITY_OR_SOURCE_BINDING_FAILURE','reason':source,'training_regression':training,'new_panel_structural_reads':len(predictions)}
        raw=frozen.projection_identity.normalize_projection(source,clauses)[0];reduced,D,T=frozen.generic_round(raw);p=prediction(reduced);direct_checks+=p.pop('direct_checks')
        row={'source':source,'source_git_blob':source_blob,'canonical_formula_sha256':formula_hash,'projected_raw_sha256':frozen.csha(raw),'reduced_raw_sha256':frozen.csha(reduced),'degree1_variables':D,'target_constraints':T,**p};predictions.append(row);prepared.append((source,reduced))
    assert len(predictions)==50
    prediction_digest=canonical_sha(predictions)
    route_rows=[];e3_closed=[];misses=[];open_false_positives=[];portfolio_open=[];portfolio_closed=[]
    pred_by={r['source']:r for r in predictions}
    for source,reduced in prepared:
        route=frozen.route_row(reduced);p=pred_by[source];e3=route.get('E3',{});e3_positive=bool(e3.get('solver_authority') is True and e3.get('status') in frozen.CLOSED_ORBIT);edges=[sorted(map(int,e)) for e in (e3.get('generator_edges') or [])];pair=p['wl_derived_pair'];recovered=bool(e3_positive and p['prediction_positive'] and pair in edges);is_open=route.get('label')=='PORTFOLIO_OPEN';false_positive=bool(is_open and p['prediction_positive'])
        rr={'source':source,'portfolio_label':route.get('label'),'closure':route.get('closure'),'E1':route.get('E1'),'E2':route.get('E2'),'E3':route.get('E3'),'e3_positive':e3_positive,'e3_generator_edges':edges,'wl_pair_recovered_e3_witness':recovered,'open_false_positive':false_positive};route_rows.append(rr)
        if e3_positive:e3_closed.append(source)
        if e3_positive and not recovered:misses.append(source)
        if false_positive:open_false_positives.append(source)
        (portfolio_open if is_open else portfolio_closed).append(source)
    if misses:outcome='FALSIFIED_AT_LEAST_ONE_E3_CLOSED_CASE_NOT_RECOVERED_BY_FROZEN_WL_PAIR_RULE'
    elif open_false_positives:outcome='FALSIFIED_AT_LEAST_ONE_PORTFOLIO_OPEN_CASE_HAS_A_WL_DERIVED_DIRECT_EXACT_TRANSPOSITION_FALSE_POSITIVE'
    elif len(e3_closed)<2:outcome='PARTIAL_COVERAGE_FEWER_THAN_TWO_E3_CLOSED_CASES'
    else:outcome='PASS_PROSPECTIVE_MULTI_CLOSED_WL_TO_E3_WITNESS_REPLICATION'
    return {'artifact_id':'JANUS-TRUMP-UF20-026-075-PROSPECTIVE-WL-ORBIT-BRIDGE-CANDIDATE-2026-09-17-v1.0','gate':'TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_GATE','verdict':outcome,'authority_guard':g,'training_regression':training,'prediction_stage_completed_before_ground_truth':True,'prediction_stage_count':50,'prediction_stage_sha256':prediction_digest,'prediction_rows':predictions,'ground_truth_rows':route_rows,'summary':{'e3_closed_sources':e3_closed,'e3_closed_count':len(e3_closed),'e3_closed_misses':misses,'portfolio_open_sources':portfolio_open,'portfolio_open_count':len(portfolio_open),'portfolio_closed_sources':portfolio_closed,'portfolio_closed_count':len(portfolio_closed),'open_false_positives':open_false_positives,'wl_prediction_positive_sources':[r['source'] for r in predictions if r['prediction_positive']]},'resource_receipt':{'new_panel_sources_read':50,'generic_reduction_rounds_per_source':1,'iterated_peeling_rounds':0,'prediction_full_transposition_searches':0,'prediction_direct_exact_checks':direct_checks,'existing_portfolio_replays':50,'signed_route_invocations':0,'new_solver_mechanisms':0,'new_action_rules':0,'new_carrier_mechanisms':0,'posthoc_thresholds_or_pair_rules':0},'claim_ceiling':'PROSPECTIVE_FINITE_FIFTY_SOURCE_REPLICATION_OF_THE_FROZEN_WL_TO_EXACT_TRANSPOSITION_WITNESS_RULE_AGAINST_THE_EXISTING_E3_GROUND_TRUTH_ONLY','scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY':'NOT_PROVED','WL_SUFFICIENCY_FOR_ORBIT_CLOSURE':'NOT_PROVED'}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
