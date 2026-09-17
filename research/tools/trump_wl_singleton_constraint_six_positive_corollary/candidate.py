from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_SIX_POSITIVE_COROLLARY_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_SIX_POSITIVE_COROLLARY_REVIEW_2026-09-18_v1.0.json"
THEOREM=ROOT/"research/TRUMP_WL_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_RESULT_2026-09-18_v1.0.json"
SCOPE=ROOT/"research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_RESULT_2026-09-18_v1.0.json"
PROJECTION=ROOT/"research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
WL=ROOT/"research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py"
ORBIT=ROOT/"research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
EXPECTED={
 PREREG:"d0e25c69006f2e54ee8d52e4d3c06ce213e943af",
 REVIEW:"9ac39a874395fd03c920d3a069cafc0dc5fbf1f7",
 THEOREM:"eda86821031e43dad76ff81f7239d3ca27387cc7",
 SCOPE:"3cbf05cb0b0249ddf365bc43d176a06ddb7f72af",
 PROJECTION:"2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
 WL:"6b697fd8b3de4c83f8226b06399b6bad99953d4e",
 ORBIT:"a076cfc56d68aad0348415e313705da1f6b9cdcd",
}

def blob(path:Path)->str:
 d=path.read_bytes();return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()

def parse(path:Path):
 clauses=[];buf=[];header=None
 for raw in path.read_text(encoding="utf-8").splitlines():
  s=raw.strip()
  if not s or s.startswith("c") or s in {"%","0"}:continue
  if s.startswith("p "):
   p=s.split();header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:
    if len(buf)!=3 or len({abs(x) for x in buf})!=3:raise ValueError("BAD_3CNF")
    clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 if header!=(20,91) or len(clauses)!=91 or buf:raise ValueError(f"UF20_CONTRACT:{header}:{len(clauses)}:{buf}")
 return clauses

def generic_round(raw):
 degree=Counter()
 for c in raw["constraints"]:
  for v in set(map(int,c["scope"])):degree[v]+=1
 D={int(v) for v in raw["variables"] if degree[int(v)]==1}
 T={str(c["id"]) for c in raw["constraints"] if D & set(map(int,c["scope"]))}
 return {
  "variables":[int(v) for v in raw["variables"] if int(v) not in D],
  "constraints":[c for c in raw["constraints"] if str(c["id"]) not in T],
 },sorted(D),sorted(T)

def measure_row(spec):
 source=spec["source"];path=ROOT/spec["path"];pair=tuple(map(int,spec["pair"]))
 if blob(path)!=spec["git_blob"]:
  return {"source":source,"outcome":"HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE","reason":"SOURCE_BLOB","pair":list(pair)}
 clauses=parse(path)
 raw,_=projection_identity.normalize_projection(source,clauses)
 reduced,D,T=generic_round(raw)
 nodes,adj,labels=wl_ref.incidence_structure(reduced)
 colors,rounds=wl_ref.wl1(nodes,adj,labels)
 node_by_var={n[1]:n for n in nodes if n[0]=="v"}
 pair_present=pair[0] in node_by_var and pair[1] in node_by_var
 pair_same=bool(pair_present and colors[node_by_var[pair[0]]]==colors[node_by_var[pair[1]]])
 cs=[n for n in nodes if n[0]=="c"];counts=Counter(colors[n] for n in cs)
 nonsingleton=sorted([{"color":int(col),"size":int(sz)} for col,sz in counts.items() if sz>1],key=lambda x:(x["size"],x["color"]))
 all_singleton=not nonsingleton
 formula=orbit.validate_and_normalize(reduced)
 n=len(formula.variables);L=formula.L
 bound=(n>=2 and 3*(2**(n-2))<=L*L)
 if not pair_same:
  outcome="THEOREM_NOT_APPLICABLE__PAIR_NOT_SAME_WL1_COLOR"
 elif not all_singleton:
  outcome="THEOREM_NOT_APPLICABLE__NON_SINGLETON_CONSTRAINT_COLOR_EXISTS"
 elif not bound:
  outcome="THEOREM_EXACT_SWAP_APPLIES_BUT_E3_RESOURCE_BOUND_OUTSIDE_SCOPE"
 else:
  outcome="THEOREM_APPLIES__EXACT_SWAP_AND_E3_ADMISSION_FOLLOW_WITHOUT_DIRECT_EXACT_SELECTOR_CALL"
 return {
  "source":source,"pair":list(pair),"pair_present":pair_present,"pair_same_stable_wl1_color":pair_same,
  "constraint_count":len(cs),"constraint_color_class_count":len(counts),"all_constraint_nodes_singleton":all_singleton,
  "non_singleton_constraint_color_classes":nonsingleton,"wl1_rounds":rounds,
  "degree1_variables":D,"removed_constraint_ids":T,
  "residual_n":n,"residual_L":L,"resource_bound_value":3*(2**(n-2)) if n>=2 else None,"L2":L*L,
  "resource_bound_holds":bound,"outcome":outcome,
 }

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
 if not all(bindings.values()):return {"verdict":"HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE","authority_bindings":bindings}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());theorem=json.loads(THEOREM.read_text());scope=json.loads(SCOPE.read_text())
 guards={
  "prereg_frozen":pre.get("status")=="FROZEN_AFTER_THEOREM_PASS_AND_BEFORE_SIX_SOURCE_APPLICABILITY_MEASUREMENT",
  "review_authorized":review.get("review_verdict")=="PASS_CLEAN_SIX_POSITIVE_SOURCE_BOUND_COROLLARY_SPEC__AUTHORIZED_TO_MEASURE_ONCE",
  "theorem_pass":theorem.get("scientific_outcome")=="PASS_SINGLETON_CONSTRAINT_WL_COLOR_IMPLIES_EXACT_SWAP_ON_R000_R111_RESIDUALS",
  "scope_theorem_pass":scope.get("scientific_outcome")=="PASS_SCOPE_BOUND_DIRECT_EXACT_TRANSPOSITION_WITNESS_SUFFICIENCY_FOR_FROZEN_E3",
 }
 if not all(guards.values()):return {"verdict":"HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE","guards":guards}
 prior={r["source"]:tuple(r["pair"]) for r in scope.get("source_bound_corollary",{}).get("rows",[])}
 specs=pre["frozen_sources"]
 pair_binding=all(tuple(s["pair"])==prior.get(s["source"]) for s in specs)
 if not pair_binding:return {"verdict":"HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE","reason":"PAIR_BINDING_TO_PRIOR_SCOPE_RESULT"}
 rows=[measure_row(s) for s in specs]
 if any(r["outcome"]=="HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE" for r in rows):
  return {"verdict":"HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE","rows":rows}
 applies=[r["source"] for r in rows if r["outcome"].startswith("THEOREM_APPLIES__")]
 exact_only=[r["source"] for r in rows if r["outcome"]=="THEOREM_EXACT_SWAP_APPLIES_BUT_E3_RESOURCE_BOUND_OUTSIDE_SCOPE"]
 nonapp=[r["source"] for r in rows if r["outcome"].startswith("THEOREM_NOT_APPLICABLE__")]
 return {
  "artifact_id":"JANUS-TRUMP-WL-SINGLETON-CONSTRAINT-SIX-POSITIVE-COROLLARY-CANDIDATE-2026-09-18-v1.0",
  "verdict":"PASS_SIX_SOURCE_COROLLARY_MEASUREMENT_COMPLETE",
  "authority_bindings":bindings,"guards":guards,"pair_binding_to_prior_scope_result":pair_binding,
  "rows":rows,
  "summary":{"applicability_count":len(applies),"applicable_sources":applies,"exact_swap_only_outside_resource_count":len(exact_only),"exact_swap_only_outside_resource_sources":exact_only,"not_applicable_count":len(nonapp),"not_applicable_sources":nonapp},
  "resource_receipt":{"source_reads":6,"projection_runs":6,"pendant_rounds":6,"wl1_runs":6,"direct_exact_check_calls":0,"e3_discovery_calls":0,"solver_calls":0},
  "scientific_firewall":{"GENERAL_SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"},
 }

if __name__=="__main__":print(json.dumps(main(),sort_keys=True,separators=(",",":")))
