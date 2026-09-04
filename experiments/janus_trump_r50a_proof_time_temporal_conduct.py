from __future__ import annotations

from typing import Any, Dict

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a

STYLE_PHASES = (
    "OBSERVE",
    "EXPOSE",
    "WAIT_FOR_AUTHORITY",
    "RECOMPUTE",
    "VERIFY",
    "EXECUTE",
    "REPLAY",
    "RETURN_OR_RECONSTRUCT",
    "SEAL_OR_REMAIN_OPEN",
)


def _event(events, phase: str, obligation: str, passed: bool = True) -> None:
    if phase not in STYLE_PHASES:
        raise ValueError(("R50A_UNKNOWN_STYLE_PHASE", phase))
    events.append({
        "logical_tick": len(events),
        "phase": phase,
        "obligation": obligation,
        "pass": bool(passed),
    })


def wait_for_authority(formula, carrier_token: Dict[str, Any]) -> Dict[str, Any]:
    """Refuse execution of a carrier before current-state authority is established.

    WAIT is a proof-state action, not a wall-clock delay.  The controller may still
    inspect other exact doors; waiting never authorizes skipping exhaustive lanes.
    """
    f = r50a.canon(formula)
    check = r50a.verify_operational_token(f, carrier_token)
    events = []
    _event(events, "OBSERVE", "bind the current explicit formula by hash")
    _event(events, "EXPOSE", "carrier token is visible but is not proof authority")
    _event(events, "WAIT_FOR_AUTHORITY", "do not execute before exact recomputation and verification")
    return {
        "status": "WAIT_FOR_AUTHORITY",
        "input_hash": r50a.formula_hash(f),
        "carrier_matches_current_recomputation": bool(check["pass"]),
        "execution_allowed": False,
        "wall_clock_used": False,
        "logical_time_only": True,
        "events": events,
    }


def authorize_after_recompute(formula, carrier_token: Dict[str, Any]) -> Dict[str, Any]:
    """Advance from WAIT to current exact authority, without executing the action."""
    f = r50a.canon(formula)
    check = r50a.verify_operational_token(f, carrier_token)
    authorized = bool(check["pass"] and check["recomputed"]["direct_exact_dp_authorized"])
    events = []
    _event(events, "WAIT_FOR_AUTHORITY", "carrier has no authority merely by being present")
    _event(events, "RECOMPUTE", "derive the token again from the current formula")
    _event(events, "VERIFY", "require carrier equality and the exact R49H sufficient condition", authorized)
    return {
        "status": "AUTHORIZED_CURRENT" if authorized else "WAIT_FOR_AUTHORITY",
        "input_hash": r50a.formula_hash(f),
        "carrier_matches_current_recomputation": bool(check["pass"]),
        "direct_exact_dp_authorized": bool(check["recomputed"]["direct_exact_dp_authorized"]),
        "execution_allowed": authorized,
        "wall_clock_used": False,
        "logical_time_only": True,
        "events": events,
    }


def audit_temporal_step(before_formula, step: Dict[str, Any]) -> Dict[str, Any]:
    """Proof-aligned temporal audit of an already produced R50A step.

    This layer adds no proof rule.  It checks that an accepted action was taken at
    a proof-state in which the existing R50A certificates already authorize it.
    """
    before = r50a.canon(before_formula)
    if step.get("input_hash") != r50a.formula_hash(before):
        raise AssertionError("R50A_STYLE_TIME_INPUT_HASH_DRIFT")
    if step.get("heuristic_ranking_used") is not False:
        raise AssertionError("R50A_STYLE_TIME_HEURISTIC_AUTHORITY")

    lane = step["lane"]
    events = []
    _event(events, "OBSERVE", "bind the current proof state")

    checks: Dict[str, bool] = {
        "input_hash_current": True,
        "heuristic_authority_absent": True,
    }

    if lane == "BLUEFIELD_EXACT_TOKEN__R49H_DIRECT_DP":
        _event(events, "EXPOSE", "all current exact tokens are exposed without ranking")
        _event(events, "WAIT_FOR_AUTHORITY", "carrier is not executable before recomputation")
        token_ok = bool(step["token_verification"]["pass"])
        _event(events, "RECOMPUTE", "selected token was exactly recomputed", token_ok)
        replay_ok = bool(step["transition_certificate"]["DP_independent_replay"]["pass"])
        envelope_ok = bool(step["transition_certificate"]["polynomial_intermediate_envelope"]["pass"])
        width_ok = int(step["successor_max_width"]) <= r50a.WIDTH_CAP
        descent_ok = bool(step["strict_variable_descent"])
        verify_ok = token_ok and replay_ok and envelope_ok and width_ok and descent_ok
        _event(events, "VERIFY", "R49H condition + DP replay + polynomial envelope + width/descent", verify_ok)
        _event(events, "EXECUTE", "canonical exact DP is executed only after VERIFY", verify_ok)
        _event(events, "REPLAY", "independent DP replay is present", replay_ok)
        return_ok = bool(step.get("tranception_reverse_contract"))
        _event(events, "RETURN_OR_RECONSTRUCT", "a SAT witness return path is declared", return_ok)
        _event(events, "SEAL_OR_REMAIN_OPEN", "seal this local transition only if all obligations passed", verify_ok and return_ok)
        checks.update({
            "token_recomputed": token_ok,
            "independent_replay": replay_ok,
            "polynomial_envelope": envelope_ok,
            "persisted_width": width_ok,
            "strict_descent": descent_ok,
            "return_path_available": return_ok,
        })

    elif lane == "EXHAUSTIVE_R47J_FIRST_CERTIFIED_WIDTH4_DESCENT":
        _event(events, "EXPOSE", "direct-token lane was empty; exact fallback doors are explicit")
        attempts = step["fallback_attempts_before_accept"]
        attempted = [int(row["pivot"]) for row in attempts]
        expected_prefix = list(sorted(r33.variables(before)))[:len(attempted)]
        order_ok = attempted == expected_prefix
        replay_ok = bool(step["transition_certificate"]["independent_replay"]["pass"])
        width_ok = int(step["successor_max_width"]) <= r50a.WIDTH_CAP
        _event(events, "VERIFY", "fallback candidates are checked in fixed order until first certified successor", order_ok and replay_ok and width_ok)
        _event(events, "EXECUTE", "execute only the independently replayed accepted fallback", replay_ok and width_ok)
        _event(events, "REPLAY", "R47J independent fixpoint replay is present", replay_ok)
        return_ok = bool(step.get("tranception_reverse_contract"))
        _event(events, "RETURN_OR_RECONSTRUCT", "return path is preserved for SAT witness reconstruction", return_ok)
        _event(events, "SEAL_OR_REMAIN_OPEN", "seal only the certified first successor", order_ok and replay_ok and width_ok and return_ok)
        checks.update({
            "fixed_order_prefix": order_ok,
            "independent_replay": replay_ok,
            "persisted_width": width_ok,
            "return_path_available": return_ok,
        })

    elif lane == "EXACT_EXHAUSTIVE_NO_WIDTH4_SUCCESSOR_UNDER_CURRENT_MACHINE":
        _event(events, "EXPOSE", "the current exact search domain is explicit")
        attempted = [int(row["pivot"]) for row in step["fallback_attempts"]]
        expected = list(sorted(r33.variables(before)))
        exhausted = bool(step["all_current_variables_checked"] and attempted == expected)
        _event(events, "VERIFY", "every required current pivot was checked before OPEN", exhausted)
        _event(events, "SEAL_OR_REMAIN_OPEN", "remain OPEN rather than invent authority", exhausted)
        checks.update({
            "all_current_variables_checked": exhausted,
            "no_execution_without_authority": True,
        })

    elif lane == "R33_CERTIFIED_REDUCTION":
        descent_ok = bool(step["strict_CLV_descent"])
        cert_ok = "R33_result" in step["transition_certificate"]
        _event(events, "VERIFY", "existing R33 certified reduction and strict CLV descent", cert_ok and descent_ok)
        _event(events, "EXECUTE", "persist the R33 successor only after its certified reduction", cert_ok and descent_ok)
        _event(events, "REPLAY", "R33 proof-carrying record is retained", cert_ok)
        return_ok = bool(step.get("tranception_reverse_contract"))
        _event(events, "RETURN_OR_RECONSTRUCT", "R33 reconstruction path is retained", return_ok)
        _event(events, "SEAL_OR_REMAIN_OPEN", "seal the local step only with descent and reconstruction path", cert_ok and descent_ok and return_ok)
        checks.update({"R33_certificate_present": cert_ok, "strict_descent": descent_ok, "return_path_available": return_ok})

    elif lane == "R33_CERTIFIED_TERMINAL":
        terminal_ok = bool(step["terminal_verification"]["verification_pass"])
        _event(events, "VERIFY", "declared R33 terminal is independently checked by the existing terminal verifier", terminal_ok)
        _event(events, "EXECUTE", "accept the terminal only after verification", terminal_ok)
        _event(events, "REPLAY", "terminal verification record is retained", terminal_ok)
        reconstruction_ok = True
        if step.get("semantic_sat") is True:
            reconstruction_ok = bool(step.get("SAT_assignment") is not None and r33.eval_formula(before, step["SAT_assignment"]))
        _event(events, "RETURN_OR_RECONSTRUCT", "SAT terminal reconstructs a predecessor witness; UNSAT fabricates none", reconstruction_ok)
        _event(events, "SEAL_OR_REMAIN_OPEN", "seal the terminal only after verification/reconstruction obligations", terminal_ok and reconstruction_ok)
        checks.update({"terminal_verified": terminal_ok, "terminal_reconstruction_ok": reconstruction_ok})

    else:
        raise ValueError(("R50A_STYLE_TIME_UNKNOWN_LANE", lane))

    passed = all(checks.values()) and all(bool(event["pass"]) for event in events)
    return {
        "schema": "R50A_PROOF_TIME_TEMPORAL_RECEIPT_V1",
        "status": "PASS" if passed else "FAIL",
        "lane": lane,
        "input_hash": r50a.formula_hash(before),
        "logical_time_only": True,
        "wall_clock_used": False,
        "style_law": "JANUS_STYLE = TIME = PROOF_ALIGNED_TEMPORAL_CONDUCT",
        "checks": checks,
        "events": events,
        "seal": "JANUS HAS STYLE WHEN JANUS KEEPS TIME WITH THE PROOF.",
    }


def audit_reverse_return(before_formula, step: Dict[str, Any], successor_assignment) -> Dict[str, Any]:
    receipt = audit_temporal_step(before_formula, step)
    replay = r50a.reverse_sat_witness(before_formula, step, successor_assignment)
    passed = bool(receipt["status"] == "PASS" and replay["pass"] and r33.eval_formula(r50a.canon(before_formula), replay["assignment"]))
    return {
        "status": "PASS" if passed else "FAIL",
        "temporal_receipt": receipt,
        "reverse_replay": replay,
        "seal": "RETURN COMPLETES THE STYLE OBLIGATION FOR THIS SAT TRANSITION.",
    }
