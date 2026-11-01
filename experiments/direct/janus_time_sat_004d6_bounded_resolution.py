#!/usr/bin/env python3
"""TIME-SAT-004D6: budgeted source-entailed XOR via exact resolution DAGs.

Research only: add bounded classical resolvents of source CNF clauses,
never replace or delete any source clause. An XOR is reported only when
a full sign-mask class is derivable. Separate verifier replays every
claimed step from the original clauses. No SAT solver, UNSAT certificate,
general complexity claim, speed comparison, or production modification.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json

from janus_time_sat_004d1_xor import (
    MAX_N, MAX_ROWS, MAX_LITERALS, source_digest
)
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor

PARENT_WIDTH=4
DERIVED_WIDTH=4
MAX_PIVOTS_PER_ROUND=128
MAX_SIDE_PARENTS=8
MAX_PAIRS=64
MAX_ADDED=2000
MAX_ROUNDS=2
MAX_EXAMPLES=8


def canonical(row):
    """Only an equivalent canonical clause may become a resolution premise."""
    if any(type(l) is not int or l == 0 for l in row):
        raise ValueError("non-integer or zero literal")
    s=set(row)
    if any(-v in s for v in s):
        return None  # tautological source clause: never used as antecedent
    return tuple(sorted(s,key=lambda l:(abs(l),l<0)))


def exact_resolvent(left,right,pivot):
    """Sound positive/negative resolution. None for invalid/tautological."""
    if type(pivot) is not int or pivot<=0:
        return None
    if pivot not in left or -pivot not in right:
        return None
    tail=set(left)
    tail.remove(pivot)
    other=set(right)
    other.remove(-pivot)
    result=tail|other
    if any(-v in result for v in result):
        return None
    if not 1 <= len(result) <= DERIVED_WIDTH:
        return None
    return tuple(sorted(result,key=lambda l:(abs(l),l<0)))


def source_derived_xor(rows,n):
    if type(n) is not int or not 1<=n<=MAX_N:
        return {"status":"ABSTAIN_INVALID_N"}
    if len(rows)>MAX_ROWS:
        return {"status":"ABSTAIN_ROW_BUDGET"}
    lit_total=0
    canonical_rows=[]
    for row in rows:
        lit_total+=len(row)
        if lit_total>MAX_LITERALS:
            return {"status":"ABSTAIN_LITERAL_BUDGET"}
        if any(type(l) is not int or not 1<=abs(l)<=n for l in row):
            return {"status":"ABSTAIN_INVALID_LITERAL"}
        canonical_rows.append(canonical(row))

    baseline=extract_paged_mixed_xor(rows,n)
    if baseline["status"]!="SOURCE_PARTITION_VERIFIED":
        return {"status":"ABSTAIN_004D4D_SOURCE_GUARD"}
    baseline_keys={
        (tuple(eq["variables"]),eq["rhs"]) for eq in baseline["equations"]
        if len(eq["variables"])<=DERIVED_WIDTH
    }

    count_source=len(rows)
    clauses={}          # exact source or derived clause by its ID
    by_clause={}        # deduplicate canonical clauses, preserving first source ID
    for i,can in enumerate(canonical_rows):
        if can is not None and 1<=len(can)<=PARENT_WIDTH:
            clauses[i]=can
            by_clause.setdefault(can,i)
    proof=[]
    stats=[]
    max_limit_reached=False
    for round_number in range(1,MAX_ROUNDS+1):
        positive=defaultdict(list)
        negative=defaultdict(list)
        for id_,clause in clauses.items():
            for lit in clause:
                (positive if lit>0 else negative)[abs(lit)].append(id_)
        eligible=[
            v for v in sorted(set(positive)&set(negative))
            if 1<=len(positive[v])<=MAX_SIDE_PARENTS
            and 1<=len(negative[v])<=MAX_SIDE_PARENTS
            and len(positive[v])*len(negative[v])<=MAX_PAIRS
            and any(len(clauses[idx])>=3 for idx in positive[v]+negative[v])
        ]
        examined=eligible[:MAX_PIVOTS_PER_ROUND]
        added_this_round=0
        skipped_taut_or_width=0
        for pivot in examined:
            for a in positive[pivot]:
                for b in negative[pivot]:
                    resolvent=exact_resolvent(clauses[a],clauses[b],pivot)
                    if resolvent is None:
                        skipped_taut_or_width+=1
                        continue
                    if resolvent in by_clause:
                        continue
                    if len(proof)>=MAX_ADDED:
                        max_limit_reached=True
                        break
                    new_id=count_source+len(proof)
                    proof.append({"id":new_id,"parents":[a,b],
                                  "pivot":pivot,"clause":list(resolvent)})
                    clauses[new_id]=resolvent
                    by_clause[resolvent]=new_id
                    added_this_round+=1
                if max_limit_reached:break
            if max_limit_reached:break
        stats.append({
            "round":round_number,
            "eligible_pivots":len(eligible),
            "examined_pivots":len(examined),
            "skipped_eligible_pivots":max(0,len(eligible)-len(examined)),
            "new_resolvents":added_this_round,
            "skipped_tautology_empty_or_width_pairs":skipped_taut_or_width,
        })
        if max_limit_reached or added_this_round==0:break

    # A parity block can combine original and independently proved clauses.
    groups=defaultdict(lambda:defaultdict(list))
    for id_,clause in clauses.items():
        if not 1<=len(clause)<=DERIVED_WIDTH:continue
        support=tuple(sorted(abs(v) for v in clause))
        if len(set(support))!=len(support):continue
        mask=sum(1<<i for i,v in enumerate(support) if -v in clause)
        groups[support][mask].append(id_)

    seen={}
    for support,masks in sorted(groups.items()):
        for p in (0,1):
            wants=[m for m in range(1<<len(support))
                   if m.bit_count()%2==p]
            if not all(m in masks for m in wants):continue
            key=(support,1^p)
            if key in baseline_keys:continue
            chosen=[min(masks[m]) for m in wants]
            if not any(x>=count_source for x in chosen):continue
            seen[key]=chosen
    witnesses=[
        {"variables":list(k[0]),"rhs":k[1],
         "clause_ids":v,"certificate":"SOURCE_EXACT_RESOLUTION_DAG_AND_FULL_MASKS"}
        for k,v in list(sorted(seen.items()))[:MAX_EXAMPLES]
    ]
    return {
        "schema":"JANUS-TIME-SAT-004D6-BOUNDED-RESOLUTION-SOURCE-ONLY-V1",
        "status":"SOURCE_RESOLUTION_BOUNDED_PASS",
        "source_n":n,"source_clauses":count_source,
        "source_logical_sha256":source_digest(rows,n),
        "original_clause_count_retained":count_source,
        "original_explicit_xor_equations":len(baseline["equations"]),
        "baseline_explicit_width_le_4_keys":len(baseline_keys),
        "round_stats":stats,
        "parent_width_cap":PARENT_WIDTH,"derived_width_cap":DERIVED_WIDTH,
        "max_side_parents":MAX_SIDE_PARENTS,"max_pairs_per_pivot":MAX_PAIRS,
        "max_pivots_per_round":MAX_PIVOTS_PER_ROUND,"max_rounds":MAX_ROUNDS,
        "max_new_resolvents":MAX_ADDED,
        "truncated_by_total_resolvent_cap":max_limit_reached,
        "total_new_resolvents":len(proof),
        "new_complete_xor_sign_mask_equations":len(seen),
        "new_witness_examples":witnesses,
        "resolution_proof_DAG":proof,
        "not_a_complete_search_of_all_resolution":"TRUE",
        "no_SAT_UNSAT_solver_invocations":True,
        "no_general_speedup_claim":True,
        "outside_admin_witness":"OPEN",
        "production_C023":"UNCHANGED"
    }
