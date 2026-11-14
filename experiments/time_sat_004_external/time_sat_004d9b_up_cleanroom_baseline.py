#!/usr/bin/env python3
"""004D9B clean-room *same-administrator* UP + sign-mask XOR baseline.

Independent implementation with no JANUS module imports. It is a falsifier
for the toy 'new XOR' demonstration; NOT evidence of outside replication.
Only test-set n <= 8 sources are processed, under the exactly frozen original
CNF and no SAT solver dependency. No mutation of source clauses.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import argparse
import json
from pathlib import Path

def simplify_unit_propagation(clauses, n):
    work=[list(c) for c in clauses]
    assigned={}
    while True:
        new=None
        for clause in work:
            remaining=[]
            satisfied=False
            for lit in clause:
                val=assigned.get(abs(lit))
                if val is None:
                    remaining.append(lit)
                elif val==(lit>0):
                    satisfied=True
                    break
            if satisfied:continue
            if not remaining:return {"status":"UNSAT_BY_UNIT_PROPAGATION"}
            if len(remaining)==1:
                lit=remaining[0]
                var=abs(lit)
                if var in assigned and assigned[var] != (lit>0):
                    return {"status":"UNSAT_BY_UNIT_PROPAGATION"}
                if var not in assigned:
                    new=lit
                    break
        if new is None:break
        assigned[abs(new)] = new>0
    out=[]
    for clause in work:
        if any(assigned.get(abs(lit))==(lit>0)
               for lit in clause if abs(lit) in assigned):
            continue
        residual=[lit for lit in clause if abs(lit) not in assigned]
        if not residual:return {"status":"UNSAT_BY_UNIT_PROPAGATION"}
        out.append(residual)
    return {"status":"SAT_OR_UNKNOWN_SIMPLIFIED",
            "assigned":{str(k):v for k,v in sorted(assigned.items())},
            "residual_clauses":out,
            "original_clause_count":len(clauses)}

def full_xor_signmasks(clauses, n):
    seen=defaultdict(set)
    for c in clauses:
        support=tuple(sorted({abs(v) for v in c}))
        if not support or len(support)!=len(c) or len(support)>6:
            continue
        mask=sum(1<<i for i,v in enumerate(support) if -v in c)
        seen[support].add(mask)
    eq=set()
    for support,masks in seen.items():
        for p in (0,1):
            required={mask for mask in range(1<<len(support))
                      if mask.bit_count()%2==p}
            if required.issubset(masks):
                eq.add((support,1^p))
    return eq

def rank(equations,n):
    basis={}
    for variables,_rhs in sorted(equations):
        mask=0
        for v in variables:mask^=1<<(v-1)
        while mask:
            k=mask.bit_length()-1
            if k not in basis:
                basis[k]=mask
                break
            mask^=basis[k]
    return len(basis)

def baseline_case(n, rows):
    original=[list(c) for c in rows]
    sim=simplify_unit_propagation(original,n)
    if sim["status"]!="SAT_OR_UNKNOWN_SIMPLIFIED":
        return {"status":sim["status"]}
    initial=full_xor_signmasks(original,n)
    reduced=full_xor_signmasks(sim["residual_clauses"],n)
    units={((int(k),),int(v)) for k,v in sim["assigned"].items()}
    baseline=initial | reduced | units
    return {
        "status":"UP_AND_COMPLETE_SIGNMASK_XOR_BASELINE_READY",
        "original_source_sha256":sha256(json.dumps(
            {"n":n,"rows":rows},sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "unit_assignments":sim["assigned"],
        "original_explicit_equations":[{"variables":list(v),"rhs":rhs} for v,rhs in sorted(initial)],
        "post_UP_equations":[{"variables":list(v),"rhs":rhs} for v,rhs in sorted(reduced)],
        "baseline_GF2_coefficient_rank":rank(baseline,n),
        "baseline_equations":[{"variables":list(v),"rhs":rhs} for v,rhs in sorted(baseline)],
        "original_source_retained":True,
        "independent_institution":"NO_SAME_ADMINISTRATOR",
        "performance_claim":"NONE"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    from time_sat_004d9b_science_demo import cases, demonstrate
    original_cases=cases()
    janus={v["case"]:v for v in demonstrate()["examples"]}
    records=[]
    for name,x in original_cases.items():
        baseline=baseline_case(x["n"],x["rows"])
        janus_math=janus[name]
        all_janus={(tuple(v["variables"]),v["rhs"])
                   for v in janus_math["explicit_xor"] + janus_math["derived_xor"]}
        base={(tuple(v["variables"]),v["rhs"])
              for v in baseline["baseline_equations"]}
        new_over_baseline=rank(base|all_janus,x["n"])-rank(base,x["n"])
        records.append({
            "case":name,
            "baseline":baseline,
            "JANUS_additional_coefficient_rank_over_original_explicit_XOR":janus_math["coefficient_rank_increment"],
            "JANUS_additional_coefficient_rank_over_UP_signmask_XOR_baseline":new_over_baseline,
            "interpretation":"Baseline is a simple known preprocessor; no general novelty inference."
        })
    sample={x["case"]:x for x in records}
    if (sample["guarded_source_derived_rank"]["JANUS_additional_coefficient_rank_over_UP_signmask_XOR_baseline"]!=0
        or sample["guarded_source_derived_rank"]["JANUS_additional_coefficient_rank_over_original_explicit_XOR"]!=1):
        raise AssertionError("Falsifier: unit propagation should fully recover illustrative XOR")
    report={
        "schema":"JANUS-TIME-SAT-004D9B-CLEANROOM-UP-XOR-FALSIFICATION-V1",
        "scope":"INTERNAL_CLASSICAL_BASELINE_SAME_ADMIN_NOT_EXTERNAL",
        "main_claim":"The guarded illustrative XOR is already revealed by unit propagation and complete-mask recognition.",
        "external_science":"OPEN",
        "records":records,
        "C023":"UNCHANGED"
    }
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"UP_BASELINE_FALSIFIER_PASS",
                      "comparisons":[{"case":r["case"],"janus_rank_over_up":r["JANUS_additional_coefficient_rank_over_UP_signmask_XOR_baseline"]}
                                     for r in records]},sort_keys=True))
if __name__=="__main__":
    main()
