from __future__ import annotations
from collections import defaultdict
from itertools import product
from pathlib import Path
import json, random, sys
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'trump_apma_compositional_synthesis'
sys.path.insert(0,str(PREV))
import core as primitives

def xor_clauses(vs,rhs):
    out=[]
    for bits in product([0,1],repeat=len(vs)):
        if (sum(bits)&1)!=rhs: out.append([(-v if b else v) for v,b in zip(vs,bits)])
    return out

def template(kind,d,role='NEUTRAL',param=0):
    v=1
    def nv():
        nonlocal v
        x=v; v+=1; return x
    ports=[nv() for _ in range(d)]; cnf=[]
    if kind==0:
        if d not in (2,3): raise ValueError(('q0-degree',d))
        cnf.append(list(ports))
        for i,a in enumerate(ports):
            for b in ports[i+1:]: cnf.append([-a,-b])
    elif kind==1:
        if role=='IMPLICATION_CHALLENGE':
            if d!=2: raise ValueError(role)
            p0,p1=ports; u0,u1=nv(),nv(); cnf=[[-p0,p1],[p0,u0],[p1,u1]]
        elif role=='CONST_TRUE':
            p=ports[0]; a=nv(); cnf=[[p,a],[p,-a]]
        elif role=='CONST_FALSE':
            p=ports[0]; a,u=nv(),nv(); cnf=[[-p,a],[-p,-a],[p,u]]
        elif role=='DENSE_EQ4':
            if d!=4: raise ValueError(role)
            for i in range(4):
                a,b=ports[i],ports[(i+1)%4]; cnf.extend([[-a,b],[-b,a]])
            for p in ports: cnf.append([p,nv()])
        else:
            if d==1:
                p=ports[0]; cnf=[[p,nv()]]
            elif d==2:
                p0,p1=ports; cnf=[[-p0,p1],[p0,nv()],[p1,nv()]]
            elif d==3:
                p0,p1,p2=ports; cnf=[[-p0,p1],[p0,nv()],[p1,nv()],[p2,nv()],[p2,nv()]]
            else: raise ValueError(('q1-degree',d))
    elif kind==2:
        h=nv()
        if role=='GATE_FALSE_PARENT':
            p0=ports[0]; a,u0,w0=nv(),nv(),nv(); cnf=[[-p0,a],[-p0,-a],[-p0,-u0,w0],[-p0,h]]
            for p in ports[1:]:
                u,w=nv(),nv(); cnf.extend([[-p,h],[-p,-u,w]])
        else:
            if d>=2: cnf.append([-ports[0],ports[1]])
            for p in ports:
                u,w=nv(),nv(); cnf.extend([[-p,h],[-p,-u,w]])
    elif kind==3:
        if role in ('CONST_TRUE','CONST_FALSE'):
            if d!=1: raise ValueError(role)
            p=ports[0]; a,b=nv(),nv(); target=1 if role=='CONST_TRUE' else 0
            cnf.extend(xor_clauses([p,a,b],0)); cnf.extend(xor_clauses([a,b],target))
        elif role=='WIDTH4_PARITY':
            if d!=4: raise ValueError(role)
            h=nv(); cnf.extend(xor_clauses([ports[0],ports[1],h],0)); cnf.extend(xor_clauses([h,ports[2],ports[3]],0))
        else:
            if d==1:
                a,b=nv(),nv(); cnf.extend(xor_clauses([ports[0],a,b],param&1))
            elif d==2: cnf.extend(xor_clauses(ports,param&1))
            elif d==3: cnf.extend(xor_clauses(ports,param&1))
            else: raise ValueError(('q3-degree',d))
    else: raise ValueError(kind)
    return {'kind':kind,'degree':d,'role':role,'param':param,'cnf':cnf,'ports':ports,'nvars':v-1}

def designated_ok(m):
    s=primitives.QS[m['kind']](m['cnf']); z=primitives.RS[m['kind']](s) if s is not None else None
    return s is not None and isinstance(z,dict) and z.get('decision')=='SAT'

def port_degrees(m): return [sum(sum(abs(x)==p for x in c) for c in m['cnf']) for p in m['ports']]

def brute_relation(m):
    vs=list(range(1,m['nvars']+1)); out=set()
    for bits in product([0,1],repeat=len(vs)):
        a={v:bool(b) for v,b in zip(vs,bits)}
        if all(any((x>0 and a[abs(x)]) or (x<0 and not a[abs(x)]) for x in c) for c in m['cnf']):
            out.add(tuple(int(a[p]) for p in m['ports']))
    return out

def topology(k,name,seed):
    if name in ('short_path','long_path'): return [(i,i+1) for i in range(k-1)]
    if k<3: return [(0,1)]
    edges=[(0,1),(1,2)]
    if name=='balanced_binary_tree':
        q=[2]; nxt=3
        while nxt<k:
            p=q.pop(0)
            for _ in range(2):
                if nxt>=k: break
                edges.append((p,nxt)); q.append(nxt); nxt+=1
    elif name=='irregular_degree_leq3':
        rng=random.Random(seed); child=defaultdict(int); cand=[2]
        for nxt in range(3,k):
            avail=[x for x in cand if child[x]<2]; p=rng.choice(avail); edges.append((p,nxt)); child[p]+=1; cand.append(nxt)
    elif name=='broom_star_like_degree_leq3':
        if k>3: edges.append((2,3))
        if k>4: edges.append((2,4))
        tails=[3,4]; nxt=5; turn=0
        while nxt<k:
            p=tails[turn%len(tails)]; edges.append((p,nxt)); tails[turn%len(tails)]=nxt; nxt+=1; turn+=1
    else: raise ValueError(name)
    return edges

def rooted(edges,root):
    adj=defaultdict(list)
    for ei,(a,b) in enumerate(edges): adj[a].append((b,ei)); adj[b].append((a,ei))
    parent={root:None}; pedge={root:None}; order=[root]
    for u in order:
        for v,e in adj[u]:
            if v not in parent: parent[v]=u; pedge[v]=e; order.append(v)
    return adj,parent,pedge,order

def choose_modules(k,edges,seed):
    deg=[0]*k
    for a,b in edges: deg[a]+=1; deg[b]+=1
    mods=[None]*k
    if k>=3:
        mods[0]=template(3,1,'CONST_TRUE'); mods[1]=template(1,2,'IMPLICATION_CHALLENGE'); mods[2]=template(2,deg[2],'GATE_FALSE_PARENT')
        cycle=[0,3,1,2]; ci=0
        for i in range(3,k):
            if deg[i]==1: mods[i]=template(3,1,'NEUTRAL',seed+i)
            else:
                kind=cycle[ci%len(cycle)]; ci+=1; mods[i]=template(kind,deg[i],'NEUTRAL',seed+i)
    else: raise ValueError('choose_modules requires k>=3')
    return mods

def make_port_map(k,edges,mods,truth):
    adj,parent,pedge,order=rooted(edges,2); pm=[{} for _ in range(k)]
    e01=next(i for i,e in enumerate(edges) if set(e)=={0,1}); e12=next(i for i,e in enumerate(edges) if set(e)=={1,2})
    pm[0][e01]=0
    if truth=='UNSAT': pm[1][e01]=0; pm[1][e12]=1
    else: pm[1][e01]=1; pm[1][e12]=0
    pm[2][e12]=0; rest=[e for _,e in adj[2] if e!=e12]
    for j,e in enumerate(sorted(rest),start=1): pm[2][e]=j
    for i in range(3,k):
        pe=pedge[i]; pm[i][pe]=0; rest=[e for _,e in adj[i] if e!=pe]
        for j,e in enumerate(sorted(rest),start=1): pm[i][e]=j
    return pm

def tree_sat(edges,mods,pm,root=2):
    adj,parent,pedge,order=rooted(edges,root); rel=[brute_relation(m) for m in mods]; feasible={}
    for u in reversed(order):
        vals=set(); root_ok=False
        for tup in rel[u]:
            ok=True
            for v,e in adj[u]:
                if parent.get(v)==u:
                    val=tup[pm[u][e]]
                    if val not in feasible[v]: ok=False; break
            if not ok: continue
            if parent[u] is None: root_ok=True; break
            vals.add(tup[pm[u][pedge[u]]])
        feasible[u]=vals if parent[u] is not None else ({0,1} if root_ok else set())
    return bool(feasible[root])

def assemble(edges,mods,pm):
    base=[]; next_id=1
    for m in mods:
        mp={v:next_id+v-1 for v in range(1,m['nvars']+1)}; next_id+=m['nvars']; base.append(mp)
    repl={}
    for ei,(a,b) in enumerate(edges):
        pa=mods[a]['ports'][pm[a][ei]]; pb=mods[b]['ports'][pm[b][ei]]; shared=10_000_000+ei
        repl[base[a][pa]]=shared; repl[base[b][pb]]=shared
    cnf=[]; comp_vars=[]
    for i,m in enumerate(mods):
        cv=set()
        for c in m['cnf']:
            z=[]
            for lit in c:
                g=base[i][abs(lit)]; g=repl.get(g,g); cv.add(g); z.append(g if lit>0 else -g)
            cnf.append(z)
        comp_vars.append(sorted(cv))
    return cnf,comp_vars

def transport(cnf,seed,encoder):
    rng=random.Random(seed); vs=sorted({abs(x) for c in cnf for x in c})
    if encoder=='cal_encoder_v1': new=[100000+19*i for i in range(1,len(vs)+1)]; rng.shuffle(new)
    elif encoder=='adm_encoder_v2': new=[400000+17*i for i in range(1,len(vs)+1)]; rng.shuffle(new)
    elif encoder=='hold_encoder_v3': new=[700000+13*i for i in range(len(vs),0,-1)]
    else: raise ValueError(encoder)
    mp=dict(zip(vs,new)); out=[]
    for c in cnf:
        z=[mp[abs(x)] if x>0 else -mp[abs(x)] for x in c]; rng.shuffle(z); out.append(z)
    rng.shuffle(out); original=list(out); out.extend([list(c) for c in original])
    fresh=max(new)+101; out.append([fresh,-fresh])
    if encoder=='hold_encoder_v3': out=list(reversed(out))
    return out

def metrics(cnf):
    real=[c for c in cnf if not any(-x in c for x in c)]; d=defaultdict(int); wh=defaultdict(int); pos=neg=0
    for c in real:
        wh[len(c)]+=1
        for x in c: d[abs(x)]+=1; pos+=x>0; neg+=x<0
    return {'n':len(d),'m':len(real),'width_hist':[list(x) for x in sorted(wh.items())],'degree_multiset':sorted(d.values()),'pos':pos,'neg':neg}

def canonical_no_units(cnf): return all(len(c)!=1 for c in primitives.canon(cnf))

def make_pair(split,pair_index,k,toponame,seed):
    edges=topology(k,toponame,seed); mods=choose_modules(k,edges,seed); enc={'cal':'cal_encoder_v1','adm':'adm_encoder_v2','hold':'hold_encoder_v3'}[split]
    cases=[]; hidden=[]
    for truth in ('SAT','UNSAT'):
        pm=make_port_map(k,edges,mods,truth); semantic=tree_sat(edges,mods,pm)
        if semantic!=(truth=='SAT'): raise AssertionError(('SEMANTIC_CONSTRUCTION_FAIL',k,toponame,truth,semantic))
        raw,comp_vars=assemble(edges,mods,pm); cnf=transport(raw,seed+9001,enc); cid=f'{split}-pair{pair_index:02d}-{truth.lower()}'
        if not canonical_no_units(cnf): raise AssertionError(('UNIT_CLAUSE',cid))
        cases.append({'id':cid,'cnf':cnf,'truth':truth if split=='cal' else None,'encoder':enc,'pair_id':f'{split}-pair{pair_index:02d}'})
        hidden.append((cid,truth,{'kinds':[m['kind'] for m in mods],'roles':[m['role'] for m in mods],'component_vars':comp_vars,'edges':edges,'port_map':pm,'topology':toponame},metrics(cnf)))
    if hidden[0][3]!=hidden[1][3]: raise AssertionError(('PAIR_METRIC_DRIFT',hidden[0][0],hidden[0][3],hidden[1][3]))
    return cases,hidden,{'pair_id':f'{split}-pair{pair_index:02d}','metrics_equal':True,'metrics':hidden[0][3],'k':k,'topology':toponame,'mechanisms':sorted(set(hidden[0][2]['kinds']))}

def make_k2(rep,truth):
    m0=template(3,1,'CONST_TRUE'); m1=template(1,1,'CONST_TRUE') if truth=='SAT' else template(2,1,'GATE_FALSE_PARENT')
    edges=[(0,1)]; mods=[m0,m1]; pm=[{0:0},{0:0}]
    # direct relation join
    r0=brute_relation(m0); r1=brute_relation(m1); semantic=any(a[0]==b[0] for a in r0 for b in r1)
    if semantic!=(truth=='SAT'): raise AssertionError(('K2',truth,semantic))
    raw,cv=assemble(edges,mods,pm); cnf=transport(raw,1500+rep*10+(truth=='UNSAT'),'cal_encoder_v1'); cid=f'cal-k2-r{rep}-{truth.lower()}'
    return {'id':cid,'cnf':cnf,'truth':truth,'encoder':'cal_encoder_v1','pair_id':None},(cid,truth,{'kinds':[m0['kind'],m1['kind']],'roles':[m0['role'],m1['role']],'component_vars':cv,'edges':edges,'port_map':pm,'topology':'single_edge_hidden_fact_pair'},metrics(cnf))

def cycle_control(seed):
    k=6; edges=[(i,(i+1)%k) for i in range(k)]; kinds=[0,1,2,3,0,3]; mods=[template(kinds[i],2,'NEUTRAL',seed+i) for i in range(k)]
    inc=[[] for _ in range(k)]
    for ei,(a,b) in enumerate(edges): inc[a].append(ei); inc[b].append(ei)
    pm=[]
    for i in range(k): pm.append({e:j for j,e in enumerate(sorted(inc[i]))})
    raw,_=assemble(edges,mods,pm); return raw,{'kinds':kinds,'edges':edges,'control':'CONTROL_CYCLE'}

def width4_control(seed):
    m0=template(1,4,'DENSE_EQ4'); m1=template(3,4,'WIDTH4_PARITY'); edges=[(0,1)]*4
    # assemble repeated pair edges manually with four distinct ports
    mods=[m0,m1]; base=[]; nxt=1
    for m in mods:
        mp={v:nxt+v-1 for v in range(1,m['nvars']+1)}; nxt+=m['nvars']; base.append(mp)
    repl={}
    for e in range(4):
        shared=11_000_000+e; repl[base[0][m0['ports'][e]]]=shared; repl[base[1][m1['ports'][e]]]=shared
    cnf=[]
    for i,m in enumerate(mods):
        for c in m['cnf']:
            cnf.append([(repl.get(base[i][abs(x)],base[i][abs(x)]) if x>0 else -repl.get(base[i][abs(x)],base[i][abs(x)])) for x in c])
    return cnf,{'kinds':[1,3],'shared_width':4,'control':'CONTROL_WIDTH_4'}

def main():
    audit_specs=[template(3,1,'CONST_TRUE'),template(1,2,'IMPLICATION_CHALLENGE'),template(2,3,'GATE_FALSE_PARENT'),template(0,2),template(0,3),template(1,3),template(2,2),template(3,3)]
    audit=[{'kind':m['kind'],'degree':m['degree'],'role':m['role'],'designated_admitted':designated_ok(m),'port_degrees':port_degrees(m),'relation_size':len(brute_relation(m)),'has_unit':not canonical_no_units(m['cnf'])} for m in audit_specs]
    if not all(x['designated_admitted'] and not x['has_unit'] for x in audit): raise AssertionError(audit)
    cal=[]; adm=[]; hold=[]; truth={}; pair_audit=[]
    for rep in range(2):
        for tr in ('SAT','UNSAT'):
            c,h=make_k2(rep,tr); cal.append(c); cid,tt,meta,met=h; truth[cid]={'truth':tt,'split':'cal','hidden_meta':meta,'metrics':met}
    idx=0
    for rep in range(2):
        for k,name in [(3,'short_path'),(4,'short_path')]:
            cs,hid,a=make_pair('cal',idx,k,name,1600+rep*100+idx); idx+=1; cal.extend(cs); pair_audit.append(a)
            for cid,tr,meta,met in hid: truth[cid]={'truth':tr,'split':'cal','hidden_meta':meta,'metrics':met}
    adm_specs=[(5,'long_path'),(8,'balanced_binary_tree'),(12,'irregular_degree_leq3'),(16,'long_path')]
    idx=0
    for rep in range(2):
        for k,name in adm_specs:
            cs,hid,a=make_pair('adm',idx,k,name,2600+rep*100+idx); idx+=1; adm.extend([{kk:vv for kk,vv in c.items() if kk!='truth'} for c in cs]); pair_audit.append(a)
            for cid,tr,meta,met in hid: truth[cid]={'truth':tr,'split':'admission','hidden_meta':meta,'metrics':met}
    hold_specs=[(5,'balanced_binary_tree'),(8,'irregular_degree_leq3'),(12,'broom_star_like_degree_leq3'),(16,'balanced_binary_tree')]
    idx=0
    for rep in range(2):
        for k,name in hold_specs:
            cs,hid,a=make_pair('hold',idx,k,name,3600+rep*100+idx); idx+=1; hold.extend([{kk:vv for kk,vv in c.items() if kk!='truth'} for c in cs]); pair_audit.append(a)
            for cid,tr,meta,met in hid: truth[cid]={'truth':tr,'split':'holdout','hidden_meta':meta,'metrics':met}
    controls=[]; ctruth={}
    for j in range(2):
        raw,meta=cycle_control(4600+j); cnf=transport(raw,5600+j,'hold_encoder_v3'); cid=f'control-cycle-{j}'; controls.append({'id':cid,'control':'CONTROL_CYCLE','cnf':cnf,'encoder':'hold_encoder_v3'}); ctruth[cid]={'hidden_meta':meta}
        raw,meta=width4_control(4700+j); cnf=transport(raw,5700+j,'hold_encoder_v3'); cid=f'control-width4-{j}'; controls.append({'id':cid,'control':'CONTROL_WIDTH_4','cnf':cnf,'encoder':'hold_encoder_v3'}); ctruth[cid]={'hidden_meta':meta}
    allcases=cal+adm+hold+controls
    if not all(canonical_no_units(c['cnf']) for c in allcases): raise AssertionError('whole population contains unit clause')
    (ROOT/'calibration.json').write_text(json.dumps({'cases':cal},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_admission.json').write_text(json.dumps({'cases':adm},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_holdout.json').write_text(json.dumps({'cases':hold},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_controls.json').write_text(json.dumps({'cases':controls},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_truth.json').write_text(json.dumps({'targets':truth,'controls':ctruth},indent=2,sort_keys=True),encoding='utf-8')
    report={'version':'v1.1','template_audit':audit,'counts':{'calibration':len(cal),'admission':len(adm),'holdout':len(hold),'controls':len(controls)},'pair_audit':pair_audit,'all_pair_metrics_equal':all(x['metrics_equal'] for x in pair_audit),'whole_population_no_unit_clauses':True,'interaction_only_design':'hidden GF2 true leaf + hidden Horn false gate + asymmetric 2CNF implication; SAT/UNSAT differs only by swapping equal-degree implication ports','controls':['genuine mixed cycle','genuine four-shared-port coupled interface']}
    (ROOT/'POPULATION_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'counts':report['counts'],'pairs':len(pair_audit),'pair_metrics':report['all_pair_metrics_equal'],'no_units':report['whole_population_no_unit_clauses'],'audit':audit},sort_keys=True))
if __name__=='__main__': main()
