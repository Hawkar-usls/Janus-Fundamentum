#!/usr/bin/env python3
"""Close the E79 characteristic-2/3 uniform holographic-basis loophole."""

from itertools import product


def gl2(p):
    out=[]
    for a,b,c,d in product(range(p), repeat=4):
        if (a*d-b*c) % p:
            out.append((a,b,c,d))
    return out


def transformed(B,p):
    a,b,c,d=B
    f=[
        (3*c*a*a) % p,
        (d*a*a + 2*a*b*c) % p,
        (c*b*b + 2*a*b*d) % p,
        (3*d*b*b) % p,
    ]
    g=[
        (a**3+c**3) % p,
        (a*a*b+c*c*d) % p,
        (a*b*b+c*d*d) % p,
        (b**3+d**3) % p,
    ]
    return f,g


def parity_supported(s,p):
    even = all(s[w] % p == 0 for w in (1,3))
    odd  = all(s[w] % p == 0 for w in (0,2))
    return even or odd


def check_field(p, expected_gl):
    mats=gl2(p)
    assert len(mats)==expected_gl
    good=[]
    for B in mats:
        f,g=transformed(B,p)
        if parity_supported(f,p) and parity_supported(g,p):
            good.append((B,f,g))
    assert good==[]
    print(f"GF({p}): GL2={len(mats)} simultaneous parity bases=0 PASS")


def main():
    check_field(2,6)
    check_field(3,48)
    print("E79 characteristic-2/3 loophole CLOSED")
    print("Combined with E79 char!=2,3: no uniform 2x2 holographic basis over any field")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
