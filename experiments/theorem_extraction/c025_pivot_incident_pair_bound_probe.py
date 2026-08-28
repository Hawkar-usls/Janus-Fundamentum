#!/usr/bin/env python3
"""Exact algebra probe for a pivot-incident B2 rescue bound.

For a root pivot x and a v2 literal pair (a,b) with |a|=x, let T be the t
clauses containing both literals and W their total width.  If a=x, write p,q
for positive/negative x-clause counts and Lp,Lq for their literal sums, while
r,Ln describe x-neutral clauses.  Before beneficial canonical cleanup, the B2
macro transforms the relevant bucket bounds as

  p' <= p-t+1,       Lp' <= Lp-W+3
  q' <= q+1,         Lq' <= Lq+2
  r' <= r+t+1,       Ln' <= Ln+(W-t)+2.

The generic exact-elimination counting lemma then gives

  U_after <= 1+r'+Ln' + q' Lp' + p' Lq' - p'q'.

For a=-x the positive and negative roles swap.  This file verifies the formula
against the frozen reachable monster and asks whether it already certifies the
first frozen-v2 rescue pair [2,3].  It is a lemma-development probe, not itself
a proof record.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP = "OPEN"
SOURCE_FP = "69e4c811b0e34534c09beb27b75578ba3bfb6625c27aaeea1f8838f44d6281c4"
PRODUCT_FP = "e10600e0f79ad6f143f3b67b04d4b616da5f59e4a4832af5cbb329a574f0dac7"


def bucket_stats(cnf: base.CNF, x: int) -> dict:
    pos=[c for c in cnf if x in c]
    neg=[c for c in cnf if -x in c]
    neutral=[c for c in cnf if x not in c and -x not in c]
    return {
        "p":len(pos), "q":len(neg), "r":len(neutral),
        "Lp":sum(len(c) for c in pos),
        "Lq":sum(len(c) for c in neg),
        "Ln":sum(len(c) for c in neutral),
    }


def incident_bound(cnf: base.CNF, pair: tuple[int,int], x: int) -> dict:
    if x not in (abs(pair[0]),abs(pair[1])):
        raise ValueError("pair is not incident to pivot")
    a = next(l for l in pair if abs(l)==x)
    b = pair[1] if pair[0]==a else pair[0]
    T=[c for c in cnf if a in c and b in c]
    t=len(T); W=sum(len(c) for c in T)
    s=bucket_stats(cnf,x)
    if a==x:
        pp=s['p']-t+1; qq=s['q']+1
        LLp=s['Lp']-W+3; LLq=s['Lq']+2
    else:
        pp=s['p']+1; qq=s['q']-t+1
        LLp=s['Lp']+2; LLq=s['Lq']-W+3
    rr=s['r']+t+1
    LLn=s['Ln']+(W-t)+2
    bound=1+rr+LLn + qq*LLp + pp*LLq - pp*qq
    return {
        **s,
        "signed_pivot_literal":a,
        "other_literal":b,
        "t":t,
        "W":W,
        "p_prime_bound":pp,
        "q_prime_bound":qq,
        "Lp_prime_bound":LLp,
        "Lq_prime_bound":LLq,
        "r_prime_bound":rr,
        "Ln_prime_bound":LLn,
        "raw_elimination_upper_bound":bound,
    }


def main() -> int:
    source,left,right=adv.build_selector_source(8,72,4,29100)
    product=adv.direct_selector_product(left,right)
    assert base.fingerprint(source)==SOURCE_FP
    assert base.fingerprint(product)==PRODUCT_FP
    N=base.input_size_units(source); cap=N*N

    state=base.EngineState(
        root=source,residual=product,fixed_assignment={},root_vars=base.vars_of(source),
        extension_defs=[],elimination_history=[],seen=set(),N=N,cap_exponent=2,
        extension_exponent=2,ledger=base.Ledger())

    pairs=core.v2.all_or_pair_candidates(product)
    rows=[]
    exact_rescues=[]
    bound_certified=[]
    # Analyze every pivot-incident pair algebraically.  Exact replay is done only
    # when the algebraic upper bound itself falls under cap, keeping this probe
    # theorem-safe and finite without pretending the scan proves totality.
    for pair in pairs:
        incident_roots=sorted(set(abs(l) for l in pair if abs(l) in set(state.root_vars)))
        for x in incident_roots:
            b=incident_bound(product,pair,x)
            row={"pair":list(pair),"pivot":x,**b,"cap":cap,
                 "bound_fits":b['raw_elimination_upper_bound']<=cap}
            rows.append(row)
            if not row['bound_fits']:
                continue
            fresh=core.v2.next_fresh_extension(state)
            macro,cert=core.v2.apply_or_pair_v2(product,pair[0],pair[1],fresh)
            assert core.v2.verify_or_pair_v2(product,macro,cert)
            out,stats=base.eliminate_var_capped(macro,x,cap)
            exact_ok=out is not None and base.verify_elimination_transition(macro,x,out,cap)
            row['exact_replay_fits']=exact_ok
            row['exact_raw_units']=int(stats['raw_units'])
            row['exact_canonical_units']=int(stats.get('canonical_units',0)) if out is not None else None
            if exact_ok:
                exact_rescues.append({"pair":list(pair),"pivot":x,"raw_units":int(stats['raw_units']),
                                      "canonical_units":int(stats['canonical_units']),
                                      "bound":b['raw_elimination_upper_bound']})
            bound_certified.append(row)

    target=incident_bound(product,(2,3),2)
    macro,cert=core.v2.apply_or_pair_v2(product,2,3,18)
    assert core.v2.verify_or_pair_v2(product,macro,cert)
    out,stats=base.eliminate_var_capped(macro,2,cap)
    assert out is not None
    target_report={
        "pair":[2,3],"pivot":2,**target,
        "cap":cap,
        "bound_fits":target['raw_elimination_upper_bound']<=cap,
        "actual_macro_units":base.state_units(macro),
        "actual_raw_units":int(stats['raw_units']),
        "actual_canonical_units":int(stats['canonical_units']),
        "bound_slack_over_actual":target['raw_elimination_upper_bound']-int(stats['raw_units']),
    }

    report={
        "schema":"JANUS/C025/PIVOT-INCIDENT-PAIR-BOUND-PROBE/v1",
        "status":"TARGET_BOUND_CERTIFIES_RESCUE" if target_report['bound_fits'] else "TARGET_BOUND_TOO_COARSE",
        "source_fingerprint":SOURCE_FP,
        "product_fingerprint":PRODUCT_FP,
        "N":N,"cap":cap,
        "target":target_report,
        "pivot_incident_cases":len(rows),
        "bound_certified_cases":len(bound_certified),
        "exact_rescues_among_bound_certified":len(exact_rescues),
        "first_exact_rescues":exact_rescues[:20],
        "scientific_boundary":{
            "algebraic_formula_uses_only_syntactic_bucket_counts":True,
            "canonical_cleanup_can_only_improve_bound":True,
            "probe_is_not_universal_proof":True,
            "L1":"OPEN",
            "P2_REACHABLE_PRESERVATION":"OPEN",
            "P_VS_NP":P_VS_NP
        }
    }
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
