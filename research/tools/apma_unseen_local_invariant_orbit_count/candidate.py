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
PREREG_BLOB = "5f02f06a920d838bca37f88c27c5053d7a606271"
DESIGN_BLOB = "bc6fedb8d8d7da8f17ccc53d30c8356745068ccd"

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


class InputContractError(ValueError):
    pass


@dataclass(frozen=True)
class Constraint:
    scope: tuple[int, ...]
    allowed: tuple[tuple[int, ...], ...]
    fingerprint: str


@dataclass(frozen=True)
class NormalizedFormula:
    variables: tuple[int, ...]
    constraints: tuple[Constraint, ...]
    semantic_bytes: bytes
    semantic_sha256: str
    L: int


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def source_guard() -> dict[str, Any]:
    observed_prereg = git_blob_sha1(PREREG_PATH)
    observed_design = git_blob_sha1(DESIGN_PATH)
    if observed_prereg != PREREG_BLOB:
        raise RuntimeError(
            f"PREREG_BLOB_MISMATCH expected={PREREG_BLOB} observed={observed_prereg}"
        )
    if observed_design != DESIGN_BLOB:
        raise RuntimeError(
            f"DESIGN_BLOB_MISMATCH expected={DESIGN_BLOB} observed={observed_design}"
        )
    return {
        "prereg_blob": observed_prereg,
        "design_blob": observed_design,
        "source_guard": True,
    }


def _ensure_int(value: Any, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputContractError(f"{what} must be an integer")
    return value


def _constraint_key(scope: Iterable[int], rows: Iterable[Iterable[int]]) -> tuple[Any, ...]:
    scope_list = list(scope)
    order = sorted(range(len(scope_list)), key=lambda i: scope_list[i])
    sorted_scope = tuple(scope_list[i] for i in order)
    canon_rows: set[tuple[int, ...]] = set()
    for raw_row in rows:
        row = tuple(raw_row)
        if len(row) != len(scope_list):
            raise InputContractError("allowed tuple length differs from scope arity")
        if any(bit not in (0, 1) for bit in row):
            raise InputContractError("allowed tuples must contain only 0/1")
        canon_rows.add(tuple(row[i] for i in order))
    return sorted_scope, tuple(sorted(canon_rows))


def _fingerprint_constraint(key: tuple[Any, ...]) -> str:
    scope, rows = key
    payload = json.dumps(
        {"scope": list(scope), "allowed": [list(r) for r in rows]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_and_normalize(raw: Any) -> NormalizedFormula:
    if not isinstance(raw, dict):
        raise InputContractError("raw object must be a JSON object")
    lower_keys = {str(k).lower() for k in raw}
    forbidden = sorted(lower_keys & FORBIDDEN_TRUST_KEYS)
    if forbidden:
        raise InputContractError(f"trusted metadata forbidden: {forbidden}")
    extra = set(raw) - TOP_LEVEL_KEYS
    missing = TOP_LEVEL_KEYS - set(raw)
    if extra:
        raise InputContractError(f"unexpected top-level keys: {sorted(extra)}")
    if missing:
        raise InputContractError(f"missing top-level keys: {sorted(missing)}")

    if not isinstance(raw["variables"], list):
        raise InputContractError("variables must be a list")
    variables = tuple(sorted(_ensure_int(v, "variable") for v in raw["variables"]))
    if len(set(variables)) != len(variables):
        raise InputContractError("variables must be distinct")
    variable_set = set(variables)

    if not isinstance(raw["constraints"], list):
        raise InputContractError("constraints must be a list")

    keys: list[tuple[Any, ...]] = []
    for index, c in enumerate(raw["constraints"]):
        if not isinstance(c, dict):
            raise InputContractError(f"constraint {index} must be an object")
        lower_constraint_keys = {str(k).lower() for k in c}
        forbidden_c = sorted(lower_constraint_keys & FORBIDDEN_TRUST_KEYS)
        if forbidden_c:
            raise InputContractError(
                f"constraint {index} contains trusted metadata: {forbidden_c}"
            )
        extra_c = set(c) - CONSTRAINT_KEYS
        if extra_c:
            raise InputContractError(
                f"constraint {index} unexpected keys: {sorted(extra_c)}"
            )
        if "scope" not in c or "allowed" not in c:
            raise InputContractError(f"constraint {index} missing scope/allowed")
        if not isinstance(c["scope"], list) or not isinstance(c["allowed"], list):
            raise InputContractError(f"constraint {index} scope/allowed must be lists")
        scope = [_ensure_int(v, f"constraint {index} scope variable") for v in c["scope"]]
        if len(set(scope)) != len(scope):
            raise InputContractError(f"constraint {index} repeats a scope variable")
        if any(v not in variable_set for v in scope):
            raise InputContractError(f"constraint {index} references undeclared variable")
        keys.append(_constraint_key(scope, c["allowed"]))

    keys.sort()
    serial = {
        "variables": list(variables),
        "constraints": [
            {"scope": list(scope), "allowed": [list(row) for row in rows]}
            for scope, rows in keys
        ],
    }
    semantic_bytes = json.dumps(
        serial, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    constraints = tuple(
        Constraint(scope, rows, _fingerprint_constraint((scope, rows)))
        for scope, rows in keys
    )
    return NormalizedFormula(
        variables=variables,
        constraints=constraints,
        semantic_bytes=semantic_bytes,
        semantic_sha256=hashlib.sha256(semantic_bytes).hexdigest(),
        L=len(semantic_bytes),
    )


def _formula_key_after_swap(formula: NormalizedFormula, u: int, v: int) -> tuple[Any, ...]:
    swapped_keys: list[tuple[Any, ...]] = []
    for c in formula.constraints:
        mapped_scope = [v if x == u else u if x == v else x for x in c.scope]
        swapped_keys.append(_constraint_key(mapped_scope, c.allowed))
    swapped_keys.sort()
    return tuple(swapped_keys)


def _formula_key(formula: NormalizedFormula) -> tuple[Any, ...]:
    return tuple((c.scope, c.allowed) for c in formula.constraints)


def is_exact_transposition_automorphism(
    formula: NormalizedFormula, u: int, v: int
) -> bool:
    if u == v:
        return True
    return _formula_key_after_swap(formula, u, v) == _formula_key(formula)


def discover_generator_edges(formula: NormalizedFormula) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    vars_list = list(formula.variables)
    for i, u in enumerate(vars_list):
        for v in vars_list[i + 1 :]:
            if is_exact_transposition_automorphism(formula, u, v):
                edges.append((u, v))
    return edges


def connected_cells(
    variables: tuple[int, ...], edges: list[tuple[int, int]]
) -> list[list[int]]:
    adjacency: dict[int, set[int]] = {v: set() for v in variables}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen: set[int] = set()
    cells: list[list[int]] = []
    for start in variables:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        cell: list[int] = []
        while stack:
            x = stack.pop()
            cell.append(x)
            for y in sorted(adjacency[x], reverse=True):
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        cells.append(sorted(cell))
    cells.sort(key=lambda c: (c[0], len(c), c))
    return cells


def spanning_tree_edges(
    cell: list[int], all_edges: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    if len(cell) <= 1:
        return []
    allowed = {tuple(sorted(e)) for e in all_edges if e[0] in cell and e[1] in cell}
    adjacency: dict[int, list[int]] = {v: [] for v in cell}
    for u, v in sorted(allowed):
        adjacency[u].append(v)
        adjacency[v].append(u)
    root = min(cell)
    seen = {root}
    queue = [root]
    tree: list[tuple[int, int]] = []
    while queue:
        u = queue.pop(0)
        for v in sorted(adjacency[u]):
            if v not in seen:
                seen.add(v)
                queue.append(v)
                tree.append((u, v))
    if seen != set(cell):
        raise RuntimeError("internal generator cell is not connected")
    return tree


def quotient_state_count(cells: list[list[int]], limit: int) -> tuple[int, bool]:
    q = 1
    for cell in cells:
        factor = len(cell) + 1
        if q > limit // factor:
            return limit + 1, False
        q *= factor
    return q, True


def assignment_from_counts(
    cells: list[list[int]], counts: tuple[int, ...]
) -> dict[int, int]:
    assignment: dict[int, int] = {}
    for cell, count in zip(cells, counts, strict=True):
        if not 0 <= count <= len(cell):
            raise ValueError("count outside cell range")
        for i, variable in enumerate(cell):
            assignment[variable] = 1 if i < count else 0
    return assignment


def first_violated_constraint(
    formula: NormalizedFormula, assignment: dict[int, int]
) -> Constraint | None:
    for c in formula.constraints:
        row = tuple(assignment[v] for v in c.scope)
        if row not in c.allowed:
            return c
    return None


def _resource_receipt(
    formula: NormalizedFormula,
    edges: list[tuple[int, int]],
    count_states_enumerated: int,
) -> dict[str, Any]:
    n = len(formula.variables)
    return {
        "input_bytes_L": formula.L,
        "variables_n": n,
        "constraints": len(formula.constraints),
        "transpositions_tested": n * (n - 1) // 2,
        "verified_generator_edges": len(edges),
        "count_states_enumerated": count_states_enumerated,
        "full_variable_cube_states_enumerated": 0,
        "global_residual_cartesian_products_materialized": 0,
        "separator_ge3_boolean_branches": 0,
        "size4_boolean_separator_assignments": 0,
        "new_unbounded_recursion": 0,
        "budget_raise": False,
        "symbolic_time_envelope": "O(L^4 log L)",
        "symbolic_certificate_envelope": "O(L^3)",
    }


def run_candidate(raw: Any) -> dict[str, Any]:
    guards = source_guard()
    try:
        formula = validate_and_normalize(raw)
    except InputContractError as exc:
        return {
            "mechanism": MECHANISM,
            "status": "REJECT_INPUT_CONTRACT",
            "reason": str(exc),
            "source_guards": guards,
            "solver_authority": False,
        }

    edges = discover_generator_edges(formula)
    cells = connected_cells(formula.variables, edges)
    nontrivial_cells = [cell for cell in cells if len(cell) >= 2]
    trees = [spanning_tree_edges(cell, edges) for cell in cells if len(cell) >= 2]
    base = {
        "mechanism": MECHANISM,
        "raw_semantic_sha256": formula.semantic_sha256,
        "input_bytes_L": formula.L,
        "variables_n": len(formula.variables),
        "constraints": len(formula.constraints),
        "generator_edges": [list(e) for e in edges],
        "cells": cells,
        "nontrivial_cells": nontrivial_cells,
        "generator_spanning_trees": [[list(e) for e in tree] for tree in trees],
        "source_guards": guards,
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        },
    }

    if not nontrivial_cells:
        return {
            **base,
            "status": "OPEN_NO_NONTRIVIAL_EXCHANGEABILITY",
            "solver_authority": False,
            "quotient_states_Q": None,
            "resource_receipt": _resource_receipt(formula, edges, 0),
        }

    limit = formula.L * formula.L
    q, within_cap = quotient_state_count(cells, limit)
    if not within_cap:
        return {
            **base,
            "status": "OPEN_ORBIT_COUNT_QUOTIENT_OVER_BUDGET",
            "solver_authority": False,
            "quotient_states_Q": q,
            "quotient_cap_L2": limit,
            "resource_receipt": _resource_receipt(formula, edges, 0),
        }

    full_cube_size = 1 << len(formula.variables)
    if q >= full_cube_size:
        return {
            **base,
            "status": "OPEN_NO_STRICT_ORBIT_COMPRESSION",
            "solver_authority": False,
            "quotient_states_Q": q,
            "quotient_cap_L2": limit,
            "resource_receipt": _resource_receipt(formula, edges, 0),
        }

    ranges = [range(len(cell) + 1) for cell in cells]
    unsat_rows: list[dict[str, Any]] = []
    enumerated = 0
    for counts in itertools.product(*ranges):
        enumerated += 1
        assignment = assignment_from_counts(cells, counts)
        violated = first_violated_constraint(formula, assignment)
        if violated is None:
            assignment_rows = [[v, assignment[v]] for v in formula.variables]
            return {
                **base,
                "status": "ADMIT_ORBIT_COUNT_QUOTIENT_SAT",
                "solver_authority": True,
                "quotient_states_Q": q,
                "quotient_cap_L2": limit,
                "strict_compression": True,
                "certificate": {
                    "type": "SAT",
                    "counts": list(counts),
                    "assignment": assignment_rows,
                    "constraints_replayed": len(formula.constraints),
                    "all_original_relations_true": True,
                },
                "resource_receipt": _resource_receipt(formula, edges, enumerated),
            }
        unsat_rows.append(
            {
                "counts": list(counts),
                "violated_constraint_fingerprint": violated.fingerprint,
            }
        )

    if enumerated != q:
        raise RuntimeError(f"quotient enumeration mismatch {enumerated} != {q}")
    return {
        **base,
        "status": "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT",
        "solver_authority": True,
        "quotient_states_Q": q,
        "quotient_cap_L2": limit,
        "strict_compression": True,
        "certificate": {
            "type": "UNSAT",
            "coverage_rows": unsat_rows,
            "coverage_count": len(unsat_rows),
        },
        "resource_receipt": _resource_receipt(formula, edges, enumerated),
    }


def _eq_relation() -> list[list[int]]:
    return [[0, 0], [1, 1]]


def _neq_relation() -> list[list[int]]:
    return [[0, 1], [1, 0]]


def _full_binary_relation() -> list[list[int]]:
    return [[0, 0], [0, 1], [1, 0], [1, 1]]


def revealed_equality_clique(n: int = 5) -> dict[str, Any]:
    return {
        "variables": list(range(n)),
        "constraints": [
            {"id": f"eq-{i}-{j}", "scope": [i, j], "allowed": _eq_relation()}
            for i in range(n)
            for j in range(i + 1, n)
        ],
    }


def revealed_odd_inequality_triangle() -> dict[str, Any]:
    return {
        "variables": [0, 1, 2],
        "constraints": [
            {"id": "neq-01", "scope": [0, 1], "allowed": _neq_relation()},
            {"id": "neq-12", "scope": [1, 2], "allowed": _neq_relation()},
            {"id": "neq-02", "scope": [0, 2], "allowed": _neq_relation()},
        ],
    }


def revealed_asymmetric_open_control() -> dict[str, Any]:
    return {
        "variables": [0, 1, 2, 3],
        "constraints": [
            {"id": "u0", "scope": [0], "allowed": [[0]]},
            {"id": "u1", "scope": [1], "allowed": [[1]]},
            {"id": "u2", "scope": [2], "allowed": [[0], [1]]},
            {"id": "u3", "scope": [3], "allowed": []},
            {"id": "b01", "scope": [0, 1], "allowed": _full_binary_relation()},
            {"id": "b12", "scope": [1, 2], "allowed": _full_binary_relation()},
            {"id": "b23", "scope": [2, 3], "allowed": _full_binary_relation()},
        ],
    }


def _renamed_and_reordered(raw: dict[str, Any]) -> dict[str, Any]:
    mapping = {v: 100 + 7 * v for v in raw["variables"]}
    constraints: list[dict[str, Any]] = []
    for c in reversed(raw["constraints"]):
        scope = [mapping[v] for v in reversed(c["scope"])]
        allowed = [list(reversed(row)) for row in reversed(c["allowed"])]
        constraints.append({"id": f"renamed-{c['id']}", "scope": scope, "allowed": allowed})
    return {"variables": [mapping[v] for v in reversed(raw["variables"])], "constraints": constraints}


def revealed_calibration() -> dict[str, Any]:
    guards = source_guard()
    sat_raw = revealed_equality_clique()
    sat = run_candidate(sat_raw)
    if sat["status"] != "ADMIT_ORBIT_COUNT_QUOTIENT_SAT":
        raise AssertionError(sat)

    unsat = run_candidate(revealed_odd_inequality_triangle())
    if unsat["status"] != "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT":
        raise AssertionError(unsat)

    open_result = run_candidate(revealed_asymmetric_open_control())
    if open_result["status"] != "OPEN_NO_NONTRIVIAL_EXCHANGEABILITY":
        raise AssertionError(open_result)

    renamed = run_candidate(_renamed_and_reordered(sat_raw))
    if renamed["status"] != sat["status"]:
        raise AssertionError((sat["status"], renamed["status"]))
    if sorted(map(len, renamed["cells"])) != sorted(map(len, sat["cells"])):
        raise AssertionError((sat["cells"], renamed["cells"]))
    if renamed["quotient_states_Q"] != sat["quotient_states_Q"]:
        raise AssertionError((sat["quotient_states_Q"], renamed["quotient_states_Q"]))

    injected = dict(sat_raw)
    injected["carrier"] = "TRUST_ME"
    rejected = run_candidate(injected)
    if rejected["status"] != "REJECT_INPUT_CONTRACT":
        raise AssertionError(rejected)

    return {
        "stage": "A_REVEALED_CALIBRATION_ONLY",
        "mechanism": MECHANISM,
        "source_guards": guards,
        "blind_authority_instantiated": False,
        "checks": {
            "revealed_symmetric_SAT": True,
            "revealed_symmetric_UNSAT": True,
            "revealed_asymmetric_OPEN_before_enumeration": True,
            "renaming_order_tuple_permutation_invariant_profile": True,
            "trusted_label_injection_rejected": True,
            "full_variable_cube_enumeration_zero": all(
                r.get("resource_receipt", {}).get("full_variable_cube_states_enumerated", 0) == 0
                for r in (sat, unsat, open_result, renamed)
            ),
        },
        "receipts": {
            "SAT": {
                "status": sat["status"],
                "cells": sat["cells"],
                "Q": sat["quotient_states_Q"],
                "raw_semantic_sha256": sat["raw_semantic_sha256"],
            },
            "UNSAT": {
                "status": unsat["status"],
                "cells": unsat["cells"],
                "Q": unsat["quotient_states_Q"],
                "coverage_count": unsat["certificate"]["coverage_count"],
                "raw_semantic_sha256": unsat["raw_semantic_sha256"],
            },
            "OPEN": {
                "status": open_result["status"],
                "cells": open_result["cells"],
                "raw_semantic_sha256": open_result["raw_semantic_sha256"],
            },
        },
        "scientific_firewall": {
            "GLOBAL_FRONTIER_ADVANCE": "NONE__REVEALED_CALIBRATION_ONLY",
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--revealed-calibration", action="store_true")
    args = parser.parse_args()

    if args.input_json is not None and args.revealed_calibration:
        raise SystemExit("choose either --input-json or --revealed-calibration")
    if args.input_json is not None:
        raw = json.loads(args.input_json.read_text(encoding="utf-8"))
        result = run_candidate(raw)
    else:
        result = revealed_calibration()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
