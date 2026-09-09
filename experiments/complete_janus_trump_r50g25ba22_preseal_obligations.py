from __future__ import annotations
import argparse,json
from pathlib import Path
PREREG="214ad418951a2dfa51ece4f27f4965e2b088522a"
EXPECTED=[
"STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","BA21_IMMUTABILITY_PASS",
"BARE_DBO_NONCLOSURE_PASS","XOR_COUNTEREXAMPLE_PASS","DGDBO_DEFINITION_PASS",
"CLAUSE_CANONICALIZATION_PASS","FIRST_TRUE_PARTITION_PASS","GUARD_DISJOINTNESS_PASS",
"BA21_RESTRICTION_APPLICABILITY_PASS","GENERIC_SINGLE_CLAUSE_CLOSURE_PASS",
"MIXED_POLARITY_PASS","CROSS_BLOCK_PASS","SAME_BLOCK_PASS","NO_PRIME_MATERIALIZATION_PASS",
"COMPACT_SIZE_PASS","CONSTRUCTION_COMPLEXITY_PASS","EXACT_MODEL_COUNT_PASS",
"DGDBO_RESTRICTION_CLOSURE_PASS","PROJECTED_SAT_PASS","PROJECTED_WITNESS_PASS",
"SOURCE_RECONSTRUCTION_PASS","FULL_ORIGINAL_SOURCE_VALIDATION_PASS",
"LARGE_DEPTH_NO_EXPANSION_PASS","MULTI_CLAUSE_NONCLAIM_PASS","INDEPENDENT_REPLAY_PASS",
"PRESEAL_COMPLETENESS_PASS"]
def main(prereg_path,result_path,verify_path,out_path):
    P=json.loads(Path(prereg_path).read_text());R=json.loads(Path(result_path).read_text());V=json.loads(Path(verify_path).read_text());errors=[]
    def ck(x,m):
        if not x:errors.append(m)
    ck(P["state"]=="FROZEN_BEFORE_IMPLEMENTATION","prereg state")
    ck(P["required_pass_count"]==27 and P["required_pass_names"]==EXPECTED and len(set(EXPECTED))==27,"prereg exact names")
    ck(R["preregistration_commit"]==PREREG,"prereg commit")
    ck(R["required_pass_names"]==EXPECTED and set(R["obligations"])==set(EXPECTED),"result exact names")
    for k in EXPECTED[:-2]:ck(R["obligations"][k]==1,"base "+k)
    ck(R["obligations"]["INDEPENDENT_REPLAY_PASS"]==0,"independent pending")
    ck(R["obligations"]["PRESEAL_COMPLETENESS_PASS"]==0,"preseal pending")
    ck(V["status"]=="PASS" and V["P_BA22"]==1 and V["implementation_imported"] is False and not V["errors"],"independent verifier")
    ck(R["no_materialization"]["PRIME_IMPLICATE_RECORDS"]==0 and R["no_materialization"]["CARTESIAN_BA20_TUPLES"]==0 and not R["no_materialization"]["EXPAND_BA20_CNF"],"no materialization")
    ck(R["historical_immutability"]["BA21"]=="SEALED_AND_UNCHANGED","BA21 immutability")
    ck(R["firewall"]["single_clause_closure_ne_arbitrary_CNF_closure"] is True,"multi-clause firewall")
    status="PASS" if not errors else "FAIL";final={k:1 for k in EXPECTED} if status=="PASS" else {}
    out={"gate":"R50G25BA22_PRESEAL_COMPLETION","kind":"EXACT_PREREG_NAME_AUDIT","status":status,"errors":errors,"required_pass_names":EXPECTED,"required_pass_count":27,"required_passes":final,"all_required_passes":status=="PASS","P_BA22_FINAL":1 if status=="PASS" else 0,"BA21_immutable":True,"BA20_lower_bound_preserved":True,"single_clause_ne_arbitrary_CNF":True,"CI_GREEN_NE_SCIENTIFIC_SEAL":True}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("; ".join(errors))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--prereg",required=True);ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.prereg,a.result,a.verify,a.out)
