#!/usr/bin/env python3
"""Resource-simplex refinement of the JANUS v0.5 exact abstract verifier.

Instead of forgetting correlation between output clause and literal caps, each
abstract transition carries the simultaneous constraints
    m<=M, L<=Lambda, 1+m+L<=S,
where S is the proven raw_units cap for that transition.
This is theorem-side abstraction only; runtime semantics are unchanged.
"""

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


def add_box(boxes: list[tuple[int,int,int]], M: int, L: int, S: int) -> None:
    if M < 7 or L < 14 or S < 22:
        return
    if any(a>=M and b>=L and c>=S for a,b,c in boxes):
        return
    boxes[:] = [(a,b,c) for a,b,c in boxes if not (M>=a and L>=b and S>=c)]
    boxes.append((M,L,S))


def verify_N_simplex(N: int, previous_frontier: int) -> dict:
    assert previous_frontier == N-1
    cap=N*N
    roots=A.hard_roots(N)
    max_n=max(roots,default=A.TAIL_N)
    boxes={n:[] for n in range(7,max_n+1)}
    rootsets={n:set(rows) for n,rows in roots.items()}
    checked_states=0; checked_transitions=0
    worst_raw=-1; worst=None; layers={}

    G.activate()
    for n in range(max_n,6,-1):
        candidates=set(rootsets.get(n,set()))
        bs=boxes[n]
        maxM=max((M for M,_,_ in bs),default=0)
        for m in range(7,maxM+1):
            # Union of boxes: choose the best simultaneous L allowance available
            # at this exact m, respecting both L<=Lambda and 1+m+L<=S.
            Lcap=max((min(Lb,Sb-1-m) for M,Lb,Sb in bs if M>=m),default=-1)
            if Lcap<0: continue
            Llo=max(2*m,n,previous_frontier-n-m)
            Lhi=min(Lcap,n*m,cap-1-m)
            if Llo>Lhi: continue
            for L in range(Llo,Lhi+1):
                dlo,dhi=A.degree_interval(n,m,L)
                if dlo<=dhi: candidates.add((m,L))
        layers[n]=len(candidates)

        for m,L in sorted(candidates):
            checked_states+=1
            dlo,dhi=A.degree_interval(n,m,L)
            for d in range(dlo,dhi+1):
                for p in range(0,d//2+1):
                    q=d-p; checked_transitions+=1
                    raw,M,Lb,R=G.transfer_bounds_global(n,m,L,d,p,q)
                    if raw>worst_raw:
                        worst_raw=raw
                        worst={"state":[n,m,L],"d":d,"p":p,"q":q,"raw_bound":raw,"m_out_bound":M,"L_out_bound":Lb,"R":R}
                    if raw>cap:
                        return {"N":N,"status":"ABSTRACT_BOUND_OPEN","cap":cap,"checked_states":checked_states,"checked_transitions":checked_transitions,"layer_counts":layers,"first_open":worst,"P_VS_NP":"OPEN"}
                    for n2 in range(7,n):
                        add_box(boxes[n2],M,Lb,raw)

    return {"N":N,"status":"PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_RESOURCE_SIMPLEX_OVERAPPROX","cap":cap,"root_states":sum(len(v) for v in roots.values()),"checked_states":checked_states,"checked_transitions":checked_transitions,"layer_counts":layers,"box_counts":{str(n):len(boxes[n]) for n in boxes},"worst_raw_bound":worst_raw,"worst_witness":worst,"P_VS_NP":"OPEN"}


def selftest() -> None:
    G.verify_N58_open_repair()
    result=verify_N_simplex(58,57)
    print(f"RESOURCE_SIMPLEX_N58_STATUS={result['status']}")
    print(f"RESOURCE_SIMPLEX_N58_CHECKED_STATES={result['checked_states']}")
    print(f"RESOURCE_SIMPLEX_N58_CHECKED_TRANSITIONS={result['checked_transitions']}")
    if result['status']!='PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_RESOURCE_SIMPLEX_OVERAPPROX':
        print(f"RESOURCE_SIMPLEX_N58_FIRST_OPEN={result['first_open']}")
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        raise AssertionError(result)
    print(f"RESOURCE_SIMPLEX_N58_WORST_RAW={result['worst_raw_bound']}")
    print('RESOURCE_SIMPLEX_N58=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    selftest()
