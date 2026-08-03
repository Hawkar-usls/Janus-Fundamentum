#!/usr/bin/env python3
import itertools, json, random, hashlib

def eval_clause(c,a): return any(a[abs(l)]==(l>0) for l in c)
def eval_cnf(F,a): return all(eval_clause(c,a) for c in F)

def encode(F,n):
    H=[]
    for clause in F:
        fals=[]
        for lit in clause:
            v=abs(lit)
            fals.append(n+v if lit>0 else v)
        H.append(tuple(-v for v in fals))
    A=[((1<<(i-1)) | (1<<(n+i-1)),1) for i in range(1,n+1)]
    return tuple(H),tuple(A)

def coord_translate(H,n):
    out=[]
    for clause in H:
        cc=[]
        for lit in clause:
            assert lit<0
            v=-lit
            cc.append(v-n if v>n else -v)
        out.append(tuple(cc))
    return tuple(out)

def primal_edges(F):
    e=set()
    for c in F:
        vs=sorted(set(map(abs,c)))
        for i in range(len(vs)):
            for j in range(i+1,len(vs)): e.add((vs[i],vs[j]))
    return e

def audit(seed=410041):
    r=random.Random(seed); cases=600; assignment_checks=0
    for _ in range(cases):
        n=r.randint(3,9); m=r.randint(1,16)
        F=[]
        for _ in range(m):
            vs=r.sample(range(1,n+1),3)
            F.append(tuple(v if r.getrandbits(1) else -v for v in vs))
        F=tuple(F)
        H,A=encode(F,n); G=coord_translate(H,n)
        assert G==F
        assert primal_edges(G)==primal_edges(F)
        for bits in itertools.product((False,True), repeat=n):
            lam={i+1:bits[i] for i in range(n)}
            ext=dict(lam)
            for i in range(1,n+1): ext[n+i]=not lam[i]
            assert eval_cnf(F,lam)==eval_cnf(H,ext)
            assignment_checks+=1
    n=24
    F=tuple((i, -((i%n)+1), ((i+1)%n)+1) for i in range(1,n+1))
    H,A=encode(F,n); G=coord_translate(H,n)
    result={
      'artifact_id':'C041-JANUS-AFFINE-COORDINATE-3SAT-IDENTITY',
      'status':'PASS','p_vs_np':'OPEN','seed':seed,'random_formulas':cases,
      'assignment_checks':assignment_checks,
      'theorem':'Under the C023 NAND3+NEQ embedding and the canonical affine parameterization x_i=lambda_i, c_i=1+lambda_i, exact coordinate translation of the Horn NAND3 clauses is syntactically identical to the source 3-CNF.',
      'linear_size':{'source_clauses':len(F),'horn_clauses':len(H),'affine_rows':len(A),'coordinate_clauses':len(G)},
      'topology_preserved':primal_edges(G)==primal_edges(F),
      'decisive_obstruction':'Affine-coordinate substitution alone does not simplify unrestricted Horn-affine composition; on the hard image it reconstructs arbitrary 3-SAT with unchanged clause supports.',
      'new_gate':'POLYNOMIAL_DISCOVERY_OF_TRACTABLE_COORDINATE_FACTOR_STRUCTURE_OR_STRICT_OPEN',
      'claim_boundary':'This blocks only coordinate substitution/factoring without an independently proved tractable structural certificate. It does not rule out richer semantic compression and does not prove P!=NP.'}
    result['integrity_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result

def main():
    x=audit(); print(json.dumps(x,indent=2,sort_keys=True))
    assert x['status']=='PASS' and x['topology_preserved']

if __name__=='__main__': main()
