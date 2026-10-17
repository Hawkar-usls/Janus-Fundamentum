#!/usr/bin/env python3
"""Replay the cube-root/rainbow-Z3 SAT terminal on a Paley 3-lift."""

from itertools import combinations

Q=11

def paley():
    residues={a*a % Q for a in range(1,Q)}
    arcs=[
        (i,j)
        for i in range(Q)
        for j in range(Q)
        if i!=j and ((j-i)%Q) in residues
    ]
    ai={a:i for i,a in enumerate(arcs)}
    triangles=[]
    for a,b,c in combinations(range(Q),3):
        for cyc in ((a,b,c),(a,c,b)):
            T=((cyc[0],cyc[1]),(cyc[1],cyc[2]),(cyc[2],cyc[0]))
            if all(e in ai for e in T):
                triangles.append(T)
    assert len(arcs)==len(triangles)==55
    return arcs,ai,triangles

def build_phase_lift():
    arcs,ai,triangles=paley()

    # Deterministic base-arc phase labels.
    h=[j%3 for j in range(55)]

    A=[[0]*165 for _ in range(165)]
    colors=[0]*165

    for j in range(55):
        for c in range(3):
            colors[3*j+c]=(h[j]+c)%3

    for t,T in enumerate(triangles):
        ids=[ai[e] for e in T]

        # Gauge the first incidence shift to zero.
        target0=h[ids[0]]
        remaining=[r for r in (0,1,2) if r!=target0]

        # Deterministic orientation choice.
        if t%2:
            remaining.reverse()

        target=(target0,remaining[0],remaining[1])
        shifts=(
            0,
            (target[1]-h[ids[1]])%3,
            (target[2]-h[ids[2]])%3,
        )

        for c in range(3):
            r=3*t+c
            cols=[]
            for pos,j in enumerate(ids):
                cc=(c+shifts[pos])%3
                v=3*j+cc
                cols.append(v)
                A[r][v]=1

            # The three phases must be a rainbow.
            assert {colors[v] for v in cols}=={0,1,2}

    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(165))==3 for j in range(165))

    supports=[{j for j,v in enumerate(row) if v} for row in A]
    assert all(
        len(supports[i]&supports[j])<=1
        for i in range(165)
        for j in range(i)
    )

    return A,colors

def main():
    A,colors=build_phase_lift()

    witnesses=[]
    for q in range(3):
        x=[1 if c==q else 0 for c in colors]
        assert sum(x)==55
        assert all(
            sum(A[i][j]*x[j] for j in range(165))==1
            for i in range(165)
        )
        witnesses.append(tuple(i for i,b in enumerate(x) if b))

    assert len(set(witnesses))==3

    print("CUBE_ROOT_KERNEL_RAINBOW_Z3_TERMINAL: PASS")
    print("Paley phase-engineered lift: n=165 square/cubic/linear")
    print("three phase classes each have 55 variables")
    print("three explicit Exact-One witnesses verified")
    print("phase-engineered full-support twisted mode => SAT")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
