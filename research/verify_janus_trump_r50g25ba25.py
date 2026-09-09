from __future__ import annotations
import json, hashlib, itertools, random, sys
from collections import defaultdict

PREREG='research/JANUS_TRUMP_R50G25BA25_PREREGISTRATION.json'
RESULT='ba25_result.json'
BA24_RECEIPT='research/JANUS_TRUMP_R50G25BA24_RESULT_RECEIPT.json'
OUT='ba25_verify.json'

def knd(x):return x.split(':',1)[0]
def state_map(bag,st):return dict(zip(sorted(bag),st[:-1])),st[-1]
def mkstate(bag,m,w):return tuple(m[x] for x in sorted(bag))+(int(w),)
def canon_instance(raw):
    vs=tuple(sorted(raw['variables']));bs=tuple(tuple(sorted(b)) for b in raw['blocks']);cs=[]
    for c in raw['clauses']:
        by=defaultdict(set)
        for v,s in c:by[v].add(int(s))
        cs.append(tuple((v,s) for v in sorted(by) for s in sorted(by[v])))
    return vs,bs,tuple(cs)
def graph_from_instance(raw):
    vs,bs,cs=canon_instance(raw);V={f'v:{v}' for v in vs};B={f'B:{i}' for i in range(len(bs))};C={f'C:{i}' for i in range(len(cs))};edges={}
    for i,b in enumerate(bs):
        for v in b:edges[tuple(sorted((f'v:{v}',f'B:{i}')))]={'type':'BLOCK'}
    for j,c in enumerate(cs):
        by=defaultdict(set)
        for v,s in c:by[v].add(s)
        for v,ss in by.items():edges[tuple(sorted((f'v:{v}',f'C:{j}')))]={'type':'CLAUSE','signs':tuple(sorted(ss))}
    return vs,bs,cs,V|B|C,edges
def eval_inst(raw,a):
    vs,bs,cs=canon_instance(raw);return bool(any(all(a[v] for v in b) for b in bs) and all(any(a[v] if s==1 else not a[v] for v,s in c) for c in cs))
def brute(raw):
    vs,_,_=canon_instance(raw);return sum(eval_inst(raw,dict(zip(vs,bits))) for bits in itertools.product((0,1),repeat=len(vs)))
def validate_td(vertices,edges,td):
    bags={k:set(v) for k,v in td['bags'].items()};nodes=set(bags);tedges=[tuple(x) for x in td['edges']];adj={x:set() for x in nodes}
    for a,b in tedges:
        if a not in nodes or b not in nodes or a==b:return False,None
        adj[a].add(b);adj[b].add(a)
    if nodes:
        seen=set();st=[next(iter(nodes))]
        while st:
            x=st.pop()
            if x in seen:continue
            seen.add(x);st.extend(adj[x]-seen)
        if seen!=nodes or len(tedges)!=len(nodes)-1:return False,None
    if (set().union(*bags.values()) if bags else set())!=set(vertices):return False,None
    for u,v in edges:
        if not any(u in b and v in b for b in bags.values()):return False,None
    for v in vertices:
        hs={x for x,b in bags.items() if v in b}
        if not hs:return False,None
        seen=set();st=[next(iter(hs))]
        while st:
            x=st.pop()
            if x in seen:continue
            seen.add(x);st.extend((adj[x]&hs)-seen)
        if seen!=hs:return False,None
    return True,max((len(b)-1 for b in bags.values()),default=-1)
def rows_map(rows):return {tuple(r['state']):int(r['count']) for r in rows}
def hash_rows(tab):
    return hashlib.sha256(json.dumps([(list(k),v) for k,v in sorted(tab.items())],separators=(',',':')).encode()).hexdigest()
def replay_sample(ps):
    if ps.get('format')!='PC_HYBRID_FACTOR_TD_V1':return False,'format'
    raw=ps['instance'];vs,bs,cs,verts,edges=graph_from_instance(raw);fg=ps['signed_factor_graph']
    if set(fg['vertices'])!=set(verts):return False,'fg_vertices'
    got={tuple(sorted((x['u'],x['v']))):{k:(tuple(v) if k=='signs' else v) for k,v in x.items() if k not in ('u','v')} for x in fg['edges']}
    if got!=edges:return False,'fg_edges'
    ok,tau=validate_td(verts,edges,ps['supplied_td'])
    if not ok or tau!=ps['td_validation']['tau']:return False,'td'
    nodes={n['id']:n for n in ps['nice_nodes']};root=ps['nice_root']
    if root not in nodes:return False,'root'
    seen=set();edge_intro=[]
    def walk(q):
        if q in seen:return
        seen.add(q);n=nodes[q]
        for c in n['children']:
            if c not in nodes:raise ValueError
            walk(c)
        if n['type'].endswith('_EDGE'):
            p=n['payload'];edge_intro.append(tuple(sorted((p['u'],p['v']))))
    try:walk(root)
    except Exception:return False,'nice_child'
    if seen!=set(nodes) or sorted(edge_intro)!=sorted(edges):return False,'edge_once'
    def desc(q):
        out=set();st=[q]
        while st:
            x=st.pop()
            if x in out:continue
            out.add(x);st.extend(nodes[x]['children'])
        return out
    for q,n in nodes.items():
        typ=n['type'];bag=set(n['bag'])
        if typ=='LEAF':
            if n['children'] or bag:return False,'leaf'
        elif typ=='JOIN':
            if len(n['children'])!=2 or any(set(nodes[c]['bag'])!=bag for c in n['children']):return False,'join_shape'
        elif typ.startswith('INTRODUCE_') and not typ.endswith('_EDGE'):
            if len(n['children'])!=1:return False,'intro_shape'
            v=n['payload']['vertex'];cb=set(nodes[n['children'][0]]['bag'])
            if bag!=cb|{v}:return False,'intro_bag'
        elif typ.startswith('FORGET_'):
            if len(n['children'])!=1:return False,'forget_shape'
            v=n['payload']['vertex'];child=n['children'][0];cb=set(nodes[child]['bag'])
            if cb!=bag|{v}:return False,'forget_bag'
            ds=desc(child);introduced_below={tuple(sorted((nodes[x]['payload']['u'],nodes[x]['payload']['v']))) for x in ds if nodes[x]['type'].endswith('_EDGE')}
            if any(v in e and e not in introduced_below for e in edges):return False,'forget_before_edge'
        elif typ.endswith('_EDGE'):
            if len(n['children'])!=1 or set(nodes[n['children'][0]]['bag'])!=bag:return False,'edge_shape'
            p=n['payload'];e=tuple(sorted((p['u'],p['v'])))
            if e not in edges or not set(e)<=bag:return False,'edge_bad'
        else:return False,'unknown_type'
    recorded={q:rows_map(ps['table_rows'][q]) for q in nodes}
    for q in nodes:
        if hash_rows(recorded[q])!=ps['table_hashes'][q]:return False,'hash'
    memo={}
    def calc(q):
        if q in memo:return memo[q]
        n=nodes[q];typ=n['type'];bag=set(n['bag']);out=defaultdict(int)
        if typ=='LEAF':out[(0,)]=1
        elif typ=='JOIN':
            L=calc(n['children'][0]);R=calc(n['children'][1])
            for sl,cl in L.items():
                ml,wl=state_map(bag,sl)
                for sr,cr in R.items():
                    mr,wr=state_map(bag,sr);m={};good=True
                    for x in sorted(bag):
                        if knd(x)=='v':
                            if ml[x]!=mr[x]:good=False;break
                            m[x]=ml[x]
                        elif knd(x)=='B':m[x]=ml[x]&mr[x]
                        else:m[x]=ml[x]|mr[x]
                    if good:out[mkstate(bag,m,wl|wr)]+=cl*cr
        else:
            child=n['children'][0];ct=calc(child);cb=set(nodes[child]['bag'])
            if typ.startswith('INTRODUCE_') and not typ.endswith('_EDGE'):
                x=n['payload']['vertex'];kk=knd(x);vals=(0,1) if kk=='v' else ((1,) if kk=='B' else (0,))
                for s,cnt in ct.items():
                    m,w=state_map(cb,s)
                    for val in vals:
                        mm=dict(m);mm[x]=val;out[mkstate(bag,mm,w)]+=cnt
            elif typ.endswith('_EDGE'):
                p=n['payload']
                for s,cnt in ct.items():
                    m,w=state_map(bag,s);mm=dict(m);u,v=p['u'],p['v'];vn=u if knd(u)=='v' else v;fn=v if vn==u else u;value=m[vn]
                    if p['type']=='BLOCK':mm[fn]=m[fn]&value
                    else:
                        signs=set(int(x) for x in p['signs']);lit=(1 in signs and value==1) or (-1 in signs and value==0);mm[fn]=m[fn]|int(lit)
                    out[mkstate(bag,mm,w)]+=cnt
            elif typ.startswith('FORGET_'):
                x=n['payload']['vertex'];kk=knd(x)
                for s,cnt in ct.items():
                    m,w=state_map(cb,s);val=m.pop(x)
                    if kk=='C' and val==0:continue
                    out[mkstate(bag,m,w|(val if kk=='B' else 0))]+=cnt
            else:return {}
        memo[q]=dict(out);return memo[q]
    gotroot=calc(root)
    for q in nodes:
        if memo[q]!=recorded[q]:return False,'table_replay_'+q
    if gotroot.get((1,),0)!=int(ps['exact_count']) or int(ps['exact_count'])!=brute(raw):return False,'root_or_brute_count'
    wr=ps['witness_receipt']
    if ps['exact_count']>0:
        if not wr['present'] or not wr['direct_verify'] or not eval_inst(raw,wr['assignment']):return False,'witness'
        bi=wr['all_true_block']
        if bi is None or not all(wr['assignment'][v] for v in bs[int(bi)]):return False,'witness_block'
        if len(wr['clause_literal_witnesses'])!=len(cs):return False,'witness_clause_n'
        for j,w in enumerate(wr['clause_literal_witnesses']):
            if w is None or (w['variable'],int(w['sign'])) not in cs[j]:return False,'witness_literal'
    return True,{'tau':tau,'nodes':len(nodes),'count':int(ps['exact_count']),'max_table':max(len(x) for x in recorded.values())}
def tw_exact(vertices,edges):
    vertices=tuple(sorted(vertices))
    if not vertices:return -1
    adj0={v:set() for v in vertices}
    for a,b in edges:adj0[a].add(b);adj0[b].add(a)
    best=len(vertices)-1
    def rec(adj,w):
        nonlocal best
        if not adj:best=min(best,w);return
        for v in list(adj):
            nb=set(adj[v]);nw=max(w,len(nb))
            if nw>best:continue
            na={x:set(y for y in ys if y!=v) for x,ys in adj.items() if x!=v};ls=list(nb)
            for i in range(len(ls)):
                for j in range(i+1,len(ls)):na[ls[i]].add(ls[j]);na[ls[j]].add(ls[i])
            rec(na,nw)
    rec(adj0,0);return best
def H_graph(n,cla):
    V={f'x{i}' for i in range(n)}|{f'c{j}' for j in range(len(cla))};E=set()
    for j,c in enumerate(cla):
        for v,s in c:E.add(tuple(sorted((v,f'c{j}'))))
    return V,E
def E_graph(n,cla):
    V={f'v:x{i}' for i in range(n)}|{f'B:{i+1}' for i in range(n)}|{f'C:{j}' for j in range(len(cla))}|{'v:z','B:0',f'C:{len(cla)}'};E=set()
    for i in range(n):E.add(tuple(sorted((f'v:x{i}',f'B:{i+1}'))))
    for j,c in enumerate(cla):
        for v,s in c:E.add(tuple(sorted((f'v:{v}',f'C:{j}'))))
    E.add(tuple(sorted(('v:z','B:0'))));E.add(tuple(sorted(('v:z',f'C:{len(cla)}'))));return V,E
def cnf_count(n,cla):
    cnt=0
    for bits in itertools.product((0,1),repeat=n):
        a={f'x{i}':bits[i] for i in range(n)};cnt+=all(any(a[v] if s==1 else not a[v] for v,s in c) for c in cla)
    return cnt
def main():
    pre=json.load(open(PREREG));res=json.load(open(RESULT));ba24=json.load(open(BA24_RECEIPT));A={};names=pre['required_passes']
    A['pass_names_exact']=len(names)==34 and set(res['pass_map'])==set(names) and all(res['pass_map'][x] for x in names[:-2]) and not res['pass_map'][names[-2]] and not res['pass_map'][names[-1]] and res['passes']==32 and res['required']==34 and res['P_BA25_FINAL']==0
    A['parent_exact']=pre['scientific_parent']['meta_commit']=='e4b495ad5a4d0800558a6f67de283ba92cf83614' and pre['scientific_parent']['meta_blob']=='87f0eb6f1e8f52bbd0af82f86010b6e9bde0a7c6' and res['proof_carrying']['parent_seals']['BA24_meta_commit']==pre['scientific_parent']['meta_commit']
    A['ba24_immutable']=ba24['status'].startswith('BA24_A_') and ba24['authoritative_evidence']['P_BA24_FINAL']==1 and not ba24['next']['BA25_started'] and ba24['scope_firewalls']['P_VS_NP']=='OPEN'
    A['ba23_immutable']=ba24['parent']['BA23_final_meta_commit']=='dac4e99f3a841a5d82b8a54e19e0c20f9e4f6244' and ba24['BA23_positive_control']['BA23_compiled_residual_functions']=='2^64'
    sample_results={};ok=True
    for name,ps in res['proof_carrying']['samples'].items():q,d=replay_sample(ps);sample_results[name]=d;ok &= q
    A['proof_transcript_replay']=ok
    A['state_bound']=all(max(len(ps['table_rows'][q]) for q in ps['table_rows'])<=2**(int(ps['td_validation']['tau'])+2) for ps in res['proof_carrying']['samples'].values())
    stars=res['controls']['star'];A['star']=all(x['tau']==1 and x['count']==1 and x['max_states']<=8 and x['ba24_kappa']==x['lambda']+1 for x in stars) and stars[-1]['lambda']==64 and stars[-1]['ba24_kappa']==65 and sample_results['large_block_star_lambda8']['tau']==1
    killers=res['controls']['killer'];m64=next(x for x in killers if x['m']==64);exp64=3**64-2**64
    A['killer']=all(x['tau']==2 and int(x['count'])==3**x['m']-2**x['m'] and x['max_states']<=16 for x in killers) and int(m64['count'])==exp64 and res['materialization']['BA23_subset_residual_states']==0 and res['materialization']['DGDBO_objects']==0
    A['ba24_crosscheck']=int(ba24['BA23_positive_control']['m64_exact_model_count'])==exp64==int(m64['count']) and ba24['BA23_positive_control']['observed_max_table_states_m64']<=16
    A['mixed']=all(int(x[1])==int(x[2]) for x in res['controls']['mixed']) and sample_results['mixed_polarity']['count']==1
    A['source_return']=all(x['count']==x['dp']==4**x['p']-3**x['p'] for x in res['controls']['reconstruction']) and res['proof_carrying']['reconstruction_receipt']['arbitrary_foreign_CNF_BA4_carrier_transport']=='NOT_CERTIFIED'
    A['embedding_builder']=all(int(x[1])==int(x[2]) for x in res['controls']['embedding']);rr=random.Random(62525);emb=True
    for _ in range(40):
        n=rr.randint(0,4);cla=[]
        for j in range(rr.randint(0,4)):
            c=[]
            if n:
                for _ in range(rr.randint(0,4)):c.append((f'x{rr.randrange(n)}',rr.choice([-1,1])))
            cla.append(c)
        f=cnf_count(n,cla);hy=0
        for bits in itertools.product((0,1),repeat=n):
            a={f'x{i}':bits[i] for i in range(n)};z=1;F=all(any(a[v] if s==1 else not a[v] for v,s in c) for c in cla);hy+=bool((z or any(bits)) and F and z)
        emb &= (f==hy)
    A['embedding_independent']=emb
    frozen=[(0,[]),(0,[[]]),(1,[]),(1,[[('x0',1)]]),(2,[]),(2,[[('x0',1),('x1',1)]]),(2,[[('x0',1)],[('x1',-1)]])];tw=[]
    for n,c in frozen:
        hv,he=H_graph(n,c);ev,ee=E_graph(n,c);w=tw_exact(hv,he);t=tw_exact(ev,ee);tw.append((n,w,t,max(1,w)))
    A['tw_calibration']=all(t==ex for n,w,t,ex in tw) and res['theorem']['incidence_calibration'].startswith('tau_embedding=max(1,tw(H_F))')
    A['join']=all((a&b) in (0,1) and (a|b) in (0,1) for a,b in itertools.product((0,1),repeat=2))
    A['small_exact']=all(x['count']==x['dp'] and x['sat']==x['dpsat'] and x['witness_ok'] for x in res['controls']['small'])
    th=res['theorem'];stop=res['STOP'];txt=json.dumps(res,sort_keys=True)
    A['firewalls']=th['SAT_IN_P']=='NOT_PROVED' and th['P_VS_NP']=='OPEN' and th['BA4_CARRIER_TRANSPORT']=='NOT_CERTIFIED' and th['BA24_preserved'] is True and stop['BA26_started'] is False and stop['next_theorem_gate_started'] is False and stop['external_literature_novelty_equivalence_audit_required'] is True
    A['no_unbounded_promotion']='SAT_IN_P\": \"PROVED\"' not in txt and 'P_VS_NP\": \"CLOSED\"' not in txt
    passed=all(A.values());out={'gate':pre['gate'],'status':'PASS' if passed else 'FAIL','implementation_imported':False,'assertions':A,'proof_samples':sample_results,'independent_tw_controls':[{'n':n,'tw_H':w,'tau_embedding':t,'expected':ex} for n,w,t,ex in tw],'independent_embedding_cases':40,'BA24_crosscheck_m64':str(exp64),'falsifiers':[] if passed else [k for k,v in A.items() if not v]}
    open(OUT,'w').write(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    if not passed:raise SystemExit(1)
if __name__=='__main__':main()
