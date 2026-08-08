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
AUTH_SCHEMA='janus.c049_1.b4_6_3.node8_up_k_authority_closure_audit.v1'
HARDENING_SCHEMA='janus.c049_1.b4_6_4.general_structural_induction_composition_authority_hardening.v1'

class VError(AssertionError):
    def __init__(self,code): super().__init__(code); self.code=code
def req(v,code):
    if not v: raise VError(code)
def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_node8_authority(receipt, hardening):
    req(receipt.get('schema')==AUTH_SCHEMA,'AUTH_SCHEMA')
    req(receipt.get('semantic_digest_scope')=='audit_payload' and dg(receipt.get('audit_payload'))==receipt.get('semantic_digest'),'AUTH_DIGEST')
    a=receipt['audit_payload']; s=a['semantic_subject']; v=a['verification_child']; adm=a['admission']; sb=a['strict_boundary']
    req(s['pr']==116 and s['proof_head']=='0fcdaa168dde2aef27603d51ff547c07860a9fd1','AUTH_PROOF_SUBJECT')
    req(s['independent_semantic_audit_review_id']==4888038247 and s['final_admission_review_id']==4888054139,'AUTH_REVIEW_BINDING')
    req(s['producer_git_blob']=='4ff08eb7b95743efa8e011e797481a6de0eea006' and s['verifier_git_blob']=='48bf8af106df64646c9ca7be50483da22adac027','AUTH_PROOF_BLOBS')
    req(v['pr']==136 and v['head']=='294de1472ea0d5ba9ea1565b89777cf99b17f472','AUTH_VERIFICATION_CHILD')
    req(v['dedicated_run_id']==31238737391 and v['dedicated_job_id']==93055942346 and v['artifact_id']==9016305442,'AUTH_CI_RECEIPT')
    req(v['workflow_success_count']==3 and v['workflow_total_count']==3 and v['registry_conclusion']=='SUCCESS' and v['round_ledger_conclusion']=='SUCCESS','AUTH_WORKFLOW_CLOSURE')
    req(adm['corrected_node8_parent_up_k_complete'] is True and adm['corrected_node8_up_k_admitted'] is True and adm['node8_b2_up_k_language_handoff']=='ADMITTED','AUTH_ADMISSION')
    req(adm['node8_to_node9_composition_edge']=='OPEN_FOR_ACTUAL_ENGINE_COMPOSITION','AUTH_HANDOFF')
    req(sb['q80_must_be_replayed_inside_actual_engine_composition'] is True and sb['actual_corrected_engine_complete_algorithm1_trace_established'] is False,'AUTH_CEILING')
    req(hardening.get('schema')==HARDENING_SCHEMA,'HARDENING_SCHEMA')
    req(hardening.get('semantic_digest_scope')=='hardening_payload' and dg(hardening.get('hardening_payload'))==hardening.get('semantic_digest'),'HARDENING_DIGEST')
    n8=hardening['hardening_payload']['node8_up_k_authority_requirement']
    req(n8['authority_established'] is True,'HARDENING_NODE8_AUTHORITY')
    req(n8['proof_subject']==s['proof_head'] and n8['semantic_audit_review_id']==s['independent_semantic_audit_review_id'] and n8['semantic_admission_review_id']==s['final_admission_review_id'],'HARDENING_AUTHORITY_BINDING')
    req(n8['authority_receipt_git_blob']=='b04124490df9737c0799ed856fd7819b37477208' and n8['authority_receipt_semantic_digest']==receipt['semantic_digest'],'HARDENING_RECEIPT_BINDING')
    req(n8['verification_head']==v['head'] and n8['verification_run_id']==v['dedicated_run_id'] and n8['verification_artifact_id']==v['artifact_id'] and n8['verification_workflows']=='3/3_SUCCESS','HARDENING_VERIFICATION_BINDING')
    return {'proof_subject':s['proof_head'],'review_id':s['final_admission_review_id'],'receipt_semantic_digest':receipt['semantic_digest']}

def authority_tampers(receipt,hardening):
    out=[]
    def ar(name,mut):
        r=copy.deepcopy(receipt); mut(r); r['semantic_digest']=dg(r['audit_payload'])
        try: verify_node8_authority(r,hardening)
        except VError as e: out.append((name,e.code)); return
        raise AssertionError('authority tamper survived '+name)
    def ah(name,mut):
        h=copy.deepcopy(hardening); mut(h); h['semantic_digest']=dg(h['hardening_payload'])
        try: verify_node8_authority(receipt,h)
        except VError as e: out.append((name,e.code)); return
        raise AssertionError('hardening tamper survived '+name)
    ar('A01_REVIEW',lambda r:r['audit_payload']['semantic_subject'].__setitem__('final_admission_review_id',0))
    ar('A02_ADMISSION',lambda r:r['audit_payload']['admission'].__setitem__('corrected_node8_up_k_admitted',False))
    ar('A03_WORKFLOW_COUNT',lambda r:r['audit_payload']['verification_child'].__setitem__('workflow_success_count',2))
    ah('A04_HARDENING_AUTHORITY',lambda h:h['hardening_payload']['node8_up_k_authority_requirement'].__setitem__('authority_established',False))
    req(len(out)==4,'AUTH_TAMPER_COUNT')
    return out

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
    ap=argparse.ArgumentParser()
    ap.add_argument('--node8-artifact',type=Path,required=True)
    ap.add_argument('--leaf5-artifact',type=Path,required=True)
    ap.add_argument('--q80-artifact',type=Path,required=True)
    ap.add_argument('--node8-authority-receipt',type=Path,required=True)
    ap.add_argument('--hardening',type=Path,required=True)
    ap.add_argument('--tamper-suite',action='store_true')
    a=ap.parse_args()
    n8,l5,q=load(a.node8_artifact),load(a.leaf5_artifact),load(a.q80_artifact)
    receipt,hardening=load(a.node8_authority_receipt),load(a.hardening)
    authority=verify_node8_authority(receipt,hardening)
    stats=verify(q,n8,l5)
    ts=tampers(q,n8,l5) if a.tamper_suite else []
    ats=authority_tampers(receipt,hardening) if a.tamper_suite else []
    print('JANUS_ACTUAL_ENGINE_Q80_COMPOSITION_REPLAY_VERIFIER = PASS')
    print('NODE8_AUTHORITY_RECEIPT_SEMANTIC_DIGEST = PASS')
    print('NODE8_AUTHORITY_REVIEW_ID =',authority['review_id'])
    print('DERIVED_SOURCE_CLASS_COUNT =',stats['derived_source_class_count'])
    print('DERIVED_LEFT_ENTRY_COUNT =',stats['left_entry_count'])
    print('DERIVED_RIGHT_ENTRY_COUNT =',stats['right_entry_count'])
    print('DERIVED_Q80_DOMAIN_COUNT =',stats['derived_domain_count'])
    print('DERIVED_FINE_HV_REFINEMENT_TOTAL =',stats['derived_fine_refinement_total'])
    print('RUN_PROFILE_PARTITION_CHECKS =',stats['run_profile_partition_checks'])
    print('EXPECTED_DOMAIN_OR_FINE_TOTAL_USED_AS_ACCEPTANCE_ORACLE = FALSE')
    print('Q80_PARTITION_FINE_LANGUAGE_CONSERVATION = PASS')
    print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN')
    print('NODE8_AUTHORITY_DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ats)}/4' if a.tamper_suite else 'NOT_RUN')
    print('TOTAL_DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)+len(ats)}/16' if a.tamper_suite else 'NOT_RUN')
    print('Q80_HISTORICAL_STANDALONE_ADMISSION = FALSE')
    print('NODE8_AUTHORITY_CLOSED = TRUE')
    print('Q80_COMPOSITION_REPLAY_COMPLETE = TRUE')
    print('ACTUAL_ENGINE_COMPOSITION_ADMITTED = FALSE')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
