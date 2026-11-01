#!/usr/bin/env python3
"""JANUS TIME-SAT-PARTIAL-002 — source-only *admission* of expensive SAT probes.

Safe experimental preprocessor: gate may skip, never delete clauses/branches.
Admission uses only ORIGINAL encoded CNF, not a target model, timing labels,
solver answers, or a previous probe outcome. Thresholds frozen in this source.

A sound unit is introduced ONLY after (a) a genuine failed-literal proof via
ordinary Boolean propagation, and (b) independent CDCL entailment validation
against unchanged source CNF. Failure/partial budget -> original external CDCL.

Research only, not a novel physical "temporal" effect or production C023.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Iterable

from janus_time_sat_partial_001 import (
    _solver, audit_units, canonical_sat_cnf, prepare, source_hash,
)
from janus_ufr_001 import verify_model

ARMS = ("raw","feature_only","unconditional","adaptive")
MAX_N_ADMISSION = 32
MAX_CLAUSES_ADMISSION = 512
MIN_BINARY_PAIRS = 1
MIN_BINARY_DENSITY = 0.25
VISITS_BUDGET = 140_000
PROBE_SHARE = 0.05
GOAL_MAX = 8


@dataclass(frozen=True)
class GateReceipt:
    admitted: bool
    reason: str
    n: int
    clauses: int
    unit_clauses: int
    binary_clauses: int
    short_clauses: int
    binary_density: float
    occurrence_imbalance: float
    binary_wedge_count: int
    binary_wedge_targets: tuple[int, ...]


def cheap_features(cnf: tuple[tuple[int, ...], ...], n: int) -> GateReceipt:
    """Linear-ish bounded input scan, no SAT/UNSAT work, no leaked labels.

    A wedge (a OR b) & (a OR -b) implies a. It is intentionally an
    EASY source-only signal that may or may not justify doing *more* work.
    The gate does not add a directly inferred unit; tests compare its value.
    """
    if type(n) is not int or n < 1 or n > 240:
        raise ValueError("invalid variable count")
    unit=binary=short=0
    pos=[0]*n
    neg=[0]*n
    binary_signs:dict[tuple[int,int],int]={}
    for row in cnf:
        if len(row)==1: unit+=1
        if len(row)==2: binary+=1
        if 0<len(row)<=3: short+=1
        for lit in row:
            if type(lit) is not int or lit==0 or abs(lit)>n:
                raise ValueError("invalid encoded literal")
            (pos if lit>0 else neg)[abs(lit)-1]+=1
        if len(row)==2:
            a,b=row
            if a == -b or a == b:
                continue
            for shared,other in ((a,b),(b,a)):
                key=(shared,abs(other))
                binary_signs[key]=binary_signs.get(key,0)|(1 if other>0 else 2)
    targets=tuple(sorted({key[0] for key,mask in binary_signs.items() if mask==3},
                         key=lambda x:(abs(x),x<0)))
    density=binary/max(1,len(cnf))
    total=sum(pos)+sum(neg)
    imbalance=sum(abs(p-q) for p,q in zip(pos,neg))/max(1,total)
    valid=(n<=MAX_N_ADMISSION and len(cnf)<=MAX_CLAUSES_ADMISSION
           and unit==0 and len(targets)>=MIN_BINARY_PAIRS
           and density>=MIN_BINARY_DENSITY)
    reason=("WEDGE_ADMITTED" if valid else
            "HAS_UNIT_CLAUSES" if unit else
            "INSTANCE_TOO_LARGE" if n>MAX_N_ADMISSION or len(cnf)>MAX_CLAUSES_ADMISSION else
            "NO_BINARY_WEDGE" if not targets else
            "BINARY_DENSITY_BELOW_THRESHOLD")
    return GateReceipt(valid,reason,n,len(cnf),unit,binary,short,
                       density,imbalance,len(targets),targets)


def run_arm(rows: Iterable[Iterable[int]], n:int, kind:str, *,
            solver_name:str, arm:str, fault_probe:bool=False) -> dict:
    """Cold same-CNF CDCL, all stage and entailment work inside wall timer.

    fault_probe simulates a preparation-only runtime fault. A partial/failed
    preprocessing step must not affect the original CDCL verdict.
    Independent entailment failure is NOT swallowed as a normal timeout.
    """
    if arm not in ARMS: raise ValueError("invalid arm")
    start=perf_counter()
    original=tuple(tuple(row) for row in rows)
    cnf=canonical_sat_cnf(original,n,kind)
    features=cheap_features(cnf,n) if arm!="raw" else None
    admitted=bool(features and features.admitted)
    prep=None
    fallback_reason=None
    should_probe=arm=="unconditional" or (arm=="adaptive" and admitted)
    if should_probe:
        try:
            if fault_probe:
                raise TimeoutError("synthetic interrupted probe")
            prep=prepare(cnf,n,stage="bidirectional",max_visits=VISITS_BUDGET,
                         probe_share=PROBE_SHARE,max_goal_vars=GOAL_MAX)
            if prep.stage!="bidirectional":
                fallback_reason="PREPROCESS_INCOMPLETE"
                prep=None
        except (TimeoutError,MemoryError) as err:
            fallback_reason=type(err).__name__
            prep=None
    units=prep.units if prep is not None else ()
    independent_unit_checks=audit_units(cnf,units) if units else 0
    ts=perf_counter()
    with _solver(solver_name,cnf) as solver:
        for lit in units:
            solver.add_clause([lit])
        sat=solver.solve()
        model=solver.get_model() if sat else None
        stats=solver.accum_stats()
    solver_time=perf_counter()-ts
    if sat is None: raise AssertionError("external SAT returned unknown")
    if sat:
        assignment={abs(x):x>0 for x in (model or [])}
        if not verify_model(original,assignment,kind):
            raise AssertionError("external solver produced incorrect model")
    return {
        "answer":"SAT" if sat else "UNSAT",
        "model_verified":bool(sat),
        "unsat_portable_proof":"NOT_PRODUCED",
        "source_sha256":source_hash(cnf,n),
        "arm":arm,"engine":solver_name,
        "whole_pipeline_seconds":perf_counter()-start,
        "cold_external_solver_seconds":solver_time,
        "gate":asdict(features) if features is not None else None,
        "probe_ran":should_probe,
        "preprocessor_fallback":fallback_reason,
        "derived_units":list(units),
        "independent_unit_checks":independent_unit_checks,
        "probe_clause_visits":prep.probing_clause_visits if prep else 0,
        "total_preparation_clause_visits":prep.original_clause_visits if prep else 0,
        "quota_exhausted":prep.quota_exhausted if prep else False,
        "native_cdcl_stats":stats,
    }
