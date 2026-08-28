#!/usr/bin/env python3
"""Minimal exact certificate for the winning v2 junction-relief mechanism.

Only frozen root pivot 2 is profiled before/after macro pair (2,3).  This isolates
the theorem-relevant identity from the broader 12-root census.  No post-subsumption
measurement is performed because C025 raw cap is pre-subsumption.
"""
from __future__ import annotations
import json
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_v2_junction_relief_microscope as slow
from experiments.theorem_extraction import c025_v2_junction_relief_microscope_fast as fast

P_VS_NP="OPEN"

def main()->int:
    source, product, _ = slow.build_witness()
    N, cap = slow.EXPECTED_N, slow.EXPECTED_CAP
    t=slow.pair_frequency(product,*slow.WINNING_PAIR)
    macro,cert=v2.apply_or_pair_v2(product,*slow.WINNING_PAIR,slow.FRESH_EXTENSION)
    assert v2.verify_or_pair_v2(product,macro,cert)
    assert cert['replaced_occurrences']==t==180
    pre=fast.raw_profile_fast(product,slow.WINNING_ROOT)
    post=fast.raw_profile_fast(macro,slow.WINNING_ROOT)
    p,q=pre['positive_parents'],pre['negative_parents']
    bound_p=p-t+1; bound_q=q+1
    guaranteed=t*(q+1)-(p+q+1)
    observed_pairs=pre['parent_pairs']-post['parent_pairs']
    relief=pre['raw_units']-post['raw_units']
    retained_delta=post['retained_units']-pre['retained_units']
    new_delta=post['unique_new_resolvent_units']-pre['unique_new_resolvent_units']
    assert post['positive_parents']<=bound_p and post['negative_parents']<=bound_q
    assert observed_pairs>=guaranteed
    assert relief==-(retained_delta+new_delta)==44197
    assert pre['raw_units']==382377 and post['raw_units']==338180
    assert post['raw_units']<=cap
    report={
      'schema':'JANUS/C025/V2-WINNING-ROOT-RELIEF-CERTIFICATE/v1',
      'status':'EXACT_LOCAL_RELIEF_CERTIFIED',
      'source_fingerprint':slow.EXPECTED_SOURCE_FP,
      'product_fingerprint':slow.EXPECTED_PRODUCT_FP,
      'N':N,'cap':cap,'pair':list(slow.WINNING_PAIR),'pair_frequency':t,'root_pivot':slow.WINNING_ROOT,
      'macro_state_units_before':base.state_units(product),'macro_state_units_after':base.state_units(macro),
      'macro_representation_reduction':base.state_units(product)-base.state_units(macro),
      'pre':pre,'post':post,
      'parent_product':{
        'p':p,'q':q,'pre_pairs':pre['parent_pairs'],
        'precanonical_post_positive':bound_p,'precanonical_post_negative':bound_q,
        'guaranteed_relief_formula':'t*(q+1)-(p+q+1)',
        'guaranteed_parent_pair_relief':guaranteed,
        'observed_parent_pair_relief':observed_pairs
      },
      'raw_relief':{
        'junction_relief':relief,
        'retained_units_delta':retained_delta,
        'unique_new_resolvent_units_delta':new_delta,
        'post_cap_margin':cap-post['raw_units']
      },
      'scientific_boundary':{
        'parent_pair_bound_is_proved_syntactic':True,
        'raw_relief_numbers_are_exact_for_one_frozen_reachable_witness':True,
        'does_not_prove_raw_relief_lower_bound_in_general':True,
        'does_not_prove_v2_totality':True,
        'L1A':'REFUTED','L1B':'REFUTED','L1':'OPEN','P2_REACHABLE_PRESERVATION':'OPEN','P_VS_NP':P_VS_NP
      },
      'P_VS_NP':P_VS_NP
    }
    print(json.dumps(report,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
