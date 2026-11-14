#!/usr/bin/env python3
"""JANUS-PENROSE-001: global schedule consistency and reversible uncompute audit.

Inspired by Penrose's *impossible staircase*: every edge can appear locally
valid as a strict ascent, while the closed loop has no global integer ranking.
This is a mathematical negative control for DAG-based reversible scheduling,
NOT a physical quantum effect and NOT a SAT solver.

The actual Deutsch-003 reversible circuit legitimately revisits the same
registers while uncomputing. Only cycles in STRICT EVENT DEPENDENCIES are
rejected; cycles through register values are not considered invalid.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Hashable, Iterable, Sequence

from janus_deutsch_003 import BlockOracle, GateStep


@dataclass(frozen=True)
class GlobalSchedule:
    consistent: bool
    ranks: tuple[tuple[str, int], ...]
    cycle_witness: tuple[str, ...]
    constraint_count: int

    def as_dict(self) -> dict:
        return {
            "consistent": self.consistent,
            "ranks": dict(self.ranks),
            "cycle_witness": list(self.cycle_witness),
            "constraint_count": self.constraint_count,
        }


def analyze_strict_precedence(nodes: Sequence[str],
                              steps: Iterable[tuple[str, str]]) -> GlobalSchedule:
    """Find h(v)>=h(u)+1 for EVERY edge u->v.

    A strictly increasing directed cycle is impossible by summing strict
    inequalities around the loop. For a DAG, longest-path ranks are a
    constructive independent satisfying witness. O(V+E), no SAT search.
    """
    if len(set(nodes)) != len(nodes) or not all(type(v) is str and v for v in nodes):
        raise ValueError("node identifiers must be unique, nonempty strings")
    vertices = tuple(nodes)
    known = set(vertices)
    adjacency: dict[str, list[str]] = {u: [] for u in vertices}
    degree = {u: 0 for u in vertices}
    edge_count = 0
    for source, target in steps:
        if source not in known or target not in known:
            raise ValueError("precedence endpoint not declared")
        adjacency[source].append(target)
        degree[target] += 1
        edge_count += 1

    ready = deque(u for u in vertices if degree[u] == 0)
    ranks = {u: 0 for u in vertices}
    visited = 0
    while ready:
        u = ready.popleft()
        visited += 1
        for v in adjacency[u]:
            ranks[v] = max(ranks[v], ranks[u] + 1)
            degree[v] -= 1
            if degree[v] == 0:
                ready.append(v)
    if visited == len(vertices):
        assert all(ranks[v] >= ranks[u] + 1
                   for u in vertices for v in adjacency[u])
        return GlobalSchedule(True, tuple((u, ranks[u]) for u in vertices),
                              (), edge_count)

    # Explicit independent audit witness: a directed cycle of strict rises.
    remaining = {u for u in vertices if degree[u] > 0}
    color: dict[str, int] = {}
    active: list[str] = []
    stack: list[tuple[str, int]] = []
    for root in vertices:
        if root not in remaining or color.get(root, 0):
            continue
        color[root] = 1
        active.append(root)
        stack.append((root, 0))
        while stack:
            u, pos = stack[-1]
            if pos == len(adjacency[u]):
                stack.pop()
                active.pop()
                color[u] = 2
                continue
            v = adjacency[u][pos]
            stack[-1] = (u, pos + 1)
            if v not in remaining:
                continue
            state = color.get(v, 0)
            if state == 1:
                witness = tuple(active[active.index(v):] + [v])
                assert all(b in adjacency[a]
                           for a, b in zip(witness, witness[1:]))
                return GlobalSchedule(False, (), witness, edge_count)
            if state == 0:
                color[v] = 1
                active.append(v)
                stack.append((v, 0))
    raise AssertionError("Kahn reported a cycle but DFS failed to find a witness")


@dataclass(frozen=True)
class ReversibilityAudit:
    passed: bool
    events: int
    blocks: int
    logical_gate_count: int
    strict_event_schedule: GlobalSchedule
    target_index: int
    forward_reverse_equal: bool

    def as_dict(self) -> dict:
        return {
            "passed": self.passed,
            "events": self.events,
            "blocks": self.blocks,
            "logical_gate_count": self.logical_gate_count,
            "strict_event_schedule": self.strict_event_schedule.as_dict(),
            "target_index": self.target_index,
            "forward_reverse_equal": self.forward_reverse_equal,
        }


def audit_reversible_schedule(oracle: BlockOracle, *,
                              supplied: Iterable[GateStep] | None = None,
                              hostile_extra_dependencies: Iterable[tuple[str, str]] = ()
                              ) -> ReversibilityAudit:
    """Check each logical operation's location and temporal consistency.

    No assumption that a *register* must be written only once; event ids are
    deliberately unique. The local blocks must compute, toggle summary, then
    uncompute, and the entire phase after target must mirror the phase before.
    A later-imposed 'target must happen before first compute' constraint is
    rejected as an impossible Penrose-like dependency loop.
    """
    steps = tuple(oracle.iter_instructions() if supplied is None else supplied)
    expected = []
    for reverse_global in (False, True):
        ordering = (range(oracle.blocks - 1, -1, -1)
                    if reverse_global else range(oracle.blocks))
        for block in ordering:
            begin = block * oracle.block_size
            width = oracle.block_widths[block]
            expected.extend(GateStep("clause", i, begin + i)
                            for i in range(width))
            expected.append(GateStep("summary", block, active_bits=width))
            expected.extend(GateStep("clause", i, begin + i)
                            for i in range(width - 1, -1, -1))
        if not reverse_global:
            expected.append(GateStep("target"))
    target_positions = [i for i, step in enumerate(steps)
                        if step.kind == "target"]
    target = target_positions[0] if len(target_positions) == 1 else -1
    reversible = (len(steps) == oracle.logical_mcx_gates
                  and steps == tuple(expected)
                  and target >= 0
                  and tuple(reversed(steps[target + 1:])) == steps[:target])
    events = tuple(f"event:{i}" for i in range(len(steps)))
    ordered = tuple(zip(events, events[1:]))
    schedule = analyze_strict_precedence(
        events, (*ordered, *tuple(hostile_extra_dependencies)))
    return ReversibilityAudit(
        reversible and schedule.consistent,
        len(steps), oracle.blocks, oracle.logical_mcx_gates, schedule,
        target, reversible,
    )


def penrose_staircase_negative_control() -> GlobalSchedule:
    """Four individually valid +1 ascents that close into contradiction."""
    return analyze_strict_precedence(
        ("north", "east", "south", "west"),
        (("north", "east"), ("east", "south"),
         ("south", "west"), ("west", "north")),
    )
