#!/usr/bin/env python3
"""Direct adversarial attack on L1 root-phase grammar totality.

Unlike the previous Delta/pair search, this search explicitly screens the entire
frozen v2 OR-pair grammar in canonical order on a selector-product reachable
candidate.  The score is not SAT hardness.  It is resistance to v2 rescue after
ordinary all-pivot overflow.

For search speed on the uniform selector-product residual we use a specialized
macro canonicalizer.  Its equivalence to ORIGINAL v2.apply_or_pair_v2 is checked
on frozen samples before any score is trusted.  Search-only screening has zero
theorem authority.  If a candidate survives every fast v2 pair, the unmodified
frozen v0.4/v2 implementation must replay the exact source and return None before
L1 can be refuted.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP = "OPEN"


def fast_apply_uniform_product(cnf: base.CNF, a: int, b: int, e: int) -> base.CNF:
    widths={len(c) for c in cnf}
    if len(widths)!=1:
        raise ValueError("uniform product required")
    replaced=[]; untouched=[]
    for clause in cnf:
        if a in clause and b in clause:
            rest=[lit for lit in clause if lit not in (a,b)]
            cc=base.canon_clause([-e,*rest])
            if cc is not None:
                replaced.append(cc)
        else:
            untouched.append(clause)
    if not replaced:
        raise ValueError("pair absent")
    defs=[base.canon_clause((-e,-a)),base.canon_clause((-e,-b)),base.canon_clause((e,a,b))]
    rows=set(untouched)
    rows.update(replaced)
    rows.update(c for c in defs if c is not None)
    # Exact on this family: e is fresh. Definition clauses cannot subsume an
    # untouched clause (no e), nor a replaced clause containing -e because the
    # latter cannot contain -a/-b after starting from a tautology-free clause
    # that contained a,b. Different nondefinition widths cannot cross-subsume.
    return tuple(sorted(rows,key=lambda c:(len(c),c)))


def equivalence_gate(product: base.CNF, pairs: list[tuple[int,int]], fresh: int) -> None:
    indices=sorted(set([0,1,min(10,len(pairs)-1),len(pairs)//2,len(pairs)-1]))
    for i in indices:
        pair=pairs[i]
        fast=fast_apply_uniform_product(product,pair[0],pair[1],fresh)
        original,cert=core.v2.apply_or_pair_v2(product,pair[0],pair[1],fresh)
        if fast!=original:
            raise AssertionError(f"FAST_MACRO_EQUIVALENCE_FAILED_AT_{i}_{pair}")
        if not core.v2.verify_or_pair_v2(product,original,cert):
            raise AssertionError("ORIGINAL_V2_REPLAY_FAILED_IN_EQUIVALENCE_GATE")


def ordinary_pressure(product: base.CNF, cap: int) -> dict:
    rows=[adv.raw_units_probe(product,v,cap) for v in base.vars_of(product)]
    return {
        "all_overflow":all(r['overflow'] for r in rows),
        "overflow_count":sum(bool(r['overflow']) for r in rows),
        "pivot_count":len(rows),
        "Delta_strict_lower_bound_if_all_overflow":min((int(r.get('delta_lower_bound',0)) for r in rows),default=0),
        "rows":rows,
    }


def fast_v2_first_rescue(source: base.CNF, product: base.CNF, cap: int) -> dict:
    roots=[v for v in base.vars_of(source) if v in set(base.vars_of(product))]
    pairs=core.v2.all_or_pair_candidates(product)
    fresh=max(base.vars_of(source))+1
    equivalence_gate(product,pairs,fresh)
    tested_pairs=0
    tested_root_probes=0
    closest_overflow=None
    for pair_index,pair in enumerate(pairs):
        tested_pairs+=1
        macro=fast_apply_uniform_product(product,pair[0],pair[1],fresh)
        macro_units=base.state_units(macro)
        if macro_units>cap:
            continue
        for x in roots:
            tested_root_probes+=1
            probe=adv.raw_units_probe(macro,x,cap)
            if not probe['overflow']:
                return {
                    "rescue_exists":True,
                    "pair_index_zero_based":pair_index,
                    "pair":list(pair),
                    "pivot":x,
                    "macro_units":macro_units,
                    "raw_units":int(probe['raw_units_observed']),
                    "cap_margin":int(probe['raw_units_observed'])-cap,
                    "pairs_tested_through_rescue":tested_pairs,
                    "root_probes":tested_root_probes,
                    "candidate_pair_count":len(pairs),
                    "closest_overflow":closest_overflow,
                }
            margin=int(probe['raw_units_observed'])-cap
            if closest_overflow is None or margin<closest_overflow['first_crossing_margin']:
                closest_overflow={"pair":list(pair),"pivot":x,"first_crossing_margin":margin}
    return {
        "rescue_exists":False,
        "pairs_tested_through_rescue":tested_pairs,
        "root_probes":tested_root_probes,
        "candidate_pair_count":len(pairs),
        "closest_overflow":closest_overflow,
    }


def exact_original_reachability(source: base.CNF, product: base.CNF) -> dict:
    return adv.verify_reachable_callsite(source,product)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--leaf-nvars',type=int,default=10)
    parser.add_argument('--leaf-clauses',type=int,default=90)
    parser.add_argument('--leaf-width',type=int,default=4)
    parser.add_argument('--seed',type=int,default=39100)
    args=parser.parse_args()

    source,left,right=adv.build_selector_source(args.leaf_nvars,args.leaf_clauses,args.leaf_width,args.seed)
    product=adv.direct_selector_product(left,right)
    N=base.input_size_units(source); cap=N*N
    ordinary=ordinary_pressure(product,cap)
    screen=None
    if ordinary['all_overflow']:
        screen=fast_v2_first_rescue(source,product,cap)
    reachability=exact_original_reachability(source,product)

    status='ORDINARY_NOT_ALL_OVERFLOW'
    if ordinary['all_overflow'] and screen and screen['rescue_exists']:
        status='FAST_EXACT_EQUIVALENT_SCREEN_FINDS_V2_RESCUE__L1_NOT_ATTACKED_TO_COMPLETION'
    elif ordinary['all_overflow'] and screen and not screen['rescue_exists']:
        status='FAST_SCREEN_V2_NONE_CANDIDATE__ORIGINAL_FULL_V2_REPLAY_REQUIRED'

    report={
        "schema":"JANUS/C025/V2-GAP-ADVERSARIAL-SEARCH/v1",
        "status":status,
        "source_meta":{
            "family":"DISJOINT_SELECTOR_PRODUCT",
            "leaf_nvars":args.leaf_nvars,"leaf_clauses":args.leaf_clauses,
            "leaf_width":args.leaf_width,"seed":args.seed,
            "source_fingerprint":base.fingerprint(source),
            "product_fingerprint":base.fingerprint(product),
            "N":N,"state_cap":cap,"product_state_units":base.state_units(product),
        },
        "ordinary_pressure":ordinary,
        "fast_v2_screen":screen,
        "original_reachability_replay":reachability,
        "candidate_results":{
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY":"OPEN__NOT_REFUTED_UNLESS_ORIGINAL_FULL_V2_RETURNS_NONE_ON_REACHABLE_CANDIDATE",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR":"REFUTED_PREVIOUSLY",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY":"REFUTED_PREVIOUSLY"
        },
        "next_gate":(
            "RUN_UNMODIFIED_FULL_V2_ON_THIS_EXACT_REACHABLE_CANDIDATE"
            if ordinary['all_overflow'] and screen and not screen['rescue_exists'] and reachability['reachable_at_frozen_ordinary_callsite']
            else "EVOLVE_SELECTOR_PRODUCT_TO_DELAY_OR_REMOVE_FIRST_V2_RESCUE"
        ),
        "scientific_boundary":{
            "fast_macro_equivalence_sampled_against_original_before_search":True,
            "fast_screen_has_theorem_authority":False,
            "original_reachability_required":True,
            "original_full_v2_none_required_to_refute_L1":True,
            "finite_rescue_does_not_prove_L1":True,
            "P2_REACHABLE_PRESERVATION":"OPEN",
            "P_VS_NP":P_VS_NP
        }
    }
    # Keep report manageable: pivot rows are useful but bulky.
    report['ordinary_pressure']['rows']=ordinary['rows']
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
