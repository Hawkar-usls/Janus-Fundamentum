#!/usr/bin/env python3
"""BABEL41 — UNIVERSAL TOTAL Exact-One SCL decision with UNSAT DAG receipt.

Complete on EVERY valid SCL input, including arbitrary connected high-width,
high-nullity inputs; never returns UNKNOWN. It deliberately DOES NOT claim
POLYNOMIAL worst-case SAT decision, P=NP, or short UNSAT certificates.

- Every true variable covers EXACTLY THREE distinct original rows.
- Branch on a not-yet-satisfied row among its <=3 possible true variables.
- Exact row propagation, cache true-bit states and store complete UNSAT DAG.
- Depth <= floor(n/3), so a conservative O(poly(n)*3^(n/3)) time bound.
- SAT witness verified against every ORIGINAL row.
- UNSAT refutation rechecked independently in verify_universal_proof.py.
No external packages, no network, no hidden oracle and no external solver.
"""
from collections import Counter
import hashlib
import json


def validate(rows):
    rows=tuple(tuple(int(v) for v in row) for row in rows)
    n=len(rows)
    if not n:
        raise ValueError("Nonempty SCL required")
    if any(len(r)!=3 or len(set(r))!=3 or
           any(v<0 or v>=n for v in r) for r in rows):
        raise ValueError("All rows must contain three distinct in-range variables")
    degrees=Counter(v for r in rows for v in r)
    if any(degrees[j]!=3 for j in range(n)):
        raise ValueError("Every variable must occur exactly three times")
    seen=set()
    for row in rows:
        for i in range(3):
            for j in range(i+1,3):
                key=tuple(sorted((row[i],row[j])))
                if key in seen:
                    raise ValueError("Pair-linear incidence violated")
                seen.add(key)
    return rows


def canonical_rows_digest(rows):
    return hashlib.sha256(json.dumps(
        [list(r) for r in rows],separators=(",",":")).encode()).hexdigest()


class ExactDecision:
    def __init__(self,rows):
        self.rows=validate(rows)
        self.n=len(rows)
        self.rowmask=[sum(1<<v for v in row) for row in rows]
        self.variable_rows=[0]*self.n
        for i,row in enumerate(rows):
            for v in row:
                self.variable_rows[v]|=1<<i
        assert all(m.bit_count()==3 for m in self.variable_rows)
        self.all_rows=(1<<self.n)-1
        self.nodes={}
        self.states_examined=0
        self.branch_nodes=0
        self.conflict_nodes=0

    def close(self,selected):
        """Exact unit row implications; returns (tag, true, row, choices).

        selected has bits only of variables fixed TRUE. Every FALSE bit is
        derived from rows already covered by a true variable.
        """
        true=selected
        while True:
            used=0
            false=0
            for v in range(self.n):
                if (true>>v)&1:
                    if used&self.variable_rows[v]:
                        return "CONFLICT",true,None,()
                    used|=self.variable_rows[v]
            for row_id,row in enumerate(self.rows):
                if (used>>row_id)&1:
                    bits=self.rowmask[row_id]
                    false|=bits & ~true
            if true&false:
                return "CONFLICT",true,None,()
            best=None
            unit=0
            for row_id,bits in enumerate(self.rowmask):
                if (used>>row_id)&1:continue
                available=bits&~false
                size=available.bit_count()
                if size==0:
                    return "CONFLICT",true,None,()
                if size==1:
                    unit|=available
                elif best is None or size<best[0]:
                    best=(size,row_id,available)
            if unit:
                # Two mutually incompatible forced choices are rejected in
                # the next pass by the row-overlap check.
                if unit&~true:
                    true|=unit
                    continue
            if used==self.all_rows:
                return "SAT",true,None,()
            assert best is not None and best[0] in (2,3)
            choicebits=best[2]
            choices=tuple(v for v in range(self.n) if (choicebits>>v)&1)
            assert len(choices)==best[0]
            return "OPEN",true,best[1],choices

    def _search(self,true):
        key=format(true,"x")
        if key in self.nodes:
            return None
        self.states_examined+=1
        kind,closed,row,choices=self.close(true)
        if kind=="SAT":
            assert all(sum((closed>>v)&1 for v in r)==1
                       for r in self.rows)
            return closed
        if kind=="CONFLICT":
            self.nodes[key]={"type":"CONFLICT"}
            self.conflict_nodes+=1
            return None
        # Provisional marker prevents accidental recursive self-reference.
        assert kind=="OPEN"
        self.nodes[key]={"type":"IN_PROGRESS"}
        self.branch_nodes+=1
        children=[]
        for v in choices:
            child=closed|(1<<v)
            child_key=format(child,"x")
            children.append(child_key)
            answer=self._search(child)
            if answer is not None:
                self.nodes.clear()
                return answer
        self.nodes[key]={"type":"BRANCH","row":row,"children":children}
        return None

    def run(self):
        if self.n%3:
            return {
                "status":"UNSAT","n":self.n,
                "certificate":{"format":"BABEL41/EXACT-UNSAT-DAG/v1",
                               "type":"DIVISIBILITY",
                               "n":self.n,
                               "rows_sha256":canonical_rows_digest(self.rows)}
            }
        found=self._search(0)
        if found is not None:
            return {"status":"SAT","n":self.n,
                    "witness":found,
                    "witness_true_variables":[v for v in range(self.n)
                                              if (found>>v)&1],
                    "rows_sha256":canonical_rows_digest(self.rows),
                    "states_examined":self.states_examined}
        assert all(x["type"]!="IN_PROGRESS" for x in self.nodes.values())
        proof={
            "format":"BABEL41/EXACT-UNSAT-DAG/v1",
            "type":"COMPLETE_EXACT_ONE_REFUTATION",
            "n":self.n,
            "rows_sha256":canonical_rows_digest(self.rows),
            "root":"0",
            "nodes":self.nodes
        }
        return {
            "status":"UNSAT","n":self.n,
            "certificate":proof,
            "states_examined":self.states_examined,
            "branch_nodes":self.branch_nodes,
            "conflict_nodes":self.conflict_nodes
        }


def solve(rows):
    return ExactDecision(rows).run()


def affine9():
    return tuple(
        tuple(3*i+j for j in range(3)) for i in range(3)
    )+tuple(
        tuple(3*i+j for i in range(3)) for j in range(3)
    )+tuple(
        tuple(3*i+(i+j)%3 for i in range(3)) for j in range(3)
    )


def fano():
    return ((0,1,2),(0,3,4),(0,5,6),(1,3,5),
            (1,4,6),(2,3,6),(2,4,5))


def triple_fano():
    return tuple(tuple(7*b+v for v in row)
                 for b in range(3) for row in fano())


def main():
    from experiments.babel37.fourport_majority_falsifier import U
    from experiments.babel38.fourport_global_balance_dsu import (
        compile_fixture
    )
    from experiments.babel29.multi_splice import build_double_swap
    print("BABEL41 standalone universal decider: call solve(rows)")
    print("SAT/UNSAT on every legal SCL; worst-case EXPONENTIAL, P vs NP OPEN")


if __name__=="__main__":
    main()
