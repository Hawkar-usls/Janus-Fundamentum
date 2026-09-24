#!/usr/bin/env python3
"""
Finite controls for NM-0016 boundary metric closure.

Checks:
  * nonnegative binary subset/cycle boundary tables are normalized subadditive
    quotient weights on GF(2) or GF(2)^2;
  * every four-state table has the exact nonnegative 3-coordinate realization;
  * Y3 quotient GF(2)^3/<111> is linearly identified with the even-parity
    Delta state space;
  * min-plus convolution preserves the class;
  * stored minimizer pointers reconstruct exact witnesses.

Finite regression only; not the theorem proof.
"""
from fractions import Fraction
import itertools
import json
import random

INF = None
EVEN = (0b000, 0b011, 0b101, 0b110)

# GF(2)^2 ids: 0,1,2,3 with xor addition.
# Delta embedding chosen as:
# 0->000, 1->011, 2->101, 3->110.
DELTA_FROM_G = {0:0, 1:0b011, 2:0b101, 3:0b110}
G_FROM_DELTA = {v:k for k,v in DELTA_FROM_G.items()}


def parity3(x):
    return x.bit_count() & 1


def y_even_representative(raw):
    # Quotient by <111>: exactly one of raw,raw^111 has even parity.
    y = raw if parity3(raw) == 0 else raw ^ 0b111
    assert y in EVEN
    return y


def y_class_id(raw):
    return G_FROM_DELTA[y_even_representative(raw)]


def check_y_map_linear():
    for x in range(8):
        for y in range(8):
            assert y_class_id(x ^ y) == (y_class_id(x) ^ y_class_id(y))
    # Every quotient class has exactly two raw reps differing by 111.
    for g in range(4):
        reps=[x for x in range(8) if y_class_id(x)==g]
        assert len(reps)==2
        assert reps[0]^reps[1]==0b111


def subset_boundary_table(labels, weights, group_size=4):
    n=len(labels)
    best=[INF]*group_size
    wit=[None]*group_size
    best[0]=Fraction(0)
    wit[0]=0
    for mask in range(1<<n):
        s=0
        c=Fraction(0)
        for i in range(n):
            if (mask>>i)&1:
                s ^= labels[i]
                c += weights[i]
        if best[s] is None or c < best[s]:
            best[s]=c
            wit[s]=mask
    assert all(x is not None for x in best)
    return best,wit


def check_witness(labels,weights,state,cost,mask):
    s=0
    c=Fraction(0)
    for i in range(len(labels)):
        if (mask>>i)&1:
            s ^= labels[i]
            c += weights[i]
    assert s==state
    assert c==cost


def assert_semimetric(d):
    q=len(d)
    assert d[0] == 0
    assert all(x >= 0 for x in d)
    for x in range(q):
        for y in range(q):
            assert d[x^y] <= d[x] + d[y], (d,x,y)


def realize_four_state(d):
    assert len(d)==4
    assert_semimetric(d)
    a,b,c=d[1],d[2],d[3]
    w1=(b+c-a)/2
    w2=(a+c-b)/2
    w3=(a+b-c)/2
    assert min(w1,w2,w3) >= 0
    # state 1=011, 2=101, 3=110
    recon=[Fraction(0),w2+w3,w1+w3,w1+w2]
    assert recon==d,(recon,d)
    return (w1,w2,w3)


def inf_convolution(f,g):
    q=len(f)
    h=[]
    ptr=[]
    for s in range(q):
        vals=[(f[t]+g[s^t],t) for t in range(q)]
        val,t=min(vals,key=lambda z:z[0])
        h.append(val)
        ptr.append(t)
    assert_semimetric(h)
    return h,ptr


def random_table(rng, nitems=None):
    if nitems is None:
        nitems=rng.randint(2,8)
    labels=[rng.randint(1,3) for _ in range(nitems)]
    # Ensure generators span GF(2)^2.
    labels[:2]=[1,2]
    weights=[Fraction(rng.randint(0,30), 2**rng.randint(0,4)) for _ in range(nitems)]
    d,wit=subset_boundary_table(labels,weights,4)
    assert_semimetric(d)
    realize_four_state(d)
    for s in range(4):
        check_witness(labels,weights,s,d[s],wit[s])
    return d


def y_raw_control(rng,trials=300):
    # Internal items export raw 3-bit Y traces.  Cost is minimized by quotient
    # class; toggling 111 on the root interface has no internal real cost.
    checked=0
    for _ in range(trials):
        n=rng.randint(3,8)
        raw=[rng.randint(1,7) for _ in range(n)]
        # ensure quotient images span rank two
        raw[0]=0b100 # class 1 -> even 011
        raw[1]=0b010 # class 2 -> even 101
        labels=[y_class_id(x) for x in raw]
        weights=[Fraction(rng.randint(0,20),2**rng.randint(0,3)) for _ in range(n)]
        d,wit=subset_boundary_table(labels,weights,4)
        assert_semimetric(d)
        w=realize_four_state(d)
        for s in range(4):
            check_witness(labels,weights,s,d[s],wit[s])
        # Fixed even-parity transversal is exactly Delta coordinates.
        assert [DELTA_FROM_G[s] for s in range(4)] == list(EVEN)
        checked+=1
    return checked


def convolution_control(rng,trials=500):
    checked=0
    max_den_bits=0
    for _ in range(trials):
        f=random_table(rng)
        g=random_table(rng)
        h,ptr=inf_convolution(f,g)
        realize_four_state(h)
        for s,t in enumerate(ptr):
            assert h[s]==f[t]+g[s^t]
        for x in h:
            max_den_bits=max(max_den_bits,x.denominator.bit_length())
        checked+=1
    return checked,max_den_bits


def polynomial_denominator_control(depth=200):
    # Worst symbolic repeated half-step only adds one power of two per level.
    d=[Fraction(0),Fraction(1),Fraction(1),Fraction(1)]
    maxbits=0
    for k in range(depth):
        w=realize_four_state(d)
        maxbits=max(maxbits,*(x.denominator.bit_length() for x in w))
        # Make another valid metric with a denominator one bit finer.
        scale=Fraction(1,2)
        d=[x*scale for x in d]
    assert maxbits <= depth+1
    return maxbits


def main():
    check_y_map_linear()
    rng=random.Random(160016)

    direct=0
    for _ in range(500):
        random_table(rng)
        direct+=1

    ychecked=y_raw_control(rng)
    conv,den=convolution_control(rng)
    polyden=polynomial_denominator_control()

    out={
      "status":"PASS_FINITE_BOUNDARY_METRIC_CLOSURE_CONTROLS",
      "direct_semimetric_tables":direct,
      "y_quotient_tables":ychecked,
      "min_plus_convolutions":conv,
      "max_random_denominator_bits":den,
      "repeated_halfstep_depth":200,
      "repeated_halfstep_max_denominator_bits":polyden,
      "theorem":{
        "boundary_groups":["GF2","GF2_SQUARED"],
        "delta_states":["000","011","101","110"],
        "y_quotient":"GF2_CUBED_MOD_111",
        "four_state_realization":"THREE_NONNEGATIVE_RATIONAL_COORDINATE_WEIGHTS",
        "witness_pointers":"EXACT",
        "P_VS_NP":"OPEN"
      }
    }
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
