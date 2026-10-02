#!/usr/bin/env python3
from itertools import product

H = [
    ((0,0,1),0),
    ((0,1,0),0),
    ((0,1,1),0),
    ((1,0,0),0),
    ((1,1,2),1),
    ((1,2,1),2),
]


def hit(h,p):
    a,c=h
    return sum(x*y for x,y in zip(a,p)) % 3 == c


def canon(v):
    j=next(i for i,x in enumerate(v) if x%3)
    inv=pow(v[j]%3,-1,3)
    return tuple((inv*x)%3 for x in v)


def main():
    assert len({canon(a) for a,_ in H}) == 6
    pts=list(product(range(3), repeat=3))
    assert all(any(hit(h,p) for h in H) for p in pts)
    assert not any(all(hit(h,p) for h in H) for p in pts)
    private=[]
    for i,h in enumerate(H):
        P=[p for p in pts if hit(h,p) and not any(hit(g,p) for j,g in enumerate(H) if j!=i)]
        assert P
        private.append(P[0])
    print({'status':'PASS_AF3_ESSENTIAL_SIX_HYPERPLANE_COVER','private_points':private})
    print('E8_D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__=='__main__':
    main()
