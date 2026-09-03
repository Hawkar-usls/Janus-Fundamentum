#!/usr/bin/env python3
import json


def classify(sig):
    fam=sig.get('family')
    payload=sig.get('payload')
    if fam=='BIJUNCTIVE_2CNF':
        ok=isinstance(payload,list) and all(isinstance(c,list) and len(c)<=2 for c in payload)
    elif fam=='HORN_CNF':
        ok=isinstance(payload,list) and all(sum(1 for l in c if l>0)<=1 for c in payload)
    elif fam=='DUAL_HORN_CNF':
        ok=isinstance(payload,list) and all(sum(1 for l in c if l<0)<=1 for c in payload)
    elif fam=='AFFINE_GF2_RREF':
        ok=isinstance(payload,dict) and isinstance(payload.get('rows'),list) and isinstance(payload.get('width'),int)
        if ok:
            w=payload['width']
            ok=all(isinstance(r,list) and len(r)==w+1 and all(x in (0,1) for x in r) for r in payload['rows'])
    else:
        ok=False
    return ok


def compose_same_family(a,b):
    assert classify(a) and classify(b)
    assert a['family']==b['family']
    fam=a['family']
    if fam in ('BIJUNCTIVE_2CNF','HORN_CNF','DUAL_HORN_CNF'):
        return {'family':fam,'payload':a['payload']+b['payload']}
    if fam=='AFFINE_GF2_RREF':
        assert a['payload']['width']==b['payload']['width']
        return {'family':fam,'payload':{'width':a['payload']['width'],'rows':a['payload']['rows']+b['payload']['rows']}}
    raise AssertionError(fam)


def dispatch_pair(a,b):
    if not classify(a) or not classify(b):
        return {'status':'OPEN_SIGNATURE_OUTSIDE_SWITCHBOARD','decision_authority':False}
    if a['family']!=b['family']:
        return {'status':'OPEN_CROSS_FAMILY_COMPOSITION_NOT_YET_ADMITTED','decision_authority':False}
    out=compose_same_family(a,b)
    assert classify(out)
    return {'status':'CERTIFIED_COMPACT_COMPOSITION','decision_authority':True,'signature':out}


fixtures=[
  (
    {'family':'BIJUNCTIVE_2CNF','payload':[[1,2],[-1,3]]},
    {'family':'BIJUNCTIVE_2CNF','payload':[[-2,-3]]},
    'CERTIFIED_COMPACT_COMPOSITION'
  ),
  (
    {'family':'HORN_CNF','payload':[[-1,-2,3],[-3]]},
    {'family':'HORN_CNF','payload':[[-4,2]]},
    'CERTIFIED_COMPACT_COMPOSITION'
  ),
  (
    {'family':'DUAL_HORN_CNF','payload':[[1,2,-3],[3]]},
    {'family':'DUAL_HORN_CNF','payload':[[4,-2]]},
    'CERTIFIED_COMPACT_COMPOSITION'
  ),
  (
    {'family':'AFFINE_GF2_RREF','payload':{'width':4,'rows':[[1,0,1,0,1]]}},
    {'family':'AFFINE_GF2_RREF','payload':{'width':4,'rows':[[0,1,1,1,0]]}},
    'CERTIFIED_COMPACT_COMPOSITION'
  ),
  (
    {'family':'UNKNOWN','payload':{}},
    {'family':'UNKNOWN','payload':{}},
    'OPEN_SIGNATURE_OUTSIDE_SWITCHBOARD'
  ),
  (
    {'family':'HORN_CNF','payload':[[-1,2]]},
    {'family':'AFFINE_GF2_RREF','payload':{'width':2,'rows':[[1,1,0]]}},
    'OPEN_CROSS_FAMILY_COMPOSITION_NOT_YET_ADMITTED'
  )
]

checks=[]
for a,b,expected in fixtures:
    r=dispatch_pair(a,b)
    assert r['status']==expected, (expected,r)
    checks.append({'left':a['family'],'right':b['family'],'status':r['status']})

print(json.dumps({
  'gate_id':'R44K_COMPACT_SIGNATURE_SWITCHBOARD',
  'checks':checks,
  'certified_families':['BIJUNCTIVE_2CNF','HORN_CNF','DUAL_HORN_CNF','AFFINE_GF2_RREF'],
  'compact_composition_demonstrated':True,
  'arbitrary_boundary_truth_table_enumerated':False,
  'universal_compiler_from_arbitrary_3cnf':'OPEN',
  'U1':'OPEN',
  'U2':'ADVANCED_FOR_ADMITTED_SIGNATURES',
  'U3':'ADVANCED_FOR_ADMITTED_SIGNATURES',
  'U4':'ADVANCED_FOR_ADMITTED_SIGNATURES',
  'P_EQUALS_NP':'NOT_PROVED',
  'P_VS_NP':'OPEN',
  'next_gate':'R44L_UNIVERSAL_COMPACT_SIGNATURE_COMPILER_OR_EXPLICIT_OUTSIDE_FAMILY'
}, sort_keys=True))
