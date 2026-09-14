from pathlib import Path
import inspect, json, math, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_incidence_2core.incidence_2core import (
    canonical_two_core_variables,
    encoding_size,
)
from research.tools.apma_incidence_c_family_scaling.falsifier_family import (
    cycle_2cnf,
    fixed_c_counterexample,
)
from research.tools.apma_trinity_sovereign.trinity_v4 import run_trinity_v4


def independent_cycle(n):
    out = []
    for i in range(1, int(n) + 1):
        j = 1 if i == n else i + 1
        out.append((i, -j) if i % 2 else (-i, j))
    return tuple(out)


def measure(n):
    src = independent_cycle(n)
    return src, len(canonical_two_core_variables(src)), encoding_size(src, n)


def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    ns = [8, 16, 32, 64, 128, 256, 512]
    measured = []
    ratios = []
    for n in ns:
        src, k, L = measure(n)
        measured.append({"n": n, "k": k, "L": L})
        ratios.append(k / math.log2(L))
    checks["exact_cycle_structure_all_sizes"] = all(
        row["k"] == row["n"] and row["L"] == 4 * row["n"]
        for row in measured
    )
    checks["ratio_strictly_increases_on_frozen_scaling_sequence"] = all(
        ratios[i + 1] > ratios[i] for i in range(len(ratios) - 1)
    )
    examples["scaling"] = {
        "measurements": measured,
        "k_over_log2L": [round(x, 6) for x in ratios],
    }

    candidate_match = []
    for c in (1, 2, 3, 4, 7):
        cand = fixed_c_counterexample(c)
        candidate_match.append(cand["source"] == independent_cycle(cand["n"]))
    checks["candidate_family_matches_independent_construction"] = all(candidate_match)

    integer_counterexamples = []
    for C in range(1, 17):
        n = 16 * C * C
        src, k, L = measure(n)
        actual_fail = (1 << k) > (L ** C)
        algebraic_upper = 6 * C + 2 * C * C
        proof_chain = (
            math.log2(C) <= C
            and C * math.log2(L) <= algebraic_upper
            and algebraic_upper < k
        )
        integer_counterexamples.append({
            "C": C,
            "n": n,
            "k": k,
            "L": L,
            "actual_2powk_gt_LpowC": actual_fail,
            "proof_chain": proof_chain,
        })
    checks["integer_c_counterexamples_1_through_16"] = all(
        row["k"] == row["n"]
        and row["L"] == 4 * row["n"]
        and row["actual_2powk_gt_LpowC"]
        and row["proof_chain"]
        for row in integer_counterexamples
    )
    examples["integer_counterexamples"] = integer_counterexamples

    proof_grid = []
    for C in range(1, 129):
        proof_grid.append(
            math.log2(C) <= C
            and 6 * C + 2 * C * C < 16 * C * C
        )
    checks["symbolic_majorant_inequality_grid_1_through_128"] = all(proof_grid)

    real_cs = [0.5, 1.25, 2.5, 5.75, 11.1]
    real_counterexamples = []
    for c in real_cs:
        C = int(math.ceil(max(1.0, c)))
        n = 16 * C * C
        src, k, L = measure(n)
        real_counterexamples.append({
            "c": c,
            "C": C,
            "n": n,
            "k": k,
            "L": L,
            "2powk_gt_LpowC": (1 << k) > (L ** C),
            "majorant_relation": C >= c,
        })
    checks["representative_real_c_majorant_counterexamples"] = all(
        row["2powk_gt_LpowC"] and row["majorant_relation"]
        for row in real_counterexamples
    )
    examples["real_c_examples"] = real_counterexamples

    src64 = independent_cycle(64)
    tri = run_trinity_v4(src64, 64)
    checks["cycle_falsifier_does_not_claim_trinity_failure"] = (
        tri["sovereign"]["decision"] in {"COMMIT_SAT", "COMMIT_UNSAT"}
        and tri["sovereign"].get("door") != "INCIDENCE_2CORE_C2"
    )
    examples["trinity_v4_on_cycle64"] = {
        "decision": tri["sovereign"]["decision"],
        "door": tri["sovereign"].get("door"),
    }

    import research.tools.apma_incidence_c_family_scaling.falsifier_family as cand
    text = inspect.getsource(cand).lower()
    forbidden = [
        "random.", "dpll", "treewidth", "backdoor", "minimum_",
        "score_candidate", "best_cut", "assignment_cube", "sat_oracle",
    ]
    hits = [term for term in forbidden if term in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_FIXED_C_FAMILY_SCALING_FALSIFIER__NO_SINGLE_FIXED_C_CAN_MAKE_CANONICAL_FULL_2CORE_ENUMERATION_UNIVERSAL__TRINITY_NOT_FALSIFIED"
        if ok else
        "FAIL_APMA_FIXED_C_FAMILY_SCALING_FALSIFIER_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_INCIDENCE_2CORE_FIXED_C_FAMILY_SCALING_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "theorem_if_pass": "For the cycle 2-CNF family, canonical incidence 2-core width k=n and encoding size L=4n. For every fixed real c>0, choose C=ceil(max(1,c)) and n=16*C^2; then 2^k>L^C>=L^c. Therefore no single fixed c makes full canonical 2-core enumeration polynomially admissible for all CNF inputs.",
        "interpretation": "This falsifies universality of the fixed-c full-2core enumeration carrier family only. It does not falsify Trinity, because other exact doors can solve members of the family.",
        "not_proved": [
            "No lower bound on all possible APMA carriers.",
            "No impossibility result for quotienting or symbolic compression before branching.",
            "No universal Trinity completeness or incompleteness theorem.",
            "No SAT-in-P or P=NP claim."
        ],
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next_gate": "APMA_INCIDENCE_CORE_QUOTIENT_BEFORE_ENUMERATION_FALSIFIER_HUNT",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
