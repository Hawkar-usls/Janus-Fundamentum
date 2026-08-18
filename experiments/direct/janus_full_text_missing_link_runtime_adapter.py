#!/usr/bin/env python3
"""Runtime adapter binding the new missing-link assembly to the exact PR197 machine.

This file is intentionally not executed in the assembly phase. The later promotion
harness must call bind_parent_runtime() first; if the inherited PR197 runtime drifts,
the full missing-link run must stop before evaluating any new stage.
"""
from __future__ import annotations

from typing import Any

from janus_pt350_351_352_atomic_triad_head_tail import run as run_pr197_parent
from janus_full_text_missing_link_assembly import (
    FORWARD,
    BACK,
    PARENT_SHA,
    PARENT_PR,
    assembly_manifest,
    link_forward,
    link_back,
)

EXPECTED_PARENT_STATUS = "PASS_KEEP_PT350_352_ATOMIC_TRIAD"
EXPECTED_PARENT_FORWARD = ["PT350","PT351","PT352","PT353","PT354","PT355","PT366","PT477","PT222"]
EXPECTED_PARENT_BACK = ["PT222","PT477","PT366","PT355","PT354","PT353","PT352","PT351","PT350"]
EXPECTED_PARENT_MIRRORS = 9


def bind_parent_runtime() -> dict[str, Any]:
    """Execute only when the later test phase explicitly calls this adapter."""
    parent = run_pr197_parent()
    gates = parent.get("gates", {})
    checks = {
        "parent_status_exact": parent.get("status") == EXPECTED_PARENT_STATUS,
        "parent_forward_exact": parent.get("FORWARD", {}).get("execution") == EXPECTED_PARENT_FORWARD,
        "parent_back_exact": parent.get("BACK", {}).get("execution") == EXPECTED_PARENT_BACK,
        "parent_9_of_9_exact": (
            parent.get("FORWARD_AGAIN", {}).get("mirror_passes") == EXPECTED_PARENT_MIRRORS
            and parent.get("FORWARD_AGAIN", {}).get("mirror_total") == EXPECTED_PARENT_MIRRORS
        ),
        "parent_all_gates_true": bool(gates) and all(bool(v) for v in gates.values()),
        "parent_p_vs_np_open": parent.get("mathematical_verdict", {}).get("P_VS_NP") == "OPEN",
    }
    return {
        "bound": all(checks.values()),
        "checks": checks,
        "parent_pr": PARENT_PR,
        "parent_sha_expected": PARENT_SHA,
        "parent_status": parent.get("status"),
        "parent_integrity_sha256": parent.get("integrity_sha256"),
        "parent_result": parent,
    }


def assemble_bound_machine(initial_anchor: str, parent_binding: dict[str, Any]) -> dict[str, Any]:
    """Link new stages only after exact parent binding. Still not a promotion verdict."""
    if not parent_binding.get("bound"):
        raise RuntimeError("PR197 parent binding failed; missing-link assembly is not authorized")
    fwd = link_forward(initial_anchor)
    back = link_back(fwd)
    return {
        "status": "ASSEMBLED_AND_PARENT_BOUND_NOT_YET_PROMOTION_TESTED",
        "parent_binding_checks": parent_binding["checks"],
        "assembly": assembly_manifest(),
        "forward_order": [env.stage for env in fwd],
        "back_order": [env.stage for env in back],
        "forward_terminal_commitment": fwd[-1].commitment,
        "back_terminal_commitment": back[-1].commitment,
        "forward_stage_count": len(fwd),
        "back_stage_count": len(back),
        "P_VS_NP": "OPEN",
    }


if __name__ == "__main__":
    raise SystemExit(
        "ASSEMBLY PHASE ONLY: do not execute parent/promotion run yet. "
        "Use this adapter from the separately frozen test harness in the next phase."
    )
