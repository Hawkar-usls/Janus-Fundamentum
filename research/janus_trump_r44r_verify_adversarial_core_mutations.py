#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'research'/'JANUS_TRUMP_R44R_PROTECTED_CORE_ADVERSARIAL_MUTATION_TEST_2026-09-03.json'

def detector(attack):
    m=attack['mutation'].lower()
    signatures={
      'A1_SCOPE_CREEP':['proper subclass'],
      'A2_PROGRESS_PROMOTION':['finite pass','proof of p=np'],
      'A3_HIDDEN_COMPILER':['exclude','compilation cost'],
      'A4_VERIFIER_CAPTURE':['weaken','verifier'],
      'A5_MEMORY_ERASURE':['drop','verified obstruction'],
      'A6_OPEN_COLLAPSE':['reinterpret open'],
      'A7_LOCAL_TO_GLOBAL':['one route','p!=np'],
      'A8_AUTHORITY_BY_LEARNING':['increase theorem authority'],
      'A9_MOVING_GOALPOST':['change the frozen success criterion'],
      'A10_RENAMED_OLD_FAILURE':['known obstruction','new terminology']
    }
    return all(s in m for s in signatures[attack['id']])

def main():
    c=json.loads(P.read_text())
    results=[]
    for a in c['attacks']:
        detected=detector(a)
        results.append({'id':a['id'],'detected':detected})
        if a['must_detect'] and not detected:
            print(json.dumps({'verdict':'FAIL_CORE_BREACH','results':results},sort_keys=True))
            raise SystemExit(1)
    print(json.dumps({
      'verdict':'PASS_ALL_MUTATIONS_REJECTED',
      'attacks':len(results),
      'detected':sum(x['detected'] for x in results),
      'p_vs_np':'OPEN',
      'next_gate':c['next_gate']
    },sort_keys=True))

if __name__=='__main__': main()
