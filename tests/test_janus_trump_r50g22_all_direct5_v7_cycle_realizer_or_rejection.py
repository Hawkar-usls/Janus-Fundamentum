import janus_trump_r50g22_all_direct5_v7_cycle_realizer_or_rejection as r50g22


def test_declared_frozen_family_size_and_hub_maps():
    assert r50g22.DECLARED_FAMILY_SIZE == 11520
    for k in range(2, 8):
        h = r50g22.hub_map_for_cycle_length(k)
        assert set(h) == set(range(1, 8))
        assert all(h[v] != v for v in h)
        assert h[k] == 1
        assert h[1] == 2


def test_all_three_direct5_geometries_construct_exact_width5_and_omit_hub():
    for geometry in r50g22.GEOMETRIES:
        p, n, c = r50g22.direct5_pair(1, 2, 127, geometry, 0)
        assert len(c) == 5
        assert 1 not in {abs(x) for x in c}
        assert 2 not in {abs(x) for x in c}
        assert 2 not in {abs(x) for x in p}
        assert 2 not in {abs(x) for x in n}
        g = r50g22.r50g14.parent_geometry(p, n, 1)
        assert g["tautological"] is False
        assert g["resolvent_width"] == 5
        assert tuple(g["resolvent"]) == c


def test_seven_cycle_source_replays_all_designated_direct5_certificates():
    out = r50g22.source_reduction_control()
    assert out["all_seven_designated_direct5_certificates"] is True
    assert out["all_designated_parent_pairs_omit_declared_hub"] is True
    assert out["hub_map"] == {"1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 1}


def test_sign_masks_and_rotations_preserve_exact_designated_ancestry():
    for sign_mask, rotation in ((0, 0), (1, 1), (42, 3), (127, 4)):
        f, h, d = r50g22.build_source(3, sign_mask, "4x4_OVERLAP1", rotation)
        assert set(r50g22.r33.variables(f)) == set(range(1, 8))
        assert r50g22.max_width(f) <= 4
        audit = r50g22.designated_ancestry_audit(f, h, d)
        assert len(audit) == 7
        assert all(row["direct5_certificate_count"] >= 1 for row in audit.values())
