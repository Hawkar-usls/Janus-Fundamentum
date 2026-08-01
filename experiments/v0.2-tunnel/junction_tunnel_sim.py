import random, time, json, csv, math
from statistics import mean, median


def gen_planted(n, m, k, rng):
    planted=[rng.randrange(2) for _ in range(n)]
    clauses=[]
    for _ in range(m):
        vs=rng.sample(range(n), k)
        while True:
            lits=[(v, bool(rng.randrange(2))) for v in vs]
            if any(((1-planted[v]) if neg else planted[v]) for v,neg in lits):
                clauses.append(lits); break
    return clauses

def sat_clause(c,a):
    return any(((1-a[v]) if neg else a[v]) for v,neg in c)

def sat_count(cs,a):
    return sum(sat_clause(c,a) for c in cs)

def unsat_idx(cs,a):
    return [i for i,c in enumerate(cs) if not sat_clause(c,a)]

def flip_delta(cs,a,v,weights=None):
    before=after=0.0
    for i,c in enumerate(cs):
        if any(x==v for x,_ in c):
            w=1.0 if weights is None else weights[i]
            ok0=sat_clause(c,a)
            a[v]^=1; ok1=sat_clause(c,a); a[v]^=1
            before += w if ok0 else 0.0
            after += w if ok1 else 0.0
    return after-before

def walksat(cs,n,budget,rng,p_random=.55):
    a=[rng.randrange(2) for _ in range(n)]; best=sat_count(cs,a)
    for s in range(1,budget+1):
        u=unsat_idx(cs,a)
        if not u: return True,s,best,{'escapes':0,'accepted_uphill':0}
        c=cs[rng.choice(u)]; vars_=[v for v,_ in c]
        if rng.random()<p_random: v=rng.choice(vars_)
        else: v=max((flip_delta(cs,a,v),rng.random(),v) for v in vars_)[2]
        a[v]^=1; best=max(best,sat_count(cs,a))
    return best==len(cs),budget,best,{'escapes':0,'accepted_uphill':0}

def junction_base(cs,n,budget,rng):
    a=[rng.randrange(2) for _ in range(n)]
    charge=[1.0]*len(cs); momentum=[0.0]*n
    best=sat_count(cs,a); stagn=0; escapes=0
    for s in range(1,budget+1):
        u=unsat_idx(cs,a)
        if not u: return True,s,best,{'escapes':escapes,'accepted_uphill':0}
        us=set(u)
        for i in range(len(cs)):
            charge[i]=min(24.0,charge[i]*1.12+0.15) if i in us else max(1.0,charge[i]*.985)
        touched={v for i in u for v,_ in cs[i]}
        v=max((sum(charge[i] for i in u if any(x==v for x,_ in cs[i])) +
               1.8*flip_delta(cs,a,v,charge)+.35*momentum[v]+rng.uniform(-.2,.2),v)
              for v in touched)[1]
        old=sat_count(cs,a); a[v]^=1; new=sat_count(cs,a)
        for j in range(n): momentum[j]*=.90
        momentum[v]=.75*momentum[v]+new-old
        if new>best: best=new; stagn=0
        else: stagn+=1
        if stagn>max(20,n//2):
            hottest=sorted(range(len(cs)),key=lambda i:charge[i],reverse=True)[:max(2,n//16)]
            pool=list({v for i in hottest for v,_ in cs[i]})
            for vv in rng.sample(pool,min(len(pool),max(1,n//20))): a[vv]^=1
            stagn=0; escapes+=1
    return best==len(cs),budget,best,{'escapes':escapes,'accepted_uphill':0}

def junction_tunnel(cs,n,budget,rng):
    """Junction with depletion escape: adaptive barrier, tabu memory, thermal tunneling and coherent multi-flip pulse."""
    a=[rng.randrange(2) for _ in range(n)]
    charge=[1.0]*len(cs); momentum=[0.0]*n; tabu=[0]*n
    best=sat_count(cs,a); current=best; stagn=0; barrier=0.0
    escapes=0; uphill=0; last_signature=None; repeats=0
    for s in range(1,budget+1):
        u=unsat_idx(cs,a)
        if not u: return True,s,best,{'escapes':escapes,'accepted_uphill':uphill}
        us=set(u)
        for i in range(len(cs)):
            if i in us: charge[i]=min(40.0,charge[i]*1.10+0.20)
            else: charge[i]=max(1.0,charge[i]*.975)
        for v in range(n):
            if tabu[v]>0: tabu[v]-=1
            momentum[v]*=.88

        signature=tuple(sorted(u[:12]))
        repeats = repeats+1 if signature==last_signature else 0
        last_signature=signature
        barrier += 0.12 + 0.035*len(u) + 0.08*repeats
        temperature=min(3.5,0.12 + barrier/(8.0+n/8.0))

        touched={v for i in u for v,_ in cs[i]}
        ranked=[]
        for v in touched:
            pressure=sum(charge[i] for i in u if any(x==v for x,_ in cs[i]))
            d=flip_delta(cs,a,v,charge)
            penalty=2.2 if tabu[v]>0 else 0.0
            score=pressure+1.75*d+.40*momentum[v]-penalty+rng.uniform(-.15,.15)
            ranked.append((score,d,v))
        ranked.sort(reverse=True)
        _, d, v=ranked[0]

        # Thermal tunneling: sometimes accept a locally harmful flip as barrier energy rises.
        accept=True
        if d<0:
            accept = rng.random() < math.exp(d/max(.15,temperature))
            if accept: uphill+=1
        if not accept and len(ranked)>1:
            v=ranked[1][2]

        old=current; a[v]^=1; current=sat_count(cs,a)
        momentum[v]=.7*momentum[v]+(current-old); tabu[v]=max(3,n//16)
        if current>best:
            best=current; stagn=0; barrier*=.35; repeats=0
        else:
            stagn+=1

        # Coherent avalanche pulse: cross the basin wall using a tested multi-bit packet.
        trigger=max(12,n//3)
        if stagn>=trigger or barrier>max(8.0,n*.32):
            hottest=sorted(u,key=lambda i:charge[i],reverse=True)[:max(3,n//12)]
            pool=list({vv for i in hottest for vv,_ in cs[i]})
            base=current; best_trial=None
            widths=range(2,min(7,max(3,len(pool)))+1)
            for width in widths:
                for _ in range(5):
                    if len(pool)<width: continue
                    packet=rng.sample(pool,width)
                    for vv in packet:a[vv]^=1
                    q=sat_count(cs,a)
                    # permit crossing the wall, but prefer packets that reduce hot unsatisfied charge
                    hot_left=sum(charge[i] for i in hottest if not sat_clause(cs[i],a))
                    merit=q-0.015*hot_left+rng.uniform(-.02,.02)
                    for vv in packet:a[vv]^=1
                    if best_trial is None or merit>best_trial[0]: best_trial=(merit,q,packet)
            if best_trial:
                _,q,packet=best_trial
                for vv in packet:
                    a[vv]^=1; tabu[vv]=max(tabu[vv],max(4,n//12))
                current=q; escapes+=1
                if current>best: best=current
            # partial discharge, not full reset: preserves information while escaping basin
            barrier*=.18; stagn=0; repeats=0
            for i in hottest: charge[i]=max(1.0,charge[i]*.55)

    return best==len(cs),budget,best,{'escapes':escapes,'accepted_uphill':uphill}

def run():
    seed=440222; master=random.Random(seed)
    # Slightly harder grid than previous test; same instance shared by all methods.
    configs=[(3,32,round(4.26*32)),(3,48,round(4.26*48)),(3,64,round(4.26*64)),
             (5,36,round(6.10*36)),(5,48,round(6.10*48)),(5,64,round(6.10*64))]
    trials=16; budget_factor=28
    methods=[('walksat',walksat),('junction_base',junction_base),('junction_tunnel',junction_tunnel)]
    rows=[]; detail=[]
    for k,n,m in configs:
        raw={name:[] for name,_ in methods}
        for t in range(trials):
            inst_seed=master.randrange(10**9); cs=gen_planted(n,m,k,random.Random(inst_seed)); budget=budget_factor*n
            for idx,(name,fn) in enumerate(methods):
                rr=random.Random(inst_seed ^ (101+idx*1009))
                t0=time.perf_counter(); solved,steps,best,diag=fn(cs,n,budget,rr); ms=(time.perf_counter()-t0)*1000
                rec={'k':k,'n':n,'m':m,'trial':t,'method':name,'solved':solved,'steps':steps,'best_ratio':best/m,'ms':ms,**diag}
                raw[name].append(rec); detail.append(rec)
        for name,_ in methods:
            vals=raw[name]; sol=[x for x in vals if x['solved']]
            rows.append({'k':k,'n':n,'m':m,'alpha':m/n,'method':name,'trials':trials,
                'solve_rate':sum(x['solved'] for x in vals)/trials,
                'median_steps_solved':median([x['steps'] for x in sol]) if sol else None,
                'mean_best_ratio':mean(x['best_ratio'] for x in vals),'mean_ms':mean(x['ms'] for x in vals),
                'mean_escapes':mean(x['escapes'] for x in vals),'mean_uphill':mean(x['accepted_uphill'] for x in vals)})
    with open('/mnt/data/junction_tunnel_results.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    with open('/mnt/data/junction_tunnel_results.json','w') as f:
        json.dump({'seed':seed,'trials':trials,'budget_factor':budget_factor,'rows':rows,'detail':detail},f,indent=2)
    print(json.dumps(rows,indent=2))
if __name__=='__main__':run()
