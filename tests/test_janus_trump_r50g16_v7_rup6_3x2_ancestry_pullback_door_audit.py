import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g15_rup6_hub_bve_blockade_saturation as r50g15
import janus_trump_r50g16_v7_rup6_3x2_ancestry_pullback_door_audit as r16


def test_frozen_family_size_and_domain():
    assert len(r16.NEG2) * len(r16.NEG3) * len(r16.NEG6) * len(r16.BLOCKERS) == 3024
    source, spec = next(r16.candidate_sources())
    assert set(r33.variables(source)) == set(range(1, 8))
    assert max(len(c) for c in source) <= 4
    assert spec["neg2"] == [-2, 4]
    assert spec["neg3"] == [-3, 4]
    assert spec["neg6"] == [-6, 2]
    assert spec["blocker"] is None


def test_r50g15_integer_boundary_is_3x2():
    b = r50g15.integer_saturation_boundary()
    assert b["minimum_total_hub_occurrences"] == 5
    assert b["unique_minimal_integer_pair"]["p"] == 3
    assert b["unique_minimal_integer_pair"]["n"] == 2


def test_mandatory_parent_pair_generates_canonical_wide6():
    source = r33.canonical_formula(r16.MANDATORY)
    pos = next(c for c in source if 1 in c)
    neg = next(c for c in source if -1 in c)
    u = (set(pos) - {1}) | (set(neg) - {-1})
    assert not any(-x in u for x in u)
    assert r33.canonical_clause(u) == r16.WIDE6


def test_finite_family_firewall_is_not_universal_proof():
    assert r16.GATE.endswith("ANCESTRY_PULLBACK_AND_DOOR_AUDIT")
    # The experiment is allowed to discover an exact witness, but finite no-find
    # never changes the universal theorem status by itself.
    assert 3024 < 2 ** 938
