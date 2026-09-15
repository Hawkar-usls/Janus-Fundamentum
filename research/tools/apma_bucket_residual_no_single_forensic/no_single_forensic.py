from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID="JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-NO-SINGLE-SEPARATOR-STRUCTURE-FORENSIC-2026-09-15-v1.0"
PREREG=Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB="bd1fb0590456e9909f4f436e24a9884a75c90d0f"
V38=Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
V38_BLOB="cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"

def root(): return Path(__file__).resolve().parents[3]
def blob(p):
 d=p.read_bytes(); return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()
def source_guard():
 r=root(); return {"ok":blob(r/PREREG)==PREREG_BLOB and blob(r/V38)==V38_BLOB,"prereg_blob":blob(r/PREREG),"v38_blob":blob(r/V38)}
def rscope(f,core): return {int(v) for v in f["scope"] if int(v) not in set(core)}
def comps(scopes):
 n=len(scopes); p=list(range(n))
 def find(x):
  while p[x]!=x: p[x]=p[p[x]]; x=p[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b: p[max(a,b)]=min(a,b)
 for i in range(n):
  for j in range(i+1,n):
   if scopes[i]&scopes[j]: union(i,j)
 g={}
 for i in range(n): g.setdefault(find(i),[]).append(i)
 return sorted((sorted(x) for x in g.values()),key=lambda x:(x[0],len(x),x))
def edges(scopes):
 out=[]
 for i in range(len(scopes)):
  for j in range(i+1,len(scopes)):
   ov=sorted(scopes[i]&scopes[j])
   if ov: out.append({"i":i,"j":j,"overlap":ov,"overlap_cardinality":len(ov)})
 return out
def disconnects(scopes,cut): return len(comps([s-set(cut) for s in scopes]))>len(comps(scopes))
def cuts(scopes):
 vs=sorted(set().union(*scopes) if scopes else set()); s1=[(v,) for v in vs if disconnects(scopes,(v,))]
 s2=[] if s1 else [p for p in itertools.combinations(vs,2) if disconnects(scopes,p)]
 return {"single":[list(x) for x in s1],"pairs":[list(x) for x in s2],"minimum_size_up_to_two":1 if s1 else (2 if s2 else None),"variables_examined":len(vs),"pair_candidates_examined":0 if s1 else len(list(itertools.combinations(vs,2)))}
def tree(scopes,es):
 p=list(range(len(scopes)))
 def find(x):
  while p[x]!=x:p[x]=p[p[x]];x=p[x]
  return x
 out=[]
 for e in sorted(es,key=lambda z:(-z["overlap_cardinality"],z["i"],z["j"])):
  a,b=find(e["i"]),find(e["j"])
  if a==b:continue
  p[max(a,b)]=min(a,b);out.append(e)
  if len(out)==len(scopes)-1:break
 return out
def ri(scopes,t):
 adj={i:[] for i in range(len(scopes))}
 for e in t:adj[e["i"]].append(e["j"]);adj[e["j"]].append(e["i"])
 fail=[]
 for v in sorted(set().union(*scopes) if scopes else set()):
  nodes=[i for i,s in enumerate(scopes) if v in s]
  if len(nodes)<=1:continue
  allowed=set(nodes);seen={nodes[0]};q=[nodes[0]]
  while q:
   u=q.pop()
   for w in adj[u]:
    if w in allowed and w not in seen:seen.add(w);q.append(w)
  if seen!=allowed:fail.append(v)
 return {"ok":not fail,"failure_variables":fail}
def amap(f,row): return {int(v):int(b) for v,b in zip(f["scope"],row)}
def compat(fs,es):
 out=[]
 for e in es:
  a,b=fs[e["i"]],fs[e["j"]];ov=e["overlap"];n=0
  for x in a["rows"]:
   ax=amap(a,x)
   for y in b["rows"]:
    ay=amap(b,y)
    if all(ax[v]==ay[v] for v in ov):n+=1
  out.append({**e,"left_rows":len(a["rows"]),"right_rows":len(b["rows"]),"compatible_pairs":n})
 return out
def branch_sizes(fs,core):
 vs=sorted(set().union(*(rscope(f,core) for f in fs)) if fs else set());out=[]
 for v in vs:
  rows=[]
  for b in (0,1):
   rf=[];empty=False
   for f in fs:
    z,_=v38._restrict_factor(f,v,b)
    if z is None:empty=True;break
    rf.append(z)
   rows.append({"value":b,"exact_empty_unsat":empty,"component_sizes":[] if empty else [len(c) for c in comps([rscope(f,core) for f in rf])]})
  out.append({"variable":v,"branches":rows})
 return out
def profile(raw,label):
 parent=v38.explain(raw);prep=v38._prepare(raw)
 if prep.get("status")!="READY":return {"label":label,"parent":parent.get("status"),"prep":prep.get("status")}
 target=next(c for c in prep["residual_components"] if len(c)>2);fs=[prep["conditioned"][i] for i in target];ss=[rscope(f,prep["core"]) for f in fs];es=edges(ss);tr=tree(ss,es)
 return {"label":label,"parent_terminal":parent.get("status"),"factor_ids":[f["id"] for f in fs],"scopes":[sorted(s) for s in ss],"edges":es,"cut_profile":cuts(ss),"tree":tr,"running_intersection":ri(ss,tr),"pairwise_compatibility":compat(fs,es),"single_condition_branch_sizes":branch_sizes(fs,prep["core"]),"resource_receipt":{"three_plus_join_chains_materialized":0,"global_residual_cartesian_products_materialized":0,"pair_assignment_branches_enumerated":0}}
def run():
 g=source_guard()
 if not g["ok"]:return {"artifact_id":ARTIFACT_ID,"status":"HALT_SOURCE_GUARD","source_guard":g}
 a=profile(v38.no_single_variable_articulation_control(),"NO_ARTICULATION");b=profile(v38.branch_still_gt2_control(),"BRANCH_STILL_GT2")
 ok=a.get("parent_terminal")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR" and b.get("parent_terminal")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR"
 return {"artifact_id":ARTIFACT_ID,"authority":"DIAGNOSTIC_ONLY","status":"PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC" if ok else "FAIL_DIAGNOSTIC","source_guard":g,"controls":[a,b],"scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY":"NOT_PROVED","GLOBAL_APMA_FRONTIER_ADVANCE":"NONE"}}
def main():print(json.dumps(run(),sort_keys=True))
if __name__=="__main__":main()
