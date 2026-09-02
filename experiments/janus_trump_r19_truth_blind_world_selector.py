#!/usr/bin/env python3
"""R19 fresh structural unseen selector. No truth or candidate access."""
from __future__ import annotations
import argparse,hashlib,inspect,json,random
from pathlib import Path
import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9

PARENT="a7531cda15cf59fcf1e48aabc8938a4b3f1438b5"
REPLICATES=32
CELLS=tuple((suite,n) for n in (24,32,40,48,56) for suite in ("PLANTED","UNSAT_CORE"))
EXPOSED={
"3777d9c56dae0be077e2141cb4821250f582261812235647528c5cc5a21462b8","9f03fef66a0b9e4968851ed72d4f51bdf8abdac400c0b81f48d4f0d5c1844cf6","fbb0eb0160ed4d4e3c4e1b645471c0cc611ea9a22f776cc97ea9e0d28a0af747","f3b380ed8e0d288079a1e6652c31be5588b71a4bf20a208d17fe03d1da8e08b7","84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88","49ae562a287b2ab6c92152d5fe61a0d1a0faeee23c9cb8e27a881ef01745e98b",
"1c9a589f5b830a5863ecec2d104d4a041f5207e10a3ea4dd81656a4f9062071c","00f3191f14905031fafc087d6c169bc36c8605abfdddc3c7d7a336744e73799e","053688f5c82eb94e294e03ff1af78c4abc69195d6fca7638e6c531054fb5cdac","13ba661067d7bdc389eeff233fc10318ad1e584ecf0d101b9071a3d21cb8ac21","1b21e911ee69fbcdaadbc325eb6a78a6dfaa0c87201a425f502cd7caa1bc8a06","179920edae423db6f588ad74ef259e09d965026dd9d0cb08ccd93ec4a445f591","1093568a55ccfd4991b48002489ce564d3754cf406c361193ef22363b576bce1","1298d8cbbba127ec91d3f004600e9c40b8a49f243c74212d71150ad219ce0fbe"}

def derive_spec(suite,n,rep):
    s=f"R19|R18B={PARENT}|suite={suite}|n={n}|rep={rep}"; d=hashlib.sha256(s.encode()).digest()
    return {"suite":suite,"n":int(n),"m":round(4.26*int(n)),"k":3,"rep":int(rep),"derivation_string":s,"seed":int.from_bytes(d[:8],"big")%(2**31),"branch_value":bool(d[8]&1)}

def structural_world(spec):
    sat=r8a.load_legacy_sat_core(); rng=random.Random(spec["seed"])
    inst=sat.gen_planted(spec["n"],spec["m"],3,rng) if spec["suite"]=="PLANTED" else sat.gen_unsat_core(spec["n"],spec["m"],3,rng)
    root=direct.canon(inst.clauses); order,_=direct.occurrence_order(root)
    if not order:return {**spec,"eligible":False,"reason":"NO_PIVOT"}
    pivot=int(order[0]); fd=r9.restriction_frame_delta(root,pivot,spec["branch_value"]); frame=tuple(fd["frame"]); bridge=tuple(fd["active_bridge_vars"])
    ftype=r9.classify_cnf(frame); fh=fd["frame_sha256"]; eligible=ftype=="GENERAL_CNF" and 6<=len(bridge)<=16 and fh not in EXPOSED
    return {**spec,"eligible":eligible,"reason":"ELIGIBLE" if eligible else "STRUCTURAL_FILTER","root_sha256":r8a.digest(root),"pivot":pivot,"frame_sha256":fh,"frame_type":ftype,"frame_variable_count":len({abs(l) for c in frame for l in c}),"frame_clause_count":len(frame),"bridge_vars":list(bridge),"bridge_variable_count":len(bridge),"delta_sha256":fd["delta_sha256"]}

def selector_firewall():
    src="\n".join(inspect.getsource(f) for f in (derive_spec,structural_world,select_worlds)); banned=["dpll(","Solver(","candidate_compile(","shadow_exact_interface","allowed_masks","truth_table"]
    hits=[x for x in banned if x in src]; return {"pass":not hits,"forbidden_hits":hits}

def select_worlds():
    chosen=[]; audit=[]; blocked=[]
    for idx,(suite,n) in enumerate(CELLS,start=1):
        pool=[structural_world(derive_spec(suite,n,r)) for r in range(REPLICATES)]; elig=sorted([x for x in pool if x["eligible"]],key=lambda x:(x["frame_sha256"],x["seed"],x["branch_value"]))
        a={"suite":suite,"n":n,"pool_size":len(pool),"eligible_count":len(elig),"eligible_bridge_sizes":sorted({x["bridge_variable_count"] for x in elig})}
        if not elig: blocked.append({"suite":suite,"n":n,"reason":"NO_ELIGIBLE_WORLD"}); audit.append(a); continue
        w=dict(elig[0]); w["id"]=f"R19-W{idx:02d}"; w.pop("eligible",None); w.pop("reason",None); chosen.append(w); a.update({"selected_id":w["id"],"selected_frame_sha256":w["frame_sha256"],"selected_bridge_size":w["bridge_variable_count"]}); audit.append(a)
    fw=selector_firewall(); fresh=len({w["frame_sha256"] for w in chosen})==len(chosen) and all(w["frame_sha256"] not in EXPOSED for w in chosen)
    status="SELECTOR_PASS" if len(chosen)==len(CELLS) and not blocked and fw["pass"] and fresh else "SELECTOR_BLOCKED"
    return {"schema":"JANUS/TRUMP/R19/FRESH_PROSPECTIVE_UNSEEN_SHANNON_DAG_HOLDOUT/WORLD_SELECTION_RESULT/v1.0","created_date":"2026-09-02","status":status,"parent_R18B_result_summary_commit":PARENT,"selector_firewall":fw,"selected_world_count":len(chosen),"selected_worlds":chosen,"cell_audit":audit,"blocked_cells":blocked,"freshness_pass":fresh,"truth_accessed":False,"candidate_accessed":False,"seal":"THE_NEW_BATTLEFIELD_WAS_PICKED_BEFORE_THE_HERO_OR_THE_JUDGE_ENTERED","P_VS_NP":"OPEN"}

def main():
    a=argparse.ArgumentParser();a.add_argument('--output',required=True);z=a.parse_args();out=select_worlds();Path(z.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"selected_world_count":out["selected_world_count"],"selected":[{"id":w["id"],"suite":w["suite"],"n":w["n"],"seed":w["seed"],"frame":w["frame_sha256"],"bridge":w["bridge_variable_count"]} for w in out["selected_worlds"]],"firewall":out["selector_firewall"],"freshness":out["freshness_pass"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True));return 0 if out["status"]=="SELECTOR_PASS" else 2
if __name__=='__main__':raise SystemExit(main())
