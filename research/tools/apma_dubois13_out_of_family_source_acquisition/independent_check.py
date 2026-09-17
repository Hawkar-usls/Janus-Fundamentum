from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / 'research/tools/apma_dubois13_out_of_family_source_acquisition/candidate.py'
RESERVATION = ROOT / 'research/TRUMP_DUBOIS13_OUT_OF_FAMILY_WL_E3_FALSIFIER_PANEL_RESERVATION_2026-09-18_v1.0.json'
PREREG = ROOT / 'research/TRUMP_DUBOIS13_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_DUBOIS13_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json'
EXPECTED = {
    CANDIDATE: 'e94e22ddd55901baeed80d1b9a330b5d61e441b2',
    RESERVATION: '46d1ec596d98735ba27794e81b0e3a091a4c1ec4',
    PREREG: 'ff33e88180774a15107acdf1975070c554ff8e42',
    REVIEW: 'defabfddeadbfecc226a0100509514d55f1bf240',
}
PRIMARY_REPO = 'Gbury/sat-bench'
PRIMARY_COMMIT = 'a4068c403daf14bb5e320102427eb812bde6f703'
VERIFY_REPO = 'proofcert/trace-checker'
VERIFY_COMMIT = 'b45762b62d0921623a76fdca424aed4db8e1e308'


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\\0'.encode('ascii') + data).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(*args: str) -> None:
    subprocess.run(['git', *args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)


def prepare(repo: str, commit: str, sparse_path: str, temp_name: str) -> Path:
    target = Path('/tmp') / temp_name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    run_git('-C', str(target), 'init', '-q')
    run_git('-C', str(target), 'remote', 'add', 'origin', f'https://github.com/{repo}.git')
    run_git('-C', str(target), 'fetch', '-q', '--depth=1', '--filter=blob:none', 'origin', commit)
    run_git('-C', str(target), 'sparse-checkout', 'init', '--cone')
    run_git('-C', str(target), 'sparse-checkout', 'set', sparse_path)
    run_git('-C', str(target), 'checkout', '-q', '--detach', 'FETCH_HEAD')
    observed = subprocess.check_output(['git', '-C', str(target), 'rev-parse', 'HEAD'], text=True).strip()
    if observed != commit:
        raise RuntimeError(f'commit_binding_mismatch:{observed}!={commit}')
    return target


def parse_exact_3cnf(data: bytes):
    nvars = None
    nclauses = None
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
                raise ValueError('duplicate_or_late_header')
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ['p', 'cnf']:
                raise ValueError('bad_header')
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        if nvars is None:
            raise ValueError('body_before_header')
        body_started = True
        tokens.extend(int(x) for x in line.split())
    if nvars is None or nclauses is None:
        raise ValueError('missing_header')
    clauses = []
    current: list[int] = []
    for value in tokens:
        if value == 0:
            if len(current) != 3:
                raise ValueError(f'non_3cnf_clause_length:{len(current)}')
            if len({abs(x) for x in current}) != 3:
                raise ValueError('repeated_variable_within_clause')
            if any(not 1 <= abs(x) <= nvars for x in current):
                raise ValueError('literal_out_of_range')
            clauses.append(tuple(current))
            current = []
        else:
            current.append(value)
            if len(current) > 3:
                raise ValueError('clause_too_long')
    if current:
        raise ValueError('unterminated_clause')
    if len(clauses) != nclauses:
        raise ValueError(f'header_clause_count_mismatch:{nclauses}!={len(clauses)}')
    canonical = ''.join(f'{a} {b} {c} 0\\n' for a, b, c in clauses).encode('ascii')
    return nvars, nclauses, clauses, sha256(canonical)


def resource_receipt(verified: int) -> dict[str, int]:
    return {
        'mirror_git_fetches': 2,
        'mirror_file_reads': 26,
        'sources_verified': verified,
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_computations': 0,
        'direct_transposition_checks': 0,
        'portfolio_replays': 0,
        'e3_witness_computations': 0,
        'solver_invocations': 0,
        'known_unsat_label_feature_reads': 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True)
    args = ap.parse_args()
    authority = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    if not all(authority.values()):
        return {'verdict': 'HALT_INDEPENDENT_DUBOIS13_AUTHORITY_BINDING_FAILURE', 'authority': authority}
    candidate = json.loads(Path(args.candidate).read_text())
    if candidate.get('verdict') != 'PASS_DUBOIS13_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE':
        return {'verdict': 'HALT_INDEPENDENT_DUBOIS13_CANDIDATE_NOT_PASS', 'candidate_verdict': candidate.get('verdict')}
    reservation = json.loads(RESERVATION.read_text())
    order = reservation['reserved_filenames']
    manifest = reservation['verification_exact_path_manifest']
    by = {r['source']: r for r in candidate.get('source_receipts', [])}
    if len(by) != 13 or set(by) != set(order):
        return {'verdict': 'FAIL_INDEPENDENT_DUBOIS13_CANDIDATE_RECEIPT_DOMAIN_MISMATCH'}
    rows = []
    try:
        primary_root = prepare(PRIMARY_REPO, PRIMARY_COMMIT, 'problems/dubois', 'janus_dubois13_independent_primary')
        verification_root = prepare(VERIFY_REPO, VERIFY_COMMIT, 'problems', 'janus_dubois13_independent_verification')
        for filename in order:
            pp = f'problems/dubois/{filename}'
            vp = manifest[filename]
            primary = (primary_root / pp).read_bytes()
            verify = (verification_root / vp).read_bytes()
            pn, pm, pc, ph = parse_exact_3cnf(primary)
            vn, vm, vc, vh = parse_exact_3cnf(verify)
            local_path = ROOT / f'research/source_data/DUBOIS13_{filename[:-4]}_2026-09-18.cnf'
            local = local_path.read_bytes()
            row = by[filename]
            checks = {
                'headers_equal': (pn, pm) == (vn, vm),
                'ordered_clauses_equal': pc == vc,
                'formula_hash_equal': ph == vh,
                'local_equals_primary': local == primary,
                'candidate_primary_blob': row.get('primary_git_blob') == blob_bytes(primary),
                'candidate_verification_blob': row.get('verification_git_blob') == blob_bytes(verify),
                'candidate_formula_hash': row.get('canonical_formula_sha256') == ph,
                'candidate_committed_blob': row.get('computed_committed_git_blob') == blob_bytes(local),
                'candidate_path': row.get('committed_copy_path') == str(local_path.relative_to(ROOT)),
            }
            rows.append({
                'source': filename,
                'independent_verified': all(checks.values()),
                'checks': checks,
                'variables': pn,
                'clauses': pm,
                'canonical_formula_sha256': ph,
                'committed_git_blob': blob_bytes(local),
                'ordered_clause_sequence_equal': pc == vc,
            })
    except Exception as exc:
        return {
            'verdict': 'HALT_INDEPENDENT_DUBOIS13_FETCH_PARSE_OR_LOCAL_READ_FAILURE',
            'error': f'{type(exc).__name__}:{exc}',
            'verified_rows': rows,
            'authority': authority,
            'resource_receipt': resource_receipt(sum(r.get('independent_verified') is True for r in rows)),
        }
    passed = len(rows) == 13 and all(r['independent_verified'] for r in rows)
    return {
        'verdict': 'PASS_INDEPENDENT_DUBOIS13_SOURCE_FREEZE_VERIFICATION' if passed else 'FAIL_INDEPENDENT_DUBOIS13_SOURCE_FREEZE_MISMATCH',
        'candidate_imported': False,
        'authority': authority,
        'verified_rows': rows,
        'sources_verified': sum(r['independent_verified'] for r in rows),
        'resource_receipt': resource_receipt(sum(r['independent_verified'] for r in rows)),
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
