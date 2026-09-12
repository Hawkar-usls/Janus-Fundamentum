import argparse
import hashlib
import json
from pathlib import Path

DOMAIN=b"JANUS_TRUMP_FRESH_BERKOWITZ_MACRO_DAG_V1\x00"
EXPECTED_CERT="d7831123307ee6d2fc6efff231815706335b4ac794db0fb1bea204b13b8e4b74"
EXPECTED_SCHEMA="TRUMP_COMPRESSED_MACROCSP_BACKEND_V1"

def jcs(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def sha(b):
    return hashlib.sha256(b).hexdigest()

def rec(kind,a,b,recipe,**kw):
    x={"kind":kind,"source_first_id":a,"source_last_id":b,"recipe_id":recipe}
    x.update(kw)
    return x

def load_nodes(cert):
    m=json.loads((cert/"manifest.json").read_text(encoding="utf-8"))
    core=dict(m)
    claimed=core.pop("certificate_digest")
    if claimed!=EXPECTED_CERT or sha(DOMAIN+jcs(core))!=claimed:
        raise ValueError("SOURCE_DIGEST")
    nodes=[]
    expected=0
    for d in m["ordered_chunk_descriptors_and_sha256s"]:
        raw=(cert/"chunks"/d["file_name"]).read_bytes()
        if sha(raw)!=d["sha256"]:
            raise ValueError("SOURCE_CHUNK_HASH")
        for line in raw.splitlines():
            n=json.loads(line)
            if n["node_id"]!=expected:
                raise ValueError("SOURCE_NODE_ORDER")
            nodes.append(n)
            expected+=1
    if expected!=366363:
        raise ValueError("SOURCE_NODE_COUNT")
    return nodes

def expected_groups(nodes):
    out=[]
    def add(kind,a,b,recipe,**kw):
        x=rec(kind,a,b,recipe,**kw)
        x["object_id"]=len(out)
        out.append(x)
    add("S4_TABLE",0,0,"COPY_EXACT_INTEGER_CONSTANT")
    add("ROOT_NUMERATORS",1,1,"COPY_EXACT_INTEGER_CONSTANT")
    add("S4_COORDINATE_FAMILY",2,281,"FINITE_DOMAIN_S4_SELECT_FAMILY",count=280)
    add("BACKGROUND_MATRIX_FAMILY",282,283,"EXACT_INDEXED_BACKGROUND_RECONSTRUCTION",count=2)
    add("C0_LOCAL_VECTOR_FAMILY",284,291,"VECTOR_CONSTRUCTOR_FAMILY",count=8)
    add("C0_FUSED_INPUT",292,292,"EXACT_FUSED_INPUT_IDENTITY")
    add("C1_LOCAL_VECTOR_FAMILY",293,300,"VECTOR_CONSTRUCTOR_FAMILY",count=8)
    add("C1_FUSED_INPUT",301,301,"EXACT_FUSED_INPUT_IDENTITY")
    add("SHARED_BASE_STAGE",302,302,"BERKOWITZ_BASE_STAGE_IDENTITY",core="SHARED",stage_d=1)
    i=303
    stage_count=0
    while i<=366287:
        n=nodes[i]
        if n["opcode"]!="MATRIX_VECTOR_CHAIN":
            raise ValueError("STAGE_START")
        d=n["stage_d"]
        core=n["determinant_core_role"]
        dot_first=i+1
        dot_last=dot_first+d-2
        tb=dot_last+1
        q=tb+1
        dots=nodes[dot_first:dot_last+1]
        if len(dots)!=d-1:
            raise ValueError("DOT_COUNT")
        for k,x in enumerate(dots):
            if x["opcode"]!="DOT_PRODUCT" or x["stage_d"]!=d or x["determinant_core_role"]!=core or x["local_index"]!=k:
                raise ValueError("DOT_FAMILY")
        if nodes[tb]["opcode"]!="LOWER_TRIANGULAR_TOEPLITZ_BUILD":
            raise ValueError("TOEPLITZ_BUILD")
        if nodes[q]["opcode"]!="TOEPLITZ_VECTOR_PRODUCT":
            raise ValueError("TOEPLITZ_PRODUCT")
        add("BERKOWITZ_STAGE_FAMILY",i,q,"FROZEN_STAGE_FAMILY_IDENTITY",core=core,stage_d=d,chain_node=i,dot_first=dot_first,dot_last=dot_last,toeplitz_build_node=tb,q_node=q)
        i=q+1
        stage_count+=1
    if stage_count!=871 or i!=366288:
        raise ValueError("STAGE_INVENTORY")
    add("COEFFICIENT_EXTRACTION_FAMILY",366288,366310,"EXACT_MASK_EXTRACTION_FAMILY",count=23)
    add("ROOT_POSTPROCESS_S23",366311,366341,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_S23")
    add("ROOT_POSTPROCESS_THETA3",366342,366342,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Theta3")
    add("ROOT_POSTPROCESS_XI23",366343,366351,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Xi23")
    add("ROOT_POSTPROCESS_OMEGA0",366352,366352,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Omega0")
    add("ROOT_POSTPROCESS_OMEGA1",366353,366353,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Omega1")
    add("ROOT_POSTPROCESS_PI",366354,366362,"ROOT_LINEAR_COMBINATION_IDENTITY",root="widehat_Pi")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cert",required=True)
    ap.add_argument("--backend",required=True)
    a=ap.parse_args()
    nodes=load_nodes(Path(a.cert))
    bpath=Path(a.backend)
    backend=json.loads(bpath.read_text(encoding="utf-8"))
    if backend.get("schema")!=EXPECTED_SCHEMA:
        raise ValueError("BACKEND_SCHEMA")
    if backend.get("input_certificate_digest")!=EXPECTED_CERT:
        raise ValueError("BACKEND_CERT_BINDING")
    exp=expected_groups(nodes)
    if backend.get("groups")!=exp:
        raise ValueError("GROUP_RECONSTRUCTION_MISMATCH")
    if backend.get("compressed_object_count")!=len(exp):
        raise ValueError("OBJECT_COUNT")
    if backend.get("stage_family_object_count")!=871:
        raise ValueError("STAGE_COUNT")
    if backend.get("branch_arity")!=24 or backend.get("branch_codes")!=list(range(24)):
        raise ValueError("BRANCH_COVERAGE")
    if len(set(backend["branch_codes"]))!=24:
        raise ValueError("BRANCH_DUPLICATE")
    if backend.get("safe_signed_width_bits")!=10996:
        raise ValueError("WIDTH_BINDING")
    if backend.get("branch_coordinate_rule")!="MIN_UNRESOLVED_COORDINATE_IN_CANONICAL_ORDER":
        raise ValueError("NONCANONICAL_BRANCH_COORDINATE_RULE")
    if backend.get("branch_value_order")!=list(range(24)):
        raise ValueError("NONCANONICAL_BRANCH_VALUE_ORDER")
    exact_true=("TRUMP_EXACT_ALGEBRA_ONLY","heuristics_forbidden","randomness_forbidden","learned_selector_forbidden","probabilistic_guidance_forbidden","approximate_pruning_forbidden","scored_ranking_forbidden")
    if any(backend.get(k) is not True for k in exact_true):
        raise ValueError("TRUMP_EXACT_ONLY_CONSTITUTION_MISSING")
    exact_false=("heuristics_present","randomness_present","learned_selector_present","probabilistic_guidance_present","approximate_pruning_present","scored_ranking_present")
    if any(backend.get(k) is not False for k in exact_false):
        raise ValueError("TRUMP_EXACT_ONLY_VIOLATION")
    if backend.get("pruning_authority")!="EXACT_REPLAYABLE_MATHEMATICAL_OR_ALGEBRAIC_DERIVATION_ONLY":
        raise ValueError("NONEXACT_PRUNING_AUTHORITY")
    if backend.get("pi_search_executed") is not False or backend.get("solver_executed") is not False:
        raise ValueError("EXECUTION_FLAG")
    cursor=0
    for x in backend["groups"]:
        if x["source_first_id"]!=cursor:
            raise ValueError("COVERAGE_GAP_OR_OVERLAP")
        cursor=x["source_last_id"]+1
    if cursor!=366363:
        raise ValueError("COVERAGE_END")
    receipt={
      "status":"PASS_COMPRESSED_BACKEND_MANIFEST_RECONSTRUCTION",
      "input_certificate_digest":EXPECTED_CERT,
      "compressed_object_count":len(exp),
      "stage_family_object_count":871,
      "source_nodes_covered":cursor,
      "branch_codes_exact":True,
      "branch_coordinate_rule_exact":True,
      "branch_value_order_exact":True,
      "TRUMP_EXACT_ALGEBRA_ONLY":True,
      "heuristics_absent":True,
      "randomness_absent":True,
      "learned_selector_absent":True,
      "probabilistic_guidance_absent":True,
      "approximate_pruning_absent":True,
      "scored_ranking_absent":True,
      "backend_sha256":sha(bpath.read_bytes())
    }
    print(json.dumps(receipt,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
