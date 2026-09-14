from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from itertools import product
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import core

def canon(raw):
    out=set()
    for c in raw:
        s=set(int(x) for x in c)
        if any(-x in s for x in s):continue
        out.add(tuple(sorted(s,key=lambda z:(abs(z),z<0))))
    return [tuple(c) for c in sorted(out,key=lambda c:(len(c),tuple((abs(x),x<0) for x in c)))]

def replay(raw,a):
    return all(any((x>0 and bool(a.get(abs(x),False))) or (x<0 and not bool(a.get(abs(x),False))) for x in c) for c in raw)

def relation_edges(raw):
    cnf=canon(raw);pos=[c for c in cnf if c and all(x>0 for x in c)];neg=[c for c in cnf if len(c)==2 and all(x<0 for x in c)]
    if len(pos)+len(neg)!=len(cnf):return None
    owner={}
    for i,b in enumerate(pos):
        for x in b:
            if x in owner:return None
            owner[x]=i
    if set(owner)!={abs(x) for c in cnf for x in c}:return None
    pairs={tuple(sorted((-a,-b))) for a,b in neg};adj=defaultdict(set)
    for b in pos:
        xs=sorted(b)
        for i,a in enumerate(xs):
            for z in xs[i+1:]:
                if (min(a,z),max(a,z)) not in pairs:return None
    for a,b in pairs:
        if owner[a]!=owner[b]:adj[a].add(b);adj[b].add(a)
    unseen=set(owner);comps=[]
    while unseen:
        s=min(unseen);unseen.remove(s);st=[s];cc={s}
        while st:
            x=st.pop()
            for y in adj[x]:
                if y in unseen:unseen.remove(y);cc.add(y);st.append(y)
        comps.append(cc)
    co={x:i for i,c in enumerate(comps) for x in c}
    for c in comps:
        seen=set()
        for x in c:
            if owner[x] in seen:return None
            seen.add(owner[x])
        for a in c:
            for b in c:
                if a<b and (a,b) not in pairs:return None
    return {i:{co[x] for x in b} for i,b in enumerate(pos)}

def verify0(raw,z):
    if z['decision']=='SAT':return replay(raw,z.get('assignment',{}))
    e=relation_edges(raw);c=z.get('certificate') or {}
    if e is None or c.get('kind')!='c0':return False
    S=set(c.get('S',[]));N=set(c.get('N',[]))
    return bool(S) and N==set().union(*(e[u] for u in S)) and len(N)<len(S)

def arc_graph(raw):
    cnf=canon(raw)
    if any(len(c)>2 or len(c)==0 for c in cnf):return None
    g=defaultdict(set)
    for c in cnf:
        arcs=[(-c[0],c[0])] if len(c)==1 else [(-c[0],c[1]),(-c[1],c[0])]
        for a,b in arcs:g[a].add(b)
    return g

def path_ok(g,p,a,b):
    return isinstance(p,list) and p and p[0]==a and p[-1]==b and all(y in g.get(x,set()) for x,y in zip(p,p[1:]))

def verify1(raw,z):
    if z['decision']=='SAT':return replay(raw,z.get('assignment',{}))
    g=arc_graph(raw);c=z.get('certificate') or {};v=c.get('v')
    return g is not None and c.get('kind')=='c1' and isinstance(v,int) and path_ok(g,c.get('p1'),v,-v) and path_ok(g,c.get('p2'),-v,v)

def rules(raw):
    rr=[]
    for c in canon(raw):
        p=[x for x in c if x>0]
        if len(p)>1:return None
        rr.append((set(-x for x in c if x<0),p[0] if p else None))
    return rr

def verify2(raw,z):
    if z['decision']=='SAT':return replay(raw,z.get('assignment',{}))
    rr=rules(raw);c=z.get('certificate') or {};tr=c.get('trace')
    if rr is None or c.get('kind')!='c2' or not isinstance(tr,list) or not tr:return False
    true=set()
    for j,i in enumerate(tr):
        if not isinstance(i,int) or not (0<=i<len(rr)):return False
        body,head=rr[i]
        if not body.issubset(true):return False
        if head is None:return j==len(tr)-1
        true.add(head)
    return False

def local_rows(raw):
    groups=defaultdict(list)
    for c in canon(raw):
        if not (1<=len(c)<=3):return None
        key=tuple(sorted(abs(x) for x in c));groups[key].append(c)
    rows=[]
    for key,clauses in sorted(groups.items()):
        good=[]
        for bits in range(1<<len(key)):
            a={v:bool((bits>>i)&1) for i,v in enumerate(key)}
            if all(any((x>0 and a[abs(x)]) or (x<0 and not a[abs(x)]) for x in c) for c in clauses):good.append(bits)
        if len(good)!=(1<<(len(key)-1)):return None
        p={sum((b>>i)&1 for i in range(len(key)))&1 for b in good}
        if len(p)!=1:return None
        rows.append((set(key),next(iter(p))))
    return rows

def verify3(raw,z):
    if z['decision']=='SAT':return replay(raw,z.get('assignment',{}))
    rr=local_rows(raw);c=z.get('certificate') or {};ix=c.get('rows')
    if rr is None or c.get('kind')!='c3' or not isinstance(ix,list) or not ix:return False
    S=set();b=0
    for i in ix:
        if not isinstance(i,int) or not (0<=i<len(rr)):return False
        S^=rr[i][0];b^=rr[i][1]
    return not S and b==1

VER=[verify0,verify1,verify2,verify3]

def metrics(cnf):
    real=[c for c in cnf if not any(-x in c for x in c)];d=defaultdict(int);w=defaultdict(int);p=n=0
    for c in real:
        w[len(c)]+=1
        for x in c:d[abs(x)]+=1;p+=x>0;n+=x<0
    return {'n':len(d),'m':len(real),'width_hist':[list(x) for x in sorted(w.items())],'degree_multiset':sorted(d.values()),'pos':p,'neg':n}

def primitive_audit(sample):
    hits=[]
    for i,q in enumerate(core.QS):
        try:z=q(sample)
        except Exception:z=None
        if isinstance(z,dict) and 'decision' in z:hits.append(f'P{i}')
    for i,r in enumerate(core.RS,4):
        try:z=r(sample)
        except Exception:z=None
        if isinstance(z,dict) and 'decision' in z:hits.append(f'P{i}')
    return hits

def main():
    cand=json.loads((ROOT/'SYNTHESIZED_CANDIDATES.json').read_text());cal=json.loads((ROOT/'calibration.json').read_text());adm=json.loads((ROOT/'sealed_admission.json').read_text());hol=json.loads((ROOT/'sealed_holdout.json').read_text());ctl=json.loads((ROOT/'sealed_controls.json').read_text());truth=json.loads((ROOT/'sealed_truth.json').read_text())
    payload=dict(cand);bundle=payload.pop('bundle_sha256');bundle_ok=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()==bundle
    synth=(ROOT/'synthesizer.py').read_text().lower();core_src=(ROOT/'core.py').read_text().lower();forbidden=['relation_resource','binary_reachability','forward_closure','local_linear_rows','sealed_admission','sealed_holdout','sealed_truth','semantic_family','trump_apma_blinded_multifamily']
    source_hits=[x for x in forbidden if x in synth or x in core_src]
    folds={};all_ok=bundle_ok and not source_hits
    dominance={}
    for f in 'ABCD':
        slot=ord(f)-65;p=cand['folds'][f]['selected_program'];ph=core.program_hash(p);expected_hash=cand['folds'][f]['selected_program_hash'];fails=[];counts={'admission':0,'holdout':0,'controls':0};timing={'substrate_ms':0.0,'carrier_ms':0.0,'verify_ms':0.0}
        sample=cal['folds'][f][0]['cnf'];dominance[f]=primitive_audit(sample)
        if dominance[f]:fails.append(['DEGENERATE_PRIMITIVE_LEAK',dominance[f]])
        if ph!=expected_hash:fails.append(['CANDIDATE_HASH_DRIFT',ph,expected_hash])
        for split,data in [('admission',adm),('holdout',hol)]:
            for case in data['folds'][f]:
                z=core.run_program(case['cnf'],p)
                for k,v in z['timing'].items():timing[k]+=v
                gt=truth[case['id']]['truth']
                ok=z['admitted'] and z['decision']==gt and VER[slot](case['cnf'],z)
                if ok:counts[split]+=1
                else:fails.append([split,case['id'],gt,z.get('decision'),z.get('admitted'),z.get('certificate')])
        collision_equal=True
        for case in ctl['folds'][f]:
            if case.get('control')=='near_collision':collision_equal &= metrics(case['cnf'])==case['control_metrics']==case['source_metrics']
            z=core.run_program(case['cnf'],p)
            for k,v in z['timing'].items():timing[k]+=v
            ok=(not z['admitted']) or VER[slot](case['cnf'],z)
            if ok:counts['controls']+=1
            else:fails.append(['control',case['id'],z.get('decision'),z.get('certificate')])
        if not collision_equal:fails.append(['NEAR_COLLISION_METRIC_DRIFT'])
        encoder_ok=all(c['encoder']=='hold_encoder_v3' for c in hol['folds'][f])
        if not encoder_ok:fails.append(['HOLDOUT_ENCODER_DRIFT'])
        fold_ok=not fails and counts['admission']==len(adm['folds'][f]) and counts['holdout']==len(hol['folds'][f]) and counts['controls']==len(ctl['folds'][f])
        folds[f]={'verdict':'PASS_COMPOSITIONAL_SYNTHESIS' if fold_ok else ('FAIL_DEGENERATE_PRIMITIVE_LEAK' if dominance[f] else 'FAIL_EXACTNESS_ADMISSION'),'program':p['id'],'program_hash':ph,'counts':counts,'expected':{'admission':len(adm['folds'][f]),'holdout':len(hol['folds'][f]),'controls':len(ctl['folds'][f])},'near_collision_equal':collision_equal,'encoder_holdout':encoder_ok,'timing_ms':timing,'failures':fails}
        all_ok &= fold_ok
    verdict='PASS_SCOPED_COMPOSITIONAL_CARRIER_SYNTHESIS' if all_ok else 'FAIL_COMPOSITIONAL_CARRIER_SYNTHESIS'
    result={'artifact':'JANUS-TRUMP-APMA-COMPOSITIONAL-CARRIER-SYNTHESIS-HOLDOUT-GATE-2026-09-14-v1.0','verdict':verdict,'folds':folds,'candidate_bundle_sha256':cand['bundle_sha256'],'candidate_bundle_integrity':bundle_ok,'source_firewall':{'forbidden_hits':source_hits,'synthesizer_reads_only_calibration':('calibration.json' in synth and 'sealed_' not in synth)},'primitive_dominance_hits':dominance,'complexity_structure':{'candidate_count':len(core.grammar()),'max_dag_size':max(x['size'] for x in core.grammar()),'max_depth':max(x['depth'] for x in core.grammar()),'constant_local_truth_table_bound':8,'candidate_generation':'constant 16 frozen DAGs; each stage polynomial','timings_are_empirical_only':True},'scientific_firewall':{'ROUTING':'SEALED_PREVIOUSLY','COMPOSITIONAL_SYNTHESIS':'PASS_SCOPED' if all_ok else 'FAILED','UNIVERSAL_DISCOVERY':'NOT_CLAIMED','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0,'NOVEL_COMPOSITE_TRANSFER':'LOCKED'}}
    (ROOT/'checker_raw.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'verdict':verdict,'folds':{f:x['verdict'] for f,x in folds.items()},'fail_counts':{f:len(x['failures']) for f,x in folds.items()},'source_hits':source_hits,'dominance':dominance},sort_keys=True))
if __name__=='__main__':main()
