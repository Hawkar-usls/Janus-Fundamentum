#!/usr/bin/env python3
"""BABEL-20 exact *full* degree-2 Fourier membership on novel legal SCL21.

Constructs complete M2 over Q, NOT only transfer columns; if nonmembership,
reconstructs h in the exact integer/rational left nullspace and verifies
h^T M2=0, h(e0)=1. Positive cases carry a full row-multiplier identity.
"""
import argparse,gzip,hashlib,json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from noncover_scout import synthesize,valid,exact_sat
from janus_babel6_transfer import xor_labels

def axpy(dest,src,scale):
    for i,v in src.items():
        w=dest.get(i,0)+scale*v
        if w:dest[i]=w
        elif i in dest:del dest[i]

def build(rows,labels,Q):
    pivots={};columns_examined=0
    for r,row in enumerate(rows):
        a,b,c=[labels[i] for i in row]
        for u in sorted(Q):
            vec={q:Fraction(v) for q,v in Counter((u,u^a,u^b,u^c)).items()}
            comb={(r,u):Fraction(1)}
            for pivot,(rowvec,rowcomb) in sorted(pivots.items()):
                if pivot in vec:
                    factor=vec[pivot]
                    axpy(vec,rowvec,-factor)
                    axpy(comb,rowcomb,-factor)
            if vec:
                p=min(vec);scale=1/vec[p]
                pivots[p]=({i:v*scale for i,v in vec.items()},
                           {k:v*scale for k,v in comb.items()})
            columns_examined+=1
            if len(pivots)==(1<<max(labels).bit_length()):
                break
        # Full rank stopping is correct but optional.
    target={0:Fraction(1)};x={}
    for p,(vec,comb) in sorted(pivots.items()):
        if p in target:
            factor=target[p]
            axpy(target,vec,-factor);axpy(x,comb,factor)
    if not target:
        check={}
        for (r,u),k in x.items():
            for z in (u,*(u^labels[j] for j in rows[r])):
                check[z]=check.get(z,0)+k
        assert {q:v for q,v in check.items() if v}=={0:Fraction(1)}
        result={"status":"FULL_Q_DEGREE2_EXPLICIT_POSITIVE_PASS",
                "nonzero_terms":len(x),"coefficient_terms":[[r,u,str(k)] for (r,u),k in sorted(x.items())]}
    else:
        q=min(target);scale=target[q]
        h={}
        for freq in range(1<<max(labels).bit_length()):
            vec={freq:Fraction(1)}
            for p,(rowvec,rowcomb) in sorted(pivots.items()):
                if p in vec:axpy(vec,rowvec,-vec[p])
            if vec.get(q,0):h[freq]=vec[q]/scale
        assert h.get(0)==1
        count=0
        for r,row in enumerate(rows):
            a,b,c=[labels[i] for i in row]
            for u in Q:
                value=sum(h.get(z,0) for z in (u,u^a,u^b,u^c))
                assert not value,("failed rational left null test",r,u,value)
                count+=1
        result={"status":"FULL_Q_DEGREE2_EXACT_NEGATIVE_PASS",
                "left_kernel_h0":str(h[0]),"checked_generators":count,
                "left_kernel":[[q,str(v)] for q,v in sorted(h.items())]}
    result["full_Q_rank"]=len(pivots)
    result["columns_examined"]=columns_examined
    return result

def search(count=20,max_d=10):
    output=[]
    for seed in range(200):
        rows=synthesize(seed)
        if rows is None:continue
        assert valid(rows)
        labels,Q,d=xor_labels(rows)
        sat=exact_sat(labels,d,21)
        if sat is None:continue
        if sat:
            status={"status":"SAT_CONTROL","sat_count":sat}
        elif d>max_d:
            status={"status":"UNKNOWN_RESOURCE_LIMIT","reason":"kernel dimension above registered rational budget"}
        else:
            status=build(rows,labels,Q)
        status.update({"seed":seed,"n":21,"nullity":d,"sat_count":sat,
             "incidence_sha256":hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest()})
        print("BABEL20_FULL_Q_SCL21_CASE",json.dumps({k:v for k,v in status.items() if k not in ("coefficient_terms","left_kernel")},sort_keys=True),flush=True)
        output.append(status)
        if len(output)>=count:break
    report={"format":"BABEL20_FULL_Q_SCL21_EXACT_MEMBERSHIP_CENSUS_V1",
       "test_count":len(output),
       "full_Q_positive":sum(x["status"]=="FULL_Q_DEGREE2_EXPLICIT_POSITIVE_PASS" for x in output),
       "full_Q_negative":sum(x["status"]=="FULL_Q_DEGREE2_EXACT_NEGATIVE_PASS" for x in output),
       "resource_unknown":sum(x["status"]=="UNKNOWN_RESOURCE_LIMIT" for x in output),
       "cases":output}
    with gzip.open("babel20_SCL21_full_rational_census.json.gz","wt",encoding="utf-8") as f:
        json.dump(report,f,separators=(",",":"),sort_keys=True)
    print("BABEL20_FULL_Q_SCL21_SUMMARY",json.dumps({k:v for k,v in report.items() if k!="cases"},sort_keys=True),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--count",type=int,default=20)
    search(ap.parse_args().count)
