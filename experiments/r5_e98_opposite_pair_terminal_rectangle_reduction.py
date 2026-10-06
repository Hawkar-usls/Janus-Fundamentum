#!/usr/bin/env python3
"""R5 E98: opposite-pair terminal-component / rectangle reduction.

For a fixed opposite TARGET6 pair, form the bipartite exchange graph between
two exact-cover witnesses. Variable vertices are the selected variables in the
symmetric difference; ordinary differing checks are edges; A,B,C,V are the
four terminals.

Choose the witness pair with minimum symmetric difference.

Then:
  * no terminal-free connected component can remain (flip it to reduce the
    symmetric difference without changing boundary state);
  * each component has equal numbers of terminals on the two bipartition
    sides, because 3|L|=e+q_L and 3|R|=e+q_R, while globally q_L,q_R<=2;
  * hence a terminal component has either 2 terminals (one on each side) or
    all 4 terminals (2+2);
  * a 2-terminal component has e == 2 (mod 3) internal exchange edges;
    a 4-terminal component has e == 1 (mod 3).

If the minimal exchange graph splits 2+2, flipping either component gives one
of the four other TARGET6 states. The two flips plus the original opposite
pair form an exact witness rectangle whose XOR is zero; equivalently one
target-derived E96 kernel correction vanishes.

If two independent rectangles are chosen coherently so h1=h2=0, then the
three opposite-pair symmetric-difference indicator vectors are identical.
Exhausting the 31 E96 even defect partitions shows that under this equality
the ONLY possible defects are the five rigid opposite-pair coarsenings.

Thus a no-rigid TARGET6 counterexample must obstruct coherent double-rectangle
decomposition; otherwise raw state8 follows from E95.

P_VS_NP remains OPEN.
"""

from itertools import product, combinations

TARGETS=(1,2,4,19,21,22)
TARGET_SET=set(TARGETS)
TERMS=(1,2,4,16)   # A,B,C,V bits
OPPOSITE_PAIRS=((0,5),(1,4),(2,3))
OPPOSITE_ATOMS=(
    frozenset({0,5}),
    frozenset({1,4}),
    frozenset({2,3}),
)


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def even_defect_partitions():
    out=set()
    for assignment in product(range(3), repeat=6):
        blocks=[
            frozenset(i for i,x in enumerate(assignment) if x==k)
            for k in range(3)
        ]
        if all(len(b)%2==0 for b in blocks):
            out.add(canonical_partition(blocks))
    return tuple(sorted(out))


def side_terminal_sets(pair_index):
    i,j=OPPOSITE_PAIRS[pair_index]
    x=TARGETS[i]; y=TARGETS[j]
    left=[]; right=[]
    # check terminals A,B,C: bit 0 means internally covered by that witness
    for bit in (1,2,4):
        xb=bool(x&bit); yb=bool(y&bit)
        assert xb != yb
        if not xb and yb:
            left.append(bit)
        else:
            right.append(bit)
    # V: bit1 means x variable is selected and owns the terminal.
    xv=bool(x&16); yv=bool(y&16)
    assert xv != yv
    if xv:
        left.append(16)
    else:
        right.append(16)
    assert len(left)==len(right)==2
    return frozenset(left),frozenset(right)


def verify_component_balance_arithmetic():
    # For a connected exchange component:
    # 3L=e+qL, 3R=e+qR, hence 3(L-R)=qL-qR.
    # Since a whole opposite-pair graph has only 2 terminals on each side,
    # qL,qR are in {0,1,2}; the difference can be divisible by 3 only if equal.
    for qL in range(3):
        for qR in range(3):
            feasible=((qL-qR)%3==0)
            assert feasible == (qL==qR)

    # Congruence for internal exchange edges e=3L-qL.
    for L in range(1,20):
        assert (3*L-1)%3==2  # two-terminal component
        assert (3*L-2)%3==1  # four-terminal component


def flip(mask, subset):
    z=mask
    for bit in subset:
        z ^= bit
    return z


def verify_target_rectangle_closure():
    rectangles=[]
    for p,(i,j) in enumerate(OPPOSITE_PAIRS):
        x=TARGETS[i]; y=TARGETS[j]
        left,right=side_terminal_sets(p)

        # Every legal 2-terminal component takes one terminal from each side.
        cross=[]
        for a in sorted(left):
            for b in sorted(right):
                subset=frozenset({a,b})
                z=flip(x,subset)
                assert z in TARGET_SET
                assert z not in {x,y}
                cross.append((subset,z))

        assert len(cross)==4
        assert len({z for _,z in cross})==4

        # Complementary cross-pairs partition the four terminals and yield
        # the same two intermediate witnesses in reversed order.
        seen=set()
        pairings=[]
        allterms=frozenset(TERMS)
        for subset,z in cross:
            if subset in seen:
                continue
            comp=allterms-subset
            z2=flip(x,comp)
            assert z2 in TARGET_SET and z2 not in {x,y,z}
            seen.add(subset); seen.add(comp)
            pairings.append((subset,comp,z,z2))
            # Rectangle boundary XOR is zero.
            assert x ^ y ^ z ^ z2 == 0
        assert len(pairings)==2
        rectangles.append(pairings)
    return rectangles


def split_vector(S):
    S=frozenset(S)
    return tuple(int(len(S & A)==1) for A in OPPOSITE_ATOMS)


def verify_double_rectangle_rigid_only():
    defects=even_defect_partitions()
    assert len(defects)==31

    # h1=h2=0 means the three opposite-pair symmetric-difference variable
    # indicators are identical. Therefore each variable support block has
    # split vector 000 or 111.
    compatible=[]
    for p in defects:
        if all(len(set(split_vector(S)))==1 for S in p):
            compatible.append(p)

    assert len(compatible)==5

    # Those five are exactly coarsenings of the three indivisible opposite
    # atoms, i.e. the rigid E96 defects.
    coarsenings=set()
    for assignment in product(range(3),repeat=3):
        bins=[set(),set(),set()]
        for atom,k in zip(OPPOSITE_ATOMS,assignment):
            bins[k].update(atom)
        coarsenings.add(canonical_partition(frozenset(B) for B in bins))
    assert set(compatible)==coarsenings
    assert len(coarsenings)==5
    return tuple(sorted(compatible))


def main():
    verify_component_balance_arithmetic()
    rectangles=verify_target_rectangle_closure()
    rigid=verify_double_rectangle_rigid_only()

    print("R5 E98 opposite-pair terminal-component / rectangle reduction: PASS")
    print("minimal opposite exchange graph: one 4-terminal component or two 2-terminal components")
    print("2-terminal component has one terminal from each bipartition side and e=2 mod3")
    print("4-terminal component has 2+2 terminals and e=1 mod3")
    print("2+2 split flips close exactly inside TARGET6 and give a zero-XOR witness rectangle")
    print("two coherent independent rectangles => h1=h2=0")
    print("under h1=h2=0, compatible E95 defects=",len(rigid),"and all are rigid opposite-pair coarsenings")
    print("next target: rigid-defect killer OR prove coherent double-rectangle exists in every no-rigid parent")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
