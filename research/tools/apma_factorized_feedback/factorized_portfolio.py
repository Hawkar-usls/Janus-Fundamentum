from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

from research.tools.apma_interface_quotient.exact_quotient import solve_affine

ARTIFACT_ID = "JANUS-TRUMP-FACTORIZED-FEEDBACK-INTERFACE-PORTFOLIO-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG_REL = Path("research/TRUMP_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "8235a16f956f388eb79c0f15961e22db7c088558"
PREREG_GIT_BLOB_SHA1 = "7410a1169e4c117ccdab929c13ff4b0312edef1c"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_components(vertices: Iterable[int], obligations: list[dict]) -> list[list[int]]:
    verts = sorted(set(int(v) for v in vertices))
    parent = {v: v for v in verts}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra > rb:
                ra, rb = rb, ra
            parent[rb] = ra

    for ob in obligations:
        scope = sorted(set(int(v) for v in ob.get("scope", [])))
        if any(v not in parent for v in scope):
            raise ValueError("OBLIGATION_SCOPE_OUTSIDE_B")
        for v in scope[1:]:
            union(scope[0], v)

    groups: dict[int, list[int]] = {}
    for v in verts:
        groups.setdefault(find(v), []).append(v)
    return sorted((sorted(xs) for xs in groups.values()), key=lambda xs: (xs[0], len(xs), xs))


def component_obligations(component: list[int], obligations: list[dict]) -> list[dict]:
    s = set(component)
    out = []
    for ob in obligations:
        scope = set(int(v) for v in ob.get("scope", []))
        if scope & s:
            if not scope <= s:
                raise AssertionError("CROSS_COMPONENT_SCOPE_AFTER_CANONICALIZATION")
            out.append(ob)
    return out


def bits_for(mask: int, variables: list[int]) -> dict[int, int]:
    return {v: (mask >> i) & 1 for i, v in enumerate(variables)}


def raw_table_holds(ob: dict, assignment: dict[int, int]) -> bool:
    scope = [int(v) for v in ob["scope"]]
    word = "".join(str(assignment[v]) for v in scope)
    return word in set(ob.get("allowed", []))


def affine_holds(ob: dict, assignment: dict[int, int]) -> bool:
    total = 0
    for k, bit in ob.get("coeff", {}).items():
        if int(bit) & 1:
            total ^= assignment[int(k)]
    return total == (int(ob.get("rhs", 0)) & 1)


def replay_obligations(obligations: list[dict], witness: dict[int, int]) -> bool:
    for ob in obligations:
        kind = ob.get("kind")
        if kind == "raw_table" and not raw_table_holds(ob, witness):
            return False
        if kind == "affine_eq" and not affine_holds(ob, witness):
            return False
        if kind not in {"raw_table", "affine_eq"}:
            return False
    return True


def solve_raw(component: list[int], obligations: list[dict], L: int) -> dict:
    log_budget = int(math.floor(math.log2(max(2, L))))
    if len(component) > log_budget:
        return {"status": "OPEN_UNSUPPORTED_LOCAL_CARRIER", "reason": "RAW_COMPONENT_EXCEEDS_LOG_BUDGET"}
    examined = 0
    for mask in range(1 << len(component)):
        examined += 1
        witness = bits_for(mask, component)
        if all(raw_table_holds(ob, witness) for ob in obligations):
            return {
                "status": "SAT",
                "carrier": "SEALED_RAW_LOG_WIDTH_CONDITIONING",
                "witness": witness,
                "local_assignments_examined": examined,
                "local_state_bound": 1 << len(component),
            }
    return {
        "status": "UNSAT",
        "carrier": "SEALED_RAW_LOG_WIDTH_CONDITIONING",
        "certificate": "EXHAUSTED_ALL_LOCAL_ASSIGNMENTS_WITHIN_LOG_WIDTH",
        "local_assignments_examined": examined,
        "local_state_bound": 1 << len(component),
    }


def solve_affine_component(component: list[int], obligations: list[dict], L: int) -> dict:
    index = {v: i for i, v in enumerate(component)}
    A: list[list[int]] = []
    b: list[int] = []
    for ob in obligations:
        row = [0] * len(component)
        for k, bit in ob.get("coeff", {}).items():
            v = int(k)
            if v not in index:
                return {"status": "OPEN_UNSUPPORTED_LOCAL_CARRIER", "reason": "AFFINE_SCOPE_MISMATCH"}
            row[index[v]] ^= int(bit) & 1
        A.append(row)
        b.append(int(ob.get("rhs", 0)) & 1)
    x = solve_affine(A, b)
    if x is None:
        return {
            "status": "UNSAT",
            "carrier": "SEALED_AFFINE_SYNDROME_QUOTIENT",
            "certificate": "INCONSISTENT_GF2_SYSTEM",
            "equation_rows": len(A),
        }
    witness = {v: int(x[i]) for i, v in enumerate(component)}
    if not all(affine_holds(ob, witness) for ob in obligations):
        raise AssertionError("AFFINE_WITNESS_REPLAY_FAILED")
    return {
        "status": "SAT",
        "carrier": "SEALED_AFFINE_SYNDROME_QUOTIENT",
        "witness": witness,
        "equation_rows": len(A),
        "local_state_bound": len(component) + len(A),
    }


def solve_instance(instance: dict) -> dict:
    L = int(instance["L"])
    B = sorted(set(int(v) for v in instance["B"]))
    obligations = list(instance["obligations"])
    components = canonical_components(B, obligations)
    portfolio: list[dict] = []
    global_witness: dict[int, int] = {}
    local_assignment_work = 0

    for comp in components:
        obs = component_obligations(comp, obligations)
        kinds = {ob.get("kind") for ob in obs}
        if not obs:
            local = {"status": "SAT", "carrier": "EMPTY_COMPONENT", "witness": {v: 0 for v in comp}}
        elif kinds == {"raw_table"}:
            local = solve_raw(comp, obs, L)
        elif kinds == {"affine_eq"}:
            local = solve_affine_component(comp, obs, L)
        else:
            local = {"status": "OPEN_UNSUPPORTED_LOCAL_CARRIER", "reason": "MIXED_OR_UNKNOWN_CONNECTED_COMPONENT"}
        local_assignment_work += int(local.get("local_assignments_examined", 0))
        rec = {"component": comp, "obligations": [ob.get("id") for ob in obs], **local}
        portfolio.append(rec)
        if local["status"].startswith("OPEN"):
            return {
                "status": local["status"],
                "reason": local.get("reason"),
                "components": components,
                "portfolio": portfolio,
                "metrics": {
                    "cartesian_products_materialized": 0,
                    "local_assignment_work": local_assignment_work,
                    "portfolio_records": len(portfolio),
                },
            }
        if local["status"] == "UNSAT":
            return {
                "status": "UNSAT",
                "unsat_component": comp,
                "components": components,
                "portfolio": portfolio,
                "metrics": {
                    "cartesian_products_materialized": 0,
                    "local_assignment_work": local_assignment_work,
                    "portfolio_records": len(portfolio),
                },
            }
        for v, bit in local.get("witness", {}).items():
            if v in global_witness and global_witness[v] != bit:
                raise AssertionError("DISJOINT_COMPONENT_WITNESS_CONFLICT")
            global_witness[v] = bit

    exact_replay = replay_obligations(obligations, global_witness)
    return {
        "status": "SAT" if exact_replay else "FAIL_REPLAY",
        "components": components,
        "portfolio": portfolio,
        "witness": global_witness,
        "exact_replay": exact_replay,
        "metrics": {
            "cartesian_products_materialized": 0,
            "local_assignment_work": local_assignment_work,
            "portfolio_records": len(portfolio),
            "stored_component_state_bound_sum": sum(int(r.get("local_state_bound", 0)) for r in portfolio),
        },
    }


def many_disconnected_control(t: int = 32) -> dict:
    return {
        "L": 1024,
        "B": list(range(t)),
        "obligations": [
            {"id": f"bit_{i}", "kind": "raw_table", "role": "transfer", "scope": [i], "allowed": ["0", "1"]}
            for i in range(t)
        ],
    }


def mixed_carrier_control() -> dict:
    obligations = [
        {"id": "raw_pair", "kind": "raw_table", "role": "transfer", "scope": [0, 1], "allowed": ["01"]},
        {"id": "a0", "kind": "affine_eq", "role": "transfer", "scope": list(range(2, 10)), "coeff": {str(v): 1 for v in range(2, 10)}, "rhs": 1},
        {"id": "a1", "kind": "affine_eq", "role": "transfer", "scope": list(range(8, 18)), "coeff": {str(v): 1 for v in range(8, 18)}, "rhs": 0},
        {"id": "a2", "kind": "affine_eq", "role": "reconstruction", "scope": [2, 5, 11, 15], "coeff": {"2": 1, "5": 1, "11": 1, "15": 1}, "rhs": 1},
    ]
    return {"L": 1024, "B": list(range(18)), "obligations": obligations}


def one_unsat_control() -> dict:
    return {
        "L": 128,
        "B": [0, 1],
        "obligations": [
            {"id": "sat_bit", "kind": "raw_table", "role": "transfer", "scope": [0], "allowed": ["0", "1"]},
            {"id": "u0", "kind": "raw_table", "role": "transfer", "scope": [1], "allowed": ["0"]},
            {"id": "u1", "kind": "raw_table", "role": "transfer", "scope": [1], "allowed": ["1"]},
        ],
    }


def cross_coupling_control(role: str = "transfer") -> dict:
    return {
        "L": 2,
        "B": [0, 1],
        "obligations": [
            {"id": "left", "kind": "raw_table", "role": "transfer", "scope": [0], "allowed": ["0", "1"]},
            {"id": "right", "kind": "raw_table", "role": "transfer", "scope": [1], "allowed": ["0", "1"]},
            {"id": "coupler", "kind": "unknown_exact", "role": role, "scope": [0, 1]},
        ],
    }


def unknown_wide_control() -> dict:
    return {
        "L": 64,
        "B": list(range(16)),
        "obligations": [
            {"id": "wide_unknown", "kind": "unknown_exact", "role": "transfer", "scope": list(range(16))}
        ],
    }


def main() -> None:
    root = repo_root()
    prereg = root / PREREG_REL
    data = json.loads(prereg.read_text(encoding="utf-8"))
    source_guard = (
        git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1
        and data.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
        and data.get("artifact_id") == "JANUS-TRUMP-FACTORIZED-FEEDBACK-INTERFACE-PORTFOLIO-PREREGISTRATION-2026-09-15-v1.0"
    )

    many = solve_instance(many_disconnected_control())
    mixed = solve_instance(mixed_carrier_control())
    unsat = solve_instance(one_unsat_control())
    cross = solve_instance(cross_coupling_control("transfer"))
    hidden = solve_instance(cross_coupling_control("reconstruction"))
    unknown = solve_instance(unknown_wide_control())

    checks = {
        "source_guard": source_guard,
        "many_disconnected_sat": many["status"] == "SAT",
        "many_components_preserved": len(many["components"]) == 32,
        "many_no_cartesian_materialization": many["metrics"]["cartesian_products_materialized"] == 0,
        "many_additive_portfolio": many["metrics"]["portfolio_records"] == 32,
        "mixed_sat": mixed["status"] == "SAT" and mixed.get("exact_replay") is True,
        "mixed_two_components": len(mixed["components"]) == 2,
        "mixed_two_sealed_carriers": sorted(r.get("carrier", "") for r in mixed["portfolio"]) == ["SEALED_AFFINE_SYNDROME_QUOTIENT", "SEALED_RAW_LOG_WIDTH_CONDITIONING"],
        "local_unsat_propagates": unsat["status"] == "UNSAT",
        "cross_coupling_merges_and_opens": cross["status"] == "OPEN_UNSUPPORTED_LOCAL_CARRIER" and len(cross["components"]) == 1,
        "hidden_reconstruction_coupling_detected": hidden["status"] == "OPEN_UNSUPPORTED_LOCAL_CARRIER" and len(hidden["components"]) == 1,
        "unknown_connected_wide_fails_closed": unknown["status"] == "OPEN_UNSUPPORTED_LOCAL_CARRIER",
    }
    verdict = "CANDIDATE_PASS_SCOPED_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO" if all(checks.values()) else "CANDIDATE_FAIL_OR_OPEN"
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "prereg_git_blob_sha1": PREREG_GIT_BLOB_SHA1,
        "checks": checks,
        "controls": {"many_disconnected": many, "mixed": mixed, "one_unsat": unsat, "cross_coupling": cross, "hidden_reconstruction": hidden, "unknown_wide": unknown},
        "complexity": {
            "dependency_components": "O(|B| + sum_a |scope(R_a)|) up to deterministic sorting overhead",
            "portfolio_storage": "O(sum_j encoded_size(Q_j) + |H_B|)",
            "portfolio_solve": "sum_j local polynomial lifecycle costs plus polynomial glue/replay",
            "cartesian_product_materialization": 0,
            "global_raw_2^B_enumeration": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_WIDE_INTERFACE_COMPRESSION": "NOT_PROVED_AND_FALSE_FOR_UNRESTRICTED_QUERY_CONTRACTS",
            "SCOPE": "EXACTLY_DISCONNECTED_FEEDBACK_DEPENDENCY_WITH_SEALED_LOCAL_CARRIERS_ONLY",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
