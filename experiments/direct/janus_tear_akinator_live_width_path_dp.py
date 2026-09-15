#!/usr/bin/env python3
"""Provider finite mechanics for the deterministic live-width path-DP lane."""

from itertools import product


def lit(name, neg=False): return (name, bool(neg))

def lval(L, env):
    v = env[L[0]]
    return (not v) if L[1] else v


def bags(gates):
    first, last = {}, {}
    for t, (out, a, b) in enumerate(gates):
        for v in {out, a[0], b[0]}:
            first.setdefault(v, t); last[v] = t
    out = []
    for t in range(len(gates)):
        out.append(tuple(sorted(v for v in first if first[v] <= t <= last[v])))
    width = max((len(x)-1 for x in out), default=-1)
    return out, width


def feasible(gates, unary):
    B, _ = bags(gates)
    prev_bag, prev_states = tuple(), {tuple()}
    for t, bag in enumerate(B):
        pos = {v:i for i,v in enumerate(bag)}
        ppos = {v:i for i,v in enumerate(prev_bag)}
        inter = tuple(v for v in bag if v in ppos)
        allowed = {tuple(s[ppos[v]] for v in inter) for s in prev_states}
        nxt = set()
        out, a, b = gates[t]
        for bits in product((False, True), repeat=len(bag)):
            if tuple(bits[pos[v]] for v in inter) not in allowed: continue
            env = {v:bits[pos[v]] for v in bag}
            if any(v in env and env[v] != val for v,val in unary.items()): continue
            if env[out] != (lval(a,env) and lval(b,env)): continue
            nxt.add(bits)
        if not nxt: return False
        prev_bag, prev_states = bag, nxt
    return bool(prev_states)


def eval_gates(gates, roots):
    env = dict(roots)
    for out,a,b in gates: env[out] = lval(a,env) and lval(b,env)
    return env


def parity(n):
    gates=[]; prev='x0'
    for i in range(1,n):
        x=f'x{i}'; a=f'p{i}a'; b=f'p{i}b'; p=f'p{i}'
        gates += [(a,lit(prev),lit(x)), (b,lit(prev,True),lit(x,True)), (p,lit(a,True),lit(b,True))]
        prev=p
    return gates, prev


def pair_fanout(n):
    gates=[]; es=[]
    for i in range(n):
        e=f'e{i}'; es.append(e); gates.append((e,lit(f'x{i}'),lit(f'y{i}')))
    gs=[]
    for i in range(n):
        for j in range(i+1,n):
            g=f'g{i}_{j}'; gs.append(g); gates.append((g,lit(es[i]),lit(es[j])))
    acc=gs[0]
    for k,g in enumerate(gs[1:],1):
        nxt=f'agg{k}'; gates.append((nxt,lit(acc),lit(g))); acc=nxt
    return gates,acc


def main():
    for n in range(2,6):
        G,out=parity(n); roots=[f'x{i}' for i in range(n)]
        _,w=bags(G); assert w<=5
        for r in range(n+1):
            for pref in product((False,True), repeat=r):
                rho=dict(zip(roots[:r],pref))
                for bit in (False,True):
                    got=feasible(G,{**rho,out:bit})
                    exp=False
                    for rest in product((False,True), repeat=n-r):
                        env=dict(rho); env.update(zip(roots[r:],rest))
                        if eval_gates(G,env)[out] == bit: exp=True; break
                    assert got==exp
    for n in range(3,15):
        G,_=pair_fanout(n); _,w=bags(G); assert w>=n-1; assert len(G)<2*n*n
    print('C025_AKINATOR_LIVE_PATH_DECOMPOSITION_FINITE = PASS')
    print('C025_AKINATOR_LIVE_DP_VS_BRUTE_FORCE = PASS')
    print('C025_AKINATOR_PARITY_CONSTANT_LIVE_WIDTH_FINITE = PASS')
    print('C025_AKINATOR_PAIR_FANOUT_LARGE_WIDTH_FINITE = PASS')
    print('C025_AKINATOR_LIVE_WIDTH_DP = ANALYTIC_THEOREM_NOT_CI')
    print('C025_AKINATOR_ANY_TOPOLOGICAL_PAIR_FANOUT_BOUND = ANALYTIC_NOT_CI')
    print('C025_AKINATOR_REWRITE_DISCOVERY = OPEN')
    print('C025_AKINATOR_GLOBAL_PROGRESS = OPEN')
    print('P_VS_NP = OPEN')

if __name__ == '__main__': main()
