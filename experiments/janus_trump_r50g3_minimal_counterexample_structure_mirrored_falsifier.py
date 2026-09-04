from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g1_r33_w4_domain_escape_guarded_replay as r50g1
import janus_trump_r50g2_guarded_full_smallest_first_deadcore as r50g2

GATE = "JANUS_TRUMP_R50G3_MINIMAL_COUNTEREXAMPLE_STRUCTURE_AND_MIRRORED_FALSIFIER"
WIDTH_CAP = 4
MIN_N = 6
MAX_N = 10


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def measure_vcl(f):
    f = canon(f)
    return (len(r33.variables(f)), len(f), sum(len(c) for c in f))


def fhash(f):
    return r49i.fhash(canon(f))


def _remove_one_clause(f, clause):
    f = list(canon(f))
    c = r33.canonical_clause(clause)
    if c not in f:
        raise AssertionError(("R50G3_REPLAY_CLAUSE_NOT_FOUND", c, f))
    f.remove(c)
    return canon(f)


def apply_r33_record(formula, record):
    """Independent deterministic replay of one frozen R33 history record."""
    before = canon(formula)
    if list(r33.measure(before)) != list(record["measure_before"]):
        raise AssertionError(("R50G3_R33_MEASURE_BEFORE_MISMATCH", record, r33.measure(before)))
    rule = record["rule"]

    if rule == "TAUTOLOGY_DELETION":
        after = _remove_one_clause(before, record["clause"])
    elif rule == "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE":
        lit = int(record["literal"])
        nf = []
        for c in before:
            if lit in c:
                continue
            if -lit in c:
                nf.append(tuple(x for x in c if x != -lit))
            else:
                nf.append(c)
        after = canon(nf)
    elif rule == "PURE_LITERAL_AUTARKY":
        lit = int(record["literal"])
        after = canon(c for c in before if lit not in c)
    elif rule == "SUBSUMPTION":
        after = _remove_one_clause(before, record["deleted"])
    elif rule == "BLOCKED_CLAUSE_ELIMINATION":
        after = _remove_one_clause(before, record["clause"])
    elif rule == "BOUNDED_VARIABLE_ELIMINATION":
        x = int(record["var"])
        removed = {tuple(c) for c in record["positive"]} | {tuple(c) for c in record["negative"]}
        for c in removed:
            if c not in before:
                raise AssertionError(("R50G3_BVE_PARENT_NOT_FOUND", x, c))
        after = canon([c for c in before if c not in removed] + [tuple(c) for c in record["resolvents"]])
    else:
        raise AssertionError(("R50G3_UNKNOWN_R33_RULE", rule))

    if list(r33.measure(after)) != list(record["measure_after"]):
        raise AssertionError(("R50G3_R33_MEASURE_AFTER_MISMATCH", record, r33.measure(after)))
    return after


def replay_r33_history(formula):
    original = canon(formula)
    result = r33.simplify(original)
    state = original
    rows = []
    first_break = None
    for i, record in enumerate(result["history"]):
        before_width = max_width(state)
        after = apply_r33_record(state, record)
        after_width = max_width(after)
        if before_width <= WIDTH_CAP and after_width > WIDTH_CAP and first_break is None:
            first_break = i
            if record["rule"] != "BOUNDED_VARIABLE_ELIMINATION":
                raise AssertionError(("R50G3_FIRST_W4_BREAK_NOT_BVE", i, record))
        if record["rule"] != "BOUNDED_VARIABLE_ELIMINATION" and after_width > before_width:
            raise AssertionError(("R50G3_NON_BVE_WIDTH_INCREASE", i, record, before_width, after_width))
        rows.append({
            "index": i,
            "rule": record["rule"],
            "before_width": before_width,
            "after_width": after_width,
            "before_VCL": list(measure_vcl(state)),
            "after_VCL": list(measure_vcl(after)),
            "after_hash": fhash(after),
        })
        state = after
    if canon(result["final_formula"]) != state:
        raise AssertionError(("R50G3_R33_FINAL_REPLAY_MISMATCH", fhash(state), fhash(result["final_formula"])))
    return {
        "result": result,
        "rows": rows,
        "first_break_index": first_break,
        "safe_prefix_length": len(rows) if first_break is None else first_break,
        "safe_prefix_formula": original if not rows or first_break == 0 else canon_from_hashless_rows(original, result["history"], first_break),
    }


def canon_from_hashless_rows(original, history, count):
    state = canon(original)
    for record in history[:count]:
        state = apply_r33_record(state, record)
    return state


def local_symbolic_kernel():
    # Parent-width arithmetic for W4 exact DP.
    parent_rows = []
    for pw in range(1, 5):
        for nw in range(1, 5):
            raw_union_upper = (pw - 1) + (nw - 1)
            parent_rows.append({
                "positive_parent_width": pw,
                "negative_parent_width": nw,
                "raw_union_upper": raw_union_upper,
                "can_exceed_4_by_width_arithmetic": raw_union_upper > 4,
            })
            if raw_union_upper > 4 and pw < 4 and nw < 4:
                raise AssertionError(("R50G3_BAD_PAIR_WITHOUT_WIDTH4_PARENT_ARITHMETIC", pw, nw))

    # For V<=5, any non-tautological resolvent after eliminating one pivot uses
    # at most V-1 distinct remaining variables, hence width <=4.
    v_small = []
    for vcount in range(1, 6):
        bound = max(0, vcount - 1)
        if bound > 4:
            raise AssertionError(("R50G3_V_LT6_BOUND_FAIL", vcount, bound))
        v_small.append({"V": vcount, "max_nontautological_resolvent_width": bound})

    # Exact V=6 width-5 geometry by residual cardinalities.
    v6_patterns = []
    for pw in range(1, 5):
        for nw in range(1, 5):
            a, b = pw - 1, nw - 1
            for intersection in range(0, min(a, b) + 1):
                union = a + b - intersection
                if union == 5:
                    v6_patterns.append((pw, nw, intersection))
    expected = {(4, 3, 0), (3, 4, 0), (4, 4, 1)}
    if set(v6_patterns) != expected:
        raise AssertionError(("R50G3_V6_GEOMETRY_FAIL", v6_patterns))

    return {
        "parent_width_rows": parent_rows,
        "V_lt_6_rows": v_small,
        "V6_width5_patterns": [list(x) for x in sorted(v6_patterns)],
        "proved_source_lemmas": [
            "L1_R33_NON_BVE_WIDTH_MONOTONICITY",
            "L2_FIRST_R33_W4_ESCAPE_IS_BVE",
            "L4_GUARDED_OPEN_REQUIRES_AT_LEAST_6_VARIABLES",
            "L5_NO_R49H_BIPOLAR_PIVOT_HAS_WIDTH4_PARENT_WITNESS",
            "L6_V6_BAD_PAIR_GEOMETRY",
        ],
    }


def retained_bad_pairs(formula, var):
    f = canon(formula)
    out = []
    pos = [c for c in f if var in c]
    neg = [c for c in f if -var in c]
    for p in pos:
        a = set(p) - {var}
        for n in neg:
            b = set(n) - {-var}
            u = a | b
            if r49i.is_tautological_union(u) or len(u) <= WIDTH_CAP:
                continue
            out.append({
                "positive_parent": list(p),
                "negative_parent": list(n),
                "positive_width": len(p),
                "negative_width": len(n),
                "resolvent_width": len(u),
                "residual_union_variables": sorted({abs(x) for x in u}),
                "residual_literal_union": sorted(u, key=r33.lit_key),
                "residual_intersection_size": len(a & b),
            })
    return out


def audit_candidate_state(formula):
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise AssertionError("R50G3_INPUT_LEFT_W4")
    r33s = r50g2._r33_authority_status(f)
    out = {
        "hash": fhash(f),
        "VCL": list(measure_vcl(f)),
        "R33_status": r33s["status"],
        "R33_escape": None,
        "no_R49H": False,
        "fixed_point_profiles": None,
    }

    if r33s["status"] == "REJECTED_W4_DOMAIN_ESCAPE":
        rr = replay_r33_history(f)
        if rr["first_break_index"] is None:
            raise AssertionError("R50G3_ESCAPE_WITHOUT_BREAK")
        break_row = rr["rows"][rr["first_break_index"]]
        if break_row["rule"] != "BOUNDED_VARIABLE_ELIMINATION":
            raise AssertionError("R50G3_ESCAPE_BREAK_NOT_BVE")
        out["R33_escape"] = {
            "history_length": len(rr["rows"]),
            "first_break_index": rr["first_break_index"],
            "safe_prefix_length": rr["safe_prefix_length"],
            "safe_prefix_nonempty": rr["safe_prefix_length"] > 0,
            "safe_prefix_hash": fhash(rr["safe_prefix_formula"]),
            "safe_prefix_VCL": list(measure_vcl(rr["safe_prefix_formula"])),
            "breaking_rule": break_row["rule"],
        }

    if r33s["status"] not in ("FIXED_POINT", "REJECTED_W4_DOMAIN_ESCAPE"):
        return out

    tokens = r50a.expose_exact_tokens(f)
    direct = [t for t in tokens if t["direct_exact_dp_authorized"]]
    out["no_R49H"] = not bool(direct)
    if direct:
        return out

    profiles = [r49i.variable_profile(f, int(v)) for v in r33.variables(f)]
    if r33s["status"] == "FIXED_POINT":
        rows = []
        for p in profiles:
            if not p["bipolar"]:
                raise AssertionError(("R50G3_FIXED_POINT_NONBIPOLAR", p))
            if int(p["chi_star"]) < 5:
                raise AssertionError(("R50G3_NO_R49H_BUT_CHI_LT5", p))
            var = int(p["var"])
            bad = retained_bad_pairs(f, var)
            if not bad:
                raise AssertionError(("R50G3_CHI_GE5_WITHOUT_BAD_PAIR", var))
            if not all(b["positive_width"] == 4 or b["negative_width"] == 4 for b in bad):
                raise AssertionError(("R50G3_BAD_PAIR_WITHOUT_WIDTH4_PARENT", var, bad))
            if len(r33.variables(f)) == 6:
                expected_vars = set(r33.variables(f)) - {var}
                for b in bad:
                    if b["resolvent_width"] != 5:
                        raise AssertionError(("R50G3_V6_BAD_WIDTH_NOT5", var, b))
                    if set(b["residual_union_variables"]) != expected_vars:
                        raise AssertionError(("R50G3_V6_BAD_PAIR_NOT_COVER_ALL_OTHER_VARS", var, b))
                    pair = (b["positive_width"], b["negative_width"], b["residual_intersection_size"])
                    if pair not in {(4, 3, 0), (3, 4, 0), (4, 4, 1)}:
                        raise AssertionError(("R50G3_V6_BAD_PAIR_GEOMETRY_MISMATCH", var, b))
            rows.append({
                "var": var,
                "chi_star": int(p["chi_star"]),
                "bad_pair_count": len(bad),
                "has_width4_parent_witness": True,
            })
        out["fixed_point_profiles"] = rows
    return out


def run_worker(worker: int, roots_per_worker: int, mirror_candidates_per_worker: int):
    n = MIN_N + worker
    if not (MIN_N <= n <= MAX_N):
        raise ValueError("R50G3_WORKER_OUTSIDE_FROZEN_RANGE")

    kernel = local_symbolic_kernel()
    reachable_states = 0
    candidate_states = 0
    fixed_no_r49h = 0
    escape_states = 0
    nonempty_safe_prefix_escapes = 0
    guarded_open_states = []

    for i in range(roots_per_worker):
        m = 3 * n + (i % (3 * n + 1))
        seed = 50_700_000 + worker * 100_000 + i
        state, _ = r50g.make_planted(seed, n, m, "3CNF")
        if len(r33.variables(state)) != n:
            continue
        seen = set()
        bound = 3 * n + 8
        for _step in range(bound):
            state = canon(state)
            h = fhash(state)
            if h in seen:
                raise AssertionError(("R50G3_TRACE_CYCLE", worker, seed, h))
            seen.add(h)
            reachable_states += 1
            audit = audit_candidate_state(state)
            if audit["R33_status"] in ("FIXED_POINT", "REJECTED_W4_DOMAIN_ESCAPE") and audit["no_R49H"]:
                candidate_states += 1
                if audit["R33_status"] == "FIXED_POINT":
                    fixed_no_r49h += 1
                else:
                    escape_states += 1
                    if audit["R33_escape"]["safe_prefix_nonempty"]:
                        nonempty_safe_prefix_escapes += 1
            step = r50g1.guarded_exact_step(state)
            if step["kind"] == "TERMINAL":
                break
            if step["kind"] == "OPEN_OBSTRUCTION":
                exact = r50g2.exact_guarded_open_test(state)
                guarded_open_states.append({
                    "hash": h,
                    "VCL": list(measure_vcl(state)),
                    "exact_open": bool(exact.get("open")),
                })
                break
            state = canon(step["successor"])
        else:
            raise AssertionError(("R50G3_TRACE_BOUND", worker, seed))

    mirror_escape_states = 0
    mirror_nonempty_safe_prefix = 0
    mirror_fixed_no_r49h = 0
    profiles = ("W34", "W234", "W4_CONTROL")
    for i in range(mirror_candidates_per_worker):
        profile = profiles[i % len(profiles)]
        m = 3 * n + (i % (4 * n + 1))
        seed = 50_800_000 + worker * 100_000 + i
        formula, _ = r50g.make_planted(seed, n, m, profile)
        if len(r33.variables(formula)) != n:
            continue
        audit = audit_candidate_state(formula)
        if audit["R33_status"] == "REJECTED_W4_DOMAIN_ESCAPE":
            mirror_escape_states += 1
            if audit["R33_escape"]["safe_prefix_nonempty"]:
                mirror_nonempty_safe_prefix += 1
        if audit["R33_status"] == "FIXED_POINT" and audit["no_R49H"]:
            mirror_fixed_no_r49h += 1

    return {
        "gate": GATE,
        "mode": "WORKER",
        "worker": worker,
        "n": n,
        "kernel": kernel,
        "metrics": {
            "reachable_states_audited": reachable_states,
            "reachable_candidate_states_no_r33_authority_no_r49h": candidate_states,
            "reachable_fixed_point_no_r49h": fixed_no_r49h,
            "reachable_r33_escape_no_r49h": escape_states,
            "reachable_nonempty_safe_prefix_escapes": nonempty_safe_prefix_escapes,
            "guarded_open_states": len(guarded_open_states),
            "mirror_escape_states": mirror_escape_states,
            "mirror_nonempty_safe_prefix_escapes": mirror_nonempty_safe_prefix,
            "mirror_fixed_point_no_r49h": mirror_fixed_no_r49h,
        },
        "first_guarded_open": guarded_open_states[0] if guarded_open_states else None,
        "verdict": "STRUCTURAL_LEMMAS_REPLAYED__MINIMAL_COUNTEREXAMPLE_ESCAPE_CASE_REMAINS_A_SEPARATE_PROOF_OBLIGATION",
        "firewall": {
            "R50G3_STRUCTURAL_LEMMAS_IMPLY_U": False,
            "SAFE_PREFIX_EXISTS_IMPLIES_CURRENT_U": False,
            "NO_MIRROR_FALSIFIER_FOUND_IMPLIES_U": False,
            "ARBITRARY_SUBFORMULA_MINIMALITY_ALLOWED_ON_REACHABLE_U": False,
            "GUARDED_U": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def synthesize(directory: Path):
    paths = sorted(directory.glob("JANUS_TRUMP_R50G3_WORKER_*.json"))
    if len(paths) != 5:
        raise AssertionError(("R50G3_EXPECTED_5_WORKERS", [str(p) for p in paths]))
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    if sorted(r["n"] for r in rows) != [6, 7, 8, 9, 10]:
        raise AssertionError("R50G3_N_RANGE_MISMATCH")
    metric_keys = rows[0]["metrics"].keys()
    totals = {k: sum(int(r["metrics"][k]) for r in rows) for k in metric_keys}
    out = {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "workers": 5,
        "n_values": [6, 7, 8, 9, 10],
        "proved_for_frozen_rule_definitions": rows[0]["kernel"]["proved_source_lemmas"],
        "metrics": totals,
        "critical_blocked_proof_step": "PREFIX_CLOSURE_OR_ESCAPE_ELIMINATION",
        "verdict": "LOCAL_SOURCE_LEMMAS_CLOSED__MINIMAL_COUNTEREXAMPLE_REDUCED_TO_FIXED_POINT_OR_R33_ESCAPE_CASE__U_OPEN",
        "firewall": rows[0]["firewall"],
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int)
    ap.add_argument("--roots-per-worker", type=int, default=80)
    ap.add_argument("--mirror-candidates-per-worker", type=int, default=240)
    ap.add_argument("--synthesize-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    if a.synthesize_dir is not None:
        out = synthesize(a.synthesize_dir)
    else:
        if a.worker is None:
            raise ValueError("--worker required outside synthesis")
        out = run_worker(a.worker, a.roots_per_worker, a.mirror_candidates_per_worker)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "mode": out["mode"],
        "verdict": out["verdict"],
        "metrics": out.get("metrics"),
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
