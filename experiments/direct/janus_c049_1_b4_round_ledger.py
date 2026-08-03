from __future__ import annotations
import argparse,hashlib,json
from janus_c049_1_b4_round_ledger_core import iterative_compression,exhaustive_prefix_oracle

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def cases():
    return [
      {'id':'many_failures_then_success','d':4,'k':1,'blocks':[[1],[2],[4],[8],[3]]},
      {'id':'no_successful_insertion','d':3,'k':0,'blocks':[[1],[2],[3]]},
      {'id':'small_final_large_cumulative','d':4,'k':1,'blocks':[[1],[2],[4],[8],[3],[12]]},
      {'id':'noncanonical_bases','d':4,'k':2,'blocks':[[3,1],[6,2],[12,4]]},
      {'id':'work_refusal','d':4,'k':1,'blocks':[[1],[2],[4],[8],[3]],'work_cap':3},
    ]
def build():
    records=[]
    for c in cases():
        result=iterative_compression(c['blocks'],c['d'],c['k'],c.get('work_cap',10**9))
        raw=exhaustive_prefix_oracle(c['blocks'],c['d'],c['k'])
        oracle={ell:{'good_count':len(g),'good_layouts_digest':digest(g)} for ell,g in raw.items()}
        item={'case':c,'result':result,'oracle':oracle}; item['case_digest']=digest(item); records.append(item)
    ctrl={'id':'partition_loss','expected_blocks':2,'presented_blocks':4,'terminal':'REJECTED','reason':'grouped factor partition lost'}; ctrl['case_digest']=digest(ctrl)
    art={'artifact_id':'C049.1-B4-ROUND-LEDGER','records':records,'controls':[ctrl]}; art['artifact_digest']=digest(art); return art
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); a=build(); open(ap.parse_args().output,'w').write(json.dumps(a,indent=2,sort_keys=True)+'\n')
