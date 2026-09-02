from experiments import janus_trump_r15a_auxiliary_representation_escape_control as r15a


def test_r15a_or_equivalence_truth_table():
    clauses = r15a.encode_or_equiv(3, 1, 2)
    for mask in range(4):
        base = r15a.bridge_assignment(2, mask)
        expected = base[1] or base[2]
        for z in (False, True):
            a = dict(base); a[3] = z
            sat = r15a.satisfies_cnf(clauses, a)
            assert sat == (z == expected)


def test_r15a_width4_clause_uses_one_aux():
    enc, defs, nxt = r15a.encode_clause_width3((1,2,3,4), 5)
    assert len(defs) == 1
    assert nxt == 6
    assert max(map(len, enc)) <= 3


def test_r15a_width6_clause_uses_three_aux():
    enc, defs, nxt = r15a.encode_clause_width3((1,2,3,4,5,6), 7)
    assert len(defs) == 3
    assert nxt == 10
    assert max(map(len, enc)) <= 3


def test_r15a_exhaustive_single_clause_projection_equivalence():
    clause = (1,-2,3,-4,5,-6)
    enc, defs, _ = r15a.encode_clause_width3(clause, 7)
    for mask in range(1 << 6):
        base = r15a.bridge_assignment(6, mask)
        original = any(r15a.eval_lit(l, base) for l in clause)
        ext = r15a.extend_assignment(mask, 6, defs)
        assert r15a.satisfies_cnf(enc, ext) == original


def test_r15a_structural_control():
    assert r15a.structural_controls() is True
