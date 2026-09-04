from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50b_minimal_deadcore_structural_classification as r50b
import janus_trump_r50c_top2_min_taut_prospective_falsifier as r50c

GATE = "JANUS_TRUMP_R50E_SHORT_PARENT_BAD_SECTOR_TRANSFER_LEMMA"
WIDTH_CAP = 4
EXPECTED_ROOTS = 52
EXPECTED_HARD_STATES = 441
EXPECTED_RESCUES = 12

CANDIDATES = (
    "LONG_LONG_CAPACITY_NONINCREASE",
    "BAD_PAIR_COUNT_NONINCREASE",
    "UNIQUE_BAD_RESOLVENT_COUNT_NONINCREASE",
    "WIDTH6_BAD_COUNT_NONINCREASE",
    "BAD_LONG_LONG_DENSITY_NONINCREASE",
    "FORCED_WIDE_CLAUSE_COUNT_NONINCREASE",
)


class IntegrityFailure(RuntimeError):
    pass


def canon(formula):
    return r33.canonical_formula(formula)


def fhash(formula):
    return r49i.fhash(canon(formula))


def max_width(formula):
    f = canon(formula)
    return 0 if not f else max(len(c) for c in f)


def clause_key(lits):
    return tuple(sorted({int(x) for x in lits}, key=lambda x: (abs(x), x)))


def residual_pair_record(pos_clause, neg_clause, var):
    var = int(var)
    a = {int(x) for x in pos_clause if int(x) != var}
    b = {int(x) for x in neg_clause if int(x) != -var}
    tautological = any(-lit in b for lit in a)
    union = a | b
    return {
        "positive_parent_width": len(pos_clause),
        "negative_parent_width": len(neg_clause),
        "positive_residual_size": len(a),
        "negative_residual_size": len(b),
        "tautological": bool(tautological),
        "resolvent_width": len(union),
        "resolvent": clause_key(union),
        "long_long": len(pos_clause) >= 3 and len(neg_clause) >= 3,
    }


def independent_pair_records(formula, var):
    f = canon(formula)
    var = int(var)
    if max_width(f) > WIDTH_CAP:
        raise IntegrityFailure(("R50E_NON_W4_INPUT", fhash(f), max_width(f)))
    pos = [c for c in f if var in c]
    neg = [c for c in f if -var in c]
    rows = [residual_pair_record(pc, nc, var) for pc in pos for nc in neg]
    return pos, neg, rows


def short_parent_theorem_kernel():
    rows = []
    for pw in range(1, WIDTH_CAP + 1):
        for nw in range(1, WIDTH_CAP + 1):
            max_union = (pw - 1) + (nw - 1)
            if pw <= 2 or nw <= 2:
                if max_union > WIDTH_CAP:
                    raise IntegrityFailure(("R50E_ARITHMETIC_KERNEL_FAIL", pw, nw, max_union))
            width6_possible = max_union >= 6
            if width6_possible and not (pw == 4 and nw == 4):
                raise IntegrityFailure(("R50E_WIDTH6_KERNEL_FAIL", pw, nw, max_union))
            rows.append({
                "positive_parent_width": pw,
                "negative_parent_width": nw,
                "max_union_without_overlap": max_union,
                "short_incident_is_width4_safe": bool(pw <= 2 or nw <= 2),
                "width6_possible_without_overlap": bool(width6_possible),
            })
    return rows


def sector_profile(formula, var):
    f = canon(formula)
    pos, neg, rows = independent_pair_records(f, var)
    retained = [r for r in rows if not r["tautological"]]
    bad = [r for r in retained if r["resolvent_width"] > WIDTH_CAP]
    long_long = [r for r in rows if r["long_long"]]
    retained_long_long = [r for r in retained if r["long_long"]]

    for r in bad:
        if not r["long_long"]:
            raise IntegrityFailure(("R50E_SHORT_PARENT_BAD_PAIR", fhash(f), int(var), r))
        if r["positive_parent_width"] <= 2 or r["negative_parent_width"] <= 2:
            raise IntegrityFailure(("R50E_BAD_PAIR_HAS_SHORT_PARENT", fhash(f), int(var), r))
        if r["resolvent_width"] == 6 and not (
            r["positive_parent_width"] == 4 and r["negative_parent_width"] == 4
        ):
            raise IntegrityFailure(("R50E_WIDTH6_NOT_4X4", fhash(f), int(var), r))

    unique_bad = {r["resolvent"] for r in bad}
    pos_long = sum(1 for c in pos if len(c) >= 3)
    neg_long = sum(1 for c in neg if len(c) >= 3)
    pos_short2 = sum(1 for c in pos if len(c) == 2)
    neg_short2 = sum(1 for c in neg if len(c) == 2)
    retained_long_count = len(retained_long_long)
    bad_density = Fraction(len(bad), retained_long_count) if retained_long_count else Fraction(0, 1)

    return {
        "var": int(var),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "positive_width2_parent_count": pos_short2,
        "negative_width2_parent_count": neg_short2,
        "positive_long_parent_count": pos_long,
        "negative_long_parent_count": neg_long,
        "cross_pair_count": len(rows),
        "tautological_cross_pair_count": sum(1 for r in rows if r["tautological"]),
        "retained_cross_pair_count": len(retained),
        "short_incident_cross_pair_count": sum(1 for r in rows if not r["long_long"]),
        "long_long_capacity": len(long_long),
        "retained_long_long_pair_count": retained_long_count,
        "bad_pair_count": len(bad),
        "unique_bad_resolvent_count": len(unique_bad),
        "width5_bad_pair_count": sum(1 for r in bad if r["resolvent_width"] == 5),
        "width6_bad_pair_count": sum(1 for r in bad if r["resolvent_width"] == 6),
        "bad_long_long_density": [bad_density.numerator, bad_density.denominator],
        "unique_bad_resolvents": [list(c) for c in sorted(unique_bad)],
        "theorem_bad_subset_long_long_pass": True,
    }


def exact_transform_trace(formula, var, sector):
    f = canon(formula)
    candidate = r47j.macro_candidate_fixpoint(f, int(var))
    if candidate is None:
        raise IntegrityFailure(("R50E_R47J_CANDIDATE_MISSING", fhash(f), int(var)))
    replay = r47j.independent_fixpoint_macro_replay(f, candidate)
    if not replay["pass"]:
        raise IntegrityFailure(("R50E_R47J_REPLAY_FAIL", fhash(f), int(var), replay))

    forced = canon(candidate["DP"]["transformed"])
    final_formula = canon(candidate["normalization"]["final_formula"])
    forced_wide = {clause_key(c) for c in forced if len(c) > WIDTH_CAP}
    allowed_wide = {tuple(c) for c in sector["unique_bad_resolvents"]}
    unexpected = forced_wide - allowed_wide
    if unexpected:
        raise IntegrityFailure(("R50E_WIDE_DP_CLAUSE_NOT_FROM_BAD_LONG_LONG", fhash(f), int(var), sorted(unexpected)))

    final_wide = [c for c in final_formula if len(c) > WIDTH_CAP]
    terminal = candidate["normalization"]["terminal"] is not None
    no_fresh = set(r33.variables(final_formula)).issubset(set(r33.variables(f)))
    strict_var_descent = len(r33.variables(final_formula)) < len(r33.variables(f))
    width4_safe = bool(terminal or (no_fresh and strict_var_descent and max_width(final_formula) <= WIDTH_CAP))

    if not forced_wide:
        clearance = "CLEAR_AT_EXACT_DP_CANONICALIZATION"
    elif not final_wide:
        clearance = "CLEAR_BY_R33_RUP_NORMALIZATION"
    else:
        clearance = "WIDE_SURVIVES_NORMALIZATION"

    return {
        "var": int(var),
        "forced_DP_max_width": max_width(forced),
        "forced_wide_clause_count": len(forced_wide),
        "forced_wide_clauses": [list(c) for c in sorted(forced_wide)],
        "all_forced_wide_traceable_to_bad_long_long": True,
        "normalization_final_max_width": max_width(final_formula),
        "normalization_final_wide_clause_count": len(final_wide),
        "normalization_round_count": int(candidate["normalization"]["round_count"]),
        "normalization_restart_count": int(candidate["normalization"]["restart_count"]),
        "normalization_terminal": candidate["normalization"]["terminal"],
        "clearance_class": clearance,
        "strict_variable_descent": bool(strict_var_descent),
        "no_fresh_variables": bool(no_fresh),
        "width4_safe": bool(width4_safe),
        "independent_replay_pass": True,
    }


def frac_value(pair):
    return Fraction(int(pair[0]), int(pair[1]))


def candidate_holds(name, p1, p2, t1, t2):
    if name == "LONG_LONG_CAPACITY_NONINCREASE":
        return p2["long_long_capacity"] <= p1["long_long_capacity"]
    if name == "BAD_PAIR_COUNT_NONINCREASE":
        return p2["bad_pair_count"] <= p1["bad_pair_count"]
    if name == "UNIQUE_BAD_RESOLVENT_COUNT_NONINCREASE":
        return p2["unique_bad_resolvent_count"] <= p1["unique_bad_resolvent_count"]
    if name == "WIDTH6_BAD_COUNT_NONINCREASE":
        return p2["width6_bad_pair_count"] <= p1["width6_bad_pair_count"]
    if name == "BAD_LONG_LONG_DENSITY_NONINCREASE":
        return frac_value(p2["bad_long_long_density"]) <= frac_value(p1["bad_long_long_density"])
    if name == "FORCED_WIDE_CLAUSE_COUNT_NONINCREASE":
        return t2["forced_wide_clause_count"] <= t1["forced_wide_clause_count"]
    raise ValueError(name)


def rescue_record(formula, probe, root_index, step_index, provenance):
    if probe.get("first_safe_rank") != 2:
        raise IntegrityFailure(("R50E_NOT_RANK2_RESCUE", probe.get("state_hash"), probe.get("first_safe_rank")))
    selected = probe["selected_rows"]
    if len(selected) != 2:
        raise IntegrityFailure(("R50E_TOP2_SIZE", probe["state_hash"], len(selected)))
    v1, v2 = int(selected[0]["var"]), int(selected[1]["var"])
    s1, s2 = sector_profile(formula, v1), sector_profile(formula, v2)
    t1, t2 = exact_transform_trace(formula, v1, s1), exact_transform_trace(formula, v2, s2)

    if t1["width4_safe"]:
        raise IntegrityFailure(("R50E_RANK1_SHOULD_FAIL", probe["state_hash"], v1))
    if not t2["width4_safe"]:
        raise IntegrityFailure(("R50E_RANK2_SHOULD_RESCUE", probe["state_hash"], v2))

    frozen = {name: bool(candidate_holds(name, s1, s2, t1, t2)) for name in CANDIDATES}
    return {
        "state_hash": probe["state_hash"],
        "state_CLV": probe["state_CLV"],
        "root_index": int(root_index),
        "trace_step": int(step_index),
        "root_provenance": provenance,
        "rank1": {"var": v1, "sector": s1, "transform": t1},
        "rank2": {"var": v2, "sector": s2, "transform": t2},
        "frozen_transfer_candidates": frozen,
    }


def trace_root(root, provenance, root_index):
    root = canon(root)
    root_vars = set(r33.variables(root))
    current = root
    seen = set()
    cap = 2 * max(1, len(root_vars)) + 8
    hard_states = 0
    rescues = []

    for step_index in range(cap):
        h = fhash(current)
        if h in seen:
            raise IntegrityFailure(("R50E_TRACE_CYCLE", root_index, h))
        seen.add(h)
        if max_width(current) > WIDTH_CAP:
            raise IntegrityFailure(("R50E_TRACE_WIDTH_DRIFT", root_index, max_width(current)))
        if not set(r33.variables(current)).issubset(root_vars):
            raise IntegrityFailure(("R50E_TRACE_FRESH_VARIABLE", root_index, h))

        probe = r50c.hard_state_probe(current)
        if probe["applicable"]:
            hard_states += 1
            # Audit the theorem on both frozen top-2 pivots for every hard state.
            for row in probe["selected_rows"]:
                sector_profile(current, int(row["var"]))
            if probe["first_safe_rank"] == 2:
                rescues.append(rescue_record(current, probe, root_index, step_index, provenance))
            elif probe["first_safe_rank"] != 1:
                raise IntegrityFailure(("R50E_TOP2_REGRESSION", root_index, h, probe["first_safe_rank"]))

        step = r50a.exact_step(current)
        if step["kind"] == "OPEN_OBSTRUCTION":
            raise IntegrityFailure(("R50E_R50A_OPEN_REGRESSION", root_index, h))
        if step["kind"] == "TERMINAL":
            return {
                "root_index": int(root_index),
                "root_hash": fhash(root),
                "provenance": provenance,
                "hard_state_count": int(hard_states),
                "rescue_count": len(rescues),
                "rescues": rescues,
            }
        current = canon(step["successor"])

    raise IntegrityFailure(("R50E_TRACE_STEP_CAP", root_index, cap, fhash(current)))


def firewall():
    return {
        "HEURISTIC_PROOF_AUTHORITY": False,
        "ML_PROOF_AUTHORITY": False,
        "RANDOM_PROOF_AUTHORITY": False,
        "SHORT_PARENT_BAD_SECTOR_CONTAINMENT_IMPLIES_TOP2_TRANSFER": False,
        "R50E_FINITE_12_PROVES_TRANSFER_LEMMA": False,
        "TOP2_UNIVERSAL_COVERAGE": "OPEN",
        "UNIVERSAL_R50A_PROGRESS": "OPEN",
        "UNIVERSAL_W4_COVERAGE": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def run_shard(shard_index=0, shard_count=4):
    short_parent_theorem_kernel()
    roots = r50c.collect_prospective_roots()
    if len(roots) != EXPECTED_ROOTS:
        raise IntegrityFailure(("R50E_ROOT_CORPUS_DRIFT", len(roots), EXPECTED_ROOTS))
    assigned = [
        (idx, root, provenance)
        for idx, (root, provenance) in enumerate(roots, 1)
        if (idx - 1) % int(shard_count) == int(shard_index)
    ]
    records = [trace_root(root, provenance, idx) for idx, root, provenance in assigned]
    rescues = [x for r in records for x in r["rescues"]]
    return {
        "gate": GATE,
        "mode": "SHARD",
        "parent_R50D_commit": "1a016d27824056bd00548010115307aa6ae6c288",
        "source_R50D_run_id": 33915068692,
        "shard": {"index": int(shard_index), "count": int(shard_count)},
        "kernel": {
            "short_parent_bad_sector_containment": "PROVED_BY_SIZE_BOUND_AND_AUDITED",
            "width6_only_4x4": "PROVED_BY_SIZE_BOUND_AND_AUDITED",
        },
        "metrics": {
            "assigned_roots": len(assigned),
            "hard_states": sum(r["hard_state_count"] for r in records),
            "rank2_rescues": len(rescues),
        },
        "roots": records,
        "firewall": firewall(),
    }


def synthesize(directory):
    directory = Path(directory)
    paths = sorted(directory.glob("JANUS_TRUMP_R50E_*_SHARD_*_OF_4.json"))
    if len(paths) != 4:
        raise IntegrityFailure(("R50E_EXPECTED_4_SHARDS", len(paths), [p.name for p in paths]))
    shards = [json.loads(p.read_text()) for p in paths]
    roots = [r for s in shards for r in s["roots"]]
    rescues = [x for r in roots for x in r["rescues"]]
    hard_states = sum(int(r["hard_state_count"]) for r in roots)
    if len(roots) != EXPECTED_ROOTS or hard_states != EXPECTED_HARD_STATES or len(rescues) != EXPECTED_RESCUES:
        raise IntegrityFailure(("R50E_REPRODUCTION_DRIFT", len(roots), hard_states, len(rescues)))

    supports = {name: sum(int(r["frozen_transfer_candidates"][name]) for r in rescues) for name in CANDIDATES}
    clearance_rank1 = {}
    clearance_rank2 = {}
    for r in rescues:
        c1 = r["rank1"]["transform"]["clearance_class"]
        c2 = r["rank2"]["transform"]["clearance_class"]
        clearance_rank1[c1] = clearance_rank1.get(c1, 0) + 1
        clearance_rank2[c2] = clearance_rank2.get(c2, 0) + 1

    out = {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "verdict": "SHORT_PARENT_BAD_SECTOR_THEOREM_PROVED__TRANSFER_CANDIDATES_FINITE_ONLY",
        "theorem": {
            "name": "SHORT_PARENT_BAD_SECTOR_CONTAINMENT",
            "statement": "BAD(v) subseteq P_ge3(v) x N_ge3(v) for W4 exact DP cross resolvents",
            "status": "PROVED",
            "scope": "MAX_PARENT_WIDTH_LE_4",
            "universal_top2_transfer_implied": False,
        },
        "metrics": {
            "roots": len(roots),
            "hard_states": hard_states,
            "rank2_rescues": len(rescues),
            "candidate_support": supports,
            "rank1_clearance_histogram": clearance_rank1,
            "rank2_clearance_histogram": clearance_rank2,
        },
        "frozen_transfer_candidates": [
            {
                "name": name,
                "support": supports[name],
                "total": len(rescues),
                "status": "FINITE_12_OF_12_SUPPORT__THEOREM_OPEN" if supports[name] == len(rescues) else "FALSIFIED_ON_R50C_RESCUES",
            }
            for name in CANDIDATES
        ],
        "rescues": rescues,
        "firewall": firewall(),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard-index", type=int)
    ap.add_argument("--shard-count", type=int, default=4)
    ap.add_argument("--synthesize-dir")
    args = ap.parse_args()

    artifacts = Path(__file__).resolve().parents[1] / "artifacts"
    artifacts.mkdir(exist_ok=True)
    if args.synthesize_dir:
        out = synthesize(args.synthesize_dir)
        path = artifacts / "JANUS_TRUMP_R50E_SHORT_PARENT_BAD_SECTOR_TRANSFER_LEMMA_SYNTHESIS.json"
    else:
        if args.shard_index is None:
            raise SystemExit("--shard-index required unless --synthesize-dir is used")
        out = run_shard(args.shard_index, args.shard_count)
        path = artifacts / f"JANUS_TRUMP_R50E_SHORT_PARENT_BAD_SECTOR_TRANSFER_LEMMA_SHARD_{args.shard_index}_OF_{args.shard_count}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate": out["gate"], "mode": out["mode"], "metrics": out.get("metrics"), "verdict": out.get("verdict")}, sort_keys=True))


if __name__ == "__main__":
    main()
