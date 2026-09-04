from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r49m_r49k_obstruction_targeted_r47j_discharge as r49m

GATE = "JANUS_TRUMP_R49O_PLANTED_WIDTH4_MACHINE_DEADCORE_HUNT"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def make_planted(seed: int, n: int, m: int):
    rng = random.Random(seed)
    assignment = {v: bool(rng.getrandbits(1)) for v in range(1, n + 1)}
    clauses = set()
    guard = 0
    while len(clauses) < m:
        guard += 1
        if guard > m * 1000:
            raise AssertionError("R49O_GENERATION_GUARD")
        vs = rng.sample(range(1, n + 1), 4)
        lits = []
        for v in vs:
            lits.append(v if rng.getrandbits(1) else -v)
        if not any((lit > 0) == assignment[abs(lit)] for lit in lits):
            j = rng.randrange(4)
            v = abs(lits[j])
            lits[j] = v if assignment[v] else -v
        clause = tuple(sorted(lits, key=lambda x: (abs(x), x < 0)))
        clauses.add(clause)
    formula = canon(clauses)
    if not r33.eval_formula(formula, assignment):
        raise AssertionError("R49O_PLANTED_WITNESS_FAIL")
    return formula, assignment


def cheap_signature(formula):
    vars_ = tuple(int(v) for v in r33.variables(formula))
    profiles = [r49i.variable_profile(formula, v) for v in vars_]
    if not profiles:
        return None
    if any(int(p["positive_parent_count"]) == 0 or int(p["negative_parent_count"]) == 0 for p in profiles):
        return None
    min_chi = min(int(p["chi_star"]) for p in profiles)
    min_pairs = min(int(p["retained_nontautological_pair_count"]) for p in profiles)
    min_side = min(min(int(p["positive_parent_count"]), int(p["negative_parent_count"])) for p in profiles)
    max_imbalance = max(abs(int(p["positive_parent_count"]) - int(p["negative_parent_count"])) for p in profiles)
    score = (min_chi, min_pairs, min_side, -max_imbalance)
    return {
        "score": score,
        "min_chi_star": min_chi,
        "min_retained_pairs": min_pairs,
        "min_polarity_side": min_side,
        "max_polarity_imbalance": max_imbalance,
        "profiles": profiles,
    }


def is_r33_fixed_core(formula):
    reduced = r33.simplify(formula)
    final = canon(reduced["final_formula"])
    return bool(reduced["terminal"] == "STALLED_STACK_LEAN_CORE" and final == canon(formula)), reduced


def exact_machine_test(formula, profiles):
    ordered = sorted(
        profiles,
        key=lambda p: (
            int(p["chi_star"]),
            int(p["retained_nontautological_pair_count"]),
            min(int(p["positive_parent_count"]), int(p["negative_parent_count"])),
            int(p["var"]),
        ),
    )
    rows = []
    candidates = {}
    for p in ordered:
        var = int(p["var"])
        row, c = r49m.candidate_row(formula, var, p)
        rows.append(row)
        if c is not None:
            candidates[var] = c
        if row.get("width4_safe", False):
            replay = r47j.independent_fixpoint_macro_replay(formula, c)
            if not replay["pass"]:
                raise AssertionError(("R49O_BREAKER_REPLAY_FAIL", var, replay))
            row["R47J_independent_replay_pass"] = True
            return {
                "deadcore": False,
                "breaker": row,
                "rows": rows,
                "all_nonbreakers_independently_replayed": False,
            }

    replay_rows = []
    for p in ordered:
        var = int(p["var"])
        c = candidates.get(var)
        if c is None:
            replay_rows.append({"var": var, "candidate": False, "replay_pass": True})
            continue
        replay = r47j.independent_fixpoint_macro_replay(formula, c)
        if not replay["pass"]:
            raise AssertionError(("R49O_NONBREAKER_REPLAY_FAIL", var, replay))
        replay_rows.append({"var": var, "candidate": True, "replay_pass": True})
    return {
        "deadcore": True,
        "breaker": None,
        "rows": rows,
        "replay_rows": replay_rows,
        "all_nonbreakers_independently_replayed": True,
    }


def run(worker: int, candidate_count: int, exact_finalists: int):
    n = 18
    ranked = []
    for i in range(candidate_count):
        m = 138 + ((worker * 7 + i) % 5) * 8
        seed = 49_000_000 + worker * 100_000 + i
        formula, assignment = make_planted(seed, n, m)
        if tuple(r33.variables(formula)) != tuple(range(1, n + 1)):
            continue
        if max_width(formula) != 4 or any(len(c) != 4 for c in formula):
            continue
        sig = cheap_signature(formula)
        if sig is None or sig["min_chi_star"] < 5 or sig["min_polarity_side"] < 3:
            continue
        ranked.append((sig["score"], seed, m, formula, assignment, sig))
    ranked.sort(key=lambda x: x[0], reverse=True)
    ranked = ranked[: max(20, exact_finalists * 5)]

    normalized = []
    for score, seed, m, formula, assignment, sig in ranked:
        fixed, reduced = is_r33_fixed_core(formula)
        if not fixed:
            continue
        normalized.append((score, seed, m, formula, assignment, sig, reduced))
        if len(normalized) >= exact_finalists:
            break

    broken = []
    for rank, item in enumerate(normalized, 1):
        score, seed, m, formula, assignment, sig, reduced = item
        exact = exact_machine_test(formula, sig["profiles"])
        summary = {
            "rank": rank,
            "seed": seed,
            "n": n,
            "m": m,
            "hash": r49i.fhash(formula),
            "CLV": list(r49i.clv(formula)),
            "cheap_score": list(score),
            "min_chi_star": sig["min_chi_star"],
            "min_retained_pairs": sig["min_retained_pairs"],
            "min_polarity_side": sig["min_polarity_side"],
            "max_polarity_imbalance": sig["max_polarity_imbalance"],
            "R33_fixed_core": True,
            "exact": exact,
        }
        if exact["deadcore"]:
            summary["formula"] = [list(c) for c in formula]
            summary["planted_assignment"] = {str(k): bool(v) for k, v in assignment.items()}
            summary["planted_assignment_verifies"] = bool(r33.eval_formula(formula, assignment))
            return {
                "gate": GATE,
                "verdict": "CURRENT_MACHINE_DEADCORE_FOUND",
                "worker": worker,
                "candidate_count": candidate_count,
                "exact_finalists_requested": exact_finalists,
                "target": summary,
                "broken_finalists": broken,
                "firewall": firewall(found=True),
            }
        broken.append(summary)

    return {
        "gate": GATE,
        "verdict": "NO_DEADCORE_FOUND_IN_THIS_WORKER_BUDGET",
        "worker": worker,
        "candidate_count": candidate_count,
        "exact_finalists_requested": exact_finalists,
        "ranked_candidate_count": len(ranked),
        "R33_fixed_finalist_count": len(normalized),
        "target": None,
        "broken_finalists": broken,
        "firewall": firewall(found=False),
    }


def firewall(found: bool):
    return {
        "CURRENT_MACHINE_DEADCORE": "EXPLICIT_FINITE_WITNESS" if found else "NOT_FOUND_IN_BUDGET",
        "MACHINE_SCOPE": "R33_FIXED_CORE + CHI_STAR_LE4_EASY_LANE + PARTIAL_R47J_WIDTH4_SUCCESSOR",
        "UNBREAKABLE_BY_ALL_POSSIBLE_ALGORITHMS": "NOT_CLAIMED",
        "SAT_WITNESS_IF_FOUND": "PLANTED_AND_DIRECTLY_VERIFIED" if found else "N/A",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int, required=True)
    ap.add_argument("--candidate-count", type=int, default=300)
    ap.add_argument("--exact-finalists", type=int, default=3)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = run(a.worker, a.candidate_count, a.exact_finalists)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "worker": out["worker"],
        "target": None if out["target"] is None else {
            "seed": out["target"]["seed"],
            "hash": out["target"]["hash"],
            "CLV": out["target"]["CLV"],
            "min_chi_star": out["target"]["min_chi_star"],
        },
        "broken_finalists": len(out["broken_finalists"]),
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
