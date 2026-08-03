from __future__ import annotations
import hashlib, json, random, sys

def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def compact(seq):
    data=[(tuple(x['left']),tuple(x['right']),x['value']) for x in seq]
    while True:
        changed=False
        for i in range(1,len(data)):
            if data[i-1]==data[i]: del data[i]; changed=True; break
        if changed: continue
        for i in range(len(data)):
            for j in range(i+2,len(data)):
                if data[i][:2]!=data[j][:2]: continue
                values=[x[2] for x in data[i:j+1]]
                inc=values[0]<=values[-1] and all(values[0]<=z<=values[-1] for z in values[1:-1])
                dec=values[0]>=values[-1] and all(values[0]>=z>=values[-1] for z in values[1:-1])
                if inc or dec: del data[i+1:j]; changed=True; break
            if changed: break
        if not changed: return [{'left':list(x[0]),'right':list(x[1]),'value':x[2]} for x in data]

def fixture(rng,theta,k):
    raw=[]
    if theta==0:
        for _ in range(rng.randrange(1,18)): raw.append({'left':[],'right':[],'value':rng.randrange(k+1)})
        return raw
    for t in range(theta+1):
        left=[1<<i for i in range(t)]; right=[1<<i for i in range(t,theta)]
        for _ in range(rng.randrange(1,8)): raw.append({'left':left,'right':right,'value':rng.randrange(k+1)})
    return raw

def regenerate():
    rng=random.Random(49101); records=[]
    for theta in range(5):
        for k in range(6):
            for index in range(4):
                source=fixture(rng,theta,k); output=compact(source)
                payload={'theta':theta,'k':k,'index':index,'input':source,'output':output,'trace':None}
                records.append({'theta':theta,'k':k,'index':index,'semantic_digest':digest(payload),'input_length':len(source),'output_length':len(output),'width':max(x['value'] for x in output),'idempotent':compact(output)==output,'length_bound':len(output)<=((2*theta+1)*(2*k+1))})
    return {'cases':len(records),'failures':sum(not(r['idempotent'] and r['length_bound']) for r in records),'semantic_audit_digest':digest(records)}

if __name__=='__main__':
    with open(sys.argv[1],encoding='utf-8') as handle: frozen=json.load(handle)
    assert regenerate()==frozen['independent_replay']
    print('VERIFIED')
