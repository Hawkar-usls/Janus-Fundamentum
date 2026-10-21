#!/usr/bin/env python3
"""BABEL-19 discover rank-two parity-kernel lifts from different source graphs."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from janus_babel10_degree_scan import frozen_instances
from janus_babel10_lift_family import make_lift
from janus_occam_solver import gf2_kernel,validate
from janus_babel6_transfer import assert_valid_double_cover

def scan(limit=64):
    sources=frozen_instances()
    base_names=[n for n in ("SCL63","SCL126_flip16","SCL126_flip68") if n in sources]
    output=[]
    for name in base_names:
        base=sources[name]
        _,kernel=gf2_kernel(validate(base,len(base)),len(base))
        d=len(kernel)
        counts=Counter()
        examples=[]
        for seed in range(limit):
            lift=make_lift(base,seed)[0]
            assert_valid_double_cover(base,lift)
            _,lbasis=gf2_kernel(validate(lift,len(lift)),len(lift))
            dd=len(lbasis)
            counts[dd-d]+=1
            if dd-d==2:
                sha=hashlib.sha256(json.dumps(lift,separators=(",",":")).encode()).hexdigest()
                examples.append({"seed":seed,"source":name,"source_nullity":d,"cover_nullity":dd,"incidence_sha256":sha})
        record={"source":name,"examined_seeds":limit,"nullity_delta_counts":dict(counts),"rank2_cover_examples":examples}
        output.append(record)
        print("BABEL19_RANK2_SOURCE_SWEEP",json.dumps(record,sort_keys=True)[:15000],flush=True)
    Path("babel19_rank2_source_sweep.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--limit",type=int,default=64);args=p.parse_args();scan(args.limit)
