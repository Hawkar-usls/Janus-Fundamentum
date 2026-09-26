#!/usr/bin/env python3
"""
Finite controls for NM-0016 boundary metric closure.

Correct Delta/Y semantics:
  * 2-sum: state group GF(2), direct scalar compiler.
  * ordinary Delta-3: primal component has interface-only 111 codeword, so
    raw traces are quotiented by <111>.  A quotient semimetric d is compiled
    by raw connector weights beta_i=d([e_i]); triangle inequalities guarantee
    min{beta_i, beta_j+beta_k}=d([e_i]).
  * dual Y/bar-3: 111 lies in the dual, so primal traces are the even-parity
    subspace {000,011,101,110}.  A semimetric is compiled by Kashyap's
    half-sum coefficients.

Also checks min-plus closure, exact state/witness pointers, and polynomial
denominator growth.  Finite regression only; not the theorem proof.
"""
from fractions import Fraction
import json
import random

EVEN=(0b000,0b011,0b101,0b110)

# Abstract GF(2)^2 ids:
# 0 -> 000
# 1 -> even rep 011 = quotient class {011,100}
# 2 -> even rep 101 = quotient class {101,010}
# 3 -> even rep 110 = quotient class {110,001}
EVEN_FROM_G={0:0b000,1:0b011,2:0b101,3:0b110}
G_FROM_EVEN={v:k for k,v in EVEN_FROM_G.items()}


def parity3(x):
    return x.bit_count()&1


def even_representative_of_delta_class(raw):
    # Exactly one of raw and raw^111 has even parity.
    y=raw if parity3(raw)==0 else raw^0b111
    assert y in EVEN
    return y


def delta_class_id(raw):
    return G_FROM_EVEN[even_representative_of_delta_class(raw)]


def assert_delta_quotient_map_linear():
    for x in range(8):
        for y in range(8):
            assert delta_class_id(x^y)==(delta_class_id(x)^delta_class_id(y))
    for g in range(4):
        reps=[x for x in range(8) if delta_class_id(x)==g]
        assert len(reps)==2
        assert reps[0]^reps[1]==0b111


def assert_semimetric(d):
    q=len(d)
    assert d[0]==0
    assert all(x>=0 for x in d)
    for x in range(q):
        for y in range(q):
            assert d[x^y] <= d[x]+d[y], (d,x,y)


def y_even_compiler(d):
    """Linear costs on the *even* traces 000,011,101,110."""
    assert len(d)==4
    assert_semimetric(d)
    a,b,c=d[1],d[2],d[3]
    w1=(b+c-a)/2
    w2=(a+c-b)/2
    w3=(a+b-c)/2
    assert min(w1,w2,w3)>=0
    def raw_cost(t):
        return ((w1 if t&0b100 else 0) +
                (w2 if t&0b010 else 0) +
                (w3 if t&0b001 else 0))
    recon=[raw_cost(EVEN_FROM_G[g]) for g in range(4)]
    assert recon==d,(recon,d)
    return (w1,w2,w3)


def delta_quotient_compiler(d):
    """
    Linear costs on raw GF(2)^3 traces, with t~t^111.
    Use singleton-class distances directly.  The induced quotient cost is
    the minimum over the two representatives.
    """
    assert len(d)==4
    assert_semimetric(d)
    # raw singleton 100 has class 1; 010 class 2; 001 class 3.
    beta=(d[1],d[2],d[3])
    def raw_cost(t):
        return ((beta[0] if t&0b100 else 0) +
                (beta[1] if t&0b010 else 0) +
                (beta[2] if t&0b001 else 0))
    for g in range(4):
        reps=[t for t in range(8) if delta_class_id(t)==g]
        induced=min(raw_cost(t) for t in reps)
        assert induced==d[g],(g,d,reps,[raw_cost(t) for t in reps])
    return beta


def two_sum_compiler(d):
    assert len(d)==2
    assert d[0]==0 and d[1]>=0
    return d[1]


def subset_boundary_table(labels,weights,q):
    n=len(labels)
    best=[None]*q
    witness=[None]*q
    for mask in range(1<<n):
        s=0
        cost=Fraction(0)
        for i in range(n):
            if (mask>>i)&1:
                s ^= labels[i]
                cost += weights[i]
        if best[s] is None or cost<best[s]:
            best[s]=cost
            witness[s]=mask
    assert all(x is not None for x in best)
    assert best[0]==0  # empty witness + nonnegative weights
    return best,witness


def check_witness(labels,weights,state,cost,mask):
    s=0
    c=Fraction(0)
    for i in range(len(labels)):
        if (mask>>i)&1:
            s ^= labels[i]
            c += weights[i]
    assert s==state
    assert c==cost


def random_four_table(rng,nitems=None):
    if nitems is None:
        nitems=rng.randint(2,8)
    labels=[rng.randint(1,3) for _ in range(nitems)]
    labels[:2]=[1,2]  # span GF(2)^2
    weights=[Fraction(rng.randint(0,30),2**rng.randint(0,4))
             for _ in range(nitems)]
    d,wit=subset_boundary_table(labels,weights,4)
    assert_semimetric(d)
    y_even_compiler(d)
    delta_quotient_compiler(d)
    for s in range(4):
        check_witness(labels,weights,s,d[s],wit[s])
    return d,wit


def random_two_table(rng):
    labels=[1 for _ in range(rng.randint(1,7))]
    weights=[Fraction(rng.randint(0,30),2**rng.randint(0,4))
             for _ in labels]
    d,wit=subset_boundary_table(labels,weights,2)
    two_sum_compiler(d)
    return d,wit


def explicit_delta_countercheck():
    # Demonstrates why the Y half-sum compiler must NOT be copied to Delta.
    d=[Fraction(0),Fraction(2),Fraction(2),Fraction(2)]
    w=y_even_compiler(d)  # (1,1,1), correct on even traces only
    # In Delta the class of 100 also contains 011: raw half-sum costs 1 vs 2.
    raw100=w[0]
    raw011=w[1]+w[2]
    assert min(raw100,raw011)==1 != d[1]
    # Correct Delta compiler is (2,2,2).
    beta=delta_quotient_compiler(d)
    assert beta==(Fraction(2),Fraction(2),Fraction(2))
    return True


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


def convolution_control(rng,trials=500):
    checked=0
    max_den_bits=0
    for _ in range(trials):
        f,_=random_four_table(rng)
        g,_=random_four_table(rng)
        h,ptr=inf_convolution(f,g)
        y_even_compiler(h)
        delta_quotient_compiler(h)
        for s,t in enumerate(ptr):
            assert h[s]==f[t]+g[s^t]
        for x in h:
            max_den_bits=max(max_den_bits,x.denominator.bit_length())
        checked+=1
    return checked,max_den_bits


def polynomial_denominator_control(depth=200):
    # Only Y half-sum can add a factor two; one bit per level is polynomial.
    d=[Fraction(0),Fraction(1),Fraction(1),Fraction(1)]
    maxbits=0
    for _ in range(depth):
        w=y_even_compiler(d)
        maxbits=max(maxbits,*(x.denominator.bit_length() for x in w))
        d=[x*Fraction(1,2) for x in d]
    assert maxbits<=depth+1
    return maxbits


def main():
    assert_delta_quotient_map_linear()
    explicit_delta_countercheck()
    rng=random.Random(160016)

    direct=0
    for _ in range(500):
        random_four_table(rng)
        direct+=1

    two=0
    for _ in range(300):
        random_two_table(rng)
        two+=1

    conv,den=convolution_control(rng)
    polyden=polynomial_denominator_control()

    out={
      "status":"PASS_FINITE_BOUNDARY_METRIC_CLOSURE_CONTROLS",
      "two_sum_tables":two,
      "four_state_semimetric_tables":direct,
      "min_plus_convolutions":conv,
      "delta_half_sum_misuse_falsifier":"PASS",
      "max_random_denominator_bits":den,
      "repeated_halfstep_depth":200,
      "repeated_halfstep_max_denominator_bits":polyden,
      "theorem":{
        "two_sum_state":"GF2",
        "delta_state":"GF2_CUBED_MOD_111",
        "delta_compiler":"SINGLETON_CLASS_DISTANCES",
        "y_state":"EVEN_PARITY_SUBSPACE_OF_GF2_CUBED",
        "y_compiler":"HALF_SUM_WEIGHTS",
        "abstract_four_state_group":"GF2_SQUARED",
        "witness_pointers":"EXACT",
        "P_VS_NP":"OPEN"
      }
    }
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
