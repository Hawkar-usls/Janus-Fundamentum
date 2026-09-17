from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESERVATION = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_PANEL_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
PREREG = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_REVIEW_2026-09-17_v1.0.json'
EXPECTED = {
    RESERVATION: '9b4696da9a12c227024bd2343e6ae4db19fb2f03',
    PREREG: 'b679bf8ae0a0474da4486c5d815ac47a56a9325b',
    REVIEW: 'ca7089d2f57ae20950bf92094282cc6d1aa3fb14',
}
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
        headers={'User-Agent': 'Janus-Fundamentum-UF20-176-275-source-freeze/1.0'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def parse(data: bytes) -> tuple[list[list[int]], str]:
    nvars = nclauses = None
    clauses: list[list[int]] = []
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


def resource_receipt(remote_fetches: int) -> dict[str, int]:
    return {
        'remote_source_fetches': remote_fetches,
        'sources_reserved': 100,
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_computations': 0,
        'direct_transposition_checks': 0,
        'portfolio_replays': 0,
        'e3_witness_computations': 0,
        'solver_invocations': 0,
    }


def guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    reservation = json.loads(RESERVATION.read_text())
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    checks = {
        'authority_bindings': all(bindings.values()),
        'reservation_status': reservation.get('status') == 'FROZEN_BEFORE_SOURCE_CONTENT_ACQUISITION_OR_ANY_STRUCTURAL_VALUE_ON_THE_THIRD_PANEL',
        'selection_exact': tuple(reservation.get('reserved_sources', [])) == ORDER,
        'panel_size_exact': reservation.get('panel_size') == 100,
        'prereg_status': prereg.get('status') == 'FROZEN_BEFORE_FIRST_RESERVED_SOURCE_CONTENT_FETCH_OR_INSPECTION_IN_THIS_LINEAGE',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_THIRD_PROSPECTIVE_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_VERIFY_ALL_ONE_HUNDRED_ONLY',
        'filename_examples_exact': token(176) == '0176' and token(200) == '0200' and token(275) == '0275',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def main() -> dict[str, Any]:
    authority = guard()
    if not authority['ok']:
        return {
            'verdict': 'HALT_AUTHORITY_OR_RESERVATION_BINDING_FAILURE',
            'authority_guard': authority,
            'resource_receipt': resource_receipt(0),
        }

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
            if primary_clauses != verification_clauses or primary_formula_hash != verification_formula_hash:
                return {
                    'verdict': 'HALT_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH',
                    'source': source,
                    'rows': rows,
                    'resource_receipt': resource_receipt(len(rows) * 2 + 2),
                }
            output = ROOT / f'research/source_data/SATLIB_UF20_{local_id}_2026-09-17.cnf'
            if output.exists():
                return {
                    'verdict': 'HALT_COMMITTED_COPY_BINDING_FAILURE',
                    'source': source,
                    'reason': 'TARGET_PATH_PREEXISTS',
                    'rows': rows,
                    'resource_receipt': resource_receipt(len(rows) * 2 + 2),
                }
            output.write_bytes(primary)
            rows.append({
                'source': source,
                'numeric_index': n,
                'remote_filename': f'uf20-{remote}.cnf',
                'committed_copy_path': str(output.relative_to(ROOT)),
                'variables': 20,
                'clauses': 91,
                'arity': 3,
                'primary_repo': PRIMARY_REPO,
                'primary_commit': PRIMARY_COMMIT,
                'primary_path': primary_path,
                'primary_git_blob': blob_bytes(primary),
                'primary_raw_sha256': sha256(primary),
                'verification_repo': VERIFY_REPO,
                'verification_commit': VERIFY_COMMIT,
                'verification_path': verification_path,
                'verification_git_blob': blob_bytes(verification),
                'verification_raw_sha256': sha256(verification),
                'canonical_formula_sha256': primary_formula_hash,
                'ordered_clause_sequence_equal': True,
                'raw_bytes_primary_equal_verification': primary == verification,
                'computed_committed_git_blob': blob_bytes(primary),
                'independent_verified': False,
                'status': 'SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION',
            })
    except Exception as exc:
        return {
            'verdict': 'HALT_SOURCE_MISSING_OR_FETCH_FAILURE',
            'error': f'{type(exc).__name__}:{exc}',
            'rows': rows,
            'resource_receipt': resource_receipt(len(rows) * 2),
        }

    return {
        'artifact_id': 'JANUS-TRUMP-UF20-176-275-THIRD-PROSPECTIVE-SOURCE-ACQUISITION-CANDIDATE-2026-09-17-v1.0',
        'verdict': 'PASS_UF20_176_275_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'authority_guard': authority,
        'source_receipts': rows,
        'resource_receipt': resource_receipt(200),
        'scientific_firewall': {
            'P_VS_NP': 'OPEN',
            'GENERAL_SAT_IN_P': 'NOT_PROVED',
            'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED',
            'WL_SUFFICIENCY_FOR_ORBIT_CLOSURE': 'NOT_PROVED',
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
