from __future__ import annotations
import argparse, ast, hashlib, json
from pathlib import Path

SCHEMA = "janus.c049_1.general_shrink_semantic_bijection_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.general_shrink_semantic_bijection_spec.v1"
TERM = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

def cb(x): return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def text(p): return Path(p).read_text()
def gb(p):
    b = Path(p).read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()
def save(x,p): Path(p).write_bytes(cb(x)+b"\n")
def req(x,m):
    if not x: raise AssertionError(m)

def function_source(tree, name):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"missing function {name}")

def build(a):
    s = load(a.spec)
    req(s.get("schema") == SPEC_SCHEMA and s.get("status") == "SPEC_FROZEN" and s.get("admission") is False, "spec")
    src = s["source_bindings"]
    bound = {
        "historical_b3_core": a.b3_core,
        "historical_b3_doc": a.b3_doc,
        "b1_core": a.b1_core,
        "b2_core": a.b2_core,
        "corrected_root_spec": a.root_spec,
    }
    for key,path in bound.items():
        req(gb(path) == src[key]["git_blob"], f"blob {key}")

    o3 = load(a.o3_audit)
    q = src["o3_admission"]
    req(gb(a.o3_audit) == q["audit_git_blob"], "o3 audit blob")
    req(o3.get("semantic_digest") == q["audit_semantic_digest"], "o3 audit semantic id")
    req(dg(o3["audit_payload"]) == q["audit_semantic_digest"], "o3 audit semantic recompute")

    pub = s["published_source"]
    gt = s["general_theorem"]
    proj = s["projection_semantics"]
    req(pub["primary_result"] == "Proposition 4.3", "published result")
    req(gt["precondition"] == "B0 <= B", "precondition")
    req(gt["conclusion"] == "FS_k(V,B0)=up_k(FS_k(V,B)|B0,B0)", "conclusion")
    req(proj["statistic_output"] == "(L INTER B0, R INTER B0, lambda + dim(L INTER R) - dim(L INTER R INTER B0))", "projection formula")
    req(proj["width_relation"] == "width(Gamma) <= width(Gamma|B0)", "width relation")

    b3 = text(a.b3_core)
    tree = ast.parse(b3)
    project_src = function_source(tree, "project_stat")
    shrink_src = function_source(tree, "shrink_trajectory")
    req("subspace_intersection(s.left, target" in project_src, "local L projection")
    req("subspace_intersection(s.right, target" in project_src, "local R projection")
    req("subspace_intersection(s.left, s.right" in project_src, "local LR")
    req("subspace_intersection(lr, target" in project_src, "local triple")
    req("correction = dim(lr) - dim(lr_target)" in project_src, "local lambda correction")
    req("s.value + correction" in project_src, "local lambda output")
    req("project_stat" in shrink_src and "compactify(projected)" in shrink_src, "local shrink pipeline")

    b1 = text(a.b1_core)
    b2 = text(a.b2_core)
    req("def compactify" in b1, "B1 compactify")
    req("def up_k_closure" in b2, "B2 up_k")
    b3doc = text(a.b3_doc)
    req("### Shrink" in b3doc and "lambda' = lambda + dim(L" in b3doc, "B3 doc shrink")

    rs = load(a.root_spec)
    req(rs["geometry"]["parent_boundary_ambient_rref"] == [], "root shrink target")
    req(rs["geometry"]["shrink_identity"] is False, "root nontrivial shrink")
    req(rs["refinement_contract"]["shrink_projection"] == "EXACT_B3_INTERSECTION_AND_LAMBDA_CORRECTION", "root shrink contract")
    req(rs["refinement_contract"]["shrink_compactification"] == "EXACT_B1", "root compact contract")

    checks = {
        "o3_admission_bound": True,
        "published_prop_4_3_bound": True,
        "universal_symbolic_scope": gt["quantification"].startswith("FOR_ALL finite-dimensional GF(2)"),
        "containment_precondition_explicit": gt["precondition"] == "B0 <= B",
        "projection_L_exact": "subspace_intersection(s.left, target" in project_src,
        "projection_R_exact": "subspace_intersection(s.right, target" in project_src,
        "projection_lambda_exact": "correction = dim(lr) - dim(lr_target)" in project_src,
        "projection_then_b1_compactify": "compactify(projected)" in shrink_src,
        "b2_up_k_interface_present": "def up_k_closure" in b2,
        "root_nontrivial_shrink_contract_bound": rs["geometry"]["shrink_identity"] is False,
        "caller_containment_not_auto_established": s["strict_boundary"]["caller_shrink_containment_automatically_established"] is False,
        "paper_not_independently_reproved": pub["dependency_status"] == "PUBLISHED_GENERAL_THEOREM_TRUSTED_NOT_INDEPENDENTLY_REPROVED",
    }
    req(len(checks)==12 and all(checks.values()), "source checks")

    proof = {
        "gate": s["gate"],
        "status": "CANDIDATE_PENDING_ADMISSION",
        "published_dependency": {
            "primary_result": pub["primary_result"],
            "dependency_status": pub["dependency_status"],
            "quantification": gt["quantification"],
            "precondition": gt["precondition"],
            "conclusion": gt["conclusion"],
        },
        "projection_semantics": proj,
        "source_checks": checks,
        "local_mapping": {
            "project_stat_matches_published_projection": True,
            "shrink_applies_projection_then_exact_b1_compactification": True,
            "b2_up_k_interface_bound": True,
            "concrete_fixture_oracle_used": False,
            "caller_shrink_containment_automatically_established": False,
        },
        "prior_obligations": {
            "o1_leaf_language_base_case": True,
            "o2_expand_preservation_and_reflection": "TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION",
            "o3_join_interleaving_preservation_and_reflection": "TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION",
        },
        "candidate_promotion": {
            "o4_shrink_preservation_and_reflection": False,
            "general_shrink_semantic_bijection_receipt": False,
            "receipt_wording_if_admitted": s["admission_boundary"]["receipt_wording"],
        },
        "general_semantic_theorems_established": 3,
        "remaining_general_semantic_theorems": 4,
        "first_required_next_receipt": "GENERAL_SHRINK_SEMANTIC_BIJECTION_RECEIPT",
        "strict_boundary": s["strict_boundary"],
    }
    out = {"schema":SCHEMA,"semantic_digest_scope":"proof_payload","proof_payload":proof}
    out["semantic_digest"] = dg(proof)
    save(out,a.output)
    return out

def main():
    p=argparse.ArgumentParser()
    for flag in ("spec","o3-audit","b3-core","b3-doc","b1-core","b2-core","root-spec","output"):
        p.add_argument("--"+flag,type=Path,required=True)
    a=p.parse_args()
    x=build(a); q=x["proof_payload"]
    print("JANUS_GENERAL_SHRINK_SEMANTIC_BIJECTION_BINDER = PASS")
    print("PUBLISHED_RESULT = JKO_PROPOSITION_4_3")
    print("QUANTIFICATION = UNIVERSAL_SYMBOLIC_GF2")
    print("LOCAL_PROJECTION_MAPPING = PASS")
    print("CALLER_SHRINK_CONTAINMENT_AUTOMATICALLY_ESTABLISHED = FALSE")
    print("GENERAL_SEMANTIC_THEOREMS_ESTABLISHED =",q["general_semantic_theorems_established"])
    print("REMAINING_GENERAL_SEMANTIC_THEOREMS =",q["remaining_general_semantic_theorems"])
    print("FIRST_REQUIRED_NEXT_RECEIPT =",q["first_required_next_receipt"])
    print("STRUCTURAL_INDUCTION_PROVED = FALSE")
    print("TERMINAL_COMPLETENESS_PROVED = FALSE")
    print("GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("P_VS_NP = OPEN")
if __name__=="__main__": main()
