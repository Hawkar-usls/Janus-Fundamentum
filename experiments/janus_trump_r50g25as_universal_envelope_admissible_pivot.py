from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25aj_signed_incidence_reachability_closure as aj
import janus_trump_r50g25ar_global_phase_root_state_size_envelope as ar

GATE = "JANUS_TRUMP_R50G25AS_UNIVERSAL_ENVELOPE_ADMISSIBLE_PIVOT_EXISTENCE_OR_REACHABLE_COUNTEREXAMPLE"
PREREG_COMMIT = "65870dc5f7942fb3876bc3760eaa3cfaa70f44ee"
PARENT_AR_RECEIPT_COMMIT = "a841fcc073b559a8bff7f72fbc80288e1f064f9d"
PARENT_AR_SEALED_HEAD = "5254dd6100e79e25850c3406c0822ea4d5ccecd8"

CERT_OBSTRUCTION = "REACHABLE_CERTIFICATE_ONLY_DP_DOOR_OBSTRUCTION_FOUND"
ACTUAL_OBSTRUCTION = "REACHABLE_ACTUAL_DP_SIZE_OBSTRUCTION_FOUND"
SURVIVAL = "NO_FROZEN_COUNTEREXAMPLE_FOUND__UNIVERSAL_EXISTENCE_REMAINS_OPEN"
FAILURE = "IMPLEMENTATION_OR_CONTRACT_FAILURE"


def canonical(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return tuple(map(int, r33.measure(canonical(formula))))


def formula_hash(formula):
    return y.canonical_hash(canonical(formula))


def clause_falsified_by_assignment(vars4, bits):
    # Clause containing +v for assigned False and -v for assigned True.
    return tuple(v if bit == 0 else -v for v, bit in zip(vars4, bits))


def encode_xor_zero(vars4):
    out = []
    for bits in itertools.product((0, 1), repeat=4):
        if sum(bits) % 2 == 1:
            out.append(clause_falsified_by_assignment(vars4, bits))
    assert len(out) == 8
    return out


def zero_sum_quads(n):
    assert n > 0 and (n & (n - 1)) == 0
    quads = set()
    for a, b, c in itertools.combinations(range(n), 3):
        d = a ^ b ^ c
        if d < 0 or d >= n or d in (a, b, c):
            continue
        q = tuple(sorted((a, b, c, d)))
        if len(set(q)) == 4:
            quads.add(q)
    return sorted(quads)


def hamming_xor_formula(n, punctured):
    clauses = []
    quads = zero_sum_quads(n)
    for q in quads:
        vars4 = tuple(i + 1 for i in q)
        clauses.extend(encode_xor_zero(vars4))
    if punctured:
        # Excludes the all-zero codeword; all-one remains an explicit SAT witness.
        clauses.append(tuple(range(1, n + 1)))
    f = canonical(clauses)
    return f, {
        "family": "PUNCTURED_EXTENDED_HAMMING_WEIGHT4_XOR_CNF" if punctured else "UNPUNCTURED_AFFINE_CONTROL",
        "n": n,
        "zero_sum_quad_count": len(quads),
        "punctured": punctured,
        "known_all_one_model": all(any((lit > 0) for lit in c) for c in f),
    }


def all_unique_3clauses(n):
    out = []
    for tri in itertools.combinations(range(1, n + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append(tuple(sign * v for sign, v in zip(signs, tri)))
    return out


def seeded_balanced_unique_3cnf(n, seed, scale):
    pool = all_unique_3clauses(n)
    rng = random.Random(seed)
    rng.shuffle(pool)
    target = min(len(pool), int(math.ceil(scale * (n ** (7.0 / 3.0)))))
    f = canonical(pool[:target])
    return f, {
        "family": "SEEDED_BALANCED_UNIQUE_3CNF",
        "n": n,
        "seed": seed,
        "scale": scale,
        "target_clause_count": target,
    }


def complement_pair_3hypergraph(n):
    target = int(math.ceil(1.5 * (n ** (7.0 / 3.0))))
    clauses = []
    for tri in itertools.combinations(range(1, n + 1), 3):
        clauses.append(tuple(tri))
        clauses.append(tuple(-v for v in tri))
        if len(clauses) >= target:
            break
    f = canonical(clauses)
    return f, {
        "family": "COMPLEMENT_PAIR_3_HYPERGRAPH",
        "n": n,
        "target_clause_count": target,
    }


def frozen_candidates():
    # Literal preregistered order.
    for n in (8, 16):
        yield hamming_xor_formula(n, punctured=True)
    for n in (8, 16):
        yield hamming_xor_formula(n, punctured=False)
    for n in (8, 10, 12):
        for seed in (65001, 65002, 65003):
            for scale in (1.0, 1.5):
                yield seeded_balanced_unique_3cnf(n, seed, scale)
    for n in (8, 10, 12):
        yield complement_pair_3hypergraph(n)


def local_pivot_rows(core, B0):
    rows = []
    C, L, V = clv(core)
    if V <= 1:
        return rows
    for var in r33.variables(core):
        rec = aj.local_signed_incidence_bound(core, B0, int(var))
        if rec is not None:
            rows.append(rec)
    rows.sort(key=lambda q: (int(q["RAW_S_UB"]), int(q["var"])))
    return rows


def exact_dp_rows(core, pivot_rows):
    exact_rows = []
    failures = []
    for p in pivot_rows:
        var = int(p["var"])
        exact = y.exact_dp_record(core, var)
        if exact is None or not exact.get("replay_pass"):
            failures.append({"kind": "EXACT_DP_REPLAY_FAILURE", "var": var})
            continue
        S1 = int(exact["CLV_after"][0] + exact["CLV_after"][1])
        ub = int(p["RAW_S_UB"])
        if S1 > ub:
            failures.append({
                "kind": "LOCAL_BOUND_UNSOUND",
                "var": var,
                "exact_S_after": S1,
                "RAW_S_UB": ub,
            })
        exact_rows.append({
            "var": var,
            "T": int(p["T"]),
            "RAW_S_UB": ub,
            "certificate_admissible": bool(p["envelope_admissible"]),
            "exact_CLV_after": list(map(int, exact["CLV_after"])),
            "exact_S_after": S1,
            "exact_size_admissible": bool(S1 <= int(p["T"])),
            "relation": str(exact["relation"]),
            "pair_checks": int(exact["pair_checks"]),
        })
    return exact_rows, failures


def compact_route(w):
    route = w.get("route", [])
    return {
        "route_length": len(route),
        "route_head": route[:3],
        "route_tail": route[-5:] if len(route) > 5 else route,
    }


def audit_candidate(formula, meta, chain):
    root = canonical(formula)
    root_CLV = clv(root)
    root_const = ar.root_constants(root)
    expected_B0 = (root_CLV[0] + root_CLV[1]) * ((root_CLV[2] + 1) ** 2)
    failures = []
    if int(root_const["B0"]) != int(expected_B0):
        failures.append({"kind": "ROOT_BUDGET_DRIFT", "root_constants": root_const, "expected_B0": expected_B0})

    w = y.policy_replay(root, chain)
    row = {
        "meta": meta,
        "root_hash": formula_hash(root),
        "root_CLV": list(root_CLV),
        "B0": int(root_const["B0"]),
        "policy_kind": str(w.get("kind")),
        "policy_state_CLV": list(clv(w["state"])),
        "policy_state_hash": formula_hash(w["state"]),
        **compact_route(w),
        "failure_count": 0,
        "failures": [],
    }

    if w.get("kind") in {"TERMINAL", "AFFINE"}:
        row["classification"] = "NON_FALSIFYING_CHEAP_POLICY_EXIT"
        row["failure_count"] = len(failures)
        row["failures"] = failures
        return row, None, failures

    if w.get("kind") != "RESIDUAL":
        failures.append({"kind": "POLICY_CONTRACT_DRIFT", "observed_kind": w.get("kind")})
        row["classification"] = "IMPLEMENTATION_OR_CONTRACT_FAILURE"
        row["failure_count"] = len(failures)
        row["failures"] = failures
        return row, None, failures

    core = canonical(w["state"])
    C, L, V = clv(core)
    pivots = local_pivot_rows(core, root_const["B0"])
    admitted = [p for p in pivots if p["envelope_admissible"]]
    row.update({
        "residual_CLV": [C, L, V],
        "residual_hash": formula_hash(core),
        "bipolar_pivot_count": len(pivots),
        "certificate_admissible_pivot_count": len(admitted),
        "minimum_local_bound": pivots[0] if pivots else None,
    })

    if admitted:
        chosen = admitted[0]
        exact = y.exact_dp_record(core, int(chosen["var"]))
        if exact is None or not exact.get("replay_pass"):
            failures.append({"kind": "EXACT_DP_REPLAY_FAILURE", "var": int(chosen["var"])})
        else:
            S1 = int(exact["CLV_after"][0] + exact["CLV_after"][1])
            if S1 > int(chosen["RAW_S_UB"]):
                failures.append({"kind": "LOCAL_BOUND_UNSOUND", "var": int(chosen["var"]), "exact_S_after": S1, "RAW_S_UB": int(chosen["RAW_S_UB"])})
            row["minimum_admitted_exact_check"] = {
                "var": int(chosen["var"]),
                "T": int(chosen["T"]),
                "RAW_S_UB": int(chosen["RAW_S_UB"]),
                "exact_CLV_after": list(map(int, exact["CLV_after"])),
                "exact_S_after": S1,
            }
        row["classification"] = "RELEVANT_RESIDUAL_WITH_CERTIFICATE_ADMISSIBLE_PIVOT"
        row["failure_count"] = len(failures)
        row["failures"] = failures
        return row, None, failures

    # This is the preregistered first-falsifier boundary. Independently inspect exact DP.
    exact_rows, exact_failures = exact_dp_rows(core, pivots)
    failures.extend(exact_failures)
    exact_admitted = [e for e in exact_rows if e["exact_size_admissible"]]
    obstruction_class = "CERTIFICATE_ONLY_ROUTE_OBSTRUCTION" if exact_admitted else "ACTUAL_DP_SIZE_ROUTE_OBSTRUCTION"
    witness = {
        "class": "RELEVANT_RESIDUAL_WITH_NO_CERTIFICATE_ADMISSIBLE_PIVOT",
        "obstruction_class": obstruction_class,
        "meta": meta,
        "root_hash": formula_hash(root),
        "root_CLV": list(root_CLV),
        "B0": int(root_const["B0"]),
        "residual_hash": formula_hash(core),
        "residual_CLV": [C, L, V],
        "formula": [list(c) for c in core],
        "bipolar_pivot_count": len(pivots),
        "certificate_admissible_pivot_count": 0,
        "minimum_local_bound": pivots[0] if pivots else None,
        "exact_size_admissible_pivot_count": len(exact_admitted),
        "minimum_exact_size_admissible": min(exact_admitted, key=lambda e: (e["exact_S_after"], e["var"])) if exact_admitted else None,
        "exact_pivots": exact_rows,
        "policy_route_summary": compact_route(w),
    }
    row["classification"] = obstruction_class
    row["exact_size_admissible_pivot_count"] = len(exact_admitted)
    row["failure_count"] = len(failures)
    row["failures"] = failures
    return row, witness, failures


def run():
    chain = r50g25g._chain()
    rows = []
    all_failures = []
    witness = None

    for formula, meta in frozen_candidates():
        row, candidate_witness, failures = audit_candidate(formula, meta, chain)
        rows.append(row)
        all_failures.extend(failures)
        if failures:
            break
        if candidate_witness is not None:
            witness = candidate_witness
            break

    if all_failures:
        verdict = FAILURE
    elif witness is not None and witness["obstruction_class"] == "ACTUAL_DP_SIZE_ROUTE_OBSTRUCTION":
        verdict = ACTUAL_OBSTRUCTION
    elif witness is not None:
        verdict = CERT_OBSTRUCTION
    else:
        verdict = SURVIVAL

    return {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AR_receipt_commit": PARENT_AR_RECEIPT_COMMIT,
        "parent_AR_sealed_head": PARENT_AR_SEALED_HEAD,
        "verdict": verdict,
        "candidate_count_audited": len(rows),
        "rows": rows,
        "first_reachable_obstruction": witness,
        "falsifier_count": len(all_failures),
        "falsifiers": all_failures,
        "scientific_scope": {
            "universal_envelope_admissible_pivot_existence": "FALSIFIED_FOR_CURRENT_CERTIFICATE_SELECTOR" if witness is not None else "OPEN",
            "actual_exact_DP_size_door_existence": ("FALSIFIED_ON_WITNESS" if witness is not None and witness["obstruction_class"] == "ACTUAL_DP_SIZE_ROUTE_OBSTRUCTION" else "OPEN"),
            "route_completeness_for_arbitrary_CNF": "OBSTRUCTION_FOUND" if witness is not None else "OPEN",
            "finite_search_is_universal_proof": False,
            "end_to_end_polynomial_runtime": "OPEN",
        },
        "next_gate": (
            "R50G25AT_TIGHTEN_ADMISSIBILITY_CERTIFICATE_ON_AS_WITNESS" if verdict == CERT_OBSTRUCTION else
            "R50G25AT_ALTERNATIVE_POLYNOMIAL_DOOR_ON_ACTUAL_SIZE_OBSTRUCTION" if verdict == ACTUAL_OBSTRUCTION else
            "R50G25AT_SYMBOLIC_RESIDUAL_FIXPOINT_INEQUALITY_OR_COUNTEREXAMPLE"
        ),
        "firewalls": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "certificate_failure_is_not_exact_DP_failure": True,
            "route_obstruction_is_not_P_vs_NP_result": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    w = result["first_reachable_obstruction"]
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "candidate_count_audited": result["candidate_count_audited"],
        "falsifier_count": result["falsifier_count"],
        "witness_family": None if w is None else w["meta"]["family"],
        "witness_n": None if w is None else w["meta"].get("n"),
        "witness_residual_CLV": None if w is None else w["residual_CLV"],
        "witness_exact_size_admissible_pivots": None if w is None else w["exact_size_admissible_pivot_count"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
