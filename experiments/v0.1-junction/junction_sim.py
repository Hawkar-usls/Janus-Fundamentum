import random, time, math, json, csv
from statistics import mean, median


def gen_planted(n, m, k, rng):
    planted=[rng.randrange(2) for _ in range(n)]
    clauses=[]
    for _ in range(m):
        vs=rng.sample(range(n), k)
        lits=[]
        while True:
            lits=[(v, bool(rng.randrange(2))) for v in vs] # negated
            if any(((1-planted[v]) if neg else planted[v]) for v,neg in lits):
                break
        clauses.append(lits)
    return clauses, planted

def sat_clause(c,a):
    return any(((1-a[v]) if neg else a[v]) for v,neg in c)

def sat_count(cs,a): return sum(sat_clause(c,a) for c in cs)

def unsat_idx(cs,a): return [i for i,c in enumerate(cs) if not sat_clause(c,a)]

def flip_delta(cs,a,v,weights=None):
    before=0.0; after=0.0
    for i,c in enumerate(cs):
        if any(x==v for x,_ in c):
            w=1.0 if weights is None else weights[i]
            before += w if sat_clause(c,a) else 0
            a[v]^=1; ok=sat_clause(c,a); a[v]^=1
            after += w if ok else 0
    return after-before

def random_search(cs,n,budget,rng):
    best=0
    for s in range(1,budget+1):
        a=[rng.randrange(2) for _ in range(n)]
        q=sat_count(cs,a); best=max(best,q)
        if q==len(cs): return True,s,best
    return False,budget,best

def walksat(cs,n,budget,rng,p_random=.55):
    a=[rng.randrange(2) for _ in range(n)]; best=sat_count(cs,a)
    for s in range(1,budget+1):
        u=unsat_idx(cs,a)
        if not u: return True,s,len(cs)
        c=cs[rng.choice(u)]
        vars_=[v for v,_ in c]
        if rng.random()<p_random: v=rng.choice(vars_)
        else:
            vals=[(flip_delta(cs,a,v),rng.random(),v) for v in vars_]
            v=max(vals)[2]
        a[v]^=1; best=max(best,sat_count(cs,a))
    return best==len(cs),budget,best

def junction(cs,n,budget,rng):
    # Clause "holes" accumulate charge; variables feel signed pressure from charged unsatisfied clauses.
    a=[rng.randrange(2) for _ in range(n)]
    charge=[1.0]*len(cs); momentum=[0.0]*n
    best=sat_count(cs,a); stagn=0
    for s in range(1,budget+1):
        u=unsat_idx(cs,a)
        if not u: return True,s,len(cs)
        us=set(u)
        for i in range(len(cs)):
            if i in us: charge[i]=min(20.0, charge[i]*1.12+0.15)
            else: charge[i]=max(1.0, charge[i]*0.985)
        pressure=[0.0]*n
        touched=set()
        for i in u:
            for v,neg in cs[i]:
                # flipping v satisfies this currently unsatisfied literal, so positive drive
                pressure[v]+=charge[i]
                touched.add(v)
        # subtract weighted damage to currently satisfied clauses and add persistence/momentum
        cand=[]
        for v in touched:
            d=flip_delta(cs,a,v,charge)
            score=pressure[v]+1.8*d+0.35*momentum[v]+rng.uniform(-0.2,0.2)
            cand.append((score,v))
        v=max(cand)[1]
        old=sat_count(cs,a); a[v]^=1; new=sat_count(cs,a)
        gain=new-old
        for j in range(n): momentum[j]*=.90
        momentum[v]=0.75*momentum[v]+gain
        if new>best: best=new; stagn=0
        else: stagn+=1
        # depletion breakdown / restart when trapped
        if stagn>max(20,n//2):
            hottest=sorted(range(len(cs)), key=lambda i: charge[i], reverse=True)[:max(2,n//16)]
            vars_hot=list({v for i in hottest for v,_ in cs[i]})
            for vv in rng.sample(vars_hot,min(len(vars_hot),max(1,n//20))): a[vv]^=1
            stagn=0
    return best==len(cs),budget,best

def run():
    seed=440221; master=random.Random(seed)
    configs=[]
    for k,alpha,sizes in [(3,4.20,[20,32,48]),(5,6.00,[24,36,48])]:
        for n in sizes: configs.append((k,n,round(alpha*n)))
    trials=8; budget_factor=35
    rows=[]
    for k,n,m in configs:
        raw={name:[] for name in ['random','walksat','junction']}
        for t in range(trials):
            inst_seed=master.randrange(10**9); ir=random.Random(inst_seed)
            cs,_=gen_planted(n,m,k,ir); budget=budget_factor*n
            for name,fn in [('random',random_search),('walksat',walksat),('junction',junction)]:
                rr=random.Random(inst_seed ^ {'random':11,'walksat':22,'junction':33}[name])
                t0=time.perf_counter(); solved,steps,best=fn(cs,n,budget,rr); ms=(time.perf_counter()-t0)*1000
                raw[name].append((solved,steps,best/m,ms))
        for name,vals in raw.items():
            solved=[v for v in vals if v[0]]
            rows.append(dict(k=k,n=n,m=m,alpha=m/n,method=name,trials=trials,
                solve_rate=sum(v[0] for v in vals)/trials,
                median_steps=median([v[1] for v in solved]) if solved else None,
                mean_best_ratio=mean(v[2] for v in vals),mean_ms=mean(v[3] for v in vals)))
    with open('/mnt/data/junction_results.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    with open('/mnt/data/junction_results.json','w') as f: json.dump({'seed':seed,'trials':trials,'budget_factor':budget_factor,'rows':rows},f,indent=2)
    print(json.dumps(rows,indent=2))
if __name__=='__main__': run()
