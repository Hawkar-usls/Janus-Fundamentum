#!/usr/bin/env python3
"""TIME-SAT-003C: standalone bounded *DRUP* replay against ORIGINAL CNF.

Trust: separate algorithm from CDCL, but maintained under SAME repo/GitHub.
DRUP additions must be RUP under input and previously checked additions.
Deletions are ignored: retaining more previously logically implied clauses
can only strengthen unit propagation, and remains sound as consequences of
original CNF. This accepts a subset of DRUP proofs; it is NOT a DRAT checker.

No solver call in verification path. Exhaustion reports NOT_VERIFIED_BUDGET;
never promotes a bare UNSAT verdict. For complete DRUP only.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from time import perf_counter


class ProofNotVerified(Exception):
    pass


@dataclass(frozen=True)
class CheckResult:
    status: str
    additions_checked: int
    deletions_ignored: int
    evidence_sha256: str
    complete_empty_clause: bool
    message: str


def unit_propagation_conflict(clauses, negated_clause, deadline):
    """Use no PySAT or solver API: independent Boolean unit refutation."""
    assign={}
    for lit in negated_clause:
        var=abs(lit)
        value=lit>0
        if var in assign and assign[var]!=value:
            return True
        assign[var]=value
    while True:
        if perf_counter()>deadline:
            raise ProofNotVerified("independent unit-replay time budget")
        changed=False
        for clause in clauses:
            pending=0
            lone=0
            satisfied=False
            for lit in clause:
                assigned=assign.get(abs(lit))
                if assigned is None:
                    pending+=1
                    lone=lit
                elif assigned==(lit>0):
                    satisfied=True
                    break
            if satisfied: continue
            if pending==0:return True
            if pending==1:
                var=abs(lone); val=lone>0
                if var in assign and assign[var]!=val:return True
                if var not in assign:
                    assign[var]=val
                    changed=True
        if not changed:return False


def verify_drup(cnf, proof, *, timeout_seconds=10.0, max_steps=10000,
                max_resident_clauses=30000):
    if type(proof) is not list:
        raise ProofNotVerified("proof must be line-list")
    deadline=perf_counter()+timeout_seconds
    known=[]
    for row in cnf:
        clause=tuple(row)
        if any(type(x) is not int or x==0 for x in clause):
            raise ProofNotVerified("invalid source CNF")
        known.append(clause)
    if len(known)>max_resident_clauses:
        raise ProofNotVerified("source proof budget")
    additions=deletions=0
    complete=False
    for line in proof:
        if perf_counter()>deadline or additions>max_steps:
            raise ProofNotVerified("budget exceeded, NOT a certified UNSAT")
        tokens=line.split()
        if not tokens:continue
        deleting=tokens[0]=="d"
        numbers=tokens[1:] if deleting else tokens
        try:vals=[int(x) for x in numbers]
        except ValueError as ex:raise ProofNotVerified("invalid DRUP tokens") from ex
        if not vals or vals[-1]!=0 or 0 in vals[:-1]:
            raise ProofNotVerified("missing terminal zero")
        clause=tuple(vals[:-1])
        if deleting:
            deletions+=1
            continue
        if not unit_propagation_conflict(known,tuple(-l for l in clause),deadline):
            raise ProofNotVerified("non-RUP proof addition")
        additions+=1
        known.append(clause)
        if len(known)>max_resident_clauses:
            raise ProofNotVerified("learned clause proof budget")
        if not clause:
            complete=True
            break
    if not complete:
        raise ProofNotVerified("no independently verified empty clause")
    digest=sha256(json.dumps({"cnf":cnf,"proof":proof},
                              separators=(",",":")).encode()).hexdigest()
    return CheckResult("INDEPENDENT_RUP_REPLAY_PASS",additions,deletions,
                       digest,True,"Independent UCP verified every addition and final empty clause")


def produce_and_check(cnf, *, timeout_seconds=10.0):
    """Glucose4 DRUP on original CNF; same-host separate independent checker."""
    from pysat.solvers import Solver
    with Solver(name="glucose4",bootstrap_with=[list(row) for row in cnf],
                with_proof=True) as s:
        sat=s.solve()
        proof=s.get_proof() if sat is False else None
    if sat:
        return {"solver_status":"SAT","proof_status":"NOT_APPLICABLE_SAT"}
    if proof is None:
        return {"solver_status":"UNSAT","proof_status":"NO_PROOF_FROM_SOLVER"}
    try:
        receipt=verify_drup(cnf,proof,timeout_seconds=timeout_seconds)
        return {"solver_status":"UNSAT","proof_status":receipt.status,
                "certificate_sha256":receipt.evidence_sha256,
                "proof_lines":len(proof),"rup_additions":receipt.additions_checked,
                "deletions":receipt.deletions_ignored}
    except ProofNotVerified as ex:
        return {"solver_status":"UNSAT","proof_status":"NOT_VERIFIED",
                "reason":str(ex),"proof_lines":len(proof)}
