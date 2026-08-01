from __future__ import annotations

import hashlib
import random

from sat_core import SATInstance, common_diag
from config_anchor import V20Config, complete_sign_core_witness, AnchorLane
from gladius_selective import GladiusSelectiveLane
from zim_adaptive import ZimAdaptiveLane


def janus_pn_swarm_v20(inst: SATInstance, initial: list[int], budget: int, rng: random.Random, cfg: V20Config = V20Config()):
    """Run Anchor, Gladius and optional Zim in parallel-round semantics.

    `steps` is first-solution latency in rounds. `aggregate_work_flips` counts
    all committed and probe flips, so parallelism is never presented as free.
    """
    witness = complete_sign_core_witness(inst) if cfg.proof_scan else None
    if witness is not None:
        return False, 0, len(inst.clauses) - 1, common_diag(
            no_recombination_state="PROVEN_NO_RECOMBINATION",
            no_recombination_witness=witness,
            winner="NONE",
            parallel_ticks=0,
            anchor_committed_flips=0,
            gladius_committed_flips=0,
            probe_flips=0,
            aggregate_work_flips=0,
            pn_packets=1,
        )

    anchor_rng = random.Random(); anchor_rng.setstate(rng.getstate())
    zim_rng = random.Random(); zim_rng.setstate(rng.getstate())
    seed_material = bytes(initial) + inst.n.to_bytes(4, "big") + len(inst.clauses).to_bytes(4, "big") + b"GLADIUS_V20"
    gladius_seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")

    anchor = AnchorLane(inst, initial, anchor_rng)
    gladius = GladiusSelectiveLane(inst, initial, random.Random(gladius_seed), cfg)
    k_guess = len(inst.clauses[0]) if inst.clauses else 0
    zim = ZimAdaptiveLane(inst, initial, zim_rng) if (k_guess == 3 and inst.n >= cfg.enable_zim_from_n) else None
    pn_packets = 0
    winner = "NONE"
    ticks = 0

    for ticks in range(1, budget + 1):
        anchor.tick()
        gladius.tick(anchor.best, anchor.best_assignment)
        if zim is not None:
            zim.tick()
        active_nodes = 2 + int(zim is not None)
        if ticks % cfg.telemetry_period_ticks == 0:
            pn_packets += active_nodes
        solved_nodes = []
        if anchor.solved: solved_nodes.append("ANCHOR")
        if gladius.solved: solved_nodes.append("GLADIUS")
        if zim is not None and zim.solved: solved_nodes.append("ZIM")
        if solved_nodes:
            winner = "+".join(solved_nodes)
            break

    solved = anchor.solved or gladius.solved or (zim is not None and zim.solved)
    best = max(anchor.best, gladius.best, zim.best if zim is not None else 0)
    gd = gladius.diag()
    aggregate = anchor.committed_flips + gladius.committed_flips + gladius.probe_flips + (zim.committed_flips + zim.probe_flips if zim is not None else 0)
    gd.update(
        no_recombination_state="RECOMBINATION_FOUND" if solved else "SEARCH_EXHAUSTED_NO_PROOF",
        no_recombination_witness=None,
        winner=winner,
        parallel_ticks=ticks,
        anchor_ticks=anchor.ticks,
        gladius_ticks=gladius.ticks,
        zim_enabled=zim is not None,
        zim_ticks=zim.ticks if zim is not None else 0,
        anchor_committed_flips=anchor.committed_flips,
        gladius_committed_flips=gladius.committed_flips,
        zim_committed_flips=zim.committed_flips if zim is not None else 0,
        anchor_escapes=anchor.escapes,
        probe_flips=gladius.probe_flips + (zim.probe_flips if zim is not None else 0),
        gladius_probe_flips=gladius.probe_flips,
        zim_probe_flips=zim.probe_flips if zim is not None else 0,
        aggregate_work_flips=aggregate,
        pn_packets=pn_packets,
        work_per_parallel_tick=aggregate / max(1, ticks),
        anchor_best_ratio=anchor.best / max(1, len(inst.clauses)),
        gladius_best_ratio=gladius.best / max(1, len(inst.clauses)),
        zim_best_ratio=(zim.best / max(1, len(inst.clauses))) if zim is not None else None,
    )
    return solved, ticks, best, gd
