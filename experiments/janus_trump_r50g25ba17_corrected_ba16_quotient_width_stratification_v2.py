from __future__ import annotations

import argparse

import janus_trump_r50g25ba17_corrected_ba16_quotient_width_stratification as ba17


def fixed_full_composition_certificate(U,g,p,n,r,stage):
    act=ba17.actual_ba4_stage(U,g,p,n,r,stage)
    nodes_full,edges_full=ba17.primal_graph(act["full_clauses"])
    qcert=ba17.stage_certificate(stage,p,n,r)
    qbags=qcert["upper_decomposition"]["bags"]
    qtree=qcert["upper_decomposition"]["tree_edges"]

    allbags={}
    tree=[]
    for k,b in qbags.items():
        allbags[f"Q:{k}"]=[str(act["qs"][act["logical_labels"].index(v)]) for v in b]
    tree += [[f"Q:{a}",f"Q:{b}"] for a,b in qtree]

    # Every BA4 lane remains an internal carrier component even after its
    # semantic quotient vertex has been eliminated. Active lanes attach to a
    # quotient bag containing their q endpoint. Inactive lanes have no
    # cross-lane clauses at this stage and therefore are disconnected carrier
    # components; their decomposition may be joined to any existing bag by a
    # tree edge without changing running intersection or width.
    base,_lv,_=ba17.ba4.build_instance(U,g,p+n+r+3)
    active_labels=set(ba17.stage_nodes(stage,p,n,r))
    global_root=next(iter(allbags)) if allbags else None

    for i,vs in enumerate(act["lane_vars"]):
        lc=[c for c in base if all(abs(int(x)) in vs for x in c)]
        ln,le=ba17.primal_graph(lc)
        lo=ba17.ba4.lane_off(g,i)
        order=[]
        for block in range(g):
            order += [str(int(v)+lo+ba17.ba4.BLOCK_STRIDE*block) for v in ba17.ba4.az.ORDER]
        d=ba17.decomp_from_order(ln,le,order)
        prefix=f"L{i}:"
        for k,b in d["bags"].items():
            allbags[prefix+k]=b
        tree += [[prefix+a,prefix+b] for a,b in d["tree_edges"]]

        q=str(act["qs"][i])
        localbag=next(prefix+k for k,b in d["bags"].items() if q in set(b))
        logical=act["logical_labels"][i]
        if logical in active_labels:
            qbag=next("Q:"+k for k,b in qbags.items() if logical in set(b))
            tree.append([localbag,qbag])
        else:
            if global_root is None:
                global_root=localbag
            else:
                tree.append([localbag,global_root])

    actual_width=max(len(set(b))-1 for b in allbags.values())
    cert={"bags":allbags,"tree_edges":tree,"width":actual_width}
    valid=ba17.validate_decomp(nodes_full,edges_full,cert)
    bound=max(13,qcert["claimed_treewidth"])
    return {
        "g":g,"p":p,"n":n,"r":r,"stage":stage,
        "quotient_exact":act["quotient_exact"],
        "all_lanes_connected":act["all_lanes_connected"],
        "quotient_width":qcert["claimed_treewidth"],
        "full_lower_bound":qcert["claimed_treewidth"],
        "full_upper_bound":bound,
        "actual_constructed_decomposition_width":actual_width,
        "decomposition_valid":valid,
        "inactive_lane_gluing":"DISCONNECTED_COMPONENT_TO_ARBITRARY_ROOT_BAG",
        "pass":act["quotient_exact"] and act["all_lanes_connected"] and valid and actual_width<=bound
    }


ba17.full_composition_certificate=fixed_full_composition_certificate


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="JANUS_TRUMP_R50G25BA17_RESULT.json")
    args=ap.parse_args()
    ba17.main(args.out)
