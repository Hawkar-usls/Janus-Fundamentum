import collections,hashlib,random
NS='JANUS-MK-BCEG-R2C-DISCOVERY-2026-08-30-A'
def seed(*p):return int.from_bytes(hashlib.sha256('|'.join(map(str,p)).encode()).digest()[:8],'big')
def canon(cs):
 out=[]
 for c in cs:
  s=set(c)
  if any(-x in s for x in s):continue
  out.append(tuple(sorted(s,key=lambda z:(abs(z),z<0))))
 out=sorted(set(out),key=lambda c:(len(c),c))
 if any(not c for c in out):return ((),)
 keep=[];ss=[]
 for c in out:
  q=set(c)
  if any(x.issubset(q) for x in ss):continue
  keep.append(c);ss.append(q)
 return tuple(keep)
def restrict(f,v,b):
 if f in ((),((),)):return f
 lit=v if b else -v;res=[]
 for c in f:
  if lit in c:continue
  if -lit in c:
   d=tuple(x for x in c if x!=-lit)
   if not d:return ((),)
   res.append(d)
  else:res.append(c)
 return canon(res)
def eval_cnf(f,a):return f!=((),) and all(any((x>0 and a[abs(x)]) or (x<0 and not a[abs(x)]) for x in c) for c in f)
def compile_obdd(f,order,cap=500000):
 memo={};uniq={};nodes={};nxt=[2]
 def rec(i,s):
  if s==():return 1
  if s==((),):return 0
  k=(i,s)
  if k in memo:return memo[k]
  v=order[i];lo=rec(i+1,restrict(s,v,0));hi=rec(i+1,restrict(s,v,1))
  if lo==hi:memo[k]=lo;return lo
  u=(v,lo,hi)
  if u not in uniq:
   uniq[u]=nxt[0];nodes[nxt[0]]=u;nxt[0]+=1
   if len(uniq)>cap:raise RuntimeError('OBDD_CAP')
  memo[k]=uniq[u];return memo[k]
 r=rec(0,canon(f));return {'root':r,'nodes':nodes,'total_nodes':len(uniq)+2}
def eval_obdd(c,a):
 i=c['root']
 while i not in (0,1):
  v,lo,hi=c['nodes'][i];i=hi if a[v] else lo
 return i==1
def make_pair(m,kind,inst):
 r=random.Random(seed(NS,m,kind,inst));ids=list(range(1,2*m+1));r.shuffle(ids);cs=[]
 for i in range(m):
  a,b=ids[2*i:2*i+2];cs += [(-a,b),(a,-b)] if kind=='RENAMED_EQ_PAIR' else [(-a,-b),(a,b)]
 return canon(cs)
def make_random(m,inst):
 r=random.Random(seed(NS,m,'MATCHED_RANDOM_2CNF_CONTROL',inst));cs=set()
 while len(cs)<2*m:
  a,b=r.sample(range(1,2*m+1),2);a=a if r.getrandbits(1) else -a;b=b if r.getrandbits(1) else -b;cs.add(tuple(sorted((a,b),key=lambda z:(abs(z),z<0))))
 return canon(cs)
def detect(f):
 work=0;mp=collections.defaultdict(list);vs=set()
 for c in f:
  work+=len(c)
  if len(c)!=2:return False,None,work
  a,b=c;vs|={abs(a),abs(b)};mp[tuple(sorted((abs(a),abs(b))))].append((1 if a>0 else -1,1 if b>0 else -1));work+=1
 partner={};pairs=[]
 for k,p in sorted(mp.items()):
  work+=1
  if len(p)!=2:continue
  a,b=k;work+=2
  if set(p) in ({(-1,1),(1,-1)},{(-1,-1),(1,1)}) and a not in partner and b not in partner:partner[a]=b;partner[b]=a;pairs.append((a,b))
 ok=len(partner)==len(vs)==2*len(pairs)
 if not ok:return False,None,work
 order=[]
 for a,b in sorted(pairs):order += [a,b];work+=2
 return True,order,work
def orders(f):
 vs=sorted({abs(x) for c in f for x in c});deg=collections.Counter(abs(x) for c in f for x in c);ok,p,w=detect(f);d={'NUMERIC_ORDER':vs,'DEGREE_ORDER':sorted(vs,key=lambda v:(deg[v],v))}
 if ok:d['PAIR_GRAPH_ORDER']=p
 return d,ok,w
def replay(f,comps):
 vs=sorted({abs(x) for c in f for x in c})
 for mask in range(1<<len(vs)):
  a={v:bool(mask>>i&1) for i,v in enumerate(vs)};t=eval_cnf(f,a)
  if any(eval_obdd(c,a)!=t for c in comps.values()):return 1
 return 0
