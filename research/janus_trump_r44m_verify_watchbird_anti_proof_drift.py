#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'research' / 'JANUS_TRUMP_R44M_WATCHBIRD_ANTI_PROOF_DRIFT_CONTRACT_2026-09-03.json'

c = json.loads(CONTRACT.read_text())
laws = set(c['constitutional_laws'])
required = {
    'LEARNING_DELTA_THEOREM_AUTHORITY=0',
    'PROGRESS != PROOF',
    'SPECIAL_CASE_IN_P != 3SAT_IN_P',
    'FINITE_FIXTURE_PASS != UNIVERSAL_COVERAGE',
    'CONDITIONAL_BRIDGE != DISCHARGED_PREMISES',
    'UNKNOWN_OR_OPEN != NEGATIVE_AND != POSITIVE',
    'COUNTEREXAMPLE_TO_ROUTE != P_NE_NP',
    'NO_COUNTEREXAMPLE_FOUND != P_EQUALS_NP',
}
assert required <= laws

# Adversarial promotion attempts. Every one must remain unauthorized.
cases = [
    {'name':'finite_fixtures_only','universal':False,'poly':True,'exact':True,'independent':True},
    {'name':'specialized_route','universal':False,'poly':True,'exact':True,'independent':True},
    {'name':'conditional_bridge_open','universal':False,'poly':True,'exact':True,'independent':True},
    {'name':'hidden_exponential_compile','universal':True,'poly':False,'exact':True,'independent':True},
    {'name':'semantic_approximation','universal':True,'poly':True,'exact':False,'independent':True},
    {'name':'self_certified_only','universal':True,'poly':True,'exact':True,'independent':False},
]

def may_promote(x):
    return all(x[k] for k in ('universal','poly','exact','independent'))

for x in cases:
    assert may_promote(x) is False, x

# Positive control: this does not assert existence; it only checks that the gate would
# authorize promotion if all theorem obligations were actually discharged.
positive_control = {'universal':True,'poly':True,'exact':True,'independent':True}
assert may_promote(positive_control) is True

assert c['current_status']['P_VS_NP'] == 'OPEN'
assert c['current_status']['authority_delta'] == 0
assert 'UNKNOWN_RESOURCE_LIMIT' in c['anti_drift_runtime_policy']['on_timeout_or_resource_limit']
assert c['proof_authority_gate']['otherwise'] == 'P_VS_NP=OPEN'

print(json.dumps({
    'gate':'R44M_WATCHBIRD_ANTI_PROOF_DRIFT',
    'adversarial_cases_blocked':len(cases),
    'positive_control_gate_logic':True,
    'theorem_authority_delta':0,
    'P_VS_NP':'OPEN',
    'verdict':'PASS'
}, sort_keys=True))
