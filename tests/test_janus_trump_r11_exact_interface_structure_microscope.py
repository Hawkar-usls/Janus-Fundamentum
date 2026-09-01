from experiments import janus_trump_r11_exact_interface_structure_microscope as r11


def test_r11_controls_have_power_to_say_no():
    controls = r11.positive_controls()
    assert controls and all(controls.values()), controls


def test_r11_exact_cnf_width_on_even_parity_three_is_three():
    allowed = [m for m in range(8) if m.bit_count() % 2 == 0]
    g = r11.exact_cnf_geometry(allowed, 3)
    assert g['minimum_same_variable_cnf_width'] == 3
    assert g['bounded_width_hulls'][-1]['false_positives'] == 0


def test_r11_relation_class_controls():
    allowed = [m for m in range(8) if not ((m & 1) and (m & 2) and not (m & 4))]
    micro = r11.microscope_relation(allowed, 3)
    assert micro['classes']['horn_AND_closed']
    parity = [m for m in range(8) if m.bit_count() % 2 == 0]
    pm = r11.microscope_relation(parity, 3)
    assert pm['classes']['affine']['exact']
    assert pm['anf']['algebraic_degree'] == 1


def test_r11_product_factorization_detects_cartesian_structure():
    relation = [m for m in range(16) if bool(m & 1) == bool(m & 2) and bool(m & 4) == bool(m & 8)]
    splits = r11.product_factor_splits(relation, 4)
    assert splits


def test_r11_preregistration_scope_does_not_claim_global_minimal_language():
    # The code-level output is explicitly scoped to same-variable CNF width.
    allowed = [0, 3, 5]
    micro = r11.microscope_relation(allowed, 3)
    assert 'minimum_same_variable_cnf_width' in micro['same_variable_cnf']
