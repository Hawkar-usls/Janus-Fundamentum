#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any, Sequence
import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
import janus_c049_1_b4_6_3_node6_up_k_integration_parent_refinement as node6
import janus_c049_1_b4_4_nonzero_boundary_node_full_set as b44

SCHEMA="C049.1-B4.6.3-NODE7-UP-K-INTEGRATION-NODE8-PREFLIGHT-v1"
TERMINAL="OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
N7,N8,ROOT=7,8,10
N7_GEN,N7_ENTRIES,N8_PAIRS,N8_REFS=13,9108,327888,602017584
NODE6_RECEIPT="88170c8f5ba5519908e88f1dba21bb2247218c0713dc6830e562a879edd3aad9"
LEAF2_RECEIPT="758de0f2407674dd299c71e69450864e9a1b597050afd5e444e79f08341c0311"
LEAF3_RECEIPT="80f424b87fd39e80013e1bb96b3dcec47d281a322f9964472b2ca32bd039e086"
FRONTIER_SHA="6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
FRONTIER_SEM="ed6b59821aaef10ac6bdb6286a72ffcafd15e2bbd2619e0edffc7f711a2b1103"
CLASS_DIGEST="d531af7e4aa67eb5d5cf4b6cb37e4fb3074a21b1ea43e23c6a7d792d932a8b08"
UPK_SHA="c085a3bee4e0c92a01eb22715390079f9858c5704ebcbf8534f9de196087d189"
UPK_SEM="23079901348590eb39d60d904d52dfd5004f8b287382a288ccbea688802b22f2"
FAMILY_DIGEST="87ffbb8ba0ef420d3f4d9e48287f8ab3daa09ad54cbff05381539a5c9c254736"
ENTRIES_DIGEST="269d5cd926d3be3df5641066a7986dfb1df049abab68b4202f6bc9a39e27a46e"
STREAM_DIGEST="aac8623a3c8c13cf284b39de0f5966606f733dd0dc71a55d6fd4227abd49ef8e"

def cj(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def dg(v:Any)->str:return hashlib.sha256(cj(v)).hexdigest()
def fsha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict:return json.loads(p.read_text(encoding="utf-8"))
def pass10(v:dict)->bool:return len(v)==10 and set(v.values())=={"PASS"}

def sources(frontier_path:Path,upk_path:Path)->tuple[dict,dict]:
    f,u=load(frontier_path),load(upk_path)
    if fsha(frontier_path)!=FRONTIER_SHA or f.get("semantic_digest")!=FRONTIER_SEM or f.get("admit") is not True:raise AssertionError("frontier binding")
    if not pass10(f.get("invariant_vector",{})) or f["quotient_frontier"]["class_count"]!=N7_GEN or f["quotient_frontier"]["class_catalog_digest"]!=CLASS_DIGEST:raise AssertionError("frontier admission")
    if fsha(upk_path)!=UPK_SHA or u.get("semantic_digest")!=UPK_SEM or u.get("semantic_digest_scope")!="proof_payload":raise AssertionError("up_k binding")
    p=u["proof_payload"]
    if p.get("admit") is not True or not pass10(p.get("invariant_vector",{})):raise AssertionError("up_k admission")
    if p["input_generator_family_digest"]!=FAMILY_DIGEST:raise AssertionError("family digest")
    s=p["source"]
    if (s["node7_frontier_artifact_sha256"],s["node7_frontier_semantic_digest"],s["node7_frontier_class_catalog_digest"])!=(FRONTIER_SHA,FRONTIER_SEM,CLASS_DIGEST):raise AssertionError("up_k source")
    c=p["exact_reachable_closure"]
    if (c["complete_reachable_catalog_size"],c["reachable_entries_digest"],c["complete_reachable_catalog_stream_sha256"],c["global_compact_universe_enumerated"])!=(N7_ENTRIES,ENTRIES_DIGEST,STREAM_DIGEST,False):raise AssertionError("closure catalog")
    if dg(c["reachable_entries"])!=ENTRIES_DIGEST:raise AssertionError("entry payload")
    return f,p

def closure(p:dict)->dict:
    c=p["exact_reachable_closure"]; entries=copy.deepcopy(c["reachable_entries"]); work=sum(int(x) for x in p["work_ledger"].values())
    out={"ambient_dim":2,"k":1,"input_generators":copy.deepcopy(p["input_generators"]),"retained_generators":copy.deepcopy(p["retained_generators"]),"removals":[],"universe_size":N7_ENTRIES,"entries":entries,"entry_count":len(entries),"ledger":{"discovery_work":work,"work":0,"certified_total_charged_operations":work},"closure_method":"CERTIFIED_NODE7_THIRTEEN_GENERATOR_REACHABLE_CATALOG","global_universe_enumerated":False,"complete_reachable_catalog_proved":True,"input_generator_family_digest":FAMILY_DIGEST,"frontier_artifact_sha256":FRONTIER_SHA,"up_k_artifact_sha256":UPK_SHA,"up_k_semantic_digest":UPK_SEM,"reachable_entries_digest":ENTRIES_DIGEST,"reachable_catalog_stream_sha256":STREAM_DIGEST,"retained_class_ids":copy.deepcopy(p["retained_class_ids"]),"invariant_vector":copy.deepcopy(p["invariant_vector"]),"admit":True}
    if (len(out["input_generators"]),len(out["retained_generators"]),len(out["removals"]),out["entry_count"])!=(13,13,0,9108):raise AssertionError("closure cardinality")
    return out

def execute7(desc:dict,seq:int,left:dict,right:dict,scaffold:dict,writers:dict,cumulative:list[int],f:dict,p:dict):
    expected={"node_id":7,"kind":"SPINE_INTERNAL_JOIN","edge_index":1,"child_node_ids":[6,2],"left_factor_ids":[0,1],"right_factor_ids":[2],"covered_factor_ids":[0,1,2],"outside_factor_ids":[3,4,5]}
    if desc!=expected or dg(desc)!=f["source"]["node7_descriptor_digest"]:raise AssertionError("descriptor")
    if left["output_receipt"]["receipt_digest"]!=NODE6_RECEIPT or right["output_receipt"]["receipt_digest"]!=LEAF2_RECEIPT:raise AssertionError("child receipt")
    ambient=int(scaffold["d"]); blocks=[tuple(x) for x in scaffold["whole_factor_blocks"]]; offsets=[int(x) for x in scaffold["affine_offsets"]]
    lb,rb=tuple(left["boundary"]),tuple(right["boundary"]); common=engine.xor_basis((*lb,*rb),ambient); parent=engine.boundary([blocks[i] for i in desc["covered_factor_ids"]],[blocks[i] for i in desc["outside_factor_ids"]],ambient); g=f["node7_geometry"]
    if [list(lb),list(rb),list(common),list(parent)]!=[g["left_boundary_ambient"],g["right_boundary_ambient"],g["common_boundary_ambient"],g["parent_boundary_ambient"]] or common!=parent or common!=lb:raise AssertionError("geometry")
    part={"whole_factor_blocks":[list(x) for x in blocks],"affine_offsets":offsets,"scaffold_order":[int(x) for x in scaffold["scaffold_order"]],"child_node_ids":desc["child_node_ids"],"left_factor_ids":desc["left_factor_ids"],"right_factor_ids":desc["right_factor_ids"],"covered_factor_ids":desc["covered_factor_ids"],"outside_factor_ids":desc["outside_factor_ids"]}; pd=dg(part)
    cl=closure(p); starts={k:w.record_count+len(w.buffer) for k,w in writers.items()}; work=cl["ledger"]["certified_total_charged_operations"]; begin=cumulative[0]; cumulative[0]+=work
    receipt=engine.output_receipt(7,desc["kind"],desc["covered_factor_ids"],parent,cl,pd); zero={k.lower():engine.make_range(starts[k],starts[k]) for k in writers}; ids=p["retained_class_ids"]
    node={"node_id":7,"sequence_index":seq,"kind":desc["kind"],"child_node_ids":desc["child_node_ids"],"left_factor_ids":desc["left_factor_ids"],"right_factor_ids":desc["right_factor_ids"],"covered_factor_ids":desc["covered_factor_ids"],"outside_factor_ids":desc["outside_factor_ids"],"covered_affine_offsets":[offsets[i] for i in desc["covered_factor_ids"]],"grouped_partition_preserved":True,"partition_receipt":part,"partition_receipt_digest":pd,"input_full_set_receipts":[copy.deepcopy(left["output_receipt"]),copy.deepcopy(right["output_receipt"])],"child_boundaries":{"left":list(lb),"right":list(rb)},"common_join_boundary":list(common),"parent_boundary":list(parent),"boundary_dimensions":{"children":[len(lb),len(rb)],"common":len(common),"parent":len(parent)},"transport_contracts":{"left_child_to_common":engine.boundary_transport(lb,common,ambient),"right_child_to_common":engine.boundary_transport(rb,common,ambient),"parent_in_common_for_shrink":engine.boundary_transport(parent,common,ambient)},"side_conditions":{"certified_by_frontier_artifact":True,"left_expand_identity":g["left_expand_identity"],"shrink_identity":g["shrink_identity"],"join_lambda_correction_identically_zero":all(int(x["correction"])==0 for x in g["join_correction_table"]),"joined_symbol_map_injective":all(x["injective"] for x in g["joined_symbol_injectivity"])},"record_ranges":zero,"node_up_k":cl,"input_generator_provenance":[{"input_generator_index":i,"class_id":x} for i,x in enumerate(ids)],"retained_generator_provenance":[{"retained_generator_index":i,"class_id":x} for i,x in enumerate(ids)],"entry_provenance":[{"entry_index":i,"source_generator_index":int(e["source_generator_index"]),"source_class_id":e["source_class_id"]} for i,e in enumerate(cl["entries"])],"output_receipt":receipt,"certified_structural_bridge":{"frontier_artifact_sha256":FRONTIER_SHA,"up_k_artifact_sha256":UPK_SHA,"frontier_classes":13,"naive_child_pairs_covered":16848,"naive_refinements_covered":9744432,"generic_pair_records_materialized":0,"generic_refinement_records_materialized":0,"closure_entries_returned_to_executor":9108},"work_ledger":{"cumulative_work_at_node_start":begin,"cumulative_work_before_node_b2":begin,"node_b2_breakdown":{"certified_node7_proof_work":work},"node_b2_work_delta":work,"cumulative_work_at_node_end":cumulative[0],"monotone_by_construction":True},"audit":{"child_full_set_entries":[int(left["closure"]["entry_count"]),int(right["closure"]["entry_count"])],"child_pairs_processed":0,"lattice_paths_processed":0,"successful_refinements":0,"failed_refinements":0,"raw_precompact_join_statistics":0,"unique_successful_generators":13,"duplicate_successful_outputs_deleted":0,"b2_dominance_deletions":0,"retained_generators":13,"final_up_k_entries":9108,"cumulative_work_delta":work,"certified_child_pairs_covered":16848,"certified_naive_refinements_covered":9744432,"certified_reachability_witnesses":13}}
    node["node_execution_digest"]=dg(node)
    return node,{"node_id":7,"covered_factor_ids":desc["covered_factor_ids"],"boundary":list(parent),"closure":cl,"output_receipt":receipt}

def exact_refs(left:Sequence[dict],right:Sequence[dict])->int:return sum(b44.delannoy_path_count(len(a["trajectory"]),len(b["trajectory"])) for a in left for b in right)
def hist(entries:Sequence[dict])->dict[str,int]:
    out={}
    for e in entries:out[str(len(e["trajectory"]))]=out.get(str(len(e["trajectory"])),0)+1
    return dict(sorted(out.items(),key=lambda x:int(x[0])))

def build(prefix:Path,hardening_path:Path,frontier_path:Path,upk_path:Path,out:Path,pair_cap:int=10000,ref_cap:int=2000000)->dict:
    prefix_manifest,hardening,records=node6.load_frozen_hardening(prefix,hardening_path); f,p=sources(frontier_path,upk_path)
    if f["source"]["manifest_digest"]!="2ca2b0bc7566fb2e24f62e9df44499044843fa08388d8573fb74221dfab80512" or p["source"]["node7_frontier_source_manifest_digest"]!=f["source"]["manifest_digest"]:raise AssertionError("source manifest")
    osel,oup,oexec,ocap,ocfg=engine.selected_scaffold,engine.up_k_closure,engine.execute_node,engine.CAP,dict(engine.DEFAULT_CAPABILITY); calls6=[]; calls7=[]
    def up(g,d,k,l):
        if int(d)==2 and int(k)==1 and len(g)==468:
            if calls6:raise AssertionError("node6 twice")
            c=node6.certified_closure(g,d,k,hardening,records); calls6.append(c["reachable_entries_digest"]); return c
        return oup(g,d,k,l)
    def ex(desc,seq,left,right,scaffold,writers,cumulative,capability):
        if int(desc["node_id"])==7:
            if calls7:raise AssertionError("node7 twice")
            r=execute7(desc,seq,left,right,scaffold,writers,cumulative,f,p); calls7.append(r[0]["output_receipt"]["receipt_digest"]); return r
        return oexec(desc,seq,left,right,scaffold,writers,cumulative,capability)
    try:
        engine.selected_scaffold=negative.selected_negative_scaffold; engine.up_k_closure=up; engine.execute_node=ex; engine.CAP=2000000; engine.DEFAULT_CAPABILITY["max_child_pairs_per_node"]=int(pair_cap); engine.DEFAULT_CAPABILITY["max_refinements_per_node"]=int(ref_cap); manifest=engine.build(out,max_refinements_per_node=int(ref_cap))
    finally:
        engine.selected_scaffold,engine.up_k_closure,engine.execute_node,engine.CAP=osel,oup,oexec,ocap; engine.DEFAULT_CAPABILITY.clear(); engine.DEFAULT_CAPABILITY.update(ocfg)
    if len(calls6)!=1 or len(calls7)!=1 or manifest["execution"]["processed_internal_node_ids"]!=[6,7]:raise AssertionError("integration calls")
    stop=manifest["execution"]["stop"]
    if (int(stop["node_id"]),stop["reason"],int(stop["required"]),int(stop["cap"]),stop["no_layout_at_cap"],stop["terminal"])!=(8,"CHILD_PAIR_CAP_EXCEEDED",N8_PAIRS,int(pair_cap),False,TERMINAL):raise AssertionError("node8 stop")
    n7=next(x for x in manifest["node_results"] if int(x["node_id"])==7)
    if n7["node_up_k"]["entry_count"]!=9108 or n7["node_up_k"]["reachable_entries_digest"]!=ENTRIES_DIGEST or any(int(x["count"]) for x in n7["record_ranges"].values()):raise AssertionError("node7 state")
    leaf3=manifest["leaf_full_sets"][3]
    if leaf3["output_receipt"]["receipt_digest"]!=LEAF3_RECEIPT:raise AssertionError("leaf3")
    le,re=n7["node_up_k"]["entries"],leaf3["full_set"]["entries"]; pairs=len(le)*len(re); refs=exact_refs(le,re)
    if (pairs,refs)!=(N8_PAIRS,N8_REFS):raise AssertionError("node8 frontier")
    summary={"schema":SCHEMA,"source":{"prefix_manifest_digest":prefix_manifest["manifest_digest"],"hardening_artifact_sha256":node6.EXPECTED_HARDENING_SHA256,"frontier_artifact_sha256":FRONTIER_SHA,"frontier_semantic_digest":FRONTIER_SEM,"up_k_artifact_sha256":UPK_SHA,"up_k_semantic_digest":UPK_SEM},"certified_calls":{"node6":1,"node7":1},"integrated_manifest_digest":manifest["manifest_digest"],"integrated_transcript_root_digest":manifest["chunking"]["transcript_root_digest"],"node7":{"node_execution_digest":n7["node_execution_digest"],"output_receipt_digest":n7["output_receipt"]["receipt_digest"],"input_generators":13,"retained_generators":13,"direct_removals":0,"up_k_entries":9108,"reachable_entries_digest":ENTRIES_DIGEST,"generic_pair_records_materialized":0,"generic_refinement_records_materialized":0},"node8_preflight":{"left_child_node_id":7,"right_child_node_id":3,"left_entry_count":len(le),"right_entry_count":len(re),"child_pair_count":pairs,"naive_refinement_count":refs,"left_length_histogram":hist(le),"right_length_histogram":hist(re),"pair_cap":int(pair_cap),"refinement_cap":int(ref_cap),"stop_reason":stop["reason"],"no_layout_at_cap":False},"execution":copy.deepcopy(manifest["execution"]),"result":"HONEST_OPEN_AT_NODE8_PARENT_FRONTIER","strict_boundary":{"node7_up_k_admitted":True,"node7_integrated_into_bottom_up_executor":True,"node7_generic_cartesian_replay_required":False,"node8_parent_refinement_started":True,"node8_parent_refinement_complete":False,"node8_parent_up_k_complete":False,"negative_root_reached":False,"terminal_completeness_proved":False,"found_layout_enabled":False,"no_layout_at_cap_enabled":False,"current_global_terminal":TERMINAL,"p_vs_np":"OPEN"},"next_gate":"C049.1_B4.6.3_NODE8_PARENT_FRONTIER_STRUCTURAL_COMPRESSION"}; summary["semantic_digest"]=dg(summary); (out/"node7-integration-node8-preflight-summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("JANUS_C049_1_B4_6_3_NODE7_UP_K_INTEGRATION = PASS"); print("PROCESSED_INTERNAL_NODE_IDS =",manifest["execution"]["processed_internal_node_ids"]); print("NODE7_UP_K_ENTRIES =",9108); print("NODE8_CHILD_PAIRS_REQUIRED =",pairs); print("NODE8_NAIVE_REFINEMENTS_REQUIRED =",refs); print("STOP_NODE =",stop["node_id"]); print("STOP_REASON =",stop["reason"]); print("ROOT_NODE =",ROOT); print("GLOBAL_TERMINAL =",TERMINAL); return summary

def main():
    a=argparse.ArgumentParser(); a.add_argument("prefix_root",type=Path); a.add_argument("hardening_artifact",type=Path); a.add_argument("frontier_artifact",type=Path); a.add_argument("up_k_artifact",type=Path); a.add_argument("--output-dir",type=Path,required=True); a.add_argument("--node8-pair-cap",type=int,default=10000); a.add_argument("--node8-refinement-cap",type=int,default=2000000); x=a.parse_args(); build(x.prefix_root,x.hardening_artifact,x.frontier_artifact,x.up_k_artifact,x.output_dir,x.node8_pair_cap,x.node8_refinement_cap)
if __name__=="__main__":main()
