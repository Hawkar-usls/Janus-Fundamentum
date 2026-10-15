#!/usr/bin/env python3
"""R5 E4.7 bounded connected UNSAT BASE multi-z scout.

Search 96 reproducible connected 36x36 legal SCL sources generated
from source-preserving cubic incidence switches, NOT 2-cover flips.
Candidate is accepted as a MULTI_Z SOURCE only if:
- connected, legal square 3-uniform/3-regular/linear SCL;
- independently exhaust ALL parity GF2 words to prove UNSAT;
- exact rational rank<=n-2 (modular lower-bound prescreen);
- enumerate ALL nonzero GF2 kernel z and DOUBLE-CHECK Y_z by
  residual clean Exact Cover vs squarefree mask DP;
- AT LEAST TWO distinct z have independently verified ternary y.

The necessary Q-nullity theorem is NOT a sufficient filter.
No SAT/UNSAT status inferred from timeouts or unknown cases.
A multi-z SOURCE is NOT automatically a same-H-lift, let alone
a degree-2 depth1 spectral SAT/UNSAT twin. That is a separate gate.
"""
from collections import Counter
import argparse,json,random

from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,fingerprint
)
from r5_connected_coverage_breaker_20261015 import (
    make_connected,connected_scl_components
)
from r5_joint_spectral_anchor_twins_20261015 import (
    unrestricted_connected_mutation
)
from r5_cover_twins_independent_audit_20261015 import (
    independently_enumerate_parity
)
from r5_e47_base_z_rational_audit_20261016 import (
    rational_rref,low_pivot_kernel,residual_two_ways
)


def mod_rank(A,prime=65521):
    n=len(A)
    M=[list(row) for row in A]
    pivot=0
    for j in range(n):
        i=next((i for i in range(pivot,n)
                if M[i][j]%prime),None)
        if i is None:continue
        M[pivot],M[i]=M[i],M[pivot]
        inv=pow(M[pivot][j],-1,prime)
        for a in range(pivot+1,n):
            if M[a][j]:
                factor=M[a][j]*inv%prime
                for b in range(j,n):
                    M[a][b]=(M[a][b]-factor*M[pivot][b])%prime
        pivot+=1
    return pivot


def survey(seed=20261016,trials=96):
    if not 1<=trials<=160:raise ValueError("bounded scan 1..160")
    counters=Counter()
    candidates=[]
    first_positive=None
    rng=random.Random(seed)
    for i in range(trials):
        source,_,_=make_connected(2,seed+(i%3))
        proposal,moves=unrestricted_connected_mutation(
            source,rng,steps=4+(i%13))
        counters["generated"]+=1
        if not moves:
            counters["NO_VALID_MUTATION"]+=1
            continue
        proposal=validate_scl(proposal)
        if len(proposal)!=36 or len(connected_scl_components(proposal))!=1:
            counters["REJECT_LEGALITY_OR_CONNECTIVITY"]+=1
            continue
        oracle=independently_enumerate_parity(proposal,cap=1<<12)
        if oracle["status"]!="EXACT":
            counters["UNKNOWN_ORACLE_RESOURCE_LIMIT"]+=1
            continue
        if oracle["sat_count"]>0:
            counters["REJECT_SAT_BASE"]+=1
            continue
        counters["CERTIFIED_UNSAT"]+=1
        A=[[int(v in row) for v in range(36)] for row in proposal]
        mod=mod_rank(A)
        # rank_(mod p) is a LOWER bound on rank_Q.
        # Necessary multi-z condition is rank_Q<=n-2=34.
        # A modular rank EQUAL to 34 is *not* sufficient
        # for rejection; it must go through exact Q rank!
        if mod>=35:
            counters["REJECT_RANK_MOD_PRIME_GE35"]+=1
            continue
        rank,pivots,pr,qbasis=rational_rref(A)
        assert rank>=mod
        if rank>34:
            counters["REJECT_EXACT_Q_NULLITY0"]+=1
            continue
        if rank==34:
            counters["REJECT_EXACT_Q_NULLITY1"]+=1
            continue
        counters["Q_NULLITY_AT_LEAST2"]+=1
        masks=[sum(1<<v for v in row) for row in proposal]
        gf2rank,basis=low_pivot_kernel(masks,36)
        assert gf2rank==36-oracle["d"]
        if oracle["d"]>12:
            counters["UNKNOWN_KERNEL_BUDGET"]+=1
            continue
        allz=[0]
        for b in basis:
            allz.extend([z^b for z in tuple(allz)])
        relevant=[]
        for z in sorted(allz):
            if not z:continue
            r=residual_two_ways(proposal,z)
            if r["Y_count"]:
                relevant.append({
                    "z_decimal":str(z),"z_weight":z.bit_count(),
                    "Y_z_count":r["Y_count"],
                    "y2_columns":r["Y_exact_covers"]
                })
        counters["FULL_Z_AUDITED"]+=1
        record={
            "candidate_index":i,
            "source_sha256":fingerprint(proposal),
            "Q_rank":rank,"Q_nullity":36-rank,
            "GF2_nullity":oracle["d"],
            "GF2_words_certifying_UNSAT":oracle["checked"],
            "total_nonzero_z":len(allz)-1,
            "relevant_z":relevant,
            "relevant_z_count":len(relevant)}
        candidates.append(record)
        counters["RELEVANT_Z_"+str(len(relevant))]+=1
        if len(relevant)>=2:
            # Actual base rows, not merely a name/seed, are part
            # of the independently replayable certificate.
            record["base_rows"]=[list(r) for r in proposal]
            first_positive=record
            break
    return {
        "gate":"MULTI_Z_CONNECTED_UNSAT_BASE_SCOUT",
        "seed":seed,"budget":trials,
        "actual_generated":counters["generated"],
        "counts":dict(counters),
        "exact_Qnullity_ge2_candidates":candidates,
        "first_multi_z_UNSAT_source":first_positive,
        "status":("FOUND_CERTIFIED_MULTI_Z_SOURCE" if first_positive
                  else "NOT_FOUND_IN_BOUNDED_CONNECTED_SAMPLE"),
        "SAT_lift_and_joint_CYCLE_feasibility":"NOT_ESTABLISHED",
        "depth1_spectral_twins":"NOT_ESTABLISHED",
        "universal_SCL_poly":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--trials",type=int,default=96)
    args=p.parse_args()
    print(json.dumps(survey(trials=args.trials),indent=2,sort_keys=True))
