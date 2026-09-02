from experiments import janus_trump_r15c_shared_extension_quotient_calibration as r15c


def test_r15c_subsumption_minimal_basis():
    f={(1,), (1,2), (1,2,3), (2,3), (2,3,4)}
    out=r15c.minimize_width3_basis(f)
    assert (1,) in out
    assert (1,2) not in out
    assert (1,2,3) not in out
    assert (2,3) in out
    assert (2,3,4) not in out


def test_r15c_shared_atom_reused_in_batch():
    wide={(1,2,3,4),(1,2,5,6)}
    cache={}
    clauses,nxt,stats=r15c.factor_batch_shared(wide,cache,7)
    assert stats['new_atoms']==1
    assert stats['reuse_hits']==1
    assert len(cache)==1
    assert max(len(c) for c in clauses)<=3


def test_r15c_pair_key_commutative():
    assert r15c.pair_key(3,-2)==r15c.pair_key(-2,3)


def test_r15c_tiny_shared_control():
    assert r15c.tiny_shared_control() is True


def test_r15c_candidate_firewall():
    fw=r15c.candidate_firewall()
    assert fw['pass'], fw
