import time
from experiments import janus_trump_r15d_bounded_observer_equivalent_refactor as r15d
from experiments import janus_trump_r15c_shared_extension_quotient_calibration as r15c


def test_r15d_minimizer_matches_r15c_examples():
    samples=[
        {(1,), (1,2), (1,2,3), (2,3), (2,3,4)},
        {(1,2,3),(-1,2,3),(2,3),(4,5,6),(4,5)},
    ]
    for s in samples:
        assert r15d.minimize_width3_basis_bounded(s,time.monotonic()+5)==r15c.minimize_width3_basis(s)


def test_r15d_variable_choice_matches_r15c():
    f={(1,2,3),(-1,2,4),(1,-2,5),(-3,4,5)}
    internal={1,2,3,4,5}
    assert r15d.choose_internal_var_bounded(f,internal,time.monotonic()+5)==r15c.choose_internal_var(f,internal)


def test_r15d_factor_batch_matches_r15c_content_shape():
    wide={(1,2,3,4),(1,2,5,6)}
    c1={}; c2={}
    a,n1,s1=r15d.factor_batch_shared_bounded(wide,c1,7,time.monotonic()+5)
    b,n2,s2=r15c.factor_batch_shared(wide,c2,7)
    assert set(a)==set(b)
    assert n1==n2 and c1==c2
    assert s1==s2


def test_r15d_equivalence_controls():
    assert r15d.equivalence_controls() is True


def test_r15d_candidate_firewall():
    fw=r15d.candidate_firewall(); assert fw['pass'], fw
