from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESERVATION = ROOT / 'research/TRUMP_AIM100_OUT_OF_FAMILY_WL_E3_FALSIFIER_PANEL_RESERVATION_2026-09-18_v1.0.json'
PREREG = ROOT / 'research/TRUMP_AIM100_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_AIM100_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json'
TRANSPORT_ERRATUM = ROOT / 'research/TRUMP_AIM100_SOURCE_ACQUISITION_TRANSPORT_ERRATUM_2026-09-18_v1.1.json'
PATH_ERRATUM = ROOT / 'research/TRUMP_AIM100_VERIFICATION_PATH_BINDING_ERRATUM_2026-09-18_v1.2.json'
EXPECTED = {
    RESERVATION: 'e509b0c2bf392b547d505b5648895c8d2b9cedaa',
    PREREG: '3dc0cffa67de19453991e86c7a31224c01e84ef6',
    REVIEW: '47708e421e2d984ab8078f5131c86a6aa598fd15',
    TRANSPORT_ERRATUM: 'fc33da20ce65000dc569e8de7f87668b8c931fbf',
    PATH_ERRATUM: '0e19c2e40cd7fa6eb37d3971b325d3d1b058b6c8',
}
PRIMARY_REPO = 'dmeoli/NeuroSAT'
PRIMARY_COMMIT = '568b022fc0c56e7e24fe08c012753ef29c60938e'
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


def prepare_mirror(repo: str, commit: str, sparse_path: str, temp_name: str) -> Path:
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


def parse_dimacs_exact_3cnf(data: bytes) -> tuple[int, int, list[list[int]], str]:
    text = data.decode('utf-8')
    nvars: int | None = None
    nclauses: int | None = None
    integer_tokens: list[int] = []
    body_started = False
    percent_terminated = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if percent_terminated or not line or line.startswith('c'):
            continue
        if line.startswith('%'):
            percent_terminated = True
            continue
        if line.startswith('p'):
            if nvars is not None or body_started:
                raise ValueError('duplicate_or_late_header')
            parts = line.split()
            if len(parts) != 4 or parts[0] != 'p' or parts[1] != 'cnf':
                raise ValueError('invalid_dimacs_header')
            nvars, nclauses = int(parts[2]), int(parts[3])
            if nvars <= 0 or nclauses < 0:
                raise ValueError('invalid_header_counts')
            continue
        if nvars is None:
            raise ValueError('body_before_header')
        body_started = True
        integer_tokens.extend(int(tok) for tok in line.split())
    if nvars is None or nclauses is None:
        raise ValueError('missing_dimacs_header')
    clauses: list[list[int]] = []
    current: list[int] = []
    for value in integer_tokens:
        if value == 0:
            if len(current) != 3:
                raise ValueError(f'non_3cnf_clause_length:{len(current)}')
            if len({abs(x) for x in current}) != 3:
                raise ValueError('repeated_variable_within_clause')
            if any(abs(x) < 1 or abs(x) > nvars for x in current):
                raise ValueError('literal_variable_out_of_header_range')
            clauses.append(current)
            current = []
        else:
            current.append(value)
            if len(current) > 3:
                raise ValueError('non_3cnf_clause_length_gt3')
    if current:
        raise ValueError('unterminated_final_clause')
    if len(clauses) != nclauses:
        raise ValueError(f'header_clause_count_mismatch:{nclauses}!={len(clauses)}')
    canonical = ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses).encode('ascii')
    return nvars, nclauses, clauses, sha256(canonical)


def resource_receipt(mirror_git_fetches: int, mirror_file_reads: int, staged_sources: int) -> dict[str, int]:
    return {
        'mirror_git_fetches': mirror_git_fetches,
        'mirror_file_reads': mirror_file_reads,
        'sources_reserved': 16,
        'sources_staged': staged_sources,
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_computations': 0,
        'direct_transposition_checks': 0,
        'portfolio_replays': 0,
        'e3_witness_computations': 0,
        'solver_invocations': 0,
        'truth_label_feature_reads': 0,
    }


def guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    reservation = json.loads(RESERVATION.read_text())
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    transport = json.loads(TRANSPORT_ERRATUM.read_text())
    path_erratum = json.loads(PATH_ERRATUM.read_text())
    names = tuple(reservation.get('reserved_filenames', []))
    expected_names = tuple(f'aim-100-{density}-{label}-{index}.cnf' for density in ('1_6', '2_0') for label in ('no', 'yes1') for index in range(1, 5))
    manifest = path_erratum.get('verification_exact_path_manifest', {})
    primary_binding = reservation.get('source_mirrors', {}).get('primary', {})
    verification_binding = reservation.get('source_mirrors', {}).get('verification', {})
    checks = {
        'authority_bindings': all(bindings.values()),
        'reservation_status': reservation.get('status') == 'FROZEN_BEFORE_ANY_PROJECTION_PENDANT_WL_DIRECT_EXACT_PORTFOLIO_OR_E3_COMPUTATION_ON_THE_RESERVED_PANEL',
        'selection_exact': names == expected_names,
        'panel_size_exact': reservation.get('panel_size') == 16 and len(names) == 16,
        'primary_repo_commit_binding': primary_binding.get('repository') == PRIMARY_REPO and primary_binding.get('commit') == PRIMARY_COMMIT,
        'verification_repo_commit_binding': verification_binding.get('repository') == VERIFY_REPO and verification_binding.get('commit') == VERIFY_COMMIT,
        'manifest_exact_domain': set(manifest) == set(names) and len(manifest) == 16,
        'manifest_all_under_pinned_repo_tree': all(isinstance(path, str) and path.startswith('problems/') and path.endswith('/' + name) for name, path in manifest.items()),
        'prereg_status': prereg.get('status') == 'FROZEN_BEFORE_FIRST_DUAL_MIRROR_BODY_ACQUISITION_AND_BEFORE_ANY_STRUCTURAL_COMPUTATION_ON_THE_RESERVED_AIM100_PANEL',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_AIM100_OUT_OF_FAMILY_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_VERIFY_EXACTLY_THE_16_RESERVED_FILES_ONCE',
        'transport_erratum': transport.get('transport_correction', {}).get('candidate', '').startswith('SPARSE_GIT_FETCH_EXACT_PINNED_COMMIT'),
        'path_erratum_status': path_erratum.get('status') == 'FROZEN_BINDING_ONLY_ERRATUM_AFTER_TWO_ZERO_SOURCE_HALTS_AND_BEFORE_SUCCESSFUL_ACQUISITION',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings, 'order': list(names), 'verification_manifest': manifest}


def main() -> dict[str, Any]:
    authority = guard()
    if not authority['ok']:
        return {'verdict': 'HALT_AIM100_AUTHORITY_OR_RESERVATION_BINDING_FAILURE', 'authority_guard': authority, 'resource_receipt': resource_receipt(0, 0, 0)}
    try:
        primary_root = prepare_mirror(PRIMARY_REPO, PRIMARY_COMMIT, 'data/aim', 'janus_aim100_candidate_primary')
        verification_root = prepare_mirror(VERIFY_REPO, VERIFY_COMMIT, 'problems', 'janus_aim100_candidate_verification')
    except Exception as exc:
        return {'verdict': 'HALT_AIM100_RESERVED_SOURCE_MISSING_OR_FETCH_FAILURE', 'source': 'MIRROR_FETCH', 'error': f'{type(exc).__name__}:{exc}', 'source_receipts': [], 'resource_receipt': resource_receipt(2, 0, 0)}

    rows: list[dict[str, Any]] = []
    manifest = authority['verification_manifest']
    for filename in authority['order']:
        primary_path = f'data/aim/{filename}'
        verification_path = manifest[filename]
        try:
            primary = (primary_root / primary_path).read_bytes()
            verification = (verification_root / verification_path).read_bytes()
        except Exception as exc:
            return {'verdict': 'HALT_AIM100_RESERVED_SOURCE_MISSING_OR_FETCH_FAILURE', 'source': filename, 'verification_path': verification_path, 'error': f'{type(exc).__name__}:{exc}', 'source_receipts': rows, 'resource_receipt': resource_receipt(2, len(rows) * 2, len(rows))}
        try:
            pn, pm, pclauses, phash = parse_dimacs_exact_3cnf(primary)
            vn, vm, vclauses, vhash = parse_dimacs_exact_3cnf(verification)
        except Exception as exc:
            return {'verdict': 'HALT_AIM100_DIMACS_OR_EXACT_3CNF_FORMAT_FAILURE', 'source': filename, 'error': f'{type(exc).__name__}:{exc}', 'source_receipts': rows, 'resource_receipt': resource_receipt(2, len(rows) * 2 + 2, len(rows))}
        if pn != vn or pm != vm or pclauses != vclauses or phash != vhash:
            return {'verdict': 'HALT_AIM100_HEADER_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH', 'source': filename, 'primary_header': [pn, pm], 'verification_header': [vn, vm], 'ordered_clause_sequence_equal': pclauses == vclauses, 'canonical_formula_equal': phash == vhash, 'source_receipts': rows, 'resource_receipt': resource_receipt(2, len(rows) * 2 + 2, len(rows))}
        stem = filename[:-4] if filename.endswith('.cnf') else filename
        output = ROOT / f'research/source_data/AIM100_{stem}_2026-09-18.cnf'
        if output.exists():
            return {'verdict': 'HALT_AIM100_COMMITTED_COPY_BINDING_FAILURE', 'source': filename, 'reason': 'TARGET_PATH_PREEXISTS', 'source_receipts': rows, 'resource_receipt': resource_receipt(2, len(rows) * 2 + 2, len(rows))}
        output.write_bytes(primary)
        rows.append({
            'source': filename,
            'committed_copy_path': str(output.relative_to(ROOT)),
            'variables': pn,
            'clauses': pm,
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
            'canonical_formula_sha256': phash,
            'ordered_clause_sequence_equal': True,
            'header_equal': True,
            'raw_bytes_primary_equal_verification': primary == verification,
            'computed_committed_git_blob': blob_bytes(primary),
            'independent_verified': False,
            'status': 'SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION',
        })
    return {
        'artifact_id': 'JANUS-TRUMP-AIM100-OUT-OF-FAMILY-SOURCE-ACQUISITION-CANDIDATE-2026-09-18-v1.2',
        'gate': 'TRUMP_AIM100_OUT_OF_FAMILY_SOURCE_ACQUISITION_GATE',
        'verdict': 'PASS_AIM100_16_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'authority_guard': authority,
        'source_receipts': rows,
        'resource_receipt': resource_receipt(2, 32, 16),
        'failed_prior_run_ids': [35277170407, 35277553768],
        'scientific_firewall': {'WL_SUFFICIENCY_WITHOUT_DIRECT_EXACT_CHECK': 'NOT_PROVED', 'GENERAL_SAT_IN_P': 'NOT_PROVED', 'P_VS_NP': 'OPEN'},
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
