#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import random
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA="C049.1-B4.6.3-CORRECTED-NODE7-INTEGRATION-NODE8-PARENT-REFINEMENT-v1"
HEAD="024afebb322c67953f310af48818d3386fdcfc27"
SOURCE_SHA="924e55a651518ce004964f5d7c5ea30e67424ca34507f18eb568341fc96528e0"
SOURCE_SEM="cfd99ea716076414847749fb98185cea63c2cf44e9ceaa659bf37eb9e8fc366a"
CLOSURE_ROOT="99a702ea7005e4a41d99fc4454040314ab106632672b267bffb5f59e29afa728"
RUNS=((0,),(0,1),(0,1,0),(1,),(1,0),(1,0,1))
LEFT=(4,2); RIGHT=(3,); COMMON=(4,2,1); PARENT=(4,1); D=3
TERMINAL="OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

def cjson(value: Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":")).encode("utf-8")

def sha(value: Any)->str:
    return hashlib.sha256(cjson(value)).hexdigest()

def fsha(path: Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reduce_space(rows: Iterable[int], dim: int)->tuple[int,...]:
    rows=[int(v) for v in rows if int(v)]
    if any(v<0 or v >= (1<<dim) for v in rows):
        raise AssertionError("CN8-INV-01")
    rows=sorted(set(rows),reverse=True)
    pivot=0
    for bit in range(dim-1,-1,-1):
        chosen=None
        for index in range(pivot,len(rows)):
            if (rows[index]>>bit)&1:
                chosen=index
                break
        if chosen is None:
            continue
        rows[pivot],rows[chosen]=rows[chosen],rows[pivot]
        row=rows[pivot]
        for index in range(len(rows)):
            if index != pivot and ((rows[index]>>bit)&1):
                rows[index] ^= row
        pivot += 1
    rows=[v for v in rows if v]
    rows.sort(key=lambda v:v.bit_length(),reverse=True)
    return tuple(rows)

def vectors(space: Sequence[int])->set[int]:
    out={0}
    for row in space:
        out.update({value^int(row) for value in tuple(out)})
    return out

def plus(a: Sequence[int],b: Sequence[int],dim: int)->tuple[int,...]:
    return reduce_space((*a,*b),dim)

def meet(a: Sequence[int],b: Sequence[int],dim: int)->tuple[int,...]:
    return reduce_space(vectors(a)&vectors(b),dim)

def lift(space: Sequence[int],basis: Sequence[int],dim: int)->tuple[int,...]:
    out=[]
    for mask in space:
        value=0
        for index,row in enumerate(basis):
            if (int(mask)>>index)&1:
                value ^= int(row)
        out.append(value)
    return reduce_space(out,dim)

def encode(traj: Sequence[tuple])->list[dict[str,Any]]:
    return [{"left":list(x[0]),"right":list(x[1]),"value":int(x[2])} for x in traj]

def compact(seq: Sequence[tuple])->tuple[tuple,...]:
    seq=list(seq)
    while True:
        modified=False
        i=1
        while i<len(seq):
            if seq[i-1]==seq[i]:
                del seq[i]; modified=True; break
            i+=1
        if modified:
            continue
        for i in range(len(seq)):
            for j in range(i+2,len(seq)):
                if seq[i][0:2] != seq[j][0:2]:
                    continue
                vals=[int(x[2]) for x in seq[i:j+1]]
                monotone=(vals[0]<=vals[-1] and all(vals[0]<=z<=vals[-1] for z in vals[1:-1])) or (vals[0]>=vals[-1] and all(vals[0]>=z>=vals[-1] for z in vals[1:-1]))
                if monotone:
                    del seq[i+1:j]
                    modified=True
                    break
            if modified:
                break
        if not modified:
            return tuple(seq)

def expand(skeleton: Sequence[tuple], assignments: Sequence[tuple[int,...]])->tuple[tuple,...]:
    raw=[]
    for geometry,run in zip(skeleton,assignments):
        raw.extend((tuple(geometry[0]),tuple(geometry[1]),int(value)) for value in run)
    return compact(raw)

def source_check(path: Path)->dict[str,Any]:
    if fsha(path)!=SOURCE_SHA:
        raise AssertionError("CN8-INV-01")
    obj=json.loads(path.read_text(encoding="utf-8"))
    if obj.get("semantic_digest")!=SOURCE_SEM or obj.get("reachable_closure",{}).get("entries_digest")!=CLOSURE_ROOT:
        raise AssertionError("CN8-INV-01")
    idem=obj.get("true_up_k_idempotence",{})
    if (
        idem.get("second_input_generator_count")!=7776
        or idem.get("second_output_entry_count")!=7776
        or idem.get("byte_identical_to_first") is not True
        or idem.get("original_six_reused_in_second_pass") is not False
        or idem.get("source_generator_ids_consumed_in_second_pass") is not False
    ):
        raise AssertionError("CN8-INV-01")
    return obj

def closure(obj: dict[str,Any])->list[tuple[tuple,...]]:
    catalog={}
    for generator in sorted(obj["input_generators"],key=cjson):
        zero=tuple((reduce_space(item["left"],2),reduce_space(item["right"],2),int(item["value"])) for item in generator["trajectory"])
        if len(zero)!=4 or any(item[2] for item in zero):
            raise AssertionError("CN8-INV-02")
        skeleton=tuple((item[0],item[1]) for item in zero)
        for assignment in itertools.product(RUNS,repeat=4):
            result=expand(skeleton,assignment)
            catalog[cjson(encode(result))]=result
    entries=[catalog[key] for key in sorted(catalog)]
    if len(entries)!=7776 or sha([encode(item) for item in entries])!=CLOSURE_ROOT:
        raise AssertionError("CN8-INV-02")
    return entries

def leaf()->list[tuple[tuple,...]]:
    skeleton=(((),(1,)),((1,),()))
    catalog={}
    for assignment in itertools.product(RUNS,repeat=2):
        item=expand(skeleton,assignment)
        catalog[cjson(encode(item))]=item
    return [catalog[key] for key in sorted(catalog)]

def paths_hv(m: int,n: int)->list[tuple[tuple[int,int],...]]:
    out=[]
    def visit(i: int,j: int,path: list[tuple[int,int]])->None:
        if i==m-1 and j==n-1:
            out.append(tuple(path)); return
        if i<m-1:
            path.append((i+1,j)); visit(i+1,j,path); path.pop()
        if j<n-1:
            path.append((i,j+1)); visit(i,j+1,path); path.pop()
    visit(0,0,[(0,0)])
    return sorted(out)

def witness(lower: Sequence[tuple],upper: Sequence[tuple])->bool:
    reachable=set()
    for i,a in enumerate(lower):
        for j,b in enumerate(upper):
            if a[:2]!=b[:2] or int(a[2])>int(b[2]):
                continue
            if (i,j)==(0,0) or (i-1,j) in reachable or (i,j-1) in reachable or (i-1,j-1) in reachable:
                reachable.add((i,j))
    return (len(lower)-1,len(upper)-1) in reachable

def histogram(entries: Sequence[Sequence[tuple]])->dict[str,int]:
    values=Counter(len(item) for item in entries)
    return {str(k):values[k] for k in sorted(values)}

def refinement_count(lh: dict[str,int],rh: dict[str,int])->int:
    total=0
    for m,mc in lh.items():
        for n,nc in rh.items():
            total += int(mc)*int(nc)*math.comb(int(m)+int(n)-2,int(m)-1)
    return total

def bridge(entries: Sequence[Sequence[tuple]])->dict[str,Any]:
    payload={
        "node_id":7,
        "kind":"CERTIFIED_CORRECTED_NODE7_UP_K_HANDOFF",
        "child_node_ids":[6,2],
        "covered_factor_ids":[0,1,2],
        "outside_factor_ids":[3,4,5],
        "parent_boundary":[4,2],
        "entry_count":len(entries),
        "entries_digest":sha([encode(item) for item in entries]),
        "source_certificate_sha256":SOURCE_SHA,
        "source_semantic_digest":SOURCE_SEM,
        "grouped_partition_preserved":True,
        "generic_pair_records_materialized":0,
        "generic_refinement_records_materialized":0,
    }
    payload["receipt_digest"]=sha(payload)
    return payload

def recompute_frontier(source: dict[str,Any],left_entries: Sequence[Sequence[tuple]],right_entries: Sequence[Sequence[tuple]])->dict[str,Any]:
    lh=histogram(left_entries); rh=histogram(right_entries)
    pairs=len(left_entries)*len(right_entries)
    refinements=refinement_count(lh,rh)
    if (pairs,refinements)!=(279936,70875648):
        raise AssertionError("CN8-INV-05")
    right_zero=(
        (lift((),RIGHT,D),lift((1,),RIGHT,D),0),
        (lift((1,),RIGHT,D),lift((),RIGHT,D),0),
    )
    unique={}
    correction=Counter()
    cells=0
    assignments=0
    for generator in sorted(source["input_generators"],key=cjson):
        gid=str(generator["generator_id"])
        left_zero=tuple((lift(item["left"],LEFT,D),lift(item["right"],LEFT,D),int(item["value"])) for item in generator["trajectory"])
        initial=meet(left_zero[0][1],right_zero[0][1],D)
        if initial:
            raise AssertionError("CN8-INV-04")
        for pindex,path in enumerate(paths_hv(4,2)):
            pre=[]
            shrink=[]
            for i,j in path:
                a,b=left_zero[i],right_zero[j]
                jl=plus(a[0],b[0],D); jr=plus(a[1],b[1],D)
                current=meet(plus(a[0],a[1],D),plus(b[0],b[1],D),D)
                if len(initial)-len(current)!=0:
                    raise AssertionError("CN8-INV-06")
                lr=meet(jl,jr,D)
                pl=meet(jl,PARENT,D); pr=meet(jr,PARENT,D)
                triple=meet(lr,PARENT,D)
                sc=len(lr)-len(triple)
                if sc not in (0,1):
                    raise AssertionError("CN8-INV-06")
                pre.append((pl,pr,sc)); shrink.append(sc); correction[sc]+=1; cells+=1
            lower=compact(pre)
            choices=[RUNS if value==0 else ((1,),) for value in shrink]
            local=0
            for choice in itertools.product(*choices):
                raw=[]
                for stat,run in zip(pre,choice):
                    raw.extend((stat[0],stat[1],int(value)) for value in run)
                if not witness(lower,compact(raw)):
                    raise AssertionError("CN8-INV-09")
                local += 1
            assignments += local
            encoded=encode(lower)
            key=cjson(encoded)
            src={
                "source_generator_id":gid,
                "local_path_index":pindex,
                "ordinary_hv_path":[[i,j] for i,j in path],
                "ordinary_hv_steps":[[b[0]-a[0],b[1]-a[1]] for a,b in zip(path,path[1:])],
                "join_corrections":[0]*len(path),
                "shrink_corrections":shrink,
                "projected_precompact":encode(pre),
                "local_direct_assignment_tests":local,
            }
            unique.setdefault(key,{"generator":encoded,"sources":[],"assignment_tests":0})
            unique[key]["sources"].append(src)
            unique[key]["assignment_tests"] += local
    if len(unique)!=20 or sum(len(item["sources"]) for item in unique.values())!=24 or assignments!=17424:
        raise AssertionError("CN8-INV-08")
    classes=[]; mapping=[]
    for index,key in enumerate(sorted(unique)):
        class_id=f"CN8-S{index:02d}"
        item=unique[key]; sources=sorted(item["sources"],key=cjson); generator=item["generator"]
        classes.append({
            "class_id":class_id,
            "canonical_generator":generator,
            "generator_digest":sha(generator),
            "length":len(generator),
            "width":max(int(stat["value"]) for stat in generator),
            "source_path_multiplicity":len(sources),
            "canonical_reachability_witness":sources[0],
            "source_path_digest":sha(sources),
            "local_direct_assignment_tests":item["assignment_tests"],
            "direct_witness_kind":"EXTENSION_PREORDER_DIRECT",
            "transitive_closure_used":False,
        })
        for src in sources:
            mapping.append({
                "source_generator_id":src["source_generator_id"],
                "local_path_index":src["local_path_index"],
                "class_id":class_id,
                "ordinary_hv_path":src["ordinary_hv_path"],
                "shrink_corrections":src["shrink_corrections"],
            })
    mapping.sort(key=cjson)
    lengths=Counter(x["length"] for x in classes)
    widths=Counter(x["width"] for x in classes)
    mult=Counter(x["source_path_multiplicity"] for x in classes)
    return {
        "descriptor":{"node_id":8,"kind":"SPINE_INTERNAL_JOIN","child_node_ids":[7,3],"left_factor_ids":[0,1,2],"right_factor_ids":[3],"covered_factor_ids":[0,1,2,3],"outside_factor_ids":[4,5]},
        "geometry":{"ambient_dim":3,"left_boundary":[4,2],"right_boundary":[3],"common_boundary":[4,2,1],"parent_boundary":[4,1],"join_lambda_correction_identically_zero":True,"shrink_is_identity":False,"shrink_correction_counts_over_quotient_cells":{str(k):correction[k] for k in sorted(correction)}},
        "exact_child_product":{"left_entry_count":len(left_entries),"right_entry_count":len(right_entries),"child_pair_count":pairs,"ordinary_hv_refinement_count":refinements,"left_length_histogram":lh,"right_length_histogram":rh,"cartesian_child_pairs_materialized":0,"fine_hv_paths_materialized":0},
        "quotient_frontier":{"ordinary_hv_steps":[[1,0],[0,1]],"ordinary_join_diagonal_allowed":False,"extension_preorder_steps":[[1,0],[0,1],[1,1]],"extension_preorder_diagonal_preserved":True,"pre_shrink_quotient_path_count":24,"post_shrink_class_count":20,"source_path_collision_count":4,"classes":classes,"path_to_class":mapping,"class_catalog_digest":sha(classes),"class_length_histogram":{str(k):lengths[k] for k in sorted(lengths)},"class_width_histogram":{str(k):widths[k] for k in sorted(widths)},"source_path_multiplicity_histogram":{str(k):mult[k] for k in sorted(mult)},"all_generators_reachable":True,"all_generators_width_at_most_k":True,"universal_direct_coverage":True,"local_direct_assignment_tests":assignments,"transitive_closure_used":False},
        "work_ledger":{"left_entries_reconstructed":len(left_entries),"right_entries_reconstructed":len(right_entries),"child_pairs_covered":pairs,"ordinary_hv_refinements_covered":refinements,"cartesian_child_pairs_materialized":0,"fine_hv_paths_materialized":0,"quotient_paths_enumerated":24,"quotient_cells_checked":cells,"post_shrink_classes":20,"local_direct_witness_assignments_tested":assignments},
    }

def expected(source: dict[str,Any])->dict[str,Any]:
    left=closure(source); right=leaf()
    right_encoded=[encode(item) for item in right]
    front=recompute_frontier(source,left,right)
    obj={
        "schema":SCHEMA,
        "source":{"parent_pr":113,"parent_exact_head":HEAD,"certificate_sha256":SOURCE_SHA,"certificate_semantic_digest":SOURCE_SEM,"node7_closure_digest":CLOSURE_ROOT},
        "corrected_path_domain":{"ordinary_join_steps":[[1,0],[0,1]],"ordinary_join_diagonal_allowed":False,"extension_preorder_steps":[[1,0],[0,1],[1,1]],"extension_preorder_diagonal_preserved":True,"legacy_delannoy_node8_frontier_consumed":False},
        "node7_integration":{"bridge":bridge(left),"node7_integrated_into_bottom_up_executor":True,"generic_node7_cartesian_replay_required":False,"certified_closure_entry_count":len(left),"certified_closure_entries_digest":sha([encode(item) for item in left]),"processed_internal_node_ids":[6,7]},
        "leaf3":{"entry_count":len(right),"entries_digest":sha(right_encoded),"zero_generator":[{"left":[],"right":[1],"value":0},{"left":[1],"right":[],"value":0}]},
        "node8_parent_refinement":front,
        "invariant_vector":{f"CN8-INV-{i:02d}":"PASS" for i in range(1,13)},
        "result":"CORRECTED_NODE7_INTEGRATED_AND_NODE8_PARENT_FRONTIER_COMPRESSED_TO_20_HV_CLASSES",
        "strict_boundary":{"pr113_node7_six_generator_up_k_admitted":True,"corrected_node7_integrated_into_bottom_up_executor":True,"corrected_node8_parent_generator_frontier_complete":True,"corrected_node8_parent_refinement_complete":True,"corrected_node8_parent_up_k_complete":False,"corrected_bottom_up_replay_complete":False,"root_parent_refinement_complete":False,"root_full_set_computed":False,"root_empty_proved":False,"found_layout":"FORBIDDEN","no_layout_at_cap":"FORBIDDEN","current_global_terminal":TERMINAL,"p_vs_np":"OPEN"},
        "next_gate":"C049.1_B4.6.3_CORRECTED_NODE8_TWENTY_GENERATOR_UP_K_HARDENING",
        "certificate_bytes":0,
    }
    while True:
        unsigned=dict(obj); unsigned.pop("semantic_digest",None)
        obj["semantic_digest"]=sha(unsigned)
        raw=cjson(obj)+b"\n"
        if obj["certificate_bytes"]==len(raw):
            return obj
        obj["certificate_bytes"]=len(raw)

def verify(source_path: Path,artifact_path: Path)->dict[str,Any]:
    source=source_check(source_path)
    observed=json.loads(artifact_path.read_text(encoding="utf-8"))
    if observed.get("schema")!=SCHEMA:
        raise AssertionError("CN8-INV-01")
    unsigned=dict(observed); claimed=unsigned.pop("semantic_digest",None)
    if claimed!=sha(unsigned) or observed.get("certificate_bytes")!=len(artifact_path.read_bytes()):
        raise AssertionError("CN8-INV-12")
    for item in observed.get("node8_parent_refinement",{}).get("quotient_frontier",{}).get("classes",[]):
        if item.get("direct_witness_kind")!="EXTENSION_PREORDER_DIRECT" or item.get("transitive_closure_used") is not False:
            raise AssertionError("DIRECT_WITNESS_MISSING")
    exp=expected(source)
    if observed.get("source")!=exp["source"]:
        raise AssertionError("CN8-INV-01")
    if observed.get("corrected_path_domain")!=exp["corrected_path_domain"]:
        raise AssertionError("CN8-INV-03")
    if observed.get("node7_integration")!=exp["node7_integration"]:
        raise AssertionError("CN8-INV-04")
    if observed.get("leaf3")!=exp["leaf3"]:
        raise AssertionError("CN8-INV-05")
    if observed.get("node8_parent_refinement",{}).get("descriptor")!=exp["node8_parent_refinement"]["descriptor"]:
        raise AssertionError("CN8-INV-06")
    if observed.get("node8_parent_refinement",{}).get("geometry")!=exp["node8_parent_refinement"]["geometry"]:
        raise AssertionError("CN8-INV-07")
    if observed.get("node8_parent_refinement",{}).get("exact_child_product")!=exp["node8_parent_refinement"]["exact_child_product"]:
        raise AssertionError("CN8-INV-08")
    if observed.get("node8_parent_refinement",{}).get("quotient_frontier")!=exp["node8_parent_refinement"]["quotient_frontier"]:
        raise AssertionError("CN8-INV-09")
    if observed.get("node8_parent_refinement",{}).get("work_ledger")!=exp["node8_parent_refinement"]["work_ledger"]:
        raise AssertionError("CN8-INV-10")
    if observed.get("invariant_vector")!=exp["invariant_vector"] or observed.get("result")!=exp["result"]:
        raise AssertionError("CN8-INV-11")
    if observed.get("strict_boundary")!=exp["strict_boundary"] or observed.get("next_gate")!=exp["next_gate"]:
        raise AssertionError("CN8-INV-12")
    if observed!=exp:
        raise AssertionError("CN8-INV-12")
    return observed

def reseal(value: dict[str,Any])->dict[str,Any]:
    item=copy.deepcopy(value); item["certificate_bytes"]=0
    while True:
        unsigned=dict(item); unsigned.pop("semantic_digest",None)
        item["semantic_digest"]=sha(unsigned)
        size=len(cjson(item)+b"\n")
        if item["certificate_bytes"]==size:
            return item
        item["certificate_bytes"]=size

def tamper(source_path: Path,artifact_path: Path)->dict[str,str]:
    original=json.loads(artifact_path.read_text(encoding="utf-8"))
    def closure_only(x):
        cls=x["node8_parent_refinement"]["quotient_frontier"]["classes"][0]
        cls["direct_witness_kind"]="TRANSITIVE_CHAIN_ONLY"
        cls["transitive_closure_used"]=True
    attacks=[
        ("source_head","CN8-INV-01",lambda x:x["source"].__setitem__("parent_exact_head","0"*40)),
        ("source_sha","CN8-INV-01",lambda x:x["source"].__setitem__("certificate_sha256","0"*64)),
        ("diagonal_join","CN8-INV-03",lambda x:x["corrected_path_domain"].__setitem__("ordinary_join_diagonal_allowed",True)),
        ("node7_count","CN8-INV-04",lambda x:x["node7_integration"].__setitem__("certified_closure_entry_count",7775)),
        ("leaf_digest","CN8-INV-05",lambda x:x["leaf3"].__setitem__("entries_digest","0"*64)),
        ("parent_boundary","CN8-INV-07",lambda x:x["node8_parent_refinement"]["geometry"].__setitem__("parent_boundary",[4,2])),
        ("child_pairs","CN8-INV-08",lambda x:x["node8_parent_refinement"]["exact_child_product"].__setitem__("child_pair_count",279935)),
        ("class_delete","CN8-INV-09",lambda x:x["node8_parent_refinement"]["quotient_frontier"]["classes"].pop()),
        ("closure_only_witness","DIRECT_WITNESS_MISSING",closure_only),
        ("work_ledger","CN8-INV-10",lambda x:x["node8_parent_refinement"]["work_ledger"].__setitem__("quotient_paths_enumerated",23)),
        ("result","CN8-INV-11",lambda x:x.__setitem__("result","FALSE_RESULT")),
        ("false_terminal","CN8-INV-12",lambda x:x["strict_boundary"].__setitem__("no_layout_at_cap",True)),
    ]
    outcomes={}
    with tempfile.TemporaryDirectory() as td:
        for name,expected_error,mutation in attacks:
            candidate=copy.deepcopy(original); mutation(candidate); candidate=reseal(candidate)
            path=Path(td)/f"{name}.json"; path.write_bytes(cjson(candidate)+b"\n")
            try:
                verify(source_path,path)
            except AssertionError as exc:
                if expected_error not in str(exc):
                    raise AssertionError(f"{name}: expected {expected_error}, got {exc}")
                outcomes[name]=expected_error
            else:
                raise AssertionError(f"tamper accepted: {name}")
    return outcomes

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    parser.add_argument("artifact",type=Path)
    parser.add_argument("--tamper-self-test",action="store_true")
    args=parser.parse_args()
    artifact=verify(args.source,args.artifact)
    outcomes=tamper(args.source,args.artifact) if args.tamper_self_test else {}
    print(json.dumps({
        "status":"PASS",
        "invariants":"12/12",
        "tamper_attacks_rejected":len(outcomes),
        "node8_classes":artifact["node8_parent_refinement"]["quotient_frontier"]["post_shrink_class_count"],
        "semantic_digest":artifact["semantic_digest"],
    },sort_keys=True))

if __name__=="__main__":
    main()
