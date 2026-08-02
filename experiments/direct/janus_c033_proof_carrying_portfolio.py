#!/usr/bin/env python3
from __future__ import annotations
import argparse, itertools, json, hashlib, random
from dataclasses import dataclass
Clause=tuple[int,...];CNF=tuple[Clause,...]
def sat_clause(c,a):return any(a.get(abs(x),False)==(x>0) for x in c)
def sat_cnf(f,a):return all(sat_clause(c,a) for c in f)
def vars_of(f):return sorted({abs(x) for c in f for x in c})
def brute(f):
 v=vars_of(f)
 for b in itertools.product((False,True),repeat=len(v)):
  a=dict(zip(v,b))
  if sat_cnf(f,a):return a
 return None
def restrict(f,var,val):
 out=[]
 for c in f:
  if any(abs(x)==var and ((x>0)==val) for x in c):continue
  d=tuple(x for x in c if abs(x)!=var)
  if not d:return ((),)
  out.append(d)
 return tuple(out)
def horn(f):return all(sum(x>0 for x in c)<=1 for c in f)
def dual_horn(f):return all(sum(x<0 for x in c)<=1 for c in f)
def two_cnf(f):return all(len(c)<=2 for c in f)
def horn_solve(f):
 a={v:False for v in vars_of(f)};changed=True
 while changed:
  changed=False
  for c in f:
   pos=[x for x in c if x>0];neg=[-x for x in c if x<0]
   if all(a[v] for v in neg):
    if not pos:return None
    h=pos[0]
    if not a[h]:a[h]=True;changed=True
 return a if sat_cnf(f,a) else None
def dual_horn_solve(f):
 a=horn_solve(tuple(tuple(-x for x in c) for c in f))
 return None if a is None else {v:not z for v,z in a.items()}
def twosat_solve(f):
 vs=vars_of(f)
 if any(len(c)>2 for c in f):return None
 g={u:[] for v in vs for u in (v,-v)};rg={u:[] for u in g}
 def imp(a,b):g.setdefault(a,[]).append(b);rg.setdefault(b,[]).append(a)
 for c in f:
  if not c:return None
  if len(c)==1:imp(-c[0],c[0])
  else:a,b=c;imp(-a,b);imp(-b,a)
 seen=set();order=[]
 def dfs(u):
  seen.add(u)
  for v in g.get(u,()):
   if v not in seen:dfs(v)
  order.append(u)
 for u in list(g):
  if u not in seen:dfs(u)
 comp={}
 def rdfs(u,k):
  comp[u]=k
  for v in rg.get(u,()):
   if v not in comp:rdfs(v,k)
 k=0
 for u in reversed(order):
  if u not in comp:rdfs(u,k);k+=1
 for v in vs:
  if comp[v]==comp[-v]:return None
 a={v:comp[v]>comp[-v] for v in vs}
 if not sat_cnf(f,a):a={v:not z for v,z in a.items()}
 return a if sat_cnf(f,a) else None
@dataclass
class Node:
 kind:str;formula:CNF;var:int|None=None;left:'Node|None'=None;right:'Node|None'=None;witness:dict[int,bool]|None=None;leaf_class:str|None=None
def leaf_solve(f):
 if horn(f):return 'HORN',horn_solve(f)
 if dual_horn(f):return 'DUAL_HORN',dual_horn_solve(f)
 if two_cnf(f):return '2CNF',twosat_solve(f)
 return None,None
def build(f,budget):
 cls,w=leaf_solve(f)
 if cls is not None:return Node('LEAF',f,witness=w,leaf_class=cls),1
 if budget<=1:return Node('OPEN',f),1
 vs=vars_of(f)
 if not vs:return Node('LEAF',f,witness={} if f!=((),) else None,leaf_class='TRIVIAL'),1
 v=vs[0];l,nl=build(restrict(f,v,False),budget-1)
 if nl>=budget:return Node('OPEN',f),nl
 r,nr=build(restrict(f,v,True),budget-nl)
 if nl+nr+1>budget:return Node('OPEN',f),nl+nr+1
 return Node('BRANCH',f,var=v,left=l,right=r),nl+nr+1
def decide(n):
 if n.kind=='OPEN':return 'OPEN',None
 if n.kind=='LEAF':return ('SAT',n.witness) if n.witness is not None else ('UNSAT',None)
 ls,lw=decide(n.left);rs,rw=decide(n.right)
 if 'OPEN' in (ls,rs):return 'OPEN',None
 if ls=='SAT':w=dict(lw);w[n.var]=False;return 'SAT',w
 if rs=='SAT':w=dict(rw);w[n.var]=True;return 'SAT',w
 return 'UNSAT',None
def verify(n):
 if n.kind=='OPEN':return True
 if n.kind=='LEAF':
  cls,w=leaf_solve(n.formula)
  return cls==n.leaf_class and ((w is None)==(n.witness is None)) and (w is None or sat_cnf(n.formula,w))
 if n.var is None or n.left is None or n.right is None:return False
 return n.left.formula==restrict(n.formula,n.var,False) and n.right.formula==restrict(n.formula,n.var,True) and verify(n.left) and verify(n.right)
def run(seed=330033,cases=500):
 rng=random.Random(seed);mism=opens=0;classes={}
 for _ in range(cases):
  n=rng.randint(1,7);m=rng.randint(1,10)
  f=tuple(tuple(v if rng.getrandbits(1) else -v for v in rng.sample(range(1,n+1),rng.randint(1,min(3,n)))) for _ in range(m))
  t,_=build(f,256);assert verify(t);ans,w=decide(t);truth=brute(f)
  if ans=='OPEN':opens+=1;continue
  if (ans=='SAT')!=(truth is not None):mism+=1
  if ans=='SAT':assert w is not None and sat_cnf(f,w)
  st=[t]
  while st:
   x=st.pop()
   if x.kind=='LEAF':classes[x.leaf_class]=classes.get(x.leaf_class,0)+1
   elif x.kind=='BRANCH':st += [x.left,x.right]
 assert mism==0
 hard=((1,2,3),(-1,-2,-3),(1,-2,3),(-1,2,-3));t,_=build(hard,1);assert t.kind=='OPEN'
 r={'artifact_id':'C033-JANUS-PROOF-CARRYING-PORTFOLIO','status':'PASS','p_vs_np':'OPEN','cases':cases,'mismatches':mism,'opens':opens,'leaf_classes':classes,'theorem':'A polynomial-size verified decision tree whose leaves are admitted polynomial tractable classes yields polynomial SAT decision and witness recovery; UNSAT is certified by all leaves rejecting.','boundary':'Does not construct polynomial-size trees for arbitrary CNF.'}
 r['integrity_sha256']=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest();return r
def main():
 p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();r=run();print(json.dumps(r,indent=2,sort_keys=True));assert not a.self_test or (r['status']=='PASS' and r['mismatches']==0)
if __name__=='__main__':main()
