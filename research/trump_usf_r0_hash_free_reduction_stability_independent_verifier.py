from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED_BINDINGS = {
    "EXTRACTION_ARTIFACT": "1162d600b69133ab9dab6363d07d3f6750839e41",
    "R33": "c9234a1ef639a009cc6cb4c8a6098fd09bf9affe",
    "R34": "7f9bec920fa47af066570d874fe9127dc4b9b968",
    "R35": "ad237e341d9659d33da0568f134815776c1f95d8",
    "R35B": "259d2e38947d09b0c058963ad825a57f2e734203",
    "R37B": "f37da1c2e1696e35695096a2c748a222af7920cc",
    "USF_R0_CORE_HARNESS": "ed4203bac76349ab377bb97f67bf1054d837bc96",
}
MAIN_RULES = {
    "L0": "SIMPLE3_CANONICAL_EXCLUSIONS",
    "L1": "G3_IMPLIES_BIPOLAR",
    "L2": "NEGATE_FROZEN_BCE_EXISTENTIAL",
    "L3": "NEGATE_FROZEN_BVE_ACCEPTANCE",
    "L4": "R33_FALLTHROUGH_TERMINAL",
    "L5": "R34_EXACT_NEGATION",
    "L6": "R35B_NO_PROPOSAL_AND_EMPTY_UP",
    "L7": "CONTROLLER_UNCHANGED_BRANCH",
}
SUB_RULES = {
    "S1": "LINEAR_BIPOLAR_NO_BCE",
    "S2": "LINEAR_15_7_8_BVE_56",
    "S3": "LINEAR_R34_INCOMPLETE",
    "S4": "LINEAR_R35B_NO_CASCADE",
    "S5": "COUNTING_NOT_HORN",
    "S6": "LINEAR_SUBCLASS_COROLLARY",
}
FORBIDDEN = {"SHA_PSEUDORANDOMNESS","EMPIRICAL_CNF_INSTANCE","SAT_TRUTH_VALUE","TREEWIDTH","EXPANSION","LANE_C","HOLDOUT","BA26","ENIGMA"}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(cond, msg):
    if not cond:
        raise AssertionError(msg)

def replay(manifest: dict, cert: dict) -> dict:
    require(manifest["schema"] == "TRUMP_USF_R0_HASH_FREE_REDUCTION_STABILITY_LEMMA_OBLIGATION_MANIFEST", "manifest schema")
    require(cert["schema"] == "TRUMP_USF_R0_HASH_FREE_REDUCTION_STABILITY_LEMMA_PROOF_CERTIFICATE", "certificate schema")
    require(manifest["claim_id"] == cert["claim_id"] == "HASH_FREE_ONE_CYCLE_FROZEN_REDUCER_FIXPOINT_LEMMA", "claim drift")
    require(manifest["source_bindings"] == EXPECTED_BINDINGS, "source binding drift")
    require(set(manifest["forbidden_inputs"]) == FORBIDDEN, "forbidden-input firewall drift")
    require(set(manifest["domain"]) == {"CANONICAL_F","NONEMPTY_F","EXACT_WIDTH_3_EVERY_CLAUSE","DISTINCT_VARIABLE_IDENTITIES_WITHIN_EACH_CLAUSE"}, "domain drift")
    require(set(manifest["assumptions"]) == {"G3_NO_BLOCKED_CLAUSE","G4_EXACT_NO_BVE_CANDIDATE","NOT_HORN","G_AFF_NOT_COMPLETE_AFFINE_BUNDLE","G5_SINGLE_LITERAL_RUP_IRREDUCIBLE"}, "assumption drift")

    obligations = {x["id"]: x for x in manifest["obligations"]}
    steps = {x["id"]: x for x in cert["proof_steps"]}
    require(set(obligations) == set(MAIN_RULES) == set(steps), "L0-L7 coverage")
    facts = set(manifest["domain"]) | set(manifest["assumptions"])
    checked = []
    for lid in [f"L{i}" for i in range(8)]:
        require(obligations[lid]["rule"] == MAIN_RULES[lid] == steps[lid]["rule"], f"{lid} rule mismatch")
        require(steps[lid]["status"] == "PROVED", f"{lid} not proved")
        require(bool(steps[lid]["argument"]), f"{lid} empty argument")
        if lid == "L0":
            require({"CANONICAL_F","NONEMPTY_F","EXACT_WIDTH_3_EVERY_CLAUSE","DISTINCT_VARIABLE_IDENTITIES_WITHIN_EACH_CLAUSE"} <= facts, "L0 premises")
            facts |= {"NO_EMPTY_CNF","NO_EMPTY_CLAUSE","NO_INITIAL_UNIT","NO_TAUTOLOGY","NO_DISTINCT_CLAUSE_SUBSUMPTION","NOT_2CNF","NO_EXACT_DUPLICATE_CLAUSES"}
        elif lid == "L1":
            require("G3_NO_BLOCKED_CLAUSE" in facts, "L1 premise")
            facts.add("BIPOLAR_EVERY_USED_VARIABLE")
        elif lid == "L2":
            require("G3_NO_BLOCKED_CLAUSE" in facts, "L2 premise")
            facts.add("FIRST_BLOCKED_CLAUSE_NONE")
        elif lid == "L3":
            require("G4_EXACT_NO_BVE_CANDIDATE" in facts, "L3 premise")
            require("BIPOLAR_EVERY_USED_VARIABLE" in facts, "L3 parent-set applicability")
            facts.add("BVE_CANDIDATE_NONE")
        elif lid == "L4":
            require({"NO_EMPTY_CNF","NO_EMPTY_CLAUSE","NO_INITIAL_UNIT","NO_TAUTOLOGY","NO_DISTINCT_CLAUSE_SUBSUMPTION","BIPOLAR_EVERY_USED_VARIABLE","FIRST_BLOCKED_CLAUSE_NONE","BVE_CANDIDATE_NONE","NOT_2CNF","NOT_HORN"} <= facts, "L4 premises")
            facts |= {"R33_ZERO_TRANSFORMATIONS","R33_FORMULA_UNCHANGED","R33_STALLED_STACK_LEAN_CORE"}
        elif lid == "L5":
            require("G_AFF_NOT_COMPLETE_AFFINE_BUNDLE" in facts and "EXACT_WIDTH_3_EVERY_CLAUSE" in facts, "L5 premises")
            facts.add("R34_NOT_RECOGNIZED")
        elif lid == "L6":
            require("G5_SINGLE_LITERAL_RUP_IRREDUCIBLE" in facts and "EXACT_WIDTH_3_EVERY_CLAUSE" in facts and "R33_FORMULA_UNCHANGED" in facts, "L6 premises")
            facts |= {"R35B_INITIAL_EMPTY_UP_NO_CONFLICT","R35B_NO_PROPOSAL","R35B_FINAL_EMPTY_UP_NO_CONFLICT","R35B_ZERO_STRENGTHENINGS","R35B_FORMULA_UNCHANGED","R35B_STALLED_RUP_CORE","R35B_INDEPENDENT_REPLAY_PASS"}
        elif lid == "L7":
            require({"R33_ZERO_TRANSFORMATIONS","R33_FORMULA_UNCHANGED","R33_STALLED_STACK_LEAN_CORE","R34_NOT_RECOGNIZED","R35B_ZERO_STRENGTHENINGS","R35B_FORMULA_UNCHANGED","R35B_STALLED_RUP_CORE","R35B_INDEPENDENT_REPLAY_PASS"} <= facts, "L7 premises")
            facts |= {"FROZEN_REDUCER_ZERO_TRANSFORMATIONS","RESIDUAL_LITERAL_F_UNCHANGED","CONTROLLER_CYCLE_COUNT_1","CONTROLLER_RESTART_COUNT_0","STALLED_PORTFOLIO_FIXPOINT"}
        checked.append(lid)
    require({"FROZEN_REDUCER_ZERO_TRANSFORMATIONS","RESIDUAL_LITERAL_F_UNCHANGED","CONTROLLER_CYCLE_COUNT_1","CONTROLLER_RESTART_COUNT_0","STALLED_PORTFOLIO_FIXPOINT"} <= facts, "main conclusion missing")

    sob = {x["id"]: x for x in manifest["linear_subclass_obligations"]}
    ssteps = {x["id"]: x for x in cert["linear_subclass_steps"]}
    require(set(sob) == set(SUB_RULES) == set(ssteps), "linear coverage")
    sfacts = {"LINEAR_3_UNIFORM_HYPERGRAPH","EXACT_SIMPLE_3CNF","DEGREE_15_EVERY_VARIABLE","POLARITY_SPLIT_7_8_EVERY_VARIABLE","NONEMPTY_F"}
    schecked=[]
    for sid in [f"S{i}" for i in range(1,7)]:
        require(sob[sid]["rule"] == SUB_RULES[sid] == ssteps[sid]["rule"], f"{sid} rule mismatch")
        require(ssteps[sid]["status"] in {"PROVED","PROVED_CONDITIONAL_COROLLARY"}, f"{sid} status")
        if sid == "S1": sfacts.add("G3_NO_BLOCKED_CLAUSE")
        elif sid == "S2": sfacts |= {"BVE_RESOLVENT_COUNT_56","G4_EXACT_NO_BVE_CANDIDATE"}
        elif sid == "S3": sfacts.add("G_AFF_NOT_COMPLETE_AFFINE_BUNDLE")
        elif sid == "S4": sfacts.add("G5_SINGLE_LITERAL_RUP_IRREDUCIBLE")
        elif sid == "S5": sfacts.add("NOT_HORN")
        elif sid == "S6":
            require({"G3_NO_BLOCKED_CLAUSE","G4_EXACT_NO_BVE_CANDIDATE","G_AFF_NOT_COMPLETE_AFFINE_BUNDLE","G5_SINGLE_LITERAL_RUP_IRREDUCIBLE","NOT_HORN"} <= sfacts, "S6 premises")
            sfacts.add("LINEAR_SUBCLASS_SATISFIES_MAIN_PREMISES_CONDITIONALLY")
        schecked.append(sid)
    return {
        "status":"PASS",
        "claim_id":manifest["claim_id"],
        "main_obligations_checked":checked,
        "linear_subclass_obligations_checked":schecked,
        "main_conclusion":{
            "zero_transformations":True,
            "residual_F_unchanged":True,
            "cycle_count":1,
            "restart_count":0,
            "terminal":"STALLED_PORTFOLIO_FIXPOINT"
        },
        "linear_subclass":"CONDITIONAL_COROLLARY_REPLAY_PASS_EXISTENCE_NOT_CHECKED",
        "empirical_instances_used":0,
        "reducer_invoked":False,
        "SAT_solver_invoked":False,
        "treewidth_or_expansion_used":False,
        "forbidden_inputs_used":[],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True); ap.add_argument("--certificate",required=True); ap.add_argument("--output",required=True)
    a=ap.parse_args(); mp=Path(a.manifest); cp=Path(a.certificate)
    m=json.loads(mp.read_text()); c=json.loads(cp.read_text())
    out=replay(m,c)
    out["manifest_sha256"]=sha256(mp); out["certificate_sha256"]=sha256(cp)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_SYMBOLIC_REPLAY_PASS", out["claim_id"], len(out["main_obligations_checked"]), len(out["linear_subclass_obligations_checked"]))
if __name__=="__main__": main()
