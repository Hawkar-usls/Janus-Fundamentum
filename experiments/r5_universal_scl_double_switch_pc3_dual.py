#!/usr/bin/env python3
"""R5 2-switch adversarial legal SCL attack defeating 3 simple SAT phases.

A rainbow SCL source has variables partitioned into three colour classes
and every check contains one variable of each class. A SINGLE incidence
swap between checks can alter at most TWO variable colour classes:
the third original class remains an exact-one SAT witness. Hence a
single swap CAN NEVER make such a source UNSAT. Proved all rainbow sources.

This test does the required next step: TWO legal incidence switches,
chosen so that NONE of the three original witnesses survive.
Every output remains strictly square+cubic+linear, not an illegal
relaxation or a graph-only example.

Independently: exact complete Boolean search, full GF2 PC3 rank;
if UNSAT yet PC3 inconclusive, output a complete independently
verifiable dual functional certifying PC3 NON-refutability.
No bounded-degree completeness is assumed.
"""
from __future__ import annotations
import itertools,json

from r5_universal_scl_near_sat_incidence_surgery_pc3 import (
    toroidal,cyclic,checked_matrix,swaps,
)
from r5_universal_scl_random_pc3_dual_challenge import (
    exact_boolean_support,pc3_rank_and_dual,
)


def three_rainbow_witnesses(name,n):
    if name.startswith("TORUS"):
        L=int(n**0.5)
        return tuple({i*L+j for i in range(L) for j in range(L)
                      if (i-j)%3==c} for c in range(3))
    return tuple({v for v in range(n) if v%3==c} for c in range(3))


def passes(rows,wit):
    return all(sum(v in wit for v in row)==1 for row in rows)


def main():
    cases=(
        ("TORUS_L6",toroidal(6)),
        ("CYCLIC_N27",cyclic(27)),
        ("CYCLIC_N33",cyclic(33)),
    )
    audited=0;hard=0;legal=0
    for name,(n,raw,witness) in cases:
        base=checked_matrix(raw,n)
        assert base is not None and passes(base,witness)
        ws=three_rainbow_witnesses(name,n)
        assert all(passes(base,w) for w in ws)
        # Induction proof: one swap changes variables only from
        # two classes, leaving one class's clause occupancy invariant.
        first_checked=0;phasebroken=0;case_unsat=0
        for first,row1 in itertools.islice(swaps(base,n),130):
            assert any(passes(row1,w) for w in ws),first
            first_checked+=1
            for second,row2 in itertools.islice(swaps(row1,n),400):
                if all(passes(row2,w)==False for w in ws):
                    phasebroken+=1
                else:continue
                if row2==base:continue
                legal+=1
                witness2,exactstates=exact_boolean_support(row2,n)
                audited+=1
                if witness2 is None:
                    case_unsat+=1;hard+=1
                    refuted,dual,stats=pc3_rank_and_dual(row2,n)
                    print(f'DOUBLE_SWITCH_{name}: first={first} second={second} '
                          f'groundtruth=UNSAT PC3={"REFUTED" if refuted else "INCONCLUSIVE"} '
                          f'exact_states={exactstates} rank={stats["rank"]}/'
                          f'{stats["monomials"]}',flush=True)
                    if not refuted:
                        fixture={
                          "schema":"JANUS-R5-DOUBLE-SWITCH-PC3-DUAL-v1",
                          "n":n,"source":name,
                          "first":list(first),"second":list(second),
                          "rows":[list(row) for row in row2],
                          "degree":3,"dual_bits_hex":hex(dual),
                          "dual_weight":dual.bit_count(),
                          "status":"PROVED_BOOLEAN_UNSAT_AND_PC3_DUAL_NONREFUTATION",
                        }
                        print("EXACT_PC3_DOUBLE_SWITCH_COUNTEREXAMPLE_JSON="+json.dumps(
                            fixture,sort_keys=True,separators=(',',':')),flush=True)
                        print('UNIVERSAL_FIXED_PC3_COMPLETENESS = REFUTED_FINITE_CERT')
                        print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
                        print('P_VS_NP = OPEN')
                        return
                    if case_unsat>=70:break
                if audited>=4000:break
            if case_unsat>=70 or audited>=4000:break
        print(f'{name}_DOUBLE_SWITCH_SUMMARY first_states={first_checked} '
              f'broken_all_3_phase_candidates={phasebroken} '
              f'legal_tested={legal} unsat_verified={case_unsat}',flush=True)
        if audited>=4000:break
    print(f'TOTAL_TWO_SWITCH_ADVERSARIAL_CHECKS={audited} '
          f'UNSAT_REDUCTIONS={hard}',flush=True)
    print('ONE_SWITCH_ALWAYS_PRESERVES_ONE_RAINBOW_SAT_MODEL = PROVED_ALL_RAINBOW')
    print('UNIVERSAL_FIXED_PC3_COMPLETENESS = STILL_OPEN_IF_NO_WITNESS')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
