from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / 'research/tools/apma_uf150_001_020_out_of_family_source_acquisition/candidate_v2.py'
RESERVATION = ROOT / 'research/TRUMP_UF150_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_PANEL_RESERVATION_2026-09-18_v1.0.json'
PREREG = ROOT / 'research/TRUMP_UF150_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF150_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json'
EXPECTED = {
    CANDIDATE: 'f22398955662b62cfd5c7985453abf65aca1da47',
    RESERVATION: 'fbd687759ba6f1e377a71615b4d4b2a8f433005c',
    PREREG: 'ee82ae4fc7933879dab800ec75c8f2dbf70d8a98',
    REVIEW: '70e06a7f47b20a48b43088b04480a73925462998',
}
PRIMARY_REPO = 'HydrogenRb/ECE51216_SAT_solver'
PRIMARY_COMMIT = '8866170d4a804bd08e70291e5488365038524660'
VERIFY_REPO = 'zeilerphone/rvv_sat'
VERIFY_COMMIT = 'cb9dfa7a0862c44882850d465d045d2a9bf86950'


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(repo: str, commit: str, path: str) -> bytes:
    url = f'https://raw.githubusercontent.com/{repo}/{commit}/{path}'
    req = urllib.request.Request(url, headers={'User-Agent':'Janus-Fundamentum-UF150-independent-source-freeze/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


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
            if len(parts) != 4 or parts[:2] != ['p','cnf']:
                raise ValueError('bad_header')
            nvars, nclauses = int(parts[2]), int(parts[3])
            if nvars != 150 or nclauses != 645:
                raise ValueError(f'unexpected_header:{nvars},{nclauses}')
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
            if any(not 1 <= abs(x) <= 150 for x in current):
                raise ValueError('literal_out_of_range')
            clauses.append(tuple(current))
            current = []
        else:
            current.append(value)
            if len(current) > 3:
                raise ValueError('clause_too_long')
    if current:
        raise ValueError('unterminated_clause')
    if len(clauses) != 645:
        raise ValueError(f'header_clause_count_mismatch:645!={len(clauses)}')
    canonical = ''.join(f'{a} {b} {c} 0\n' for a,b,c in clauses).encode('ascii')
    return clauses, sha256(canonical)


def resource_receipt(verified: int) -> dict[str,int]:
    return {
        'remote_source_fetches': 40,
        'sources_verified': verified,
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_computations': 0,
        'direct_transposition_checks': 0,
        'portfolio_replays': 0,
        'e3_witness_computations': 0,
        'solver_invocations': 0,
        'known_sat_label_feature_reads': 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True)
    args = ap.parse_args()
    authority = {str(p.relative_to(ROOT)): blob(p) == h for p,h in EXPECTED.items()}
    if not all(authority.values()):
        return {'verdict':'HALT_INDEPENDENT_UF150_AUTHORITY_BINDING_FAILURE','authority':authority}

    candidate = json.loads(Path(args.candidate).read_text())
    if candidate.get('verdict') != 'PASS_UF150_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE':
        return {'verdict':'HALT_INDEPENDENT_UF150_CANDIDATE_NOT_PASS','candidate_verdict':candidate.get('verdict')}

    reservation = json.loads(RESERVATION.read_text())
    order = reservation['reserved_filenames']
    manifest = reservation['exact_path_manifest']
    by = {r['filename']:r for r in candidate.get('source_receipts', [])}
    if len(by) != 20 or set(by) != set(order):
        return {'verdict':'FAIL_INDEPENDENT_UF150_CANDIDATE_RECEIPT_DOMAIN_MISMATCH'}

    rows = []
    try:
        for filename in order:
            paths = manifest[filename]
            p = fetch(PRIMARY_REPO, PRIMARY_COMMIT, paths['primary'])
            v = fetch(VERIFY_REPO, VERIFY_COMMIT, paths['verification'])
            pc, ph = parse_exact_3cnf(p)
            vc, vh = parse_exact_3cnf(v)
            numeric = int(filename.removeprefix('uf150-').removesuffix('.cnf'))
            local_path = ROOT / f'research/source_data/SATLIB_UF150_{numeric:03d}_2026-09-18.cnf'
            local = local_path.read_bytes()
            row = by[filename]
            checks = {
                'ordered_clauses_equal': pc == vc,
                'formula_hash_equal': ph == vh,
                'local_equals_primary': local == p,
                'candidate_primary_blob': row.get('primary_git_blob') == blob_bytes(p),
                'candidate_verification_blob': row.get('verification_git_blob') == blob_bytes(v),
                'candidate_formula_hash': row.get('canonical_formula_sha256') == ph,
                'candidate_committed_blob': row.get('computed_committed_git_blob') == blob_bytes(local),
                'candidate_path': row.get('committed_copy_path') == str(local_path.relative_to(ROOT)),
            }
            rows.append({
                'source':f'UF150_{numeric:03d}',
                'filename':filename,
                'independent_verified':all(checks.values()),
                'checks':checks,
                'canonical_formula_sha256':ph,
                'committed_git_blob':blob_bytes(local),
                'ordered_clause_sequence_equal':pc==vc,
            })
    except Exception as exc:
        return {
            'verdict':'HALT_INDEPENDENT_UF150_FETCH_PARSE_OR_LOCAL_READ_FAILURE',
            'error':f'{type(exc).__name__}:{exc}',
            'verified_rows':rows,
            'authority':authority,
            'resource_receipt':resource_receipt(sum(r.get('independent_verified') is True for r in rows)),
        }
    passed = len(rows)==20 and all(r['independent_verified'] for r in rows)
    return {
        'verdict':'PASS_INDEPENDENT_UF150_001_020_SOURCE_FREEZE_VERIFICATION' if passed else 'FAIL_INDEPENDENT_UF150_001_020_SOURCE_FREEZE_MISMATCH',
        'candidate_imported':False,
        'authority':authority,
        'verified_rows':rows,
        'sources_verified':sum(r['independent_verified'] for r in rows),
        'resource_receipt':resource_receipt(sum(r['independent_verified'] for r in rows)),
    }


if __name__ == '__main__':
    print(json.dumps(main(),sort_keys=True,separators=(',',':')))
