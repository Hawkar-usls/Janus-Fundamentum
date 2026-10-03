#!/usr/bin/env python3
"""R5 E55 exact controls: the E12 hardness bridge uses only SWITCH4 and FREE8 claw types.

For cyclic 3-regular RXC3 fixtures of sizes q=6,9,12, build the full E12 target and
classify every conflict-graph vertex by its E53 claw-family orbit.

Expected exact role/count theorem:
  * every z or z' internal variable is SWITCH4, canonical family
      {000,001,010,101};
  * every t internal variable is FREE8;
  * every global boundary x or x' variable is FREE8;
  * hence in a 17q-variable target:
      SWITCH4 = 12q,
      FREE8   =  5q,
    and no other E53 claw orbit occurs.
"""
import itertools
from collections import Counter

SWITCH4=((0,0,0),(0,0,1),(0,1,0),(1,0,1))
FREE8=tuple(itertools.product((0,1), repeat=3))


def transform(z,p,flip):
    return tuple(z[p[i]] ^ flip[i] for i in range(3))


def canonical(F):
    imgs=[]
    for p in itertools.permutations(range(3)):
        for flip in itertools.product((0,1), repeat=3):
            imgs.append(tuple(sorted(transform(z,p,flip) for z in F)))
    return min(imgs)


def source_fixture(q):
    # 3-uniform, 3-regular source: C_i={i,i+1,i+3} mod q.
    rows=[((i+0)%q,(i+1)%q,(i+3)%q) for i in range(q)]
    deg=Counter(v for r in rows for v in r)
    assert all(len(set(r))==3 for r in rows)
    assert all(deg[v]==3 for v in range(q))
    return rows


def transform_rx(q, source_sets):
    target=[]
    x=[f"x:{i}" for i in range(q)]
    xp=[f"xp:{i}" for i in range(q)]
    for j,C in enumerate(source_sets):
        a,b,c=C
        bx=[x[a],x[b],x[c]]
        bxp=[xp[a],xp[b],xp[c]]
        z=[f"g{j}:z{i}" for i in range(1,7)]
        zp=[f"g{j}:zp{i}" for i in range(1,7)]
        t=[f"g{j}:t{i}" for i in range(1,4)]
        target += [
            {bx[0],z[0],z[3]}, {bx[1],z[1],z[4]}, {bx[2],z[2],z[5]},
            {z[0],z[1],z[2]}, {z[3],z[4],z[5]},
            {bxp[0],zp[0],zp[3]}, {bxp[1],zp[1],zp[4]}, {bxp[2],zp[2],zp[5]},
            {zp[0],zp[1],zp[2]}, {zp[3],zp[4],zp[5]},
            {z[1],z[5],t[0]}, {z[2],z[3],t[1]}, {z[0],z[4],t[2]},
            {zp[1],zp[5],t[1]}, {zp[2],zp[3],t[2]}, {zp[0],zp[4],t[0]},
            {t[0],t[1],t[2]},
        ]
    return target


def classify(rows):
    verts=sorted(set().union(*rows))
    idx={v:i for i,v in enumerate(verts)}
    inc=[[] for _ in verts]
    adj=[set() for _ in verts]
    for R0 in rows:
        R={idx[v] for v in R0}
        for v in R:
            inc[v].append(R)
        for a,b in itertools.combinations(R,2):
            adj[a].add(b); adj[b].add(a)

    out={}
    for vi,name in enumerate(verts):
        assert len(inc[vi])==3
        pairs=[tuple(sorted(R-{vi})) for R in inc[vi]]
        F=[]
        for z in itertools.product((0,1), repeat=3):
            leaves=[pairs[i][z[i]] for i in range(3)]
            if all(leaves[j] not in adj[leaves[i]]
                   for i in range(3) for j in range(i+1,3)):
                F.append(z)
        out[name]=canonical(tuple(F))
    return out


def role(name):
    if name.startswith("x:"): return "x"
    if name.startswith("xp:"): return "xp"
    token=name.split(":",1)[1]
    if token.startswith("zp"): return "zp"
    if token.startswith("z"): return "z"
    if token.startswith("t"): return "t"
    raise AssertionError(name)


def main():
    for q in (6,9,12):
        src=source_fixture(q)
        target=transform_rx(q,src)
        C=classify(target)
        assert len(C)==17*q

        by_type=Counter(C.values())
        assert set(by_type)=={SWITCH4,FREE8}
        assert by_type[SWITCH4]==12*q
        assert by_type[FREE8]==5*q

        by_role=Counter((role(v),F) for v,F in C.items())
        assert by_role[("z",SWITCH4)]==6*q
        assert by_role[("zp",SWITCH4)]==6*q
        assert by_role[("t",FREE8)]==3*q
        assert by_role[("x",FREE8)]==q
        assert by_role[("xp",FREE8)]==q

        # No role leaks into the other type.
        assert sum(by_role.values())==17*q

    print("R5 E55 E12 SWITCH4/FREE8 hardness localization: PASS")
    print("all z/z' -> SWITCH4")
    print("all t/x/x' -> FREE8")
    print("counts: SWITCH4=12q, FREE8=5q, total=17q")


if __name__=="__main__":
    main()
