#!/usr/bin/env python3
"""R5 27-state transfer certificate for the infinite Isaacs flower family.

Three colours on each of the three edges entering one flower block
constitute a boundary state in C={0,1,2}^3 (27 possibilities).
The unique per-block compatibility condition is that there exist
spoke colours p_b,p_c,p_d forming a permutation of all three colours,
where for every lane j the three incident edge colours
(incoming[j],spoke[j],outgoing[j]) form a permutation.
Thus a Boolean 27x27 transfer T describes an arbitrary block.

The seam of the Isaacs flower is twisted: (b,c,d) -> (b,d,c).
For length k there is a colouring iff there exists a boundary
state s and terminal t with T^k[s,t]=1 and s=twist(t).
The entire proof is independent of exponential Boolean branching.

Stronger uniform theorem over ALL odd k>=5:
* constant triple -> no transition;
* all-distinct triple -> all-distinct same coordinate-parity,
  while twist REVERSES coordinate-parity;
* two-equal triple -> singleton colour invariant, repeated colour
  flips at every block; twist PRESERVES repeated colour;
  odd number of flips contradicts the twisted seam.
Every one of the finite 27^2 candidate transitions is checked.
The three cases partition all 27 states, proving zero trace
symbolically for all odd k, not only for k=5/7.

This original-SCL UNSAT certificate is valid ONLY after a complete
comparison to the authenticated make_scl(flower(k)) source rows.
It is a linear-time constant-state family-specific decision, NOT
a universal polynomial algorithm for arbitrary SCL sources.
"""
from __future__ import annotations
from itertools import permutations,product
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl
from r5_universal_exact_support_residual_dag_attack import validate_sparse

COLOURS=(0,1,2)
STATES=tuple(product(COLOURS,repeat=3))
STATE_INDEX={state:i for i,state in enumerate(STATES)}
PERMS=set(permutations(COLOURS))


def twist(state):
    return (state[0],state[2],state[1])


def parity(state):
    assert len(set(state))==3
    return sum(state[i]>state[j] for i in range(3) for j in range(i+1,3))%2


def local_allowed(incoming,outgoing):
    """Independent existential local spoke enumeration, ONLY 6 options."""
    return any(all(tuple(sorted((incoming[j],p[j],outgoing[j])))==COLOURS
                   for j in range(3)) for p in PERMS)


def construct_transfer():
    T=tuple(tuple(int(local_allowed(s,t)) for t in STATES) for s in STATES)
    assert sum(map(sum,T))==48
    return T


def verify_uniform_odd_invariant(T):
    """Inductive proof by exhaustively checking the constant local alphabet."""
    for i,s in enumerate(STATES):
        for j,t in enumerate(STATES):
            assert T[i][j] == int(local_allowed(s,t))
            if not T[i][j]:continue
            category=len(set(s))
            assert category in (2,3),"all-equal state gained an illegal transition"
            assert len(set(t))==category
            if category==3:
                # Moving one block preserves orientation. The seam reverses it.
                assert parity(t)==parity(s)
                assert parity(twist(t))!=parity(t)
            else:
                singleton=lambda x: next(c for c in COLOURS if x.count(c)==1)
                repeated=lambda x: next(c for c in COLOURS if x.count(c)==2)
                assert singleton(s)==singleton(t)
                assert repeated(s)!=repeated(t)
                assert repeated(twist(t))==repeated(t)
    assert all(not any(T[STATE_INDEX[s]]) for s in STATES if len(set(s))==1)
    return True


def boolean_power_paths(T,k):
    """Independent bounded 27-state path reachability, O(k * 27^3)."""
    size=len(STATES)
    reachable=[[int(i==j) for j in range(size)] for i in range(size)]
    for _ in range(k):
        nxt=[[0]*size for _ in range(size)]
        for i in range(size):
            for middle in range(size):
                if reachable[i][middle]:
                    for j in range(size):
                        if T[middle][j]:nxt[i][j]=1
        reachable=nxt
    return reachable


def twisted_accepted_states(T,k):
    path=boolean_power_paths(T,k)
    return tuple((s,t) for s in STATES for t in STATES
                 if s==twist(t) and path[STATE_INDEX[s]][STATE_INDEX[t]])


def verify_authenticated_flower_unsat(rows,n,k):
    assert type(k) is int and k>=5 and k%2==1
    source,n_source,_,_=make_scl(flower(k))
    assert n==n_source and n==18*k
    assert validate_sparse(rows,n)==source, "source not an EXACT flower Holyer SCL"
    T=construct_transfer()
    assert verify_uniform_odd_invariant(T)
    # The invariant establishes for EVERY ODD k that there can be
    # no twisted closed path; the finite check independently verifies.
    assert not twisted_accepted_states(T,k)
    return True


def main():
    T=construct_transfer()
    assert verify_uniform_odd_invariant(T)
    print("FLOWER_27_STATE_TRANSFER_LOCAL_COMPATIBILITY=48_OF_729",flush=True)
    print("FLOWER_ALL_ODD_K_SYMBOLIC_TRANSFER_PARITY_UNSAT=PROVED",
          flush=True)
    for k in (5,7,9,11,13):
        rows,n,_,_=make_scl(flower(k))
        assert verify_authenticated_flower_unsat(rows,n,k)
        accepted=twisted_accepted_states(T,k)
        assert not accepted
        print(f"ISAACS_J{k}_AUTHENTICATED_SOURCE_SCL{n}_"
              "TRANSFER_UNSAT=SOURCE_REPLAYED",flush=True)

    # Positive transfer controls: the same block admits paths with
    # twisted closure for even k (although flower() intentionally
    # restricts graph construction to odd snarks).
    for k in (2,4,6,8):
        assert twisted_accepted_states(T,k)
        print(f"FLOWER_EVEN_{k}_TRANSFER_SAT=PASS",flush=True)

    # Source authenticity is indispensable. One flipped original
    # Exact-One row must invalidate family-proof authorization.
    rows,n,_,_=make_scl(flower(5))
    tampered=list(rows)
    altered=list(tampered[0]); altered[-1]=max(
        v for v in range(n) if v not in altered
    )
    tampered[0]=tuple(sorted(altered))
    try:
        verify_authenticated_flower_unsat(tampered,n,5)
    except (AssertionError,ValueError):
        print("FORGED_FLOWER_ORIGINAL_SOURCE_GATE_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("accepting a counterfeit Holyer source")
    print("FLOWER_CONSTANT_BOUNDARY_CERTIFICATE_UNIFORM_POLYTIME=PROVED")
    print("ARBITRARY_SCL_BOUNDED_INTERFACE_OR_GLOBAL_POLY=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
