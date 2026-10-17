#!/usr/bin/env python3
from itertools import product

NEG={(0,4),(0,6),(0,7),(0,9),(1,3),(1,5),(1,6),(1,8),(2,3),(2,4),(2,5),(2,8),(3,8),(3,9),(4,6),(4,9),(5,7),(5,8),(6,7),(7,9)}
POS={(0,4),(0,6),(0,7),(0,9),(1,3),(1,5),(1,7),(1,8),(2,3),(2,4),(2,5),(2,8),(3,8),(3,9),(4,6),(4,9),(5,6),(5,8),(6,7),(7,9)}
HNEG=(0,4,2,3,8,5,1,6,7,9,0)
HPOS=(0,4,2,3,1,8,5,6,7,9,0)
A={0,4,6,7,9}
B=set(range(10))-A


def ce(a,b): return (a,b) if a<b else (b,a)
NEG={ce(*e) for e in NEG}; POS={ce(*e) for e in POS}


def degrees(E):
    return [sum(v in e for e in E) for v in range(10)]


def connected(E):
    adj=[set() for _ in range(10)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    seen={0};stack=[0]
    while stack:
        v=stack.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w);stack.append(w)
    return len(seen)==10


def valid_hamiltonian(E,C):
    return len(C)==11 and C[0]==C[-1] and set(C[:-1])==set(range(10)) and len(set(C[:-1]))==10 and all(ce(C[i],C[i+1]) in E for i in range(10))


def count3(E):
    cnt=0;first=None
    for c in product(range(3),repeat=10):
        if all(c[a]!=c[b] for a,b in E):
            cnt+=1
            if first is None:first=c
    return cnt,first


def main():
    print('E8 v6.8 full transition-matroid balanced-mutation coloring barrier')
    for name,E,C in [('NEG',NEG,HNEG),('POS',POS,HPOS)]:
        assert len(E)==20
        assert degrees(E)==[4]*10
        assert connected(E)
        assert valid_hamiltonian(E,C)
        print(f'PASS {name}: simple connected 4-regular and Hamiltonian')

    cut={e for e in NEG if (e[0] in A)!=(e[1] in A)}
    expected_cut={ce(6,1),ce(4,2),ce(9,3),ce(7,5)}
    assert cut==expected_cut,(cut,expected_cut)
    removed=NEG-POS;added=POS-NEG
    assert removed=={ce(6,1),ce(7,5)}
    assert added=={ce(6,5),ce(7,1)}
    # These four half-edges are one paired portion of the four-edge cut;
    # the other cut pair (4-2,9-3) is reassembled unchanged.
    print('PASS balanced mutation edge reassembly: remove',sorted(removed),'add',sorted(added))

    ncnt,nfirst=count3(NEG)
    pcnt,pfirst=count3(POS)
    assert ncnt==0 and nfirst is None
    assert pcnt==18 and pfirst is not None
    assert pfirst==(0,0,0,1,1,1,2,1,2,2),pfirst
    print('PASS exhaustive 3^10 coloring: NEG=0, POS=18')
    print('PASS explicit POS witness:',pfirst)
    print('SOURCE THEOREM: balanced mutation preserves full transition-matroid isomorphism')
    print('CONCLUSION: 3-colorability is not determined by the full transition matroid')
    print('P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY')

if __name__=='__main__':
    main()
