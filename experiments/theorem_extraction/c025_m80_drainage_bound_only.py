#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_root_pivot_grammar_falsifier as common

M=80
SEED=32100+M
EXPECTED_FP='2e92d85f5c02976a9a5d6036dbc83d31f88236e6455c7e27f5f9224e8c02708e'

def state(root):
    return base.EngineState(root=root,residual=root,fixed_assignment={},root_vars=base.vars_of(root),extension_defs=[],elimination_history=[],seen=set(),N=base.input_size_units(root),cap_exponent=2,extension_exponent=2,ledger=base.Ledger())

def main():
    root=common.selector_product_case(8,M,4,SEED)
    st=state(root)
    first=base.first_capped_elimination(st); assert first is not None
    pivot,product,stats=first; assert pivot==1
    assert base.verify_elimination_transition(root,1,product,st.state_cap)
    assert base.fingerprint(product)==EXPECTED_FP
    lit=Counter(); pairs=Counter()
    for c in product:
        lit.update(c)
        for i in range(len(c)):
            for j in range(i+1,len(c)):
                a,b=c[i],c[j]
                if abs(a)==abs(b): continue
                p=tuple(sorted((a,b),key=lambda z:(abs(z),z<0)))
                pairs[p]+=1
    s=base.state_units(product); n=len(base.vars_of(product)); cap=st.state_cap
    rows=[]
    for pair,t in pairs.items():
        for a in pair:
            if abs(a) not in st.root_vars: continue
            cs=lit[a]; co=lit[-a]
            B=s-t+10+(n+1)*(cs-t+1)*(co+1)
            rows.append({'pair':list(pair),'drained_literal':a,'pivot':abs(a),'t':t,'c_sigma':cs,'c_opp':co,'B_drain':B,'fits':B<=cap})
    rows.sort(key=lambda r:(r['B_drain'],tuple((abs(z),z<0) for z in r['pair']),abs(r['drained_literal']),r['drained_literal']<0))
    q=[r for r in rows if r['fits']]
    actual=[r for r in rows if r['pair']==[2,4] and r['pivot']==2]
    out={'schema':'JANUS/C025/M80-DRAINAGE-BOUND-ONLY/v1','N':st.N,'cap':cap,'product_units':s,'product_fingerprint':EXPECTED_FP,'tested_signed_pair_pivot_routes':len(rows),'qualifying_count':len(q),'best':rows[:20],'actual_v2_pair_2_4_pivot_2_rows':actual,'L1C_M80':'NOT_REFUTED__SUPPORTED' if q else 'REFUTED_BY_M80','scientific_boundary':{'actual_v2_rescue_is_taken_only_from_frozen_exact_M80_certificate':True,'this_script_only_tests_the_symbolic_sufficient_bound':True,'absence_of_drainage_bound_does_not_refute_L1':True,'P_VS_NP':'OPEN'}}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
