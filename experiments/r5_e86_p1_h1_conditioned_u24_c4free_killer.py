#!/usr/bin/env python3
"""R5 E86: p=1,h=1 conditioned-U2,4 C4-free killer for t<=2.

E85 reduced every hypothetical nonbinary linear RXC3 interface to a four-port
conditioned residual network.  The smallest genuinely new minor-only lane is

    p = 1 variable-side survivor port,
    q = 3 check-side survivor ports,
    h = 1 retained check-side zero hole.

The E85 equations force

    a = 3t+1 active checks,
    b = 3t   active variables,

and every one of the six U2,4-twist states selects exactly t variables.

E86 closes the first two sizes of this lane.

t=1:
  a=4,b=3.  Internal variable degrees are [2,3,3], so there are 8 internal
  incidences.  C4-freeness allows each pair of the three variables to share at
  most one check, hence the total pair-intersection count is at most 3.
  But every possible positive check-degree pattern summing to 8 with degrees
  <=3 has sum C(d_i,2) >=4.  Therefore a C4-free residual incidence graph
  cannot exist at all.

t=2:
  a=7,b=6.  Fix the unique degree-2 variable as variable 0; the other five
  variables have degree 3.  There are two complete check-degree cases:

    hole overlaps a survivor check:
      [1,2,2,3,3,3,3]

    hole lies on a distinct check:
      [2,2,2,2,3,3,3]

  A backtracking generator exhausts every normalized bipartite incidence matrix
  with those degree sequences and pairwise variable-neighborhood intersections
  <=1 (exact Tanner C4-freeness).  Counts are 1,440 and 17,280 graphs.

For each of the 18,720 graphs, all four possible choices of which raw
check-boundary coordinate is pinned to zero are tested: 74,880 pin
configurations total.  None yields the p=1 conditioned U2,4-twist relation

    {0001,0010,0100,1011,1101,1110}

(up to the frozen boundary ordering used by the checker).

Thus p=1,h=1 conditioned U2,4 is impossible for t<=2 under C4-freeness.
The first open size in this lane is t=3, i.e. a=10,b=9.

P_VS_NP remains OPEN.
"""

from itertools import combinations

from r5_e83_canonical_matroid_twist_u24_frontier import generic_boundary_relation
from r5_e85_conditioned_u24_minor_normal_form import project_pin

TARGET_P1 = frozenset({1,2,4,11,13,14})

EXPECTED_GRAPH_COUNTS = {
    "overlap": 1440,
    "distinct": 17280,
}
EXPECTED_TOTAL_GRAPHS = 18720
EXPECTED_TOTAL_PINS = 74880


def choose2(x):
    return x*(x-1)//2


def verify_t1_c4_counting_obstruction():
    # Three variables have internal degrees 2,3,3.  If the Tanner graph is
    # C4-free, each of the three variable pairs shares at most one check.
    max_pair_intersections = choose2(3)

    patterns=set()
    for d0 in range(1,4):
        for d1 in range(1,4):
            for d2 in range(1,4):
                for d3 in range(1,4):
                    ds=tuple(sorted((d0,d1,d2,d3)))
                    if sum(ds)==8:
                        patterns.add(ds)

    assert patterns
    for ds in patterns:
        pair_intersections=sum(choose2(d) for d in ds)
        assert pair_intersections > max_pair_intersections

    return tuple(sorted(patterns))


def generate_c4free_incidence(check_caps, variable_degrees):
    """Generate every normalized incidence matrix with exact degrees.

    Variables are processed in frozen order.  C4-freeness is exactly the
    requirement that any two variable neighborhoods intersect in at most one
    check.
    """
    caps=list(check_caps)
    neighborhoods=[]

    def rec(j):
        if j == len(variable_degrees):
            if all(c==0 for c in caps):
                yield tuple(neighborhoods)
            return

        d=variable_degrees[j]
        available=[i for i,c in enumerate(caps) if c>0]
        for N in combinations(available,d):
            Ns=set(N)
            if any(len(Ns & set(P)) >= 2 for P in neighborhoods):
                continue

            for i in N:
                caps[i]-=1
            neighborhoods.append(tuple(N))

            remaining=variable_degrees[j+1:]
            remaining_count=len(remaining)
            if (
                sum(caps) == sum(remaining)
                and all(c <= remaining_count for c in caps)
            ):
                yield from rec(j+1)

            neighborhoods.pop()
            for i in N:
                caps[i]+=1

    yield from rec(0)


def neighborhoods_to_edges(neighborhoods):
    return {
        (i,j)
        for j,N in enumerate(neighborhoods)
        for i in N
    }


def verify_t2_complete_census():
    variable_degrees=(2,3,3,3,3,3)
    cases={
        "overlap": (1,2,2,3,3,3,3),
        "distinct": (2,2,2,2,3,3,3),
    }

    graph_counts={}
    pin_count=0
    conditioned_u24_hits=0

    for name,check_degrees in cases.items():
        count=0
        for neighborhoods in generate_c4free_incidence(
            check_degrees, variable_degrees
        ):
            count += 1
            edges=neighborhoods_to_edges(neighborhoods)

            arity,check_boundary,family=generic_boundary_relation(7,6,edges)
            assert arity == 5
            assert check_boundary == 4

            # All four raw check-side boundary coordinates are candidates for
            # the unique retained zero hole.  The other three survive free.
            for e in range(4):
                pin_count += 1
                conditioned=project_pin(family,5,e,0)
                if conditioned == TARGET_P1:
                    conditioned_u24_hits += 1

        graph_counts[name]=count
        assert count == EXPECTED_GRAPH_COUNTS[name]

    assert sum(graph_counts.values()) == EXPECTED_TOTAL_GRAPHS
    assert pin_count == EXPECTED_TOTAL_PINS
    assert conditioned_u24_hits == 0
    return graph_counts,pin_count


def main():
    patterns=verify_t1_c4_counting_obstruction()
    graph_counts,pins=verify_t2_complete_census()

    print("R5 E86 p=1,h=1 conditioned-U2,4 C4-free killer: PASS")
    print("t=1 impossible by pair-intersection count; check-degree patterns:", patterns)
    print("t=2 complete normalized C4-free graph counts:", graph_counts)
    print("t=2 zero-hole pin configurations tested:", pins)
    print("conditioned p=1 U2,4 hits=0")
    print("p=1,h=1 excluded for t<=2; first open size t=3 => 10 checks / 9 variables")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
