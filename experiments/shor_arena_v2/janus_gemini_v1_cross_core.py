#!/usr/bin/env python3
import argparse, hashlib, json, math, random, statistics
from pathlib import Path

BITS=[14,18,22,26,30,34]
FAMILIES=["BALANCED","BLUM","SKEWED","ROUGH_P_MINUS_1","FAR_FROM_SQUARE","MIXED"]
BASES=[2,3,5,7,11,13,17,19]
STEP_EXPS=[1,3,7,15,31,63,127,255]
WALKERS=8
SMALL_DIVS=[2,3,5,7,11,13]
FRESH_NS="JANUS-GEMINI-V1-FRESH-SCALE-2026-08-29"

def hseed(*parts):
    return int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'big')

def powmod_count(a,e,n):
    r=1; b=a%n; m=0
    while e:
        if e&1:
            r=(r*b)%n; m+=1
        e//=2
        if e:
            b=(b*b)%n; m+=1
    return r,m

def trial_factor(x):
    y=x; fs=[]; div=0; d=2
    while d*d<=y:
        div+=1
        if y%d==0:
            k=0
            while y%d==0:
                y//=d; k+=1
            fs.append((d,k))
        d=3 if d==2 else d+2
    if y>1: fs.append((y,1))
    return fs,div

def exact_reduce(candidate,n,a):
    g=candidate; fs,div=trial_factor(g); mm=0; checks=0
    for q,k in fs:
        for _ in range(k):
            if g%q: break
            v,c=powmod_count(a,g//q,n); mm+=c; checks+=1
            if v==1: g//=q
            else: break
    v,c=powmod_count(a,g,n); mm+=c; checks+=1
    if v!=1:
        return None,False,{"modmults":mm,"trial_divisions":div,"pow_checks":checks}
    f2,d2=trial_factor(g); div+=d2; ok=True
    for q,_ in f2:
        v,c=powmod_count(a,g//q,n); mm+=c; checks+=1
        ok &= (v!=1)
    return g,ok,{"modmults":mm,"trial_divisions":div,"pow_checks":checks,"prime_factors":f2}

def is_prime(n):
    if n<2:return False
    for p in [2,3,5,7,11,13,17,19,23,29,31,37]:
        if n%p==0:return n==p
    d=n-1;s=0
    while d%2==0:s+=1;d//=2
    for a in [2,325,9375,28178,450775,9780504,1795265022]:
        if a%n==0:continue
        x=pow(a,d,n)
        if x in (1,n-1):continue
        for _ in range(s-1):
            x=(x*x)%n
            if x==n-1:break
        else:return False
    return True

def next_prime(x,mod4=None,rough=False):
    x=max(3,x|1)
    while True:
        if mod4 is not None and x%4!=mod4:
            x+=2;continue
        if is_prime(x):
            if rough:
                f,_=trial_factor(x-1); mp=max((q for q,_ in f),default=1)
                if mp<int(math.sqrt(x-1)):
                    x+=2;continue
            return x
        x+=2

def make_case(bitlen,family,idx):
    rng=random.Random(hseed(FRESH_NS,bitlen,family,idx))
    if family=='SKEWED':
        pb=max(5,bitlen//3); qb=bitlen-pb
        px=(1<<(pb-1))+rng.randrange(max(2,1<<(max(1,pb-2))))
        qx=(1<<(qb-1))+rng.randrange(max(2,1<<(max(1,qb-2))))
    elif family=='FAR_FROM_SQUARE':
        pb=bitlen//2; qb=bitlen-pb
        px=(1<<(pb-1))+rng.randrange(max(2,1<<(max(1,pb-4))))
        qx=(1<<qb)-1-rng.randrange(max(2,1<<(max(1,qb-4))))
    else:
        pb=bitlen//2; qb=bitlen-pb
        px=(1<<(pb-1))+rng.randrange(max(2,1<<(max(1,pb-2))))
        qx=(1<<(qb-1))+rng.randrange(max(2,1<<(max(1,qb-2))))
    mod4=3 if family=='BLUM' else None
    rough=(family=='ROUGH_P_MINUS_1')
    p=next_prime(px,mod4=mod4,rough=rough)
    q=next_prime(qx+101,mod4=mod4,rough=rough)
    if p==q:q=next_prime(q+2,mod4=mod4,rough=rough)
    n=p*q
    for a in BASES:
        if math.gcd(a,n)==1:break
    return {"bit_target":bitlen,"family":family,"N":n,"a":a,"p":p,"q":q}

def true_order_from_phi(n,a,p,q):
    phi=(p-1)*(q-1); r=phi; fs,_=trial_factor(phi)
    for prime,k in fs:
        for _ in range(k):
            if r%prime==0 and pow(a,r//prime,n)==1:r//=prime
            else:break
    return r

def shor_post(n,a,r):
    if not r or r%2:return {"status":"ORDER_NOT_USABLE","modmults":0,"gcds":0,"factors":[]}
    h,c=powmod_count(a,r//2,n)
    if h==n-1:return {"status":"ORDER_NOT_USABLE","modmults":c,"gcds":0,"factors":[]}
    gs=[math.gcd(h-1,n),math.gcd(h+1,n)]; fac=sorted({g for g in gs if 1<g<n and n%g==0})
    return {"status":"FACTOR_FOUND" if fac else "NO_FACTOR","modmults":c,"gcds":2,"factors":fac}

def early_factor_from_multiple(n,a,d):
    mm=gcds=0; checks=0
    v,c=powmod_count(a,d,n); mm+=c; checks+=1
    if v!=1:
        return {"status":"INVALID_MULTIPLE","modmults":mm,"gcds":gcds,"trial_divisions":0,"checks":checks,"factors":[]}
    exps=[]
    for q in SMALL_DIVS:
        if d%q==0:
            e=d//q
            if e>0 and e not in exps:exps.append(e)
    for e in exps:
        x,c=powmod_count(a,e,n); mm+=c; checks+=1
        for z in (x-1,x+1):
            g=math.gcd(z,n); gcds+=1
            if 1<g<n and n%g==0:
                return {"status":"FACTOR_FOUND","factors":sorted({g,n//g}),"source_exponent":e,"multiple":d,"modmults":mm,"gcds":gcds,"trial_divisions":0,"checks":checks}
    return {"status":"NO_FACTOR","factors":[],"multiple":d,"modmults":mm,"gcds":gcds,"trial_divisions":0,"checks":checks}

def step_table(a,n):
    tab=[]; mm=0
    for e in STEP_EXPS:
        v,c=powmod_count(a,e,n); tab.append(v); mm+=c
    return tab,mm

def partition(y,salt):
    z=(y ^ (y>>11) ^ (y>>23) ^ salt) & ((1<<64)-1)
    z ^= (z>>30); z=(z*0xbf58476d1ce4e5b9)&((1<<64)-1)
    z ^= (z>>27); z=(z*0x94d049bb133111eb)&((1<<64)-1)
    z ^= (z>>31)
    return z % len(STEP_EXPS)

def incremental_orbit_collision(n,a,walkers=WALKERS,max_transitions=None):
    if math.gcd(n,a)!=1:return {"status":"NON_COPRIME"}
    if max_transitions is None:max_transitions=4*math.isqrt(n)+64
    table,mm=step_table(a,n)
    states=[]; store={}; peak=0; gcds=0; transitions=0; collisions=0
    y=1
    for w in range(walkers):
        y=(y*a)%n; mm+=1
        e=w+1; salt=hseed('GEMINI-V1-WALKER',n,a,w)
        states.append([y,e,salt])
        prev=store.get(y)
        if prev and prev[0]!=e:
            d=abs(e-prev[0])
            if d:return {"status":"COLLISION","multiple":d,"modmults":mm,"gcds":gcds,"transitions":transitions,"peak_stored":len(store),"collisions":1}
        store[y]=(e,w); peak=max(peak,len(store))
    while transitions<max_transitions:
        for w in range(walkers):
            if transitions>=max_transitions:break
            y,e,salt=states[w]; j=partition(y,salt)
            y=(y*table[j])%n; e+=STEP_EXPS[j]; mm+=1; transitions+=1
            states[w]=[y,e,salt]
            prev=store.get(y)
            if prev is not None and prev[0]!=e:
                d=abs(e-prev[0]); collisions+=1
                return {"status":"COLLISION","multiple":d,"modmults":mm,"gcds":gcds,"transitions":transitions,"peak_stored":max(peak,len(store)),"collisions":collisions}
            if prev is None:
                store[y]=(e,w); peak=max(peak,len(store))
    return {"status":"UNKNOWN_RESOURCE_LIMIT","modmults":mm,"gcds":gcds,"transitions":transitions,"peak_stored":peak,"collisions":collisions}

def orbit_standalone_factor(n,a):
    col=incremental_orbit_collision(n,a)
    mm=col.get('modmults',0); gcds=col.get('gcds',0); div=0
    if col.get('status')!='COLLISION':
        return {"status":"UNKNOWN_RESOURCE_LIMIT","modmults":mm,"gcds":gcds,"trial_divisions":div,"peak_stored":col.get('peak_stored',0),"transitions":col.get('transitions',0)}
    d=col['multiple']; r,ok,red=exact_reduce(d,n,a); mm+=red['modmults']; div+=red['trial_divisions']
    if not ok:
        return {"status":"CERTIFICATE_FAILURE","modmults":mm,"gcds":gcds,"trial_divisions":div,"peak_stored":col.get('peak_stored',0)}
    post=shor_post(n,a,r); mm+=post['modmults']; gcds+=post['gcds']
    return {"status":"FACTOR_FOUND" if post['status']=='FACTOR_FOUND' else "ORDER_FOUND_NO_FACTOR","factors":post.get('factors',[]),"order":r,"collision_multiple":d,"modmults":mm,"gcds":gcds,"trial_divisions":div,"peak_stored":col.get('peak_stored',0),"transitions":col.get('transitions',0)}

def rho_order(n,a,max_transitions=None):
    if max_transitions is None:max_transitions=16*math.isqrt(n)+256
    table,mm=step_table(a,n); salt=hseed('GEMINI-V1-RHO',n,a)
    y=1;e=0;store={1:0};peak=1
    for t in range(1,max_transitions+1):
        j=partition(y,salt); y=(y*table[j])%n; e+=STEP_EXPS[j];mm+=1
        if y in store and store[y]!=e:
            d=abs(e-store[y]); r,ok,red=exact_reduce(d,n,a);mm+=red['modmults']
            return {"status":"FOUND" if ok else "CERTIFICATE_FAILURE","order":r,"candidate":d,"modmults":mm,"trial_divisions":red['trial_divisions'],"gcds":0,"peak_stored":peak,"transitions":t}
        if y not in store:store[y]=e;peak=max(peak,len(store))
    return {"status":"UNKNOWN_RESOURCE_LIMIT","modmults":mm,"trial_divisions":0,"gcds":0,"peak_stored":peak,"transitions":max_transitions}

def rho_factor(n,a):
    r=rho_order(n,a);mm=r.get('modmults',0);div=r.get('trial_divisions',0);gcds=0
    if r.get('status')!='FOUND':return {"status":"UNKNOWN_RESOURCE_LIMIT","modmults":mm,"trial_divisions":div,"gcds":gcds,"peak_stored":r.get('peak_stored',0)}
    post=shor_post(n,a,r['order']);mm+=post['modmults'];gcds+=post['gcds']
    return {"status":"FACTOR_FOUND" if post['status']=='FACTOR_FOUND' else "ORDER_FOUND_NO_FACTOR","factors":post.get('factors',[]),"order":r['order'],"modmults":mm,"trial_divisions":div,"gcds":gcds,"peak_stored":r.get('peak_stored',0)}

def bsgs_order(n,a):
    if math.gcd(a,n)!=1:return {"status":"NON_COPRIME"}
    m=math.isqrt(n)+1; baby={1:0};v=1;mult=0;look=0;div=0
    for j in range(1,m):
        v=(v*a)%n;mult+=1
        if v not in baby:baby[v]=j
    am,c=powmod_count(a,m,n);mult+=c;y=1
    for i in range(1,m+1):
        y=(y*am)%n;mult+=1;look+=1;j=baby.get(y)
        if j is not None:
            d=i*m-j
            if d>0:
                r,ok,red=exact_reduce(d,n,a);mult+=red['modmults'];div+=red['trial_divisions']
                if ok:return {"status":"FOUND","order":r,"group_mults":mult,"trial_divisions":div,"gcds":0,"peak_stored":len(baby),"lookups":look}
    return {"status":"UNKNOWN_RESOURCE_LIMIT","group_mults":mult,"trial_divisions":div,"gcds":0,"peak_stored":len(baby),"lookups":look}

def bsgs_factor(n,a):
    b=bsgs_order(n,a);mm=b.get('group_mults',0);div=b.get('trial_divisions',0);gcds=0
    if b.get('status')!='FOUND':return {"status":"UNKNOWN_RESOURCE_LIMIT","modmults":mm,"trial_divisions":div,"gcds":gcds,"peak_stored":b.get('peak_stored',0)}
    post=shor_post(n,a,b['order']);mm+=post['modmults'];gcds+=post['gcds']
    return {"status":"FACTOR_FOUND" if post['status']=='FACTOR_FOUND' else "ORDER_FOUND_NO_FACTOR","factors":post.get('factors',[]),"order":b['order'],"modmults":mm,"trial_divisions":div,"gcds":gcds,"peak_stored":b.get('peak_stored',0)}

def relation_scout(n,bits):
    budget=bits**3; root=math.isqrt(n);x=root+(root*root<n);ints=0;gcds=0;best_gap=None
    for step in range(budget):
        z=x*x-n;ints+=1;y=math.isqrt(z);gap=abs(z-y*y)
        if best_gap is None or gap<best_gap:best_gap=gap
        if y*y==z:
            gs=[math.gcd(x-y,n),math.gcd(x+y,n)];gcds+=2;fac=sorted({g for g in gs if 1<g<n and n%g==0})
            if fac:return {"status":"FACTOR_FOUND","factors":fac,"integer_mults":ints,"gcds":gcds,"trial_divisions":0,"peak_stored":1,"steps":step+1,"best_square_gap":best_gap}
        x+=1
    return {"status":"UNKNOWN_RESOURCE_LIMIT","factors":[],"integer_mults":ints,"gcds":gcds,"trial_divisions":0,"peak_stored":1,"steps":budget,"best_square_gap":best_gap}

def work_proxy(d):
    return int(d.get('modmults',0))+int(d.get('integer_mults',0))+int(d.get('gcds',0))+int(d.get('trial_divisions',0))

def gemini_v1(n,a,bits):
    rel=relation_scout(n,bits); total={"modmults":0,"integer_mults":rel.get('integer_mults',0),"gcds":rel.get('gcds',0),"trial_divisions":0}; peak=rel.get('peak_stored',0)
    if rel['status']=='FACTOR_FOUND':
        out={"status":"FACTOR_FOUND","factors":rel['factors'],"source":"RELATION_DIRECT","relation":rel,"orbit":None,"early":None,"ledger":total,"peak_stored":peak,"cross_core_synergy":False};out['scalar_work_proxy']=work_proxy(total);return out
    col=incremental_orbit_collision(n,a); total['modmults']+=col.get('modmults',0); total['gcds']+=col.get('gcds',0);peak=max(peak,col.get('peak_stored',0))
    if col.get('status')!='COLLISION':
        out={"status":"UNKNOWN_RESOURCE_LIMIT","source":None,"relation":rel,"orbit":col,"early":None,"ledger":total,"peak_stored":peak,"cross_core_synergy":False};out['scalar_work_proxy']=work_proxy(total);return out
    early=early_factor_from_multiple(n,a,col['multiple']); total['modmults']+=early['modmults'];total['gcds']+=early['gcds']
    if early['status']=='FACTOR_FOUND':
        out={"status":"FACTOR_FOUND","factors":early['factors'],"source":"ORBIT_COLLISION_TO_EARLY_FACTOR","relation":rel,"orbit":col,"early":early,"ledger":total,"peak_stored":peak,"cross_core_synergy":True};out['scalar_work_proxy']=work_proxy(total);return out
    r,ok,red=exact_reduce(col['multiple'],n,a);total['modmults']+=red['modmults'];total['trial_divisions']+=red['trial_divisions']
    if not ok:
        out={"status":"CERTIFICATE_FAILURE","source":None,"relation":rel,"orbit":col,"early":early,"ledger":total,"peak_stored":peak,"cross_core_synergy":False};out['scalar_work_proxy']=work_proxy(total);return out
    post=shor_post(n,a,r);total['modmults']+=post['modmults'];total['gcds']+=post['gcds']
    st='FACTOR_FOUND' if post['status']=='FACTOR_FOUND' else 'ORDER_FOUND_NO_FACTOR'
    out={"status":st,"factors":post.get('factors',[]),"order":r,"source":"ORBIT_FULL_ORDER_POST" if st=='FACTOR_FOUND' else None,"relation":rel,"orbit":col,"early":early,"ledger":total,"peak_stored":peak,"cross_core_synergy":False};out['scalar_work_proxy']=work_proxy(total);return out

def exact_factor_ok(n,res):
    if res.get('status')!='FACTOR_FOUND':return True
    fs=res.get('factors',[])
    return bool(fs) and all(1<f<n and n%f==0 for f in fs)

def self_tests():
    tests=[]
    for n,a,r0 in [(15,2,4),(21,2,6),(35,2,12),(143,2,60),(10403,2,5100)]:
        b=bsgs_order(n,a);rho=rho_order(n,a)
        assert b.get('status')=='FOUND' and b.get('order')==r0,(n,b)
        assert rho.get('status')=='FOUND' and rho.get('order')==r0,(n,rho)
        col=incremental_orbit_collision(n,a,max_transitions=max(n if n<20000 else 4*math.isqrt(n)+64,64))
        assert col.get('status')=='COLLISION',(n,col)
        rr,ok,_=exact_reduce(col['multiple'],n,a);assert ok and rr==r0,(n,col,rr)
        tests.append({"N":n,"order":r0,"bsgs_work":work_proxy({"modmults":b['group_mults'],"trial_divisions":b['trial_divisions']}),"rho_work":work_proxy(rho),"incremental_orbit_transitions":col['transitions']})
    for n in [15,77,143]:assert relation_scout(n,n.bit_length())['status']=='FACTOR_FOUND'
    return tests

def linreg(xs,ys):
    xm=sum(xs)/len(xs);ym=sum(ys)/len(ys);den=sum((x-xm)**2 for x in xs)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/den if den else 0.0

def run_fresh():
    rows=[]
    for bits in BITS:
        for idx,fam in enumerate(FAMILIES):
            c=make_case(bits,fam,idx);n=c['N'];a=c['a'];truth=true_order_from_phi(n,a,c['p'],c['q'])
            bso=bsgs_order(n,a);rhoo=rho_order(n,a);bsf=bsgs_factor(n,a);rhof=rho_factor(n,a);rel=relation_scout(n,n.bit_length());orb=orbit_standalone_factor(n,a);gem=gemini_v1(n,a,n.bit_length())
            rows.append({"bits_target":bits,"actual_bits":n.bit_length(),"family":fam,"N":n,"a":a,"evaluation":{"hidden_factors":[c['p'],c['q']],"true_order":truth},"order_track":{"bsgs":bso,"rho":rhoo,"bsgs_exact":bso.get('order')==truth,"rho_exact":(rhoo.get('order')==truth if rhoo.get('status')=='FOUND' else None)},"factor_track":{"bsgs_shor":bsf,"rho_shor":rhof,"relation":rel,"orbit_standalone":orb,"gemini":gem},"exact":{"bsgs_factor":exact_factor_ok(n,bsf),"rho_factor":exact_factor_ok(n,rhof),"relation_factor":exact_factor_ok(n,rel),"orbit_factor":exact_factor_ok(n,orb),"gemini_factor":exact_factor_ok(n,gem)}})
    synergy=0;gem_success=0;comp_const=0;strong_ratios=[]; strong_comp=0
    for r in rows:
        f=r['factor_track'];g=f['gemini']
        if g['status']=='FACTOR_FOUND':gem_success+=1
        singles=[]
        if f['relation']['status']=='FACTOR_FOUND':singles.append(work_proxy(f['relation']))
        if f['orbit_standalone']['status']=='FACTOR_FOUND':singles.append(work_proxy(f['orbit_standalone']))
        if g['status']=='FACTOR_FOUND' and singles:
            comp_const+=1;synergy += (g['scalar_work_proxy'] < min(singles))
        strong=[]
        if f['bsgs_shor']['status']=='FACTOR_FOUND':strong.append(work_proxy(f['bsgs_shor']))
        if f['rho_shor']['status']=='FACTOR_FOUND':strong.append(work_proxy(f['rho_shor']))
        if g['status']=='FACTOR_FOUND' and strong:
            strong_comp+=1; strong_ratios.append(g['scalar_work_proxy']/min(strong))
    synergy_frac=synergy/len(rows);medstrong=statistics.median(strong_ratios) if strong_ratios else None
    rung=[]
    for bits in BITS:
        rr=[r for r in rows if r['bits_target']==bits]
        bmed=statistics.median(work_proxy({"modmults":x['order_track']['bsgs'].get('group_mults',0),"trial_divisions":x['order_track']['bsgs'].get('trial_divisions',0)}) for x in rr)
        rmed=statistics.median(work_proxy(x['order_track']['rho']) for x in rr)
        gmed=statistics.median(x['factor_track']['gemini']['scalar_work_proxy'] for x in rr)
        rung.append({"bits":bits,"bsgs_order_median_work":bmed,"rho_order_median_work":rmed,"gemini_factor_median_work":gmed})
    slope=linreg([x['bits'] for x in rung],[math.log2(max(1,x['gemini_factor_median_work'])) for x in rung])
    exact_ok=all(all(x['exact'].values()) and x['order_track']['bsgs_exact'] and (x['order_track']['rho']['status']!='FOUND' or x['order_track']['rho_exact']) for x in rows)
    mem_ok=all(all('peak_stored' in x['factor_track'][k] for k in ['bsgs_shor','rho_shor','relation','orbit_standalone','gemini']) for x in rows)
    donor_ok=all(x['factor_track']['gemini'].get('ledger') is not None and x['factor_track']['gemini']['scalar_work_proxy']==work_proxy(x['factor_track']['gemini']['ledger']) for x in rows)
    gates=[
      {"gate":"G1_EXACT_RETURNED_RESULTS","passed":exact_ok,"value":"all exact factor receipts valid; BSGS/rho order exact"},
      {"gate":"G2_CROSS_CORE_ADDED_VALUE","passed":synergy_frac>=0.25,"value":{"synergy_wins":synergy,"fraction_over_all_fresh_cases":synergy_frac,"comparable_constituent_cases":comp_const},"criterion":">= 0.25 of all 36 fresh cases"},
      {"gate":"G3_STRONG_BASELINE_MEDIAN","passed":medstrong is not None and medstrong<=1.0,"value":{"median_ratio":medstrong,"comparable_factor_cases":strong_comp},"criterion":"<= 1.0"},
      {"gate":"G4_MEMORY_LEDGER","passed":mem_ok,"value":"peak_stored reported"},
      {"gate":"G5_NO_DONOR_COST_ERASURE","passed":donor_ok,"value":"GEMINI scalar proxy equals charged ledger"},
      {"gate":"G6_SCALE_SLOPE","passed":True,"value":{"gemini_log2_work_slope_per_target_bit":slope},"criterion":"informational only"},
      {"gate":"G7_NO_LEAKAGE","passed":True,"value":"solver calls constructed from N,a only; p,q only evaluation truth"}
    ]
    summary={"fresh_cases":len(rows),"gemini_factor_success":gem_success,"cross_core_synergy_wins":synergy,"cross_core_synergy_fraction":synergy_frac,"median_gemini_vs_strong_factor_baseline_ratio":medstrong,"strong_factor_comparable_cases":strong_comp,"gemini_log2_work_slope_per_target_bit":slope,"performance_hypothesis_pass":gates[1]['passed'] and gates[2]['passed']}
    return rows,rung,summary,gates

def historical_regressions():
    out=[]
    for n,a,label in [(489407411,2,"OLD_ORBIT_ENEMY_66_9592"),(360253417,2,"OLD_ORBIT_SURVIVOR")]:
        bits=n.bit_length();col=incremental_orbit_collision(n,a);rel=relation_scout(n,bits);gem=gemini_v1(n,a,bits)
        out.append({"label":label,"N":n,"a":a,"incremental_orbit":col,"relation":rel,"gemini":gem})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test-only',action='store_true');ap.add_argument('--output')
    args=ap.parse_args();tests=self_tests()
    if args.self_test_only:
        print(json.dumps({"status":"PASS","tests":tests},indent=2));return
    if not args.output:ap.error('--output required')
    rows,rung,summary,gates=run_fresh()
    result={"schema":"JANUS/GEMINI-V1/FRESH-SCALE-RESULT/v1.0","status":"COMPLETE","self_tests":tests,"historical_nonvoting_regressions":historical_regressions(),"summary":summary,"rung_summary":rung,"gates":gates,"cases":rows,"scientific_boundary":{"polynomial_time_factoring":False,"asymptotic_theorem":False,"P_VS_NP":"OPEN"}}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({"summary":summary,"gates":gates,"rung_summary":rung},indent=2))
if __name__=='__main__':main()
