from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PREREG_COMMIT = "8235a16f956f388eb79c0f15961e22db7c088558"
PREREG_REL = "research/TRUMP_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO_PREREGISTRATION_2026-09-15.json"
PREREG_GIT_BLOB_SHA1 = "7410a1169e4c117ccdab929c13ff4b0312edef1c"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    import hashlib

    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_candidate(root: Path) -> dict:
    p = subprocess.run(
        [sys.executable, "-m", "research.tools.apma_factorized_feedback.factorized_portfolio"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(p.stdout.strip().splitlines()[-1])


def holds_raw(ob: dict, witness: dict[str, int] | dict[int, int]) -> bool:
    scope = [int(v) for v in ob["scope"]]
    word = "".join(str(int(witness.get(str(v), witness.get(v)))) for v in scope)
    return word in set(ob.get("allowed", []))


def holds_affine(ob: dict, witness: dict[str, int] | dict[int, int]) -> bool:
    total = 0
    for k, bit in ob.get("coeff", {}).items():
        if int(bit) & 1:
            total ^= int(witness.get(str(int(k)), witness.get(int(k))))
    return total == (int(ob.get("rhs", 0)) & 1)


def replay(control: dict, obligations: list[dict]) -> bool:
    witness = control.get("witness", {})
    if control.get("status") != "SAT":
        return False
    for ob in obligations:
        if ob["kind"] == "raw_table" and not holds_raw(ob, witness):
            return False
        if ob["kind"] == "affine_eq" and not holds_affine(ob, witness):
            return False
    return True


def mixed_obligations() -> list[dict]:
    return [
        {"id": "raw_pair", "kind": "raw_table", "role": "transfer", "scope": [0, 1], "allowed": ["01"]},
        {"id": "a0", "kind": "affine_eq", "role": "transfer", "scope": list(range(2, 10)), "coeff": {str(v): 1 for v in range(2, 10)}, "rhs": 1},
        {"id": "a1", "kind": "affine_eq", "role": "transfer", "scope": list(range(8, 18)), "coeff": {str(v): 1 for v in range(8, 18)}, "rhs": 0},
        {"id": "a2", "kind": "affine_eq", "role": "reconstruction", "scope": [2, 5, 11, 15], "coeff": {"2": 1, "5": 1, "11": 1, "15": 1}, "rhs": 1},
    ]


def source_has_forbidden_product_enumerator(root: Path) -> bool:
    src = (root / "research/tools/apma_factorized_feedback/factorized_portfolio.py").read_text(encoding="utf-8")
    forbidden = ["itertools.product", "from itertools import product", "cartesian_state_tuples", "global_assignment_product"]
    return any(x in src for x in forbidden)


def main() -> None:
    root = repo_root()
    prereg_path = root / PREREG_REL
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    candidate = run_candidate(root)
    controls = candidate["controls"]

    prereg_guard = (
        git_blob_sha1(prereg_path) == PREREG_GIT_BLOB_SHA1
        and prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
        and prereg.get("artifact_id") == "JANUS-TRUMP-FACTORIZED-FEEDBACK-INTERFACE-PORTFOLIO-PREREGISTRATION-2026-09-15-v1.0"
    )

    many = controls["many_disconnected"]
    mixed = controls["mixed"]
    unsat = controls["one_unsat"]
    cross = controls["cross_coupling"]
    hidden = controls["hidden_reconstruction"]
    unknown = controls["unknown_wide"]

    many_components_disjoint = (
        len(many["components"]) == 32
        and sorted(v for c in many["components"] for v in c) == list(range(32))
        and len({v for c in many["components"] for v in c}) == 32
    )
    many_all_local = all(len(c) == 1 for c in many["components"])
    many_no_product = many["metrics"]["cartesian_products_materialized"] == 0
    many_additive = many["metrics"]["portfolio_records"] == 32 and many["metrics"]["stored_component_state_bound_sum"] <= 64

    mixed_replay = replay(mixed, mixed_obligations())
    mixed_component_partition = sorted(mixed["components"]) == [[0, 1], list(range(2, 18))]
    mixed_carriers = sorted(r.get("carrier", "") for r in mixed["portfolio"]) == [
        "SEALED_AFFINE_SYNDROME_QUOTIENT",
        "SEALED_RAW_LOG_WIDTH_CONDITIONING",
    ]

    unsat_exact = unsat["status"] == "UNSAT" and unsat.get("unsat_component") == [1]
    cross_merged = cross["status"] == "OPEN_UNSUPPORTED_LOCAL_CARRIER" and cross["components"] == [[0, 1]]
    hidden_merged = hidden["status"] == "OPEN_UNSUPPORTED_LOCAL_CARRIER" and hidden["components"] == [[0, 1]]
    unknown_fail_closed = unknown["status"] == "OPEN_UNSUPPORTED_LOCAL_CARRIER" and unknown["components"] == [list(range(16))]

    checks = {
        "prereg_source_guard": prereg_guard,
        "candidate_internal_checks": all(candidate["checks"].values()),
        "many_components_disjoint": many_components_disjoint,
        "many_all_local": many_all_local,
        "many_no_product": many_no_product,
        "many_additive_storage": many_additive,
        "mixed_exact_replay": mixed_replay,
        "mixed_component_partition": mixed_component_partition,
        "mixed_sealed_carriers": mixed_carriers,
        "one_local_unsat_certifies_global": unsat_exact,
        "transfer_cross_coupling_merges": cross_merged,
        "reconstruction_cross_coupling_merges": hidden_merged,
        "unknown_connected_wide_fails_closed": unknown_fail_closed,
        "candidate_source_has_no_cross_product_enumerator": not source_has_forbidden_product_enumerator(root),
        "reported_cartesian_materialization_zero": candidate["complexity"]["cartesian_product_materialization"] == 0,
        "reported_global_raw_enumeration_zero": candidate["complexity"]["global_raw_2^B_enumeration"] == 0,
    }

    verdict = "PASS_SCOPED_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO" if all(checks.values()) else "FAIL_OR_OPEN"
    out = {
        "artifact_id": "JANUS-TRUMP-FACTORIZED-FEEDBACK-INTERFACE-PORTFOLIO-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "prereg_commit": PREREG_COMMIT,
        "checks": checks,
        "complexity": {
            "dependency_graph_and_components": "polynomial in explicit scope incidence size",
            "portfolio_size": "additive sum of sealed local carrier sizes; no product materialization",
            "local_raw_search": "allowed only when each raw component width <= floor(log2 L), hence <= L states per such component",
            "affine_local_carrier": "polynomial GF(2) elimination inherited from sealed affine-syndrome quotient",
            "global_cartesian_products_materialized": 0,
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
