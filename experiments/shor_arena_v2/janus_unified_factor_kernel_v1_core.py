#!/usr/bin/env python3
import hashlib,json,math
from dataclasses import dataclass,field

PORTFOLIO=['DIRECT_GCD_FACTOR','EUCLIDEAN_GCD_CHAIN','DIFFERENCE_OF_SQUARES','MODULAR_POWER_EQUALITY','RESIDUE_COLLISION_ORDER_MULTIPLE','EXACT_MULTIPLICATIVE_ORDER','SHOR_POSTPROCESS_FACTOR','NEAR_SQUARE_EXACT_RELATION','SYMBOLIC_ARITHMETIC_FACTOR']
PROJECTIONS=['FACTOR_TERMINAL','COLLISION_TO_ORDER_DIVIDES','EXACT_ORDER_TO_SHOR_POST','DIFF_SQUARES_TO_GCD','NEAR_SQUARE_NO_PROJECTION_UNLESS_GCD']
ADAPTIVE=['SPIDER_ADVISORY_ONLY','M2R_EXACT_KEY_CAPABILITY_REPLAY','FINGERPRINT_RANKING_ONLY','PIPPI_NEXT_EPOCH_SWITCH_ONLY','KEYMASTER_NO_PRUNE','DELAYED_LEARNING','BOUNDARY_CERT_REQUIRED']
CAPS={'max_unique_payload_bytes':2_000_000,'max_serialized_certificate_bytes':4_000_000,'max_canonicalization_bytes':8_000_000,'max_lookup':2_000_000,'max_frontier_bytes':2_000_000}
def C(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(x):return hashlib.sha256(x).hexdigest()
def capability(extra=None):return H(C({'v':'UFKv1.2','portfolio':PORTFOLIO,'projections':PROJECTIONS,'adaptive':ADAPTIVE,'caps':CAPS,'extra':extra or {}}))
@dataclass
class Ledger:
 unique:int=0;refs:int=0;index:int=0;prov:int=0;canon:int=0;lookups:int=0;frontier:int=0;serialized:int=0;modmul:int=0;intmul:int=0;gcd:int=0;trial:int=0
 def d(self):return self.__dict__.copy()
@dataclass
class Node:
 id:str;lang:str;kind:str;payload:dict;size:int;prov:list=field(default_factory=list)
class Limit(Exception):pass
class DAG:
 def __init__(self,caps=None):self.n={};self.L=Ledger();self.caps=dict(CAPS if caps is None else caps);self.front=[]
 def chk(self):
  L=self.L;c=self.caps
  if L.unique>c['max_unique_payload_bytes'] or L.serialized>c['max_serialized_certificate_bytes']:raise Limit('OPEN_REPRESENTATION_VOLUME')
  if L.canon>c['max_canonicalization_bytes'] or L.lookups>c['max_lookup']:raise Limit('OPEN_CANONICALIZATION_BUDGET')
  if L.frontier>c['max_frontier_bytes']:raise Limit('OPEN_INTERFACE_VOLUME')
 def add(self,lang,kind,payload,prov):
  b=C({'language':lang,'kind':kind,'payload':payload});self.L.canon+=len(b);i=H(b);self.L.lookups+=1;new=i not in self.n
  if new:self.n[i]=Node(i,lang,kind,json.loads(json.dumps(payload)),len(b));self.L.unique+=len(b);self.L.index+=len(i)+len(lang)+len(kind)
  pb=len(C(prov));self.n[i].prov.append(json.loads(json.dumps(prov)));self.L.prov+=pb;self.L.serialized+=len(b)+pb;self.L.refs+=len(i);self.chk();return i,new
 def get(self,i):self.L.lookups+=1;self.chk();return self.n[i]
 def set_front(self,ids):self.front=list(ids);self.L.frontier=max(self.L.frontier,sum(self.n[i].size+len(i) for i in ids));self.chk()
 def profile(self):
  q={};rel=res=order=0
  for i in self.front:
   n=self.n[i];z=q.setdefault(n.lang,{'nodes':0,'bytes':0});z['nodes']+=1;z['bytes']+=n.size
   rel+=n.kind in ('NEAR_SQUARE','DIFFERENCE_OF_SQUARES');res+=('RESIDUE' in n.kind or 'MODULAR' in n.kind);order+=('ORDER' in n.kind)
  return {'dag_frontier_nodes':len(self.front),'active_exact_relation_nodes':rel,'active_residue_generators':res,'active_order_constraints':order,'active_message_language_ids':sorted(q),'per_language_frontier':q,'unresolved_cross_language_join_count':max(0,len(q)-1),'largest_single_message_bytes':max([self.n[i].size for i in self.front] or [0]),'unique_semantic_payload_bytes':self.L.unique}
class Spider:
 def __init__(self):self.e=[]
 def add(self,a,b,s):self.e.append((a,b,float(s)))
 def certifies(self,*_):return False
class M2R:
 def __init__(self,cap):self.cap=cap;self.i={}
 def remember(self,nid,lang,replay):self.i[(self.cap,nid)]={'node_id':nid,'language':lang,'replay_digest':replay}
 def get(self,nid,cap):
  if cap!=self.cap:return {'status':'CAPABILITY_MISMATCH'}
  return {'status':'EXACT_RETRIEVAL_CANDIDATE','record':self.i[(cap,nid)]} if (cap,nid) in self.i else {'status':'MISS'}
 def similarity_authority(self):return False
class Selector:
 def __init__(self,c):self.c=list(c);self.s={x:0. for x in c};self.p=[]
 def rank(self):return sorted(self.c,key=lambda x:(-self.s[x],self.c.index(x)))
 def log(self,c,u,e):self.p.append((c,float(u),e))
 def close(self,e):
  keep=[]
  for c,u,x in self.p:
   if x<e:self.s[c]=.9*self.s[c]+.1*u
   else:keep.append((c,u,x))
  self.p=keep
class Pippi:
 def __init__(self):self.e=[]
 def record(self,e,l,w,b,a,t):self.e.append((e,l,w,b,a,t))
 def next_switch(self,e,k=3):
  p=[x for x in self.e if x[0]<e]
  if len(p)<k:return 'NO_SIGNAL'
  w=p[-k:]
  return 'NEXT_EPOCH_LANGUAGE_SWITCH_CANDIDATE' if len({x[1] for x in w})==1 and all(x[4]>=x[3] for x in w) and all(x[5] not in ('FACTOR_FOUND','TERMINAL_FACTOR') for x in w) else 'NO_SIGNAL'
def fp(profile):return H(C({k:profile[k] for k in ['dag_frontier_nodes','active_message_language_ids','per_language_frontier','unresolved_cross_language_join_count','largest_single_message_bytes']}))
def pw(a,e,n):
 r=1;b=a%n;m=0
 while e:
  if e&1:r=r*b%n;m+=1
  e//=2
  if e:b=b*b%n;m+=1
 return r,m
def exact_order(a,n,d,L):
 g=d;y=g;q=2;fs=[]
 while q*q<=y:
  L.trial+=1
  if y%q==0:
   fs.append(q)
   while y%q==0:y//=q
  q=3 if q==2 else q+2
 if y>1:fs.append(y)
 for p in fs:
  while g%p==0:
   v,c=pw(a,g//p,n);L.modmul+=c
   if v==1:g//=p
   else:break
 v,c=pw(a,g,n);L.modmul+=c
 if v!=1:return None
 for p in set(fs):
  if g%p==0:
   v,c=pw(a,g//p,n);L.modmul+=c
   if v==1:return None
 return g
def project(D,i,state):
 n=D.get(i);N=state['N'];p=n.payload
 if n.kind=='FACTOR':
  g=p['g'];return {'status':'TERMINAL_FACTOR','factor':g} if 1<g<N and N%g==0 else {'status':'CERTIFICATE_FAILURE'}
 if n.kind=='RESIDUE_COLLISION':
  vi,ci=pw(p['a'],p['i'],N);vj,cj=pw(p['a'],p['j'],N);D.L.modmul+=ci+cj
  if vi!=p['ri'] or vj!=p['rj'] or vi!=vj or p['i']==p['j']:return {'status':'CERTIFICATE_FAILURE'}
  d=abs(p['i']-p['j']);j,_=D.add('RESIDUE_COLLISION_ORDER_MULTIPLE','ORDER_DIVIDES',{'N':N,'a':p['a'],'divides':d,'source':i},{'rule':'COLLISION_TO_ORDER_DIVIDES'})
  return {'status':'EXACT_PROJECTION','node':j,'ord_divides':d}
 if n.kind=='EXACT_ORDER':
  r=exact_order(p['a'],N,p['r'],D.L)
  if r!=p['r']:return {'status':'CERTIFICATE_FAILURE'}
  if r%2:return {'status':'EXACT_PROJECTION','exact_order':r}
  h,c=pw(p['a'],r//2,N);D.L.modmul+=c
  if h==N-1:return {'status':'EXACT_PROJECTION','exact_order':r,'shor_unusable':True}
  for z in (h-1,h+1):
   g=math.gcd(z,N);D.L.gcd+=1
   if 1<g<N:
    j,_=D.add('SHOR_POSTPROCESS_FACTOR','FACTOR',{'N':N,'g':g,'source':i},{'rule':'ORDER_TO_FACTOR'});return {'status':'TERMINAL_FACTOR','factor':g,'node':j}
 if n.kind=='DIFFERENCE_OF_SQUARES':
  x,y=p['x'],p['y'];D.L.intmul+=2
  if x*x-y*y!=N:return {'status':'CERTIFICATE_FAILURE'}
  for z in (x-y,x+y):
   g=math.gcd(z,N);D.L.gcd+=1
   if 1<g<N:
    j,_=D.add('DIRECT_GCD_FACTOR','FACTOR',{'N':N,'g':g,'source':i},{'rule':'DIFF_SQUARES_GCD'});return {'status':'TERMINAL_FACTOR','factor':g,'node':j}
  return {'status':'NO_TRACTABLE_PROJECTION'}
 if n.kind=='NEAR_SQUARE':
  x,y,e=p['x'],p['y'],p['epsilon'];D.L.intmul+=2
  if x*x-N-y*y!=e:return {'status':'CERTIFICATE_FAILURE'}
  for z in (x-y,x+y,e):
   g=math.gcd(abs(z),N);D.L.gcd+=1
   if 1<g<N:
    j,_=D.add('DIRECT_GCD_FACTOR','FACTOR',{'N':N,'g':g,'source':i},{'rule':'NEAR_GCD'});return {'status':'TERMINAL_FACTOR','factor':g,'node':j}
  return {'status':'NO_TRACTABLE_PROJECTION','retained_full_relation':True}
 return {'status':'NO_TRACTABLE_PROJECTION','symbolic_exact_node':n.kind in ('PRODUCT','POWER','MODULAR_EQUALITY','ORDER_DIVIDES','GCD_CONSTRAINT','FACTOR_CANDIDATE')}
def join(D,a,b,c=None):
 A,B=D.get(a),D.get(b)
 if a==b:return {'status':'SAFE_IDENTICAL_MERGE','node':a}
 if not c:return {'status':'OPEN_NO_CERTIFIED_BOUNDARY_JOIN'}
 Cc=D.get(c)
 if Cc.kind!='CONSISTENCY_CERT' or Cc.payload!={'left':a,'right':b,'verified':True}:return {'status':'CERTIFICATE_FAILURE'}
 j,_=D.add('BOUNDARY_GATED_COMPOSITION','CERTIFIED_JOIN',{'left':a,'right':b,'cert':c},{'rule':'BOUNDARY_JOIN'});return {'status':'EXACT_JOIN','node':j}
def open_receipt(D,t,cap,reason):return {'terminal':t,'capability_digest':cap,'reason':reason,'frontier_node_ids':list(D.front),'interface_profile':D.profile(),'ledger':D.L.d(),'immutable':True}
def tests():
 T=[];cap=capability();D=DAG();p={'N':15,'a':2,'e':4,'residue':1};a,n1=D.add('MODULAR_POWER_EQUALITY','MODULAR_EQUALITY',p,{'r':'A'});b,n2=D.add('MODULAR_POWER_EQUALITY','MODULAR_EQUALITY',p,{'r':'B'});assert a==b and n1 and not n2 and len(D.n[a].prov)==2;T+=['hash_cons_multi_provenance']
 c,_=D.add('MODULAR_POWER_EQUALITY','MODULAR_EQUALITY',{'N':15,'a':4,'e':2,'residue':1},{'r':'C'});assert c!=a;T+=['full_operands_no_false_collapse']
 bad,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':35,'x':10,'y':7,'epsilon':15},{'r':'bad'});assert project(D,bad,{'N':35})['status']=='CERTIFICATE_FAILURE'
 near,_=D.add('NEAR_SQUARE_EXACT_RELATION','NEAR_SQUARE',{'N':21,'x':5,'y':0,'epsilon':4},{'r':'near'});assert project(D,near,{'N':21})['status']=='NO_TRACTABLE_PROJECTION';T+=['near4_no_fake_projection']
 ri=pow(2,1,15);rj=pow(2,5,15);col,_=D.add('RESIDUE_COLLISION_ORDER_MULTIPLE','RESIDUE_COLLISION',{'N':15,'a':2,'i':1,'j':5,'ri':ri,'rj':rj},{'r':'col'});assert project(D,col,{'N':15})['ord_divides']==4;T+=['collision_order_divides_only']
 eo,_=D.add('EXACT_MULTIPLICATIVE_ORDER','EXACT_ORDER',{'N':15,'a':2,'r':4},{'r':'order'});assert project(D,eo,{'N':15})['status']=='TERMINAL_FACTOR';T+=['exact_order_factor']
 sym,_=D.add('SYMBOLIC_ARITHMETIC_FACTOR','PRODUCT',{'N':15,'left':3,'right':5},{'r':'sym'});assert project(D,sym,{'N':15})['status']=='NO_TRACTABLE_PROJECTION';T+=['symbolic_nonvoting']
 D.set_front([near,col,eo,sym]);P=D.profile();assert len(P['active_message_language_ids'])==4 and D.L.serialized>0;T+=['language_interface_accounting']
 Q=DAG({**CAPS,'max_unique_payload_bytes':100});ok=False
 try:Q.add('X','Y',{'blob':'x'*400},{'r':'cap'})
 except Limit:ok=True
 assert ok;T+=['hash_pointer_cheat_rejected']
 cap2=capability({'x':1});assert cap!=cap2;T+=['capability_changes']
 S=Spider();S.add('a','b',.9);assert not S.certifies();T+=['spider_not_proof']
 R=Selector(['A','B']);z=R.rank();R.log('B',10,5);assert R.rank()==z;R.close(5);assert R.rank()==z;R.close(6);assert R.rank()[0]=='B' and set(R.rank())=={'A','B'};T+=['delayed_learning_no_prune']
 M=M2R(cap);M.remember(near,D.n[near].lang,H(C(D.n[near].payload)));assert M.get(near,cap)['status']=='EXACT_RETRIEVAL_CANDIDATE' and M.get(near,cap2)['status']=='CAPABILITY_MISMATCH' and not M.similarity_authority();assert project(D,near,{'N':21})['status']=='NO_TRACTABLE_PROJECTION';T+=['m2r_capability_replay']
 f1=fp(P);assert f1==fp(P) and len(f1)==64;T+=['fingerprint_ranking_only']
 J=Pippi();[J.record(e,'ORDER',100,10,11,'OPEN_DISCOVERY_BUDGET') for e in (1,2,3)];assert J.next_switch(3)=='NO_SIGNAL' and J.next_switch(4).startswith('NEXT_EPOCH');T+=['pippi_next_epoch_switch']
 assert join(D,near,col)['status']=='OPEN_NO_CERTIFIED_BOUNDARY_JOIN';cc,_=D.add('BOUNDARY_GATED_COMPOSITION','CONSISTENCY_CERT',{'left':near,'right':col,'verified':True},{'r':'cc'});assert join(D,near,col,cc)['status']=='EXACT_JOIN';T+=['boundary_cert_join']
 O=open_receipt(D,'OPEN_NO_TRACTABLE_PROJECTION',cap,'test');assert O['immutable'] and O['frontier_node_ids']==D.front and O['interface_profile']['active_message_language_ids']==D.profile()['active_message_language_ids'];T+=['open_exact_frontier_witness']
 return {'status':'PASS','tests':T,'test_count':len(T),'capability_digest':cap,'ledger':D.L.d(),'interface_profile':P}
if __name__=='__main__':
 d=tests();print(json.dumps(d,indent=2))
