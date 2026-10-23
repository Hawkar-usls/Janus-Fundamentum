#!/usr/bin/env python3
"""Independent receipt checker for BABEL31 exact bounded-frontier #SAT proofs.

NOT a call back into the BABEL31 discovery or leaf DPLL/merge functions.
Leaf tables reconstructed by choosing the UNIQUE true literal of each row,
rather than producer's Boolean-variable-first propagation. Internal merges
independently join full counted signatures over original incidence IDs.
"""
from collections import Counter,defaultdict
from itertools import product


def original_edges(rows):
    n=len(rows)
    return tuple(sorted((r,n+v) for r,row in rows.items() for v in row))


def check_proof(rows,output):
    assert output["status"] in ("SAT","UNSAT")
    certificate=output["receipt"]
    assert certificate["schema"]=="BABEL31/EXACT-BOUNDARY-TABLE-TREE/v1"
    n=len(rows)
    assert certificate["original_rows"]==n
    W=certificate["leaf_vertices"]
    B=certificate["frontier_limit"]
    edges=original_edges(rows)
    assert len(edges)==3*n
    universe=set(range(2*n))

    def frontier(region):
        return tuple(i for i,(r,v) in enumerate(edges)
                     if (r in region)!=(v in region))

    def table_data(node):
        data={}
        for item in node["table"]:
            key=tuple(item["bits"])
            count=item["count"]
            witness=int(item["witness"])
            assert key not in data and len(key)==len(node["frontier"])
            assert count>0 and all(v in (0,1) for v in key)
            data[key]=(count,witness)
        return data

    def independent_leaf(region,boundary):
        variable_nodes={v for v in region if v>=n}
        symbols={("v",v-n) for v in variable_nodes}
        clauses=[]
        for row_id in sorted(v for v in region if v<n):
            clause=[]
            for v in rows[row_id]:
                if n+v in region:
                    symbol=("v",v)
                else:
                    eid=edges.index((row_id,n+v))
                    symbol=("external_port",eid)
                symbols.add(symbol)
                clause.append(symbol)
            assert len(set(clause))==3
            clauses.append(clause)
        # Independent exact-one enumeration: for each row, try each of its
        # three choices as the unique TRUE literal and reject contradictions.
        table=Counter()
        representative={}
        calls=[0]
        def emit(assignment):
            remaining=sorted(symbols-set(assignment))
            for remaining_bits in product((0,1),repeat=len(remaining)):
                full=dict(assignment)
                full.update(zip(remaining,remaining_bits))
                witness=sum(1<<v for v in range(n)
                            if ("v",v) in symbols and full[("v",v)]==1)
                signature=[]
                for eid in boundary:
                    r,varnode=edges[eid]
                    if varnode in region:
                        signature.append(full[("v",varnode-n)])
                    else:
                        signature.append(full[("external_port",eid)])
                signature=tuple(signature)
                table[signature]+=1
                representative.setdefault(signature,witness)
        def visit(i,assigned):
            calls[0]+=1
            if i==len(clauses):
                emit(assigned)
                return
            row=clauses[i]
            for true_slot in range(3):
                next_assignment=assigned.copy()
                for k,symbol in enumerate(row):
                    val=int(k==true_slot)
                    if symbol in next_assignment and next_assignment[symbol]!=val:
                        break
                    next_assignment[symbol]=val
                else:
                    visit(i+1,next_assignment)
        visit(0,{})
        return {bits:(count,representative[bits]) for bits,count in table.items()},calls[0]

    def prove_node(node):
        region=set(node["vertices"])
        assert len(region)==len(node["vertices"]) and region
        assert region<=universe
        boundary=frontier(region)
        assert list(boundary)==node["frontier"]
        assert len(boundary)<=B
        claimed=table_data(node)
        if node["type"]=="leaf":
            assert len(region)<=W
            actual,loc_calls=independent_leaf(region,boundary)
            assert {bits:pair[0] for bits,pair in actual.items()}=={
                bits:pair[0] for bits,pair in claimed.items()}
            kind={"leaves":1,"merges":0,"independent_leaf_choices":loc_calls}
        else:
            assert node["type"]=="merge"
            A,computed_a,stats_a=prove_node(node["left"])
            C,computed_c,stats_c=prove_node(node["right"])
            assert not (A&C)
            assert A|C==region
            side_a=frontier(A)
            side_c=frontier(C)
            ia={eid:i for i,eid in enumerate(side_a)}
            ic={eid:i for i,eid in enumerate(side_c)}
            between=tuple(sorted(set(ia)&set(ic)))
            assert not set(between)&set(boundary)
            recomputed=Counter()
            for ka,(counta,_) in computed_a.items():
                for kc,(countc,_) in computed_c.items():
                    if any(ka[ia[e]]!=kc[ic[e]] for e in between):
                        continue
                    sig=tuple(ka[ia[e]] if e in ia else kc[ic[e]]
                              for e in boundary)
                    recomputed[sig]+=counta*countc
            assert dict(recomputed)=={
                sig:pair[0] for sig,pair in claimed.items()}
            kind={
                "leaves":stats_a["leaves"]+stats_c["leaves"],
                "merges":stats_a["merges"]+stats_c["merges"]+1,
                "independent_leaf_choices":(
                    stats_a["independent_leaf_choices"]+
                    stats_c["independent_leaf_choices"])
            }
        # Validate representative physical assignments for each positive
        # boundary entry using ORIGINAL row incidences (not restored rows).
        allowed_vars={v-n for v in region if v>=n}
        for bits,(count,witness) in claimed.items():
            assert count>0
            assert all(((witness>>v)&1)==0 for v in range(n)
                       if v not in allowed_vars)
            ports=dict(zip(boundary,bits))
            for eid,bit in ports.items():
                r,vnode=edges[eid]
                if vnode in region:
                    assert (witness>>(vnode-n))&1==bit
            for r in (v for v in region if v<n):
                total=0
                for v in rows[r]:
                    if n+v in region:
                        total+=(witness>>v)&1
                    else:
                        eid=edges.index((r,n+v))
                        total+=ports[eid]
                assert total==1,("bad receipt witness",r,total)
        return region,claimed,kind

    regions,table,stats=prove_node(certificate["root"])
    assert regions==universe
    assert set(table).issubset({()})
    exact_count=table.get((),(0,None))[0]
    assert exact_count==output["count"]
    if exact_count:
        model=output["witness"]
        assert model is not None
        assert model==table[()][1]
        assert all(sum((model>>v)&1 for v in row)==1 for row in rows.values())
    else:
        assert output["witness"] is None
    assert output["status"]==("SAT" if exact_count else "UNSAT")
    return {
        "receipt_verification":"PASS",
        "exact_count":exact_count,
        "independent_rows_replayed":n,
        "leaf_width_limit":W,
        "frontier_limit":B,
        "verified_leaves":stats["leaves"],
        "verified_joins":stats["merges"],
        "independent_row_choice_DPLL_nodes":stats["independent_leaf_choices"]
    }
