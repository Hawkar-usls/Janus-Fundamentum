from experiments import janus_trump_r14_width_witness_forensics as r14


def test_r14_clause_semantics():
    # Clause (1,-2) is false only on x1=0,x2=1.
    assert r14.satisfies_clause(0b00, (1, -2)) is True
    assert r14.satisfies_clause(0b01, (1, -2)) is True
    assert r14.satisfies_clause(0b10, (1, -2)) is False
    assert r14.satisfies_clause(0b11, (1, -2)) is True


def test_r14_allowed_by_is_exact_for_tiny_cnf():
    cs = [(1,), (-2,)]
    assert r14.allowed_by(cs, 2) == {0b01}


def test_r14_minimum_separator_prefers_fewest_then_width():
    fps = (0, 1, 2)
    missing = [
        (1,),       # rejects 0,2
        (2,),       # rejects 0,1
        (1, 2),    # rejects only 0
        (-1, -2),  # rejects only 3, irrelevant
    ]
    sep = r14.minimum_separator(missing, fps)
    assert sep is not None
    assert sep["clause_count"] == 2
    assert sep["max_width"] == 1


def test_r14_width_hull_monotone_false_positives():
    exact = {0b11}
    primes = [(1,), (2,)]
    rows = r14.width_hull(primes, 2, exact)
    assert rows[0]["false_positive_count"] >= rows[1]["false_positive_count"]
    assert rows[1]["exact"] is True


def test_r14_frozen_constants_are_r13_receipt_values():
    assert r14.W05_ID == "R13-W05"
    assert r14.EXPECTED_ALLOWED == 287
    assert r14.EXPECTED_K4_ALLOWED == 292
    assert r14.EXPECTED_FALSE_POSITIVES == (32050, 32546, 32562, 65328, 65332)
    assert r14.EXPECTED_MISSING == 14
