from experiments import janus_trump_r50g11_width4_xor_cycle_all_existing_doors_counterexample as r50g11


def test_frozen_core_is_width4_complete_affine_sat():
    core, _source = r50g11.build_core_and_source()
    assert r50g11.max_width(core) == 4
    affine = r50g11.r34.recognize_complete_affine_cnf(core)
    assert affine['recognized']
    solution = r50g11.r34.solve_gf2_with_certificate(affine['equations'])
    assert solution['sat']
    assert r50g11.r34.verify_affine_certificate(core, affine, solution)['pass']


def test_gate_never_overpromotes_local_result_to_reachability_or_pnp():
    out = r50g11.run()
    fw = out['firewall']
    assert fw['REACHABILITY_OF_R50G11_WITNESS'] == 'NOT_ESTABLISHED'
    assert fw['U_MU'] == 'OPEN'
    assert fw['SAT_IN_P'] == 'NOT_PROVED'
    assert fw['P_VS_NP'] == 'OPEN'
    assert fw['TRUMP_finished'] is False
    if out['construction']['construction_valid_for_target']:
        doors = out['all_existing_doors_audit']
        controller_open = out['refined_U_mu_step']['kind'] == 'OPEN_OBSTRUCTION'
        assert controller_open == doors['all_existing_doors_blocked']
        if doors['all_existing_doors_blocked']:
            assert fw['LOCAL_EXISTING_DOOR_THEOREM'] == 'REFUTED_BY_EXPLICIT_W4_SAT_OPEN'
        else:
            assert fw['LOCAL_EXISTING_DOOR_THEOREM'] == 'OPEN'
