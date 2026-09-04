from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a

GATE = "JANUS_TRUMP_R50G_DUAL_UNIVERSAL_W4_STEP_PROOF_AND_SMALLEST_FIRST_EXACT_DEADCORE_FALSIFIER"
WIDTH_CAP = 4
MIN_DEADCORE_VARIABLES = 6


def canon(formula):
    return r33.canonical_formula(formula)


def max_width(formula):
    return max((len(c) for c in canon(formula)), default=0)


def clv(formula):
    return tuple(r33.measure(canon(formula)))


def fhash(formula):
    return r49i.fhash(canon(formula))


def false_witness(n):
    return {v: False for v in range(1, n + 1)}


def make_planted(seed: int, n: int, m: int, profile: str):
    """Deterministic discovery generator; never a theorem oracle.

    The all-false assignment is the planted SAT witness.  Every generated clause
    is forced to contain at least one negative literal.  Profiles deliberately
    include mixed widths so R49O's exact-width4 restriction is not inherited.
    """
    rng = random.Random(seed)
    witness = false_witness(n)
    clauses = set()
    guard = 0
    while len(clauses) < m:
        guard += 1
        if guard > max(10000, m * 2000):
            raise AssertionError(("R50G_GENERATION_GUARD", seed, n, m, profile))
        i = len(clauses) + guard
        if profile == "3CNF":
            width = 3
        elif profile == "W34":
            width = 3 if i % 3 == 0 else 4
        elif profile == "W234":
            width = 2 if i % 11 == 0 else (3 if i % 3 == 0 else 4)
        elif profile == "W4_CONTROL":
            width = 4
        else:
            raise ValueError(profile)
        width = min(width, n)
        vs = rng.sample(range(1, n + 1), width)
        lits = [v if rng.getrandbits(1) else -v for v in vs]
        if all(l > 0 for l in lits):
            j = rng.randrange(width)
            lits[j] = -abs(lits[j])
        clause = tuple(sorted(lits, key=lambda x: (abs(x), x < 0)))
        clauses.add(clause)
    formula = canon(clauses)
    if not r33.eval_formula(formula, witness):
        raise AssertionError("R50G_PLANTED_WITNESS_FAIL")
    return formula, witness


def bad_pair_shape_lemma(profile_formula, var):
    """Mechanical replay of the strengthened local W4 parent-shape lemma."""
    f = canon(profile_formula)
    pos = [c for c in f if var in c]
    neg = [c for c in f if -var in c]
    wide_pairs = []
    for p in pos:
        a = set(p) - {var}
        for q in neg:
            b = set(q) - {-var}
            u = a | b
            if r49i.is_tautological_union(u) or len(u) <= 4:
                continue
            row = {
                "positive_width": len(p),
                "negative_width": len(q),
                "resolvent_width": len(u),
            }
            if len(p) < 4 and len(q) < 4:
                raise AssertionError(("R50G_WIDE_PAIR_WITHOUT_WIDTH4_PARENT", var, p, q, u))
            if len(u) == 6 and not (len(p) == 4 and len(q) == 4):
                raise AssertionError(("R50G_WIDTH6_WITHOUT_4X4", var, p, q, u))
            wide_pairs.append(row)
    return wide_pairs


def exact_hard_state_test(formula):
    """Exact all-pivot test for the frozen current machine.

    Unlike R49O, no hostile score orders pivots and every nonbreaker candidate is
    independently replayed.  A deadcore verdict is allowed only after the frozen
    R50A controller independently agrees that all current variables were checked.
    """
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        return {"applicable": False, "reason": "WIDTH_GT_4"}
    reduced = r33.simplify(f)
    reduced_final = canon(reduced["final_formula"])
    if reduced["terminal"] != "STALLED_STACK_LEAN_CORE" or reduced_final != f:
        return {
            "applicable": False,
            "reason": "R33_NOT_LITERAL_FIXED_POINT",
            "R33_terminal": reduced["terminal"],
            "R33_final_CLV": list(clv(reduced_final)),
        }

    vars_ = tuple(int(v) for v in r33.variables(f))
    if len(vars_) < MIN_DEADCORE_VARIABLES:
        return {"applicable": False, "reason": "V_LT_6_THEOREM_EXCLUDES_DEADCORE"}
    profiles = [r49i.variable_profile(f, v) for v in vars_]
    if any(not p["bipolar"] for p in profiles):
        return {"applicable": False, "reason": "NON_BIPOLAR_AT_R33_FIXED_POINT", "profiles": profiles}
    direct = [p for p in profiles if int(p["chi_star"]) <= WIDTH_CAP]
    if direct:
        return {
            "applicable": False,
            "reason": "R49H_DIRECT_PIVOT_EXISTS",
            "direct_pivots": [int(p["var"]) for p in direct],
            "profiles": profiles,
        }

    rows = []
    breaker = None
    before_vars = set(vars_)
    for p in sorted(profiles, key=lambda x: int(x["var"])):
        v = int(p["var"])
        wide_shapes = bad_pair_shape_lemma(f, v)
        if not wide_shapes:
            raise AssertionError(("R50G_NO_WIDE_PAIR_DESPITE_CHI_GE5", v, p))
        candidate = r47j.macro_candidate_fixpoint(f, v)
        if candidate is None:
            raise AssertionError(("R50G_BIPOLAR_PIVOT_WITHOUT_R47J_CANDIDATE", v))
        replay = r47j.independent_fixpoint_macro_replay(f, candidate)
        if not replay["pass"]:
            raise AssertionError(("R50G_R47J_REPLAY_FAIL", v, replay))
        final = canon(candidate["normalization"]["final_formula"])
        after_vars = set(r33.variables(final))
        terminal = candidate["normalization"]["terminal"]
        no_fresh = after_vars <= before_vars
        strict_v = len(after_vars) < len(before_vars)
        final_w = max_width(final)
        safe = bool(terminal is not None or (no_fresh and strict_v and final_w <= WIDTH_CAP))
        row = {
            "var": v,
            "chi_star": int(p["chi_star"]),
            "positive_parent_count": int(p["positive_parent_count"]),
            "negative_parent_count": int(p["negative_parent_count"]),
            "wide_parent_pair_count": len(wide_shapes),
            "terminal": terminal,
            "final_hash": fhash(final),
            "final_CLV": list(clv(final)),
            "final_max_width": final_w,
            "no_fresh_variables": no_fresh,
            "strict_variable_descent": strict_v,
            "width4_safe": safe,
            "independent_replay_pass": True,
        }
        rows.append(row)
        if safe and breaker is None:
            breaker = row

    if breaker is not None:
        return {
            "applicable": True,
            "deadcore": False,
            "breaker": breaker,
            "rows": rows,
            "profiles": profiles,
        }

    controller = r50a.exact_step(f)
    if not (
        controller["kind"] == "OPEN_OBSTRUCTION"
        and controller.get("all_current_variables_checked") is True
    ):
        raise AssertionError(("R50G_ALL_PIVOTS_UNSAFE_BUT_CONTROLLER_NOT_OPEN", controller))
    if any(r["final_max_width"] <= WIDTH_CAP for r in rows):
        raise AssertionError("R50G_DEADCORE_WITH_NONWIDE_NONTERMINAL_ROW")
    return {
        "applicable": True,
        "deadcore": True,
        "breaker": None,
        "rows": rows,
        "profiles": profiles,
        "controller_open": {
            "lane": controller["lane"],
            "input_hash": controller["input_hash"],
            "all_current_variables_checked": controller["all_current_variables_checked"],
        },
    }


def projected_witness(formula, original_witness):
    a = {v: bool(original_witness[v]) for v in r33.variables(formula) if v in original_witness}
    return a if r33.eval_formula(canon(formula), a) else None


def trace_reachable_root(root, witness, provenance):
    state = canon(root)
    seen = set()
    trace = []
    max_steps = 3 * max(1, len(r33.variables(state))) + 8
    for step_index in range(max_steps):
        h = fhash(state)
        if h in seen:
            raise AssertionError(("R50G_REACHABLE_TRACE_CYCLE", h))
        seen.add(h)
        if max_width(state) > WIDTH_CAP:
            raise AssertionError(("R50G_TRACE_LEFT_W4", max_width(state)))
        step = r50a.exact_step(state)
        trace.append({
            "step": step_index,
            "state_hash": h,
            "state_CLV": list(clv(state)),
            "kind": step["kind"],
            "lane": step["lane"],
        })
        if step["kind"] == "TERMINAL":
            return {"deadcore": None, "trace": trace, "terminal": step.get("terminal"), "provenance": provenance}
        if step["kind"] == "OPEN_OBSTRUCTION":
            exact = exact_hard_state_test(state)
            if not exact.get("deadcore"):
                raise AssertionError(("R50G_CONTROLLER_OPEN_NOT_EXACT_DEADCORE", exact))
            sat_witness = projected_witness(state, witness)
            if sat_witness is None:
                # Falsifier-only exponential witness recovery is allowed only as
                # verification scaffolding and carries zero theorem authority.
                sat_witness = r33.brute_force_model(state)
            if sat_witness is None or not r33.eval_formula(state, sat_witness):
                raise AssertionError("R50G_REACHABLE_DEADCORE_NOT_SAT")
            return {
                "deadcore": {
                    "kind": "REACHABLE_FROM_PLANTED_3CNF_UNDER_FROZEN_R50A",
                    "formula": [list(c) for c in state],
                    "hash": h,
                    "CLV": list(clv(state)),
                    "max_width": max_width(state),
                    "SAT_witness": {str(k): bool(v) for k, v in sat_witness.items()},
                    "SAT_witness_directly_verifies": True,
                    "exact_machine_test": exact,
                    "provenance": provenance,
                    "trace": trace,
                },
                "trace": trace,
                "terminal": None,
                "provenance": provenance,
            }
        successor = canon(step["successor"])
        # The planted witness should normally project through exact existential
        # eliminations and implication-preserving reductions.  We do not use this
        # as transition authority; it is only a cheap SAT witness sanity check.
        state = successor
    raise AssertionError(("R50G_TRACE_BOUND_EXHAUSTED", provenance, trace[-1] if trace else None))


def direct_w4_candidate(formula, witness, provenance):
    exact = exact_hard_state_test(formula)
    if not exact.get("deadcore"):
        return None
    if not r33.eval_formula(formula, witness):
        raise AssertionError("R50G_DIRECT_W4_WITNESS_FAIL")
    return {
        "kind": "GENERATED_ALL_W4__REACHABILITY_NOT_ESTABLISHED",
        "formula": [list(c) for c in canon(formula)],
        "hash": fhash(formula),
        "CLV": list(clv(formula)),
        "max_width": max_width(formula),
        "SAT_witness": {str(k): bool(v) for k, v in witness.items()},
        "SAT_witness_directly_verifies": True,
        "exact_machine_test": exact,
        "provenance": provenance,
    }


def candidate_key(target):
    C, L, V = target["CLV"]
    return (V, C, L, target["hash"])


def run_worker(worker: int, roots_per_worker: int, w4_candidates_per_worker: int):
    n = MIN_DEADCORE_VARIABLES + int(worker)
    if n > 10:
        raise ValueError("R50G_WORKER_N_GT_10_NOT_IN_FROZEN_FIRST_BUDGET")
    reachable_targets = []
    trace_rows = []
    for i in range(roots_per_worker):
        m = 3 * n + (i % (3 * n + 1))
        seed = 50_700_000 + worker * 100_000 + i
        root, witness = make_planted(seed, n, m, "3CNF")
        if len(r33.variables(root)) != n:
            continue
        result = trace_reachable_root(root, witness, {
            "source": "PLANTED_3CNF",
            "worker": worker,
            "seed": seed,
            "n": n,
            "m": m,
            "root_hash": fhash(root),
        })
        trace_rows.append({
            "seed": seed,
            "root_hash": fhash(root),
            "root_CLV": list(clv(root)),
            "trace_length": len(result["trace"]),
            "terminal": result["terminal"],
            "deadcore_found": result["deadcore"] is not None,
        })
        if result["deadcore"] is not None:
            reachable_targets.append(result["deadcore"])

    direct_targets = []
    hard_finalists_tested = 0
    generated_hard = []
    profiles = ("W34", "W234", "W4_CONTROL")
    for i in range(w4_candidates_per_worker):
        profile = profiles[i % len(profiles)]
        m = 3 * n + (i % (4 * n + 1))
        seed = 50_800_000 + worker * 100_000 + i
        formula, witness = make_planted(seed, n, m, profile)
        if len(r33.variables(formula)) != n:
            continue
        reduced = r33.simplify(formula)
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE" or canon(reduced["final_formula"]) != formula:
            continue
        ps = [r49i.variable_profile(formula, int(v)) for v in r33.variables(formula)]
        if not ps or any(not p["bipolar"] for p in ps) or any(int(p["chi_star"]) <= WIDTH_CAP for p in ps):
            continue
        generated_hard.append((candidate_key({"CLV": list(clv(formula)), "hash": fhash(formula)}), formula, witness, {
            "source": "PLANTED_W4_GENERATED_POOL",
            "profile": profile,
            "worker": worker,
            "seed": seed,
            "n": n,
            "m": m,
        }))

    generated_hard.sort(key=lambda row: row[0])
    for _, formula, witness, provenance in generated_hard[:8]:
        hard_finalists_tested += 1
        target = direct_w4_candidate(formula, witness, provenance)
        if target is not None:
            direct_targets.append(target)

    reachable_targets.sort(key=candidate_key)
    direct_targets.sort(key=candidate_key)
    return {
        "gate": GATE,
        "mode": "WORKER",
        "worker": worker,
        "n": n,
        "budget": {
            "reachable_3cnf_roots_requested": roots_per_worker,
            "direct_w4_candidates_requested": w4_candidates_per_worker,
            "direct_hard_finalists_exactly_tested": hard_finalists_tested,
        },
        "reachable_trace_rows": trace_rows,
        "reachable_deadcores": reachable_targets,
        "all_w4_deadcores_reachability_open": direct_targets,
        "verdict": (
            "REACHABLE_CURRENT_MACHINE_DEADCORE_FOUND"
            if reachable_targets
            else "ALL_W4_DEADCORE_FOUND__REACHABILITY_OPEN"
            if direct_targets
            else "NO_DEADCORE_FOUND_IN_GENERATED_WORKER_BUDGET"
        ),
        "firewall": firewall(bool(reachable_targets), bool(direct_targets)),
    }


def firewall(reachable_found: bool, allw4_found: bool):
    return {
        "U_FOR_FROZEN_REACHABLE_MACHINE": "REFUTED_BY_EXPLICIT_REACHABLE_WITNESS" if reachable_found else "OPEN",
        "STRONGER_ALL_W4_STEP_COVERAGE": "REFUTED_BY_EXPLICIT_WITNESS" if (reachable_found or allw4_found) else "OPEN",
        "NO_DEADCORE_FOUND_IMPLIES_U": False,
        "GENERATED_POOL_SMALLEST_IS_GLOBAL_MINIMUM": False,
        "FINITE_SEARCH_PROVES_P_EQUALS_NP": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def synthesize(directory: Path):
    rows = []
    for path in sorted(directory.rglob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("gate") == GATE and d.get("mode") == "WORKER":
            rows.append(d)
    if not rows:
        raise AssertionError("R50G_NO_WORKER_RESULTS")
    reachable = [x for d in rows for x in d.get("reachable_deadcores", [])]
    allw4 = [x for d in rows for x in d.get("all_w4_deadcores_reachability_open", [])]
    reachable.sort(key=candidate_key)
    allw4.sort(key=candidate_key)
    if reachable:
        verdict = "EXPLICIT_REACHABLE_CURRENT_MACHINE_DEADCORE_FOUND__U_REFUTED_FOR_FROZEN_MACHINE"
    elif allw4:
        verdict = "EXPLICIT_ALL_W4_DEADCORE_FOUND__REACHABILITY_TO_U_DOMAIN_OPEN"
    else:
        verdict = "NO_DEADCORE_FOUND_IN_GENERATED_FIRST_BUDGET__U_REMAINS_OPEN"
    return {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "verdict": verdict,
        "workers": len(rows),
        "n_values": sorted({int(d["n"]) for d in rows}),
        "reachable_root_traces": sum(len(d.get("reachable_trace_rows", [])) for d in rows),
        "reachable_deadcore_count": len(reachable),
        "all_w4_deadcore_count_reachability_open": len(allw4),
        "smallest_generated_reachable_deadcore": reachable[0] if reachable else None,
        "smallest_generated_all_w4_deadcore": allw4[0] if allw4 else None,
        "symbolic_lemmas": {
            "W4_BAD_PAIR_REQUIRES_WIDTH4_PARENT": "PROVED_IN_R50G_NOTE_AND_MECHANICALLY_REPLAYED_ON_EXACT_FINALISTS",
            "WIDTH6_REQUIRES_WIDTH4_X_WIDTH4": "PROVED_IN_R50G_NOTE_AND_MECHANICALLY_REPLAYED_ON_EXACT_FINALISTS",
            "NO_W4_DEADCORE_WITH_V_LE_5": "PROVED_LOCAL_COMBINATORICS",
            "U": "OPEN" if not reachable else "REFUTED_FOR_FROZEN_REACHABLE_MACHINE",
        },
        "firewall": firewall(bool(reachable), bool(allw4)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int)
    ap.add_argument("--roots-per-worker", type=int, default=80)
    ap.add_argument("--w4-candidates-per-worker", type=int, default=240)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--synthesize-dir", type=Path)
    a = ap.parse_args()
    if a.synthesize_dir is not None:
        out = synthesize(a.synthesize_dir)
        output = a.output or Path("artifacts/JANUS_TRUMP_R50G_DUAL_SYNTHESIS.json")
    else:
        if a.worker is None or a.output is None:
            ap.error("worker and output are required outside synthesis mode")
        out = run_worker(a.worker, a.roots_per_worker, a.w4_candidates_per_worker)
        output = a.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "mode": out["mode"],
        "verdict": out["verdict"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
