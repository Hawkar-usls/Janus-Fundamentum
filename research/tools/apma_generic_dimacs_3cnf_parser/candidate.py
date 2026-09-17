from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_GENERIC_DIMACS_3CNF_PARSER_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_GENERIC_DIMACS_3CNF_PARSER_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
EXPECTED = {
    PREREG: '9f59895d989d47b9a1d5e485a9658bced424283c',
    REVIEW: '6f869c063d243df8da2b2e1889f2d7ccd44ded3f',
}


class Dimacs3CNFError(ValueError):
    pass


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def canonical_bytes(clauses: list[tuple[int, int, int]]) -> bytes:
    return ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses).encode('ascii')


def parse_dimacs_3cnf_bytes(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise Dimacs3CNFError('NON_UTF8_INPUT') from exc
    header: tuple[int, int] | None = None
    clauses: list[tuple[int, int, int]] = []
    buf: list[int] = []
    terminated = False
    body_started = False

    for lineno, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith('c'):
            continue
        if terminated:
            if s == '0':
                continue
            raise Dimacs3CNFError(f'FORMULA_TOKENS_AFTER_PERCENT_TERMINATOR@{lineno}')
        if s == '%':
            terminated = True
            continue
        if s.startswith('p '):
            if header is not None:
                raise Dimacs3CNFError(f'MULTIPLE_HEADERS@{lineno}')
            if body_started or buf or clauses:
                raise Dimacs3CNFError(f'LATE_HEADER@{lineno}')
            fields = s.split()
            if len(fields) != 4 or fields[:2] != ['p', 'cnf']:
                raise Dimacs3CNFError(f'INVALID_HEADER@{lineno}')
            try:
                nvars, nclauses = int(fields[2]), int(fields[3])
            except ValueError as exc:
                raise Dimacs3CNFError(f'INVALID_HEADER_INTEGER@{lineno}') from exc
            if nvars <= 0 or nclauses <= 0:
                raise Dimacs3CNFError(f'NONPOSITIVE_HEADER@{lineno}')
            header = (nvars, nclauses)
            continue
        if header is None:
            raise Dimacs3CNFError(f'MISSING_HEADER_BEFORE_BODY@{lineno}')
        if s == '0' and not buf and len(clauses) == header[1]:
            continue
        try:
            tokens = [int(x) for x in s.split()]
        except ValueError as exc:
            raise Dimacs3CNFError(f'NONINTEGER_TOKEN@{lineno}') from exc
        body_started = True
        for token in tokens:
            if token == 0:
                if not buf:
                    raise Dimacs3CNFError(f'EMPTY_CLAUSE_OR_EARLY_STANDALONE_ZERO@{lineno}')
                if len(buf) != 3:
                    raise Dimacs3CNFError(f'CLAUSE_ARITY_{len(buf)}@{lineno}')
                if len({abs(x) for x in buf}) != 3:
                    raise Dimacs3CNFError(f'REPEATED_ABSOLUTE_VARIABLE@{lineno}')
                if any(abs(x) < 1 or abs(x) > header[0] for x in buf):
                    raise Dimacs3CNFError(f'LITERAL_OUTSIDE_DECLARED_RANGE@{lineno}')
                clauses.append((buf[0], buf[1], buf[2]))
                buf = []
                if len(clauses) > header[1]:
                    raise Dimacs3CNFError(f'CLAUSE_COUNT_EXCEEDS_HEADER@{lineno}')
            else:
                if len(clauses) >= header[1] and not buf:
                    raise Dimacs3CNFError(f'FORMULA_TOKENS_AFTER_DECLARED_CLAUSES@{lineno}')
                buf.append(token)
                if len(buf) > 3:
                    raise Dimacs3CNFError(f'CLAUSE_ARITY_GT3@{lineno}')

    if header is None:
        raise Dimacs3CNFError('MISSING_HEADER')
    if buf:
        raise Dimacs3CNFError('UNTERMINATED_PARTIAL_CLAUSE')
    if len(clauses) != header[1]:
        raise Dimacs3CNFError(f'CLAUSE_COUNT_MISMATCH expected={header[1]} observed={len(clauses)}')
    canonical = canonical_bytes(clauses)
    return {
        'nvars': header[0],
        'nclauses': header[1],
        'clauses': [list(c) for c in clauses],
        'canonical_formula_sha256': hashlib.sha256(canonical).hexdigest(),
        'canonical_bytes_len': len(canonical),
    }


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


def main() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): git_blob(path) == expected for path, expected in EXPECTED.items()}
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    guards = {
        'authority_bindings': all(bindings.values()),
        'prereg_status': prereg.get('status') == 'FROZEN_BEFORE_GENERIC_PARSER_IMPLEMENTATION_AND_BEFORE_AIM_FORMULA_CONTENT_READ',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_GENERIC_DIMACS_3CNF_PARSER_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_RUN_SYNTHETIC_CONTROLS_ONLY',
    }
    if not all(guards.values()):
        return {'verdict': 'HALT_GENERIC_PARSER_AUTHORITY_FAILURE', 'guards': guards, 'bindings': bindings}
    positive = {'N4_M2_STANDARD', 'N101_M1_SIZE_GENERIC', 'COMMENTS_WHITESPACE_PERCENT_AND_TRAILING_ZERO', 'CLAUSE_TOKENS_SPLIT_ACROSS_LINES'}
    rows = []
    for name, data in controls().items():
        expected_accept = name in positive
        try:
            parsed = parse_dimacs_3cnf_bytes(data)
            accepted = True
            error = None
        except Dimacs3CNFError as exc:
            parsed = None
            accepted = False
            error = str(exc)
        rows.append({'control': name, 'expected_accept': expected_accept, 'accepted': accepted, 'match': accepted == expected_accept, 'parsed': parsed, 'error': error})
    passed = all(row['match'] for row in rows)
    return {
        'artifact_id': 'JANUS-TRUMP-GENERIC-DIMACS-3CNF-PARSER-CANDIDATE-2026-09-17-v1.0',
        'verdict': 'PASS_GENERIC_DIMACS_3CNF_PARSER_SYNTHETIC_CONTROLS' if passed else 'FAIL_GENERIC_DIMACS_3CNF_PARSER_SYNTHETIC_CONTROLS',
        'guards': guards,
        'rows': rows,
        'resource_receipt': {'synthetic_controls': len(rows), 'reserved_aim_formula_reads': 0, 'projection_computations': 0, 'pendant_computations': 0, 'wl_computations': 0, 'portfolio_replays': 0, 'solver_invocations': 0},
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED'},
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
