from __future__ import annotations

import json
from pathlib import Path

JOURNAL = Path('research/JANUS_TRUMP_R50G25_CHAIN_JOURNAL.json')
V_RECEIPT = Path('research/R50G25V_TWO_RESIDUAL_FORENSICS_RESULT_RECEIPT.json')
W_RECEIPT = Path('research/R50G25W_SA_BVE_POLICY_LIFT_RESULT_RECEIPT.json')

x = json.loads(JOURNAL.read_text())
v = json.loads(V_RECEIPT.read_text())
w = json.loads(W_RECEIPT.read_text())
entries = [e for e in x.get('entries', []) if e.get('gate') not in {'R50G25V', 'R50G25W'}]
entries.extend([v, w])
x['entries'] = entries
x['version'] = '2.0'
x.setdefault('policy', {})['append_only_intent'] = True
x['policy']['exact_ids_or_null_only'] = True
x['policy']['finite_success_is_not_universal_coverage'] = True
x['policy']['P_VS_NP'] = 'OPEN'
x['policy']['SAT_IN_P'] = 'NOT_PROVED'
x['policy']['TRUMP_finished'] = False
JOURNAL.write_text(json.dumps(x, indent=2, sort_keys=False) + '\n')
print(json.dumps({
    'version': x['version'],
    'entry_count': len(entries),
    'last_gates': [e['gate'] for e in entries[-3:]],
    'V_run': v['run_id'],
    'W_run': w['run_id'],
    'firewall': x['policy'],
}, indent=2, sort_keys=True))
