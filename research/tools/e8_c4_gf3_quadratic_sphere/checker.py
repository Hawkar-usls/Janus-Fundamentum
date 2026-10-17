#!/usr/bin/env python3
from itertools import product

P=3


def one_nonzero(y):
    return sum(v != 0 for v in y) == 1


def sphere(y):
    return sum((v*v) % P for v in y) % P == 1


def main():
    for y in product(range(P), repeat=3):
        assert one_nonzero(y) == sphere(y), y

    proper=[]
    for a in product((1,2), repeat=4):
        if sum(a)%P:
            continue
        y = (-(a[0]+a[1])%P, -(a[0]+a[2])%P, -(a[0]+a[3])%P)
        assert sphere(y)
        proper.append((a,y))
    assert len(proper)==6

    # Nonzero edge tension iff square equals one over GF(3).
    for t in range(P):
        assert ((t != 0) == ((t*t)%P == 1))

    print('PASS: ONE_NONZERO_3 <=> GF3 quadratic sphere and C4 translation verified')

if __name__=='__main__':
    main()
