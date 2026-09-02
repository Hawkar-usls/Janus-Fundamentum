#!/usr/bin/env python3
"""R18 exposed discovery: exact existential quantification in a shared AND/OR DAG.

Candidate lane contains no SAT solver, DPLL, assignment enumeration, resolution,
or truth table.  It compiles the frozen W04 CNF to a hash-consed Boolean DAG and
eliminates original internal variables by the Shannon identity
    exists x G == G[x=0] OR G[x=1].
Only after candidate terminal does the independent verifier inspect bridge truth.
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

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r16_prospective_unseen_factored_bridge_holdout as r16

WORLD_ID = "R16-W04"
EXPECTED_FRAME_SHA = "13ba661067d7bdc389eeff233fc10318ad1e584ecf0d101b9071a3d21cb8ac21"
WALL_SECONDS = 120.0
MAX_NODES = 1_000_000
MAX_RESTRICT_CALLS = 20_000_000


class ResourceLimit(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


@dataclass
class Budget:
    deadline: float
    restrict_calls: int = 0
    nodes_created_total: int = 0

    def check(self):
        if time.monotonic() >= self.deadline:
            raise ResourceLimit("HARD_DEADLINE")
        if self.restrict_calls > MAX_RESTRICT_CALLS:
            raise ResourceLimit("RESTRICT_CALL_CAP")


class Dag:
    """Canonical hash-consed n-ary AND/OR DAG with literal leaves and constants."""
    def __init__(self, budget: Budget):
        self.budget = budget
        self.nodes = {
            0: ("CONST", False),
            1: ("CONST", True),
        }
        self.support = {0: 0, 1: 0}
        self.intern = {("CONST", False): 0, ("CONST", True): 1}
        self.next_id = 2
        self.max_nodes_seen = 2
        self.gc_calls = 0
        self.gc_removed_total = 0
        self.mk_calls = 0
        self.hashcons_hits = 0

    def _check_nodes(self):
        self.budget.check()
        if len(self.nodes) >= MAX_NODES:
            raise ResourceLimit("NODE_CAP")

    def lit(self, lit: int):
        lit = int(lit)
        if lit == 0:
            raise ValueError("literal zero")
        key = ("LIT", lit)
        got = self.intern.get(key)
        if got is not None:
            self.hashcons_hits += 1
            return got
        self._check_nodes()
        nid = self.next_id; self.next_id += 1
        self.nodes[nid] = key
        self.support[nid] = 1 << (abs(lit) - 1)
        self.intern[key] = nid
        self.budget.nodes_created_total += 1
        self.max_nodes_seen = max(self.max_nodes_seen, len(self.nodes))
        return nid

    def kind(self, nid):
        return self.nodes[nid][0]

    def children(self, nid):
        rec = self.nodes[nid]
        return rec[1] if rec[0] in ("AND", "OR") else ()

    def mk(self, op: str, children):
        if op not in ("AND", "OR"):
            raise ValueError(op)
        self.mk_calls += 1
        if (self.mk_calls & 4095) == 0:
            self.budget.check()
        identity = 1 if op == "AND" else 0
        annihilator = 0 if op == "AND" else 1
        flat = []
        for cid in children:
            cid = int(cid)
            if cid == annihilator:
                return annihilator
            if cid == identity:
                continue
            rec = self.nodes[cid]
            if rec[0] == op:
                flat.extend(rec[1])
            else:
                flat.append(cid)
        if not flat:
            return identity
        uniq = set(flat)
        literal_signs = {}
        for cid in uniq:
            rec = self.nodes[cid]
            if rec[0] == "LIT":
                lit = int(rec[1]); v = abs(lit); s = lit > 0
                old = literal_signs.get(v)
                if old is not None and old != s:
                    return annihilator
                literal_signs[v] = s
        if len(uniq) == 1:
            return next(iter(uniq))
        kids = tuple(sorted(uniq))
        key = (op, kids)
        got = self.intern.get(key)
        if got is not None:
            self.hashcons_hits += 1
            return got
        self._check_nodes()
        nid = self.next_id; self.next_id += 1
        self.nodes[nid] = key
        mask = 0
        for cid in kids:
            mask |= self.support[cid]
        self.support[nid] = mask
        self.intern[key] = nid
        self.budget.nodes_created_total += 1
        self.max_nodes_seen = max(self.max_nodes_seen, len(self.nodes))
        return nid

    def AND(self, *children):
        return self.mk("AND", children)

    def OR(self, *children):
        return self.mk("OR", children)

    def restrict(self, root: int, var: int, value: bool):
        var = int(var); bit = 1 << (var - 1); memo = {}
        def rec(nid):
            got = memo.get(nid)
            if got is not None:
                return got
            self.budget.restrict_calls += 1
            if (self.budget.restrict_calls & 4095) == 0:
                self.budget.check()
            if not (self.support[nid] & bit):
                memo[nid] = nid
                return nid
            node = self.nodes[nid]
            if node[0] == "LIT":
                lit = int(node[1])
                out = 1 if ((lit > 0) == bool(value)) else 0
            elif node[0] in ("AND", "OR"):
                out = self.mk(node[0], (rec(c) for c in node[1]))
            else:
                out = nid
            memo[nid] = out
            return out
        return rec(int(root)), len(memo)

    def exists(self, root: int, var: int):
        a, ma = self.restrict(root, var, False)
        b, mb = self.restrict(root, var, True)
        return self.OR(a, b), ma + mb

    def gc(self, root: int):
        reachable = {0, 1}
        stack = [int(root)]
        while stack:
            nid = stack.pop()
            if nid in reachable:
                continue
            reachable.add(nid)
            node = self.nodes[nid]
            if node[0] in ("AND", "OR"):
                stack.extend(node[1])
        before = len(self.nodes)
        self.nodes = {nid: self.nodes[nid] for nid in reachable}
        self.support = {nid: self.support[nid] for nid in reachable}
        self.intern = {rec: nid for nid, rec in self.nodes.items()}
        removed = before - len(self.nodes)
        self.gc_calls += 1
        self.gc_removed_total += removed
        return removed

    def evaluate(self, root: int, assignment: dict[int, bool]):
        memo = {}
        def rec(nid):
            if nid in memo:
                return memo[nid]
            node = self.nodes[nid]
            if node[0] == "CONST":
                out = bool(node[1])
            elif node[0] == "LIT":
                lit = int(node[1]); out = bool(assignment[abs(lit)]) == (lit > 0)
            elif node[0] == "AND":
                out = all(rec(c) for c in node[1])
            elif node[0] == "OR":
                out = any(rec(c) for c in node[1])
            else:
                raise AssertionError(node)
            memo[nid] = out
            return out
        return rec(int(root))


def compile_cnf(dag: Dag, frame):
    clause_nodes = []
    for clause in frame:
        clause_nodes.append(dag.OR(*(dag.lit(lit) for lit in clause)))
    return dag.AND(*clause_nodes)


def elimination_order(frame, bridge):
    order, _ = direct.occurrence_order(frame)
    bridge_set = set(bridge)
    original = {abs(l) for c in frame for l in c}
    internal = original - bridge_set
    out = [int(v) for v in order if int(v) in internal]
    if set(out) != internal:
        out.extend(sorted(internal - set(out)))
    return tuple(out)


def candidate_compile(frame, bridge):
    started = time.monotonic(); budget = Budget(deadline=started + WALL_SECONDS); dag = Dag(budget)
    try:
        root = compile_cnf(dag, frame)
        dag.gc(root)
        order = elimination_order(frame, bridge)
        trajectory = []
        max_active = len(dag.nodes)
        for step, var in enumerate(order, start=1):
            before_nodes = len(dag.nodes)
            before_support = dag.support[root].bit_count()
            created_before = budget.nodes_created_total
            calls_before = budget.restrict_calls
            root, memo_entries = dag.exists(root, var)
            pre_gc_nodes = len(dag.nodes)
            removed = dag.gc(root)
            after_nodes = len(dag.nodes)
            max_active = max(max_active, pre_gc_nodes, after_nodes)
            trajectory.append({
                "step": step,
                "quantified_var": var,
                "before_active_nodes": before_nodes,
                "pre_gc_nodes": pre_gc_nodes,
                "after_active_nodes": after_nodes,
                "gc_removed_nodes": removed,
                "support_variables_before": before_support,
                "support_variables_after": dag.support[root].bit_count(),
                "new_nodes_created_step": budget.nodes_created_total - created_before,
                "restrict_calls_step": budget.restrict_calls - calls_before,
                "restrict_memo_entries_step": memo_entries,
            })
        bridge_set = set(bridge)
        support_vars = {v for v in range(1, max({abs(l) for c in frame for l in c}, default=0)+1) if dag.support[root] & (1 << (v-1))}
        if not support_vars <= bridge_set:
            return {"status":"FAIL_INTEGRITY","reason":"FINAL_SUPPORT_NOT_BRIDGE_ONLY","support":sorted(support_vars),"trajectory":trajectory}
        return {
            "status": "COMPLETE_INTERFACE_DAG",
            "elapsed_seconds": time.monotonic() - started,
            "root": root,
            "dag": dag,
            "elimination_order": list(order),
            "trajectory": trajectory,
            "final_active_nodes": len(dag.nodes),
            "maximum_nodes_seen_before_gc": max(max_active, dag.max_nodes_seen),
            "nodes_created_total": budget.nodes_created_total,
            "restrict_calls_total": budget.restrict_calls,
            "hashcons_hits": dag.hashcons_hits,
            "gc_calls": dag.gc_calls,
            "gc_removed_total": dag.gc_removed_total,
            "final_support": sorted(support_vars),
        }
    except ResourceLimit as e:
        return {
            "status": "OPEN_RESOURCE_LIMIT",
            "reason": e.reason,
            "elapsed_seconds": time.monotonic() - started,
            "active_nodes": len(dag.nodes),
            "maximum_nodes_seen": dag.max_nodes_seen,
            "nodes_created_total": budget.nodes_created_total,
            "restrict_calls_total": budget.restrict_calls,
            "hashcons_hits": dag.hashcons_hits,
        }


def candidate_firewall():
    funcs = [Dag, compile_cnf, elimination_order, candidate_compile]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["Solver(", "dpll(", "range(1 <<", "shadow_exact_interface", "exact_cnf_geometry", "resolve_on(", "allowed_masks"]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def assumptions_for_mask(bridge, mask):
    return [int(v) if ((mask >> i) & 1) else -int(v) for i, v in enumerate(bridge)]


def replay_model(cnf, assumptions, model):
    vals = {abs(int(l)): int(l) > 0 for l in model if int(l) != 0}
    for lit in assumptions:
        vals[abs(lit)] = lit > 0
    return all(any(vals.get(abs(lit)) == (lit > 0) for lit in clause) for clause in cnf)


def independent_original_allowed(frame, bridge):
    allowed=[]; replay_fail=[]; started=time.monotonic()
    with Solver(name="m22", bootstrap_with=[list(c) for c in frame]) as solver:
        for mask in range(1 << len(bridge)):
            assumps=assumptions_for_mask(bridge,mask)
            if solver.solve(assumptions=assumps):
                model=solver.get_model()
                if model is None or not replay_model(frame,assumps,model):
                    replay_fail.append(mask); break
                allowed.append(mask)
    return {"allowed_masks":allowed,"allowed_count":len(allowed),"replay_failures":replay_fail,"elapsed_seconds":time.monotonic()-started}


def candidate_allowed(candidate, bridge):
    dag=candidate["dag"]; root=candidate["root"]; allowed=[]; started=time.monotonic()
    for mask in range(1 << len(bridge)):
        assignment={int(v): bool((mask>>i)&1) for i,v in enumerate(bridge)}
        if dag.evaluate(root,assignment): allowed.append(mask)
    return {"allowed_masks":allowed,"allowed_count":len(allowed),"elapsed_seconds":time.monotonic()-started}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks),separators=(",",":")).encode()).hexdigest()


def tiny_controls():
    budget=Budget(deadline=time.monotonic()+10); dag=Dag(budget)
    # exists x: (x or b) & (~x or c) == b or c
    frame=((1,2),(-1,3)); bridge=(2,3)
    cand=candidate_compile(frame,bridge)
    if cand["status"]!="COMPLETE_INTERFACE_DAG": return False
    got=candidate_allowed(cand,bridge)["allowed_masks"]
    return got==[1,2,3]


def run():
    freeze,_=r16.load_contracts(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r16.generate_frozen_world(spec)
    frame=tuple(world["frame"]); bridge=tuple(world["bridge"])
    if spec["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W04 freeze drift")
    fw=candidate_firewall(); tiny=tiny_controls()
    candidate=candidate_compile(frame,bridge)
    base={
        "schema":"JANUS/TRUMP/R18/SHANNON_HASHCONS_INTERFACE_DAG_DISCOVERY/RESULT/v1.0",
        "created_date":"2026-09-02",
        "world":{"id":WORLD_ID,"frame_sha256":spec["frame_sha256"],"frame_clauses":len(frame),"frame_variables":spec["frame_variable_count"],"bridge_variables":len(bridge),"bridge_vars":list(bridge),"R17_physical_width3_checkpoint_clauses":533525},
        "candidate_firewall":fw,
        "tiny_control":tiny,
        "P_VS_NP":"OPEN",
    }
    if not fw["pass"] or not tiny or candidate["status"]=="FAIL_INTEGRITY":
        return {**base,"verdict":"R18_FAIL_INTEGRITY","candidate":{k:v for k,v in candidate.items() if k not in ("dag","root")},"verifier":{"not_run":True}}
    if candidate["status"]=="OPEN_RESOURCE_LIMIT":
        return {**base,"verdict":"R18_OPEN_RESOURCE_LIMIT","candidate":candidate,"verifier":{"not_run":True},"seal":"THE_NEW_LANGUAGE_HIT_ITS_FROZEN_RESOURCE_WALL__NO_SEMANTIC_VERDICT"}
    # Truth becomes visible only here, after candidate terminal.
    original=independent_original_allowed(frame,bridge); got=candidate_allowed(candidate,bridge)
    exact=set(original["allowed_masks"]); cand=set(got["allowed_masks"]); fp=sorted(cand-exact); fn=sorted(exact-cand)
    comparison={
        "full_domain":True,"domain_size":1<<len(bridge),"original_allowed":len(exact),"candidate_allowed":len(cand),
        "false_positive_count":len(fp),"false_negative_count":len(fn),"first_false_positive_masks":fp[:32],"first_false_negative_masks":fn[:32],
        "original_truth_table_sha256":mask_hash(original["allowed_masks"]),"candidate_truth_table_sha256":mask_hash(got["allowed_masks"]),
        "allowed_set_equal":not fp and not fn,"original_sat_model_replay_failures":original["replay_failures"]
    }
    verdict="R18_EXPOSED_W04_FULL_DOMAIN_SEMANTIC_MATCH" if comparison["allowed_set_equal"] and not original["replay_failures"] else "R18_EXPOSED_W04_SEMANTIC_MISMATCH"
    csummary={k:v for k,v in candidate.items() if k not in ("dag","root")}
    csummary["compression_vs_R17_physical_clauses"] = 533525 / candidate["final_active_nodes"] if candidate["final_active_nodes"] else None
    return {**base,"verdict":verdict,"candidate":csummary,"verifier":{"original":{k:v for k,v in original.items() if k!="allowed_masks"},"candidate_evaluation":{k:v for k,v in got.items() if k!="allowed_masks"}},"comparison":comparison,
            "scientific_interpretation":"This is exposed W04 discovery only. MATCH shows that exact existential interface semantics can be carried by this shared DAG under the frozen discovery envelope; it does not establish unseen generalization or polynomial scaling.",
            "seal":"THE_HALF_MILLION_CLAUSE_ROOM_WAS_REPLACED_BY_A_SHARED_BOOLEAN_MACHINE__NOW_VERIFY_BEFORE_CELEBRATING"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"candidate":d["candidate"],"comparison":d.get("comparison"),"firewall":d["candidate_firewall"],"tiny_control":d["tiny_control"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True)); return 2 if d["verdict"]=="R18_FAIL_INTEGRITY" else 0


if __name__=="__main__": raise SystemExit(main())
