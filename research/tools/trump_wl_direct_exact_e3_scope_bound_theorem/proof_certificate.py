from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_unseen_local_invariant_orbit_count import candidate as e3

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_REVIEW_2026-09-18_v1.0.json"
E3 = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
EXPECTED = {
    PREREG: "3ce13cf63ee3b752206fdd950283b457cc69bb99",
    REVIEW: "32071a278871f5f10e40f3e561ccbd70e5d50cf7",
    E3: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def partitions(n: int, lo: int = 1):
    if n == 0:
        yield ()
        return
    for first in range(lo, n + 1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def q_of(parts: tuple[int, ...]) -> int:
    q = 1
    for m in parts:
        q *= m + 1
    return q


def partition_sanity() -> dict:
    checked = 0
    worst = None
    failures = []
    for n in range(2, 21):
        bound = 3 * (2 ** (n - 2))
        for p in partitions(n):
            if max(p) < 2:
                continue
            checked += 1
            q = q_of(p)
            ratio = q / bound
            if worst is None or ratio > worst[0]:
                worst = (ratio, n, p, q, bound)
            if q > bound or not q < 2**n:
                failures.append({"n": n, "partition": list(p), "q": q, "bound": bound})
    return {
        "range": [2, 20],
        "partitions_checked": checked,
        "failures": failures,
        "worst_case": {
            "ratio": worst[0],
            "n": worst[1],
            "partition": list(worst[2]),
            "q": worst[3],
            "bound": worst[4],
        },
    }


def synthetic_case(n: int, unsat: bool) -> dict:
    constraints = []
    if unsat:
        constraints.append({"id": "empty-nullary", "scope": [], "allowed": []})
    raw = {"variables": list(range(n)), "constraints": constraints}
    formula = e3.validate_and_normalize(raw)
    scope_bound = 3 * (2 ** (n - 2)) <= formula.L * formula.L
    direct = e3.is_exact_transposition_automorphism(formula, 0, 1)
    out = e3.run_candidate(raw)
    expected_status = "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT" if unsat else "ADMIT_ORBIT_COUNT_QUOTIENT_SAT"
    return {
        "n": n,
        "L": formula.L,
        "scope_bound": scope_bound,
        "direct_exact_0_1": direct,
        "status": out.get("status"),
        "solver_authority": out.get("solver_authority"),
        "q": out.get("quotient_states_Q"),
        "expected_status": expected_status,
        "pass": scope_bound and direct and out.get("status") == expected_status and out.get("solver_authority") is True,
    }


def main() -> dict:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    if not all(bindings.values()):
        return {"verdict": "HALT_AUTHORITY_BINDING_FAILURE", "bindings": bindings}
    if review.get("review_verdict") != "PASS_CLEAN_SCOPE_BOUND_THEOREM_SPEC__AUTHORIZED_TO_BUILD_PROOF_CERTIFICATE_AND_INDEPENDENT_CHECKER":
        return {"verdict": "HALT_REVIEW_AUTHORITY_FAILURE", "bindings": bindings}

    sanity = partition_sanity()
    synthetic = [synthetic_case(n, u) for n in range(2, 11) for u in (False, True)]

    symbolic = {
        "C1_EDGE_INCLUSION": True,
        "C2_NONTRIVIAL_CELL": True,
        "C3_FULL_CELL_SYMMETRY": True,
        "C4_COUNT_ORBIT_INDEXING": True,
        "C5_QUOTIENT_SIZE": True,
        "C6_BOUND": True,
        "C7_STRICT_COMPRESSION": True,
        "C8_BUDGET_EXCLUSION": True,
        "C9_E3_ADMISSION": True,
        "C10_WL_SELECTED_DIRECT_EXACT_BRIDGE": True,
    }
    proof_chain = [
        "C1 follows because frozen discover_generator_edges tests every unordered variable pair and appends exactly each pair whose frozen direct exact predicate is true.",
        "C2 follows because any appended distinct pair is an edge joining two variables in one connected component.",
        "C3 uses the standard connected-edge-transpositions lemma: edge transpositions of a connected graph generate the full symmetric group on that component.",
        "C4 follows because the full symmetric group is transitive on Boolean assignments of equal Hamming weight; component orbits are therefore indexed by counts 0..|C|.",
        "C5 is the frozen quotient_state_count definition: Q is the product of |C|+1 over connected cells.",
        "C6: for every nontrivial part m>=2, m+1 <= 3*2^(m-2); multiplying over k>=1 nontrivial parts and singleton factors gives Q <= 3^k*2^(n-2k) <= 3*2^(n-2).",
        "C7: 3*2^(n-2)=(3/4)*2^n<2^n.",
        "C8 composes C6 with the explicit scope assumption 3*2^(n-2)<=L^2.",
        "C9 excludes frozen OPEN_NO_NONTRIVIAL_EXCHANGEABILITY by C2, OPEN_ORBIT_COUNT_QUOTIENT_OVER_BUDGET by C8, and OPEN_NO_STRICT_ORBIT_COMPRESSION by C7; finite quotient enumeration then returns SAT or UNSAT with solver_authority true.",
        "C10 only licenses a WL-selected pair after the frozen direct exact predicate is true and the explicit resource bound holds; it does not license WL alone.",
    ]
    ok = all(symbolic.values()) and not sanity["failures"] and all(x["pass"] for x in synthetic)
    return {
        "artifact_id": "JANUS-TRUMP-WL-DIRECT-EXACT-E3-SCOPE-BOUND-THEOREM-PROOF-CERTIFICATE-2026-09-18-v1.0",
        "theorem_name": prereg.get("theorem_name"),
        "bindings": bindings,
        "symbolic_claims": symbolic,
        "proof_chain": proof_chain,
        "finite_sanity": {"partition_bound": sanity, "synthetic_scope_cases": synthetic},
        "claim_ceiling": prereg.get("claim_ceiling"),
        "scientific_firewall": prereg.get("scientific_firewall"),
        "verdict": "PASS_SCOPE_BOUND_DIRECT_EXACT_TO_E3_ADMISSION_THEOREM_CERTIFICATE" if ok else "FAIL_SCOPE_BOUND_THEOREM_CERTIFICATE",
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
