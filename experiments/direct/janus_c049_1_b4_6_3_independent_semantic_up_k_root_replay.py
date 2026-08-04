#!/usr/bin/env python3
from __future__ import annotations
import argparse, gzip, hashlib, json
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence, Any

SCHEMA="C049.1-B4.6.3-INDEPENDENT-SEMANTIC-UP-K-ROOT-REPLAY-v1"
TERMINAL="OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

def canonical_json(v: Any)->bytes:
    return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def digest(v: Any)->str: return hashlib.sha256(canonical_json(v)).hexdigest()

def rref(rows: Iterable[int], dim:int)->tuple[int,...]:
    limit=1<<dim; table={}
    for raw in rows:
        x=int(raw)
        if x<0 or x>=limit: raise ValueError("vector outside ambient space")
        while x:
            p=x.bit_length()-1
            if p in table: x ^= table[p]
            else:
                table[p]=x
                for q,row in list(table.items()):
                    if q!=p and ((row>>p)&1): table[q]=row^x
                break
    return tuple(table[p] for p in sorted(table,reverse=True))
def contains(big,small):
    for raw in small:
        x=raw
        for row in big: x=min(x,x^row)
        if x:return False
    return True
def parse_stat(raw,dim):
    v=int(raw["value"])
    if v<0: raise ValueError("negative value")
    return rref(raw["left"],dim),rref(raw["right"],dim),v
def compact(sequence):
    seq=list(sequence)
    while True:
        changed=False
        for i in range(1,len(seq)):
            if seq[i-1]==seq[i]: del seq[i]; changed=True; break
        if changed: continue
        for s in range(len(seq)):
            for e in range(s+2,len(seq)):
                if seq[s][:2]!=seq[e][:2]: continue
                vals=[x[2] for x in seq[s:e+1]]
                inc=vals[0]<=vals[-1] and all(vals[0]<=v<=vals[-1] for v in vals[1:-1])
                dec=vals[0]>=vals[-1] and all(vals[0]>=v>=vals[-1] for v in vals[1:-1])
                if inc or dec: del seq[s+1:e]; changed=True; break
            if changed: break
        if not changed:return tuple(seq)
def trajectory(raw:Sequence[dict],dim:int):
    if not raw: raise ValueError("empty trajectory")
    seq=tuple(parse_stat(x,dim) for x in raw)
    if seq[0][1]!=seq[-1][0]: raise ValueError("endpoint mismatch")
    for a,b in zip(seq,seq[1:]):
        if not contains(b[0],a[0]) or not contains(a[1],b[1]): raise ValueError("monotonicity")
    if compact(seq)!=seq: raise ValueError("noncompact")
    return seq
def encode(seq): return [{"left":list(x[0]),"right":list(x[1]),"value":x[2]} for x in seq]
def stat_leq(a,b):return a[0]==b[0] and a[1]==b[1] and a[2]<=b[2]
def canonical_path(lower,upper):
    parent={}
    for i in range(len(lower)):
        for j in range(len(upper)):
            if not stat_leq(lower[i],upper[j]):continue
            if (i,j)==(0,0):parent[(i,j)]=None;continue
            for prev in ((i-1,j-1),(i-1,j),(i,j-1)):
                if prev in parent: parent[(i,j)]=prev;break
    t=(len(lower)-1,len(upper)-1)
    if t not in parent:return None
    out=[];cur=t
    while cur is not None:out.append(cur);cur=parent[cur]
    return list(reversed(out))
def witness(path):return {"path":[list(x) for x in path],"path_length":len(path)}
def subspaces(dim):
    seen={()};q=[()]
    while q:
        cur=q.pop(0)
        for v in range(1,1<<dim):
            cand=rref((*cur,v),dim)
            if cand not in seen:seen.add(cand);q.append(cand)
    return tuple(sorted(seen))
def universe(dim,k):
    spaces=subspaces(dim);states=tuple((l,r,v) for l in spaces for r in spaces for v in range(k+1))
    bound=(2*dim+1)*(2*k+1);emitted={}
    def dfs(seq,target):
        last=seq[-1]
        if last[0]==target:emitted[seq]=seq
        if len(seq)>=bound:return
        for nxt in states:
            if not contains(nxt[0],last[0]) or not contains(last[1],nxt[1]) or not contains(target,nxt[0]):continue
            cand=(*seq,nxt)
            if compact(cand)==cand:dfs(cand,target)
    for first in states:
        if contains(first[1],first[0]):dfs((first,),first[1])
    return tuple(emitted[k] for k in sorted(emitted))
def expected_minimal(gens):
    ordered=tuple(sorted({g:g for g in gens}.values()))
    relation={(i,j):canonical_path(a,b) for i,a in enumerate(ordered) for j,b in enumerate(ordered)}
    relation={p:x for p,x in relation.items() if x is not None};retained_idx=[]
    for j in range(len(ordered)):
        strict=any(i!=j and (i,j) in relation and (j,i) not in relation for i in range(len(ordered)))
        equiv=any(i<j and (i,j) in relation and (j,i) in relation for i in range(len(ordered)))
        if not strict and not equiv:retained_idx.append(j)
    retained=tuple(ordered[i] for i in retained_idx);removals=[]
    for j,removed in enumerate(ordered):
        if j in retained_idx:continue
        candidates=[i for i in retained_idx if (i,j) in relation]
        if not candidates:raise AssertionError("removed generator lacks retained predecessor")
        i=min(candidates,key=lambda z:ordered[z])
        removals.append({"removed":encode(removed),"retained":encode(ordered[i]),"witness":witness(relation[(i,j)]),"reason":"STRICTLY_COVERED" if (j,i) not in relation else "EQUIVALENT_CANONICAL_REPRESENTATIVE"})
    return retained,removals
def expected_closure(raw):
    dim=int(raw["ambient_dim"]);k=int(raw["k"]);gens=tuple(trajectory(x,dim) for x in raw["input_generators"])
    retained,removals=expected_minimal(gens);uni=universe(dim,k);entries=[]
    for cand in uni:
        chosen=None
        for i,src in enumerate(retained):
            p=canonical_path(src,cand)
            if p is not None:chosen=(i,p);break
        if chosen is not None:entries.append({"trajectory":encode(cand),"source_generator_index":chosen[0],"witness":witness(chosen[1])})
    return {"retained_generators":[encode(x) for x in retained],"removals":removals,"universe_size":len(uni),"entries":entries,"entry_count":len(entries)}

def read_records(round_dir:Path, manifest:dict, kind:str):
    for meta in manifest["chunking"]["chunk_groups"][kind]:
        payload=json.loads(gzip.decompress((round_dir/meta["filename"]).read_bytes()))
        if payload["kind"]!=kind or payload["record_count"]!=meta["record_count"]:raise AssertionError("chunk metadata mismatch")
        yield from payload["records"]

def replay_round(round_dir:Path)->dict:
    manifest=json.loads((round_dir/"manifest.json").read_text());all_generators=list(read_records(round_dir,manifest,"GENERATORS"));all_deletions=list(read_records(round_dir,manifest,"DELETIONS"));results=[]
    for node in manifest["node_results"]:
        node_id=int(node["node_id"]);rr=node["record_ranges"];rstart,rend=rr["refinements"]["first"],rr["refinements"]["last"];successful=defaultdict(list)
        for rec in read_records(round_dir,manifest,"REFINEMENTS"):
            aid=int(rec["attempt_id"])
            if aid<rstart:continue
            if aid>rend:break
            if int(rec["node_id"])!=node_id:raise AssertionError("refinement node range drift")
            if rec["status"]=="SUCCESS":successful[canonical_json(rec["output_parent_coordinates"]).decode()].append(aid)
            elif rec["status"]!="FAILED_WIDTH_CAP":raise AssertionError("unknown refinement status")
        gs=[g for g in all_generators if rr["generators"]["first"]<=int(g["generator_id"])<=rr["generators"]["last"]]
        if len(gs)!=rr["generators"]["count"]:raise AssertionError("generator range mismatch")
        expected_keys=sorted(successful);ordered_g=sorted(gs,key=lambda x:int(x["local_generator_index"]));actual_keys=[canonical_json(g["trajectory_parent_coordinates"]).decode() for g in ordered_g]
        if actual_keys!=expected_keys:raise AssertionError("unique successful generator family mismatch")
        for g,key in zip(ordered_g,expected_keys):
            ids=successful[key]
            if g["provenance_attempt_ids"]!=ids or int(g["canonical_retained_attempt_id"])!=ids[0]:raise AssertionError("generator provenance partition mismatch")
            if g["trajectory_digest"]!=digest(g["trajectory_parent_coordinates"]):raise AssertionError("generator trajectory digest mismatch")
        ds=[d for d in all_deletions if rr["deletions"]["first"]<=int(d["deletion_id"])<=rr["deletions"]["last"]]
        expected_dups={(int(g["generator_id"]),aid) for g in gs for aid in g["provenance_attempt_ids"][1:]};actual_dups={(int(d["generator_id"]),int(d["removed_attempt_id"])) for d in ds}
        if actual_dups!=expected_dups:raise AssertionError("duplicate deletion partition mismatch")
        by_gid={int(g["generator_id"]):g for g in gs}
        for d in ds:
            g=by_gid[int(d["generator_id"])]
            if int(d["retained_attempt_id"])!=int(g["canonical_retained_attempt_id"]) or d["trajectory_digest"]!=g["trajectory_digest"]:raise AssertionError("duplicate semantic mismatch")
        ordered=[by_gid[int(p["generator_id"])]["trajectory_parent_coordinates"] for p in node["input_generator_provenance"]]
        if ordered!=node["node_up_k"]["input_generators"]:raise AssertionError("up_k input generator handoff mismatch")
        expected=expected_closure(node["node_up_k"])
        for f in ("retained_generators","removals","universe_size","entries","entry_count"):
            if node["node_up_k"][f]!=expected[f]:raise AssertionError("semantic up_k mismatch: "+f)
        retained_prov=node["retained_generator_provenance"]
        if len(retained_prov)!=len(expected["retained_generators"]):raise AssertionError("retained provenance count mismatch")
        for i,p in enumerate(retained_prov):
            if by_gid[int(p["generator_id"])]["trajectory_parent_coordinates"]!=expected["retained_generators"][i]:raise AssertionError("retained provenance semantic mismatch")
        if node["output_receipt"]["entry_count"]!=expected["entry_count"] or node["output_receipt"]["entries_digest"]!=digest(expected["entries"]):raise AssertionError("output receipt mismatch")
        results.append({"node_id":node_id,"successful_attempts":sum(map(len,successful.values())),"unique_generators":len(gs),"duplicate_deletions":len(ds),"retained_generators":len(expected["retained_generators"]),"universe_size":expected["universe_size"],"entry_count":expected["entry_count"],"entries_digest":digest(expected["entries"]),"semantic_up_k_replay_complete":True})
    root_id=int(manifest["execution"]["root_node_id"]);root=next(x for x in results if x["node_id"]==root_id)
    return {"round":round_dir.name,"root_node_id":root_id,"nodes":results,"root_entry_count":root["entry_count"],"root_entries_digest":root["entries_digest"],"semantic_up_k_replay_complete":True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("cycle_dir");ap.add_argument("--output",required=True);a=ap.parse_args();root=Path(a.cycle_dir)
    rounds=[replay_round(p) for p in sorted(root.glob("round-*"))]
    out={"schema":SCHEMA,"source_cycle_artifact":json.loads((root/"artifact.json").read_text())["manifest_digest"],"rounds":rounds,"all_rounds_semantically_replayed":all(x["semantic_up_k_replay_complete"] for x in rounds),"strict_boundary":{"inventory_completeness":True,"semantic_up_k_replay_complete":True,"terminal_completeness_proved":False,"found_layout_enabled":False,"no_layout_at_cap_enabled":False,"current_global_terminal":TERMINAL,"p_vs_np":"OPEN"}}
    out["semantic_digest"]=digest(out);Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
