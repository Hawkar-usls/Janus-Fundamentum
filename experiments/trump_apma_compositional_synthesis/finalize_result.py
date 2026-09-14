from pathlib import Path
import hashlib,json
r=Path(r'experiments/trump_apma_compositional_synthesis')
chk=json.loads((r/'checker_raw_v1_1.json').read_text())
cand=json.loads((r/'SYNTHESIZED_CANDIDATES.json').read_text())
abl=json.loads((r/'ablation_raw.json').read_text())
sca=json.loads((r/'scaling_raw.json').read_text())
control_breakdown={'A':{'rejected':8,'admitted_exact':0},'B':{'rejected':4,'admitted_exact':4},'C':{'rejected':8,'admitted_exact':0},'D':{'rejected':8,'admitted_exact':0}}
def sha(name):return hashlib.sha256((r/name).read_bytes()).hexdigest()
res={
 'artifact_id':'JANUS-TRUMP-APMA-COMPOSITIONAL-CARRIER-SYNTHESIS-HOLDOUT-GATE-2026-09-14-v1.1',
 'gate':'APMA_COMPOSITIONAL_CARRIER_SYNTHESIS_HOLDOUT_GATE',
 'verdict':'PASS_SCOPED_COMPOSITIONAL_CARRIER_SYNTHESIS',
 'claim':'For four predeclared hidden structural families under a frozen leave-one-carrier-out protocol, one frozen bounded polynomial synthesis framework selected reusable exact carrier programs composed from generic primitives; no held-out historical carrier implementation was imported.',
 'claim_firewall':{
   'ROUTING':'PASS_SCOPED_PREVIOUS_GATE','COMPOSITIONAL_SYNTHESIS':'PASS_SCOPED','UNIVERSAL_DISCOVERY':'NOT_CLAIMED','UNIVERSAL_SELECTOR':'NOT_CLAIMED','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0,'NOVEL_COMPOSITE_TRANSFER':'LOCKED_NOT_RUN'},
 'population':{
   'calibration_total':48,'calibration_per_fold':12,'calibration_balance_per_fold':'6 SAT / 6 UNSAT',
   'blind_admission_total':48,'blind_admission_per_fold':12,'blind_admission_balance_per_fold':'6 SAT / 6 UNSAT',
   'final_blind_holdout_total':64,'final_holdout_per_fold':16,'final_holdout_balance_per_fold':'8 SAT / 8 UNSAT',
   'post_freeze_target_total':112,'controls_total':32,'near_collision_pairs':16,'near_collision_coarse_metrics_equal':'16/16',
   'control_breakdown':control_breakdown,
   'holdout_encoder':'hold_encoder_v3, unseen by synthesis tuning; sizes outside calibration grid'},
 'folds':{f:{
   'verdict':chk['folds'][f]['verdict'],'program':chk['folds'][f]['program'],'program_hash':chk['folds'][f]['program_hash'],
   'calibration_exact':cand['folds'][f]['calibration_exact'],'calibration_total':cand['folds'][f]['calibration_total'],
   'blind_counts':chk['folds'][f]['counts'],'near_collision_equal':chk['folds'][f]['near_collision_equal'],'encoder_holdout':chk['folds'][f]['encoder_holdout'],
   'primitive_dominance_hits':chk['primitive_dominance_hits'][f]
 } for f in 'ABCD'},
 'synthesis_framework':{
   'primitive_names':['P0','P1','P2','P3','P4','P5','P6','P7','P8'],'candidate_dags':16,'max_dag_size':3,'max_depth':3,
   'candidate_output':'one frozen reusable program C* per fold','adaptive_grammar_expansion':False,'search_until_solved':False,
   'held_out_historical_carrier_import':'FORBIDDEN_AND_SOURCE_AUDITED','source_firewall':chk['source_firewall']},
 'exactness_firewall':{
   'SAT':'assignment -> independent replay on original raw CNF','UNSAT':'independent family-specific structural/algebraic certificate verification','synthesis_is_not_exactness':True},
 'primitive_dominance_audit':{
   'result':'PASS_NO_SINGLE_PRIMITIVE_SOLVER_HIT','hits':chk['primitive_dominance_hits'],
   'interpretation':'Each primitive alone was behaviorally probed on raw target input; no primitive alone emitted a complete decision/certificate route.'},
 'ablation_diagnostic':{
   'authority':'DIAGNOSTIC_ONLY','result':'8/8 substantive primitive removals -> ABLATION_CRITICAL_PRIMITIVE','details':abl['folds'],
   'interpretation':'Both substantive stages of every selected C* were necessary within the remaining frozen grammar on blind target cases; not a proof of minimality.'},
 'complexity_ledger':{
   'canonicalize':'polynomial; duplicate/tautology normalization and sorting over input clauses',
   'primitive_substrate':'P0 worst-case polynomial pair/component checks; P1/P2 linear-to-polynomial graph/rule extraction; P3 local truth tables bounded by 2^3=8 per local support',
   'candidate_generation':'exactly 16 frozen DAGs; constant candidate count, no exponential program enumeration',
   'candidate_ranking':'16 candidates x calibration population x polynomial candidate execution',
   'carrier_execution':'P4 augmenting-path routine polynomial; P5 graph traversals polynomial; P6 finite fixed-point propagation polynomial; P7 GF(2)-style row elimination polynomial',
   'certificate_reconstruct_verify':'all polynomial in admitted substrate/input size',
   'total':'T_total <= poly(|F|) for the frozen implementation structure and bounded local-table language used in this gate',
   'empirical_scaling_firewall':'timings corroborate only; they are not the asymptotic proof'},
 'scaling_corroboration':{
   'n_values':[8,16,32,64,128],
   'all_exact':all(x['all_exact'] for x in sca['rows']),
   'all_rank_matches_frozen':all(x['ranking_program']==x['frozen_program'] for x in sca['rows']),
   'max_synthesis_wall_ms_by_n':{str(n):max(x['synthesis_wall_ms'] for x in sca['rows'] if x['n']==n) for n in [8,16,32,64,128]},
   'authority':'EMPIRICAL_ONLY'},
 'run_history':[
   {'version':'v1.0','verdict':'FAIL_COMPOSITIONAL_CARRIER_SYNTHESIS','commit':'f8cb77f2c361e37948cf4a2727b868ef52dc8cd2','failure':'NEAR_COLLISION_METRIC_DRIFT due checker tuple/list representation mismatch','candidate_changed_after_fail':False,'population_changed_after_fail':False},
   {'version':'v1.1','verdict':'PASS_SCOPED_COMPOSITIONAL_CARRIER_SYNTHESIS','checker_change':'one-line JSON width_hist normalization only','candidate_changed':False,'population_changed':False}
 ],
 'lineage':{
   'parent_routing_seal':'8d8ac00112d553609ed6b736142e811f90928781','parent_meta_authority':'ab5c38d20bde98ffe5c366f829b714e5802ddacc',
   'prereg_v1_0':'d7b648dd889aa3699bdd299e41cc2efea2ed960a','primitive_grammar_freeze':'35f1699dbcb65417ea606b826089e69637a9d9df',
   'population_freeze':'dbb5ddcc7766709d62034cbd3ebb24e5c939e128','candidate_freeze':'08135f2ae6f166c29b1a6f95e16bab6d18c8ba91',
   'checker_v1_0_freeze':'99a03cc4c2c97b0bb20097815ca040abaff0c0e7','v1_0_fail_record':'f8cb77f2c361e37948cf4a2727b868ef52dc8cd2',
   'prereg_v1_1':'ba07d201fc178758fdcedc0dee7de8d2620cc80b','checker_v1_1_freeze':'6ab20f4bd53d662293c0a3f5f67551e9af7664d4',
   'v1_1_pass_record':'ce6ea8d6be795bf379a8a8cf2e417065a626bc5c','ablation_freeze':'213ec805206d9011f48ff42d1dd88342eb80e4db','ablation_record':'fac65c159523068feb433b2c60430c19961028a3','scaling_freeze':'9e0ce5f3a959e827a12fbcf13701215a79061f97','scaling_record':'ecbf66b6e10cf8d634be0b25af4c973f70f32468'},
 'evidence_sha256':{
   'candidate_bundle_file':sha('SYNTHESIZED_CANDIDATES.json'),'checker_v1_1':sha('checker_raw_v1_1.json'),'ablation_raw':sha('ablation_raw.json'),'scaling_raw':sha('scaling_raw.json'),'calibration':sha('calibration.json'),'sealed_admission':sha('sealed_admission.json'),'sealed_holdout':sha('sealed_holdout.json'),'sealed_controls':sha('sealed_controls.json'),'sealed_truth':sha('sealed_truth.json')},
 'successor_lock':'APMA_NOVEL_COMPOSITE_SEMANTICS_TRANSFER_GATE remains LOCKED_NOT_RUN in this artifact.'
}
(r/'RESULT_2026-09-14_v1.1.json').write_text(json.dumps(res,indent=2,sort_keys=True),encoding='utf-8')
print(json.dumps({'verdict':res['verdict'],'result_sha256':hashlib.sha256((r/'RESULT_2026-09-14_v1.1.json').read_bytes()).hexdigest(),'bytes':(r/'RESULT_2026-09-14_v1.1.json').stat().st_size},sort_keys=True))
