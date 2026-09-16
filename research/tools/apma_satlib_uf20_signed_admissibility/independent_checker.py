from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path


PREREG = Path("research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_PREREGISTRATION_2026-09-16.json")
PROOF = Path("research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_DIRECT_PROOF_2026-09-16.md")
EXPECTED = {
    str(PREREG): "90ac18670617bfb29e4a52f63b4c226ed498e5b6",
    str(PROOF): "e1515e047e53535882913d3764425814290f3334",
    "research/source_data/SATLIB_UF20_01_2026-09-16.cnf": "8330041b292e0501f8d74c1b1d32ca96c4498864",
    "research/source_data/SATLIB_UF20_02_2026-09-16.cnf": "f924caaef0d868bf62b1658e83e030ad8daee865",
    "research/source_data/SATLIB_UF20_03_2026-09-16.cnf": "8f3d15154515457281f49201b843f2a7134dfa9f",
    "research/source_data/SATLIB_UF20_04_2026-09-16.cnf": "34ced5c169f967b2dc44ef5e42f2ee2c924813e1",
    "research/source_data/SATLIB_UF20_05_2026-09-16.cnf": "3b04eff26ee37bdd0bc21b1066486974f92a2c9b",
}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def move(row: tuple[int, ...], perm: tuple[int, ...], eps: tuple[int, ...]) -> tuple[int, ...]:
    out = [0, 0, 0]
    for i in range(3):
        out[perm[i]] = row[i] ^ eps[i]
    return tuple(out)


def finite_counts() -> dict[str, int | bool]:
    cube = tuple(itertools.product((0, 1), repeat=3))
    relations = 0
    points = 0
    satisfaction = 0
    for forbidden in cube:
        relation = set(cube) - {forbidden}
        for perm in itertools.permutations(range(3)):
            for eps in cube:
                relations += 1
                moved_cube = {move(row, perm, eps) for row in cube}
                assert moved_cube == set(cube)
                points += len(cube)
                moved_relation = {move(row, perm, eps) for row in relation}
                assert set(cube) - moved_relation == {move(forbidden, perm, eps)}
                for a in cube:
                    satisfaction += 1
                    assert (a in relation) == (move(a, perm, eps) in moved_relation)
    return {
        "relation_transport_cases": relations,
        "assignment_bijection_points_checked": points,
        "satisfaction_equivariance_cases": satisfaction,
        "all_pass": True,
    }


def parse(path: Path) -> tuple[int, list[tuple[int, int, int]]]:
    n = None
    m = None
    clauses: list[tuple[int, int, int]] = []
    acc: list[int] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            _, kind, ns, ms = line.split()
            assert kind == "cnf"
            n, m = int(ns), int(ms)
            continue
        for x in map(int, line.split()):
            if x:
                acc.append(x)
            else:
                assert len(acc) == 3
                assert len({abs(z) for z in acc}) == 3
                clauses.append(tuple(acc))  # type: ignore[arg-type]
                acc = []
    assert n is not None and m is not None and not acc and len(clauses) == m
    return n, clauses


def partition(path: Path) -> dict[str, object]:
    n, clauses = parse(path)
    adj = {v: set() for v in range(1, n + 1)}
    pos = {v: 0 for v in range(1, n + 1)}
    neg = {v: 0 for v in range(1, n + 1)}
    for clause in clauses:
        vs = [abs(x) for x in clause]
        for u, v in itertools.combinations(vs, 2):
            adj[u].add(v)
            adj[v].add(u)
        for lit in clause:
            (pos if lit > 0 else neg)[abs(lit)] += 1
    buckets: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    ordered = []
    for v in range(1, n + 1):
        p, q = pos[v], neg[v]
        ordered.append([v, len(adj[v]), p, q])
        buckets[(len(adj[v]), min(p, q), max(p, q))].append(v)
    classes = sorted((sorted(xs) for xs in buckets.values()), key=lambda xs: (xs[0], len(xs), xs))
    nonsingle = [xs for xs in classes if len(xs) > 1]
    return {
        "variables": n,
        "clauses": len(clauses),
        "unsigned_S1_classes": classes,
        "class_count": len(classes),
        "all_singleton": len(classes) == n,
        "non_singleton_classes": nonsingle,
        "non_singleton_variable_count": sum(map(len, nonsingle)),
        "ordered_S1": ordered,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-json", type=Path, required=True)
    args = ap.parse_args()
    candidate = json.loads(args.candidate_json.read_text().strip().splitlines()[-1])

    guards = {path: blob(Path(path)) == expected for path, expected in EXPECTED.items()}
    expected_rows = []
    for idx in range(1, 6):
        name = f"UF20_{idx:02d}"
        expected_rows.append({"source": name, **partition(Path(f"research/source_data/SATLIB_UF20_{idx:02d}_2026-09-16.cnf"))})

    expected_finite = finite_counts()
    checks = {
        "source_guards": all(guards.values()),
        "candidate_verdict": candidate.get("verdict") == "PASS_SIGNED_ACTION_SEMANTICS_AND_UNSIGNED_S1_NECESSARY_INVARIANT",
        "candidate_authority": candidate.get("authority") == "DIAGNOSTIC_DEFINITION_AND_PROOF_SANITY_ONLY__NO_GROUP_SEARCH_SOLVER_OR_CARRIER",
        "finite_counts": all(candidate.get("finite_sanity", {}).get(k) == v for k, v in expected_finite.items()),
        "five_source_partitions": candidate.get("five_source_unsigned_S1_receipt") == expected_rows,
        "no_group_search": candidate.get("resource_receipt", {}).get("signed_group_elements_enumerated") == 0 and candidate.get("resource_receipt", {}).get("signed_automorphism_candidates_tested") == 0 and candidate.get("resource_receipt", {}).get("new_group_search_mechanisms") == 0,
        "no_solver_carrier": candidate.get("resource_receipt", {}).get("solver_invocations") == 0 and candidate.get("resource_receipt", {}).get("new_solver_mechanisms") == 0 and candidate.get("resource_receipt", {}).get("new_carrier_mechanisms") == 0,
        "no_quotient": candidate.get("resource_receipt", {}).get("quotient_states_enumerated") == 0,
        "firewall": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN" and candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
    }
    result = {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-SIGNED-AUTOMORPHISM-ADMISSIBILITY-INDEPENDENT-CHECK-2026-09-16-v1.0",
        "authority": "INDEPENDENT_DIAGNOSTIC_CHECK_ONLY",
        "candidate_imported": False,
        "source_guards": guards,
        "checks": checks,
        "verified": all(checks.values()),
        "independent_finite_sanity": expected_finite,
        "independent_five_source_unsigned_S1_receipt": expected_rows,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    if not result["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
