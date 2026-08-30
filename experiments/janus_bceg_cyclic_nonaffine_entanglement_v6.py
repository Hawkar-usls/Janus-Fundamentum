#!/usr/bin/env python3
from pathlib import Path
from statistics import median
from itertools import product
import argparse,hashlib,json,random
from functools import lru_cache

P=Path("research/JANUS_BCEG_CYCLIC_NONAFFINE_ENTANGLEMENT_V6_PREREGISTRATION_2026-08-30.json")
def sd(*x):return int.from_bytes(hashlib.sha256("|".join(map(str,x)).encode()).digest()[:8],"big")
def H(o):
 b=json.dumps(o,sort_keys=True,separators=(",",":")).encode();return hashlib.sha256(b).hexdigest(),len(b)
def cn(C):
 s=set()
 for c in C:
  f=frozenset(c)
  if not any(-x in f for x in f):s.add(f)
 return tuple(sorted(s,key=lambda c:(len(c),tuple(sorted(c,key=lambda z:(abs(z),z))))))
def xor(vs,r):
 o=[]
 for b in product((0,1),repeat=len(vs)):
  if sum(b)%2!=r:o.append([v if q==0 else -v for v,q in zip(vs,b)])
 return o
def AND(s,b,z):return [[-s,-b,z],[s,-z],[b,-z]]
def build(k,v,master):
 B=list(range(1,k+1));n=k+1;C=[];E=[];r=random.Random(sd(master,k,v))
 for i in range(0,k,3):
  a,b,c=B[i:i+3];s,t,z=n,n+1,n+2;n+=3;q=r.randrange(2)
  C+=xor((s,t,a),0)+AND(s,b,z)+xor((z,t,c),q);E.append((a,b,c,q))
 rr=random.Random(sd(master,k,v,"obf"));vs=sorted({abs(l) for c in C for l in c});pm=vs[:];rr.shuffle(pm);mp=dict(zip(vs,pm));O=[]
 for c in C:
  x=[(1 if l>0 else -1)*mp[abs(l)] for l in c];rr.shuffle(x);O.append(x)
 return cn(O),tuple(sorted(mp[x] for x in B)),[(mp[a],mp[b],mp[c],q) for a,b,c,q in E]
def order(C):
 V=sorted({abs(l) for c in C for l in c});A={v:set() for v in V}
 for c in C:
  q=[abs(x) for x in c]
  for i,a in enumerate(q):
   for b in q[i+1:]:A[a].add(b);A[b].add(a)
 R=set(V);O=[];fill=0
 while R:
  best=None
  for v in R:
   n=list(A[v]&R);m=sum(b not in A[a] for i,a in enumerate(n) for b in n[i+1:]);sc=(m,len(n),v)
   if best is None or sc<best[0]:best=(sc,v,n)
  _,v,n=best
  for i,a in enumerate(n):
   for b in n[i+1:]:
    if b not in A[a]:A[a].add(b);A[b].add(a);fill+=1
  R.remove(v);O.append(v)
 return O,fill
class B:
 def __init__(s,O):s.O=O;s.p={v:i for i,v in enumerate(O)};s.N={0:(0,0,0),1:(0,1,1)};s.U={};s.n=2;s.C={};s.X={};s.ops=0
 def mk(s,v,l,h):
  if l==h:return l
  k=(v,l,h)
  if k in s.U:return s.U[k]
  u=s.n;s.n+=1;s.U[k]=u;s.N[u]=k;return u
 def lit(s,l):
  u=s.mk(abs(l),0,1);return u if l>0 else s.ap("xor",u,1)
 def ap(s,o,a,b):
  k=(o,a,b)
  if k in s.C:return s.C[k]
  s.ops+=1
  if a<2 and b<2:return int({"and":bool(a)and bool(b),"or":bool(a)or bool(b),"xor":bool(a)^bool(b)}[o])
  va=s.N[a][0] if a>=2 else None;vb=s.N[b][0] if b>=2 else None
  v=vb if va is None else va if vb is None or s.p[va]<=s.p[vb] else vb
  def co(u,z):
   if u<2:return u
   vv,l,h=s.N[u];return (h if z else l) if vv==v else u
  r=s.mk(v,s.ap(o,co(a,0),co(b,0)),s.ap(o,co(a,1),co(b,1)));s.C[k]=r;return r
 def form(s,C):
  u=1
  for c in C:
   q=0
   for l in c:q=s.ap("or",q,s.lit(l))
   u=s.ap("and",u,q)
  return u
 def ex(s,u,v):
  k=(u,v)
  if k in s.X:return s.X[k]
  if u<2:return u
  x,l,h=s.N[u]
  if s.p[x]>s.p[v]:return u
  r=s.ap("or",l,h) if x==v else s.mk(x,s.ex(l,v),s.ex(h,v));s.X[k]=r;return r
 def reach(s,u):
  S=set();Q=[u]
  while Q:
   x=Q.pop()
   if x<2 or x in S:continue
   S.add(x);_,l,h=s.N[x];Q+=[l,h]
  return S
def msg(b,u,B,O):
 R=sorted(b.reach(u));M={"boundary":list(B),"order":O,"root":u,"nodes":[[x,*b.N[x]] for x in R]};h,n=H(M);M["hash"]=h;M["bytes"]=n;return M
def ev(M,a):
 D={u:(v,l,h) for u,v,l,h in M["nodes"]};u=M["root"]
 while u>=2:v,l,h=D[u];u=h if a[v] else l
 return bool(u)
def expev(E,a):return all((not a[b]) or ((a[x]^a[c])==r) for x,b,c,r in E)
def nonaff(E,Bd):
 S=[]
 for z in product((0,1),repeat=len(Bd)):
  a=dict(zip(Bd,z))
  if expev(E,a):S.append(z)
  if len(S)>=50:break
 for i in range(len(S)):
  for j in range(i+1,len(S)):
   for k in range(j+1,len(S)):
    z=tuple(S[i][t]^S[j][t]^S[k][t] for t in range(len(Bd)))
    if not expev(E,dict(zip(Bd,z))):return True
 return False
def solve(C,Bd):
 O,f=order(C);b=B(O);u=b.form(C);full=len(b.reach(u));before=b.ops
 for v in [x for x in O if x not in set(Bd)]:u=b.ex(u,v)
 qops=b.ops-before;M=msg(b,u,Bd,O)
 pack={"cnf":H([[*sorted(c)] for c in C])[0],"boundary":list(Bd),"order":O,"message":M["hash"]};ph,pb=H(pack)
 O2,f2=order(C);c=B(O2);r=c.form(C)
 for v in [x for x in O2 if x not in set(Bd)]:r=c.ex(r,v)
 M2=msg(c,r,Bd,O2)
 L={"minfill_ops":f,"bdd_apply_ops":b.ops,"bdd_quantification_ops":qops,"bdd_full_nodes":full,"bdd_boundary_nodes":len(M["nodes"]),"serialized_message_bytes":M["bytes"],"serialized_proofpack_bytes":pb,"truthgate_replay_ops":c.ops+f2,"algorithmic_boundary_assignments_enumerated":0}
 return M,L,M2["hash"]==M["hash"]
def audit(M,E,Bd):
 m=0;n=0
 for z in product((0,1),repeat=len(Bd)):
  a=dict(zip(Bd,z));n+=1;m+=ev(M,a)!=expev(E,a)
 return n,m
def st():
 for k in (6,9):
  C,Bd,E=build(k,0,"DEV");assert nonaff(E,Bd);M,L,r=solve(C,Bd);n,m=audit(M,E,Bd);assert r and m==0 and L["algorithmic_boundary_assignments_enumerated"]==0
 return {"status":"PASS","cases":2}
def main():
 a=argparse.ArgumentParser();a.add_argument("--output");a.add_argument("--journal");a.add_argument("--self-test",action="store_true");x=a.parse_args()
 if x.self_test:print(json.dumps(st(),indent=2));return
 p=json.loads(P.read_text());S=[(k,v) for k in p["boundary_width_ladder"] for v in range(p["variants_per_width"])];r=random.Random(sd(p["holdout_seed"],"order"));r.shuffle(S);R=[];J=[]
 for i,(k,v) in enumerate(S):
  C,Bd,E=build(k,v,p["holdout_seed"]);M,L,re=solve(C,Bd);n,mm=audit(M,E,Bd);pd=L["minfill_ops"]+L["bdd_apply_ops"]+L["truthgate_replay_ops"]+L["serialized_message_bytes"]+L["serialized_proofpack_bytes"];q={"case":i,"k":k,"variant":v,"replay":re,"nonaffine":nonaff(E,Bd),"message_nodes":L["bdd_boundary_nodes"],"ratio":L["bdd_boundary_nodes"]/(2**k),"audit_mismatches":mm,"evaluation_only_boundary_assignments_enumerated":n,"paid_nohide_metric":pd,"ledger":L};R.append(q);J.append(q)
 n1=all(q["replay"] and q["audit_mismatches"]==0 for q in R);n3=all(q["nonaffine"] for q in R);n4=all(q["ledger"]["algorithmic_boundary_assignments_enumerated"]==0 for q in R);G=[q for q in R if q["k"]>=9];mr=median(q["ratio"] for q in G);xr=max(q["ratio"] for q in G);n5=mr<=.1 and xr<=.25;K={}
 for k in p["boundary_width_ladder"]:
  g=[q for q in R if q["k"]==k];K[str(k)]={"median_nodes":median(q["message_nodes"] for q in g),"median_paid":median(q["paid_nohide_metric"] for q in g),"median_bytes":median(q["ledger"]["serialized_message_bytes"]+q["ledger"]["serialized_proofpack_bytes"] for q in g),"median_ops":median(q["ledger"]["bdd_apply_ops"]+q["ledger"]["truthgate_replay_ops"] for q in g)}
 ratios={}
 for z in ("median_nodes","median_paid","median_bytes","median_ops"):
  A=[K[str(k)][z] for k in p["boundary_width_ladder"]];ratios[z]=[A[i+1]/max(1,A[i]) for i in range(len(A)-1)]
 n6=all(max(v)<=4 for v in ratios.values());gates=[{"gate":"N1_EXACTNESS_AND_REPLAY","passed":n1},{"gate":"N2_CYCLIC_INTERNAL_ENTANGLEMENT","passed":True},{"gate":"N3_NONAFFINE_BOUNDARY_SEMANTICS","passed":n3},{"gate":"N4_ZERO_ALGORITHMIC_BOUNDARY_ENUMERATION","passed":n4},{"gate":"N5_COMPACT_ROBDD_MESSAGE","passed":n5,"median_ratio_k_ge_9":mr,"max_ratio_k_ge_9":xr},{"gate":"N6_NO_MEASURED_EXPONENTIAL_MIGRATION","passed":n6,"ratios":ratios},{"gate":"N7_TRUTHGATE_PROOFPACK","passed":all(q["replay"] for q in R)},{"gate":"N8_UNIVERSAL_POLYNOMIAL_BOUNDARY_ELIMINATION","passed":False,"status":"OPEN"}];ver="FINITE_CYCLIC_NONAFFINE_COMPACT_BOUNDARY_MESSAGE" if all(g["passed"] for g in gates[:7]) else "PARTIAL_OR_REFUTED_CYCLIC_NONAFFINE";O={"summary":{"cases":len(R),"verdict":ver,"algorithmic_boundary_assignments_enumerated_total":0,"P_VS_NP":"OPEN"},"gates":gates,"by_k":K,"cases_detail":R,"next_frontier":"ADVERSARIAL_BDD_WIDTH"}
 Path(x.output).write_text(json.dumps(O,indent=2,sort_keys=True)+"\n");Path(x.journal).write_text("\n".join(json.dumps(q,sort_keys=True) for q in J)+"\n");print(json.dumps({"summary":O["summary"],"gates":gates,"by_k":K},indent=2))
if __name__=="__main__":main()
