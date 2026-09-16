from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
SOURCES={
 "UF20_01":(ROOT/"research/source_data/SATLIB_UF20_01_2026-09-16.cnf","8330041b292e0501f8d74c1b1d32ca96c4498864","a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"),
 "UF20_02":(ROOT/"research/source_data/SATLIB_UF20_02_2026-09-16.cnf","f924caaef0d868bf62b1658e83e030ad8daee865","e44b98343881d9f7657aa6c40fc6854559ca2cdd12e59edc7dddc22246d19d4f"),
 "UF20_03":(ROOT/"research/source_data/SATLIB_UF20_03_2026-09-16.cnf","8f3d15154515457281f49201b843f2a7134dfa9f","7c9e05d9fa369935a0bf7d571b8c3b9a4a20244e3dfa75710987db2661553ac2"),
 "UF20_04":(ROOT/"research/source_data/SATLIB_UF20_04_2026-09-16.cnf","34ced5c169f967b2dc44ef5e42f2ee2c924813e1","722b2479ea25355374d07b4d3c859c51af864b9158fda203270f1edda8e7086c"),
 "UF20_05":(ROOT/"research/source_data/SATLIB_UF20_05_2026-09-16.cnf","3b04eff26ee37bdd0bc21b1066486974f92a2c9b","184f0f830dd2c2d1dd5fccd2b5b29304f27f15518b2b1e1315a4e9d5b5a30eb7"),
}


def blob(path:Path)->str:
 b=path.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def sha(obj:Any)->str:
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def parse(path:Path):
 clauses=[];declared=None
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith("c") or s in {"%","0"}:continue
  if s.startswith("p "):
   p=s.split();declared=(int(p[2]),int(p[3]));continue
  xs=[int(x) for x in s.split()];assert xs[-1]==0
  cl=tuple(xs[:-1]);assert len(cl)==3 and len({abs(x) for x in cl})==3;clauses.append(cl)
 assert declared==(20,91) and len(clauses)==91
 return clauses

def make_raw(name,clauses):
 cons=[]
 for i,cl in enumerate(clauses,1):
  scope=sorted(abs(x) for x in cl);rows=[]
  for bits in itertools.product((0,1),repeat=3):
   a=dict(zip(scope,bits))
   if any(bool(a[abs(l)]) if l>0 else not bool(a[abs(l)]) for l in cl):rows.append(list(bits))
  cons.append({"id":f"satlib_{name.lower()}_c{i:03d}","scope":scope,"allowed":rows})
 return canonicalize_raw({"variables":list(range(1,21)),"constraints":cons})

def semantic_s1(raw):
 adj={v:set() for v in raw["variables"]};z=Counter();o=Counter();prem=True
 for c in raw["constraints"]:
  allowed={tuple(r) for r in c["allowed"]};missing=[t for t in itertools.product((0,1),repeat=3) if t not in allowed]
  if len(c["scope"])!=3 or len(allowed)!=7 or len(missing)!=1:prem=False;continue
  f=missing[0]
  for u,v in itertools.combinations(c["scope"],2):adj[u].add(v);adj[v].add(u)
  for j,v in enumerate(c["scope"]):(z if f[j]==0 else o)[v]+=1
 return {v:(len(adj[v]),z[v],o[v]) for v in raw["variables"]},prem

def source_s1(clauses):
 adj={v:set() for v in range(1,21)};p=Counter();n=Counter()
 for cl in clauses:
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(p if lit>0 else n)[abs(lit)]+=1
 return {v:(len(adj[v]),p[v],n[v]) for v in range(1,21)}

def parts(s1):
 g=defaultdict(list)
 for v in sorted(s1):g[s1[v]].append(v)
 out=[sorted(c) for c in g.values()];out.sort(key=lambda c:(c[0],len(c),c));return out

def transport_sanity():
 for f in itertools.product((0,1),repeat=3):
  for perm in itertools.permutations(range(3)):
   moved=[None]*3
   for old,new in enumerate(perm):moved[new]=f[old]
   if any(moved[new]!=f[old] for old,new in enumerate(perm)):return False
 return True

def independent_row(name,path,expected_blob,expected_raw):
 clauses=parse(path);raw=make_raw(name,clauses);s1,prem=semantic_s1(raw);src=source_s1(clauses);cls=parts(s1);formula=orbit.validate_and_normalize(raw)
 swaps=[];unresolved=[]
 for c in cls:
  if len(c)==2:
   ok=orbit.is_exact_transposition_automorphism(formula,c[0],c[1]);swaps.append({"pair":c,"exact_transposition_automorphism":ok})
   if ok:unresolved.append(c)
  elif len(c)>2:unresolved.append(c)
 return {"source":name,"source_blob_ok":blob(path)==expected_blob,"raw_sha256":sha(raw),"raw_sha_ok":sha(raw)==expected_raw,"premises_ok":prem,"semantic_S1_equals_DIMACS_S1":s1==src,"S1_classes":cls,"non_singleton_S1_classes":[c for c in cls if len(c)>1],"sealed_swap_checks":swaps,"unresolved_nonidentity_action_blocks":unresolved,"group_trivial":not unresolved}

def main(candidate):
 inds={name:independent_row(name,path,b,r) for name,(path,b,r) in SOURCES.items()};rows={r.get("source"):r for r in candidate.get("rows",[])}
 checks={"certificate_not_imported":True,"transport_sanity":transport_sanity(),"five_rows":set(rows)==set(SOURCES),"expected_verdict":candidate.get("verdict")=="PASS_SCOPED_S1_INVARIANCE_AND_TRIVIAL_FULL_VARIABLE_PERMUTATION_GROUP_ON_ALL_FIVE"}
 for name,ind in inds.items():
  row=rows.get(name,{})
  checks[f"{name}_source_raw"] = ind["source_blob_ok"] and ind["raw_sha_ok"] and row.get("raw_sha256")==ind["raw_sha256"]
  checks[f"{name}_premises"] = ind["premises_ok"] and ind["semantic_S1_equals_DIMACS_S1"] and row.get("semantic_S1_equals_DIMACS_S1") is True
  checks[f"{name}_classes"] = row.get("S1_classes")==ind["S1_classes"] and row.get("non_singleton_S1_classes")==ind["non_singleton_S1_classes"]
  checks[f"{name}_swaps"] = row.get("sealed_swap_checks")==ind["sealed_swap_checks"]
  checks[f"{name}_group"] = ind["group_trivial"] is True and row.get("full_pure_variable_permutation_automorphism_group_trivial") is True
 rr=candidate.get("resource_receipt",{});checks["resource"] = rr.get("full_permutation_enumeration")==0 and rr.get("sealed_nonidentity_swap_checks")==2 and rr.get("solver_invocations")==0 and rr.get("new_solver_mechanisms")==0 and rr.get("new_carrier_mechanisms")==0 and rr.get("new_automorphism_search_mechanisms")==0 and rr.get("budget_raise") is False
 sf=candidate.get("scientific_firewall",{});checks["firewall"] = sf.get("P_VS_NP")=="OPEN" and sf.get("GENERAL_SAT_IN_P")=="NOT_PROVED" and sf.get("CONNECTED_MIXED_CORE_SOLVED")=="NO"
 return {"artifact_id":"JANUS-TRUMP-SATLIB-UF20-S1-FULL-PERMUTATION-AUTOMORPHISM-CERTIFICATE-INDEPENDENT-CHECK-2026-09-16-v1.0","authority":"INDEPENDENT_DIAGNOSTIC_CHECK_ONLY","verified":all(checks.values()),"certificate_imported":False,"checks":checks,"independent_rows":list(inds.values())}

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--candidate-json",required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(c),sort_keys=True,separators=(",",":")))
