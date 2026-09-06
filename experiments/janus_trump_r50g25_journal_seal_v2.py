from __future__ import annotations

import json
from pathlib import Path

PATH = Path('research/JANUS_TRUMP_R50G25_CHAIN_JOURNAL.json')

data = json.loads(PATH.read_text())
entries = [e for e in data.get('entries', []) if e.get('gate') not in {'R50G25V','R50G25W'}]
entries.extend([
    {
      "gate":"R50G25V","status":"SUCCESS","branch":"research/r50g25v-two-residual-fixpoint-forensics-alternate-door-2026-09-06","preregistration_commit":"695719e3937f89279cb077598707a9a569a0dc79","run_head_commit":"21c21a9ec50d73d4ea91d4c0fcc16f7e48acb04b","result_receipt_commit":"0bd1a4b1d3aba9b4f5dd6f55dd831438dfa8e31b","run_id":34044114670,"artifact":{"name":"janus-trump-r50g25v-two-residual-forensics","id":9992576787,"zip_sha256":"93c430c4995a4d804b89931aee2119d43cecd0dece6f0d3645ab65a0c8bd79db"},"verdict":"RESIDUAL_HAS_DESCENDING_EXACT_DP_DOOR_OUTSIDE_CURRENT_R33_POLICY","reproduced_residual_count":2,"multi_literal_RUP":{"residual_0_checked":54,"residual_0_found":0,"residual_1_checked":64,"residual_1_found":0},"residual_cores":[{"hash":"62704c498273163c542ea8abd726686195cb3bd8288e21836444571133293fc9","CLV":[18,50,10],"best_DP_var":15,"best_DP_after_CLV":[16,44,9],"strict_descent":True,"downstream_terminal":"DIRECT_EMPTY_CNF"},{"hash":"8671c49c61798c3cdea7bcd51e313cb53bb47872f8604b48227aaeb4ee0f6342","CLV":[19,54,11],"best_DP_var":22,"best_DP_after_CLV":[18,52,10],"strict_descent":True,"downstream_terminal":"DIRECT_EMPTY_CNF"}],"mechanistic_explanation":"R33 legacy BVE tests raw-resolvent replacement before subsumption-aware minimization; R42/R45 exact DP applies subsumption_minimize(pool) before descent test.","next_gate":"R50G25W_R42_SA_BVE_POLICY_LIFT_OR_COUNTEREXAMPLE"
    },
    {
      "gate":"R50G25W","status":"SUCCESS","branch":"research/r50g25w-r42-sa-bve-policy-lift-outer-replay-2026-09-06","preregistration_commit":"b10247ac6b86480de67ffac8194dfab416988d91","run_head_commit":"597d38b2ee361c65c7392e26a42e9e7a79fdc36a","result_receipt_commit":"a087a39211327075d9344808872e626bff8fa624","run_id":34044471849,"artifact":{"name":"janus-trump-r50g25w-sa-bve-policy-lift","id":9992684695,"zip_sha256":"e89a50084daec41b3e91eaadaf4e111b96b3a98e4bedaa34370454be0bc8d1e9"},"verdict":"SA_BVE_POLICY_LIFT_REPAIRS_V_RESIDUALS_AND_COMBINED_OUTER_REPLAY","combined_domain_count":138,"old_residual_count":4,"new_residual_count":0,"semantic_disagreement_on_previously_decided_count":0,"SAT_reconstruction_failure_count":0,"SA_BVE_application_histogram":{"0":134,"1":4},"SA_BVE_total_applications":4,"V_core_repairs":[{"core_hash":"62704c498273163c542ea8abd726686195cb3bd8288e21836444571133293fc9","pivot":15,"CLV_before":[18,50,10],"CLV_after":[16,44,9],"terminal":"DIRECT_EMPTY_CNF"},{"core_hash":"8671c49c61798c3cdea7bcd51e313cb53bb47872f8604b48227aaeb4ee0f6342","pivot":22,"CLV_before":[19,54,11],"CLV_after":[18,52,10],"terminal":"DIRECT_EMPTY_CNF"}],"next_gate":"R50G25X_UNIVERSAL_COMPLETENESS_OBLIGATION_AND_ADVERSARIAL_STALL_SEARCH"
    }
])
data['version'] = '2.0'
data['entries'] = entries
data.setdefault('policy', {})['P_VS_NP'] = 'OPEN'
data['policy']['SAT_IN_P'] = 'NOT_PROVED'
data['policy']['TRUMP_finished'] = False
data['policy']['finite_success_is_not_universal_coverage'] = True
PATH.write_text(json.dumps(data, indent=2, sort_keys=False) + '\n')
print(json.dumps({'version':data['version'],'entry_count':len(entries),'last_gates':[e['gate'] for e in entries[-3:]],'firewall':data['policy']},indent=2,sort_keys=True))
