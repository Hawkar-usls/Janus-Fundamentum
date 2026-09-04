from experiments import janus_trump_r50g9_explicit_local_wide_fixpoint_counterexample as r50g9


def test_frozen_source_recipe_is_w4_and_preclean():
    _core, _shifted, source = r50g9.source_formula()
    assert r50g9.max_width(source) == 4
    assert r50g9.r50g8.pre_bve_clean(source)


def test_first_microstep_is_immediate_bve_on_frozen_pivot():
    _core, _shifted, source = r50g9.source_formula()
    direct = r50g9.r50g4.first_r33_micro_candidate(source)
    assert direct['rule'] == 'BOUNDED_VARIABLE_ELIMINATION'
    assert direct['var'] == 1
    assert r50g9.EXPECTED_WIDE in r50g9.canon(direct['after'])
    assert r50g9.r50g4.micro_r33_status(source)['status'] == 'IMMEDIATE_BVE_W4_ESCAPE'


def test_constructive_witness_refutes_only_local_theorem():
    out = r50g9.run()
    w = out['witness']
    assert w['final_width'] > 4
    assert w['terminal'] is None
    assert w['R33_fixed'] and w['RUP_fixed'] and w['BVE_fixed'] and w['affine_negative']
    assert w['same_pivot_machine_safe'] is False
    assert w['ancestry_kind'] == 'DIRECT_DP_WIDE_SURVIVOR_TO_FIXPOINT'
    assert out['firewall']['LOCAL_WIDE_ANCESTRY_IMPOSSIBILITY_THEOREM'] == 'REFUTED'
    assert out['firewall']['LOCAL_SAME_PIVOT_W4_SAFETY'] == 'REFUTED'
    assert out['firewall']['REACHABILITY_OF_WITNESS'] == 'NOT_ESTABLISHED'
    assert out['firewall']['REACHABLE_SAME_PIVOT_W4_SAFETY'] == 'OPEN'
    assert out['firewall']['SAT_IN_P'] == 'NOT_PROVED'
    assert out['firewall']['P_VS_NP'] == 'OPEN'
