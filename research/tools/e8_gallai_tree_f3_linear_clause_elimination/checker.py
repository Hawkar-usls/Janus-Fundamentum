#!/usr/bin/env python3
from itertools import product, combinations

P = 3
COLORS = (0, 1, 2)


def all_edges(vertices):
    return {tuple(sorted(e)) for e in combinations(vertices, 2)}


CASES = [
    {"name":"isolated", "V":(0,), "E":set(), "boundary":{0:("a","b","c")}, "blocks":()},
    {"name":"K2", "V":(0,1), "E":{(0,1)}, "boundary":{0:("a","b"),1:("c","d")}, "blocks":(("K2",(0,1)),)},
    {"name":"K2_path3", "V":(0,1,2), "E":{(0,1),(1,2)}, "boundary":{0:("a","b"),1:("c",),2:("d","e")}, "blocks":(("K2",(0,1)),("K2",(1,2)))},
    {"name":"triangle", "V":(0,1,2), "E":all_edges((0,1,2)), "boundary":{0:("a",),1:("b",),2:("c",)}, "blocks":(("K3",(0,1,2)),)},
    {"name":"triangle_shared_boundary", "V":(0,1,2), "E":all_edges((0,1,2)), "boundary":{0:("a",),1:("a",),2:("b",)}, "blocks":(("K3",(0,1,2)),)},
    {"name":"odd_C5", "V":(0,1,2,3,4), "E":{(0,1),(1,2),(2,3),(3,4),(0,4)}, "boundary":{0:("a",),1:("b",),2:("c",),3:("d",),4:("e",)}, "blocks":(("ODD",(0,1,2,3,4)),)},
    {"name":"triangle_plus_K2", "V":(0,1,2,3), "E":all_edges((0,1,2))|{(2,3)}, "boundary":{0:("a",),1:("b",),2:(),3:("c","d")}, "blocks":(("K3",(0,1,2)),("K2",(2,3)))},
    {"name":"K2_star3", "V":(0,1,2,3), "E":{(0,1),(0,2),(0,3)}, "boundary":{0:(),1:("a","b"),2:("c","d"),3:("e","f")}, "blocks":(("K2",(0,1)),("K2",(0,2)),("K2",(0,3)))},
    {"name":"K4", "V":(0,1,2,3), "E":all_edges((0,1,2,3)), "boundary":{0:(),1:(),2:(),3:()}, "blocks":(("K4",(0,1,2,3)),)},
]


def degree_H(case, v):
    return sum(v in e for e in case["E"])


def boundary_names(case):
    out=[]
    for v in case["V"]:
        for b in case["boundary"].get(v,()):
            if b not in out:
                out.append(b)
    return tuple(out)


def extension_exists(case, bcol):
    V=case["V"]
    for vals in product(COLORS, repeat=len(V)):
        c=dict(zip(V, vals))
        if any(c[u]==c[v] for u,v in case["E"]):
            continue
        ok=True
        for v in V:
            for b in case["boundary"].get(v,()):
                if c[v]==bcol[b]:
                    ok=False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def add_row(rows, terms):
    row={}
    for var,coef in terms:
        row[var]=(row.get(var,0)+coef)%P
        if row[var]==0:
            del row[var]
    rows.append(row)


def build_bad_linear_system(case):
    # Returns equality rows, disequality rows, label variable names, boundary names.
    blocks=case["blocks"]
    if len(blocks)==1 and blocks[0][0]=="K4":
        return "K4", [], [], [], boundary_names(case)
    labels=[]
    block_label={}
    for i,(kind,_) in enumerate(blocks):
        if kind!="K4":
            name=f"k{i}"
            labels.append(name)
            block_label[i]=name
    eq=[]; neq=[]
    for v in case["V"]:
        ids=[i for i,(_,vs) in enumerate(blocks) if v in vs]
        kinds=[blocks[i][0] for i in ids]
        ks=[block_label[i] for i in ids if i in block_label]
        outs=list(case["boundary"].get(v,()))
        if not ids:
            assert len(case["V"])==1 and len(outs)==3
            add_row(eq, [(outs[0],1),(outs[1],1),(outs[2],1)])
            add_row(neq, [(outs[0],1),(outs[1],-1)])
        elif len(ids)==1 and kinds[0]=="K2" and len(outs)==2:
            add_row(eq, [(ks[0],1),(outs[0],1),(outs[1],1)])
            add_row(neq, [(outs[0],1),(outs[1],-1)])
        elif len(ids)==1 and kinds[0] in ("K3","ODD") and len(outs)==1:
            add_row(eq, [(ks[0],1),(outs[0],-1)])
        elif len(ids)==2 and all(k=="K2" for k in kinds) and len(outs)==1:
            add_row(eq, [(ks[0],1),(ks[1],1),(outs[0],1)])
            add_row(neq, [(ks[0],1),(ks[1],-1)])
        elif len(ids)==2 and set(kinds) in ({"K2","K3"},{"K2","ODD"}) and len(outs)==0:
            add_row(eq, [(ks[0],1),(ks[1],-1)])
        elif len(ids)==3 and all(k=="K2" for k in kinds) and len(outs)==0:
            add_row(eq, [(ks[0],1),(ks[1],1),(ks[2],1)])
            add_row(neq, [(ks[0],1),(ks[1],-1)])
        else:
            raise AssertionError((case["name"],v,kinds,outs))
    return "NORMAL", eq, neq, labels, boundary_names(case)


def dense(row, vars_):
    return [row.get(v,0)%P for v in vars_]


def rref(matrix):
    A=[row[:] for row in matrix]
    m=len(A); n=len(A[0]) if A else 0
    pivots=[]; r=0
    for c in range(n):
        piv=next((i for i in range(r,m) if A[i][c]%P),None)
        if piv is None:
            continue
        A[r],A[piv]=A[piv],A[r]
        inv=1 if A[r][c]%P==1 else 2
        A[r]=[(x*inv)%P for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]%P:
                f=A[i][c]%P
                A[i]=[(A[i][j]-f*A[r][j])%P for j in range(n)]
        pivots.append(c); r+=1
        if r==m:
            break
    A=[row for row in A if any(x%P for x in row)]
    return A,pivots[:len(A)]


def dot(row, assignment, vars_):
    return sum(row[i]*assignment[vars_[i]] for i in range(len(vars_)))%P


def compile_clause(case):
    mode,eq_sparse,neq_sparse,labels,boundaries=build_bad_linear_system(case)
    if mode=="K4":
        return {"constant":False,"boundaries":boundaries,"res_eq":[],"res_neq":[],"labels":labels}
    vars_=tuple(labels)+tuple(boundaries)
    eq=[dense(r,vars_) for r in eq_sparse]
    R,pivs=rref(eq)
    label_count=len(labels)
    assert all(c in pivs for c in range(label_count)), (case["name"],labels,pivs,R)

    # Residual equality rows have no label coordinates after RREF.
    res_eq=[row[:] for row,p in zip(R,pivs) if p>=label_count]
    assert all(all(row[c]==0 for c in range(label_count)) for row in res_eq)

    # Reduce disequalities modulo the complete equality row space.
    pivot_row={p:row for row,p in zip(R,pivs)}
    res_neq=[]
    impossible_bad=False
    for sp in neq_sparse:
        q=dense(sp,vars_)
        for p in pivs:
            if q[p]:
                f=q[p]
                prow=pivot_row[p]
                q=[(q[j]-f*prow[j])%P for j in range(len(vars_))]
        assert all(q[c]==0 for c in range(label_count))
        if not any(q):
            impossible_bad=True
        else:
            res_neq.append(q)

    if impossible_bad:
        return {"constant":True,"boundaries":boundaries,"vars":vars_,"res_eq":res_eq,"res_neq":res_neq,"labels":labels}
    return {"constant":None,"boundaries":boundaries,"vars":vars_,"res_eq":res_eq,"res_neq":res_neq,"labels":labels}


def compiled_extend_value(compiled,bcol):
    if compiled["constant"] is not None:
        return compiled["constant"]
    assignment={v:0 for v in compiled["labels"]}
    assignment.update(bcol)
    vars_=compiled["vars"]
    # EXT = OR(residual equality violated) OR(residual disequality becomes zero).
    return any(dot(r,assignment,vars_)!=0 for r in compiled["res_eq"]) or any(dot(r,assignment,vars_)==0 for r in compiled["res_neq"])


def literal_count(compiled):
    if compiled["constant"] is not None:
        return 0
    # R!=0 is (R=1 OR R=2); S==0 is one affine literal.
    return 2*len(compiled["res_eq"])+len(compiled["res_neq"])


def run_case(case):
    for v in case["V"]:
        assert degree_H(case,v)+len(case["boundary"].get(v,()))==3
    comp=compile_clause(case)
    bnames=boundary_names(case)
    total=0
    for vals in product(COLORS,repeat=len(bnames)):
        bcol=dict(zip(bnames,vals))
        actual=extension_exists(case,bcol)
        compiled=compiled_extend_value(comp,bcol)
        assert actual==compiled,(case["name"],bcol,actual,compiled,comp)
        total+=1
    return total,literal_count(comp),len(comp.get("res_eq",[])),len(comp.get("res_neq",[])),len(comp.get("labels",[]))


def main():
    print("E8 v6.6 Gallai-tree -> single GF(3) linear clause checker")
    total=0
    for case in CASES:
        n,lits,neqs,nneq,nlabels=run_case(case)
        total+=n
        print(f"PASS {case['name']}: boundary={n}, labels={nlabels}, residual_eq={neqs}, residual_neq={nneq}, affine_clause_literals={lits}")
    print(f"PASS exact compiled-clause equivalence on {total} boundary assignments across {len(CASES)} Gallai controls")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__=="__main__":
    main()
