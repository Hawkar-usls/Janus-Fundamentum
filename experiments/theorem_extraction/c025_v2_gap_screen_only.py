#!/usr/bin/env python3
"""Screen-only front end for the frozen v2-gap adversarial search.

This intentionally performs NO original reachability replay.  It is only a fast
candidate-ranking lane.  A rescue found here is useful for rejecting a candidate
from further theorem work.  A NONE result has zero theorem authority and must be
followed by unmodified frozen reachability + full v2 replay.
"""
from __future__ import annotations
import argparse,json
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_v2_gap_adversarial_search as gap

P_VS_NP='OPEN'

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--leaf-nvars',type=int,required=True)
    p.add_argument('--leaf-clauses',type=int,required=True)
    p.add_argument('--leaf-width',type=int,default=4)
    p.add_argument('--seed',type=int,required=True)
    a=p.parse_args()
    source,left,right=adv.build_selector_source(a.leaf_nvars,a.leaf_clauses,a.leaf_width,a.seed)
    product=adv.direct_selector_product(left,right)
    N=base.input_size_units(source); cap=N*N
    ordinary=gap.ordinary_pressure(product,cap)
    screen=gap.fast_v2_first_rescue(source,product,cap) if ordinary['all_overflow'] else None
    report={
      'schema':'JANUS/C025/V2-GAP-SCREEN-ONLY/v1',
      'status':('SCREEN_RESCUE_FOUND' if screen and screen['rescue_exists'] else
                'SCREEN_NONE__ORIGINAL_REPLAY_REQUIRED' if screen is not None else
                'ORDINARY_NOT_ALL_OVERFLOW'),
      'source_meta':{
        'leaf_nvars':a.leaf_nvars,'leaf_clauses':a.leaf_clauses,'leaf_width':a.leaf_width,'seed':a.seed,
        'N':N,'cap':cap,'product_state_units':base.state_units(product),
        'source_fingerprint':base.fingerprint(source),'product_fingerprint':base.fingerprint(product)},
      'ordinary':{k:v for k,v in ordinary.items() if k!='rows'},
      'fast_v2_screen':screen,
      'scientific_boundary':{
        'screen_only':True,'original_reachability_replay_performed':False,
        'screen_none_has_theorem_authority':False,'screen_rescue_can_reject_candidate_from_followup':True,
        'L1':'OPEN','P2_REACHABLE_PRESERVATION':'OPEN','P_VS_NP':P_VS_NP}}
    print(json.dumps(report,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
