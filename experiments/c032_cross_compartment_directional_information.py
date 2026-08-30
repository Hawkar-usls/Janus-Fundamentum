#!/usr/bin/env python3
import csv, hashlib, io, json, math, random, statistics, urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np

URL='https://raw.githubusercontent.com/BROOKELAB/Viral-dynamics-modeling/8d71ca82ac453a4b3c3c13d61a7174fbed4bdf8d/Data/data_samples.csv'
BLOB='a4b5cd9e06af494c859f9fefab194a703500af01'
PREREG='eb87f246bfcb8fb9236ed76a07063d73f6fca05e'
N_PERM=1000
MIN_N=30
MIN_SUBJ=10
TOL=1e-9


def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def ffloat(x):
    s='' if x is None else str(x).strip()
    if not s or s.upper() in {'NA','NAN','NULL','NONE'}: return None
    try: v=float(s)
    except ValueError: return None
    return v if math.isfinite(v) else None


def fetch():
    with urllib.request.urlopen(URL,timeout=30) as r: b=r.read()
    if blob_sha(b)!=BLOB: raise RuntimeError('blob mismatch')
    return b


def unique_rows(b):
    raw=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
    g=defaultdict(list)
    for r in raw:
        sid=str(r.get('Ind','')).strip(); t=ffloat(r.get('Time'))
        if sid and t is not None: g[(sid,t)].append(r)
    u={}; amb=0
    for k,v in g.items():
        if len(v)!=1: amb+=1; continue
        r=v[0]
        u[k]={'subject':k[0],'time':k[1],'nasal':ffloat(r.get('Nasal_CN')),'saliva':ffloat(r.get('Saliva_Ct'))}
    return u, {'input_rows':len(raw),'subject_time_keys':len(g),'unique_keys':len(u),'ambiguous_keys':amb}


def lookup(u,sid,t):
    if (sid,t) in u: return u[(sid,t)]
    h=[v for (s,x),v in u.items() if s==sid and abs(x-t)<=TOL]
    return h[0] if len(h)==1 else None


def transitions(u):
    out=[]
    for (sid,t),cur in sorted(u.items(),key=lambda z:(z[0][0],z[0][1])):
        nxt=lookup(u,sid,t+1.0)
        if nxt is None: continue
        vals=[cur['nasal'],nxt['nasal'],cur['saliva'],nxt['saliva']]
        if any(x is None for x in vals): continue
        if cur['nasal']>=48 or nxt['nasal']>=48 or cur['saliva']>=47 or nxt['saliva']>=47: continue
        out.append({'subject':sid,'time':float(t),'nasal':float(cur['nasal']),'saliva':float(cur['saliva']),
                    'd_nasal':float(nxt['nasal']-cur['nasal']),'d_saliva':float(nxt['saliva']-cur['saliva'])})
    return out


def loso(rows, direction, enriched, override=None):
    # direction SN: target d_nasal, base current nasal, cross saliva. NS is mirror.
    subjects=sorted({r['subject'] for r in rows}); indexed=list(enumerate(rows)); preds=[None]*len(rows)
    for sid in subjects:
        train=[(i,r) for i,r in indexed if r['subject']!=sid]
        test=[(i,r) for i,r in indexed if r['subject']==sid]
        X=[]; y=[]
        for i,r in train:
            if direction=='SN': base=r['nasal']; cross=r['saliva']; target=r['d_nasal']
            else: base=r['saliva']; cross=r['nasal']; target=r['d_saliva']
            if override is not None: cross=override[i]
            feat=[1.0,base,r['time']]+([cross] if enriched else [])
            X.append(feat); y.append(target)
        beta,_,_,_=np.linalg.lstsq(np.asarray(X,float),np.asarray(y,float),rcond=None)
        for i,r in test:
            if direction=='SN': base=r['nasal']; cross=r['saliva']
            else: base=r['saliva']; cross=r['nasal']
            if override is not None: cross=override[i]
            feat=[1.0,base,r['time']]+([cross] if enriched else [])
            preds[i]=float(np.dot(np.asarray(feat,float),beta))
    return preds


def mae(rows,preds,direction):
    key='d_nasal' if direction=='SN' else 'd_saliva'
    return float(statistics.fmean(abs(r[key]-p) for r,p in zip(rows,preds)))


def directional(rows,direction,seed):
    pa=loso(rows,direction,False); pb=loso(rows,direction,True)
    a=mae(rows,pa,direction); b=mae(rows,pb,direction); gain=(a-b)/a
    cross=[r['saliva'] if direction=='SN' else r['nasal'] for r in rows]
    rng=random.Random(seed); null=[]
    for _ in range(N_PERM):
        p=list(cross); rng.shuffle(p)
        pm=loso(rows,direction,True,p); m=mae(rows,pm,direction); null.append((a-m)/a)
    pv=(1+sum(x>=gain for x in null))/(N_PERM+1)
    return {'baseline_MAE':a,'enriched_MAE':b,'relative_gain':gain,'permutation_p':pv,
            'null':{'min':min(null),'median':float(statistics.median(null)),'mean':float(statistics.fmean(null)),'max':max(null),'count_ge':sum(x>=gain for x in null)}}


def main():
    b=fetch(); u,meta=unique_rows(b); rows=transitions(u); subjects=sorted({r['subject'] for r in rows})
    eligible={'n_transitions':len(rows),'n_subjects':len(subjects)}
    if len(rows)<MIN_N or len(subjects)<MIN_SUBJ:
        result={'experiment_id':'C032_CROSS_COMPARTMENT_DIRECTIONAL_INFORMATION_RESULT_v1','prereg_commit':PREREG,
                'status':'EVIDENCE_INSUFFICIENT','eligibility':eligible,'row_binding':meta}
    else:
        sn=directional(rows,'SN',32032); ns=directional(rows,'NS',32033); gap=sn['relative_gain']-ns['relative_gain']
        if sn['relative_gain']>=0.10 and sn['permutation_p']<=0.01 and gap>=0.05 and sn['enriched_MAE']<sn['baseline_MAE']:
            terminal='PASS'
        elif sn['relative_gain']<=0 or sn['permutation_p']>0.05 or gap<=0 or (ns['relative_gain']>=0.10 and ns['permutation_p']<=0.01 and ns['relative_gain']-sn['relative_gain']>=0.05):
            terminal='FAIL'
        else: terminal='EVIDENCE_INSUFFICIENT'
        result={'experiment_id':'C032_CROSS_COMPARTMENT_DIRECTIONAL_INFORMATION_RESULT_v1','prereg_commit':PREREG,'status':'COMPUTATION_COMPLETE',
                'input_integrity':{'git_blob_sha':blob_sha(b),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},
                'row_binding':meta,'eligibility':eligible,'S_to_N':sn,'N_to_S':ns,'directional_gain_gap_SN_minus_NS':gap,'terminal':terminal,
                'claim_ceiling':{'causation':False,'scientific_novelty':False,'independent_replication':False,'scientific_breakthrough':False,'outreach':'BLOCKED'}}
    Path('out').mkdir(exist_ok=True)
    Path('out/C032_CROSS_COMPARTMENT_DIRECTIONAL_INFORMATION_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    compact={k:result.get(k) for k in ['eligibility','S_to_N','N_to_S','directional_gain_gap_SN_minus_NS','terminal','status']}
    print('C032_COMPACT='+json.dumps(compact,sort_keys=True))

if __name__=='__main__': main()
