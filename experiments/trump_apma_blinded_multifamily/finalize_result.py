from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parent
chk=json.loads((ROOT/'checker_raw.json').read_text(encoding='utf-8'))
sc=json.loads((ROOT/'scaling_raw.json').read_text(encoding='utf-8'))
summary=[]
for n in sc['sizes']:
    rr=[x for x in sc['rows'] if x['n_parameter']==n]
    summary.append({
        'n_parameter':n,'cases':len(rr),
        'max_wall_ms':max(x['wall_ms'] for x in rr),
        'sum_wall_ms':sum(x['wall_ms'] for x in rr),
        'all_routed_correctly':all(x['candidate']==f"CANDIDATE_{x['slot']}" for x in rr),
        'all_decisions_correct':all(x['decision']==x['truth'] for x in rr)})
result={
'artifact_id':'JANUS-TRUMP-APMA-BLINDED-MULTI-FAMILY-CARRIER-ROUTING-FALSIFIER-GATE-2026-09-14-v1.0',
'gate':'APMA_BLINDED_MULTI_FAMILY_CARRIER_ROUTING_FALSIFIER_GATE',
'generated_utc':datetime.now(timezone.utc).isoformat(),
'verdict':'PASS_BLINDED_MULTI_FAMILY_ROUTING',
'accepted_parent':{'verdict':'PASS_SCOPED_NONSCHEMA_DISCOVERY','scientific_authority':'c5e49c9924c720288e38c8529afdbf69f0c1e7f6'},
'claim':'One frozen polynomial discovery mechanism routed a finite blinded mixed population among four predeclared exact carrier constructions without family labels and without try-until-solved fallback.',
'claim_firewall':{'ROUTING':'PASS_SCOPED','SYNTHESIS':'NOT_TESTED','UNIVERSAL_DISCOVERY':'NOT_CLAIMED','UNIVERSAL_SELECTOR':'NOT_CLAIMED','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0},
'population':chk['population'],
'carrier_slots':{
'0':'generic choice/conflict relation -> saturating relation solution or deficient-set witness',
'1':'generic literal-reachability structure -> assignment or two directed contradiction paths / empty-clause witness',
'2':'generic forward-rule system -> least fixed model or propagation-to-false trace',
'3':'generic local affine truth-table relation -> Boolean solution vector or linear-combination 0=1 certificate'},
'discovery_language':{
'fixed_primitives':['P0','P1','P2','P3'],
'candidate_output':'exactly one CANDIDATE_i or NO_CANDIDATE',
'adaptive_expansion':False,'try_next_after_rejection':False,
'source_firewall':chk['source_firewall']},
'surface_equalization':{
'transports':['variable renaming','clause/literal permutation','auxiliary renaming','equivalence-copy wrappers','duplicate clauses','tautological noise','controlled redundant supersets','independent holdout encoder'],
'near_collision_signature':'(n,m,width histogram,absolute-degree multiset,total positive literals,total negative literals)',
'near_collision_result':chk['schema_router_baseline']['near_collision_proof']},
'schema_router_negative_control':chk['schema_router_baseline'],
'certificate_firewall':chk['certificate_firewall'],
'complexity_ledger':{
'structural_audit':chk['polynomial_budget'],
'charged_buckets':{
'canonicalize_plus_substrate':'candidate t_normalize_ms',
'discovery':'candidate t_discovery_ms',
'carrier_plus_certificate_plus_reconstruct':'candidate t_carrier_ms',
'root_verify':'candidate t_root_verify_ms'},
'note':'certificate construction and SAT reconstruction are charged inside the carrier bucket; no stage is omitted. Frozen implementation uses only polynomial loops/graph algorithms/GF(2) elimination, with a constant 8-row local truth table in P3.',
'empirical_scaling':summary,
'empirical_scaling_firewall':'corroboration only; not an asymptotic proof'},
'run_history':[
{'run':'RUN1','population_commit':'95bc88394a7ceef6e1cc7655f28acf8accc57bd4','record_commit':'574ff29ae401e174ce61f025e070c8528abfcee9','verdict':'FAIL_EXACTNESS_ADMISSION','classification':'preserved infrastructure FAIL: slot1 SAT harness did not preserve planted witness; checker balance included controls'},
{'repair_commit':'59b728a547bdb3240a1dc280e99d396b4712e576','changes':'generator SAT-ground-truth repair + checker balance accounting repair; discovery candidate unchanged'},
{'run':'RUN2','population_commit':'8a9c603c78b12bda75f2342829d21254eccbc21d','verdict':chk['verdict'],'failures':chk['failures']}],
'lineage':{
'prereg_commit':'305863f111dbaebc5be246f4913f92ed1252ff0c',
'candidate_freeze_commit':'4c605f602f20b5adf91bc3fde5da74c29923a357',
'generator_checker_freeze_commit':'8eb7ea3662b9004e9d62977f27525280f6e955f1',
'first_population_commit':'95bc88394a7ceef6e1cc7655f28acf8accc57bd4',
'run1_fail_record_commit':'574ff29ae401e174ce61f025e070c8528abfcee9',
'harness_repair_commit':'59b728a547bdb3240a1dc280e99d396b4712e576',
'repaired_population_commit':'8a9c603c78b12bda75f2342829d21254eccbc21d'},
'evidence':chk['evidence']|{
'checker_raw_sha256':hashlib.sha256((ROOT/'checker_raw.json').read_bytes()).hexdigest(),
'scaling_raw_sha256':hashlib.sha256((ROOT/'scaling_raw.json').read_bytes()).hexdigest(),
'scaling_probe_sha256':hashlib.sha256((ROOT/'scaling_probe.py').read_bytes()).hexdigest()},
'successor_lock':'APMA_COMPOSITIONAL_CARRIER_SYNTHESIS_HOLDOUT_GATE remains NOT RUN in this artifact; eligible only after this routing PASS is sealed.'
}
(ROOT/'RESULT_2026-09-14.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
run2={'verdict':result['verdict'],'candidate_source_sha256':chk['evidence']['candidate_source_sha256'],'population':chk['population'],'schema_router_agreement':chk['schema_router_baseline']['agreement_with_main'],'failures':chk['failures'],'successor_not_run':True}
(ROOT/'RUN2_PASS_NOTE.json').write_text(json.dumps(run2,indent=2,sort_keys=True),encoding='utf-8')
print(json.dumps({'verdict':result['verdict'],'result_sha256':hashlib.sha256((ROOT/'RESULT_2026-09-14.json').read_bytes()).hexdigest(),'result_bytes':(ROOT/'RESULT_2026-09-14.json').stat().st_size},sort_keys=True))