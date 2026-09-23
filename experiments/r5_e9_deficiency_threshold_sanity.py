#!/usr/bin/env python3
"""Counting identities for the R5 E9 deficiency frontier."""

def regular_uniform_deficiency(vertices: int, edge_size: int, degree: int):
    incidence = degree * vertices
    assert incidence % edge_size == 0
    edges = incidence // edge_size
    return edges - vertices

def main():
    for n in range(3, 301, 3):
        # 3-uniform, 3-regular: m=n -> deficiency 0.
        assert regular_uniform_deficiency(n,3,3) == 0
        # 3-uniform, 4-regular: m=4n/3 -> deficiency n/3.
        assert regular_uniform_deficiency(n,3,4) == n//3
    print("R5 E9 deficiency threshold identities: PASS")

if __name__ == "__main__":
    main()
