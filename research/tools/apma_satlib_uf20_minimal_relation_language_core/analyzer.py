from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORE_PREREGISTRATION_2026-09-16.json'
PARENT = ROOT / 'research/TRUMP_SATLIB_UF20_FAMILY_SEALED_PORTFOLIO_REPLICATION_RESULT_2026-09-16.json'
EXPECTED = {
    PREREG: 'b75582fe0e0cb53e5b55dcf37a84944477505f92',
    PARENT: '277214289387abf6cf7e2d97bdf7dcf1f1727e07',
}
SOURCES = {
    'UF20_01': (ROOT / 'research/source_data/SATLIB_UF20_01_2026-09-16.cnf', '8330041b292e0501f8d74c1b1d32ca96c4498864'),
    'UF20_02': (ROOT / 'research/source_data/SATLIB_UF20_02_2026-09-16.cnf', 'f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT / 'research/source_data/SATLIB_UF20_03_2026-09-16.cnf', '8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT / 'research/source_data/SATLIB_UF20_04_2026-09-16.cnf', '34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT / 'research/source_data/SATLIB_UF20_05_2026-09-16.cnf', '3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
RELATION_IDS = tuple(f'{i:03b}' for i in range(8))
BASIS = ('ZERO_VALID', 'ONE_VALID', 'HORN', 'DUAL_HORN', 'BIJUNCTIVE', 'AFFINE')
CUBE = tuple(itertools.product((0, 1), repeat=3))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def relation(rid: str) -> set[tuple[int, int, int]]:
    forbidden = tuple(int(x) for x in rid)
    return set(CUBE) - {forbidden}


def pairwise_closed(R, op) -> bool:
    return all(op(a, b) in R for a in R for b in R)


def triple_closed(R, op) -> bool:
    return all(op(a, b, c) in R for a in R for b in R for c in R)


def properties(rid: str) -> dict[str, bool]:
    R = relation(rid)
    bit_and = lambda a, b: tuple(x & y for x, y in zip(a, b))
    bit_or = lambda a, b: tuple(x | y for x, y in zip(a, b))
    majority = lambda a, b, c: tuple(1 if x + y + z >= 2 else 0 for x, y, z in zip(a, b, c))
    xor3 = lambda a, b, c: tuple(x ^ y ^ z for x, y, z in zip(a, b, c))
    return {
        'ZERO_VALID': (0, 0, 0) in R,
        'ONE_VALID': (1, 1, 1) in R,
        'HORN': pairwise_closed(R, bit_and),
        'DUAL_HORN': pairwise_closed(R, bit_or),
        'BIJUNCTIVE': triple_closed(R, majority),
        'AFFINE': triple_closed(R, xor3),
    }


def language_basis(ids: tuple[str, ...], prop_table: dict[str, dict[str, bool]]) -> list[str]:
    if not ids:
        return list(BASIS)
    return [b for b in BASIS if all(prop_table[r][b] for r in ids)]


def enumerate_languages(prop_table: dict[str, dict[str, bool]]) -> tuple[list[dict], list[list[str]]]:
    rows = []
    obstructions: list[tuple[str, ...]] = []
    for mask in range(256):
        ids = tuple(RELATION_IDS[i] for i in range(8) if mask & (1 << i))
        candidates = language_basis(ids, prop_table)
        obstruction = bool(ids) and not candidates
        if obstruction:
            obstructions.append(ids)
        rows.append({'mask': mask, 'relation_types': list(ids), 'candidate_basis': candidates, 'obstruction': obstruction})
    minimal = []
    obstruction_set = set(obstructions)
    for ids in obstructions:
        if all(tuple(x for x in ids if x != r) not in obstruction_set for r in ids):
            minimal.append(list(ids))
    minimal.sort(key=lambda x: (len(x), x))
    return rows, minimal


def parse_dimacs(path: Path) -> list[tuple[int, int, int]]:
    clauses = []
    declared = None
    pending = []
    for raw in path.read_text(encoding='utf-8').splitlines():
        s = raw.strip()
        if not s or s.startswith('c') or s in {'%', '0'}:
            continue
        if s.startswith('p '):
            p = s.split()
            assert len(p) == 4 and p[1] == 'cnf'
            declared = (int(p[2]), int(p[3]))
            continue
        for tok in map(int, s.split()):
            if tok == 0:
                assert len(pending) == 3
                assert len({abs(x) for x in pending}) == 3
                clauses.append(tuple(pending))
                pending = []
            else:
                pending.append(tok)
    assert declared == (20, 91) and len(clauses) == 91 and not pending
    return clauses


def relation_type_from_clause(clause: tuple[int, int, int]) -> str:
    ordered = sorted(clause, key=lambda lit: abs(lit))
    return ''.join('0' if lit > 0 else '1' for lit in ordered)


def source_receipt(path: Path, minimal_cores: list[list[str]]) -> dict:
    counts = Counter(relation_type_from_clause(c) for c in parse_dimacs(path))
    surface = sorted(counts)
    return {
        'relation_surface': surface,
        'all_eight_relation_types_present': surface == list(RELATION_IDS),
        'relation_type_counts': {r: counts[r] for r in RELATION_IDS},
        'minimal_core_presence': [
            {'core': core, 'present': all(r in counts for r in core)} for core in minimal_cores
        ],
    }


def main() -> dict:
    bindings = {str(p.relative_to(ROOT)): blob(p) == sha for p, sha in EXPECTED.items()}
    source_bindings = {name: blob(path) == sha for name, (path, sha) in SOURCES.items()}
    if not all(bindings.values()) or not all(source_bindings.values()):
        return {'verdict': 'SOURCE_OR_PARENT_GUARD_FAILURE', 'bindings': bindings, 'source_bindings': source_bindings}

    prop_table = {r: properties(r) for r in RELATION_IDS}
    languages, minimal_cores = enumerate_languages(prop_table)
    source_rows = [{'source': name, **source_receipt(path, minimal_cores)} for name, (path, _) in SOURCES.items()]
    surfaces_ok = all(row['all_eight_relation_types_present'] for row in source_rows)
    minimality_ok = all(
        not language_basis(tuple(core), prop_table)
        and all(language_basis(tuple(x for x in core if x != r), prop_table) for r in core)
        for core in minimal_cores
    )
    verdict = (
        'PASS_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORES_ENUMERATED'
        if minimal_cores and surfaces_ok and minimality_ok
        else 'NO_RELATION_LANGUAGE_OBSTRUCTION_FOUND' if not minimal_cores
        else 'SOURCE_RELATION_SURFACE_GUARD_FAILURE' if not surfaces_ok
        else 'MINIMALITY_CHECK_FAILURE'
    )
    return {
        'artifact_id': 'JANUS-TRUMP-SATLIB-UF20-MINIMAL-RELATION-LANGUAGE-OBSTRUCTION-CORE-2026-09-16-v1.0',
        'authority': 'DIAGNOSTIC_FINITE_RELATION_LANGUAGE_ANALYSIS_ONLY__NO_FORMULA_SOLVER_OR_MECHANISM',
        'verdict': verdict,
        'source_guard': {'ok': all(bindings.values()) and all(source_bindings.values()), 'bindings': bindings, 'source_bindings': source_bindings},
        'relation_property_table': prop_table,
        'language_count': len(languages),
        'obstruction_language_count': sum(1 for row in languages if row['obstruction']),
        'inclusion_minimal_obstruction_cores': minimal_cores,
        'minimal_core_count': len(minimal_cores),
        'source_presence': source_rows,
        'resource_receipt': {
            'relation_languages_enumerated': 256,
            'formula_subsets_enumerated': 0,
            'variable_assignment_cubes_enumerated': 0,
            'solver_invocations': 0,
            'new_solver_mechanisms': 0,
            'new_carrier_mechanisms': 0,
            'new_adapters': 0,
            'new_quotients': 0,
            'budget_raise': False,
        },
        'scientific_firewall': {
            'P_VS_NP': 'OPEN',
            'GENERAL_SAT_IN_P': 'NOT_PROVED',
            'GENERAL_GT2_TRACTABILITY': 'NOT_PROVED',
            'CONNECTED_MIXED_CORE_SOLVED': 'NO',
            'ARBITRARY_UNSEEN_INVARIANT_DISCOVERY': 'NOT_PROVED',
            'MINIMAL_LANGUAGE_CORE_IMPLIES_HARDNESS': False,
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
