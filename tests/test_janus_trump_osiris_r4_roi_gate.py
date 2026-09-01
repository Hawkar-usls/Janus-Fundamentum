from __future__ import annotations
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments'
if str(EXP) not in sys.path:
    sys.path.insert(0, str(EXP))

from janus_trump_osiris_r4_roi_gate import (
    R4_RULE_ID,
    collect_holdout_residuals,
    evaluate_row,
    frozen_roi_prediction,
    graph_signature,
    holdout_roots,
)


def test_frozen_rule_abstains_without_truth():
    for root in holdout_roots():
        sig = graph_signature(root.formula)
        assert frozen_roi_prediction(sig) == 'ABSTAIN_TO_EXACT'


def test_holdout_sources_are_new_families():
    old = {'EASY_2SAT_CHAIN','EQUALITY_PAIR_CNF','PIGEONHOLE_PHP','RANDOM_3SAT_NEAR_DENSE','TSEITIN_CYCLE_PARITY'}
    roots = holdout_roots()
    assert roots
    assert not ({r.family for r in roots} & old)


def test_pretruth_witness_firewall():
    rows = collect_holdout_residuals()
    assert rows
    for row in rows:
        w = row['pretruth_witness']
        assert w['truth'] is None
        assert w['candidate_result'] is None
        assert w['verification_result'] is None
        assert w['frozen_rule_id'] == R4_RULE_ID
        assert w['route_prediction'] == 'ABSTAIN_TO_EXACT'


def test_small_sample_exactness_and_shadow_audit():
    rows = collect_holdout_residuals()[:8]
    out = [evaluate_row(r) for r in rows]
    assert all(r['checks']['guarded_terminal_match'] for r in out)
    assert all(r['checks']['guarded_sat_replay'] for r in out)
    assert all(r['checks']['shadow_terminal_match'] for r in out)
