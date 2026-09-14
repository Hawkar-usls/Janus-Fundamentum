from __future__ import annotations
from collections import defaultdict, deque, Counter
from pathlib import Path
import json, hashlib, re

ROOT=Path(__file__).resolve().parent
inputs=json.loads((ROOT/'hidden_inputs.json').read_text(encoding='utf-8'))
truth=json.loads((ROOT/'hidden_truth.json').read_text(encoding='utf-8'))['truth']
rawout=json.loads((ROOT/'candidate_raw.json').read_text(encoding='utf-8'))
rows={r['case_id']:r for r in rawout['rows']}; cases={c['case_id']:[tuple(x) for x in c['cnf']] for c in inputs['cases']}
source=(ROOT/'candidate.py').read_text(encoding='utf-8')

def c0(cnf):
    out=set()
    for cl in cnf:
        s=set(int(x) for x in cl)
        if any(-x in s for x in s):continue
        out.add(tuple(sorted(s,key=lambda x:(abs(x),x<0))))
    return [tuple(c) for c in sorted(out,key=lambda c:(len(c),tuple((abs(x),x<0) for x in c)))]
def csub(cnf):
    cs=[frozenset(c) for c in c0(cnf)];out=[]
    for i,c in enumerate(cs):
        if any(i!=j and d<c for j,d in enumerate(cs)):continue
        out.append(tuple(c))
    return c0(out)
def ccontract(cnf):
    cs=c0(cnf)
    while True:
        occ=Counter(abs(x) for c in cs for x in c);lookup={frozenset(c):i for i,c in enumerate(cs)};used=set();add=[];hit=False
        for i,c in enumerate(cs):
            if i in used:continue
            s=set(c)
            for lit in c:
                if occ[abs(lit)]!=2:continue
                j=lookup.get(frozenset((s-{lit})|{-lit}))
                if j is not None and j!=i and j not in used:used|={i,j};add.append(tuple(s-{lit}));hit=True;break
        if not hit:return csub(cs)
        cs=csub([c for i,c in enumerate(cs) if i not in used]+add)
def cnorm(raw):
    rv={abs(x) for c in raw for x in c};cs=ccontract(raw);parent={v:v for v in rv}
    def f(x):
        parent.setdefault(x,x)
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def u(a,b):
        a,b=f(a),f(b)
        if a==b:return
        if a>b:a,b=b,a
        parent[b]=a
    while True:
        imp=set()
        for c in cs:
            if len(c)==2:
                a,b=c
                if a<0<b:imp.add((-a,b))
                if b<0<a:imp.add((-b,a))
        pairs=[(a,b) for a,b in imp if (b,a) in imp and f(a)!=f(b)]
        if not pairs:break
        for a,b in pairs:u(a,b)
        mapped=[]
        for c in cs:mapped.append([(f(abs(x)) if x>0 else -f(abs(x))) for x in c])
        cs=ccontract(mapped)
    return ccontract(cs)

def q0(cnf):
    pos=[frozenset(c) for c in cnf if c and all(x>0 for x in c)];neg=[frozenset(c) for c in cnf if len(c)==2 and all(x<0 for x in c)]
    if not pos:return None
    owner={}
    for i,b in enumerate(pos):
        for x in b:
            if x in owner:return None
            owner[x]=i
    if set(owner)!={abs(x) for c in cnf for x in c}:return None
    pairs={tuple(sorted(-x for x in c)) for c in neg}
    for b in pos:
        xs=sorted(b)
        for i,a in enumerate(xs):
            for z in xs[i+1:]:
                if (a,z) not in pairs:return None
    adj=defaultdict(set)
    for a,b in pairs:
        if owner[a]!=owner[b]:adj[a].add(b);adj[b].add(a)
    unseen=set(owner);comps=[]
    while unseen:
        s=min(unseen);unseen.remove(s);cc={s};st=[s]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y in unseen:unseen.remove(y);cc.add(y);st.append(y)
        comps.append(frozenset(cc))
    ci={x:i for i,c in enumerate(comps) for x in c}
    for cc in comps:
        xs=sorted(cc);bo=set()
        for x in xs:
            if owner[x] in bo:return None
            bo.add(owner[x])
        for i,a in enumerate(xs):
            for b in xs[i+1:]:
                if (a,b) not in pairs:return None
    allowed=set(pos)|set(neg)
    if any(frozenset(c) not in allowed for c in cnf):return None
    edges={i:set() for i in range(len(pos))}
    for x,i in owner.items():edges[i].add(ci[x])
    return {'edges':edges,'blocks':pos,'components':comps}
def q1(cnf):
    if not cnf or any(len(c)>2 for c in cnf):return None
    edges=set();vs={abs(x) for c in cnf for x in c}
    for c in cnf:
        if len(c)==0:return {'edges':edges,'empty':True,'vars':vs}
        if len(c)==1:edges.add((-c[0],c[0]))
        else:
            a,b=c;edges.add((-a,b));edges.add((-b,a))
    return {'edges':edges,'empty':False,'vars':vs}
def q2(cnf):
    if not cnf or not any(len(c)>=3 for c in cnf) or any(sum(x>0 for x in c)>1 for c in cnf):return None
    rr={}
    for i,c in enumerate(cnf):rr[i]=(tuple(sorted(-x for x in c if x<0)),next((x for x in c if x>0),None))
    return rr
def q3(cnf):
    if not cnf or any(len(c)!=3 for c in cnf):return None
    groups=defaultdict(list)
    for c in cnf:groups[tuple(sorted(abs(x) for x in c))].append(c)
    eq=[]
    for sc,cls in sorted(groups.items()):
        if len(cls)!=4:return None
        good=[]
        for bits in range(8):
            val={sc[i]:bool((bits>>i)&1) for i in range(3)}
            if all(any(val[abs(x)] if x>0 else not val[abs(x)] for x in c) for c in cls):good.append(bits)
        if len(good)!=4:return None
        p={((b&1)^((b>>1)&1)^((b>>2)&1)) for b in good}
        if len(p)!=1:return None
        eq.append((sc,next(iter(p))))
    return eq

def replay(raw,ass):return all(any((x>0 and ass.get(abs(x),False)) or (x<0 and not ass.get(abs(x),False)) for x in c) for c in raw)
def coarse(raw):
    deg=Counter(abs(x) for c in raw for x in c);wh=Counter(len(c) for c in raw);pos=sum(x>0 for c in raw for x in c);neg=sum(x<0 for c in raw for x in c)
    return (len(deg),len(raw),tuple(sorted(wh.items())),tuple(sorted(deg.values())),pos,neg)

def verify_unsat(slot,norm,cert):
    if slot==0:
        r=q0(norm)
        if r is None:return False
        S=set(cert.get('S',[]));N=set(cert.get('N',[]));nu=set()
        for u in S:
            if u not in r['edges']:return False
            nu|=set(r['edges'][u])
        return bool(S) and N==nu and len(N)<len(S)
    if slot==1:
        r=q1(norm)
        if r is None:return False
        if cert.get('empty_clause'):return r['empty'] and () in norm
        v=cert.get('var');p=cert.get('path_pos_neg',[]);q=cert.get('path_neg_pos',[])
        def vp(path,a,b):return bool(path) and path[0]==a and path[-1]==b and all((path[i],path[i+1]) in r['edges'] for i in range(len(path)-1))
        return isinstance(v,int) and vp(p,v,-v) and vp(q,-v,v)
    if slot==2:
        rr=q2(norm)
        if rr is None:return False
        true=set()
        for step in cert.get('trace',[]):
            if not isinstance(step,list) or len(step)!=2:return False
            i,h=step
            if i not in rr:return False
            ant,head=rr[i]
            if head!=h or head is None or not all(x in true for x in ant):return False
            true.add(head)
        si=cert.get('sink_clause')
        if si not in rr:return False
        ant,head=rr[si]
        return head is None and all(x in true for x in ant)
    if slot==3:
        eq=q3(norm)
        if eq is None:return False
        ids=cert.get('equation_indices',[])
        if not ids:return False
        mask=Counter();rhs=0
        for i in ids:
            if not isinstance(i,int) or i<0 or i>=len(eq):return False
            sc,b=eq[i];rhs^=b
            for v in sc:mask[v]^=1
        return rhs==1 and all((z%2)==0 for z in mask.values())
    return False

fail=[];misroute=[];exact=[];outfail=[]
# Discovery-source firewall: inspect only the routing function body.
a=source.index('def discover');b=source.index('def solve0');disc=source[a:b].lower();forbidden=['family','schema','matching','hall','scc','horn','xor','gauss','php','pigeon','hole','sat','unsat']
firewall_hits=[w for w in forbidden if w in disc];fixed='probes=(p0,p1,p2,p3)' in disc
counts=defaultdict(lambda:Counter());hold=defaultdict(int)
for t in truth:
    cid=t['case_id'];raw=cases[cid];r=rows.get(cid)
    if r is None:fail.append([cid,'missing-output']);continue
    es=t['expected_slot'];kind=t['kind']
    if es is None:
        if r.get('candidate')!='NO_CANDIDATE':outfail.append([cid,kind,r.get('candidate')])
        continue
    if kind=='HIDDEN':
        counts[es][t['truth']]+=1
        if t.get('holdout'):hold[es]+=1
    if r.get('candidate')!=f'CANDIDATE_{es}':misroute.append([cid,es,r.get('candidate'),kind]);continue
    if r.get('decision')!=t['truth']:exact.append([cid,'decision',t['truth'],r.get('decision')]);continue
    norm=cnorm(raw);probe=(q0(norm) if es==0 else q1(norm) if es==1 else q2(norm) if es==2 else q3(norm))
    if probe is None:exact.append([cid,'independent-admission-fail']);continue
    if t['truth']=='SAT':
        ass={int(k):bool(v) for k,v in (r.get('assignment') or {}).items()}
        if not replay(raw,ass) or r.get('root_replay') is not True:exact.append([cid,'root-replay-fail'])
    else:
        if not verify_unsat(es,norm,r.get('certificate') or {}):exact.append([cid,'unsat-certificate-fail'])
# Required balance and holdout cardinality.
for s in range(4):
    if counts[s]['SAT']!=16 or counts[s]['UNSAT']!=16:fail.append(['balance',s,dict(counts[s])])
    if hold[s]!=8:fail.append(['holdout-count',s,hold[s]])
# Near-collision proof against the frozen cheap schema signature.
pairs=defaultdict(list)
for t in truth:
    if t['kind']=='STRUCTURAL_NEAR_COLLISION':pairs[t['pair']].append((t['expected_slot'],coarse(cases[t['case_id']]),t['case_id']))
collision_ok=True;collision_detail=[]
for k,items in sorted(pairs.items()):
    sigs={x[1] for x in items};slots={x[0] for x in items};ok=(len(items)==2 and len(sigs)==1 and slots=={2,3});collision_ok&=ok;collision_detail.append({'pair':k,'ok':ok,'cases':[x[2] for x in items]})
# Explicit schema-router baseline: exact coarse-signature lookup learned only on non-holdout hidden cases.
train=defaultdict(list)
for t in truth:
    if t['kind']=='HIDDEN' and not t['holdout']:train[coarse(cases[t['case_id']])].append(t['expected_slot'])
lookup={sig:Counter(v).most_common(1)[0][0] for sig,v in train.items()}
challenge=[t for t in truth if t.get('holdout') or t['kind']!='HIDDEN'];agree=0;total=0
for t in challenge:
    pred=lookup.get(coarse(cases[t['case_id']]))
    main=rows[t['case_id']]['candidate'];mp=None if main=='NO_CANDIDATE' else int(main.rsplit('_',1)[1])
    agree+=int(pred==mp);total+=1
baseline_agreement=(agree/total if total else 1.0);schema_fail=(not collision_ok) or baseline_agreement>=0.95
# Structural polynomial budget audit of the frozen implementation, not an empirical theorem.
poly_forbidden=['itertools.product','itertools.permutations','itertools.combinations','search_until','while solved','eval(']
poly_hits=[x for x in poly_forbidden if x in source.lower()]
local_truth_table_constant='for bits in range(8)' in source;single_dispatch=('solve0(cand) if cand[\'slot\']==0' in source and 'for probe in probes' in source)
poly_ok=(not poly_hits and local_truth_table_constant and fixed and single_dispatch)
if not fixed or firewall_hits:fail.append(['source-firewall',firewall_hits,fixed])
if not poly_ok:fail.append(['polynomial-budget-audit',poly_hits,local_truth_table_constant,single_dispatch])
if not collision_ok:fail.append(['near-collision-contract'])
verdict='PASS_BLINDED_MULTI_FAMILY_ROUTING'
if not poly_ok:verdict='FAIL_POLYNOMIAL_BUDGET'
elif outfail:verdict='FAIL_OUT_OF_LIBRARY_REJECTION'
elif schema_fail:verdict='FAIL_SCHEMA_FINGERPRINT'
elif misroute:verdict='FAIL_CARRIER_MISROUTING'
elif exact or fail:verdict='FAIL_EXACTNESS_ADMISSION'
result={
'artifact':'JANUS-TRUMP-APMA-BLINDED-MULTI-FAMILY-CARRIER-ROUTING-FALSIFIER-GATE-2026-09-14-v1.0',
'verdict':verdict,
'population':{'total':len(truth),'hidden':sum(t['kind']=='HIDDEN' for t in truth),'controls':sum(t['kind']!='HIDDEN' for t in truth),'per_slot':{str(s):dict(counts[s]) for s in range(4)},'holdout_per_slot':dict(hold)},
'source_firewall':{'fixed_four_primitives':fixed,'forbidden_hits':firewall_hits},
'schema_router_baseline':{'feature':'(n,m,width_hist,absolute_degree_multiset,total_positive,total_negative)','challenge_cases':total,'agreement_with_main':baseline_agreement,'near_collision_proof':collision_detail,'practically_identical_threshold':0.95,'failed_schema_fingerprint':schema_fail},
'polynomial_budget':{'structural_audit':poly_ok,'forbidden_hits':poly_hits,'constant_local_truth_table_8':local_truth_table_constant,'empirical_scaling_is_not_asymptotic_proof':True},
'failures':{'general':fail,'misrouting':misroute,'exactness':exact,'out_of_library':outfail},
'certificate_firewall':{'SAT':'assignment replayed on original raw CNF','UNSAT':'independent slot-specific structural witness verification'},
'lineage':{'prereg_commit':'305863f111dbaebc5be246f4913f92ed1252ff0c','candidate_freeze_commit':'4c605f602f20b5adf91bc3fde5da74c29923a357'},
'evidence':{'candidate_source_sha256':hashlib.sha256((ROOT/'candidate.py').read_bytes()).hexdigest(),'hidden_inputs_sha256':hashlib.sha256((ROOT/'hidden_inputs.json').read_bytes()).hexdigest(),'hidden_truth_sha256':hashlib.sha256((ROOT/'hidden_truth.json').read_bytes()).hexdigest(),'candidate_raw_sha256':hashlib.sha256((ROOT/'candidate_raw.json').read_bytes()).hexdigest()},
'scientific_firewall':{'ROUTING':'TESTED_SCOPED','SYNTHESIS':'NOT_TESTED','UNIVERSAL_DISCOVERY':'NOT_CLAIMED','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0}
}
print(json.dumps(result,sort_keys=True,separators=(',',':')))
