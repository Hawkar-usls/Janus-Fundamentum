#!/usr/bin/env python3
"""Exact controls for R5 E32 root-kernel / mod-3 potential terminal.

For a certified root kernel
    y_(u->v) = t_u - t_v,
Exact-One is equivalent to the mod-3 difference system
    phi_v = phi_u + 1 (mod 3)
on every oriented edge.

This checker verifies the global terminal on three frozen JANUS root-kernel controls:
  * E18 complete directed K7 arc set: UNSAT by opposite-arc contradiction;
  * E19 Paley-11 tournament orientation: UNSAT by inconsistent mod-3 potential;
  * E31 tripartite orientation A->B->C->A: SAT, with centered edge values {-1,2}.

P_VS_NP remains OPEN.
"""

from collections import deque


def solve_mod3_potential(num_vertices, edges):
    """Return (True,colors,None) or (False,None,conflict_edge)."""
    adj = [[] for _ in range(num_vertices)]
    for eid,(u,v) in enumerate(edges):
        # phi_v = phi_u + 1; reverse traversal gives -1.
        adj[u].append((v,1,eid))
        adj[v].append((u,-1,eid))

    color = [None]*num_vertices
    for root in range(num_vertices):
        if color[root] is not None:
            continue
        color[root] = 0
        q = deque([root])
        while q:
            u = q.popleft()
            for v,delta,eid in adj[u]:
                want = (color[u] + delta) % 3
                if color[v] is None:
                    color[v] = want
                    q.append(v)
                elif color[v] != want:
                    return False,None,(eid,u,v,color[u],color[v],want)
    return True,color,None


def centered_from_colors(colors, edges):
    # Representatives are 0,1,2.  If phi_v=phi_u+1 mod3, then
    # t_u-t_v is -1 for 0->1 and 1->2, and +2 for 2->0.
    y=[]
    for u,v in edges:
        d = colors[u]-colors[v]
        if d == -1:
            y.append(-1)
        elif d == 2:
            y.append(2)
        else:
            raise AssertionError((u,v,colors[u],colors[v],d))
    return y


def e18_complete_directed_k7():
    edges=[(u,v) for u in range(7) for v in range(7) if u != v]
    ok,colors,conflict = solve_mod3_potential(7,edges)
    assert not ok
    return len(edges), conflict


def paley11_edges():
    q=11
    residues={a*a % q for a in range(1,q)}
    edges=[]
    for u in range(q):
        for v in range(q):
            if u != v and ((v-u) % q) in residues:
                edges.append((u,v))
    assert len(edges) == 55
    return edges


def e19_paley11():
    edges=paley11_edges()
    ok,colors,conflict = solve_mod3_potential(11,edges)
    assert not ok
    return len(edges), conflict


def e31_tripartite(m):
    # Vertex ids: A_a, B_b, C_c.
    def A(a): return a
    def B(b): return m+b
    def C(c): return 2*m+c

    edges=[]
    for a in range(m):
        for b in range(m):
            edges.append((A(a),B(b)))
    for b in range(m):
        for c in range(m):
            edges.append((B(b),C(c)))
    for c in range(m):
        for a in range(m):
            edges.append((C(c),A(a)))

    ok,colors,conflict = solve_mod3_potential(3*m,edges)
    assert ok and conflict is None

    # The system fixes the three parts to cyclic colors, up to component shift.
    ca={colors[A(a)] for a in range(m)}
    cb={colors[B(b)] for b in range(m)}
    cc={colors[C(c)] for c in range(m)}
    assert len(ca)==len(cb)==len(cc)==1
    av=next(iter(ca)); bv=next(iter(cb)); cv=next(iter(cc))
    assert bv == (av+1)%3
    assert cv == (bv+1)%3
    assert av == (cv+1)%3

    y=centered_from_colors(colors,edges)
    assert set(y) <= {-1,2}
    assert len(y) == 3*m*m
    return len(edges), (av,bv,cv), y.count(2)


def main():
    n18,c18=e18_complete_directed_k7()
    print(f"E18 root control: edges={n18}, MOD3-POTENTIAL=UNSAT, conflict={c18[:3]}")

    n19,c19=e19_paley11()
    print(f"E19 root control: edges={n19}, MOD3-POTENTIAL=UNSAT, conflict={c19[:3]}")

    for m in range(4,9):
        n31,colors,twos=e31_tripartite(m)
        print(
            f"E31 m={m}: edges={n31}, MOD3-POTENTIAL=SAT, "
            f"part_colors={colors}, centered_twos={twos}"
        )

    print("R5 E32 root-kernel mod-3 potential terminal: PASS")
    print("Scientific ceiling: P_VS_NP remains OPEN.")


if __name__ == "__main__":
    main()
