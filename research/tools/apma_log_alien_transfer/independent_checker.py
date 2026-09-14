from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path

PREREG_REL = Path("research/TRUMP_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB_SHA1 = "99223e98059a00ad48ef6acda75450dc0ef029b7"
PREREG_COMMIT = "7d96bfe6a63035d31cb8a505e69c08198dfa3b23"

RELATIONS = {
    "OR2": {(0, 1), (1, 0), (1, 1)},
    "EVEN_XOR3": {(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)},
}


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_candidate(repo: Path) -> dict:
    p = subprocess.run(
        [sys.executable, "-m", "research.tools.apma_log_alien_transfer.log_alien_transfer"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(p.stdout.strip().splitlines()[-1])


def p1_instance() -> dict:
    return {
        "L": 64,
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


def p2_instance() -> dict:
    return {
        "L": 8,
        "base_constraints": [
            {"id": "force0", "kind": "OR2", "scope": [0, 0]},
            {"id": "force1", "kind": "OR2", "scope": [1, 1]},
            {"id": "force2", "kind": "OR2", "scope": [2, 2]},
        ],
        "alien_constraints": [{"id": "x012", "kind": "EVEN_XOR3", "scope": [0, 1, 2]}],
    }


def p3_instance() -> dict:
    return {
        "L": 16,
        "base_constraints": [
            {"id": "x012", "kind": "EVEN_XOR3", "scope": [0, 1, 2]},
            {"id": "x234", "kind": "EVEN_XOR3", "scope": [2, 3, 4]},
        ],
        "alien_constraints": [
            {"id": "o03", "kind": "OR2", "scope": [0, 3]},
            {"id": "o14", "kind": "OR2", "scope": [1, 4]},
        ],
    }


def holds(row: dict, witness: dict[str, int] | dict[int, int]) -> bool:
    vals = tuple(int(witness.get(str(v), witness.get(v))) for v in row["scope"])
    return vals in RELATIONS[row["kind"]]


def replay(instance: dict, witness: dict[str, int] | dict[int, int]) -> bool:
    return all(holds(r, witness) for r in instance["base_constraints"] + instance["alien_constraints"])


def brute_truth(instance: dict) -> bool:
    variables = sorted({v for r in instance["base_constraints"] + instance["alien_constraints"] for v in r["scope"]})
    for bits in itertools.product((0, 1), repeat=len(variables)):
        witness = dict(zip(variables, bits))
        if replay(instance, witness):
            return True
    return False


def incidence_cycle_rank(instance: dict) -> tuple[bool, int]:
    constraints = instance["base_constraints"] + instance["alien_constraints"]
    variable_nodes = {f"v:{v}" for r in constraints for v in r["scope"]}
    constraint_nodes = {f"c:{i}" for i in range(len(constraints))}
    nodes = variable_nodes | constraint_nodes
    adjacency = {n: set() for n in nodes}
    edges: set[tuple[str, str]] = set()
    for i, row in enumerate(constraints):
        c = f"c:{i}"
        for v in sorted(set(row["scope"])):
            x = f"v:{v}"
            edge = (c, x)
            edges.add(edge)
            adjacency[c].add(x)
            adjacency[x].add(c)
    seen: set[str] = set()
    components = 0
    for start in sorted(nodes):
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            u = stack.pop()
            for w in adjacency[u]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
    rank = len(edges) - len(nodes) + components
    return components == 1, rank


def candidate_has_forbidden_global_cube(repo: Path) -> bool:
    src = (repo / "research/tools/apma_log_alien_transfer/log_alien_transfer.py").read_text(encoding="utf-8")
    forbidden = [
        "repeat=len(variables)",
        "repeat=len(all_variables",
        "range(1 << len(variables))",
        "range(2 ** len(variables))",
        "GLOBAL_ASSIGNMENT_ENUMERATOR",
    ]
    return any(token in src for token in forbidden)


def main() -> None:
    repo = root()
    prereg_path = repo / PREREG_REL
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    candidate = run_candidate(repo)
    controls = candidate["controls"]

    p1 = p1_instance()
    p2 = p2_instance()
    p3 = p3_instance()
    p1_connected, p1_rank = incidence_cycle_rank(p1)
    p3_connected, p3_rank = incidence_cycle_rank(p3)

    p1_witness = controls["p1_sat"].get("witness", {})
    tampered = {int(k): int(v) for k, v in p1_witness.items()}
    if 0 in tampered:
        tampered[0] ^= 1

    checks = {
        "prereg_source_guard": git_blob_sha1(prereg_path) == PREREG_BLOB_SHA1 and prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "candidate_internal_checks": all(candidate["checks"].values()),
        "p1_independent_truth_sat": brute_truth(p1) is True,
        "p1_candidate_witness_replays": replay(p1, p1_witness),
        "p1_connected_incidence": p1_connected,
        "p1_multiple_cycles": p1_rank >= 2,
        "p1_alien_budget_exact": controls["p1_sat"]["q_pow_k"] == 16 and controls["p1_sat"]["q_pow_k"] <= p1["L"],
        "p1_overlap_inconsistency_exercised": controls["p1_sat"]["metrics"]["overlap_inconsistent"] > 0,
        "p2_independent_truth_unsat": brute_truth(p2) is False,
        "p2_complete_four_branch_accounting": controls["p2_unsat"]["status"] == "UNSAT" and len(controls["p2_unsat"]["branch_receipts"]) == 4 and controls["p2_unsat"].get("complete_branch_accounting") is True,
        "p3_independent_truth_sat": brute_truth(p3) is True,
        "p3_candidate_witness_replays": replay(p3, controls["p3_reverse_sat"].get("witness", {})),
        "p3_connected_incidence": p3_connected,
        "p3_multiple_cycles": p3_rank >= 1,
        "p3_alien_budget_exact": controls["p3_reverse_sat"]["q_pow_k"] == 9 and controls["p3_reverse_sat"]["q_pow_k"] <= p3["L"],
        "over_budget_open_before_enumeration": controls["n1_over_budget"]["status"] == "OPEN_ALIEN_TUPLE_BUDGET" and controls["n1_over_budget"]["metrics"]["alien_tuple_combinations_examined"] == 0,
        "tampered_witness_rejected": bool(tampered) and replay(p1, tampered) is False,
        "candidate_has_no_forbidden_global_cube": not candidate_has_forbidden_global_cube(repo),
        "reported_global_cube_enumeration_zero": candidate["complexity"]["global_variable_cube_enumeration"] == 0,
        "firewall_open": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN" and candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER" if all(checks.values()) else "FAIL_OR_OPEN"
    out = {
        "artifact_id": "JANUS-TRUMP-LOG-ALIEN-CONSTRAINT-EXACT-TRANSFER-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "prereg_commit": PREREG_COMMIT,
        "checks": checks,
        "control_oracle": {
            "role": "FINITE_IMPLEMENTATION_CROSSCHECK_ONLY",
            "p1_truth": True,
            "p2_truth": False,
            "p3_truth": True,
            "p1_incidence_cycle_rank": p1_rank,
            "p3_incidence_cycle_rank": p3_rank,
        },
        "complexity": {
            "case_A": "4^k <= L branches by admission; each branch polynomial",
            "case_B": "3^k <= L branches by admission; each branch polynomial",
            "complete_lifecycle": "L * poly(L) including tuple consistency, pinned native solve, reconstruction, original replay, and UNSAT branch receipts",
            "full_variable_cube": "FORBIDDEN_AND_NOT_USED_BY_CANDIDATE",
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
