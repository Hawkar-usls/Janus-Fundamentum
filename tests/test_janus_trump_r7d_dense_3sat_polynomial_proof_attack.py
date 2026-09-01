from experiments import janus_trump_r7d_dense_3sat_polynomial_proof_attack as r7d
from janus_trump_p_vs_np_direct_challenge_r0 import canon


def test_target_scope_is_exactly_ten_dense_cases():
    rows = r7d.target_cases()
    assert len(rows) == 10
    assert {x['family'] for x in rows} == {'RANDOM_3SAT_NEAR_DENSE'}


def test_width4_resolution_refutes_simple_unsat():
    f = canon(((1, 2), (-1, 2), (1, -2), (-1, -2)))
    rr = r7d.fixed_width_resolution(f, 4)
    assert rr.status == 'UNSAT'
    assert rr.proof is not None
    assert r7d.replay_resolution_proof(f, rr.proof, 4)


def test_width4_elimination_reconstructs_sat_model():
    f = canon(((1, 2, 3), (-1, 2, 3), (1, -2, 3), (1, 2, -3)))
    er = r7d.width_bounded_eliminate(f, 4)
    assert er.status == 'SAT'
    assert er.witness is not None
    assert r7d.r7b.verify_sat(f, er.witness)
    assert r7d.replay_elimination_certificate(f, er.records, er.final_cnf, 4)


def test_pivot_width_barrier_is_detected():
    f = canon(((1, 2, 3, 4), (-1, 5, 6, 7)))
    p = r7d.pivot_resolvents(f, 1, 4)
    assert p['safe'] is False
    assert p['blocked']['width'] == 6


def test_candidate_source_firewall():
    fw = r7d.candidate_source_firewall()
    assert fw['pass'] is True
    assert fw['forbidden_hits'] == []
