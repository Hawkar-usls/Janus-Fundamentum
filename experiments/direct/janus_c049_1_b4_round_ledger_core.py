from __future__ import annotations
from itertools import permutations
from hashlib import sha256
import json

def rref(rows,d):
    lim=1<<d; piv={}
    for raw in rows:
        x=int(raw)
        if x<0 or x>=lim: raise ValueError('vector outside ambient')
        while x:
            p=x.bit_length()-1
            if p in piv: x^=piv[p]
            else:
                piv[p]=x
                for q,y in list(piv.items()):
                    if q!=p and ((y>>p)&1): piv[q]=y^x
                break
    return tuple(piv[p] for p in sorted(piv,reverse=True))

def span(blocks,d): return rref([x for b in blocks for x in b],d)
def vectors(b):
    s={0}
    for x in b: s|={y^x for y in tuple(s)}
    return s

def width_vector(blocks,order,d):
    out=[]
    for t in range(1,len(order)):
        left=span([blocks[i] for i in order[:t]],d)
        right=span([blocks[i] for i in order[t:]],d)
        out.append(len(rref(sorted(vectors(left)&vectors(right)),d)))
    return out

def layout_digest(order):
    return sha256(json.dumps(list(order),separators=(',',':')).encode()).hexdigest()

def insertion_candidates(prev,new):
    return [tuple(prev[:p])+(new,)+tuple(prev[p:]) for p in range(len(prev)+1)]

def compression_round(blocks,prev,new,d,k,work_cap=10**9):
    ledger=[]; charged=0
    for pos,cand in enumerate(insertion_candidates(prev,new)):
        wv=width_vector(blocks,cand,d); charged+=max(1,len(wv))
        ledger.append({'candidate_index':pos,'position':pos,'order':list(cand),'width_vector':wv,'max_width':max(wv,default=0),'accepted':max(wv,default=0)<=k,'layout_digest':layout_digest(cand),'cumulative_work':charged})
        if charged>work_cap:
            return {'terminal':'OPEN_WORK_BUDGET','ledger':ledger,'charged_work':charged,'selected':None}
    good=[x for x in ledger if x['accepted']]
    selected=min(good,key=lambda x:(x['max_width'],sum(x['width_vector']),x['layout_digest'])) if good else None
    return {'terminal':'ROUND_CLOSED' if selected else 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE','ledger':ledger,'charged_work':charged,'selected':selected}

def iterative_compression(blocks,d,k,work_cap=10**9):
    blocks=[rref(b,d) for b in blocks]
    if any(not b for b in blocks): raise ValueError('empty grouped factor block')
    rounds=[]; order=(0,); cumulative=0
    for new in range(1,len(blocks)):
        rr=compression_round(blocks,order,new,d,k,work_cap-cumulative)
        cumulative+=rr['charged_work']; rr.update(round_index=new,prefix_size=new+1,cumulative_work_global=cumulative); rounds.append(rr)
        if rr['terminal']!='ROUND_CLOSED':
            return {'terminal':rr['terminal'],'rounds':rounds,'final_order':None,'cumulative_work':cumulative,'grouped_block_count':len(blocks)}
        order=tuple(rr['selected']['order'])
    return {'terminal':'LAYOUT_CANDIDATE','rounds':rounds,'final_order':list(order),'final_width_vector':width_vector(blocks,order,d),'cumulative_work':cumulative,'grouped_block_count':len(blocks)}

def exhaustive_prefix_oracle(blocks,d,k):
    blocks=[rref(b,d) for b in blocks]; out={}
    for ell in range(1,len(blocks)+1):
        good=[]
        for p in permutations(range(ell)):
            wv=width_vector(blocks,p,d)
            if max(wv,default=0)<=k: good.append(list(p))
        out[str(ell)]=good
    return out
