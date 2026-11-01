#!/usr/bin/env python3
"""TIME-SAT-003A/B: direct binary resolution and source-only cost admission.

Four arms are deliberately classical: raw CDCL, direct 2-clause resolvents,
a frozen conservative expected-net-work gate, and previous TIME-SAT-002 gate.
No solved labels or observed test runtimes inform a live decision.

The direct rule (a|b)&(a|-b) => a is standard resolution, NOT novel SAT
technology. Original source CNF always goes to CDCL; an optional redundant
unit needs independent entailment audit before use. Fail closed to raw CDCL.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import asdict, dataclass
from time import perf_counter

from janus_time_sat_partial_001 import _solver, audit_units, canonical_sat_cnf, source_hash
from janus_time_sat_partial_002 import run_arm as legacy_arm
from janus_ufr_001 import verify_model

ARMS=("raw","direct","forecast","legacy_adaptive")
# These are hypothesis constants frozen ahead of the first 003 run, not
# measurements of external CDCL and not a calibrated model.
MIN_N_FORECAST=64
MIN_ROWS_FORECAST=128
MAX_DIRECT_UNITS=32
SAVINGS_PER_OCCURRENCE=16
SCAN_COST_PER_LITERAL=2
AUDIT_COST_PER_UNIT_ROW=4
INSERT_COST_PER_UNIT=8


@dataclass(frozen=True)
class Wedge:
    literal: int
    first_idx: int
    second_idx: int
    companion: int


@dataclass(frozen=True)
class CostForecast:
    admit: bool
    reason: str
    estimated_saved_work_units: int
    estimated_scan_work_units: int
    estimated_audit_work_units: int
    estimated_insert_work_units: int
    estimated_net_work_units: int
    candidate_count: int


def direct_wedges(cnf, n):
    """One linear binary-clause scan; witness clauses are original-indexed.

    Duplicates and tautological (a|-a) clauses do not create a false witness.
    Returning no units is safe; once MAX_DIRECT_UNITS reached we still scan
    the original CNF for auditable feature counts but do not infer more.
    """
    pair_seen={}
    winners={}
    occurrence=[0]*(n+1)
    literal_count=0
    for idx,row in enumerate(cnf):
        literal_count+=len(row)
        for l in row:
            if type(l) is not int or l==0 or abs(l)>n:
                raise ValueError("invalid literal")
            occurrence[abs(l)]+=1
        if len(row)!=2:
            continue
        a,b=row
        if a==b or a==-b: # repeated or tautological: not 2 distinct non-tautological lits
            continue
        for shared,other in ((a,b),(b,a)):
            key=(shared,abs(other))
            mask=1 if other>0 else 2
            previous=pair_seen.get((key,3-mask))
            if previous is not None and shared not in winners:
                first_idx, companion=previous
                winners[shared]=Wedge(shared,first_idx,idx,companion)
            pair_seen.setdefault((key,mask),(idx,other))
    # Explicitly do not inject both x and -x from a contradictory formula;
    # let original CDCL determine UNSAT and provide its own proof.
    both={abs(k) for k in winners if -k in winners}
    selected=tuple(winners[k] for k in sorted(winners,key=lambda k:(abs(k),k<0))
                   if abs(k) not in both)[:MAX_DIRECT_UNITS]
    return selected,literal_count,occurrence


def replay_wedges(cnf,wedges):
    """Independent resolution witness check: original indices and polarity."""
    used=set()
    for w in wedges:
        if type(w.literal) is not int or w.literal==0 or abs(w.literal) in used:
            raise AssertionError("duplicate or invalid direct unit")
        used.add(abs(w.literal))
        if w.first_idx==w.second_idx or min(w.first_idx,w.second_idx)<0 or max(w.first_idx,w.second_idx)>=len(cnf):
            raise AssertionError("invalid original clause positions")
        first=set(cnf[w.first_idx])
        second=set(cnf[w.second_idx])
        if first!={w.literal,w.companion} or second!={w.literal,-w.companion}:
            raise AssertionError("forged resolution witness")
        if abs(w.literal)==abs(w.companion):
            raise AssertionError("tautological fake resolution witness")
    return True


def frozen_forecast(n,cnf,wedges,literal_count,occurrence):
    """Uncalibrated conservative workload proxy, never calls a solver.

    No hidden labels and no historical timing data. 'Work units' are not
    milliseconds; real adoption requires out-of-sample cost calibration.
    """
    proposed=len(wedges)
    saved=SAVINGS_PER_OCCURRENCE*sum(occurrence[abs(w.literal)] for w in wedges)
    scanned=SCAN_COST_PER_LITERAL*literal_count
    audit=AUDIT_COST_PER_UNIT_ROW*len(cnf)*proposed
    inserted=INSERT_COST_PER_UNIT*proposed
    net=saved-scanned-audit-inserted
    admitted=(n>=MIN_N_FORECAST and len(cnf)>=MIN_ROWS_FORECAST
              and proposed>0 and net>0)
    reason=("FORECAST_POSITIVE" if admitted else "NO_RESOLVENTS" if not proposed
            else "TOO_SMALL_TO_AMORTIZE" if n<MIN_N_FORECAST or len(cnf)<MIN_ROWS_FORECAST
            else "EXPECTED_NET_NOT_POSITIVE")
    return CostForecast(admitted,reason,saved,scanned,audit,inserted,net,proposed)


def run_arm(rows,n,kind,*,solver_name,arm,inject_fault=False):
    """All costs charged, no inferred UNSAT, independent SAT verification."""
    if arm not in ARMS:raise ValueError("unsupported TIME-SAT-003 arm")
    if arm=="legacy_adaptive":
        old=legacy_arm(rows,n,kind,solver_name=solver_name,arm="adaptive")
        return dict(old,arm=arm,status=old["answer"],
                    model_independently_verified=old["model_verified"],
                    cdcl_stats=old["native_cdcl_stats"],
                    full_wall_seconds=old["whole_pipeline_seconds"],
                    wedge_count=0,forecast=None,witnesses=[],audit_count=old["independent_unit_checks"],
                    fault_fallback=False)
    start=perf_counter()
    original=tuple(tuple(r) for r in rows)
    cnf=canonical_sat_cnf(original,n,kind)
    wedges=()
    forecast=None
    skipped="raw_control"
    units=()
    fault_fallback=False
    if arm!="raw":
        wedges,literal_count,occurrence=direct_wedges(cnf,n)
        replay_wedges(cnf,wedges)
        if arm=="forecast":
            forecast=frozen_forecast(n,cnf,wedges,literal_count,occurrence)
        perform=(arm=="direct" or bool(forecast and forecast.admit))
        skipped=("forecast_rejected" if not perform else "not_skipped")
        if perform:
            try:
                if inject_fault:raise TimeoutError("injected direct extraction failure")
                units=tuple(w.literal for w in wedges)
            except (TimeoutError,MemoryError):
                units=()
                fault_fallback=True
                skipped="fault_fallback"
    # Independent entailment challenges for EACH derived unit. Audits are
    # separately costed; failure is fatal and not swallowed as a timeout.
    audits=audit_units(cnf,units) if units else 0
    tsolve=perf_counter()
    with _solver(solver_name,cnf) as solver:
        for u in units: solver.add_clause([u])
        sat=solver.solve()
        model=solver.get_model() if sat else None
        cdcl=solver.accum_stats()
    solve_s=perf_counter()-tsolve
    if sat is None:raise AssertionError("external CDCL undecided")
    if sat:
        candidate={abs(x):x>0 for x in model or ()}
        if not verify_model(original,candidate,kind):
            raise AssertionError("SAT model invalid under original constraints")
    return {
      "arm":arm,"solver":solver_name,
      "status":"SAT" if sat else "UNSAT",
      "model_independently_verified":bool(sat),
      "unsat_portable_proof":"NOT_PRODUCED_IN_THIS_CALL",
      "input_sha256":source_hash(cnf,n),
      "full_wall_seconds":perf_counter()-start,
      "external_cdcl_seconds":solve_s,
      "wedge_count":len(wedges),
      "witnesses":[asdict(w) for w in wedges],
      "forecast":asdict(forecast) if forecast else None,
      "derived_units":list(units),"audit_count":audits,
      "fault_fallback":fault_fallback,"admission_reason":skipped,
      "cdcl_stats":cdcl,
    }
