from experiments import janus_trump_r50g10_one_step_reachability_lift_and_all_doors_audit as r50g10


def test_one_step_root_is_w3_and_reaches_frozen_w4_state():
    _core, root, reached = r50g10.build_root_and_reached()
    assert r50g10.max_width(root) <= 3
    direct = r50g10.r50g4.first_r33_micro_candidate(root)
    assert direct['rule'] == 'BOUNDED_VARIABLE_ELIMINATION'
    assert direct['var'] == 1
    assert r50g10.canon(direct['after']) == reached
    micro = r50g10.r50g4.micro_r33_status(root)
    assert micro['status'] == 'AUTHORIZED_R33_MICROSTEP'
    assert r50g10.max_width(micro['after']) == 4


def test_reached_state_reproduces_bad_same_pivot_wide_fixpoint():
    _core, _root, reached = r50g10.build_root_and_reached()
    inspection = r50g10.r50g8.inspect_immediate_bve_state(reached)
    assert inspection['applicable']
    assert inspection['pivot'] == 2
    assert inspection['same_pivot_safe'] is False
    assert inspection['terminal'] is None
    assert inspection['final_width'] > 4


def test_full_gate_sets_only_the_supported_status():
    out = r50g10.run()
    fw = out['firewall']
    assert fw['REACHABILITY_OF_R50G9_ISOMORPH'] == 'PROVED_BY_EXPLICIT_ONE_STEP_U_MU_TRACE'
    assert fw['REACHABLE_SAME_PIVOT_W4_SAFETY'] == 'REFUTED'
    blocked = out['all_existing_doors_audit']['all_existing_doors_blocked']
    if blocked:
        assert fw['U_MU'] == 'REFUTED_BY_EXPLICIT_ONE_STEP_REACHABLE_SAT_OPEN'
        assert out['refined_U_mu_step']['kind'] == 'OPEN_OBSTRUCTION'
    else:
        assert fw['U_MU'] == 'OPEN'
        assert out['refined_U_mu_step']['kind'] != 'OPEN_OBSTRUCTION'
    assert fw['SAT_IN_P'] == 'NOT_PROVED'
    assert fw['P_VS_NP'] == 'OPEN'
