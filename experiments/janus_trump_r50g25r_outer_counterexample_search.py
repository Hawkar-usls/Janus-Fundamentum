from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25h_micro_rup_restart_broader_1212_polynomial_ledger_audit as r50g25h

GATE = "JANUS_TRUMP_R50G25R_OUTER_COUNTEREXAMPLE_SEARCH"
Q_PREREG_COMMIT = "f2f5005bd68420dc04e5a4bf7e76f6a482d41384"
Q_JOURNAL_COMMIT = "600ee156f0fc45bec538ee13c9a1dbe7046955bb"
FALSIFIER_CLASSES = (
    "CERTIFICATE_FAILURE",
    "RECONSTRUCTION_FAILURE",
    "PROGRESS_FAILURE",
    "RESIDUAL_FIXPOINT",
    "POLYNOMIAL_LEDGER_FAILURE",
    "SEMANTIC_MISMATCH",
)


def exact_semantic_validation(r33, formula):
    """Validation oracle only. Never used to generate/select candidates."""
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 9:
        raise AssertionError(("R50G25R_VALIDATION_DOMAIN_DRIFT", len(vs)))
    count = 0
    first_model = None
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if r33.eval_formula(formula, a):
            count += 1
            if first_model is None:
                first_model = {str(k): bool(v) for k, v in sorted(a.items())}
    return {
        "variable_count": len(vs),
        "assignment_space_checked": 2 ** len(vs),
        "sat": count > 0,
        "model_count": count,
        "first_model": first_model,
    }


def random_3cnf(r33, n, m, seed, planted=None):
    rng = random.Random(int(seed))
    clauses = set()
    attempts = 0
    while len(clauses) < m and attempts < 20000:
        attempts += 1
        vars3 = sorted(rng.sample(range(1, n + 1), 3))
        lits = []
        for v in vars3:
            sign = 1 if rng.getrandbits(1) else -1
            lits.append(sign * v)
        clause = tuple(r33.canonical_clause(lits))
        if planted is not None:
            # Reject only clauses falsified by the planted assignment.  Selection
            # is syntactic/planted, never based on exact SAT enumeration.
            if not any((lit > 0) == bool(planted[abs(lit)]) for lit in clause):
                continue
        clauses.add(clause)
    if len(clauses) < m:
        raise AssertionError(("R50G25R_GENERATOR_EXHAUSTED", n, m, seed, len(clauses)))
    return r33.canonical_formula(clauses)


def xor3_cnf(r33, a, b, c, parity):
    clauses = []
    for bits in itertools.product((False, True), repeat=3):
        if (int(bits[0]) ^ int(bits[1]) ^ int(bits[2])) == int(parity):
            continue
        clause = []
        for v, bit in zip((a, b, c), bits):
            clause.append(-v if bit else v)
        clauses.append(tuple(r33.canonical_clause(clause)))
    return clauses


def xor_cycle_formula(r33, n, pattern):
    clauses = []
    for i in range(n):
        a = i + 1
        b = ((i + 1) % n) + 1
        c = ((i + 2) % n) + 1
        if pattern == "ZERO":
            p = 0
        elif pattern == "ONE":
            p = 1
        elif pattern == "ALT":
            p = i & 1
        else:
            raise AssertionError(pattern)
        clauses.extend(xor3_cnf(r33, a, b, c, p))
    return r33.canonical_formula(clauses)


def generate_outer_candidates(r33):
    """Truth-blind deterministic outer expansion beyond frozen <=6-var targets."""
    out = {}
    requested = Counter()

    def add(family, formula, meta):
        formula = r33.canonical_formula(formula)
        vcount = len(r33.variables(formula))
        if vcount < 7:
            return
        key = tuple(formula)
        out.setdefault(key, {"family": family, "formula": formula, "meta": meta})

    # Broad random 3-SAT around/aroundside the classical phase-transition density.
    for n in (7, 8, 9):
        for density in (3.80, 4.26, 4.80):
            m = max(1, int(round(density * n)))
            for seed_i in range(24):
                seed = 100000 * n + 1000 * int(round(density * 100)) + seed_i
                requested["RANDOM_THRESHOLD"] += 1
                add("RANDOM_THRESHOLD", random_3cnf(r33, n, m, seed), {
                    "n": n, "m": m, "density": density, "seed": seed,
                })

    # Planted SAT formulas: generation knows a planted assignment, but exact truth
    # remains hidden from selection and is checked only after the scheduler runs.
    for n in (7, 8, 9):
        m = int(round(4.60 * n))
        for seed_i in range(16):
            seed = 700000 + 10000 * n + seed_i
            rng = random.Random(seed ^ 0x5A17)
            planted = {v: bool(rng.getrandbits(1)) for v in range(1, n + 1)}
            requested["PLANTED_THRESHOLD"] += 1
            add("PLANTED_THRESHOLD", random_3cnf(r33, n, m, seed, planted=planted), {
                "n": n, "m": m, "density": 4.60, "seed": seed,
                "planted_assignment_hash_only": hash(tuple(sorted(planted.items()))),
            })

    # Structured parity-rich 3CNFs, independent from the old pair-state grammar.
    for n in (7, 8, 9):
        for pattern in ("ZERO", "ONE", "ALT"):
            requested["XOR_CYCLE"] += 1
            add("XOR_CYCLE", xor_cycle_formula(r33, n, pattern), {
                "n": n, "pattern": pattern,
            })

    # Adversarial structural selection: search for formulas where frozen R33 alone
    # stalls.  This uses solver behavior only; exact SAT truth is never consulted.
    stall_selected = 0
    stall_scanned = 0
    for seed_i in range(2500):
        if stall_selected >= 40:
            break
        n = 9
        m = 39
        seed = 9000000 + seed_i
        formula = random_3cnf(r33, n, m, seed)
        stall_scanned += 1
        try:
            baseline = r33.simplify(formula)
        except AssertionError:
            # Preserve candidate for the outer audit rather than using an exception
            # to silently filter it away.
            requested["R33_STALL_TARGET"] += 1
            add("R33_STALL_TARGET", formula, {
                "n": n, "m": m, "seed": seed,
                "prefilter": "R33_ASSERTION",
            })
            stall_selected += 1
            continue
        if str(baseline.get("terminal")) == "STALLED_STACK_LEAN_CORE":
            requested["R33_STALL_TARGET"] += 1
            add("R33_STALL_TARGET", formula, {
                "n": n, "m": m, "seed": seed,
                "prefilter": "R33_STALLED_STACK_LEAN_CORE",
            })
            stall_selected += 1

    return list(out.values()), {
        "requested_by_family": dict(sorted(requested.items())),
        "unique_candidate_count": len(out),
        "stall_prefilter_scanned": stall_scanned,
        "stall_prefilter_selected": stall_selected,
        "truth_used_for_generation_or_selection": False,
    }


def classify_assertion(exc):
    text = repr(exc)
    upper = text.upper()
    if "RECONSTRUCTION" in upper:
        return "RECONSTRUCTION_FAILURE"
    if "STRICT_DESCENT" in upper or "HEIGHT_BOUND" in upper or "PROGRESS" in upper:
        return "PROGRESS_FAILURE"
    if "CERT_FAIL" in upper or "VERIFY_FAIL" in upper or "CERTIFICATE" in upper:
        return "CERTIFICATE_FAILURE"
    return None


def meter_violations(micro, envelope):
    pairs = {
        "R33_check_operation_upper_ledger": "R33_check_operation_upper_ledger_bound",
        "RUP_checks": "RUP_checks_bound",
        "RUP_UP_clause_scans": "RUP_UP_clause_scans_bound",
        "RUP_UP_literal_inspections": "RUP_UP_literal_inspections_bound",
        "restart_count": "restart_count_bound",
        "GF2_estimated_bit_ops": "GF2_estimated_bit_ops_bound",
    }
    violations = []
    for observed_key, bound_key in pairs.items():
        observed = int(micro.get("ledger", {}).get(observed_key, 0))
        bound = int(envelope[bound_key])
        if observed > bound:
            violations.append({"metric": observed_key, "observed": observed, "bound": bound})
    return violations


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    candidates, generation = generate_outer_candidates(r33)
    if generation["unique_candidate_count"] < 200:
        raise AssertionError(("R50G25R_OUTER_BATCH_TOO_SMALL", generation))
    if generation["truth_used_for_generation_or_selection"]:
        raise AssertionError("R50G25R_TRUTH_LEAK_IN_GENERATOR")

    family_hist = Counter()
    exact_hist = Counter()
    terminal_hist = Counter()
    rup_hist = Counter()
    restart_hist = Counter()
    falsifier_hist = Counter()
    unclassified_assertion_count = 0
    exact_validation_count = 0
    examples = []
    falsifiers = []

    for index, item in enumerate(candidates):
        formula = r33.canonical_formula(item["formula"])
        family = item["family"]
        family_hist[family] += 1
        vcount = len(r33.variables(formula))
        if not (7 <= vcount <= 9):
            raise AssertionError(("R50G25R_OUTER_VARIABLE_BOUND_DRIFT", vcount, family))
        state_hash = r50g23.r50g4.fhash(formula)
        initial_measure = tuple(r33.measure(formula))
        envelope = r50g25h.polynomial_meter_envelope(initial_measure)

        micro = None
        local_classes = []
        local_detail = []
        try:
            micro = r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
        except AssertionError as exc:
            cls = classify_assertion(exc)
            if cls is None:
                unclassified_assertion_count += 1
                local_detail.append({"class": "UNCLASSIFIED_ASSERTION", "detail": repr(exc)[:1000]})
            else:
                local_classes.append(cls)
                local_detail.append({"class": cls, "detail": repr(exc)[:1000]})

        # Exact truth is consulted only now, after candidate generation/selection and
        # after the candidate scheduler run/exception.
        exact = exact_semantic_validation(r33, formula)
        exact_validation_count += 1
        exact_hist["SAT" if exact["sat"] else "UNSAT"] += 1

        if micro is not None:
            micro_sat = micro.get("semantic_sat")
            terminal = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
            terminal_hist[terminal] += 1
            rup_hist[int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0))] += 1
            restart_hist[int(micro.get("restart_count", 0))] += 1

            if micro_sat is None:
                local_classes.append("RESIDUAL_FIXPOINT")
                local_detail.append({"class": "RESIDUAL_FIXPOINT", "final_CLV": micro.get("final_CLV")})
            elif bool(micro_sat) != bool(exact["sat"]):
                local_classes.append("SEMANTIC_MISMATCH")
                local_detail.append({
                    "class": "SEMANTIC_MISMATCH",
                    "micro_sat": bool(micro_sat),
                    "exact_sat": bool(exact["sat"]),
                })

            if micro_sat is True and not micro.get("SAT_reconstruction", {}).get("pass", False):
                local_classes.append("RECONSTRUCTION_FAILURE")
                local_detail.append({"class": "RECONSTRUCTION_FAILURE", "source": "returned_micro_result"})

            violations = meter_violations(micro, envelope)
            if violations:
                local_classes.append("POLYNOMIAL_LEDGER_FAILURE")
                local_detail.append({"class": "POLYNOMIAL_LEDGER_FAILURE", "violations": violations})

        unique_classes = sorted(set(local_classes), key=lambda x: FALSIFIER_CLASSES.index(x))
        for cls in unique_classes:
            falsifier_hist[cls] += 1
        if unique_classes and len(falsifiers) < 50:
            falsifiers.append({
                "index": index,
                "state_hash": state_hash,
                "family": family,
                "meta": item["meta"],
                "CLV": list(initial_measure),
                "exact_validation": exact,
                "classes": unique_classes,
                "details": local_detail,
                "formula": [list(c) for c in formula],
            })

        if len(examples) < 30:
            examples.append({
                "index": index,
                "state_hash": state_hash,
                "family": family,
                "CLV": list(initial_measure),
                "exact_sat": bool(exact["sat"]),
                "exact_model_count": int(exact["model_count"]),
                "micro_terminal": None if micro is None else (str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"),
                "micro_RUP_strengthenings": None if micro is None else int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
                "micro_restarts": None if micro is None else int(micro.get("restart_count", 0)),
                "falsifier_classes": unique_classes,
            })

    found_classes = [c for c in FALSIFIER_CLASSES if falsifier_hist[c] > 0]
    if found_classes:
        verdict = "OUTER_COUNTEREXAMPLE_FOUND__" + "__".join(found_classes)
        next_gate = "R50G25S_MINIMAL_OUTER_FALSIFIER_FORENSICS"
    elif unclassified_assertion_count:
        verdict = "NO_Q_FALSIFIER_BUT_UNCLASSIFIED_ASSERTION_REQUIRES_FORENSICS"
        next_gate = "R50G25S_UNCLASSIFIED_ASSERTION_FORENSICS"
    else:
        verdict = "NO_Q_FALSIFIER_IN_PREREGISTERED_OUTER_BATCH"
        next_gate = "R50G25S_OUTER_SCALE_OR_STRUCTURED_COUNTEREXAMPLE_ESCALATION"

    return {
        "gate": GATE,
        "parent_Q_preregistration_commit": Q_PREREG_COMMIT,
        "parent_Q_journal_commit": Q_JOURNAL_COMMIT,
        "outer_expansion_authorized_by_user": True,
        "generation_contract": generation,
        "evaluated_outer_candidate_count": len(candidates),
        "family_partition": dict(sorted(family_hist.items())),
        "exact_validation_partition": dict(sorted(exact_hist.items())),
        "micro_terminal_partition": dict(sorted(terminal_hist.items())),
        "micro_RUP_strengthening_histogram": {str(k): int(v) for k, v in sorted(rup_hist.items())},
        "micro_restart_histogram": {str(k): int(v) for k, v in sorted(restart_hist.items())},
        "frozen_Q_falsifier_classes": list(FALSIFIER_CLASSES),
        "falsifier_partition": {c: int(falsifier_hist[c]) for c in FALSIFIER_CLASSES},
        "found_falsifier_classes": found_classes,
        "unclassified_assertion_count": unclassified_assertion_count,
        "exact_validation_count": exact_validation_count,
        "falsifier_examples": falsifiers,
        "examples": examples,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "candidate_generation_is_truth_blind": True,
            "exact_enumeration_is_validation_only": True,
            "outer_batch_is_not_universal_3CNF_coverage": True,
            "absence_of_falsifier_in_batch_is_not_proof": True,
            "presence_of_Q_falsifier_is_a_real_counterexample_to_current_candidate_machine_not_to_P_equals_NP": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
