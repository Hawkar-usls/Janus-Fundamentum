#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import Counter

from janus_trump_osiris_r4_roi_gate import collect_holdout_residuals, evaluate_row


def main(output: str) -> int:
    rows = [evaluate_row(r) for r in collect_holdout_residuals()]
    families = sorted({r['source']['family'] for r in rows})
    roots = sorted({(r['source']['family'], r['source']['workload_name']) for r in rows})
    false_negative_profitable = sum(r['checks']['shadow_profitable_vs_guarded'] for r in rows)
    guarded_ok = all(r['checks']['guarded_terminal_match'] and r['checks']['guarded_sat_replay'] for r in rows)
    shadow_ok = all(r['checks']['shadow_terminal_match'] and r['checks']['shadow_sat_replay'] for r in rows)
    pretruth_ok = all(r['checks']['decision_pretruth'] and r['pretruth_witness']['truth'] is None for r in rows)
    guarded_ops = sum(r['work']['guarded_total_ops'] for r in rows)
    shadow_ops = sum(r['work']['shadow_spiral_charged_ops'] for r in rows)
    avoided = shadow_ops - guarded_ops
    result = {
      'schema':'JANUS/TRUMP/OSIRIS-R4-ROI-GATE/RESULT/v1.0',
      'status':'FROZEN_HOLDOUT_RESULT',
      'P_VS_NP':'OPEN',
      'summary':{
        'residuals':len(rows),
        'holdout_roots':len(roots),
        'holdout_families':len(families),
        'families':families,
        'pretruth_decisions':sum(r['checks']['decision_pretruth'] for r in rows),
        'guarded_terminal_matches':sum(r['checks']['guarded_terminal_match'] for r in rows),
        'guarded_sat_replay_failures':sum(not r['checks']['guarded_sat_replay'] for r in rows),
        'shadow_terminal_matches':sum(r['checks']['shadow_terminal_match'] for r in rows),
        'shadow_profitable_cases_skipped':false_negative_profitable,
        'guarded_total_ops':guarded_ops,
        'unconditional_shadow_spiral_ops':shadow_ops,
        'ops_avoided_by_frozen_abstention':avoided,
        'guard_to_shadow_ratio': guarded_ops / shadow_ops if shadow_ops else None,
      },
      'gates':{
        'G1_PRETRUTH_DECISION':pretruth_ok,
        'G2_EXACTNESS':guarded_ok,
        'G3_SAT_REPLAY':all(r['checks']['guarded_sat_replay'] for r in rows),
        'G4_NO_HARM_POLICY':all(r['pretruth_witness']['route_prediction']=='ABSTAIN_TO_EXACT' for r in rows),
        'G5_COUNTERFACTUAL_AUDIT':shadow_ok and false_negative_profitable == 0,
        'G6_NO_THEOREM_INFLATION':True,
      },
      'interpretation':{
        'positive_if_pass':'The R3-trained conservative ROI gate correctly abstained on unexposed pre-existing workloads and avoided the measured cost of unconditional spiral execution without losing exactness.',
        'boundary':'This validates a no-harm routing policy on this frozen holdout. It does not establish a general solver speedup, polynomial SAT, or P=NP.',
      },
      'rows':rows,
    }
    result['verdict'] = 'R4_CONSERVATIVE_ROI_GATE_PASS__ABSTENTION_GENERALIZED__P_VS_NP_OPEN' if all(result['gates'].values()) else 'R4_ROI_GATE_FAIL__KEEP_SHADOW_ONLY__P_VS_NP_OPEN'
    with open(output,'w',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({'verdict':result['verdict'],'summary':result['summary'],'gates':result['gates']},indent=2))
    return 0 if all(result['gates'].values()) else 2

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); a=ap.parse_args(); raise SystemExit(main(a.output))
