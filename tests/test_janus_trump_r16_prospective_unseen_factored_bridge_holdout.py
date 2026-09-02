import janus_trump_r16_prospective_unseen_factored_bridge_holdout as r16


def test_r16_all_eight_worlds_regenerate_exactly():
    freeze, resources = r16.load_contracts()
    assert len(freeze['worlds']) == 8
    for spec in freeze['worlds']:
        generated = r16.generate_frozen_world(spec)
        assert all(generated['checks'].values())
        assert tuple(spec['bridge_vars']) == generated['bridge']


def test_r16_candidate_blob_and_resource_contract_are_frozen():
    freeze, resources = r16.load_contracts()
    assert freeze['frozen_candidate']['blob_sha'] == r16.EXPECTED_CANDIDATE_BLOB
    assert resources['candidate']['blob_sha'] == r16.EXPECTED_CANDIDATE_BLOB
    assert resources['candidate']['wall_seconds_per_world'] == 120
    assert resources['verifier']['wall_seconds_total_after_candidate_per_world'] == 300


def test_r16_candidate_firewall_passes():
    assert r16.r15d.candidate_firewall()['pass'] is True


def test_r16_primary_endpoint_is_decision_invariant():
    freeze, _ = r16.load_contracts()
    assert freeze['primary_endpoint'] == 'FULL_BRIDGE_ALLOWED_SET_EXACTNESS'
    assert freeze['P_VS_NP'] == 'OPEN'
