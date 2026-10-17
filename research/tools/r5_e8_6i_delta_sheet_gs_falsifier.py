#!/usr/bin/env python3
"""Exact GS falsifier for the frozen three-sheet base language Delta_sheet.

Source definition used:
A set of constraints has the guaranteed satisfaction (GS) property iff every
finite subset has a solution.

The frozen base language contains all eight signed threshold-2 ternary
relations M_tau. In particular:

    M_+++ = AT_LEAST_2(x,y,z)
    M_--- = AT_LEAST_2(not x,not y,not z) = AT_MOST_1(x,y,z)

Their conjunction on the same variable triple is unsatisfiable.
No SAT solver is used; all 8 Boolean assignments are replayed explicitly.
"""
from __future__ import annotations
import itertools, json

BITS=(0,1)

def m_plus(x,y,z):
    return int(x+y+z >= 2)

def m_minus(x,y,z):
    return int((1-x)+(1-y)+(1-z) >= 2)

def receipt():
    rows=[]
    simultaneous=[]
    for row in itertools.product(BITS, repeat=3):
        p=m_plus(*row)
        n=m_minus(*row)
        rows.append({
            "assignment": list(row),
            "M_+++": p,
            "M_---": n,
            "both": int(bool(p and n)),
        })
        if p and n:
            simultaneous.append(row)

    assert len(simultaneous)==0

    return {
        "schema":"janus.r5_e8_6i.delta_sheet_gs_falsifier.v1",
        "status":"PASS_EXACT_GS_FALSIFIER",
        "source_definition":"GS iff every finite subset of the constraint set has a solution.",
        "finite_witness":[
            "M_+++(x,y,z)=AT_LEAST_2(x,y,z)",
            "M_---(x,y,z)=AT_LEAST_2(NOT x,NOT y,NOT z)=AT_MOST_1(x,y,z)"
        ],
        "truth_table": rows,
        "common_solutions": len(simultaneous),
        "verdict":"GS(Delta_sheet)=FALSE",
        "firewall":{
            "uses_P_not_equal_NP":False,
            "uses_SAT_oracle":False,
            "source_model_binding":"ALREADY_PROVED",
            "P_VS_NP":"OPEN",
            "D1":"EMPTY"
        }
    }

if __name__=="__main__":
    print(json.dumps(receipt(),indent=2,sort_keys=True))
