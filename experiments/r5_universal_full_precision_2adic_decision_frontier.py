#!/usr/bin/env python3
"""R5 all-input cubic graph gate: linear-bit 2-adic residue is exact count.

For a connected simple cubic graph G with v=2h vertices and F(G)
labelled proper 3-edge-colourings, Ivanov (2020) proved:
  F(G) <= 2**h+8 if h even;
  F(G) <= 2**h+4 if h odd.
As F is divisible by 6, C(G)=F(G)//6 satisfies 0 <= C(G)<2**h.

Thus SAT(G) iff C(G) mod 2**h != 0. The ring modulus requires only
h+1 bits. The problem is EVALUATING this residue, not big-integer size!
Computing C(G) mod 2**h for ALL G in poly(v) bit-time would imply P=NP.
It is NOT implemented here. All finite counts use an exponential
independent perfect-matching enumerator, or predecessor exact formulas.

The connected SAT family H_t=Prism_3 +_3 t*K33 has v=6+4t and C(H_t)=2**t,
so 2-adic precision <=t gives a false zero despite SAT. This gives a
LINEAR necessary-bit lower bound for this *specific modular-count route*.
This is not a lower bound for arbitrary SAT algorithms.
"""
from __future__ import annotations

from r5_universal_cubic_flow_lowmoment_collision_20v import (
    SAT20,flower,three_edge_colour_count,
)
from r5_universal_cubic_flow_snf_discriminator import normalized
from r5_universal_cubic_three_edge_cut_factorization import (
    K4,K33,cube,petersen,
)
from r5_universal_modular_flow_count_all_q_no_go import (
    prism,build_fixed_modulus_collision,verify_colouring,
)


def ivanov_upper_bound(v):
    assert v>=4 and v%2==0
    h=v//2
    return 2**h+(8 if h%2==0 else 4)


def audit_finite(name,v,raw,want):
    E=normalized(v,raw)
    full,matches,extendable=three_edge_colour_count(v,E)
    assert full==want, (name,full,want)
    assert full%6==0
    assert full<=ivanov_upper_bound(v)
    normalized_count=full//6
    h=v//2
    modulus=1<<h
    assert normalized_count<modulus
    assert (normalized_count%modulus>0)==(want>0)
    print(f'{name}: vertices={v}, Col3={full}, normalized={normalized_count}, '
          f'full_precision_2adic_bits={h}, mod_full={normalized_count%modulus}, '
          f'PM={matches}, extendable_PM={extendable}',flush=True)


def main():
    p5,e5=prism(5)
    controls=[
        ("K4",4,K4(),6),
        ("K33",6,K33(),12),
        ("CUBE",8,cube(),24),
        ("ODD_PRISM5",p5,e5,30),
        ("PETERSEN",10,petersen(),0),
        ("FLOWER_J5",20,flower(5),0),
        ("CUBIC20_SAT",20,SAT20,72),
    ]
    for name,v,edges,expected in controls:
        audit_finite(name,v,edges,expected)

    for t in (1,2,3,4,8,16):
        v,E,k,a,C,colors=build_fixed_modulus_collision(2**t)
        assert a==t and k==3 and v==6+4*t and C==2**t
        verify_colouring(v,E,colors)
        H=v//2
        assert H==3+2*t
        assert (C%(1<<t))==0
        assert (C%(1<<(t+1)))==C
        assert (C%(1<<H))==C
        assert 6*C<=ivanov_upper_bound(v)
        # This is a *constructively* SAT connected graph, with a
        # demonstrably zero residue at every precision <=t.
        print(f'LOW_PRECISION_COLLISION_t={t}: vertices={v}, '
              f'normalized_Col3={C}, zero_mod_2pow_{t}=YES, '
              f'first_nonzero_bit_index={t}, exact_bits={H}, '
              f'constructed_witness=YES',flush=True)

    print('CONNECTED_CUBIC_S3_NORMALIZED_COLOUR_COUNT_LT_2POW_VHALF = IVANOV_2020')
    print('UNIFORM_HIGH_PRECISION_2ADIC_RESIDUE_AS_DECISION = EXACT_THEOREM')
    print('LINEAR_ADIC_PRECISION_NEEDED_ON_EXPLICIT_SAT_FAMILY = PROVED')
    print('POLYTIME_UNIFORM_HIGH_PRECISION_2ADIC_EVALUATOR = NOT_CONSTRUCTED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
