import argparse, hashlib, json
from pathlib import Path

DOMAIN=b"JANUS_TRUMP_FRESH_BERKOWITZ_MACRO_DAG_V1\x00"
BACKEND_SCHEMA="TRUMP_COMPRESSED_MACROCSP_BACKEND_V1"
EXPECTED_CERT="d7831123307ee6d2fc6efff231815706335b4ac794db0fb1bea204b13b8e4b74"

def jcs(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load_source(cert):
    m=json.loads((cert/"manifest.json").read_text(encoding="utf-8"))
    core=dict(m); claimed=core.pop("certificate_digest")
    if sha(DOMAIN+jcs(core)) != claimed or claimed != EXPECTED_CERT:
        raise RuntimeError("source_manifest_digest_mismatch")
    nodes=[]; expect=0
    for d in m["ordered_chunk_descriptors_and_sha256s"]:
        raw=(cert/"chunks"/d["file_name"]).read_bytes()
        if sha(raw) != d["sha256"]: raise RuntimeError(("chunk_hash",d["file_name"]))
        for line in raw.splitlines():
            n=json.loads(line)
            if n["node_id"] != expect: raise RuntimeError(("node_id",expect,n["node_id"]))
            nodes.append(n); expect += 1
    if expect != m["total_logical_node_count"]: raise RuntimeError("node_count")
    return m,nodes

def add(groups,kind,a,b,recipe,**extra):
    g={"object_id":len(groups),"kind":kind,"source_first_id":a,"source_last_id":b,"recipe_id":recipe}
    g.update(extra); groups.append(g)

def build_groups(nodes):
    g=[]
    add(g,"S4_TABLE",0,0,"COPY_EXACT_INTEGER_CONSTANT")
    add(g,"ROOT_NUMERATORS",1,1,"COPY_EXACT_INTEGER_CONSTANT")
    add(g,"S4_COORDINATE_FAMILY",2,281,"FINITE_DOMAIN_S4_SELECT_FAMILY",count=280)
    add(g,"BACKGROUND_MATRIX_FAMILY",282,283,"EXACT_INDEXED_BACKGROUND_RECONSTRUCTION",count=2)
    add(g,"C0_LOCAL_VECTOR_FAMILY",284,291,"VECTOR_CONSTRUCTOR_FAMILY",count=8)
    add(g,"C0_FUSED_INPUT",292,292,"EXACT_FUSED_INPUT_IDENTITY")
    add(g,"C1_LOCAL_VECTOR_FAMILY",293,300,"VECTOR_CONSTRUCTOR_FAMILY",count=8)
    add(g,"C1_FUSED_INPUT",301,301,"EXACT_FUSED_INPUT_IDENTITY")
    add(g,"SHARED_BASE_STAGE",302,302,"BERKOWITZ_BASE_STAGE_IDENTITY",core="SHARED",stage_d=1)
    i=303; stages=0
    while i <= 366287:
        n=nodes[i]
        if n["opcode"]!="MATRIX_VECTOR_CHAIN": raise RuntimeError(("stage_start",i,n["opcode"]))
        d=n["stage_d"]; core=n["determinant_core_role"]
        dot_first=i+1; dot_last=dot_first+d-2; tb=dot_last+1; q=tb+1
        dots=nodes[dot_first:dot_last+1]
        if len(dots)!=d-1 or any(x["opcode"]!="DOT_PRODUCT" or x["stage_d"]!=d or x["determinant_core_role"]!=core or x["local_index"]!=k for k,x in enumerate(dots)):
            raise RuntimeError(("dot_family",core,d))
        if nodes[tb]["opcode"]!="LOWER_TRIANGULAR_TOEPLITZ_BUILD" or nodes[q]["opcode"]!="TOEPLITZ_VECTOR_PRODUCT":
            raise RuntimeError(("stage_tail",core,d))
        add(g,"BERKOWITZ_STAGE_FAMILY",i,q,"FROZEN_STAGE_FAMILY_IDENTITY",core=core,stage_d=d,chain_node=i,dot_first=dot_first,dot_last=dot_last,toeplitz_build_node=tb,q_node=q)
        i=q+1; stages+=1
    if stages!=871 or i!=366288: raise RuntimeError(("stage_inventory",stages,i))
    add(g,"COEFFICIENT_EXTRACTION_FAMILY",366288,366310,"EXACT_MASK_EXTRACTION_FAMILY",count=23)
    add(g,"ROOT_POSTPROCESS_S23",366311,366341,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_S23")
    add(g,"ROOT_POSTPROCESS_THETA3",366342,366342,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Theta3")
    add(g,"ROOT_POSTPROCESS_XI23",366343,366351,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Xi23")
    add(g,"ROOT_POSTPROCESS_OMEGA0",366352,366352,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Omega0")
    add(g,"ROOT_POSTPROCESS_OMEGA1",366353,366353,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Omega1")
    add(g,"ROOT_POSTPROCESS_PI",366354,366362,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Pi")
    cursor=0
    for x in g:
        if x["source_first_id"]!=cursor: raise RuntimeError(("coverage_gap",cursor,x))
        cursor=x["source_last_id"]+1
    if cursor!=366363: raise RuntimeError(("coverage_end",cursor))
    return g

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cert",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); cert=Path(a.cert); out=Path(a.out)
    src,nodes=load_source(cert); groups=build_groups(nodes)
    manifest={
      "schema":BACKEND_SCHEMA,"version":"1.1","input_certificate_digest":EXPECTED_CERT,
      "source_logical_node_count":src["total_logical_node_count"],"compressed_object_count":len(groups),
      "stage_family_object_count":sum(x["kind"]=="BERKOWITZ_STAGE_FAMILY" for x in groups),
      "groups":groups,
      "architecture":"EXACT_WORD_LEVEL_MACROCSP_PLUS_PROOF_CARRYING_24_ARY_DECISION_DAG_V1",
      "branch_codes":list(range(24)),"branch_arity":24,
      "branch_coordinate_rule":"MIN_UNRESOLVED_COORDINATE_IN_CANONICAL_ORDER",
      "branch_value_order":list(range(24)),
      "TRUMP_EXACT_ALGEBRA_ONLY":True,"heuristics_forbidden":True,
      "randomness_forbidden":True,"learned_selector_forbidden":True,"probabilistic_guidance_forbidden":True,
      "approximate_pruning_forbidden":True,"scored_ranking_forbidden":True,
      "heuristics_present":False,"randomness_present":False,
      "learned_selector_present":False,"probabilistic_guidance_present":False,
      "approximate_pruning_present":False,"scored_ranking_present":False,
      "pruning_authority":"EXACT_REPLAYABLE_MATHEMATICAL_OR_ALGEBRAIC_DERIVATION_ONLY",
      "memoization_rule":"BYTE_IDENTICAL_CANONICAL_RESIDUAL_STATE_OR_SEPARATELY_CERTIFIED_EXACT_EQUIVALENCE",
      "sat_authority":"REPLAY_SAME_CERTIFICATE_DIGEST",
      "unsat_authority":"INDEPENDENTLY_CHECKABLE_EXHAUSTIVE_PROOF_DAG_ONLY",
      "safe_signed_width_bits":10996,
      "pi_search_executed":False,"solver_executed":False
    }
    raw=jcs(manifest)+b"\n"; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(raw)
    print(json.dumps({"status":"BUILT","objects":len(groups),"stages":manifest["stage_family_object_count"],"bytes":len(raw),"sha256":sha(raw)},sort_keys=True))
if __name__=="__main__": raise SystemExit(main())
