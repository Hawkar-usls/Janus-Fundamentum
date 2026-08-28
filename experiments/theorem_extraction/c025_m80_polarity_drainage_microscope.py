#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_root_pivot_grammar_falsifier as common

M=80
SEED=32100+M


def signed_counts(cnf: base.CNF) -> Counter[int]:
    c=Counter()
    for clause in cnf:
        c.update(clause)
    return c


def pair_counts(cnf: base.CNF) -> Counter[tuple[int,int]]:
    c=Counter()
    for clause in cnf:
        for i in range(len(clause)):
            for j in range(i+1,len(clause)):
                a,b=clause[i],clause[j]
                if abs(a)==abs(b):
                    continue
                pair=tuple(sorted((a,b),key=lambda z:(abs(z),z<0)))
                c[pair]+=1
    return c


def make_state(root: base.CNF) -> base.EngineState:
    return base.EngineState(root=root,residual=root,fixed_assignment={},root_vars=base.vars_of(root),extension_defs=[],elimination_history=[],seen=set(),N=base.input_size_units(root),cap_exponent=2,extension_exponent=2,ledger=base.Ledger())


def main():
    source=common.selector_product_case(8,M,4,SEED)
    st=make_state(source)
    first=base.first_capped_elimination(st)
    assert first is not None
    pivot,product,stats=first
    assert pivot==1
    assert base.verify_elimination_transition(source,1,product,st.state_cap)
    s=base.state_units(product); n=len(base.vars_of(product)); cap=st.state_cap
    lc=signed_counts(product); pc=pair_counts(product)
    rows=[]
    for pair,t in pc.items():
        for a,b in (pair,(pair[1],pair[0])):
            x=abs(a)
            if x not in st.root_vars or x not in base.vars_of(product):
                continue
            cs=lc[a]; co=lc[-a]
            B=s-t+10+(n+1)*(cs-t+1)*(co+1)
            rows.append({"pair":list(pair),"drained_literal":a,"root_pivot":x,"t":t,"c_sigma":cs,"c_opp":co,"B_drain":B,"fits":B<=cap})
    rows.sort(key=lambda r:(r['B_drain'],tuple((abs(z),z<0) for z in r['pair']),abs(r['drained_literal']),r['drained_literal']<0))
    qualifying=[r for r in rows if r['fits']]
    # frozen v2 actual chosen candidate
    gs=make_state(source); gs.residual=product; gs.elimination_history.append(base.ElimSnapshot(source,1,'PURE_ELIM'))
    rr=v2.discover_macro_restore_v2(gs)
    actual=None
    if rr is not None:
        macro,pv,after,cert,es=rr
        actual={"pair":cert['represents'],"replaced_occurrences":cert['replaced_occurrences'],"root_pivot":pv,"macro_units":base.state_units(macro),"elim_raw_units":es['raw_units'],"after_units":base.state_units(after)}
        ap=tuple(cert['represents'])
        actual_candidates=[r for r in rows if tuple(r['pair'])==ap and r['root_pivot']==pv]
        actual['drainage_rows_for_actual_pair_and_pivot']=actual_candidates
    out={"schema":"JANUS/C025/M80-POLARITY-DRAINAGE-MICROSCOPE/v1","N":st.N,"cap":cap,"product_units":s,"live_variables":n,"product_fingerprint":base.fingerprint(product),"qualifying_drainage_count":len(qualifying),"best_drainage":rows[:20],"first_qualifying_canonical":None,"actual_v2":actual,"L1C_on_M80":"SUPPORTED_BY_EXPLICIT_DRAINABLE_PAIR" if qualifying else "REFUTED_ON_M80","P_VS_NP":"OPEN"}
    # canonical v2 pair order, among pairs for which either literal gives a proved-drain route
    qkeys={(tuple(r['pair'])) for r in qualifying}
    for p in v2.all_or_pair_candidates(product):
        if tuple(p) in qkeys:
            out['first_qualifying_canonical']=list(p); break
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
