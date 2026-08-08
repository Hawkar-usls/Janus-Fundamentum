#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

AMBIENT=3
RIGHT_BASIS=(5,)
PARENT_BOUNDARY=(1,)
Q80_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
N8_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
L5_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-RIGHT-LEAF5-CANDIDATE-v1'

class VError(AssertionError):
    def __init__(self,code): super().__init__(code); self.code=code
def req(v,code):
    if not v: raise VError(code)
def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rr(rows):
    vals=[]
    for raw in rows:
        x=int(raw); req(0<=x<(1<<AMBIENT),'GEOMETRY_RANGE')
        if x and x not in vals: vals.append(x)
    vals.sort(reverse=True); t=0
    for col in range(AMBIENT-1,-1,-1):
        s=next((i for i in range(t,len(vals)) if (vals[i]>>col)&1),None)
        if s is None: continue
        vals[t],vals[s]=vals[s],vals[t]; p=vals[t]
        for i in range(len(vals)):
            if i!=t and ((vals[i]>>col)&1): vals[i]^=p
        t+=1
    return tuple(sorted((x for x in vals if x),key=lambda x:x.bit_length(),reverse=True))
def span(rows):
    o={0}
    for r in rr(rows): o|={x^r for x in tuple(o)}
    return o
def add(a,b): return rr((*a,*b))
def meet(a,b): return rr(sorted(span(a)&span(b)))
def coord(space,basis):
    rows=[]
    for mask in space:
        v=0
        for i,q in enumerate(basis):
            if (int(mask)>>i)&1: v^=int(q)
        rows.append(v)
    return rr(rows)
def seg(tr):
    sk=[]; runs=[]
    for s in tr:
        g=(tuple(map(int,s['left'])),tuple(map(int,s['right'])))
        if not sk or sk[-1]!=g: sk.append(g); runs.append(1)
        else: runs[-1]+=1
    return tuple(sk),tuple(runs)
def amb(sk,basis=None):
    return tuple((coord(a,basis),coord(b,basis)) if basis else (rr(a),rr(b)) for a,b in sk)
def encsk(sk): return [{'left':list(a),'right':list(b)} for a,b in sk]
def hv_paths(m,n):
    out=[]
    def rec(i,j,p):
        if (i,j)==(m-1,n-1): out.append(tuple(p)); return
        if i+1<m: p.append((i+1,j)); rec(i+1,j,p); p.pop()
        if j+1<n: p.append((i,j+1)); rec(i,j+1,p); p.pop()
    rec(0,0,[(0,0)]); return sorted(out)
def smap(runs): return tuple(i for i,n in enumerate(runs) for _ in range(int(n)))
def qcount(lruns,rruns,q):
    lm,rm=smap(lruns),smap(rruns); allow=set(q); dp=[[0]*len(rm) for _ in lm]; dp[0][0]=1
    for i in range(len(lm)):
        for j in range(len(rm)):
            if i==0 and j==0: continue
            if (lm[i],rm[j]) not in allow: continue
            dp[i][j]=(dp[i-1][j] if i else 0)+(dp[i][j-1] if j else 0)
    return dp[-1][-1]
def hv_count(m,n): return math.comb(m+n-2,m-1)
def hist(entries,sk):
    c=Counter()
    for e in entries:
        got,r=seg(e['trajectory']); req(got==sk,'SOURCE_SKELETON_DRIFT'); c[r]+=1
    return c
def geometry(lsk,rsk,q):
    initial=meet(lsk[0][1],rsk[0][1]); jv=[]; sv=[]
    for i,j in q:
        l,r=lsk[i],rsk[j]
        jl,jr=add(l[0],r[0]),add(l[1],r[1])
        jc=len(initial)-len(meet(add(l[0],l[1]),add(r[0],r[1])))
        lr=meet(jl,jr); sc=len(lr)-len(meet(lr,PARENT_BOUNDARY))
        req(jc>=0 and sc>=0,'NEGATIVE_CORRECTION'); jv.append(jc); sv.append(sc)
    return jv,sv

def derive(node8,leaf5):
    req(node8.get('schema')==N8_SCHEMA and node8.get('semantic_digest')==dg(node8['proof_payload']),'NODE8_SEMANTIC_BINDING')
    req(leaf5.get('schema')==L5_SCHEMA and leaf5.get('semantic_digest')==dg(leaf5['leaf_payload']),'LEAF5_SEMANTIC_BINDING')
    left=node8['proof_payload']['reachable_closure']['entries']; retained=node8['proof_payload']['preorder_hardening']['retained_generators']
    byret={x['class_id']:x for x in retained}; by=defaultdict(list)
    for e in left:
        req(e['source_class_id'] in byret,'SOURCE_CLASS_COVERAGE'); by[e['source_class_id']].append(e)
    req(set(by)==set(byret),'SOURCE_CLASS_COVERAGE')
    right=leaf5['leaf_payload']['entries']; rset={seg(e['trajectory'])[0] for e in right}; req(len(rset)==1,'LEAF_SKELETON')
    rsk0=next(iter(rset)); rsk=amb(rsk0,RIGHT_BASIS); rh=hist(right,rsk0); leaf_digest=dg(encsk(rsk))
    expected={}; partition_checks=0
    for cid in sorted(byret):
        sk0,_=seg(byret[cid]['generator']); lsk=amb(sk0); lh=hist(by[cid],sk0); source_digest=dg(encsk(lsk)); qs=hv_paths(len(lsk),len(rsk))
        for lr,lc in lh.items():
            for rr0,rc in rh.items():
                exact=hv_count(sum(lr),sum(rr0)); lifted=sum(qcount(lr,rr0,q) for q in qs)
                req(lifted==exact,'QUOTIENT_PARTITION_INCOMPLETE'); partition_checks+=1
        for qi,q in enumerate(qs):
            mult=0
            for lr,lc in lh.items():
                for rr0,rc in rh.items(): mult+=int(lc)*int(rc)*qcount(lr,rr0,q)
            jv,sv=geometry(lsk,rsk,q)
            basis={'source_class_id':cid,'local_quotient_path_index':qi,'quotient_path':[list(z) for z in q],'source_skeleton_digest':source_digest,'leaf_skeleton_digest':leaf_digest}
            did='CN9Q-'+dg(basis)[:20]
            expected[did]={'source_class_id':cid,'local_quotient_path_index':qi,'quotient_path':[list(z) for z in q],'ordinary_hv_steps':[[b[0]-a[0],b[1]-a[1]] for a,b in zip(q,q[1:])],'join_correction_vector':jv,'shrink_correction_vector':sv,'fine_lift_multiplicity':mult}
    lhist=Counter(len(e['trajectory']) for e in left); rhist=Counter(len(e['trajectory']) for e in right)
    analytic=sum(lc*rc*hv_count(ll,rl) for ll,lc in lhist.items() for rl,rc in rhist.items())
    return expected,analytic,partition_checks,len(left),len(right),len(byret)

def verify(q80,node8,leaf5):
    req(q80.get('schema')==Q80_SCHEMA and q80.get('semantic_digest')==dg(q80['proof_payload']),'Q80_SEMANTIC_DIGEST')
    expected,analytic,checks,left_n,right_n,source_n=derive(node8,leaf5); p=q80['proof_payload']; domains=p['quotient_domains']; got={x['domain_id']:x for x in domains}
    req(len(got)==len(domains)==len(expected),'DOMAIN_ID_CONSERVATION')
    req(set(got)==set(expected),'DOMAIN_SET_MISMATCH')
    for did,e in expected.items():
        g=got[did]
        for key in ('source_class_id','local_quotient_path_index','quotient_path','ordinary_hv_steps','join_correction_vector','shrink_correction_vector','fine_lift_multiplicity'):
            req(g.get(key)==e[key],'DOMAIN_FIELD_MISMATCH')
    total=sum(x['fine_lift_multiplicity'] for x in domains)
    req(total==analytic,'FINE_LANGUAGE_CONSERVATION')
    ledger=p['conservation_ledger']
    req(ledger['left_entry_count']==left_n and ledger['right_entry_count']==right_n,'SOURCE_COUNT_CONSERVATION')
    req(ledger['ordinary_hv_refinement_count_analytic']==analytic and ledger['sum_fine_lift_multiplicities']==analytic,'FINE_LANGUAGE_CONSERVATION')
    req(ledger['fine_refinement_domain_count']==len(expected),'DOMAIN_COUNT_CONSERVATION')
    req(ledger['fine_refinement_domains_pairwise_disjoint_under_quotient_map'] is True and ledger['fine_refinement_domain_union_complete_by_per_profile_dp_partition'] is True,'PARTITION_COVERAGE')
    req(ledger['omitted_fine_refinement_multiplicity']==0 and ledger['duplicated_fine_refinement_multiplicity']==0 and ledger['conservation_holds'] is True,'FINE_LANGUAGE_CONSERVATION')
    req(p['geometry']['ordinary_join_steps']==[[1,0],[0,1]] and p['geometry']['ordinary_join_diagonal_allowed'] is False and p['geometry']['extension_preorder_steps']==[[1,0],[0,1],[1,1]],'PATH_DOMAIN_SEPARATION')
    req(p['classification_boundary']['all_domains_unresolved'] is True,'NO_CLASSIFICATION_PROMOTION')
    req(p['strict_boundary']['node9_frontier_candidate_complete'] is False and p['strict_boundary']['formal_admission']=='BLOCKED' and p['strict_boundary']['p_vs_np']=='OPEN','NO_CLASSIFICATION_PROMOTION')
    return {'derived_domain_count':len(expected),'derived_fine_refinement_total':analytic,'run_profile_partition_checks':checks,'derived_source_class_count':source_n,'left_entry_count':left_n,'right_entry_count':right_n}

def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tampers(q80,n8,l5):
    out=[]
    def attack(name,mut):
        x=copy.deepcopy(q80); mut(x); seal(x)
        try: verify(x,n8,l5)
        except VError as e: out.append((name,e.code)); return
        raise AssertionError('tamper survived '+name)
    attack('T01_DELETE_DOMAIN',lambda x:x['proof_payload']['quotient_domains'].pop())
    attack('T02_DOMAIN_MULTIPLICITY',lambda x:x['proof_payload']['quotient_domains'][0].__setitem__('fine_lift_multiplicity',x['proof_payload']['quotient_domains'][0]['fine_lift_multiplicity']+1))
    attack('T03_QUOTIENT_PATH',lambda x:x['proof_payload']['quotient_domains'][0].__setitem__('quotient_path',[[0,0]]))
    attack('T04_JOIN_CORRECTION',lambda x:x['proof_payload']['quotient_domains'][0]['join_correction_vector'].__setitem__(0,9))
    attack('T05_SHRINK_CORRECTION',lambda x:x['proof_payload']['quotient_domains'][0]['shrink_correction_vector'].__setitem__(0,9))
    attack('T06_ANALYTIC_TOTAL',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('ordinary_hv_refinement_count_analytic',0))
    attack('T07_OMISSION',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('omitted_fine_refinement_multiplicity',1))
    attack('T08_DUPLICATION',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('duplicated_fine_refinement_multiplicity',1))
    attack('T09_DIAGONAL_JOIN',lambda x:x['proof_payload']['geometry'].__setitem__('ordinary_join_diagonal_allowed',True))
    attack('T10_PARTITION_FALSE',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('fine_refinement_domain_union_complete_by_per_profile_dp_partition',False))
    attack('T11_PROMOTE_FRONTIER',lambda x:x['proof_payload']['strict_boundary'].__setitem__('node9_frontier_candidate_complete',True))
    attack('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    req(len(out)==12,'TAMPER_COUNT'); return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--node8-artifact',type=Path,required=True); ap.add_argument('--leaf5-artifact',type=Path,required=True); ap.add_argument('--q80-artifact',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args()
    n8,l5,q=load(a.node8_artifact),load(a.leaf5_artifact),load(a.q80_artifact); stats=verify(q,n8,l5); ts=tampers(q,n8,l5) if a.tamper_suite else []
    print('JANUS_ACTUAL_ENGINE_Q80_COMPOSITION_REPLAY_VERIFIER = PASS')
    print('DERIVED_SOURCE_CLASS_COUNT =',stats['derived_source_class_count'])
    print('DERIVED_LEFT_ENTRY_COUNT =',stats['left_entry_count'])
    print('DERIVED_RIGHT_ENTRY_COUNT =',stats['right_entry_count'])
    print('DERIVED_Q80_DOMAIN_COUNT =',stats['derived_domain_count'])
    print('DERIVED_FINE_HV_REFINEMENT_TOTAL =',stats['derived_fine_refinement_total'])
    print('RUN_PROFILE_PARTITION_CHECKS =',stats['run_profile_partition_checks'])
    print('EXPECTED_DOMAIN_OR_FINE_TOTAL_USED_AS_ACCEPTANCE_ORACLE = FALSE')
    print('Q80_PARTITION_FINE_LANGUAGE_CONSERVATION = PASS')
    print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN')
    print('Q80_HISTORICAL_STANDALONE_ADMISSION = FALSE')
    print('NODE8_AUTHORITY_CLOSED = FALSE')
    print('ACTUAL_ENGINE_COMPOSITION_ADMITTED = FALSE')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
