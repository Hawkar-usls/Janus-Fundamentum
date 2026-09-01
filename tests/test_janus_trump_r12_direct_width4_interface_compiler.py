import janus_trump_r12_direct_width4_interface_compiler as r12


def test_r12_canonical_name_vs_content_quotient():
    assert r12.canonical_clause([3, 1, 3, -2]) == r12.canonical_clause([-2, 1, 3])
    assert r12.canonical_clause([1, 2]) != r12.canonical_clause([1, -2])
    assert r12.canonical_clause([1, -1, 2]) is None


def test_r12_resolution_replay_control():
    out = r12.saturate_width4(((1, 2), (-1, 3)))
    assert (2, 3) in out['clauses']
    assert r12.replay_derivations(out)


def test_r12_duplicate_paths_are_collapsed():
    out = r12.saturate_width4(((1, 2), (-1, 3), (-1, 4), (-3, 4)))
    assert len(out['clauses']) == len(set(out['clauses']))
    assert r12.replay_derivations(out)


def test_r12_candidate_firewall():
    fw = r12.candidate_firewall()
    assert fw['pass'], fw


def test_r12_frozen_targets():
    assert r12.OPEN_INDICES == (3, 7)
    assert r12.EXPECTED[3]['allowed'] == 135
    assert r12.EXPECTED[7]['allowed'] == 127
    assert r12.WIDTH_CAP == 4
