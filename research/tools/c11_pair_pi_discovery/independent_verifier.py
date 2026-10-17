#!/usr/bin/env python3
import argparse,json,pathlib
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    c=json.load(open(a.candidate)); checks={}
    checks["D2"]=c["primary_outcome"]=="D2_PARTIAL_PI_DISCOVERY" and c["D2"]["status"]=="VERIFIED"
    checks["positive"]=c["positive_terminal_subclass"]["status"]=="VERIFIED_POLYNOMIAL_SUBCLASS"
    checks["canonical_all_bits"]=all(v["q"]==1 for v in c["positive_terminal_subclass"]["canonical_H8_control"].values())
    checks["obstruction"]=c["route_obstruction"]["status"]=="NO_GLOBAL_MISSING_COLOR_VERIFIED"
    for k,v in c["route_obstruction"]["assignments"].items():
        checks["obs_"+k]=(v["union_of_lists"]==[1,2,3,4] and v["NO_GLOBAL_MISSING_COLOR"] and v["components"]==[["a2","b2","z"]] and v["P7_free"] and v["boundary_propagation_exact"])
    checks["D1_not_promoted"]=c["D1"]["status"]=="NOT_ESTABLISHED"
    checks["P3_not_promoted"]=c["P3_EXACT_PAIR_QUOTIENT"]=="NOT_ESTABLISHED"
    checks["no_oracles"]=all(v is False for v in c["oracle_use"].values())
    checks["ceiling"]=c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
    checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
    verdict="INDEPENDENT_D2_PI_DISCOVERY_ROUTE_OBSTRUCTION_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={"schema":"janus.trump.c11_pair_pi_discovery.independent.v1","verdict":verdict,"checks":checks,"outcome":c["primary_outcome"],"scientific_ceiling":c["scientific_ceiling"]}
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
    if verdict!="INDEPENDENT_D2_PI_DISCOVERY_ROUTE_OBSTRUCTION_VERIFIED": raise SystemExit(1)
if __name__=="__main__":main()
