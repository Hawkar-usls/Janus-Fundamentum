from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42

Formula = Tuple[Tuple[int, ...], ...]
SEED, N, RATIO = 43004, 48, 4.3
EXPECTED_INPUT_HASH = "eab8907cd5e97c244548797f226a91dfd0d43c196fb4461fb8880234c7de43a6"
EXPECTED_STALL_HASH = "95c0051895557d9353cc889cc7b1a35d225e60f264dfd8da56bb4da67439a6b7"
EXPECTED_STALL_CLV = (203, 603, 48)


def clv(f: Formula) -> Tuple[int, int, int]:
    return r33.measure(f)


def replay_to_r42_stall() -> dict:
    formula = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    if r42.formula_hash(formula) != EXPECTED_INPUT_HASH:
        raise AssertionError("R44 input drift")
    cycles: List[dict] = []
    for cycle_index in range(1000):
        before = formula
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            raise AssertionError(("unexpected terminal before sealed R43 stall", reduced["terminal"]))
        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            raise AssertionError("unexpected affine terminal before sealed R43 stall")
        rup = r35b.run_candidate(after_r33)
        rup_check = r35b.independent_certificate_replay(after_r33, rup)
        if not rup_check["pass"]:
            raise AssertionError("RUP replay failed")
        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            raise AssertionError("unexpected RUP terminal before sealed R43 stall")
        after_rup = r33.canonical_formula(rup["final_formula"])
        bve, _ = r42.best_sa_bve_candidate(after_rup)
        after_bve = after_rup
        if bve is not None:
            check = r42.independent_sa_bve_replay(after_rup, bve)
            if not check["pass"]:
                raise AssertionError("SA-BVE replay failed")
            after_bve = r33.canonical_formula(bve["transformed"])
        cycles.append({
            "cycle": cycle_index,
            "before_CLV": list(clv(before)),
            "R33_rules": reduced["total_rule_applications"],
            "RUP_strengthenings": rup["successful_strengthenings"],
            "SA_BVE_applied": bve is not None,
            "after_CLV": list(clv(after_bve)),
        })
        if after_bve == before:
            if r42.formula_hash(after_bve) != EXPECTED_STALL_HASH or clv(after_bve) != EXPECTED_STALL_CLV:
                raise AssertionError("sealed R43 stall drift")
            return {"formula": after_bve, "cycles": cycles}
        formula = after_bve
    raise AssertionError("replay cycle limit")


def forced_elimination(formula: Formula, var: int) -> Optional[dict]:
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(formula, var)
    if not pos or not neg:
        return None
    base = tuple(c for c in formula if var not in c and -var not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    forced = r42.subsumption_minimize(pool)
    before_clv = clv(formula)
    forced_clv = clv(forced)

    reduced = r33.simplify(forced)
    after_r33 = r33.canonical_formula(reduced["final_formula"])
    terminal = None
    semantic_sat = None
    after_norm = after_r33
    affine_reason = None
    rup_strengthenings = None

    if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
        solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
        if not solved["verification_pass"]:
            raise AssertionError(("terminal verification failed", var))
        terminal = solved["kind"]
        semantic_sat = solved["sat"]
    else:
        affine = r34.recognize_complete_affine_cnf(after_r33)
        affine_reason = affine["reason"]
        if affine["recognized"]:
            solution = r34.solve_gf2_with_certificate(affine["equations"])
            verify = r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("affine verification failed", var))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = solution["sat"]
        else:
            rup = r35b.run_candidate(after_r33)
            rup_check = r35b.independent_certificate_replay(after_r33, rup)
            if not rup_check["pass"]:
                raise AssertionError(("forced RUP replay failed", var))
            rup_strengthenings = rup["successful_strengthenings"]
            after_norm = r33.canonical_formula(rup["final_formula"])
            if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
                terminal = "RUP_UNSAT"
                semantic_sat = False

    final_clv = clv(after_norm)
    escape = terminal is not None or final_clv < before_clv
    return {
        "var": var,
        "source_positive_count": len(pos),
        "source_negative_count": len(neg),
        "non_tautological_resolvent_count": len(resolvents),
        "resolution_pair_checks": pair_checks,
        "pool_clause_count_before_subsumption": len(pool),
        "forced_CLV": list(forced_clv),
        "immediate_CLV_descent": forced_clv < before_clv,
        "temporary_clause_delta": forced_clv[0] - before_clv[0],
        "temporary_literal_delta": forced_clv[1] - before_clv[1],
        "R33_rule_applications_after_forced_step": reduced["total_rule_applications"],
        "RUP_strengthenings_after_forced_step": rup_strengthenings,
        "affine_reason": affine_reason,
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "post_normalization_CLV": list(final_clv),
        "net_CLV_descent_from_original_stall": final_clv < before_clv,
        "escape_signal": escape,
    }


def run_forensics() -> dict:
    replay = replay_to_r42_stall()
    stall: Formula = replay["formula"]

    r33_check = r33.simplify(stall)
    affine = r34.recognize_complete_affine_cnf(stall)
    rup = r35b.run_candidate(stall)
    rup_replay = r35b.independent_certificate_replay(stall, rup)
    direct_bve, direct_ledger = r42.best_sa_bve_candidate(stall)

    local_minimum = (
        r33_check["terminal"] == "STALLED_STACK_LEAN_CORE"
        and r33_check["total_rule_applications"] == 0
        and not affine["recognized"]
        and rup["status"] == "STALLED_RUP_CORE"
        and rup["successful_strengthenings"] == 0
        and rup_replay["pass"]
        and direct_bve is None
    )

    probes = []
    for var in r33.variables(stall):
        row = forced_elimination(stall, var)
        if row is not None:
            probes.append(row)
    immediate_descents = [x for x in probes if x["immediate_CLV_descent"]]
    escapes = [x for x in probes if x["escape_signal"]]
    best_escape = min(
        escapes,
        key=lambda x: (0 if x["terminal"] else 1, tuple(x["post_normalization_CLV"]), x["var"]),
        default=None,
    )

    if not local_minimum or immediate_descents:
        verdict = "R44_NOT_A_MONOTONE_LOCAL_MINIMUM_OR_LINEAGE_DRIFT"
    elif escapes:
        verdict = "R44_MONOTONE_CLV_LOCAL_MINIMUM__ONE_ELIMINATION_ASCENT_TO_DESCENT_ESCAPE_EXISTS"
    else:
        verdict = "R44_MONOTONE_CLV_LOCAL_MINIMUM__NO_ONE_ELIMINATION_ESCAPE"

    return {
        "schema": "JANUS_TRUMP_R44_43004_STALL_CLASS_FORENSICS_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "sealed_counterexample": {
            "seed": SEED,
            "input_sha256": EXPECTED_INPUT_HASH,
            "stall_sha256": EXPECTED_STALL_HASH,
            "stall_measure_CLV": list(EXPECTED_STALL_CLV),
            "replay_cycles": replay["cycles"],
        },
        "operator_exhaustion": {
            "R33_zero_rules": r33_check["total_rule_applications"] == 0,
            "R34_affine_recognized": affine["recognized"],
            "R34_reason": affine["reason"],
            "R35B_status": rup["status"],
            "R35B_strengthenings": rup["successful_strengthenings"],
            "R35B_independent_replay_pass": rup_replay["pass"],
            "SA_BVE_immediate_candidate": direct_bve is not None,
            "SA_BVE_scan_ledger": direct_ledger,
            "monotone_CLV_local_minimum": local_minimum,
        },
        "forced_exact_DP_probe": {
            "diagnostic_only": True,
            "variables_with_both_polarities": len(probes),
            "immediate_descent_count": len(immediate_descents),
            "escape_count": len(escapes),
            "best_escape": best_escape,
            "rows": probes,
        },
        "class_level_failure_mechanism": {
            "id": "MONOTONE_CLV_LOCAL_MINIMUM" if local_minimum else "UNRESOLVED",
            "statement": "The frozen controller can reach a nonsemantic state where every admitted monotone operator is exhausted. Immediate strict CLV descent is therefore too strong to establish coverage for this controller.",
            "candidate_successor_mechanism": "BOUNDED_EXACT_ASCENT_TO_DESCENT_MACRO" if escapes else None,
            "candidate_is_admitted": False,
            "required_future_proof": "A successor may use an atomic macro only if its internal exact work, intermediate representation size, reconstruction/certification, and step count are polynomially bounded and the macro boundary has strict net global-rank descent for every state in its declared applicability class.",
        },
        "claim_ceiling": {
            "R42_remains_refuted": True,
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "next_gate": "R45_PREREGISTER_BOUNDED_ASCENT_TO_DESCENT_MACRO" if escapes else "RETURN_TO_CAPTAIN_CLASS_LEVEL_MECHANISM_SEARCH",
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_forensics()
    assert d["sealed_counterexample"]["stall_sha256"] == EXPECTED_STALL_HASH
    assert d["operator_exhaustion"]["monotone_CLV_local_minimum"] is True
    assert d["forced_exact_DP_probe"]["immediate_descent_count"] == 0
    assert d["P_VS_NP"] == "OPEN"
    print("R44_SELF_TEST_PASS", d["verdict"], "escapes", d["forced_exact_DP_probe"]["escape_count"])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_forensics(), indent=2, sort_keys=True) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
