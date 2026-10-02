#!/usr/bin/env python3
"""Finite exact controls for R5 E33.

For a totally-unimodular integer matrix R, test the theorem

    exists x in {0,1}^n with R(3x-1)=0
    iff
    every coordinate of R*1 is divisible by 3.

The proof in the theorem note is general; this checker brute-forces small signed
incidence matrices (a canonical TU class) as independent controls.

P_VS_NP remains OPEN.
"""

from itertools import product


def incidence(num_vertices, edges):
    # Column e=(u,v) has +1 at tail u and -1 at head v.
    R=[[0]*len(edges) for _ in range(num_vertices)]
    for j,(u,v) in enumerate(edges):
        R[u][j]=1
        R[v][j]=-1
    return R


def matvec(R,x):
    return [sum(a*b for a,b in zip(row,x)) for row in R]


def criterion(R):
    s=matvec(R,[1]*len(R[0])) if R and R[0] else [0]*len(R)
    return all(v % 3 == 0 for v in s)


def brute(R):
    n=len(R[0]) if R else 0
    one=[1]*n
    for x in product((0,1), repeat=n):
        y=[3*x[i]-1 for i in range(n)]
        if matvec(R,y) == [0]*len(R):
            return True,x
    return False,None


def check_case(name,V,edges):
    R=incidence(V,edges)
    c=criterion(R)
    sat,w=brute(R)
    assert c == sat
    print(f"{name}: V={V}, E={len(edges)}, criterion={c}, brute={sat}, witness={w}")


def main():
    # Directed 3-cycle: balanced, all -1 is already a centered circulation.
    check_case("directed_triangle",3,[(0,1),(1,2),(2,0)])

    # Three parallel arcs: imbalance (+3,-3) is divisible by three; one selected
    # edge and two unselected edges give centered values (2,-1,-1).
    check_case("three_parallel",2,[(0,1),(0,1),(0,1)])

    # One outgoing star: leaf imbalances are -1, so the mod-3 condition fails.
    check_case("out_star_3",4,[(0,1),(0,2),(0,3)])

    # Opposite pair is balanced and has a centered circulation (-1,-1).
    check_case("opposite_pair",2,[(0,1),(1,0)])

    # Small mixed graph controls.
    check_case("two_triangles",5,[(0,1),(1,2),(2,0),(0,3),(3,4),(4,0)])
    check_case("path_plus_arc",4,[(0,1),(1,2),(2,3),(0,3)])

    print("R5 E33 TU-kernel terminal controls: PASS")
    print("Scientific ceiling: P_VS_NP remains OPEN.")


if __name__ == "__main__":
    main()
