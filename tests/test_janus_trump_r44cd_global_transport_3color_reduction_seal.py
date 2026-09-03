from itertools import combinations
import importlib.util
from pathlib import Path

P = Path(__file__).parents[1] / "experiments" / "janus_trump_r44cd_global_transport_3color_reduction_seal.py"
spec = importlib.util.spec_from_file_location("r44cd", P)
r44cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44cd)


def test_triangle_has_six_global_transports():
    triangle = [(0, 1), (1, 2), (0, 2)]
    assert r44cd.verify_instance(3, triangle)["assignment_count"] == 6


def test_k4_has_no_global_transport():
    k4 = list(combinations(range(4), 2))
    result = r44cd.verify_instance(4, k4)
    assert result["assignment_count"] == 0
    assert result["transport_exists"] is False


def test_exhaustive_small_universe_and_firewalls():
    result = r44cd.audit(max_n=4)
    assert result["exact_bijection_on_enumerated_universe"] is True
    assert result["construction_polynomial"] is True
    assert result["additional_polynomial_invariant_ruled_out"] is False
    assert result["full_TRUMP_polynomiality_proven"] is False
    assert result["TRUMP_finished"] is False
    assert result["SAT_IN_P"] == "NOT_PROVED"
    assert result["P_VS_NP"] == "OPEN"
