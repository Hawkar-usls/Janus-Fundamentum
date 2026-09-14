from __future__ import annotations
from collections import defaultdict
from itertools import product
from pathlib import Path
import json, random, sys
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'trump_apma_compositional_synthesis'
sys.path.insert(0,str(PREV))
import core as primitives

def xor_clauses(vs,rhs):
    out=[]
    for bits in product([0,1],repeat=len(vs)):
        if (sum(bits)&1)!=rhs:
            out.append([(-v if b else v) for v,b in zip(vs,bits)])
    return out

def module_template(kind):
    cnf=[]; T=[]; F=[]; v=1
    if kind==0:
        n=8; diag=[]; off=[]
        for i in range(n):
            diag.append(v); v+=1
            if i<n-1: off.append(v); v+=1
        for i in range(n):
            block=[diag[i]]+([off[i]] if i<n-1 else [])
            cnf.append(block)
            if i<n-1: cnf.append([-diag[i],-off[i]])
        for i in range(1,n): cnf.append([-off[i-1],-diag[i]])
        T=[diag[i] for i in range(1,5)]; F=[off[i] for i in range(0,4)]
    elif kind==1:
        h=v; v+=1; T=list(range(v,v+4)); v+=4; F=list(range(v,v+4)); v+=4; u=v; vv=v+1; v+=2
        cnf=[[h]]+[[-h,t] for t in T]+[[-h,-f] for f in F]+[[u,vv],[-u,h],[-vv,h]]
    elif kind==2:
        h=v; v+=1; T=list(range(v,v+4)); v+=4; F=list(range(v,v+4)); v+=4; u=v; vv=v+1; v+=2
        cnf=[[h]]+[[-h,t] for t in T]+[[-h,-f] for f in F]+[[u],[-h,-u,vv],[-vv,h]]
    elif kind==3:
        h=v; v+=1; T=list(range(v,v+4)); v+=4; F=list(range(v,v+4)); v+=4; u=v; vv=v+1; v+=2
        cnf=[[h]]
        for t in T: cnf.extend(xor_clauses([t,h],0))
        for f in F: cnf.extend(xor_clauses([f,h],1))
        cnf.extend(xor_clauses([h,u,vv],0))
    else: raise ValueError(kind)
    return {'kind':kind,'cnf':cnf,'true_ports':T,'false_ports':F,'nvars':v-1}

def local_port_degree(m,p):
    return sum(sum(abs(x)==p for x in c) for c in m['cnf'])

def template_audit():
    out=[]
    for kind in range(4):
        m=module_template(kind); s=primitives.QS[kind](m['cnf']); z=primitives.RS[kind](s) if s is not None else None
        td=[local_port_degree(m,x) for x in m['true_ports']]; fd=[local_port_degree(m,x) for x in m['false_ports']]
        out.append({'kind':kind,'designated_admitted':s is not None and isinstance(z,dict) and z.get('decision')=='SAT','true_port_degrees':td,'false_port_degrees':fd,'degree_symmetry':td==fd})
    return out

def path_edges(k): return [(i,i+1) for i in range(k-1)]
def balanced_edges(k): return [((i-1)//2,i) for i in range(1,k)]
def shallow4(): return [(0,1),(1,2),(1,3)]
def irregular_edges(k,seed):
    rng=random.Random(seed); deg=[0]*k; edges=[]
    for i in range(1,k):
        cand=[j for j in range(i) if deg[j]<3]
        p=cand[rng.randrange(len(cand))]; edges.append((p,i)); deg[p]+=1; deg[i]+=1
    return edges

def broom_edges(k):
    if k<=4: return balanced_edges(k)
    edges=[(0,1),(1,2),(1,3)]; deg=[0]*k
    for a,b in edges: deg[a]+=1; deg[b]+=1
    frontier=[2,3]; nxt=4; turn=0
    while nxt<k:
        p=frontier[turn%len(frontier)]
        if deg[p]>=3:
            turn+=1; continue
        edges.append((p,nxt)); deg[p]+=1; deg[nxt]+=1; frontier.append(nxt); nxt+=1; turn+=1
    return edges

def component_kinds(k):
    if k==2: return [0,3]
    if k==3: return [0,2,3]
    return [i%4 for i in range(k)]

def assign_widths(edges,mode):
    if mode=='w3': return [3]
    if mode=='path12': return [1 if i%2==0 else 2 for i in range(len(edges))]
    return [1]*len(edges)

def transport(cnf,seed,encoder):
    rng=random.Random(seed); vs=sorted({abs(x) for c in cnf for x in c})
    if encoder=='cal_encoder_v1':
        new=[100000+19*i for i in range(1,len(vs)+1)]; rng.shuffle(new)
    elif encoder=='adm_encoder_v2':
        new=[400000+17*i for i in range(1,len(vs)+1)]; rng.shuffle(new)
    elif encoder=='hold_encoder_v3':
        new=[700000+13*i for i in range(len(vs),0,-1)]
    else: raise ValueError(encoder)
    mp=dict(zip(vs,new)); out=[]
    for c in cnf:
        z=[mp[abs(x)] if x>0 else -mp[abs(x)] for x in c]; rng.shuffle(z); out.append(z)
    rng.shuffle(out)
    dup=2 if encoder=='cal_encoder_v1' else 3
    out.extend([list(out[i%len(out)]) for i in range(dup)])
    fresh=max(new)+101 if new else 999999; out.append([fresh,-fresh])
    if encoder=='hold_encoder_v3': out=list(reversed(out))
    return out

def metrics(cnf):
    real=[c for c in cnf if not any(-x in c for x in c)]; d=defaultdict(int); wh=defaultdict(int); pos=neg=0
    for c in real:
        wh[len(c)]+=1
        for x in c: d[abs(x)]+=1; pos+=x>0; neg+=x<0
    return {'n':len(d),'m':len(real),'width_hist':[list(x) for x in sorted(wh.items())],'degree_multiset':sorted(d.values()),'pos':pos,'neg':neg}

def build_logical(k,edges,widths,truth,seed):
    kinds=component_kinds(k); modules=[module_template(t) for t in kinds]
    base_maps=[]; next_id=1
    for m in modules:
        mp={v:next_id+i for i,v in enumerate(range(1,m['nvars']+1))}; next_id+=m['nvars']; base_maps.append(mp)
    used=[0]*k; replace={}
    mismatch_done=False; gluing=[]
    for ei,((a,b),w) in enumerate(zip(edges,widths)):
        for j in range(w):
            sa=used[a]; sb=used[b]; used[a]+=1; used[b]+=1
            bit=(seed+ei+j)&1; ba=bit; bb=bit
            if truth=='UNSAT' and not mismatch_done:
                bb=1-bit; mismatch_done=True
            pa=modules[a]['true_ports'][sa] if ba else modules[a]['false_ports'][sa]
            pb=modules[b]['true_ports'][sb] if bb else modules[b]['false_ports'][sb]
            ga=base_maps[a][pa]; gb=base_maps[b][pb]; shared=10_000_000+ei*10+j
            replace[ga]=shared; replace[gb]=shared
            gluing.append({'edge':[a,b],'slot':j,'bit_a':ba,'bit_b':bb,'width':w})
    if max(used,default=0)>4: raise ValueError('port budget exceeded')
    cnf=[]; component_vars=[]
    for i,m in enumerate(modules):
        cv=set()
        for c in m['cnf']:
            z=[]
            for lit in c:
                g=base_maps[i][abs(lit)]; g=replace.get(g,g); cv.add(g); z.append(g if lit>0 else -g)
            cnf.append(z)
        component_vars.append(sorted(cv))
    return cnf,{'kinds':kinds,'component_vars':component_vars,'gluing':gluing,'incident_widths':used}

def make_pair(split,pair_index,k,topology,width_mode,seed):
    if topology in ('short_path','long_path'): edges=path_edges(k)
    elif topology=='small_shallow_tree': edges=shallow4()
    elif topology=='balanced_binary_tree': edges=balanced_edges(k)
    elif topology=='irregular_degree_leq3': edges=irregular_edges(k,seed)
    elif topology=='broom_star_like_degree_leq3': edges=broom_edges(k)
    else: raise ValueError(topology)
    widths=assign_widths(edges,width_mode)
    if any(sum(w for (e,w) in zip(edges,widths) if i in e)>3 for i in range(k)): raise ValueError('boundary >3')
    encoder={'cal':'cal_encoder_v1','adm':'adm_encoder_v2','hold':'hold_encoder_v3'}[split]
    out=[]; hidden=[]
    for truth in ('SAT','UNSAT'):
        logical,meta=build_logical(k,edges,widths,truth,seed)
        cid=f'{split}-pair{pair_index:02d}-{truth.lower()}'
        cnf=transport(logical,seed+9001,encoder)
        out.append({'id':cid,'cnf':cnf,'truth':truth if split=='cal' else None,'encoder':encoder,'pair_id':f'{split}-pair{pair_index:02d}'})
        hidden.append((cid,truth,meta,metrics(cnf)))
    if hidden[0][3]!=hidden[1][3]: raise AssertionError(('PAIR_METRIC_DRIFT',hidden[0][0],hidden[0][3],hidden[1][3]))
    return out,hidden,{'pair_id':f'{split}-pair{pair_index:02d}','metrics_equal':True,'metrics':hidden[0][3],'k':k,'topology':topology,'widths':widths}

def make_control(name,seed):
    if name=='CONTROL_CYCLE':
        k=6; edges=path_edges(k)+[(k-1,0)]; widths=[1]*len(edges); logical,meta=build_logical(k,edges,widths,'SAT',seed)
    elif name=='CONTROL_WIDTH_4':
        k=2; edges=[(0,1)]; widths=[4]; logical,meta=build_logical(k,edges,widths,'SAT',seed)
    else: raise ValueError(name)
    return {'id':f'control-{name.lower()}-{seed}','control':name,'cnf':transport(logical,seed+12001,'hold_encoder_v3'),'encoder':'hold_encoder_v3'},meta

def main():
    audit=template_audit()
    if not all(x['designated_admitted'] and x['degree_symmetry'] for x in audit): raise AssertionError(audit)
    cal=[]; adm=[]; hold=[]; truth={}; pair_audit=[]
    cal_specs=[(2,'short_path','w3'),(3,'short_path','path12'),(4,'small_shallow_tree','w1')]
    adm_specs=[(5,'long_path','path12'),(8,'balanced_binary_tree','w1'),(12,'irregular_degree_leq3','w1'),(16,'long_path','path12')]
    hold_specs=[(5,'balanced_binary_tree','w1'),(8,'irregular_degree_leq3','w1'),(12,'broom_star_like_degree_leq3','w1'),(16,'balanced_binary_tree','w1')]
    idx=0
    for rep in range(2):
        for spec in cal_specs:
            cases,hid,a=make_pair('cal',idx,*spec,seed=1000+rep*100+idx); idx+=1; cal.extend(cases); pair_audit.append(a)
            for cid,tr,meta,met in hid: truth[cid]={'truth':tr,'split':'cal','hidden_meta':meta,'metrics':met}
    idx=0
    for rep in range(2):
        for spec in adm_specs:
            cases,hid,a=make_pair('adm',idx,*spec,seed=2000+rep*100+idx); idx+=1; adm.extend([{k:v for k,v in c.items() if k!='truth'} for c in cases]); pair_audit.append(a)
            for cid,tr,meta,met in hid: truth[cid]={'truth':tr,'split':'admission','hidden_meta':meta,'metrics':met}
    idx=0
    for rep in range(2):
        for spec in hold_specs:
            cases,hid,a=make_pair('hold',idx,*spec,seed=3000+rep*100+idx); idx+=1; hold.extend([{k:v for k,v in c.items() if k!='truth'} for c in cases]); pair_audit.append(a)
            for cid,tr,meta,met in hid: truth[cid]={'truth':tr,'split':'holdout','hidden_meta':meta,'metrics':met}
    controls=[]; control_truth={}
    for j in range(2):
        for name in ('CONTROL_CYCLE','CONTROL_WIDTH_4'):
            c,meta=make_control(name,4000+j*10+(0 if name=='CONTROL_CYCLE' else 1)); controls.append(c); control_truth[c['id']]={'control':name,'hidden_meta':meta}
    (ROOT/'calibration.json').write_text(json.dumps({'cases':cal},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_admission.json').write_text(json.dumps({'cases':adm},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_holdout.json').write_text(json.dumps({'cases':hold},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_controls.json').write_text(json.dumps({'cases':controls},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_truth.json').write_text(json.dumps({'targets':truth,'controls':control_truth},indent=2,sort_keys=True),encoding='utf-8')
    report={'template_audit':audit,'counts':{'calibration':len(cal),'admission':len(adm),'holdout':len(hold),'controls':len(controls)},'pair_audit':pair_audit,'all_pair_metrics_equal':all(x['metrics_equal'] for x in pair_audit),'calibration_k':sorted({truth[c['id']]['hidden_meta']['incident_widths'].__len__() for c in cal if c['id'].endswith('-sat')})}
    (ROOT/'POPULATION_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'counts':report['counts'],'templates':audit,'pairs':len(pair_audit),'all_pair_metrics_equal':report['all_pair_metrics_equal']},sort_keys=True))
if __name__=='__main__': main()
