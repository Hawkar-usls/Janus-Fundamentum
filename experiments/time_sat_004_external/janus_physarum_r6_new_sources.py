#!/usr/bin/env python3
"""R6 source-only CNF manifest. New seeds; preexisting R5 generator, NO scores.

Reusing a generator is NOT a new SAT *family* and is not externally blinded.
Original SHA list is frozen before any model/scorer sees the outcomes.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import janus_juxtapose_r5_new_sources as old
SEEDS=(2026111611,2026111612,2026111613,2026111614)
COUNT=30
SCHEMA="JANUS-PHYSARUM-JUXTAPOSE-R6-120-NEW-SOURCE-SHA-ONLY-V1"
old.SEEDS=SEEDS

def generate(seed,slot):
    if seed not in SEEDS or not 0<=slot<COUNT:
        raise ValueError("not preregistered")
    return old.generate(seed,slot)

def manifest():
    rows=[]
    for seed in SEEDS:
        for slot in range(COUNT):
            f=generate(seed,slot)
            rows.append({k:f[k] for k in ("seed","slot","family","n","source_logical_sha256")})
    if len(rows)!=120 or len({x["source_logical_sha256"] for x in rows})!=120:
        raise AssertionError("not 120 unique SHA frozen sources")
    return {"schema":SCHEMA,"source_origins":"R5 family generator NEW seeds, not new families",
            "source_count":120,"no_labels_no_training":True,"items":rows}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    o=manifest()
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(o,sort_keys=True,indent=2)+"\n")
    print("PHYSARUM_R6_SHA_ONLY="+json.dumps(o,sort_keys=True,separators=(",",":")))
