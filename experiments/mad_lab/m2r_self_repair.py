#!/usr/bin/env python3
"""Proof-gated M2R self-repair layer for JANUS MAD-LAB.

The surgeon may tighten an action only with already-existing exact theorem-side
bounds/lemmas. If those do not close the cap, it emits a proof obligation and
fails OPEN. It never promotes a freshly invented lemma during the same run.

This is deliberately stricter than a heuristic self-healer: a candidate repair
can be *generated* for later study, but cannot be *used* until a separate exact
proof artifact/provider exists.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from experiments.direct.janus_v05_abstract_frontier_global_raw_universe import transfer_bounds_global
from experiments.direct import janus_v05_abstract_frontier_N58_23x27_projection_fiber as PROVED_CHAIN
from experiments.mad_lab.m2r_jump_counter import ActionCandidate

LANE = "JANUS_MAD_LAB"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"


@dataclass(frozen=True)
class RepairResult:
    verdict: str
    N: int
    action_label: str
    cap: int
    base_raw: int
    final_raw: int
    improvement: int
    provider: str
    proof_gated: bool
    rollback_required: bool
    proof_obligation: dict | None
    lane: str = LANE
    status: str = STATUS
    P_VS_NP: str = P_VS_NP


class M2RSurgeon:
    """Exact self-repair controller with rollback and fail-closed semantics."""

    PROVED_PROVIDER = "THEOREM_SIDE_INCIDENCE_SURPLUS_PLUS_PROVED_N58_RESCUES_THROUGH_23X27"

    def repair(self, action: ActionCandidate) -> RepairResult:
        base_raw, _, _, _ = transfer_bounds_global(
            action.n, action.m, action.L, action.d, action.p, action.q
        )
        cap = action.N * action.N

        if base_raw <= cap:
            return RepairResult(
                verdict="LAND_NO_REPAIR",
                N=action.N,
                action_label=action.label,
                cap=cap,
                base_raw=base_raw,
                final_raw=base_raw,
                improvement=0,
                provider="GLOBAL_RAW_BASE",
                proof_gated=True,
                rollback_required=False,
                proof_obligation=None,
            )

        candidate = PROVED_CHAIN.enhanced_rescue(
            action.n, action.m, action.L, action.d, action.p, action.q
        )
        if candidate is not None:
            repaired_raw = int(candidate[0])
            if repaired_raw < 0:
                raise AssertionError("negative repaired bound")
            # A repair provider is allowed to tighten, never to silently worsen.
            final_raw = min(base_raw, repaired_raw)
            provider = self.PROVED_PROVIDER if repaired_raw < base_raw else "NO_EXACT_IMPROVEMENT"
        else:
            final_raw = base_raw
            provider = "NO_EXACT_REPAIR_PROVIDER"

        if final_raw <= cap:
            return RepairResult(
                verdict="REPAIRED_LAND",
                N=action.N,
                action_label=action.label,
                cap=cap,
                base_raw=base_raw,
                final_raw=final_raw,
                improvement=base_raw-final_raw,
                provider=provider,
                proof_gated=True,
                rollback_required=False,
                proof_obligation=None,
            )

        obligation = {
            "state": [action.n, action.m, action.L],
            "action": {"d": action.d, "p": action.p, "q": action.q},
            "cap": cap,
            "best_exact_raw_known": final_raw,
            "jump_debt": final_raw-cap,
            "required": "SEPARATE_EXACT_LEMMA_OR_CERTIFIED_ALTERNATIVE_ACTION",
            "same_run_candidate_use": "FORBIDDEN",
            "falsification_first": True,
        }
        return RepairResult(
            verdict="OPEN_REPAIR_REQUIRED",
            N=action.N,
            action_label=action.label,
            cap=cap,
            base_raw=base_raw,
            final_raw=final_raw,
            improvement=base_raw-final_raw,
            provider=provider,
            proof_gated=False,
            rollback_required=True,
            proof_obligation=obligation,
        )

    def as_record(self, action: ActionCandidate) -> dict:
        return asdict(self.repair(action))


def selftest() -> None:
    s = M2RSurgeon()

    # Three theorem-side rescues are already proved on the frozen N58 branch.
    for p, q in ((21, 29), (22, 28), (23, 27)):
        a = ActionCandidate(58, 7, 78, 350, 50, p, q, f"N58_{p}x{q}")
        r = s.repair(a)
        assert r.final_raw <= 3364, r
        assert r.verdict in ("REPAIRED_LAND", "LAND_NO_REPAIR"), r
        assert r.rollback_required is False

    # The next obstruction must remain OPEN: no self-deception / no same-run lemma invention.
    a = ActionCandidate(58, 7, 78, 350, 50, 24, 26, "N58_24x26")
    r = s.repair(a)
    assert r.verdict == "OPEN_REPAIR_REQUIRED", r
    assert r.final_raw == 3425, r
    assert r.proof_obligation["jump_debt"] == 61
    assert r.rollback_required is True
    assert r.proof_obligation["same_run_candidate_use"] == "FORBIDDEN"

    print("M2R_SURGEON_PROVED_REPAIR_CHAIN=PASS")
    print("M2R_SURGEON_24X26_FAILS_CLOSED=PASS")
    print("SAME_RUN_LEMMA_PROMOTION=FORBIDDEN")
    print("ROLLBACK_ON_UNPROVED_REPAIR=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
