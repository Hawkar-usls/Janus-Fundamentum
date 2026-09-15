from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID="JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-TWO-VARIABLE-SEPARATOR-FACTORIZED-PAYLOAD-CANDIDATE-2026-09-15-v1.0"
AUTHORITY="CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG=Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB="08579c4bcfecce6d006c2a3b1d53cc78e333ce70"
PARENT=Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.9.json")
PARENT_BLOB="9d0c49695b2201d05ba00f13c65d55ac848ba3fc"
V38=Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
V38_BLOB="cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"
V36=Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
V36_BLOB="8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"

def root(): return Path(__file__).resolve().parents[3]
def blob(p):
 d=p.read_bytes(); return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()
def cb(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(o): return hashlib.sha256(cb(o)).hexdigest()
def source_guard():
 r=root(); checks={"prereg":blob(r/PREREG)==PREREG_BLOB,"parent":blob(r/PARENT)==PARENT_BLOB,"v38":blob(r/V38)==V38_BLOB,"v36":blob(r/V36)==V36_BLOB}
 return {"ok":all(checks.values()),"checks":checks}
def firewall(): return {"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","CONNECTED_MIXED_CORE_SOLVED":"NO","GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY":"NOT_PROVED","GENERAL_PARTIAL_OVERLAP_FACTORIZATION":"NOT_PROVED","GLOBAL_APMA_FRONTIER_ADVANCE":"NONE_PENDING_HQ_REVIEW","SCOPE":"UNIQUE_COMMON_CORE_WITH_RAW_DERIVED_RESIDUAL_VARIABLE_PAIR_WHOSE_FOUR_BRANCHES_REDUCE_TO_COMPONENT_SIZE_AT_MOST_TWO_OR_EXACT_UNSAT"}

def rscope(f,core): return {int(v) for v in f["scope"] if int(v) not in set(core)}
def comps(scopes):
 n=len(scopes);p=list(range(n))
 def find(x):
  while p[x]!=x:p[x]=p[p[x]];x=p[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:p[max(a,b)]=min(a,b)
 for i in range(n):
  for j in range(i+1,n):
   if scopes[i]&scopes[j]:union(i,j)
 g={}
 for i in range(n):g.setdefault(find(i),[]).append(i)
 return sorted((sorted(x) for x in g.values()),key=lambda x:(x[0],len(x),x))

def target_component(prep): return next(c for c in prep["residual_components"] if len(c)>2)
def pair_disconnects(prep,pair):
 tc=target_component(prep);ss=[rscope(prep["conditioned"][i],prep["core"]) for i in tc]
 return len(comps([s-set(pair) for s in ss]))>len(comps(ss))

def restrict_pair_factor(f,pair,values):
 os=[int(v) for v in f["scope"]]; rows=[tuple(int(x) for x in r) for r in f["rows"]]; wanted=dict(zip(pair,values)); keep_positions=[i for i,v in enumerate(os) if v not in wanted]; ns=[os[i] for i in keep_positions]; witness={}
 for r in rows:
  if any(v in os and r[os.index(v)]!=bit for v,bit in wanted.items()):continue
  nr=tuple(r[i] for i in keep_positions);witness.setdefault(nr,r)
 if not witness:return None,{"factor_id":f["id"],"surviving_rows":0}
 return {**f,"scope":ns,"rows":sorted(witness),"_pair_origin_scope":os,"_pair_origin_witness":witness,"_separator_pair":list(pair),"_separator_values":list(values)},{"factor_id":f["id"],"surviving_rows":len(witness)}

def branch_structure(prep,pair,values):
 fs=[];rec=[]
 for f in prep["conditioned"]:
  z,r=restrict_pair_factor(f,pair,values);rec.append(r)
  if z is None:return {"status":"EXACT_UNSAT_BY_EMPTY_PAIR_RESTRICTION","values":list(values),"factors":None,"residual_components":[],"restriction_receipt":rec}
  fs.append(z)
 cs=v36.residual_components(fs,prep["core"])
 if any(len(c)>2 for c in cs):return {"status":"OPEN_PAIR_BRANCH_RESIDUAL_COMPONENT_GT2","values":list(values),"factors":fs,"residual_components":cs,"restriction_receipt":rec}
 return {"status":"READY_PAIR_BRANCH_LE2","values":list(values),"factors":fs,"residual_components":cs,"restriction_receipt":rec}

def pair_candidates(prep):
 tc=target_component(prep);vs=sorted(set().union(*(rscope(prep["conditioned"][i],prep["core"]) for i in tc)));out=[]
 for pair in itertools.combinations(vs,2):
  if not pair_disconnects(prep,pair):continue
  bs=[branch_structure(prep,pair,v) for v in ((0,0),(0,1),(1,0),(1,1))]
  ok=all(b["status"] in {"READY_PAIR_BRANCH_LE2","EXACT_UNSAT_BY_EMPTY_PAIR_RESTRICTION"} for b in bs)
  out.append({"pair":list(pair),"branch_statuses":[b["status"] for b in bs],"structural_ok":ok})
 return out

def proposal(prep,pair,cands):
 body={"kind":"UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_TO_LE2_BRANCH_PORTFOLIOS","raw_object_sha256":sha(prep["canonical"]),"separator_pair":list(pair),"branch_values":[[0,0],[0,1],[1,0],[1,1]],"candidate_pairs":[c["pair"] for c in cands],"truth_authority":False,"proof_authority":False,"automatic_promotion":False};body["proposal_sha256"]=sha(body);return body
def verify(prep,pair,cands,p):
 body=dict(p);claimed=body.pop("proposal_sha256",None);return isinstance(claimed,str) and sha(body)==claimed and p==proposal(prep,pair,cands)

def portfolio_prep(prep,branch): return {"ready":prep["ready"],"canonical":prep["canonical"],"core":prep["core"],"state":prep["state"],"conditioned":branch["factors"],"residual_components":branch["residual_components"]}
def original_row(f,r): return tuple(int(x) for x in f.get("_pair_origin_witness",{}).get(tuple(r),tuple(r)))
def reconstruct(prep,portfolio,pair,values,assignment0):
 a={int(k):int(v) for k,v in assignment0.items()};cut=set(int(v) for v in prep["ready"]["cut"]);internal={int(v) for gi in prep["ready"]["component"] for v in prep["canonical"]["constraints"][gi]["scope"] if int(v) not in cut}
 for v in internal:a.pop(v,None)
 for v,b in zip(prep["core"],prep["state"]):a[int(v)]=int(b)
 for v,b in zip(pair,values):a[int(v)]=int(b)
 chosen=[]
 for c in portfolio["carriers"]:
  key=tuple(int(a[v]) for v in c["boundary_scope"]);w=c["witness"].get(key)
  if w is None:return {"ok":False,"reason":"BOUNDARY_TUPLE_MISSING"}
  rr=[w] if len(c["factors"])==1 else list(w)
  for f,r in zip(c["factors"],rr):
   orow=original_row(f,tuple(r));oscope=[int(v) for v in f.get("_pair_origin_scope",f["scope"])]
   for v,b in zip(oscope,orow):
    if v in a and a[v]!=int(b):return {"ok":False,"reason":"ORIGINAL_ROW_CONFLICT","variable":v}
    a[v]=int(b)
   chosen.append({"factor_id":f["id"],"original_sorted_row":list(orow)})
 ok=guarded.verify_original_assignment(prep["canonical"],a);return {"ok":ok,"assignment":a,"chosen_rows":chosen}

def execute_branch(prep,pair,values):
 b=branch_structure(prep,pair,values)
 if b["status"]=="EXACT_UNSAT_BY_EMPTY_PAIR_RESTRICTION":return {"values":list(values),"status":b["status"],"exact_unsat":True,"exact_sat":False}
 if b["status"]!="READY_PAIR_BRANCH_LE2":return {"values":list(values),"status":b["status"],"exact_unsat":False,"exact_sat":False,"residual_components":b.get("residual_components",[])}
 bp=portfolio_prep(prep,b);port=v36.build_portfolio(bp)
 if port.get("status")=="EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN":return {"values":list(values),"status":port["status"],"exact_unsat":True,"exact_sat":False}
 if port.get("status")!="ADMIT_RESIDUAL_LE2_PORTFOLIO":return {"values":list(values),"status":port.get("status","OPEN_PORTFOLIO"),"exact_unsat":False,"exact_sat":False}
 transformed=canonicalize_raw(v36._transformed_raw(bp,port));tcs=parent_support.constraint_components_after_cut(transformed,list(prep["ready"]["cut"]));hand=guarded.run_guarded_elimination(transformed,list(prep["ready"]["cut"]),tcs)
 rec={"values":list(values),"residual_component_sizes":[len(c) for c in b["residual_components"]],"portfolio_records":port["metrics"]["residual_component_count"],"pair_join_count":port["metrics"]["pair_join_count"],"three_plus_join_chains_materialized":0,"global_residual_cartesian_products_materialized":0,"handoff_terminal":hand.get("status")}
 if hand.get("status")=="EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":return {"values":list(values),"status":"EXACT_UNSAT_BY_PAIR_SEPARATOR_BRANCH_HANDOFF","exact_unsat":True,"exact_sat":False,"receipt":rec}
 if hand.get("status")!="ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":return {"values":list(values),"status":"OPEN_PAIR_SEPARATOR_BRANCH_HANDOFF","exact_unsat":False,"exact_sat":False,"receipt":rec}
 rr=reconstruct(prep,port,pair,values,{int(k):int(v) for k,v in hand["witness"]["assignment"].items()});rec["original_witness_verified"]=bool(rr["ok"])
 if not rr["ok"]:return {"values":list(values),"status":"OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE","exact_unsat":False,"exact_sat":False,"receipt":rec}
 return {"values":list(values),"status":"ADMIT_EXACT_PAIR_SEPARATOR_BRANCH_SAT","exact_unsat":False,"exact_sat":True,"receipt":rec,"witness":{str(v):int(rr["assignment"][v]) for v in sorted(rr["assignment"])},"witness_verified":True}

def build(raw,p_override=None):
 prep=v38._prepare(raw)
 if prep.get("status")!="READY":return prep
 cands=pair_candidates(prep);good=[c for c in cands if c["structural_ok"]]
 if not good:return {"status":"OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR","pair_candidates":cands,"pair_assignment_branches_enumerated":0,"three_plus_join_chains_materialized":0,"global_residual_cartesian_products_materialized":0}
 pair=tuple(good[0]["pair"]);p=p_override or proposal(prep,pair,cands)
 if not verify(prep,pair,cands,p):return {"status":"REJECT_TAMPERED_PROVENANCE"}
 bs=[execute_branch(prep,pair,v) for v in ((0,0),(0,1),(1,0),(1,1))];sat=next((b for b in bs if b.get("exact_sat") and b.get("witness_verified")),None);allu=all(b.get("exact_unsat") for b in bs)
 receipt={"separator_pair":list(pair),"branch_values":[[0,0],[0,1],[1,0],[1,1]],"branch_statuses":[b["status"] for b in bs],"pair_candidate_count":len(cands),"selected_pair_is_lexicographic_min_admissible":list(pair)==min(c["pair"] for c in good),"three_plus_join_chains_materialized":0,"global_residual_cartesian_products_materialized":0,"separator_sets_size_three_or_more":0,"budget_raised":False,"alternative_order_search":0,"external_solver_calls":0}
 if sat:return {"status":"ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD","proposal":p,"branches":bs,"receipt":receipt,"witness":sat["witness"],"witness_verified":True}
 if allu:return {"status":"EXACT_UNSAT_BY_ALL_PAIR_SEPARATOR_BRANCHES","proposal":p,"branches":bs,"receipt":receipt,"witness":None,"witness_verified":True}
 return {"status":"OPEN_PAIR_SEPARATOR_BRANCH_NOT_FULLY_ADMITTED","proposal":p,"branches":bs,"receipt":receipt}

def explain(raw):
 g=source_guard()
 if not g["ok"]:return {"artifact_id":ARTIFACT_ID,"status":"HALT_SOURCE_GUARD","source_guard":g,"scientific_firewall":firewall()}
 try:canonicalize_raw(raw)
 except RawBasisInputError as e:return {"artifact_id":ARTIFACT_ID,"status":"REJECT_RAW_INPUT","reason":str(e),"scientific_firewall":firewall()}
 c=build(raw);return {"artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"status":c["status"],"carrier":c,"source_guard":g,"scientific_firewall":firewall()}

def positive_control(): return v38.no_single_variable_articulation_control()
def branch_still_gt2_control(): return v38.branch_still_gt2_control()
def one_assignment_sat_control():
 raw=positive_control();s0=next(r for r in raw["constraints"] if r["id"]=="sticky_0");a,b=int(s0["scope"][-2]),int(s0["scope"][-1]);pa,pb=s0["scope"].index(a),s0["scope"].index(b);s0["allowed"]=[r for r in s0["allowed"] if int(r[pa])==1 and int(r[pb])==1];return raw
def all_assignments_unsat_control():
 raw=positive_control();s0=next(r for r in raw["constraints"] if r["id"]=="sticky_0");s1=next(r for r in raw["constraints"] if r["id"]=="sticky_1");s2=next(r for r in raw["constraints"] if r["id"]=="sticky_2");a,b=int(s0["scope"][-2]),int(s0["scope"][-1]);pa,pb=s0["scope"].index(a),s0["scope"].index(b);s0["allowed"]=[r for r in s0["allowed"] if not(int(r[pa])==0 and int(r[pb])==0)];p1=s1["scope"].index(a);s1["allowed"]=[r for r in s1["allowed"] if int(r[p1])==0];p2=s2["scope"].index(b);s2["allowed"]=[r for r in s2["allowed"] if int(r[p2])==0];return raw
def no_pair_k4_control():
 raw=cc_v1.filtered_still_overbudget_control();rels=[next(r for r in raw["constraints"] if r["id"]==f"sticky_{i}") for i in range(4)];start=max(raw["variables"])+1;es=list(range(start,start+6));raw["variables"].extend(es);trip=[(es[0],es[1],es[2]),(es[0],es[3],es[4]),(es[1],es[3],es[5]),(es[2],es[4],es[5])]
 for rel,vs in zip(rels,trip):
  cores=sorted({tuple(r[:-2]) for r in rel["allowed"]});rel["scope"]=rel["scope"][:-2]+list(vs);rel["allowed"]=[list(c)+list(bits) for c in cores for bits in itertools.product((0,1),repeat=3)]
 return raw
def injected_hint_control():
 raw=positive_control();raw["residual_pair_separator"]=[47,48];return raw
def tampered_control():
 raw=positive_control();prep=v38._prepare(raw);c=pair_candidates(prep);good=[x for x in c if x["structural_ok"]]
 if not good:return {"status":"HALT_NO_PAIR_FOR_TAMPER"}
 pair=tuple(good[0]["pair"]);p=proposal(prep,pair,c);p["branch_values"]=list(reversed(p["branch_values"]));return build(raw,p)
def main():
 out={"artifact_id":ARTIFACT_ID,"positive":explain(positive_control()),"branch_still_gt2":explain(branch_still_gt2_control()),"one_assignment_sat":explain(one_assignment_sat_control()),"all_assignments_unsat":explain(all_assignments_unsat_control()),"no_pair_k4":explain(no_pair_k4_control()),"hint":explain(injected_hint_control()),"tamper":tampered_control(),"scientific_firewall":firewall()};print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
