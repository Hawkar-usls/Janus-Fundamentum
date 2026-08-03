from __future__ import annotations
import argparse,copy,hashlib,itertools,json,os,tempfile

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def rref(rows,d):
    piv={}
    for raw in rows:
        x=int(raw)
        if x<0 or x>=1<<d: raise ValueError('range')
        while x:
            p=x.bit_length()-1
            if p in piv:x^=piv[p]
            else:
                piv[p]=x
                for q,y in list(piv.items()):
                    if q!=p and ((y>>p)&1): piv[q]=y^x
                break
    return tuple(piv[p] for p in sorted(piv,reverse=True))
def vecs(b):
    s={0}
    for x in b:s|={y^x for y in tuple(s)}
    return s
def wv(blocks,o,d):
    out=[]
    for t in range(1,len(o)):
        L=rref([x for i in o[:t] for x in blocks[i]],d); R=rref([x for i in o[t:] for x in blocks[i]],d)
        out.append(len(rref(sorted(vecs(L)&vecs(R)),d)))
    return out

def verify(path):
    a=json.load(open(path)); outer=a.pop('artifact_digest')
    if digest(a)!=outer: raise AssertionError('outer digest')
    a['artifact_digest']=outer
    for rec in a['records']:
        cd=rec.pop('case_digest')
        if digest(rec)!=cd: raise AssertionError('case digest')
        rec['case_digest']=cd; c=rec['case']; blocks=[rref(b,c['d']) for b in c['blocks']]; last=(0,); total=0
        for rnd in rec['result']['rounds']:
            exp=[list(last[:p]+(rnd['round_index'],)+last[p:]) for p in range(len(last)+1)]; got=[x['order'] for x in rnd['ledger']]
            if rnd['terminal']=='OPEN_WORK_BUDGET':
                if got!=exp[:len(got)]: raise AssertionError('refusal prefix')
            elif got!=exp: raise AssertionError('manifest')
            prev=0
            for e in rnd['ledger']:
                q=wv(blocks,tuple(e['order']),c['d'])
                if q!=e['width_vector'] or max(q,default=0)!=e['max_width']: raise AssertionError('width')
                if e['cumulative_work']<=prev: raise AssertionError('round cost')
                prev=e['cumulative_work']
            total+=rnd['charged_work']
            if rnd['cumulative_work_global']!=total: raise AssertionError('global cost')
            ell=rnd['prefix_size']; goods=[]
            for p in itertools.permutations(range(ell)):
                q=wv(blocks,p,c['d'])
                if max(q,default=0)<=c['k']: goods.append(list(p))
            if rec['oracle'][str(ell)]!={'good_count':len(goods),'good_layouts_digest':digest(goods)}: raise AssertionError('oracle')
            if rnd['terminal']=='ROUND_CLOSED':
                if rnd['selected']['order'] not in goods: raise AssertionError('selection')
                last=tuple(rnd['selected']['order'])
        if rec['result']['cumulative_work']!=total: raise AssertionError('total')
    if a['controls'][0]['reason']!='grouped factor partition lost': raise AssertionError('partition')

def repair(a):
    for r in a['records']: r.pop('case_digest',None); r['case_digest']=digest(r)
    a.pop('artifact_digest',None); a['artifact_digest']=digest(a)
def self_test(path):
    src=json.load(open(path)); muts=[]
    a=copy.deepcopy(src); a['records'][0]['result']['rounds'][1]['ledger'][0]['order']=[99,0,1]; muts.append(a)
    a=copy.deepcopy(src); a['records'][0]['result']['rounds'][1]['ledger'][0]['width_vector']=[99]; muts.append(a)
    a=copy.deepcopy(src); a['records'][0]['result']['rounds'][1]['cumulative_work_global']+=1; muts.append(a)
    for a in muts:
        repair(a); fd,p=tempfile.mkstemp(); os.close(fd); open(p,'w').write(json.dumps(a))
        try:
            try: verify(p)
            except Exception: pass
            else: raise AssertionError('tamper accepted')
        finally: os.unlink(p)
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('artifact'); ap.add_argument('--self-test',action='store_true'); z=ap.parse_args(); verify(z.artifact)
    if z.self_test:self_test(z.artifact)
    print('B4 round-ledger transcript verified')
