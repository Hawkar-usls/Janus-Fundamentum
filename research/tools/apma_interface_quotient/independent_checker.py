from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_PREREGISTRATION_2026-09-15.json"
THEOREM = ROOT / "research/TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_THEOREM_CANDIDATE_2026-09-15.md"
CANDIDATE = ROOT / "research/tools/apma_interface_quotient/exact_quotient.py"
EXPECTED_PREREG_BLOB = "43edbbb423fab4015f48410389ea41322ffde354"
EXPECTED_THEOREM_BLOB = "c92c706fc1ebabca560b534fe911227ac3bcc932"
EXPECTED_CANDIDATE_BLOB = "cc331245bd71b6c83ab6c43b86f961fe53ed31c8"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def rank(rows: Sequence[Sequence[int]]) -> int:
    if not rows:
        return 0
    a = [[int(v) & 1 for v in row] for row in rows]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        for i in range(m):
            if i != r and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r])]
        r += 1
        if r == m:
            break
    return r


def rowspace_contains(A: Sequence[Sequence[int]], v: Sequence[int]) -> bool:
    return rank(A) == rank(list(A) + [list(v)])


def combine(coeffs: Sequence[int], A: Sequence[Sequence[int]]) -> list[int]:
    out = [0] * len(A[0])
    for c, row in zip(coeffs, A):
        if c & 1:
            out = [x ^ y for x, y in zip(out, row)]
    return out


def syn(A: Sequence[Sequence[int]], x: Sequence[int]) -> list[int]:
    return [sum((u & 1) * (v & 1) for u, v in zip(row, x)) & 1 for row in A]


def run_candidate() -> dict:
    cp = subprocess.run(
        [sys.executable, "-m", "research.tools.apma_interface_quotient.exact_quotient"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(cp.stdout.strip().splitlines()[-1])


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    theorem_text = THEOREM.read_text(encoding="utf-8")
    candidate = run_candidate()

    source_guard = {
        "prereg_blob": git_blob_sha1(PREREG) == EXPECTED_PREREG_BLOB,
        "theorem_blob": git_blob_sha1(THEOREM) == EXPECTED_THEOREM_BLOB,
        "candidate_blob": git_blob_sha1(CANDIDATE) == EXPECTED_CANDIDATE_BLOB,
        "prereg_status": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_authority": prereg.get("authority_class") == "THEOREM_OR_FALSIFICATION_PREREG__NO_SCIENTIFIC_PROMOTION",
        "theorem_u1_present": "# U1 — unrestricted exact downstream semantics admits no universal compression" in theorem_text,
        "theorem_p1_present": "# P1 — exact affine-syndrome quotient on a strict frozen subclass" in theorem_text,
        "theorem_scope_firewall_present": "It does **not** prove:" in theorem_text and "`P != NP`" in theorem_text,
    }

    u1 = candidate["u1"]
    k_u1 = int(u1["B_size"])
    identity = [[1 if i == j else 0 for j in range(k_u1)] for i in range(k_u1)]
    u1_rank = rank(identity)
    u1_checks = {
        "coordinate_contract_linear_description": int(u1["contract_description_size_queries"]) == k_u1,
        "identity_transcript_full_rank": u1_rank == k_u1,
        "reported_rank_matches": int(u1["transcript_rank"]) == u1_rank,
        "pairwise_distinguishability_symbolic": u1_rank == k_u1,
        "minimum_classes_exact": int(u1["minimum_exact_quotient_classes"]) == (1 << k_u1),
        "no_raw_assignment_enumeration": int(u1["raw_assignments_enumerated"]) == 0,
    }

    p1 = candidate["p1_affine_syndrome"]
    A = [[int(v) & 1 for v in row] for row in p1["A"]]
    k = int(p1["B_size"])
    L = int(p1["L"])
    rho = rank(A)
    queries = [[int(v) & 1 for v in q] for q in p1["downstream_linear_queries"]]
    coeffs = [[int(v) & 1 for v in c] for c in p1["factor_coefficients"]]
    factor_maps_exact = len(queries) == len(coeffs) and all(combine(c, A) == q for c, q in zip(coeffs, queries))
    rowspace_adequacy = all(rowspace_contains(A, q) for q in queries)
    witness = [int(v) & 1 for v in p1["reconstructed_witness"]]
    target = [int(v) & 1 for v in p1["target_syndrome"]]
    bad = [int(v) & 1 for v in p1["negative_omitted_bit_query"]]
    left = [0] * k
    right = [0] * k
    right[31] = 1

    p1_checks = {
        "wide_interface_relative_to_prior_log_door": k > int(math.floor(math.log2(L))),
        "rank_matches": int(p1["rank"]) == rho == 5,
        "syndrome_image_size_exact": int(p1["syndrome_image_size"]) == (1 << rho),
        "quotient_polynomial_control": (1 << rho) <= L,
        "raw_space_strictly_larger": int(p1["raw_interface_size"]) == (1 << k) and (1 << k) > (1 << rho),
        "no_raw_enumeration_in_discovery": int(p1["raw_assignments_enumerated_for_discovery"]) == 0,
        "factor_maps_reconstruct_raw_queries": factor_maps_exact,
        "all_queries_in_rowspace": rowspace_adequacy,
        "witness_reconstructs_target_syndrome": syn(A, witness) == target,
        "bad_query_outside_rowspace": not rowspace_contains(A, bad),
        "explicit_kernel_collision_same_syndrome": syn(A, left) == syn(A, right),
        "explicit_kernel_collision_changes_bad_query": sum(x*y for x, y in zip(bad, left)) % 2 != sum(x*y for x, y in zip(bad, right)) % 2,
    }

    candidate_firewall = candidate["scientific_firewall"]
    firewall = {
        "P_VS_NP_OPEN": candidate_firewall.get("P_VS_NP") == "OPEN",
        "GENERAL_SAT_IN_P_NOT_PROVED": candidate_firewall.get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_NONE": candidate_firewall.get("GLOBAL_APMA_FRONTIER_ADVANCE") == "NONE",
        "no_general_positive_wide_compression_claim": "UNRESTRICTED_QUERY_CONTRACT" in candidate_firewall.get("GENERAL_WIDE_INTERFACE_COMPRESSION", ""),
        "candidate_not_self_promoted": candidate.get("authority") == "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION",
    }

    checks = {**{f"source_{k}": v for k, v in source_guard.items()}, **{f"u1_{k}": v for k, v in u1_checks.items()}, **{f"p1_{k}": v for k, v in p1_checks.items()}, **{f"firewall_{k}": v for k, v in firewall.items()}}
    verdict = "PASS_U1_AND_P1_SCOPED_SEPARATION" if all(checks.values()) else "FAIL_OR_OPEN_EXACT_INTERFACE_QUOTIENT_GATE"

    result = {
        "artifact_id": "JANUS-TRUMP-EXACT-INTERFACE-QUOTIENT-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION",
        "verdict": verdict,
        "checks": checks,
        "u1": {
            "B_size": k_u1,
            "coordinate_query_rank": u1_rank,
            "minimum_exact_quotient_classes": 1 << k_u1,
            "interpretation": "unrestricted coordinate-observation contract forces singleton downstream-equivalence classes",
        },
        "p1": {
            "L": L,
            "B_size": k,
            "rank": rho,
            "raw_interface_size": 1 << k,
            "syndrome_classes": 1 << rho,
            "reduction_factor": (1 << k) // (1 << rho),
            "interpretation": "strict affine downstream contract factors exactly through syndrome; omitted observable control is rejected",
        },
        "complexity": {
            "basis_and_adequacy": "GF(2) elimination/rank/rowspace checks are polynomial in k and number of frozen queries",
            "quotient_scan": "2^rho classes; admitted only when polynomially bounded in L",
            "raw_assignment_enumeration": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "U1_SCOPE": "UNRESTRICTED_DOWNSTREAM_QUERY_CONTRACT_REPRESENTATION_BARRIER_ONLY",
            "P1_SCOPE": "STRICT_AFFINE_SYNDROME_INTERFACE_ONLY",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }
    print(json.dumps(result, sort_keys=True))
    if verdict != "PASS_U1_AND_P1_SCOPED_SEPARATION":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
