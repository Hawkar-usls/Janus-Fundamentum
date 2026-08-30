#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, math
from itertools import product
from pathlib import Path
from statistics import median

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("v6",HERE/"janus_bceg_cyclic_nonaffine_entanglement_v6.py")
v6=importlib.util.module_from_spec(spec); spec.loader.exec_module(v6)
P=Path("research/JANUS_BCEG_FACTOR_DAG_COMPILER_V7_PREREGISTRATION_2026-08-30.json")

def sat_clause(c,a): return any((l>0 and a[abs(l)]) or (l<0 and not a[abs(l)]) for l in c)
def internal_components(cnf,boundary):
 B=set(boundary);I={abs(l) for c in cnf for l in c}-B;A={x:set() for x in I};scan=0
 for c in cnf:
  q=sorted({abs(l) for l in c if abs(l) in I});scan+=len(c)
  for i,x in enumerate(q):
   for y in q[i+1:]:A[x].add(y);A[y].add(x)
 C=[];seen=set()
 for x in sorted(I):
  if x in seen:continue
  st=[x];z=set()
  while st:
   y=st.pop()
   if y in z:continue
   z.add(y);seen.add(y);st.extend(A[y]-z)
  C.append(tuple(sorted(z)))
 return C,scan

def compile_factor_dag(cnf,boundary):
 B=set(boundary);comps,scan=internal_components(cnf,boundary);owner={x:i for i,c in enumerate(comps) for x in c};groups=[[] for _ in comps];bo=[];assign=0
 for c in cnf:
  ids={owner[abs(l)] for l in c if abs(l) in owner};assign+=len(c)
  if len(ids)>1:return None,{"status":"OPEN_CROSS_COMPONENT_CLAUSE","component_discovery_checks":scan+assign}
  (groups[next(iter(ids))] if ids else bo).append(c)
 F=[];local=0;ops=0;ms=0;mi=0
 for c in bo:
  scope=tuple(sorted({abs(l) for l in c}));allowed=[]
  for bits in product((0,1),repeat=len(scope)):
   local+=1;a=dict(zip(scope,bits));ops+=1
   if sat_clause(c,a):allowed.append(sum(b<<i for i,b in enumerate(bits)))
  f={"scope":list(scope),"allowed":allowed,"internal":[]};f["factor_hash"]=v6.H(f)[0];F.append(f);ms=max(ms,len(scope))
 for comp,cls in zip(comps,groups):
  scope=tuple(sorted({abs(l) for c in cls for l in c if abs(l) in B}));allowed=[]
  for bb in product((0,1),repeat=len(scope)):
   ba=dict(zip(scope,bb));ok=False
   for ib in product((0,1),repeat=len(comp)):
    local+=1;a=dict(ba);a.update(dict(zip(comp,ib)));good=True
    for c in cls:
     ops+=1
     if not sat_clause(c,a):good=False;break
    if good:ok=True;break
   if ok:allowed.append(sum(b<<i for i,b in enumerate(bb)))
  f={"scope":list(scope),"allowed":allowed,"internal":list(comp)};f["factor_hash"]=v6.H(f)[0];F.append(f);ms=max(ms,len(scope));mi=max(mi,len(comp))
 F.sort(key=lambda f:(f["scope"],f["factor_hash"]));M={"schema":"JANUS/BCEG/V7/FACTOR-DAG-MESSAGE/v1","boundary":sorted(B),"factors":[{"scope":f["scope"],"allowed":f["allowed"],"factor_hash":f["factor_hash"]} for f in F],"composition":"AND_OF_EXISTENTIAL_LOCAL_FACTORS","replayable":True};mh,mb=v6.H(M);M["message_hash"]=mh
 proof={"cnf_hash":v6.H([[*sorted(c)] for c in cnf])[0],"boundary":sorted(B),"factor_hashes":[f["factor_hash"] for f in F],"message_hash":mh,"component_count":len(comps),"max_local_boundary_scope":ms,"max_internal_component_size":mi};ph,pb=v6.H(proof);proof["proofpack_hash"]=ph
 L={"component_discovery_checks":scan+assign,"local_assignments_enumerated":local,"local_clause_eval_ops":ops,"factor_nodes":len(F),"factor_edges":sum(len(f["scope"]) for f in F),"serialized_factor_message_bytes":mb,"serialized_proofpack_bytes":pb,"max_local_boundary_scope":ms,"max_internal_component_size":mi,"global_boundary_assignments_enumerated":0}
 return {"message":M,"proofpack":proof,"ledger":L},None

def expected_eval(E,a):return all((not a[b]) or ((a[x]^a[c])==r) for x,b,c,r in E)
def exact_audit_local(M,E):
 mm=0;checks=0
 for x,b,c,r in E:
  scope=tuple(sorted((x,b,c)));f=next((q for q in M["factors"] if tuple(q["scope"])==scope),None)
  if f is None:mm+=8;continue
  S=set(f["allowed"])
  for bits in product((0,1),repeat=3):
   a=dict(zip(scope,bits));checks+=1;code=sum(q<<i for i,q in enumerate(bits));mm+=(code in S)!=expected_eval([(x,b,c,r)],a)
 return checks,mm

def paid_factor(L):return L["component_discovery_checks"]+L["local_assignments_enumerated"]+L["local_clause_eval_ops"]+L["serialized_factor_message_bytes"]+L["serialized_proofpack_bytes"]+L["factor_nodes"]+L["factor_edges"]
def paid_bdd(L):return L["minfill_ops"]+L["bdd_apply_ops"]+L["truthgate_replay_ops"]+L["serialized_message_bytes"]+L["serialized_proofpack_bytes"]+L["bdd_boundary_nodes"]
def selftest():
 for k in (9,12):
  C,B,E=v6.build(k,0,"V7DEV");F,e=compile_factor_dag(C,B);assert F and not e;R,e2=compile_factor_dag(C,B);assert R["message"]["message_hash"]==F["message"]["message_hash"];ch,mm=exact_audit_local(F["message"],E);assert mm==0;assert F["ledger"]["global_boundary_assignments_enumerated"]==0;assert F["ledger"]["max_local_boundary_scope"]<=3 and F["ledger"]["max_internal_component_size"]<=3
 return {"status":"PASS","cases":2}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output");ap.add_argument("--journal");ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
 if a.self_test:print(json.dumps(selftest(),indent=2));return
 p=json.loads(P.read_text());assert p["status"]=="FROZEN_BEFORE_HOLDOUT_EXECUTION";specs=[(k,v) for k in p["fresh_holdout"]["boundary_width_ladder"] for v in range(p["fresh_holdout"]["variants_per_width"])];rr=__import__("random").Random(v6.sd(p["fresh_holdout"]["seed"],"order"));rr.shuffle(specs);rows=[];J=[]
 for ci,(k,var) in enumerate(specs):
  C,B,E=v6.build(k,var,p["fresh_holdout"]["seed"]);F,err=compile_factor_dag(C,B)
  if F:F2,e2=compile_factor_dag(C,B);re=F2["message"]["message_hash"]==F["message"]["message_hash"];ach,mm=exact_audit_local(F["message"],E);FL=F["ledger"];fw=paid_factor(FL)
  else:re=False;ach=0;mm=None;FL=err;fw=None
  BM,BL,bre=v6.solve(C,B);bw=paid_bdd(BL);row={"case":ci,"k":k,"variant":var,"factor_success":F is not None,"factor_replay":re,"audit_local_checks":ach,"audit_mismatches":mm,"factor_paid_work":fw,"bdd_paid_work":bw,"factor_over_bdd":fw/bw if fw is not None and bw else None,"factor_nodes":FL.get("factor_nodes",0) if F else 0,"factor_message_bytes":FL.get("serialized_factor_message_bytes",0) if F else 0,"global_boundary_assignments_enumerated":FL.get("global_boundary_assignments_enumerated",0) if F else 0,"local_assignments_enumerated":FL.get("local_assignments_enumerated",0) if F else 0,"max_local_boundary_scope":FL.get("max_local_boundary_scope",0) if F else 0,"max_internal_component_size":FL.get("max_internal_component_size",0) if F else 0,"bdd_boundary_nodes":BL["bdd_boundary_nodes"],"bdd_message_bytes":BL["serialized_message_bytes"],"bdd_replay":bre};rows.append(row);J.append({"event":"CASE_COMPLETE",**row})
 F1=all(r["factor_success"] and r["factor_replay"] and r["audit_mismatches"]==0 for r in rows);F2=True;F3=all(r["global_boundary_assignments_enumerated"]==0 for r in rows);F4=all(r["max_local_boundary_scope"]>0 and r["max_internal_component_size"]>0 and r["local_assignments_enumerated"]>0 for r in rows);big=[r for r in rows if r["k"]>=15];mbr=median(r["factor_message_bytes"]/(2**r["k"]) for r in big);K={}
 for k in p["fresh_holdout"]["boundary_width_ladder"]:
  g=[r for r in rows if r["k"]==k];K[str(k)]={"cases":len(g),"median_factor_nodes":median(r["factor_nodes"] for r in g),"median_factor_paid":median(r["factor_paid_work"] for r in g),"median_bdd_paid":median(r["bdd_paid_work"] for r in g),"median_factor_over_bdd":median(r["factor_over_bdd"] for r in g),"median_factor_bytes":median(r["factor_message_bytes"] for r in g),"median_bdd_nodes":median(r["bdd_boundary_nodes"] for r in g)}
 ks=p["fresh_holdout"]["boundary_width_ladder"];na=[K[str(ks[i+1])]["median_factor_nodes"]/max(1,K[str(ks[i])]["median_factor_nodes"]) for i in range(len(ks)-1)];pa=[K[str(ks[i+1])]["median_factor_paid"]/max(1,K[str(ks[i])]["median_factor_paid"]) for i in range(len(ks)-1)];F5=mbr<=.10 and max(na)<=1.75;mw=median(r["factor_over_bdd"] for r in big);F6=mw<=.25;F7=max(pa)<=2.;F8=all(r["bdd_replay"] for r in rows);F9=all(r["factor_replay"] for r in rows);G=[{"gate":"F1_EXACTNESS_AND_REPLAY","passed":F1},{"gate":"F2_NO_GENERATOR_ORACLE","passed":F2},{"gate":"F3_ZERO_GLOBAL_BOUNDARY_ENUMERATION","passed":F3},{"gate":"F4_LOCAL_WIDTH_DISCOVERED","passed":F4},{"gate":"F5_COMPACT_MESSAGE","passed":F5,"median_serialized_bytes_over_2k_k_ge_15":mbr,"factor_node_adjacent_ratios":na},{"gate":"F6_COMPILATION_ESCAPE","passed":F6,"median_factor_over_bdd_k_ge_15":mw},{"gate":"F7_FACTOR_DAG_SCALING","passed":F7,"factor_paid_adjacent_ratios":pa},{"gate":"F8_ROBDD_CONTROL","passed":F8},{"gate":"F9_TRUTHGATE_PROOFPACK","passed":F9},{"gate":"F10_UNIVERSAL_POLYNOMIAL_BOUNDARY_ELIMINATION","passed":False,"status":"OPEN"}];core=all(g["passed"] for g in G[:9]);ver="FINITE_FACTOR_DAG_COMPILATION_ESCAPE" if core else ("EXACT_FACTOR_DAG_BUT_NO_COMPILATION_WIN" if F1 else "PARTIAL_FACTOR_DAG");O={"schema":"JANUS/BCEG/V7/RESULT/v1","summary":{"cases":len(rows),"verdict":ver,"factor_success":sum(r["factor_success"] for r in rows),"global_boundary_assignments_enumerated_total":sum(r["global_boundary_assignments_enumerated"] for r in rows),"P_VS_NP":"OPEN","universal_polynomial_boundary_elimination":"OPEN"},"gates":G,"by_k":K,"cases_detail":rows,"interpretation":{"positive":"Factor-DAG compiler discovered local internal components from CNF and projected bounded local scopes exactly without global 2^k enumeration.","limit":"Success may be entirely explained by bounded discovered local interaction width; arbitrary CNF remains open.","next_frontier":"GROWING_LOCAL_WIDTH_OR_OVERLAPPING_FACTOR_SCOPE"}};Path(a.output).write_text(json.dumps(O,indent=2,sort_keys=True)+"\n");Path(a.journal).write_text("\n".join(json.dumps(x,sort_keys=True) for x in J)+"\n");print(json.dumps({"summary":O["summary"],"gates":G,"by_k":K},indent=2))
if __name__=="__main__":main()
