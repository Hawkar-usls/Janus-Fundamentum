#!/usr/bin/env python3
import argparse, itertools, json, pathlib

def ce(a,b): return tuple(sorted((str(a),str(b))))
def edges(o): return {ce(a,b) for a,b in o["edges"]}
def has(o,a,b): return ce(a,b) in edges(o)
def nbr(o,v): return {u for u in o["vertices"] if u!=v and has(o,u,v)}
def proper(o,c):
    return all(c[a]!=c[b] for a,b in edges(o))
def induced_path(o,seq):
    if len(set(seq))!=len(seq): return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if has(o,a,seq[j]) != (j==i+1): return False
    return True

def no_induced_p6(o):
    if len(o["vertices"])<6:return True
    return not any(induced_path(o,p) for p in itertools.permutations(o["vertices"],6))

def check_axioms(o):
    V=set(o["vertices"]); S=set(o["S"]); X0=set(o["X0"]); X=set(o["X"]); Y0=set(o["Y0"]); Y=set(o["Y"])
    parts=[S,X0,X,Y0,Y]
    if set().union(*parts)!=V or sum(map(len,parts))!=len(V): return False,"partition"
    # connectivity of G\X0 and S
    def conn(A):
        A=set(A)
        if not A:return False
        seen=set(); stack=[next(iter(A))]
        while stack:
            v=stack.pop()
            if v in seen:continue
            seen.add(v); stack.extend((nbr(o,v)&A)-seen)
        return seen==A
    if not conn(V-X0):return False,"i"
    if not conn(S):return False,"ii_conn"
    if any(S <= nbr(o,v) for v in V-S):return False,"ii_complete"
    NS=set().union(*(nbr(o,s) for s in S))-S
    if Y0 != V-(NS|X0|S):return False,"iii"
    for a,b in edges(o):
        if a in Y0 and b in Y0:
            for v in V-(Y0|X0):
                if has(o,v,a)!=has(o,v,b):return False,"iv"
    f=o["f"]
    for v in V-S:
        if v in X0: size=1
        else:
            used={f[s] for s in nbr(o,v)&S}
            size=4-len(used)
        expected={1:X0,2:X,3:Y,4:Y0}[size]
        if v not in expected:return False,"v"
    return True,"ok"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("run_dir"); ap.add_argument("output")
    args=ap.parse_args(); root=pathlib.Path(args.run_dir)
    fixture=json.loads((root/"PROBE_GLOBAL_INTERACTION_3TYPE.fixture.json").read_text())
    receipt=json.loads((root/"PROBE_GLOBAL_INTERACTION_3TYPE.receipt.json").read_text())
    summary=json.loads((root/"summary.json").read_text())
    checks={}
    ok,why=check_axioms(fixture)
    checks["input_axioms_i_v"]=ok
    checks["input_axiom_detail"]=why
    checks["extension_c_proper"]=proper(fixture,fixture["c"])
    checks["P7_free_trivial_n_lt_7"]=len(fixture["vertices"])<7
    checks["also_P6_free_by_exhaustive_order_search"]=no_induced_p6(fixture)

    # Independently verify the two local legacy decisions sufficient for the collision.
    # T_U={s1}, T_A={s2}, T_W={s3}.
    v="v"; n="n"; z="z"
    # Pair (U,W): bad pair with common z -> legacy 111.
    checks["UW_bad_pair_nonadjacent"]=not has(fixture,v,n)
    checks["UW_endpoint_colors_outside_seed_colors"]=(fixture["c"][v] not in {1,3} and fixture["c"][n] not in {1,3})
    checks["UW_common_z"]=has(fixture,v,z) and has(fixture,n,z) and z in fixture["Y0"]
    # Pair (A,U): no A-side Y vertex; U-side v has c(v)=f(A)=2 -> legacy 000.
    A_type_vertices=[x for x in fixture["Y"] if (nbr(fixture,x)&set(fixture["S"]))=={"s2"}]
    U_type_vertices=[x for x in fixture["Y"] if (nbr(fixture,x)&set(fixture["S"]))=={"s1"}]
    checks["AU_no_left_endpoint"]=A_type_vertices==[]
    checks["AU_right_vertices_all_color_fA"]=all(fixture["c"][x]==2 for x in U_type_vertices if any(has(fixture,x,y0) for y0 in fixture["Y0"]))
    legacy111_support={v,z,n}
    legacy000_Z=set(U_type_vertices)
    collision=legacy111_support&legacy000_Z
    checks["independent_support_Z_collision"]=collision=={"v"}
    observed=receipt.get("verdict")
    checks["raw_universal_not_promoted"]=summary.get("raw_equivalence_universal") is False
    checks["subgate_A_open"]=summary.get("subgate_A")=="OPEN"

    if observed=="FAIL_SUPPORT_Z_COLLISION":
        checks["candidate_failure_code"]=True
        checks["candidate_collision_same"]=set(receipt.get("witness",{}).get("detail",{}).get("collision",[]))=={"v"}
        checks["scientific_gate_matches_fail"]=summary.get("scientific_gate")=="FAIL_RAW_REPRESENTATIVE_COVERAGE"
        authority_checks={k:v for k,v in checks.items() if isinstance(v,bool)}
        verdict="INDEPENDENT_FAIL_WITNESS_VERIFIED" if all(authority_checks.values()) else "INDEPENDENT_REPLAY_FAIL"
        interpretation={
          "RIGID_SPLIT4_LOCAL_SCHEMA":"NOT_FALSIFIED_BY_THIS_WITNESS",
          "RAW_GLOBAL_REPRESENTATIVE_COVERAGE":"FALSIFIED_UNDER_LITERAL_CONSTRUCTOR",
          "PAPER_II_THEOREM_INVALID":"NOT_CLAIMED",
          "SOURCE_INTERPRETATION_OR_IMPLICIT_NORMALIZATION":"REQUIRES_REVIEW",
          "SUBGATE_A":"OPEN","P_VS_NP":"OPEN"
        }
    elif observed=="RAW_EQUIVALENCE_WITNESS_PASS":
        checks["candidate_pass_code"]=True
        checks["independent_no_support_Z_collision"]=len(collision)==0
        checks["scientific_gate_matches_finite_pass"]=summary.get("scientific_gate")=="FINITE_REPLAY_PASS__UNIVERSAL_AUTHORITY_NOT_ESTABLISHED"
        authority_checks={k:v for k,v in checks.items() if isinstance(v,bool)}
        verdict="INDEPENDENT_FINITE_PASS_REPLAY" if all(authority_checks.values()) else "INDEPENDENT_REPLAY_FAIL"
        interpretation={
          "RAW_GLOBAL_REPRESENTATIVE_COVERAGE":"FINITE_REPLAY_ONLY",
          "UNIVERSAL_RAW_EQUIVALENCE":"NOT_ESTABLISHED",
          "SUBGATE_A":"OPEN","P_VS_NP":"OPEN"
        }
    else:
        verdict="INDEPENDENT_REPLAY_FAIL"
        interpretation={"unexpected_candidate_verdict":observed}

    out={"schema":"janus.trump.p7_split4.raw_coverage_independent.v1",
         "verdict":verdict,"checks":checks,
         "witness":{
           "vertices":fixture["vertices"],"edges":fixture["edges"],
           "support_from_pair_UW":sorted(legacy111_support),
           "Z_from_pair_AU":sorted(legacy000_Z),
           "collision":sorted(collision)
         },
         "interpretation_ceiling":interpretation}
    pathlib.Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"collision":sorted(collision)},sort_keys=True))
    if verdict=="INDEPENDENT_REPLAY_FAIL": raise SystemExit(1)

if __name__=="__main__": main()
