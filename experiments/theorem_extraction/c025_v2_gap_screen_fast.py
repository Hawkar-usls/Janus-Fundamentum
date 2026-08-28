#!/usr/bin/env python3
"""Optimized ZERO-AUTHORITY v2-gap candidate screen.

The specialized uniform-product macro identity is checked against ORIGINAL v2
on a small exact selector-product fixture.  Large candidates then use only the
specialized macro + exact raw cap stream for ranking.  A large SCREEN_NONE is
never a theorem result; it only triggers the expensive original frozen replay.
"""
from __future__ import annotations
import argparse,json
from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_v2_gap_adversarial_search as gap

P_VS_NP='OPEN'

def small_equivalence_selftest()->dict:
    source,left,right=adv.build_selector_source(6,18,3,37001)
    product=adv.direct_selector_product(left,right)
    pairs=core.v2.all_or_pair_candidates(product)
    fresh=max(base.vars_of(source))+1
    idxs=sorted(set([0,1,5,len(pairs)//2,len(pairs)-1]))
    for i in idxs:
        a,b=pairs[i]
        fast=gap.fast_apply_uniform_product(product,a,b,fresh)
        orig,cert=core.v2.apply_or_pair_v2(product,a,b,fresh)
        assert fast==orig,(i,(a,b))
        assert core.v2.verify_or_pair_v2(product,orig,cert)
    return {'fixture_source_fingerprint':base.fingerprint(source),'fixture_product_fingerprint':base.fingerprint(product),'pairs_checked':idxs}

def fast_scan(source:base.CNF, product:base.CNF, cap:int)->dict:
    roots=[v for v in base.vars_of(source) if v in set(base.vars_of(product))]
    pairs=core.v2.all_or_pair_candidates(product)
    fresh=max(base.vars_of(source))+1
    probes=0
    for pi,pair in enumerate(pairs):
        macro=gap.fast_apply_uniform_product(product,pair[0],pair[1],fresh)
        mu=base.state_units(macro)
        if mu>cap: continue
        for x in roots:
            probes+=1
            r=adv.raw_units_probe(macro,x,cap)
            if not r['overflow']:
                return {'rescue_exists':True,'pair_index_zero_based':pi,'pair':list(pair),'pivot':x,
                        'macro_units':mu,'raw_units':int(r['raw_units_observed']),'cap_margin':int(r['raw_units_observed'])-cap,
                        'pairs_tested_through_rescue':pi+1,'root_probes':probes,'candidate_pair_count':len(pairs)}
    return {'rescue_exists':False,'pairs_tested_through_rescue':len(pairs),'root_probes':probes,'candidate_pair_count':len(pairs)}

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--leaf-nvars',type=int,required=True); p.add_argument('--leaf-clauses',type=int,required=True); p.add_argument('--leaf-width',type=int,default=4); p.add_argument('--seed',type=int,required=True); a=p.parse_args()
    gate=small_equivalence_selftest()
    source,left,right=adv.build_selector_source(a.leaf_nvars,a.leaf_clauses,a.leaf_width,a.seed)
    product=adv.direct_selector_product(left,right); N=base.input_size_units(source); cap=N*N
    ordinary=gap.ordinary_pressure(product,cap)
    screen=fast_scan(source,product,cap) if ordinary['all_overflow'] else None
    status='ORDINARY_NOT_ALL_OVERFLOW' if screen is None else ('SCREEN_RESCUE_FOUND' if screen['rescue_exists'] else 'SCREEN_NONE__ORIGINAL_REPLAY_REQUIRED')
    print(json.dumps({'schema':'JANUS/C025/V2-GAP-FAST-SCREEN/v1','status':status,
      'source_meta':{'leaf_nvars':a.leaf_nvars,'leaf_clauses':a.leaf_clauses,'leaf_width':a.leaf_width,'seed':a.seed,'N':N,'cap':cap,'product_state_units':base.state_units(product),'source_fingerprint':base.fingerprint(source),'product_fingerprint':base.fingerprint(product)},
      'small_original_equivalence_gate':gate,
      'ordinary':{k:v for k,v in ordinary.items() if k!='rows'},'screen':screen,
      'scientific_boundary':{'large_screen_has_theorem_authority':False,'small_fixture_original_equivalence_passed':True,'screen_none_requires_original_replay':True,'L1':'OPEN','P2_REACHABLE_PRESERVATION':'OPEN','P_VS_NP':P_VS_NP}},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
