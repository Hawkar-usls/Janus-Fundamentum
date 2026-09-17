from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESERVATION = ROOT / 'research/TRUMP_UF150_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_PANEL_RESERVATION_2026-09-18_v1.0.json'
PREREG = ROOT / 'research/TRUMP_UF150_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF150_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json'
EXPECTED = {
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
    req = urllib.request.Request(url, headers={'User-Agent':'Janus-Fundamentum-UF150-source-freeze/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse_exact_3cnf(data: bytes) -> tuple[int, int, list[tuple[int,int,int]], str]:
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

    clauses: list[tuple[int,int,int]] = []
    current: list[int] = []
    for value in tokens:
        if value == 0:
            if len(current) != 3:
                raise ValueError(f'non_3cnf_clause_length:{len(current)}')
            if len({abs(x) for x in current}) != 3:
                raise ValueError('repeated_variable_within_clause')
            if any(not 1 <= abs(x) <= 150 for x in current):
                raise ValueError('literal_out_of_range')
            clauses.append((current[0],current[1],current[2]))
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
    return 150, 645, clauses, sha256(canonical)


def receipt(staged: int, fetches: int) -> dict[str,int]:
    return {
        'remote_source_fetches': fetches,
        'sources_reserved': 20,
        'sources_staged': staged,
        'projected_raw_computations': 0,
        'pendant_target_computations': 0,
        'wl_computations': 0,
        'direct_transposition_checks': 0,
        'portfolio_replays': 0,
        'e3_witness_computations': 0,
        'solver_invocations': 0,
        'known_sat_label_feature_reads': 0,
    }


def guard() -> dict[str,Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p,h in EXPECTED.items()}
    reservation = json.loads(RESERVATION.read_text())
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    order = reservation.get('reserved_filenames', [])
    expected_order = [f'uf150-0{i}.cnf' for i in range(1,21)]
    manifest = reservation.get('exact_path_manifest', {})
    checks = {
        'bindings': all(bindings.values()),
        'reservation_status': reservation.get('status') == 'FROZEN_BEFORE_UF150_BODY_ACQUISITION_AND_BEFORE_ANY_PROJECTION_PENDANT_WL_DIRECT_EXACT_PORTFOLIO_OR_E3_VALUE',
        'order': order == expected_order and len(order) == 20,
        'manifest_domain': set(manifest) == set(order),
        'prereg_status': prereg.get('status') == 'FROZEN_BEFORE_FIRST_UF150_BODY_ACQUISITION_OR_STRUCTURAL_COMPUTATION',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_UF150_001_020_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_INDEPENDENTLY_VERIFY_ALL_20_ONCE',
    }
    return {'ok':all(checks.values()),'checks':checks,'bindings':bindings,'order':order,'manifest':manifest}


def main() -> dict[str,Any]:
    g = guard()
    if not g['ok']:
        return {'verdict':'HALT_UF150_AUTHORITY_OR_RESERVATION_BINDING_FAILURE','authority_guard':g,'resource_receipt':receipt(0,0)}

    rows = []
    for filename in g['order']:
        paths = g['manifest'][filename]
        try:
            primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, paths['primary'])
            verify = fetch(VERIFY_REPO, VERIFY_COMMIT, paths['verification'])
        except Exception as exc:
            return {'verdict':'HALT_UF150_RESERVED_SOURCE_MISSING_OR_FETCH_FAILURE','source':filename,'error':f'{type(exc).__name__}:{exc}','source_receipts':rows,'resource_receipt':receipt(len(rows),len(rows)*2)}
        try:
            pn,pm,pc,ph = parse_exact_3cnf(primary)
            vn,vm,vc,vh = parse_exact_3cnf(verify)
        except Exception as exc:
            return {'verdict':'HALT_UF150_DIMACS_OR_EXACT_3CNF_FORMAT_FAILURE','source':filename,'error':f'{type(exc).__name__}:{exc}','source_receipts':rows,'resource_receipt':receipt(len(rows),len(rows)*2+2)}
        if (pn,pm,pc,ph) != (vn,vm,vc,vh):
            return {
                'verdict':'HALT_UF150_HEADER_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH',
                'source':filename,
                'primary_header':[pn,pm],
                'verification_header':[vn,vm],
                'ordered_clause_sequence_equal':pc==vc,
                'canonical_formula_equal':ph==vh,
                'source_receipts':rows,
                'resource_receipt':receipt(len(rows),len(rows)*2+2),
            }
        numeric = int(filename.removeprefix('uf150-').removesuffix('.cnf'))
        output = ROOT / f'research/source_data/SATLIB_UF150_{numeric:03d}_2026-09-18.cnf'
        if output.exists():
            return {'verdict':'HALT_UF150_COMMITTED_COPY_BINDING_FAILURE','source':filename,'reason':'TARGET_PATH_PREEXISTS','source_receipts':rows,'resource_receipt':receipt(len(rows),len(rows)*2+2)}
        output.write_bytes(primary)
        rows.append({
            'source':f'UF150_{numeric:03d}',
            'filename':filename,
            'variables':pn,
            'clauses':pm,
            'arity':3,
            'primary_repo':PRIMARY_REPO,
            'primary_commit':PRIMARY_COMMIT,
            'primary_path':paths['primary'],
            'primary_git_blob':blob_bytes(primary),
            'primary_raw_sha256':sha256(primary),
            'verification_repo':VERIFY_REPO,
            'verification_commit':VERIFY_COMMIT,
            'verification_path':paths['verification'],
            'verification_git_blob':blob_bytes(verify),
            'verification_raw_sha256':sha256(verify),
            'raw_bytes_primary_equal_verification':primary==verify,
            'ordered_clause_sequence_equal':True,
            'canonical_formula_sha256':ph,
            'committed_copy_path':str(output.relative_to(ROOT)),
            'computed_committed_git_blob':blob_bytes(primary),
            'independent_verified':False,
            'status':'SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION',
        })
    return {
        'artifact_id':'JANUS-TRUMP-UF150-001-020-OUT-OF-FAMILY-SOURCE-ACQUISITION-CANDIDATE-2026-09-18-v1.0',
        'gate':'TRUMP_UF150_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_GATE',
        'verdict':'PASS_UF150_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'authority_guard':g,
        'source_receipts':rows,
        'resource_receipt':receipt(20,40),
        'scientific_firewall':{'WL_SUFFICIENCY_WITHOUT_DIRECT_EXACT_CHECK':'NOT_PROVED','GENERAL_SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN'},
    }


if __name__ == '__main__':
    print(json.dumps(main(),sort_keys=True,separators=(',',':')))
