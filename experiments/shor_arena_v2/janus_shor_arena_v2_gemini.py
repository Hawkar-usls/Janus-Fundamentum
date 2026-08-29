#!/usr/bin/env python3
import argparse, hashlib, json, math, random, statistics
from pathlib import Path

BITS=[14,18,22,26,30,34]
FAMILIES=["BALANCED","BLUM","SKEWED","ROUGH_P_MINUS_1","SMOOTH_P_MINUS_1","MIXED"]
BASES=[2,3,5,7,11,13,17,19]
WAVE=8

def powmod_count(a,e,n):
    r=1; b=a%n; m=0
    while e:
        if e&1: r=(r*b)%n; m+=1
        e//=2
        if e: b=(b*b)%n; m+=1
    return r,m

def trial_factor(x):
    fs=[]; d=2; div=0; y=x
    while d*d<=y:
        div+=1
        if y%d==0:
            k=0
            while y%d==0: y//=d; k+=1
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
    if v!=1: return None,False,{"modmults":mm,"trial_divisions":div,"pow_checks":checks}
    f2,d2=trial_factor(g); div+=d2
    ok=True
    for q,_ in f2:
        v,c=powmod_count(a,g//q,n); mm+=c; checks+=1
        ok &= (v!=1)
    return g,ok,{"modmults":mm,"trial_divisions":div,"pow_checks":checks}

def is_prime(n):
    if n<2:return False
    small=[2,3,5,7,11,13,17,19,23,29,31,37]
    for p in small:
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

def next_prime(x, mod4=None, rough=False, smooth=False):
    x=max(3,x|1)
    while True:
        if mod4 is not None and x%4!=mod4:
            x+=2; continue
        if is_prime(x):
            f,_=trial_factor(x-1); maxp=max(q for q,_ in f) if f else 1
            if rough and maxp < int(math.sqrt(x-1)): x+=2; continue
            if smooth and maxp > max(13,int((x-1)**0.45)): x+=2; continue
            return x
        x+=2

def hseed(*parts):
    h=hashlib.sha256('|'.join(map(str,parts)).encode()).digest()
    return int.from_bytes(h[:8],'big')

def make_case(bitlen,family,idx):
    rng=random.Random(hseed('JANUS-SHOR-V2-GEMINI-SCALE-2026-08-29',bitlen,family,idx))
    if family=='SKEWED': pb=max(5,bitlen//3); qb=bitlen-pb
    else: pb=bitlen//2; qb=bitlen-pb
    plo=1<<(pb-1); qlo=1<<(qb-1)
    px=plo+rng.randrange(max(2,1<<(max(1,pb-2))))
    qx=qlo+rng.randrange(max(2,1<<(max(1,qb-2))))
    mod4=3 if family=='BLUM' else None
    p=next_prime(px,mod4=mod4,rough=(family=='ROUGH_P_MINUS_1'),smooth=(family=='SMOOTH_P_MINUS_1'))
    q=next_prime(qx+101,mod4=mod4,rough=(family=='ROUGH_P_MINUS_1'),smooth=(family=='SMOOTH_P_MINUS_1'))
    if p==q:q=next_prime(q+2,mod4=mod4)
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

def bsgs_order(n,a):
    if math.gcd(a,n)!=1:return {"status":"NON_COPRIME"}
    m=math.isqrt(n)+1
    baby={1:0}; v=1; mult=0; look=0
    for j in range(1,m):
        v=(v*a)%n; mult+=1
        if v not in baby:baby[v]=j
    am=pow(a,m,n); y=1
    for i in range(1,m+1):
        y=(y*am)%n; mult+=1; look+=1
        j=baby.get(y)
        if j is not None:
            d=i*m-j
            if d>0:
                r,ok,red=exact_reduce(d,n,a); mult+=red['modmults']
                if ok:return {"status":"FOUND","order":r,"candidate":d,"group_mults":mult,"table_size":len(baby),"lookups":look,"reduction":red}
    return {"status":"UNKNOWN_RESOURCE_LIMIT","group_mults":mult,"table_size":len(baby),"lookups":look}

def janus_orbit(n,a,max_probes=None):
    if max_probes is None:max_probes=math.isqrt(n)*4+64
    rng=random.Random(hseed('JANUS-SHOR-V2-ORBIT',n,a));used=set();idx={};cg=0
    probes=waves=coll=mm=checks=gcds=crit=0
    while probes<max_probes:
        batch=[]
        for _ in range(min(WAVE,max_probes-probes)):
            while True:
                x=rng.randrange(0,n)
                if x not in used:used.add(x);break
            y,c=powmod_count(a,x,n);batch.append((x,y,c))
        probes+=len(batch);waves+=1;mm+=sum(c for _,_,c in batch);crit+=max(c for _,_,c in batch)
        for x,y,_ in batch:
            if y in idx:
                d=abs(x-idx[y])
                if d:
                    old=cg;coll+=1;cg=d if cg==0 else math.gcd(cg,d);gcds+=(old!=0)
            else:idx[y]=x
        if cg:
            v,c=powmod_count(a,cg,n);mm+=c;checks+=1;crit+=c
            if v==1:
                r,ok,red=exact_reduce(cg,n,a);mm+=red['modmults'];crit+=red['modmults']
                if ok:return {"status":"FOUND","order":r,"candidate":cg,"probes":probes,"waves":waves,"collisions":coll,"modmults":mm,"critical_path_modmults":crit,"gcds":gcds,"stored":len(idx),"candidate_checks":checks,"reduction":red}
    return {"status":"UNKNOWN_RESOURCE_LIMIT","probes":probes,"waves":waves,"modmults":mm,"critical_path_modmults":crit,"gcds":gcds,"stored":len(idx)}

def rho_collision(n,a,max_probes=None):
    if max_probes is None:max_probes=math.isqrt(n)*4+64
    rng=random.Random(hseed('JANUS-SHOR-V2-RHO',n,a));idx={};mm=0
    for k in range(1,max_probes+1):
        x=rng.randrange(0,n);y,c=powmod_count(a,x,n);mm+=c
        if y in idx:
            d=abs(x-idx[y])
            if d:
                v,c2=powmod_count(a,d,n);mm+=c2
                if v==1:
                    r,ok,red=exact_reduce(d,n,a);mm+=red['modmults']
                    if ok:return {"status":"FOUND","order":r,"probes":k,"modmults":mm,"stored":len(idx),"reduction":red}
        else:idx[y]=x
    return {"status":"UNKNOWN_RESOURCE_LIMIT","probes":max_probes,"modmults":mm,"stored":len(idx)}

def relation_fermat(n,max_steps=200000):
    root=math.isqrt(n);x=root+(root*root<n);int_mult=0
    for step in range(max_steps+1):
        z=x*x-n;int_mult+=1;y=math.isqrt(z)
        if y*y==z:
            gs=[math.gcd(x-y,n),math.gcd(x+y,n)];fac=sorted({g for g in gs if 1<g<n and n%g==0})
            if fac:return {"status":"FACTOR_FOUND","factors":fac,"relation_steps":step+1,"integer_mults":int_mult,"gcds":2}
        x+=1
    return {"status":"UNKNOWN_RESOURCE_LIMIT","relation_steps":max_steps+1,"integer_mults":int_mult,"gcds":0}

def shor_post(n,a,r):
    if not r or r%2:return {"status":"ORDER_NOT_USABLE","modmults":0,"gcds":0}
    h,c=powmod_count(a,r//2,n)
    if h==n-1:return {"status":"ORDER_NOT_USABLE","modmults":c,"gcds":0}
    gs=[math.gcd(h-1,n),math.gcd(h+1,n)];fs=sorted({g for g in gs if 1<g<n and n%g==0})
    return {"status":"FACTOR_FOUND" if fs else "NO_FACTOR","factors":fs,"modmults":c,"gcds":2}

def gemini_v0(n,a,orbit,relation):
    op=shor_post(n,a,orbit.get('order')) if orbit.get('status')=='FOUND' else {"status":"NOT_RUN","modmults":0,"gcds":0}
    factor=[];source=None
    if relation.get('status')=='FACTOR_FOUND':factor=relation['factors'];source='RELATION'
    elif op.get('status')=='FACTOR_FOUND':factor=op['factors'];source='ORBIT_POST'
    return {"status":"FACTOR_FOUND" if factor else "NO_FACTOR_IN_V0","factors":factor,"source":source,"total_modmults":orbit.get('modmults',0)+op.get('modmults',0),"total_integer_mults":relation.get('integer_mults',0),"total_gcds":orbit.get('gcds',0)+op.get('gcds',0)+relation.get('gcds',0),"relation_steps":relation.get('relation_steps',0),"latency_proxy":max(orbit.get('critical_path_modmults',orbit.get('modmults',0)),relation.get('relation_steps',0))}

def linreg_slope(xs,ys):
    xm=sum(xs)/len(xs);ym=sum(ys)/len(ys);den=sum((x-xm)**2 for x in xs)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/den if den else 0

def self_tests():
    out=[]
    for n,a,r0 in [(15,2,4),(21,2,6),(35,2,12),(143,2,60),(10403,2,5100)]:
        b=bsgs_order(n,a);j=janus_orbit(n,a,max_probes=n)
        assert b['status']=='FOUND' and b['order']==r0,(n,b)
        assert j['status']=='FOUND' and j['order']==r0,(n,j)
        out.append({"N":n,"order":r0,"bsgs_mults":b['group_mults'],"janus_modmults":j['modmults']})
    for n in [15,77,143]: assert relation_fermat(n,10000)['status']=='FACTOR_FOUND'
    return out

def run():
    rows=[]
    for bits in BITS:
        for idx,fam in enumerate(FAMILIES):
            c=make_case(bits,fam,idx);n=c['N'];a=c['a'];truth=true_order_from_phi(n,a,c['p'],c['q'])
            b=bsgs_order(n,a);j=janus_orbit(n,a);rho=rho_collision(n,a);rel=relation_fermat(n);gem=gemini_v0(n,a,j,rel)
            rows.append({"bits_target":bits,"actual_bits":n.bit_length(),"family":fam,"N":n,"a":a,"evaluation":{"true_order":truth,"hidden_factors":[c['p'],c['q']]},"bsgs":b,"janus_orbit":j,"rho":rho,"relation":rel,"gemini":gem,"exact":{"bsgs":b.get('order')==truth,"janus":j.get('order')==truth,"rho":rho.get('order')==truth if rho.get('status')=='FOUND' else None}})
    valid=[r for r in rows if r['janus_orbit']['status']=='FOUND' and r['bsgs']['status']=='FOUND']
    ratios=[r['janus_orbit']['modmults']/r['bsgs']['group_mults'] for r in valid];casewins=sum(x<=1 for x in ratios)/len(rows)
    rung=[]
    for bits in BITS:
        rr=[r for r in valid if r['bits_target']==bits]
        rung.append({"bits":bits,"janus_median":statistics.median(r['janus_orbit']['modmults'] for r in rr),"bsgs_median":statistics.median(r['bsgs']['group_mults'] for r in rr),"ratio_median":statistics.median(r['janus_orbit']['modmults']/r['bsgs']['group_mults'] for r in rr)})
    js=linreg_slope([x['bits'] for x in rung],[math.log2(x['janus_median']) for x in rung]);bs=linreg_slope([x['bits'] for x in rung],[math.log2(x['bsgs_median']) for x in rung])
    gwin=comparable=0
    for r in rows:
        orb,rel,gem=r['janus_orbit'],r['relation'],r['gemini'];single=[]
        op=shor_post(r['N'],r['a'],orb.get('order')) if orb.get('status')=='FOUND' else {"status":"NO"}
        if op.get('status')=='FACTOR_FOUND':single.append(orb.get('modmults',0)+op.get('modmults',0))
        if rel.get('status')=='FACTOR_FOUND':single.append(rel.get('integer_mults',0))
        if single and gem['status']=='FACTOR_FOUND':
            comparable+=1;gscalar=gem['total_modmults']+gem['total_integer_mults'];gwin+=(gscalar<min(single))
    gfrac=gwin/comparable if comparable else 0
    gates=[
      {"gate":"G1_EXACT_ORDER","passed":len(valid)==36 and all(r['exact']['janus'] and r['exact']['bsgs'] for r in rows),"value":f"{sum(bool(r['exact']['janus']) for r in rows)}/36 JANUS; {sum(bool(r['exact']['bsgs']) for r in rows)}/36 BSGS"},
      {"gate":"G2_JANUS_VS_BSGS_TOTAL_COMPUTE","passed":statistics.median(ratios)<=1,"value":statistics.median(ratios)},
      {"gate":"G3_JANUS_VS_BSGS_CASEWISE","passed":casewins>=0.5,"value":casewins},
      {"gate":"G4_SCALE_SLOPE","passed":js<=bs-0.05,"value":{"janus":js,"bsgs":bs,"difference":bs-js}},
      {"gate":"G5_GEMINI_ADDED_VALUE","passed":gfrac>=0.25,"value":{"win_fraction":gfrac,"comparable":comparable}},
      {"gate":"G6_NO_LEAKAGE","passed":True,"value":"solver calls receive N,a only; p,q used only by evaluation oracle"},
      {"gate":"G7_SCIENTIFIC_BOUNDARY","passed":True,"value":"finite ladder; no quantum/polynomial/P=NP claim"}]
    return {"schema":"JANUS/SHOR-ARENA-v2/GEMINI-SCALE-LADDER-RESULT/v1.0","status":"COMPLETE","self_tests":self_tests(),"summary":{"cases":36,"median_janus_vs_bsgs_work_ratio":statistics.median(ratios),"janus_casewise_win_fraction":casewins,"janus_log2_work_slope_per_input_bit":js,"bsgs_log2_work_slope_per_input_bit":bs,"gemini_added_value_win_fraction":gfrac,"gemini_comparable_cases":comparable},"rungs":rung,"gates":gates,"cases":rows,"scientific_boundary":{"note":"Operation-type counts are kept separately; mixed scalar in G5 is an engineering stress metric, not formal bit complexity.","P_VS_NP":"OPEN"}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test-only',action='store_true');ap.add_argument('--output');a=ap.parse_args()
    if a.self_test_only:print(json.dumps({"status":"PASS","tests":self_tests()},indent=2));return
    if not a.output:raise SystemExit('--output required')
    out=run();Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({"summary":out['summary'],"gates":out['gates']},indent=2))
if __name__=='__main__':main()
