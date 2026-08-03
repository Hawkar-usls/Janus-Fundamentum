#!/usr/bin/env python3
from __future__ import annotations
from typing import Any
from janus_c047_affine_trellis_core import *

def precompute_layout(ordered:list[dict[str,Any]],dimension:int,meter:Meter):
    m=len(ordered)
    prefix=[()]
    for f in ordered:
        meter.charge("prefix_span",max(1,len(f["equations"])))
        prefix.append(span(prefix[-1],tuple(mask for mask,_ in f["equations"]),dimension=dimension))
    suffix=[() for _ in range(m+1)]
    for i in range(m-1,-1,-1):
        meter.charge("suffix_span",max(1,len(ordered[i]["equations"])))
        suffix[i]=span(tuple(mask for mask,_ in ordered[i]["equations"]),suffix[i+1],dimension=dimension)
    boundaries=[]
    widths=[]
    for i in range(m+1):
        meter.charge("cut_intersection",max(1,len(prefix[i])+len(suffix[i])))
        b=intersection(prefix[i],suffix[i],dimension)
        boundaries.append(b); widths.append(len(b))
        meter.max_width=max(meter.max_width,len(b))
    return prefix,suffix,boundaries,widths

def compile_trellis(
    factors:list[dict[str,Any]],
    dimension:int,
    *,
    requested_width_cap:int=3,
    work_cap:int|None=None,
    certificate_cap:int|None=None,
)->dict[str,Any]:
    normalized=normalize_factors(factors,dimension)
    L=input_length(normalized,dimension)
    cap=Capability(L,requested_width_cap,work_cap,certificate_cap)
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
        order_payload=[f["factor_id"] for f in ordered]
        prefix,suffix,boundaries,widths=precompute_layout(ordered,dimension,meter)
        for cut,w in enumerate(widths):
            if w>cap.width_limit:
                body={
                    **base,
                    "status":OPEN_CUT_WIDTH,
                    "reason":"DETERMINISTIC_ORDER_EXCEEDS_WIDTH_CAP",
                    "order_policy":"PARALLEL_BLOCKS_FIRST_OCCURRENCE",
                    "factor_order":order_payload,
                    "cut_widths":widths,
                    "first_overflow_cut":cut,
                    "overflow_boundary":list(boundaries[cut]),
                    "overflow_width":w,
                }
                body["producer_ledger"]=meter.snapshot()
                body["integrity_sha256"]=digest(body)
                return body

        reachable={0:{"prefix_basis":(),"prefix_values":0,"parent":None}}
        layers=[{
            "cut":0,
            "boundary_basis":list(boundaries[0]),
            "reachable_states":[0],
            "records":{"0":{"prefix_basis":[],"prefix_values":0,"parent":None}},
        }]
        for t,f in enumerate(ordered,1):
            prev_boundary=boundaries[t-1]
            current_boundary=boundaries[t]
            normal_basis=tuple(mask for mask,_ in f["equations"])
            next_reachable={}
            transition_records=[]
            for prev_state in sorted(reachable):
                prev_record=reachable[prev_state]
                for current_state in range(1<<len(current_boundary)):
                    meter.transition_tests+=1
                    meter.charge("transition_test",max(1,len(prev_boundary)+len(current_boundary)+len(normal_basis)))
                    local=extend_avoiding(
                        prev_boundary,prev_state,current_boundary,current_state,
                        f["equations"],dimension)
                    if local is None:
                        transition_records.append({
                            "from":prev_state,"to":current_state,"status":"BLOCKED"
                        })
                        continue
                    transition_records.append({
                        "from":prev_state,"to":current_state,"status":"OPEN_EDGE",
                        "local_basis":local["local_basis"],
                        "local_values":local["local_values"],
                        "factor_values":local["factor_values"],
                        "separating_row":local["separating_row"],
                    })
                    if current_state in next_reachable:
                        continue
                    combined_basis,combined_values=combine_functionals(
                        tuple(prev_record["prefix_basis"]),int(prev_record["prefix_values"]),
                        normal_basis,int(local["factor_values"]),dimension)
                    if restrict_functional(combined_basis,combined_values,current_boundary)!=current_state:
                        raise AssertionError("combined prefix misses current state")
                    next_reachable[current_state]={
                        "prefix_basis":combined_basis,
                        "prefix_values":combined_values,
                        "parent":{
                            "previous_state":prev_state,
                            "factor_id":f["factor_id"],
                            "factor_values":local["factor_values"],
                            "separating_row":local["separating_row"],
                        },
                    }
            reachable=next_reachable
            meter.states_materialized+=len(reachable)
            layer_records={
                str(s):{
                    "prefix_basis":list(r["prefix_basis"]),
                    "prefix_values":r["prefix_values"],
                    "parent":r["parent"],
                } for s,r in sorted(reachable.items())
            }
            layers.append({
                "cut":t,
                "factor_id":f["factor_id"],
                "boundary_basis":list(current_boundary),
                "reachable_states":sorted(reachable),
                "records":layer_records,
                "transition_records":transition_records,
            })

        body={
            **base,
            "order_policy":"PARALLEL_BLOCKS_FIRST_OCCURRENCE",
            "factor_order":order_payload,
            "cut_widths":widths,
            "boundaries":[list(b) for b in boundaries],
            "layers":layers,
        }
        if 0 not in reachable:
            body.update({
                "status":"UNSAT",
                "reason":"ROOT_FUNCTIONAL_SET_EMPTY",
                "root_reachable_states":[],
            })
        else:
            root=reachable[0]
            point=solve_point(tuple(root["prefix_basis"]),int(root["prefix_values"]),dimension)
            if point is None:
                raise AssertionError("root functional failed to lift")
            if any(point_in_factor(point,f["equations"]) for f in normalized):
                raise AssertionError("lifted point lies in forbidden factor")
            body.update({
                "status":"SAT",
                "reason":"ROOT_FUNCTIONAL_EXISTS",
                "root_reachable_states":[0],
                "ambient_witness":str(point),
                "witness_bits":[(point>>i)&1 for i in range(dimension)],
                "root_normal_basis":list(root["prefix_basis"]),
                "root_functional_values":root["prefix_values"],
            })
        return fixed_point_certificate(body,cap,meter)
    except OpenResult as err:
        body={
            **base,
            "status":err.status,
            "reason":err.stage,
            "overflow_evidence":err.evidence,
            "producer_ledger":meter.snapshot(),
        }
        body["integrity_sha256"]=digest(body)
        return body
