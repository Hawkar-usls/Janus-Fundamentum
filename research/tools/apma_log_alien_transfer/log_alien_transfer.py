from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_interface_quotient.exact_quotient import solve_affine

ARTIFACT_ID = "JANUS-TRUMP-LOG-ALIEN-CONSTRAINT-EXACT-TRANSFER-CANDIDATE-2026-09-15-v1.0"
PREREG_REL = Path("research/TRUMP_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB_SHA1 = "99223e98059a00ad48ef6acda75450dc0ef029b7"
PREREG_COMMIT = "7d96bfe6a63035d31cb8a505e69c08198dfa3b23"

RELATIONS = {
    "OR2": ((0, 1), (1, 0), (1, 1)),
    "EVEN_XOR3": ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_constraints(rows: list[dict]) -> list[dict]:
    return sorted(
        ({"id": str(r["id"]), "kind": str(r["kind"]), "scope": tuple(int(v) for v in r["scope"])} for r in rows),
        key=lambda r: (r["kind"], r["scope"], r["id"]),
    )


def relation_holds(kind: str, scope: tuple[int, ...], witness: dict[int, int]) -> bool:
    return tuple(int(witness[v]) for v in scope) in RELATIONS[kind]


def replay_instance(instance: dict, witness: dict[int, int]) -> bool:
    constraints = canonical_constraints(instance["base_constraints"] + instance["alien_constraints"])
    try:
        return all(relation_holds(r["kind"], r["scope"], witness) for r in constraints)
    except KeyError:
        return False


def all_variables(instance: dict) -> list[int]:
    return sorted({int(v) for r in instance["base_constraints"] + instance["alien_constraints"] for v in r["scope"]})


def solve_or2_base(base: list[dict], pins: dict[int, int], variables: list[int]) -> dict:
    witness = {v: int(pins.get(v, 1)) for v in variables}
    bad = [r["id"] for r in base if not relation_holds("OR2", r["scope"], witness)]
    if bad:
        return {"status": "UNSAT", "reason": "PINNED_OR2_CONFLICT", "bad_constraints": bad}
    return {"status": "SAT", "witness": witness, "native_carrier": "OR2_BIJUNCTIVE_NATIVE"}


def solve_affine_base(base: list[dict], pins: dict[int, int], variables: list[int]) -> dict:
    index = {v: i for i, v in enumerate(variables)}
    A: list[list[int]] = []
    b: list[int] = []
    for r in base:
        row = [0] * len(variables)
        for v in r["scope"]:
            row[index[v]] ^= 1
        A.append(row)
        b.append(0)
    for v, bit in sorted(pins.items()):
        row = [0] * len(variables)
        row[index[v]] = 1
        A.append(row)
        b.append(int(bit))
    if not A:
        return {"status": "SAT", "witness": {v: 0 for v in variables}, "native_carrier": "AFFINE_GF2_NATIVE"}
    x = solve_affine(A, b)
    if x is None:
        return {"status": "UNSAT", "reason": "INCONSISTENT_PINNED_GF2_SYSTEM"}
    witness = {v: int(x[i]) for i, v in enumerate(variables)}
    if any(not relation_holds("EVEN_XOR3", r["scope"], witness) for r in base):
        raise AssertionError("AFFINE_NATIVE_REPLAY_FAILED")
    if any(witness[v] != bit for v, bit in pins.items()):
        raise AssertionError("AFFINE_PIN_REPLAY_FAILED")
    return {"status": "SAT", "witness": witness, "native_carrier": "AFFINE_GF2_NATIVE"}


def merge_alien_tuple_selection(aliens: list[dict], selected: tuple[tuple[int, ...], ...]) -> tuple[dict[int, int] | None, str | None]:
    pins: dict[int, int] = {}
    for relation, values in zip(aliens, selected):
        for v, bit in zip(relation["scope"], values):
            if v in pins and pins[v] != bit:
                return None, "OVERLAP_INCONSISTENT"
            pins[v] = int(bit)
    return pins, None


def solve_instance(instance: dict) -> dict:
    L = int(instance["L"])
    base_kind = str(instance["base_kind"])
    alien_kind = str(instance["alien_kind"])
    if (base_kind, alien_kind) not in {("OR2", "EVEN_XOR3"), ("EVEN_XOR3", "OR2")}:
        return {"status": "OPEN_UNSUPPORTED_ORIENTATION", "metrics": {"global_variable_assignments_enumerated": 0}}

    base = canonical_constraints(instance["base_constraints"])
    aliens = canonical_constraints(instance["alien_constraints"])
    if any(r["kind"] != base_kind for r in base) or any(r["kind"] != alien_kind for r in aliens):
        return {"status": "OPEN_UNSUPPORTED_ORIENTATION", "metrics": {"global_variable_assignments_enumerated": 0}}

    q = len(RELATIONS[alien_kind])
    k = len(aliens)
    branch_budget = q ** k
    if branch_budget > L:
        return {
            "status": "OPEN_ALIEN_TUPLE_BUDGET",
            "L": L,
            "k": k,
            "q": q,
            "q_pow_k": branch_budget,
            "branch_receipts": [],
            "metrics": {
                "alien_tuple_combinations_examined": 0,
                "overlap_inconsistent": 0,
                "native_solves": 0,
                "global_variable_assignments_enumerated": 0,
            },
        }

    variables = all_variables(instance)
    tuple_options = [RELATIONS[alien_kind] for _ in aliens]
    receipts: list[dict] = []
    overlap_bad = 0
    native_solves = 0
    examined = 0

    for branch_index, selected in enumerate(itertools.product(*tuple_options)):
        examined += 1
        pins, error = merge_alien_tuple_selection(aliens, selected)
        if error:
            overlap_bad += 1
            receipts.append({"branch": branch_index, "status": error})
            continue

        native_solves += 1
        if base_kind == "OR2":
            native = solve_or2_base(base, pins or {}, variables)
        else:
            native = solve_affine_base(base, pins or {}, variables)

        if native["status"] == "UNSAT":
            receipts.append({"branch": branch_index, "status": "NATIVE_UNSAT", "reason": native.get("reason")})
            continue

        witness = native["witness"]
        if not replay_instance(instance, witness):
            raise AssertionError("ORIGINAL_RELATION_REPLAY_FAILED")
        receipts.append({"branch": branch_index, "status": "SAT", "native_carrier": native["native_carrier"]})
        return {
            "status": "SAT",
            "L": L,
            "k": k,
            "q": q,
            "q_pow_k": branch_budget,
            "witness": witness,
            "winning_branch": branch_index,
            "branch_receipts": receipts,
            "exact_replay": True,
            "metrics": {
                "alien_tuple_combinations_examined": examined,
                "overlap_inconsistent": overlap_bad,
                "native_solves": native_solves,
                "global_variable_assignments_enumerated": 0,
            },
        }

    return {
        "status": "UNSAT",
        "L": L,
        "k": k,
        "q": q,
        "q_pow_k": branch_budget,
        "branch_receipts": receipts,
        "complete_branch_accounting": len(receipts) == branch_budget,
        "metrics": {
            "alien_tuple_combinations_examined": examined,
            "overlap_inconsistent": overlap_bad,
            "native_solves": native_solves,
            "global_variable_assignments_enumerated": 0,
        },
    }


def connected_or2_xor_sat() -> dict:
    return {
        "L": 64,
        "base_kind": "OR2",
        "alien_kind": "EVEN_XOR3",
        "base_constraints": [
            {"id": "force0", "kind": "OR2", "scope": [0, 0]},
            {"id": "b01", "kind": "OR2", "scope": [0, 1]},
            {"id": "b12", "kind": "OR2", "scope": [1, 2]},
            {"id": "b23", "kind": "OR2", "scope": [2, 3]},
            {"id": "b30", "kind": "OR2", "scope": [3, 0]},
            {"id": "b45", "kind": "OR2", "scope": [4, 5]},
            {"id": "b50", "kind": "OR2", "scope": [5, 0]},
            {"id": "b42", "kind": "OR2", "scope": [4, 2]},
        ],
        "alien_constraints": [
            {"id": "x024", "kind": "EVEN_XOR3", "scope": [0, 2, 4]},
            {"id": "x134", "kind": "EVEN_XOR3", "scope": [1, 3, 4]},
        ],
    }


def connected_or2_xor_unsat() -> dict:
    return {
        "L": 8,
        "base_kind": "OR2",
        "alien_kind": "EVEN_XOR3",
        "base_constraints": [
            {"id": "force0", "kind": "OR2", "scope": [0, 0]},
            {"id": "force1", "kind": "OR2", "scope": [1, 1]},
            {"id": "force2", "kind": "OR2", "scope": [2, 2]},
        ],
        "alien_constraints": [
            {"id": "x012", "kind": "EVEN_XOR3", "scope": [0, 1, 2]},
        ],
    }


def connected_affine_or2_sat() -> dict:
    return {
        "L": 16,
        "base_kind": "EVEN_XOR3",
        "alien_kind": "OR2",
        "base_constraints": [
            {"id": "x012", "kind": "EVEN_XOR3", "scope": [0, 1, 2]},
            {"id": "x234", "kind": "EVEN_XOR3", "scope": [2, 3, 4]},
        ],
        "alien_constraints": [
            {"id": "o03", "kind": "OR2", "scope": [0, 3]},
            {"id": "o14", "kind": "OR2", "scope": [1, 4]},
        ],
    }


def over_budget_control() -> dict:
    return {
        "L": 64,
        "base_kind": "OR2",
        "alien_kind": "EVEN_XOR3",
        "base_constraints": [{"id": "b01", "kind": "OR2", "scope": [0, 1]}],
        "alien_constraints": [
            {"id": f"x{i}", "kind": "EVEN_XOR3", "scope": [3 * i, 3 * i + 1, 3 * i + 2]}
            for i in range(4)
        ],
    }


def main() -> None:
    root = repo_root()
    prereg_path = root / PREREG_REL
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    source_guard = (
        git_blob_sha1(prereg_path) == PREREG_BLOB_SHA1
        and prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
        and prereg.get("artifact_id") == "JANUS-TRUMP-LOG-ALIEN-CONSTRAINT-EXACT-TRANSFER-PREREGISTRATION-2026-09-15-v1.0"
    )

    p1_instance = connected_or2_xor_sat()
    p2_instance = connected_or2_xor_unsat()
    p3_instance = connected_affine_or2_sat()
    n1_instance = over_budget_control()
    p1 = solve_instance(p1_instance)
    p2 = solve_instance(p2_instance)
    p3 = solve_instance(p3_instance)
    n1 = solve_instance(n1_instance)

    checks = {
        "source_guard": source_guard,
        "p1_connected_or2_xor_sat": p1["status"] == "SAT" and p1.get("exact_replay") is True,
        "p1_budget_admitted": p1["q_pow_k"] <= p1["L"],
        "p1_overlap_conflicts_observed": p1["metrics"]["overlap_inconsistent"] > 0,
        "p2_connected_or2_xor_unsat": p2["status"] == "UNSAT",
        "p2_complete_branch_accounting": p2.get("complete_branch_accounting") is True and len(p2["branch_receipts"]) == p2["q_pow_k"],
        "p3_connected_affine_or2_sat": p3["status"] == "SAT" and p3.get("exact_replay") is True,
        "p3_budget_admitted": p3["q_pow_k"] <= p3["L"],
        "n1_over_budget_fails_closed": n1["status"] == "OPEN_ALIEN_TUPLE_BUDGET" and n1["metrics"]["alien_tuple_combinations_examined"] == 0,
        "no_global_variable_cube": all(z["metrics"]["global_variable_assignments_enumerated"] == 0 for z in (p1, p2, p3, n1)),
    }
    verdict = "CANDIDATE_PASS_SCOPED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER" if all(checks.values()) else "CANDIDATE_FAIL_OR_OPEN"
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION",
        "prereg_commit": PREREG_COMMIT,
        "checks": checks,
        "controls": {"p1_sat": p1, "p2_unsat": p2, "p3_reverse_sat": p3, "n1_over_budget": n1},
        "complexity": {
            "case_A": "4^k alien tuple branches; admitted only when 4^k <= L",
            "case_B": "3^k alien tuple branches; admitted only when 3^k <= L",
            "per_branch": "polynomial overlap/pinning/native solve/original replay",
            "total": "L * poly(L) under frozen admission",
            "global_variable_cube_enumeration": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "UNRESTRICTED_CONNECTED_MIXED_CARRIER": "SCHAEFER_NP_COMPLETE_BARRIER_REMAINS",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
