#!/usr/bin/env python3
"""R5 E87: p=1,h=1 residual-exchange-graph killer at t=3.

E86 excluded the smallest conditioned-U2,4 lane p=1,h=1 for t<=2.
E87 derives and exhausts the correct reference-cover residual normal form for

    t=3:
      a=10 active checks,
      b=9 active variables.

Choose one of the six target states with
  * variable survivor bit = 1,
  * two check survivor bits = 1,
  * the third check survivor bit = 0.

If the zero hole overlaps a survivor check, choose the reference state so the
overlapped survivor is one of the two boundary-1 checks.

The reference cover selects t=3 variables:
  * the unique boundary variable, with two internal checks;
  * two ordinary cubic variables, with three checks each.

The other 2t=6 variables are residual.  Removing the reference-cover variables
turns the ten checks into:
  * eight ordinary residual edges between residual variables;
  * two residual half-edges.

Every residual variable has degree 3 counting half-edges.  Tanner C4-freeness
makes the ordinary residual graph simple.  Each selected reference-cover
variable induces a matching block among check-objects, so the ten checks split
as:
  * two externally satisfied distinguished checks A,B;
  * one size-2 matching block for the boundary variable;
  * two unordered size-3 matching blocks for the other selected variables.

Two cases are exhaustive:
  overlap : second half-edge is external check A;
  distinct: second half-edge is the pinned-zero hole H.

The checker fixes the half-edge C of the third survivor check at residual
vertex 0 (without loss by residual relabeling), enumerates all complete simple
ordinary graphs compatible with residual degree 3, then every admissible
matching partition and boundary role.

Frozen complete counts:
  residual graphs = 300
  overlap configurations = 6,600
  distinct configurations = 103,800
  total configurations = 110,400
  conditioned p=1 U2,4 hits = 0.

A direct brute-force ExactOne/Equality evaluator is also cross-checked against
the residual semantics on the first 100 deterministic configurations.

Therefore p=1,h=1 conditioned U2,4 is excluded through t=3.  The first open
size in this lane is t=4 (13 checks / 12 variables).

P_VS_NP remains OPEN.
"""

from itertools import combinations
from collections import Counter

TARGET = frozenset({1,2,4,11,13,14})

EXPECTED_RESIDUAL_GRAPHS = 300
EXPECTED_CONFIG_COUNTS = {
    "overlap": 6600,
    "distinct": 103800,
}
EXPECTED_TOTAL_CONFIGS = 110400
EXPECTED_CROSSCHECKS = 100


def is_matching(block, endpoints):
    used=set()
    for obj in block:
        for v in endpoints[obj]:
            if v in used:
                return False
            used.add(v)
    return True


def matching_partitions_2_3_3(objects, endpoints):
    """Distinguished size-2 block + two unordered size-3 blocks."""
    objects=tuple(objects)
    for xblock in combinations(objects,2):
        if not is_matching(xblock,endpoints):
            continue
        rem=[o for o in objects if o not in xblock]
        first=rem[0]
        for extra in combinations(rem[1:],2):
            core0=(first,)+extra
            if not is_matching(core0,endpoints):
                continue
            core1=tuple(o for o in rem if o not in core0)
            if not is_matching(core1,endpoints):
                continue
            yield tuple(xblock),tuple(core0),tuple(core1)


def residual_graphs_t3():
    """All normalized simple 8-edge + 2-half-edge residual graphs on 6 vertices.

    Half-edge C is fixed at vertex 0 by residual-vertex relabeling.  The second
    half-edge endpoint is allowed to be any of the six vertices, including 0.
    Ordinary degrees are exactly 3 minus incident half-edge multiplicity.
    """
    n=6
    all_edges=tuple(combinations(range(n),2))
    C_ENDPOINT=0

    for t_endpoint in range(n):
        half_count=[0]*n
        half_count[C_ENDPOINT]+=1
        half_count[t_endpoint]+=1
        target_degree=[3-h for h in half_count]

        for edges in combinations(all_edges,8):
            degree=[0]*n
            for u,v in edges:
                degree[u]+=1
                degree[v]+=1
            if degree == target_degree:
                yield t_endpoint,tuple(edges)


def independent_sets(n, ordinary_edges):
    for S in range(1<<n):
        if any(((S>>u)&1) and ((S>>v)&1) for u,v in ordinary_edges.values()):
            continue
        yield S


def residual_family(n, ordinary_edges, C, T, case, A, B, blocks, endpoints):
    """Exact four-port family from the reference-cover residual semantics."""
    family=set()

    for S in independent_sets(n,ordinary_edges):
        cross={
            obj: sum((S>>v)&1 for v in ends)
            for obj,ends in endpoints.items()
        }
        assert all(z in (0,1) for z in cross.values())

        A_bit=1-cross[A]
        B_bit=1-cross[B]

        # x-block selection z0 equals the variable-side survivor bit.
        for z0 in (0,1):
            for z1 in (0,1):
                for z2 in (0,1):
                    zs=(z0,z1,z2)
                    C_bit=None
                    ok=True

                    for bi,block in enumerate(blocks):
                        z=zs[bi]
                        for obj in block:
                            total=z+cross[obj]

                            if case=="distinct" and obj==T:
                                # The second half-edge is the fixed-zero hole.
                                if total != 1:
                                    ok=False
                                    break
                            elif obj==C:
                                # Third survivor check: its boundary bit fills
                                # exactly the remaining ExactOne demand.
                                bit=1-total
                                if bit not in (0,1):
                                    ok=False
                                    break
                                C_bit=bit
                            else:
                                if total != 1:
                                    ok=False
                                    break
                        if not ok:
                            break

                    if ok:
                        assert C_bit is not None
                        v_bit=z0
                        mask=A_bit | (B_bit<<1) | (C_bit<<2) | (v_bit<<3)
                        family.add(mask)

    return frozenset(family)


def brute_family(n, ordinary_edges, C, T, case, A, B, blocks, endpoints):
    """Independent direct ExactOne/Equality replay on 6+3 variables."""
    block_of={}
    for bi,block in enumerate(blocks):
        for obj in block:
            block_of[obj]=bi

    objects=tuple(ordinary_edges)+ (C,T)
    family=set()

    # Variables 0..5 are residual; 6=x, 7/8=the two core reference vars.
    for ymask in range(1<<9):
        ok=True
        A_bit=B_bit=C_bit=None

        for obj in objects:
            selected=sum((ymask>>v)&1 for v in endpoints[obj])
            if obj in block_of:
                selected += (ymask>>(6+block_of[obj]))&1

            if obj==A:
                bit=1-selected
                if bit not in (0,1):
                    ok=False
                    break
                A_bit=bit
            elif obj==B:
                bit=1-selected
                if bit not in (0,1):
                    ok=False
                    break
                B_bit=bit
            elif obj==C:
                bit=1-selected
                if bit not in (0,1):
                    ok=False
                    break
                C_bit=bit
            elif case=="distinct" and obj==T:
                # Pinned-zero check hole.
                if selected != 1:
                    ok=False
                    break
            else:
                if selected != 1:
                    ok=False
                    break

        if ok:
            v_bit=(ymask>>6)&1
            family.add(A_bit | (B_bit<<1) | (C_bit<<2) | (v_bit<<3))

    return frozenset(family)


def main():
    residual_graph_count=0
    config_counts=Counter()
    target_hits=0
    crosschecks=0

    for t_endpoint,edge_tuple in residual_graphs_t3():
        residual_graph_count += 1

        ordinary_edges={i:e for i,e in enumerate(edge_tuple)}
        C=8
        T=9
        endpoints={
            **{i:e for i,e in ordinary_edges.items()},
            C:(0,),
            T:(t_endpoint,),
        }

        # OVERLAP: T is the external survivor check A carrying both
        # the free boundary port and the zero hole. B is an ordinary edge.
        for B in range(8):
            block_objects=[i for i in range(8) if i!=B] + [C]
            for blocks in matching_partitions_2_3_3(block_objects,endpoints):
                config_counts["overlap"] += 1
                fam=residual_family(
                    6,ordinary_edges,C,T,"overlap",T,B,blocks,endpoints
                )
                if fam == TARGET:
                    target_hits += 1

                if crosschecks < EXPECTED_CROSSCHECKS:
                    brute=brute_family(
                        6,ordinary_edges,C,T,"overlap",T,B,blocks,endpoints
                    )
                    assert brute == fam
                    crosschecks += 1

        # DISTINCT: C and T=H are both block members. A,B are ordered
        # distinct ordinary external checks.
        for A in range(8):
            for B in range(8):
                if A==B:
                    continue
                block_objects=[
                    i for i in range(8)
                    if i not in (A,B)
                ] + [C,T]
                for blocks in matching_partitions_2_3_3(
                    block_objects,endpoints
                ):
                    config_counts["distinct"] += 1
                    fam=residual_family(
                        6,ordinary_edges,C,T,"distinct",A,B,blocks,endpoints
                    )
                    if fam == TARGET:
                        target_hits += 1

                    if crosschecks < EXPECTED_CROSSCHECKS:
                        brute=brute_family(
                            6,ordinary_edges,C,T,"distinct",A,B,blocks,endpoints
                        )
                        assert brute == fam
                        crosschecks += 1

    assert residual_graph_count == EXPECTED_RESIDUAL_GRAPHS
    assert dict(config_counts) == EXPECTED_CONFIG_COUNTS
    assert sum(config_counts.values()) == EXPECTED_TOTAL_CONFIGS
    assert target_hits == 0
    assert crosschecks == EXPECTED_CROSSCHECKS

    print("R5 E87 p=1,h=1 residual-exchange-graph killer t=3: PASS")
    print("normalized residual graphs:", residual_graph_count)
    print("configuration counts:", dict(config_counts))
    print("total configurations:", sum(config_counts.values()))
    print("direct semantic crosschecks:", crosschecks)
    print("conditioned p=1 U2,4 hits=0")
    print("p=1,h=1 excluded through t=3; first open size t=4 => 13 checks / 12 variables")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
