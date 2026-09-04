from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50c_top2_min_taut_prospective_falsifier as r50c
import janus_trump_r50e_short_parent_bad_sector_transfer_lemma as r50e

GATE = "JANUS_TRUMP_R50F_WIDE_CLAUSE_SURVIVAL_CERTIFICATE_AND_CLEARANCE_REPAIR"
WIDTH_CAP = 4
EXPECTED_ROOTS = 52
EXPECTED_HARD_STATES = 441
EXPECTED_RESCUES = 12


class IntegrityFailure(RuntimeError):
    pass


def canon(formula):
    return r33.canonical_formula(formula)


def fhash(formula):
    return r49i.fhash(canon(formula))


def max_width(formula):
    f = canon(formula)
    return 0 if not f else max(len(c) for c in f)


def ckey(clause):
    return tuple(r33.canonical_clause(clause))


def wide_set(formula):
    return {ckey(c) for c in canon(formula) if len(c) > WIDTH_CAP}


def _wide_json(items):
    return [list(c) for c in sorted(items)]


def _event(stage, rule, before, after, metadata=None):
    before = canon(before)
    after = canon(after)
    bw = wide_set(before)
    aw = wide_set(after)
    removed = bw - aw
    added = aw - bw
    if added and rule not in {
        "R33_UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE",
        "R33_BOUNDED_VARIABLE_ELIMINATION",
        "RUP_SINGLE_LITERAL_STRENGTHENING",
    }:
        raise IntegrityFailure(("R50F_UNACCOUNTED_WIDE_CREATION", stage, rule, _wide_json(added)))
    return {
        "stage": stage,
        "rule": rule,
        "before_hash": r42.formula_hash(before),
        "after_hash": r42.formula_hash(after),
        "wide_before_count": len(bw),
        "wide_after_count": len(aw),
        "removed_wide": _wide_json(removed),
        "added_wide": _wide_json(added),
        "metadata": metadata or {},
    }


def dp_subsumption_certificate(formula, var):
    f = canon(formula)
    dp = r45a.exact_dp_record(f, int(var))
    if dp is None:
        raise IntegrityFailure(("R50F_DP_MISSING", fhash(f), int(var)))
    replay = r45a.independent_dp_replay(f, dp)
    if not replay["pass"]:
        raise IntegrityFailure(("R50F_DP_REPLAY_FAIL", fhash(f), int(var), replay))

    base = tuple(c for c in f if int(var) not in c and -int(var) not in c)
    resolvents = canon(dp["full_non_tautological_resolvents"])
    pool = canon(list(base) + list(resolvents))
    transformed = canon(dp["transformed"])
    pool_wide = wide_set(pool)
    transformed_wide = wide_set(transformed)
    omitted_wide = pool_wide - transformed_wide
    transformed_sets = [(c, set(c)) for c in transformed]
    witnesses = []
    for c in sorted(omitted_wide):
        candidates = [k for k, ks in transformed_sets if ks <= set(c)]
        if not candidates:
            raise IntegrityFailure(("R50F_DP_SUBSUMPTION_WITNESS_MISSING", fhash(f), int(var), c))
        witness = min(candidates, key=lambda x: (len(x), x))
        witnesses.append({"omitted_wide_clause": list(c), "witness_subclause": list(witness)})

    event = _event(
        "EXACT_DP_SUBSUMPTION",
        "DP_SUBSUMPTION",
        pool,
        transformed,
        {
            "omitted_wide_subsumption_witnesses": witnesses,
            "pool_clause_count": len(pool),
            "transformed_clause_count": len(transformed),
        },
    )
    return {
        "dp": dp,
        "pool": pool,
        "transformed": transformed,
        "event": event,
        "independent_dp_replay_pass": True,
        "all_omitted_wide_have_subsumption_witness": len(witnesses) == len(omitted_wide),
    }


def apply_r33_record(active, record):
    active = canon(active)
    rule = record["rule"]
    metadata = {}

    if rule == "TAUTOLOGY_DELETION":
        clause = ckey(record["clause"])
        if clause not in active:
            raise IntegrityFailure(("R50F_R33_TAUT_SOURCE_MISSING", clause))
        after = canon(c for c in active if c != clause)
        event_rule = "R33_TAUTOLOGY_DELETION"

    elif rule == "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE":
        lit = int(record["literal"])
        nf = []
        for c in active:
            if lit in c:
                continue
            if -lit in c:
                nf.append(tuple(x for x in c if x != -lit))
            else:
                nf.append(c)
        after = canon(nf)
        metadata = {"literal": lit}
        event_rule = "R33_UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE"

    elif rule == "PURE_LITERAL_AUTARKY":
        lit = int(record["literal"])
        after = canon(c for c in active if lit not in c)
        metadata = {"literal": lit}
        event_rule = "R33_PURE_LITERAL_AUTARKY"

    elif rule == "SUBSUMPTION":
        deleted = ckey(record["deleted"])
        witness = ckey(record["witness_subclause"])
        if deleted not in active or witness not in active or not set(witness) <= set(deleted):
            raise IntegrityFailure(("R50F_R33_SUBSUMPTION_BAD_WITNESS", deleted, witness))
        after = canon(c for c in active if c != deleted)
        metadata = {"deleted": list(deleted), "witness_subclause": list(witness)}
        event_rule = "R33_SUBSUMPTION"

    elif rule == "BLOCKED_CLAUSE_ELIMINATION":
        clause = ckey(record["clause"])
        if clause not in active:
            raise IntegrityFailure(("R50F_R33_BLOCKED_SOURCE_MISSING", clause))
        after = canon(c for c in active if c != clause)
        metadata = {"blocking_literal": int(record["blocking_literal"]), "clause": list(clause)}
        event_rule = "R33_BLOCKED_CLAUSE_ELIMINATION"

    elif rule == "BOUNDED_VARIABLE_ELIMINATION":
        var = int(record["var"])
        pos = tuple(ckey(c) for c in record["positive"])
        neg = tuple(ckey(c) for c in record["negative"])
        resolvents = tuple(ckey(c) for c in record["resolvents"])
        for c in pos + neg:
            if c not in active:
                raise IntegrityFailure(("R50F_R33_BVE_PARENT_MISSING", var, c))
        removed = set(pos + neg)
        after = canon([c for c in active if c not in removed] + list(resolvents))
        metadata = {
            "var": var,
            "positive_parent_count": len(pos),
            "negative_parent_count": len(neg),
            "resolvent_count": len(resolvents),
        }
        event_rule = "R33_BOUNDED_VARIABLE_ELIMINATION"

    else:
        raise IntegrityFailure(("R50F_UNKNOWN_R33_RULE", rule))

    if list(r33.measure(after)) != list(record["measure_after"]):
        raise IntegrityFailure(("R50F_R33_MEASURE_REPLAY_MISMATCH", rule, r33.measure(after), record["measure_after"]))
    return after, _event("R33", event_rule, active, after, metadata)


def replay_r33_history(initial_formula, result):
    active = canon(initial_formula)
    events = []
    for record in result["history"]:
        if list(r33.measure(active)) != list(record["measure_before"]):
            raise IntegrityFailure(("R50F_R33_MEASURE_BEFORE_MISMATCH", record["rule"]))
        active, event = apply_r33_record(active, record)
        events.append(event)
    expected = canon(result["final_formula"])
    if active != expected:
        raise IntegrityFailure(("R50F_R33_FINAL_REPLAY_MISMATCH", r42.formula_hash(active), r42.formula_hash(expected)))
    return active, events


def replay_rup_history(initial_formula, rup):
    active = canon(initial_formula)
    events = []
    replay = r35b.independent_certificate_replay(active, rup)
    if not replay["pass"]:
        raise IntegrityFailure(("R50F_RUP_REPLAY_FAIL", replay))
    for record in rup["history"]:
        source = ckey(record["source_clause"])
        strengthened = ckey(record["strengthened_clause"])
        if source not in active:
            raise IntegrityFailure(("R50F_RUP_SOURCE_MISSING", source))
        after = r35b.replace_clause_with_subclause(active, source, strengthened)
        event = _event(
            "RUP",
            "RUP_SINGLE_LITERAL_STRENGTHENING",
            active,
            after,
            {
                "source_clause": list(source),
                "removed_literal": int(record["removed_literal"]),
                "strengthened_clause": list(strengthened),
                "up_conflict_certified": True,
            },
        )
        active = canon(after)
        events.append(event)
    expected = canon(rup["final_formula"])
    if active != expected:
        raise IntegrityFailure(("R50F_RUP_FINAL_REPLAY_MISMATCH", r42.formula_hash(active), r42.formula_hash(expected)))
    return active, events


def instrument_normalization(forced_formula, claimed_normalization):
    forced = canon(forced_formula)
    state = forced
    events = []
    rounds = []
    height_bound = r47j.restart_height_bound(forced)

    for round_index in range(height_bound + 1):
        before = state
        reduced = r33.simplify(before)
        after_r33, r33_events = replay_r33_history(before, reduced)
        events.extend(r33_events)
        round_row = {
            "round": round_index,
            "before_hash": r42.formula_hash(before),
            "before_wide_count": len(wide_set(before)),
            "r33_rule_counts": dict(reduced["rule_counts"]),
            "after_r33_hash": r42.formula_hash(after_r33),
            "after_r33_wide_count": len(wide_set(after_r33)),
            "rup_rule_count": 0,
        }

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            state = after_r33
            round_row["stop"] = reduced["terminal"]
            rounds.append(round_row)
            break

        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            state = after_r33
            round_row["stop"] = "AFFINE_RECOGNIZED"
            rounds.append(round_row)
            break

        rup = r35b.run_candidate(after_r33)
        after_rup, rup_events = replay_rup_history(after_r33, rup)
        events.extend(rup_events)
        round_row["rup_rule_count"] = len(rup["history"])
        round_row["after_rup_hash"] = r42.formula_hash(after_rup)
        round_row["after_rup_wide_count"] = len(wide_set(after_rup))
        round_row["rup_status"] = rup["status"]

        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            state = after_rup
            round_row["stop"] = "RUP_UNSAT"
            rounds.append(round_row)
            break
        if after_rup != after_r33:
            state = after_rup
            round_row["restart"] = True
            rounds.append(round_row)
            continue

        state = after_rup
        round_row["stop"] = "CERTIFIED_NORMALIZATION_FIXPOINT"
        rounds.append(round_row)
        break
    else:
        raise IntegrityFailure(("R50F_NORMALIZATION_HEIGHT_BOUND", height_bound))

    expected = canon(claimed_normalization["final_formula"])
    if state != expected:
        raise IntegrityFailure(("R50F_NORMALIZATION_FINAL_MISMATCH", r42.formula_hash(state), r42.formula_hash(expected)))

    transitions_to_zero = [
        e for e in events if int(e["wide_before_count"]) > 0 and int(e["wide_after_count"]) == 0
    ]
    final_clearance_event = transitions_to_zero[-1] if transitions_to_zero and not wide_set(state) else None
    return {
        "pass": True,
        "rounds": rounds,
        "events": events,
        "final_formula": [list(c) for c in state],
        "final_hash": r42.formula_hash(state),
        "final_wide_clauses": _wide_json(wide_set(state)),
        "final_wide_count": len(wide_set(state)),
        "final_clearance_event": final_clearance_event,
    }


def wide_clearance_certificate(formula, var):
    f = canon(formula)
    dp_cert = dp_subsumption_certificate(f, int(var))
    candidate = r47j.macro_candidate_fixpoint(f, int(var))
    if candidate is None:
        raise IntegrityFailure(("R50F_R47J_CANDIDATE_MISSING", fhash(f), int(var)))
    macro_replay = r47j.independent_fixpoint_macro_replay(f, candidate)
    if not macro_replay["pass"]:
        raise IntegrityFailure(("R50F_MACRO_REPLAY_FAIL", fhash(f), int(var), macro_replay))

    instrumented = instrument_normalization(dp_cert["transformed"], candidate["normalization"])
    all_events = [dp_cert["event"]] + instrumented["events"]
    final_formula = canon(instrumented["final_formula"])
    no_fresh = set(r33.variables(final_formula)).issubset(set(r33.variables(f)))
    strict_var_descent = len(r33.variables(final_formula)) < len(r33.variables(f))
    terminal = candidate["normalization"]["terminal"] is not None
    final_wide_empty = len(wide_set(final_formula)) == 0
    width4_safe = bool(terminal or (no_fresh and strict_var_descent and final_wide_empty and max_width(final_formula) <= WIDTH_CAP))

    dp_event = dp_cert["event"]
    if int(dp_event["wide_before_count"]) > 0 and int(dp_event["wide_after_count"]) == 0:
        final_clearance = dp_event
        clearance_class = "CLEAR_AT_EXACT_DP_SUBSUMPTION"
    elif final_wide_empty and instrumented["final_clearance_event"] is not None:
        final_clearance = instrumented["final_clearance_event"]
        clearance_class = "CLEAR_BY_CERTIFIED_NORMALIZATION"
    elif final_wide_empty:
        final_clearance = None
        clearance_class = "NO_WIDE_AFTER_DP"
    else:
        final_clearance = None
        clearance_class = "WIDE_SURVIVES_NORMALIZATION"

    return {
        "var": int(var),
        "input_hash": fhash(f),
        "certificate_pass": True,
        "exact_dp_replay_pass": True,
        "macro_independent_replay_pass": True,
        "dp_subsumption": {
            "wide_pool_count": int(dp_event["wide_before_count"]),
            "wide_transformed_count": int(dp_event["wide_after_count"]),
            "omitted_wide_witnesses": dp_event["metadata"]["omitted_wide_subsumption_witnesses"],
        },
        "normalization": instrumented,
        "event_count": len(all_events),
        "events": all_events,
        "clearance_class": clearance_class,
        "final_clearance_rule": final_clearance["rule"] if final_clearance else None,
        "final_clearance_stage": final_clearance["stage"] if final_clearance else None,
        "final_wide_empty": final_wide_empty,
        "final_wide_clauses": _wide_json(wide_set(final_formula)),
        "no_fresh_variables": bool(no_fresh),
        "strict_variable_descent": bool(strict_var_descent),
        "terminal": candidate["normalization"]["terminal"],
        "controller_width4_safe_authorized": bool(width4_safe),
        "repair_contract": "OPAQUE_FINAL_WIDTH_CHECK_REPLACED_BY_REPLAYABLE_WIDE_CLEARANCE_LEDGER_PLUS_EXISTING_R47J_OBLIGATIONS",
    }


def rescue_record(formula, probe, root_index, step_index, provenance):
    if probe.get("first_safe_rank") != 2:
        raise IntegrityFailure(("R50F_NOT_RANK2_RESCUE", probe.get("state_hash")))
    selected = probe["selected_rows"]
    if len(selected) != 2:
        raise IntegrityFailure(("R50F_TOP2_SIZE", probe["state_hash"], len(selected)))
    v1 = int(selected[0]["var"])
    v2 = int(selected[1]["var"])
    c1 = wide_clearance_certificate(formula, v1)
    c2 = wide_clearance_certificate(formula, v2)
    if c1["controller_width4_safe_authorized"]:
        raise IntegrityFailure(("R50F_RANK1_UNEXPECTED_SAFE", probe["state_hash"], v1))
    if not c2["controller_width4_safe_authorized"]:
        raise IntegrityFailure(("R50F_RANK2_RESCUE_NOT_CERTIFIED", probe["state_hash"], v2))
    if c1["final_wide_empty"]:
        raise IntegrityFailure(("R50F_RANK1_EXPECTED_WIDE_SURVIVOR", probe["state_hash"], v1))
    if not c2["final_wide_empty"]:
        raise IntegrityFailure(("R50F_RANK2_WIDE_NOT_CLEARED", probe["state_hash"], v2))
    return {
        "state_hash": probe["state_hash"],
        "state_CLV": probe["state_CLV"],
        "root_index": int(root_index),
        "trace_step": int(step_index),
        "root_provenance": provenance,
        "rank1": c1,
        "rank2": c2,
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
            raise IntegrityFailure(("R50F_TRACE_CYCLE", root_index, h))
        seen.add(h)
        if max_width(current) > WIDTH_CAP:
            raise IntegrityFailure(("R50F_TRACE_WIDTH_DRIFT", root_index, max_width(current)))
        if not set(r33.variables(current)).issubset(root_vars):
            raise IntegrityFailure(("R50F_TRACE_FRESH_VARIABLE", root_index, h))

        probe = r50c.hard_state_probe(current)
        if probe["applicable"]:
            hard_states += 1
            if probe["first_safe_rank"] == 2:
                rescues.append(rescue_record(current, probe, root_index, step_index, provenance))
            elif probe["first_safe_rank"] != 1:
                raise IntegrityFailure(("R50F_TOP2_REGRESSION", root_index, h, probe["first_safe_rank"]))

        step = r50a.exact_step(current)
        if step["kind"] == "OPEN_OBSTRUCTION":
            raise IntegrityFailure(("R50F_R50A_OPEN_REGRESSION", root_index, h))
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

    raise IntegrityFailure(("R50F_TRACE_STEP_CAP", root_index, cap, fhash(current)))


def firewall():
    return {
        "HEURISTIC_PROOF_AUTHORITY": False,
        "ML_PROOF_AUTHORITY": False,
        "RANDOM_PROOF_AUTHORITY": False,
        "WIDE_CLEARANCE_CERTIFICATE_IS_PREDICTOR": False,
        "R50F_ADDS_NEW_SAT_PROOF_RULE": False,
        "R50F_FINITE_12_PROVES_TOP2_TRANSFER": False,
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
    roots = r50c.collect_prospective_roots()
    if len(roots) != EXPECTED_ROOTS:
        raise IntegrityFailure(("R50F_ROOT_CORPUS_DRIFT", len(roots), EXPECTED_ROOTS))
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
        "parent_R50E_commit": "64c800d8538b03323024b5fdf4f85a5d5b5e0dc8",
        "source_R50E_run_id": 33916878594,
        "shard": {"index": int(shard_index), "count": int(shard_count)},
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
    paths = sorted(directory.glob("JANUS_TRUMP_R50F_*_SHARD_*_OF_4.json"))
    if len(paths) != 4:
        raise IntegrityFailure(("R50F_EXPECTED_4_SHARDS", len(paths), [p.name for p in paths]))
    shards = [json.loads(p.read_text()) for p in paths]
    roots = [r for s in shards for r in s["roots"]]
    rescues = [x for r in roots for x in r["rescues"]]
    hard_states = sum(int(r["hard_state_count"]) for r in roots)
    if len(roots) != EXPECTED_ROOTS or hard_states != EXPECTED_HARD_STATES or len(rescues) != EXPECTED_RESCUES:
        raise IntegrityFailure(("R50F_REPRODUCTION_DRIFT", len(roots), hard_states, len(rescues)))

    rank2_clearance = Counter(r["rank2"]["clearance_class"] for r in rescues)
    rank2_final_rules = Counter(r["rank2"]["final_clearance_rule"] or "NONE" for r in rescues)
    rank1_survivor_widths = Counter()
    all_rank2_removal_rules = Counter()
    for r in rescues:
        for clause in r["rank1"]["final_wide_clauses"]:
            rank1_survivor_widths[str(len(clause))] += 1
        for e in r["rank2"]["events"]:
            if e["removed_wide"]:
                all_rank2_removal_rules[e["rule"]] += len(e["removed_wide"])

    out = {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "verdict": "EXACT_WIDE_SURVIVAL_CAUSES_CERTIFIED__CLEARANCE_REPAIR_PASS_ON_12_RESCUES__TRANSFER_THEOREM_OPEN",
        "metrics": {
            "roots": len(roots),
            "hard_states": hard_states,
            "rank2_rescues": len(rescues),
            "rank2_clearance_class_histogram": dict(sorted(rank2_clearance.items())),
            "rank2_final_clearance_rule_histogram": dict(sorted(rank2_final_rules.items())),
            "rank2_all_wide_removal_rule_histogram": dict(sorted(all_rank2_removal_rules.items())),
            "rank1_final_wide_survivor_width_histogram": dict(sorted(rank1_survivor_widths.items())),
            "rank1_survival_certificates": sum(int(not r["rank1"]["final_wide_empty"]) for r in rescues),
            "rank2_clearance_certificates": sum(int(r["rank2"]["final_wide_empty"]) for r in rescues),
            "rank2_controller_authorizations": sum(int(r["rank2"]["controller_width4_safe_authorized"]) for r in rescues),
        },
        "repair": {
            "name": "WIDE_CLEARANCE_CERTIFICATE",
            "status": "IMPLEMENTED_AND_REPLAYED_ON_R50C_RESCUES",
            "meaning": "A pivot is not trusted because wide clauses merely disappear in a final snapshot. Every disappearance/shrinkage is carried by an exact DP-subsumption, R33, or RUP event ledger, then the existing R47J replay/no-fresh/descent obligations are checked.",
            "new_semantic_proof_rule_added": False,
            "predictive_selector_added": False,
            "universal_transfer_proved": False
        },
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
        path = artifacts / "JANUS_TRUMP_R50F_WIDE_CLAUSE_SURVIVAL_CERTIFICATE_AND_CLEARANCE_REPAIR_SYNTHESIS.json"
    else:
        if args.shard_index is None:
            raise SystemExit("--shard-index required unless --synthesize-dir is used")
        out = run_shard(args.shard_index, args.shard_count)
        path = artifacts / f"JANUS_TRUMP_R50F_WIDE_CLAUSE_SURVIVAL_CERTIFICATE_AND_CLEARANCE_REPAIR_SHARD_{args.shard_index}_OF_{args.shard_count}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate": out["gate"], "mode": out["mode"], "metrics": out.get("metrics"), "verdict": out.get("verdict")}, sort_keys=True))


if __name__ == "__main__":
    main()
