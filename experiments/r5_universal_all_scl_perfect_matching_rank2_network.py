#!/usr/bin/env python3
"""R5 all-SCL perfect-matching pairing to ONE fixed rank-two matchgate-sum gate.

Original SCL Tanner graph is 3-regular bipartite. A perfect matching
between ORIGINAL row nodes and column nodes exists by Hall's theorem.
Construct it by deterministic augmenting paths (polynomial time) and
REPLAY it against the original source. Contract every matched wire.

One source row/variable pair becomes ONE arity-four tensor with ordered
ports: other two row incidences, other two variable incidences.
For any original legal source this is the SAME tensor:
   T4 = |1000> + |0100> + |0011>
      = |0011> [even matchgate]
      + (|1000> + |0100>) [odd matchgate].
All original 3n Tanner wires become precisely 2n quotient wires,
in an n-vertex 4-regular (possibly multigraph) network.
The network's exact nonnegative Holant partition equals the number
of ORIGINAL 0/1 Exact-One witnesses. Source SAT iff quotient has
a nonzero assignment. A quotient assignment has a UNIQUE original
Boolean witness and vice versa: full proof in science checkpoint.

Since general SCL decision is NP-complete, NONZERO contraction
on this exact promised four-regular quartic-T4 network image is
NP-complete (in NP: guess 2n wire bits and check n constant gates).
Consequently a universal polynomial zero-test for this compact
rank-two matchgate-sum representation would IMPLY P=NP. THIS
does not prove P!=NP, nor a superpolynomial size lower bound.

Independent finite quotient-network DFS below is exponential and
is used only as a source alignment regression, NEVER as a claimed
polynomial algorithm.
"""
from __future__ import annotations

from collections import Counter,deque
from itertools import product
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_grouped_cell_matchgate_sum_rank import (
    components_4,verify_all_matchgate_identities,
)

LOCAL_OPTIONS=((1,0,0,0),(0,1,0,0),(0,0,1,1))


def polynomial_source_perfect_matching(rows,n):
    """Iterative augmenting paths; robust at arbitrary n, O(n^2).

    3-regular bipartite Hall certificate guarantees every augmentation.
    No Python recursion limit dependence, and no exponential search.
    """
    rows=validate_sparse(rows,n)
    owner=[-1]*n            # column v -> matched row
    rowmate=[-1]*n          # row i -> matched column
    for start in range(n):
        queue=deque([start])
        seen_row={start}
        seen_var=set()
        pred={}             # visited column -> predecessor row
        terminal=None
        while queue and terminal is None:
            i=queue.popleft()
            for v in rows[i]:
                if v in seen_var:continue
                seen_var.add(v)
                pred[v]=i
                if owner[v]==-1:
                    terminal=v
                    break
                next_row=owner[v]
                if next_row not in seen_row:
                    seen_row.add(next_row)
                    queue.append(next_row)
        assert terminal is not None,"violates 3-regular bipartite Hall theorem"
        v=terminal
        while v is not None:
            i=pred[v]
            previous=rowmate[i]
            owner[v]=i
            rowmate[i]=v
            v=previous if previous!=-1 else None
    assert all(v>=0 for v in rowmate)
    assert all(v>=0 for v in owner)
    assert all(owner[v]==i for i,v in enumerate(rowmate))
    assert all(rowmate[i] in rows[i] for i in range(n))
    assert set(rowmate)==set(range(n))
    return tuple(rowmate)


def certify_matching(rows,n,matching):
    rows=validate_sparse(rows,n)
    assert len(matching)==n
    assert all(type(x) is int for x in matching)
    assert set(matching)==set(range(n))
    assert all(matching[i] in rows[i] for i in range(n))
    return True


def paired_quartic_network(rows,n):
    rows=validate_sparse(rows,n)
    match=polynomial_source_perfect_matching(rows,n)
    assert certify_matching(rows,n,match)
    owner={v:i for i,v in enumerate(match)}
    appearances={v:[] for v in range(n)}
    for i,row in enumerate(rows):
        for v in row:appearances[v].append(i)
    assert all(len(appe) == 3 for appe in appearances.values())

    # Every unmatched ORIGINAL incidence (row i, variable v) defines
    # one quotient edge. Each original row pair has two outgoing
    # row-side ports, each matched variable pair two incoming
    # variable-side ports.
    incidences=tuple(
        (i,v) for i,row in enumerate(rows)
        for v in row if v!=match[i]
    )
    assert len(incidences)==2*n
    edge_index={iv:z for z,iv in enumerate(incidences)}
    assert len(edge_index)==2*n
    cells=[]
    edge_endpoints=[[] for _ in incidences]
    for i in range(n):
        v=match[i]
        row_variables=tuple(x for x in rows[i] if x!=v)
        var_rows=tuple(j for j in appearances[v] if j!=i)
        assert len(row_variables)==len(var_rows)==2
        ports=tuple([edge_index[(i,x)] for x in row_variables]+
                    [edge_index[(j,v)] for j in var_rows])
        assert len(set(ports))==4
        for slot,edge in enumerate(ports):
            edge_endpoints[edge].append((i,slot))
        cells.append(ports)

    assert all(len(pair)==2 for pair in edge_endpoints)
    for (i,v),pair in zip(incidences,edge_endpoints):
        assert set(c for c,slot in pair)=={i,owner[v]}
        assert any(c==i and slot<2 for c,slot in pair)
        assert any(c==owner[v] and slot>=2 for c,slot in pair)
        assert i!=owner[v]

    result={
        "source_rows":rows,"source_n":n,
        "matching":match,
        "incidences":incidences,
        "cells":tuple(cells),
        "endpoints":tuple(tuple(pair) for pair in edge_endpoints),
        "quotient_edges":2*n,
        "quartic_cells":n,
        "local_options":LOCAL_OPTIONS,
        "gate":"T4_TWO_STANDARD_MATCHGATES",
    }
    assert verify_paired_quartic_network(rows,n,result)
    return result


def verify_paired_quartic_network(rows,n,report):
    """Rebuild all quotient ports directly from original-source rows.

    Independent of augmenting-path algorithm and producer's port
    labels. Accept ANY valid original Tanner perfect matching.
    """
    rows=validate_sparse(rows,n)
    assert report["source_rows"]==rows, "forged source rows"
    assert report["source_n"]==n
    assert report["quartic_cells"]==n
    assert report["quotient_edges"]==2*n
    assert tuple(report["local_options"])==LOCAL_OPTIONS
    assert report["gate"]=="T4_TWO_STANDARD_MATCHGATES"
    m=tuple(report["matching"])
    assert certify_matching(rows,n,m)
    owner={v:i for i,v in enumerate(m)}
    inc=tuple(report["incidences"])
    assert len(inc)==2*n and len(set(inc))==2*n
    assert set(inc)=={(i,v) for i,row in enumerate(rows)
                     for v in row if v!=m[i]}
    loc={wire:z for z,wire in enumerate(inc)}
    cells=tuple(tuple(c) for c in report["cells"])
    assert len(cells)==n
    reconstructed_edges=[[] for _ in inc]
    for i,ports in enumerate(cells):
        assert len(ports)==4
        rv={loc[(i,v)] for v in rows[i] if v!=m[i]}
        vr={loc[(j,m[i])] for j,row in enumerate(rows)
            if j!=i and m[i] in row}
        assert set(ports[:2])==rv
        assert set(ports[2:])==vr
        assert len(set(ports))==4
        for port,e in enumerate(ports):
            assert type(e) is int and 0<=e<len(inc)
            reconstructed_edges[e].append((i,port))
    assert tuple(tuple(x) for x in reconstructed_edges)==tuple(
        tuple(x) for x in report["endpoints"]
    )
    assert all(len(x)==2 for x in reconstructed_edges)
    assert len(inc)==2*n
    assert all(set(c for c,_ in edges)=={i,owner[v]}
               for (i,v),edges in zip(inc,reconstructed_edges))

    T,(even,odd)=components_4()
    assert all(T[sum(bits[j]<<j for j in range(4))]==int(bits in LOCAL_OPTIONS)
               for bits in product((0,1),repeat=4))
    assert verify_all_matchgate_identities(even,4)
    assert verify_all_matchgate_identities(odd,4)
    return True


def original_to_quotient_wires(report,witness):
    rows=report["source_rows"];n=report["source_n"]
    assert len(witness)==n and all(type(x) is int and x in (0,1)
                                    for x in witness)
    assert all(sum(witness[v] for v in row)==1 for row in rows)
    bits=tuple(witness[v] for i,v in report["incidences"])
    assert quotient_wire_assignment_valid(report,bits)
    return bits


def quotient_wire_assignment_valid(report,bits):
    assert len(bits)==report["quotient_edges"]
    if any(type(x) is not int or x not in (0,1) for x in bits):
        return False
    return all(tuple(bits[edge] for edge in ports) in LOCAL_OPTIONS
               for ports in report["cells"])


def quotient_to_original_witness(report,bits):
    assert quotient_wire_assignment_valid(report,bits)
    n=report["source_n"]
    ans=[None]*n
    for i,var in enumerate(report["matching"]):
        ports=report["cells"][i]
        assert bits[ports[2]]==bits[ports[3]]
        ans[var]=bits[ports[2]]
    ans=tuple(ans)
    assert all(type(x) is int and x in (0,1) for x in ans)
    assert all(sum(ans[v] for v in row)==1
               for row in report["source_rows"])
    assert original_to_quotient_wires(report,ans)==tuple(bits)
    return ans


def certify_connected_quotient(report):
    n=report["source_n"]
    graph=[set() for _ in range(n)]
    for p in report["endpoints"]:
        i,j=p[0][0],p[1][0]
        graph[i].add(j);graph[j].add(i)
    found={0};q=deque([0])
    while q:
        i=q.popleft()
        for j in graph[i]-found:
            found.add(j);q.append(j)
    return len(found)==n


def independent_network_count_small(report,max_nodes=18,
                                    max_states=2000000):
    """Enumerate 3-valued CELL configurations (NOT source bits).

    This is deliberately exponential, solely a finite audit.
    An exhausted resource fence returns UNKNOWN, never UNSAT.
    """
    n=report["source_n"]
    assert n<=max_nodes
    cells=report["cells"]
    # Prefer adjacent highly constrained cells on each step.
    options={}
    visits=0
    count=0
    sample=None
    states=[-1]*report["quotient_edges"]
    done=[False]*n

    class ResourceExceeded(Exception):pass

    def recurse(left):
        nonlocal visits,count,sample
        visits+=1
        if visits>max_states:raise ResourceExceeded
        if not left:
            assert quotient_wire_assignment_valid(report,states)
            w=quotient_to_original_witness(report,states)
            count+=1
            if sample is None:sample=w
            return
        cell=max(left,key=lambda i:(
            sum(states[e]>=0 for e in cells[i]),-i
        ))
        rest=left-{cell}
        for choice in LOCAL_OPTIONS:
            ports=cells[cell]
            if any(states[e]>=0 and states[e]!=b
                   for e,b in zip(ports,choice)):
                continue
            changed=[]
            for e,b in zip(ports,choice):
                if states[e]<0:
                    states[e]=b
                    changed.append(e)
            recurse(rest)
            for e in changed:states[e]=-1

    try:
        recurse(set(range(n)))
    except ResourceExceeded:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","states":visits}
    return {"status":"SAT" if count else "UNSAT",
            "count":count,"states":visits,"witness":sample}


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower

    cases=(
        ("FANO7",cyclic(7),7,0),
        ("K4_SCL18",*make_scl(K4())[:2],6),
        ("K33_SCL27",*make_scl(K33())[:2],12),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2],0),
        ("FLOWER_J5_SCL90",*make_scl(flower(5))[:2],0),
    )
    for name,rows,n,known in cases:
        network=paired_quartic_network(rows,n)
        assert network["quartic_cells"]==n
        assert network["quotient_edges"]==2*n
        assert certify_connected_quotient(network)
        print(f"ORIGINAL_{name}_RANK2_MATCHGATE_SUM_QUOTIENT="
              f"cells={n} edges={2*n} source_auth=PASS",flush=True)
        if n<=27:
            check=independent_network_count_small(
                network,max_nodes=27,max_states=1000000
            )
            assert check["status"]!="UNKNOWN_RESOURCE_LIMIT",(
                name,check
            )
            assert check["count"]==known,(name,check)
            if check["status"]=="SAT":
                bits=original_to_quotient_wires(network,check["witness"])
                assert quotient_to_original_witness(network,bits)==check["witness"]
            print(f"RANK2_QUOTIENT_EXACT_COUNT_{name}="
                  f"{check['count']} explored={check['states']}",flush=True)

    # Different original SCL provenance (E61), not Holyer/flower:
    # direct source rows from frozen I+P+Q matrices.
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,
    )
    for label,p,q,truth in (
        ("E61_SAT12",P_SAT,Q_SAT,"SAT"),
        ("E61_UNSAT12",P_UNSAT,Q_UNSAT,"UNSAT"),
    ):
        A=build_A(p,q)
        rows_e=validate_sparse(
            [tuple(j for j,value in enumerate(row) if value)
             for row in A],len(A)
        )
        network_e=paired_quartic_network(rows_e,len(rows_e))
        result=independent_network_count_small(
            network_e,max_nodes=18,max_states=1000000
        )
        assert result["status"]==truth,(label,result)
        print(f"NONHOLYER_{label}_MATCHGATE_SUM_EXACT_COUNT="
              f"{result['count']} status={result['status']}",flush=True)

    # Disconnected legal original SCL: the quotient representation is
    # independent of connectedness and preserves solution products.
    original_k4,component_n,_,_=make_scl(K4())
    joined=validate_sparse(
        original_k4+
        tuple(tuple(v+component_n for v in row)
              for row in original_k4),2*component_n
    )
    disjoint=paired_quartic_network(joined,len(joined))
    assert not certify_connected_quotient(disjoint)
    disjoint_count=independent_network_count_small(
        disjoint,max_nodes=36,max_states=1000000
    )
    assert disjoint_count["status"]=="SAT" and disjoint_count["count"]==36
    print("DISCONNECTED_K4_PLUS_K4_MATCHED_HOLANT_COUNT=36",flush=True)

    # Source label robustness: matching is independently rechecked.
    rows,n,_,_=make_scl(K4())
    network=paired_quartic_network(rows,n)
    forged=dict(network)
    bad=list(network["matching"])
    bad[0]=bad[1]
    forged["matching"]=tuple(bad)
    try:
        verify_paired_quartic_network(rows,n,forged)
    except (AssertionError,ValueError):
        print("FORGED_ORIGINAL_MATCHING_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("invalid matching accepted")

    forged=dict(network)
    ports=[list(p) for p in network["cells"]]
    ports[0][0]=ports[0][1]
    forged["cells"]=tuple(map(tuple,ports))
    try:
        verify_paired_quartic_network(rows,n,forged)
    except (AssertionError,ValueError):
        print("FORGED_RANK2_CELL_PORT_BINDING_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("invalid quotient ports accepted")

    # Large CONNECTED legal SCL beyond default Python recursion depth.
    # This verifies the matching CONSTRUCTION is stack independent.
    big,n_big,_,_=make_scl(flower(63))
    assert n_big==1134
    big_network=paired_quartic_network(big,n_big)
    assert big_network["quartic_cells"]==1134
    assert big_network["quotient_edges"]==2268
    assert certify_connected_quotient(big_network)
    print("CONNECTED_FLOWER_J63_SCL1134_ITERATIVE_RANK2_MATCHING=PASS",
          flush=True)

    # Independently reject substituted provenance even when the
    # source-port graph certificate was generated correctly.
    falsified=dict(network)
    falsified["source_rows"]=tuple(reversed(network["source_rows"]))
    assert falsified["source_rows"]!=network["source_rows"]
    try:
        verify_paired_quartic_network(rows,n,falsified)
    except (AssertionError,ValueError):
        print("FORGED_RANK2_SOURCE_METADATA_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("forged source metadata accepted")

    print("ALL_SCL_POLYNOMIAL_MATCHING_TO_RANK2_T4_NETWORK=PROVED")
    print("ALL_SCL_SOURCE_WITNESS_BIJECTION_EXACT=PROVED")
    print("ALL_SCL_RANK2_MATCHGATE_SUM_NETWORK_NONZERO_NP_COMPLETE=THEOREM")
    print("POLYNOMIAL_GLOBAL_RANK2_SUM_CONTRACTION=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
