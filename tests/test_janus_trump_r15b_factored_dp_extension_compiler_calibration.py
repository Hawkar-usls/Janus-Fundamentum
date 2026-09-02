from experiments import janus_trump_r15b_factored_dp_extension_compiler_calibration as r15b


def test_r15b_factor_width4_projection_equivalence():
    clause=(1,-2,3,-4)
    enc,a,_=r15b.factor_width4(clause,5)
    assert max(map(len,enc))<=3
    for mask in range(16):
        vals={i+1:bool((mask>>i)&1) for i in range(4)}
        original=any((vals[abs(l)] if l>0 else not vals[abs(l)]) for l in clause)
        possible=False
        for av in (False,True):
            x=dict(vals); x[a]=av
            if all(any((x[abs(l)] if l>0 else not x[abs(l)]) for l in c) for c in enc): possible=True
        assert possible==original


def test_r15b_resolve_width_bound():
    p=(1,2,3); n=(-1,4,5)
    r=r15b.resolve_on(p,n,1)
    assert r is not None and len(r)==4


def test_r15b_tautological_resolvent_removed():
    p=(1,2,3); n=(-1,-2,4)
    assert r15b.resolve_on(p,n,1) is None


def test_r15b_tiny_projection_control():
    assert r15b.tiny_projection_control() is True


def test_r15b_candidate_firewall():
    fw=r15b.candidate_firewall()
    assert fw['pass'], fw
