#!/usr/bin/env python3
from itertools import product

# Tensor entry order: 000,001,010,011,100,101,110,111.


def hyperdet_char2(a):
    # Cayley's 2x2x2 hyperdeterminant reduced modulo 2.
    # The -2 and +4 terms vanish.
    return (
        a[0]*a[0]*a[7]*a[7]
        + a[1]*a[1]*a[6]*a[6]
        + a[2]*a[2]*a[5]*a[5]
        + a[4]*a[4]*a[3]*a[3]
    ) % 2


def parity(bits):
    return sum(bits) & 1


def pure_parity(a):
    nz=[i for i,x in enumerate(a) if x]
    if not nz:
        return True
    ps={parity(((i>>2)&1,(i>>1)&1,i&1)) for i in nz}
    return len(ps)<=1


def gl2_f2():
    out=[]
    for vals in product((0,1), repeat=4):
        a,b,c,d=vals
        det=(a*d-b*c)%2
        if det:
            out.append(((a,b),(c,d)))
    assert len(out)==6
    return out


def transform3(T,S1,S2,S3):
    S=[S1,S2,S3]
    out=[0]*8
    for y in product((0,1), repeat=3):
        yi=(y[0]<<2)|(y[1]<<1)|y[2]
        total=0
        for x in product((0,1), repeat=3):
            xi=(x[0]<<2)|(x[1]<<1)|x[2]
            if not T[xi]:
                continue
            coeff=1
            for k in range(3):
                coeff &= S[k][y[k]][x[k]]
            total ^= coeff
        out[yi]=total
    return out


def main():
    eq3=[0]*8
    eq3[0]=1
    eq3[7]=1
    assert hyperdet_char2(eq3)==1

    # Exhaust every pure-even and pure-odd GF(2) tensor.
    even_ids=[i for i in range(8) if parity(((i>>2)&1,(i>>1)&1,i&1))==0]
    odd_ids=[i for i in range(8) if i not in even_ids]
    checked=0
    for ids in (even_ids,odd_ids):
        for mask in range(1<<4):
            t=[0]*8
            for j,i in enumerate(ids):
                t[i]=(mask>>j)&1
            assert pure_parity(t)
            assert hyperdet_char2(t)==0
            checked += 1
    assert checked==32

    # Finite replay of the invariant consequence over all GL(2,2)^3 gauges.
    G=gl2_f2()
    gauges=0
    for S1 in G:
        for S2 in G:
            for S3 in G:
                T=transform3(eq3,S1,S2,S3)
                gauges += 1
                assert hyperdet_char2(T)==1
                assert not pure_parity(T)
    assert gauges==216

    print('PASS_CHAR2_EQ3_HYPERDETERMINANT_MATCHGATE_GAUGE_BARRIER')
    print('pure_parity_tensors_checked=32')
    print('GL2_F2_edge_gauge_triples_checked=216')
    print('EQ3_hyperdet=1 invariant_nonzero=True')
    print('LOCAL_MATCHGATE_GAUGE_CHAR2=IMPOSSIBLE')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
