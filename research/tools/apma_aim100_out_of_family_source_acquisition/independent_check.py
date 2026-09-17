from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE_FILE = ROOT / 'research/tools/apma_aim100_out_of_family_source_acquisition/candidate.py'
RESERVATION = ROOT / 'research/TRUMP_AIM100_OUT_OF_FAMILY_WL_E3_FALSIFIER_PANEL_RESERVATION_2026-09-18_v1.0.json'
PREREG = ROOT / 'research/TRUMP_AIM100_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_AIM100_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json'
EXPECTED = {
    CANDIDATE_FILE: '9dfc5825f1c5da6f448321d3251bf54677cdfc78',
    RESERVATION: 'e509b0c2bf392b547d505b5648895c8d2b9cedaa',
    PREREG: '3dc0cffa67de19453991e86c7a31224c01e84ef6',
    REVIEW: '47708e421e2d984ab8078f5131c86a6aa598fd15',
}
PRIMARY_REPO = 'dmeoli/NeuroSAT'
PRIMARY_COMMIT = '568b022fc0c56e7e24fe08c012753ef29c60938e'
VERIFY_REPO = 'proofcert/trace-checker'
VERIFY_COMMIT = 'b45762b62d0921623a76fdca424aed4db8e1e308'
CANDIDATE_MODULE = 'research.tools.apma_aim100_out_of_family_source_acquisition.candidate'


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(repo: str, commit: str, path: str) -> bytes:
    request = urllib.request.Request(
        f'https://raw.githubusercontent.com/{repo}/{commit}/{path}',
        headers={'User-Agent': 'Janus-Fundamentum-AIM100-source-independent-check/1.0'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def parse_dimacs_exact_3cnf(data: bytes) -> tuple[int, int, list[tuple[int, int, int]], str]:
    nvars: int | None = None
    nclauses: int | None = None
    tokens: list[int] = []
    body_started = False
    terminated = False
    for raw in data.decode('utf-8').splitlines():
        line = raw.strip()
        if terminated or not line or line.startswith('c'):
            continue
        if line.startswith('%'):
            terminated = True
            continue
        if line.startswith('p'):
            if nvars is not None or body_started:
                raise ValueError('bad_header_position')
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ['p', 'cnf']:
                raise ValueError('bad_header')
            nvars, nclauses = int(parts[2]), int(parts[3])
            if nvars <= 0 or nclauses < 0:
                raise ValueError('bad_header_counts')
            continue
        if nvars is None:
            raise ValueError('body_before_header')
        body_started = True
        tokens.extend(int(x) for x in line.split())
    if nvars is None or nclauses is None:
        raise ValueError('missing_header')

    clauses: list[tuple[int, int, int]] = []
    current: list[int] = []
    for value in tokens:
        if value == 0:
            if len(current) != 3:
                raise ValueError('not_exact_3cnf')
            if len({abs(x) for x in current}) != 3:
                raise ValueError('repeated_clause_variable')
            if any(not 1 <= abs(x) <= nvars for x in current):
                raise ValueError('literal_out_of_range')
            clauses.append((current[0], current[1], current[2]))
            current = []
        else:
            current.append(value)
            if len(current) > 3:
                raise ValueError('clause_too_long')
    if current:
        raise ValueError('unterminated_clause')
    if len(clauses) != nclauses:
        raise ValueError('header_count_mismatch')
    canonical = ''.join(f'{a} {b} {c} 0\n' for a, b, c in clauses).encode('ascii')
    return nvars, nclauses, clauses, sha256(canonical)


def recompute() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    if not all(bindings.values()):
        return {'verdict': 'HALT_INDEPENDENT_AIM100_AUTHORITY_BINDING_FAILURE', 'bindings': bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {'verdict': 'HALT_INDEPENDENT_AIM100_CANDIDATE_IMPORT_VIOLATION'}

    reservation = json.loads(RESERVATION.read_text())
    names = reservation.get('reserved_filenames', [])
    if len(names) != 16:
        return {'verdict': 'HALT_INDEPENDENT_AIM100_PANEL_BINDING_FAILURE'}

    rows = []
    for filename in names:
        pp = f'data/aim/{filename}'
        vp = f'problems/aim/{filename}'
        try:
            primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, pp)
            verification = fetch(VERIFY_REPO, VERIFY_COMMIT, vp)
            pn, pm, pc, ph = parse_dimacs_exact_3cnf(primary)
            vn, vm, vc, vh = parse_dimacs_exact_3cnf(verification)
        except Exception as exc:
            return {'verdict': 'HALT_INDEPENDENT_AIM100_FETCH_OR_FORMAT_FAILURE', 'source': filename, 'error': f'{type(exc).__name__}:{exc}'}
        if (pn, pm, pc, ph) != (vn, vm, vc, vh):
            return {'verdict': 'HALT_INDEPENDENT_AIM100_MIRROR_MISMATCH', 'source': filename}

        stem = filename[:-4] if filename.endswith('.cnf') else filename
        staged = ROOT / f'research/source_data/AIM100_{stem}_2026-09-18.cnf'
        if not staged.exists() or staged.read_bytes() != primary:
            return {'verdict': 'HALT_INDEPENDENT_AIM100_STAGED_COPY_MISMATCH', 'source': filename}
        rows.append({
            'source': filename,
            'variables': pn,
            'clauses': pm,
            'canonical_formula_sha256': ph,
            'primary_git_blob': blob_bytes(primary),
            'verification_git_blob': blob_bytes(verification),
            'primary_raw_sha256': sha256(primary),
            'verification_raw_sha256': sha256(verification),
            'committed_copy_path': str(staged.relative_to(ROOT)),
            'computed_committed_git_blob': blob(staged),
            'ordered_clause_sequence_equal': True,
            'header_equal': True,
            'independent_verified': True,
        })
    return {
        'verdict': 'PASS_INDEPENDENT_AIM100_16_SOURCE_FREEZE_VERIFICATION',
        'candidate_imported': False,
        'bindings': bindings,
        'sources_verified': len(rows),
        'rows': rows,
        'resource_receipt': {
            'remote_source_fetches': 32,
            'projected_raw_computations': 0,
            'pendant_target_computations': 0,
            'wl_computations': 0,
            'direct_transposition_checks': 0,
            'portfolio_replays': 0,
            'e3_witness_computations': 0,
            'solver_invocations': 0,
            'truth_label_feature_reads': 0,
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())
    independent = recompute()
    if independent.get('verdict') != 'PASS_INDEPENDENT_AIM100_16_SOURCE_FREEZE_VERIFICATION':
        return independent

    candidate_rows = candidate.get('source_receipts', [])
    independent_rows = independent['rows']
    by_candidate = {row.get('source'): row for row in candidate_rows}
    comparisons = []
    for row in independent_rows:
        c = by_candidate.get(row['source'], {})
        comparisons.append({
            'source': row['source'],
            'variables': c.get('variables') == row['variables'],
            'clauses': c.get('clauses') == row['clauses'],
            'canonical_formula_sha256': c.get('canonical_formula_sha256') == row['canonical_formula_sha256'],
            'primary_git_blob': c.get('primary_git_blob') == row['primary_git_blob'],
            'verification_git_blob': c.get('verification_git_blob') == row['verification_git_blob'],
            'committed_copy_path': c.get('committed_copy_path') == row['committed_copy_path'],
            'computed_committed_git_blob': c.get('computed_committed_git_blob') == row['computed_committed_git_blob'],
        })
    checks = {
        'candidate_pass': candidate.get('verdict') == 'PASS_AIM100_16_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'candidate_not_imported': independent['candidate_imported'] is False,
        'candidate_source_count_16': len(candidate_rows) == 16,
        'independent_source_count_16': independent['sources_verified'] == 16,
        'all_row_fields_match': all(all(v is True for k, v in row.items() if k != 'source') for row in comparisons),
        'candidate_blind_barrier_zero': all(candidate.get('resource_receipt', {}).get(key) == 0 for key in (
            'projected_raw_computations', 'pendant_target_computations', 'wl_computations',
            'direct_transposition_checks', 'portfolio_replays', 'e3_witness_computations',
            'solver_invocations', 'truth_label_feature_reads')),
        'independent_blind_barrier_zero': all(independent.get('resource_receipt', {}).get(key) == 0 for key in (
            'projected_raw_computations', 'pendant_target_computations', 'wl_computations',
            'direct_transposition_checks', 'portfolio_replays', 'e3_witness_computations',
            'solver_invocations', 'truth_label_feature_reads')),
    }
    return {
        **independent,
        'candidate_verdict': candidate.get('verdict'),
        'comparison_checks': checks,
        'row_comparisons': comparisons,
        'verdict': 'PASS_INDEPENDENT_AIM100_SOURCE_ACQUISITION_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_AIM100_SOURCE_ACQUISITION_MISMATCH',
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
