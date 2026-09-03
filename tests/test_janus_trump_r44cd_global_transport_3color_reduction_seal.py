from itertools import combinations
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).parents[1] / "experiments" / "janus_trump_r44cd_global_transport_3color_reduction_seal.py"
spec = importlib.util.spec_from_file_location("r44cd", P)
r44cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44cd)


class R44CDReductionSealTests(unittest.TestCase):
    def test_triangle_has_six_global_transports(self):
        triangle = [(0, 1), (1, 2), (0, 2)]
        self.assertEqual(r44cd.verify_instance(3, triangle)["assignment_count"], 6)

    def test_k4_has_no_global_transport(self):
        k4 = list(combinations(range(4), 2))
        result = r44cd.verify_instance(4, k4)
        self.assertEqual(result["assignment_count"], 0)
        self.assertFalse(result["transport_exists"])

    def test_exhaustive_small_universe_and_firewalls(self):
        result = r44cd.audit(max_n=4)
        self.assertTrue(result["exact_bijection_on_enumerated_universe"])
        self.assertTrue(result["construction_polynomial"])
        self.assertFalse(result["additional_polynomial_invariant_ruled_out"])
        self.assertFalse(result["full_TRUMP_polynomiality_proven"])
        self.assertFalse(result["TRUMP_finished"])
        self.assertEqual(result["SAT_IN_P"], "NOT_PROVED")
        self.assertEqual(result["P_VS_NP"], "OPEN")


if __name__ == "__main__":
    unittest.main()
