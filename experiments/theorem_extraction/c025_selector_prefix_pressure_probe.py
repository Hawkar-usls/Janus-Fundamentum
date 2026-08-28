#!/usr/bin/env python3
"""Direct certified-prefix pressure probe for root-phase L1.

It reproduces the v0.4 root terminal portfolio only until the first ordinary
elimination.  If every earlier exact lane declines and frozen canonical
elimination selects selector 1, exact replay certifies the resulting product
state as reachable.  The probe then checks every pivot and, only if all overflow,
runs frozen v2 on that state.  No suffix decision is needed for this question.
"""
from __future__ import annotations

import argparse
import json

from experiments.direct import janus_matching_hall_escape as hall
from experiments.direct import janus_one_variable_separator_escape as sep
from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_theorem_input_normal_form as input_nf
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_root_pivot_grammar_falsifier as common


def make_state(root: base.CNF) -> base.EngineState:
    return base.EngineState(root=root, residual=root, fixed_assignment={},
        root_vars=base.vars_of(root), extension_defs=[], elimination_history=[],
        seen=set(), N=base.input_size_units(root), cap_exponent=2,
        extension_exponent=2, ledger=base.Ledger())


def portfolio_declines(root: base.CNF) -> dict:
    reduced, implied, ok, _ = base.unit_propagate(root)
    if implied or not ok or reduced != root: return {"declines": False, "lane": "UNIT"}
    h=hall.solve_matching_hall_escape(root)
    if h.get("status") in {"SAT","UNSAT"}: return {"declines": False,"lane":"HALL","status":h["status"]}
    s=sep.solve_one_variable_escape(root)
    if s.get("status") in {"SAT","UNSAT"}: return {"declines": False,"lane":"SEPARATOR","status":s["status"]}
    if base.solve_2sat_exact(root) is not None: return {"declines":False,"lane":"2SAT"}
    if base.solve_gf2_explicit_exact(root) is not None: return {"declines":False,"lane":"GF2"}
    refuted,cert=base.bounded_width_resolution_refutes(root,3)
    if refuted: return {"declines":False,"lane":"WIDTH3","certificate":cert}
    return {"declines":True,"lane":None}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--leaf-clauses',type=int,required=True); ap.add_argument('--seed',type=int,default=32100)
    a=ap.parse_args(); m=a.leaf_clauses
    source=common.selector_product_case(8,m,4,a.seed+m)
    normal=input_nf.dense_normalize(source); root=normal.normalized
    prefix=portfolio_declines(root)
    out={"schema":"JANUS/C025/SELECTOR-PREFIX-PRESSURE/v1","leaf_clauses":m,
         "source_fingerprint":base.fingerprint(root),"prefix_portfolio":prefix,
         "N":base.input_size_units(root),"state_cap":base.input_size_units(root)**2,
         "certified_reachable_product":False,"P_VS_NP":"OPEN"}
    if not prefix['declines']:
        out['status']='PREFIX_INTERCEPTED'; print(json.dumps(out,indent=2,sort_keys=True)); return 0
    st=make_state(root); first=base.first_capped_elimination(st)
    if first is None:
        out['status']='ROOT_NO_ORDINARY_MOVE'; print(json.dumps(out,indent=2,sort_keys=True)); return 0
    pivot,product,stats=first; out['first_pivot']=pivot; out['selector_stats']=stats
    if pivot!=1 or not base.verify_elimination_transition(root,1,product,st.state_cap):
        out['status']='SELECTOR_PREFIX_NOT_CERTIFIED'; print(json.dumps(out,indent=2,sort_keys=True)); return 0
    out['certified_reachable_product']=True; out['product_fingerprint']=base.fingerprint(product); out['product_state_units']=base.state_units(product)
    rows=[]
    for v in base.vars_of(product):
        nxt,ss=base.eliminate_var_capped(product,v,st.state_cap)
        rows.append({"pivot":v,"status":"FIT" if nxt is not None else "OVERFLOW","raw_units":ss.get('raw_units'),"pairs":ss.get('pairs'),"tautologies":ss.get('tautologies'),"canonical_units":ss.get('canonical_units')})
    fits=sum(r['status']=='FIT' for r in rows); out['pivot_rows']=rows; out['ordinary_fit_count']=fits; out['all_ordinary_overflow']=fits==0
    P,tmax,pair=common.pair_stats(product); s=base.state_units(product); n=len(base.vars_of(product)); req=s-2*st.N+11; preq=2*n*(n-1)*req
    out['pair_pressure']={"P":P,"tmax":tmax,"pair":pair,"frequent_required":req,"density_required":preq,"L1A":tmax>=req,"L1B":P>=preq}
    out['v2_rescue_exists']=None
    if fits==0:
        gs=make_state(root); gs.residual=product; gs.elimination_history.append(base.ElimSnapshot(root,1,'PURE_ELIM'))
        rr=core.v2.discover_macro_restore_v2(gs); out['v2_rescue_exists']=rr is not None
        if rr is not None:
            macro,pv,after,cert,es=rr; out['v2_rescue']={"pair":cert.get('represents'),"reused":cert.get('reused_occurrences'),"root_pivot":pv,"macro_units":base.state_units(macro),"after_units":base.state_units(after),"elim_raw":es.get('raw_units')}
    out['candidate_status']={"L1":"REFUTED" if fits==0 and out['v2_rescue_exists'] is False else "NOT_REFUTED__NOT_PROVED","L1A":"REFUTED" if fits==0 and not out['pair_pressure']['L1A'] else "NOT_REFUTED__NOT_PROVED","L1B":"REFUTED" if fits==0 and not out['pair_pressure']['L1B'] else "NOT_REFUTED__NOT_PROVED"}
    out['status']='MEASURED'; print(json.dumps(out,indent=2,sort_keys=True)); return 0

if __name__=='__main__': raise SystemExit(main())
