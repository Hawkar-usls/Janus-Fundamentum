from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import janus_trump_r50g25as_universal_envelope_admissible_pivot as asmod

GATE = "JANUS_TRUMP_R50G25AT_AFFINE_CORE_PLUS_DEFECT_POLYNOMIAL_DOOR_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "3ac282d8594920cb37cfae08e79b2a0f526165fb"
PARENT_AS_RECEIPT = "4ca2803aae8503e05dfc7ed46266ebe89add67b9"
PARENT_AS_SEALED_HEAD = "7c8a2f2ba6b6de2591d6f1be1e5da59900bfdb63"
D_MAX = 4
AS_RESIDUAL_HASH = "0d46b6d6120f9a123ae75faf92ac6cfafbb57641bbc77c2c4512a8b642af3de7"
AS_RESIDUAL_CLV = (1121, 4485, 16)

PASS = "AFFINE_CORE_PLUS_BOUNDED_DEFECT_POLYNOMIAL_DOOR_PASS"
FAIL = "AT_FROZEN_DOOR_FALSIFIED_OR_IMPLEMENTATION_FAILURE"
BOUNDARY = "DEFECT_BOUND_EXCEEDED"


def canonical(formula):
    return asmod.canonical(formula)


def clv(formula):
    return asmod.clv(formula)


def formula_hash(formula):
    return asmod.formula_hash(formula)


def variables(formula):
    return sorted({abs(int(lit)) for clause in formula for lit in clause})


def clause_satisfied(clause, model):
    return any(bool(model.get(abs(lit), False)) == (lit > 0) for lit in clause)


def model_satisfies(formula, model):
    return all(clause_satisfied(c, model) for c in formula)


def clause_from_falsifying_bits(support, bits):
    return tuple(v if bit == 0 else -v for v, bit in zip(support, bits))


def replay_parity_block(support, rhs):
    # Equation XOR(support) = rhs. CNF excludes assignments with opposite parity.
    out = []
    forbidden_parity = 1 - int(rhs)
    for bits in itertools.product((0, 1), repeat=len(support)):
        if sum(bits) % 2 == forbidden_parity:
            out.append(clause_from_falsifying_bits(support, bits))
    return set(canonical(out))


def extract_affine_core(formula):
    f = canonical(formula)
    grouped = defaultdict(list)
    for clause in f:
        support = tuple(sorted(abs(int(lit)) for lit in clause))
        grouped[support].append(tuple(clause))

    equations = []
    affine_clauses = set()
    defects = []
    replay_failures = []
    group_rows = []

    for support in sorted(grouped):
        group = set(grouped[support])
        k = len(support)
        expected = 1 << max(0, k - 1)
        sign_parities = {sum(1 for lit in clause if lit < 0) % 2 for clause in group}
        recognized = len(group) == expected and len(sign_parities) == 1
        row = {
            "support": list(support),
            "width": k,
            "clause_count": len(group),
            "expected_parity_block_clause_count": expected,
            "recognized_affine": recognized,
        }
        if recognized:
            forbidden_parity = next(iter(sign_parities))
            rhs = 1 - forbidden_parity
            replay = replay_parity_block(support, rhs)
            replay_pass = replay == group
            row.update({"rhs": rhs, "replay_pass": replay_pass})
            if not replay_pass:
                replay_failures.append({
                    "kind": "AFFINE_REPLAY_MISMATCH",
                    "support": list(support),
                    "source_count": len(group),
                    "replay_count": len(replay),
                })
            else:
                equations.append({"vars": list(support), "rhs": int(rhs)})
                affine_clauses.update(group)
        else:
            defects.extend(sorted(group))
        group_rows.append(row)

    # Exact partition check: no source clause disappears or appears twice.
    defect_set = set(defects)
    partition_pass = affine_clauses.isdisjoint(defect_set) and (affine_clauses | defect_set) == set(f)
    if not partition_pass:
        replay_failures.append({"kind": "AFFINE_EXTRACTION_FAILURE", "detail": "partition mismatch"})

    return {
        "equations": equations,
        "defects": [tuple(c) for c in canonical(defects)],
        "affine_clause_count": len(affine_clauses),
        "defect_clause_count": len(defect_set),
        "recognized_equation_count": len(equations),
        "group_rows": group_rows,
        "replay_failures": replay_failures,
        "partition_pass": partition_pass,
    }


def row_from_equation(eq, var_index):
    mask = 0
    for v in eq["vars"]:
        mask ^= 1 << var_index[int(v)]
    return mask, int(eq["rhs"]) & 1


def provenance_indices(bits, count):
    return [i for i in range(count) if (bits >> i) & 1]


def verify_contradiction_certificate(source_rows, indices):
    mask = 0
    rhs = 0
    for i in indices:
        sm, sr = source_rows[int(i)]
        mask ^= sm
        rhs ^= sr
    return mask == 0 and rhs == 1


def gaussian_solve(equations, selected_literals, universe):
    universe = sorted(set(int(v) for v in universe))
    var_index = {v: i for i, v in enumerate(universe)}
    source_rows = []
    source_labels = []

    for eq in equations:
        source_rows.append(row_from_equation(eq, var_index))
        source_labels.append({"kind": "AFFINE", "vars": list(eq["vars"]), "rhs": int(eq["rhs"])})
    for lit in selected_literals:
        v = abs(int(lit))
        rhs = 1 if int(lit) > 0 else 0
        source_rows.append((1 << var_index[v], rhs))
        source_labels.append({"kind": "SELECTED_LITERAL", "literal": int(lit), "rhs": rhs})

    rows = [[m, r, 1 << i] for i, (m, r) in enumerate(source_rows)]
    rank = 0
    pivots = []
    xor_count = 0
    pivot_search_count = 0

    for col in range(len(universe)):
        bit = 1 << col
        pivot = None
        for i in range(rank, len(rows)):
            pivot_search_count += 1
            if rows[i][0] & bit:
                pivot = i
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and (rows[i][0] & bit):
                rows[i][0] ^= rows[rank][0]
                rows[i][1] ^= rows[rank][1]
                rows[i][2] ^= rows[rank][2]
                xor_count += 1
        pivots.append((col, rank))
        rank += 1

    contradiction = next((row for row in rows if row[0] == 0 and row[1] == 1), None)
    ledger = {
        "source_row_count": len(source_rows),
        "variable_count": len(universe),
        "rank": rank,
        "row_xor_count": xor_count,
        "pivot_search_count": pivot_search_count,
    }
    if contradiction is not None:
        indices = provenance_indices(contradiction[2], len(source_rows))
        cert_pass = verify_contradiction_certificate(source_rows, indices)
        return {
            "consistent": False,
            "contradiction_certificate_indices": indices,
            "contradiction_certificate_labels": [source_labels[i] for i in indices],
            "certificate_pass": cert_pass,
            "ledger": ledger,
        }

    # RREF + all free variables = 0 gives a deterministic witness.
    values = [0] * len(universe)
    for col, row_idx in pivots:
        rhs = rows[row_idx][1]
        other_mask = rows[row_idx][0] & ~(1 << col)
        accum = 0
        for j in range(len(universe)):
            if (other_mask >> j) & 1:
                accum ^= values[j]
        values[col] = rhs ^ accum
    model = {v: bool(values[var_index[v]]) for v in universe}

    equations_pass = True
    for sm, sr in source_rows:
        lhs = 0
        for j, v in enumerate(universe):
            if (sm >> j) & 1:
                lhs ^= int(model[v])
        if lhs != sr:
            equations_pass = False
            break

    return {
        "consistent": True,
        "model": {str(v): int(model[v]) for v in universe},
        "equations_pass": equations_pass,
        "ledger": ledger,
    }


def bounded_defect_decide(formula):
    f = canonical(formula)
    extraction = extract_affine_core(f)
    failures = list(extraction["replay_failures"])
    if not extraction["partition_pass"]:
        failures.append({"kind": "AFFINE_EXTRACTION_FAILURE"})
    if failures:
        return {"status": "FAIL", "failures": failures, "extraction": extraction}

    defects = extraction["defects"]
    if len(defects) > D_MAX:
        return {
            "status": BOUNDARY,
            "defect_count": len(defects),
            "extraction": extraction,
            "failures": [],
        }

    universe = variables(f)
    branch_count = math.prod(len(c) for c in defects) if defects else 1
    branches = []
    sat_result = None
    all_certificates_pass = True
    total_row_xors = 0
    total_pivot_searches = 0

    choices = itertools.product(*defects) if defects else [tuple()]
    for branch_index, selected in enumerate(choices):
        solved = gaussian_solve(extraction["equations"], selected, universe)
        total_row_xors += int(solved["ledger"]["row_xor_count"])
        total_pivot_searches += int(solved["ledger"]["pivot_search_count"])
        record = {
            "branch_index": branch_index,
            "selected_literals": list(map(int, selected)),
            "consistent": bool(solved["consistent"]),
            "ledger": solved["ledger"],
        }
        if solved["consistent"]:
            model = {int(k): bool(v) for k, v in solved["model"].items()}
            model_pass = bool(solved.get("equations_pass")) and model_satisfies(f, model)
            record["model_pass"] = model_pass
            record["true_variables"] = [v for v in universe if model[v]]
            branches.append(record)
            if model_pass:
                sat_result = record
                break
            failures.append({"kind": "RECONSTRUCTION_FAILURE", "branch_index": branch_index})
            break
        else:
            cert_pass = bool(solved.get("certificate_pass"))
            record["certificate_pass"] = cert_pass
            record["contradiction_certificate_indices"] = solved.get("contradiction_certificate_indices", [])
            branches.append(record)
            all_certificates_pass = all_certificates_pass and cert_pass
            if not cert_pass:
                failures.append({"kind": "GAUSSIAN_CERTIFICATE_FAILURE", "branch_index": branch_index})
                break

    if failures:
        decision = "FAIL"
    elif sat_result is not None:
        decision = "SAT"
    else:
        decision = "UNSAT" if len(branches) == branch_count and all_certificates_pass else "FAIL"
        if decision == "FAIL":
            failures.append({"kind": "GAUSSIAN_CERTIFICATE_FAILURE", "detail": "branch coverage incomplete"})

    return {
        "status": decision,
        "CLV": list(clv(f)),
        "formula_hash": formula_hash(f),
        "extraction": {
            "affine_clause_count": extraction["affine_clause_count"],
            "recognized_equation_count": extraction["recognized_equation_count"],
            "defect_clause_count": extraction["defect_clause_count"],
            "partition_pass": extraction["partition_pass"],
            "replay_failure_count": len(extraction["replay_failures"]),
        },
        "branch_count_bound_exact": branch_count,
        "branches_executed": len(branches),
        "winning_branch": sat_result,
        "all_unsat_certificates_pass": all_certificates_pass,
        "aggregate_ledger": {
            "total_row_xors": total_row_xors,
            "total_pivot_searches": total_pivot_searches,
            "theoretical_branch_bound": "product defect widths <= L^4 because D_MAX=4",
        },
        "failures": failures,
    }


def build_as_residual():
    root, meta = asmod.hamming_xor_formula(16, punctured=True)
    chain = asmod.r50g25g._chain()
    replay = asmod.y.policy_replay(root, chain)
    if replay.get("kind") != "RESIDUAL":
        raise RuntimeError(f"AS witness replay did not reach RESIDUAL: {replay.get('kind')}")
    residual = canonical(replay["state"])
    observed_hash = formula_hash(residual)
    observed_clv = clv(residual)
    if observed_hash != AS_RESIDUAL_HASH or observed_clv != AS_RESIDUAL_CLV:
        raise RuntimeError(f"AS witness drift: hash={observed_hash}, CLV={observed_clv}")
    return residual, {
        "root_meta": meta,
        "root_CLV": list(clv(root)),
        "residual_CLV": list(observed_clv),
        "residual_hash": observed_hash,
        "policy_route_length": len(replay.get("route", [])),
    }


def simple_controls():
    return [
        (
            "SIMPLE_D1_UNSAT",
            canonical([(-1,), (-2,), (1, 2)]),
            "UNSAT",
        ),
        (
            "SIMPLE_D2_SAT",
            canonical([(-1,), (-2,), (1, 3), (2, 3)]),
            "SAT",
        ),
        (
            "SIMPLE_D4_UNSAT",
            canonical([
                (-1,), (-2,), (-3,), (-4,),
                (1, 5), (2, 5), (3, -5), (4, -5),
            ]),
            "UNSAT",
        ),
    ]


def run():
    falsifiers = []
    rows = []

    try:
        as_residual, as_meta = build_as_residual()
        as_result = bounded_defect_decide(as_residual)
    except Exception as exc:
        return {
            "gate": GATE,
            "verdict": FAIL,
            "falsifier_count": 1,
            "falsifiers": [{"kind": "AS_WITNESS_NOT_SOLVED_BY_FROZEN_DOOR", "error": repr(exc)}],
            "firewall": firewall(),
        }

    rows.append({"name": "AS_WITNESS_D1_SAT", "expected": "SAT", "meta": as_meta, "result": as_result})
    if as_result.get("status") != "SAT":
        falsifiers.append({"kind": "AS_WITNESS_NOT_SOLVED_BY_FROZEN_DOOR", "observed": as_result.get("status")})
    if as_result.get("extraction", {}).get("defect_clause_count") != 1:
        falsifiers.append({"kind": "AFFINE_EXTRACTION_FAILURE", "control": "AS_WITNESS_D1_SAT", "observed_defects": as_result.get("extraction", {}).get("defect_clause_count")})

    for name, formula, expected in simple_controls():
        result = bounded_defect_decide(formula)
        rows.append({"name": name, "expected": expected, "result": result})
        if result.get("status") != expected:
            falsifiers.append({"kind": "BOUNDED_DEFECT_CONTROL_FAILURE", "control": name, "expected": expected, "observed": result.get("status")})

    for row in rows:
        result = row["result"]
        for failure in result.get("failures", []):
            kind = failure.get("kind", "IMPLEMENTATION_FAILURE")
            falsifiers.append({"kind": kind, "control": row["name"], "detail": failure})
        extraction = result.get("extraction", {})
        if extraction.get("replay_failure_count", 0):
            falsifiers.append({"kind": "AFFINE_REPLAY_MISMATCH", "control": row["name"]})
        if extraction.get("defect_clause_count", 0) > D_MAX:
            falsifiers.append({"kind": "NO_POLYNOMIAL_DOOR_ON_BOUNDED_DEFECT", "control": row["name"]})

    verdict = PASS if not falsifiers else FAIL
    return {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AS_receipt": PARENT_AS_RECEIPT,
        "parent_AS_sealed_head": PARENT_AS_SEALED_HEAD,
        "verdict": verdict,
        "D_MAX": D_MAX,
        "candidate_count_audited": len(rows),
        "rows": rows,
        "falsifier_count": len(falsifiers),
        "falsifiers": falsifiers,
        "scientific_scope": {
            "established_if_pass": "proof-carrying polynomial decision door only for exactly recognized affine-core plus <=4 defect clauses",
            "unbounded_defect_count": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "AS_universal_DP_route": "REMAINS_FALSIFIED",
            "complexity_theorem": "NONE_FOR_GENERAL_SAT",
        },
        "recommended_next_gate_if_pass": "R50G25AU_DEFECT_COUNT_GROWTH_OR_SECOND_STRUCTURAL_DOOR",
        "firewall": firewall(),
    }


def firewall():
    return {
        "P_VS_NP": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "TRUMP_finished": False,
        "AT_success_is_bounded_defect_only": True,
        "AT_does_not_repair_AS_universal_DP_claim": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("JANUS_TRUMP_R50G25AT_RESULT.json"))
    args = parser.parse_args()
    result = run()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": GATE,
        "verdict": result["verdict"],
        "falsifier_count": result["falsifier_count"],
        "candidate_count_audited": result.get("candidate_count_audited"),
    }, sort_keys=True))
    raise SystemExit(0 if result["verdict"] == PASS else 1)


if __name__ == "__main__":
    main()
