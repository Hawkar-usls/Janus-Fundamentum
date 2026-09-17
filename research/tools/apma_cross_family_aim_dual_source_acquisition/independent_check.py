from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

from research.tools.apma_generic_dimacs_3cnf_parser import independent_check as parser2

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_DUAL_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_DUAL_SOURCE_ACQUISITION_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
PANEL = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_PANEL_RESERVATION_PREREGISTRATION_2026-09-17_v1.0.json'
DISCOVERY = ROOT / 'research/TRUMP_CROSS_FAMILY_AIM_SECOND_SOURCE_DISCOVERY_RESULT_2026-09-17_v1.0.json'
PARSER_RESULT = ROOT / 'research/TRUMP_GENERIC_DIMACS_3CNF_PARSER_RESULT_2026-09-17_v1.0.json'
PARSER2_CODE = ROOT / 'research/tools/apma_generic_dimacs_3cnf_parser/independent_check.py'
ACQUISITION_CANDIDATE = ROOT / 'research/tools/apma_cross_family_aim_dual_source_acquisition/candidate.py'
EXPECTED = {
    PREREG: '210e2b16259ce726477c74652fb8d8868a0a8ba4',
    REVIEW: 'e9634d317c713acfb4c0f0dc52560b97fca0b8c5',
    PANEL: '737ce2def5953e1a727a8d50e772e59fcfc438be',
    DISCOVERY: '9b4698175d187a9c549d17fe8fc22d9cc71de20b',
    PARSER_RESULT: '81b406dcdd5c4c47cd00d8e8d8fd34a8000c6554',
    PARSER2_CODE: 'a05d9c44dca2f70ab0ad3700dedef6a5dd4e6020',
    ACQUISITION_CANDIDATE: '49ba5d210b73d3a2e1f89dbd73d32fe2924d2591',
}
A_REPO = 'dncarley/MolecularSimulation'
A_COMMIT = 'd23a1d1775a939af0a6032ec459e5055919843a7'
B_REPO = 'dmeoli/NeuroSAT'
B_COMMIT = '568b022fc0c56e7e24fe08c012753ef29c60938e'
BASENAMES = (
    'aim-100-1_6-no-1.cnf','aim-100-1_6-no-2.cnf','aim-100-1_6-no-3.cnf','aim-100-1_6-no-4.cnf',
    'aim-100-1_6-yes1-1.cnf','aim-100-1_6-yes1-2.cnf','aim-100-1_6-yes1-3.cnf','aim-100-1_6-yes1-4.cnf',
)


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def blob_file(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(repo: str, commit: str, basename: str) -> bytes:
    url = f'https://raw.githubusercontent.com/{repo}/{commit}/data/aim/{basename}'
    req = urllib.request.Request(url, headers={'User-Agent':'Janus-Fundamentum-AIM-independent-source-check/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def local_path(basename: str) -> Path:
    stem = basename[:-4] if basename.endswith('.cnf') else basename
    token = re.sub(r'[^A-Za-z0-9]+', '_', stem).strip('_').upper()
    return ROOT / f'research/source_data/SATLIB_AIM_{token}_2026-09-17.cnf'


def main(candidate_path: Path) -> dict[str, Any]:
    candidate = json.loads(candidate_path.read_text())
    bindings = {str(path.relative_to(ROOT)): blob_file(path) == expected for path, expected in EXPECTED.items()}
    own_rows = []
    for basename in BASENAMES:
        a = fetch(A_REPO, A_COMMIT, basename)
        b = fetch(B_REPO, B_COMMIT, basename)
        pa = parser2.parse_independent(a)
        pb = parser2.parse_independent(b)
        ordered_equal = pa['clauses'] == pb['clauses']
        n_m_equal = (pa['nvars'], pa['nclauses']) == (pb['nvars'], pb['nclauses'])
        canonical_equal = pa['canonical_formula_sha256'] == pb['canonical_formula_sha256']
        lp = local_path(basename)
        local = lp.read_bytes() if lp.exists() else b''
        own_rows.append({
            'basename': basename,
            'status': 'SOURCE_READY_TO_FREEZE' if ordered_equal and n_m_equal and canonical_equal else 'SOURCE_MISMATCH',
            'nvars': pa['nvars'],
            'nclauses': pa['nclauses'],
            'source_A_repo': A_REPO,
            'source_A_commit': A_COMMIT,
            'source_A_path': f'data/aim/{basename}',
            'source_A_git_blob': blob_bytes(a),
            'source_A_raw_sha256': sha256(a),
            'source_B_repo': B_REPO,
            'source_B_commit': B_COMMIT,
            'source_B_path': f'data/aim/{basename}',
            'source_B_git_blob': blob_bytes(b),
            'source_B_raw_sha256': sha256(b),
            'ordered_clause_sequence_equal': ordered_equal,
            'n_m_equal': n_m_equal,
            'canonical_formula_sha256_equal': canonical_equal,
            'canonical_formula_sha256': pa['canonical_formula_sha256'],
            'local_copy_path': str(lp.relative_to(ROOT)),
            'computed_local_git_blob': blob_bytes(a),
            'local_copy_exists': bool(local),
            'local_copy_byte_equal_source_A': local == a,
            'local_copy_git_blob_equal_source_A': blob_bytes(local) == blob_bytes(a) if local else False,
        })

    candidate_rows = candidate.get('rows', [])
    comparable_rows = []
    for own in own_rows:
        c = next((row for row in candidate_rows if row.get('basename') == own['basename']), None)
        if c is None:
            comparable_rows.append({'basename': own['basename'], 'match': False, 'reason': 'MISSING_CANDIDATE_ROW'})
            continue
        core = {k:v for k,v in own.items() if not k.startswith('local_copy_')}
        comparable_rows.append({'basename': own['basename'], 'match': c == core, 'local_copy_exists': own['local_copy_exists'], 'local_copy_byte_equal_source_A': own['local_copy_byte_equal_source_A'], 'local_copy_git_blob_equal_source_A': own['local_copy_git_blob_equal_source_A']})

    receipt = candidate.get('resource_receipt', {})
    checks = {
        'authority_bindings': all(bindings.values()),
        'candidate_pass': candidate.get('verdict') == 'PASS_AIM_DUAL_SOURCE_ACQUISITION_CANDIDATE',
        'candidate_exact_eight_rows': tuple(row.get('basename') for row in candidate_rows) == BASENAMES,
        'own_all_eight_pass': all(row['status'] == 'SOURCE_READY_TO_FREEZE' for row in own_rows),
        'candidate_rows_exact': all(row.get('match') is True for row in comparable_rows),
        'local_copies_exact': all(row.get('local_copy_exists') and row.get('local_copy_byte_equal_source_A') and row.get('local_copy_git_blob_equal_source_A') for row in comparable_rows),
        'metadata_firewall': candidate.get('metadata_firewall') == {'filename_yes_no_tokens_used': False, 'discovered_metadata_numbers_used': False},
        'structural_actions_zero': all(receipt.get(k) == 0 for k in ('projected_raw_computations','pendant_computations','wl_computations','portfolio_replays','route_labels','solver_invocations')),
        'fetch_and_parse_counts_exact': receipt.get('formula_body_fetches') == 16 and receipt.get('generic_3cnf_parses') == 16 and receipt.get('canonical_formula_hashes') == 16,
    }
    return {
        'artifact_id':'JANUS-TRUMP-CROSS-FAMILY-AIM-DUAL-SOURCE-ACQUISITION-INDEPENDENT-CHECK-2026-09-17-v1.0',
        'verdict':'PASS_INDEPENDENT_AIM_DUAL_SOURCE_ACQUISITION_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_AIM_DUAL_SOURCE_ACQUISITION_VERIFICATION',
        'candidate_imported':False,
        'checks':checks,
        'independent_rows':own_rows,
        'comparison':comparable_rows,
        'resource_receipt':{'formula_body_fetches':16,'generic_3cnf_parses':16,'canonical_formula_hashes':16,'projected_raw_computations':0,'pendant_computations':0,'wl_computations':0,'portfolio_replays':0,'route_labels':0,'solver_invocations':0},
        'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY':'NOT_PROVED'},
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True)
    args = ap.parse_args()
    result = main(Path(args.candidate))
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    raise SystemExit(0 if result['verdict'].startswith('PASS_') else 1)
