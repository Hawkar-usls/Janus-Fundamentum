from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


MECHANISM = "EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT"
PREREG_PATH = Path(
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE_PREREGISTRATION_2026-09-16.json"
)
DESIGN_PATH = Path(
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_A_DESIGN_2026-09-16.json"
)
CANDIDATE_PATH = Path(
    "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
)
PREREG_BLOB = "5f02f06a920d838bca37f88c27c5053d7a606271"
DESIGN_BLOB = "bc6fedb8d8d7da8f17ccc53d30c8356745068ccd"
CANDIDATE_BLOB = "a076cfc56d68aad0348415e313705da1f6b9cdcd"

TOP_LEVEL_KEYS = {"variables", "constraints"}
CONSTRAINT_KEYS = {"id", "scope", "allowed"}
FORBIDDEN_TRUST_KEYS = {
    "family",
    "family_name",
    "holdout",
    "holdout_name",
    "carrier",
    "carrier_label",
    "mechanism",
    "mechanism_label",
    "class",
    "kind",
    "base_kind",
    "alien_kind",
    "schaefer",
    "schaefer_class",
    "expected_invariant",
    "expected_quotient",
    "truth",
    "truth_label",
    "sat",
    "unsat",
    "reference_solution",
    "reference_carrier",
    "source_theorem",
}


class CheckError(RuntimeError):
    pass


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class Constraint:
    scope: tuple[int, ...]
    rows: tuple[tuple[int, ...], ...]
    fingerprint: str


@dataclass(frozen=True)
class Formula:
    variables: tuple[int, ...]
    constraints: tuple[Constraint, ...]
    semantic_sha256: str
    L: int


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def source_guard() -> dict[str, Any]:
    observed = {
        "prereg_blob": git_blob_sha1(PREREG_PATH),
        "design_blob": git_blob_sha1(DESIGN_PATH),
        "candidate_blob": git_blob_sha1(CANDIDATE_PATH),
    }
    expected = {
        "prereg_blob": PREREG_BLOB,
        "design_blob": DESIGN_BLOB,
        "candidate_blob": CANDIDATE_BLOB,
    }
    if observed != expected:
        raise CheckError(f"SOURCE_GUARD_MISMATCH expected={expected} observed={observed}")
    return {**observed, "source_guard": True, "candidate_imported": False}


def _as_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError(f"{label} must be int")
    return value


def _canon_constraint(scope: Iterable[int], raw_rows: Iterable[Iterable[int]]) -> tuple[Any, ...]:
    scope_list = list(scope)
    order = sorted(range(len(scope_list)), key=lambda i: scope_list[i])
    sorted_scope = tuple(scope_list[i] for i in order)
    rows: set[tuple[int, ...]] = set()
    for raw_row in raw_rows:
        row = tuple(raw_row)
        if len(row) != len(scope_list):
            raise InputError("row arity mismatch")
        if any(bit not in (0, 1) for bit in row):
            raise InputError("row is not Boolean")
        rows.add(tuple(row[i] for i in order))
    return sorted_scope, tuple(sorted(rows))


def _constraint_fp(key: tuple[Any, ...]) -> str:
    scope, rows = key
    data = json.dumps(
        {"scope": list(scope), "allowed": [list(r) for r in rows]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def normalize(raw: Any) -> Formula:
    if not isinstance(raw, dict):
        raise InputError("top-level object required")
    lower = {str(k).lower() for k in raw}
    if lower & FORBIDDEN_TRUST_KEYS:
        raise InputError("trusted metadata forbidden")
    if set(raw) != TOP_LEVEL_KEYS:
        raise InputError("top-level keys must be exactly variables,constraints")
    if not isinstance(raw["variables"], list) or not isinstance(raw["constraints"], list):
        raise InputError("variables/constraints must be lists")
    variables = tuple(sorted(_as_int(v, "variable") for v in raw["variables"]))
    if len(set(variables)) != len(variables):
        raise InputError("duplicate variable")
    varset = set(variables)

    keys: list[tuple[Any, ...]] = []
    for idx, c in enumerate(raw["constraints"]):
        if not isinstance(c, dict):
            raise InputError(f"constraint {idx} must be object")
        lower_c = {str(k).lower() for k in c}
        if lower_c & FORBIDDEN_TRUST_KEYS:
            raise InputError(f"constraint {idx} trusted metadata forbidden")
        if not set(c).issubset(CONSTRAINT_KEYS):
            raise InputError(f"constraint {idx} extra keys")
        if "scope" not in c or "allowed" not in c:
            raise InputError(f"constraint {idx} missing scope/allowed")
        if not isinstance(c["scope"], list) or not isinstance(c["allowed"], list):
            raise InputError(f"constraint {idx} scope/allowed must be lists")
        scope = [_as_int(v, f"constraint {idx} scope") for v in c["scope"]]
        if len(scope) != len(set(scope)):
            raise InputError(f"constraint {idx} repeated variable")
        if not set(scope).issubset(varset):
            raise InputError(f"constraint {idx} undeclared variable")
        keys.append(_canon_constraint(scope, c["allowed"]))

    keys.sort()
    semantic = json.dumps(
        {
            "variables": list(variables),
            "constraints": [
                {"scope": list(scope), "allowed": [list(r) for r in rows]}
                for scope, rows in keys
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    constraints = tuple(
        Constraint(scope, rows, _constraint_fp((scope, rows))) for scope, rows in keys
    )
    return Formula(
        variables=variables,
        constraints=constraints,
        semantic_sha256=hashlib.sha256(semantic).hexdigest(),
        L=len(semantic),
    )


def formula_key(formula: Formula) -> tuple[Any, ...]:
    return tuple((c.scope, c.rows) for c in formula.constraints)


def swapped_key(formula: Formula, u: int, v: int) -> tuple[Any, ...]:
    keys: list[tuple[Any, ...]] = []
    for c in formula.constraints:
        mapped_scope = [v if x == u else u if x == v else x for x in c.scope]
        keys.append(_canon_constraint(mapped_scope, c.rows))
    keys.sort()
    return tuple(keys)


def exact_swap(formula: Formula, u: int, v: int) -> bool:
    return swapped_key(formula, u, v) == formula_key(formula)


def all_generator_edges(formula: Formula) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    variables = list(formula.variables)
    for i, u in enumerate(variables):
        for v in variables[i + 1 :]:
            if exact_swap(formula, u, v):
                out.append((u, v))
    return out


def components(variables: tuple[int, ...], edges: list[tuple[int, int]]) -> list[list[int]]:
    adj = {v: set() for v in variables}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen: set[int] = set()
    out: list[list[int]] = []
    for start in variables:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        cell: list[int] = []
        while stack:
            x = stack.pop()
            cell.append(x)
            for y in sorted(adj[x], reverse=True):
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        out.append(sorted(cell))
    out.sort(key=lambda c: (c[0], len(c), c))
    return out


def q_count(cells: list[list[int]], limit: int) -> tuple[int, bool]:
    q = 1
    for cell in cells:
        f = len(cell) + 1
        if q > limit // f:
            return limit + 1, False
        q *= f
    return q, True


def assignment(cells: list[list[int]], counts: tuple[int, ...]) -> dict[int, int]:
    result: dict[int, int] = {}
    for cell, count in zip(cells, counts, strict=True):
        if not 0 <= count <= len(cell):
            raise CheckError("count outside cell")
        for index, var in enumerate(cell):
            result[var] = int(index < count)
    return result


def violated(formula: Formula, a: dict[int, int]) -> list[Constraint]:
    bad: list[Constraint] = []
    for c in formula.constraints:
        row = tuple(a[v] for v in c.scope)
        if row not in c.rows:
            bad.append(c)
    return bad


def _candidate_common_checks(candidate: dict[str, Any], formula: Formula) -> tuple[list[tuple[int, int]], list[list[int]]]:
    if candidate.get("mechanism") != MECHANISM:
        raise CheckError("wrong mechanism")
    if candidate.get("raw_semantic_sha256") != formula.semantic_sha256:
        raise CheckError("raw semantic hash mismatch")
    if candidate.get("input_bytes_L") != formula.L:
        raise CheckError("L mismatch")
    if candidate.get("variables_n") != len(formula.variables):
        raise CheckError("n mismatch")
    if candidate.get("constraints") != len(formula.constraints):
        raise CheckError("constraint count mismatch")
    expected_edges = all_generator_edges(formula)
    observed_edges = [tuple(e) for e in candidate.get("generator_edges", [])]
    if observed_edges != expected_edges:
        raise CheckError(f"generator edge mismatch expected={expected_edges} observed={observed_edges}")
    expected_cells = components(formula.variables, expected_edges)
    if candidate.get("cells") != expected_cells:
        raise CheckError("cell partition mismatch")
    expected_nontrivial = [c for c in expected_cells if len(c) >= 2]
    if candidate.get("nontrivial_cells") != expected_nontrivial:
        raise CheckError("nontrivial cell mismatch")

    trees = candidate.get("generator_spanning_trees", [])
    if len(trees) != len(expected_nontrivial):
        raise CheckError("spanning tree count mismatch")
    edge_set = set(expected_edges)
    for cell, raw_tree in zip(expected_nontrivial, trees, strict=True):
        tree = [tuple(e) for e in raw_tree]
        if len(tree) != len(cell) - 1:
            raise CheckError("spanning tree wrong edge count")
        adj = {v: set() for v in cell}
        for u, v in tree:
            e = tuple(sorted((u, v)))
            if e not in edge_set:
                raise CheckError("spanning tree contains unverified generator")
            if u not in adj or v not in adj:
                raise CheckError("spanning tree edge outside cell")
            adj[u].add(v)
            adj[v].add(u)
        seen = {cell[0]}
        stack = [cell[0]]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if seen != set(cell):
            raise CheckError("reported generator tree does not span cell")
    return expected_edges, expected_cells


def _resource_checks(candidate: dict[str, Any]) -> None:
    rr = candidate.get("resource_receipt")
    if not isinstance(rr, dict):
        raise CheckError("missing resource receipt")
    zero_fields = [
        "full_variable_cube_states_enumerated",
        "global_residual_cartesian_products_materialized",
        "separator_ge3_boolean_branches",
        "size4_boolean_separator_assignments",
        "new_unbounded_recursion",
    ]
    for field in zero_fields:
        if rr.get(field) != 0:
            raise CheckError(f"resource firewall violated: {field}={rr.get(field)}")
    if rr.get("budget_raise") is not False:
        raise CheckError("budget raise must be false")


def verify(raw: Any, candidate: dict[str, Any]) -> dict[str, Any]:
    guards = source_guard()
    try:
        formula = normalize(raw)
    except InputError as exc:
        if candidate.get("status") != "REJECT_INPUT_CONTRACT":
            raise CheckError(f"invalid input was not rejected: {exc}")
        return {
            "verified": True,
            "status": candidate.get("status"),
            "input_contract_rejection": True,
            "source_guards": guards,
        }

    candidate_guards = candidate.get("source_guards", {})
    if candidate_guards.get("prereg_blob") != PREREG_BLOB:
        raise CheckError("candidate prereg guard mismatch")
    if candidate_guards.get("design_blob") != DESIGN_BLOB:
        raise CheckError("candidate design guard mismatch")
    if candidate_guards.get("source_guard") is not True:
        raise CheckError("candidate source guard false")

    edges, cells = _candidate_common_checks(candidate, formula)
    status = candidate.get("status")
    nontrivial = [c for c in cells if len(c) >= 2]
    limit = formula.L * formula.L
    q, within = q_count(cells, limit)

    if status == "OPEN_NO_NONTRIVIAL_EXCHANGEABILITY":
        if nontrivial:
            raise CheckError("candidate opened for no symmetry despite nontrivial cell")
        if candidate.get("solver_authority") is not False:
            raise CheckError("OPEN carried solver authority")
        _resource_checks(candidate)
        return {
            "verified": True,
            "status": status,
            "cells": cells,
            "source_guards": guards,
        }

    if status == "OPEN_ORBIT_COUNT_QUOTIENT_OVER_BUDGET":
        if not nontrivial:
            raise CheckError("overbudget OPEN without nontrivial orbit")
        if within:
            raise CheckError("candidate claimed quotient over budget but Q is within cap")
        if candidate.get("solver_authority") is not False:
            raise CheckError("OPEN carried solver authority")
        _resource_checks(candidate)
        return {
            "verified": True,
            "status": status,
            "cells": cells,
            "Q_saturated": q,
            "source_guards": guards,
        }

    if status == "OPEN_NO_STRICT_ORBIT_COMPRESSION":
        if not nontrivial or not within:
            raise CheckError("strict-compression OPEN preconditions mismatch")
        if q < (1 << len(formula.variables)):
            raise CheckError("candidate claimed no strict compression but quotient is compressed")
        if candidate.get("solver_authority") is not False:
            raise CheckError("OPEN carried solver authority")
        _resource_checks(candidate)
        return {
            "verified": True,
            "status": status,
            "cells": cells,
            "Q": q,
            "source_guards": guards,
        }

    if status not in {
        "ADMIT_ORBIT_COUNT_QUOTIENT_SAT",
        "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT",
    }:
        raise CheckError(f"unknown candidate status: {status}")
    if not nontrivial:
        raise CheckError("admission without nontrivial exchangeability")
    if not within:
        raise CheckError("admission over quotient budget")
    if q >= (1 << len(formula.variables)):
        raise CheckError("admission without strict orbit compression")
    if candidate.get("solver_authority") is not True:
        raise CheckError("admitted carrier missing solver authority")
    if candidate.get("quotient_states_Q") != q:
        raise CheckError("Q mismatch")
    if candidate.get("quotient_cap_L2") != limit:
        raise CheckError("L^2 cap mismatch")
    _resource_checks(candidate)

    cert = candidate.get("certificate")
    if not isinstance(cert, dict):
        raise CheckError("missing certificate")

    if status.endswith("_SAT"):
        if cert.get("type") != "SAT":
            raise CheckError("SAT certificate type mismatch")
        raw_counts = cert.get("counts")
        if not isinstance(raw_counts, list) or len(raw_counts) != len(cells):
            raise CheckError("SAT count vector malformed")
        counts = tuple(_as_int(x, "SAT count") for x in raw_counts)
        expected_assignment = assignment(cells, counts)
        raw_assignment = cert.get("assignment")
        if not isinstance(raw_assignment, list):
            raise CheckError("SAT assignment malformed")
        observed_assignment: dict[int, int] = {}
        for row in raw_assignment:
            if not isinstance(row, list) or len(row) != 2:
                raise CheckError("SAT assignment row malformed")
            var = _as_int(row[0], "SAT assignment variable")
            bit = _as_int(row[1], "SAT assignment bit")
            if bit not in (0, 1):
                raise CheckError("SAT assignment bit non-Boolean")
            if var in observed_assignment:
                raise CheckError("SAT assignment duplicate variable")
            observed_assignment[var] = bit
        if observed_assignment != expected_assignment:
            raise CheckError("SAT assignment is not the canonical count representative")
        if violated(formula, observed_assignment):
            raise CheckError("SAT assignment violates an original relation")
        if cert.get("all_original_relations_true") is not True:
            raise CheckError("SAT replay flag false")
        return {
            "verified": True,
            "status": status,
            "raw_semantic_sha256": formula.semantic_sha256,
            "cells": cells,
            "Q": q,
            "counts": list(counts),
            "source_guards": guards,
            "checks": {
                "all_generator_edges_recomputed": True,
                "orbit_cells_recomputed": True,
                "quotient_cap_verified": True,
                "canonical_reconstruction_verified": True,
                "all_original_relations_replayed": True,
                "resource_firewalls": True,
            },
        }

    if cert.get("type") != "UNSAT":
        raise CheckError("UNSAT certificate type mismatch")
    rows = cert.get("coverage_rows")
    if not isinstance(rows, list) or cert.get("coverage_count") != len(rows):
        raise CheckError("UNSAT coverage malformed")
    if len(rows) != q:
        raise CheckError(f"UNSAT coverage count {len(rows)} != Q {q}")
    fp_to_constraints: dict[str, list[Constraint]] = {}
    for c in formula.constraints:
        fp_to_constraints.setdefault(c.fingerprint, []).append(c)

    expected_vectors = itertools.product(*[range(len(c) + 1) for c in cells])
    checked = 0
    for expected_counts, row in zip(expected_vectors, rows, strict=True):
        if not isinstance(row, dict):
            raise CheckError("UNSAT coverage row must be object")
        observed_counts = tuple(row.get("counts", []))
        if observed_counts != expected_counts:
            raise CheckError(
                f"UNSAT count coverage mismatch expected={expected_counts} observed={observed_counts}"
            )
        fp = row.get("violated_constraint_fingerprint")
        if fp not in fp_to_constraints:
            raise CheckError("UNSAT row cites unknown constraint fingerprint")
        a = assignment(cells, expected_counts)
        bad = violated(formula, a)
        if not bad:
            raise CheckError("UNSAT coverage contains satisfying quotient state")
        if fp not in {c.fingerprint for c in bad}:
            raise CheckError("UNSAT row cites a constraint not violated by representative")
        checked += 1
    if checked != q:
        raise CheckError("UNSAT independent coverage incomplete")

    return {
        "verified": True,
        "status": status,
        "raw_semantic_sha256": formula.semantic_sha256,
        "cells": cells,
        "Q": q,
        "coverage_checked": checked,
        "source_guards": guards,
        "checks": {
            "all_generator_edges_recomputed": True,
            "orbit_cells_recomputed": True,
            "quotient_cap_verified": True,
            "complete_count_vector_coverage": True,
            "every_quotient_state_independently_falsified": True,
            "resource_firewalls": True,
        },
    }


def eq_relation() -> list[list[int]]:
    return [[0, 0], [1, 1]]


def neq_relation() -> list[list[int]]:
    return [[0, 1], [1, 0]]


def full_binary() -> list[list[int]]:
    return [[0, 0], [0, 1], [1, 0], [1, 1]]


def fixture(name: str) -> dict[str, Any]:
    if name == "equality":
        n = 5
        return {
            "variables": list(range(n)),
            "constraints": [
                {"id": f"eq-{i}-{j}", "scope": [i, j], "allowed": eq_relation()}
                for i in range(n)
                for j in range(i + 1, n)
            ],
        }
    if name == "odd-neq":
        return {
            "variables": [0, 1, 2],
            "constraints": [
                {"id": "a", "scope": [0, 1], "allowed": neq_relation()},
                {"id": "b", "scope": [1, 2], "allowed": neq_relation()},
                {"id": "c", "scope": [0, 2], "allowed": neq_relation()},
            ],
        }
    if name == "asymmetric":
        return {
            "variables": [0, 1, 2, 3],
            "constraints": [
                {"id": "u0", "scope": [0], "allowed": [[0]]},
                {"id": "u1", "scope": [1], "allowed": [[1]]},
                {"id": "u2", "scope": [2], "allowed": [[0], [1]]},
                {"id": "u3", "scope": [3], "allowed": []},
                {"id": "b01", "scope": [0, 1], "allowed": full_binary()},
                {"id": "b12", "scope": [1, 2], "allowed": full_binary()},
                {"id": "b23", "scope": [2, 3], "allowed": full_binary()},
            ],
        }
    if name == "trusted-label":
        raw = fixture("equality")
        raw["carrier"] = "TRUSTED_FORBIDDEN"
        return raw
    raise CheckError(f"unknown revealed fixture name: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--candidate-json", type=Path)
    parser.add_argument(
        "--emit-fixture", choices=["equality", "odd-neq", "asymmetric", "trusted-label"]
    )
    args = parser.parse_args()

    if args.emit_fixture is not None:
        if args.input_json is not None or args.candidate_json is not None:
            raise SystemExit("--emit-fixture cannot be combined with verification inputs")
        print(json.dumps(fixture(args.emit_fixture), sort_keys=True, separators=(",", ":")))
        return

    if args.input_json is None or args.candidate_json is None:
        raise SystemExit("verification requires --input-json and --candidate-json")
    raw = json.loads(args.input_json.read_text(encoding="utf-8"))
    candidate = json.loads(
        args.candidate_json.read_text(encoding="utf-8").strip().splitlines()[-1]
    )
    try:
        receipt = verify(raw, candidate)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "verified": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        raise SystemExit(1) from exc
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
