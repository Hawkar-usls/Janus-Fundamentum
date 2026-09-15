from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

ARTIFACT_ID = "JANUS-TRUMP-EXACT-INTERFACE-QUOTIENT-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG_REL = Path("research/TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_PREREGISTRATION_2026-09-15.json")
PREREG_GIT_BLOB_SHA1 = "43edbbb423fab4015f48410389ea41322ffde354"
PREREG_COMMIT = "eb4539f4cd8553cb5835b1ab1ffc9db31b3f1d25"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def gf2_rank(rows: Sequence[Sequence[int]], ncols: int | None = None) -> int:
    if not rows:
        return 0
    width = ncols if ncols is not None else len(rows[0])
    a = [[int(x) & 1 for x in row[:width]] for row in rows]
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for r in range(len(a)):
            if r != rank and a[r][col]:
                a[r] = [x ^ y for x, y in zip(a[r], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def xor_rows(coeffs: Sequence[int], rows: Sequence[Sequence[int]]) -> list[int]:
    if not rows:
        return []
    out = [0] * len(rows[0])
    for bit, row in zip(coeffs, rows):
        if bit & 1:
            out = [x ^ (int(y) & 1) for x, y in zip(out, row)]
    return out


def in_rowspace(v: Sequence[int], rows: Sequence[Sequence[int]]) -> bool:
    if not rows:
        return not any(v)
    n = len(rows[0])
    return gf2_rank(rows, n) == gf2_rank(list(rows) + [list(v)], n)


def syndrome(a: Sequence[Sequence[int]], x: Sequence[int]) -> list[int]:
    return [sum((u & 1) * (v & 1) for u, v in zip(row, x)) & 1 for row in a]


def solve_affine(a: Sequence[Sequence[int]], b: Sequence[int]) -> list[int] | None:
    if len(a) != len(b):
        raise ValueError("ROW_RHS_MISMATCH")
    if not a:
        return []
    m = len(a)
    n = len(a[0])
    aug = [[int(v) & 1 for v in row] + [int(rhs) & 1] for row, rhs in zip(a, b)]
    pivot_cols: list[int] = []
    rank = 0
    for col in range(n):
        pivot = next((r for r in range(rank, m) if aug[r][col]), None)
        if pivot is None:
            continue
        aug[rank], aug[pivot] = aug[pivot], aug[rank]
        for r in range(m):
            if r != rank and aug[r][col]:
                aug[r] = [x ^ y for x, y in zip(aug[r], aug[rank])]
        pivot_cols.append(col)
        rank += 1
        if rank == m:
            break
    for r in range(rank, m):
        if not any(aug[r][:n]) and aug[r][n]:
            return None
    x = [0] * n
    for row_idx, col in enumerate(pivot_cols):
        x[col] = aug[row_idx][n]
    return x


def make_affine_control() -> dict:
    k = 32
    L = 1024
    r = 5
    # Five disjoint parity blocks; bit 31 is intentionally outside the syndrome basis.
    groups = [
        [0, 5, 10, 15, 20, 25, 30],
        [1, 6, 11, 16, 21, 26],
        [2, 7, 12, 17, 22, 27],
        [3, 8, 13, 18, 23, 28],
        [4, 9, 14, 19, 24, 29],
    ]
    A: list[list[int]] = []
    for group in groups:
        row = [0] * k
        for j in group:
            row[j] = 1
        A.append(row)

    # Frozen downstream linear observations, each explicitly factored through A.
    lambdas = [
        [1, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1],
    ]
    queries = [xor_rows(c, A) for c in lambdas]
    rank = gf2_rank(A, k)
    adequacy = [in_rowspace(q, A) for q in queries]

    target = [1, 0, 1, 1, 0]
    witness = solve_affine(A, target)
    if witness is None:
        raise AssertionError("FULL_RANK_CONTROL_TARGET_MUST_BE_REACHABLE")
    witness_ok = syndrome(A, witness) == target

    # Negative control: exact downstream query reads the omitted raw bit 31.
    bad_query = [0] * k
    bad_query[31] = 1
    bad_in_rowspace = in_rowspace(bad_query, A)
    kernel_collision_left = [0] * k
    kernel_collision_right = [0] * k
    kernel_collision_right[31] = 1
    collision_same_syndrome = syndrome(A, kernel_collision_left) == syndrome(A, kernel_collision_right)
    collision_bad_query_differs = kernel_collision_left[31] != kernel_collision_right[31]

    log_budget = int(math.floor(math.log2(L)))
    quotient_size = 1 << rank
    return {
        "L": L,
        "B_size": k,
        "prior_log_budget": log_budget,
        "is_wide_relative_to_prior_door": k > log_budget,
        "A": A,
        "rank": rank,
        "syndrome_image_size": quotient_size,
        "raw_interface_size": 1 << k,
        "raw_assignments_enumerated_for_discovery": 0,
        "syndrome_states_to_scan": quotient_size,
        "polynomial_size_control": quotient_size <= L,
        "factor_coefficients": lambdas,
        "downstream_linear_queries": queries,
        "all_queries_in_rowspace": all(adequacy),
        "target_syndrome": target,
        "reconstructed_witness": witness,
        "witness_ok": witness_ok,
        "negative_omitted_bit_query": bad_query,
        "negative_bad_query_in_rowspace": bad_in_rowspace,
        "negative_collision_same_syndrome": collision_same_syndrome,
        "negative_collision_query_differs": collision_bad_query_differs,
        "negative_adequacy_rejected": (
            (not bad_in_rowspace) and collision_same_syndrome and collision_bad_query_differs
        ),
    }


def make_u1_symbolic_control(k: int = 24) -> dict:
    # The downstream contract is the k coordinate projections. Its transcript matrix is I_k.
    identity = [[1 if i == j else 0 for j in range(k)] for i in range(k)]
    rank = gf2_rank(identity, k)
    return {
        "B_size": k,
        "downstream_contract": "COORDINATE_PROJECTIONS_d_i(sigma)=sigma_i",
        "contract_description_size_queries": k,
        "transcript_rank": rank,
        "pairwise_separation_symbolic": rank == k,
        "minimum_exact_quotient_classes": 1 << rank,
        "raw_assignments_enumerated": 0,
        "proof_rule": "sigma!=tau => choose a differing coordinate i => d_i(sigma)!=d_i(tau)",
    }


def main() -> None:
    root = repo_root()
    prereg = root / PREREG_REL
    source_guard = git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1
    prereg_data = json.loads(prereg.read_text(encoding="utf-8"))
    source_guard = source_guard and prereg_data.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
    source_guard = source_guard and prereg_data.get("artifact_id") == "JANUS-TRUMP-EXACT-INTERFACE-QUOTIENT-BASIS-PREREGISTRATION-2026-09-15-v1.0"

    u1 = make_u1_symbolic_control()
    p1 = make_affine_control()
    checks = {
        "source_guard": source_guard,
        "u1_symbolic_pairwise_separation": u1["pairwise_separation_symbolic"],
        "u1_no_raw_enumeration": u1["raw_assignments_enumerated"] == 0,
        "p1_wide_interface": p1["is_wide_relative_to_prior_door"],
        "p1_polynomial_syndrome_image": p1["polynomial_size_control"],
        "p1_no_raw_enumeration_in_discovery": p1["raw_assignments_enumerated_for_discovery"] == 0,
        "p1_exact_query_factorization": p1["all_queries_in_rowspace"],
        "p1_exact_reconstruction": p1["witness_ok"],
        "negative_omitted_observable_rejected": p1["negative_adequacy_rejected"],
    }
    verdict = (
        "CANDIDATE_PASS_U1_AND_P1_SCOPED_SEPARATION"
        if all(checks.values())
        else "CANDIDATE_FAIL_OR_OPEN"
    )
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "prereg_git_blob_sha1": PREREG_GIT_BLOB_SHA1,
        "checks": checks,
        "u1": u1,
        "p1_affine_syndrome": p1,
        "complexity": {
            "u1_checker": "O(k^3) rank/identity-contract verification; theorem proof is symbolic pairwise separation",
            "p1_discovery_and_adequacy": "polynomial GF(2) rank/rowspace/Gaussian-elimination operations",
            "p1_quotient_scan": "2^rho syndrome states, admitted only when 2^rho <= poly(L)",
            "raw_2^B_enumeration": "FORBIDDEN_AND_NOT_USED",
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_WIDE_INTERFACE_COMPRESSION": "REFUTED_ONLY_FOR_UNRESTRICTED_QUERY_CONTRACT_AS_UNIVERSAL_PROMISE",
            "AFFINE_SYNDROME_TRANSFER": "CANDIDATE_SCOPED_ONLY_PENDING_INDEPENDENT_CHECK",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
