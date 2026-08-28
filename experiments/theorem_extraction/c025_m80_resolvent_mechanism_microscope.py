#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_root_pivot_grammar_falsifier as common

M=80
SEED=32100+M
EXPECTED_PRODUCT='2e92d85f5c02976a9a5d6036dbc83d31f88236e6455c7e27f5f9224e8c02708e'
PAIR=(2,4)
PIVOT=2

def state(root):
    return base.EngineState(root=root,residual=root,fixed_assignment={},root_vars=base.vars_of(root),extension_defs=[],elimination_history=[],seen=set(),N=base.input_size_units(root),cap_exponent=2,extension_exponent=2,ledger=base.Ledger())

def main():
    root=common.selector_product_case(8,M,4,SEED)
    st=state(root)
    first=base.first_capped_elimination(st); assert first is not None
    pv,product,_=first; assert pv==1
    assert base.verify_elimination_transition(root,1,product,st.state_cap)
    assert base.fingerprint(product)==EXPECTED_PRODUCT
    fresh=max(base.vars_of(product))+1
    macro,cert=v2.apply_or_pair_v2(product,PAIR[0],PAIR[1],fresh)
    assert v2.verify_or_pair_v2(product,macro,cert)
    pos=[c for c in macro if PIVOT in c]
    neg=[c for c in macro if -PIVOT in c]
    retained=[c for c in macro if PIVOT not in c and -PIVOT not in c]
    retained_raw=set(retained)
    retained_units=base.state_units(tuple(retained_raw))
    total_pairs=len(pos)*len(neg)
    taut=0
    non_taut=0
    width_sum_units=0
    uniq=set()
    width_hist=Counter()
    duplicate_non_taut=0
    for p in pos:
        for n in neg:
            r=base.resolve_on_var(p,n,PIVOT)
            if r is None:
                taut+=1
                continue
            non_taut+=1
            width_hist[len(r)]+=1
            width_sum_units += 1+len(r)
            if r in retained_raw or r in uniq:
                duplicate_non_taut+=1
            else:
                uniq.add(r)
    unique_units=sum(1+len(r) for r in uniq)
    exact_full_raw=retained_units+unique_units
    live_macro=len(base.vars_of(macro))
    max_res_width=live_macro-1
    B_conflict=base.state_units(macro)+(1+max_res_width)*(total_pairs-taut)
    B_width=base.state_units(macro)+width_sum_units
    B_unique_loose=base.state_units(macro)+unique_units
    out_exact,stats=base.eliminate_var_capped(macro,PIVOT,st.state_cap)
    assert out_exact is not None
    assert base.verify_elimination_transition(macro,PIVOT,out_exact,st.state_cap)
    out={
      'schema':'JANUS/C025/M80-RESOLVENT-MECHANISM/v1',
      'N':st.N,'cap':st.state_cap,'product_units':base.state_units(product),'macro_units':base.state_units(macro),
      'pair':list(PAIR),'replaced_occurrences':cert['replaced_occurrences'],'pivot':PIVOT,
      'parent_counts':{'positive':len(pos),'negative':len(neg),'pairs':total_pairs},
      'tautologies':taut,'tautology_fraction':taut/total_pairs,
      'non_taut_parent_pairs':non_taut,'duplicate_or_retained_collisions':duplicate_non_taut,
      'unique_new_resolvents':len(uniq),'width_histogram':dict(sorted(width_hist.items())),
      'bounds':{
        'B_conflict_max_width':B_conflict,
        'B_width_no_dedupe':B_width,
        'B_unique_using_macro_as_retained_upper':B_unique_loose,
        'exact_retained_units':retained_units,
        'exact_unique_new_units':unique_units,
        'exact_full_raw_reconstructed':exact_full_raw,
        'exact_engine_raw_units':stats['raw_units']
      },
      'first_sufficient_layer': next((name for name,val in [('CONFLICT_MAX_WIDTH',B_conflict),('WIDTH_NO_DEDUPE',B_width),('UNIQUE_COLLISION_AWARE',B_unique_loose),('EXACT_RETAINED_PLUS_UNIQUE',exact_full_raw)] if val<=st.state_cap),None),
      'P_VS_NP':'OPEN'
    }
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
