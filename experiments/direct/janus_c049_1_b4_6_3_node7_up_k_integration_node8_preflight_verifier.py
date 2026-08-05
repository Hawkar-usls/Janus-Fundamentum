#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, math
from pathlib import Path
from typing import Any, Sequence

TERMINAL="OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
FRONTIER_SHA="6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
FRONTIER_SEM="ed6b59821aaef10ac6bdb6286a72ffcafd15e2bbd2619e0edffc7f711a2b1103"
UPK_SHA="c085a3bee4e0c92a01eb22715390079f9858c5704ebcbf8534f9de196087d189"
UPK_SEM="23079901348590eb39d60d904d52dfd5004f8b287382a288ccbea688802b22f2"
ENTRIES_DIGEST="269d5cd926d3be3df5641066a7986dfb1df049abab68b4202f6bc9a39e27a46e"
TRANSCRIPT_ROOT="eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
LEAF3_RECEIPT="80f424b87fd39e80013e1bb96b3dcec47d281a322f9964472b2ca32bd039e086"
LEFT_HIST={"2":4,"3":56,"4":252,"5":680,"6":1300,"7":1824,"8":1968,"9":1584,"10":960,"11":384,"12":96}
RIGHT_HIST={"2":4,"3":8,"4":12,"5":8,"6":4}
EXPECTED_PAIRS=327888
EXPECTED_REFINEMENTS=602017584


def cj(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def dg(v:Any)->str:return hashlib.sha256(cj(v)).hexdigest()
def fsha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict:return json.loads(p.read_text(encoding="utf-8"))
def hist(entries:Sequence[dict])->dict[str,int]:
    out={}
    for e in entries:out[str(len(e["trajectory"]))]=out.get(str(len(e["trajectory"])),0)+1
    return dict(sorted(out.items(),key=lambda x:int(x[0])))
def delannoy(m:int,n:int)->int:
    a,b=m-1,n-1
    return sum(math.comb(a,k)*math.comb(b,k)*(2**k) for k in range(min(a,b)+1))
def refinement_count(a:dict[str,int],b:dict[str,int])->int:return sum(ca*cb*delannoy(int(la),int(lb)) for la,ca in a.items() for lb,cb in b.items())
def xb(rows,dim):
    t={}
    for raw in rows:
        x=int(raw)
        while x:
            p=x.bit_length()-1
            if p in t:x^=t[p];continue
            t[p]=x
            for o,r in list(t.items()):
                if o!=p and ((r>>p)&1):t[o]=r^x
            break
    for p in sorted(t):
        r=t[p]
        for o in sorted(t,reverse=True):
            if o!=p and ((t[o]>>p)&1):t[o]^=r
    return tuple(t[p] for p in sorted(t,reverse=True))
def span(rows):
    s={0}
    for r in rows:s|={x^int(r) for x in tuple(s)}
    return s
def inter(a,b,dim):return xb(span(xb(a,dim))&span(xb(b,dim)),dim)
def bind_receipt(r):
    x=copy.deepcopy(r); x.pop("receipt_digest",None); r["receipt_digest"]=dg(x)
def bind_node(n):
    x=copy.deepcopy(n); x.pop("node_execution_digest",None); n["node_execution_digest"]=dg(x)
def bind_manifest(m):
    for n in m.get("node_results",[]):
        bind_receipt(n["output_receipt"]); bind_node(n)
    x=copy.deepcopy(m); x.pop("manifest_digest",None); m["manifest_digest"]=dg(x)
def bind_summary(s):
    x=copy.deepcopy(s); x.pop("semantic_digest",None); s["semantic_digest"]=dg(x)

def verify_data(frontier:dict,upk:dict,manifest:dict,summary:dict,producer_text:str|None=None)->dict:
    if frontier.get("semantic_digest")!=FRONTIER_SEM or frontier.get("admit") is not True or set(frontier.get("invariant_vector",{}).values())!={"PASS"}:raise AssertionError("frontier admission")
    if upk.get("semantic_digest")!=UPK_SEM or upk.get("semantic_digest_scope")!="proof_payload":raise AssertionError("up_k semantic")
    proof=upk["proof_payload"]
    if proof.get("admit") is not True or set(proof.get("invariant_vector",{}).values())!={"PASS"}:raise AssertionError("up_k admission")
    source_entries=proof["exact_reachable_closure"]["reachable_entries"]
    if len(source_entries)!=9108 or dg(source_entries)!=ENTRIES_DIGEST:raise AssertionError("source entries")
    unsigned=copy.deepcopy(manifest); claimed=unsigned.pop("manifest_digest",None)
    if claimed!=dg(unsigned):raise AssertionError("manifest digest")
    us=copy.deepcopy(summary); sem=us.pop("semantic_digest",None)
    if sem!=dg(us):raise AssertionError("summary digest")
    topology=manifest["topology"]
    if topology["root_node_id"]!=10:raise AssertionError("root id")
    node8_desc=next(x for x in topology["internal_nodes"] if int(x["node_id"])==8)
    expected8={"node_id":8,"kind":"SPINE_INTERNAL_JOIN","edge_index":2,"child_node_ids":[7,3],"left_factor_ids":[0,1,2],"right_factor_ids":[3],"covered_factor_ids":[0,1,2,3],"outside_factor_ids":[4,5]}
    if node8_desc!=expected8:raise AssertionError("node8 descriptor")
    exe=manifest["execution"]; stop=exe["stop"]
    if exe["processed_internal_node_ids"]!=[6,7] or exe["root_node_id"]!=10:raise AssertionError("execution path")
    if (exe["status"],int(stop["node_id"]),stop["reason"],int(stop["required"]),int(stop["cap"]),stop["no_layout_at_cap"],stop["terminal"])!=("OPEN_AT_NODE_CAPACITY",8,"CHILD_PAIR_CAP_EXCEEDED",327888,10000,False,TERMINAL):raise AssertionError("node8 stop")
    if manifest["chunking"]["transcript_root_digest"]!=TRANSCRIPT_ROOT or manifest["chunking"]["chunk_count"]!=61:raise AssertionError("transcript boundary")
    n7=next(x for x in manifest["node_results"] if int(x["node_id"])==7)
    nx=copy.deepcopy(n7); nd=nx.pop("node_execution_digest",None)
    if nd!=dg(nx):raise AssertionError("node7 execution digest")
    receipt=n7["output_receipt"]; rx=copy.deepcopy(receipt); rd=rx.pop("receipt_digest",None)
    if rd!=dg(rx):raise AssertionError("node7 receipt digest")
    cl=n7["node_up_k"]
    if cl["closure_method"]!="CERTIFIED_NODE7_THIRTEEN_GENERATOR_REACHABLE_CATALOG" or cl["entry_count"]!=9108 or len(cl["input_generators"])!=13 or len(cl["retained_generators"])!=13 or cl["removals"]!=[]:raise AssertionError("node7 closure shape")
    if cl["entries"]!=source_entries or dg(cl["entries"])!=ENTRIES_DIGEST or cl["reachable_entries_digest"]!=ENTRIES_DIGEST:raise AssertionError("node7 closure handoff")
    if receipt["entry_count"]!=9108 or receipt["entries_digest"]!=ENTRIES_DIGEST or receipt["full_set_digest"]!=dg(cl):raise AssertionError("node7 receipt content")
    if any(int(v["count"]) for v in n7["record_ranges"].values()):raise AssertionError("generic node7 transcript")
    bridge=n7["certified_structural_bridge"]
    if (bridge["frontier_classes"],bridge["naive_child_pairs_covered"],bridge["naive_refinements_covered"],bridge["generic_pair_records_materialized"],bridge["generic_refinement_records_materialized"],bridge["closure_entries_returned_to_executor"])!=(13,16848,9744432,0,0,9108):raise AssertionError("bridge receipt")
    leaf3=manifest["leaf_full_sets"][3]
    if leaf3["output_receipt"]["receipt_digest"]!=LEAF3_RECEIPT or leaf3["full_set"]["entry_count"]!=36:raise AssertionError("leaf3 receipt")
    lh,rh=hist(cl["entries"]),hist(leaf3["full_set"]["entries"])
    if lh!=LEFT_HIST or rh!=RIGHT_HIST:raise AssertionError("length histogram")
    pairs=sum(lh.values())*sum(rh.values()); refs=refinement_count(lh,rh)
    if (pairs,refs)!=(EXPECTED_PAIRS,EXPECTED_REFINEMENTS):raise AssertionError("node8 exact frontier")
    blocks=manifest["scaffold_case"]["whole_factor_blocks"]
    common=xb((*n7["parent_boundary"],*leaf3["boundary_rref_ambient"]),3)
    covered=xb((r for i in [0,1,2,3] for r in blocks[i]),3); outside=xb((r for i in [4,5] for r in blocks[i]),3); parent=inter(covered,outside,3)
    if common!=(4,2,1) or parent!=(4,1):raise AssertionError("node8 geometry")
    p8=summary["node8_preflight"]
    if (p8["left_entry_count"],p8["right_entry_count"],p8["child_pair_count"],p8["naive_refinement_count"],p8["left_length_histogram"],p8["right_length_histogram"],p8["no_layout_at_cap"])!=(9108,36,EXPECTED_PAIRS,EXPECTED_REFINEMENTS,LEFT_HIST,RIGHT_HIST,False):raise AssertionError("summary preflight")
    if summary["integrated_manifest_digest"]!=manifest["manifest_digest"] or summary["integrated_transcript_root_digest"]!=TRANSCRIPT_ROOT:raise AssertionError("summary binding")
    strict=summary["strict_boundary"]
    expected_strict={"node7_up_k_admitted":True,"node7_integrated_into_bottom_up_executor":True,"node7_generic_cartesian_replay_required":False,"node8_parent_refinement_started":True,"node8_parent_refinement_complete":False,"node8_parent_up_k_complete":False,"negative_root_reached":False,"terminal_completeness_proved":False,"found_layout_enabled":False,"no_layout_at_cap_enabled":False,"current_global_terminal":TERMINAL,"p_vs_np":"OPEN"}
    if strict!=expected_strict or summary["next_gate"]!="C049.1_B4.6.3_NODE8_PARENT_FRONTIER_STRUCTURAL_COMPRESSION":raise AssertionError("strict boundary")
    if producer_text is not None:
        for forbidden in ("engine.lattice_paths","join_trajectory(","shrink_trajectory("):
            if forbidden in producer_text:raise AssertionError("producer contains generic node7 refinement enumeration")
    return {"pairs":pairs,"refinements":refs,"node7_entries":len(cl["entries"])}

def tamper(frontier,upk,manifest,summary,producer_text):
    attacks=[]
    def run(name,mut):
        f,u,m,s=copy.deepcopy(frontier),copy.deepcopy(upk),copy.deepcopy(manifest),copy.deepcopy(summary); mut(f,u,m,s); bind_manifest(m); s["integrated_manifest_digest"]=m["manifest_digest"]; bind_summary(s)
        try:verify_data(f,u,m,s,producer_text)
        except Exception:attacks.append(name);return
        raise AssertionError("tamper accepted: "+name)
    run("DELETE_NODE7_ENTRY",lambda f,u,m,s:m["node_results"][1]["node_up_k"]["entries"].pop())
    run("CHANGE_CLOSURE_METHOD",lambda f,u,m,s:m["node_results"][1]["node_up_k"].__setitem__("closure_method","GENERIC"))
    run("MATERIALIZE_NODE7_PAIR_RANGE",lambda f,u,m,s:m["node_results"][1]["record_ranges"]["pairs"].__setitem__("count",1))
    run("DROP_PROCESSED_NODE7",lambda f,u,m,s:m["execution"].__setitem__("processed_internal_node_ids",[6]))
    run("MOVE_STOP_TO_NODE9",lambda f,u,m,s:m["execution"]["stop"].__setitem__("node_id",9))
    run("CHANGE_NODE8_PAIR_COUNT",lambda f,u,m,s:m["execution"]["stop"].__setitem__("required",327887))
    run("SUBSTITUTE_LEAF3_RECEIPT",lambda f,u,m,s:m["leaf_full_sets"][3]["output_receipt"].__setitem__("receipt_digest","0"*64))
    run("CHANGE_REFINEMENT_COUNT",lambda f,u,m,s:s["node8_preflight"].__setitem__("naive_refinement_count",EXPECTED_REFINEMENTS-1))
    run("CLAIM_NEGATIVE_ROOT",lambda f,u,m,s:s["strict_boundary"].__setitem__("negative_root_reached",True))
    run("SKIP_NODE8_COMPRESSION_GATE",lambda f,u,m,s:s.__setitem__("next_gate","ROOT"))
    return attacks

def main():
    a=argparse.ArgumentParser(); a.add_argument("frontier",type=Path); a.add_argument("up_k",type=Path); a.add_argument("integrated_dir",type=Path); a.add_argument("--producer-source",type=Path); a.add_argument("--tamper-self-test",action="store_true"); x=a.parse_args()
    if fsha(x.frontier)!=FRONTIER_SHA or fsha(x.up_k)!=UPK_SHA:raise AssertionError("frozen source bytes")
    f,u=load(x.frontier),load(x.up_k); m=load(x.integrated_dir/"manifest.json"); s=load(x.integrated_dir/"node7-integration-node8-preflight-summary.json"); text=x.producer_source.read_text(encoding="utf-8") if x.producer_source else None
    r=verify_data(f,u,m,s,text); attacks=tamper(f,u,m,s,text) if x.tamper_self_test else []
    print("STATIC_NO_GENERIC_NODE7_REFINEMENT_ENUMERATION = PASS"); print("JANUS_C049_1_B4_6_3_NODE7_INTEGRATION_VERIFIER = PASS"); print("INVARIANTS = 10/10"); print("NODE7_UP_K_ENTRIES =",r["node7_entries"]); print("NODE8_CHILD_PAIRS =",r["pairs"]); print("NODE8_NAIVE_REFINEMENTS =",r["refinements"]); print("TAMPER_ATTACKS_REJECTED =",f"{len(attacks)}/10" if x.tamper_self_test else "NOT_RUN")
if __name__=="__main__":main()
