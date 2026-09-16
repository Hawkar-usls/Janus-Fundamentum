from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_SATLIB_UF20_SIGNATURE_ABLATION_REPLICATION_PREREGISTRATION_2026-09-16.json"
PARENT = ROOT / "research/TRUMP_SATLIB_UF20_FAMILY_ASYMMETRY_REPLICATION_RESULT_2026-09-16.json"
ORBIT = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
ORBIT_CHECKER = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py"
EXPECTED = {
    PREREG: "ec7c43258ecb76426f114dde9b75f528ad12e480",
    PARENT: "878a7417b1b631c405e80476751fd8a620bb992b",
    ORBIT: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
    ORBIT_CHECKER: "0e12304d843ef0bcce6b6c032fd2af2c68abcd14",
}
SOURCES = {
    "UF20_01": (ROOT / "research/source_data/SATLIB_UF20_01_2026-09-16.cnf", "8330041b292e0501f8d74c1b1d32ca96c4498864", "a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"),
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865", "e44b98343881d9f7657aa6c40fc6854559ca2cdd12e59edc7dddc22246d19d4f"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f", "7c9e05d9fa369935a0bf7d571b8c3b9a4a20244e3dfa75710987db2661553ac2"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1", "722b2479ea25355374d07b4d3c859c51af864b9158fda203270f1edda8e7086c"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b", "184f0f830dd2c2d1dd5fccd2b5b29304f27f15518b2b1e1315a4e9d5b5a30eb7"),
}


def git_blob_sha1(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode("ascii") + b).hexdigest()


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def source_guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): git_blob_sha1(p) == sha for p, sha in EXPECTED.items()}
    source_bindings = {name: git_blob_sha1(path) == blob for name, (path, blob, _) in SOURCES.items()}
    return {"ok": all(bindings.values()) and all(source_bindings.values()), "bindings": bindings, "source_bindings": source_bindings}


def parse_dimacs(path: Path) -> list[tuple[int, ...]]:
    clauses: list[tuple[int, ...]] = []
    declared = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("c") or s in {"%", "0"}:
            continue
        if s.startswith("p "):
            p = s.split()
            if len(p) != 4 or p[1] != "cnf":
                raise ValueError("BAD_DIMACS_HEADER")
            declared = (int(p[2]), int(p[3]))
            continue
        row = [int(x) for x in s.split()]
        if not row or row[-1] != 0:
            raise ValueError("BAD_DIMACS_CLAUSE")
        clause = tuple(row[:-1])
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError("NOT_DISTINCT_3CNF")
        clauses.append(clause)
    if declared != (20, 91) or len(clauses) != 91:
        raise ValueError("BAD_DIMACS_COUNTS")
    return clauses


def raw_from_clauses(source: str, clauses: list[tuple[int, ...]]) -> dict[str, Any]:
    constraints = []
    prefix = source.lower()
    for ordinal, clause in enumerate(clauses, 1):
        scope = sorted(abs(x) for x in clause)
        allowed = []
        for bits in itertools.product((0, 1), repeat=3):
            assignment = dict(zip(scope, bits))
            if any(bool(assignment[abs(lit)]) if lit > 0 else not bool(assignment[abs(lit)]) for lit in clause):
                allowed.append(list(bits))
        constraints.append({"id": f"satlib_{prefix}_c{ordinal:03d}", "scope": scope, "allowed": allowed})
    return canonicalize_raw({"variables": list(range(1, 21)), "constraints": constraints})


def relation_key(c: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted("".join(str(int(bit)) for bit in row) for row in c["allowed"]))


def frozen_feature_rows(raw: dict[str, Any], clauses: list[tuple[int, ...]]) -> dict[int, dict[str, Any]]:
    variables = raw["variables"]
    adj = {v: set() for v in variables}
    for c in raw["constraints"]:
        for u, v in itertools.combinations(c["scope"], 2):
            adj[u].add(v); adj[v].add(u)
    degree = {v: len(adj[v]) for v in variables}
    pos = Counter(); neg = Counter()
    for clause in clauses:
        for lit in clause:
            (pos if lit > 0 else neg)[abs(lit)] += 1
    surfaces = sorted({relation_key(c) for c in raw["constraints"]})
    if len(surfaces) != 8:
        raise ValueError(f"EXPECTED_EIGHT_RELATION_SURFACES_GOT_{len(surfaces)}")
    index = {surface: i for i, surface in enumerate(surfaces)}
    incidence = {v: [0] * len(surfaces) for v in variables}
    for c in raw["constraints"]:
        i = index[relation_key(c)]
        for v in c["scope"]:
            incidence[v][i] += 1
    return {
        v: {
            "S0": (degree[v],),
            "S1": (degree[v], pos[v], neg[v]),
            "S2": (degree[v], pos[v], neg[v], tuple(incidence[v])),
            "S3": (degree[v], pos[v], neg[v], tuple(incidence[v]), tuple(sorted(degree[n] for n in adj[v]))),
        }
        for v in variables
    }


def partition(features: dict[int, dict[str, Any]], level: str) -> list[list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for v in sorted(features):
        signature = features[v][level]
        key = json.dumps(signature, separators=(",", ":"))
        groups[key].append(v)
    classes = [sorted(vs) for vs in groups.values()]
    classes.sort(key=lambda c: (c[0], len(c), c))
    return classes


def component_sizes(vertices: list[int], edges: list[tuple[int, int]]) -> list[int]:
    adj = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    seen = set(); sizes = []
    for start in sorted(vertices):
        if start in seen:
            continue
        stack = [start]; seen.add(start); n = 0
        while stack:
            u = stack.pop(); n += 1
            for v in sorted(adj[u], reverse=True):
                if v not in seen:
                    seen.add(v); stack.append(v)
        sizes.append(n)
    return sorted(sizes, reverse=True)


def audit_level(formula: orbit.NormalizedFormula, classes: list[list[int]]) -> dict[str, Any]:
    non_singletons = [c for c in classes if len(c) > 1]
    tested = 0; exact_edges: list[tuple[int, int]] = []; class_rows = []
    for cls in classes:
        edges = []
        if len(cls) > 1:
            for u, v in itertools.combinations(cls, 2):
                tested += 1
                if orbit.is_exact_transposition_automorphism(formula, u, v):
                    edge = (u, v); edges.append(edge); exact_edges.append(edge)
        class_rows.append({
            "variables": cls,
            "size": len(cls),
            "candidate_pairs_tested": len(cls) * (len(cls) - 1) // 2,
            "exact_transposition_edges": [list(e) for e in edges],
            "exact_component_sizes": component_sizes(cls, edges),
        })
    if not non_singletons:
        outcome = "SIGNATURE_LEVEL_ALREADY_ALL_SINGLETON"
    elif exact_edges:
        outcome = "EXACT_TRANSPOSITION_SYMMETRY_REAPPEARS_WITHIN_COARSE_CLASS"
    else:
        outcome = "COARSE_CLASSES_EXIST_BUT_ALL_EXACT_TRANSPOSITIONS_FAIL"
    return {
        "outcome": outcome,
        "class_count": len(classes),
        "class_size_multiset": sorted((len(c) for c in classes), reverse=True),
        "max_class_size": max(len(c) for c in classes),
        "non_singleton_class_count": len(non_singletons),
        "variables_in_non_singleton_classes": sum(len(c) for c in non_singletons),
        "candidate_transposition_pairs_tested": tested,
        "exact_semantic_transposition_count": len(exact_edges),
        "exact_semantic_transposition_edges": [list(e) for e in exact_edges],
        "classes": class_rows,
    }


def audit_source(name: str, path: Path, expected_raw_sha: str) -> dict[str, Any]:
    clauses = parse_dimacs(path)
    raw = raw_from_clauses(name, clauses)
    observed_raw_sha = canonical_sha256(raw)
    if observed_raw_sha != expected_raw_sha:
        return {"source": name, "status": "RAW_SHA_GUARD_FAILURE", "expected_raw_sha256": expected_raw_sha, "observed_raw_sha256": observed_raw_sha}
    formula = orbit.validate_and_normalize(raw)
    features = frozen_feature_rows(raw, clauses)
    levels = {level: audit_level(formula, partition(features, level)) for level in ("S0", "S1", "S2", "S3")}
    first_all_singleton = next((level for level in ("S0", "S1", "S2", "S3") if levels[level]["non_singleton_class_count"] == 0), None)
    first_zero_exact_with_coarse_classes = next((level for level in ("S0", "S1", "S2", "S3") if levels[level]["non_singleton_class_count"] > 0 and levels[level]["exact_semantic_transposition_count"] == 0), None)
    return {
        "source": name,
        "status": "PROFILED",
        "raw_sha256": observed_raw_sha,
        "orbit_internal_semantic_sha256": formula.semantic_sha256,
        "levels": levels,
        "first_all_singleton_level": first_all_singleton,
        "first_zero_exact_with_coarse_classes": first_zero_exact_with_coarse_classes,
    }


def main() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"verdict": "SOURCE_OR_SEALED_PRIMITIVE_GUARD_FAILURE", "source_guard": guard}
    rows = [audit_source(name, path, raw_sha) for name, (path, _, raw_sha) in SOURCES.items()]
    if any(row.get("status") != "PROFILED" for row in rows):
        verdict = "SOURCE_OR_SEALED_PRIMITIVE_GUARD_FAILURE"
    else:
        outcomes = {row["levels"][level]["outcome"] for row in rows for level in ("S0", "S1", "S2", "S3")}
        if outcomes == {"COARSE_CLASSES_EXIST_BUT_ALL_EXACT_TRANSPOSITIONS_FAIL"}:
            verdict = "COARSE_CLASSES_EXIST_BUT_ALL_EXACT_TRANSPOSITIONS_FAIL"
        elif outcomes == {"SIGNATURE_LEVEL_ALREADY_ALL_SINGLETON"}:
            verdict = "SIGNATURE_LEVEL_ALREADY_ALL_SINGLETON"
        elif outcomes == {"EXACT_TRANSPOSITION_SYMMETRY_REAPPEARS_WITHIN_COARSE_CLASS"}:
            verdict = "EXACT_TRANSPOSITION_SYMMETRY_REAPPEARS_WITHIN_COARSE_CLASS"
        else:
            verdict = "MIXED_LEVEL_OUTCOMES"
    total_tests = sum(row.get("levels", {}).get(level, {}).get("candidate_transposition_pairs_tested", 0) for row in rows for level in ("S0", "S1", "S2", "S3"))
    total_exact = sum(row.get("levels", {}).get(level, {}).get("exact_semantic_transposition_count", 0) for row in rows for level in ("S0", "S1", "S2", "S3"))
    return {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-SIGNATURE-ABLATION-REPLICATION-2026-09-16-v1.0",
        "authority": "DIAGNOSTIC_ONLY__FROZEN_FEATURE_ABLATION_AND_EXISTING_ORBIT_REPLAY__NO_NEW_MECHANISM",
        "verdict": verdict,
        "source_guard": guard,
        "sealed_exact_transposition_primitive": {"path": str(ORBIT.relative_to(ROOT)), "blob": EXPECTED[ORBIT], "predicate": "is_exact_transposition_automorphism"},
        "rows": rows,
        "resource_receipt": {
            "candidate_transposition_pairs_tested": total_tests,
            "exact_semantic_transpositions_verified": total_exact,
            "pairs_outside_same_coarse_class_tested": 0,
            "quotient_states_enumerated": 0,
            "solver_invocations": 0,
            "full_variable_cube_states_enumerated": 0,
            "new_solver_mechanisms": 0,
            "new_carrier_mechanisms": 0,
            "new_representation_adapters": 0,
            "separator_branching": 0,
            "budget_raise": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
