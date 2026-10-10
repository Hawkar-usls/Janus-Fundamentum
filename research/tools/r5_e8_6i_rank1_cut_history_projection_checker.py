#!/usr/bin/env python3
from itertools import product

VARS = ("a","b","c","u","v")
VID = {v:i for i,v in enumerate(VARS)}
EDGES = (
    ("a","b"),
    ("a","u"),
    ("a","c"),
    ("a","v"),
    ("b","c"),
    ("b","v"),
    ("c","u"),
    ("u","v"),
)
OR3 = {abc for abc in product((0,1), repeat=3) if any(abc)}
TRUE3 = set(product((0,1), repeat=3))


def boundary_relation(mask: int):
    rel=set()
    for vals in product((0,1), repeat=5):
        fixed={}
        for ei,(x,y) in enumerate(EDGES):
            if (mask>>ei)&1:
                fixed[ei]=vals[VID[x]] & vals[VID[y]]

        # The affine moment system always contains p_uv = 0.
        if 7 in fixed and fixed[7] != 0:
            continue
        fixed[7]=0

        # The linearized majority equation is xor of all eight moment products = 1.
        # Any free product among the first seven can absorb the parity requirement.
        free=[i for i in range(7) if i not in fixed]
        parity=0
        for value in fixed.values():
            parity ^= value

        if free or parity == 1:
            rel.add(vals[:3])
    return rel


def main():
    classes={}
    for mask in range(256):
        rel=frozenset(boundary_relation(mask))
        classes.setdefault(rel,[]).append(mask)

    assert len(classes)==2
    true_masks=classes[frozenset(TRUE3)]
    or_masks=classes[frozenset(OR3)]

    assert len(true_masks)==254
    assert set(or_masks)=={0b01111111,0b11111111}

    required_first_seven=set(range(7))
    for mask in or_masks:
        assert all((mask>>i)&1 for i in required_first_seven)

    # Removing any one of the seven semantic product cuts destroys all boundary information.
    for i in range(7):
        mask=0b01111111 ^ (1<<i)
        assert boundary_relation(mask)==TRUE3

    print("CUT_HISTORIES = 256")
    print("BOUNDARY_RELATION_CLASSES = 2")
    print("TRUE3_HISTORIES = 254")
    print("OR3_HISTORIES = 2")
    print("MIN_REQUIRED_SEMANTIC_PRODUCT_CUTS = 7")
    print("UV_IDENTITY_BOUNDARY_RELEVANCE = NONE")
    print("PARTIAL_PRODUCT_CUT_BOUNDARY_INFORMATION = ZERO")
    print("NAIVE_MULTIPLICATIVE_RAIL = CLAUSE_REACTIVATION_REPACKAGING")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
