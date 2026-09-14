from __future__ import annotations
from collections import defaultdict, deque
from pathlib import Path
import json, hashlib, random, re

ROOT=Path('experiments/trump_apma_nonschema')
raw=json.loads((ROOT/'candidate_raw.json').read_text(encoding='utf-8-sig'))
prereg=json.loads((ROOT/'PREREG_2026-09-14.json').read_text(encoding='utf-8-sig'))
source=(ROOT/'discovery_gate.py').read_text()
rows={r['name']:r for r in raw['rows']}

# Independent generic parser/extractor: no import of candidate implementation.
def canon(cnf):
    out=set()
    for c in cnf:
        s=set(c)
        if any(-x in s for x in s): continue
        out.add(tuple(sorted(s,key=lambda x:(abs(x),x<0))))
    return [frozenset(c) for c in sorted(out,key=lambda c:(len(c),tuple(sorted(c,key=lambda x:(abs(x),x)))))]

def collapse(cnf):
    cnf=canon(cnf); parent={abs(x):abs(x) for c in cnf for x in c}
    def f(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def u(a,b):
        a,b=f(a),f(b)
        if a!=b: parent[b]=a
    imp=set()
    for c in cnf:
        if len(c)==2:
            a,b=sorted(c,key=lambda x:abs(x))
            if a<0 and b>0: imp.add((-a,b))
            elif b<0 and a>0: imp.add((-b,a))
    for a,b in list(imp):
        if (b,a) in imp: u(a,b)
    reps={x:f(x) for x in parent}
    out=[]
    for c in cnf:
        z=set()
        for lit in c:
            r=reps[abs(lit)]; z.add(r if lit>0 else -r)
        out.append(frozenset(z))
    return canon(out),reps

def independent_relation(cnf):
    cnf,reps=collapse(cnf); pos=[c for c in cnf if c and all(x>0 for x in c)]; neg=[c for c in cnf if len(c)==2 and all(x<0 for x in c)]
    owner={}
    for i,b in enumerate(pos):
        for x in b:
            if x in owner:return None
            owner[x]=i
    if set(owner)!={abs(x) for c in cnf for x in c}: return None
    pairs={tuple(sorted(-x for x in c)) for c in neg}
    for b in pos:
        xs=sorted(b)
        for i,a in enumerate(xs):
            for z in xs[i+1:]:
                if (min(a,z),max(a,z)) not in pairs:return None
    adj=defaultdict(set)
    for a,b in pairs:
        if owner[a]!=owner[b]: adj[a].add(b); adj[b].add(a)
    unseen=set(owner); comps=[]
    while unseen:
        s=next(iter(unseen)); unseen.remove(s); q=[s]; comp={s}
        while q:
            x=q.pop()
            for y in adj[x]:
                if y in unseen: unseen.remove(y); comp.add(y); q.append(y)
        comps.append(frozenset(comp))
    co={x:i for i,c in enumerate(comps) for x in c}
    for c in comps:
        xs=sorted(c); blocks=set()
        for x in xs:
            if owner[x] in blocks:return None
            blocks.add(owner[x])
        for i,a in enumerate(xs):
            for b in xs[i+1:]:
                if (min(a,b),max(a,b)) not in pairs:return None
    allowed=set(pos)|set(neg)
    if any(c not in allowed for c in cnf):return None
    edges={i:set() for i in range(len(pos))}
    for x,i in owner.items(): edges[i].add(co[x])
    if any(not e for e in edges.values()):return None
    return pos,comps,edges,reps

def solve(rel):
    pos,comps,edges=rel[:3]; mr={}
    def aug(u,seen):
        for v in sorted(edges[u]):
            if v in seen:continue
            seen.add(v)
            if v not in mr or aug(mr[v],seen):mr[v]=u;return True
        return False
    for u in range(len(pos)):
        if not aug(u,set()):
            S={u};N=set();q=deque([u])
            while q:
                a=q.popleft()
                for v in sorted(edges[a]):
                    if v in N:continue
                    N.add(v)
                    if v in mr and mr[v] not in S:S.add(mr[v]);q.append(mr[v])
            return 'UNSAT',S,N,None
    ml={u:v for v,u in mr.items()};return 'SAT',None,None,ml

def replay(cnf,assignment):
    return all(any((x>0 and assignment.get(abs(x),False)) or (x<0 and not assignment.get(abs(x),False)) for x in c) for c in cnf)

def make_graph(m,n,seed,degree=3):
    rng=random.Random(seed)
    for _ in range(2000):
        e=set()
        for u in range(m):
            a=list(range(n));rng.shuffle(a)
            for v in a[:degree]:e.add((u,v))
        if len({v for _,v in e})<n:continue
        rd=defaultdict(int)
        for u,v in e:rd[v]+=1
        if max(rd.values())<=5:return sorted(e)
    raise RuntimeError('graph')

def make_sat_graph(n,seed,degree=3):
    rng=random.Random(seed);e={(u,u) for u in range(n)}
    for u in range(n):
        a=[v for v in range(n) if v!=u];rng.shuffle(a)
        for v in a[:degree-1]:e.add((u,v))
    return sorted(e)

def encode(m,n,e):
    L=defaultdict(list);R=defaultdict(list)
    for u,v in e:L[u].append(v);R[v].append(u)
    c=[]
    for u in range(m):
        xs=[100000*u+v+1 for v in sorted(L[u])];c.append(frozenset(xs))
        for i,a in enumerate(xs):
            for b in xs[i+1:]:c.append(frozenset((-a,-b)))
    for v in range(n):
        xs=[100000*u+v+1 for u in sorted(R[v])]
        for i,a in enumerate(xs):
            for b in xs[i+1:]:c.append(frozenset((-a,-b)))
    return canon(c)

def stable(s):return int.from_bytes(hashlib.sha256(s.encode()).digest()[:2],'big')
def rename(cnf,seed):
    rng=random.Random(seed);vs=sorted({abs(x) for c in cnf for x in c});nv=vs[:];rng.shuffle(nv);mp=dict(zip(vs,[1000000+x for x in nv]));out=[]
    for c in cnf:
        z=[mp[abs(x)] if x>0 else -mp[abs(x)] for x in c];rng.shuffle(z);out.append(frozenset(z))
    rng.shuffle(out);return canon(out)
def noise(cnf,seed):
    rng=random.Random(seed);out=list(cnf);vs=sorted({abs(x) for c in cnf for x in c});base=max(vs)+1
    for i in range(max(1,len(vs)//8)):z=base+i;out.append(frozenset((z,-z)))
    out += [rng.choice(out) for _ in range(min(5,len(out)))]
    return canon(out)
def equiv(cnf,seed):
    rng=random.Random(seed);vs=sorted({abs(x) for c in cnf for x in c});base=max(vs)+1000;mp={v:base+i for i,v in enumerate(vs)};out=list(cnf)
    for v,y in mp.items():out += [frozenset((-v,y)),frozenset((-y,v))]
    rng.shuffle(out);return canon(out)
def decoy(cnf):
    vs=sorted({abs(x) for c in cnf for x in c});return canon(list(cnf)+[frozenset((vs[0],-vs[1],vs[2]))])
def cross(seed):
    rng=random.Random(seed);vs=list(range(1,25));return canon([frozenset(rng.sample(vs,3)) for _ in range(32)])

# Discovery-layer blind-source firewall.
start=source.index('def discover_h3'); end=source.index('def solve_relation')
discovery_source=source[start:end].lower()
forbidden=['php','fp​hp','pigeon','hole','matching','hall','cardinality','sat','unsat']
firewall_hits=[x for x in forbidden if x in discovery_source]
fixed_probe_guard='probes=(discover_h0,discover_h1,discover_h2,discover_h3)' in source

expected={}
for n,seed in [(8,11),(10,17),(12,23)]:
    expected[f'hidden_unsat_{n}']=(encode(n+1,n,make_graph(n+1,n,seed)),'UNSAT')
    expected[f'hidden_sat_{n}']=(encode(n,n,make_sat_graph(n,seed+100)),'SAT')
base=encode(9,8,make_graph(9,8,41))
controls={'CONTROL_A_DECOY':(decoy(base),None),'CONTROL_B_CROSS':(cross(92),None)}
for name,(cnf,truth) in list(expected.items()):
    for tag,fn in [('rename',lambda x,s:rename(x,s)),('noise',lambda x,s:noise(x,s)),('equiv',lambda x,s:equiv(x,s))]:
        expected[name+'_'+tag]=(fn(cnf,stable(name+tag)),truth)

fail=[]; exact_ok=True; gen_ok=True
for name,(cnf,truth) in expected.items():
    rel=independent_relation(cnf)
    if rel is None:fail.append((name,'no-independent-carrier'));gen_ok=False;continue
    dec,S,N,ml=solve(rel)
    if dec!=truth:fail.append((name,'decision-mismatch'));exact_ok=False
    if dec=='SAT':
        ass={}
        pos,comps,edges,reps=rel
        for u,v in ml.items():
            xs=[x for x in pos[u] if x in comps[v]]
            if len(xs)!=1:fail.append((name,'nonunique-reconstruction'));exact_ok=False
            else:ass[xs[0]]=True
        for c in pos:
            for x in c:ass.setdefault(x,False)
        ass_root={x:ass.get(reps.get(x,x),False) for x in reps}
        if not replay(cnf,ass_root):fail.append((name,'root-replay-fail'));exact_ok=False
    else:
        if not S or not N or len(N)>=len(S):fail.append((name,'bad-deficient-witness'));exact_ok=False
for name,(cnf,_) in controls.items():
    if independent_relation(cnf) is not None:fail.append((name,'false-positive-carrier'));gen_ok=False

# Compare the recorded discovery population to the independent result.
for name in expected:
    r=rows.get(name)
    if not r or r.get('discovery')!='H3':fail.append((name,'recorded-discovery-mismatch'));gen_ok=False
for name in controls:
    r=rows.get(name)
    if not r or r.get('discovery')!='NO_CANDIDATE':fail.append((name,'recorded-control-mismatch'));gen_ok=False

result={
  'artifact':'TRUMP-APMA-NONSCHEMA-POLYTIME-QUOTIENT-DISCOVERY-FALSIFIER-HUNT-2026-09-14',
  'independent_source_firewall':{'forbidden_hits':firewall_hits,'fixed_four_hypotheses':fixed_probe_guard},
  'population':{'hidden_target_cases':len(expected),'controls':len(controls),'sat_unsat_mixed':True},
  'verdicts':{
    'DISCOVERY_PASS':len(firewall_hits)==0 and fixed_probe_guard and not fail,
    'GENERALIZATION_PASS':gen_ok and len(expected)==24,
    'EXACTNESS_ADMISSION':exact_ok and gen_ok,
    'FALSIFIED':bool(fail),
    'NONSCHEMA_DISCOVERY_FALSIFIED':bool(fail)
  },
  'failures':fail,
  'candidate_raw_sha256':hashlib.sha256((ROOT/'candidate_raw.json').read_bytes()).hexdigest(),
  'scientific_firewall':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0}
}
print(json.dumps(result,sort_keys=True,separators=(',',':')))

