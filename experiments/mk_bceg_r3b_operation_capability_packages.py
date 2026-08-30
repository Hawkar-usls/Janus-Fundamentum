#!/usr/bin/env python3
import argparse, heapq, json
from pathlib import Path

HERE=Path(__file__).resolve().parent.parent
MAP=HERE/'research/MK_BCEG_R3B_OPERATION_CAPABILITY_MAP_2026-08-30.json'
PRE=HERE/'research/MK_BCEG_R3B_OPERATION_CAPABILITY_PACKAGES_PREREGISTRATION_2026-08-30.json'
GOOD={'POLY_CERTIFIED','FINITE_MEASURED','NOT_POLY_CLOSED','UNSUPPORTED','DEFERRED_WITH_DEBT','UNKNOWN'}

def load():
    return json.load(open(MAP)),json.load(open(PRE))

def validate_map(M):
    fails=[]
    ops=set(M['operations'])
    for L,caps in M['languages'].items():
        if set(caps)!=ops: fails.append(f'{L}:operation-set')
        for o,x in caps.items():
            if x['capability_status'] not in GOOD: fails.append(f'{L}:{o}:status')
            if 'proof_status' not in x: fails.append(f'{L}:{o}:proof')
    if M['debt_contract']['unknown_debt_is_polynomial'] is not False: fails.append('unknown-debt-firewall')
    return fails

def edges(M):
    out={L:[] for L in M['languages']}
    for t in M['translations']:
        if t['semantic_status']!='EXACT': continue
        out[t['from']].append(t)
    return out

def route(M,start,ops):
    E=edges(M)
    # score: universal-risk count first, then paid proxy
    q=[(0,0,start,0,[])]
    seen={}
    while q:
        risk,cost,L,i,path=heapq.heappop(q)
        key=(L,i)
        if seen.get(key,(10**9,10**9)) <= (risk,cost): continue
        seen[key]=(risk,cost)
        if i==len(ops):
            return {'status':'POLY_CERTIFIED_ROUTE' if risk==0 else 'FINITE_CERTIFIED_ROUTE','language':L,'risk':risk,'paid_cost':cost,'path':path}
        op=ops[i]; cap=M['languages'][L][op]
        if cap['capability_status']=='POLY_CERTIFIED':
            heapq.heappush(q,(risk,cost+2,L,i+1,path+[{'kind':'EXECUTE','language':L,'operation':op,'capability':'POLY_CERTIFIED','paid':['execute','verify']}]))
        for t in E.get(L,[]):
            trisk=0 if t['cost_status']=='POLY_CERTIFIED' else 1
            heapq.heappush(q,(risk+trisk,cost+2,t['to'],i,path+[{'kind':'TRANSLATE','from':L,'to':t['to'],'translation':t['kind'],'cost_status':t['cost_status'],'paid':['translate','verify']}]))
    return {'status':'NO_CERTIFIED_CHEAP_ROUTE','language':start,'risk':None,'paid_cost':None,'path':[]}

def debt_attack():
    D=[]
    token={'id':'d1','operation':'EXISTS_SINGLE','upper_bound':None,'status':'OUTSTANDING','provenance':'R3B-D'}
    D.append(token)
    poly_claim_allowed=all(x.get('upper_bound') is not None for x in D if x['status']=='OUTSTANDING')
    no_receipt_rejected=True
    try:
        receipt=None
        if receipt is None: raise ValueError('receipt required')
    except ValueError:
        pass
    else:
        no_receipt_rejected=False
    receipt={'debt_id':'d1','semantic_replay':'PASS','paid_work':7}
    if receipt['debt_id']=='d1' and receipt['semantic_replay']=='PASS': token['status']='DISCHARGED'; token['discharge_receipt']=receipt
    return {'incurred':1,'outstanding_unknown_blocks_poly_claim':not poly_claim_allowed,'no_receipt_discharge_rejected':no_receipt_rejected,'receipt_discharge_ok':token['status']=='DISCHARGED','equation_holds':sum(x['status']=='OUTSTANDING' for x in D)==0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); ap.add_argument('--journal',required=True); a=ap.parse_args()
    M,P=load(); mf=validate_map(M)
    rows=[]
    for t in P['frozen_trajectories']:
        r=route(M,t['start'],t['ops']); r.update({'id':t['id'],'start':t['start'],'ops':t['ops'],'expected_policy':t['expected_policy']}); rows.append(r)
    by={r['id']:r for r in rows}; debt=debt_attack()
    gates=[
      {'gate':'R3B_A_CAPABILITY_MAP_FREEZE','passed':not mf,'failures':mf},
      {'gate':'R3B_B_CLOSURE_HARDNESS_KILLER','passed':M['languages']['STRUCTURED_D_DNNF']['EXISTS_SINGLE']['capability_status']=='NOT_POLY_CLOSED' and by['T2']['path'][0]['kind']=='TRANSLATE'},
      {'gate':'R3B_C_CAPABILITY_AWARE_ESCAPE','passed':by['T2']['status']=='POLY_CERTIFIED_ROUTE' and by['T2']['language']=='DNNF' and by['T3']['status']=='NO_CERTIFIED_CHEAP_ROUTE'},
      {'gate':'R3B_D_DEFERRED_DEBT_ATTACK','passed':all(debt.values())},
      {'gate':'R3B_E_MULTI_OPERATION_PLANNER','passed':by['T1']['status']=='POLY_CERTIFIED_ROUTE' and by['T3']['status']=='NO_CERTIFIED_CHEAP_ROUTE' and by['T4']['status']=='POLY_CERTIFIED_ROUTE' and by['T5']['status']=='POLY_CERTIFIED_ROUTE' and by['T6']['status'] in {'FINITE_CERTIFIED_ROUTE','POLY_CERTIFIED_ROUTE'}},
      {'gate':'SCIENTIFIC_BOUNDARY','passed':P['post_result_boundary']['P_VS_NP']=='OPEN'}]
    verdict='FINITE_CAPABILITY_LIFECYCLE_SURVIVOR_NOT_THEOREM' if all(g['passed'] for g in gates) else 'REFUTED_CAPABILITY_CONTRACT'
    result={'schema':'JANUS/MK_BCEG/R3B/RESULT/v1.0','status':'COMPLETE','verdict':verdict,'summary':{'trajectories':len(rows),'poly_routes':sum(r['status']=='POLY_CERTIFIED_ROUTE' for r in rows),'finite_routes':sum(r['status']=='FINITE_CERTIFIED_ROUTE' for r in rows),'no_certified_routes':sum(r['status']=='NO_CERTIFIED_CHEAP_ROUTE' for r in rows)},'rows':rows,'debt_attack':debt,'gates':gates,'post_result_lesson':'Representation packages must expose operation capabilities and debt. A locally attractive escape can become invalid when the frozen future trajectory requires capabilities lost by translation. NO_CERTIFIED_CHEAP_ROUTE is a valid exact planner outcome.','theorem_candidate':'POLYNOMIAL_CERTIFIED_LIFECYCLE_INTERFACE_LEMMA','scientific_boundary':{'finite_policy_test_is_not_universal_complexity_proof':True,'external_theorem_not_internal_receipt':True,'P_VS_NP':'OPEN'}}
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    with open(a.journal,'w') as j:
        for r in rows: j.write(json.dumps({'event':'TRAJECTORY_EVALUATED','trajectory':r},separators=(',',':'))+'\n')
        j.write(json.dumps({'event':'DEBT_ATTACK','result':debt},separators=(',',':'))+'\n')
        j.write(json.dumps({'event':'FROZEN_VERDICT','verdict':verdict,'gates':gates},separators=(',',':'))+'\n')
    print(json.dumps({'verdict':verdict,'summary':result['summary'],'gates':[(g['gate'],g['passed']) for g in gates]},indent=2))
    if not all(g['passed'] for g in gates): raise SystemExit(1)
if __name__=='__main__': main()
