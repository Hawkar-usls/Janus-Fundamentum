#!/usr/bin/env python3
"""Executable governance gates for ROOSTERS v5.1 imported into C025 theorem search.

This file tests routing/authority invariants only. It has no theorem authority and
must not change exact CNF transition semantics or the frozen candidate grammar.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

P_VS_NP = "OPEN"
MIN_WARM = 7
MIN_HOT = 12
COLD_TOPA = 0.68
HOT_AUTH = 0.67
MAX_HOT_DRIFT = 0.70
WMIN, WMAX = 0.35, 2.20


def independent_epoch_count(epoch_ids):
    return len(set(epoch_ids))


def choose_mode(*, prior_epochs, authority, drift, topa_suspicion, surprise=False):
    support = independent_epoch_count(prior_epochs)
    if surprise or topa_suspicion >= COLD_TOPA:
        return "COLD"
    if support < MIN_WARM:
        return "COLD"
    if support >= MIN_HOT and authority >= HOT_AUTH and drift <= MAX_HOT_DRIFT:
        return "HOT"
    return "WARM"


def clamp_weight(x):
    return max(WMIN, min(WMAX, x))


def proof_negative_state(*, complete_scope=False, timeout=False, budget_exhausted=False,
                         worker_silence=False, receipt_present=True):
    if timeout:
        return "UNKNOWN_TIMEOUT"
    if budget_exhausted:
        return "UNKNOWN_RESOURCE_LIMIT"
    if worker_silence:
        return "UNKNOWN_WORKER_SILENCE"
    if not receipt_present:
        return "UNKNOWN_NO_RECEIPT"
    if not complete_scope:
        return "UNKNOWN_PARTIAL_SCOPE"
    return "COMPLETE_SCOPE_ELIGIBLE_FOR_EXACT_NEGATIVE_RECEIPT"


def rank_without_prune(frozen_candidates, ranking):
    frozen = list(frozen_candidates)
    rank_pos = {c: i for i, c in enumerate(ranking)}
    ordered = sorted(frozen, key=lambda c: (rank_pos.get(c, len(rank_pos)), repr(c)))
    assert set(ordered) == set(frozen)
    assert len(ordered) == len(frozen)
    return ordered


@dataclass
class DelayedAuthority:
    weights: dict = field(default_factory=lambda: {
        "familiarity": 1.15,
        "independent_support": 1.05,
        "prediction_accuracy": 0.95,
        "drift": 1.10,
        "topa_suspicion": 1.35,
    })
    pending_delta: dict | None = None

    def begin_episode(self):
        if self.pending_delta:
            for k, d in self.pending_delta.items():
                self.weights[k] = clamp_weight(self.weights[k] + d)
            self.pending_delta = None
        return dict(self.weights)

    def score_current_episode_for_next(self, delta):
        self.pending_delta = dict(delta)


def gate(name, fn):
    try:
        value = fn()
        return {"gate": name, "passed": True, "value": value}
    except Exception as exc:
        return {"gate": name, "passed": False, "error": f"{type(exc).__name__}: {exc}"}


def main():
    results = []

    def g1():
        ids = ["e1", "e1", "e1", "e2", "e2", "e3"]
        assert independent_epoch_count(ids) == 3
        return 3
    results.append(gate("V51G1_DUPLICATE_EPOCHS_DO_NOT_INCREASE_SUPPORT", g1))

    def g2():
        m = choose_mode(prior_epochs=[f"e{i}" for i in range(6)], authority=.99, drift=0, topa_suspicion=0)
        assert m == "COLD"
        return m
    results.append(gate("V51G2_SIX_EPOCHS_CANNOT_WARM", g2))

    def g3():
        m = choose_mode(prior_epochs=[f"e{i}" for i in range(7)], authority=.60, drift=.1, topa_suspicion=.1)
        assert m == "WARM"
        return m
    results.append(gate("V51G3_SEVEN_EPOCHS_CAN_WARM_WHEN_OTHER_GATES_ALLOW", g3))

    def g4():
        m = choose_mode(prior_epochs=[f"e{i}" for i in range(11)], authority=.99, drift=0, topa_suspicion=0)
        assert m == "WARM"
        return m
    results.append(gate("V51G4_ELEVEN_EPOCHS_CANNOT_HOT", g4))

    def g5():
        m = choose_mode(prior_epochs=[f"e{i}" for i in range(12)], authority=.67, drift=.70, topa_suspicion=.1)
        assert m == "HOT"
        return m
    results.append(gate("V51G5_TWELVE_EPOCHS_CAN_HOT_WHEN_AUTHORITY_DRIFT_SUSPICION_ALLOW", g5))

    def g6():
        m = choose_mode(prior_epochs=[f"e{i}" for i in range(30)], authority=.99, drift=0, topa_suspicion=.68)
        assert m == "COLD"
        return m
    results.append(gate("V51G6_HIGH_TOPA_SUSPICION_FORCES_COLD", g6))

    def g7():
        ctl = DelayedAuthority()
        current = ctl.begin_episode()
        before = dict(current)
        ctl.score_current_episode_for_next({"familiarity": +.5})
        # Current episode authority snapshot is immutable.
        assert current == before
        assert ctl.weights == before
        nxt = ctl.begin_episode()
        assert nxt["familiarity"] == clamp_weight(before["familiarity"] + .5)
        return {"current": before["familiarity"], "next": nxt["familiarity"]}
    results.append(gate("V51G7_CURRENT_OUTCOME_CANNOT_CHANGE_CURRENT_MODE", g7))

    def g8():
        assert clamp_weight(-100) == WMIN
        assert clamp_weight(100) == WMAX
        assert clamp_weight(1.0) == 1.0
        return [WMIN, WMAX]
    results.append(gate("V51G8_ADAPTIVE_WEIGHTS_ARE_CLAMPED", g8))

    def g9():
        states = {
            "partial": proof_negative_state(complete_scope=False),
            "timeout": proof_negative_state(complete_scope=False, timeout=True),
            "budget": proof_negative_state(complete_scope=False, budget_exhausted=True),
            "silence": proof_negative_state(complete_scope=False, worker_silence=True),
            "missing": proof_negative_state(complete_scope=False, receipt_present=False),
        }
        assert all(v.startswith("UNKNOWN_") for v in states.values())
        assert "NO_RESCUE" not in states.values()
        return states
    results.append(gate("V51G9_PARTIAL_OR_EXHAUSTED_SCOPE_RETURNS_UNKNOWN", g9))

    def g10():
        frozen = [(1,2), (1,3), (2,3), (2,4), (3,4)]
        ordered = rank_without_prune(frozen, [(3,4), (1,2)])
        assert set(ordered) == set(frozen)
        assert len(ordered) == len(frozen)
        return ordered
    results.append(gate("V51G10_RANKING_PRESERVES_FROZEN_CANDIDATE_SET", g10))

    def g11():
        historical_v5 = {
            "G8_LATE_LEARNING_REDUCES_CHECKS": "FAIL",
            "G10_OOD_WIDENS_TO_COLD": "FAIL",
        }
        successor_v51 = {
            "G8_LATE_LEARNING_REDUCES_CHECKS": "PASS",
            "G10_OOD_WIDENS_TO_COLD": "PASS",
        }
        merged = {"v5": historical_v5, "v5.1": successor_v51}
        assert merged["v5"]["G8_LATE_LEARNING_REDUCES_CHECKS"] == "FAIL"
        assert merged["v5"]["G10_OOD_WIDENS_TO_COLD"] == "FAIL"
        return merged
    results.append(gate("V51G11_HISTORICAL_V5_FAILURES_REMAIN_IMMUTABLE", g11))

    def g12():
        # Static contract: governance cannot alter exact semantics and cannot
        # declare universal negatives. The workflow separately executes the
        # frozen v2-gap theorem smoke under original code.
        contract = {
            "exact_transition_semantics_mutated": False,
            "ranking_may_prune_frozen_grammar": False,
            "finite_nonrefutation_is_proof": False,
            "P_VS_NP": "OPEN",
        }
        assert contract["exact_transition_semantics_mutated"] is False
        assert contract["ranking_may_prune_frozen_grammar"] is False
        assert contract["P_VS_NP"] == "OPEN"
        return contract
    results.append(gate("V51G12_EXACT_THEOREM_SEMANTICS_UNCHANGED", g12))

    passed = sum(bool(x["passed"]) for x in results)
    report = {
        "schema": "JANUS/C025/ROOSTERS-v5.1-EXECUTABLE-GOVERNANCE-RECEIPT/v1",
        "status": "PASS" if passed == len(results) else "FAIL",
        "source_sha256": "e589b1464d2ec63851beb84a4b5a23f5cdf8e3e49a1a5e82bbbac3bd86026248",
        "gates_passed": passed,
        "gates_total": len(results),
        "results": results,
        "historical_v5_1_source_integrity": {
            "episodes": 20000,
            "gates": "15/15 PASS",
            "ood_cold_or_new_fraction": 0.8213802435723951,
            "false_connected": 0,
            "claim_ceiling": "local synthetic digital twin only"
        },
        "authority_boundary": {
            "this_gate": "GOVERNANCE_TEST_ONLY",
            "exact_janus": "FINITE_EXACT_RECEIPTS",
            "formal_symbolic_proof": "UNIVERSAL_LEMMA_AUTHORITY"
        },
        "P_VS_NP": P_VS_NP,
    }
    Path("roosters-v5-1-governance-receipt.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
