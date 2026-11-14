#!/usr/bin/env python3
"""Penrose-001: falsify locally plausible but globally impossible schedules."""
from __future__ import annotations

from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))

from janus_deutsch_002 import DirectOracle
from janus_deutsch_003 import BlockOracle, GateStep, choose_block_size
from janus_penrose_001 import (
    analyze_strict_precedence, audit_reversible_schedule,
    penrose_staircase_negative_control,
)
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES


class PenroseAuditTests(unittest.TestCase):
    def test_four_rise_staircase_has_explicit_global_cycle_witness(self):
        result = penrose_staircase_negative_control()
        self.assertFalse(result.consistent)
        self.assertEqual(result.constraint_count, 4)
        self.assertGreaterEqual(len(result.cycle_witness), 5)
        self.assertEqual(result.cycle_witness[0], result.cycle_witness[-1])

    def test_dag_has_constructive_monotone_rank_witness(self):
        nodes = ("north", "east", "south", "west", "finish")
        edges = (("north", "east"), ("east", "south"),
                 ("south", "west"), ("west", "finish"))
        data = analyze_strict_precedence(nodes, edges)
        self.assertTrue(data.consistent)
        self.assertEqual(data.cycle_witness, ())
        h = dict(data.ranks)
        self.assertTrue(all(h[v] >= h[u] + 1 for u, v in edges))
        # Strict loop impossible, but a non-returning staircase is valid.
        self.assertGreater(h["finish"], h["north"])

    def test_reject_disconnected_cycle_self_loop_and_undeclared_nodes(self):
        bad = analyze_strict_precedence(
            ("a", "b", "x", "y"),
            (("a", "b"), ("x", "y"), ("y", "x")))
        self.assertFalse(bad.consistent)
        self.assertEqual(bad.cycle_witness[0], bad.cycle_witness[-1])
        self.assertFalse(analyze_strict_precedence(("x",), (("x", "x"),)).consistent)
        with self.assertRaises(ValueError):
            analyze_strict_precedence(("x", "x"), ())
        with self.assertRaises(ValueError):
            analyze_strict_precedence(("x", "y"), (("x", "z"),))

    def test_schedule_legitimate_recompute_is_not_misclassified_as_cycle(self):
        formulas = [
            ((), 3, "SAT"),
            (((),), 3, "SAT"),
            (((1, 2, 3),), 3, "EXACT_ONE"),
            (((1, -2), (-2, 3), (1, -3)), 3, "SAT"),
        ]
        for rows, n, kind in formulas:
            for size in (1, 2, 3, 8):
                oracle = BlockOracle.compile(rows, n, kind, block_size=size)
                audit = audit_reversible_schedule(oracle)
                self.assertTrue(audit.passed, (rows, kind, size, audit))
                self.assertEqual(audit.events, oracle.logical_mcx_gates)
                self.assertTrue(audit.forward_reverse_equal)
                self.assertTrue(audit.strict_event_schedule.consistent)
                for x in range(1 << n):
                    for b in (0, 1):
                        self.assertEqual(oracle.apply_basis(x, b)[1],
                                         b ^ int(oracle.original.evaluate(x)))

    def test_detect_corrupt_schedule_and_injected_dependency_loop(self):
        oracle = BlockOracle.compile(((1, -2), (-1, 3)), 3, block_size=2)
        valid = list(oracle.iter_instructions())
        self.assertTrue(audit_reversible_schedule(oracle, supplied=valid).passed)
        changed = valid[:]
        changed[0] = GateStep("clause", 0, 999)
        fail = audit_reversible_schedule(oracle, supplied=changed)
        self.assertFalse(fail.passed)
        self.assertFalse(fail.forward_reverse_equal)

        extra = (("event:" + str(len(valid)-1), "event:0"),)
        wrong = audit_reversible_schedule(
            oracle, hostile_extra_dependencies=extra)
        self.assertFalse(wrong.passed)
        self.assertTrue(wrong.forward_reverse_equal)
        self.assertFalse(wrong.strict_event_schedule.consistent)
        self.assertEqual(
            wrong.strict_event_schedule.cycle_witness[0],
            wrong.strict_event_schedule.cycle_witness[-1])

    def test_maJ3_k4_full_4161_event_schedule_no_global_inconsistency(self):
        cnf, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
        direct = DirectOracle.compile(cnf, n)
        oracle = choose_block_size(direct)
        audit = audit_reversible_schedule(oracle)
        self.assertTrue(audit.passed)
        self.assertEqual(audit.events, 4161)
        self.assertEqual(oracle.qubit_estimate, 113)
        self.assertEqual(oracle.maximum_controls, 32)
        rng = random.Random(1958)
        for x in [0, (1 << n)-1] + [rng.getrandbits(n) for _ in range(32)]:
            self.assertEqual(oracle.evaluate(x), direct.evaluate(x))
        invalid = audit_reversible_schedule(
            oracle,
            hostile_extra_dependencies=((f"event:{audit.events-1}", "event:0"),))
        self.assertFalse(invalid.passed)
        self.assertTrue(invalid.strict_event_schedule.cycle_witness)

    def test_acyclic_graph_property_fuzz(self):
        rng = random.Random(57201958)
        for n in range(2, 22):
            nodes = [f"step:{i}" for i in range(n)]
            edges = [(nodes[i], nodes[j]) for i in range(n) for j in range(i+1, n)
                     if rng.random() < 0.15]
            result = analyze_strict_precedence(nodes, edges)
            self.assertTrue(result.consistent)
            ranks = dict(result.ranks)
            self.assertTrue(all(ranks[b] > ranks[a] for a, b in edges))
            cycle = [(nodes[i], nodes[(i+1) % n]) for i in range(n)]
            counter = analyze_strict_precedence(nodes, cycle)
            self.assertFalse(counter.consistent)
            self.assertEqual(counter.cycle_witness[0], counter.cycle_witness[-1])


if __name__ == "__main__":
    unittest.main()
