from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_GENERIC_DIMACS_3CNF_PARSER_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_GENERIC_DIMACS_3CNF_PARSER_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
CANDIDATE = ROOT / 'research/tools/apma_generic_dimacs_3cnf_parser/candidate.py'
EXPECTED = {
    PREREG: '9f59895d989d47b9a1d5e485a9658bced424283c',
    REVIEW: '6f869c063d243df8da2b2e1889f2d7ccd44ded3f',
    CANDIDATE: '8937b4f9314c73be1718bfe7058b9263cf98fad7',
}


class IndependentParseError(ValueError):
    pass


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def parse_independent(data: bytes) -> dict[str, Any]:
    try:
        lines = data.decode('utf-8').splitlines()
    except UnicodeDecodeError as exc:
        raise IndependentParseError('decode') from exc
    n = m = None
    clauses: list[list[int]] = []
    pending: list[int] = []
    terminated = False
    body = False
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith('c'):
            continue
        if terminated:
            if s != '0':
                raise IndependentParseError('after_percent')
            continue
        if s == '%':
            terminated = True
            continue
        fields = s.split()
        if fields and fields[0] == 'p':
            if n is not None or body or pending or clauses:
                raise IndependentParseError('header_position_or_duplicate')
            if len(fields) != 4 or fields[1] != 'cnf':
                raise IndependentParseError('header_shape')
            try:
                n, m = int(fields[2]), int(fields[3])
            except ValueError as exc:
                raise IndependentParseError('header_integer') from exc
            if n <= 0 or m <= 0:
                raise IndependentParseError('header_positive')
            continue
        if n is None or m is None:
            raise IndependentParseError('missing_header')
        if s == '0' and not pending and len(clauses) == m:
            continue
        body = True
        try:
            integers = [int(x) for x in fields]
        except ValueError as exc:
            raise IndependentParseError('integer') from exc
        for z in integers:
            if z != 0:
                if len(clauses) >= m and not pending:
                    raise IndependentParseError('after_declared_count')
                pending.append(z)
                if len(pending) > 3:
                    raise IndependentParseError('arity_gt3')
                continue
            if len(pending) != 3:
                raise IndependentParseError('arity_not3')
            av = [abs(x) for x in pending]
            if len(set(av)) != 3:
                raise IndependentParseError('repeated_var')
            if min(av) < 1 or max(av) > n:
                raise IndependentParseError('range')
            clauses.append(list(pending))
            pending.clear()
            if len(clauses) > m:
                raise IndependentParseError('too_many')
    if n is None or m is None:
        raise IndependentParseError('missing_header_final')
    if pending:
        raise IndependentParseError('unterminated')
    if len(clauses) != m:
        raise IndependentParseError('count')
    canonical = ''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses).encode('ascii')
    return {'nvars': n, 'nclauses': m, 'clauses': clauses, 'canonical_formula_sha256': hashlib.sha256(canonical).hexdigest(), 'canonical_bytes_len': len(canonical)}


def controls() -> dict[str, bytes]:
    return {
        'N4_M2_STANDARD': b'c standard\np cnf 4 2\n1 -2 3 0\n-1 2 4 0\n',
        'N101_M1_SIZE_GENERIC': b'p cnf 101 1\n1 -50 101 0\n',
        'COMMENTS_WHITESPACE_PERCENT_AND_TRAILING_ZERO': b' c lead\n p cnf 6 2 \n 1 2 -6 0\nc middle\n-1   4 5 0\n%\n0\n',
        'CLAUSE_TOKENS_SPLIT_ACROSS_LINES': b'p cnf 5 1\n1 -2\n5 0\n',
        'MISSING_HEADER': b'1 2 3 0\n',
        'MULTIPLE_HEADERS': b'p cnf 3 1\np cnf 3 1\n1 2 3 0\n',
        'NONPOSITIVE_N_OR_M': b'p cnf 0 1\n1 2 3 0\n',
        'CLAUSE_ARITY_TWO': b'p cnf 3 1\n1 2 0\n',
        'CLAUSE_ARITY_FOUR': b'p cnf 4 1\n1 2 3 4 0\n',
        'REPEATED_ABSOLUTE_VARIABLE_IN_CLAUSE': b'p cnf 3 1\n1 -1 2 0\n',
        'LITERAL_OUTSIDE_DECLARED_RANGE': b'p cnf 3 1\n1 2 4 0\n',
        'CLAUSE_COUNT_MISMATCH': b'p cnf 4 2\n1 2 3 0\n',
        'UNTERMINATED_PARTIAL_CLAUSE': b'p cnf 4 1\n1 2 3\n',
        'FORMULA_TOKENS_AFTER_PERCENT_TERMINATOR': b'p cnf 4 1\n1 2 3 0\n%\n1 2 4 0\n',
    }


def main(candidate_path: Path) -> dict[str, Any]:
    candidate = json.loads(candidate_path.read_text())
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    positive = {'N4_M2_STANDARD', 'N101_M1_SIZE_GENERIC', 'COMMENTS_WHITESPACE_PERCENT_AND_TRAILING_ZERO', 'CLAUSE_TOKENS_SPLIT_ACROSS_LINES'}
    own_rows = []
    for name, data in controls().items():
        expected_accept = name in positive
        try:
            parsed = parse_independent(data)
            accepted = True
        except IndependentParseError:
            parsed = None
            accepted = False
        own_rows.append({'control': name, 'expected_accept': expected_accept, 'accepted': accepted, 'match': accepted == expected_accept, 'parsed': parsed})
    by_name = {r['control']: r for r in candidate.get('rows', [])}
    comparison = {}
    for row in own_rows:
        c = by_name.get(row['control'], {})
        comparison[row['control']] = {
            'acceptance_equal': c.get('accepted') == row['accepted'],
            'expectation_equal': c.get('expected_accept') == row['expected_accept'],
            'positive_parse_exact': (c.get('parsed') == row['parsed']) if row['accepted'] else True,
            'candidate_match_true': c.get('match') is True,
        }
    checks = {
        'authority_bindings': all(bindings.values()),
        'candidate_verdict_pass': candidate.get('verdict') == 'PASS_GENERIC_DIMACS_3CNF_PARSER_SYNTHETIC_CONTROLS',
        'own_controls_all_match': all(r['match'] for r in own_rows),
        'candidate_has_exact_control_set': set(by_name) == set(controls()),
        'full_comparison_pass': all(all(v.values()) for v in comparison.values()),
        'candidate_aim_reads_zero': candidate.get('resource_receipt', {}).get('reserved_aim_formula_reads') == 0,
        'candidate_science_actions_zero': all(candidate.get('resource_receipt', {}).get(k) == 0 for k in ('projection_computations','pendant_computations','wl_computations','portfolio_replays','solver_invocations')),
    }
    return {
        'artifact_id': 'JANUS-TRUMP-GENERIC-DIMACS-3CNF-PARSER-INDEPENDENT-CHECK-2026-09-17-v1.0',
        'verdict': 'PASS_INDEPENDENT_GENERIC_DIMACS_3CNF_PARSER_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_GENERIC_DIMACS_3CNF_PARSER_VERIFICATION',
        'candidate_imported': False,
        'checks': checks,
        'comparison': comparison,
        'independent_rows': own_rows,
        'resource_receipt': {'synthetic_controls': len(own_rows), 'reserved_aim_formula_reads': 0, 'projection_computations': 0, 'pendant_computations': 0, 'wl_computations': 0, 'portfolio_replays': 0, 'solver_invocations': 0},
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED'},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    result = main(Path(args.candidate))
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    raise SystemExit(0 if result['verdict'].startswith('PASS_') else 1)
