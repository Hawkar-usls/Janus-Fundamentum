from experiments import janus_trump_r50g12_three_wide_resolvent_affine_rescue_poison as r50g12


def test_frozen_parent_geometry_has_expected_three_resolvents_if_applicable():
    _core, source = r50g12.build_source()
    assert r50g12.max_width(source) == 4
    out = r50g12.run()
    c = out['construction']
    if c['construction_valid_for_target']:
        assert c['expected_resolvents_exact']
        assert c['wide_variable_intersection'] == []
        assert len(c['exact_unique_nontaut_resolvents']) == 3


def test_status_never_exceeds_exact_result():
    out = r50g12.run()
    fw = out['firewall']
    assert fw['REACHABILITY_OF_R50G12_WITNESS'] == 'NOT_ESTABLISHED'
    assert fw['U_MU'] == 'OPEN'
    assert fw['SAT_IN_P'] == 'NOT_PROVED'
    assert fw['P_VS_NP'] == 'OPEN'
    if out['construction']['construction_valid_for_target']:
        doors = out['all_existing_doors_audit']
        assert (out['refined_U_mu_step']['kind'] == 'OPEN_OBSTRUCTION') == doors['all_existing_doors_blocked']
        if doors['all_existing_doors_blocked']:
            assert fw['LOCAL_EXISTING_DOOR_THEOREM'] == 'REFUTED_BY_EXPLICIT_W4_SAT_OPEN'
