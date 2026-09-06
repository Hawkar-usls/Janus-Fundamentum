from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25r_outer_counterexample_search as r50g25r
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25h_micro_rup_restart_broader_1212_polynomial_ledger_audit as r50g25h

GATE = "JANUS_TRUMP_R50G25S_MAX_RUP_OUTER_WITNESS_MINIMIZATION_AND_STRUCTURED_ESCALATION"
R_RUN = 34042681532
R_JOURNAL_COMMIT = "d77c1b7a0316d4bfd914e79ced8d5a1da5ce04c0"
S_PREREG_COMMIT = "d1185d2d348d616f9fe42f6ddabd231ee8dfc2b2"
EXPECTED_R_MAX_RUP = 21
FALSIFIER_CLASSES = tuple(r50g25r.FALSIFIER_CLASSES)


def exact_semantic_validation(r33, formula):
    """Validation oracle only; never used for generation, selection, or minimization."""
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 12:
        raise AssertionError(("R50G25S_VALIDATION_DOMAIN_DRIFT", len(vs)))
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


def micro_cost(micro):
    return (
        int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
        int(micro.get("restart_count", 0)),
        int(micro.get("round_count", 0)),
    )


def try_micro(formula, r50g23, r35b, r33, r47j):
    try:
        return r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j), None
    except AssertionError as exc:
        return None, exc


def recover_r_max_witness(r50g23, r35b, r33, r47j):
    candidates, generation = r50g25r.generate_outer_candidates(r33)
    best = None
    hist = Counter()
    assertion_count = 0
    for index, item in enumerate(candidates):
        formula = r33.canonical_formula(item["formula"])
        micro, exc = try_micro(formula, r50g23, r35b, r33, r47j)
        if exc is not None:
            assertion_count += 1
            continue
        cost = micro_cost(micro)
        hist[cost[0]] += 1
        row = {
            "index": index,
            "family": item["family"],
            "meta": item["meta"],
            "formula": formula,
            "state_hash": r50g23.r50g4.fhash(formula),
            "CLV": list(r33.measure(formula)),
            "cost": cost,
            "terminal": str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
        }
        if best is None or (cost, tuple(r33.measure(formula)), row["state_hash"]) > (
            best["cost"], tuple(best["CLV"]), best["state_hash"]
        ):
            best = row
    if best is None:
        raise AssertionError("R50G25S_NO_RECOVERED_R_WITNESS")
    if best["cost"][0] != EXPECTED_R_MAX_RUP:
        raise AssertionError(("R50G25S_R_MAX_RUP_DRIFT", best["cost"], hist))
    return best, {
        "recovered_candidate_count": len(candidates),
        "generation_contract": generation,
        "micro_assertion_count": assertion_count,
        "RUP_histogram": {str(k): int(v) for k, v in sorted(hist.items())},
    }


def preserves_target_debt(formula, target_rup, r50g23, r35b, r33, r47j):
    micro, exc = try_micro(formula, r50g23, r35b, r33, r47j)
    if exc is not None or micro is None or micro.get("semantic_sat") is None:
        return False, micro, exc
    return micro_cost(micro)[0] >= int(target_rup), micro, None


def minimize_high_rup_witness(initial, target_rup, r50g23, r35b, r33, r47j):
    """Truth-blind greedy syntactic minimizer. This is adversarial generation, not an equivalence rewrite."""
    state = r33.canonical_formula(initial)
    trace = []
    changed = True
    while changed:
        changed = False
        for clause in list(state):
            candidate = r33.canonical_formula(c for c in state if c != clause)
            if not candidate:
                continue
            ok, micro, _exc = preserves_target_debt(candidate, target_rup, r50g23, r35b, r33, r47j)
            if ok:
                trace.append({
                    "op": "DELETE_CLAUSE",
                    "removed": list(clause),
                    "before_CLV": list(r33.measure(state)),
                    "after_CLV": list(r33.measure(candidate)),
                    "preserved_RUP": micro_cost(micro)[0],
                })
                state = candidate
                changed = True
                break

    # Literal-deletion pass after clause-minimality. The result may be <=3-CNF;
    # this is a hard-instance minimizer only and is never claimed equivalent.
    changed = True
    while changed:
        changed = False
        for clause in list(state):
            if len(clause) <= 1:
                continue
            for lit in list(clause):
                shortened = tuple(x for x in clause if x != lit)
                candidate = r33.canonical_formula([shortened if c == clause else c for c in state])
                if not candidate:
                    continue
                ok, micro, _exc = preserves_target_debt(candidate, target_rup, r50g23, r35b, r33, r47j)
                if ok:
                    trace.append({
                        "op": "DELETE_LITERAL",
                        "source_clause": list(clause),
                        "removed_literal": int(lit),
                        "before_CLV": list(r33.measure(state)),
                        "after_CLV": list(r33.measure(candidate)),
                        "preserved_RUP": micro_cost(micro)[0],
                    })
                    state = candidate
                    changed = True
                    break
            if changed:
                break

    micro, exc = try_micro(state, r50g23, r35b, r33, r47j)
    if exc is not None or micro is None:
        raise AssertionError(("R50G25S_MINIMIZER_FINAL_MICRO_FAIL", repr(exc)))
    return state, micro, trace


def prism_graph(k):
    # 2k vertices, 3k edges, every vertex degree 3.
    edges = []
    for i in range(k):
        edges.append((i, (i + 1) % k))
        edges.append((k + i, k + ((i + 1) % k)))
        edges.append((i, k + i))
    return 2 * k, edges


def tseitin_prism_formula(r33, k, charge_pattern):
    vertex_count, edges = prism_graph(k)
    incident = {v: [] for v in range(vertex_count)}
    for edge_index, (u, v) in enumerate(edges, start=1):
        incident[u].append(edge_index)
        incident[v].append(edge_index)
    if not all(len(incident[v]) == 3 for v in incident):
        raise AssertionError("R50G25S_PRISM_NOT_CUBIC")

    if charge_pattern == "ZERO":
        charges = [0] * vertex_count
    elif charge_pattern == "SINGLE":
        charges = [1] + [0] * (vertex_count - 1)
    elif charge_pattern == "PAIR":
        charges = [1, 1] + [0] * (vertex_count - 2)
    elif charge_pattern == "ALT":
        charges = [v & 1 for v in range(vertex_count)]
    else:
        raise AssertionError(charge_pattern)

    clauses = []
    for v in range(vertex_count):
        a, b, c = incident[v]
        clauses.extend(r50g25r.xor3_cnf(r33, a, b, c, charges[v]))
    return r33.canonical_formula(clauses), {
        "prism_k": k,
        "vertex_count": vertex_count,
        "edge_variable_count": len(edges),
        "charge_pattern": charge_pattern,
        "charge_parity": sum(charges) & 1,
    }


def generate_structured_escalation(r33):
    out = {}
    requested = Counter()

    def add(family, formula, meta):
        f = r33.canonical_formula(formula)
        if len(r33.variables(f)) > 12:
            raise AssertionError(("R50G25S_STRUCTURED_VAR_BOUND", family, len(r33.variables(f))))
        out.setdefault(tuple(f), {"family": family, "formula": f, "meta": meta})
        requested[family] += 1

    # Cubic Tseitin cores: parity structure with proof complexity relevance.
    for k in (3, 4):  # 9 and 12 edge variables
        for pattern in ("ZERO", "SINGLE", "PAIR", "ALT"):
            f, meta = tseitin_prism_formula(r33, k, pattern)
            add("TSEITIN_PRISM", f, meta)

    # Larger parity cycles than R, still exact-validatable.
    for n in (10, 11, 12):
        for pattern in ("ZERO", "ONE", "ALT"):
            add("XOR_CYCLE_LARGE", r50g25r.xor_cycle_formula(r33, n, pattern), {
                "n": n, "pattern": pattern,
            })

    # Larger random threshold instances. Generation is deterministic and truth blind.
    for n in (10, 11, 12):
        for density in (4.00, 4.26, 4.55):
            m = int(round(density * n))
            for seed_i in range(12):
                seed = 15000000 + 100000 * n + 1000 * int(round(density * 100)) + seed_i
                add("RANDOM_THRESHOLD_LARGE", r50g25r.random_3cnf(r33, n, m, seed), {
                    "n": n, "m": m, "density": density, "seed": seed,
                })

    # Truth-blind targeted selection of larger states on which R33 alone stalls.
    selected = 0
    scanned = 0
    for seed_i in range(4000):
        if selected >= 36:
            break
        n = 12
        m = 51
        seed = 18000000 + seed_i
        f = r50g25r.random_3cnf(r33, n, m, seed)
        scanned += 1
        try:
            baseline = r33.simplify(f)
            stalled = str(baseline.get("terminal")) == "STALLED_STACK_LEAN_CORE"
        except AssertionError:
            stalled = True
        if stalled:
            add("R33_STALL_TARGET_LARGE", f, {"n": n, "m": m, "seed": seed})
            selected += 1

    return list(out.values()), {
        "requested_by_family": dict(sorted(requested.items())),
        "unique_candidate_count": len(out),
        "stall_prefilter_scanned": scanned,
        "stall_prefilter_selected": selected,
        "truth_used_for_generation_or_selection": False,
    }


def audit_candidate(item, r50g23, r35b, r33, r47j):
    formula = r33.canonical_formula(item["formula"])
    state_hash = r50g23.r50g4.fhash(formula)
    measure = tuple(r33.measure(formula))
    envelope = r50g25h.polynomial_meter_envelope(measure)
    local_classes = []
    details = []

    micro, exc = try_micro(formula, r50g23, r35b, r33, r47j)
    if exc is not None:
        cls = r50g25r.classify_assertion(exc)
        if cls is None:
            details.append({"class": "UNCLASSIFIED_ASSERTION", "detail": repr(exc)[:1000]})
        else:
            local_classes.append(cls)
            details.append({"class": cls, "detail": repr(exc)[:1000]})

    # Validation only after candidate fixed and scheduler attempted.
    exact = exact_semantic_validation(r33, formula)

    if micro is not None:
        micro_sat = micro.get("semantic_sat")
        if micro_sat is None:
            local_classes.append("RESIDUAL_FIXPOINT")
            details.append({"class": "RESIDUAL_FIXPOINT", "final_CLV": micro.get("final_CLV")})
        elif bool(micro_sat) != bool(exact["sat"]):
            local_classes.append("SEMANTIC_MISMATCH")
            details.append({"class": "SEMANTIC_MISMATCH", "micro_sat": bool(micro_sat), "exact_sat": bool(exact["sat"])})
        if micro_sat is True and not micro.get("SAT_reconstruction", {}).get("pass", False):
            local_classes.append("RECONSTRUCTION_FAILURE")
            details.append({"class": "RECONSTRUCTION_FAILURE", "source": "returned_micro_result"})
        violations = r50g25r.meter_violations(micro, envelope)
        if violations:
            local_classes.append("POLYNOMIAL_LEDGER_FAILURE")
            details.append({"class": "POLYNOMIAL_LEDGER_FAILURE", "violations": violations})

    classes = sorted(set(local_classes), key=lambda x: FALSIFIER_CLASSES.index(x))
    return {
        "family": item["family"],
        "meta": item["meta"],
        "state_hash": state_hash,
        "CLV": list(measure),
        "formula": [list(c) for c in formula],
        "exact": exact,
        "micro_terminal": None if micro is None else (str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"),
        "micro_cost": None if micro is None else list(micro_cost(micro)),
        "classes": classes,
        "details": details,
        "unclassified_assertion": bool(exc is not None and r50g25r.classify_assertion(exc) is None),
    }


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()

    max_witness, recovery = recover_r_max_witness(r50g23, r35b, r33, r47j)
    minimized, minimized_micro, minimization_trace = minimize_high_rup_witness(
        max_witness["formula"], EXPECTED_R_MAX_RUP, r50g23, r35b, r33, r47j
    )
    minimized_exact = exact_semantic_validation(r33, minimized)
    original_exact = exact_semantic_validation(r33, max_witness["formula"])
    preserved_exact_max = micro_cost(minimized_micro)[0] >= EXPECTED_R_MAX_RUP

    structured, generation = generate_structured_escalation(r33)
    family_hist = Counter()
    exact_hist = Counter()
    terminal_hist = Counter()
    rup_hist = Counter()
    restart_hist = Counter()
    falsifier_hist = Counter()
    unclassified = 0
    falsifiers = []
    top_cost = []

    # Include minimized witness as a dedicated adversarial candidate, but do not
    # double-count it as evidence for structured family diversity.
    all_items = structured + [{
        "family": "MINIMIZED_R_MAX_WITNESS",
        "formula": minimized,
        "meta": {"source_state_hash": max_witness["state_hash"], "target_RUP": EXPECTED_R_MAX_RUP},
    }]

    for item in all_items:
        row = audit_candidate(item, r50g23, r35b, r33, r47j)
        family_hist[row["family"]] += 1
        exact_hist["SAT" if row["exact"]["sat"] else "UNSAT"] += 1
        terminal_hist[str(row["micro_terminal"])] += 1
        if row["micro_cost"] is not None:
            rup_hist[int(row["micro_cost"][0])] += 1
            restart_hist[int(row["micro_cost"][1])] += 1
            top_cost.append((tuple(row["micro_cost"]), row["state_hash"], row["family"], row["CLV"]))
        for cls in row["classes"]:
            falsifier_hist[cls] += 1
        if row["unclassified_assertion"]:
            unclassified += 1
        if row["classes"] and len(falsifiers) < 50:
            falsifiers.append(row)

    top_cost.sort(reverse=True)
    found_classes = [c for c in FALSIFIER_CLASSES if falsifier_hist[c] > 0]
    if found_classes:
        verdict = "STRUCTURED_OUTER_COUNTEREXAMPLE_FOUND__" + "__".join(found_classes)
        next_gate = "R50G25T_MINIMAL_STRUCTURED_FALSIFIER_FORENSICS"
    elif unclassified:
        verdict = "NO_Q_FALSIFIER_BUT_UNCLASSIFIED_ASSERTION_IN_STRUCTURED_ESCALATION"
        next_gate = "R50G25T_UNCLASSIFIED_STRUCTURED_ASSERTION_FORENSICS"
    else:
        verdict = "NO_Q_FALSIFIER_IN_S_STRUCTURED_ESCALATION"
        next_gate = "R50G25T_RESOURCE_GROWTH_LADDER_AND_HARD_FAMILY_ESCALATION"

    return {
        "gate": GATE,
        "parent_R_run": R_RUN,
        "parent_R_journal_commit": R_JOURNAL_COMMIT,
        "S_preregistration_commit": S_PREREG_COMMIT,
        "max_R_witness_recovery": {
            "state_hash": max_witness["state_hash"],
            "family": max_witness["family"],
            "meta": max_witness["meta"],
            "CLV": max_witness["CLV"],
            "micro_cost_RUP_restart_rounds": list(max_witness["cost"]),
            "terminal": max_witness["terminal"],
            "exact_validation_after_selection": original_exact,
            "recovery_audit": recovery,
        },
        "truth_blind_minimization": {
            "target_RUP": EXPECTED_R_MAX_RUP,
            "preserved_exact_R_maximum": preserved_exact_max,
            "source_CLV": max_witness["CLV"],
            "final_CLV": list(r33.measure(minimized)),
            "source_clause_count": len(max_witness["formula"]),
            "final_clause_count": len(minimized),
            "final_micro_cost_RUP_restart_rounds": list(micro_cost(minimized_micro)),
            "final_terminal": str(minimized_micro.get("terminal")),
            "operation_count": len(minimization_trace),
            "operations": minimization_trace,
            "source_and_minimized_truth_required_equal": false,
            "exact_validation_after_minimization": minimized_exact,
            "final_state_hash": r50g23.r50g4.fhash(minimized),
            "final_formula": [list(c) for c in minimized],
        },
        "structured_generation_contract": generation,
        "evaluated_candidate_count_including_minimized_witness": len(all_items),
        "family_partition": dict(sorted(family_hist.items())),
        "exact_validation_partition": dict(sorted(exact_hist.items())),
        "micro_terminal_partition": dict(sorted(terminal_hist.items())),
        "micro_RUP_strengthening_histogram": {str(k): int(v) for k, v in sorted(rup_hist.items())},
        "micro_restart_histogram": {str(k): int(v) for k, v in sorted(restart_hist.items())},
        "top_10_route_costs": [
            {"cost_RUP_restart_rounds": list(cost), "state_hash": h, "family": fam, "CLV": clv}
            for cost, h, fam, clv in top_cost[:10]
        ],
        "frozen_Q_falsifier_classes": list(FALSIFIER_CLASSES),
        "falsifier_partition": {c: int(falsifier_hist[c]) for c in FALSIFIER_CLASSES},
        "unclassified_assertion_count": unclassified,
        "falsifier_examples": falsifiers,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "minimization_is_adversarial_generation_not_equivalence_rewrite": True,
            "truth_not_used_for_selection_or_minimization": True,
            "exact_enumeration_is_validation_only": True,
            "finite_structured_success_is_not_universal_coverage": True,
            "absence_of_falsifier_is_not_proof": True,
        },
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
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
