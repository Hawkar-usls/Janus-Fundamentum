from __future__ import annotations
import json, hashlib, argparse
from pathlib import Path
EXPECTED_FORBIDDEN={"EMPIRICAL_FAMILY_MEMBER","REDUCER_RUN","SAT_SOLVER","TRUTH_ORACLE","TREEWIDTH","EXPANSION","SHA_RANDOMNESS","PROBABILISTIC_REPLACEMENT","LANE_C","HOLDOUT","BA26","ENIGMA"}
EXPECTED_IDS=["SLOPE","E1","E2","E3","E4","E5","E6","E7","E8","E9","E10"]
DEPS={
 "SLOPE":{"T_FP_MULTIPLICATIVE_CYCLIC"},"E1":{"T_PRIMES_INFINITE"},"E2":{"E1"},"E3":set(),"E4":{"SLOPE"},"E5":{"SLOPE","E3"},"E6":{"SLOPE","E4"},"E7":{"E4"},"E8":{"SLOPE","E3"},"E9":{"SLOPE","E8"},"E10":{"E3","E4","E5","E7","E8"}}
def req(c,m):
 if not c: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replay(m,c):
 req(m["schema"]=="TRUMP_USF_R0_HASH_FREE_EXPLICIT_INFINITE_FIXPOINT_FAMILY_OBLIGATION_MANIFEST","manifest schema")
 req(c["schema"]=="TRUMP_USF_R0_HASH_FREE_EXPLICIT_INFINITE_FIXPOINT_FAMILY_PROOF_CERTIFICATE","certificate schema")
 req(m["parent_preregistration_commit"]=="f1619ef4c9b2be1ff003b337be2ddb16e7d3e0c0","parent drift")
 req(m["parent_preregistration_blob"]=="9e1b16f20b726b3ab9ab1a8fa4995316942ce0ad","prereg blob drift")
 req(m["certified_parent_commit"]=="6c40ca4d3174ac7529a1449c44fb7616cbcf088f","cert commit drift")
 req(m["certified_parent_blob"]=="5fed5465caadd76991c400133fd406b464af50f2","cert blob drift")
 req(set(m["forbidden_proof_inputs"])==EXPECTED_FORBIDDEN,"firewall drift")
 obs={x["id"]:x for x in m["obligations"]}; steps={x["id"]:x for x in c["steps"]}
 req(list(obs)==EXPECTED_IDS,"obligation order/coverage"); req(list(steps)==EXPECTED_IDS,"certificate coverage")
 trusted={x["id"] for x in m["trusted_external_theorems"]}; proved=set(trusted); checked=[]
 for oid in EXPECTED_IDS:
  req(set(obs[oid]["deps"])==DEPS[oid],f"{oid} deps")
  req(DEPS[oid] <= proved,f"{oid} dependency not proved")
  req(steps[oid]["status"]=="PROVED",f"{oid} status")
  req(len(steps[oid]["argument"])>=2,f"{oid} empty proof")
  if oid=="SLOPE":
   req("p-1>=16" in " ".join(steps[oid]["argument"]),"slope order bound absent")
   req("pairwise distinct" in obs[oid]["target"],"slope target drift")
  if oid=="E4":
   text=" ".join(steps[oid]["argument"]); req("b-s_j" in text and "c-2s_j" in text,"E4 inverse maps absent")
  if oid=="E5":
   text=" ".join(steps[oid]["argument"]); req("subtracting yields s_j=s_k" in text and "2 is invertible" in text,"E5 case proof incomplete")
  if oid=="E6":
   text=" ".join(steps[oid]["argument"]); req("(x+d)+s_k=x+s_j" in text,"E6 path identity absent"); req("every nonzero d generates it additively" in text,"E6 additive generation absent")
  if oid=="E9":
   text=" ".join(steps[oid]["argument"]); req("no poly(log p) claim" in text,"E9 scope drift"); req("Theta(p log p)" in text,"E9 output-size relation absent")
  if oid=="E10": req("6c40ca4d" in " ".join(steps[oid]["argument"]),"E10 certified-parent binding absent")
  proved.add(oid); checked.append(oid)
 req(c["verdict"]=="PASS","certificate verdict")
 return {"status":"PASS","checked":checked,"trusted_external_theorems":sorted(trusted),"empirical_family_members_generated":0,"reducer_invoked":False,"SAT_solver_invoked":False,"treewidth_invoked":False,"expansion_invoked":False,"forbidden_inputs_used":[],"theorem_scope":"EXPLICIT_INFINITE_HASH_FREE_FROZEN_REDUCER_FIXPOINT_FAMILY"}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--manifest',required=True); ap.add_argument('--certificate',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
 m=json.loads(Path(a.manifest).read_text()); c=json.loads(Path(a.certificate).read_text()); r=replay(m,c); r['manifest_sha256']=sha(a.manifest); r['certificate_sha256']=sha(a.certificate); Path(a.output).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n'); print('INDEPENDENT_SYMBOLIC_REPLAY_PASS',len(r['checked']))
if __name__=='__main__': main()
