from __future__ import annotations

import inspect

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r8b_width_barrier_hunt as r8b


def test_r8a_frozen_legacy_residual_count_and_hash_uniqueness():
    rows = r8a.frozen_residuals()
    assert len(rows) == 16
    assert len({r['formula_sha256'] for r in rows}) == 16
    assert {r['source']['suite'] for r in rows} == {'LEGACY_MAIN_SAT', 'LEGACY_UNSAT_CORE_STRESS'}
    assert all(r['stage'] == 'POST_RESTRICTION_PRE_UNIT' for r in rows)


def test_r8a_candidate_firewall_has_no_quarantined_search():
    fw = r8a.candidate_firewall()
    assert fw['pass'], fw
    assert not fw['forbidden_hits']


def test_r8b_existing_control_reproduces_width3_vs_width4():
    tear = r8b.load_tear_audit()
    cnf = r8b.to_cnf(tear.tseitin_cnf())
    s = r8b.sweep(cnf, (3, 4))
    assert s['3']['status'] == 'SATURATION_COMPLETE_NO_REFUTATION'
    assert s['4']['status'] == 'UNSAT'
    assert s['4']['proof_replay'] is True


def test_r8b_php4_input_is_nontrivially_within_width4():
    cnf = direct.f_php(4)
    assert max(len(c) for c in cnf) == 4
    assert len(direct.variables(cnf)) == 20


def test_r8b_candidate_path_does_not_call_shadow_dpll():
    src = inspect.getsource(r8b.sweep) + inspect.getsource(r8b.r7d.width_bounded_eliminate)
    assert 'dpll(' not in src
    assert 'exact_search_witness' not in src
