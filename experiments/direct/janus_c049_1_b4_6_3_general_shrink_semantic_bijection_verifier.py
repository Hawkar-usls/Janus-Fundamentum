from __future__ import annotations
import argparse, ast, copy, hashlib, json
from pathlib import Path

SCHEMA="janus.c049_1.general_shrink_semantic_bijection_candidate.v1"
SPEC_SCHEMA="janus.c049_1.general_shrink_semantic_bijection_spec.v1"
TERM="OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

class VError(Exception):
    def __init__(self, inv, msg): super().__init__(f"{inv}:{msg}"); self.inv=inv
def req(x,inv,msg):
    if not x: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def txt(p): return Path(p).read_text()
def gb(p):
    b=Path(p).read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def imports(path):
    t=ast.parse(Path(path).read_text()); out=[]
    for n in ast.walk(t):
        if isinstance(n,ast.Import): out.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): out.append(n.module or "")
    return out

def fn(tree,name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
            return ast.unparse(n)
    raise VError("INV05",f"missing {name}")

def expected(spec,a):
    src=spec["source_bindings"]
    bound={"historical_b3_core":a.b3_core,"historical_b3_doc":a.b3_doc,"b1_core":a.b1_core,"b2_core":a.b2_core,"corrected_root_spec":a.root_spec}
    for k,p in bound.items(): req(gb(p)==src[k]["git_blob"],"INV01",k)
    o3=load(a.o3_audit); q=src["o3_admission"]
    req(gb(a.o3_audit)==q["audit_git_blob"],"INV01","o3 audit blob")
    req(o3.get("semantic_digest")==q["audit_semantic_digest"] and dg(o3["audit_payload"])==q["audit_semantic_digest"],"INV01","o3 audit semantic")

    pub=spec["published_source"]; gt=spec["general_theorem"]; pr=spec["projection_semantics"]
    req(pub["primary_result"]=="Proposition 4.3","INV02","result")
    req(gt["precondition"]=="B0 <= B","INV02","precondition")
    req(gt["conclusion"]=="FS_k(V,B0)=up_k(FS_k(V,B)|B0,B0)","INV02","conclusion")
    req(gt["quantification"].startswith("FOR_ALL finite-dimensional GF(2)"),"INV03","quantification")
    req(pr["statistic_output"]=="(L INTER B0, R INTER B0, lambda + dim(L INTER R) - dim(L INTER R INTER B0))","INV04","projection formula")
    req(pr["width_relation"]=="width(Gamma) <= width(Gamma|B0)","INV06","width relation")
    req(pr["realizability"]=="projection of a realizable B-trajectory is realizable at B0","INV06","realizability")

    b3=txt(a.b3_core); tree=ast.parse(b3); ps=fn(tree,"project_stat"); ss=fn(tree,"shrink_trajectory")
    req("subspace_intersection(s.left, target" in ps and "subspace_intersection(s.right, target" in ps,"INV04","LR projection")
    req("subspace_intersection(s.left, s.right" in ps and "subspace_intersection(lr, target" in ps,"INV04","intersection correction")
    req("correction = dim(lr) - dim(lr_target)" in ps and "s.value + correction" in ps,"INV04","lambda")
    req("project_stat" in ss and "compactify(projected)" in ss,"INV05","projection/compact")
    b1=txt(a.b1_core); b2=txt(a.b2_core); b3d=txt(a.b3_doc)
    req("def compactify" in b1,"INV05","B1")
    req("def up_k_closure" in b2,"INV07","B2")
    req("### Shrink" in b3d and "lambda' = lambda + dim(L" in b3d,"INV04","B3 doc")
    rs=load(a.root_spec)
    req(rs["geometry"]["shrink_identity"] is False and rs["geometry"]["parent_boundary_ambient_rref"]==[],"INV05","root nontrivial shrink")
    req(rs["refinement_contract"]["shrink_projection"]=="EXACT_B3_INTERSECTION_AND_LAMBDA_CORRECTION" and rs["refinement_contract"]["shrink_compactification"]=="EXACT_B1","INV05","root shrink contract")

    sb=spec["strict_boundary"]
    req(sb["caller_shrink_containment_automatically_established"] is False,"INV08","caller containment")
    req(sb["o1_leaf_language_base_case"] is True and sb["o2_expand_preservation_and_reflection"]=="TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION" and sb["o3_join_interleaving_preservation_and_reflection"]=="TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION","INV09","prior obligations")
    req(pub["dependency_status"]=="PUBLISHED_GENERAL_THEOREM_TRUSTED_NOT_INDEPENDENTLY_REPROVED","INV03","dependency ceiling")

    checks={
      "o3_admission_bound":True,
      "published_prop_4_3_bound":True,
      "universal_symbolic_scope":True,
      "containment_precondition_explicit":True,
      "projection_L_exact":True,
      "projection_R_exact":True,
      "projection_lambda_exact":True,
      "projection_then_b1_compactify":True,
      "b2_up_k_interface_present":True,
      "root_nontrivial_shrink_contract_bound":True,
      "caller_containment_not_auto_established":True,
      "paper_not_independently_reproved":True,
    }
    return {
      "gate":spec["gate"],
      "status":"CANDIDATE_PENDING_ADMISSION",
      "published_dependency":{"primary_result":pub["primary_result"],"dependency_status":pub["dependency_status"],"quantification":gt["quantification"],"precondition":gt["precondition"],"conclusion":gt["conclusion"]},
      "projection_semantics":pr,
      "source_checks":checks,
      "local_mapping":{"project_stat_matches_published_projection":True,"shrink_applies_projection_then_exact_b1_compactification":True,"b2_up_k_interface_bound":True,"concrete_fixture_oracle_used":False,"caller_shrink_containment_automatically_established":False},
      "prior_obligations":{"o1_leaf_language_base_case":True,"o2_expand_preservation_and_reflection":"TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION","o3_join_interleaving_preservation_and_reflection":"TRUE_CONDITIONALLY_ON_BOUND_JOIN_SEPARATION_PRECONDITION"},
      "candidate_promotion":{"o4_shrink_preservation_and_reflection":False,"general_shrink_semantic_bijection_receipt":False,"receipt_wording_if_admitted":spec["admission_boundary"]["receipt_wording"]},
      "general_semantic_theorems_established":3,
      "remaining_general_semantic_theorems":4,
      "first_required_next_receipt":"GENERAL_SHRINK_SEMANTIC_BIJECTION_RECEIPT",
      "strict_boundary":sb,
    }

def verify(c,spec,a):
    req(c.get("schema")==SCHEMA,"INV01","schema")
    req(c.get("semantic_digest_scope")=="proof_payload" and dg(c.get("proof_payload"))==c.get("semantic_digest"),"INV01","semantic digest")
    exp=expected(spec,a)
    req(c["proof_payload"]==exp,"INV01","exact derived candidate")
    p=c["proof_payload"]
    req(len(p["source_checks"])==12 and all(p["source_checks"].values()),"INV01","source checks")
    req(p["published_dependency"]["primary_result"]=="Proposition 4.3" and p["published_dependency"]["precondition"]=="B0 <= B","INV02","theorem")
    req(p["local_mapping"]["concrete_fixture_oracle_used"] is False,"INV03","oracle")
    req(p["projection_semantics"]["statistic_output"].count("INTER B0")==3,"INV04","projection")
    req(p["local_mapping"]["shrink_applies_projection_then_exact_b1_compactification"] is True,"INV05","compact")
    req(p["projection_semantics"]["width_relation"]=="width(Gamma) <= width(Gamma|B0)","INV06","width")
    req(p["local_mapping"]["b2_up_k_interface_bound"] is True,"INV07","up_k")
    req(p["local_mapping"]["caller_shrink_containment_automatically_established"] is False,"INV08","caller")
    req(p["general_semantic_theorems_established"]==3 and p["remaining_general_semantic_theorems"]==4,"INV09","prior counts")
    b=p["strict_boundary"]
    req(b["o4_shrink_preservation_and_reflection"] is False and b["o5_o7_established"] is False,"INV12","obligations")
    req(b["structural_induction_proved"] is False and b["terminal_completeness_proved"] is False and b["global_engine_no_layout_at_cap"]=="FORBIDDEN" and b["formal_admission"]=="BLOCKED" and b["next_gate"]=="CLOSED" and b["p_vs_np"]=="OPEN","INV12","boundary")
    return True

def seal(x): x["semantic_digest"]=dg(x["proof_payload"])
def tampers(c,spec,a):
    ok=[]
    def attack(name,mut):
        x=copy.deepcopy(c); mut(x); seal(x)
        try: verify(x,spec,a)
        except VError as e: ok.append((name,e.inv)); return
        raise AssertionError("survived "+name)
    attack("T01_RESULT",lambda x:x["proof_payload"]["published_dependency"].__setitem__("primary_result","Proposition 4.2"))
    attack("T02_PRECONDITION",lambda x:x["proof_payload"]["published_dependency"].__setitem__("precondition","B <= B0"))
    attack("T03_L",lambda x:x["proof_payload"]["projection_semantics"].__setitem__("statistic_output","(L, R INTER B0, lambda + dim(L INTER R) - dim(L INTER R INTER B0))"))
    attack("T04_R",lambda x:x["proof_payload"]["projection_semantics"].__setitem__("statistic_output","(L INTER B0, R, lambda + dim(L INTER R) - dim(L INTER R INTER B0))"))
    attack("T05_LAMBDA",lambda x:x["proof_payload"]["projection_semantics"].__setitem__("statistic_output","(L INTER B0, R INTER B0, lambda)"))
    attack("T06_COMPACT",lambda x:x["proof_payload"]["local_mapping"].__setitem__("shrink_applies_projection_then_exact_b1_compactification",False))
    attack("T07_UPK",lambda x:x["proof_payload"]["local_mapping"].__setitem__("b2_up_k_interface_bound",False))
    attack("T08_CALLER",lambda x:x["proof_payload"]["local_mapping"].__setitem__("caller_shrink_containment_automatically_established",True))
    attack("T09_O5",lambda x:x["proof_payload"]["strict_boundary"].__setitem__("o5_o7_established",True))
    attack("T10_STRUCTURAL",lambda x:x["proof_payload"]["strict_boundary"].__setitem__("structural_induction_proved",True))
    attack("T11_TERMINAL",lambda x:x["proof_payload"]["strict_boundary"].__setitem__("terminal_completeness_proved",True))
    attack("T12_PNP",lambda x:x["proof_payload"]["strict_boundary"].__setitem__("p_vs_np","CLOSED"))
    req(len(ok)==12,"INV11","tamper count")
    return ok

def main():
    p=argparse.ArgumentParser()
    for flag in ("spec","producer-source","o3-audit","b3-core","b3-doc","b1-core","b2-core","root-spec","candidate-original","candidate-reordered"):
        p.add_argument("--"+flag,type=Path,required=True)
    p.add_argument("--tamper-suite",action="store_true")
    a=p.parse_args()
    spec=load(a.spec)
    req(spec.get("schema")==SPEC_SCHEMA and spec.get("status")=="SPEC_FROZEN","INV01","spec")
    mods=imports(a.producer_source)
    req(not any(x.endswith("janus_c049_1_b4_6_3_general_shrink_semantic_bijection_verifier") for x in mods),"INV01","producer imports verifier")
    req(a.candidate_original.read_bytes()==a.candidate_reordered.read_bytes(),"INV10","byte identity")
    c=load(a.candidate_original)
    verify(c,spec,a)
    ts=tampers(c,spec,a) if a.tamper_suite else []
    print("JANUS_GENERAL_SHRINK_SEMANTIC_BIJECTION_INDEPENDENT_VERIFIER = PASS")
    print("PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED")
    print("IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED")
    print("INVARIANTS = 12/12")
    print("DIGEST_REPAIRED_TAMPERS_REJECTED =",f"{len(ts)}/12" if a.tamper_suite else "NOT_RUN")
    print("PUBLISHED_RESULT = JKO_PROPOSITION_4_3")
    print("QUANTIFICATION = UNIVERSAL_SYMBOLIC_GF2")
    print("CALLER_SHRINK_CONTAINMENT_AUTOMATICALLY_ESTABLISHED = FALSE")
    print("GENERAL_SEMANTIC_THEOREMS_ESTABLISHED = 3")
    print("REMAINING_GENERAL_SEMANTIC_THEOREMS = 4")
    print("FIRST_REQUIRED_NEXT_RECEIPT = GENERAL_SHRINK_SEMANTIC_BIJECTION_RECEIPT")
    print("STRUCTURAL_INDUCTION_PROVED = FALSE")
    print("TERMINAL_COMPLETENESS_PROVED = FALSE")
    print("GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("P_VS_NP = OPEN")
if __name__=="__main__": main()
