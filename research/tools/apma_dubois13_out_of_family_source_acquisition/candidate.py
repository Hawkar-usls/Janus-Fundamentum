from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESERVATION = ROOT / 'research/TRUMP_DUBOIS13_OUT_OF_FAMILY_WL_E3_FALSIFIER_PANEL_RESERVATION_2026-09-18_v1.0.json'
PREREG = ROOT / 'research/TRUMP_DUBOIS13_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_DUBOIS13_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json'
EXPECTED = {
    RESERVATION: '46d1ec596d98735ba27794e81b0e3a091a4c1ec4',
    PREREG: 'ff33e88180774a15107acdf1975070c554ff8e42',
    REVIEW: 'defabfddeadbfecc226a0100509514d55f1bf240',
}
PRIMARY_REPO = 'Gbury/sat-bench'
PRIMARY_COMMIT = 'a4068c403daf14bb5e320102427eb812bde6f703'
VERIFY_REPO = 'proofcert/trace-checker'
VERIFY_COMMIT = 'b45762b62d0921623a76fdca424aed4db8e1e308'


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


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


def parse_exact_3cnf(data: bytes) -> tuple[int, int, list[tuple[int, int, int]], str]:
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
                raise ValueError(f'non_3cnf_clause_length:{len(current)}')
            if len({abs(x) for x in current}) != 3:
                raise ValueError('repeated_variable_within_clause')
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
        raise ValueError(f'header_clause_count_mismatch:{nclauses}!={len(clauses)}')
    canonical = ''.join(f'{a} {b} {c} 0\n' for a, b, c in clauses).encode('ascii')
    return nvars, nclauses, clauses, sha256(canonical)


def receipt(staged: int, reads: int) -> dict[str, int]:
    return {
        'mirror_git_fetches': 2,
        'mirror_file_reads': reads,
        'sources_reserved': 13,
        'sources_staged': staged,
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_computations': 0,
        'direct_transposition_checks': 0,
        'portfolio_replays': 0,
        'e3_witness_computations': 0,
        'solver_invocations': 0,
        'known_unsat_label_feature_reads': 0,
    }


def guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    reservation = json.loads(RESERVATION.read_text())
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    names = reservation.get('reserved_filenames', [])
    expected_names = [*(f'dubois{i}.cnf' for i in range(20, 31)), 'dubois50.cnf', 'dubois100.cnf']
    manifest = reservation.get('verification_exact_path_manifest', {})
    checks = {
        'bindings': all(bindings.values()),
        'reservation_status': reservation.get('status') == 'FROZEN_BEFORE_DUBOIS_BODY_ACQUISITION_AND_BEFORE_ANY_PROJECTION_PENDANT_WL_DIRECT_EXACT_PORTFOLIO_OR_E3_VALUE',
        'complete_family_order': names == expected_names and len(names) == 13,
        'manifest_domain': set(manifest) == set(names),
        'primary_binding': reservation.get('source_mirrors', {}).get('primary') == {
            'repository': PRIMARY_REPO,
            'commit': PRIMARY_COMMIT,
            'path_template': 'problems/dubois/{filename}',
        },
        'verification_repo_commit': reservation.get('source_mirrors', {}).get('verification') == {
            'repository': VERIFY_REPO,
            'commit': VERIFY_COMMIT,
        },
        'prereg_status': prereg.get('status') == 'FROZEN_BEFORE_FIRST_DUBOIS_BODY_ACQUISITION_OR_STRUCTURAL_COMPUTATION',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_DUBOIS13_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_INDEPENDENTLY_VERIFY_ALL_13_ONCE',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings, 'order': names, 'verification_manifest': manifest}


def main() -> dict[str, Any]:
    g = guard()
    if not g['ok']:
        return {'verdict': 'HALT_DUBOIS13_AUTHORITY_OR_RESERVATION_BINDING_FAILURE', 'authority_guard': g, 'resource_receipt': receipt(0, 0)}
    try:
        primary_root = prepare(PRIMARY_REPO, PRIMARY_COMMIT, 'problems/dubois', 'janus_dubois13_candidate_primary')
        verification_root = prepare(VERIFY_REPO, VERIFY_COMMIT, 'problems', 'janus_dubois13_candidate_verification')
    except Exception as exc:
        return {'verdict': 'HALT_DUBOIS13_RESERVED_SOURCE_MISSING_OR_FETCH_FAILURE', 'source': 'MIRROR_FETCH', 'error': f'{type(exc).__name__}:{exc}', 'resource_receipt': receipt(0, 0)}
    rows = []
    for filename in g['order']:
        pp = f'problems/dubois/{filename}'
        vp = g['verification_manifest'][filename]
        try:
            primary = (primary_root / pp).read_bytes()
            verify = (verification_root / vp).read_bytes()
        except Exception as exc:
            return {'verdict': 'HALT_DUBOIS13_RESERVED_SOURCE_MISSING_OR_FETCH_FAILURE', 'source': filename, 'error': f'{type(exc).__name__}:{exc}', 'source_receipts': rows, 'resource_receipt': receipt(len(rows), len(rows) * 2)}
        try:
            pn, pm, pc, ph = parse_exact_3cnf(primary)
            vn, vm, vc, vh = parse_exact_3cnf(verify)
        except Exception as exc:
            return {'verdict': 'HALT_DUBOIS13_DIMACS_OR_EXACT_3CNF_FORMAT_FAILURE', 'source': filename, 'error': f'{type(exc).__name__}:{exc}', 'source_receipts': rows, 'resource_receipt': receipt(len(rows), len(rows) * 2 + 2)}
        if (pn, pm, pc, ph) != (vn, vm, vc, vh):
            return {
                'verdict': 'HALT_DUBOIS13_HEADER_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH',
                'source': filename,
                'primary_header': [pn, pm],
                'verification_header': [vn, vm],
                'ordered_clause_sequence_equal': pc == vc,
                'canonical_formula_equal': ph == vh,
                'source_receipts': rows,
                'resource_receipt': receipt(len(rows), len(rows) * 2 + 2),
            }
        output = ROOT / f'research/source_data/DUBOIS13_{filename[:-4]}_2026-09-18.cnf'
        if output.exists():
            return {'verdict': 'HALT_DUBOIS13_COMMITTED_COPY_BINDING_FAILURE', 'source': filename, 'reason': 'TARGET_PATH_PREEXISTS', 'source_receipts': rows, 'resource_receipt': receipt(len(rows), len(rows) * 2 + 2)}
        output.write_bytes(primary)
        rows.append({
            'source': filename,
            'variables': pn,
            'clauses': pm,
            'arity': 3,
            'primary_repo': PRIMARY_REPO,
            'primary_commit': PRIMARY_COMMIT,
            'primary_path': pp,
            'primary_git_blob': blob_bytes(primary),
            'primary_raw_sha256': sha256(primary),
            'verification_repo': VERIFY_REPO,
            'verification_commit': VERIFY_COMMIT,
            'verification_path': vp,
            'verification_git_blob': blob_bytes(verify),
            'verification_raw_sha256': sha256(verify),
            'raw_bytes_primary_equal_verification': primary == verify,
            'ordered_clause_sequence_equal': True,
            'canonical_formula_sha256': ph,
            'committed_copy_path': str(output.relative_to(ROOT)),
            'computed_committed_git_blob': blob_bytes(primary),
            'independent_verified': False,
            'status': 'SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION',
        })
    return {
        'artifact_id': 'JANUS-TRUMP-DUBOIS13-OUT-OF-FAMILY-SOURCE-ACQUISITION-CANDIDATE-2026-09-18-v1.0',
        'gate': 'TRUMP_DUBOIS13_OUT_OF_FAMILY_SOURCE_ACQUISITION_GATE',
        'verdict': 'PASS_DUBOIS13_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'authority_guard': g,
        'source_receipts': rows,
        'resource_receipt': receipt(13, 26),
        'scientific_firewall': {'WL_SUFFICIENCY_WITHOUT_DIRECT_EXACT_CHECK': 'NOT_PROVED', 'GENERAL_SAT_IN_P': 'NOT_PROVED', 'P_VS_NP': 'OPEN'},
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
