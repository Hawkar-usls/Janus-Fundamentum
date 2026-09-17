from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
CANDIDATE=ROOT/"research/tools/trump_wl_singleton_constraint_six_positive_corollary/candidate.py"
PREREG=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_SIX_POSITIVE_COROLLARY_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_SIX_POSITIVE_COROLLARY_REVIEW_2026-09-18_v1.0.json"
THEOREM=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_RESULT_2026-09-18_v1.0.json"
SCOPE=ROOT/"research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_RESULT_2026-09-18_v1.0.json"
ORBIT=ROOT/"research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
EXPECTED={
 CANDIDATE:"10918864fb1a6d683490faff9b29abf4d0191a29",
 PREREG:"d0e25c69006f2e54ee8d52e4d3c06ce213e943af",
 REVIEW:"9ac39a874395fd03c920d3a069cafc0dc5fbf1f7",
 THEOREM:"eda86821031e43dad76ff81f7239d3ca27387cc7",
 SCOPE:"3cbf05cb0b0249ddf365bc43d176a06ddb7f72af",
 ORBIT:"a076cfc56d68aad0348415e313705da1f6b9cdcd",
}

def blob(path):
 d=Path(path).read_bytes();return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()

def parse(path):
 clauses=[];buf=[];header=None
 for raw in Path(path).read_text(encoding="utf-8").splitlines():
  s=raw.strip()
  if not s or s.startswith("c") or s in {"%","0"}:continue
  if s.startswith("p "):
   p=s.split();header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:
    if len(buf)!=3 or len({abs(x) for x in buf})!=3:raise ValueError("BAD_3CNF")
    clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 if header!=(20,91) or len(clauses)!=91 or buf:raise ValueError("UF20_CONTRACT")
 return clauses

def project(source,clauses):
 constraints=[];vars_set=set()
 for ordinal,clause in enumerate(clauses,1):
  ordered=sorted(clause,key=lambda x:abs(x))
  rid="".join("0" if x>0 else "1" for x in ordered)
  if rid not in {"000","111"}:continue
  scope=sorted(abs(x) for x in clause);vars_set.update(scope)
  allowed=[]
  for bits in itertools.product((0,1),repeat=3):
   assign=dict(zip(scope,bits,strict=True))
   sat=any(assign[abs(lit)]==1 if lit>0 else assign[abs(lit)]==0 for lit in clause)
   if sat:allowed.append(list(bits))
  constraints.append({"id":f"satlib_{source.lower()}_c{ordinal:03d}","scope":scope,"allowed":allowed})
 return {"variables":sorted(vars_set),"constraints":constraints}

def pendant(raw):
 degree=Counter()
 for c in raw["constraints"]:
  for v in set(c["scope"]):degree[v]+=1
 D={v for v in raw["variables"] if degree[v]==1}
 T={c["id"] for c in raw["constraints"] if D & set(c["scope"])}
 return {"variables":[v for v in raw["variables"] if v not in D],"constraints":[c for c in raw["constraints"] if c["id"] not in T]},sorted(D),sorted(T)

def relation_signature(c):
 rows=sorted("".join(str(int(b)) for b in row) for row in c["allowed"])
 return f"a{len(c['scope'])}:"+"/".join(rows)

def rank(d):
 uniq=sorted(set(d.values()),key=repr);m={v:i for i,v in enumerate(uniq)}
 return {k:m[v] for k,v in d.items()}

def wl1(raw):
 nodes=[];adj=defaultdict(set);labels={}
 for v in sorted(raw["variables"]):
  n=("v",v);nodes.append(n);labels[n]="V";adj[n]
 for c in raw["constraints"]:
  cn=("c",str(c["id"]));nodes.append(cn);labels[cn]="C:"+relation_signature(c);adj[cn]
  for v in set(c["scope"]):
   vn=("v",v);adj[cn].add(vn);adj[vn].add(cn)
 nodes=sorted(nodes,key=lambda n:(n[0],str(n[1])))
 colors=rank({n:(labels[n],) for n in nodes});rounds=0
 while True:
  sig={n:(colors[n],tuple(sorted(colors[x] for x in adj[n]))) for n in nodes}
  new=rank(sig);rounds+=1
  if len(set(new.values()))==len(set(colors.values())):return nodes,adj,new,rounds
  colors=new

def row(spec):
 source=spec["source"];path=ROOT/spec["path"];pair=tuple(spec["pair"])
 if blob(path)!=spec["git_blob"]:return {"source":source,"outcome":"HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE"}
 raw=project(source,parse(path));reduced,D,T=pendant(raw)
 nodes,adj,colors,rounds=wl1(reduced)
 byvar={n[1]:n for n in nodes if n[0]=="v"}
 same=pair[0] in byvar and pair[1] in byvar and colors[byvar[pair[0]]]==colors[byvar[pair[1]]]
 cs=[n for n in nodes if n[0]=="c"];cnt=Counter(colors[n] for n in cs)
 nons=sorted([{"color":int(k),"size":int(v)} for k,v in cnt.items() if v>1],key=lambda x:(x["size"],x["color"]))
 single=not nons
 formula=orbit.validate_and_normalize(reduced);n=len(formula.variables);L=formula.L
 bound=n>=2 and 3*(2**(n-2))<=L*L
 if not same:o="THEOREM_NOT_APPLICABLE__PAIR_NOT_SAME_WL1_COLOR"
 elif not single:o="THEOREM_NOT_APPLICABLE__NON_SINGLETON_CONSTRAINT_COLOR_EXISTS"
 elif not bound:o="THEOREM_EXACT_SWAP_APPLIES_BUT_E3_RESOURCE_BOUND_OUTSIDE_SCOPE"
 else:o="THEOREM_APPLIES__EXACT_SWAP_AND_E3_ADMISSION_FOLLOW_WITHOUT_DIRECT_EXACT_SELECTOR_CALL"
 return {"source":source,"pair":list(pair),"pair_present":pair[0] in byvar and pair[1] in byvar,"pair_same_stable_wl1_color":bool(same),"constraint_count":len(cs),"constraint_color_class_count":len(cnt),"all_constraint_nodes_singleton":single,"non_singleton_constraint_color_classes":nons,"wl1_rounds":rounds,"degree1_variables":D,"removed_constraint_ids":T,"residual_n":n,"residual_L":L,"resource_bound_value":3*(2**(n-2)) if n>=2 else None,"L2":L*L,"resource_bound_holds":bound,"outcome":o}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);args=ap.parse_args()
 bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
 if not all(bindings.values()):return {"verdict":"HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE","authority_bindings":bindings}
 pre=json.loads(PREREG.read_text());scope=json.loads(SCOPE.read_text());cand=json.loads(Path(args.candidate).read_text())
 prior={r["source"]:tuple(r["pair"]) for r in scope["source_bound_corollary"]["rows"]}
 pair_binding=all(tuple(s["pair"])==prior.get(s["source"]) for s in pre["frozen_sources"])
 rows=[row(s) for s in pre["frozen_sources"]]
 applies=[r["source"] for r in rows if r["outcome"].startswith("THEOREM_APPLIES__")]
 exact_only=[r["source"] for r in rows if r["outcome"]=="THEOREM_EXACT_SWAP_APPLIES_BUT_E3_RESOURCE_BOUND_OUTSIDE_SCOPE"]
 nonapp=[r["source"] for r in rows if r["outcome"].startswith("THEOREM_NOT_APPLICABLE__")]
 summary={"applicability_count":len(applies),"applicable_sources":applies,"exact_swap_only_outside_resource_count":len(exact_only),"exact_swap_only_outside_resource_sources":exact_only,"not_applicable_count":len(nonapp),"not_applicable_sources":nonapp}
 checks={
  "candidate_pass":cand.get("verdict")=="PASS_SIX_SOURCE_COROLLARY_MEASUREMENT_COMPLETE",
  "candidate_not_imported":True,
  "pair_binding":pair_binding,
  "rows_equal":rows==cand.get("rows"),
  "summary_equal":summary==cand.get("summary"),
  "no_halt":all(r["outcome"]!="HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE" for r in rows),
 }
 return {"verdict":"PASS_INDEPENDENT_SIX_SOURCE_COROLLARY_RECOMPUTATION" if all(checks.values()) else "FAIL_INDEPENDENT_SIX_SOURCE_COROLLARY_MISMATCH","candidate_imported":False,"checks":checks,"rows":rows,"summary":summary,"resource_receipt":{"direct_exact_check_calls":0,"e3_discovery_calls":0,"solver_calls":0}}

if __name__=="__main__":print(json.dumps(main(),sort_keys=True,separators=(",",":")))
