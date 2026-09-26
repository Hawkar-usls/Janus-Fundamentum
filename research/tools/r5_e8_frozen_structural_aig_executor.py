#!/usr/bin/env python3
"""
R5 E8 frozen structural AIG reference executor.

Scope:
- exact structural cofactoring only;
- no SAT/equivalence oracle;
- no FRAIG/BDD sweeping;
- complemented-edge AIG;
- rewrites: CONST, IDEMPOTENCE, COMPLEMENT, COMMUTATIVE canonicalization;
- isolated trial arenas;
- GC after winner commit;
- exact greedy key: (projected reachable nodes, A_x, variable id).

This file is the executable authority for finite diagnostics in
R5_E8_GREEDY_EXACT_STRUCTURAL_PROJECTOR_GATE_V1 after v1.3.
It does NOT establish any asymptotic theorem.
"""
from __future__ import annotations

import argparse
import copy
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

Ref = Tuple[int, bool]  # (node_id, complemented); node_id=0 is constant FALSE/TRUE.

FALSE: Ref = (0, False)
TRUE: Ref = (0, True)


def neg(r: Ref) -> Ref:
    return (r[0], not r[1])


def lit_key(lit: int) -> Tuple[int, int]:
    # Frozen: abs variable id ascending, then positive before negative.
    return (abs(lit), 0 if lit > 0 else 1)


@dataclass
class Trial:
    variable: int
    cost: int
    cone: int
    root: Ref
    arena: "AIG"


class AIG:
    def __init__(self, nvars: int):
        self.nvars = nvars
        self.nodes: Dict[int, Tuple[Ref, Ref]] = {}
        self.unique: Dict[Tuple[Ref, Ref], int] = {}
        self.next_id = nvars + 1

    def clone(self) -> "AIG":
        out = AIG(self.nvars)
        out.nodes = self.nodes.copy()
        out.unique = self.unique.copy()
        out.next_id = self.next_id
        return out

    @staticmethod
    def _ref_key(r: Ref) -> Tuple[int, int]:
        # False complement bit before true; constants are simplified before interning.
        return (r[0], 1 if r[1] else 0)

    def and2(self, a: Ref, b: Ref) -> Ref:
        # CONST
        if a == FALSE or b == FALSE:
            return FALSE
        if a == TRUE:
            return b
        if b == TRUE:
            return a

        # IDEMPOTENCE / COMPLEMENT
        if a == b:
            return a
        if a == neg(b):
            return FALSE

        # COMMUTATIVE CANONICALIZATION
        if self._ref_key(a) > self._ref_key(b):
            a, b = b, a

        key = (a, b)
        hit = self.unique.get(key)
        if hit is not None:
            return (hit, False)

        nid = self.next_id
        self.next_id += 1
        self.nodes[nid] = key
        self.unique[key] = nid
        return (nid, False)

    def or2(self, a: Ref, b: Ref) -> Ref:
        # OR is De Morgan over the same AND unique table.
        return neg(self.and2(neg(a), neg(b)))

    def _balanced(self, refs: Sequence[Ref], op: str) -> Ref:
        work = list(refs)
        if not work:
            return TRUE if op == "and" else FALSE
        while len(work) > 1:
            nxt: List[Ref] = []
            i = 0
            while i + 1 < len(work):
                if op == "and":
                    nxt.append(self.and2(work[i], work[i + 1]))
                else:
                    nxt.append(self.or2(work[i], work[i + 1]))
                i += 2
            if i < len(work):
                # Frozen: carry unpaired final item unchanged.
                nxt.append(work[i])
            work = nxt
        return work[0]

    def literal_ref(self, lit: int) -> Ref:
        v = abs(lit)
        if v < 1 or v > self.nvars:
            raise ValueError(f"literal variable {v} outside 1..{self.nvars}")
        return (v, lit < 0)

    def compile_cnf(self, clauses: Iterable[Iterable[int]]) -> Ref:
        normalized: List[Tuple[int, ...]] = []
        for raw in clauses:
            vals = set(int(x) for x in raw)
            if any(-x in vals for x in vals):
                # Frozen: tautological clauses removed.
                continue
            clause = tuple(sorted(vals, key=lit_key))
            normalized.append(clause)

        # Frozen: exact duplicate clauses removed, then lexicographic order.
        normalized = sorted(
            set(normalized),
            key=lambda c: tuple(lit_key(x) for x in c),
        )

        clause_refs = [
            self._balanced([self.literal_ref(l) for l in c], "or")
            for c in normalized
        ]
        return self._balanced(clause_refs, "and")

    def restrict(self, root: Ref, var: int, value: bool) -> Ref:
        memo: Dict[int, Ref] = {}

        def rec(r: Ref) -> Ref:
            nid, inv = r
            if nid == 0:
                return r
            if inv:
                return neg(rec((nid, False)))
            if nid <= self.nvars:
                if nid == var:
                    return TRUE if value else FALSE
                return r
            hit = memo.get(nid)
            if hit is not None:
                return hit
            a, b = self.nodes[nid]
            out = self.and2(rec(a), rec(b))
            memo[nid] = out
            return out

        return rec(root)

    def project(self, root: Ref, var: int) -> Ref:
        c0 = self.restrict(root, var, False)
        c1 = self.restrict(root, var, True)
        return self.or2(c0, c1)

    def reachable(self, root: Ref) -> set[int]:
        seen: set[int] = set()

        def rec(r: Ref) -> None:
            nid = r[0]
            if nid == 0 or nid in seen:
                return
            seen.add(nid)
            if nid > self.nvars:
                a, b = self.nodes[nid]
                rec(a)
                rec(b)

        rec(root)
        return seen

    def reachable_size(self, root: Ref) -> int:
        # Variables + AND nodes; constants excluded.
        return len(self.reachable(root))

    def cone_size(self, root: Ref, var: int) -> int:
        # Frozen A_x: reachable AND gates whose transitive fanin contains var.
        reach = self.reachable(root)
        memo: Dict[int, bool] = {}

        def dep_ref(r: Ref) -> bool:
            nid = r[0]
            if nid == 0:
                return False
            if nid <= self.nvars:
                return nid == var
            return dep_node(nid)

        def dep_node(nid: int) -> bool:
            hit = memo.get(nid)
            if hit is not None:
                return hit
            a, b = self.nodes[nid]
            out = dep_ref(a) or dep_ref(b)
            memo[nid] = out
            return out

        return sum(
            1
            for nid in reach
            if nid > self.nvars and dep_node(nid)
        )

    def garbage_collect(self, root: Ref) -> None:
        # Frozen: prune unreachable AND nodes / unique-table entries;
        # do NOT renumber live node ids; next_id remains monotone.
        reach = self.reachable(root)
        for nid in list(self.nodes):
            if nid not in reach:
                key = self.nodes.pop(nid)
                if self.unique.get(key) == nid:
                    del self.unique[key]

    def trial(self, root: Ref, var: int) -> Trial:
        # Frozen isolated ephemeral arena.
        arena = self.clone()
        out = arena.project(root, var)
        return Trial(
            variable=var,
            cost=arena.reachable_size(out),
            cone=self.cone_size(root, var),
            root=out,
            arena=arena,
        )


def greedy_run(arena: AIG, root: Ref, variables: Sequence[int]) -> dict:
    remaining = list(variables)
    trace = []
    live_sizes = [arena.reachable_size(root)]

    while remaining and root[0] != 0:
        trials = [arena.trial(root, x) for x in remaining]
        trials.sort(key=lambda t: (t.cost, t.cone, t.variable))
        winner = trials[0]

        trace.append(
            {
                "step": len(trace),
                "selected_variable": winner.variable,
                "winning_key": [winner.cost, winner.cone, winner.variable],
                "all_keys": [
                    [t.cost, t.cone, t.variable]
                    for t in trials
                ],
            }
        )

        # Frozen winner commit: transfer the isolated winning arena.
        arena = winner.arena
        root = winner.root
        arena.garbage_collect(root)
        remaining.remove(winner.variable)
        live_sizes.append(arena.reachable_size(root))
        trace[-1]["next_state_nodes"] = live_sizes[-1]

    return {
        "initial_live_nodes": live_sizes[0],
        "live_sizes": live_sizes,
        "peak_live_nodes": max(live_sizes),
        "selected_variables": [x["selected_variable"] for x in trace],
        "trace": trace,
        "terminal_constant": (
            None
            if root[0] != 0
            else bool(root[1])
        ),
    }


def kernel_formula() -> tuple[int, list[list[int]]]:
    return 9, [
        [-6, 8],
        [-2, -7],
        [-2, 9],
        [-1, -8],
        [1, 5],
        [-4, 9],
        [3, 6],
        [4, -5],
        [-7, -9],
    ]


def eq_formula(k: int) -> tuple[int, list[list[int]]]:
    clauses: list[list[int]] = []
    for i in range(1, k + 1):
        y = k + i
        clauses.append([i, -y])
        clauses.append([-i, y])
    return 2 * k, clauses


def cyclic_shared_payload_formula(m: int) -> tuple[int, list[list[int]]]:
    def z(j: int) -> int:
        return m + 1 + (j % m)

    clauses: list[list[int]] = []
    for i in range(m):
        x = i + 1
        clauses.append([x, z(i), -z(i + 1)])
        clauses.append([-x, z(i + 2), -z(i + 3)])
    return 2 * m, clauses


def build_builtin(name: str, m: int | None) -> tuple[int, list[list[int]]]:
    if name == "kernel":
        return kernel_formula()
    if m is None or m < 1:
        raise ValueError(f"--builtin {name} requires --m >= 1")
    if name == "eq":
        return eq_formula(m)
    if name == "cyclic":
        return cyclic_shared_payload_formula(m)
    raise ValueError(name)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builtin", choices=["kernel", "eq", "cyclic"], default="kernel")
    ap.add_argument("--m", type=int)
    ap.add_argument(
        "--variables",
        help="comma-separated elimination variables; default 1..n",
    )
    args = ap.parse_args()

    nvars, clauses = build_builtin(args.builtin, args.m)
    arena = AIG(nvars)
    root = arena.compile_cnf(clauses)

    variables = (
        [int(x) for x in args.variables.split(",") if x.strip()]
        if args.variables
        else list(range(1, nvars + 1))
    )

    out = {
        "executor": "R5_E8_FROZEN_STRUCTURAL_AIG_EXECUTOR_V1",
        "builtin": args.builtin,
        "parameter_m": args.m,
        "nvars": nvars,
        "clauses": clauses,
        "result": greedy_run(arena, root, variables),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
