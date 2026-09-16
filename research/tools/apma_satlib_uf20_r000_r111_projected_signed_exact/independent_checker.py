from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_PREREGISTRATION_2026-09-16.json'
SOURCES = {
    'UF20_01': ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf',
    'UF20_02': ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
    'UF20_03': ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
    'UF20_04': ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
    'UF20_05': ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf',
}


def source_authority(path: Path, variables: list[int]) -> dict[str, Any]:
    V = list(variables)
    adj = {v:set() for v in V}
    p, n = Counter(), Counter()
    selected = []
    for clause in projection_identity.parse(path):
        rid = projection_identity.rid(clause)
        if rid not in {'000','111'}:
            continue
        scope = sorted(abs(x) for x in clause)
        selected.append((tuple(scope), (0,0,0) if rid == '000' else (1,1,1)))
        for u,v in itertools.combinations(scope,2):
            adj[u].add(v); adj[v].add(u)
        for v in scope:
            (p if rid == '000' else n)[v] += 1
    assert sorted({v for scope,_ in selected for v in scope}) == V
    ordered = {v:(p[v],n[v]) for v in V}
    unsigned = {v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in V}
    groups: dict[tuple[int,int,int], list[int]] = defaultdict(list)
    for v in V:
        groups[unsigned[v]].append(v)
    classes = [sorted(xs) for xs in groups.values()]
    classes.sort(key=lambda xs:(xs[0],len(xs),xs))
    balanced = sorted(v for v in V if p[v] == n[v])
    perm = math.prod(math.factorial(len(c)) for c in classes)
    eps = 1 << len(balanced)
    return {
        'variables':V,'ordered_p_n':ordered,'unsigned_classes':classes,
        'balanced_variables':balanced,'permutation_candidates':perm,
        'epsilon_multiplicity':eps,'residual_action_count':perm*eps,
        'forbidden_multiset':Counter(selected),
    }


def descriptor(V: list[int], sigma: dict[int,int], eps: dict[int,int]) -> dict[str, Any]:
    return {
        'sigma_images':[sigma[v] for v in V],
        'epsilon_bits':[eps[v] for v in V],
        'moves':[[v,sigma[v]] for v in V if sigma[v] != v],
        'flips':[v for v in V if eps[v] == 1],
        'identity':all(sigma[v] == v for v in V) and all(eps[v] == 0 for v in V),
    }


def generate(authority: dict[str, Any], frozen: dict[str, Any]) -> list[dict[str, Any]]:
    V = authority['variables']
    classes = frozen['unsigned_classes']
    balanced_sorted = sorted(frozen['balanced_variables'])
    balanced = set(balanced_sorted)
    ordered = authority['ordered_p_n']
    out = []
    for choices in itertools.product(*(list(itertools.permutations(cls)) for cls in classes)):
        sigma = {v:v for v in V}
        for cls,images in zip(classes,choices,strict=True):
            for old,new in zip(cls,images,strict=True):
                sigma[old] = new
        forced = {}
        for v in V:
            if v in balanced:
                continue
            w = sigma[v]; src = ordered[v]; dst = ordered[w]
            if dst == src:
                forced[v] = 0
            elif dst == (src[1],src[0]):
                forced[v] = 1
            else:
                raise AssertionError(('epsilon-incompatible',v,w,src,dst))
        for bits in itertools.product((0,1), repeat=len(balanced_sorted)):
            eps = dict(forced)
            for v,b in zip(balanced_sorted,bits,strict=True):
                eps[v] = b
            out.append(descriptor(V,sigma,eps))
    return out


def transported_forbidden(original: Counter, V: list[int], action: dict[str, Any]) -> Counter:
    sigma = {v:w for v,w in zip(V,action['sigma_images'],strict=True)}
    eps = {v:b for v,b in zip(V,action['epsilon_bits'],strict=True)}
    out = Counter()
    for (scope,forbidden), multiplicity in original.items():
        moved = {sigma[v]: int(bit) ^ eps[v] for v,bit in zip(scope,forbidden,strict=True)}
        target_scope = tuple(sorted(moved))
        target_forbidden = tuple(moved[v] for v in target_scope)
        out[(target_scope,target_forbidden)] += multiplicity
    return out


def independent_row(name: str, path: Path, frozen: dict[str, Any]) -> dict[str, Any]:
    auth = source_authority(path,frozen['variables'])
    assert auth['unsigned_classes'] == frozen['unsigned_classes']
    assert auth['balanced_variables'] == frozen['balanced_variables']
    assert auth['permutation_candidates'] == frozen['permutation_candidates']
    assert auth['epsilon_multiplicity'] == frozen['epsilon_multiplicity']
    assert auth['residual_action_count'] == frozen['residual_action_count']
    actions = generate(auth,frozen)
    assert len(actions) == frozen['residual_action_count']
    positives = []
    original = auth['forbidden_multiset']
    for ordinal,action in enumerate(actions):
        if transported_forbidden(original,auth['variables'],action) == original:
            positives.append({'action_ordinal':ordinal,**action})
    identities = sum(1 for x in positives if x['identity'])
    nonidentity = [x for x in positives if not x['identity']]
    return {
        'source':name,'generated_action_count':len(actions),'exact_actions_tested':len(actions),
        'identity_positive_count':identities,'exact_signed_automorphism_count':len(positives),
        'nonidentity_exact_signed_automorphism_count':len(nonidentity),
        'nonidentity_exact_signed_automorphisms':nonidentity,
    }


def main(candidate: dict[str, Any]) -> dict[str, Any]:
    pre = json.loads(PREREG.read_text())
    frozen = {r['source']:r for r in pre['frozen_projected_residual_authority']}
    candidate_rows = {r['source']:r for r in candidate.get('rows',[])}
    independent = {name:independent_row(name,path,frozen[name]) for name,path in SOURCES.items()}
    checks = {
        'candidate_not_imported':True,
        'candidate_source_set':set(candidate_rows) == set(SOURCES),
        'candidate_total_exact_actions':candidate.get('total_exact_actions_tested') == 15808,
    }
    for name in SOURCES:
        c = candidate_rows.get(name,{})
        i = independent[name]
        checks[f'{name}_generated_count'] = c.get('generated_action_count') == i['generated_action_count']
        checks[f'{name}_tested_count'] = c.get('exact_actions_tested') == i['exact_actions_tested']
        checks[f'{name}_identity_count'] = c.get('identity_positive_count') == i['identity_positive_count']
        checks[f'{name}_automorphism_count'] = c.get('exact_signed_automorphism_count') == i['exact_signed_automorphism_count']
        checks[f'{name}_nonidentity_count'] = c.get('nonidentity_exact_signed_automorphism_count') == i['nonidentity_exact_signed_automorphism_count']
        checks[f'{name}_nonidentity_witnesses'] = c.get('nonidentity_exact_signed_automorphisms') == i['nonidentity_exact_signed_automorphisms']
    total_nonid = sum(x['nonidentity_exact_signed_automorphism_count'] for x in independent.values())
    expected_verdict = 'NONIDENTITY_PROJECTED_SIGNED_AUTOMORPHISM_WITNESS_FOUND' if total_nonid else 'PASS_PROJECTED_SIGNED_GROUP_TRIVIAL_ON_ALL_FIVE'
    checks['candidate_verdict'] = candidate.get('verdict') == expected_verdict
    rr = candidate.get('resource_receipt',{})
    checks['resources'] = (
        rr.get('exact_action_tests') == 15808 and rr.get('actions_outside_frozen_residual_set_tested') == 0
        and rr.get('group_closure_computation') == 0 and rr.get('quotient_states_enumerated') == 0
        and rr.get('solver_invocations') == 0 and rr.get('new_signature_features') == 0
        and rr.get('new_invariants') == 0 and rr.get('new_group_search_mechanisms') == 0
        and rr.get('new_solver_mechanisms') == 0 and rr.get('new_carrier_mechanisms') == 0
        and rr.get('new_adapters') == 0 and rr.get('new_quotients') == 0 and rr.get('budget_raise') is False
    )
    sf = candidate.get('scientific_firewall',{})
    checks['firewall'] = sf.get('P_VS_NP') == 'OPEN' and sf.get('GENERAL_SAT_IN_P') == 'NOT_PROVED' and sf.get('NEW_INVARIANT_LICENSED') is False
    return {
        'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SIGNED-RESIDUAL-EXACT-INDEPENDENT-CHECK-2026-09-16-v1.0',
        'candidate_imported':False,
        'comparison_model':'SOURCE_BOUND_UNIQUE_FORBIDDEN_TUPLE_MULTISET_TRANSPORT',
        'verified':all(checks.values()),'checks':checks,
        'independent_rows':[independent[name] for name in SOURCES],
        'independent_total_exact_actions_tested':sum(x['exact_actions_tested'] for x in independent.values()),
        'independent_total_nonidentity_exact_signed_automorphisms':total_nonid,
        'independent_expected_verdict':expected_verdict,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate-json',required=True)
    args = ap.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text().strip().splitlines()[-1])
    out = main(candidate)
    print(json.dumps(out,sort_keys=True,separators=(',',':')))
    raise SystemExit(0 if out['verified'] else 1)
