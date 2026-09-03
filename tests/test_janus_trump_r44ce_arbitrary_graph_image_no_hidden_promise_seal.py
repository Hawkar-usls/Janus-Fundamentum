import importlib.util
import unittest
from itertools import combinations
from pathlib import Path

P=Path(__file__).parents[1]/'experiments'/'janus_trump_r44ce_arbitrary_graph_image_no_hidden_promise_seal.py'
spec=importlib.util.spec_from_file_location('r44ce',P)
r44ce=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44ce)

class R44CETest(unittest.TestCase):
    def test_k5_roundtrip(self):
        E=tuple(combinations(range(5),2))
        A,B=r44ce.encode_graph(5,E)
        self.assertEqual(r44ce.decode_graph(A,B),(5,E))

    def test_k33_roundtrip(self):
        E=tuple((u,v) for u in range(3) for v in range(3,6))
        A,B=r44ce.encode_graph(6,E)
        self.assertEqual(r44ce.decode_graph(A,B),(6,E))

    def test_all_graphs_through_4(self):
        d=r44ce.audit(4)
        self.assertTrue(d['formula_only_decoder'])
        self.assertTrue(d['decode_encode_left_inverse_on_enumerated_universe'])
        self.assertTrue(d['no_hidden_graph_promise_in_image_family'])
        self.assertFalse(d['polynomial_algorithm_for_r44cc_family_found'])
        self.assertFalse(d['additional_algebraic_or_semantic_invariant_ruled_out'])
        self.assertEqual(d['P_VS_NP'],'OPEN')

if __name__=='__main__':
    unittest.main()
