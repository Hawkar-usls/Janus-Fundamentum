from experiments import janus_trump_r10_exact_semantic_bridge_interface as r10


def test_r10_candidate_firewall():
    assert r10.candidate_firewall()["pass"]


def test_r10_exact_projection_and_decoder():
    # EXISTS x [(x OR b) AND (~x OR b)] == b.
    x, b = 1, 2
    frame = ((x, b), (-x, b))
    cand = r10.compile_projection_interface(frame, (b,), 4)
    assert cand["status"] == "EXACT_INTERFACE"
    assert not r10.interface_accepts(cand, (b,), 0)
    assert r10.interface_accepts(cand, (b,), 1)
    dec = r10.diverge_decoder(frame, (b,), 1, cand)
    assert dec["status"] == "SAT_WITNESS"


def test_r10_width_barrier_returns_open_without_dropping_resolvent():
    # Eliminating x requires a width-6 resolvent, so frozen k=4 must OPEN.
    x = 1
    frame = ((x, 2, 3, 4), (-x, 5, 6, 7))
    cand = r10.compile_projection_interface(frame, (2, 3, 4, 5, 6, 7), 4)
    assert cand["status"] == "OPEN"
    assert cand["minimum_observed_required_width"] == 6


def test_r10_shadow_2sat_classifier_on_unit_relation():
    rep = r10.exact_2sat_representation((1,), [1])
    assert rep["exact"]
