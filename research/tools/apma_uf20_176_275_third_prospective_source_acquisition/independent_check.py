from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / 'research/tools/apma_uf20_176_275_third_prospective_source_acquisition/candidate.py'
RESERVATION = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_PANEL_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
PREREG = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_REVIEW_2026-09-17_v1.0.json'
EXPECTED = {
    CANDIDATE: 'e3ac104be3d46000eeed714df767102e0856c332',
    RESERVATION: '9b4696da9a12c227024bd2343e6ae4db19fb2f03',
    PREREG: 'b679bf8ae0a0474da4486c5d815ac47a56a9325b',
    REVIEW: 'ca7089d2f57ae20950bf92094282cc6d1aa3fb14',
}
CANDIDATE_MODULE = 'research.tools.apma_uf20_176_275_third_prospective_source_acquisition.candidate'
PRIMARY_REPO = 'Jany26/tree-aut-lib'
PRIMARY_COMMIT = '6cd58ade6de0a5c05511deb76c261ee75356ff31'
VERIFY_REPO = 'dncarley/MolecularSimulation'
VERIFY_COMMIT = 'd23a1d1775a939af0a6032ec459e5055919843a7'
ORDER = tuple(f'UF20_{i:03d}' for i in range(176, 276))


def token(n: int) -> str:
    return '0' + str(n)


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(repo: str, commit: str, path: str) -> bytes:
    request = urllib.request.Request(
        f'https://raw.githubusercontent.com/{repo}/{commit}/{path}',
        headers={'User-Agent': 'Janus-Fundamentum-independent-UF20-176-275-source-freeze/1.0'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def parse(data: bytes):
    nvars = nclauses = None
    clauses = []
    for raw in data.decode('utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('c') or line in {'%', '0'}:
            continue
        if line.startswith('p '):
            parts = line.split()
            assert parts[:2] == ['p', 'cnf'] and len(parts) == 4
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        values = [int(x) for x in line.split()]
        assert values and values[-1] == 0
        clause = values[:-1]
        assert len(clause) == 3 and len({abs(x) for x in clause}) == 3
        clauses.append(clause)
    assert nvars == 20 and nclauses == 91 and len(clauses) == 91
    canonical = ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses).encode('ascii')
    return clauses, sha256(canonical)


def main() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())

    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    if not all(bindings.values()):
        return {'verdict': 'HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE', 'bindings': bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {'verdict': 'HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION'}
    if candidate.get('verdict') != 'PASS_UF20_176_275_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE':
        return {'verdict': 'HALT_INDEPENDENT_CANDIDATE_NOT_PASS', 'candidate_verdict': candidate.get('verdict')}

    by_source = {row['source']: row for row in candidate['source_receipts']}
    if tuple(by_source) != ORDER:
        return {'verdict': 'HALT_INDEPENDENT_CANDIDATE_SOURCE_ORDER_FAILURE'}

    rows = []
    try:
        for source in ORDER:
            n = int(source.split('_')[1])
            remote = token(n)
            local_id = f'{n:03d}'
            primary_path = f'benchmark/dimacs/uf20/uf20-{remote}.cnf'
            verification_path = f'data/uf20-91/uf20-{remote}.cnf'
            primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, primary_path)
            verification = fetch(VERIFY_REPO, VERIFY_COMMIT, verification_path)
            primary_clauses, primary_formula_hash = parse(primary)
            verification_clauses, verification_formula_hash = parse(verification)
            local_path = ROOT / f'research/source_data/SATLIB_UF20_{local_id}_2026-09-17.cnf'
            local = local_path.read_bytes()
            candidate_row = by_source[source]
            ok = (
                primary_clauses == verification_clauses
                and primary_formula_hash == verification_formula_hash
                and local == primary
                and blob_bytes(local) == candidate_row['computed_committed_git_blob']
                and primary_formula_hash == candidate_row['canonical_formula_sha256']
                and blob_bytes(primary) == candidate_row['primary_git_blob']
                and blob_bytes(verification) == candidate_row['verification_git_blob']
                and candidate_row['remote_filename'] == f'uf20-{remote}.cnf'
            )
            rows.append({
                'source': source,
                'remote_filename': f'uf20-{remote}.cnf',
                'independent_verified': ok,
                'committed_git_blob': blob_bytes(local),
                'canonical_formula_sha256': primary_formula_hash,
                'ordered_clause_sequence_equal': primary_clauses == verification_clauses,
            })
    except Exception as exc:
        return {
            'verdict': 'HALT_INDEPENDENT_FETCH_OR_PARSE_FAILURE',
            'error': f'{type(exc).__name__}:{exc}',
            'verified_rows': rows,
            'bindings': bindings,
        }

    passed = len(rows) == 100 and all(row['independent_verified'] for row in rows)
    return {
        'verdict': 'PASS_INDEPENDENT_UF20_176_275_SOURCE_FREEZE_VERIFICATION' if passed else 'FAIL_INDEPENDENT_UF20_176_275_SOURCE_FREEZE_MISMATCH',
        'candidate_imported': False,
        'bindings': bindings,
        'verified_rows': rows,
        'sources_verified': sum(row['independent_verified'] for row in rows),
        'resource_receipt': {
            'remote_source_fetches': 200,
            'projected_raw_computations': 0,
            'pendant_target_computations': 0,
            'wl_computations': 0,
            'direct_transposition_checks': 0,
            'portfolio_replays': 0,
            'e3_witness_computations': 0,
            'solver_invocations': 0,
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
