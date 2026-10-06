#!/usr/bin/env python3
"""R5 E91: sigma=2 distinct-pair-shares local defect normal form.

Assume the E90 first surviving p=1,h=1 lane:
  T1 in Q_AB cap Q_AC,
  T2 in Q_AB cap Q_BC,
  T1,T2 distinct and disjoint,
  no other near-class sharing,
  sigma=2.

Then exactly four cubic variables lie outside the three v=1 near-classes.

Universal degree bookkeeping shows that every completion triple is supported
entirely on the fixed local defect ground

    T1 union T2 union {A,B,C,r,s}.

No saturated ordinary W-point outside T1 union T2 can occur in a completion,
and such a point cannot host the distinct zero hole.

For a fixed representative hole, the relaxed local completion skeletons
(subject only to degree deficits and source-linearity constraints internal to
the defect) are:
    overlap survivor hole A : 252
    distinct hole r         : 1152
    distinct hole t1 in T1  : 324

For the distinct r-hole case, exact coverage of r in all three v=0 states
forces the unique r-completion to belong to X_A,X_B,X_C simultaneously.
Hence it avoids A,B,C and, by linearity with x={r,s}, T1 and T2, has exactly

    {r, one point of T1, one point of T2}.

Imposing only the necessary r/s endpoint-cover condition for all three v=0
covers leaves exactly 558 of the 1152 relaxed r-hole skeletons.

These are necessary local normal forms, not yet a full exclusion.  Additional
linearity against the nonlocal near-class blocks and the existence of complete
X_A,X_B,X_C covers remain the E92 global-extension target.

P_VS_NP remains OPEN.
"""

from itertools import combinations

A,B,C = "A","B","C"
R,S = "r","s"
T1 = ("t1","t2","t3")
T2 = ("u1","u2","u3")
POINTS = (A,B,C,R,S) + T1 + T2

def triple_allowed(e):
    E=set(e)
    return (
        len(E & set(T1)) <= 1
        and len(E & set(T2)) <= 1
        and len(E & {R,S}) <= 1
    )

CANDIDATES=tuple(
    frozenset(e)
    for e in combinations(POINTS,3)
    if triple_allowed(e)
)

def deficits(kind,hole):
    d={v:0 for v in POINTS}
    for v in T1+T2:
        d[v]=1
    for v in (A,B,C):
        d[v]=1
    d[R]=d[S]=2
    d[hole]-=1
    assert sum(d.values())==12
    return d

def enumerate_quadruples(d):
    cands=tuple(
        sorted(
            (e for e in CANDIDATES if all(d[v]>0 for v in e)),
            key=lambda e: tuple(sorted(e)),
        )
    )
    out=[]

    def rec(start,rem,chosen):
        if len(chosen)==4:
            if all(x==0 for x in rem.values()):
                out.append(tuple(chosen))
            return
        if sum(rem.values()) != 3*(4-len(chosen)):
            return

        for i in range(start,len(cands)):
            e=cands[i]
            if any(rem[v] <= 0 for v in e):
                continue
            if any(len(e & f) > 1 for f in chosen):
                continue
            nr=rem.copy()
            for v in e:
                nr[v]-=1
            rec(i+1,nr,chosen+(e,))

    rec(0,d.copy(),())
    return tuple(out)

def endpoint_cover_possible(system, omitted):
    rblocks=[e for e in system if R in e and omitted not in e]
    sblocks=[e for e in system if S in e and omitted not in e]
    return any(er.isdisjoint(es) for er in rblocks for es in sblocks)

def verify_r_hole_forcing(systems):
    survivors=[]
    for sys in systems:
        if not all(endpoint_cover_possible(sys,o) for o in (A,B,C)):
            continue
        rblocks=[e for e in sys if R in e]
        assert len(rblocks)==1
        e=rblocks[0]

        # r has cubic degree one after the zero hole, so this block must be
        # selected in every X_A,X_B,X_C cover.  It therefore cannot contain
        # an omitted survivor A/B/C.
        assert not (e & {A,B,C})

        # It also cannot contain s (linearity with x={r,s}); with two slots
        # left and no saturated ordinary points available, it must take one
        # point from each shared block.
        assert len(e & set(T1))==1
        assert len(e & set(T2))==1
        survivors.append(sys)

    assert len(survivors)==558
    return tuple(survivors)

def main():
    overlap=enumerate_quadruples(deficits("overlap",A))
    r_hole=enumerate_quadruples(deficits("distinct",R))
    shared_hole=enumerate_quadruples(deficits("distinct","t1"))

    assert len(overlap)==252
    assert len(r_hole)==1152
    assert len(shared_hole)==324

    survivors=verify_r_hole_forcing(r_hole)

    print("R5 E91 sigma2 local-defect normal form: PASS")
    print("completion ground = T1 union T2 union {A,B,C,r,s}, independent of t")
    print("fixed-hole relaxed local skeletons: overlap=252 r-hole=1152 shared-hole=324")
    print("r-hole skeletons surviving necessary all-three endpoint cover:", len(survivors))
    print("every surviving r-hole system has unique common completion {r,t_i,u_j}")
    print("remaining target: global near-class extension / complete X_A,X_B,X_C covers")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
