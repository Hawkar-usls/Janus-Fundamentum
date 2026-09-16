from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_PREREGISTRATION_2026-09-16_v1.1.json'
V11 = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_BOUND_RESULT_2026-09-16_v1.1.json'
EXPECTED = {
    PREREG: 'd801cf79f6dfbaa25b284967867a7e0b59b67ed4',
    V11: '4ca743fffe93deb597aed0d78fec94fb77220a4d',
    ROOT / 'research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_DIRECT_PROOF_2026-09-16.md': 'e1515e047e53535882913d3764425814290f3334',
    ROOT / 'research/TRUMP_SATLIB_UF20_SIGNED_EPSILON_DETERMINATION_DIRECT_PROOF_2026-09-16.md': 'adfa4b1dd935109e5593fba7509d37ba5fe0400b',
    ROOT / 'research/tools/apma_satlib_uf20_signed_residual_exact_certificate/certificate.py': 'cae7f3b1713e36c5fda7744e5defb0b9e73db181',
    ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py': '2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
SOURCES = {
    'UF20_01': (ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
    'UF20_02': (ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
CUBE = tuple(itertools.product((0,1), repeat=3))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def canonical_sha(raw: Any) -> str:
    return hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode()).hexdigest()


def unique_forbidden(c: dict[str, Any]) -> tuple[int,int,int]:
    allowed = {tuple(int(x) for x in row) for row in c['allowed']}
    missing = set(CUBE) - allowed
    if len(c['scope']) != 3 or len(allowed) != 7 or len(missing) != 1:
        raise ValueError('NON_SINGLE_FORBIDDEN_TUPLE_RELATION_FOUND')
    return next(iter(missing))


def recompute_authority(raw: dict[str, Any]) -> dict[str, Any]:
    V = list(raw['variables'])
    adj = {v:set() for v in V}
    p, n = Counter(), Counter()
    for c in raw['constraints']:
        f = unique_forbidden(c)
        scope = list(c['scope'])
        for u,v in itertools.combinations(scope,2):
            adj[u].add(v); adj[v].add(u)
        for v,b in zip(scope,f,strict=True):
            (p if b == 0 else n)[v] += 1
    ordered = {v:(p[v],n[v]) for v in V}
    unsigned = {v:(len(adj[v]), min(p[v],n[v]), max(p[v],n[v])) for v in V}
    groups: dict[tuple[int,int,int], list[int]] = defaultdict(list)
    for v in V:
        groups[unsigned[v]].append(v)
    classes = [sorted(xs) for xs in groups.values()]
    classes.sort(key=lambda xs:(xs[0],len(xs),xs))
    balanced = sorted(v for v in V if p[v] == n[v])
    perm_count = math.prod(math.factorial(len(c)) for c in classes)
    eps_mult = 1 << len(balanced)
    return {
        'variables': V,
        'ordered_p_n': ordered,
        'unsigned_classes': classes,
        'balanced_variables': balanced,
        'permutation_candidates': perm_count,
        'epsilon_multiplicity': eps_mult,
        'residual_action_count': perm_count * eps_mult,
    }


def action_descriptor(V: list[int], sigma: dict[int,int], eps: dict[int,int]) -> dict[str, Any]:
    images = [sigma[v] for v in V]
    bits = [eps[v] for v in V]
    return {
        'sigma_images': images,
        'epsilon_bits': bits,
        'moves': [[v,sigma[v]] for v in V if sigma[v] != v],
        'flips': [v for v in V if eps[v] == 1],
        'identity': all(sigma[v] == v for v in V) and all(eps[v] == 0 for v in V),
    }


def generate_actions(authority: dict[str, Any], frozen: dict[str, Any]) -> list[dict[str, Any]]:
    V = authority['variables']
    classes = frozen['unsigned_classes']
    balanced = set(frozen['balanced_variables'])
    ordered = authority['ordered_p_n']
    class_permutations = [list(itertools.permutations(cls)) for cls in classes]
    actions: list[dict[str, Any]] = []
    balanced_sorted = sorted(balanced)
    for choices in itertools.product(*class_permutations):
        sigma = {v:v for v in V}
        for cls, image_tuple in zip(classes, choices, strict=True):
            for old, new in zip(cls, image_tuple, strict=True):
                sigma[old] = new
        forced: dict[int,int] = {}
        for v in V:
            if v in balanced:
                continue
            w = sigma[v]
            src = ordered[v]
            dst = ordered[w]
            if dst == src:
                forced[v] = 0
            elif dst == (src[1],src[0]):
                forced[v] = 1
            else:
                raise ValueError(f'EPSILON_COUNTING_COMPATIBILITY_FAILURE:{v}->{w}:{src}:{dst}')
        for free_bits in itertools.product((0,1), repeat=len(balanced_sorted)):
            eps = dict(forced)
            for v,b in zip(balanced_sorted, free_bits, strict=True):
                eps[v] = b
            actions.append(action_descriptor(V,sigma,eps))
    return actions


def explicit_multiset(raw: dict[str, Any]) -> Counter:
    out = Counter()
    for c in raw['constraints']:
        scope = tuple(int(v) for v in c['scope'])
        rows = tuple(sorted(tuple(int(b) for b in row) for row in c['allowed']))
        out[(scope,rows)] += 1
    return out


def transported_multiset(raw: dict[str, Any], V: list[int], action: dict[str, Any]) -> Counter:
    sigma = {v:w for v,w in zip(V, action['sigma_images'], strict=True)}
    eps = {v:b for v,b in zip(V, action['epsilon_bits'], strict=True)}
    out = Counter()
    for c in raw['constraints']:
        old_scope = list(c['scope'])
        target_scope = tuple(sorted(sigma[v] for v in old_scope))
        rows = []
        for row in c['allowed']:
            moved = {sigma[v]: int(bit) ^ eps[v] for v,bit in zip(old_scope,row,strict=True)}
            rows.append(tuple(moved[v] for v in target_scope))
        out[(target_scope, tuple(sorted(rows)))] += 1
    return out


def exact_test(raw: dict[str, Any], actions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    original = explicit_multiset(raw)
    positives = []
    tested = 0
    for ordinal, action in enumerate(actions):
        tested += 1
        if transported_multiset(raw, list(raw['variables']), action) == original:
            positives.append({'action_ordinal':ordinal, **action})
    return positives, tested


def main() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == sha for p,sha in EXPECTED.items()}
    source_bindings = {name: blob(path) == sha for name,(path,sha) in SOURCES.items()}
    if not all(bindings.values()) or not all(source_bindings.values()):
        return {'verdict':'PROJECTED_RAW_OR_BINDING_GUARD_FAILURE','source_guard':{'ok':False,'bindings':bindings,'source_bindings':source_bindings}}
    pre = json.loads(PREREG.read_text())
    v10 = json.loads((ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_PREREGISTRATION_2026-09-16.json').read_text())
    frozen = {r['source']:r for r in v10['frozen_projected_residual_authority']}
    rows = []
    total_tested = 0
    try:
        for name,(path,_) in SOURCES.items():
            raw,_ = projection_identity.normalize_projection(name, projection_identity.parse(path))
            f = frozen[name]
            raw_sha = canonical_sha(raw)
            auth = recompute_authority(raw)
            authority_match = (
                raw_sha == f['raw_sha256'] and auth['variables'] == f['variables'] and
                auth['unsigned_classes'] == f['unsigned_classes'] and
                auth['balanced_variables'] == f['balanced_variables'] and
                auth['permutation_candidates'] == f['permutation_candidates'] and
                auth['epsilon_multiplicity'] == f['epsilon_multiplicity'] and
                auth['residual_action_count'] == f['residual_action_count']
            )
            if not authority_match:
                return {'verdict':'RESIDUAL_GENERATION_COUNT_OR_AUTHORITY_MISMATCH','source':name,'raw_sha256':raw_sha,'recomputed':{k:v for k,v in auth.items() if k!='ordered_p_n'},'frozen':f,'exact_actions_tested':0}
            actions = generate_actions(auth,f)
            generated = len(actions)
            if generated != f['residual_action_count']:
                return {'verdict':'RESIDUAL_GENERATION_COUNT_OR_AUTHORITY_MISMATCH','source':name,'generated':generated,'expected':f['residual_action_count'],'exact_actions_tested':0}
            positives,tested = exact_test(raw,actions)
            total_tested += tested
            identity_count = sum(1 for x in positives if x['identity'])
            nonidentity = [x for x in positives if not x['identity']]
            rows.append({
                'source':name,'raw_sha256':raw_sha,
                'generated_action_count':generated,'exact_actions_tested':tested,
                'identity_positive_count':identity_count,
                'exact_signed_automorphism_count':len(positives),
                'nonidentity_exact_signed_automorphism_count':len(nonidentity),
                'nonidentity_exact_signed_automorphisms':nonidentity,
            })
    except ValueError as e:
        return {'verdict':'RESIDUAL_GENERATION_COUNT_OR_AUTHORITY_MISMATCH','error':str(e),'exact_actions_tested':total_tested}
    if total_tested != pre['resource_constraints']['expected_exact_action_tests']:
        return {'verdict':'RESIDUAL_GENERATION_COUNT_OR_AUTHORITY_MISMATCH','exact_actions_tested':total_tested,'expected':pre['resource_constraints']['expected_exact_action_tests']}
    if any(r['identity_positive_count'] != 1 for r in rows):
        verdict = 'IDENTITY_POSITIVE_CONTROL_FAILURE'
    elif any(r['nonidentity_exact_signed_automorphism_count'] > 0 for r in rows):
        verdict = 'NONIDENTITY_PROJECTED_SIGNED_AUTOMORPHISM_WITNESS_FOUND'
    else:
        verdict = 'PASS_PROJECTED_SIGNED_GROUP_TRIVIAL_ON_ALL_FIVE'
    return {
        'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SIGNED-RESIDUAL-EXACT-CERTIFICATE-2026-09-16-v1.1',
        'authority':'DIAGNOSTIC_FINITE_EXACT_REPLAY_OF_ALREADY_PROVED_SIGNED_ACTION_SEMANTICS_ONLY__NO_SIGNED_QUOTIENT_NEW_GROUP_SEARCH_SOLVER_OR_CARRIER',
        'verdict':verdict,
        'source_guard':{'ok':True,'bindings':bindings,'source_bindings':source_bindings},
        'rows':rows,
        'total_exact_actions_tested':total_tested,
        'total_nonidentity_exact_signed_automorphisms':sum(r['nonidentity_exact_signed_automorphism_count'] for r in rows),
        'resource_receipt':{
            'expected_exact_action_tests':15808,'exact_action_tests':total_tested,
            'actions_outside_frozen_residual_set_tested':0,'group_closure_computation':0,
            'quotient_states_enumerated':0,'solver_invocations':0,'new_signature_features':0,
            'new_invariants':0,'new_group_search_mechanisms':0,'new_solver_mechanisms':0,
            'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False,
        },
        'scientific_firewall':{
            'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED',
            'CONNECTED_MIXED_CORE_SOLVED':'NO','SIGNED_SYMMETRY_IMPLIES_TRACTABILITY':False,
            'SIGNED_ASYMMETRY_IMPLIES_HARDNESS':False,'NEW_INVARIANT_LICENSED':False,
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(),sort_keys=True,separators=(',',':')))
