from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g1_r33_w4_domain_escape_guarded_replay as r50g1


def test_guarded_step_never_commits_wide_persisted_successor():
    for seed in (51100000, 51100001, 51100002):
        f, _ = __import__('janus_trump_r50g_smallest_first_exact_deadcore_falsifier').make_planted(seed, 10, 30, '3CNF')
        if len(r33.variables(f)) != 10:
            continue
        step = r50g1.guarded_exact_step(f)
        if step['kind'] == 'NONTERMINAL':
            assert r50g1.max_width(step['successor']) <= 4


def test_firewall_does_not_promote_finite_repair():
    out = r50g1.run()
    assert out['firewall']['FINITE_REPAIR_SUCCESS_PROVES_U'] is False
    assert out['firewall']['SAT_IN_P'] == 'NOT_PROVED'
    assert out['firewall']['P_VS_NP'] == 'OPEN'
    assert out['firewall']['TRUMP_finished'] is False
