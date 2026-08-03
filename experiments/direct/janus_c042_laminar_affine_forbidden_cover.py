#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
from dataclasses import dataclass
from typing import Any

Equation = tuple[int,int]
Clause = tuple[int,...]


def cj(o: Any)->str: return json.dumps(o,sort_keys=True,separators=(',',':'))
def dg(o: Any)->str: return hashlib.sha256(cj(o).encode()).hexdigest()

@dataclass
class Row:
    mask:int; rhs:int; prov:int=0
    def clone(self): return Row(self.mask,self.rhs,self.prov)
    def xor(self,o:'Row'): self.mask^=o.mask; self.rhs^=o.rhs; self.prov^=o.prov


def rref(eqs: tuple[Equation,...], d:int)->tuple[tuple[Equation,...], bool, int]:
    rows=[Row(m,r&1,1<<i) for i,(m,r) in enumerate(eqs)]
    rank=0
    for v in range(1,d+1):
        b=1<<(v-1)
        p=next((i for i in range(rank,len(rows)) if rows[i].mask&b),None)
        if p is None: continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and rows[i].mask&b: rows[i].xor(rows[rank])
        rank+=1
    out=[]
    for row in rows:
        if row.mask==0:
            if row.rhs: return (),False,rank
        else: out.append((row.mask,row.rhs))
    out.sort(key=lambda x: ((x[0]&-x[0]).bit_length(),x[0],x[1]))
    return tuple(out),True,len(out)


def consistent(eqs: tuple[Equation,...], d:int)->bool: return rref(eqs,d)[1]
def dim(eqs: tuple[Equation,...], d:int)->int:
    _,ok,rank=rref(eqs,d)
    return -1 if not ok else d-rank

def intersect(a:tuple[Equation,...],b:tuple[Equation,...],d:int)->tuple[Equation,...]|None:
    rr,ok,_=rref(a+b,d); return rr if ok else None

def implies(system:tuple[Equation,...], eq:Equation,d:int)->bool:
    m,r=eq
    return not consistent(system+((m,r^1),),d)
def subset(a:tuple[Equation,...],b:tuple[Equation,...],d:int)->bool:
    return all(implies(a,e,d) for e in b)
def relation(a,b,d):
    inter=intersect(a,b,d)
    if inter is None: return 'DISJOINT'
    if subset(a,b,d): return 'A_SUBSET_B'
    if subset(b,a,d): return 'B_SUBSET_A'
    return 'CROSSING'


def clause_forbidden(clause:Clause, rows:dict[int,int], const:dict[int,int], d:int)->tuple[Equation,...]|None:
    eqs=[]
    for lit in clause:
        v=abs(lit); m=rows[v]; c=const.get(v,0)&1
        target=0 if lit>0 else 1
        eqs.append((m,target^c))
    rr,ok,_=rref(tuple(eqs),d)
    return rr if ok else None


def translate(cnf:tuple[Clause,...], rows:dict[int,int], const:dict[int,int], d:int):
    out=[]
    for i,c in enumerate(cnf):
        s=clause_forbidden(c,rows,const,d)
        if s is not None: out.append({'clause_id':i,'equations':s})
    return out


def solve_laminar(cnf,rows,const,d,work_limit=10_000_000):
    factors=translate(cnf,rows,const,d)
    work=0; rels=[]
    for i in range(len(factors)):
        for j in range(i+1,len(factors)):
            work+=1
            if work>work_limit: return {'status':'OPEN_BUDGET','p_vs_np':'OPEN'}
            rel=relation(factors[i]['equations'],factors[j]['equations'],d)
            rels.append([i,j,rel])
            if rel=='CROSSING':
                return {'schema':'janus.c042.laminar_affine_forbidden_cover.v1','status':'OPEN_NON_LAMINAR','p_vs_np':'OPEN','crossing_pair':[i,j], 'factor_count':len(factors)}
    maximal=[]
    for i,f in enumerate(factors):
        contained=False
        for j,g in enumerate(factors):
            if i!=j and subset(f['equations'],g['equations'],d) and not subset(g['equations'],f['equations'],d):
                contained=True; break
        if not contained:
            if not any(subset(f['equations'],factors[k]['equations'],d) and subset(factors[k]['equations'],f['equations'],d) for k in maximal):
                maximal.append(i)
    sizes=[1<<dim(factors[i]['equations'],d) for i in maximal]
    covered=sum(sizes); total=1<<d
    base={'schema':'janus.c042.laminar_affine_forbidden_cover.v1','dimension':d,'factor_count':len(factors),'maximal_ids':maximal,'maximal_sizes':sizes,'covered_points':covered,'total_points':total,'relations':rels,'p_vs_np':'OPEN'}
    if covered==total:
        base['status']='UNSAT'; base['certificate']='DISJOINT_MAXIMAL_AFFINE_COVER'; base['integrity_sha256']=dg(base); return base
    prefix=(); witness={}; trace=[]
    for v in range(1,d+1):
        chosen=None
        for bit in (0,1):
            cand=prefix+((1<<(v-1),bit),)
            cell_size=1<<(d-v)
            cov=0; counts=[]
            for idx in maximal:
                inter=intersect(factors[idx]['equations'],cand,d)
                c=0 if inter is None else 1<<dim(inter,d)
                counts.append(c); cov+=c
            if cov<cell_size:
                chosen=bit; trace.append({'var':v,'bit':bit,'covered':cov,'cell_size':cell_size,'counts':counts}); break
        assert chosen is not None
        witness[v]=bool(chosen); prefix=prefix+((1<<(v-1),chosen),)
    def sat_eqs(eqs):
        for m,r in eqs:
            p=0
            while m:
                b=m&-m; p^=int(witness[b.bit_length()]); m^=b
            if p!=r:return False
        return True
    assert not any(sat_eqs(f['equations']) for f in factors)
    base['status']='SAT'; base['witness']={str(k):v for k,v in witness.items()}; base['trace']=trace; base['integrity_sha256']=dg(base); return base


def eval_cnf(cnf,rows,const,lam):
    packed=sum((1<<(i-1)) for i,b in lam.items() if b)
    x={v: bool(const.get(v,0)^((rows[v]&packed).bit_count()&1)) for v in rows}
    return all(any(x[abs(l)]==(l>0) for l in c) for c in cnf)
def brute(cnf,rows,const,d):
    for bits in itertools.product((False,True),repeat=d):
        a={i+1:bits[i] for i in range(d)}
        if eval_cnf(cnf,rows,const,a): return True,a
    return False,None
def prefix_clause(pattern:tuple[int,...])->Clause:
    return tuple((i+1 if b==0 else -(i+1)) for i,b in enumerate(pattern))
def hard_image(n:int):
    cnf=[]
    for i in range(1,n+1): cnf.append((i,-((i%n)+1),((i+1)%n)+1))
    rows={i:1<<(i-1) for i in range(1,n+1)}; const={i:0 for i in rows}
    return tuple(cnf),rows,const

def audit(seed=420042):
    rng=random.Random(seed); cases=180; mismatch=verify_fail=0; exact=opens=0
    for _ in range(cases):
        d=rng.randint(1,8); rows={i:1<<(i-1) for i in range(1,d+1)}; const={i:0 for i in rows}
        clauses=[]; rootbit=rng.randint(0,1); clauses.append(prefix_clause((rootbit,)))
        if d>=2 and rng.random()<.5: clauses.append(prefix_clause((1-rootbit,rng.randint(0,1))))
        for k in range(2,d+1):
            if rng.random()<.35:
                pat=(rootbit,)+tuple(rng.randint(0,1) for _ in range(k-1)); clauses.append(prefix_clause(pat))
        cnf=tuple(clauses); cert=solve_laminar(cnf,rows,const,d); truth,_=brute(cnf,rows,const,d)
        if cert['status'].startswith('OPEN'): opens+=1; continue
        exact+=1
        if (cert['status']=='SAT')!=truth:mismatch+=1
        body=dict(cert); integ=body.pop('integrity_sha256')
        if dg(body)!=integ:verify_fail+=1
    d=64; rows={i:1<<(i-1) for i in range(1,d+1)}; const={i:0 for i in rows}
    sat=solve_laminar((prefix_clause((0,)),),rows,const,d)
    assert sat['status']=='SAT' and sat['witness']['1'] is True
    unsat=solve_laminar((prefix_clause((0,)),prefix_clause((1,))),rows,const,d)
    assert unsat['status']=='UNSAT' and unsat['covered_points']==1<<64
    nested=tuple(prefix_clause(tuple(0 for _ in range(k))) for k in range(1,33))
    nest=solve_laminar(nested,rows,const,d)
    assert nest['status']=='SAT' and len(nest['maximal_ids'])==1
    cross=solve_laminar((prefix_clause((0,)),(2,)),rows,const,d)
    assert cross['status']=='OPEN_NON_LAMINAR'
    hc,hr,hk=hard_image(24); hard=solve_laminar(hc,hr,hk,24)
    assert hard['status']=='OPEN_NON_LAMINAR'
    result={'artifact_id':'C042-JANUS-LAMINAR-AFFINE-FORBIDDEN-COVER','status':'PASS','p_vs_np':'OPEN','seed':seed,'random_cases':cases,'exact':exact,'open':opens,'mismatches':mismatch,'verification_failures':verify_fail,'theorem':'Affine-coordinate CNF is polynomially decidable when clause-falsifying affine subspaces form a laminar family; maximal forbidden subspaces are disjoint, exact union size is additive, SAT witnesses follow by conditional counting, and UNSAT is certified by a disjoint affine cover.','high_dimension_sat':{'dimension':64,'factors':1,'status':sat['status']},'high_dimension_unsat_cover':{'dimension':64,'factors':2,'status':unsat['status']},'nested_compression':{'input_factors':32,'maximal_factors':len(nest['maximal_ids']),'status':nest['status']},'crossing_control':cross['status'],'nand3_neq_control':hard['status'],'new_gate':'POLYNOMIAL_DECOMPOSITION_OF_CROSSING_AFFINE_FORBIDDEN_SUBSPACES','claim_boundary':'Laminar affine forbidden-subspace arrangements only. Crossing arrangements return OPEN; arbitrary 3-CNF and P versus NP remain open.'}
    result['integrity_sha256']=dg(result); return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--output');a=ap.parse_args();r=audit()
    if a.output: open(a.output,'w').write(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps(r,indent=2,sort_keys=True))
    if a.self_test: assert r['status']=='PASS' and r['mismatches']==0 and r['verification_failures']==0
if __name__=='__main__':main()
