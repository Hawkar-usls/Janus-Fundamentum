#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random, sqlite3

SCHEMA='janus.cross_language_negotiation.v1'; POLICY='UNARY_SHARED_CONSEQUENCE_FIXPOINT_V1'

def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def dg(x): return hashlib.sha256(cj(x).encode()).hexdigest()
def norm(f):
 out=[]
 for c in f:
  s=set(c)
  if any(-x in s for x in s): continue
  q=tuple(sorted(s,key=lambda x:(abs(x),x<0)))
  if q not in out: out.append(q)
 out.sort(key=lambda c:(len(c),c)); keep=[]
 for c in out:
  if not any(set(d)<=set(c) for d in keep): keep.append(c)
 return tuple(keep)
def horn(f): return all(sum(x>0 for x in c)<=1 for c in f)
def ec(c,a): return any(a[abs(x)]==(x>0) for x in c)
def eh(f,a): return all(ec(c,a) for c in f)
def ea(rows,a): return all(sum(int(a[i+1]) for i in range(max(1,max(a))) if m>>i&1)%2==b for m,b in rows)

class OpenBudget(Exception): pass
class Meter:
 def __init__(s,limit): s.limit=limit;s.work=s.hcalls=s.acalls=s.scans=s.xors=0
 def q(s,k=1):
  s.work+=k
  if s.work>s.limit: raise OpenBudget

def hsolve(f,n,u,M):
 M.hcalls+=1;M.q(); cs=list(norm(f))+[((v,) if b else (-v,)) for v,b in sorted(u.items())];cs=norm(cs);a={i:False for i in range(1,n+1)};tr=[]
 if not horn(cs): return {'status':'OPEN_LANGUAGE'}
 ch=True
 while ch:
  ch=False
  for j,c in enumerate(cs):
   M.scans+=1;M.q(); p=next((x for x in c if x>0),None);body=[-x for x in c if x<0]
   if all(a[v] for v in body):
    if p is None:return {'status':'UNSAT','trace':tr+[{'op':'conflict','clause':j}]}
    if not a[p]:a[p]=True;tr.append({'op':'set','var':p,'clause':j});ch=True
 assert eh(cs,a);return {'status':'SAT','assignment':a,'trace':tr}
def asolve(rows,n,u,M):
 M.acalls+=1;M.q(); ext=[(m,b,1<<i) for i,(m,b) in enumerate(rows)];base=len(ext)
 ext += [(1<<(v-1),int(b),1<<(base+j)) for j,(v,b) in enumerate(sorted(u.items()))]
 B={};ops=[]
 for i,(m,b,p) in enumerate(ext):
  while m:
   k=(m&-m).bit_length()-1
   if k not in B:B[k]=(m,b,p);ops.append(['p',i,k+1]);break
   q,r,s=B[k];m^=q;b^=r;p^=s;M.xors+=1;M.q();ops.append(['x',i,k+1])
  if not m and b:return {'status':'UNSAT','provenance':p,'row_ops':ops}
 a={i:False for i in range(1,n+1)}
 for k in sorted(B,reverse=True):
  m,b,_=B[k];v=b
  for i in range(n):
   if i!=k and m>>i&1:v^=int(a[i+1])
  a[k+1]=bool(v)
 assert ea(rows,a);return {'status':'SAT','assignment':a,'row_ops':ops}
def forced(lang,obj,n,u,v,M):
 for b in (False,True):
  q=dict(u);q[v]=b;r=hsolve(obj,n,q,M) if lang=='HORN' else asolve(obj,n,q,M)
  if r['status']=='UNSAT':return {'var':v,'value':not b,'native_proof':r}
 return None

def payloads(h,a,n):
 H={'language':'HORN','n':n,'clauses':[list(c) for c in norm(h)]};A={'language':'AFFINE_GF2','n':n,'rows':[list(r) for r in a]}
 H['digest']=dg(H);A['digest']=dg(A);return H,A
def finish(c,M):
 c['cost']={'work_units':M.work,'horn_calls':M.hcalls,'affine_calls':M.acalls,'horn_clause_scans':M.scans,'row_xors':M.xors,'step_count':len(c.get('events',[]))};c['cost']['certificate_bytes']=len(cj(c));c['integrity']={'sha256':dg(c)};return c

def pingpong(h,a,n,shared,budget=200000,initial=None):
 h=norm(h)
 if not horn(h):return {'schema':SCHEMA,'terminal':{'status':'OPEN_LANGUAGE'}}
 M=Meter(budget);H,A=payloads(h,a,n);u=dict(initial or {});c={'schema':SCHEMA,'policy':POLICY,'modules':[H,A],'shared_vars':sorted(set(shared)),'initial_facts':[{'var':v,'value':b} for v,b in sorted(u.items())],'events':[]}
 try:
  while True:
   for L,O,S in [('HORN',h,hsolve),('AFFINE_GF2',a,asolve)]:
    r=S(O,n,u,M)
    if r['status']=='UNSAT':c['terminal']={'status':'CONFLICT','module':L,'native_proof':r};return finish(c,M)
   add=False
   for L,O in [('HORN',h),('AFFINE_GF2',a)]:
    for v in c['shared_vars']:
     if v in u:continue
     q=forced(L,O,n,u,v,M)
     if q:
      q|={'seq':len(c['events']),'kind':'ENTAILED_LITERAL','producer':L,'fact_id':dg({'v':v,'b':q['value']})[:24]};c['events'].append(q);u[v]=q['value'];add=True;break
    if add:break
   if not add:c['terminal']={'status':'OPEN_FIXPOINT','facts':[{'var':v,'value':b} for v,b in sorted(u.items())],'reason':'fixpoint is not compatibility'};return finish(c,M)
 except OpenBudget:c['terminal']={'status':'OPEN_BUDGET','budget':budget};return finish(c,M)

def affine_to_horn(h,a,n,budget=200000):
 h=norm(h);M=Meter(budget);H,A=payloads(h,a,n);c={'schema':SCHEMA,'policy':'AFFINE_TO_HORN_DIRECTED_INCLUSION_V1','modules':[H,A],'events':[]}
 try:
  r=asolve(a,n,{},M)
  if r['status']=='UNSAT':c['terminal']={'status':'AFFINE_EMPTY_SUBSET','native_proof':r};return finish(c,M)
  for j,cl in enumerate(h):
   u={abs(x):x<0 for x in cl};r=asolve(a,n,u,M)
   if r['status']=='SAT':
    w=r['assignment'];assert ea(a,w) and not ec(cl,w);c['terminal']={'status':'SEPARATOR','direction':'AFFINE_NOT_HORN','assignment':{str(v):int(w[v]) for v in w},'clause_index':j};return finish(c,M)
   c['events'].append({'seq':len(c['events']),'kind':'AFFINE_ENTAILS_HORN_CLAUSE','clause_index':j,'falsifying_units':u,'provenance':r['provenance'],'row_ops':r['row_ops']})
  c['terminal']={'status':'DIRECTED_INCLUSION','relation':'MODELS(AFFINE) SUBSET MODELS(HORN)','reverse_direction':'OPEN'};return finish(c,M)
 except OpenBudget:c['terminal']={'status':'OPEN_BUDGET','budget':budget};return finish(c,M)
def verify_directed(c,h,a,n):
 t=c['terminal']
 if t['status']=='SEPARATOR':
  w={int(v):bool(b) for v,b in t['assignment'].items()};return ea(a,w) and not eh(norm(h),w)
 if t['status'] in ('DIRECTED_INCLUSION','AFFINE_EMPTY_SUBSET'):
  M=Meter(10**8);return all(asolve(a,n,{abs(x):x<0 for x in cl},M)['status']=='UNSAT' for cl in norm(h))
 return t['status']=='OPEN_BUDGET'
def verify_ping(c,h,a,n):
 u={x['var']:bool(x['value']) for x in c.get('initial_facts',[])};M=Meter(10**8)
 for e in c.get('events',[]):
  q=forced(e['producer'],norm(h) if e['producer']=='HORN' else a,n,u,e['var'],M)
  if not q or q['value']!=bool(e['value']):return False
  u[e['var']]=bool(e['value'])
 t=c['terminal']['status']
 if t=='CONFLICT':return hsolve(norm(h),n,u,M)['status']=='UNSAT' or asolve(a,n,u,M)['status']=='UNSAT'
 if t=='OPEN_FIXPOINT':return all(forced(L,O,n,u,v,M) is None for v in c['shared_vars'] if v not in u for L,O in [('HORN',norm(h)),('AFFINE_GF2',a)])
 return t=='OPEN_BUDGET'

def initdb(db):db.executescript('''CREATE TABLE IF NOT EXISTS proof_blob(proof_digest BLOB PRIMARY KEY,payload BLOB) WITHOUT ROWID;CREATE TABLE IF NOT EXISTS negotiation_certificate(cert_digest BLOB PRIMARY KEY,pattern_digest BLOB UNIQUE,policy TEXT,terminal_code TEXT,step_count INT,work_units INT,certificate_bytes INT) WITHOUT ROWID;CREATE TABLE IF NOT EXISTS negotiation_step(cert_digest BLOB,seq INT,opcode TEXT,producer TEXT,var_id INT,bool_value INT,proof_digest BLOB,PRIMARY KEY(cert_digest,seq)) WITHOUT ROWID;''')
def cache(db,c):
 initdb(db);raw=cj(c).encode();ch=hashlib.sha256(raw).digest();pk=bytes.fromhex(dg({'s':c['schema'],'p':c['policy'],'m':[x['digest'] for x in c['modules']],'v':c.get('shared_vars',[]),'i':c.get('initial_facts',[])}))
 db.execute('INSERT OR IGNORE INTO negotiation_certificate VALUES(?,?,?,?,?,?,?)',(ch,pk,c['policy'],c['terminal']['status'],len(c.get('events',[])),c['cost']['work_units'],c['cost']['certificate_bytes']))
 for i,e in enumerate(c.get('events',[])):
  p=cj(e.get('native_proof',{})).encode();ph=hashlib.sha256(p).digest();db.execute('INSERT OR IGNORE INTO proof_blob VALUES(?,?)',(ph,p));db.execute('INSERT OR IGNORE INTO negotiation_step VALUES(?,?,?,?,?,?,?)',(ch,i,e['kind'],e.get('producer'),e.get('var'),int(bool(e.get('value'))) if 'value'in e else None,ph))
 db.commit();return ch.hex()

def models(h,a,n):
 out=[]
 for bits in itertools.product((False,True),repeat=n):
  w={i+1:bits[i] for i in range(n)}
  if eh(h,w) and ea(a,w):out.append(w)
 return out
def rh(R,n,m):
 z=[]
 for _ in range(m):
  body=R.sample(range(1,n+1),R.randint(0,min(3,n)));rest=[v for v in range(1,n+1) if v not in body];head=R.choice(rest) if rest and R.random()<.65 else None;z.append(tuple([-v for v in body]+([head] if head else [])))
 return norm(z)
def ra(R,n,m):
 z=[]
 for _ in range(m):
  mask=0
  while not mask:
   for i in range(n):
    if R.random()<.45:mask|=1<<i
  z.append((mask,R.randrange(2)))
 return tuple(z)
def run():
 R=random.Random(37037);conf=op=0
 for _ in range(400):
  n=R.randint(1,6);h=rh(R,n,R.randint(1,9));a=ra(R,n,R.randint(1,6));d=affine_to_horn(h,a,n,10**6);assert verify_directed(d,h,a,n);p=pingpong(h,a,n,range(1,n+1),10**6);assert verify_ping(p,h,a,n)
  if p['terminal']['status']=='CONFLICT':assert not models(h,a,n);conf+=1
  else:op+=1
 h=norm(((-1,2),(1,-2)));a=((3,1),);p=pingpong(h,a,2,(1,2));assert p['terminal']['status']=='OPEN_FIXPOINT' and not models(h,a,2)
 hn=norm(((-4,-5,-6),));an=((0b001001,1),(0b010010,1),(0b100100,1));assert pingpong(hn,an,6,range(1,7))['terminal']['status']=='OPEN_FIXPOINT'
 ht=norm(((1,),(2,),(3,)));at=((7,0),);q=pingpong(ht,at,3,(1,2,3));assert q['terminal']['status']=='CONFLICT'
 db=sqlite3.connect(':memory:');k=cache(db,q);counts=[db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('negotiation_certificate','negotiation_step','proof_blob')];assert k==cache(db,q) and counts==[db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('negotiation_certificate','negotiation_step','proof_blob')]
 print(cj({'status':'PASS','random_directional_checks':400,'random_conflicts':conf,'random_open_fixpoints':op,'literal_only_equality_neq':'OPEN_ON_JOINTLY_UNSAT','nand3_neq_image':'OPEN','tseitin_unit_parity':'CERTIFIED','sqlite_cache_idempotent':True,'p_vs_np':'OPEN'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();run() if a.self_test else p.error('use --self-test')
