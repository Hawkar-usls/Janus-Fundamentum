from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORDER = tuple(f'UF20_{i:03d}' for i in range(16, 26))
PRIMARY_REPO = 'Jany26/tree-aut-lib'
PRIMARY_COMMIT = '6cd58ade6de0a5c05511deb76c261ee75356ff31'
PRIMARY_TEMPLATE = 'benchmark/dimacs/uf20/uf20-{nnn}.cnf'
VERIFY_REPO = 'dncarley/MolecularSimulation'
VERIFY_COMMIT = 'd23a1d1775a939af0a6032ec459e5055919843a7'
VERIFY_TEMPLATE = 'data/uf20-91/uf20-{nnn}.cnf'


def blob(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(repo: str, commit: str, path: str) -> bytes:
    url = f'https://raw.githubusercontent.com/{repo}/{commit}/{path}'
    request = urllib.request.Request(url, headers={'User-Agent': 'Janus-Fundamentum-UF20-016-025-independent-check/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def parse(data: bytes) -> dict[str, Any]:
    nvars = None
    nclauses = None
    clauses: list[tuple[int, int, int]] = []
    for line in data.decode('utf-8').splitlines():
        s = line.strip()
        if not s or s.startswith('c') or s in {'%', '0'}:
            continue
        if s.startswith('p '):
            fields = s.split()
            assert fields[:2] == ['p', 'cnf'] and len(fields) == 4
            nvars, nclauses = int(fields[2]), int(fields[3])
            continue
        values = [int(x) for x in s.split()]
        assert values[-1] == 0
        values = values[:-1]
        assert len(values) == 3 and len({abs(x) for x in values}) == 3
        assert all(1 <= abs(x) <= 20 for x in values)
        clauses.append(tuple(values))
    assert nvars == 20 and nclauses == 91 and len(clauses) == 91
    canonical = ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses).encode('ascii')
    return {'clauses': clauses, 'canonical': sha256(canonical)}


def main(candidate_path: str) -> dict[str, Any]:
    candidate = json.loads(Path(candidate_path).read_text())
    candidate_rows = {row['source']: row for row in candidate.get('rows', [])}
    zero_keys = ('projected_raw_computations', 'pendant_target_computations', 'wl_feature_computations', 'portfolio_replays', 'route_class_labels', 'solver_invocations', 'iterated_pendant_rounds', 'new_solver_rules', 'new_reduction_rules')
    receipt = candidate.get('resource_receipt', {})
    global_checks = {
        'candidate_passed': candidate.get('verdict') == 'PASS_UF20_016_025_DUAL_MIRROR_SOURCE_ACQUISITION_CANDIDATE',
        'candidate_has_exact_ten_rows': tuple(row.get('source') for row in candidate.get('rows', [])) == ORDER,
        'candidate_forbidden_resources_zero': all(receipt.get(key) == 0 for key in zero_keys),
    }
    rows = []
    for source in ORDER:
        nnn = source.rsplit('_', 1)[1]
        primary_path = PRIMARY_TEMPLATE.format(nnn=nnn)
        verify_path = VERIFY_TEMPLATE.format(nnn=nnn)
        primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, primary_path)
        verification = fetch(VERIFY_REPO, VERIFY_COMMIT, verify_path)
        p = parse(primary)
        v = parse(verification)
        local_path = ROOT / f'research/source_data/SATLIB_{source}_2026-09-17.cnf'
        local = local_path.read_bytes() if local_path.exists() else b''
        c = candidate_rows.get(source, {})
        checks = {
            'ordered_clause_sequence_equal': p['clauses'] == v['clauses'],
            'canonical_formula_sha256_equal': p['canonical'] == v['canonical'],
            'local_copy_exists': bool(local),
            'local_copy_byte_equal_primary': local == primary,
            'local_git_blob_equal_primary': blob(local) == blob(primary) if local else False,
            'candidate_primary_blob_matches': c.get('primary_git_blob') == blob(primary),
            'candidate_verification_blob_matches': c.get('verification_git_blob') == blob(verification),
            'candidate_primary_raw_sha256_matches': c.get('primary_raw_sha256') == sha256(primary),
            'candidate_verification_raw_sha256_matches': c.get('verification_raw_sha256') == sha256(verification),
            'candidate_canonical_sha256_matches': c.get('canonical_formula_sha256') == p['canonical'],
            'candidate_status_ready': c.get('status') == 'SOURCE_READY_TO_FREEZE',
        }
        rows.append({'source': source, 'ok': all(checks.values()), 'checks': checks, 'primary_git_blob': blob(primary), 'verification_git_blob': blob(verification), 'canonical_formula_sha256': p['canonical']})
    passed = all(global_checks.values()) and all(row['ok'] for row in rows)
    return {
        'artifact_id': 'JANUS-TRUMP-UF20-016-025-INDEPENDENT-CLASS-COVERAGE-SOURCE-ACQUISITION-INDEPENDENT-CHECK-2026-09-17-v1.0',
        'candidate_imported': False,
        'global_checks': global_checks,
        'rows': rows,
        'sources_verified': sum(1 for row in rows if row['ok']),
        'resource_receipt': {
            'remote_source_fetches': 20,
            'schema_parses': 20,
            'projected_raw_computations': 0,
            'pendant_target_computations': 0,
            'wl_feature_computations': 0,
            'portfolio_replays': 0,
            'route_class_labels': 0,
            'solver_invocations': 0,
        },
        'verdict': 'PASS_INDEPENDENT_UF20_016_025_SOURCE_ACQUISITION_VERIFICATION' if passed else 'FAIL_INDEPENDENT_UF20_016_025_SOURCE_ACQUISITION_VERIFICATION',
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED', 'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED'},
    }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: independent_check.py CANDIDATE_JSON')
    print(json.dumps(main(sys.argv[1]), sort_keys=True, separators=(',', ':')))
