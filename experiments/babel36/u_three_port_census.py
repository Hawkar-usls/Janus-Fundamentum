#!/usr/bin/env python3
"""BABEL36: COMPLETE finite 3-port census for frozen U=SCL27.

For EACH of 2,925 distinct 3-deleted-row sets, independently enumerate ALL
27-bit Exact-One solutions of 24 rows via (A) unit-propagation Boolean DPLL
and (B) rational Gaussian row-echelon with ALL Boolean free projections.
Then exhaustively evaluate ALL row-distinct variable-distinct port choices.
This is a finite fixed-gadget theorem, NOT a theorem about arbitrary SCL.
"""
import hashlib
import itertools
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from experiments.babel34.local_three_port_forcing import (
    ROWS,SHA,local_dpll,exhaustive_q_boolean_projection
)

TRIPLE_RELATION=(
    ((0,0,0),(0,0,0)),
    ((0,0,0),(1,1,1)),
    ((1,1,1),(0,0,0))
)
EXPECTED_HIST={1:71067,2:1871,3:16}


def local_models_for_rows(deleted):
    assert len(deleted)==3 and len(set(deleted))==3
    unchanged=tuple(row for i,row in enumerate(ROWS) if i not in deleted)
    M,dcalls=local_dpll(unchanged)
    N,rank,free=exhaustive_q_boolean_projection(unchanged)
    assert M==N,("independent local mismatch",deleted,M,N)
    return tuple(sorted(M)),rank,len(free),dcalls


def relation_from_models(ports,models):
    ports=tuple(sorted(ports))
    assert len(ports)==3 and len({r for r,v in ports})==3
    assert len({v for r,v in ports})==3
    assert all(v in ROWS[r] for r,v in ports)
    relation=[]
    for physical in models:
        outbound=tuple(physical>>v&1 for r,v in ports)
        incoming=tuple(1-sum(physical>>j&1 for j in ROWS[r] if j!=v)
                       for r,v in ports)
        if all(b in (0,1) for b in incoming):
            relation.append((outbound,incoming,physical))
    assert len({(a,b,x) for a,b,x in relation})==len(relation)
    return tuple(sorted(relation))


def get_relation(ports):
    rs=tuple(sorted(r for r,v in ports))
    models,_,_,_=local_models_for_rows(rs)
    return relation_from_models(ports,models)


def exhaustive_census():
    assert hashlib.sha256(json.dumps(ROWS,separators=(",",":")).encode()).hexdigest()==SHA
    h=Counter();three_patterns=Counter();rank_hist=Counter()
    total_ports=0;all_rowsets=0;total_dpll_nodes=0;max_models=0
    examples={}
    for deleted in itertools.combinations(range(27),3):
        all_rowsets+=1
        models,rank,k,dcalls=local_models_for_rows(deleted)
        rank_hist[rank]+=1
        total_dpll_nodes+=dcalls
        max_models=max(max_models,len(models))
        for vars_ in itertools.product(*(ROWS[ri] for ri in deleted)):
            if len(set(vars_))!=3:continue
            ports=tuple(zip(deleted,vars_))
            relation=relation_from_models(ports,models)
            count=len(relation)
            assert 1<=count<=3,(ports,count,relation)
            h[count]+=1;total_ports+=1
            if count not in examples:
                examples[count]={
                   "port_occurrences":[list(p) for p in ports],
                   "relation":[{"export":list(a),"import":list(b)}
                               for a,b,x in relation]}
            if count==3:
                pattern=tuple(sorted((a,b) for a,b,x in relation))
                assert pattern==TRIPLE_RELATION,(ports,pattern)
                three_patterns[pattern]+=1
    assert all_rowsets==2925 and total_ports==72954
    assert dict(h)==EXPECTED_HIST,(h,EXPECTED_HIST)
    assert len(three_patterns)==1 and next(iter(three_patterns.values()))==16
    return {
        "all_deleted_3row_sets_exact_DPLL_AND_rational":all_rowsets,
        "all_variable_distinct_3port_tuples":total_ports,
        "complete_relation_cardinality_histogram":{str(k):h[k] for k in sorted(h)},
        "ALL_16_THREE_STATE_RELATIONS_IDENTICAL":True,
        "three_state_R":TRIPLE_RELATION,
        "rational_punctured_rank_histogram":dict(rank_hist),
        "maximum_unfiltered_punctured_models":max_models,
        "total_exact_DPLL_nodes":total_dpll_nodes,
        "example_each_relation_cardinality":examples
    }


def main():
    result=exhaustive_census()
    print(json.dumps({
      "gate":"BABEL36_COMPLETE_THREE_PORT_U_FINITE_CLASSIFICATION",
      "all_72954_cases_independently_complete":"EXACT_PASS",
      "all_2925_rowsets_independent_Q_DPLL_agreement":"EXACT_PASS",
      "max_relation_size":3,
      "only_size3_relation":"{(000,000),(000,111),(111,000)}",
      "uniform_macro_2SAT_reduction":"MATHEMATICAL_THEOREM",
      "general_SCL_polynomiality":"NOT_PROVED",
      "P_vs_NP":"OPEN",
      "census":result
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
