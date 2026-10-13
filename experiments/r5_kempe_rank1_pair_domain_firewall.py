#!/usr/bin/env python3
"""R5: rank-one GF4 colour-pair impossibility via LOCAL EDGE DOMAINS.

ALL-SIZE THEOREM. Fix any proper cubic sixpole with six distinct
physical semiport roots, any ordered 6-port tuple s and its Klein-four
flow difference space Z_s (from the fixed-port linear envelope).

If dim Z_s=0, at most one full proper colouring extends s.
If dim Z_s=1, let D be the UNIQUE nonzero candidate difference.
At every vertex, enumerate at most six proper local permutations
of nonzero colours 1,2,3, keeping physical semiedge colours fixed
and demanding c_e != D_e for every internal edge e (this condition is
equivalent to c_e XOR D_e nonzero). Kirchhoff conservation of D then
guarantees that the second local edge tuple is proper too.

For every ordinary edge (u,v), let L_u(e), L_v(e) be the sets of
reference edge colours allowed by these local constraints. If any
edge has L_u(e) intersect L_v(e) = EMPTY, no two distinct full proper
colourings over s can exist. This condition is a sound polynomial
LOCAL certificate; failure to find a conflict is NOT evidence of a pair.

Combine with the previously proved forced Kempe fibre-bijections:
under GLOBAL Bits(M) subset GOOD, all 36 full-colouring fibres of
each realized bit b have the SAME size m_b. If ANY s of bit b has
rank0 OR rank1 with this empty edge-domain intersection, then m_b=1.
Given two distinct full-colouring witnesses over a different good
port tuple t of the same bit, lift a <=4 forced-path route to such s:
some actual pairing must fail, producing an explicit forbidden full
colouring after <=6 real Kempe path switches.

FINITE independent n8 census with reference physical tuple 001212:
  |fibre|  min rank  rank/local capacity-one witness  count
       1         0                         yes         1104
       1         1                         yes          208
       2         0                         yes          112
       2         1                         yes           48

Thus ALL 160 of the 160 n8 labelled proper simple connected reference
configurations with two internal colourings have a rank+local-pair
obstruction to the GLOBAL GOOD-only promise. This is NOT an all-n
Exact-One no-go: high-rank residual graphs remain completely open.

Explicit rank1 witness: n8 edges E48 below, physical reference t=001212
has two full proper colourings. At target s=000202 (b=100), dim Z_s=1,
D=000101110 in 9 edgewise F2^2 codes (entries 0/1). At internal vertex
6 the D-pattern (0,1,1) forces the fixed ordinary edge (4,6) to have
colour code 1, but semiedge root 4 has external colour code 1 and
forces that same ordinary edge to be code 2 or 3. Contradiction.
A real (0,1) Kempe path flip from one input witness exposes forbidden
physical tuple 010212, whose pair-equality bits are 000.
"""
from collections import Counter
from itertools import permutations, product

from r5_kempe_fixed_port_gf4_linear_envelope import linear_envelope, binary_rank
from r5_kempe_min_port_rank_fibre_obstruction import (
    lift_or_forbidden, real_terminal_paths
)
from r5_kempe_sixpole_saturation_or_forbidden_gate import (
    forced_transition_graph, routes_from, parity_states
)
from r5_kempe_coupled_involutions_n8_barrier import (
    bits, GOOD, COLORS, matchings, verify_colouring, is_connected
)
from r5_kempe_physical_fiveloop_gf4_flow_witness import (
    PORTS, REFERENCE_C, fibre_at_fixed_ports,
)

# Small explicit rank-one residual physical witness.
E48 = (
    (2, 3), (4, 6), (5, 7),
    (0, 1), (3, 5), (6, 7),
    (0, 6), (1, 7), (2, 4),
)
E48_SECOND = (0, 0, 0, 2, 1, 2, 1, 1, 2)
TARGET_48 = (0, 0, 0, 2, 0, 2)


def unique_nonzero_difference(rows, edge_count):
    """Full rank-one kernel vector of a binary matrix of 2m columns."""
    pivots = {}
    for r in rows:
        while r:
            j = r.bit_length()-1
            if j in pivots:
                r ^= pivots[j]
            else:
                pivots[j] = r
                break
    free = [j for j in range(2*edge_count) if j not in pivots]
    assert len(free) == 1, ("expected dimension one", len(free))
    vector = 1 << free[0]
    for p in sorted(pivots):
        if (vector & pivots[p]).bit_count() & 1:
            vector |= 1 << p
    assert vector != 0
    assert all((vector & row).bit_count()%2==0 for row in rows)
    return tuple((vector>>(2*i))&3 for i in range(edge_count))


def edge_domain_conflicts(edges, port_tuple, difference):
    """Sufficient certificate that this D cannot join two full proper flows."""
    n = max(max(u,v) for u,v in edges)+1
    assert n == len({v for uv in edges for v in uv})
    inc=[[] for _ in range(n)]
    for k,(u,v) in enumerate(edges):
        inc[u].append(k)
        inc[v].append(k)
    roots=set(range(6))
    assert all(len(inc[v])+(v in roots)==3 for v in range(n))
    domains=[]
    for v in range(n):
        local = {}
        for values in permutations((1,2,3),len(inc[v])):
            if v in roots and (set(values)|{port_tuple[v]+1})!={1,2,3}:
                continue
            if any(difference[e] and values[k] == difference[e]
                   for k,e in enumerate(inc[v])):
                continue
            # The candidate difference is zero-divergence; requiring
            # c XOR D nonzero makes both local colourings proper.
            for k,e in enumerate(inc[v]):
                local.setdefault(e,set()).add(values[k])
        domains.append(local)
    conflict=[]
    for k,(u,v) in enumerate(edges):
        left=domains[u].get(k,set())
        right=domains[v].get(k,set())
        if not left & right:
            conflict.append((k,(u,v),difference[k],
                             tuple(sorted(left)),tuple(sorted(right))))
    return tuple(conflict)


def pair_capacity_one(edges, physical):
    dimension, rows = linear_envelope(
        edges, tuple(range(6)), physical)
    if dimension == 0:
        return ("RANK0", None)
    if dimension == 1:
        difference = unique_nonzero_difference(rows,len(edges))
        conflicts = edge_domain_conflicts(edges,physical,difference)
        if conflicts:
            return ("RANK1_EDGE_CONFLICT", (difference,conflicts))
    return None


def choose_capacity_one_target(edges, bit, source, graph):
    routes=routes_from(source,graph)
    possible=[]
    for physical in parity_states():
        if bits(physical)!=bit:
            continue
        certificate=pair_capacity_one(edges,physical)
        if certificate is not None:
            possible.append((len(routes[physical]),physical,certificate))
    if not possible:
        return None
    return min(possible,key=lambda x:(x[0],x[1]))


def two_witness_forbidden(edges, first, second, ports, graph):
    n=max(max(u,v) for u,v in edges)+1
    assert first!=second and bits(ports) in GOOD
    assert is_connected(n,edges)
    verify_colouring(n,edges,first,ports)
    verify_colouring(n,edges,second,ports)
    target_info=choose_capacity_one_target(edges,bits(ports),ports,graph)
    assert target_info is not None, "conditional pair capacity-1 gate unavailable"
    distance, target, certificate=target_info
    assert distance<=4
    route=routes_from(ports,graph)[target]
    arrivals=[]
    for start in (first,second):
        status,witness,trace=lift_or_forbidden(edges,start,ports,route,graph)
        if status=="FORBIDDEN":
            return target,certificate,witness,trace
        arrivals.append(witness[0])
    assert arrivals[0]!=arrivals[1], "Kempe path reverse uniqueness"
    raise AssertionError("two full arrivals contradict capacity-one certificate")


def test_rank1_witness():
    graph=forced_transition_graph()
    verify_colouring(8,E48,REFERENCE_C,PORTS)
    verify_colouring(8,E48,E48_SECOND,PORTS)
    assert is_connected(8,E48)
    assert len(fibre_at_fixed_ports(E48,PORTS))==2
    assert min(linear_envelope(E48,tuple(range(6)),s)[0]
               for s in parity_states() if bits(s)=="100")==1
    dim,rows=linear_envelope(E48,tuple(range(6)),TARGET_48)
    assert dim==1
    difference=unique_nonzero_difference(rows,9)
    assert difference==(0,0,0,1,0,1,1,1,0)
    conflicts=edge_domain_conflicts(E48,TARGET_48,difference)
    assert (1,(4,6),0,(2,3),(1,)) in conflicts
    target,cert,forbidden,trace=two_witness_forbidden(
        E48,REFERENCE_C,E48_SECOND,PORTS,graph)
    assert target==TARGET_48
    assert cert[0]=="RANK1_EDGE_CONFLICT"
    assert forbidden[1]==(0,1,0,2,1,2)
    assert bits(forbidden[1])=="000"
    print("RANK1_PHYSICAL_EDGE_CONFLICT",conflicts,flush=True)
    print("RANK1_KEMPE_FORBIDDEN",trace,forbidden[1],flush=True)


def test_n8_complete():
    profile=Counter()
    samples=0
    colour_matchings={
        c:list(matchings(tuple(v for v in range(8)
               if v>=6 or PORTS[v]!=c)))
        for c in COLORS
    }
    for m0,m1,m2 in product(*(colour_matchings[c] for c in COLORS)):
        edges=m0+m1+m2
        if len(set(edges))!=9 or not is_connected(8,edges):
            continue
        verify_colouring(8,edges,REFERENCE_C,PORTS)
        actual_fibre_size=len(fibre_at_fixed_ports(edges,PORTS))
        good_states=[s for s in parity_states() if bits(s)=="100"]
        ranks=[linear_envelope(edges,tuple(range(6)),s)[0]
               for s in good_states]
        minimum=min(ranks)
        assert minimum in (0,1) and actual_fibre_size in (1,2)
        has_capacity1=any(pair_capacity_one(edges,s) is not None
                          for s in good_states)
        assert has_capacity1, ("n8 uncaught finite control",edges)
        profile[(actual_fibre_size,minimum)]+=1
        samples+=1
    assert samples==1472
    assert profile==Counter({
        (1,0):1104,(1,1):208,
        (2,0):112,(2,1):48
    }),profile
    print("N8_MINRANK_PLUS_LOCAL_PAIR_CAPACITY_ONE_ALL_1472",dict(sorted(profile.items())),flush=True)
    print("N8_TWO_COLOUR_WITNESSES_160_OF_160_EXCLUDED_AS_GLOBAL_GOOD_ONLY")
    print("ALL_N_CAPACITY_ONE_WITH_TWO_WITNESSES_CONSTRUCTS_FORBIDDEN")
    print("UNIVERSAL_EXACTONE_6POLE_NO_GO=OPEN; SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    test_rank1_witness()
    test_n8_complete()
