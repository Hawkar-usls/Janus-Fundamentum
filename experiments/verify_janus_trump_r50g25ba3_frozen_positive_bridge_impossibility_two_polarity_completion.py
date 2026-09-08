from __future__ import annotations

import argparse, json
from itertools import product
from pathlib import Path

import janus_trump_r50g25ba2_persistent_endpoint_correlation_channel as ba2

Q,P,R=2,30,32
ALL=((1,1),(1,1)); I=((1,0),(0,1)); XOR=((0,1),(1,0)); B=((0,1),(1,1)); C_STAR=((1,1),(1,0))
BA2_CLAUSE=(-Q,-P); BA3_BLOCK=(Q,P)

def compose(A,B):
    return tuple(tuple(int(any(A[x][y] and B[y][z] for y in (0,1))) for z in (0,1)) for x in (0,1))
def rowset(row): return frozenset(i for i,b in enumerate(row) if b)
def clause_ok(a,c): return any((bool(a[abs(l)]) if l>0 else not bool(a[abs(l)])) for l in c)
def clause_rel(lits):
    vals=[]
    for x,y in product((0,1),repeat=2):
        a=(x,y); vals.append(int(any(bool(a[v]) if pos else not bool(a[v]) for v,pos in lits)))
    return ((vals[0],vals[1]),(vals[2],vals[3]))
def inter(A,B): return tuple(tuple(int(A[i][j] and B[i][j]) for j in (0,1)) for i in (0,1))
def exact2(T): return T in (I,XOR)
def clauses():
    out=[]
    for v in (0,1):
        for s in (False,True): out.append(((v,s),))
    for a in (False,True):
        for b in (False,True): out.append(((0,a),(1,b)))
    return out

def verify(path):
    x=json.loads(Path(path).read_text()); errs=[]
    if x.get('outcome')!='BA3-A_PERSISTENT_TWO_POLARITY_BOOLEAN_CHANNEL_CERTIFIED': errs.append('OUTCOME')
    if x.get('preregistration_commit')!='d602ffd76d6413f4a92322b62da897727231ab43': errs.append('PREREG')
    if x.get('falsifiers') or x.get('failure_count')!=0: errs.append('FAILURE_LEDGER')

    Uinfo,U,models,counts,first,RU=ba2.actual_source()
    if RU!=ALL: errs.append('R_U')
    expected={(0,0):8,(0,1):19,(1,0):12,(1,1):21}
    if {k:int(v) for k,v in counts.items()}!=expected: errs.append('ENDPOINT_COUNTS')
    Bactual=ba2.bridge_relation()
    if Bactual!=B: errs.append('B')

    # Independent frozen-positive-bridge impossibility over all 16 C.
    possible=set(); force0=[]
    for mask in range(16):
        v=[(mask>>i)&1 for i in range(4)]; C=((v[0],v[1]),(v[2],v[3])); T=compose(C,Bactual)
        for row in T:
            s=rowset(row); possible.add(s)
            if s==frozenset({0}): force0.append(mask)
    if force0 or possible!={frozenset(),frozenset({1}),frozenset({0,1})}: errs.append('FROZEN_BRIDGE_IMPOSSIBILITY')

    # Independent actual-CNF materialization of XOR block.
    ccounts={(q,p):0 for q in (0,1) for p in (0,1)}
    for a in models:
        if clause_ok(a,BA2_CLAUSE) and clause_ok(a,BA3_BLOCK): ccounts[(int(bool(a[Q])),int(bool(a[P])))]+=1
    CX=tuple(tuple(int(ccounts[(q,p)]>0) for p in (0,1)) for q in (0,1))
    if CX!=XOR or ccounts[(0,1)]!=19 or ccounts[(1,0)]!=12 or ccounts[(0,0)] or ccounts[(1,1)]: errs.append('C_X_REALIZATION')

    # Independent bridge-CNF truth table.
    bx=[]
    for p,r in product((0,1),repeat=2): bx.append(int(bool(p or r) and bool((not p) or (not r))))
    BX=((bx[0],bx[1]),(bx[2],bx[3]))
    if BX!=XOR: errs.append('B_X_REALIZATION')
    T=compose(CX,BX)
    if T!=I or compose(T,T)!=I: errs.append('IDENTITY_PERSISTENCE')

    # Direct source-preimage transport counts.
    tr={(q,r):0 for q in (0,1) for r in (0,1)}
    for a in models:
        if not (clause_ok(a,BA2_CLAUSE) and clause_ok(a,BA3_BLOCK)): continue
        q=int(bool(a[Q])); p=int(bool(a[P]))
        for r in (0,1):
            if (p or r) and ((not p) or (not r)): tr[(q,r)]+=1
    if tr[(0,0)]<=0 or tr[(1,1)]<=0 or tr[(0,1)] or tr[(1,0)]: errs.append('SOURCE_PREIMAGE')

    # Independent minimality audit in preregistered unary/binary endpoint clause grammar.
    cls=clauses(); cost1=[]; cost2=[]
    for cb in cls:
        C=inter(C_STAR,clause_rel(cb));
        if exact2(compose(C,B)): cost1.append(('BLOCK',cb))
    for cr in cls:
        BX1=inter(B,clause_rel(cr));
        if exact2(compose(C_STAR,BX1)): cost1.append(('BRIDGE',cr))
    for cb in cls:
        C=inter(C_STAR,clause_rel(cb))
        for cr in cls:
            BX1=inter(B,clause_rel(cr)); T1=compose(C,BX1)
            if exact2(T1): cost2.append((cb,cr,C,BX1,T1))
    expected_cb=((0,True),(1,True)); expected_cr=((0,False),(1,False))
    if cost1 or len(cost2)!=1 or cost2[0][0]!=expected_cb or cost2[0][1]!=expected_cr or cost2[0][4]!=I: errs.append('MINIMALITY')

    # Check recorded hierarchy/complexity/width and actual reconstruction samples.
    z=x['BA3_10_complexity']; w=z['width']
    if z['C_g']!='67*g-2' or z['L_g']!='163*g-4' or z['V_g']!='20*g': errs.append('SIZE_RECURRENCES')
    if w['generic_width_upper_bound']>13 or w['width_delta_from_BA2']!=0 or not w['same_primal_graph_as_BA2_LAST'] or not w['same_primal_graph_as_BA2_MID']: errs.append('WIDTH')
    if not all(c.get('pass') for c in x['BA3_7_reconstruction']['checks']): errs.append('RECONSTRUCTION')
    if x['BA3_5_information']['N_direction']!=2 or x['BA3_5_information']['I_direction_bits']!=1.0: errs.append('INFORMATION')
    if not all(x['BA3_6_realization_gates'].values()): errs.append('REALIZATION_GATES')
    if not x['BA3_11_minimality']['pass']: errs.append('RECORDED_MINIMALITY')
    if x['firewall']!={'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}: errs.append('FIREWALL')
    return {'gate':'R50G25BA3_INDEPENDENT_VERIFY','status':'PASS' if not errs else 'FAIL','errors':errs,'error_count':len(errs),
            'independent_facts':{'R_U':[[1,1],[1,1]],'B':[[0,1],[1,1]],'C_X':[[0,1],[1,0]],'B_X':[[0,1],[1,0]],'T':[[1,0],[0,1]],
                                 'minimum_additional_clause_cost_beyond_BA2':2,'unique_minimal_pair':['q OR p','NOT p OR NOT r']}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--result',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    v=verify(a.result); Path(a.out).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':v['status'],'errors':v['error_count']},sort_keys=True))
    if v['error_count']: raise SystemExit(3)
if __name__=='__main__': main()
