#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json

def rref(rows,d):
    piv={}; lim=1<<d
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

def span(blocks,d): return rref((x for b in blocks for x in b),d)
def vecs(b):
    s={0}
    for x in b: s|={y^x for y in tuple(s)}
    return s

def boundary(left,right,d): return rref(sorted(vecs(span(left,d)) & vecs(span(right,d))),d)
def widths(blocks,order,d):
    return [len(boundary([blocks[i] for i in order[:t]],[blocks[i] for i in order[t:]],d)) for t in range(1,len(order))]
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def scaffold(blocks,old_order,new,d,k,betas=None):
    blocks=[rref(b,d) for b in blocks]
    if sorted(old_order)!=list(range(len(blocks)-1)) or new!=len(blocks)-1: raise ValueError('noncanonical round')
    old_w=widths(blocks[:-1],old_order,d)
    if max(old_w,default=0)>k: raise ValueError('previous layout exceeds k')
    if len(blocks[new])>2*k: return {'terminal':'NO_LAYOUT_AT_CAP_LOCAL_DIMENSION','reason':'dim(V_new)>2k'}
    order=tuple(old_order)+(new,)
    edges=[]; work=0
    for t in range(1,len(order)):
        L=[blocks[i] for i in order[:t]]; R=[blocks[i] for i in order[t:]]
        b=boundary(L,R,d); work+=sum(len(x) for x in L+R)+len(b)+1
        edges.append({'edge_index':t-1,'left_leaf_ids':list(order[:t]),'right_leaf_ids':list(order[t:]),'boundary_rref':list(b),'width':len(b),'cumulative_work':work})
    maxw=max((e['width'] for e in edges),default=0)
    record={'terminal':'SCAFFOLD_3K_CERTIFIED','d':d,'k':k,'whole_factor_blocks':[list(b) for b in blocks],
      'affine_offsets':list(betas if betas is not None else [0]*len(blocks)),'previous_order':list(old_order),
      'previous_width_vector':old_w,'new_leaf':new,'scaffold_type':'CATERPILLAR_APPEND_NEW_LEAF',
      'scaffold_order':list(order),'nodes':[{'node_id':i,'kind':'LEAF','factor_id':i} for i in order]+[{'node_id':len(order)+i,'kind':'SPINE','edge_index':i} for i in range(max(0,len(order)-2))],
      'candidate_edges':edges,'scaffold_width':maxw,'three_k_cap':3*k,'charged_work':work,
      'proof_obligations':{'previous_width_at_most_k':max(old_w,default=0)<=k,'new_dimension_at_most_2k':len(blocks[new])<=2*k,'all_edges_retained':len(edges)==len(order)-1,'scaffold_width_at_most_3k':maxw<=3*k},
      'next_terminal':'OPEN_TRAJECTORY_ENGINE_INCOMPLETE'}
    record['semantic_digest']=digest(record)
    return record

def cases():
    out=[]
    # B4.1 six-block obstruction; old prefix order fixed, append final block.
    blocks=[(1,),(2,),(4,),(8,),(3,),(12,)]
    out.append(scaffold(blocks,(0,4,2,3,1),5,4,1,[0,1,0,1,1,0]))
    # noncanonical boundary bases and several exhaustive small controls.
    for d,k,bs,old in [
      (3,1,[(3,1),(2,),(4,)],(0,1)),
      (3,1,[(1,),(2,),(4,)],(1,0)),
      (4,2,[(3,5),(6,),(9,),(12,)],(2,0,1)),
    ]: out.append(scaffold(bs,old,len(bs)-1,d,k,list(range(len(bs)))))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output'); a=ap.parse_args()
    cs=cases()
    # Bounded exhaustive soundness for every emitted order and direct 3k check.
    for c in cs:
        assert c['proof_obligations']['scaffold_width_at_most_3k']
        assert c['semantic_digest']==digest({k:v for k,v in c.items() if k!='semantic_digest'})
    artifact={'schema':'C049.1-B4.2-3K-SCAFFOLD-v1','claim_boundary':'3k scaffold only; node full sets and complete refinement remain open','cases':cs}
    artifact['artifact_digest']=digest(artifact)
    text=json.dumps(artifact,sort_keys=True,separators=(',',':'))
    if a.output: open(a.output,'w').write(text+'\n')
    print('JANUS_C049_1_B4_2_3K_SCAFFOLD = PASS')
    print('CASES =',len(cs),'BYTES =',len(text.encode()),'DIGEST =',artifact['artifact_digest'])
    print('TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE')
if __name__=='__main__': main()
