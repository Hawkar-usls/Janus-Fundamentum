import unittest
from itertools import combinations
from experiments.janus_trump_r44cb_domain3_pairwise_csp_3color_boundary import (
    compatibility_assignments,
    graph_3color_assignments,
    audit,
)


class R44CBTests(unittest.TestCase):
    def test_triangle(self):
        edges = [(0, 1), (1, 2), (0, 2)]
        self.assertEqual(len(compatibility_assignments(3, edges)), 6)
        self.assertEqual(compatibility_assignments(3, edges), graph_3color_assignments(3, edges))

    def test_k4(self):
        edges = list(combinations(range(4), 2))
        self.assertEqual(compatibility_assignments(4, edges), [])

    def test_small_universe(self):
        r = audit(max_n=4)
        self.assertTrue(r['exact_bijection_verified_on_enumerated_universe'])
        self.assertFalse(r['R44CA_boolean_2sat_extension_universal'])
        self.assertEqual(r['P_VS_NP'], 'OPEN')


if __name__ == '__main__':
    unittest.main()
