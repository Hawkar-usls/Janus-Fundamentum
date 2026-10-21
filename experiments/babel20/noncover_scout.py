#!/usr/bin/env python3
"""BABEL-20 non-cover connected legal SCL21 full-degree2 Fourier scout.

This is a finite exact fixture search, not a proof about all SCL. Only a
rational left-kernel witness against *every* degree2 multiplier is accepted
as a negative gate. Modular failures alone are marked CANDIDATE.
"""
import argparse,hashlib,json,random
from collections import Counter
from pathlib import Path
from fractions import Fraction
from janus_babel6_transfer import xor_labels

P=65521

def base_fano():
    return [tuple(sorted((7*b+i,7*b+(i+1)%7,7*b+(i+3)%7)))
            for b in range(3) for i in range(7)]

def valid(rows):
    n=len(rows)
    if any(len(row)!=3 or len(set(row))!=3 for row in rows):return False
    degrees=Counter(j for row in rows for j in row)
    if len(degrees)!=n or any(degrees[j]!=3 for j in range(n)):return False
    if len({frozenset((a,b)) for row in rows for a in row for b in row if a<b})!=3*n:
        return False
    visits={0};queue=[0]
    while queue:
        r=queue.pop()
        for i in rows[r]:
            for j in range(n):
                if j not in visits and i in rows[j]:
                    visits.add(j);queue.append(j)
    return len(visits)==n

def synthesize(seed):
    rnd=random.Random(seed)
    for retry in range(60):
        rows=[list(row) for row in base_fano()]
        pairs=[(0,1),(1,2)]+[rnd.sample(range(3),2) for _ in range(2+seed%4)]
        for a,b in pairs:
            r=rnd.randrange(7*a,7*a+7)
            s=rnd.randrange(7*b,7*b+7)
            pa=rnd.randrange(3);pb=rnd.randrange(3)
            rows[r][pa],rows[s][pb]=rows[s][pb],rows[r][pa]
            rows[r].sort();rows[s].sort()
        if valid(rows):
            return [tuple(r) for r in rows]
    return None

def exact_sat(labels,d,n):
    if d>16:return None
    count=0
    for a in range(1<<d):
        wt=sum((a & q).bit_count()%2 for q in labels)
        if wt==2*n//3:count+=1
    return count

def echelon(cols,prime=P):
    pivots={}
    for raw in cols:
        vec={q:v%prime for q,v in raw.items() if v%prime}
        while vec:
            p=min(vec)
            if p not in pivots:
                inv=pow(vec[p],-1,prime)
                pivots[p]={q:v*inv%prime for q,v in vec.items()}
                break
            a=vec[p]
            for q,v in pivots[p].items():
                x=(vec.get(q,0)-a*v)%prime
                if x:vec[q]=x
                elif q in vec:del vec[q]
    target={0:1}
    while target:
        p=min(target)
        if p not in pivots:return len(pivots),False
        a=target[p]
        for q,v in pivots[p].items():
            x=(target.get(q,0)-a*v)%prime
            if x:target[q]=x
            elif q in target:del target[q]
    return len(pivots),True

def cols_from_rows(rows,labels,Q):
    for row in rows:
        a,b,c=[labels[j] for j in row]
        for u in Q:
            d=Counter((u,u^a,u^b,u^c))
            yield d

def scout(target=20):
    out=[];count=0
    for seed in range(200):
        rows=synthesize(seed)
        if rows is None:continue
        assert valid(rows)
        labels,Q,d=xor_labels(rows)
        sat=exact_sat(labels,d,21)
        if sat is None:continue
        sha=hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest()
        item={"seed":seed,"rows":21,"nullity":d,"sat_count_exact":sat,
           "incidence_sha256":sha,"legal_linear_cubic_connected":True}
        if sat==0:
            rank,member=echelon(cols_from_rows(rows,labels,Q))
            item.update({"modular_full_degree2_rank":rank,
             "modular_e0_membership":member,
             "exact_Q_e0_nonmembership_proved":False,
             "status":"MODULAR_NONMEMBERSHIP_CANDIDATE_ONLY" if not member else "MODULAR_MEMBERSHIP"})
            if not member:
                print("BABEL20_POTENTIAL_FULL_DEGREE4_BARRIER",json.dumps(item,sort_keys=True),flush=True)
        out.append(item)
        count+=1
        if count%5==0:print("BABEL20_NONCOVER_PROGRESS",count,flush=True)
        if count>=target:break
    summary={"gate":"BABEL20_NONCOVER_SCL21_FULL_M2_SCOUT",
      "tested_legal_connected":count,
      "unsat_exact":sum(x["sat_count_exact"]==0 for x in out),
      "modular_nonmembership_candidates":sum(x.get("modular_e0_membership") is False for x in out),
      "exact_rational_full_degree4_obstructions":0,
      "scope":"Noncover finite family; modular flags are not rational proofs.","cases":out}
    Path("babel20_noncovers_21.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("BABEL20_NONCOVER_SUMMARY",json.dumps({k:v for k,v in summary.items() if k!="cases"},sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--count",type=int,default=20)
    scout(p.parse_args().count)
