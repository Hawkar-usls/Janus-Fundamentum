import json
from pathlib import Path

PATH = Path('research/JANUS_TRUMP_R44B_P_EQUALS_NP_BRIDGE_OBLIGATION_2026-09-03.json')
obj = json.loads(PATH.read_text())

assert obj['target_theorem'] == 'P_EQUALS_NP'
assert obj['current_verdict'] == 'BRIDGE_VALID_CONDITIONALLY__P_EQUALS_NP_NOT_PROVED'
assert obj['P_VS_NP'] == 'OPEN'

premises = {p['id']: p for p in obj['premises']}
required = {
    'U1_UNIVERSAL_TOTALITY',
    'U2_EXACT_SEMANTICS',
    'U3_POLYNOMIAL_LOCAL_COST',
    'U4_POLYNOMIAL_STATE_ENVELOPE',
    'U5_POLYNOMIAL_TERMINATION',
    'U6_END_TO_END_VERIFIER',
}
assert set(premises) == required

promotion = set(obj['promotion_rule']['P_EQUALS_NP_may_be_set_true_only_if'])
assert promotion == {
    'U1_PROVED', 'U2_PROVED', 'U3_PROVED', 'U4_PROVED', 'U5_PROVED', 'U6_PROVED'
}

# Fail closed: until every universal premise is PROVED, the theorem may not be promoted.
all_proved = all(p['status'] == 'PROVED' for p in premises.values())
assert all_proved is False
assert obj['promotion_rule']['finite_test_success_is_insufficient'] is True
assert obj['promotion_rule']['portfolio_coverage_on_benchmarks_is_insufficient'] is True
assert obj['promotion_rule']['single_counterexample_to_current_switchboard_does_not_imply_P_NE_NP'] is True

# Mechanical composition check for the conditional theorem structure.
derivation = ' '.join(obj['derivation'])
for needle in ['decides 3SAT in polynomial time', '3SAT is NP-complete', 'NP subseteq P', 'P = NP']:
    assert needle in derivation

print(json.dumps({
    'status': 'PASS',
    'bridge': '3SAT_IN_P => P_EQUALS_NP',
    'universal_premises_proved': False,
    'P_VS_NP': 'OPEN',
    'next_attack': obj['next_attack'],
}, sort_keys=True))
