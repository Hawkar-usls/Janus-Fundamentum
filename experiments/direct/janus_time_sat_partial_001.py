#!/usr/bin/env python3
"""TIME-SAT-PARTIAL-001: compare source-only partial consistency with CDCL.

The *baseline and augmented variants use the same strong external SAT solver*,
identical original CNF and search input. Added unit clauses must be entailed
by the original CNF. Classical forward-time inference only; no physics claim.

Bounded, deterministic forward unit support + backward/goal-first failed
literal probing on partial states. A failed/incomplete probe is NEVER accepted
as a failed literal. A third independent CDCL assumption test checks every
additional derived literal, fully charged to the augmented pipeline.

Public deterministic instances are NOT external blinded instances; no
promotion of C023, no P=NP, no portable UNSAT proof from this program.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from time import perf_counter
import json

from janus_novikov_002 import (
    UNSET, Exhausted, ProbeQuota, Meter, propagate, validated,
)
from janus_ufr_001 import verify_model


def canonical_sat_cnf(rows, n: int, kind: str):
    """Native Exact-One -> pairwise at-most-one + at-least-one over LITERALS.

    Negated and duplicate literals are deliberately left intact. Their
    multiplicity is crucial: [x,x] must be impossible for Exact-One.
    """
    source=validated(rows,n,kind)
    if kind=="SAT":
        return source
    cnf=[]
    for row in source:
        cnf.append(tuple(row))
        for i in range(len(row)):
            for j in range(i+1,len(row)):
                cnf.append((-row[i],-row[j]))
    return tuple(cnf)


def source_hash(cnf,n):
    return sha256(json.dumps({"n":n,"cnf":cnf},
           sort_keys=True,separators=(",",":")).encode()).hexdigest()


@dataclass(frozen=True)
class Preparation:
    units: tuple[int,...]
    stage: str
    original_clause_visits: int
    probing_clause_visits: int
    explored_literal_assumptions: int
    rejected_probe_values: int
    quota_exhausted: bool
    input_contradiction_detected: bool
    seconds: float


def _units(values):
    return tuple((i+1 if v else -(i+1))
                 for i,v in enumerate(values) if v != UNSET)


def prepare(cnf, n:int, *, stage:str, max_visits:int=140000,
            probe_share:float=0.05, time_limit:float=4.0,
            max_goal_vars:int=8) -> Preparation:
    """No unverified constraint derived from an input-only heuristic.

    Stage 'raw': no preprocessing.
    Stage 'forward': ordinary deterministic unit propagation.
    Stage 'bidirectional': same forward stage, then goal-ordered double
    hypothetical assignment with unit-propagation consistency. A literal is
    added only when the negation causes a concrete conflict. Different from
    a physical backwards-in-time channel.
    """
    start=perf_counter()
    if stage not in ("raw","forward","bidirectional"):
        raise ValueError("invalid partial-preparation stage")
    if (type(n) is not int or n<1 or n>240
            or type(max_visits) is not int or max_visits<1
            or type(probe_share) not in (int,float)
            or isinstance(probe_share,bool) or not 0<=probe_share<=0.25
            or type(max_goal_vars) is not int or not 0<=max_goal_vars<=32
            or not 0.01<=time_limit<=30):
        raise ValueError("invalid bounded preparation configuration")
    if stage=="raw":
        return Preparation((),"raw",0,0,0,0,False,False,perf_counter()-start)
    meter=Meter(max_nodes=1000000,max_visits=max_visits,
                deadline=perf_counter()+time_limit,
                max_probe_visits=int(max_visits*probe_share))
    values=[UNSET]*n
    initial_conflict=False
    try:
        if not propagate(cnf,values,"SAT",meter):
            initial_conflict=True
    except Exhausted:
        # An interrupted initial fixed point does not authorize the partially
        # computed units, because they have not passed independent checking.
        return Preparation((),"FORWARD_BUDGET_EXHAUSTED",meter.clause_visits,
                           0,0,0,False,False,perf_counter()-start)
    if stage=="bidirectional" and not initial_conflict and max_goal_vars:
        score=[0]*n
        clause_by_scope=[]
        for row in cnf:
            scope={abs(l)-1 for l in row if values[abs(l)-1]==UNSET}
            if not scope:
                continue
            clause_by_scope.append((len(scope),row,scope))
            weight=max(1,128//max(1,len(scope)))
            for i in scope:
                score[i]+=weight
        # Backward from tightest constraint goals: deterministic tie-break.
        goals=sorted((i for i in range(n) if values[i]==UNSET),
                     key=lambda i:(-score[i],i))[:max_goal_vars]
        for v in goals:
            if values[v]!=UNSET or meter.probing_disabled:
                continue
            possible=[]
            aborted=False
            for bit in (0,1):
                probe=values[:]
                probe[v]=bit
                meter.probes+=1
                meter.probing=True
                try:
                    consistent=propagate(cnf,probe,"SAT",meter)
                except ProbeQuota:
                    aborted=True
                    break
                except Exhausted:
                    aborted=True
                    meter.probing_disabled=True
                    break
                finally:
                    meter.probing=False
                if not consistent:
                    meter.conflict_probes+=1
                possible.append(consistent)
            if aborted:
                break
            if not any(possible):
                initial_conflict=True
                break
            if possible[0] != possible[1]:
                values[v]=int(possible[1])
                try:
                    if not propagate(cnf,values,"SAT",meter):
                        initial_conflict=True
                        break
                except Exhausted:
                    # Drop ALL units on an interrupted consistency derivation.
                    return Preparation((),"PREPARATION_BUDGET_EXHAUSTED",
                           meter.clause_visits,meter.probe_clause_visits,
                           meter.probes,meter.conflict_probes,
                           meter.probing_disabled,False,perf_counter()-start)
    # An initial or two-sided conflict is not a portable UNSAT proof. Let
    # strong CDCL solve the original formula instead of trusting our claim.
    units=() if initial_conflict else _units(values)
    return Preparation(units,stage,meter.clause_visits,
                       meter.probe_clause_visits,meter.probes,
                       meter.conflict_probes,meter.probing_disabled,
                       initial_conflict,perf_counter()-start)


def _solver(name,cnf):
    from pysat.solvers import Solver
    return Solver(name=name, bootstrap_with=[list(row) for row in cnf])


def audit_units(cnf, units:tuple[int,...]) -> int:
    """Every proposed clause is independently checked via a second CDCL.

    Reusing the original formula as a trustworthy source, prove CNF |= unit
    by solving CNF + NOT(unit). This is redundant inference, not cheating.
    All time is included in the augmented pipeline's cost.
    """
    checked=0
    if len(set(abs(x) for x in units))!=len(units):
        raise AssertionError("duplicate variable in derived unit set")
    with _solver("cadical195",cnf) as independent:
        for unit in units:
            if independent.solve(assumptions=[-unit]) is not False:
                raise AssertionError("unsound partial consistency unit: "+str(unit))
            checked+=1
    return checked


def one_run(rows,n:int,kind:str, *, solver_name:str, stage:str,
            max_visits:int=140000, probe_share:float=0.05,
            max_goal_vars:int=8):
    """Cold-start full-pipeline wall time: normalize, preprocess, audit, CDCL."""
    start=perf_counter()
    cnf=canonical_sat_cnf(rows,n,kind)
    prep=prepare(cnf,n,stage=stage,max_visits=max_visits,
                 probe_share=probe_share,max_goal_vars=max_goal_vars)
    audits=audit_units(cnf,prep.units) if prep.units else 0
    tsolve=perf_counter()
    with _solver(solver_name,cnf) as solver:
        for lit in prep.units:
            solver.add_clause([lit])
        answer=solver.solve()
        external_model=solver.get_model() if answer else None
        stats=solver.accum_stats()
    solve_time=perf_counter()-tsolve
    if answer:
        values={abs(v):v>0 for v in external_model or ()}
        # Strong solver model is never accepted unverified.
        if not verify_model(rows,values,kind):
            raise AssertionError("external SAT solver produced invalid model")
    if answer is None:
        raise AssertionError("unbounded CDCL solver returned UNKNOWN")
    return {
        "answer":"SAT" if answer else "UNSAT",
        "model_independently_verified":bool(answer),
        "portable_unsat_proof":"NOT_PRODUCED",
        "full_pipeline_seconds":perf_counter()-start,
        "external_solver_only_seconds":solve_time,
        "preprocess_seconds":prep.seconds,
        "derived_units":list(prep.units),
        "independent_entailment_audits":audits,
        "probe_assumptions":prep.explored_literal_assumptions,
        "failed_literal_propagation_conflicts":prep.rejected_probe_values,
        "preprocess_clause_visits":prep.original_clause_visits,
        "probe_clause_visits":prep.probing_clause_visits,
        "probe_quota_exhausted":prep.quota_exhausted,
        "preprocess_stage":prep.stage,
        "input_conflict_seen_by_preprocessor":prep.input_contradiction_detected,
        "CDCL_statistics":stats,
    }
