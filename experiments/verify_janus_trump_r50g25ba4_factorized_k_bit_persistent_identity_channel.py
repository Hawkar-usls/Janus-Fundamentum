from __future__ import annotations

import argparse, hashlib, json
from itertools import combinations
from pathlib import Path

import janus_trump_r50g25ba2_persistent_endpoint_correlation_channel as ba2
import janus_trump_r50g25ba3_frozen_positive_bridge_impossibility_two_polarity_completion as ba3
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

PREREG='451304721fdf7c369ead9f502666384cbfefc2b4'
Q,P=2,30
ORDER=az.ORDER


def ok(a,c): return any((bool(a[abs(int(l))]) if int(l)>0 else not bool(a[abs(int(l))])) for l in c)
def shift(c,o): return tuple((abs(int(l))+o if int(l)>0 else -(abs(int(l))+o)) for l in c)
def lo(g,i): return 30*g*i


def lane(U,g,i):
    out=[]; base=lo(g,i)
    for j in range(g):
        o=base+30*j
        out.extend(shift(c,o) for c in U)
        q=Q+o; p=P+o; out.extend(((-q,-p),(q,p)))
    for j in range(g-1):
        p=P+base+30*j; qn=Q+base+30*(j+1); out.extend(((p,qn),(-p,-qn)))
    return out,set(abs(int(l)) for c in out for l in c)


def instance(U,g,k):
    cs=[]; vs=[]
    for i in range(k):
        c,v=lane(U,g,i); cs+=c; vs.append(v)
    return cs,vs


def independent_width(cs,vs,g,k):
    adj={v:set() for x in vs for v in x}
    for c in cs:
        s=sorted({abs(int(l)) for l in c})
        for a,b in combinations(s,2): adj[a].add(b); adj[b].add(a)
    for i,j in combinations(range(k),2):
        if vs[i]&vs[j]: return None,'VAR_OVERLAP'
    membership={v:i for i,x in enumerate(vs) for v in x}
    for c in cs:
        if len({membership[abs(int(l))] for l in c})!=1: return None,'CROSS_LANE_CLAUSE'
    order=[]
    for i in range(k):
        for j in range(g): order += [v+lo(g,i)+30*j for v in ORDER]
    w=az.explicit_width(adj,order)
    return w['width'],None


def make_model(first,U,g,k,bits):
    a={}
    for i,b in enumerate(bits):
        proto=first[(int(b),1-int(b))]
        for j in range(g):
            o=lo(g,i)+30*j
            for v,val in proto.items(): a[int(v)+o]=bool(val)
    cs,vs=instance(U,g,k)
    if any(not ok(a,c) for c in cs): return False
    for i,b in enumerate(bits):
        qs=[int(bool(a[Q+lo(g,i)+30*j])) for j in range(g)]
        if qs!=[int(b)]*g: return False
    return len(a)==20*g*k


def verify(path):
    x=json.loads(Path(path).read_text()); errs=[]
    if x.get('outcome')!='BA4-A_FACTORIZED_K_BIT_PERSISTENT_IDENTITY_CHANNEL_CERTIFIED': errs.append('OUTCOME')
    if x.get('preregistration_commit')!=PREREG: errs.append('PREREG')
    if x.get('failure_count')!=0 or x.get('falsifiers'): errs.append('FAILURE_LEDGER')
    if x.get('BA5_started') or x.get('arbitrary_CNF_coverage_started'): errs.append('SCOPE_ESCAPE')

    Uinfo,U,models,counts,first,RU=ba2.actual_source()
    if len(U)!=63 or sum(len(c) for c in U)!=155: errs.append('FROZEN_U_CL')
    cx_counts,first_x,CX=ba3.filter_models(models,[ba3.BA2_CLAUSE,ba3.BA3_BLOCK])
    BX=ba3.bridge_xor_relation(); T=ba3.compose(CX,BX)
    if CX!=((0,1),(1,0)) or BX!=((0,1),(1,0)) or T!=((1,0),(0,1)): errs.append('BA3_IDENTITY_DRIFT')
    dp,_=ba3.generic_projection(Uinfo['defects'],Uinfo['equations'],[ba3.BA2_CLAUSE,ba3.BA3_BLOCK],(Q,P))
    if dp!=CX or (0,1) not in first_x or (1,0) not in first_x: errs.append('SOURCE_PREIMAGE_OR_DP')

    tests=((3,2),(5,3),(7,4),(16,8))
    independent=[]
    for g,k in tests:
        cs,vs=instance(U,g,k)
        C=len(cs); L=sum(len(c) for c in cs); V=len(set().union(*vs)); n=C+L+V
        exp=(k*(67*g-2),k*(163*g-4),20*g*k,k*(250*g-6))
        if (C,L,V,n)!=exp: errs.append(f'SIZE_{g}_{k}')
        w,e=independent_width(cs,vs,g,k)
        if e or w!=13: errs.append(f'WIDTH_{g}_{k}_{e}_{w}')
        patterns=[tuple([0]*k),tuple([1]*k),tuple(i%2 for i in range(k)),tuple([1]+[0]*(k-1)),tuple([0]+[1]*(k-1))]
        raw=hashlib.sha256(f'BA4:{g}:{k}:independent'.encode()).digest()
        patterns.append(tuple((raw[i//8]>>(i%8))&1 for i in range(k)))
        if any(not make_model(first,U,g,k,b) for b in patterns): errs.append(f'RECON_{g}_{k}')
        independent.append({'g':g,'k':k,'C':C,'L':L,'V':V,'n':n,'width':w,'vectors_tested':len(set(patterns))})

    # Exact k=1 sealed-BA3 recovery.
    cs,vs=instance(U,5,1)
    if (len(cs),sum(len(c) for c in cs),len(vs[0]))!=(333,811,100): errs.append('K1_RECOVERY')

    p=x.get('BA4_2_product_relation',{})
    if p.get('explicit_2powk_table_materialized') is not False or p.get('proof_mode')!='COMPONENTWISE_CARTESIAN_PRODUCT_NOT_STATE_ENUMERATION': errs.append('PRODUCT_PROOF_MODE')
    cert=x.get('BA4_4_factorized_certificate',{})
    if cert.get('state_table_rows')!=0 or cert.get('enumerated_boundary_vectors')!=0: errs.append('EXPLICIT_STATE_TABLE')
    cpl=x.get('BA4_7_complexity',{})
    expected={'c(g,k)':'k*(67*g-2)','l(g,k)':'k*(163*g-4)','v(g,k)':'20*g*k','n(g,k)':'k*(250*g-6)'}
    for a,b in expected.items():
        if cpl.get(a)!=b: errs.append('COMPLEXITY_'+a)
    if cpl.get('semantic_state_count')!='2^k' or cpl.get('representation_state_rows')!=0: errs.append('INFO_REPRESENTATION')
    if x.get('firewall')!={'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}: errs.append('FIREWALL')
    return {'gate':'R50G25BA4_INDEPENDENT_VERIFY','status':'PASS' if not errs else 'FAIL','errors':errs,'error_count':len(errs),
            'independent_facts':{'single_lane_T':[[1,0],[0,1]],'product_proof':'componentwise disjoint conjunction','N_direction(k)':'2^k','I_direction(k)':'k bits',
                                 'explicit_2powk_rows':0,'holdouts':independent,'width_bound':13}}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--result',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    v=verify(a.result); Path(a.out).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':v['status'],'errors':v['error_count']},sort_keys=True))
    if v['error_count']: raise SystemExit(3)

if __name__=='__main__': main()
