from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x

GATE = "JANUS_TRUMP_R49I_BIPOLAR_NONTAUTO_CROSS_UNION_WIDTH5_CORE_HUNT"
EXPECTED_ROOTS = 52
MAX_ORDINAL = 64
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def fhash(f):
    return r47f.formula_hash(canon(f))


def clv(f):
    return tuple(r33.measure(canon(f)))


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def collect_roots():
    center_original, _, center_fixpoint = r47x.load_center_original()
    roots = []
    seen = set()

    center = canon(center_fixpoint)
    roots.append((center, {
        "kind": "CENTER_CONTROL",
        "frontier_ordinal": 0,
        "phase": "CENTER",
        "source_clause": None,
        "replacement_clause": None,
    }))
    seen.add(fhash(center))

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal > MAX_ORDINAL:
            break
        if mutated is None:
            continue
        r47x.validate_exact_3cnf(mutated)
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            continue
        root = canon(reached["formula"])
        rh = fhash(root)
        if rh in seen:
            continue
        seen.add(rh)
        roots.append((root, {
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
        }))

    if len(roots) != EXPECTED_ROOTS:
        raise AssertionError(("R49I_ROOT_CORPUS_DRIFT", len(roots), EXPECTED_ROOTS))
    return roots


def is_tautological_union(lits):
    s = set(lits)
    return any(-x in s for x in s)


def variable_profile(formula, var):
    f = canon(formula)
    pos = [c for c in f if var in c]
    neg = [c for c in f if -var in c]
    retained = []
    for c in pos:
        a = set(c)
        a.discard(var)
        for d in neg:
            b = set(d)
            b.discard(-var)
            u = a | b
            if is_tautological_union(u):
                continue
            retained.append((len(u), tuple(sorted(u, key=lambda x: (abs(x), x < 0)))))
    chi_star = max((w for w, _ in retained), default=0)
    witness = max(retained, default=None, key=lambda x: (x[0], x[1]))
    return {
        "var": int(var),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "bipolar": bool(pos and neg),
        "pure": bool((pos and not neg) or (neg and not pos)),
        "retained_nontautological_pair_count": len(retained),
        "chi_star": int(chi_star),
        "max_width_witness": None if witness is None else list(witness[1]),
    }


def inspect_state(formula, provenance, root_index):
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise AssertionError(("R49I_NON_W4_ROOT", root_index, max_width(f)))
    vars_ = [int(v) for v in r33.variables(f)]
    profiles = [variable_profile(f, v) for v in vars_]
    pure = [p for p in profiles if p["pure"]]
    non_bipolar = [p for p in profiles if not p["bipolar"]]
    safe = [p for p in profiles if p["bipolar"] and p["chi_star"] <= WIDTH_CAP]
    hard = bool(vars_) and not pure and not non_bipolar and all(p["chi_star"] >= 5 for p in profiles)
    return {
        "root_index": int(root_index),
        "root_hash": fhash(f),
        "root_CLV": list(clv(f)),
        "root_max_width": max_width(f),
        "provenance": provenance,
        "variable_count": len(vars_),
        "pure_variables": [int(p["var"]) for p in pure],
        "safe_bipolar_pivots": [int(p["var"]) for p in safe],
        "minimum_chi_star": min((int(p["chi_star"]) for p in profiles if p["bipolar"]), default=None),
        "maximum_chi_star": max((int(p["chi_star"]) for p in profiles if p["bipolar"]), default=None),
        "is_bipolar_nontauto_cross_union_width5_core": hard,
        "profiles": profiles,
        "formula": [list(c) for c in f] if hard else None,
    }


def run():
    roots = collect_roots()
    rows = []
    first_core = None
    for idx, (root, provenance) in enumerate(roots, 1):
        row = inspect_state(root, provenance, idx)
        rows.append(row)
        if row["is_bipolar_nontauto_cross_union_width5_core"] and first_core is None:
            first_core = row

    safe_count = sum(1 for r in rows if r["safe_bipolar_pivots"])
    pure_count = sum(1 for r in rows if r["pure_variables"])
    core_count = sum(1 for r in rows if r["is_bipolar_nontauto_cross_union_width5_core"])
    min_chi_hist = {}
    for r in rows:
        k = str(r["minimum_chi_star"])
        min_chi_hist[k] = min_chi_hist.get(k, 0) + 1

    verdict = (
        "EXPLICIT_REACHABLE_BIPOLAR_NONTAUTO_WIDTH5_CORE_FOUND"
        if first_core is not None
        else "NO_CORE_IN_FROZEN_52_ROOT_CORPUS__FINITE_ONLY"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "corpus": {
            "kind": "R47X_CENTER_PLUS_FIRST64_ONE_SWAP_REACHABLE_FIXPOINTS_DEDUPED",
            "expected_unique_root_count": EXPECTED_ROOTS,
            "actual_unique_root_count": len(rows),
            "every_state_persisted_width_le_4": all(r["root_max_width"] <= WIDTH_CAP for r in rows),
        },
        "metrics": {
            "roots_scanned": len(rows),
            "roots_with_pure_literal": pure_count,
            "roots_with_chi_star_safe_bipolar_pivot": safe_count,
            "explicit_width5_core_count": core_count,
            "minimum_chi_star_histogram": min_chi_hist,
        },
        "first_core": first_core,
        "rows": rows,
        "interpretation": {
            "one_core_refutes_universal_easy_pure_or_chi_star_safe_pivot_existence": first_core is not None,
            "no_core_in_finite_corpus_proves_universal_easy_lane_existence": False,
            "if_core_found_next": "PROFILE_R47J_RUP_WIDTH_DISCHARGE_ON_THIS_EXPLICIT_CORE",
        },
        "firewall": {
            "R49H_LOCAL_SAFE_PIVOT_LEMMA": "UNCHANGED_PROVED_IN_SCOPE",
            "UNIVERSAL_EASY_LANE_EXISTENCE": "REFUTED" if first_core is not None else "NOT_PROVED",
            "PARTIAL_R47J_DIRECT_W4_STEP_COVERAGE": "OPEN",
            "DIRECT_W4_STEP_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    out = run()
    path = Path("artifacts/JANUS_TRUMP_R49I_BIPOLAR_NONTAUTO_CROSS_UNION_WIDTH5_CORE_HUNT_RESULT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "metrics": out["metrics"],
        "first_core": out["first_core"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
