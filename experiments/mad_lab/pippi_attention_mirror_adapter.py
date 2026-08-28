#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA='JANUS/PIPPI/SPIDER-ATTENTION-MIRROR/v1.0.0'
P_VS_NP='OPEN'

def stable_hash(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]

def enrich(mirror,attention_rows):
    edges=[x for x in attention_rows if x.get('kind')=='EDGE_ATTENTION']
    nodes=[x for x in attention_rows if x.get('kind')=='NODE_ATTENTION']
    focus=[x for x in nodes if x.get('focus_state') in {'PRIMARY_FOCUS','ACTIVE_FOCUS'}]
    focus=sorted(focus,key=lambda x:(x.get('focus_rank',10**9),-float(x.get('attention_score',0))))
    stale=sorted([x for x in edges if x.get('attention_movement')=='SATURATED_REPLAY_DECAY' or (int(x.get('replay_streak') or 0)>=4 and float(x.get('attention_delta',0) or 0)<0)],key=lambda x:(-int(x.get('replay_streak') or 0),float(x.get('attention_weight',0))))
    rising=sorted([x for x in edges if float(x.get('attention_delta',0) or 0)>0],key=lambda x:-float(x.get('attention_delta',0)))
    out=dict(mirror)
    out['spider_attention_ecology']={
      'schema':SCHEMA,'P_VS_NP':P_VS_NP,'attention_rows':len(attention_rows),'edge_attention_rows':len(edges),'node_attention_rows':len(nodes),
      'focus_centers':[{'node_id':x.get('node_id'),'focus_rank':x.get('focus_rank'),'focus_state':x.get('focus_state'),'attention_score':x.get('attention_score'),'attention_delta':x.get('attention_delta'),'focus_age':x.get('focus_age'),'spiral_ring_trace':x.get('spiral_ring_trace',[])} for x in focus[:10]],
      'rising_patterns':[{'edge_key':x.get('edge_key'),'attention_weight':x.get('attention_weight'),'attention_delta':x.get('attention_delta'),'replay_streak':x.get('replay_streak'),'fresh_evidence_signature':x.get('fresh_evidence_signature')} for x in rising[:20]],
      'stale_or_saturated_patterns':[{'edge_key':x.get('edge_key'),'attention_weight':x.get('attention_weight'),'attention_delta':x.get('attention_delta'),'replay_streak':x.get('replay_streak'),'movement':x.get('attention_movement')} for x in stale[:20]],
      'mirror_questions':['Which focus center gained attention and why?','Which repeated pattern saturated and released attention?','Did fresh exact/source evidence renew a previously stale pattern?','Did Slime or Keymaster follow a focus that later decayed without gain?','Which focus migration should TOPA CORE falsify before the next cycle?'],
      'laws':['ATTENTION_WEIGHT_IS_NOT_EVIDENCE_WEIGHT','REPETITION_MAY_TRIGGER_INSPECTION_BUT_NOT_TRUTH','REPLAY_SATURATES_AND_FATIGUES','NO_FIXED_HYPOTHESIS_CENTER','FOCUS_MAY_MIGRATE_OR_DIE','PIPPI_MIRROR_IS_ADVISORY_ONLY']}
    out.setdefault('slime_advisory_context',{})['attention_ecology_use']='Read focus migration, rising patterns and replay-fatigue events before next route proposal; never convert attention alone into an exact label.'
    out.setdefault('keymaster_advisory_context',{})['attention_ecology_use']='Use attention ecology to reorder/diversify exact checks and avoid stale repeated waste; truth semantics remain exact-only.'
    out.setdefault('scientific_firewall',{})['SPIDER_ATTENTION_IS_NOT_PROOF']=True
    out['attention_mirror_checkpoint_id']=stable_hash(out)[:32]
    return out

def self_test():
    m={'status':'READY','P_VS_NP':'OPEN','slime_advisory_context':{},'keymaster_advisory_context':{},'scientific_firewall':{}}
    a=[
      {'kind':'EDGE_ATTENTION','edge_key':'A|B','attention_weight':0.44,'attention_delta':0.08,'replay_streak':2,'fresh_evidence_signature':False,'attention_movement':'ATTENTION_STRENGTHENED'},
      {'kind':'EDGE_ATTENTION','edge_key':'C|D','attention_weight':0.05,'attention_delta':-0.06,'replay_streak':9,'attention_movement':'SATURATED_REPLAY_DECAY'},
      {'kind':'NODE_ATTENTION','node_id':'A','attention_score':0.7,'attention_delta':0.1,'focus_rank':1,'focus_state':'PRIMARY_FOCUS','focus_age':2,'spiral_ring_trace':[0.4,0.6,0.7]}]
    o=enrich(m,a)
    assert o['spider_attention_ecology']['focus_centers'][0]['node_id']=='A'
    assert o['spider_attention_ecology']['stale_or_saturated_patterns'][0]['edge_key']=='C|D'
    assert o['scientific_firewall']['SPIDER_ATTENTION_IS_NOT_PROOF'] is True
    return {'status':'PASS','schema':SCHEMA,'P_VS_NP':P_VS_NP}

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True); sp.add_parser('self-test')
    p=sp.add_parser('enrich'); p.add_argument('--mirror',required=True); p.add_argument('--attention-state',required=True); p.add_argument('--out',required=True)
    a=ap.parse_args()
    if a.cmd=='self-test': print(json.dumps(self_test(),indent=2)); return 0
    m=json.loads(Path(a.mirror).read_text(encoding='utf-8')); rows=read_jsonl(a.attention_state); out=enrich(m,rows)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','focus_centers':len(out['spider_attention_ecology']['focus_centers']),'stale_patterns':len(out['spider_attention_ecology']['stale_or_saturated_patterns']),'P_VS_NP':P_VS_NP},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
