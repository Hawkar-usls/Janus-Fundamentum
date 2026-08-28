#!/usr/bin/env python3
"""Zero-authority front-door sentinel for selector-product adversarial chassis.

A chassis is useless as an L1 counterexample if an early frozen-v2 pair already
opens an exact capped root elimination.  Therefore this ranking-only tool checks
the first K canonical v2 pairs BEFORE paying for ordinary-all-overflow or frozen
reachability.  Any rescue rejects the chassis.  No-rescue has no theorem authority.
"""
from __future__ import annotations
import argparse,json
from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_v2_gap_adversarial_search as gap
from experiments.theorem_extraction.c025_v2_gap_screen_fast import small_equivalence_selftest

P_VS_NP='OPEN'

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--leaf-nvars',type=int,required=True); p.add_argument('--leaf-clauses',type=int,required=True); p.add_argument('--leaf-width',type=int,default=4); p.add_argument('--seed',type=int,required=True); p.add_argument('--first-k',type=int,default=8); a=p.parse_args()
    gate=small_equivalence_selftest()
    source,left,right=adv.build_selector_source(a.leaf_nvars,a.leaf_clauses,a.leaf_width,a.seed)
    product=adv.direct_selector_product(left,right); N=base.input_size_units(source); cap=N*N; fresh=max(base.vars_of(source))+1
    pairs=core.v2.all_or_pair_candidates(product); roots=[v for v in base.vars_of(source) if v in set(base.vars_of(product))]
    result=None; probes=0
    for pi,pair in enumerate(pairs[:a.first_k]):
        macro=gap.fast_apply_uniform_product(product,pair[0],pair[1],fresh)
        for x in roots:
            probes+=1; r=adv.raw_units_probe(macro,x,cap)
            if not r['overflow']:
                result={'pair_index_zero_based':pi,'pair':list(pair),'pivot':x,'raw_units':int(r['raw_units_observed']),'cap':cap,'cap_margin':int(r['raw_units_observed'])-cap,'macro_units':base.state_units(macro)}; break
        if result: break
    print(json.dumps({'schema':'JANUS/C025/V2-FRONTDOOR-SENTINEL/v1','status':'EARLY_V2_RESCUE_FOUND__REJECT_CHASSIS' if result else 'NO_RESCUE_IN_FIRST_K__NO_THEOREM_AUTHORITY','source_meta':{'leaf_nvars':a.leaf_nvars,'leaf_clauses':a.leaf_clauses,'leaf_width':a.leaf_width,'seed':a.seed,'N':N,'cap':cap,'product_units':base.state_units(product),'pair_count':len(pairs)},'first_k':a.first_k,'root_probes':probes,'rescue':result,'small_equivalence_gate':gate,'scientific_boundary':{'ranking_only':True,'no_rescue_is_not_evidence_of_L1_failure':True,'rescue_exact_raw_screen_can_reject_chassis_from_followup':True,'P_VS_NP':P_VS_NP}},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
