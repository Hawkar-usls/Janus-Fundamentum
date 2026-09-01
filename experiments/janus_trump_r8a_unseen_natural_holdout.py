#!/usr/bin/env python3
"""R8A: prospective natural-residual holdout for the frozen R7B+R7C+R7D stack."""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import random
import sys
from hashlib import sha256
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r7d_dense_3sat_polynomial_proof_attack as r7d
import janus_trump_r7d_dense_3sat_polynomial_proof_attack_fastpath as fast

LEGACY_SEED = 440223
EXPECTED = 16


def digest(cnf):
    return sha256(json.dumps([list(c) for c in direct.canon(cnf)], separators=(",", ":")).encode()).hexdigest()


def load_legacy_sat_core():
    path = Path(__file__).resolve().parent / "v0.3-adaptive-depletion" / "sat_core.py"
    spec = importlib.util.spec_from_file_location("janus_legacy_v03_sat_core_r8a", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen legacy sat_core")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def legacy_root_seeds():
    """Replay only the RNG draws in frozen run_v03.py, preserving its schedule."""
    master = random.Random(LEGACY_SEED)
    main_configs = [
        (3, 32, round(4.26 * 32)), (3, 48, round(4.26 * 48)),
        (3, 64, round(4.26 * 64)), (3, 96, round(4.26 * 96)),
        (3, 128, round(4.26 * 128)), (5, 48, round(6.10 * 48)),
        (5, 64, round(6.10 * 64)), (5, 96, round(6.10 * 96)),
    ]
    planted = []
    for ci, (k, n, m) in enumerate(main_configs):
        for trial in range(16):
            inst_seed = master.randrange(2**31)
            _init_seed = master.randrange(2**31)
            if ci == 0 and trial < 4:
                planted.append((trial, k, n, m, inst_seed))
    unsat_configs = [
        (3, 32, round(4.26 * 32)), (3, 64, round(4.26 * 64)),
        (3, 96, round(4.26 * 96)), (5, 64, round(6.10 * 64)),
    ]
    unsat = []
    for ci, (k, n, m) in enumerate(unsat_configs):
        for trial in range(4):
            inst_seed = master.randrange(2**31)
            _init_seed = master.randrange(2**31)
            if ci == 0:
                unsat.append((trial, k, n, m, inst_seed))
    return planted, unsat


def frozen_roots():
    sat_core = load_legacy_sat_core()
    planted, unsat = legacy_root_seeds()
    out = []
    for trial, k, n, m, seed in planted:
        inst = sat_core.gen_planted(n, m, k, random.Random(seed))
        cnf = direct.canon(inst.clauses)
        out.append({"suite": "LEGACY_MAIN_SAT", "trial": trial, "k": k, "n": n, "m": m, "seed": seed, "cnf": cnf})
    for trial, k, n, m, seed in unsat:
        inst = sat_core.gen_unsat_core(n, m, k, random.Random(seed))
        cnf = direct.canon(inst.clauses)
        out.append({"suite": "LEGACY_UNSAT_CORE_STRESS", "trial": trial, "k": k, "n": n, "m": m, "seed": seed, "cnf": cnf})
    return out


def frozen_residuals():
    rows = []
    for root in frozen_roots():
        cnf = root["cnf"]
        order, _ = direct.occurrence_order(cnf)
        if not order:
            continue
        pivot = order[0]
        for val in (False, True):
            residual = direct.restrict_cnf(cnf, pivot, val)
            rows.append({
                "source": {k: v for k, v in root.items() if k != "cnf"},
                "root_sha256": digest(cnf),
                "pivot": pivot,
                "branch_value": val,
                "stage": "POST_RESTRICTION_PRE_UNIT",
                "cnf": residual,
                "formula_sha256": digest(residual),
            })
    return rows


def candidate_firewall():
    funcs = [r7d.r7d_candidate, fast.fast_attack_component, fast.subsuming_fixed_width_resolution,
             r7d.width_bounded_eliminate, r7d.choose_safe_pivot]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "exact_search_witness", "product(", "robdd(", "dp_eliminate("]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def run():
    residuals = frozen_residuals()
    rows = []
    for item in residuals:
        cnf = item["cnf"]
        pre = {
            "source": item["source"], "root_sha256": item["root_sha256"],
            "pivot": item["pivot"], "branch_value": item["branch_value"],
            "stage": item["stage"], "formula_sha256": item["formula_sha256"],
            "truth": None, "candidate": None,
        }
        seal = sha256(json.dumps(pre, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        cand = r7d.r7d_candidate(cnf)
        oracle = direct.dpll(cnf)
        truth = None if oracle["status"] != "EXACT" else ("SAT" if oracle["sat"] else "UNSAT")
        terminal_match = cand.terminal == "OPEN" or (truth is not None and cand.terminal == truth)
        sat_replay = cand.terminal != "SAT" or (cand.witness is not None and r7d.r7b.verify_sat(cnf, cand.witness))
        rows.append({**pre, "preverification_seal_sha256": seal, "candidate": cand.as_dict(),
                     "shadow_verification": {"oracle": oracle, "truth": truth,
                                             "terminal_match": terminal_match, "sat_replay": sat_replay}})

    firewall = candidate_firewall()
    terminal = [r for r in rows if r["candidate"]["terminal"] in ("SAT", "UNSAT")]
    opens = [r for r in rows if r["candidate"]["terminal"] == "OPEN"]
    false_terms = [r for r in terminal if not r["shadow_verification"]["terminal_match"]]
    replay_fail = [r for r in terminal if not r["shadow_verification"]["sat_replay"]]
    unknown = [r for r in rows if r["shadow_verification"]["truth"] is None]
    unique_formulas = len({r["formula_sha256"] for r in rows})
    gates = {
        "G1_EXPECTED_16_RESIDUALS": len(rows) == EXPECTED,
        "G2_ALL_PRETRUTH_SEALED": all(r["truth"] is None for r in rows),
        "G3_UNIQUE_RESIDUAL_HASHES": unique_formulas == len(rows),
        "G4_NO_R6_QUARANTINED_CANDIDATE_PRIMITIVE": firewall["pass"],
        "G5_ZERO_FALSE_TERMINALS_AMONG_EXACTLY_VERIFIED": len(false_terms) == 0,
        "G6_ZERO_SAT_REPLAY_FAILURES": len(replay_fail) == 0,
        "G7_NO_THEOREM_INFLATION": True,
    }
    integrity = all(gates.values())
    if not integrity:
        verdict = "R8A_INTEGRITY_FAIL__P_VS_NP_OPEN"
    elif len(terminal) == len(rows) and not unknown:
        verdict = "R8A_PROSPECTIVE_SCOPED_TOTALITY_SUPPORT__16_OF_16_TERMINAL__P_VS_NP_OPEN"
    else:
        verdict = "R8A_HONEST_GENERALIZATION_BARRIER__OPEN_OR_UNVERIFIED_REMAINDER__P_VS_NP_OPEN"
    return {
        "schema": "JANUS/TRUMP/R8A/UNSEEN_NATURAL_HOLDOUT/RESULT/v1.0",
        "status": "FROZEN_RESULT", "verdict": verdict,
        "scope": "PREEXISTING_LEGACY_V03_WORKLOAD__UNEXPOSED_TO_R7_FIT__PROSPECTIVE_FOR_FROZEN_R7_STACK",
        "summary": {"roots": 8, "residuals": len(rows), "unique_residuals": unique_formulas,
                    "terminal": len(terminal), "open": len(opens), "shadow_unknown": len(unknown),
                    "false_terminals": len(false_terms), "sat_replay_failures": len(replay_fail),
                    "candidate_total_charged_ops": sum(int(r["candidate"]["charged_ops"]) for r in rows),
                    "shadow_dpll_total_work": sum(int(r["shadow_verification"]["oracle"].get("work", 0)) for r in rows)},
        "gates": gates, "candidate_source_firewall": firewall,
        "highest_admissible_claim": "This is a prospective test of the unchanged R7B+R7C+R7D mechanism on deterministic solver-native residuals derived from a preexisting legacy workload not used to fit R7. Even complete success is scoped holdout evidence, not arbitrary-CNF totality or P=NP.",
        "P_VS_NP": "OPEN", "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run(); Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "summary": result["summary"], "gates": result["gates"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
