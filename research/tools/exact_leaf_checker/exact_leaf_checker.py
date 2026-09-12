import argparse, hashlib, json
from pathlib import Path

PROOF_SCHEMA="TRUMP_EXACT_PROOF_DAG_V1"
STATE_SCHEMA="TRUMP_CANONICAL_RESIDUAL_STATE_V1"
CERT="d7831123307ee6d2fc6efff231815706335b4ac794db0fb1bea204b13b8e4b74"
MANIFEST="9179ffa25c2b52707dc3c039aee3f71821637856c77dce1b1d7c477843d3ad20"
CONSTITUTION="d6b069a6e070d51573b9b84576d19d1074fc0054d8672c3a6801b1ea984d30eb"
PAIR_ORDER_COMMIT="507bd2437afc6de3a060b6fb6899454206b7fce2"

TOP_KEYS={"schema","version","certificate_digest","compressed_manifest_sha256","exact_only_constitution_sha256","pair_order_preregistration_commit","nodes","root_node_id"}
STATE_KEYS={"schema","version","certificate_digest","compressed_manifest_sha256","exact_only_constitution_sha256","assignment_vector"}
COMMON_NODE_KEYS={"node_id","type","state"}

def jcs(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def validate_state(s):
    if set(s)!=STATE_KEYS: raise ValueError("STATE_KEYS")
    if s.get("schema")!=STATE_SCHEMA or s.get("version")!="1.0": raise ValueError("STATE_SCHEMA")
    if s.get("certificate_digest")!=CERT: raise ValueError("STATE_CERT")
    if s.get("compressed_manifest_sha256")!=MANIFEST: raise ValueError("STATE_MANIFEST")
    if s.get("exact_only_constitution_sha256")!=CONSTITUTION: raise ValueError("STATE_CONSTITUTION")
    v=s.get("assignment_vector")
    if not isinstance(v,list) or len(v)!=560: raise ValueError("STATE_VECTOR_LENGTH")
    if any(type(x) is not int or x < -1 or x > 23 for x in v): raise ValueError("STATE_VALUE_DOMAIN")
    return v

def state_bytes(s):
    validate_state(s)
    return jcs(s)

def least_unresolved(v):
    for i,x in enumerate(v):
        if x == -1: return i
    return None

def lex_lt_violation(v):
    for i in range(280):
        a,b=v[i],v[280+i]
        if a == -1 or b == -1:
            return False
        if a < b:
            return False
        if a > b:
            return True
    return True

def expected_child_state(parent_state, rank, value):
    pv=validate_state(parent_state)
    if pv[rank] != -1: raise ValueError("PARENT_BRANCH_ALREADY_RESOLVED")
    nv=list(pv); nv[rank]=value
    out=dict(parent_state); out["assignment_vector"]=nv
    return out

def reject_unknown_keys(node, allowed):
    if set(node)!=allowed: raise ValueError("NODE_KEYS")

def verify_node(node, nodes, verified_unsat):
    t=node.get("type")
    if t=="UNSAT_EXACT_WORD_LEVEL_CONTRADICTION":
        reject_unknown_keys(node,COMMON_NODE_KEYS|{"derivation_kind"})
        v=validate_state(node["state"])
        if node.get("derivation_kind")!="A_LEX_LT_B_VIOLATION":
            raise ValueError("UNSUPPORTED_WORD_LEVEL_DERIVATION")
        if not lex_lt_violation(v): raise ValueError("FAKE_LEX_CONTRADICTION")
        return True
    if t=="UNSAT_EXACT_MEMOIZED_RESIDUAL_REUSE":
        reject_unknown_keys(node,COMMON_NODE_KEYS|{"target_unsat_node_id"})
        validate_state(node["state"])
        q=node.get("target_unsat_node_id")
        if type(q) is not int or q<0 or q>=node["node_id"]: raise ValueError("MEMO_TARGET_ORDER")
        if q not in verified_unsat: raise ValueError("MEMO_TARGET_NOT_VERIFIED_UNSAT")
        if state_bytes(node["state"])!=state_bytes(nodes[q]["state"]): raise ValueError("MEMO_STATE_NOT_BYTE_IDENTICAL")
        return True
    if t in {"SAT_COMPLETE_ASSIGNMENT_REPLAY","UNSAT_CERTIFIED_BOUND_CONTRADICTION"}:
        raise ValueError("LEAF_TYPE_NOT_IMPLEMENTED")
    if t=="INTERNAL_24_WAY_PARTITION":
        reject_unknown_keys(node,COMMON_NODE_KEYS|{"branch_rank","children"})
        return verify_partition(node,nodes,verified_unsat)
    raise ValueError("UNKNOWN_NODE_TYPE")

def verify_partition(node,nodes,verified_unsat):
    v=validate_state(node["state"])
    rank=least_unresolved(v)
    if rank is None: raise ValueError("PARTITION_COMPLETE_STATE")
    if node.get("branch_rank")!=rank: raise ValueError("NONMINIMAL_BRANCH_RANK")
    children=node.get("children")
    if not isinstance(children,list) or len(children)!=24: raise ValueError("CHILD_COUNT")
    for value,link in enumerate(children):
        if not isinstance(link,dict) or set(link)!={"value","node_id"}: raise ValueError("CHILD_LINK_KEYS")
        if link.get("value")!=value: raise ValueError("NONCANONICAL_CHILD_VALUE_ORDER")
        cid=link.get("node_id")
        if type(cid) is not int or cid<0 or cid>=node["node_id"]: raise ValueError("CHILD_TOPOLOGICAL_ORDER")
        if cid not in verified_unsat: raise ValueError("CHILD_NOT_VERIFIED_UNSAT")
        expected=expected_child_state(node["state"],rank,value)
        if state_bytes(nodes[cid]["state"])!=state_bytes(expected): raise ValueError("CHILD_STATE_TRANSITION")
    return True

def verify_proof(proof):
    if set(proof)!=TOP_KEYS: raise ValueError("PROOF_KEYS")
    if proof.get("schema")!=PROOF_SCHEMA or proof.get("version")!="1.0": raise ValueError("PROOF_SCHEMA")
    if proof.get("certificate_digest")!=CERT: raise ValueError("PROOF_CERT")
    if proof.get("compressed_manifest_sha256")!=MANIFEST: raise ValueError("PROOF_MANIFEST")
    if proof.get("exact_only_constitution_sha256")!=CONSTITUTION: raise ValueError("PROOF_CONSTITUTION")
    if proof.get("pair_order_preregistration_commit")!=PAIR_ORDER_COMMIT: raise ValueError("PROOF_PAIR_ORDER")
    nodes=proof.get("nodes")
    if not isinstance(nodes,list) or not nodes: raise ValueError("NODE_LIST")
    for i,n in enumerate(nodes):
        if not isinstance(n,dict) or n.get("node_id")!=i: raise ValueError("NODE_ID_ORDER")
    if proof.get("root_node_id")!=len(nodes)-1: raise ValueError("ROOT_MUST_BE_LAST")
    verified_unsat=set()
    for n in nodes:
        if verify_node(n,nodes,verified_unsat): verified_unsat.add(n["node_id"])
    root=proof["root_node_id"]
    if root not in verified_unsat: raise ValueError("ROOT_NOT_VERIFIED_UNSAT")
    return {
      "status":"PASS_SCOPED_EXACT_STATE_PARTITION_AND_MEMOIZATION_CHECKER",
      "root_verified_unsat":True,
      "node_count":len(nodes),
      "verified_unsat_node_count":len(verified_unsat),
      "implemented_leaf_types":["UNSAT_EXACT_WORD_LEVEL_CONTRADICTION:A_LEX_LT_B_VIOLATION","UNSAT_EXACT_MEMOIZED_RESIDUAL_REUSE"],
      "unimplemented_leaf_types":["SAT_COMPLETE_ASSIGNMENT_REPLAY","UNSAT_CERTIFIED_BOUND_CONTRADICTION","GENERAL_EXACT_WORD_LEVEL_ALGEBRAIC_CONTRADICTION"],
      "global_leaf_checker_pass_claimed":False
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--proof",required=True); a=ap.parse_args()
    p=Path(a.proof); proof=json.loads(p.read_text(encoding="utf-8"))
    receipt=verify_proof(proof); receipt["proof_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps(receipt,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
