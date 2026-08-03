#!/usr/bin/env python3
from __future__ import annotations
from typing import Any
from janus_c047_affine_trellis_core import *

def independent_layout(ordered,dimension,meter):
    prefix=[()]
    for f in ordered:
        meter.charge("prefix_span",max(1,len(f["equations"])))
        prefix.append(span(prefix[-1],tuple(m for m,_ in f["equations"]),dimension=dimension))
    suffix=[() for _ in range(len(ordered)+1)]
    for i in range(len(ordered)-1,-1,-1):
        meter.charge("suffix_span",max(1,len(ordered[i]["equations"])))
        suffix[i]=span(tuple(m for m,_ in ordered[i]["equations"]),suffix[i+1],dimension=dimension)
    boundaries=[]; widths=[]
    for i in range(len(ordered)+1):
        meter.charge("cut_intersection",max(1,len(prefix[i])+len(suffix[i])))
        b=intersection(prefix[i],suffix[i],dimension)
        boundaries.append(b); widths.append(len(b))
        meter.max_width=max(meter.max_width,len(b))
    return prefix,boundaries,widths

def reconstruct(
    factors:list[dict[str,Any]],dimension:int,cap:Capability
)->dict[str,Any]:
    normalized=normalize_factors(factors,dimension)
    meter=Meter(cap)
    base={
        "schema":SCHEMA,
        "dimension":dimension,
        "input_factors":[
            {"factor_id":f["factor_id"],"equations":[list(x) for x in f["equations"]],
             "input_position":f["input_position"]}
            for f in normalized
        ],
        "capability":cap.manifest(),
        "p_vs_np":"OPEN",
    }
    try:
        meter.charge("order_discovery",max(1,len(normalized)))
        order=deterministic_order(normalized)
        ordered=[normalized[i] for i in order]
        factor_order=[f["factor_id"] for f in ordered]
        prefix,boundaries,widths=independent_layout(ordered,dimension,meter)
        for cut,w in enumerate(widths):
            if w>cap.width_limit:
                body={
                    **base,"status":OPEN_CUT_WIDTH,
                    "reason":"DETERMINISTIC_ORDER_EXCEEDS_WIDTH_CAP",
                    "order_policy":"PARALLEL_BLOCKS_FIRST_OCCURRENCE",
                    "factor_order":factor_order,"cut_widths":widths,
                    "first_overflow_cut":cut,
                    "overflow_boundary":list(boundaries[cut]),
                    "overflow_width":w,
                }
                body["producer_ledger"]=meter.snapshot()
                body["integrity_sha256"]=digest(body)
                return body

        reachable={0:((),0,None)}
        layers=[{"cut":0,"boundary_basis":list(boundaries[0]),
                 "reachable_states":[0],
                 "records":{"0":{"prefix_basis":[],"prefix_values":0,"parent":None}}}]
        for t,f in enumerate(ordered,1):
            pb=boundaries[t-1]; cb=boundaries[t]
            W=tuple(m for m,_ in f["equations"])
            nxt={}; transitions=[]
            for ps in sorted(reachable):
                prev_basis,prev_values,_=reachable[ps]
                for cs in range(1<<len(cb)):
                    meter.transition_tests+=1
                    meter.charge("transition_test",max(1,len(pb)+len(cb)+len(W)))
                    local=extend_avoiding(pb,ps,cb,cs,f["equations"],dimension)
                    if local is None:
                        transitions.append({"from":ps,"to":cs,"status":"BLOCKED"})
                        continue
                    transitions.append({
                        "from":ps,"to":cs,"status":"OPEN_EDGE",
                        "local_basis":local["local_basis"],
                        "local_values":local["local_values"],
                        "factor_values":local["factor_values"],
                        "separating_row":local["separating_row"],
                    })
                    if cs in nxt: continue
                    total,vals=combine_functionals(prev_basis,prev_values,W,local["factor_values"],dimension)
                    if restrict_functional(total,vals,cb)!=cs:
                        raise AssertionError("independent current-state mismatch")
                    parent={"previous_state":ps,"factor_id":f["factor_id"],
                            "factor_values":local["factor_values"],
                            "separating_row":local["separating_row"]}
                    nxt[cs]=(total,vals,parent)
            reachable=nxt
            meter.states_materialized+=len(reachable)
            layers.append({
                "cut":t,"factor_id":f["factor_id"],"boundary_basis":list(cb),
                "reachable_states":sorted(reachable),
                "records":{
                    str(s):{"prefix_basis":list(v[0]),"prefix_values":v[1],"parent":v[2]}
                    for s,v in sorted(reachable.items())
                },
                "transition_records":transitions,
            })
        body={**base,"order_policy":"PARALLEL_BLOCKS_FIRST_OCCURRENCE",
              "factor_order":factor_order,"cut_widths":widths,
              "boundaries":[list(b) for b in boundaries],"layers":layers}
        if 0 not in reachable:
            body.update({"status":"UNSAT","reason":"ROOT_FUNCTIONAL_SET_EMPTY",
                         "root_reachable_states":[]})
        else:
            rb,rv,_=reachable[0]
            point=solve_point(rb,rv,dimension)
            if point is None or any(point_in_factor(point,f["equations"]) for f in normalized):
                raise AssertionError("independent witness failed")
            body.update({"status":"SAT","reason":"ROOT_FUNCTIONAL_EXISTS",
                         "root_reachable_states":[0],"ambient_witness":str(point),
                         "witness_bits":[(point>>i)&1 for i in range(dimension)],
                         "root_normal_basis":list(rb),"root_functional_values":rv})
        return fixed_point_certificate(body,cap,meter)
    except OpenResult as err:
        body={**base,"status":err.status,"reason":err.stage,
              "overflow_evidence":err.evidence,"producer_ledger":meter.snapshot()}
        body["integrity_sha256"]=digest(body)
        return body

def verify(factors:list[dict[str,Any]],dimension:int,certificate:dict[str,Any])->bool:
    try:
        if certificate.get("schema")!=SCHEMA: return False
        integrity=certificate.get("integrity_sha256")
        body=dict(certificate); body.pop("integrity_sha256",None)
        if integrity!=digest(body): return False
        m=certificate["capability"]
        cap=Capability(
            int(m["input_length"]),int(m["requested_width_cap"]),
            None if m["work_cap"] is None else int(m["work_cap"]),
            None if m["certificate_cap"] is None else int(m["certificate_cap"]),
        )
        normalized=normalize_factors(factors,dimension)
        if cap.input_length!=input_length(normalized,dimension): return False
        expected=reconstruct(factors,dimension,cap)
        return expected==certificate
    except (KeyError,TypeError,ValueError,AssertionError):
        return False
