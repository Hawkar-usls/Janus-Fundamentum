from __future__ import annotations

import base64
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_SOURCE_EXTENSION_SELECTION_PREREGISTRATION_2026-09-17.json'
EXPECTED_PREREG_BLOB = '9679bed3017df016002a10aa45ba249df198baa4'

SOURCES = {
    'UF20_06': {
        'filename': 'uf20-06.cnf',
        'local': ROOT / 'research/source_data/SATLIB_UF20_06_2026-09-17.cnf',
        'local_blob': '42d6feffa98dc1a213e019f28cf6bc7ddf94c0bf',
        'primary_repo': 'Jany26/tree-aut-lib',
        'primary_blob': '42d6feffa98dc1a213e019f28cf6bc7ddf94c0bf',
        'verification_repo': 'dncarley/MolecularSimulation',
        'verification_blob': '721a31c31419ea920ae672cc879dfaa8b07bd98c',
    },
    'UF20_07': {
        'filename': 'uf20-07.cnf',
        'local': ROOT / 'research/source_data/SATLIB_UF20_07_2026-09-17.cnf',
        'local_blob': '9d7c4412e43bfd0e573ce8deab39c9d6e14d10b6',
        'primary_repo': 'Jany26/tree-aut-lib',
        'primary_blob': '9d7c4412e43bfd0e573ce8deab39c9d6e14d10b6',
        'verification_repo': 'dncarley/MolecularSimulation',
        'verification_blob': '75ca893b20054ecd7819426b5ffabb5fee4b2f26',
    },
    'UF20_08': {
        'filename': 'uf20-08.cnf',
        'local': ROOT / 'research/source_data/SATLIB_UF20_08_2026-09-17.cnf',
        'local_blob': '461108f1c8f2eddeab2d8a902b1bc1d2c9b03e3e',
        'primary_repo': 'Jany26/tree-aut-lib',
        'primary_blob': '461108f1c8f2eddeab2d8a902b1bc1d2c9b03e3e',
        'verification_repo': 'dncarley/MolecularSimulation',
        'verification_blob': 'a37c997e4a9d1efaceddde48d65c709fa13a82c1',
    },
    'UF20_09': {
        'filename': 'uf20-09.cnf',
        'local': ROOT / 'research/source_data/SATLIB_UF20_09_2026-09-17.cnf',
        'local_blob': '0dc336cbc82430deb22f64fdfb8c051c7493e5a0',
        'primary_repo': 'Jany26/tree-aut-lib',
        'primary_blob': '0dc336cbc82430deb22f64fdfb8c051c7493e5a0',
        'verification_repo': 'dncarley/MolecularSimulation',
        'verification_blob': 'a0c29bfed8c034ef817ee3c83de7b327d3d5db30',
    },
    'UF20_010': {
        'filename': 'uf20-010.cnf',
        'local': ROOT / 'research/source_data/SATLIB_UF20_010_2026-09-17.cnf',
        'local_blob': 'afe1163b633a9f1844e20010f77e8f2d94bd52c5',
        'primary_repo': 'Jany26/tree-aut-lib',
        'primary_blob': 'afe1163b633a9f1844e20010f77e8f2d94bd52c5',
        'verification_repo': 'dncarley/MolecularSimulation',
        'verification_blob': '61a315ceafdcae95d00097c057119fa8183bf4e7',
    },
}
ORDER = ('UF20_06', 'UF20_07', 'UF20_08', 'UF20_09', 'UF20_010')


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_blob(repo: str, blob_sha: str) -> bytes:
    url = f'https://api.github.com/repos/{repo}/git/blobs/{blob_sha}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Janus-Fundamentum-source-freeze/1.0', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode('utf-8'))
    if payload.get('sha') != blob_sha or payload.get('encoding') != 'base64':
        raise RuntimeError(f'blob fetch mismatch for {repo}@{blob_sha}')
    return base64.b64decode(payload['content'])


def parse_dimacs(data: bytes) -> dict[str, Any]:
    text = data.decode('utf-8')
    nvars = None
    declared = None
    clauses: list[list[int]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('c') or line == '%' or line == '0':
            continue
        if line.startswith('p '):
            parts = line.split()
            if len(parts) != 4 or parts[0] != 'p' or parts[1] != 'cnf':
                raise ValueError(f'bad DIMACS header: {line!r}')
            nvars, declared = int(parts[2]), int(parts[3])
            continue
        vals = [int(x) for x in line.split()]
        if not vals or vals[-1] != 0:
            raise ValueError(f'clause missing terminator: {line!r}')
        clause = vals[:-1]
        if len(clause) != 3:
            raise ValueError(f'non-ternary clause: {clause!r}')
        clauses.append(clause)
    if nvars is None or declared is None:
        raise ValueError('missing header')
    if len(clauses) != declared:
        raise ValueError((len(clauses), declared))
    if any(abs(lit) < 1 or abs(lit) > nvars for c in clauses for lit in c):
        raise ValueError('literal outside variable range')
    canonical = ''.join(' '.join(str(x) for x in c) + ' 0\n' for c in clauses).encode('ascii')
    return {
        'variables': nvars,
        'declared_clauses': declared,
        'clauses': clauses,
        'canonical_formula_sha256': sha256(canonical),
    }


def guard() -> dict[str, Any]:
    prereg_data = PREREG.read_bytes()
    pre = json.loads(prereg_data.decode('utf-8'))
    local_bindings = {name: git_blob_sha(spec['local'].read_bytes()) == spec['local_blob'] for name, spec in SOURCES.items()}
    checks = {
        'prereg_blob': git_blob_sha(prereg_data) == EXPECTED_PREREG_BLOB,
        'status': pre.get('status') == 'FROZEN_BEFORE_UNSEEN_SOURCE_CONTENT_ACQUISITION_OR_ANY_L3_S3_VALUE_COMPUTATION',
        'selection_exact': tuple(pre.get('neutral_selection_rule', {}).get('selected_unseen_sources', ())) == ORDER,
        'local_bindings': all(local_bindings.values()),
    }
    return {'ok': all(checks.values()), 'checks': checks, 'local_bindings': local_bindings}


def main() -> dict[str, Any]:
    g = guard()
    if not g['ok']:
        return {'verdict': 'HALT_SOURCE_ACQUISITION_BINDING_FAILURE', 'guard': g}
    rows = []
    for name in ORDER:
        spec = SOURCES[name]
        primary = fetch_blob(spec['primary_repo'], spec['primary_blob'])
        verification = fetch_blob(spec['verification_repo'], spec['verification_blob'])
        local = spec['local'].read_bytes()
        p = parse_dimacs(primary)
        v = parse_dimacs(verification)
        l = parse_dimacs(local)
        valid_shape = p['variables'] == v['variables'] == l['variables'] == 20 and p['declared_clauses'] == v['declared_clauses'] == l['declared_clauses'] == 91 and len(p['clauses']) == 91
        ordered_equal = p['clauses'] == v['clauses'] == l['clauses']
        primary_blob_ok = git_blob_sha(primary) == spec['primary_blob']
        verification_blob_ok = git_blob_sha(verification) == spec['verification_blob']
        local_blob_ok = git_blob_sha(local) == spec['local_blob']
        row_ok = valid_shape and ordered_equal and primary_blob_ok and verification_blob_ok and local_blob_ok
        rows.append({
            'source': name,
            'filename': spec['filename'],
            'status': 'SOURCE_FROZEN' if row_ok else 'SOURCE_MISMATCH',
            'variables': p['variables'],
            'clauses': p['declared_clauses'],
            'clause_arity': 3,
            'ordered_clause_sequence_equal_across_primary_verification_and_committed_copy': ordered_equal,
            'primary_repo': spec['primary_repo'],
            'primary_git_blob': spec['primary_blob'],
            'primary_raw_sha256': sha256(primary),
            'verification_repo': spec['verification_repo'],
            'verification_git_blob': spec['verification_blob'],
            'verification_raw_sha256': sha256(verification),
            'committed_git_blob': spec['local_blob'],
            'committed_raw_sha256': sha256(local),
            'canonical_formula_sha256': p['canonical_formula_sha256'],
            'canonical_formula_sha256_equal_across_all_three': p['canonical_formula_sha256'] == v['canonical_formula_sha256'] == l['canonical_formula_sha256'],
            'raw_bytes_primary_equal_committed_copy': primary == local,
            'raw_bytes_primary_equal_verification_mirror': primary == verification,
        })
    passed = all(r['status'] == 'SOURCE_FROZEN' and r['canonical_formula_sha256_equal_across_all_three'] for r in rows)
    return {
        'artifact_id': 'JANUS-TRUMP-SATLIB-UF20-R000-R111-UNSEEN-SOURCE-ACQUISITION-FREEZE-CANDIDATE-2026-09-17-v1.0',
        'authority': 'SOURCE_ACQUISITION_AND_HASH_FREEZE_ONLY__NO_L3_S3_VALUE_COMPUTATION',
        'verdict': 'PASS_UNSEEN_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FORMULA_FREEZE' if passed else 'HALT_SOURCE_ACQUISITION_MIRROR_OR_SHAPE_MISMATCH',
        'guard': g,
        'rows': rows,
        'resource_receipt': {
            'sources': 5,
            'remote_blob_fetches': 10,
            'L3_values_computed': 0,
            'S3_values_computed': 0,
            'projected_partition_relations_computed': 0,
            'solver_invocations': 0,
            'portfolio_replays': 0,
            'action_tests': 0,
            'group_searches': 0,
            'group_closure_computation': 0,
            'new_feature_definitions': 0,
            'new_graph_statistics': 0,
        },
        'scientific_firewall': {
            'P_VS_NP': 'OPEN',
            'GENERAL_SAT_IN_P': 'NOT_PROVED',
            'GENERAL_GT2_TRACTABILITY': 'NOT_PROVED',
            'CONNECTED_MIXED_CORE_SOLVED': 'NO',
            'L3_GENERALIZES': 'NOT_PROVED',
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
