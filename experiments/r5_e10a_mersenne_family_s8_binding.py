#!/usr/bin/env python3
"""Algebraic side-check for NM-0021 family-wide S8 binding.

The two matroid structure implications are source-bound theorem inputs.
This checker verifies the exact family parameters and the elementary
graphic/cographic contradictions used to exclude regularity.
"""
from __future__ import annotations
import json

def cert(L: int) -> dict:
    assert L >= 7
    m = L*L + 1
    r = L*L - L + 1
    rdual = L

    # If M_L were graphic and connected, a representing graph would have
    # n=r+1 non-isolated vertices. 3n-2m>0 forces average degree <3, hence
    # a nonempty cut of size <=2, contradicting cogirth(M_L)=4.
    graphic_slack = 3*(r+1) - 2*m
    assert graphic_slack == L*L - 3*L + 4
    assert graphic_slack > 0

    # If M_L were cographic then M_L* would be a simple graphic matroid
    # of rank L, hence represented by a simple graph on L+1 vertices.
    # Its edge count cannot exceed C(L+1,2).
    cographic_surplus2 = 2*m - L*(L+1)
    assert cographic_surplus2 == L*L - L + 2
    assert cographic_surplus2 > 0

    assert m > 10
    return {
        "L": L,
        "elements": m,
        "rank": r,
        "dual_rank": rdual,
        "graphic_average_degree_slack_3n_minus_2m": graphic_slack,
        "cographic_twice_edge_surplus": cographic_surplus2,
    }

# Representative Mersenne sizes; the proof for all L>=7 is algebraic.
samples=[cert((1<<k)-1) for k in range(3,9)]

out={
    "status":"PASS_MERSENNE_FAMILY_S8_BINDING_ALGEBRAIC_SIDE_CHECK",
    "source_theorem_inputs":[
        "binary 3-connected S8-free => regular or F7 or F7* or AG(3,2)",
        "internally 4-connected regular => graphic or cographic or R10",
    ],
    "janus_inputs":[
        "M_L binary",
        "M_L 3-connected",
        "M_L has no exact 3-separation",
        "cogirth(M_L)=4",
        "M_L* simple",
        "|E(M_L)|=L^2+1",
        "r(M_L)=L^2-L+1",
        "r(M_L*)=L",
    ],
    "derived":[
        "M_L internally 4-connected",
        "M_L not graphic",
        "M_L not cographic",
        "M_L not R10 by size",
        "M_L nonregular",
        "M_L has an S8 minor",
    ],
    "scope":{
        "L":"2^k-1, k>=3",
        "binding":"EXISTENCE_THEOREM_NOT_UNIFORM_COORDINATE_EXTRACTION",
        "P_VS_NP":"OPEN",
        "P_EQ_NP":"NOT_PROVED",
    },
    "samples":samples,
}
print(json.dumps(out,sort_keys=True))
