from __future__ import annotations
import itertools, json
from research.tools.apma_bucket_residual_no_single_forensic import no_single_forensic as prof
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

def rscope(f,core): return {int(v) for v in f["scope"] if int(v) not in set(core)}
def bfs(scopes):
 n=len(scopes);adj={i:[] for i in range(n)}
 for i in range(n):
  for j in range(i+1,n):
   if scopes[i]&scopes[j]:adj[i].append(j);adj[j].append(i)
 seen=set();out=[]
 for s in range(n):
  if s in seen:continue
  seen.add(s);q=[s];c=[]
  while q:
   u=q.pop(0);c.append(u)
   for w in sorted(adj[u]):
    if w not in seen:seen.add(w);q.append(w)
  out.append(sorted(c))
 return sorted(out,key=lambda x:(x[0],len(x),x))
def disconnects(scopes,cut):return len(bfs([s-set(cut) for s in scopes]))>len(bfs(scopes))
def cut_profile(scopes):
 vs=sorted(set().union(*scopes) if scopes else set());one=[[v] for v in vs if disconnects(scopes,{v})]
 pairs=[] if one else [list(p) for p in itertools.combinations(vs,2) if disconnects(scopes,set(p))]
 return {"single":one,"pairs":pairs,"minimum_size_up_to_two":1 if one else (2 if pairs else None)}
def edge_list(scopes):
 out=[]
 for i in range(len(scopes)):
  for j in range(i+1,len(scopes)):
   ov=sorted(scopes[i]&scopes[j])
   if ov:out.append({"i":i,"j":j,"overlap":ov,"overlap_cardinality":len(ov)})
 return out
def prim(scopes,edges):
 if not scopes:return []
 used={0};out=[]
 while len(used)<len(scopes):
  opts=[e for e in edges if (e["i"] in used)^(e["j"] in used)]
  if not opts:break
  e=sorted(opts,key=lambda z:(-z["overlap_cardinality"],z["i"],z["j"]))[0];out.append(e);used|={e["i"],e["j"]}
 return out
def ri(scopes,t):
 adj={i:[] for i in range(len(scopes))}
 for e in t:adj[e["i"]].append(e["j"]);adj[e["j"]].append(e["i"])
 bad=[]
 for v in sorted(set().union(*scopes) if scopes else set()):
  ns=[i for i,s in enumerate(scopes) if v in s]
  if len(ns)<2:continue
  allowed=set(ns);seen={ns[0]};q=[ns[0]]
  while q:
   u=q.pop(0)
   for w in adj[u]:
    if w in allowed and w not in seen:seen.add(w);q.append(w)
  if seen!=allowed:bad.append(v)
 return {"ok":not bad,"failure_variables":bad}
def amap(f,row):return {int(v):int(b) for v,b in zip(f["scope"],row)}
def hash_compat(fs,edges):
 out=[]
 for e in edges:
  L,R=fs[e["i"]],fs[e["j"]];ov=e["overlap"];idx={}
  for r in R["rows"]:
   m=amap(R,r);key=tuple(m[v] for v in ov);idx[key]=idx.get(key,0)+1
  n=0
  for r in L["rows"]:
   m=amap(L,r);n+=idx.get(tuple(m[v] for v in ov),0)
  out.append({**e,"compatible_pairs":n})
 return out
def independent(raw,label):
 p=v38._prepare(raw);parent=v38.explain(raw)
 if p.get("status")!="READY":return {"label":label,"parent_terminal":parent.get("status"),"prep":p.get("status")}
 target=next(c for c in p["residual_components"] if len(c)>2);fs=[p["conditioned"][i] for i in target];ss=[rscope(f,p["core"]) for f in fs];es=edge_list(ss);t=prim(ss,es)
 return {"label":label,"parent_terminal":parent.get("status"),"factor_ids":[f["id"] for f in fs],"scopes":[sorted(s) for s in ss],"edges":es,"cut_profile":cut_profile(ss),"running_intersection":ri(ss,t),"pairwise_compatibility":hash_compat(fs,es)}
def normalize_compat(x):return [(e["i"],e["j"],e["overlap"],e["compatible_pairs"]) for e in x]
def run():
 p=prof.run();ind=[independent(v38.no_single_variable_articulation_control(),"NO_ARTICULATION"),independent(v38.branch_still_gt2_control(),"BRANCH_STILL_GT2")];pcs=p.get("controls",[])
 checks={"source_guard":prof.source_guard()["ok"] is True,"profiler_pass":p.get("status")=="PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC","parent_open":all(x.get("parent_terminal")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR" for x in ind),"factor_ids_match":all(pcs[i].get("factor_ids")==ind[i].get("factor_ids") for i in range(2)),"scopes_match":all(pcs[i].get("scopes")==ind[i].get("scopes") for i in range(2)),"cuts_match":all(pcs[i].get("cut_profile",{}).get("single")==ind[i].get("cut_profile",{}).get("single") and pcs[i].get("cut_profile",{}).get("pairs")==ind[i].get("cut_profile",{}).get("pairs") and pcs[i].get("cut_profile",{}).get("minimum_size_up_to_two")==ind[i].get("cut_profile",{}).get("minimum_size_up_to_two") for i in range(2)),"ri_match":all(pcs[i].get("running_intersection")==ind[i].get("running_intersection") for i in range(2)),"compat_match":all(normalize_compat(pcs[i].get("pairwise_compatibility",[]))==normalize_compat(ind[i].get("pairwise_compatibility",[])) for i in range(2)),"zero_join":all(x.get("resource_receipt",{}).get("three_plus_join_chains_materialized")==0 for x in pcs),"zero_pair_branching":all(x.get("resource_receipt",{}).get("pair_assignment_branches_enumerated")==0 for x in pcs),"FW_pvsnp":p.get("scientific_firewall",{}).get("P_VS_NP")=="OPEN","FW_sat":p.get("scientific_firewall",{}).get("GENERAL_SAT_IN_P")=="NOT_PROVED"}
 verdict="PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC" if all(checks.values()) else "FAIL_DIAGNOSTIC"
 return {"artifact_id":"JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-NO-SINGLE-SEPARATOR-STRUCTURE-FORENSIC-INDEPENDENT-CHECK-2026-09-15","authority":"INDEPENDENT_DIAGNOSTIC_CHECKER","checks":checks,"controls":ind,"verdict":verdict,"scientific_firewall":p.get("scientific_firewall")}
def main():print(json.dumps(run(),sort_keys=True))
if __name__=="__main__":main()
