#!/usr/bin/env python3
"""BABEL-17 full seed3 Fourier certificate reconstruction and independent replay.

Pure arbitrary-precision integer arithmetic; a local-instance linear Fourier
ideal identity, NOT a standard PSD SOS hierarchy or polynomial-time proof.
"""
import argparse,gzip,hashlib,json,math
from collections import defaultdict,deque
from fractions import Fraction
from pathlib import Path
from janus_babel14_antisector_augmented import prepare
from janus_babel14_exact_transfer import edge_data
from janus_babel14_expand_exact import add,fourier
from janus_babel6_transfer import xor_labels,make_projection,signed_graph
from janus_babel8_krylov_verify import input_data,normal

def sparse_integer_solve(matrix,rhs):
    """Sparse exact rational elimination with Markowitz-style short-row pivoting."""
    n=len(matrix)
    assert len(rhs)==n and all(len(row)==n for row in matrix)
    rows=[]
    bycol=[set() for _ in range(n)]
    for i,mrow in enumerate(matrix):
        row={j:Fraction(v) for j,v in enumerate(mrow) if v}
        assert row
        rows.append(row)
        for j in row:bycol[j].add(i)
    b=[Fraction(v) for v in rhs]
    active=set(range(n))
    pivots=[]
    for step in range(n):
        # Sparse row minimization strongly limits fill-in for graph-like transfers.
        i=min(active,key=lambda j:(len(rows[j]),j))
        assert rows[i],("singular sparse matrix",step)
        j=min(rows[i],key=lambda k:(len(bycol[k]),k))
        pv=rows[i][j]
        prow={k:v/pv for k,v in rows[i].items()}
        pb=b[i]/pv
        active.remove(i)
        for k in rows[i]:bycol[k].discard(i)
        for other in list(bycol[j]):
            factor=rows[other].pop(j)
            bycol[j].discard(other)
            for k,v in prow.items():
                if k==j:continue
                new=rows[other].get(k,Fraction(0))-factor*v
                if new:
                    rows[other][k]=new
                    bycol[k].add(other)
                else:
                    rows[other].pop(k,None)
                    bycol[k].discard(other)
            b[other]-=factor*pb
        pivots.append((j,prow,pb))
        if (step+1)%100==0:
            print("SEED3_SPARSE_COUPLED_ELIMINATION",step+1,"/",n,
                  "active_support",sum(len(rows[k]) for k in active),flush=True)
    solution=[Fraction(0) for _ in range(n)]
    for j,row,pb in reversed(pivots):
        solution[j]=pb-sum((v*solution[k] for k,v in row.items() if k!=j),Fraction(0))
    assert all(x.denominator==1 for x in solution),"nonintegral solve despite unimodular determinant"
    ans=[int(x) for x in solution]
    assert all(sum(v*ans[j] for j,v in enumerate(row) if v)==rhs[i]
               for i,row in enumerate(matrix)), "sparse integer solve replay"
    return ans

def build(circuit_file, output_path):
    circuit=json.loads(Path(circuit_file).read_text())
    assert circuit["seed"]==3 and abs(circuit["coupled_determinant_integer"])==1
    source,lift,labels,Q,e,canonical,touched,active,missing=prepare(3)
    source_rows,src_labels,src_basis,eq,origins=input_data(68)
    assert source_rows==source and src_labels==xor_labels(source)[0]
    polypath=Path("babel9_BALANCED_BIT68_DEGREE4_KRYLOV.json")
    assert hashlib.sha256(polypath.read_bytes()).hexdigest()==circuit["source_krylov_sha256"]
    poly=json.loads(polypath.read_text())["polynomial_coefficients_low_to_high"]
    P0=poly[0]
    v=[0]*32768
    for step,c in enumerate(reversed(poly[1:])):
        v=normal(v,eq);v[0]+=c
        if (step+1)%100==0:print("SEED3_SOURCE_KRYLOV",step+1,"/",len(poly)-1,flush=True)
    check=normal(v,eq)
    assert check[0]==-P0 and not any(check[1:])
    pi,_=make_projection(src_labels,labels,15,16)
    reps={}
    for u in sorted(Q):reps.setdefault(pi(u),u)
    assert set(reps)==set(src_basis)
    witness=circuit["source_syzygy_witnesses"]
    denoms=[Fraction(w["exact_coefficient"]).denominator for w in witness]
    scale=4*math.lcm(*denoms)
    D=scale*4*abs(P0)
    sign=-1 if P0>0 else 1
    terms=defaultdict(int)
    for a,b,c,d in eq:
        r,u=origins[(a,b,c,d)]
        coefficient=scale*4*sign*(v[a]+v[b]+v[c]+v[d])
        if coefficient:add(terms,(r,reps[u]),coefficient)
    print("SEED3_BASE_SOURCE_TERMS",len(terms),"SCALE",scale,flush=True)
    for w in witness:
        scalar=scale*Fraction(w["exact_coefficient"])
        assert scalar.denominator==1
        for r,u,k in w["terms"]:
            assert u in Q and 0<=r<len(source)
            add(terms,(r,u),int(scalar)*k)
    H=fourier(terms,lift,labels)
    seven=circuit["paired_invisible_frequencies"]
    assert all(H.get(q,0)-H.get(q^e,0)==0 for q in seven),"source syzygy failed"
    print("SEED3_SOURCE_SYZYGIES_INVISIBLE_ZERO",len(seven),flush=True)
    forced=set(circuit["base_forced_zero_frequencies"])
    assert all(H.get(q,0)-H.get(q^e,0)==0 for q in forced)
    n=len(source)
    def paired_correction(r,u,k):
        if not k:return
        add(terms,(r,u),k);add(terms,(r,u^e),-k)
        for z in (u,*(u^labels[j] for j in lift[r])):
            add(H,z,k);add(H,z^e,-k)
    rest=circuit["coupled_residual_frequencies"]
    matrix=circuit["coupled_matrix_rows_by_frequencies_columns_by_generators"]
    rhs=[]
    for q in rest:
        a=H.get(q,0)-H.get(q^e,0)
        assert a%2==0
        rhs.append(-a//2)
    correction=sparse_integer_solve(matrix,rhs)
    for w,k in zip(circuit["coupled_generators"],correction):
        paired_correction(w["row"],w["multiplier"],k)
    assert all(H.get(q,0)-H.get(q^e,0)==0 for q in rest)
    for w in circuit["singleton_witnesses"]:
        q,r,u,s=(w[key] for key in ("frequency","row","multiplier","signed_coefficient"))
        a=H.get(q,0)-H.get(q^e,0)
        assert a%(2*s)==0
        paired_correction(r,u,-a//(2*s))
        assert H.get(q,0)-H.get(q^e,0)==0
    assert all(H.get(q,0)-H.get(q^e,0)==0 for q in missing),"unrepaired offgraph"
    print("SEED3_ALL_OFFGRAPH_ZERO",len(missing),flush=True)
    _,_,edges=signed_graph(source,lift,labels,e)
    adjacency=defaultdict(list)
    for r,u in circuit["graph_spanning_forest_edges"]:
        a,b,alpha,beta=edge_data(r,u,edges,labels,canonical)
        adjacency[a].append((b,alpha,beta,r,u))
        adjacency[b].append((a,beta,alpha,r,u))
    signs,parent,order,component={},{},[],{}
    for root in circuit["graph_roots"]:
        signs[root],parent[root],component[root]=1,None,root
        todo=deque([root])
        while todo:
            q=todo.popleft()
            order.append(q)
            for other,alpha,beta,r,u in adjacency[q]:
                if other in signs:continue
                signs[other]=-signs[q]*alpha*beta
                parent[other]=(q,alpha,beta,r,u)
                component[other]=root
                todo.append(other)
    assert set(signs)==touched
    imbalance={}
    for q in touched:
        difference=(D if q==0 else 0)-(H.get(q,0)-H.get(q^e,0))
        assert difference%2==0
        imbalance[q]=difference//2
    def add_row_difference(r,u,k):
        if k:
            add(terms,(r,u),k)
            add(terms,(r+n,u),-k)
    for r,u in circuit["graph_frustrating_chords"]:
        a,z,alpha,beta=edge_data(r,u,edges,labels,canonical)
        root=component[a]
        assert root==component[z]
        denom=signs[a]*alpha+signs[z]*beta
        assert abs(denom)==2
        total=sum(signs[q]*imbalance[q] for q in order if component[q]==root)
        assert total%denom==0
        k=total//denom
        imbalance[a]-=k*alpha
        imbalance[z]-=k*beta
        add_row_difference(r,u,k)
    for q in reversed(order):
        entry=parent[q]
        if entry is None:
            assert imbalance[q]==0
            continue
        p,alpha_parent,beta_child,r,u=entry
        k=imbalance[q]*beta_child
        imbalance[p]-=k*alpha_parent
        imbalance[q]=0
        add_row_difference(r,u,k)
    final=fourier(terms,lift,labels)
    assert final=={0:D},("FAILED_FULL_FOURIER_IDENTITY",len(final))
    print("SEED3_EXACT_FULL_INTEGER_IDENTITY_PASS","terms",len(terms),"normalization_digits",len(str(D)),flush=True)
    with gzip.open(output_path,"wt",encoding="utf-8",compresslevel=6) as out:
        json.dump({"format":"JANUS_BABEL17_SEED3_EXPLICIT_INTEGER_IDENTITY_V1","seed":3,
                   "degree2":True,"n":252,"terms_count":len(terms),
                   "positive_integer_normalization_D":str(D),
                   "terms":[[r,u,str(k)] for (r,u),k in sorted(terms.items())]},
                  out,sort_keys=True,separators=(",",":"))
    return {"status":"BABEL17_SEED3_FULL_INTEGER_IDENTITY_PASS",
            "seed":3,"coefficients":len(terms),"normalization_digits":len(str(D)),
            "exact_all_frequency_identity":True,"expanded_sha256":hashlib.sha256(Path(output_path).read_bytes()).hexdigest()}

def independent_verify(output_path):
    _,lift,labels,Q,e,_,_,_,_=prepare(3)
    with gzip.open(output_path,"rt",encoding="utf-8") as stream:cert=json.load(stream)
    assert cert["format"]=="JANUS_BABEL17_SEED3_EXPLICIT_INTEGER_IDENTITY_V1"
    D=int(cert["positive_integer_normalization_D"])
    assert D>0 and cert["terms_count"]==len(cert["terms"])
    sums=defaultdict(int)
    for r,u,k in cert["terms"]:
        assert 0<=r<252 and u in Q
        k=int(k)
        add(sums,u,k)
        for j in lift[r]:add(sums,u^labels[j],k)
    assert sums=={0:D},("INDEPENDENT_FULL_REPLAY_FAILED",len(sums))
    return {"status":"BABEL17_SEED3_INDEPENDENT_EXACT_FOURIER_REPLAY_PASS","coefficients":len(cert["terms"]),"D_positive":True}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--circuit",type=Path,default=Path("babel17_SEED3_TRANSFER_SCHEME.json"))
    ap.add_argument("--output",type=Path,default=Path("babel17_SEED3_EXPLICIT_INTEGER_IDENTITY.json.gz"))
    ap.add_argument("--verify-only",action="store_true")
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    verdict=independent_verify(args.output) if args.verify_only else build(args.circuit,args.output)
    if args.report:args.report.write_text(json.dumps(verdict,indent=2,sort_keys=True)+"\n")
    print(json.dumps(verdict,sort_keys=True,indent=2),flush=True)
