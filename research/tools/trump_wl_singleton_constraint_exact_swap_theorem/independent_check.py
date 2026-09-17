from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
CANDIDATE=ROOT/"research/tools/trump_wl_singleton_constraint_exact_swap_theorem/candidate.py"
PREREG=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_REVIEW_2026-09-18_v1.0.json"
PROJECTION=ROOT/"research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
WL=ROOT/"research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py"
ORBIT=ROOT/"research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
SCOPE_THEOREM=ROOT/"research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_RESULT_2026-09-18_v1.0.json"
EXPECTED={
 CANDIDATE:"04850c06ed0d5af05be16371ba63d1b45b20a39f",
 PREREG:"5f3a4087a9399411f51e4abd90f77dd786497189",
 REVIEW:"5b693b091533eec19f8e96bb8d78a0e77663c950",
 PROJECTION:"2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
 WL:"6b697fd8b3de4c83f8226b06399b6bad99953d4e",
 ORBIT:"a076cfc56d68aad0348415e313705da1f6b9cdcd",
 SCOPE_THEOREM:"3cbf05cb0b0249ddf365bc43d176a06ddb7f72af",
}

def blob(path:Path)->str:
 d=path.read_bytes()
 return hashlib.sha1(f"blob {len(d)}\0".encode("ascii")+d).hexdigest()

def allowed(kind:str):
 forbidden=(0,0,0) if kind=="R000" else (1,1,1)
 return tuple(bits for bits in itertools.product((0,1),repeat=3) if bits!=forbidden)

R000=allowed("R000");R111=allowed("R111")

def relation_signature(rows):
 return "a3:"+"/".join("".join(str(x) for x in row) for row in sorted(rows))

def rank(values):
 unique=sorted(set(values.values()),key=repr)
 idx={v:i for i,v in enumerate(unique)}
 return {k:idx[v] for k,v in values.items()}

def structure(raw):
 nodes=[];adj=defaultdict(set);labels={}
 for v in raw["variables"]:
  n=("v",int(v));nodes.append(n);adj[n];labels[n]="V"
 for c in raw["constraints"]:
  cn=("c",str(c["id"]));nodes.append(cn);adj[cn]
  rows=tuple(tuple(x) for x in c["allowed"])
  labels[cn]="C:"+relation_signature(rows)
  for v in set(c["scope"]):
   vn=("v",int(v));adj[cn].add(vn);adj[vn].add(cn)
 return sorted(nodes,key=lambda x:(x[0],str(x[1]))),adj,labels

def wl1(raw):
 nodes,adj,labels=structure(raw)
 colors=rank({n:(labels[n],) for n in nodes})
 rounds=0
 while True:
  sig={n:(colors[n],tuple(sorted(colors[x] for x in adj[n]))) for n in nodes}
  new=rank(sig);rounds+=1
  if len(set(new.values()))==len(set(colors.values())):
   return nodes,adj,labels,new,rounds
  colors=new

def constraint_key(scope,rows):
 scope=list(scope)
 order=sorted(range(len(scope)),key=lambda i:scope[i])
 sorted_scope=tuple(scope[i] for i in order)
 canon={tuple(tuple(r)[i] for i in order) for r in rows}
 return sorted_scope,tuple(sorted(canon))

def formula_key(raw):
 return tuple(sorted(constraint_key(c["scope"],c["allowed"]) for c in raw["constraints"]))

def after_swap_key(raw,u,v):
 out=[]
 for c in raw["constraints"]:
  scope=[v if x==u else u if x==v else x for x in c["scope"]]
  out.append(constraint_key(scope,c["allowed"]))
 return tuple(sorted(out))

def exact(raw,u,v):
 return after_swap_key(raw,u,v)==formula_key(raw)

def make_raw(n,selected):
 constraints=[]
 for i,(scope,kind) in enumerate(selected):
  rows=R000 if kind=="R000" else R111
  constraints.append({"id":f"s{i:03d}_{kind}","scope":list(scope),"allowed":[list(r) for r in rows]})
 return {"variables":list(range(1,n+1)),"constraints":constraints}

def iter_synthetic():
 for n,maxk in ((3,None),(4,None),(5,3),(6,2)):
  universe=[(tuple(t),kind) for t in itertools.combinations(range(1,n+1),3) for kind in ("R000","R111")]
  if maxk is None:
   for mask in range(1<<len(universe)):
    yield n,tuple(universe[i] for i in range(len(universe)) if mask&(1<<i))
  else:
   for k in range(maxk+1):
    yield from ((n,combo) for combo in itertools.combinations(universe,k))

def equitable(nodes,adj,colors):
 by=defaultdict(set)
 for n in nodes:
  by[colors[n]].add((colors[n],tuple(sorted(colors[x] for x in adj[n]))))
 return all(len(x)==1 for x in by.values())

def constraint_singletons(nodes,colors):
 cs=[n for n in nodes if n[0]=="c"]
 cnt=Counter(colors[n] for n in cs)
 return all(v==1 for v in cnt.values())

def same_pairs(nodes,colors):
 vs=[n for n in nodes if n[0]=="v"]
 return [(u[1],v[1]) for i,u in enumerate(vs) for v in vs[i+1:] if colors[u]==colors[v]]

def independent_recompute():
 failures=[];cases=0;premise_formulas=0;pair_checks=0
 relation_symmetry={}
 for name,rows in (("R000",R000),("R111",R111)):
  rowset=set(rows)
  relation_symmetry[name]=all({tuple(r[i] for i in p) for r in rows}==rowset for p in itertools.permutations(range(3)))
 for n,selected in iter_synthetic():
  raw=make_raw(n,selected);cases+=1
  nodes,adj,labels,colors,rounds=wl1(raw)
  if not equitable(nodes,adj,colors):
   failures.append({"class":"NON_EQUITABLE_RETURN","n":n});break
  vc={colors[x] for x in nodes if x[0]=="v"};cc={colors[x] for x in nodes if x[0]=="c"}
  if vc&cc:
   failures.append({"class":"TYPE_COLOR_COLLISION","n":n});break
  if not constraint_singletons(nodes,colors):continue
  pairs=same_pairs(nodes,colors)
  if not pairs:continue
  premise_formulas+=1
  for u,v in pairs:
   pair_checks+=1
   # Independent neighborhood consequence.
   iu={c["id"] for c in raw["constraints"] if u in c["scope"]}
   iv={c["id"] for c in raw["constraints"] if v in c["scope"]}
   if iu!=iv or not exact(raw,u,v):
    failures.append({"class":"COUNTEREXAMPLE","n":n,"pair":[u,v],"selected":[[list(s),k] for s,k in selected],"same_incidence":iu==iv,"exact":exact(raw,u,v)})
    break
  if failures:break
 return {"cases":cases,"premise_formulas":premise_formulas,"premise_pair_checks":pair_checks,"relation_symmetry":relation_symmetry,"failures":failures}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);args=ap.parse_args()
 bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
 if not all(bindings.values()):
  return {"verdict":"HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE","authority_bindings":bindings}
 candidate=json.loads(Path(args.candidate).read_text())
 independent=independent_recompute()
 scope=json.loads(SCOPE_THEOREM.read_text())
 checks={
  "candidate_pass":candidate.get("verdict")=="PASS_SINGLETON_CONSTRAINT_WL_COLOR_IMPLIES_EXACT_SWAP_ON_R000_R111_RESIDUALS",
  "candidate_not_imported":True,
  "no_independent_failures":not independent["failures"],
  "relation_symmetry":all(independent["relation_symmetry"].values()),
  "cases_match":independent["cases"]==candidate.get("synthetic_sanity",{}).get("formulas_checked"),
  "premise_formulas_match":independent["premise_formulas"]==candidate.get("synthetic_sanity",{}).get("premise_formulas"),
  "premise_pair_checks_match":independent["premise_pair_checks"]==candidate.get("synthetic_sanity",{}).get("premise_pair_checks"),
  "prior_scope_theorem_pass":scope.get("scientific_outcome")=="PASS_SCOPE_BOUND_DIRECT_EXACT_TRANSPOSITION_WITNESS_SUFFICIENCY_FOR_FROZEN_E3",
 }
 return {
  "verdict":"PASS_INDEPENDENT_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_MISMATCH",
  "candidate_imported":False,
  "checks":checks,
  "independent_sanity":independent,
  "scientific_firewall":{"GENERAL_SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"},
 }

if __name__=="__main__":
 print(json.dumps(main(),sort_keys=True,separators=(",",":")))
