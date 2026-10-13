#!/usr/bin/env python3
"""R5 all-size uniform-fibre/minimum-GF4-rank obstruction and certificate.

THEOREM (no all-size Exact-One exclusion):
For a connected simple cubic sixpole with six DISTINCT physical roots,
let b be one of {100,010,001}. For every ordered six-port colour tuple s
of bit b, build over F2 the zero-divergence difference space Z_s with
the boundary-root constraints from r5_kempe_fixed_port_gf4_linear_envelope.

If the FULL physical boundary bit relation is subset of GOOD, the
previously proven forced-Kempe 36-state path-bijections imply a common
nonzero fibre size m_b, and for each s every colour in that fibre
injects into Z_s relative to any fixed reference colouring. Therefore

    m_b <= 2**r_b,   r_b = min_{s:bits(s)=b} dim_F2 Z_s .

The finite minimum of 36 ranks is polynomial-time computable from the
UNCOLOURED graph (no reference colouring needed). In particular,
r_b=0 => m_b=1 and EVERY forced-loop monodromy on that bit is trivial.

CONSTRUCTIVE VIOLATION:
Given two different full proper colourings with the SAME physical
allowed bit-b tuple t and a rank-zero tuple s of the SAME bit,
a forbidden full colouring can be found in polynomial time:
select a length<=4 forced-Kempe route t->s; try to lift it from both
input colourings; if an actual two-colour path pairing deviates from
the uniquely GOOD-safe pairing, switching <=3 disjoint actual paths
produces a forbidden state. If both paths lift, they give two distinct
full colourings over s, which contradicts dim Z_s=0. Thus one must fail.

FINITE n8 REPRODUCTION (fixed starting tuple 001212):
  fibre 1, r_b 0: 1104
  fibre 1, r_b 1:  208
  fibre 2, r_b 0:  112  (rank-witness obstruction applies)
  fibre 2, r_b 1:   48  (not resolved by this rank condition)

This does not decide whether any gadget exists. All-n Exact-One no-go,
unbounded native PC degree and a universal SCL solver remain OPEN.
"""
from collections import Counter
from itertools import product

from r5_kempe_coupled_involutions_n8_barrier import (
    COLORS, GOOD, bits, matchings, kempe_moves, verify_colouring,
    is_connected
)
from r5_kempe_sixpole_saturation_or_forbidden_gate import (
    forced_transition_graph, routes_from, parity_states
)
from r5_kempe_fixed_port_gf4_linear_envelope import linear_envelope
from r5_kempe_physical_fiveloop_gf4_flow_witness import (
    PORTS, REFERENCE_C, WITNESS_EDGES, WITNESS_AFTER,
    GIRTH6_EDGES, GIRTH6_AFTER, fibre_at_fixed_ports
)


def minimum_rank_same_bit(edges, ports, bit, start=None, graph=None):
    assert len(ports) == 6
    candidates = (s for s in parity_states() if bits(s) == bit)
    values = [(linear_envelope(edges, tuple(range(6)), s)[0], s)
              for s in candidates]
    assert len(values) == 36
    if start is not None:
        assert graph is not None and bits(start) == bit
        routes = routes_from(start, graph)
        assert len(routes) == 36
        return min(values, key=lambda item: (
            item[0], len(routes[item[1]]), item[1]))
    return min(values)


def real_terminal_paths(edges, ec, ports, pair):
    """Actual labelled disjoint path flips, one per pair of port ends."""
    n = max(max(u,v) for u,v in edges) + 1
    proper = kempe_moves(n, edges, ec, ports)
    result = {}
    for new_ec, new_ports, colour_pair, ends in proper:
        if colour_pair == pair and len(ends) == 2:
            assert ends not in result
            result[ends] = (new_ec, new_ports)
    assert len(result) <= 3
    actual_ports = {k for ends in result for k in ends}
    required = {i for i, c in enumerate(ports) if c in pair}
    assert actual_ports == required, (actual_ports, required)
    return result


def switch_subset(edges, ec, ports, pair, selected_ends):
    for ends in selected_ends:
        ec, ports = real_terminal_paths(edges, ec, ports, pair)[ends]
    return ec, ports


def lift_or_forbidden(edges, ec, ports, path, graph):
    """Lift a prescribed forced route or return full forbidden witness."""
    trace = []
    for pair, required_ends, desired_ports in path:
        actual = real_terminal_paths(edges, ec, ports, pair)
        canonical = {ends for _, colour_pair, ends in graph[ports]
                     if colour_pair == pair}
        if set(actual) != canonical:
            available = sorted(actual)
            for mask in range(1, 1 << len(available)):
                subset = [ends for j, ends in enumerate(available)
                          if mask & (1 << j)]
                bad_ec, bad_ports = switch_subset(
                    edges, ec, ports, pair, subset
                )
                if bits(bad_ports) not in GOOD:
                    n = max(max(u,v) for u,v in edges) + 1
                    verify_colouring(n, edges, bad_ec, bad_ports)
                    trace.append(("FORBIDDEN", pair, tuple(subset), bad_ports))
                    return "FORBIDDEN", (bad_ec, bad_ports), trace
            raise AssertionError("GOOD-unique matching lemma contradicted")
        ec, ports = actual[required_ends]
        assert ports == desired_ports
        trace.append(("FORCED", pair, required_ends, ports))
    return "LIFTED", (ec, ports), trace


def rank_zero_forbidden_certificate(edges, a, b, ports, graph):
    """Find full bad witness from 2 distinct full colourings and rank0."""
    assert a != b and bits(ports) in GOOD
    n = max(max(u,v) for u,v in edges) + 1
    assert n == len({v for uv in edges for v in uv})
    assert is_connected(n, edges)
    verify_colouring(n, edges, a, ports)
    verify_colouring(n, edges, b, ports)
    rank, target = minimum_rank_same_bit(
        edges, ports, bits(ports), start=ports, graph=graph)
    assert rank == 0, ("rank-zero precondition unavailable", rank)
    path = routes_from(ports, graph)[target]
    assert len(path) <= 4
    full_outputs = []
    for ec in (a, b):
        kind, witness, trace = lift_or_forbidden(
            edges, ec, ports, path, graph
        )
        if kind == "FORBIDDEN":
            assert bits(witness[1]) not in GOOD
            return target, witness, trace
        full_outputs.append(witness[0])
    # Each prescribed Kempe flip is invertible on FULL colourings,
    # so the two lifted full colourings must be different.
    assert full_outputs[0] != full_outputs[1]
    # Rank0 says there can be at most one full colouring over target:
    raise AssertionError("impossible: two different liftings into rank0 fibre")


def n8_census():
    cases = Counter()
    colour_matchings = {
        c: list(matchings(tuple(v for v in range(8)
                 if v >= 6 or PORTS[v] != c)))
        for c in COLORS
    }
    assert all(len(p) == 15 for p in colour_matchings.values())
    for m0,m1,m2 in product(*(colour_matchings[c] for c in COLORS)):
        edges = m0+m1+m2
        if len(set(edges)) != 9 or not is_connected(8, edges):
            continue
        verify_colouring(8, edges, REFERENCE_C, PORTS)
        fibre_size = len(fibre_at_fixed_ports(edges, PORTS))
        assert fibre_size in (1, 2)
        rank, _ = minimum_rank_same_bit(edges, PORTS, "100")
        assert rank in (0, 1)
        cases[(fibre_size, rank)] += 1
    assert cases == Counter({
        (1,0):1104, (1,1):208,
        (2,0):112, (2,1):48
    }), cases
    assert sum(cases.values()) == 1472
    print("N8_COMPLETE_FIBRE_MIN_RANK_PROFILE", dict(sorted(cases.items())),
          flush=True)
    return cases


def run():
    graph = forced_transition_graph()
    for name, edges, second in (
        ("FOURCYCLE", WITNESS_EDGES, WITNESS_AFTER),
        ("GIRTH6", GIRTH6_EDGES, GIRTH6_AFTER),
    ):
        minimum, target = minimum_rank_same_bit(edges, PORTS, "100")
        assert minimum == 0
        target, forbidden, trace = rank_zero_forbidden_certificate(
            edges, REFERENCE_C, second, PORTS, graph
        )
        assert target == (0,0,1,2,2,1)
        assert forbidden[1] == (0,0,2,2,2,2)
        assert bits(forbidden[1]) == "111"
        assert len(trace) <= 6
        print("RANK_ZERO_TO_REAL_FORBIDDEN", name, {
            "rank_at_target":minimum,
            "target":target, "forbidden_ports":forbidden[1],
            "actual_flip_trace":trace
        }, flush=True)
    profile = n8_census()
    assert profile[(2,0)] == 112 and profile[(2,1)] == 48
    print("THEOREM: ALL_SIZE_GOOD_ONLY_IMPLIES_m_b_LE_2_POWER_MIN_PORT_RANK")
    print("RANK_ZERO_WITH_TWO_SAME_BOUNDARY_COLOURINGS_FORCES_BAD_WITNESS")
    print("UNIVERSAL_EXACTONE_6POLE_NO_GO=OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    run()
