from __future__ import annotations
"""Independent preexecution verifier for TRUMP USF R0 Lane-A V3.

Runs only synthetic non-USF fixtures. It tests the V3 generic width adapter,
independently re-validates the produced factor TD, and statically audits the
binding so the construction lemma cannot be substituted for measurement.
"""
import ast, hashlib, importlib, json, sys
from pathlib import Path

EXECUTOR_PATH="research/trump_usf_r0_lane_a_phase_and_width_separated_calibration_v3.py"
EXECUTOR_BLOB="80c134d76cc6a5986f8367a0f1eb26167c90bbb5"
PHASE=("research/TRUMP_USF_R0_LANE_A_INPUT_CLASS_VS_POST_REDUCER_TERMINAL_METHODOLOGICAL_SUCCESSOR_2026-09-10.json","6d8db87c7c0bc36e3e8c08d5df691714aa2448ff")
WIDTH=("research/TRUMP_USF_R0_INCIDENCE_WIDTH_VS_BA25_FACTOR_TD_WIDTH_BINDING_METHODOLOGICAL_SUCCESSOR_2026-09-10.json","9b412cbbef47738ff80fa28355eed42bcd5694c6")
V1=("research/TRUMP_USF_R0_LANE_A_CALIBRATION_DISCOVERY_FAILURE_2026-09-10.json","97b454cefb2be61b6f0ccd021980b06831cab66d")
V2=("research/TRUMP_USF_R0_LANE_A_PHASE_SEPARATED_CALIBRATION_V2_FAILURE_2026-09-10.json","0e88340237fd6e151ad14fad4f8565c5f1232d86")
SCI={
"GENERATOR":("research/trump_usf_r0_frozen_generators.py","fe33883dc08e7e1eacadf287093aa0bb1f16c19a"),
"ENTRYPOINT":("research/trump_usf_r0_execution_harness_frozen_entrypoint.py","50e8eedd461b87de37385cc9f3d30ea6224909fb"),
"CORE":("research/trump_usf_r0_execution_harness.py","ed4203bac76349ab377bb97f67bf1054d837bc96"),
"R37B":("experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py","f37da1c2e1696e35695096a2c748a222af7920cc"),
"R33":("experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py","c9234a1ef639a009cc6cb4c8a6098fd09bf9affe"),
"R34":("experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py","7f9bec920fa47af066570d874fe9127dc4b9b968"),
"R35":("experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py","ad237e341d9659d33da0568f134815776c1f95d8"),
"R35B":("experiments/janus_trump_r35b_single_literal_rup_vivification.py","259d2e38947d09b0c058963ad825a57f2e734203"),
"R38":("experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py","816b53c390d78af415e580eaf358acf191796205"),
"WIDTH_EXTENDER":("experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py","ea36a6b69f8c6034aa00ae4c4217bbd4d7735750"),
"BA25":("research/janus_trump_r50g25ba25.py","cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff"),
}
REQUIRED_FAILURE_DOMAINS={"SOURCE_CLASS_CALIBRATION_FAILURE","REDUCER_REPLAY_FAILURE","INCIDENCE_WIDTH_AUTHORITY_FAILURE","BA25_FACTOR_TD_BINDING_FAILURE","BA25_DIAGNOSTIC_FAILURE","POST_REDUCER_TERMINAL_CALIBRATION_FAILURE","TRUTH_AUTHORITY_FAILURE","CAUSAL_FIREWALL_FAILURE"}

def blob(p:Path):
    b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def own_validate(vertices,edges,td):
    nodes=set(td.bags); adj={x:set() for x in nodes}
    for a,b in td.edges:
        if a not in nodes or b not in nodes or a==b:return {"pass":False,"why":"bad_td_edge"}
        adj[a].add(b);adj[b].add(a)
    if nodes:
        seen=set();stack=[next(iter(nodes))]
        while stack:
            x=stack.pop()
            if x in seen:continue
            seen.add(x);stack.extend(adj[x]-seen)
        if seen!=nodes or len(td.edges)!=len(nodes)-1:return {"pass":False,"why":"not_tree"}
    cover=set().union(*td.bags.values()) if td.bags else set()
    if cover!=set(vertices):return {"pass":False,"why":"vertex_coverage"}
    for a,b in edges:
        if not any(a in bag and b in bag for bag in td.bags.values()):return {"pass":False,"why":"edge_coverage","edge":[a,b]}
    for v in vertices:
        holders={n for n,bag in td.bags.items() if v in bag}
        if not holders:return {"pass":False,"why":"vertex_missing","v":v}
        reached=set();stack=[next(iter(holders))]
        while stack:
            x=stack.pop()
            if x in reached:continue
            reached.add(x);stack.extend((adj[x]&holders)-reached)
        if reached!=holders:return {"pass":False,"why":"running_intersection","v":v}
    return {"pass":True,"tree":True,"vertex_coverage":True,"edge_coverage":True,"running_intersection":True,"width":max((len(b)-1 for b in td.bags.values()),default=-1)}

def static_audit(source):
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="factor_td_binding")
    text=ast.get_source_segment(source,fn)
    for forbidden in ("A1_2SAT_EQUIVALENCE_RING","n=32","actual=1","c991bd0e8af4373582b62f0978c0a8658fc6ad47e913faa091a6498ffbaba1de"):
        if forbidden in text:raise AssertionError("INSTANCE_SPECIFIC_WIDTH_LOGIC:"+forbidden)
    u_f_assign=[n for n in ast.walk(fn) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="u_f" for t in n.targets)]
    assert len(u_f_assign)==1
    val=u_f_assign[0].value
    assert isinstance(val,ast.Subscript) and isinstance(val.value,ast.Name) and val.value.id=="iv"
    max_to_uf=False
    for n in ast.walk(fn):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="validate_td":
            for kw in n.keywords:
                if kw.arg=="claimed_tau" and isinstance(kw.value,ast.Name) and kw.value.id=="u_f":max_to_uf=True
    assert max_to_uf
    return {"factor_width_is_measured_from_independent_validation":True,"claimed_tau_uses_measured_u_F":True,"instance_specific_width_logic_absent":True}

def main():
    root=Path(__file__).resolve().parents[1]
    pins={"V3_EXECUTOR":(EXECUTOR_PATH,EXECUTOR_BLOB),"PHASE":PHASE,"WIDTH":WIDTH,"V1":V1,"V2":V2,**SCI}
    for role,(p,e) in pins.items():
        o=blob(root/p)
        if o!=e:raise AssertionError(f"PIN_DRIFT:{role}:{o}:{e}")
    source=(root/EXECUTOR_PATH).read_text()
    static=static_audit(source)
    for d in ("research","experiments"):
        s=str(root/d)
        if s not in sys.path:sys.path.insert(0,s)
    v3=importlib.import_module("trump_usf_r0_lane_a_phase_and_width_separated_calibration_v3")
    core,entry,gen,r33,r34,r35,r35b,r38,width,ba25,ass=v3.modules(root)
    assert REQUIRED_FAILURE_DOMAINS<=set(v3.FAILURE_DOMAINS)
    fixtures=[
        ("SYNTH_EMPTY_INCIDENCE",gen.canonical_formula([]),-1),
        ("SYNTH_ISOLATED_EMPTY_CLAUSE",gen.canonical_formula([[]]),0),
        ("SYNTH_UNIT_EDGE",gen.canonical_formula([[1]]),1),
        ("SYNTH_K2_2_INCIDENCE",gen.canonical_formula([[1,2],[1,-2]]),2),
    ]
    rows=[]
    for name,formula,expected_ui in fixtures:
        pub,priv=entry.width_evidence(core,width,formula,name)
        u_i=pub["verified_td_upper_bound"]
        if u_i!=expected_ui:raise AssertionError(f"FIXTURE_UI_DRIFT:{name}:{u_i}:{expected_ui}")
        bind,p=v3.factor_td_binding(core,width,ba25,priv)
        own=own_validate(p["factor_vertices"],p["factor_edges"],p["factor_td"])
        if own.get("pass") is not True:raise AssertionError(("OWN_FACTOR_TD_VALIDATION_FAIL",name,own))
        u_f=own["width"]
        if u_f!=bind["BA25_FACTOR_TD_VERIFIED_WIDTH"]:raise AssertionError("ADAPTER_VS_OWN_WIDTH_MISMATCH")
        if u_f!=max(u_i,1):raise AssertionError("LIFT_RELATION_FAIL")
        old_ok,old_receipt=ba25.validate_td(p["factor_vertices"],p["factor_edges"],p["factor_td"],claimed_tau=u_i)
        if u_f!=u_i:
            if old_ok:raise AssertionError("OLD_BINDING_WAS_NOT_REJECTED:"+name)
            if old_receipt.get("why")!="tau" or old_receipt.get("actual")!=u_f or old_receipt.get("claimed")!=u_i:raise AssertionError(("OLD_BINDING_WRONG_REJECTION",name,old_receipt))
        rows.append({"fixture":name,"INCIDENCE_TD_VERIFIED_UB":u_i,"BA25_FACTOR_TD_VERIFIED_WIDTH":u_f,"independent_factor_td_validation":own,"lift_relation_pass":True,"old_binding_differs":u_f!=u_i,"old_binding_rejected_when_different":(not old_ok) if u_f!=u_i else None,"old_binding_receipt":old_receipt})
    assert {r["INCIDENCE_TD_VERIFIED_UB"] for r in rows}=={-1,0,1,2}
    out={"schema":"TRUMP_USF_R0_LANE_A_V3_PREEXECUTION_INDEPENDENT_VERIFIER","status":"PASS","V3_EXECUTOR_BLOB":EXECUTOR_BLOB,"static_audit":static,"synthetic_non_USF_fixtures":rows,"covered_incidence_width_cases":["u_I=-1","u_I=0","u_I=1","u_I>1"],"old_binding_mechanically_rejected_where_width_differs":True,"construction_lemma_not_used_as_measurement_substitute":True,"real_lane_a_instance_executed":False,"scheduled_USF_generator_called":False,"LANE_B_EXECUTION_STARTED":False,"LANE_C_EXECUTION_STARTED":False,"HOLDOUT_EXECUTION_STARTED":False,"BA26_STARTED":False}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
