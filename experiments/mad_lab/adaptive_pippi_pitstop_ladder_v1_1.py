#!/usr/bin/env python3
"""JANUS PIPPI adaptive ladder v1.1 bootstrap verifier correction.

The v1.0 harness correctly required independent UNSAT verification, but applied
`solve_2sat_exact` to the historical width-5 50:50 bootstrap witnesses.  That
solver correctly returns None outside the 2-CNF class.  v1.1 preserves v1.0
race semantics and replaces only the root episode admission gate:

- 2-CNF track formulas: exact 2-SAT verification.
- historical n=7 width-5 bootstrap: exhaustive 2^n truth-table verification.

No historical UNSAT label is trusted without an independent check.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1


def brute_force_unsat(cnf: base.CNF) -> bool:
    vs=list(base.vars_of(cnf))
    if len(vs)>16:
        raise AssertionError("truth-table fallback intentionally bounded to <=16 variables")
    pos={v:i for i,v in enumerate(vs)}
    for mask in range(1<<len(vs)):
        sat=True
        for clause in cnf:
            clause_sat=False
            for lit in clause:
                bit=(mask>>pos[abs(lit)])&1
                clause_sat |= bool(bit) if lit>0 else not bool(bit)
                if clause_sat: break
            if not clause_sat:
                sat=False; break
        if sat:
            return False
    return True


def exact_root_episode_v1_1(cnf: base.CNF, d: int, seed: int, source: str, stage_serial: int) -> dict[str,Any]:
    fp=base.fingerprint(cnf); vs=list(base.vars_of(cnf)); root_units=base.state_units(cnf)
    sat2=base.solve_2sat_exact(cnf)
    if sat2 is None:
        assert brute_force_unsat(cnf), (source,seed,"bootstrap unexpectedly SAT")
        independent_unsat_verifier="EXHAUSTIVE_TRUTH_TABLE"
    else:
        assert sat2[0] is False
        independent_unsat_verifier="EXACT_2SAT"
    tokens=[]; raw=[]; pairs=[]; after=[]
    for p in vs:
        tokens.append(v1.candidate_tokens(cnf,p))
        out,st=base.eliminate_var_capped(cnf,p,v1.UNBOUNDED_CAP)
        assert out is not None and base.verify_elimination_transition(cnf,p,out,v1.UNBOUNDED_CAP)
        raw.append(int(st['raw_units'])); pairs.append(int(st.get('pairs',0))); after.append(base.state_units(out))
    order=sorted(range(len(vs)),key=lambda i:(raw[i],v1.stable_hash(tokens[i])))
    qidx=max(0,min(len(vs)-1,int(0.30*(len(vs)-1))))
    cap=max(root_units,sorted(raw)[qidx])
    mn,mx=min(raw),max(raw)
    rel=[0.0 if mx==mn else (x-mn)/(mx-mn) for x in raw]
    best={i for i,x in enumerate(raw) if x==mn}; safe={i for i,x in enumerate(raw) if x<=cap}
    return {
        'd':d,'seed':seed,'source':source,'stage_serial':stage_serial,'fingerprint':fp,'cnf':cnf,
        'vars':vs,'tokens':tokens,'raw':raw,'pair_labels':pairs,'after_units':after,'raw_relative':rel,
        'best_indices':sorted(best),'safe_indices':sorted(safe),'local_stress_cap':cap,'root_units':root_units,
        'raw_span':mx-mn,'oracle_root_order':order,'independent_unsat_verifier':independent_unsat_verifier,
    }


def main()->int:
    v1.exact_root_episode=exact_root_episode_v1_1
    return v1.main()


if __name__=='__main__':
    raise SystemExit(main())
