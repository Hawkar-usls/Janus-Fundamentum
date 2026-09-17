from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

from research.tools.apma_generic_dimacs_3cnf_parser import candidate as parser

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_DUAL_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_DUAL_SOURCE_ACQUISITION_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
PANEL = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_PANEL_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
DISCOVERY = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_SECOND_SOURCE_DISCOVERY_RESULT_2026-09-17_v1.0.json'
PARSER_RESULT = ROOT / 'research/TRUMP_GENERIC_DIMACS_3CNF_PARSER_RESULT_2026-09-17_v1.0.json'
PARSER_CODE = ROOT / 'research/tools/apma_generic_dimacs_3cnf_parser/candidate.py'
EXPECTED = {
    PREREG: '210e2b16259ce726477c74652fb8d8868a0a8ba4',
    REVIEW: 'e9634d317c713acfb4c0f0dc52560b97fca0b8c5',
    PANEL: '737ce2def5953e1a727a8d50e772e59fcfc438be',
    DISCOVERY: '9b4698175d187a9c549d17fe8fc22d9cc71de20b',
    PARSER_RESULT: '81b406dcdd5c4c47cd00d8e8d8fd34a8000c6554',
    PARSER_CODE: '8937b4f9314c73be1718bfe7058b9263cf98fad7',
}
SOURCE_A_REPO = 'dncarley/MolecularSimulation'
SOURCE_A_COMMIT = 'd23a1d1775a939af0a6032ec459e5055919843a7'
SOURCE_B_REPO = 'dmeoli/NeuroSAT'
SOURCE_B_COMMIT = '568b022fc0c56e7e24fe08c012753ef29c60938e'
BASENAMES = (
    'aim-100-1_6-no-1.cnf',
    'aim-100-1_6-no-2.cnf',
    'aim-100-1_6-no-3.cnf',
    'aim-100-1_6-no-4.cnf',
    'aim-100-1_6-yes1-1.cnf',
    'aim-100-1_6-yes1-2.cnf',
    'aim-100-1_6-yes1-3.cnf',
    'aim-100-1_6-yes1-4.cnf',
)


def git_blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def git_blob_file(path: Path) -> str:
    return git_blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_url(repo: str, commit: str, basename: str) -> str:
    return f'https://raw.githubusercontent.com/{repo}/{commit}/data/aim/{basename}'


def fetch(repo: str, commit: str, basename: str) -> bytes:
    req = urllib.request.Request(raw_url(repo, commit, basename), headers={'User-Agent': 'Janus-Fundamentum-AIM-dual-source-freeze/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def local_path(basename: str) -> Path:
    stem = basename[:-4] if basename.endswith('.cnf') else basename
    token = re.sub(r'[^A-Za-z0-9]+', '_', stem).strip('_').upper()
    return ROOT / f'research/source_data/SATLIB_AIM_{token}_2026-09-17.cnf'


def authority_guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): git_blob_file(path) == expected for path, expected in EXPECTED.items()}
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    panel = json.loads(PANEL.read_text())
    discovery = json.loads(DISCOVERY.read_text())
    parser_result = json.loads(PARSER_RESULT.read_text())
    checks = {
        'authority_bindings': all(bindings.values()),
        'prereg_status': prereg.get('status') == 'FROZEN_BEFORE_FIRST_RESERVED_AIM_FORMULA_BODY_FETCH_FOR_CANONICAL_IDENTITY',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_AIM_DUAL_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_VALIDATE_COMPARE_AND_FREEZE_ALL_EIGHT_ONCE',
        'panel_exact': tuple(panel.get('reserved_sources', [])) == BASENAMES,
        'discovery_pass': discovery.get('verdict') == 'PASS_DISTINCT_PUBLIC_SECOND_SOURCE_FOUND_FOR_ALL_EIGHT_RESERVED_AIM_IDENTITIES',
        'source_b_exact': discovery.get('selected_source_B', {}).get('repo') == SOURCE_B_REPO and discovery.get('selected_source_B', {}).get('commit') == SOURCE_B_COMMIT,
        'parser_pass': parser_result.get('verdict') == 'PASS_GENERIC_DIMACS_3CNF_PARSER_INDEPENDENTLY_VERIFIED',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def main() -> dict[str, Any]:
    guard = authority_guard()
    zero = {'projected_raw_computations': 0, 'pendant_computations': 0, 'wl_computations': 0, 'portfolio_replays': 0, 'route_labels': 0, 'solver_invocations': 0}
    if not guard['ok']:
        return {'verdict': 'HALT_AIM_ACQUISITION_AUTHORITY_BINDING_FAILURE', 'authority_guard': guard, 'resource_receipt': {**zero, 'formula_body_fetches': 0, 'canonical_formula_hashes': 0}, 'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED'}}

    rows = []
    staged: list[tuple[Path, bytes]] = []
    for basename in BASENAMES:
        a = fetch(SOURCE_A_REPO, SOURCE_A_COMMIT, basename)
        b = fetch(SOURCE_B_REPO, SOURCE_B_COMMIT, basename)
        pa = parser.parse_dimacs_3cnf_bytes(a)
        pb = parser.parse_dimacs_3cnf_bytes(b)
        ordered_equal = pa['clauses'] == pb['clauses']
        n_m_equal = (pa['nvars'], pa['nclauses']) == (pb['nvars'], pb['nclauses'])
        canonical_equal = pa['canonical_formula_sha256'] == pb['canonical_formula_sha256']
        ok = ordered_equal and n_m_equal and canonical_equal
        lp = local_path(basename)
        rows.append({
            'basename': basename,
            'status': 'SOURCE_READY_TO_FREEZE' if ok else 'SOURCE_MISMATCH',
            'nvars': pa['nvars'],
            'nclauses': pa['nclauses'],
            'source_A_repo': SOURCE_A_REPO,
            'source_A_commit': SOURCE_A_COMMIT,
            'source_A_path': f'data/aim/{basename}',
            'source_A_git_blob': git_blob_bytes(a),
            'source_A_raw_sha256': sha256(a),
            'source_B_repo': SOURCE_B_REPO,
            'source_B_commit': SOURCE_B_COMMIT,
            'source_B_path': f'data/aim/{basename}',
            'source_B_git_blob': git_blob_bytes(b),
            'source_B_raw_sha256': sha256(b),
            'ordered_clause_sequence_equal': ordered_equal,
            'n_m_equal': n_m_equal,
            'canonical_formula_sha256_equal': canonical_equal,
            'canonical_formula_sha256': pa['canonical_formula_sha256'],
            'local_copy_path': str(lp.relative_to(ROOT)),
            'computed_local_git_blob': git_blob_bytes(a),
        })
        staged.append((lp, a))

    passed = all(row['status'] == 'SOURCE_READY_TO_FREEZE' for row in rows)
    if passed:
        for path, data in staged:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    return {
        'artifact_id': 'JANUS-TRUMP-CROSS-FAMILY-AIM-DUAL-SOURCE-ACQUISITION-CANDIDATE-2026-09-17-v1.0',
        'authority': 'DUAL_PUBLIC_SOURCE_PROVENANCE_AND_EXACT_FORMULA_IDENTITY_ONLY__NO_STRUCTURAL_EVALUATION',
        'verdict': 'PASS_AIM_DUAL_SOURCE_ACQUISITION_CANDIDATE' if passed else 'HALT_AIM_DUAL_SOURCE_FORMULA_IDENTITY_MISMATCH',
        'authority_guard': guard,
        'rows': rows,
        'resource_receipt': {**zero, 'reserved_sources': 8, 'formula_body_fetches': 16, 'generic_3cnf_parses': 16, 'canonical_formula_hashes': 16},
        'metadata_firewall': {'filename_yes_no_tokens_used': False, 'discovered_metadata_numbers_used': False},
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED', 'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED'},
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
