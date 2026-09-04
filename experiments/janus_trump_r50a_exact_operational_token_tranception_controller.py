from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i

GATE = "JANUS_TRUMP_R50A_EXACT_OPERATIONAL_TOKEN_TRANCEPTION_CONTROLLER"
WIDTH_CAP = 4
R49H_THEOREM = "R49H_V1_2_BIPOLAR_NONTAUTO_CROSS_UNION_WIDTH4_SAFE_EXACT_DP"


def canon(formula):
    return r33.canonical_formula(formula)


def formula_hash(formula):
    return r49i.fhash(canon(formula))


def max_width(formula):
    return max((len(c) for c in canon(formula)), default=0)


def _digest(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def operational_token(formula, var):
    """Exact lossy action token. It has no authority until recomputed and verified.

    The token deliberately does not encode the whole formula.  It carries only the
    exact local facts required by the R49H sufficient condition plus an input hash.
    There is no score, learned weight, probability, sampling, or semantic number
    preference.
    """
    f = canon(formula)
    profile = r49i.variable_profile(f, int(var))
    body = {
        "schema": "R50A_OPERATIONAL_TOKEN_V1",
        "input_formula_hash": formula_hash(f),
        "pivot": int(var),
        "positive_parent_count": int(profile["positive_parent_count"]),
        "negative_parent_count": int(profile["negative_parent_count"]),
        "retained_nontautological_pair_count": int(profile["retained_nontautological_pair_count"]),
        "chi_star": int(profile["chi_star"]),
        "bipolar": bool(profile["bipolar"]),
        "pure": bool(profile["pure"]),
        "direct_exact_dp_authorized": bool(profile["bipolar"] and int(profile["chi_star"]) <= WIDTH_CAP),
        "action_if_authorized": "CANONICAL_EXACT_DP",
        "proof_rule": R49H_THEOREM,
    }
    body["token_sha256"] = _digest(body)
    return body


def verify_operational_token(formula, token):
    expected = operational_token(formula, int(token["pivot"]))
    return {
        "pass": expected == token,
        "input_hash_ok": token.get("input_formula_hash") == formula_hash(formula),
        "token_digest_ok": token.get("token_sha256") == expected.get("token_sha256"),
        "recomputed": expected,
    }


def expose_exact_tokens(formula):
    """Blue-field layer, made exact: expose every pivot token, never rank it."""
    f = canon(formula)
    return [operational_token(f, int(v)) for v in sorted(r33.variables(f))]


def _direct_dp_transition(formula, token):
    f = canon(formula)
    token_check = verify_operational_token(f, token)
    if not token_check["pass"]:
        raise AssertionError(("R50A_TOKEN_RECOMPUTE_FAIL", token_check))
    if not token["direct_exact_dp_authorized"]:
        raise AssertionError("R50A_UNAUTHORIZED_DIRECT_TOKEN")

    var = int(token["pivot"])
    dp = r45a.exact_dp_record(f, var)
    if dp is None:
        raise AssertionError(("R50A_R49H_AUTHORIZED_WITHOUT_DP_RECORD", var))
    replay = r45a.independent_dp_replay(f, dp)
    envelope = r45a.polynomial_envelope(f, dp)
    if not replay["pass"] or not envelope["pass"]:
        raise AssertionError(("R50A_DIRECT_DP_CERTIFICATE_FAIL", var, replay, envelope))

    successor = canon(dp["transformed"])
    before_vars = set(r33.variables(f))
    after_vars = set(r33.variables(successor))
    if var in after_vars:
        raise AssertionError(("R50A_DIRECT_PIVOT_SURVIVED", var))
    if not after_vars <= before_vars:
        raise AssertionError(("R50A_DIRECT_FRESH_VARIABLE", var))
    if len(after_vars) >= len(before_vars):
        raise AssertionError(("R50A_DIRECT_NO_VARIABLE_DESCENT", var))
    if max_width(successor) > WIDTH_CAP:
        raise AssertionError(("R50A_R49H_WIDTH_CONTRACT_FAIL", var, max_width(successor)))

    return {
        "kind": "NONTERMINAL",
        "lane": "BLUEFIELD_EXACT_TOKEN__R49H_DIRECT_DP",
        "selection_policy": "ASCENDING_VARIABLE_ID_FIRST_THEOREM_AUTHORIZED_TOKEN",
        "heuristic_ranking_used": False,
        "input_hash": formula_hash(f),
        "input_CLV": list(r33.measure(f)),
        "selected_token": token,
        "token_verification": {k: v for k, v in token_check.items() if k != "recomputed"},
        "successor": [list(c) for c in successor],
        "successor_hash": formula_hash(successor),
        "successor_CLV": list(r33.measure(successor)),
        "successor_max_width": max_width(successor),
        "strict_variable_descent": len(after_vars) < len(before_vars),
        "transition_certificate": {
            "DP": dp,
            "DP_independent_replay": replay,
            "polynomial_intermediate_envelope": envelope,
        },
        "tranception_reverse_contract": "SUCCESSOR_SAT_WITNESS -> r42.reconstruct_sa_bve(DP) -> PREDECESSOR_SAT_WITNESS",
    }


def _fallback_candidate(formula, var):
    f = canon(formula)
    candidate = r47j.macro_candidate_fixpoint(f, int(var))
    if candidate is None:
        return {"pivot": int(var), "candidate": False, "width4_safe": False}, None

    final = canon(candidate["normalization"]["final_formula"])
    before_vars = set(r33.variables(f))
    after_vars = set(r33.variables(final))
    terminal = candidate["normalization"]["terminal"]
    no_fresh = after_vars <= before_vars
    strict_v = len(after_vars) < len(before_vars)
    safe = bool(terminal is not None or (no_fresh and strict_v and max_width(final) <= WIDTH_CAP))
    row = {
        "pivot": int(var),
        "candidate": True,
        "terminal": terminal,
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "final_hash": formula_hash(final),
        "final_CLV": list(r33.measure(final)),
        "final_max_width": max_width(final),
        "no_fresh_variables": bool(no_fresh),
        "strict_variable_descent": bool(strict_v),
        "width4_safe": bool(safe),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
    }
    return row, candidate


def _r33_first(formula):
    """Certified deterministic preprocessing lane. No candidate ordering occurs here."""
    f = canon(formula)
    reduced = r33.simplify(f)
    after = canon(reduced["final_formula"])
    terminal = reduced["terminal"]

    if terminal != "STALLED_STACK_LEAN_CORE":
        solved = r42.solve_declared_terminal(after, terminal)
        if not solved["verification_pass"]:
            raise AssertionError(("R50A_R33_TERMINAL_VERIFY_FAIL", solved))
        full_assignment = None
        if solved["sat"]:
            full_assignment = r33.reconstruct_model(reduced, dict(solved.get("assignment") or {}))
            if not r33.eval_formula(f, full_assignment):
                raise AssertionError("R50A_R33_TERMINAL_RECONSTRUCTION_FAIL")
        return {
            "kind": "TERMINAL",
            "lane": "R33_CERTIFIED_TERMINAL",
            "heuristic_ranking_used": False,
            "input_hash": formula_hash(f),
            "terminal": solved["kind"],
            "semantic_sat": bool(solved["sat"]),
            "terminal_verification": solved,
            "SAT_assignment": full_assignment,
            "transition_certificate": {"R33_result": reduced},
        }

    if after != f:
        if not tuple(r33.measure(after)) < tuple(r33.measure(f)):
            raise AssertionError(("R50A_R33_NOT_STRICT_CLV_DESCENT", r33.measure(f), r33.measure(after)))
        if max_width(after) > WIDTH_CAP:
            raise AssertionError("R50A_R33_WIDTH4_PERSISTENCE_FAIL")
        return {
            "kind": "NONTERMINAL",
            "lane": "R33_CERTIFIED_REDUCTION",
            "heuristic_ranking_used": False,
            "input_hash": formula_hash(f),
            "input_CLV": list(r33.measure(f)),
            "successor": [list(c) for c in after],
            "successor_hash": formula_hash(after),
            "successor_CLV": list(r33.measure(after)),
            "successor_max_width": max_width(after),
            "strict_CLV_descent": True,
            "transition_certificate": {"R33_result": reduced},
            "tranception_reverse_contract": "SUCCESSOR_SAT_WITNESS -> r33.reconstruct_model(R33_result) -> PREDECESSOR_SAT_WITNESS",
        }
    return None


def exact_step(formula):
    """One exact R50A successor step over an explicit persisted width-4 state.

    Order is authority order, not a heuristic preference:
      1. existing certified R33 reduction/terminal;
      2. theorem-authorized operational tokens (all tokens exposed exactly);
      3. exact exhaustive R47J fallback in ascending variable-id order;
      4. explicit OPEN obstruction if every current pivot has been checked.
    """
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise ValueError("R50A_DOMAIN_IS_PERSISTED_MAX_WIDTH_LE_4")

    r33_step = _r33_first(f)
    if r33_step is not None:
        return r33_step

    tokens = expose_exact_tokens(f)
    for token in tokens:
        if token["direct_exact_dp_authorized"]:
            step = _direct_dp_transition(f, token)
            step["exposed_token_count"] = len(tokens)
            step["direct_authorized_token_count"] = sum(int(t["direct_exact_dp_authorized"]) for t in tokens)
            return step

    attempts = []
    for var in sorted(r33.variables(f)):
        row, candidate = _fallback_candidate(f, int(var))
        attempts.append(row)
        if not row["width4_safe"]:
            continue
        replay = r47j.independent_fixpoint_macro_replay(f, candidate)
        if not replay["pass"]:
            raise AssertionError(("R50A_FALLBACK_REPLAY_FAIL", var, replay))
        final = canon(candidate["normalization"]["final_formula"])
        terminal = candidate["normalization"]["terminal"]
        result = {
            "kind": "TERMINAL" if terminal is not None else "NONTERMINAL",
            "lane": "EXHAUSTIVE_R47J_FIRST_CERTIFIED_WIDTH4_DESCENT",
            "selection_policy": "ASCENDING_VARIABLE_ID_ONLY__NO_SCORE__NO_RANKER",
            "heuristic_ranking_used": False,
            "input_hash": formula_hash(f),
            "input_CLV": list(r33.measure(f)),
            "exposed_token_count": len(tokens),
            "direct_authorized_token_count": 0,
            "fallback_attempts_before_accept": attempts,
            "selected_pivot": int(var),
            "successor": [list(c) for c in final],
            "successor_hash": formula_hash(final),
            "successor_CLV": list(r33.measure(final)),
            "successor_max_width": max_width(final),
            "terminal": terminal,
            "semantic_sat": candidate["normalization"]["semantic_sat"],
            "transition_certificate": {"R47J_candidate": candidate, "independent_replay": replay},
            "tranception_reverse_contract": "R47J_SUCCESSOR_WITNESS -> reverse R33 reconstruction records -> exact DP reconstruction -> PREDECESSOR_WITNESS",
        }
        if terminal is not None and candidate["normalization"]["semantic_sat"] is True:
            result["SAT_assignment"] = candidate["SAT_reconstruction"].get("assignment")
        return result

    return {
        "kind": "OPEN_OBSTRUCTION",
        "lane": "EXACT_EXHAUSTIVE_NO_WIDTH4_SUCCESSOR_UNDER_CURRENT_MACHINE",
        "heuristic_ranking_used": False,
        "input_hash": formula_hash(f),
        "input_CLV": list(r33.measure(f)),
        "exposed_tokens": tokens,
        "fallback_attempts": attempts,
        "all_current_variables_checked": True,
        "claim": "CURRENT_R50A_MACHINE_HAS_NO_CERTIFIED_WIDTH4_SUCCESSOR_FROM_THIS_STATE",
        "not_claimed": "NO_SUCCESSOR_IN_ALL_POSSIBLE_PROOF_SYSTEMS",
    }


def reverse_sat_witness(before_formula, step, successor_assignment):
    """Tranception made literal and exact: replay a SAT witness backward one step."""
    before = canon(before_formula)
    if step["kind"] != "NONTERMINAL":
        raise ValueError("R50A_REVERSE_REQUIRES_NONTERMINAL_STEP")
    successor = canon(step["successor"])
    assignment = {int(k): bool(v) for k, v in successor_assignment.items()}
    if not r33.eval_formula(successor, assignment):
        raise AssertionError("R50A_REVERSE_INPUT_IS_NOT_SUCCESSOR_MODEL")

    if step["lane"] == "R33_CERTIFIED_REDUCTION":
        lifted = r33.reconstruct_model(step["transition_certificate"]["R33_result"], assignment)
    elif step["lane"] == "BLUEFIELD_EXACT_TOKEN__R49H_DIRECT_DP":
        lifted = r42.reconstruct_sa_bve(step["transition_certificate"]["DP"], assignment)
    elif step["lane"] == "EXHAUSTIVE_R47J_FIRST_CERTIFIED_WIDTH4_DESCENT":
        candidate = step["transition_certificate"]["R47J_candidate"]
        lifted = dict(assignment)
        for result in reversed(candidate["normalization"]["R33_reconstruction_results"]):
            lifted = r33.reconstruct_model(result, lifted)
        lifted = r42.reconstruct_sa_bve(candidate["DP"], lifted)
    else:
        raise ValueError(("R50A_UNKNOWN_REVERSE_LANE", step["lane"]))

    missing = set(r33.variables(before)) - set(lifted)
    for var in sorted(missing):
        lifted[var] = False
    if not r33.eval_formula(before, lifted):
        raise AssertionError("R50A_REVERSE_PREDECESSOR_MODEL_FAIL")
    return {"pass": True, "assignment": lifted}


def _first_model(formula):
    f = canon(formula)
    variables = list(r33.variables(f))
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if r33.eval_formula(f, assignment):
            return assignment
    return None


def demo():
    # Small bipolar parity-style control: no random generation and no learned choice.
    formula = canon([
        (1, 2, 3),
        (-1, 2, -3),
        (1, -2, -3),
        (-1, -2, 3),
    ])
    step = exact_step(formula)
    reverse = None
    if step["kind"] == "NONTERMINAL":
        model = _first_model(step["successor"])
        if model is not None:
            reverse = reverse_sat_witness(formula, step, model)
    return {
        "gate": GATE,
        "verdict": "PASS" if step["heuristic_ranking_used"] is False else "FAIL",
        "demo_input_hash": formula_hash(formula),
        "demo_lane": step["lane"],
        "demo_kind": step["kind"],
        "reverse_witness_pass": None if reverse is None else bool(reverse["pass"]),
        "machine_contract": {
            "blue_field": "EXPOSE_ALL_EXACT_OPERATIONAL_TOKENS__NO_PROBABILISTIC_RANKING",
            "ya_mama_carrier": "TOKEN_CARRIES_ACTION_BUT_MUST_BE_RECOMPUTED_BEFORE_EXECUTION",
            "tranception": "EVERY_ACCEPTED_FORWARD_TRANSITION_HAS_INDEPENDENT_REPLAY_AND_SAT_WITNESS_RETURN_PATH",
            "dougan_direction": "R33_STRICT_CLV_DESCENT_OR_DP_STRICT_VARIABLE_DESCENT",
            "freestyler_remote": "FORWARD_AND_REVERSE_ARE_CERTIFICATE_OPERATIONS_NOT_TIME_TRAVEL",
            "attractor_control": "NO_LEARNED_OR_SEMANTIC_NUMERIC_PREFERENCE",
        },
        "firewall": {
            "HEURISTIC_RANKER_AUTHORITY": False,
            "ML_MODEL_AUTHORITY": False,
            "RANDOM_SAMPLING_AUTHORITY": False,
            "UNIVERSAL_W4_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    out = demo()
    path = Path("artifacts/JANUS_TRUMP_R50A_EXACT_OPERATIONAL_TOKEN_TRANCEPTION_CONTROLLER_RESULT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
