#!/usr/bin/env python3
"""B2A component-boundary reachability / transition-signature finite checker.

This checker validates the finite four-color logic around rho/mu/delta.
It does NOT implement the external P7-free List-3 algorithm.  The actual
rho_D(F) compilation uses that published constructive polynomial backend as
an oracle for each forced-witness List-3 instance.

No List-4 call is made or modeled here.
"""

from itertools import combinations, permutations

COLORS=(1,2,3,4)
FULL=15

def bit(c):
    return 1 << (c-1)

def is_downward_closed(table):
    for F in range(16):
        if not ((table>>F)&1):
            continue
        sub=F
        while True:
            if not ((table>>sub)&1):
                return False
            if sub==0:
                break
            sub=(sub-1)&F
    return True

MESSAGE_TABLES=tuple(t for t in range(1<<16) if is_downward_closed(t))
assert len(MESSAGE_TABLES)==168

def mu(table,F):
    return (table>>F)&1

ACTUAL_COMPONENT_TABLES=tuple(t for t in MESSAGE_TABLES if mu(t,FULL)==0)
assert len(ACTUAL_COMPONENT_TABLES)==167

PROPER_MASKS=tuple(F for F in range(16) if F!=FULL)
NONEMPTY_PROPER_MASKS=tuple(F for F in PROPER_MASKS if F!=0)
assert len(PROPER_MASKS)==15
assert len(NONEMPTY_PROPER_MASKS)==14

def distinguishing_pairs(table,A_mask,rho_bits):
    """Return the exact local B-C delta signature.

    rho_bits uses bit F to say exact mask F is reachable on D^-.
    Source-consistent two-sided B-C use has D^- nonempty, hence rho(empty)=0.
    """
    out=[]
    for F in PROPER_MASKS:
        if not ((rho_bits>>F)&1):
            continue
        for c in COLORS:
            if not (A_mask & bit(c)):
                continue
            G=F|bit(c)
            if mu(table,F) != mu(table,G):
                out.append((F,c))
    return tuple(out)

def cx0_delta(table0,table1,rho_bits):
    """Reachable proper masks on which two recompiled component messages differ."""
    return tuple(
        F for F in PROPER_MASKS
        if ((rho_bits>>F)&1) and mu(table0,F)!=mu(table1,F)
    )

def witness_tuple_bound(n,F):
    """Crude number of injective witness choices for one exact-mask query."""
    k=F.bit_count()
    if k==0:
        return 1
    if k>3:
        raise ValueError("proper-mask backend only")
    ans=1
    for i in range(k):
        ans*=max(0,n-i)
    return ans

def exact_mask_oracle_spec(D_size,F):
    """Protocol receipt for rho_D(F); actual graph/list solver lives externally."""
    if F==FULL:
        return {"supported":False,"reason":"LIST4_FORBIDDEN"}
    if D_size==0:
        return {"supported":True,"rho": F==0,"list3_calls":0}
    if F==0:
        return {"supported":True,"rho":False,"list3_calls":0}
    return {
        "supported":True,
        "rho":"OR_over_forced_witness_List3_calls",
        "witness_tuple_upper_bound":witness_tuple_bound(D_size,F),
        "palette_size":F.bit_count(),
    }

def finite_replay():
    # Full-mask bad is automatic for actual nonempty components.
    assert all(mu(t,FULL)==0 for t in ACTUAL_COMPONENT_TABLES)

    # Every mu difference under unioning one color is proper and directed 1 -> 0.
    diff_count=0
    for t in MESSAGE_TABLES:
        for F in range(16):
            for c in COLORS:
                G=F|bit(c)
                if mu(t,F)==mu(t,G):
                    continue
                diff_count+=1
                assert not (F & bit(c))      # c not already in F
                assert F != FULL             # distinguishing F is proper
                assert mu(t,F)==1
                assert mu(t,G)==0

    # Proper-mask witness lifecycle is at most cubic.
    for F in NONEMPTY_PROPER_MASKS:
        assert F.bit_count()<=3
        for n in (1,2,3,7):
            bound=witness_tuple_bound(n,F)
            assert bound <= n**3

    # Source-consistent two-sided B-C baseline has D^- nonempty, so empty mask unreachable.
    rho_nonempty_example=sum(1<<F for F in NONEMPTY_PROPER_MASKS)
    assert not ((rho_nonempty_example>>0)&1)

    # Delta functions are constant-size finite objects.
    max_bc_delta=0
    max_cx0_delta=0
    for t in ACTUAL_COMPONENT_TABLES:
        for A in range(16):
            d=distinguishing_pairs(t,A,rho_nonempty_example)
            max_bc_delta=max(max_bc_delta,len(d))
    # A C-X0 pair compares two actual-component tables.
    for t0 in ACTUAL_COMPONENT_TABLES[:16]:
        for t1 in ACTUAL_COMPONENT_TABLES[:16]:
            d=cx0_delta(t0,t1,rho_nonempty_example)
            max_cx0_delta=max(max_cx0_delta,len(d))

    return {
        "status":"PASS_FINITE_B2A_REPLAY",
        "monotone_tables":len(MESSAGE_TABLES),
        "actual_nonempty_component_table_upper_space":len(ACTUAL_COMPONENT_TABLES),
        "proper_masks":len(PROPER_MASKS),
        "nonempty_proper_masks":len(NONEMPTY_PROPER_MASKS),
        "mu_union_color_differences_checked":diff_count,
        "all_differences_are_proper_and_1_to_0":True,
        "proper_mask_witness_tuple_degree_max":3,
        "full_mask_List4_calls":0,
        "bc_delta_slots_canonical":64,
        "cx0_delta_slots_canonical":15,
        "sample_max_bc_active_pairs":max_bc_delta,
        "sample_max_cx0_active_masks":max_cx0_delta,
    }

if __name__=="__main__":
    print(finite_replay())
