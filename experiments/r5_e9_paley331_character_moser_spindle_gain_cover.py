#!/usr/bin/env python3
"""Exact regression for the q=331 character/Moser-spindle AF3 cover."""
from itertools import combinations, product

Q=331
R=Q-2
EXPECTED_ORBIT=(1,329,4,323,16,299,64,203,256,150,31,269,124,83,165)
PATTERN=(
    ("X","A"),("X","B"),("A","B"),("A","U"),("B","U"),
    ("X","C"),("X","D"),("C","D"),("C","V"),("D","V"),
    ("U","V"),
)
WITNESSES={
    0: {"X":(0,0),"A":(1,0),"B":(32,2),"U":(33,2),"C":(327,2),"D":(203,2),"V":(199,1)},
    1: {"X":(0,0),"A":(1,2),"B":(300,2),"U":(301,1),"C":(256,0),"D":(248,2),"V":(173,2)},
    2: {"X":(0,0),"A":(1,1),"B":(32,1),"U":(33,2),"C":(323,1),"D":(248,0),"V":(240,1)},
}


def orbit():
    out=[]; x=1
    while x not in out:
        out.append(x); x=x*R%Q
    return tuple(out)


O=orbit()
EXP={d:k for k,d in enumerate(O)}
SUPPORT=set(O)|{(-d)%Q for d in O}


def gain_uv(u,v,c):
    """Return required h(v)-h(u) if {u,v} is a support edge."""
    d=(v-u)%Q
    if d in EXP:
        return (-(EXP[d]%3)-c)%3
    d=(u-v)%Q
    if d in EXP:
        g=(-(EXP[d]%3)-c)%3
        return (-g)%3
    return None


def adjacent_lifted(a,b,c):
    u,hu=a; v,hv=b
    g=gain_uv(u,v,c)
    return g is not None and (hv-hu)%3==g


def neighbours(node,c):
    u,hu=node
    out=[]
    for d in O:
        k=EXP[d]%3
        g=(-k-c)%3
        out.append(((u+d)%Q,(hu+g)%3))
        out.append(((u-d)%Q,(hu-g)%3))
    assert len(out)==2*len(O)
    assert len(set(out))==len(out)
    return out


def support_adjacent(u,v):
    return ((v-u)%Q) in SUPPORT


def k4_free_check():
    n0=sorted(SUPPORT)
    checked=0
    for a,b,c in combinations(n0,3):
        checked+=1
        if support_adjacent(a,b) and support_adjacent(a,c) and support_adjacent(b,c):
            return False,checked,(0,a,b,c)
    return True,checked,None


def chromatic_checks():
    names=("X","A","B","U","C","D","V")
    idx={v:i for i,v in enumerate(names)}
    edges=[(idx[a],idx[b]) for a,b in PATTERN]
    def proper(col):
        return all(col[i]!=col[j] for i,j in edges)
    three=any(proper(col) for col in product(range(3), repeat=7))
    four=next((col for col in product(range(4), repeat=7) if proper(col)),None)
    return three,four


def verify_witness(c,w):
    assert len({w[name][0] for name in w})==7
    for a,b in PATTERN:
        assert adjacent_lifted(w[a],w[b],c), (
            c,a,b,w[a],w[b],gain_uv(w[a][0],w[b][0],c)
        )
    return True


def find_spindle(c):
    """Deterministic fixed-pattern extractor in the lifted gain graph."""
    X=(0,0)
    nx=neighbours(X,c)
    diamonds=[]
    seen=set()
    for A,B in combinations(nx,2):
        if A[0]==B[0] or not adjacent_lifted(A,B,c):
            continue
        nb=set(neighbours(B,c))
        for U in neighbours(A,c):
            if U==X or U not in nb:
                continue
            if len({0,A[0],B[0],U[0]})<4:
                continue
            key=(U,tuple(sorted((A,B))))
            if key in seen:
                continue
            seen.add(key)
            diamonds.append((U,A,B))

    # Exact q=331 census under the normalization X=(0,0).
    assert len(diamonds)==30, (c,len(diamonds))

    for i,(U,A,B) in enumerate(diamonds):
        left={0,U[0],A[0],B[0]}
        for V,C,D in diamonds[i+1:]:
            if not adjacent_lifted(U,V,c):
                continue
            right={0,V[0],C[0],D[0]}
            if left & right != {0}:
                continue
            w={"X":X,"U":U,"A":A,"B":B,"V":V,"C":C,"D":D}
            verify_witness(c,w)
            return w,len(diamonds)
    raise AssertionError(f"no spindle for c={c}")


def main():
    assert O==EXPECTED_ORBIT
    assert len(O)==15

    zeta=pow(R,len(O)//3,Q)
    assert zeta==299
    assert pow(zeta,3,Q)==1 and zeta!=1 and pow(zeta,2,Q)==31

    free,checked,bad=k4_free_check()
    assert free and checked==4060 and bad is None

    three,four=chromatic_checks()
    assert not three
    assert four is not None

    for c,w in WITNESSES.items():
        verify_witness(c,w)

    found={}
    for c in range(3):
        w,count=find_spindle(c)
        found[c]={k:v for k,v in w.items()}
        assert count==30

    print("PASS_PALEY331_CHARACTER_MOSER_SPINDLE_GAIN_COVER")
    print("q=331 ord_331(-2)=15 zeta=299 zeta2=31")
    print("support_degree=30 normalized_K4_triples_checked=4060 K4=False")
    print("moser_vertices=7 moser_edges=11 three_colorable=False four_colorable=True")
    print("explicit_gain_edges_verified=33")
    print("balanced_diamonds_per_c=30,30,30")
    for c in range(3):
        print(f"c={c} extractor_witness={found[c]}")
    print("FIXED_PATTERN_EXTRACTOR=POLYNOMIAL")
    print("FAMILY_WIDE_4CRITICAL_BOUND=OPEN")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__=="__main__":
    main()
