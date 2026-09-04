from experiments import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8
from experiments import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
from experiments import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
from experiments import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33


def first_immediate():
    for worker, n in enumerate(range(6, 11)):
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            root, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(root)) != n:
                continue
            state = r50g8.canon(root)
            seen = set()
            for _ in range(200):
                h = r50g4.fhash(state)
                assert h not in seen
                seen.add(h)
                if r50g4.micro_r33_status(state)["status"] == "IMMEDIATE_BVE_W4_ESCAPE":
                    return state
                step = r50g4.refined_exact_step(state)
                if step["kind"] in ("TERMINAL", "OPEN_OBSTRUCTION"):
                    break
                state = r50g8.canon(step["successor"])
    raise AssertionError("frozen immediate BVE witness missing")


def test_frozen_immediate_is_pre_bve_clean():
    f = first_immediate()
    assert r50g8.pre_bve_clean(f)


def test_post_dp_wide_origin_and_same_pivot_replay():
    row = r50g8.inspect_immediate_bve_state(first_immediate())
    assert row["applicable"] is True
    assert row["post_DP_width"] > 4
    assert row["post_DP_wide_clause_count"] >= 1
    assert row["post_DP_all_wide_are_cross_resolvents"] is True
    assert row["independent_replay_pass"] is True
    assert row["same_pivot_safe"] is True


def test_nonblocking_supports_are_distinct_per_literal():
    c = (1, 2, 3, 4, 5)
    f = r50g8.canon([
        c,
        (-1, 6, 7),
        (-2, 8, 9),
        (-3, 10, 11),
        (-4, 12, 13),
        (-5, 14, 15),
    ])
    supports = r50g8.nonblocking_supports_for_clause(f, c)
    assert supports is not None
    assert len(supports) == 5
    assert len(set(supports.values())) == 5


def test_firewall_cannot_promote_finite_no_find():
    fw = r50g8.firewall(False)
    assert fw["HEURISTIC_AUTHORITY"] is False
    assert fw["FINITE_NO_FIND_IMPLIES_THEOREM"] is False
    assert fw["WIDE_ANCESTRY_IMPOSSIBILITY_THEOREM"] == "OPEN"
    assert fw["IMMEDIATE_BVE_CASE_ELIMINATED"] is False
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
