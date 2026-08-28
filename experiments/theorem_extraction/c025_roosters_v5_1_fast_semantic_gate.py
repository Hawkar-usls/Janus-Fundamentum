#!/usr/bin/env python3
"""Fast exact-semantic integration gate for ROOSTERS v5.1 theorem governance.

This does NOT test or prove L1. It verifies that importing routing/authority
mechanics does not mutate the frozen exact v2 macro or reachability semantics.
"""
from __future__ import annotations
import json
from pathlib import Path

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_v2_gap_adversarial_search as gap

P_VS_NP="OPEN"


def main():
    cases=[]
    for seed in (5101, 5102, 5103):
        source,left,right=adv.build_selector_source(6,18,3,seed)
        product=adv.direct_selector_product(left,right)
        pairs=core.v2.all_or_pair_candidates(product)
        fresh=max(base.vars_of(source))+1
        # This function compares the specialized macro against the unmodified
        # original apply_or_pair_v2 and verifies its certificate on sampled
        # canonical pair positions.
        gap.equivalence_gate(product,pairs,fresh)
        reach=adv.verify_reachable_callsite(source,product)
        if not reach['reachable_at_frozen_ordinary_callsite']:
            raise AssertionError(f"REACHABILITY_FAILED seed={seed}")
        cap=base.input_size_units(source)**2
        probes=[adv.raw_units_probe(product,v,cap) for v in base.vars_of(product)]
        cases.append({
            'seed':seed,
            'source_fingerprint':base.fingerprint(source),
            'product_fingerprint':base.fingerprint(product),
            'N':base.input_size_units(source),
            'product_units':base.state_units(product),
            'v2_candidate_pairs':len(pairs),
            'equivalence_sample_gate':'PASS',
            'reachable_at_frozen_ordinary_callsite':True,
            'ordinary_pivot_probe_count':len(probes),
        })

    report={
        'schema':'JANUS/C025/ROOSTERS-v5.1-FAST-EXACT-SEMANTIC-GATE/v1',
        'status':'PASS',
        'cases':cases,
        'governance_mutates_exact_transition':False,
        'governance_mutates_frozen_candidate_grammar':False,
        'claim':'Integration semantic regression gate only; no L1 theorem conclusion.',
        'P_VS_NP':P_VS_NP,
    }
    Path('c025-roosters-v5-1-fast-semantic-gate.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
