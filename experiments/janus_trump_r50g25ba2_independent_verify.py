from __future__ import annotations

import argparse,json
from itertools import combinations
from pathlib import Path

import janus_trump_r50g25ba0_target_family_expressivity_interface_capacity as ba0
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

Q,P,R=2,30,32
CSTAR=((1,1),(1,0)); B=((0,1),(1,1)); TSTAR=((1,1),(0,1)); ALL=((1,1),(1,1))

def comp(A,B): return tuple(tuple(int(any(A[x][y] and B[y][z] for y in (0,1))) for z in (0,1)) for x in (0,1))
def ml(M): return [list(r) for r in M]
def clause_ok(a): return (not bool(a[Q])) or (not bool(a[P]))
def mat_from_mask(mask):
    v=[(mask>>i)&1 for i in range(4)]; return ((v[0],v[1]),(v[2],v[3]))
def both(C): return any(C[0]) and any(C[1])
def persistent(T):
    seen=set(); cur=T
    while cur not in seen:
        if cur[0]==cur[1]: return False
        seen.add(cur); cur=comp(cur,T)
    return cur[0]!=cur[1]
def local_clause_ok(cl,q,p):
    vals={1:bool(q),2:bool(p)}; return any(vals[abs(l)] if l>0 else not vals[abs(l)] for l in cl)
def min_cost(C):
    clauses=[(),(1,),(-1,),(2,),(-2,),(1,2),(1,-2),(-1,2),(-1,-2)]; assigns=[(0,0),(0,1),(1,0),(1,1)]; target={a for a in assigns if C[a[0]][a[1]]}
    if target==set(assigns): return 0
    for k in range(1,5):
        for cs in combinations(clauses,k):
            if {a for a in assigns if all(local_clause_ok(c,*a) for c in cs)}==target: return k
    raise AssertionError(C)
def verify(result):
    fail=[]
    Uinfo=az.source_unit(); U=ba0.r33.canonical_formula(Uinfo['root']); models,counts,first=ba0.enumerate_unit_models(U)
    RU=tuple(tuple(int(counts[(q,p)]>0) for p in (0,1)) for q in (0,1))
    if RU!=ALL or len(models)!=60: fail.append(('SOURCE',RU,len(models)))
    b=tuple(tuple(int(bool(p or r)) for r in (0,1)) for p in (0,1))
    if b!=B: fail.append(('BRIDGE',b))
    ccounts={(q,p):0 for q in (0,1) for p in (0,1)}
    for a in models:
        if clause_ok(a): ccounts[(int(bool(a[Q])),int(bool(a[P])))]+=1
    C=tuple(tuple(int(ccounts[(q,p)]>0) for p in (0,1)) for q in (0,1))
    if C!=CSTAR or ccounts[(1,1)]!=0 or not all(ccounts[x]>0 for x in ((0,0),(0,1),(1,0))): fail.append(('CNF_REALIZATION',C,ccounts))
    T=comp(C,b)
    if T!=TSTAR or comp(T,T)!=T: fail.append(('ALGEBRA',T,comp(T,T)))
    direct={(q,r):0 for q in (0,1) for r in (0,1)}
    for a in models:
        if not clause_ok(a): continue
        q=int(bool(a[Q])); p=int(bool(a[P]))
        for r in (0,1):
            if p or r: direct[(q,r)]+=1
    TD=tuple(tuple(int(direct[(q,r)]>0) for r in (0,1)) for q in (0,1))
    if TD!=TSTAR or direct[(1,0)]!=0: fail.append(('SOURCE_PREIMAGE',TD,direct))
    # Independent complete 16-relation minimality audit.
    persist=[]
    for mask in range(16):
        C0=mat_from_mask(mask); T0=comp(C0,b)
        if both(C0) and persistent(T0): persist.append((mask,min_cost(C0),T0))
    minc=min(c for _,c,_ in persist)
    mins=[m for m,c,_ in persist if c==minc]
    if minc!=1 or 7 not in mins or any(m==15 for m,_,_ in persist): fail.append(('MINIMALITY',persist))
    if comp(((1,0),(0,1)),b)!=b or comp(b,b)!=ALL: fail.append('EQ_CONTROL')
    if comp(((0,1),(1,0)),b)!=TSTAR or min_cost(((0,1),(1,0)))<=min_cost(CSTAR): fail.append('XOR_CONTROL')
    # Recompute structural width directly from actual carrier incidence.
    defects=list(Uinfo['defects'])+[(-Q,-P)]; eqs=Uinfo['equations']; scopes=[tuple(sorted({abs(int(l)) for l in c})) for c in defects]+[tuple(sorted(set(e['vars']))) for e in eqs]+[(P,R)]
    w=az.explicit_width(az.primal_graph(tuple(az.UNIT_VARS)+(R,),scopes),az.ORDER)['width']
    rr=result
    if rr['preregistration_commit']!='a4737c4f934c480658645943554fb6d2d62d9014': fail.append('PREREG_DRIFT')
    if rr['crossfeed_guard_commit']!='82df84cb22606e9cd7a358e79c226f87b7dbeb60': fail.append('CROSSFEED_DRIFT')
    if rr['BA2_0_actual']['R_U']!=ml(RU) or rr['BA2_0_actual']['B']!=ml(b): fail.append('RESULT_SOURCE_DRIFT')
    if rr['BA2_4_candidate']['C_STAR_actual']!=ml(C) or rr['BA2_4_candidate']['T_STAR']!=ml(T): fail.append('RESULT_CANDIDATE_DRIFT')
    if rr['BA2_7_real_cnf_and_source_preimage']['transport_pair_counts']!={str(k):int(v) for k,v in sorted(direct.items())}: fail.append('RESULT_PREIMAGE_DRIFT')
    if rr['BA2_10_complexity']['width_upper_bound']!=w: fail.append(('WIDTH_DRIFT',w,rr['BA2_10_complexity']['width_upper_bound']))
    if rr['outcome'].startswith('BA2-A'):
        if not all(rr['source_preimage_realizability_gate'].values()): fail.append('SUCCESS_WITH_GUARD_FAIL')
        if rr['falsifiers']: fail.append(('SUCCESS_WITH_FALSIFIERS',rr['falsifiers']))
    if rr['interpretation']['arbitrary_CNF_coverage_started'] is not False or rr['interpretation']['BA3_started'] is not False: fail.append('SCOPE_VIOLATION')
    if rr['firewall']!={'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}: fail.append('FIREWALL')
    return {'status':'PASS' if not fail else 'FAIL','failure_count':len(fail),'failures':fail,'independent_R_U':ml(RU),'independent_C_STAR':ml(C),'independent_T_STAR':ml(T),'independent_min_persistent_clause_cost':minc,'independent_minimal_persistent_masks':mins,'independent_width':w,'finite_g_ladder_replayed':False,'arbitrary_CNF_coverage_started':False}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--result',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); r=json.loads(a.result.read_text()); v=verify(r); a.out.write_text(json.dumps(v,indent=2,sort_keys=True)); print(json.dumps(v,sort_keys=True)); raise SystemExit(0 if v['status']=='PASS' else 1)
if __name__=='__main__': main()
