from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as cand
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded

ARTIFACT_ID="JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-TWO-VARIABLE-SEPARATOR-FACTORIZED-PAYLOAD-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT="PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1"
CAND=Path("research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py")
CAND_BLOB="0853ebb9a3e273fdaeca172dbe2502cc7214cf61"
def root():return Path(__file__).resolve().parents[3]
def blob(p):
 d=p.read_bytes();return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()
def rscope(f,core):return {int(v) for v in f["scope"] if int(v) not in set(core)}
def bfs(ss):
 n=len(ss);adj={i:[] for i in range(n)}
 for i in range(n):
  for j in range(i+1,n):
   if ss[i]&ss[j]:adj[i].append(j);adj[j].append(i)
 seen=set();out=[]
 for s in range(n):
  if s in seen:continue
  seen.add(s);q=[s];c=[]
  while q:
   u=q.pop(0);c.append(u)
   for w in adj[u]:
    if w not in seen:seen.add(w);q.append(w)
  out.append(sorted(c))
 return sorted(out,key=lambda x:(x[0],len(x),x))
def restrict(f,pair,vals):
 sc=[int(v) for v in f["scope"]];want=dict(zip(pair,vals));keep=[i for i,v in enumerate(sc) if v not in want];rows=[]
 for r in f["rows"]:
  r=tuple(int(x) for x in r)
  if all(v not in sc or r[sc.index(v)]==b for v,b in want.items()):rows.append(tuple(r[i] for i in keep))
 rows=sorted(set(rows));return None if not rows else {**f,"scope":[sc[i] for i in keep],"rows":rows}
def independent(raw):
 p=v38._prepare(raw)
 if p.get("status")!="READY":return {"status":p.get("status")}
 tc=next(c for c in p["residual_components"] if len(c)>2);tfs=[p["conditioned"][i] for i in tc];ss=[rscope(f,p["core"]) for f in tfs];base=len(bfs(ss));vs=sorted(set().union(*ss));cands=[]
 for pair in itertools.combinations(vs,2):
  if len(bfs([s-set(pair) for s in ss]))<=base:continue
  statuses=[];ok=True
  for vals in ((0,0),(0,1),(1,0),(1,1)):
   fs=[];empty=False
   for f in p["conditioned"]:
    z=restrict(f,pair,vals)
    if z is None:empty=True;break
    fs.append(z)
   if empty:statuses.append("EXACT_UNSAT_BY_EMPTY_PAIR_RESTRICTION");continue
   cs=bfs([rscope(f,p["core"]) for f in fs]);bad=any(len(c)>2 for c in cs);statuses.append("OPEN_PAIR_BRANCH_RESIDUAL_COMPONENT_GT2" if bad else "READY_PAIR_BRANCH_LE2");ok &= not bad
  cands.append({"pair":list(pair),"branch_statuses":statuses,"structural_ok":ok})
 good=[c for c in cands if c["structural_ok"]];return {"status":"READY" if good else "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR","selected_pair":good[0]["pair"] if good else None,"candidates":cands,"canonical":p["canonical"]}
def carrier(o):return o.get("carrier",{})
def statuses(o):return [b.get("status") for b in carrier(o).get("branches",[])]
def witness_ok(raw,o):
 w=carrier(o).get("witness");p=v38._prepare(raw)
 return isinstance(w,dict) and p.get("status")=="READY" and guarded.verify_original_assignment(p["canonical"],{int(k):int(v) for k,v in w.items()})
def run():
 raws={"pos":cand.positive_control(),"leaf":cand.branch_still_gt2_control(),"one":cand.one_assignment_sat_control(),"all":cand.all_assignments_unsat_control(),"k4":cand.no_pair_k4_control()};ind={k:independent(v) for k,v in raws.items()};out={k:cand.explain(v) for k,v in raws.items()};hint=cand.explain(cand.injected_hint_control());tamper=cand.tampered_control();pc=carrier(out["pos"]);lc=carrier(out["leaf"])
 checks={"G1_blob":blob(root()/CAND)==CAND_BLOB,"G1_guard":cand.source_guard()["ok"] is True,"G2_pos_pair_ind":ind["pos"].get("selected_pair")==[47,48],"G2_pos_pair_candidate":pc.get("receipt",{}).get("separator_pair")==[47,48],"G3_pos_sat":out["pos"].get("status")=="ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD","G3_pos_witness":witness_ok(raws["pos"],out["pos"]),"G4_four_branches":len(pc.get("branches",[]))==4,"G5_leaf_pair_ind":ind["leaf"].get("selected_pair")==[47,48],"G5_leaf_pair_candidate":lc.get("receipt",{}).get("separator_pair")==[47,48],"G5_leaf_sat":out["leaf"].get("status")=="ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD","G6_one_assignment":out["one"].get("status")=="ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD" and sum(1 for s in statuses(out["one"]) if s=="ADMIT_EXACT_PAIR_SEPARATOR_BRANCH_SAT")==1,"G7_all_unsat":out["all"].get("status")=="EXACT_UNSAT_BY_ALL_PAIR_SEPARATOR_BRANCHES","G8_k4_ind_open":ind["k4"].get("status")=="OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR","G8_k4_candidate_open":out["k4"].get("status")=="OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR","G9_hint":hint.get("status")=="REJECT_RAW_INPUT","G9_tamper":tamper.get("status")=="REJECT_TAMPERED_PROVENANCE","G10_zero_join":pc.get("receipt",{}).get("three_plus_join_chains_materialized")==0,"G10_zero_product":pc.get("receipt",{}).get("global_residual_cartesian_products_materialized")==0,"G10_no_ge3":pc.get("receipt",{}).get("separator_sets_size_three_or_more")==0,"FW_pvsnp":cand.firewall()["P_VS_NP"]=="OPEN","FW_sat":cand.firewall()["GENERAL_SAT_IN_P"]=="NOT_PROVED","FW_separator":cand.firewall()["GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY"]=="NOT_PROVED"}
 verdict=VERDICT if all(checks.values()) else "FAIL_OR_OPEN_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1"
 return {"artifact_id":ARTIFACT_ID,"authority":"INDEPENDENT_CHECKER__SCOPED_ONLY","checks":checks,"controls":{"positive":out["pos"].get("status"),"positive_pair":pc.get("receipt",{}).get("separator_pair"),"positive_statuses":statuses(out["pos"]),"leaf":out["leaf"].get("status"),"leaf_pair":lc.get("receipt",{}).get("separator_pair"),"leaf_statuses":statuses(out["leaf"]),"one":out["one"].get("status"),"one_statuses":statuses(out["one"]),"all":out["all"].get("status"),"all_statuses":statuses(out["all"]),"k4":out["k4"].get("status"),"k4_independent":ind["k4"].get("status"),"hint":hint.get("status"),"tamper":tamper.get("status")},"independent_methods":{"componentization":"BFS","pair_discovery":"UNORDERED_PAIR_SCAN","candidate_pair_helpers_used":False,"witness":"FULL_ORIGINAL_RELATION_REPLAY"},"scientific_firewall":cand.firewall(),"verdict":verdict}
def main():print(json.dumps(run(),sort_keys=True))
if __name__=="__main__":main()
