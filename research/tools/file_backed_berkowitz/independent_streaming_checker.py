from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from array import array
from collections import Counter, defaultdict
from pathlib import Path

CHUNK_MAX=4096
DOMAIN=b"JANUS_TRUMP_FRESH_BERKOWITZ_MACRO_DAG_V1\x00"
SEMANTIC_BLOB="f7686ec7bb7d3ab30a350aaecbdf1ed33f049277"
SRC_D37="d37be23c8ce8425d1672a8ed118fb10099195de0"
SRC_B906="b9060a05562fcb29b8ecc15d0f03085b4214fe1d"
SRC_449="449d5e3044dd69dd857ae40d8499cd589eb78cac"
C0_VARS=["u","v","a0","a1","b0","b1","c0","c1"]
C1_VARS=["v","u","b1","zvec","x_plus_zvec","x","y_plus_zvec","y"]
ROOT_NAMES=["widehat_S23","widehat_Theta3","widehat_Xi23","widehat_Omega0","widehat_Omega1","widehat_Pi"]
C0_MASKS={
 "Coeff1_u":1,"Coeff1_v":2,"Coeff2_u_a0":5,"Coeff2_v_a0":6,"Coeff2_u_a1":9,"Coeff2_v_a1":10,
 "Coeff2_u_b0":17,"Coeff2_v_b0":18,"Coeff2_u_b1":33,"Coeff2_v_b1":34,"Delta00":19,"Delta01_u":37,
 "Delta01_v":38,"Delta10_u":25,"Delta10_v":26,"Theta3":35,"Omega0":99,"Omega1":163}
C1_MASKS={"Q_zvec":15,"Q_x_plus_zvec":23,"Q_x":39,"Q_y_plus_zvec":71,"Q_y":135}
ROOT_TERMS={
 "widehat_S23":[("Coeff1_u",-96),("Coeff1_v",96),("Coeff2_u_a0",-64),("Coeff2_v_a0",64),("Coeff2_u_a1",-32),("Coeff2_v_a1",32),("Coeff2_u_b0",-48),("Coeff2_v_b0",48),("Coeff2_u_b1",-48),("Coeff2_v_b1",48),("Delta00",-32),("Delta01_u",-32),("Delta01_v",32),("Delta10_u",-16),("Delta10_v",16),("Theta3",16)],
 "widehat_Theta3":[("Theta3",96)],
 "widehat_Xi23":[("Delta00",32),("Delta01_u",32),("Delta01_v",-32),("Delta10_u",16),("Delta10_v",-16)],
 "widehat_Omega0":[("Omega0",96)],"widehat_Omega1":[("Omega1",96)],
 "widehat_Pi":[("Q_zvec",240),("Q_x_plus_zvec",-48),("Q_x",48),("Q_y_plus_zvec",-96),("Q_y",96)]}
REQUIRED_FIELDS=["node_id","opcode","ordered_parent_ids","input_shapes","output_shape","semantic_role","determinant_core_role","stage_d","local_index","exact_index_parameters","exact_integer_constants","coefficient_variable_order","semantic_source_commit","semantic_source_section"]
ALLOWED_OPCODES={"INTEGER_CONSTANT","FINITE_DOMAIN_S4_SELECT","VECTOR_ADD","VECTOR_SUB","MATRIX_VECTOR_PRODUCT","MATRIX_VECTOR_CHAIN","DOT_PRODUCT","LOWER_TRIANGULAR_TOEPLITZ_BUILD","TOEPLITZ_VECTOR_PRODUCT","VECTOR_CONCAT_SLICE","POLYNOMIAL_VECTOR_ADD","POLYNOMIAL_VECTOR_SCALE","EXACT_INDEXED_MUX"}
FORBIDDEN={"DET","CHARPOLY","BERKOWITZ","BERKOWITZ_STAGE","COMPUTE_STATE","Replay_gate"}

def jcs(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def sha(b): return hashlib.sha256(b).hexdigest()
def fail(code,detail=None):
    raise AssertionError(json.dumps({"code":code,"detail":detail},sort_keys=True))
def need(cond,code,detail=None):
    if not cond: fail(code,detail)
def pop(n): return int(n).bit_count()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--cert",required=True)
    ap.add_argument("--report")
    args=ap.parse_args()
    repo=Path(args.repo).resolve(); cert=(repo/args.cert).resolve()
    report={"status":"FAIL","certificate_digest":None,"checks":[]}
    try:
        raw_manifest=(cert/"manifest.json").read_bytes()
        need(raw_manifest.endswith(b"\n"),"MANIFEST_FINAL_LF")
        need(b"\r" not in raw_manifest,"MANIFEST_CR_FORBIDDEN")
        manifest=json.loads(raw_manifest)
        need(jcs(manifest)+b"\n"==raw_manifest,"MANIFEST_NOT_JCS")
        expected_digest=manifest.get("certificate_digest")
        core=dict(manifest); core.pop("certificate_digest",None)
        actual_digest=sha(DOMAIN+jcs(core))
        need(expected_digest==actual_digest,"FAIL_CHECKER_DIGEST_BINDING",[expected_digest,actual_digest])
        report["certificate_digest"]=actual_digest
        report["checks"].append("manifest_digest")
        need(manifest.get("schema")=="FRESH_BERKOWITZ_MACRO_DAG_CHUNKED_V1","MANIFEST_SCHEMA")
        need(manifest.get("source_commits")==[SRC_D37,SRC_B906,SRC_449],"SOURCE_COMMITS")
        need(manifest.get("normalization")=="96*D_base","NORMALIZATION")
        need(manifest.get("zeta_coefficient_order")=="[zeta^0,zeta^1,...,zeta^744]","ZETA_ORDER")
        blob=subprocess.check_output(["git","-C",str(repo),"cat-file","blob",SEMANTIC_BLOB])
        need(sha(blob)==manifest.get("semantic_source_digest"),"SEMANTIC_SOURCE_DIGEST")
        report["checks"].append("semantic_source_digest")

        descs=manifest.get("ordered_chunk_descriptors_and_sha256s",[])
        need(len(descs)==manifest.get("total_chunk_count"),"CHUNK_COUNT")
        need(descs,"NO_CHUNKS")
        parents_flat=array('I'); offsets=array('Q',[0])
        opcode_counts=Counter(); role_to_id={}; stage_nodes=defaultdict(lambda:defaultdict(list)); extract_nodes={}; root_nodes={}
        node_count=0; edge_count=0; stage_core_edges=0; stage_core_nodes=0
        output_shape=[]
        special={}

        for ci,d in enumerate(descs):
            need(d["chunk_index"]==ci,"CHUNK_INDEX",ci)
            need(d["file_name"]==f"chunk_{ci:06d}.jsonl","CHUNK_FILENAME",ci)
            p=cert/"chunks"/d["file_name"]
            need(p.exists(),"MISSING_CHUNK",str(p))
            raw=p.read_bytes()
            need(len(raw)==d["raw_byte_count"],"CHUNK_BYTE_COUNT",ci)
            need(sha(raw)==d["sha256"],"FAIL_CHUNK_DIGEST_MISMATCH",ci)
            need(raw.endswith(b"\n"),"CHUNK_FINAL_LF",ci)
            need(b"\r" not in raw,"CHUNK_CR_FORBIDDEN",ci)
            lines=raw.splitlines(keepends=True)
            need(len(lines)==d["node_count"],"CHUNK_NODE_COUNT",ci)
            if ci<len(descs)-1: need(len(lines)==CHUNK_MAX,"NONFINAL_CHUNK_SIZE",ci)
            else: need(1<=len(lines)<=CHUNK_MAX,"FINAL_CHUNK_SIZE",ci)
            need(d["first_node_id"]==node_count,"CHUNK_FIRST_ID",ci)
            for line in lines:
                need(line.endswith(b"\n"),"LINE_LF")
                payload=line[:-1]
                obj=json.loads(payload)
                need(jcs(obj)==payload,"NODE_NOT_JCS",node_count)
                need(list(sorted(obj.keys()))==list(sorted(REQUIRED_FIELDS)),"NODE_SCHEMA",node_count)
                nid=obj["node_id"]
                need(nid==node_count,"FAIL_NODE_ID_GAP_OR_DUPLICATE",[node_count,nid])
                op=obj["opcode"]
                need(op in ALLOWED_OPCODES and op not in FORBIDDEN,"OPCODE_WHITELIST",[nid,op])
                pars=obj["ordered_parent_ids"]
                need(isinstance(pars,list) and all(isinstance(x,int) and 0<=x<nid for x in pars),"FORWARD_OR_BAD_PARENT",nid)
                parents_flat.extend(pars); offsets.append(len(parents_flat)); edge_count+=len(pars)
                opcode_counts[op]+=1
                role=obj["semantic_role"]
                if role in role_to_id: fail("DUPLICATE_SEMANTIC_ROLE",role)
                role_to_id[role]=nid
                core_role=obj["determinant_core_role"]; sd=obj["stage_d"]
                if op in {"MATRIX_VECTOR_CHAIN","DOT_PRODUCT","LOWER_TRIANGULAR_TOEPLITZ_BUILD","TOEPLITZ_VECTOR_PRODUCT"}:
                    need(core_role in {"SHARED","C0","C1"},"STAGE_CORE_ROLE",nid)
                    need(isinstance(sd,int) and 2<=sd<=744,"STAGE_D",nid)
                    stage_nodes[(core_role,sd)][op].append(nid)
                    stage_core_nodes+=1; stage_core_edges+=len(pars)
                if role.startswith("COEFF"):
                    extract_nodes[role]=nid
                if role in ROOT_NAMES:
                    root_nodes[role]=nid
                # Lightweight semantic and shape checks done streaming.
                if op=="MATRIX_VECTOR_CHAIN":
                    need(len(pars)==2,"CHAIN_PARENT_COUNT",nid)
                    need(obj["output_shape"]==[sd-1,sd-1],"CHAIN_SHAPE",nid)
                    need(obj["exact_index_parameters"].get("power_end_inclusive")==sd-2,"CHAIN_ENDPOINT",nid)
                    need(obj["exact_index_parameters"].get("orientation")=="w_j=M^j*c","CHAIN_ORIENTATION",nid)
                elif op=="DOT_PRODUCT":
                    j=obj["local_index"]
                    need(isinstance(j,int) and 0<=j<=sd-2,"DOT_LOCAL_INDEX",[nid,j,sd])
                    need(len(pars)==2,"DOT_PARENT_COUNT",nid)
                    need(obj["exact_index_parameters"].get("right_chain_index")==j,"DOT_CHAIN_INDEX",nid)
                    need(obj["exact_index_parameters"].get("orientation")=="r*M^j*c","DOT_ORIENTATION",nid)
                    need(obj["output_shape"]==[],"DOT_SHAPE",nid)
                elif op=="LOWER_TRIANGULAR_TOEPLITZ_BUILD":
                    need(len(pars)==sd,"TOEPLITZ_PARENT_COUNT",nid)
                    need(obj["output_shape"]==[sd+1,sd],"TOEPLITZ_SHAPE",nid)
                    law=obj["exact_index_parameters"].get("first_column_law")
                    need(law==["1","-a"]+[f"-s_{j}" for j in range(sd-1)],"TOEPLITZ_SIGNS",nid)
                    need(obj["exact_index_parameters"].get("zero_based_coefficient_index") is True,"TOEPLITZ_OFFSET",nid)
                elif op=="TOEPLITZ_VECTOR_PRODUCT":
                    need(len(pars)==2,"TOEPLITZ_PRODUCT_PARENT_COUNT",nid)
                    need(obj["output_shape"]==[sd+1],"Q_SHAPE",nid)
                node_count+=1
            need(d["last_node_id"]==node_count-1,"CHUNK_LAST_ID",ci)
        report["checks"].append("raw_chunks_and_global_ids")
        need(node_count==manifest.get("total_logical_node_count"),"TOTAL_NODE_COUNT",[node_count,manifest.get("total_logical_node_count")])
        need(edge_count==manifest.get("total_dependency_edge_count"),"TOTAL_EDGE_COUNT",[edge_count,manifest.get("total_dependency_edge_count")])
        need(dict(sorted(opcode_counts.items()))==manifest.get("opcode_counts"),"OPCODE_COUNTS")
        need(stage_core_nodes==365985==manifest.get("mandatory_nonbase_stage_core_nodes"),"STAGE_CORE_NODE_COUNT",stage_core_nodes)
        need(stage_core_edges==1094471==manifest.get("mandatory_nonbase_stage_core_edges"),"STAGE_CORE_EDGE_COUNT",stage_core_edges)

        # Resolve structural nodes by independently frozen semantic roles.
        def rid(role):
            need(role in role_to_id,"MISSING_ROLE",role); return role_to_id[role]
        s4=rid("IMMUTABLE_S4_PERMUTATION_MATRIX_TABLE")
        roots_const=rid("IMMUTABLE_NORMALIZED_SHEET_ROOT_NUMERATORS")
        k0=rid("K_C0_BACKGROUND_EXACT_744_MATRIX"); k1=rid("K_C1_BACKGROUND_EXACT_744_MATRIX")
        x0=rid("C0_FUSED_DETERMINANT_INPUT_K_MINUS_TAU_PROJECTORS"); x1=rid("C1_FUSED_DETERMINANT_INPUT_K_MINUS_TAU_PROJECTORS")
        q1=rid("BERKOWITZ_SHARED_STAGE_Q_D1")
        need(q1 < node_count,"BASE_Q1")

        # Stage inventory and exact wiring, including d616/d617 boundary.
        prev=q1
        q_shared={1:q1}
        for d in range(2,617):
            groups=stage_nodes[("SHARED",d)]
            need(len(groups["MATRIX_VECTOR_CHAIN"])==1 and len(groups["DOT_PRODUCT"])==d-1 and len(groups["LOWER_TRIANGULAR_TOEPLITZ_BUILD"])==1 and len(groups["TOEPLITZ_VECTOR_PRODUCT"])==1,"FAIL_STAGE_INVENTORY_MISMATCH",["SHARED",d])
            chain=groups["MATRIX_VECTOR_CHAIN"][0]; dots=groups["DOT_PRODUCT"]; t=groups["LOWER_TRIANGULAR_TOEPLITZ_BUILD"][0]; q=groups["TOEPLITZ_VECTOR_PRODUCT"][0]
            need(list(parents_flat[offsets[chain]:offsets[chain+1]])==[x0,x0],"CHAIN_MATRIX_SHARED",d)
            need(list(parents_flat[offsets[t]:offsets[t+1]])==[x0]+dots,"TOEPLITZ_PARENT_WIRING",["SHARED",d])
            for j,did in enumerate(dots): need(list(parents_flat[offsets[did]:offsets[did+1]])==[x0,chain],"DOT_PARENT_WIRING",["SHARED",d,j])
            need(list(parents_flat[offsets[q]:offsets[q+1]])==[t,prev],"FAIL_STAGE_LINKAGE",["SHARED",d])
            prev=q; q_shared[d]=q
        need(616 in q_shared,"MISSING_D616")
        final_q={}
        for core,matrix in [("C0",x0),("C1",x1)]:
            prev=q_shared[616]
            for d in range(617,745):
                groups=stage_nodes[(core,d)]
                need(len(groups["MATRIX_VECTOR_CHAIN"])==1 and len(groups["DOT_PRODUCT"])==d-1 and len(groups["LOWER_TRIANGULAR_TOEPLITZ_BUILD"])==1 and len(groups["TOEPLITZ_VECTOR_PRODUCT"])==1,"FAIL_STAGE_INVENTORY_MISMATCH",[core,d])
                chain=groups["MATRIX_VECTOR_CHAIN"][0]; dots=groups["DOT_PRODUCT"]; t=groups["LOWER_TRIANGULAR_TOEPLITZ_BUILD"][0]; q=groups["TOEPLITZ_VECTOR_PRODUCT"][0]
                need(list(parents_flat[offsets[chain]:offsets[chain+1]])==[matrix,matrix],"CHAIN_MATRIX_CORE",[core,d])
                need(list(parents_flat[offsets[t]:offsets[t+1]])==[matrix]+dots,"TOEPLITZ_PARENT_WIRING",[core,d])
                for j,did in enumerate(dots): need(list(parents_flat[offsets[did]:offsets[did+1]])==[matrix,chain],"DOT_PARENT_WIRING",[core,d,j])
                need(list(parents_flat[offsets[q]:offsets[q+1]])==[t,prev],"FAIL_STAGE_LINKAGE",[core,d])
                prev=q
            final_q[core]=prev
        report["checks"].append("independent_stage_inventory_and_linkage")

        # Independently recover extraction nodes from manifest maps and frozen masks.
        expected_maps={"C0":C0_MASKS,"C1":C1_MASKS}
        name_to_eid={}
        for core,masks in expected_maps.items():
            fq=final_q[core]; var_order=C0_VARS if core=="C0" else C1_VARS
            for name,mask in masks.items():
                k=pop(mask); role=f"COEFF{k}_{core}_{name}"; eid=rid(role)
                name_to_eid[name]=eid
                pars=list(parents_flat[offsets[eid]:offsets[eid+1]])
                need(pars==[fq],"EXTRACTION_PARENT",role)
                # Manifest mapping must agree with independently located node.
                mm=manifest[f"Coeff{k}_extraction_mappings"].get(name)
                need(mm=={"node_id":eid,"core":core,"mask":mask},"EXTRACTION_MANIFEST_MAP",role)
        report["checks"].append("four_coefficient_extraction_maps")

        # Exact root helper pattern and root IDs.
        expected_root_ids={}
        for root in ROOT_NAMES:
            scaled=[]
            for idx,(name,weight) in enumerate(ROOT_TERMS[root]):
                role=f"{root}_TERM_{idx:02d}_{name}_SCALE"; sid=rid(role)
                need(list(parents_flat[offsets[sid]:offsets[sid+1]])==[name_to_eid[name]],"ROOT_SCALE_PARENT",role)
                # Re-read exact node from semantic role is not retained; stream lookup later below.
                scaled.append(sid)
            acc=scaled[0]
            for add_idx,nxt in enumerate(scaled[1:],start=1):
                aid=rid(f"{root}_ADD_{add_idx:02d}")
                need(list(parents_flat[offsets[aid]:offsets[aid+1]])==[acc,nxt],"ROOT_ADD_WIRING",[root,add_idx])
                acc=aid
            expected_root_ids[root]=acc
        need(manifest.get("all_six_root_node_ids")==expected_root_ids,"FAIL_ROOT_MAPPING",[manifest.get("all_six_root_node_ids"),expected_root_ids])
        report["checks"].append("six_root_wiring")

        # Second semantic pass: exact root weights and extraction metadata, independent of generator.
        semantic_seen=set()
        for d in descs:
            with open(cert/"chunks"/d["file_name"],"rb") as fh:
                for line in fh:
                    obj=json.loads(line)
                    role=obj["semantic_role"]
                    if role.startswith("COEFF"):
                        name=obj["exact_index_parameters"].get("semantic_name")
                        mask=obj["exact_index_parameters"].get("tau_monomial_mask")
                        k=obj["exact_index_parameters"].get("coefficient_order")
                        need(obj["exact_index_parameters"].get("determinant_component_index")==744,"EXTRACTION_DET_COMPONENT",role)
                        need(obj["output_shape"]==[745],"EXTRACTION_SHAPE",role)
                        need(k==pop(mask),"EXTRACTION_ORDER_MASK",role)
                        semantic_seen.add(role)
                    if "_TERM_" in role and role.endswith("_SCALE"):
                        # role embeds exact root, term index and name.
                        ep=obj["exact_index_parameters"]
                        root=ep.get("root"); idx=ep.get("term_index"); name=ep.get("semantic_name")
                        need(root in ROOT_TERMS and isinstance(idx,int) and 0<=idx<len(ROOT_TERMS[root]),"ROOT_TERM_METADATA",role)
                        ename,eweight=ROOT_TERMS[root][idx]
                        need(name==ename and obj["exact_integer_constants"]==[eweight],"ROOT_WEIGHT",role)
                    if role=="BERKOWITZ_SHARED_STAGE_Q_D1":
                        need(obj["output_shape"]==[2] and obj["exact_integer_constants"]==[1,-1],"BASE_STAGE_SEMANTICS")
        need(len(semantic_seen)==23,"EXTRACTION_NODE_TOTAL",len(semantic_seen))
        report["checks"].append("semantic_metadata_and_root_weights")

        # Backward reachability from six roots. Every node must be reachable: no whitelist needed in this certificate.
        roots=list(expected_root_ids.values())
        seen=bytearray(node_count); stack=roots[:]
        while stack:
            n=stack.pop()
            if seen[n]: continue
            seen[n]=1
            a=offsets[n]; b=offsets[n+1]
            stack.extend(parents_flat[a:b])
        reachable=sum(seen)
        need(reachable==node_count,"FAIL_CERTIFICATE_COMPLETENESS",{"reachable":reachable,"total":node_count})
        report["checks"].append("backward_reachability_no_extras")

        need(manifest.get("determinant_core_count")==2,"CORE_COUNT")
        need(manifest.get("semantic_stage_count")==1488,"SEMANTIC_STAGE_COUNT")
        need(manifest.get("unique_stage_subgraph_count")==872,"UNIQUE_STAGE_COUNT")
        need(manifest.get("shared_stage_interval")=="d=1..616" and manifest.get("C0_specific_interval")=="d=617..744" and manifest.get("C1_specific_interval")=="d=617..744","SHARING_BOUNDARY")
        need(manifest.get("maximum_MATVEC_CHAIN_length")==742,"MAX_CHAIN")
        report["checks"].append("frozen_global_counts")

        report["status"]="PASS_FRESH_EXACT_BERKOWITZ_CHUNKED_COMPLETE_MACRO_DAG_AND_INDEPENDENT_STREAMING_CHECKER"
        report["node_count"]=node_count; report["edge_count"]=edge_count; report["reachable_nodes"]=reachable
        out=json.dumps(report,sort_keys=True,separators=(",",":"))
        print(out)
        if args.report: Path(args.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
        return 0
    except Exception as e:
        report["error"]=str(e)
        out=json.dumps(report,sort_keys=True,separators=(",",":"))
        print(out,file=sys.stderr)
        if args.report: Path(args.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
        return 1

if __name__=="__main__":
    raise SystemExit(main())
