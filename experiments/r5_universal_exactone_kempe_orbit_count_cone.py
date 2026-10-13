#!/usr/bin/env python3
"""All-size necessary Kempe-chain COLORING MULTIPLICITY cone for open sixpole.

Hypothetical physical full boundary relation is EXACTLY the set S of
108 six-colour tuples with 3 paired colour-equality bits {100,010,001}.
For an arbitrary colourable 3-edge-coloured cubic multipole M,
let w_s=count of complete proper interior colourings with boundary s.
All w_s > 0 if Col(M)=S, and w_s=0 outside S.

For each fixed pair of colours (a,b), the a/b-edge components are cycles
and paths that pair boundary a/b semiedges. Flipping any subset of these
pairwise disjoint paths produces a Boolean hypercube of distinct boundary
states; each cube has uniform number of complete interior colourings
since switches are invertible. Thus the vector w must be a nonnegative
sum of indicator vectors of admissible path-flip hypercubes for EACH
of the 3 colour-pairs (a,b), with the SAME w across all 3.

The feasibility of these THREE simultaneous nonnegative orbit cones,
plus w_s>=1 for all 108 states, is an ALL-SIZE NECESSARY CONDITION.
The orbit sets are constructed exactly. Linear programming is used to
probe feasibility. A claimed feasible solution is rationalized and
EVERY exact linear equality independently recomputed in Fractions.
A numerical infeasibility report alone is NEVER promoted to a theorem
without a frozen exact dual Farkas certificate.
"""
from itertools import product
from fractions import Fraction
from collections import defaultdict
import hashlib
import json

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

PAIRS=((0,1),(0,2),(1,2))
ONEHOT={(1,0,0),(0,1,0),(0,0,1)}


def states():
    return tuple(s for s in product(range(3),repeat=6)
                 if all(s.count(c)%2==0 for c in range(3))
                 and tuple(int(s[i]==s[i+3]) for i in range(3)) in ONEHOT)


STATES=states()
INDEX={s:i for i,s in enumerate(STATES)}
assert len(STATES)==108


def all_matchings(nodes):
    if not nodes:
        yield ()
        return
    first,*rest=nodes
    for j,last in enumerate(rest):
        for tail in all_matchings(rest[:j]+rest[j+1:]):
            yield ((first,last),)+tail


def orbit(s,a,b,matching):
    out=set()
    for mask in range(1<<len(matching)):
        state=list(s)
        for k,(u,v) in enumerate(matching):
            if (mask>>k)&1:
                for i in (u,v):
                    state[i]=b if state[i]==a else a
        out.add(tuple(state))
    assert len(out)==1<<len(matching)
    return frozenset(out)


def valid_orbits(a,b):
    orbits=set()
    for s in STATES:
        term=[i for i,c in enumerate(s) if c in (a,b)]
        assert len(term)%2==0
        for M in all_matchings(term):
            O=orbit(s,a,b,M)
            if O <= INDEX.keys():
                orbits.add(frozenset(INDEX[t] for t in O))
    assert all(any(i in O for O in orbits) for i in range(len(STATES)))
    return tuple(sorted(orbits,key=lambda o:(len(o),tuple(sorted(o)))))


def exact_rational_replay(z,orbits,denom=100000):
    # Independent INTEGER verification, not an LP floating residual.
    fr=[Fraction(float(x)).limit_denominator(denom) for x in z]
    nw=len(STATES)
    assert all(v>=1 for v in fr[:nw])
    j=nw
    for O in orbits:
        coeff=fr[j:j+len(O)]
        assert all(a>=0 for a in coeff)
        for s in range(nw):
            assert fr[s]==sum(coeff[i] for i,o in enumerate(O) if s in o),(
                "rationalization not exact",j,s,fr[s],
                sum(coeff[i] for i,o in enumerate(O) if s in o))
        j+=len(O)
    assert j==len(fr)
    return fr


def main():
    orbits=[valid_orbits(*ab) for ab in PAIRS]
    print("BOUNDARY_STATES",len(STATES),flush=True)
    print("KEMPE_ORBITS",[(p,len(o),
            Counter(len(z) for z in o)) for p,o in zip(PAIRS,orbits)],flush=True)
    nw=len(STATES)
    offsets=[]
    nvars=nw
    for O in orbits:
        offsets.append(nvars)
        nvars+=len(O)
    r=[];c=[];values=[]
    for pair_index,O in enumerate(orbits):
        for s in range(nw):
            row=pair_index*nw+s
            r.append(row);c.append(s);values.append(1)
        for oi,state_set in enumerate(O):
            for s in state_set:
                r.append(pair_index*nw+s)
                c.append(offsets[pair_index]+oi)
                values.append(-1)
    A=coo_matrix((values,(r,c)),shape=(3*nw,nvars)).tocsr()
    objective=np.zeros(nvars)
    objective[:nw]=1
    bounds=[(1,None)]*nw+[(0,None)]*(nvars-nw)
    res=linprog(objective,A_eq=A,b_eq=np.zeros(3*nw),
                bounds=bounds,method="highs")
    print("HIGHS_STATUS",{"status":int(res.status),
          "message":res.message,"objective":float(res.fun) if res.fun is not None else None},
          flush=True)
    if res.success:
        error=np.max(np.abs(A@res.x))
        print("NUMERICAL_MAX_RESIDUAL",float(error),flush=True)
        assert error < 1e-7
        try:
            rational=exact_rational_replay(res.x,orbits)
        except AssertionError as e:
            print("EXACT_RATIONAL_REPLAY=FAILED; numerical feasibility only",
                  str(e)[:500],flush=True)
        else:
            print("EXACT_RATIONAL_REPLAY=PASS",flush=True)
            print("RATIONAL_NONZERO",sum(x!=0 for x in rational),flush=True)
            print("RATIONAL_W_COUNTS",Counter(rational[:nw]),flush=True)
            # Canonical certificate digest. Stored source allows re-solving.
            cert=json.dumps([str(x) for x in rational],separators=(",",":")).encode()
            print("RATIONAL_CERT_SHA256",hashlib.sha256(cert).hexdigest(),flush=True)
            print("VERDICT: ORBIT-CONE NECESSARY CONDITION SATISFIABLE EXACTLY",flush=True)
            print("  Therefore this generalized Kempe count test cannot rule out")
            print("  open ExactOne in arbitrary-size cubic sixpoles.",flush=True)
    elif res.status==2:
        print("HIGHS_INFEASIBLE_UNCERTIFIED: NEED EXACT FARKAS DUAL",flush=True)
    else:
        print("UNKNOWN_NUMERICAL_RESOURCE_OR_STATUS",flush=True)
    print("NO_GADGET_CONSTRUCTED; UNIVERSAL_PC_TRANSFER=OPEN",flush=True)
    print("UNBOUNDED_NATIVE_SCL_PC_DEGREE=OPEN; P_VS_NP=OPEN",flush=True)


if __name__=="__main__":
    from collections import Counter
    main()
