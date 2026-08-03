#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys

def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rr(rows,d):
    piv={}; lim=1<<d
    for raw in rows:
        x=int(raw)
        if x<0 or x>=lim: raise ValueError
        while x:
            p=x.bit_length()-1
            if p in piv: x^=piv[p]
            else:
                piv[p]=x
                for q,y in list(piv.items()):
                    if q!=p and ((y>>p)&1): piv[q]=y^x
                break
    return tuple(piv[p] for p in sorted(piv,reverse=True))
def vs(b):
    s={0}
    for x in b:s|={y^x for y in tuple(s)}
    return s
def sp(bs,d):return rr((x for b in bs for x in b),d)
def bd(L,R,d):return rr(sorted(vs(sp(L,d))&vs(sp(R,d))),d)
def verify_case(c):
    z={k:v for k,v in c.items() if k!='semantic_digest'}
    assert c['semantic_digest']==h(z)
    d=int(c['d']);k=int(c['k']); blocks=[rr(b,d) for b in c['whole_factor_blocks']]; order=tuple(c['scaffold_order'])
    assert len(c['affine_offsets'])==len(blocks)
    assert sorted(order)==list(range(len(blocks)))
    assert order[-1]==c['new_leaf'] and tuple(order[:-1])==tuple(c['previous_order'])
    edges=[];work=0
    for t in range(1,len(order)):
        L=[blocks[i] for i in order[:t]];R=[blocks[i] for i in order[t:]]; b=bd(L,R,d)
        work+=sum(len(x) for x in L+R)+len(b)+1
        edges.append((list(b),len(b),work))
    assert len(edges)==len(c['candidate_edges'])
    for got,e in zip(edges,c['candidate_edges']):
        assert got==(e['boundary_rref'],e['width'],e['cumulative_work'])
    assert c['scaffold_width']==max((x[1] for x in edges),default=0)
    assert len(blocks[c['new_leaf']])<=2*k
    assert c['scaffold_width']<=3*k
    assert c['charged_work']==work
    assert c['next_terminal']=='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
def main():
    a=json.load(open(sys.argv[1])); outer=a['artifact_digest']; z={k:v for k,v in a.items() if k!='artifact_digest'}; assert outer==h(z)
    assert a['schema']=='C049.1-B4.2-3K-SCAFFOLD-v1'
    for c in a['cases']: verify_case(c)
    # digest-repaired semantic tamper: width changed and both digests repaired must still fail replay.
    t=json.loads(json.dumps(a));t['cases'][0]['candidate_edges'][0]['width']+=1
    cc=t['cases'][0];cc['semantic_digest']=h({k:v for k,v in cc.items() if k!='semantic_digest'});t['artifact_digest']=h({k:v for k,v in t.items() if k!='artifact_digest'})
    try:
        for c in t['cases']:verify_case(c)
    except AssertionError: pass
    else: raise AssertionError('digest-repaired tamper accepted')
    print('JANUS_C049_1_B4_2_3K_SCAFFOLD_VERIFIER = PASS')
if __name__=='__main__':main()
