#!/usr/bin/env python3
"""Choice-resource Hall terminal layered over uniform Gaussian closure.

This is a SOUND POLYNOMIAL SCOPED terminal, not a universal SAT solver.

Input model
-----------
The universal solver is allowed to retain exact provenance from its OWN
polynomial CNF -> 2-XNF normalization.  We therefore inspect the source CNF,
not hidden benchmark labels.

Detect:
  * pairwise-disjoint positive clauses G_i = (x_1 OR ... OR x_t);
  * all negative binary clauses inside each G_i, making G_i exactly-one;
  * negative binary clauses between groups.

If cross-group conflict components are cliques and contain at most one variable
from each choice group, treat each component as a unit-capacity RESOURCE.
Every satisfying assignment must choose one variable/resource per choice group
and no resource can serve two groups.  Therefore a matching saturating all
choice groups is necessary.

If no such matching exists, Hall gives an exact UNSAT certificate S,N(S) with
    |N(S)| < |S|.
This certificate is independently replayable in polynomial time.

On standard PHP_{k+1}^k:
  * the k+1 pigeon clauses are detected as exact-choice groups;
  * the k hole columns are recovered as resource conflict cliques;
  * maximum matching size is k < k+1;
  * Hall certificate uses all pigeons and all k holes.

Thus the infinite PHP OPEN family from php_scalable_open_firewall.py is solved
without branching.

Failure to detect such a structure returns OPEN and carries NO negative
evidence about SAT.  GENERAL_SAT_IN_P and P=NP remain unproved.
"""

from collections import defaultdict, deque

from php_scalable_open_firewall import php_cnf, xnf_to_2xnf
from uniform_gaussian_implication_audit import uniform_gaussian_implication_closure


def ordinary_literal(l):
    mask,const=l
    return mask and (mask & (mask-1))==0


def variable_of(l):
    assert ordinary_literal(l)
    return l[0].bit_length()-1


def source_clause_views(cnf):
    positive_groups=[]
    neg_pairs=set()
    other=[]

    for C in cnf:
        if all(ordinary_literal(l) and l[1]==0 for l in C):
            positive_groups.append(frozenset(variable_of(l) for l in C))
        elif len(C)==2 and all(ordinary_literal(l) and l[1]==1 for l in C):
            a,b=sorted(variable_of(l) for l in C)
            neg_pairs.add((a,b))
        else:
            other.append(C)

    return tuple(positive_groups),frozenset(neg_pairs),tuple(other)


def choose_disjoint_groups(groups):
    """Deterministic polynomial scoped detector.

    Only accepts the clean case where all positive groups are nonempty and
    pairwise disjoint.  Otherwise returns no terminal rather than solving a
    set-packing problem.
    """
    if not groups or any(not G for G in groups):
        return None
    seen=set()
    for G in groups:
        if seen & set(G):
            return None
        seen |= set(G)
    return tuple(groups)


def exact_choice_groups(groups,neg_pairs):
    for G in groups:
        for a in G:
            for b in G:
                if a<b and (a,b) not in neg_pairs:
                    return False
    return True


def resource_components(groups,neg_pairs):
    owner={}
    universe=set()
    for i,G in enumerate(groups):
        for v in G:
            owner[v]=i
            universe.add(v)

    adj={v:set() for v in universe}
    for a,b in neg_pairs:
        if a not in universe or b not in universe:
            continue
        if owner[a]==owner[b]:
            continue
        adj[a].add(b)
        adj[b].add(a)

    comps=[]
    unseen=set(universe)
    while unseen:
        s=min(unseen)
        unseen.remove(s)
        C={s}
        q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    C.add(v)
                    q.append(v)
        comps.append(frozenset(C))

    # Every resource component must be a clique and contain at most one
    # variable from each choice group.
    for C in comps:
        owners=[owner[v] for v in C]
        if len(set(owners))!=len(owners):
            return None
        for a in C:
            for b in C:
                if a<b and (a,b) not in neg_pairs:
                    return None

    return tuple(comps),owner


def bipartite_graph(groups,resources):
    resource_of={}
    for j,R in enumerate(resources):
        for v in R:
            resource_of[v]=j

    adj={i:set() for i in range(len(groups))}
    for i,G in enumerate(groups):
        for v in G:
            adj[i].add(resource_of[v])
    return adj


def max_matching(adj,n_right):
    match_r={}
    match_l={}

    def aug(u,seen):
        for v in sorted(adj[u]):
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or aug(match_r[v],seen):
                match_r[v]=u
                match_l[u]=v
                return True
        return False

    for u in sorted(adj):
        aug(u,set())

    return match_l,match_r


def hall_deficiency_certificate(adj,match_l,match_r):
    """Alternating-reachable Hall witness from unmatched left vertices."""
    left_reach=set(u for u in adj if u not in match_l)
    right_reach=set()
    q=deque(("L",u) for u in sorted(left_reach))

    while q:
        side,x=q.popleft()
        if side=="L":
            for v in adj[x]:
                # Traverse unmatched L->R edges.
                if match_l.get(x)==v:
                    continue
                if v not in right_reach:
                    right_reach.add(v)
                    q.append(("R",v))
        else:
            if x in match_r:
                u=match_r[x]
                if u not in left_reach:
                    left_reach.add(u)
                    q.append(("L",u))

    # For a maximum matching with unmatched left nodes, N(S)=right_reach and
    # deficiency is positive.
    neigh=set().union(*(adj[u] for u in left_reach)) if left_reach else set()
    assert neigh==right_reach
    assert len(neigh)<len(left_reach)
    return frozenset(left_reach),frozenset(neigh)


def hall_terminal(cnf):
    groups0,neg_pairs,other=source_clause_views(cnf)
    groups=choose_disjoint_groups(groups0)
    if groups is None:
        return {"status":"OPEN","reason":"positive_groups_not_pairwise_disjoint"}

    if not exact_choice_groups(groups,neg_pairs):
        return {"status":"OPEN","reason":"groups_not_exact_choice"}

    rc=resource_components(groups,neg_pairs)
    if rc is None:
        return {"status":"OPEN","reason":"cross_conflicts_not_resource_cliques"}

    resources,owner=rc
    adj=bipartite_graph(groups,resources)
    ml,mr=max_matching(adj,len(resources))

    if len(ml)<len(groups):
        S,N=hall_deficiency_certificate(adj,ml,mr)
        return {
            "status":"UNSAT",
            "reason":"HALL_DEFICIENCY",
            "group_count":len(groups),
            "resource_count":len(resources),
            "matching_size":len(ml),
            "hall_groups":tuple(sorted(S)),
            "hall_resources":tuple(sorted(N)),
            "hall_lhs":len(S),
            "hall_rhs":len(N),
        }

    # A saturating matching only proves the detected matching skeleton can be
    # satisfied. Other source clauses may still constrain it. Do NOT promote
    # to SAT unless the source is exactly the recognized skeleton.
    return {
        "status":"OPEN",
        "reason":"HALL_SATURATING_MATCHING_NOT_FULL_FORMULA_CERTIFICATE",
        "group_count":len(groups),
        "resource_count":len(resources),
        "matching_size":len(ml),
    }


def verify_certificate(cnf,receipt):
    assert receipt["status"]=="UNSAT"
    groups0,neg_pairs,_=source_clause_views(cnf)
    groups=choose_disjoint_groups(groups0)
    assert groups is not None
    resources,_=resource_components(groups,neg_pairs)
    adj=bipartite_graph(groups,resources)

    S=set(receipt["hall_groups"])
    N=set(receipt["hall_resources"])
    actual=set().union(*(adj[u] for u in S))
    assert actual==N
    assert len(N)<len(S)

    # Replay why every satisfying assignment induces an injection S -> N.
    for u in S:
        G=groups[u]
        assert G
        for a in G:
            for b in G:
                if a<b:
                    assert (a,b) in neg_pairs

    for r in N:
        R=resources[r]
        for a in R:
            for b in R:
                if a<b:
                    assert (a,b) in neg_pairs

    return True


def main():
    receipts=[]
    for k in range(3,9):
        cnf,n0,_=php_cnf(k)
        formula,n=xnf_to_2xnf(cnf,n0)

        # Baseline uniform closure demonstrably stalls.
        status,eqs,active=uniform_gaussian_implication_closure(formula,n)
        assert status=="OPEN"
        assert eqs==tuple()

        rec=hall_terminal(cnf)
        assert rec["status"]=="UNSAT"
        assert rec["group_count"]==k+1
        assert rec["resource_count"]==k
        assert rec["matching_size"]==k
        assert rec["hall_lhs"]==k+1
        assert rec["hall_rhs"]==k
        assert verify_certificate(cnf,rec)
        receipts.append((k,rec))

    print("CHOICE-RESOURCE HALL TERMINAL: PASS")
    print("UGIC OPEN PHP family is solved without Boolean branching")
    for k,rec in receipts:
        print("k=",k,rec)
    print("detector/certificate operations are graph scans + polynomial matching")
    print("terminal is SCOPED: nonmatching residues return OPEN")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
