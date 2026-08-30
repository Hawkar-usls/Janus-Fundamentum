#!/usr/bin/env python3
import hashlib, json, math, random, statistics, urllib.request
from collections import defaultdict
from pathlib import Path
import openpyxl

URL='https://data.caltech.edu/records/0yw13-j0441/files/SARS_CoV_2_extreme_differences_in_viral_loads.xlsx?download=1'
MD5='6e6216d751c95b6afb6a7d0d96da6f1a'
PREREG='7117688fdec64f8c35f3d0870f4e1ba2315da7c9'
SCHEMA='45c232f90e4db23c6b2a390b1c5ddfa65fa34088'
MIN_VISITS=5
MIN_RANGE=1.0
MIN_SUBJECTS=10
AREA_THRESHOLD=-0.10
P_THRESHOLD=0.01
N_PERM=10000
SEED=34034


def fnum(x):
    if x is None: return None
    if isinstance(x,(int,float)):
        v=float(x); return v if math.isfinite(v) else None
    s=str(x).strip()
    if not s or s.lower() in {'na','nan','nd','n/a','none','not detected','not quantifiable','negative'}: return None
    try: v=float(s)
    except Exception: return None
    return v if math.isfinite(v) else None


def fetch():
    req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 JANUS-C034-public-data-replay/1.0'})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read()
    got=hashlib.md5(b).hexdigest()
    if got!=MD5: raise RuntimeError(f'md5 mismatch {got}')
    Path('tmp').mkdir(exist_ok=True); Path('tmp/c034.xlsx').write_bytes(b)
    return b


def sign_test_p(vals):
    nz=[v for v in vals if abs(v)>1e-15]
    n=len(nz)
    if n==0:return 1.0,0,0,0
    neg=sum(v<0 for v in nz); pos=n-neg
    k=min(neg,pos)
    tail=sum(math.comb(n,j) for j in range(k+1))/(2**n)
    return min(1.0,2*tail),n,neg,pos


def area(points):
    s=0.0
    n=len(points)
    for i in range(n):
        x1,y1=points[i]; x2,y2=points[(i+1)%n]
        s += x1*y2-x2*y1
    return 0.5*s


def normalized_area(points):
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    rx=max(xs)-min(xs); ry=max(ys)-min(ys)
    if rx<MIN_RANGE or ry<MIN_RANGE:return None,rx,ry
    return area(points)/(rx*ry),rx,ry


def load_subjects(path):
    wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    ws=wb['MainDataTable']
    rows=ws.iter_rows(values_only=True)
    header=[str(x).strip() if x is not None else '' for x in next(rows)]
    idx={h:i for i,h in enumerate(header)}
    need=['participantid','timefromenrollment','salivaviralload','nasalviralload']
    for k in need:
        if k not in idx: raise RuntimeError(f'missing column {k}')
    grouped=defaultdict(list); raw_rows=0; candidate_rows=0
    for r in rows:
        raw_rows+=1
        sid='' if r[idx['participantid']] is None else str(r[idx['participantid']]).strip()
        t=fnum(r[idx['timefromenrollment']]); s=fnum(r[idx['salivaviralload']]); n=fnum(r[idx['nasalviralload']])
        if not sid or t is None or s is None or n is None or s<=0 or n<=0: continue
        candidate_rows+=1
        grouped[(sid,t)].append((math.log10(n),math.log10(s)))
    by_sub=defaultdict(list); ambiguous=0
    for (sid,t),pts in grouped.items():
        if len(pts)!=1:
            ambiguous+=1; continue
        by_sub[sid].append((t,pts[0][0],pts[0][1]))
    return by_sub,{'raw_rows':raw_rows,'candidate_positive_paired_rows':candidate_rows,'ambiguous_subject_time_keys':ambiguous,'subjects_with_any_positive_pair':len(by_sub)}


def subject_records(by_sub):
    recs=[]
    eligible=[]
    for sid,vals in sorted(by_sub.items()):
        vals=sorted(vals,key=lambda z:z[0])
        pts=[(x,y) for _,x,y in vals]
        if len(pts)<MIN_VISITS:
            recs.append({'subject':sid,'eligible':False,'reason':'TOO_FEW_VISITS','n_visits':len(pts)})
            continue
        a,rx,ry=normalized_area(pts)
        if a is None:
            recs.append({'subject':sid,'eligible':False,'reason':'DYNAMIC_RANGE_LT_1_LOG','n_visits':len(pts),'nasal_range':rx,'saliva_range':ry})
            continue
        r={'subject':sid,'eligible':True,'n_visits':len(pts),'normalized_area':a,'signed_area':area(pts),'nasal_range':rx,'saliva_range':ry,'times':[v[0] for v in vals]}
        recs.append(r); eligible.append((sid,pts,a))
    return recs,eligible


def main():
    b=fetch(); by_sub,meta=load_subjects('tmp/c034.xlsx'); recs,elig=subject_records(by_sub)
    vals=[a for _,_,a in elig]
    result={'experiment_id':'C034_SPECIMEN_PHASE_HYSTERESIS_LOOP_RESULT_v1','prereg_commit':PREREG,'schema_binding_commit':SCHEMA,'status':'COMPUTATION_COMPLETE',
            'input_integrity':{'md5':hashlib.md5(b).hexdigest(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},'row_binding':meta,'subjects':recs,
            'frozen_gate':{'min_subjects':MIN_SUBJECTS,'median_area_max':AREA_THRESHOLD,'sign_p_max':P_THRESHOLD,'permutation_p_max':P_THRESHOLD,'permutations':N_PERM,'seed':SEED}}
    if len(vals)<MIN_SUBJECTS:
        result.update({'eligible_subjects':len(vals),'terminal':'EVIDENCE_INSUFFICIENT','reason':'fewer than frozen minimum eligible subjects','claim_ceiling':{'scientific_breakthrough':False,'outreach':'BLOCKED'}})
    else:
        obs=statistics.median(vals); sp,nnz,neg,pos=sign_test_p(vals)
        rng=random.Random(SEED); null=[]
        for _ in range(N_PERM):
            perm_areas=[]
            for sid,pts,a in elig:
                q=list(pts); rng.shuffle(q)
                pa,_,_=normalized_area(q)
                perm_areas.append(pa)
            null.append(statistics.median(perm_areas))
        pp=(1+sum(x<=obs for x in null))/(N_PERM+1)
        opposite = obs>=0 and sp<=P_THRESHOLD and pos>neg
        if obs<=AREA_THRESHOLD and sp<=P_THRESHOLD and neg>pos and pp<=P_THRESHOLD: terminal='PASS'
        elif obs>=0 or opposite or sp>0.05 or pp>0.05: terminal='FAIL'
        else: terminal='EVIDENCE_INSUFFICIENT'
        result.update({'eligible_subjects':len(vals),'median_normalized_area':obs,'sign_test_p':sp,'n_nonzero':nnz,'negative_areas':neg,'positive_areas':pos,
                       'chronology_permutation_p':pp,'null_median_summary':{'min':min(null),'median':statistics.median(null),'mean':statistics.fmean(null),'max':max(null),'count_le_observed':sum(x<=obs for x in null)},
                       'terminal':terminal,'claim_ceiling':{'path_dependence_observable_tested':True,'causation':False,'scientific_novelty':False,'independent_second_replication':False,'scientific_breakthrough':False,'outreach':'BLOCKED'}})
    Path('out').mkdir(exist_ok=True); Path('out/C034_SPECIMEN_PHASE_HYSTERESIS_LOOP_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    compact={k:result.get(k) for k in ['eligible_subjects','median_normalized_area','sign_test_p','negative_areas','positive_areas','chronology_permutation_p','terminal','reason']}
    print('C034_COMPACT='+json.dumps(compact,sort_keys=True))

if __name__=='__main__': main()
