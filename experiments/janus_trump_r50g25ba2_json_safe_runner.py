from __future__ import annotations
import argparse,json
from pathlib import Path
import janus_trump_r50g25ba2_persistent_endpoint_correlation_channel as ba2

def safe(x):
    if isinstance(x,dict):
        return {str(k):safe(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        return [safe(v) for v in x]
    return x

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    r=safe(ba2.run()); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(r,indent=2,sort_keys=True))
    print(json.dumps({'outcome':r['outcome'],'guards':r['source_preimage_realizability_gate'],'falsifiers':r['falsifiers'],'width':r['BA2_10_complexity']['width_upper_bound']},sort_keys=True))
if __name__=='__main__': main()
