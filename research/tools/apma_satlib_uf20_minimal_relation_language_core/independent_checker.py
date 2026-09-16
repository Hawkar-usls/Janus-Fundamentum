from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORE_PREREGISTRATION_2026-09-16.json'
PARENT = ROOT / 'research/TRUMP_SATLIB_UF20_FAMILY_SEALED_PORTFOLIO_REPLICATION_RESULT_2026-09-16.json'
EXPECTED = {
    str(PREREG): 'b75582fe0e0cb53e5b55dcf37a84944477505f92',
    str(PARENT): '277214289387abf6cf7e2d97bdf7dcf1f1727e07',
}
SOURCES = {
    'UF20_01': (ROOT / 'research/source_data/SATLIB_UF20_01_2026-09-16.cnf', '8330041b292e0501f8d74c1b1d32ca96c4498864'),
    'UF20_02': (ROOT / 'research/source_data/SATLIB_UF20_02_2026-09-16.cnf', 'f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT / 'research/source_data/SATLIB_UF20_03_2026-09-16.cnf', '8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT / 'research/source_data/SATLIB_UF20_04_2026-09-16.cnf', '34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT / 'research/source_data/SATLIB_UF20_05_2026-09-16.cnf', '3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
RIDS = tuple(f'{i:03b}' for i in range(8))
BASES = ('ZERO_VALID', 'ONE_VALID', 'HORN', 'DUAL_HORN', 'BIJUNCTIVE', 'AFFINE')
CUBE = tuple(itertools.product((0, 1), repeat=3))


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def relation(rid: str):
    f = tuple(map(int, rid))
    return set(CUBE) - {f}


def bool_props(rid: str) -> dict[str, bool]:
    R = relation(rid)
    def aand(a, b): return tuple(x & y for x, y in zip(a, b))
    def oor(a, b): return tuple(x | y for x, y in zip(a, b))
    def maj(a, b, c): return tuple(int(x + y + z >= 2) for x, y, z in zip(a, b, c))
    def xor(a, b, c): return tuple(x ^ y ^ z for x, y, z in zip(a, b, c))
    return {
        'ZERO_VALID': (0, 0, 0) in R,
        'ONE_VALID': (1, 1, 1) in R,
        'HORN': all(aand(a, b) in R for a in R for b in R),
        'DUAL_HORN': all(oor(a, b) in R for a in R for b in R),
        'BIJUNCTIVE': all(maj(a, b, c) in R for a in R for b in R for c in R),
        'AFFINE': all(xor(a, b, c) in R for a in R for b in R for c in R),
    }


def candidates(ids: tuple[str, ...], table: dict[str, dict[str, bool]]) -> tuple[str, ...]:
    return tuple(b for b in BASES if all(table[r][b] for r in ids)) if ids else BASES


def independent_minimal_cores(table: dict[str, dict[str, bool]]) -> tuple[int, list[list[str]]]:
    obstructing = []
    for mask in range(1, 256):
        ids = tuple(RIDS[i] for i in range(8) if mask & (1 << i))
        if not candidates(ids, table):
            obstructing.append(ids)
    obs = set(obstructing)
    minimal = [list(ids) for ids in obstructing if all(tuple(x for x in ids if x != r) not in obs for r in ids)]
    minimal.sort(key=lambda x: (len(x), x))
    return len(obstructing), minimal


def parse_dimacs(path: Path):
    clauses = []
    buf = []
    header = None
    for raw in path.read_text(encoding='utf-8').splitlines():
        s = raw.strip()
        if not s or s.startswith('c') or s in {'%', '0'}:
            continue
        if s.startswith('p '):
            p = s.split(); header = (int(p[2]), int(p[3])); continue
        for x in map(int, s.split()):
            if x == 0:
                assert len(buf) == 3 and len({abs(y) for y in buf}) == 3
                clauses.append(tuple(buf)); buf = []
            else:
                buf.append(x)
    assert header == (20, 91) and len(clauses) == 91 and not buf
    return clauses


def clause_rid(clause) -> str:
    return ''.join('0' if lit > 0 else '1' for lit in sorted(clause, key=lambda z: abs(z)))


def source_projection(path: Path, cores: list[list[str]]) -> dict:
    cnt = Counter(clause_rid(c) for c in parse_dimacs(path))
    surface = sorted(cnt)
    return {
        'relation_surface': surface,
        'all_eight_relation_types_present': surface == list(RIDS),
        'relation_type_counts': {r: cnt[r] for r in RIDS},
        'minimal_core_presence': [{'core': c, 'present': all(r in cnt for r in c)} for c in cores],
    }


def main(candidate: dict) -> dict:
    guards = {str(Path(path).relative_to(ROOT)): git_blob(Path(path)) == sha for path, sha in EXPECTED.items()}
    source_guards = {name: git_blob(path) == sha for name, (path, sha) in SOURCES.items()}
    table = {r: bool_props(r) for r in RIDS}
    obstruction_count, minimal = independent_minimal_cores(table)
    sources = [{'source': name, **source_projection(path, minimal)} for name, (path, _) in SOURCES.items()]
    checks = {
        'candidate_not_imported': True,
        'guards': all(guards.values()) and all(source_guards.values()),
        'verdict': candidate.get('verdict') == 'PASS_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORES_ENUMERATED',
        'language_count': candidate.get('language_count') == 256,
        'obstruction_language_count': candidate.get('obstruction_language_count') == obstruction_count,
        'relation_property_table': candidate.get('relation_property_table') == table,
        'minimal_cores': candidate.get('inclusion_minimal_obstruction_cores') == minimal,
        'minimal_core_count': candidate.get('minimal_core_count') == len(minimal),
        'source_presence': candidate.get('source_presence') == sources,
        'all_source_surfaces': all(x['all_eight_relation_types_present'] for x in sources),
        'all_minimal_cores_present': all(all(c['present'] for c in x['minimal_core_presence']) for x in sources),
    }
    rr = candidate.get('resource_receipt', {})
    checks['resources'] = (
        rr.get('relation_languages_enumerated') == 256 and rr.get('formula_subsets_enumerated') == 0
        and rr.get('variable_assignment_cubes_enumerated') == 0 and rr.get('solver_invocations') == 0
        and rr.get('new_solver_mechanisms') == 0 and rr.get('new_carrier_mechanisms') == 0
        and rr.get('new_adapters') == 0 and rr.get('new_quotients') == 0 and rr.get('budget_raise') is False
    )
    sf = candidate.get('scientific_firewall', {})
    checks['firewall'] = sf.get('P_VS_NP') == 'OPEN' and sf.get('GENERAL_SAT_IN_P') == 'NOT_PROVED' and sf.get('MINIMAL_LANGUAGE_CORE_IMPLIES_HARDNESS') is False
    return {
        'artifact_id': 'JANUS-TRUMP-SATLIB-UF20-MINIMAL-RELATION-LANGUAGE-OBSTRUCTION-CORE-INDEPENDENT-CHECK-2026-09-16-v1.0',
        'candidate_imported': False,
        'verified': all(checks.values()),
        'checks': checks,
        'independent_obstruction_language_count': obstruction_count,
        'independent_minimal_cores': minimal,
        'independent_source_presence': sources,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate-json', required=True)
    args = ap.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text().strip().splitlines()[-1])
    out = main(candidate)
    print(json.dumps(out, sort_keys=True, separators=(',', ':')))
    if not out['verified']:
        raise SystemExit(1)
