from __future__ import annotations

import argparse
import base64
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_SOURCE_EXTENSION_SELECTION_PREREGISTRATION_2026-09-17.json'
EXPECTED_PREREG_BLOB = '9679bed3017df016002a10aa45ba249df198baa4'
ORDER = ('UF20_06', 'UF20_07', 'UF20_08', 'UF20_09', 'UF20_010')
SOURCES = {
    'UF20_06': ('uf20-06.cnf', ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf', '42d6feffa98dc1a213e019f28cf6bc7ddf94c0bf', 'Jany26/tree-aut-lib', '42d6feffa98dc1a213e019f28cf6bc7ddf94c0bf', 'dncarley/MolecularSimulation', '721a31c31419ea920ae672cc879dfaa8b07bd98c'),
    'UF20_07': ('uf20-07.cnf', ROOT/'research/source_data/SATLIB_UF20_07_2026-09-17.cnf', '9d7c4412e43bfd0e573ce8deab39c9d6e14d10b6', 'Jany26/tree-aut-lib', '9d7c4412e43bfd0e573ce8deab39c9d6e14d10b6', 'dncarley/MolecularSimulation', '75ca893b20054ecd7819426b5ffabb5fee4b2f26'),
    'UF20_08': ('uf20-08.cnf', ROOT/'research/source_data/SATLIB_UF20_08_2026-09-17.cnf', '461108f1c8f2eddeab2d8a902b1bc1d2c9b03e3e', 'Jany26/tree-aut-lib', '461108f1c8f2eddeab2d8a902b1bc1d2c9b03e3e', 'dncarley/MolecularSimulation', 'a37c997e4a9d1efaceddde48d65c709fa13a82c1'),
    'UF20_09': ('uf20-09.cnf', ROOT/'research/source_data/SATLIB_UF20_09_2026-09-17.cnf', '0dc336cbc82430deb22f64fdfb8c051c7493e5a0', 'Jany26/tree-aut-lib', '0dc336cbc82430deb22f64fdfb8c051c7493e5a0', 'dncarley/MolecularSimulation', 'a0c29bfed8c034ef817ee3c83de7b327d3d5db30'),
    'UF20_010': ('uf20-010.cnf', ROOT/'research/source_data/SATLIB_UF20_010_2026-09-17.cnf', 'afe1163b633a9f1844e20010f77e8f2d94bd52c5', 'Jany26/tree-aut-lib', 'afe1163b633a9f1844e20010f77e8f2d94bd52c5', 'dncarley/MolecularSimulation', '61a315ceafdcae95d00097c057119fa8183bf4e7'),
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_blob(repo: str, blob_sha: str) -> bytes:
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/git/blobs/{blob_sha}',
        headers={'User-Agent': 'Janus-Fundamentum-source-freeze-independent/1.0', 'Accept': 'application/vnd.github+json'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode('utf-8'))
    assert payload['sha'] == blob_sha and payload['encoding'] == 'base64', payload
    data = base64.b64decode(payload['content'])
    assert git_blob_sha(data) == blob_sha, (repo, blob_sha)
    return data


def independently_parse(data: bytes) -> tuple[int, int, list[list[int]], str]:
    nvars = nclauses = None
    clauses: list[list[int]] = []
    for raw in data.decode('utf-8').splitlines():
        s = raw.strip()
        if not s or s.startswith('c') or s in ('%', '0'):
            continue
        if s.startswith('p '):
            bits = s.split()
            assert bits[:2] == ['p', 'cnf'] and len(bits) == 4, bits
            nvars, nclauses = int(bits[2]), int(bits[3])
            continue
        vals = [int(x) for x in s.split()]
        assert vals[-1] == 0, vals
        clause = vals[:-1]
        assert len(clause) == 3, clause
        clauses.append(clause)
    assert nvars == 20 and nclauses == 91 and len(clauses) == 91
    assert all(1 <= abs(x) <= 20 for c in clauses for x in c)
    canonical = ''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses).encode('ascii')
    return nvars, nclauses, clauses, sha256(canonical)


def expected_rows() -> list[dict[str, Any]]:
    prereg = PREREG.read_bytes()
    assert git_blob_sha(prereg) == EXPECTED_PREREG_BLOB
    pre = json.loads(prereg.decode('utf-8'))
    assert tuple(pre['neutral_selection_rule']['selected_unseen_sources']) == ORDER
    rows = []
    for name in ORDER:
        filename, local_path, local_blob, primary_repo, primary_blob, verification_repo, verification_blob = SOURCES[name]
        local = local_path.read_bytes()
        assert git_blob_sha(local) == local_blob
        primary = exact_blob(primary_repo, primary_blob)
        verification = exact_blob(verification_repo, verification_blob)
        pn, pc, pclauses, pcanonical = independently_parse(primary)
        vn, vc, vclauses, vcanonical = independently_parse(verification)
        ln, lc, lclauses, lcanonical = independently_parse(local)
        ordered_equal = pclauses == vclauses == lclauses
        assert pn == vn == ln == 20 and pc == vc == lc == 91
        status = 'SOURCE_FROZEN' if ordered_equal else 'SOURCE_MISMATCH'
        rows.append({
            'source': name,
            'filename': filename,
            'status': status,
            'variables': pn,
            'clauses': pc,
            'clause_arity': 3,
            'ordered_clause_sequence_equal_across_primary_verification_and_committed_copy': ordered_equal,
            'primary_repo': primary_repo,
            'primary_git_blob': primary_blob,
            'primary_raw_sha256': sha256(primary),
            'verification_repo': verification_repo,
            'verification_git_blob': verification_blob,
            'verification_raw_sha256': sha256(verification),
            'committed_git_blob': local_blob,
            'committed_raw_sha256': sha256(local),
            'canonical_formula_sha256': pcanonical,
            'canonical_formula_sha256_equal_across_all_three': pcanonical == vcanonical == lcanonical,
            'raw_bytes_primary_equal_committed_copy': primary == local,
            'raw_bytes_primary_equal_verification_mirror': primary == verification,
        })
    return rows


def main(candidate_json: Path) -> dict[str, Any]:
    candidate = json.loads(candidate_json.read_text().strip().splitlines()[-1])
    rows = expected_rows()
    assert candidate['rows'] == rows, (candidate['rows'], rows)
    passed = all(r['status'] == 'SOURCE_FROZEN' and r['canonical_formula_sha256_equal_across_all_three'] for r in rows)
    verdict = 'PASS_UNSEEN_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FORMULA_FREEZE' if passed else 'HALT_SOURCE_ACQUISITION_MIRROR_OR_SHAPE_MISMATCH'
    assert candidate['verdict'] == verdict
    rr = candidate['resource_receipt']
    assert rr['sources'] == 5 and rr['remote_blob_fetches'] == 10
    assert rr['L3_values_computed'] == 0 and rr['S3_values_computed'] == 0 and rr['projected_partition_relations_computed'] == 0
    assert rr['solver_invocations'] == 0 and rr['portfolio_replays'] == 0 and rr['action_tests'] == 0 and rr['group_searches'] == 0 and rr['group_closure_computation'] == 0
    assert rr['new_feature_definitions'] == 0 and rr['new_graph_statistics'] == 0
    sf = candidate['scientific_firewall']
    assert sf['P_VS_NP'] == 'OPEN' and sf['GENERAL_SAT_IN_P'] == 'NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED'] == 'NO'
    return {
        'verified': True,
        'candidate_imported': False,
        'verdict': verdict,
        'sources_verified': 5,
        'L3_values_computed': 0,
        'S3_values_computed': 0,
        'rows': rows,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-json', required=True)
    args = parser.parse_args()
    print(json.dumps(main(Path(args.candidate_json)), sort_keys=True, separators=(',', ':')))
