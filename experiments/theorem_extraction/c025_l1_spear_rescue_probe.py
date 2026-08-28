#!/usr/bin/env python3
"""Exact learned-prior spear probe against the frozen 39100 L1 witness.

This is a positive-existence accelerator only. Historical rescue motifs may
order candidates, but they cannot prune the full grammar and a negative spear
result has zero global NO_RESCUE authority.
"""
from __future__ import annotations

import json
from pathlib import Path

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP='OPEN'


def main():
    source,left,right=adv.build_selector_source(10,90,4,39100)
    product=adv.direct_selector_product(left,right)
    N=base.input_size_units(source); cap=N*N
    assert base.fingerprint(source)=='bc07cfeb7d1ef62916d7319ed59edc8d2e4a92ce34881a13186d2c47991c66bc'
    assert base.fingerprint(product)=='037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3'
    assert N==1102 and cap==1214404 and base.state_units(product)==72901

    state=base.EngineState(
        root=source,residual=product,fixed_assignment={},root_vars=base.vars_of(source),
        extension_defs=[],elimination_history=[base.ElimSnapshot(source,1,'PURE_ELIM')],
        seen=set(),N=N,cap_exponent=2,extension_exponent=2,ledger=base.Ledger(question_count=1)
    )
    candidates=core.v2.all_or_pair_candidates(product)
    historical=[(2,4),(2,-4),(-2,4),(-2,-4)]
    ordered=[]
    for p in historical + candidates[:32]:
        if p in candidates and p not in ordered:
            ordered.append(p)

    fresh=core.v2.next_fresh_extension(state)
    before_phi=state.progress_phi()
    rows=[]; rescue=None
    for p in ordered:
        idx=candidates.index(p)
        macro,cert=core.v2.apply_or_pair_v2(product,p[0],p[1],fresh)
        assert core.v2.verify_or_pair_v2(product,macro,cert)
        mu=base.state_units(macro)
        row={'pair':list(p),'pair_index':idx,'macro_units':mu,'macro_over_cap':mu>cap}
        if mu<=cap:
            elim=base.first_capped_elimination(state,macro,roots_only=True)
            if elim is not None:
                pivot,after,stats=elim
                assert base.verify_elimination_transition(macro,pivot,after,cap)
                after_phi=state.progress_phi(after,state.ledger.extension_count+1)
                row.update({'pivot':pivot,'after_units':base.state_units(after),'after_fingerprint':base.fingerprint(after),'before_phi':before_phi,'after_phi':after_phi,'progress_accepts':after_phi<before_phi,'elim_stats':stats})
                if after_phi<before_phi:
                    rescue=dict(row); rows.append(row); break
        rows.append(row)

    report={
      'schema':'JANUS/C025/L1-LEARNED-PRIOR-SPEAR-PROBE/v1',
      'status':'EXACT_V2_RESCUE_FOUND' if rescue else 'NO_RESCUE_IN_SPEAR_SCOPE__NO_GLOBAL_CONCLUSION',
      'candidate':{'source_fingerprint':base.fingerprint(source),'product_fingerprint':base.fingerprint(product),'N':N,'cap':cap,'product_units':base.state_units(product)},
      'global_pair_count':len(candidates),
      'ordered_scope_count':len(ordered),
      'rows':rows,
      'rescue':rescue,
      'scientific_boundary':{
        'learned_history_orders_only':True,
        'negative_spear_result_has_global_no_rescue_authority':False,
        'positive_exact_rescue_is_sufficient_to_show_this_witness_does_not_refute_L1':True,
        'full_fanout_still_required_for_global_no_rescue':True,
        'P_VS_NP':P_VS_NP,
      },
      'P_VS_NP':P_VS_NP,
    }
    Path('c025-l1-spear-rescue-probe.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
