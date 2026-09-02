#!/usr/bin/env python3
"""R21 exposed discovery: canonical reduced ordered BDD function DAG on R19-W05.

The candidate has no SAT solver, DPLL, assignment enumeration, truth-table build,
resolution fallback, dynamic reordering, or semantic oracle.  W05 is exposed
material.  Only after candidate terminal is independent bridge truth inspected.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import time
from dataclasses import dataclass
from pathlib import Path

from pysat.solvers import Solver

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19

WORLD_ID = "R19-W05"
EXPECTED_FRAME_SHA = "cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384"
WALL_SECONDS = 120.0
MAX_NODES = 1_000_000
MAX_APPLY_CALLS = 20_000_000
MAX_QUANTIFY_CALLS = 20_000_000
MAX_GC_CALLS = 1000


class ResourceLimit(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason); self.reason = reason


class IntegrityFailure(RuntimeError):
    pass


@dataclass
class Budget:
    deadline: float
    nodes_created_total: int = 0
    apply_calls: int = 0
    quantify_calls: int = 0

    def check(self):
        if time.monotonic() >= self.deadline:
            raise ResourceLimit("HARD_DEADLINE")
        if self.apply_calls > MAX_APPLY_CALLS:
            raise ResourceLimit("APPLY_CALL_CAP")
        if self.quantify_calls > MAX_QUANTIFY_CALLS:
            raise ResourceLimit("QUANTIFY_CALL_CAP")


class ROBDD:
    """Canonical ROBDD under one immutable total variable order."""
    def __init__(self, variable_order, budget: Budget):
        order = tuple(int(v) for v in variable_order)
        if len(order) != len(set(order)):
            raise IntegrityFailure("DUPLICATE_VARIABLE_IN_ORDER")
        self.order = order
        self.rank = {v:i for i,v in enumerate(order)}
        self.budget = budget
        self.nodes = {0:("CONST",False), 1:("CONST",True)}
        self.support = {0:0, 1:0}
        self.unique = {}
        self.next_id = 2
        self.max_nodes_seen = 2
        self.unique_hits = 0
        self.apply_cache_hits = 0
        self.quantify_cache_hits = 0
        self.gc_calls = 0
        self.gc_removed_total = 0

    def _check_node_budget(self):
        self.budget.check()
        if len(self.nodes) >= MAX_NODES:
            raise ResourceLimit("NODE_CAP")

    def _node_rank(self, nid):
        if nid in (0,1): return len(self.order) + 1
        return self.rank[self.nodes[int(nid)][1]]

    def mk(self, var, low, high):
        var=int(var); low=int(low); high=int(high)
        if low == high: return low
        if var not in self.rank: raise IntegrityFailure("VARIABLE_NOT_IN_ORDER")
        vr=self.rank[var]
        if low not in self.nodes or high not in self.nodes: raise IntegrityFailure("MISSING_CHILD")
        if self._node_rank(low) <= vr or self._node_rank(high) <= vr:
            raise IntegrityFailure("ORDER_VIOLATION")
        key=(var,low,high)
        got=self.unique.get(key)
        if got is not None:
            self.unique_hits += 1
            return got
        self._check_node_budget()
        nid=self.next_id; self.next_id += 1
        self.nodes[nid]=("DECISION",var,low,high)
        self.support[nid]=(1 << (var-1)) | self.support[low] | self.support[high]
        self.unique[key]=nid
        self.budget.nodes_created_total += 1
        self.max_nodes_seen=max(self.max_nodes_seen,len(self.nodes))
        return nid

    def literal(self, lit):
        lit=int(lit); var=abs(lit)
        return self.mk(var,0,1) if lit>0 else self.mk(var,1,0)

    def apply(self, op, left, right):
        if op not in ("AND","OR"): raise ValueError(op)
        memo={}
        def rec(u,v):
            self.budget.apply_calls += 1
            if (self.budget.apply_calls & 4095) == 0: self.budget.check()
            u=int(u); v=int(v)
            if u > v: u,v=v,u
            if op=="AND":
                if u==0 or v==0: return 0
                if u==1: return v
                if v==1: return u
                if u==v: return u
            else:
                if u==1 or v==1: return 1
                if u==0: return v
                if v==0: return u
                if u==v: return u
            key=(u,v)
            got=memo.get(key)
            if got is not None:
                self.apply_cache_hits += 1
                return got
            ru=self._node_rank(u); rv=self._node_rank(v); top_rank=min(ru,rv)
            if top_rank > len(self.order): raise IntegrityFailure("NONTERMINAL_EXPECTED")
            top=self.order[top_rank]
            if ru==top_rank:
                _,_,ul,uh=self.nodes[u]
            else:
                ul=uh=u
            if rv==top_rank:
                _,_,vl,vh=self.nodes[v]
            else:
                vl=vh=v
            low=rec(ul,vl); high=rec(uh,vh); out=self.mk(top,low,high); memo[key]=out; return out
        return rec(int(left),int(right)), len(memo)

    def exists_var(self, root, var):
        var=int(var); target_rank=self.rank[var]; memo={}; apply_memo_entries=0
        def rec(nid):
            nonlocal apply_memo_entries
            self.budget.quantify_calls += 1
            if (self.budget.quantify_calls & 4095) == 0: self.budget.check()
            nid=int(nid)
            if nid in (0,1): return nid
            got=memo.get(nid)
            if got is not None:
                self.quantify_cache_hits += 1
                return got
            _,node_var,low,high=self.nodes[nid]; nr=self.rank[node_var]
            if nr > target_rank:
                out=nid
            elif node_var == var:
                out, used = self.apply("OR",low,high); apply_memo_entries += used
            else:
                out=self.mk(node_var,rec(low),rec(high))
            memo[nid]=out; return out
        return rec(int(root)), len(memo), apply_memo_entries

    def gc(self, root):
        if self.gc_calls >= MAX_GC_CALLS: raise ResourceLimit("GC_CALL_CAP")
        reachable={0,1}; stack=[int(root)]
        while stack:
            nid=stack.pop()
            if nid in reachable: continue
            reachable.add(nid); rec=self.nodes[nid]
            if rec[0]=="DECISION": stack.extend((rec[2],rec[3]))
        before=len(self.nodes)
        self.nodes={nid:self.nodes[nid] for nid in reachable}
        self.support={nid:self.support[nid] for nid in reachable}
        self.unique={(rec[1],rec[2],rec[3]):nid for nid,rec in self.nodes.items() if rec[0]=="DECISION"}
        removed=before-len(self.nodes); self.gc_calls += 1; self.gc_removed_total += removed
        return removed

    def evaluate(self, root, assignment):
        nid=int(root)
        while nid not in (0,1):
            _,var,low,high=self.nodes[nid]
            nid=high if bool(assignment[int(var)]) else low
        return nid==1


def frozen_variable_order(frame, bridge):
    internal=tuple(r18.elimination_order(frame,bridge)); bridge_set=set(int(v) for v in bridge)
    occ,_=r18.direct.occurrence_order(frame); tail=[]; seen=set()
    for v in occ:
        v=int(v)
        if v in bridge_set and v not in seen: tail.append(v); seen.add(v)
    tail.extend(sorted(bridge_set-seen))
    out=tuple(internal)+tuple(tail)
    variables={abs(l) for c in frame for l in c}
    if set(out)!=variables or len(out)!=len(variables): raise IntegrityFailure("VARIABLE_ORDER_COVERAGE_FAIL")
    return out


def candidate_compile(frame, bridge):
    started=time.monotonic(); budget=Budget(deadline=started+WALL_SECONDS); order=frozen_variable_order(frame,bridge); bdd=ROBDD(order,budget)
    root=1; clause_trajectory=[]; quantify_trajectory=[]; phase="BUILD_CNF"; current=None
    try:
        for idx,clause in enumerate(frame,start=1):
            before=len(bdd.nodes); created_before=budget.nodes_created_total; calls_before=budget.apply_calls; hits_before=bdd.unique_hits
            clause_root=0
            for lit in clause:
                lit_root=bdd.literal(lit); clause_root,_=bdd.apply("OR",clause_root,lit_root)
            root,_=bdd.apply("AND",root,clause_root)
            pre_gc=len(bdd.nodes); removed=bdd.gc(root); after=len(bdd.nodes)
            clause_trajectory.append({"clause_index":idx,"elapsed_seconds":time.monotonic()-started,"before_active_nodes":before,"pre_gc_nodes":pre_gc,"after_active_nodes":after,"gc_removed_nodes":removed,"new_nodes_created":budget.nodes_created_total-created_before,"apply_calls":budget.apply_calls-calls_before,"unique_hits":bdd.unique_hits-hits_before})
        initial_compiled_nodes=len(bdd.nodes); phase="QUANTIFY"
        internal=r18.elimination_order(frame,bridge)
        for step,var in enumerate(internal,start=1):
            before=len(bdd.nodes); support_before=bdd.support[root].bit_count(); created_before=budget.nodes_created_total; apply_before=budget.apply_calls; q_before=budget.quantify_calls; hits_before=bdd.unique_hits
            current={"step":step,"var":int(var),"before_active_nodes":before,"support_before":support_before,"created_before":created_before,"apply_before":apply_before,"quantify_before":q_before}
            root,qmemo,amemo=bdd.exists_var(root,var)
            pre_gc=len(bdd.nodes); removed=bdd.gc(root); after=len(bdd.nodes)
            quantify_trajectory.append({"step":step,"quantified_var":int(var),"elapsed_seconds":time.monotonic()-started,"before_active_nodes":before,"pre_gc_nodes":pre_gc,"after_active_nodes":after,"gc_removed_nodes":removed,"support_before":support_before,"support_after":bdd.support[root].bit_count(),"new_nodes_created":budget.nodes_created_total-created_before,"apply_calls":budget.apply_calls-apply_before,"quantify_calls":budget.quantify_calls-q_before,"unique_hits":bdd.unique_hits-hits_before,"quantify_memo_entries":qmemo,"apply_memo_entries_inside_quantify":amemo})
            current=None
        bridge_set=set(bridge); support={v for v in order if bdd.support[root] & (1 << (v-1))}
        if not support <= bridge_set: return {"status":"FAIL_INTEGRITY","reason":"FINAL_SUPPORT_NOT_BRIDGE_ONLY","support":sorted(support),"clause_trajectory":clause_trajectory,"quantify_trajectory":quantify_trajectory}
        return {"status":"COMPLETE_INTERFACE_ROBDD","elapsed_seconds":time.monotonic()-started,"root":root,"bdd":bdd,"variable_order":list(order),"initial_compiled_nodes":initial_compiled_nodes,"final_active_nodes":len(bdd.nodes),"maximum_nodes_seen":bdd.max_nodes_seen,"nodes_created_total":budget.nodes_created_total,"unique_table_hits":bdd.unique_hits,"apply_cache_hits":bdd.apply_cache_hits,"quantify_cache_hits":bdd.quantify_cache_hits,"apply_calls_total":budget.apply_calls,"quantify_calls_total":budget.quantify_calls,"gc_calls":bdd.gc_calls,"gc_removed_total":bdd.gc_removed_total,"final_support":sorted(support),"clause_trajectory":clause_trajectory,"quantify_trajectory":quantify_trajectory}
    except ResourceLimit as e:
        partial=None
        if current is not None:
            partial={**current,"elapsed_seconds":time.monotonic()-started,"reason":e.reason,"active_nodes_at_open":len(bdd.nodes),"partial_nodes_created":budget.nodes_created_total-current["created_before"],"partial_apply_calls":budget.apply_calls-current["apply_before"],"partial_quantify_calls":budget.quantify_calls-current["quantify_before"]}
        return {"status":"OPEN_RESOURCE_LIMIT","reason":e.reason,"phase":phase,"elapsed_seconds":time.monotonic()-started,"active_nodes":len(bdd.nodes),"maximum_nodes_seen":bdd.max_nodes_seen,"nodes_created_total":budget.nodes_created_total,"unique_table_hits":bdd.unique_hits,"apply_calls_total":budget.apply_calls,"quantify_calls_total":budget.quantify_calls,"gc_calls":bdd.gc_calls,"gc_removed_total":bdd.gc_removed_total,"variable_order":list(order),"clause_trajectory":clause_trajectory,"quantify_trajectory":quantify_trajectory,"partial_open_step":partial}
    except IntegrityFailure as e:
        return {"status":"FAIL_INTEGRITY","reason":str(e),"phase":phase,"clause_trajectory":clause_trajectory,"quantify_trajectory":quantify_trajectory}


def candidate_firewall():
    src="\n".join(inspect.getsource(x) for x in (ROBDD,frozen_variable_order,candidate_compile))
    forbidden=["Solver(","solve(","range(1 <<","allowed_masks","truth_table","dpll(","resolve_on(","dynamic_reorder"]
    hits=[x for x in forbidden if x in src]
    return {"pass":not hits,"forbidden_hits":hits}


def assumptions_for_mask(bridge,mask):
    return [int(v) if ((mask>>i)&1) else -int(v) for i,v in enumerate(bridge)]


def replay_model(cnf,assumptions,model):
    vals={abs(int(l)):int(l)>0 for l in model if int(l)!=0}
    for lit in assumptions: vals[abs(lit)]=lit>0
    return all(any(vals.get(abs(lit))==(lit>0) for lit in clause) for clause in cnf)


def independent_original_allowed(frame,bridge):
    allowed=[]; replay_fail=[]; started=time.monotonic()
    with Solver(name="m22",bootstrap_with=[list(c) for c in frame]) as solver:
        for mask in range(1 << len(bridge)):
            assumptions=assumptions_for_mask(bridge,mask)
            if solver.solve(assumptions=assumptions):
                model=solver.get_model()
                if model is None or not replay_model(frame,assumptions,model): replay_fail.append(mask); break
                allowed.append(mask)
    return {"allowed_masks":allowed,"allowed_count":len(allowed),"replay_failures":replay_fail,"elapsed_seconds":time.monotonic()-started}


def candidate_allowed(candidate,bridge):
    bdd=candidate["bdd"]; root=candidate["root"]; allowed=[]; started=time.monotonic()
    for mask in range(1 << len(bridge)):
        assignment={int(v):bool((mask>>i)&1) for i,v in enumerate(bridge)}
        if bdd.evaluate(root,assignment): allowed.append(mask)
    return {"allowed_masks":allowed,"allowed_count":len(allowed),"elapsed_seconds":time.monotonic()-started}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks),separators=(",",":")).encode()).hexdigest()


def tiny_control():
    frame=((1,2),(-1,3)); bridge=(2,3); c=candidate_compile(frame,bridge)
    if c["status"]!="COMPLETE_INTERFACE_ROBDD": return False
    return candidate_allowed(c,bridge)["allowed_masks"]==[1,2,3]


def run():
    freeze=r19.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r19.generate_frozen_world(spec); frame=tuple(world["frame"]); bridge=tuple(world["bridge"])
    if spec["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W05 freeze drift")
    fw=candidate_firewall(); tiny=tiny_control(); candidate_started=time.monotonic(); candidate=candidate_compile(frame,bridge); candidate_completed=time.monotonic()
    csummary={k:v for k,v in candidate.items() if k not in ("bdd","root")}
    base={"schema":"JANUS/TRUMP/R21/CANONICAL_ROBDD_FUNCTION_DAG_DISCOVERY/RESULT/v1.0","created_date":"2026-09-02","scientific_role":"EXPOSED_REPRESENTATION_DISCOVERY__NOT_UNSEEN","world":{"id":WORLD_ID,"frame_sha256":spec["frame_sha256"],"frame_clauses":len(frame),"frame_variables":spec["frame_variable_count"],"internal_variables":spec["internal_variable_count"],"bridge_variables":len(bridge),"bridge_vars":list(bridge)},"candidate_firewall":fw,"tiny_control":tiny,"candidate_started_monotonic":candidate_started,"candidate_completed_monotonic":candidate_completed,"P_VS_NP":"OPEN"}
    if not fw["pass"] or not tiny or candidate["status"]=="FAIL_INTEGRITY": return {**base,"verdict":"R21_FAIL_INTEGRITY","candidate":csummary,"verifier_ran":False}
    if candidate["status"]=="OPEN_RESOURCE_LIMIT": return {**base,"verdict":"R21_OPEN_RESOURCE_LIMIT__NO_SEMANTIC_VERDICT","candidate":csummary,"verifier_ran":False,"scientific_firewall":{"truth_not_accessed":True,"resource_limit_not_negative_evidence":True}}
    if candidate["status"]!="COMPLETE_INTERFACE_ROBDD": return {**base,"verdict":"R21_FAIL_INTEGRITY","candidate":csummary,"verifier_ran":False,"reason":"UNKNOWN_CANDIDATE_STATUS"}
    verifier_started=time.monotonic(); original=independent_original_allowed(frame,bridge); got=candidate_allowed(candidate,bridge); verifier_completed=time.monotonic()
    if original["replay_failures"]: return {**base,"verdict":"R21_FAIL_INTEGRITY","candidate":csummary,"verifier_ran":True,"reason":"SAT_MODEL_REPLAY_FAIL","replay_failures":original["replay_failures"]}
    exact=set(original["allowed_masks"]); observed=set(got["allowed_masks"]); fp=sorted(observed-exact); fn=sorted(exact-observed); match=not fp and not fn
    comparison={"full_domain":True,"domain_size":1<<len(bridge),"original_allowed":len(exact),"candidate_allowed":len(observed),"false_positive_count":len(fp),"false_negative_count":len(fn),"first_false_positive_masks":fp[:32],"first_false_negative_masks":fn[:32],"original_truth_table_sha256":mask_hash(original["allowed_masks"]),"candidate_truth_table_sha256":mask_hash(got["allowed_masks"]),"allowed_set_equal":match,"original_sat_model_replay_failures":original["replay_failures"]}
    verdict="R21_EXPOSED_W05_FULL_DOMAIN_SEMANTIC_MATCH" if match else "R21_EXPOSED_W05_SEMANTIC_MISMATCH"
    return {**base,"verdict":verdict,"candidate":csummary,"verifier_ran":True,"verifier_started_monotonic":verifier_started,"verifier_completed_monotonic":verifier_completed,"verifier":{"original":{k:v for k,v in original.items() if k!="allowed_masks"},"candidate_evaluation":{k:v for k,v in got.items() if k!="allowed_masks"}},"comparison":comparison,"scientific_firewall":{"candidate_terminal_before_truth":candidate_completed<=verifier_started,"full_domain_compared":True,"world_is_exposed_not_unseen":True},"claim_ceiling":"Exposed W05 discovery only. No unseen or asymptotic complexity authority.","seal":"THE_FUNCTION_CANONICAL_MACHINE_MET_THE_EXPOSED_CHURN_WORLD__GRADE_IT_EXACTLY_BEFORE_ANY_PROMOTION","P_VS_NP":"OPEN"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(json.dumps({"verdict":d["verdict"],"candidate":d["candidate"],"comparison":d.get("comparison"),"firewall":d["candidate_firewall"],"tiny_control":d["tiny_control"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True)); return 2 if d["verdict"]=="R21_FAIL_INTEGRITY" else 0


if __name__=="__main__": raise SystemExit(main())
