from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path
from collections import Counter

SCHEMA = "FRESH_BERKOWITZ_MACRO_DAG_CHUNKED_V1"
VERSION = "1.0"
CHUNK_MAX = 4096
DOMAIN = b"JANUS_TRUMP_FRESH_BERKOWITZ_MACRO_DAG_V1\x00"
SRC_D37 = "d37be23c8ce8425d1672a8ed118fb10099195de0"
SRC_B906 = "b9060a05562fcb29b8ecc15d0f03085b4214fe1d"
SRC_449 = "449d5e3044dd69dd857ae40d8499cd589eb78cac"
SEMANTIC_BLOB = "f7686ec7bb7d3ab30a350aaecbdf1ed33f049277"

C0_VARS = ["u","v","a0","a1","b0","b1","c0","c1"]
C1_VARS = ["v","u","b1","zvec","x_plus_zvec","x","y_plus_zvec","y"]
ROOT_NAMES = ["widehat_S23","widehat_Theta3","widehat_Xi23","widehat_Omega0","widehat_Omega1","widehat_Pi"]

C0_MASKS = {
 "Coeff1_u":1, "Coeff1_v":2,
 "Coeff2_u_a0":5, "Coeff2_v_a0":6, "Coeff2_u_a1":9, "Coeff2_v_a1":10,
 "Coeff2_u_b0":17, "Coeff2_v_b0":18, "Coeff2_u_b1":33, "Coeff2_v_b1":34,
 "Delta00":19, "Delta01_u":37, "Delta01_v":38, "Delta10_u":25, "Delta10_v":26,
 "Theta3":35, "Omega0":99, "Omega1":163
}
C1_MASKS = {"Q_zvec":15,"Q_x_plus_zvec":23,"Q_x":39,"Q_y_plus_zvec":71,"Q_y":135}

ROOT_TERMS = {
 "widehat_S23":[
   ("Coeff1_u",-96),("Coeff1_v",96),
   ("Coeff2_u_a0",-64),("Coeff2_v_a0",64),
   ("Coeff2_u_a1",-32),("Coeff2_v_a1",32),
   ("Coeff2_u_b0",-48),("Coeff2_v_b0",48),
   ("Coeff2_u_b1",-48),("Coeff2_v_b1",48),
   ("Delta00",-32),("Delta01_u",-32),("Delta01_v",32),
   ("Delta10_u",-16),("Delta10_v",16),("Theta3",16)
 ],
 "widehat_Theta3":[("Theta3",96)],
 "widehat_Xi23":[("Delta00",32),("Delta01_u",32),("Delta01_v",-32),("Delta10_u",16),("Delta10_v",-16)],
 "widehat_Omega0":[("Omega0",96)],
 "widehat_Omega1":[("Omega1",96)],
 "widehat_Pi":[("Q_zvec",240),("Q_x_plus_zvec",-48),("Q_x",48),("Q_y_plus_zvec",-96),("Q_y",96)]
}

S4_CODES = [
"1234","1243","1324","1342","1423","1432","2134","2143","2314","2341","2413","2431",
"3124","3142","3214","3241","3412","3421","4123","4132","4213","4231","4312","4321"
]

LOCAL_VECTOR_SPECS = {
 "u":{"formula":"L_minus(alpha)","root":"alpha","h":1,"t":-1},
 "v":{"formula":"L_plus(alpha)","root":"alpha","h":1,"t":1},
 "a0":{"formula":"L_plus(beta)","root":"beta","h":1,"t":1},
 "a1":{"formula":"L_minus(beta)","root":"beta","h":1,"t":-1},
 "b0":{"formula":"L_plus(gamma)","root":"gamma","h":1,"t":1},
 "b1":{"formula":"L_minus(gamma)","root":"gamma","h":1,"t":-1},
 "c0":{"formula":"L_plus(delta)","root":"delta","h":1,"t":1},
 "c1":{"formula":"L_minus(delta)","root":"delta","h":1,"t":-1},
 "zvec":{"formula":"t_tensor_eta","root":"eta","h":0,"t":1},
 "x_plus_zvec":{"formula":"h_tensor_delta_plus_t_tensor_eta","root_pair":["delta","eta"],"h":1,"t":1},
 "x":{"formula":"h_tensor_delta","root":"delta","h":1,"t":0},
 "y_plus_zvec":{"formula":"t_tensor_delta_plus_t_tensor_eta","root_pair":["delta","eta"],"h":0,"t":1},
 "y":{"formula":"t_tensor_delta","root":"delta","h":0,"t":1}
}

REQUIRED_FIELDS = [
"node_id","opcode","ordered_parent_ids","input_shapes","output_shape","semantic_role",
"determinant_core_role","stage_d","local_index","exact_index_parameters","exact_integer_constants",
"coefficient_variable_order","semantic_source_commit","semantic_source_section"
]

def jcs(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False).encode("utf-8")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def bitcount(n:int)->int:
    return int(n).bit_count()

def s4_matrices():
    mats=[]
    for code in S4_CODES:
        m=[[0]*4 for _ in range(4)]
        for col,ch in enumerate(code):
            row=int(ch)-1
            m[row][col]=1
        mats.append(m)
    return mats

class Writer:
    def __init__(self, out_dir:Path):
        self.out_dir=out_dir
        self.chunks_dir=out_dir/"chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        for p in self.chunks_dir.glob("chunk_*.jsonl"):
            p.unlink()
        self.node_id=0
        self.edge_count=0
        self.opcodes=Counter()
        self.chunk_index=0
        self.chunk_count=0
        self.chunk_first=None
        self.chunk_path=None
        self.chunk_file=None
        self.chunk_hasher=None
        self.chunk_bytes=0
        self.descriptors=[]
    def _open_chunk(self):
        self.chunk_first=self.node_id
        self.chunk_count=0
        self.chunk_bytes=0
        self.chunk_hasher=hashlib.sha256()
        self.chunk_path=self.chunks_dir/f"chunk_{self.chunk_index:06d}.jsonl"
        self.chunk_file=open(self.chunk_path,"wb")
    def _close_chunk(self):
        if self.chunk_file is None: return
        self.chunk_file.flush(); os.fsync(self.chunk_file.fileno()); self.chunk_file.close()
        self.descriptors.append({
            "chunk_index":self.chunk_index,
            "file_name":self.chunk_path.name,
            "first_node_id":self.chunk_first,
            "last_node_id":self.node_id-1,
            "node_count":self.chunk_count,
            "raw_byte_count":self.chunk_bytes,
            "sha256":self.chunk_hasher.hexdigest()
        })
        self.chunk_index+=1
        self.chunk_file=None
    def emit(self, **kw):
        if self.chunk_file is None:
            self._open_chunk()
        node={k:kw.get(k) for k in REQUIRED_FIELDS}
        node["node_id"]=self.node_id
        raw=jcs(node)+b"\n"
        self.chunk_file.write(raw)
        self.chunk_hasher.update(raw)
        self.chunk_bytes+=len(raw)
        self.chunk_count+=1
        self.edge_count+=len(node["ordered_parent_ids"])
        self.opcodes[node["opcode"]]+=1
        out=self.node_id
        self.node_id+=1
        if self.chunk_count==CHUNK_MAX:
            self._close_chunk()
        return out
    def finish(self):
        self._close_chunk()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    repo=Path(args.repo).resolve()
    out=(repo/args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    w=Writer(out)

    s4_id=w.emit(
        opcode="INTEGER_CONSTANT", ordered_parent_ids=[], input_shapes=[], output_shape=[24,4,4],
        semantic_role="IMMUTABLE_S4_PERMUTATION_MATRIX_TABLE", determinant_core_role=None, stage_d=None, local_index=None,
        exact_index_parameters={"coding":S4_CODES,"column_rule":"column i equals e_sigma(i)","index_order":"code,row,column"},
        exact_integer_constants=s4_matrices(), coefficient_variable_order=[],
        semantic_source_commit=SRC_D37, semantic_source_section="EXACT_S4_COMPILER"
    )
    roots_id=w.emit(
        opcode="INTEGER_CONSTANT", ordered_parent_ids=[], input_shapes=[], output_shape=[5,4],
        semantic_role="IMMUTABLE_NORMALIZED_SHEET_ROOT_NUMERATORS", determinant_core_role=None, stage_d=None, local_index=None,
        exact_index_parameters={"root_order":["alpha","beta","gamma","delta","eta"],"normalization_denominator_symbol":"sqrt(2)","projector_denominator":2},
        exact_integer_constants=[[1,-1,0,0],[1,0,-1,0],[0,1,-1,0],[1,0,0,-1],[0,1,0,-1]],
        coefficient_variable_order=[], semantic_source_commit=SRC_D37, semantic_source_section="VECTOR_CONSTRUCTOR_CLOSURE"
    )

    context_ids=[]
    for i in range(280):
        context_ids.append(w.emit(
            opcode="FINITE_DOMAIN_S4_SELECT", ordered_parent_ids=[s4_id], input_shapes=[[24,4,4]], output_shape=[4,4],
            semantic_role=f"RESIDUAL_S4_COORDINATE_{i:03d}", determinant_core_role=None, stage_d=None, local_index=i,
            exact_index_parameters={"external_symbol":f"r_{i:03d}","domain_codes":[0,23],"selector_axis":0,"residual_coordinate_index":i},
            exact_integer_constants=[], coefficient_variable_order=[], semantic_source_commit=SRC_D37, semantic_source_section="RESIDUAL_HOLONOMY_COORDINATES"
        ))

    k_ids={}
    for core in ["C0","C1"]:
        k_ids[core]=w.emit(
            opcode="EXACT_INDEXED_MUX", ordered_parent_ids=[s4_id]+context_ids,
            input_shapes=[[24,4,4]]+[[4,4]]*280, output_shape=[744,744],
            semantic_role=f"K_{core}_BACKGROUND_EXACT_744_MATRIX", determinant_core_role=core, stage_d=None, local_index=None,
            exact_index_parameters={
                "ambient_dimension":744,
                "base_vertex_order":"P1..P31_then_lexicographic_STS31_blocks",
                "sheet_order":[1,2,3,4],
                "physical_index_map":"4*base_position+(sheet-1)",
                "distinguished_edge":{"h":"P1","t":"B[1,2,3]","h_sheet_indices":[0,1,2,3],"t_sheet_indices":[124,125,126,127]},
                "matrix_law":"zeta*I_744-M14_C",
                "core_role":core,
                "canonical_context":"xi34=I; forest labels I; residual chords in inherited canonical E+ order",
                "row_major":True
            },
            exact_integer_constants=[], coefficient_variable_order=[],
            semantic_source_commit=SRC_D37, semantic_source_section="K_CIRCUIT_CLOSURE"
        )

    vector_ids={}
    for core,var_order in [("C0",C0_VARS),("C1",C1_VARS)]:
        local=[]
        for idx,name in enumerate(var_order):
            spec=LOCAL_VECTOR_SPECS[name]
            vid=w.emit(
                opcode="VECTOR_CONCAT_SLICE", ordered_parent_ids=[roots_id], input_shapes=[[5,4]], output_shape=[744],
                semantic_role=f"{core}_LOCAL_VECTOR_{name}", determinant_core_role=core, stage_d=None, local_index=idx,
                exact_index_parameters={
                    "name":name,"constructor":spec,"ambient_dimension":744,
                    "h_base_position":0,"t_base_position":31,
                    "h_sheet_indices":[0,1,2,3],"t_sheet_indices":[124,125,126,127],
                    "all_other_coordinates_zero":True,
                    "normalization_projector_denominator":2
                },
                exact_integer_constants=[], coefficient_variable_order=var_order,
                semantic_source_commit=SRC_D37, semantic_source_section="VECTOR_CONSTRUCTOR_CLOSURE"
            )
            vector_ids[(core,name)]=vid
            local.append(vid)
        x_id=w.emit(
            opcode="EXACT_INDEXED_MUX", ordered_parent_ids=[k_ids[core]]+local,
            input_shapes=[[744,744]]+[[744]]*8, output_shape=[744,744],
            semantic_role=f"{core}_FUSED_DETERMINANT_INPUT_K_MINUS_TAU_PROJECTORS", determinant_core_role=core, stage_d=None, local_index=None,
            exact_index_parameters={
                "formula":"K_core - sum_i tau_i * w_i*w_i^T",
                "coefficient_variable_order":var_order,
                "projector_denominator":2,
                "exact_ring":"Z[1/2][zeta,tau_0,...,tau_7]",
                "row_major":True
            },
            exact_integer_constants=[], coefficient_variable_order=var_order,
            semantic_source_commit=SRC_B906, semantic_source_section="FRESH_MACRO_STAGE_COMPILATION.universal_variable_fusion"
        )
        vector_ids[(core,"X")]=x_id

    x_c0=vector_ids[("C0","X")]
    x_c1=vector_ids[("C1","X")]

    q_shared=w.emit(
        opcode="VECTOR_CONCAT_SLICE", ordered_parent_ids=[x_c0], input_shapes=[[744,744]], output_shape=[2],
        semantic_role="BERKOWITZ_SHARED_STAGE_Q_D1", determinant_core_role="SHARED", stage_d=1, local_index=None,
        exact_index_parameters={"trailing_start":743,"a_index":[743,743],"formula":["1","-a_1"],"stage_internal_order":"monic_then_descending_lambda_degree"},
        exact_integer_constants=[1,-1], coefficient_variable_order=[],
        semantic_source_commit=SRC_B906, semantic_source_section="FRESH_STAGE_RECURRENCE.base_case"
    )

    stage_products={("SHARED",1):q_shared}
    stage_inventory_count=0
    stage_edge_count=0
    max_chain_endpoint=0

    def emit_stage(core,d,prev_q,matrix_id,var_order):
        nonlocal stage_inventory_count, stage_edge_count, max_chain_endpoint
        start=744-d
        chain=w.emit(
            opcode="MATRIX_VECTOR_CHAIN", ordered_parent_ids=[matrix_id,matrix_id],
            input_shapes=[[d-1,d-1],[d-1]], output_shape=[d-1,d-1],
            semantic_role=f"BERKOWITZ_{core}_D{d:03d}_MATRIX_VECTOR_CHAIN", determinant_core_role=core, stage_d=d, local_index=None,
            exact_index_parameters={
                "matrix_slice":{"row_start":start+1,"row_end_exclusive":744,"col_start":start+1,"col_end_exclusive":744},
                "vector_slice":{"row_start":start+1,"row_end_exclusive":744,"col":start},
                "power_start":0,"power_end_inclusive":d-2,
                "orientation":"w_j=M^j*c"
            }, exact_integer_constants=[], coefficient_variable_order=var_order,
            semantic_source_commit=SRC_B906, semantic_source_section="FRESH_MACRO_STAGE_COMPILATION.MATRIX_VECTOR_CHAIN"
        )
        dot_ids=[]
        for j in range(d-1):
            dot_ids.append(w.emit(
                opcode="DOT_PRODUCT", ordered_parent_ids=[matrix_id,chain],
                input_shapes=[[d-1],[d-1]], output_shape=[],
                semantic_role=f"BERKOWITZ_{core}_D{d:03d}_DOT_J{j:03d}", determinant_core_role=core, stage_d=d, local_index=j,
                exact_index_parameters={
                    "left_row_slice":{"row":start,"col_start":start+1,"col_end_exclusive":744},
                    "right_chain_index":j,
                    "orientation":"r*M^j*c"
                }, exact_integer_constants=[], coefficient_variable_order=var_order,
                semantic_source_commit=SRC_B906, semantic_source_section="FRESH_MACRO_STAGE_COMPILATION.DOT_PRODUCT"
            ))
        t=w.emit(
            opcode="LOWER_TRIANGULAR_TOEPLITZ_BUILD", ordered_parent_ids=[matrix_id]+dot_ids,
            input_shapes=[[]]+[[]]*(d-1), output_shape=[d+1,d],
            semantic_role=f"BERKOWITZ_{core}_D{d:03d}_TOEPLITZ_BUILD", determinant_core_role=core, stage_d=d, local_index=None,
            exact_index_parameters={
                "a_index":[start,start],
                "first_column_law":["1","-a"]+[f"-s_{j}" for j in range(d-1)],
                "entry_law":"T[i,j]=c[i-j] for i>=j else 0",
                "zero_based_coefficient_index":True
            }, exact_integer_constants=[1,-1], coefficient_variable_order=var_order,
            semantic_source_commit=SRC_B906, semantic_source_section="FRESH_STAGE_RECURRENCE"
        )
        q=w.emit(
            opcode="TOEPLITZ_VECTOR_PRODUCT", ordered_parent_ids=[t,prev_q],
            input_shapes=[[d+1,d],[d]], output_shape=[d+1],
            semantic_role=f"BERKOWITZ_{core}_D{d:03d}_Q", determinant_core_role=core, stage_d=d, local_index=None,
            exact_index_parameters={
                "formula":"q^(d)=T^(d)*q^(d-1)",
                "stage_internal_order":"monic_then_descending_lambda_degree",
                "external_zeta_storage_order":"ascending_zeta_degree"
            }, exact_integer_constants=[], coefficient_variable_order=var_order,
            semantic_source_commit=SRC_B906, semantic_source_section="FRESH_STAGE_RECURRENCE"
        )
        stage_inventory_count += 1
        stage_edge_count += 3*d+2
        max_chain_endpoint=max(max_chain_endpoint,d-2)
        return q

    for d in range(2,617):
        q_shared=emit_stage("SHARED",d,q_shared,x_c0,[])
        stage_products[("SHARED",d)]=q_shared

    q_c0=q_shared
    for d in range(617,745):
        q_c0=emit_stage("C0",d,q_c0,x_c0,C0_VARS)
        stage_products[("C0",d)]=q_c0
    q_c1=q_shared
    for d in range(617,745):
        q_c1=emit_stage("C1",d,q_c1,x_c1,C1_VARS)
        stage_products[("C1",d)]=q_c1

    if stage_inventory_count != 871 or stage_edge_count != 1094471 or max_chain_endpoint != 742:
        raise RuntimeError(("stage_receipt_mismatch",stage_inventory_count,stage_edge_count,max_chain_endpoint))

    extracts=[]
    for core,masks,final_q,var_order in [("C0",C0_MASKS,q_c0,C0_VARS),("C1",C1_MASKS,q_c1,C1_VARS)]:
        for name,mask in masks.items():
            extracts.append((bitcount(mask),0 if core=="C0" else 1,mask,name,core,final_q,var_order))
    extracts.sort()
    extract_ids={}
    coeff_maps={1:{},2:{},3:{},4:{}}
    for k,_,mask,name,core,final_q,var_order in extracts:
        eid=w.emit(
            opcode="EXACT_INDEXED_MUX", ordered_parent_ids=[final_q], input_shapes=[[745]], output_shape=[745],
            semantic_role=f"COEFF{k}_{core}_{name}", determinant_core_role=core, stage_d=744, local_index=mask,
            exact_index_parameters={
                "determinant_component_index":744,
                "tau_monomial_mask":mask,
                "coefficient_order":k,
                "semantic_name":name,
                "zeta_output_order":"zeta^0..zeta^744"
            }, exact_integer_constants=[], coefficient_variable_order=var_order,
            semantic_source_commit=SRC_449, semantic_source_section=f"FRESH_COEFF{k}_BRIDGE"
        )
        extract_ids[name]=eid
        coeff_maps[k][name]={"node_id":eid,"core":core,"mask":mask}

    root_ids={}
    for root in ROOT_NAMES:
        scaled=[]
        for term_index,(name,weight) in enumerate(ROOT_TERMS[root]):
            sid=w.emit(
                opcode="POLYNOMIAL_VECTOR_SCALE", ordered_parent_ids=[extract_ids[name]], input_shapes=[[745]], output_shape=[745],
                semantic_role=f"{root}_TERM_{term_index:02d}_{name}_SCALE", determinant_core_role=None, stage_d=None, local_index=term_index,
                exact_index_parameters={"semantic_name":name,"root":root,"term_index":term_index},
                exact_integer_constants=[weight], coefficient_variable_order=[],
                semantic_source_commit=SRC_449, semantic_source_section="SIX_ROOT_SUBSTITUTION_THEOREM.fresh_integer_weight_formulas"
            )
            scaled.append(sid)
        acc=scaled[0]
        for add_index,nxt in enumerate(scaled[1:], start=1):
            acc=w.emit(
                opcode="POLYNOMIAL_VECTOR_ADD", ordered_parent_ids=[acc,nxt], input_shapes=[[745],[745]], output_shape=[745],
                semantic_role=f"{root}_ADD_{add_index:02d}", determinant_core_role=None, stage_d=None, local_index=add_index,
                exact_index_parameters={"root":root,"left_fold_index":add_index},
                exact_integer_constants=[], coefficient_variable_order=[],
                semantic_source_commit=SRC_449, semantic_source_section="SIX_ROOT_SUBSTITUTION_THEOREM.fresh_integer_weight_formulas"
            )
        root_ids[root]=acc

    w.finish()

    blob_bytes=subprocess.check_output(["git","-C",str(repo),"cat-file","blob",SEMANTIC_BLOB])
    semantic_digest=sha256_bytes(blob_bytes)

    manifest_core={
        "schema":SCHEMA,
        "version":VERSION,
        "source_commits":[SRC_D37,SRC_B906,SRC_449],
        "logical_certificate_id":"R4_PI24_FRESH_EXACT_BERKOWITZ_COMPLETE_MACRO_DAG_V1",
        "chunk_format_version":"UTF8_JSONL_JCS_V1",
        "canonical_node_ordering_law":"globally unique zero-based node IDs; parent<child; frozen category/stage order",
        "chunk_size_rule":{"max_logical_nodes":CHUNK_MAX,"nonfinal_exact":CHUNK_MAX,"file_name_pattern":"chunk_%06d.jsonl"},
        "ordered_chunk_descriptors_and_sha256s":w.descriptors,
        "total_chunk_count":len(w.descriptors),
        "total_logical_node_count":w.node_id,
        "total_dependency_edge_count":w.edge_count,
        "opcode_counts":dict(sorted(w.opcodes.items())),
        "determinant_core_count":2,
        "semantic_stage_count":1488,
        "unique_stage_subgraph_count":872,
        "shared_stage_interval":"d=1..616",
        "C0_specific_interval":"d=617..744",
        "C1_specific_interval":"d=617..744",
        "maximum_MATVEC_CHAIN_length":742,
        "Coeff1_extraction_mappings":coeff_maps[1],
        "Coeff2_extraction_mappings":coeff_maps[2],
        "Coeff3_extraction_mappings":coeff_maps[3],
        "Coeff4_extraction_mappings":coeff_maps[4],
        "all_six_root_node_ids":root_ids,
        "normalization":"96*D_base",
        "zeta_coefficient_order":"[zeta^0,zeta^1,...,zeta^744]",
        "semantic_source_digest_algorithm":"SHA-256 over exact git blob bytes of sealed 449d5e30 proof artifact",
        "semantic_source_digest":semantic_digest,
        "semantic_source_version":"R4_PI24_FRESH_EXACT_BERKOWITZ_SEMANTICS_V1",
        "semantic_source_git_blob":SEMANTIC_BLOB,
        "mandatory_nonbase_stage_core_nodes":365985,
        "mandatory_nonbase_stage_core_edges":1094471,
        "structural_ids":{
            "s4_table":s4_id,"sheet_root_numerators":roots_id,
            "K_C0_background":k_ids["C0"],"K_C1_background":k_ids["C1"],
            "X_C0":x_c0,"X_C1":x_c1,
            "shared_q_d1":stage_products[("SHARED",1)],
            "shared_q_d616":stage_products[("SHARED",616)],
            "C0_q_d744":q_c0,"C1_q_d744":q_c1
        }
    }
    cert_digest=sha256_bytes(DOMAIN+jcs(manifest_core))
    manifest=dict(manifest_core)
    manifest["certificate_digest"]=cert_digest
    (out/"manifest.json").write_bytes(jcs(manifest)+b"\n")
    print(json.dumps({
        "status":"MATERIALIZED",
        "certificate_digest":cert_digest,
        "chunks":len(w.descriptors),
        "nodes":w.node_id,
        "edges":w.edge_count,
        "stage_core_nodes":365985,
        "stage_core_edges":stage_edge_count,
        "semantic_source_digest":semantic_digest
    },sort_keys=True))

if __name__=="__main__":
    main()
