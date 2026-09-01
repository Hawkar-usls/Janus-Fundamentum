#!/usr/bin/env python3
"""One-index infrastructure carrier for the frozen R8A hard residuals."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import janus_trump_r8a_shard_runner as shard

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--index',type=int,required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    d=shard.run_shard(a.index,16)
    d['schema']='JANUS/TRUMP/R8A/HARD_SINGLETON_EVIDENCE/v1.0'
    d['singleton_index']=a.index
    d['gates'].pop('G1_TWO_FROZEN_INDICES',None)
    d['gates']['G1_ONE_FROZEN_INDEX']=d['summary']['rows']==1 and d['indices']==[a.index]
    Path(a.output).write_text(json.dumps(d,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'index':a.index,'indices':d['indices'],'summary':d['summary'],'gates':d['gates']},indent=2))
    return 0 if all(d['gates'].values()) else 2
if __name__=='__main__': raise SystemExit(main())
