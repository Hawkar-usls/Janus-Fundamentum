#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json
from collections import Counter
from itertools import product, combinations
from pathlib import Path
from statistics import median
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("v6",HERE/"janus_bceg_cyclic_nonaffine_entanglement_v6.py");v6=importlib.util.module_from_spec(sp);sp.loader.exec_module(v6)
P=Path("research/JANUS_BCEG_ARTICULATION_TRELLIS_V8_PREREGISTRATION_2026-08-30.json")
def EQ(a,b):return [[-a,b],[a,-b]]
def build_chain(k,var,master):
 B=list(range(1,k+1));n=k+1;C=[];rng=__import__("random").Random(v6.sd(master,k,var,"shape"));prev=None
 for i in range(0,k,3):
  a,b,c=B[i:i+3];s,t,z=n,n+1,n+2;n+=3
  if prev is not None:C+=EQ(prev,s)
  q=rng.randrange(2);C+=v6.xor((s,t,a),0)+v6.AND(s,b,z)+v6.xor((z,t,c),q);prev=z
 rr=__import__("random").Random(v6.sd(master,k,var,"obf"));vs=sorted({abs(l) for c in C for l in c});pm=vs[:];rr.shuffle(pm);mp=dict(zip(vs,pm));O=[]
 for c in C:
  cc=[(1 if l>0 else -1)*mp[abs(l)] for l in c];rr.shuffle(cc);O.append(cc)
 rr.shuffle(O);return v6.cn(O),tuple(sorted(mp[x] for x in B))
def sat(c,a):return any((l>0 and a[abs(l)]) or (l<0 and not a[abs(l)]) for l in c)
class UF:
 def __init__(s,xs):s.p={x:x for x in xs};s.ops=0
 def find(s,x):
  s.ops+=1
  if s.p[x]!=x:s.p[x]=s.find(s.p[x])
  return s.p[x]
 def union(s,a,b):
  a=s.find(a);b=s.find(b)
  if a!=b:s.p[max(a,b)]=min(a,b);s.ops+=1
def raw_components(cnf,B):
 B=set(B);I={abs(l) for c in cnf for l in c}-B;A={x:set() for x in I};ops=0
 for c in cnf:
  q=sorted({abs(l) for l in c if abs(l) in I});ops+=len(c)
  for i,a in enumerate(q):
   for b in q[i+1:]:A[a].add(b);A[b].add(a)
 C=[];seen=set()
 for x in sorted(I):
  if x in seen:continue
  st=[x];z=set()
  while st:
   y=st.pop()
   if y in z:continue
   z.add(y);seen.add(y);st.extend(A[y]-z)
  C.append(z)
 return C,ops
def normalize_eq(cnf,B):
 B=set(B);bins=set(c for c in cnf if len(c)==2);vs=sorted({abs(l) for c in cnf for l in c});uf=UF(vs);checks=0;pairs=[]
 for a,b in combinations(vs,2):
  checks+=1
  if a not in B and b not in B and frozenset((-a,b)) in bins and frozenset((a,-b)) in bins:uf.union(a,b);pairs.append((a,b))
 O=[]
 for c in cnf:O.append([(uf.find(abs(l)) if l>0 else -uf.find(abs(l))) for l in c])
 return v6.cn(O),uf,pairs,checks
def primal(cnf):
 V=sorted({abs(l) for c in cnf for l in c});A={v:set() for v in V};e=0
 for c in cnf:
  q=sorted({abs(l) for l in c})
  for i,a in enumerate(q):
   for b in q[i+1:]:
    if b not in A[a]:e+=1
    A[a].add(b);A[b].add(a)
 return A,e
def bcc(A):
 d={};lo={};pa={};st=[];tm=[0];C=[];op=[0]
 def dfs(u):
  tm[0]+=1;d[u]=lo[u]=tm[0]
  for w in sorted(A[u]):
   op[0]+=1
   if w not in d:
    pa[w]=u;st.append((u,w));dfs(w);lo[u]=min(lo[u],lo[w])
    if lo[w]>=d[u]:
     z=set()
     while st:
      e=st.pop();z.update(e)
      if e==(u,w):break
     if z:C.append(z)
   elif pa.get(u)!=w and d[w]<d[u]:lo[u]=min(lo[u],d[w]);st.append((u,w))
 for u in sorted(A):
  if u not in d:dfs(u)
 cnt=Counter(x for c in C for x in c);return C,{x for x,n in cnt.items() if n>1},op[0]
def compile_t(cnf,B):
 raw,rop=raw_components(cnf,B);N,uf,pairs,eqc=normalize_eq(cnf,B);A,edges=primal(N);BC,arts,bop=bcc(A);BS=set(B);arts={x for x in arts if x not in BS};G=[[] for _ in BC]
 for c in N:
  vs={abs(l) for l in c};cand=[i for i,z in enumerate(BC) if vs.issubset(z)]
  if not cand:return None,{"status":"OPEN_UNASSIGNED_CLAUSE"}
  G[min(cand,key=lambda i:len(BC[i]))].append(c)
 amap={v:i for i,v in enumerate(sorted(arts))};F=[];le=0;co=0;me=0;ml=0
 for bag,cls in zip(BC,G):
  if not cls:continue
  bs=tuple(sorted(bag&BS));ss=tuple(sorted(bag&arts));loc=tuple(sorted(set().union(*({abs(l) for l in c} for c in cls))-set(bs)-set(ss)));scope=bs+ss;al=[]
  for eb in product((0,1),repeat=len(scope)):
   base=dict(zip(scope,eb));ok=False
   for ib in product((0,1),repeat=len(loc)):
    le+=1;a=dict(base);a.update(dict(zip(loc,ib)));good=True
    for c in cls:
     co+=1
     if not sat(c,a):good=False;break
    if good:ok=True;break
   if ok:al.append(sum(q<<i for i,q in enumerate(eb)))
  f={"boundary_scope":list(bs),"state_scope":[amap[x] for x in ss],"allowed":al};f["factor_hash"]=v6.H(f)[0];F.append(f);me=max(me,len(scope));ml=max(ml,len(loc))
 F.sort(key=lambda f:(f["boundary_scope"],f["state_scope"],f["factor_hash"]));M={"schema":"JANUS/BCEG/V8/ARTICULATION-TRELLIS/v1","boundary":sorted(BS),"state_count":len(arts),"factors":F,"replayable":True};mh,mb=v6.H(M);M["message_hash"]=mh;proof={"cnf_hash":v6.H([[*sorted(c)] for c in cnf])[0],"message_hash":mh,"state_count":len(arts),"bag_count":len(F),"max_bag_external_scope":me,"max_bag_local_internal_count":ml};ph,pb=v6.H(proof);proof["hash"]=ph;L={"raw_internal_component_count":len(raw),"raw_internal_component_size":max(map(len,raw),default=0),"equality_scan_checks":eqc,"union_find_ops":uf.ops,"primal_graph_edges":edges,"bcc_dfs_ops":bop+rop,"articulation_state_count":len(arts),"bag_count":len(F),"max_bag_external_scope":me,"max_bag_local_internal_count":ml,"local_assignments_enumerated":le,"local_clause_eval_ops":co,"trellis_factor_nodes":len(F),"trellis_serialized_bytes":mb,"serialized_proofpack_bytes":pb,"global_boundary_assignments_enumerated":0};return {"message":M,"proofpack":proof,"ledger":L},None
def teval(M,aB):
 for sb in product((0,1),repeat=M["state_count"]):
  ok=True
  for f in M["factors"]:
   bits=[aB[x] for x in f["boundary_scope"]]+[sb[q] for q in f["state_scope"]];code=sum(z<<i for i,z in enumerate(bits))
   if code not in set(f["allowed"]):ok=False;break
  if ok:return True
 return False
def cf(c):
 s=tuple(sorted(abs(l) for l in c));A=set()
 for b in product((0,1),repeat=len(s)):
  a=dict(zip(s,b))
  if sat(c,a):A.add(sum(q<<i for i,q in enumerate(b)))
 return s,A
def fv(f,a):
 s,A=f;return sum(a[x]<<i for i,x in enumerate(s)) in A
def norm(fs):
 D={}
 for s,A in fs:
  if len(A)==2**len(s):continue
  D[s]=set(A) if s not in D else D[s]&set(A)
 return [(s,A) for s,A in sorted(D.items())]
def flat(cnf,B):
 fs=norm([cf(c) for c in cnf]);I={x for s,A in fs for x in s}-set(B);w=0;mx=max((len(s) for s,A in fs),default=0)
 while I:
  best=None
  for v in I:
   G=[f for f in fs if v in f[0]];U=tuple(sorted(set().union(*(set(f[0]) for f in G))));sc=(len(U),sum(len(A) for s,A in G),v)
   if best is None or sc<best[0]:best=(sc,v,G,U)
  _,v,G,U=best;R=tuple(x for x in U if x!=v);A=set()
  for b in product((0,1),repeat=len(U)):
   w+=len(G);a=dict(zip(U,b))
   if all(fv(f,a) for f in G):A.add(sum(a[x]<<i for i,x in enumerate(R)))
  fs=norm([f for f in fs if f not in G]+[(R,A)]);I.remove(v);mx=max(mx,len(U))
 return {"work":w,"max_scope":mx,"final_factors":len(fs)}
def pt(L):return sum(L[k] for k in ("equality_scan_checks","union_find_ops","primal_graph_edges","bcc_dfs_ops","local_assignments_enumerated","local_clause_eval_ops","trellis_factor_nodes","trellis_serialized_bytes","serialized_proofpack_bytes"))
def pb(L):return L["minfill_ops"]+L["bdd_apply_ops"]+L["truthgate_replay_ops"]+L["serialized_message_bytes"]+L["serialized_proofpack_bytes"]+L["bdd_boundary_nodes"]
def audit(M,BM,B):
 mm=0;n=0
 for bits in product((0,1),repeat=len(B)):
  a=dict(zip(B,bits));n+=1;mm+=teval(M,a)!=v6.ev(BM,a)
 return n,mm
def st():
 for k in (6,9):
  C,B=build_chain(k,0,"V8DEV");T,e=compile_t(C,B);assert T and not e;T2,e2=compile_t(C,B);assert T2["message"]["message_hash"]==T["message"]["message_hash"];BM,BL,re=v6.solve(C,B);n,mm=audit(T["message"],BM,B);assert re and mm==0 and T["ledger"]["raw_internal_component_count"]==1 and T["ledger"]["global_boundary_assignments_enumerated"]==0
 return {"status":"PASS","cases":2}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output");ap.add_argument("--journal");ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
 if a.self_test:print(json.dumps(st(),indent=2));return
 p=json.loads(P.read_text());assert p["status"]=="FROZEN_BEFORE_HOLDOUT_EXECUTION";S=[(k,v) for k in p["fresh_holdout"]["boundary_width_ladder"] for v in range(p["fresh_holdout"]["variants_per_width"])];rr=__import__("random").Random(v6.sd(p["fresh_holdout"]["seed"],"order"));rr.shuffle(S);R=[];J=[]
 for ci,(k,var) in enumerate(S):
  C,B=build_chain(k,var,p["fresh_holdout"]["seed"]);T,e=compile_t(C,B);T2,e2=compile_t(C,B);re=T and T2 and T["message"]["message_hash"]==T2["message"]["message_hash"];BM,BL,bre=v6.solve(C,B);n,mm=audit(T["message"],BM,B) if T else (0,None);FB=flat(C,B);L=T["ledger"] if T else {};tw=pt(L) if T else None;bw=pb(BL);row={"case":ci,"k":k,"variant":var,"trellis_success":T is not None,"trellis_replay":re,"robdd_replay":bre,"audit_mismatches":mm,"evaluation_only_boundary_assignments_enumerated":n,"trellis_paid":tw,"flat_bucket_work":FB["work"],"flat_bucket_max_scope":FB["max_scope"],"robdd_paid":bw,"trellis_over_flat":tw/FB["work"] if tw is not None else None,"trellis_over_robdd":tw/bw if tw is not None else None,**L};R.append(row);J.append({"event":"CASE_COMPLETE",**row})
 T1=all(r["trellis_success"] and r["trellis_replay"] and r["robdd_replay"] and r["audit_mismatches"]==0 for r in R);T2=all(r["raw_internal_component_count"]==1 and r["raw_internal_component_size"]==r["k"] for r in R);T3=median(r["max_bag_external_scope"] for r in R)<=5;T4=all(r["global_boundary_assignments_enumerated"]==0 for r in R);big=[r for r in R if r["k"]>=9];mbr=median(r["trellis_serialized_bytes"]/(2**r["k"]) for r in big);K={}
 for k in p["fresh_holdout"]["boundary_width_ladder"]:
  g=[r for r in R if r["k"]==k];K[str(k)]={"median_states":median(r["articulation_state_count"] for r in g),"median_factors":median(r["trellis_factor_nodes"] for r in g),"median_trellis_paid":median(r["trellis_paid"] for r in g),"median_flat_bucket_work":median(r["flat_bucket_work"] for r in g),"median_flat_bucket_max_scope":median(r["flat_bucket_max_scope"] for r in g),"median_robdd_paid":median(r["robdd_paid"] for r in g),"median_trellis_bytes":median(r["trellis_serialized_bytes"] for r in g)}
 ks=p["fresh_holdout"]["boundary_width_ladder"];fa=[K[str(ks[i+1])]["median_factors"]/max(1,K[str(ks[i])]["median_factors"]) for i in range(len(ks)-1)];pa=[K[str(ks[i+1])]["median_trellis_paid"]/max(1,K[str(ks[i])]["median_trellis_paid"]) for i in range(len(ks)-1)];T5=mbr<=.15 and max(fa)<=1.75;T6=max(pa)<=2.;b12=[r for r in R if r["k"]>=12];mf=median(r["trellis_over_flat"] for r in b12);mr=median(r["trellis_over_robdd"] for r in b12);T7=mf<=.2;T8=mr<=.35;T9=all(r["local_assignments_enumerated"]>0 and r["flat_bucket_work"]>0 and r["robdd_paid"]>0 for r in R);G=[{"gate":"T1_EXACTNESS_AND_REPLAY","passed":T1},{"gate":"T2_ONE_GROWING_INTERNAL_COMPONENT","passed":T2},{"gate":"T3_ARTICULATION_STATE_DISCOVERY","passed":T3,"median_max_bag_external_scope":median(r["max_bag_external_scope"] for r in R)},{"gate":"T4_ZERO_SOLVER_GLOBAL_ENUMERATION","passed":T4},{"gate":"T5_COMPACT_TRELLIS","passed":T5,"median_bytes_over_2k_k_ge_9":mbr,"factor_adjacent_ratios":fa},{"gate":"T6_STATE_ON_CUT_SCALING","passed":T6,"paid_adjacent_ratios":pa},{"gate":"T7_ESCAPE_FLAT_BUCKET","passed":T7,"median_trellis_over_flat_k_ge_12":mf},{"gate":"T8_ESCAPE_GLOBAL_ROBDD","passed":T8,"median_trellis_over_robdd_k_ge_12":mr},{"gate":"T9_FULL_ACCOUNTING","passed":T9},{"gate":"T10_UNIVERSAL_POLYNOMIAL_BOUNDARY_ELIMINATION","passed":False,"status":"OPEN"}];core=all(g["passed"] for g in G[:9]);ver="FINITE_STATE_ON_CUT_COMPILATION_ESCAPE" if core else ("EXACT_TRELLIS_NO_FULL_ESCAPE" if T1 else "REFUTED_ARTICULATION_TRELLIS");O={"schema":"JANUS/BCEG/V8/RESULT/v1","summary":{"cases":len(R),"verdict":ver,"trellis_success":sum(r["trellis_success"] for r in R),"global_boundary_assignments_enumerated_total":sum(r["global_boundary_assignments_enumerated"] for r in R),"P_VS_NP":"OPEN"},"gates":G,"by_k":K,"cases_detail":R,"interpretation":{"positive":"A growing internal connected component can be compiled through articulation-state trellis messages when discovered block-cut width remains bounded.","limit":"This is a bounded block-cut-width constructed chain. It does not prove compact compilation for graphs with growing separator/treewidth.","next_frontier":"GROWING_SEPARATOR_WIDTH"}};Path(a.output).write_text(json.dumps(O,indent=2,sort_keys=True)+"\n");Path(a.journal).write_text("\n".join(json.dumps(x,sort_keys=True) for x in J)+"\n");print(json.dumps({"summary":O["summary"],"gates":G,"by_k":K},indent=2))
if __name__=="__main__":main()
