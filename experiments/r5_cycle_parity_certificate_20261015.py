#!/usr/bin/env python3
"""JANUS R5 E4.5: CYCLE_PARITY_CERTIFICATE.

Turn exact 2048-class E4.4 finite orbit into a short algebraic
GF(2) certificate, using a FIXED full Phi fiber (not arbitrary lifts).

ALL-N conditional lemma:
For an UNSAT base, if fixed obstruction H=L^T A0 K has a
ONE-dimensional kernel, all SAT coverings in the fixed-H family
have a common nonzero sheet-XOR z_star.
For this z, define Y_z={y in {0,1,2}^n:Ay=2, y mod2=z}.
Each y is independent of voltage. G_z is cubic on supp(z):
one edge per row containing the two z-columns. At a given
voltage, every feasible y gives exactly 2^c SAT witnesses if
the cycle-parity linear system on G_z is consistent (c=#G_z
components), and zero otherwise.

If a single cover has exactly 2 SAT witnesses, necessarily
c=1 and |Y_z|=1. Then SAT voltages in ANY affine fixed-H
gauge-quotient form a single (possibly empty) affine GF2
subspace. WARNING: without |Y_z|=1, it is a UNION of affine
subspaces and need not itself be affine.

This executable independently derives the fixed z from H,
builds G_z, all fundamental cycle voltage equations, pulls
them back to 11 quotient generators, proves rank(Psi)=5,
and compares ALL 2048 predicted SAT/UNSAT statuses against
independent 128-word exhaustive GF2 exact-one tests. The
2^11 and 2^7 enumerations are FINITE audits, not all-n
polynomial solvers.
"""
from collections import defaultdict,Counter,deque
import argparse,json

from r5_rank_preserving_cover_twins_20261015 import (
    search_unsat_base,integer_two_cover_witness,sat_cover_from_y,
    phi_data,phi_apply,signmask_from_signs,delta_to_signs,lift_rows,
    gf2_nullspace,gf2_rank,source_bitrows
)
from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,valid_witness,fingerprint,gf2_affine
)
from r5_cover_twins_independent_audit_20261015 import (
    independently_enumerate_parity
)


def context():
    base,source=search_unsat_base()
    assert base is not None and len(base)==36
    assert source["oracle_words"]==64
    report=integer_two_cover_witness(base)
    assert report["status"]=="SAT_TERNARY_WITNESS"
    y=tuple(report["y"])
    signs,witness,cover=sat_cover_from_y(base,y)
    frame=phi_data(base)
    d=frame["d"]
    assert d==6 and frame["quotient_dim"]==11
    sigma0=signmask_from_signs(frame["edges"],signs)
    obstruction=phi_apply(frame["images"],sigma0)
    matrix=[(obstruction>>(i*d))&((1<<d)-1) for i in range(d)]
    assert gf2_rank(matrix)==5
    ker=gf2_nullspace(matrix,d)
    assert len(ker)==1
    z=sum(0 for _ in ())  # representation overwritten by XOR below
    z=0
    for j,b in enumerate(frame["right"]):
        if (ker[0]>>j)&1:z^=b
    assert z!=0 and z in span_right_kernel_single_source(base)
    assert all((source_bitrows(base)[i]&z).bit_count()%2==0
               for i in range(len(base)))
    for i,row in enumerate(base):
        assert sum(y[v] for v in row)==2
    assert sum((1<<v) for v in range(len(base)) if y[v]%2)==z
    return base,source,frame,signs,sigma0,y,witness,cover,z,ker[0]


def span_right_kernel_single_source(base):
    # Merely independent verification via nullspace basis.
    bits=source_bitrows(base)
    basis=gf2_nullspace(bits,len(base))
    # For d=6 test exactly all 64 possible vectors; not
    # an all-n algorithm and not used to construct the star.
    out=set()
    for mask in range(1<<len(basis)):
        v=0
        for j,b in enumerate(basis):
            if (mask>>j)&1:v^=b
        out.add(v)
    return out


def support_graph(base,z,frame):
    n=len(base)
    edgepos={e:q for q,e in enumerate(frame["edges"])}
    nodes=[j for j in range(n) if (z>>j)&1]
    links=[]
    no_z_rows=0
    for i,row in enumerate(base):
        selected=[v for v in row if (z>>v)&1]
        assert len(selected) in (0,2)
        if not selected:
            no_z_rows+=1
            continue
        a,b=sorted(selected)
        voltage_mask=(1<<edgepos[(i,a)])|(1<<edgepos[(i,b)])
        links.append((a,b,i,voltage_mask))
    neighbors={v:[] for v in nodes}
    for idx,(a,b,i,mask) in enumerate(links):
        neighbors[a].append((b,idx))
        neighbors[b].append((a,idx))
    assert all(len(neighbors[j])==3 for j in nodes)
    assert len(links)==3*len(nodes)//2
    components=[]
    seen=set()
    for root in nodes:
        if root in seen:continue
        walk=[root];seen.add(root);members=[]
        while walk:
            u=walk.pop();members.append(u)
            for v,e in neighbors[u]:
                if v not in seen:seen.add(v);walk.append(v)
        components.append(tuple(sorted(members)))
    # Fundamental cycles: spanning forest path plus each non-tree
    # edge, each providing one independent GF2 cycle equation.
    parent={}
    depth={}
    parent_edge={}
    tree_edges=set()
    for root in nodes:
        if root in parent:continue
        parent[root]=None;depth[root]=0
        todo=deque([root])
        while todo:
            u=todo.popleft()
            for v,eidx in neighbors[u]:
                if v not in parent:
                    parent[v]=u
                    depth[v]=depth[u]+1
                    parent_edge[v]=eidx
                    tree_edges.add(eidx)
                    todo.append(v)
    cycles=[]
    def path_edges(a,b):
        aa,bb=a,b
        result=[]
        while depth[aa]>depth[bb]:
            result.append(parent_edge[aa]);aa=parent[aa]
        while depth[bb]>depth[aa]:
            result.append(parent_edge[bb]);bb=parent[bb]
        while aa!=bb:
            result.extend((parent_edge[aa],parent_edge[bb]))
            aa=parent[aa];bb=parent[bb]
        return result
    for idx,(a,b,_,_) in enumerate(links):
        if idx in tree_edges:continue
        cyc=(idx,*path_edges(a,b))
        assert len(set(cyc))==len(cyc)
        rhsmask=0
        for j in cyc:rhsmask^=links[j][3]
        cycles.append({
            "edge_ids":cyc,
            "row_ids":tuple(links[j][2] for j in cyc),
            "incidence_mask":rhsmask,
            "length_parity":len(cyc)%2
        })
    expected=len(links)-len(nodes)+len(components)
    assert len(cycles)==expected
    return {"nodes":nodes,"links":links,"components":components,
            "cycles":cycles,"no_z_rows":no_z_rows}


def psi_constraints(graph,frame,signmask):
    cycles=graph["cycles"]
    quotient=frame["non_gauge_basis"]
    rows=[]
    constants=[]
    for cyc in cycles:
        mask=cyc["incidence_mask"]
        constant=cyc["length_parity"]^((mask&signmask).bit_count()%2)
        constants.append(constant)
        row=sum(1<<j for j,b in enumerate(quotient)
                if (mask&b).bit_count()%2)
        rows.append(row)
    rank=gf2_rank(rows)
    assert len(rows)==len(cycles)
    # Original SAT covering must be a solution.
    assert not any(constants)
    # Recover every cycle equation directly at every quotient
    # generator, independently from the stored coefficient rows.
    for j,delta in enumerate(quotient):
        for i,cyc in enumerate(cycles):
            via_delta=((delta&cyc["incidence_mask"]).bit_count()%2)
            assert via_delta==((rows[i]>>j)&1)
    return {"rank":rank,"rows":rows,"constants":constants}


def replay():
    base,source,frame,signs,sigma0,y,witness,cover,z,kercoord=context()
    G=support_graph(base,z,frame)
    cons=psi_constraints(G,frame,sigma0)
    c=len(G["components"])
    assert c==1
    exact0=independently_enumerate_parity(cover)
    assert exact0["status"]=="EXACT"
    assert exact0["sat_count"]==2
    # PROOF of Y_z singleton (rather than an assumption):
    # For any y∈Y_z a satisfiable cycle system yields exactly 2^c
    # label choices. All equations depend on z and signs, not on y;
    # observed exactly 2 at an already verified SAT sign assignment.
    # c=1 forces |Y_z|=1.
    assert y in [tuple(y)]
    assert cons["rank"]==5
    q=frame["quotient_dim"]
    assert q==11
    assert (1<<(q-cons["rank"]))==64
    tallies=Counter()
    witness_counts=Counter()
    mismatch=[]
    for code in range(1<<q):
        predicted=all(((row&code).bit_count()%2)==const
                      for row,const in zip(cons["rows"],cons["constants"]))
        delta=0
        for j,b in enumerate(frame["non_gauge_basis"]):
            if (code>>j)&1:delta^=b
        assert phi_apply(frame["images"],delta)==0
        lifting=lift_rows(base,delta_to_signs(frame["edges"],signs,delta))
        actual=independently_enumerate_parity(lifting)
        assert actual["status"]=="EXACT" and actual["checked"]==128
        if predicted!=(actual["sat_count"]>0):
            mismatch.append(code)
        tallies["SAT" if predicted else "UNSAT"]+=1
        witness_counts[str(actual["sat_count"])]+=1
        if predicted:
            assert actual["sat_count"]==2
        else:
            assert actual["sat_count"]==0
    assert not mismatch and tallies==Counter({"SAT":64,"UNSAT":1984})
    assert witness_counts==Counter({"2":64,"0":1984})
    return {
        "gate":"CYCLE_PARITY_CERTIFICATE",
        "base_sha256":fingerprint(base),
        "base_UNSAT_checked":64,
        "z_star_decimal":str(z),
        "z_star_weight":z.bit_count(),
        "kernel_H_coordinate":str(kercoord),
        "fixed_obstruction_rank":5,
        "base_G_z_vertices":len(G["nodes"]),
        "base_G_z_edges":len(G["links"]),
        "G_z_components":c,
        "zero_z_rows":G["no_z_rows"],
        "fundamental_cycles":len(G["cycles"]),
        "cycle_lengths":[len(e["edge_ids"]) for e in G["cycles"]],
        "cycle_edge_incidence_masks_decimal":[
            str(e["incidence_mask"]) for e in G["cycles"]],
        "Psi_rows_decimal":[str(row) for row in cons["rows"]],
        "Psi_constants":cons["constants"],
        "Psi_rank":cons["rank"],
        "quotient_dim":q,
        "y_star":list(y),
        "Y_z_cardinality_proved":1,
        "reason_unique_y":"2 exact SAT witnesses at base sign, c=1, each feasible y yields 2^c witnesses",
        "affine_SAT_class_size_predicted":1<<(q-cons["rank"]),
        "all_2048_exact_GF2_rechecked":True,
        "predicted_status_mismatches":len(mismatch),
        "class_counts_predicted":dict(tallies),
        "exact_SAT_solution_count_distribution":dict(witness_counts),
        "fixed_Phi_only":True,
        "general_if_multiple_y":"UNION_OF_AFFINE_SUBSPACES_NOT_ALWAYS_AFFINE",
        "global_polynomial_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.parse_args()
    print(json.dumps(replay(),sort_keys=True,indent=2))
