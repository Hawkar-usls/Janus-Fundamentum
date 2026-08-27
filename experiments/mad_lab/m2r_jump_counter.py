#!/usr/bin/env python3
"""M2R pre-action counter / jump gate for JANUS MAD-LAB.

EXPERIMENTAL ONLY. NOT A THEOREM COMPONENT.

The gate evaluates a proposed abstract elimination action *before* it is taken.
It may veto an action whose frozen theorem-side upper bound exceeds N^2 and may
select another supplied cap-safe action. It never invents an action and never
turns a veto into a truth claim.

Important semantics:
- LAND: the supplied upper bound is cap-safe.
- JUMP: primary action is vetoed; another *supplied* cap-safe action is chosen.
- OPEN: no supplied action is certified cap-safe. Record the obstruction.

A JUMP is action-level. It does NOT skip a failed N and does NOT advance the
finite theorem frontier.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isqrt
from typing import Callable, Iterable

from experiments.direct.janus_v05_abstract_frontier_global_raw_universe import (
    transfer_bounds_global,
)

LANE = "JANUS_MAD_LAB"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
AUTOMATIC_PROMOTION = False

Bounder = Callable[[int, int, int, int, int, int], tuple[int, int, int, int]]


@dataclass(frozen=True)
class ActionCandidate:
    N: int
    n: int
    m: int
    L: int
    d: int
    p: int
    q: int
    label: str = ""

    def __post_init__(self) -> None:
        if self.N < 2:
            raise ValueError("N must be >= 2")
        if self.n < 1 or self.m < 0 or self.L < 0 or self.d < 0:
            raise ValueError("invalid nonnegative abstract state")
        if self.p < 0 or self.q < 0 or self.p + self.q != self.d:
            raise ValueError("p+q must equal d")


@dataclass(frozen=True)
class M2RDecision:
    action: ActionCandidate
    verdict: str
    cap: int
    raw_bound: int
    margin: int
    jump_debt: int
    minimum_N_for_this_bound: int
    m_out_bound: int
    L_out_bound: int
    resolvent_bound: int
    lane: str = LANE
    status: str = STATUS
    P_VS_NP: str = P_VS_NP
    automatic_promotion: bool = AUTOMATIC_PROMOTION


class M2RJumpCounter:
    """Backward obligation gate with veto power only.

    The counter asks one question before an action:
        "Does the frozen upper bound fit under the current N^2 cap?"

    It does not prove the action is necessary, optimal, or semantically true.
    """

    def __init__(self, bounder: Bounder = transfer_bounds_global) -> None:
        self.bounder = bounder
        self.actions_seen = 0
        self.landed = 0
        self.jumped = 0
        self.vetoed = 0
        self.open = 0
        self.cumulative_jump_debt = 0
        self.max_jump_debt = 0

    def assess(self, action: ActionCandidate) -> M2RDecision:
        raw, M, Lb, R = self.bounder(
            action.n, action.m, action.L, action.d, action.p, action.q
        )
        cap = action.N * action.N
        margin = cap - raw
        debt = max(0, -margin)
        min_N = isqrt(max(0, raw - 1)) + 1
        verdict = "LAND" if raw <= cap else "VETO"
        return M2RDecision(
            action=action,
            verdict=verdict,
            cap=cap,
            raw_bound=raw,
            margin=margin,
            jump_debt=debt,
            minimum_N_for_this_bound=min_N,
            m_out_bound=M,
            L_out_bound=Lb,
            resolvent_bound=R,
        )

    def pre_action(self, primary: ActionCandidate, alternatives: Iterable[ActionCandidate] = ()) -> dict:
        """Assess primary first; if vetoed, jump to a supplied safe alternative.

        Alternatives must describe the same abstract state and N. The gate never
        fabricates pivots/splits. Canonical fallback is lexicographic over the
        action tuple, not a learned or semantic score.
        """
        self.actions_seen += 1
        primary_decision = self.assess(primary)
        if primary_decision.verdict == "LAND":
            self.landed += 1
            return {
                "verdict": "LAND",
                "selected": asdict(primary_decision),
                "primary": asdict(primary_decision),
                "counter": self.snapshot(),
            }

        self.vetoed += 1
        self.cumulative_jump_debt += primary_decision.jump_debt
        self.max_jump_debt = max(self.max_jump_debt, primary_decision.jump_debt)

        pool: list[M2RDecision] = []
        for alt in alternatives:
            if (alt.N, alt.n, alt.m, alt.L) != (primary.N, primary.n, primary.m, primary.L):
                raise ValueError("jump alternatives must belong to the same N/state")
            d = self.assess(alt)
            if d.verdict == "LAND":
                pool.append(d)

        if pool:
            pool.sort(
                key=lambda x: (
                    x.action.d,
                    x.action.p,
                    x.action.q,
                    x.action.label,
                )
            )
            selected = pool[0]
            self.jumped += 1
            return {
                "verdict": "JUMP",
                "selected": asdict(selected),
                "primary": asdict(primary_decision),
                "safe_alternatives_seen": len(pool),
                "counter": self.snapshot(),
            }

        self.open += 1
        return {
            "verdict": "OPEN",
            "selected": None,
            "primary": asdict(primary_decision),
            "reason": "NO_SUPPLIED_CAP_SAFE_ACTION__OBSTRUCTION_MUST_BE_RECORDED",
            "counter": self.snapshot(),
        }

    def snapshot(self) -> dict:
        return {
            "actions_seen": self.actions_seen,
            "landed": self.landed,
            "jumped": self.jumped,
            "vetoed": self.vetoed,
            "open": self.open,
            "cumulative_jump_debt": self.cumulative_jump_debt,
            "max_jump_debt": self.max_jump_debt,
            "lane": LANE,
            "status": STATUS,
            "P_VS_NP": P_VS_NP,
        }


def selftest() -> None:
    gate = M2RJumpCounter()

    # Current N58 calibration obstruction: preflight sees the hole before action.
    primary = ActionCandidate(58, 7, 78, 350, 50, 24, 26, "N58_24x26")
    d = gate.assess(primary)
    assert d.raw_bound == 3425, d
    assert d.cap == 3364
    assert d.jump_debt == 61
    assert d.verdict == "VETO"

    # Synthetic supplied alternative for jump-mechanics calibration only.
    # This is NOT a claim that such a pivot exists in the actual N58 CNF.
    alternative = ActionCandidate(58, 7, 78, 350, 50, 0, 50, "synthetic_pure_sign")
    out = gate.pre_action(primary, [alternative])
    assert out["verdict"] == "JUMP", out
    assert out["selected"]["raw_bound"] <= 58 * 58

    # Without a certified supplied route, fail closed.
    gate2 = M2RJumpCounter()
    out2 = gate2.pre_action(primary, [])
    assert out2["verdict"] == "OPEN", out2

    print("MAD_LAB_M2R_PREFLIGHT=PASS")
    print("N58_24X26_RAW_BOUND=3425")
    print("N58_24X26_CAP=3364")
    print("N58_24X26_JUMP_DEBT=61")
    print("M2R_HAS_VETO_NOT_TRUTH_POWER")
    print("JUMP_IS_ACTION_LEVEL_NOT_N_SKIP")
    print("NO_SAFE_ACTION_FAILS_CLOSED=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
