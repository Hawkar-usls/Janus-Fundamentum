from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


PREREG_PATH = Path("research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_PREREGISTRATION_2026-09-16.json")
PROOF_PATH = Path("research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_DIRECT_PROOF_2026-09-16.md")
PREREG_BLOB = "90ac18670617bfb29e4a52f63b4c226ed498e5b6"
PROOF_BLOB = "e1515e047e53535882913d3764425814290f3334"

SOURCES = {
    "UF20_01": (Path("research/source_data/SATLIB_UF20_01_2026-09-16.cnf"), "8330041b292e0501f8d74c1b1d32ca96c4498864"),
    "UF20_02": (Path("research/source_data/SATLIB_UF20_02_2026-09-16.cnf"), "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (Path("research/source_data/SATLIB_UF20_03_2026-09-16.cnf"), "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (Path("research/source_data/SATLIB_UF20_04_2026-09-16.cnf"), "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (Path("research/source_data/SATLIB_UF20_05_2026-09-16.cnf"), "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def source_guard() -> dict[str, object]:
    bindings = {
        str(PREREG_PATH): git_blob_sha1(PREREG_PATH) == PREREG_BLOB,
        str(PROOF_PATH): git_blob_sha1(PROOF_PATH) == PROOF_BLOB,
    }
    source_blobs: dict[str, str] = {}
    for name, (path, expected) in SOURCES.items():
        observed = git_blob_sha1(path)
        source_blobs[name] = observed
        bindings[str(path)] = observed == expected
    return {"ok": all(bindings.values()), "bindings": bindings, "source_blobs": source_blobs}


def cube(arity: int) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product((0, 1), repeat=arity))


def transport_row(row: tuple[int, ...], permutation: tuple[int, ...], epsilon: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(row)
    for old_i, target_i in enumerate(permutation):
        out[target_i] = row[old_i] ^ epsilon[old_i]
    return tuple(out)


def finite_arity3_sanity() -> dict[str, object]:
    rows = cube(3)
    relation_cases = 0
    satisfaction_cases = 0
    bijection_cases = 0
    for forbidden in rows:
        allowed = set(rows) - {forbidden}
        for permutation in itertools.permutations(range(3)):
            for epsilon in rows:
                relation_cases += 1
                transformed_all = {transport_row(row, permutation, epsilon) for row in rows}
                if transformed_all != set(rows):
                    raise AssertionError(("assignment_action_not_bijective", forbidden, permutation, epsilon))
                bijection_cases += len(rows)

                transformed_allowed = {transport_row(row, permutation, epsilon) for row in allowed}
                expected_forbidden = transport_row(forbidden, permutation, epsilon)
                missing = set(rows) - transformed_allowed
                if missing != {expected_forbidden}:
                    raise AssertionError(("forbidden_tuple_xor_rule_failed", forbidden, permutation, epsilon, missing, expected_forbidden))

                for assignment in rows:
                    satisfaction_cases += 1
                    transported_assignment = transport_row(assignment, permutation, epsilon)
                    if (assignment in allowed) != (transported_assignment in transformed_allowed):
                        raise AssertionError(("satisfaction_equivariance_failed", forbidden, permutation, epsilon, assignment))

    return {
        "arity": 3,
        "forbidden_tuples": 8,
        "coordinate_permutations": 6,
        "bit_flip_patterns": 8,
        "relation_transport_cases": relation_cases,
        "assignment_bijection_points_checked": bijection_cases,
        "satisfaction_equivariance_cases": satisfaction_cases,
        "all_pass": True,
    }


def parse_dimacs(path: Path) -> tuple[int, list[tuple[int, int, int]]]:
    nvars = None
    expected_clauses = None
    clauses: list[tuple[int, int, int]] = []
    pending: list[int] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise AssertionError(("bad_header", path, line))
            nvars = int(parts[2])
            expected_clauses = int(parts[3])
            continue
        for token in map(int, line.split()):
            if token == 0:
                if len(pending) != 3:
                    raise AssertionError(("non_3cnf_clause", path, pending))
                clause = tuple(pending)
                if len({abs(x) for x in clause}) != 3:
                    raise AssertionError(("repeated_variable_in_clause", path, clause))
                clauses.append(clause)  # type: ignore[arg-type]
                pending = []
            else:
                pending.append(token)
    if pending:
        raise AssertionError(("unterminated_clause", path, pending))
    if nvars is None or expected_clauses is None:
        raise AssertionError(("missing_header", path))
    if len(clauses) != expected_clauses:
        raise AssertionError(("clause_count_mismatch", path, len(clauses), expected_clauses))
    return nvars, clauses


def unsigned_partition(path: Path) -> dict[str, object]:
    nvars, clauses = parse_dimacs(path)
    adjacency: dict[int, set[int]] = {v: set() for v in range(1, nvars + 1)}
    positive = {v: 0 for v in range(1, nvars + 1)}
    negative = {v: 0 for v in range(1, nvars + 1)}

    for clause in clauses:
        vars_in_clause = [abs(lit) for lit in clause]
        for u, v in itertools.combinations(vars_in_clause, 2):
            adjacency[u].add(v)
            adjacency[v].add(u)
        for lit in clause:
            if lit > 0:
                positive[lit] += 1
            else:
                negative[-lit] += 1

    signatures: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    ordered_signatures: dict[int, tuple[int, int, int]] = {}
    for v in range(1, nvars + 1):
        p = positive[v]
        n = negative[v]
        ordered_signatures[v] = (len(adjacency[v]), p, n)
        signatures[(len(adjacency[v]), min(p, n), max(p, n))].append(v)

    classes = sorted((sorted(vs) for vs in signatures.values()), key=lambda xs: (xs[0], len(xs), xs))
    non_singleton = [xs for xs in classes if len(xs) > 1]
    return {
        "variables": nvars,
        "clauses": len(clauses),
        "unsigned_S1_classes": classes,
        "class_count": len(classes),
        "all_singleton": len(classes) == nvars,
        "non_singleton_classes": non_singleton,
        "non_singleton_variable_count": sum(len(xs) for xs in non_singleton),
        "ordered_S1": [[v, *ordered_signatures[v]] for v in range(1, nvars + 1)],
    }


def main() -> None:
    guard = source_guard()
    if not guard["ok"]:
        raise SystemExit(json.dumps({"status": "SOURCE_GUARD_FAILURE", "source_guard": guard}, sort_keys=True))

    sanity = finite_arity3_sanity()
    source_rows = []
    for source, (path, _) in SOURCES.items():
        source_rows.append({"source": source, **unsigned_partition(path)})

    result = {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-SIGNED-AUTOMORPHISM-ADMISSIBILITY-PROOF-SANITY-2026-09-16-v1.0",
        "authority": "DIAGNOSTIC_DEFINITION_AND_PROOF_SANITY_ONLY__NO_GROUP_SEARCH_SOLVER_OR_CARRIER",
        "source_guard": guard,
        "finite_sanity": sanity,
        "five_source_unsigned_S1_receipt": source_rows,
        "resource_receipt": {
            "signed_group_elements_enumerated": 0,
            "signed_automorphism_candidates_tested": 0,
            "solver_invocations": 0,
            "new_solver_mechanisms": 0,
            "new_carrier_mechanisms": 0,
            "new_group_search_mechanisms": 0,
            "quotient_states_enumerated": 0,
            "budget_raise": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        },
        "verdict": "PASS_SIGNED_ACTION_SEMANTICS_AND_UNSIGNED_S1_NECESSARY_INVARIANT",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
