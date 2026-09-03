import unittest
from itertools import combinations
from experiments.janus_trump_r44cc_internal_ternary_transport_inequality_realizability import (
    target_formula, source_formula, recover_transport_csp,
    recovered_transport_colorings, proper_colorings, audit
)


class R44CCTests(unittest.TestCase):
    def test_single_edge_relation_is_exact_inequality(self):
        A = target_formula(2, [(0, 1)])
        B = source_formula(2, [(0, 1)])
        blocks, cands, allowed = recover_transport_csp(A, B)
        self.assertEqual([len(x) for x in blocks], [3, 3])
        self.assertEqual([len(x) for x in cands], [3, 3])
        expected = {(a, b) for a in range(3) for b in range(3) if a != b}
        self.assertEqual(allowed[(0, 1)], expected)

    def test_triangle_has_six_transports(self):
        edges = [(0, 1), (1, 2), (0, 2)]
        got, _, _, _ = recovered_transport_colorings(target_formula(3, edges), source_formula(3, edges))
        self.assertEqual(got, proper_colorings(3, edges))
        self.assertEqual(len(got), 6)

    def test_k4_has_no_transport(self):
        edges = list(combinations(range(4), 2))
        got, _, _, _ = recovered_transport_colorings(target_formula(4, edges), source_formula(4, edges))
        self.assertEqual(got, set())

    def test_formula_size_is_linear(self):
        n = 7
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
        self.assertEqual(len(target_formula(n, edges)), 4*n + len(edges))
        self.assertEqual(len(source_formula(n, edges)), 4*n + 6*len(edges))

    def test_full_finite_gate(self):
        d = audit(5)
        self.assertTrue(d['internal_ternary_inequality_realizable'])
        self.assertTrue(d['exact_bijection_with_graph_3colorings_on_enumerated_universe'])
        self.assertEqual(d['P_VS_NP'], 'OPEN')


if __name__ == '__main__':
    unittest.main()
