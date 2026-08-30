#!/usr/bin/env python3
import csv, hashlib, io, json, math, random, statistics, urllib.request
from collections import defaultdict
from pathlib import Path

URL='https://raw.githubusercontent.com/BROOKELAB/Viral-dynamics-modeling/8d71ca82ac453a4b3c3c13d61a7174fbed4bdf8d/Data/data_samples.csv'
BLOB='a4b5cd9e06af494c859f9fefab194a703500af01'
PREREG='cb3cc9f20262e4d0c144d06ad4132cd35b83ac48'
OFFSETS=range(1,8); MIN_N=10; H_THRESHOLD=2.0; P_THRESHOLD=0.01; N_PERM=10000; SEED=33033; TOL=1e-9

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def ffloat(x):
    s='' if x is None else str(x).strip()
    if not s or s.upper() in {'NA','NAN','NULL','NONE'}: return None
    try:v=float(s)
    except ValueError:return None
    return v if math.isfinite(v) else None

def fetch():
    with urllib.request.urlopen(URL,timeout=30) as r:b=r.read()
    if blob_sha(b)!=BLOB: raise RuntimeError('blob mismatch')
    return b

def load(b):
    rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')))); g=defaultdict(list)
    for r in rows:
        sid=str(r.get('Ind','')).strip(); t=ffloat(r.get('Time'))
        if sid and t is not None:g[(sid,t)].append(r)
    u={}; amb=0
    for k,v in g.items():
        if len(v)!=1: amb+=1; continue
        r=v[0]; n=ffloat(r.get('Nasal_CN')); s=ffloat(r.get('Saliva_Ct'))
        u[k]={'subject':k[0],'time':k[1],'nasal':n,'saliva':s}
    return u,{'input_rows':len(rows),'subject_time_keys':len(g),'unique_keys':len(u),'ambiguous_keys':amb}

def get(u,sid,t):
    if (sid,t) in u:return u[(sid,t)]
    h=[v for (s,x),v in u.items() if s==sid and abs(x-t)<=TOL]
    return h[0] if len(h)==1 else None

def binom_cdf(k,n):return sum(math.comb(n,j) for j in range(k+1))/(2**n)
def binom_sf(k,n):return sum(math.comb(n,j) for j in range(k,n+1))/(2**n)
def sign_p(vals):
    nz=[x for x in vals if abs(x)>1e-12]; n=len(nz)
    if n==0:return 1.0,0,0,0
    pos=sum(x>0 for x in nz); neg=n-pos
    return min(1.0,2*min(binom_cdf(pos,n),binom_sf(pos,n))),n,pos,neg

def build_h(u):
    subjects=sorted({s for s,_ in u}); by_d={d:[] for d in OFFSETS}; by_subject={s:{} for s in subjects}
    for s in subjects:
        for d in OFFSETS:
            pre=get(u,s,-float(d)); post=get(u,s,float(d))
            if pre is None or post is None:continue
            vals=[pre['nasal'],pre['saliva'],post['nasal'],post['saliva']]
            if any(x is None for x in vals):continue
            if pre['nasal']>=48 or post['nasal']>=48 or pre['saliva']>=47 or post['saliva']>=47:continue
            h=(post['saliva']-post['nasal'])-(pre['saliva']-pre['nasal'])
            by_d[d].append((s,h)); by_subject[s][d]=h
    return by_d,by_subject

def main():
    b=fetch(); u,meta=load(b); by_d,by_subject=build_h(u)
    recs=[]; first=None; robust_opposite=None
    for d in OFFSETS:
        vals=[h for _,h in by_d[d]]; n=len(vals); med=statistics.median(vals) if vals else None
        p,nnz,pos,neg=sign_p(vals)
        pass_pos=bool(n>=MIN_N and med is not None and med>=H_THRESHOLD and p<=P_THRESHOLD)
        pass_neg=bool(n>=MIN_N and med is not None and med<=-H_THRESHOLD and p<=P_THRESHOLD)
        rec={'offset_day':d,'n_matched':n,'median_H':med,'sign_test_p':p if vals else None,'n_nonzero':nnz,'positive_H':pos,'negative_H':neg,'positive_criterion_pass':pass_pos,'opposite_criterion_pass':pass_neg}
        recs.append(rec)
        if first is None and pass_pos:first=rec.copy()
        if robust_opposite is None and pass_neg:robust_opposite=rec.copy()
    eligible_medians=[r['median_H'] for r in recs if r['n_matched']>=MIN_N and r['median_H'] is not None]
    obs_max=max(eligible_medians) if eligible_medians else None
    A=sum(eligible_medians) if eligible_medians else None
    subjects=sorted(by_subject)
    rng=random.Random(SEED); null_max=[]
    if obs_max is not None:
        for _ in range(N_PERM):
            signs={s:(1 if rng.random()<0.5 else -1) for s in subjects}
            meds=[]
            for d in OFFSETS:
                vals=[signs[s]*h for s,h in by_d[d]]
                if len(vals)>=MIN_N:meds.append(statistics.median(vals))
            null_max.append(max(meds) if meds else float('-inf'))
        fwp=(1+sum(x>=obs_max for x in null_max))/(N_PERM+1)
    else:fwp=None
    if first is not None and fwp is not None and fwp<=0.01:terminal='PASS'
    elif robust_opposite is not None or (fwp is not None and fwp>0.05) or (eligible_medians and max(eligible_medians)<=0):terminal='FAIL'
    else:terminal='EVIDENCE_INSUFFICIENT'
    result={'experiment_id':'C033_CROSS_COMPARTMENT_MIRROR_HYSTERESIS_RESULT_v1','prereg_commit':PREREG,'status':'COMPUTATION_COMPLETE',
            'input_integrity':{'git_blob_sha':blob_sha(b),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},'row_binding':meta,
            'per_offset':recs,'first_break':first,'opposite_first_break':robust_opposite,'global_A_sum_median_H':A,'observed_max_median_H':obs_max,
            'familywise_signflip_p':fwp,'null_max_summary':None if not null_max else {'iterations':len(null_max),'min':min(null_max),'median':statistics.median(null_max),'mean':statistics.fmean(null_max),'max':max(null_max),'count_ge':sum(x>=obs_max for x in null_max)},
            'terminal':terminal,'claim_ceiling':{'scientific_novelty':False,'independent_replication':False,'scientific_breakthrough':False,'outreach':'BLOCKED'}}
    Path('out').mkdir(exist_ok=True); Path('out/C033_CROSS_COMPARTMENT_MIRROR_HYSTERESIS_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    print('C033_COMPACT='+json.dumps({'per_offset':recs,'first_break':first,'opposite_first_break':robust_opposite,'global_A':A,'familywise_p':fwp,'terminal':terminal},sort_keys=True))
if __name__=='__main__':main()
