#!/usr/bin/env python3
"""R5 E107: defect quantization -> 12-flat threshold / exact 3-fold cover.

Current parent lane is E85/E93 p=1,h=1:
  number of active check vertices a = 3t+1.

For ANY GF(2)-parity-compatible raw8 candidate Y:
  * raw8 has E=1, so check E receives 0 internal selected incidences;
  * A,B,C and every other non-E check have odd parity, hence integer selected
    degree 1 or 3;
  * let delta be the number of ordinary checks with selected degree 3;
  * x is unselected (V=0), so every selected internal variable contributes
    three internal incidences.

Double counting selected incidences gives

    3|Y| = (a-1) + 2 delta.

Since a-1 is divisible by 3,

    delta == 0 (mod 3).

In the E105 flat language delta(z) is exactly the number of forbidden check
fibers containing kernel point z.

After E106 propagation, every active forbidden fiber has relative codimension
two, hence size |D|/4 in residual affine domain D.

If NO_RAW8:
  delta(z) >= 3 for every z in D,
so
  m |D| / 4 = sum_z delta(z) >= 3 |D|,
hence
  m >= 12.

Therefore:
  fewer than 12 active rank-2 flats => RAW8 exists.

At the threshold m=12, equality forces
  delta(z)=3 for every z:
the forbidden fibers form an exact 3-fold affine cover of D.

Fourier consequence at m=12:
write each codim2 flat as the fiber of a rank2 dual line L_c <= D* with marked
character chi_c.  Indicator expansion gives
  1_{B_c}(x) = 1/4 sum_{g in L_c} (-1)^{chi_c(g)+g(x)}.
If sum_c 1_{B_c}(x)=3 identically, then for every nonzero dual g,
  sum_{c: g in L_c} (-1)^{chi_c(g)} = 0.
Thus every used dual functional occurs with an even number of + / - marked
incidences and the signs balance exactly.

E104 replay:
  residual domain has 8 points;
  active rank2 flats m=18;
  defect multiplicity spectrum is {0:4 points, 9:4 points};
  average defect multiplicity = 18/4 = 4.5.
The four zero-defect points are exactly raw8 witnesses.

P_VS_NP remains OPEN.
"""

from collections import Counter

from r5_e106_affine_unit_propagation_rank2_core import (
    build_e104_flat_sets,
    propagate_explicit,
    all_points,
)


def verify_defect_quantization_arithmetic():
    # Abstract p=1,h=1 sizes: a=3t+1.
    for t in range(1,50):
        a=3*t+1
        for delta in range(0,a+1):
            rhs=(a-1)+2*delta
            if rhs%3==0:
                assert delta%3==0


def verify_twelve_flat_threshold():
    # At a fixed-point pure rank2 domain every active flat has density 1/4.
    # NO_RAW8 + defect quantization means multiplicity >=3 everywhere.
    for dim in range(2,10):
        N=1<<dim
        q=N//4
        for m in range(0,12):
            total=m*q
            assert total < 3*N

    # At m=12 total membership is exactly 3|D|, so if every point is covered
    # at least three times then every point is covered exactly three times.
    for dim in range(2,10):
        N=1<<dim
        total=12*(N//4)
        assert total==3*N


def dot_parity(x,y):
    return (x&y).bit_count()&1


def flat_from_line_character(d,a,b,alpha,beta):
    assert a and b and a!=b
    return frozenset(
        x for x in range(1<<d)
        if dot_parity(a,x)==alpha and dot_parity(b,x)==beta
    )


def fourier_coefficient_of_flat(B,g,d):
    return sum((1 if dot_parity(g,x)==0 else -1) for x in B)


def verify_threshold_fourier_identity():
    # Generic exact 3-fold cover example: take all four cosets of one
    # codim2 subspace, repeated three times.  This is NOT claimed realizable
    # by our Tanner geometry; it only freezes the Fourier necessity.
    d=4
    a,b=1,2
    four=[
        flat_from_line_character(d,a,b,alpha,beta)
        for alpha in (0,1) for beta in (0,1)
    ]
    flats=four*3

    mult=Counter()
    for B in flats:
        for x in B:
            mult[x]+=1
    assert set(mult.values())=={3}
    assert len(mult)==1<<d

    # Nonconstant Fourier coefficients of the total multiplicity vanish.
    for g in range(1,1<<d):
        coeff=sum(fourier_coefficient_of_flat(B,g,d) for B in flats)
        assert coeff==0


def verify_e104_replay():
    vn,support,cn,basis,words,e,flats=build_e104_flat_sets()
    D=all_points(len(basis))
    D2,active,unsat=propagate_explicit(D,flats)
    assert not unsat
    assert D2==D
    assert len(active)==18

    mult=Counter({x:0 for x in D2})
    for B in active:
        for x in D2&B:
            mult[x]+=1

    spectrum=Counter(mult.values())
    assert spectrum==Counter({0:4,9:4})
    assert all(k%3==0 for k in spectrum)
    assert sum(mult.values())==len(active)*len(D2)//4
    assert sum(mult.values())/len(D2)==18/4

    return {
        "domain_points":len(D2),
        "active_rank2_flats":len(active),
        "multiplicity_spectrum":dict(sorted(spectrum.items())),
        "average_multiplicity":sum(mult.values())/len(D2),
    }


def main():
    verify_defect_quantization_arithmetic()
    verify_twelve_flat_threshold()
    verify_threshold_fourier_identity()
    stats=verify_e104_replay()

    print("R5 E107 defect-quantized rank2-cover threshold: PASS")
    print("raw8 parity defect count delta is always 0 mod3 on the p=1,h=1 parent lane")
    print("NO_RAW8 in E106 pure rank2 core => every point has multiplicity >=3")
    print("therefore active rank2 flat count m>=12")
    print("m<12 => RAW8 guaranteed")
    print("m=12 + NO_RAW8 => exact 3-fold affine cover")
    print("threshold Fourier balance: every nonzero dual frequency cancels")
    print("E104 replay:",stats)
    print("next target: classify or kill structured 12-flat triple covers, then extend to m>12")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
