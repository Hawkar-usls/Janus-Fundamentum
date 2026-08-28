#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

P_VS_NP = "OPEN"


def load_many(root: Path, pattern: str):
    out=[]; errors=[]
    for p in sorted(root.rglob(pattern)):
        try:
            out.append(json.loads(p.read_text()))
        except Exception as exc:
            errors.append({"file":str(p),"error":f"{type(exc).__name__}: {exc}"})
    return out, errors


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-dir',required=True)
    ap.add_argument('--ordinary-shards',type=int,required=True)
    ap.add_argument('--v2-shards',type=int,required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    root=Path(args.input_dir)

    reach, er = load_many(root,'reachability.json')
    ordinary, eo = load_many(root,'ordinary-*.json')
    v2, ev = load_many(root,'v2-*.json')

    reach_ok = len(reach)==1 and reach[0].get('status')=='PASS' and reach[0].get('reachable_at_frozen_ordinary_callsite') is True and reach[0].get('selector_pivot_1_exact_product') is True

    candidate_rows = [*reach, *ordinary, *v2]
    fps={(r.get('candidate',{}).get('source_fingerprint'),r.get('candidate',{}).get('product_fingerprint')) for r in candidate_rows}
    candidate_consistent = len(fps)==1 and bool(candidate_rows)

    ordinary_by={r.get('shard',{}).get('index'):r for r in ordinary if r.get('shard',{}).get('count')==args.ordinary_shards}
    ordinary_missing=[i for i in range(args.ordinary_shards) if i not in ordinary_by]
    ordinary_covered=set(); ordinary_fit=[]
    pivot_count_vals=set()
    for i,r in ordinary_by.items():
        pivot_count_vals.add(int(r.get('global_pivot_count',-1)))
        if r.get('complete_for_selected_indices') is True:
            ordinary_covered.update(int(x) for x in r.get('selected_pivot_indices',[]))
        for row in r.get('rows',[]):
            if row.get('overflow') is False:
                ordinary_fit.append(row)
    pivot_count=next(iter(pivot_count_vals)) if len(pivot_count_vals)==1 else None
    delta_positive = bool(
        candidate_consistent and reach_ok and not ordinary_missing and pivot_count is not None
        and ordinary_covered==set(range(pivot_count)) and not ordinary_fit
        and len(ordinary_by)==args.ordinary_shards
    )

    v2_by={r.get('shard',{}).get('index'):r for r in v2 if r.get('shard',{}).get('count')==args.v2_shards}
    v2_missing=[i for i in range(args.v2_shards) if i not in v2_by]
    rescues=[]; pair_count_vals=set(); v2_covered=set(); v2_incomplete=[]
    for i,r in v2_by.items():
        pair_count_vals.add(int(r.get('global_pair_count',-1)))
        if r.get('rescue') is not None:
            rescues.append(r['rescue'])
        elif r.get('complete_for_selected_indices') is True:
            v2_covered.update(int(x) for x in r.get('selected_pair_indices',[]))
        else:
            v2_incomplete.append(i)
    rescues.sort(key=lambda x:int(x['pair_index']))
    pair_count=next(iter(pair_count_vals)) if len(pair_count_vals)==1 else None
    gamma_positive = bool(
        candidate_consistent and reach_ok and not rescues and not v2_missing and not v2_incomplete
        and pair_count is not None and v2_covered==set(range(pair_count))
        and len(v2_by)==args.v2_shards
    )

    if rescues:
        status='EXACT_V2_RESCUE_FOUND__L1_SURVIVES_THIS_WITNESS'
        l1='SURVIVES_THIS_FROZEN_WITNESS__NOT_PROVED'
        next_gate='FREEZE_FIRST_EXACT_RESCUE_AND_ATTACK_ITS_CONFLICT_COLLISION_STRUCTURE'
    elif delta_positive and gamma_positive:
        status='L1_ROOT_GRAMMAR_COUNTEREXAMPLE_FOUND'
        l1='REFUTED_BY_REACHABLE_WITNESS_WITH_DELTA_POSITIVE_AND_GAMMA_POSITIVE'
        next_gate='FREEZE_L1_COUNTEREXAMPLE_AND_DESIGN_STRICT_SUCCESSOR_GRAMMAR'
    else:
        status='UNKNOWN_INCOMPLETE_OR_UNSATISFIED_SCOPE'
        l1='OPEN__NO_FULL_EXACT_COUNTEREXAMPLE_VERDICT'
        next_gate='COMPLETE_MISSING_SCOPE_OR_INSPECT_NONPOSITIVE_DELTA_GAMMA_COMPONENT'

    candidate = candidate_rows[0].get('candidate') if candidate_rows else None
    report={
      'schema':'JANUS/C025/L1-FANOUT-DELTA-GAMMA-AGGREGATE/v1',
      'status':status,
      'candidate':candidate,
      'reachability':{'pass':reach_ok,'receipt_count':len(reach)},
      'Delta':{
        'positive_exact':delta_positive,
        'pivot_count':pivot_count,
        'covered_indices_count':len(ordinary_covered),
        'missing_shards':ordinary_missing,
        'fitting_pivots':ordinary_fit,
      },
      'Gamma':{
        'positive_exact':gamma_positive,
        'pair_count':pair_count,
        'covered_indices_count':len(v2_covered),
        'missing_shards':v2_missing,
        'incomplete_shards':v2_incomplete,
        'first_exact_rescue':rescues[0] if rescues else None,
      },
      'parse_errors':er+eo+ev,
      'candidate_results':{
        'L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY':l1,
        'L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR':'REFUTED_PREVIOUSLY',
        'L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY':'REFUTED_PREVIOUSLY',
        'L1C_POLARITY_DRAINAGE_TOTALITY':'REFUTED_BY_M80_EXACT_BOUND_NEGATIVE_CERTIFICATE',
      },
      'next_gate':next_gate,
      'scientific_boundary':{
        'delta_uses_original_eliminate_var_capped':True,
        'gamma_uses_original_v2_apply_verify_and_original_root_elimination':True,
        'reachability_required':True,
        'missing_scope_maps_to_UNKNOWN':True,
        'finite_counterexample_can_refute_L1_candidate_only':True,
        'P2_REACHABLE_PRESERVATION':'OPEN',
        'P_VS_NP':P_VS_NP,
      },
      'P_VS_NP':P_VS_NP,
    }
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
