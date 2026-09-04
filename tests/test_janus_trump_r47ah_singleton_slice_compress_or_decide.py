import importlib.util
from pathlib import Path


MODULE = Path(__file__).resolve().parents[1] / 'experiments' / 'janus_trump_r47ah_singleton_slice_compress_or_decide.py'
spec = importlib.util.spec_from_file_location('r47ah', MODULE)
r47ah = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r47ah)


def test_exact3_has_no_r44bw_binary_equality_certificates():
    f = r47ah.canonical_formula([
        (1, 2, 3),
        (-1, 2, 4),
        (1, -3, -4),
    ])
    q, classes = r47ah.exact_congruence_quotient(f)
    assert r47ah.is_exact3(f)
    assert r47ah.is_singleton_classes(classes)
    assert q == r47ah.dense_rename(f)


def test_dense_rename_only_on_non_dense_exact3():
    f = r47ah.canonical_formula([
        (5, -9, 20),
        (-5, 9, 20),
    ])
    q, classes = r47ah.exact_congruence_quotient(f)
    assert r47ah.is_singleton_classes(classes)
    assert q == ((1, -2, 3), (-1, 2, 3))
    assert len(q) == len(f)
    assert sum(map(len, q)) == sum(map(len, f))


def test_outside_slice_explicit_equality_can_compress():
    f = r47ah.canonical_formula([
        (-1, 2), (1, -2),
        (1, 3, 4), (-2, 3, 4),
    ])
    q, classes = r47ah.exact_congruence_quotient(f)
    assert not r47ah.is_singleton_classes(classes)
    assert len(r47ah.variables(q)) < len(r47ah.variables(f))
    assert r47ah.exact_sat(f) == r47ah.exact_sat(q)


def test_full_audit_and_firewalls():
    result = r47ah.audit()
    a = result['finite_structural_audit']
    assert a['n3_all_clause_subsets'] == 256
    assert a['n4_up_to_3_clauses'] == 5489
    assert a['total_formulas_checked'] == 5745
    assert a['result'] == 'PASS'
    assert result['finite_semantic_calibration_n3']['authority'].startswith('CALIBRATION_ONLY')
    assert result['compression_lane'].startswith('OPEN_')
    assert result['direct_decider_lane'].startswith('OPEN_')
    assert result['SAT_IN_P'] == 'NOT_PROVED'
    assert result['P_VS_NP'] == 'OPEN'
    assert result['TRUMP_finished'] is False
