from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_UF20_016_025_INDEPENDENT_CLASS_COVERAGE_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_016_025_INDEPENDENT_CLASS_COVERAGE_SOURCE_ACQUISITION_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
RESERVATION = ROOT / 'research/TRUMP_UF20_016_025_INDEPENDENT_CLASS_COVERAGE_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
EXPECTED_BLOBS = {
    PREREG: 'cf28308070b070e4ce41b37af8d9fdcc32b1359f',
    REVIEW: '8c6aaadadfae8d4f4fb402ca3e2f111f32aac561',
    RESERVATION: '459ce52dc66a92e8940749d4107dbff9f5f425b1',
}
ORDER = tuple(f'UF20_{i:03d}' for i in range(16, 26))
PRIMARY_REPO = 'Jany26/tree-aut-lib'
PRIMARY_COMMIT = '6cd58ade6de0a5c05511deb76c261ee75356ff31'
PRIMARY_TEMPLATE = 'benchmark/dimacs/uf20/uf20-{nnn}.cnf'
VERIFY_REPO = 'dncarley/MolecularSimulation'
VERIFY_COMMIT = 'd23a1d1775a939af0a6032ec459e5055919843a7'
VERIFY_TEMPLATE = 'data/uf20-91/uf20-{nnn}.cnf'


def git_blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def git_blob_file(path: Path) -> str:
    return git_blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_url(repo: str, commit: str, path: str) -> str:
    return f'https://raw.githubusercontent.com/{repo}/{commit}/{path}'


def fetch(repo: str, commit: str, path: str) -> bytes:
    req = urllib.request.Request(
        raw_url(repo, commit, path),
        headers={'User-Agent': 'Janus-Fundamentum-UF20-016-025-source-freeze/1.0'},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse_dimacs(data: bytes) -> dict[str, Any]:
    nvars = None
    nclauses = None
    clauses: list[list[int]] = []
    for raw in data.decode('utf-8').splitlines():
        s = raw.strip()
        if not s or s.startswith('c') or s in {'%', '0'}:
            continue
        if s.startswith('p '):
            p = s.split()
            assert p[:2] == ['p', 'cnf'] and len(p) == 4
            nvars, nclauses = int(p[2]), int(p[3])
            continue
        vals = [int(x) for x in s.split()]
        assert vals and vals[-1] == 0
        clause = vals[:-1]
        assert len(clause) == 3
        assert len({abs(x) for x in clause}) == 3
        assert all(1 <= abs(x) <= 20 for x in clause)
        clauses.append(clause)
    assert nvars == 20 and nclauses == 91 and len(clauses) == 91
    canonical = ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses).encode('ascii')
    return {
        'variables': nvars,
        'clauses_count': nclauses,
        'arity': 3,
        'clauses': clauses,
        'canonical_formula_sha256': sha256(canonical),
    }


def authority_guard() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    reservation = json.loads(RESERVATION.read_text())
    bindings = {str(path.relative_to(ROOT)): git_blob_file(path) == expected for path, expected in EXPECTED_BLOBS.items()}
    pins = prereg.get('pinned_mirrors', {})
    checks = {
        'authority_blob_bindings': all(bindings.values()),
        'reservation_status': reservation.get('status') == 'FROZEN_BEFORE_SOURCE_CONTENT_ACQUISITION_OR_ROUTE_WL_EVALUATION',
        'reservation_exact': tuple(reservation.get('reserved_sources', [])) == ORDER,
        'review_authorized': review.get('verdict') == 'PASS_SOURCE_ACQUISITION_PREREGISTRATION_CLEAN_WITH_DISCLOSED_UF20_016_PROVENANCE_PROBE__AUTHORIZED_TO_ACQUIRE_AND_FREEZE_ONLY',
        'primary_pin_exact': pins.get('primary') == {'repo': PRIMARY_REPO, 'commit': PRIMARY_COMMIT, 'path_template': PRIMARY_TEMPLATE},
        'verification_pin_exact': pins.get('verification') == {'repo': VERIFY_REPO, 'commit': VERIFY_COMMIT, 'path_template': VERIFY_TEMPLATE},
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def firewall() -> dict[str, str]:
    return {
        'P_VS_NP': 'OPEN',
        'GENERAL_SAT_IN_P': 'NOT_PROVED',
        'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED',
    }


def main() -> dict[str, Any]:
    guard = authority_guard()
    zero_receipt = {
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_feature_computations': 0,
        'portfolio_replays': 0,
        'route_class_labels': 0,
        'solver_invocations': 0,
        'iterated_pendant_rounds': 0,
        'new_solver_rules': 0,
        'new_reduction_rules': 0,
    }
    if not guard['ok']:
        return {
            'verdict': 'HALT_SOURCE_ACQUISITION_AUTHORITY_BINDING_FAILURE',
            'authority_guard': guard,
            'resource_receipt': zero_receipt,
            'scientific_firewall': firewall(),
        }

    staged: list[tuple[Path, bytes]] = []
    rows: list[dict[str, Any]] = []
    for source in ORDER:
        nnn = source.rsplit('_', 1)[1]
        primary_path = PRIMARY_TEMPLATE.format(nnn=nnn)
        verification_path = VERIFY_TEMPLATE.format(nnn=nnn)
        primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, primary_path)
        verification = fetch(VERIFY_REPO, VERIFY_COMMIT, verification_path)
        primary_parsed = parse_dimacs(primary)
        verification_parsed = parse_dimacs(verification)
        ordered_equal = primary_parsed['clauses'] == verification_parsed['clauses']
        canonical_equal = primary_parsed['canonical_formula_sha256'] == verification_parsed['canonical_formula_sha256']
        source_ok = ordered_equal and canonical_equal
        local_path = ROOT / f'research/source_data/SATLIB_{source}_2026-09-17.cnf'
        rows.append({
            'source': source,
            'filename': f'uf20-{nnn}.cnf',
            'status': 'SOURCE_READY_TO_FREEZE' if source_ok else 'SOURCE_MISMATCH',
            'variables': 20,
            'clauses': 91,
            'arity': 3,
            'primary_repo': PRIMARY_REPO,
            'primary_commit': PRIMARY_COMMIT,
            'primary_path': primary_path,
            'primary_git_blob': git_blob_bytes(primary),
            'primary_raw_sha256': sha256(primary),
            'verification_repo': VERIFY_REPO,
            'verification_commit': VERIFY_COMMIT,
            'verification_path': verification_path,
            'verification_git_blob': git_blob_bytes(verification),
            'verification_raw_sha256': sha256(verification),
            'ordered_clause_sequence_equal': ordered_equal,
            'canonical_formula_sha256_equal': canonical_equal,
            'canonical_formula_sha256': primary_parsed['canonical_formula_sha256'],
            'committed_copy_path': str(local_path.relative_to(ROOT)),
            'computed_committed_git_blob': git_blob_bytes(primary),
        })
        staged.append((local_path, primary))

    passed = all(row['status'] == 'SOURCE_READY_TO_FREEZE' for row in rows)
    if passed:
        for path, data in staged:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    return {
        'artifact_id': 'JANUS-TRUMP-UF20-016-025-INDEPENDENT-CLASS-COVERAGE-SOURCE-ACQUISITION-CANDIDATE-2026-09-17-v1.0',
        'authority': 'SOURCE_PROVENANCE_AND_DUAL_MIRROR_FORMULA_FREEZE_ONLY__NO_PROJECTED_PENDANT_WL_ROUTE_OR_SOLVER_EVALUATION',
        'verdict': 'PASS_UF20_016_025_DUAL_MIRROR_SOURCE_ACQUISITION_CANDIDATE' if passed else 'HALT_UF20_016_025_SOURCE_ACQUISITION_MISMATCH',
        'authority_guard': guard,
        'rows': rows,
        'resource_receipt': {**zero_receipt, 'reserved_sources': 10, 'remote_source_fetches': 20, 'schema_parses': 20, 'canonical_provenance_hashes': 20},
        'scientific_firewall': firewall(),
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
