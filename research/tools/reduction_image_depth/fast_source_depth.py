def canon(source):
    return tuple(sorted(set(tuple(c) for c in source), key=lambda c:(len(c),c)))


def restrict_source(source,v,val):
    out=[]
    for clause in source:
        rem=[]; sat=False
        for lit in clause:
            if abs(lit)==v:
                if bool(val)==(lit>0): sat=True; break
            else: rem.append(lit)
        if sat: continue
        if not rem: return ((),)
        out.append(tuple(rem))
    return canon(out)


def terminal_status(source):
    if any(len(c)==0 for c in source): return False
    if not source: return True
    units={c[0] for c in source if len(c)==1}
    if any(-u in units for u in units): return False
    return None


def source_components(source):
    clauses=list(source); unseen=set(range(len(clauses))); comps=[]
    supports=[{abs(l) for l in c} for c in clauses]
    while unseen:
        seed=unseen.pop(); ids={seed}; support=set(supports[seed]); changed=True
        while changed:
            changed=False
            for j in list(unseen):
                if support & supports[j]:
                    unseen.remove(j); ids.add(j); support |= supports[j]; changed=True
        comps.append(canon(clauses[i] for i in sorted(ids)))
    return tuple(comps)

def state_vars(source):
    return sorted({abs(l) for c in source for l in c})


def exact_depth(source,reverse=False):
    memo={}; choices={}; stats={'states':0,'terminal':0,'parallel':0}
    def rec(s):
        s=canon(s)
        if s in memo: return memo[s]
        stats['states']+=1
        term=terminal_status(s)
        if term is not None:
            stats['terminal']+=1; memo[s]=0; choices[s]=('T',term); return 0
        comps=source_components(s)
        if len(comps)>1:
            stats['parallel']+=1
            d=max(rec(c) for c in comps)
            memo[s]=d; choices[s]=('P',comps); return d
        candidates=sorted(state_vars(s),reverse=reverse)
        best=None; bestvars=[]
        for v in candidates:
            d=1+max(rec(restrict_source(s,v,0)),rec(restrict_source(s,v,1)))
            if best is None or d<best: best=d; bestvars=[v]
            elif d==best: bestvars.append(v)
        memo[s]=best; choices[s]=('S',(min(bestvars),tuple(bestvars))); return best
    root=canon(source)
    return rec(root),memo,choices,stats


def replay(source,bits,choices):
    def walk(s):
        s=canon(s); kind,payload=choices[s]
        if kind=='T': return 0
        if kind=='P': return max((walk(c) for c in payload),default=0)
        v,_=payload
        return 1+walk(restrict_source(s,v,bits[v-1]))
    return walk(source)
