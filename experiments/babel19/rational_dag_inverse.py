#!/usr/bin/env python3
"""BABEL-19 rational inverse via affine substitution DAG; exact arithmetic only.

Given an ordered independent list of sparse integer columns in Q^m, prove
C*lambda=target by reconstructing linear forms y_i in measurements s_j=C_j^T y.
The solver makes NO modular-to-rational inference. It returns Fraction values
and verifies them independently over Q.

Only the source+cover experiment determines whether coefficients are practical.
"""
from collections import defaultdict
from fractions import Fraction

class Circuit:
    def __init__(self):
        self.nodes=[()] # zero node
        self.leaves={}
    def leaf(self,i):
        at=len(self.nodes)
        self.nodes.append(("leaf",i))
        self.leaves[at]=i
        return at
    def linear(self,terms):
        accum=defaultdict(Fraction)
        for coeff,node in terms:
            if coeff and node:accum[node]+=Fraction(coeff)
        pairs=tuple((node,k) for node,k in sorted(accum.items()) if k)
        if not pairs:return 0
        if len(pairs)==1 and pairs[0][1]==1:return pairs[0][0]
        at=len(self.nodes)
        self.nodes.append(pairs)
        return at
    def adjoints(self,target,scale=1):
        d=[0]*len(self.nodes)
        d[target]=Fraction(scale)
        out=defaultdict(Fraction)
        for k in range(len(self.nodes)-1,0,-1):
            val=d[k]
            if not val:continue
            v=self.nodes[k]
            if isinstance(v,tuple) and len(v)==2 and v[0]=="leaf":
                out[v[1]]+=val
            else:
                for child,factor in v:d[child]+=val*factor
        return {i:v for i,v in out.items() if v}

class SparseExactInverse:
    def __init__(self,n):
        self.n=n
        self.par=list(range(n))
        self.mul=[Fraction(1)]*n
        self.offset=[0]*n
        self.dead=[False]*n
        self.size=[1]*n
        self.nodes=Circuit()
        self.pivots=0
        self.max_offset_depth=0
    def find(self,i):
        p=self.par[i]
        if p==i:
            if self.dead[i]:return None,Fraction(0),self.offset[i]
            return i,Fraction(1),0
        root,w,shift=self.find(p)
        weight=self.mul[i]
        off=self.nodes.linear(((1,self.offset[i]),(weight,shift)))
        if root is None:
            self.par[i]=i
            self.dead[i]=True
            self.mul[i]=Fraction(0)
        else:
            self.par[i]=root
            self.mul[i]=weight*w
        self.offset[i]=off
        return root,self.mul[i],off
    def add_column(self,signature):
        accum=defaultdict(Fraction)
        shift_terms=[]
        for i,coefficient in signature:
            root,weight,offset=self.find(i)
            if root is not None:accum[root]+=coefficient*weight
            if offset:shift_terms.append((coefficient,offset))
        live=[(root,a) for root,a in accum.items() if a]
        assert 1<=len(live)<=2,("not short independent column",self.pivots,len(live))
        leaf=self.nodes.leaf(self.pivots)
        shift=self.nodes.linear(shift_terms)
        rhs=self.nodes.linear(((1,leaf),(-1,shift)))
        if len(live)==1:
            root,a=live[0]
            self.dead[root]=True
            self.offset[root]=self.nodes.linear(((Fraction(1,a),rhs),))
        else:
            (r,a),(s,b)=live
            # Merge the smaller component into the larger one.
            if self.size[r]>self.size[s]:
                r,s=s,r
                a,b=b,a
            self.par[r]=s
            self.mul[r]=-b/a
            self.offset[r]=self.nodes.linear(((1/a,rhs),))
            self.size[s]+=self.size[r]
        self.pivots+=1
    def solve(self,nonzero_rhs):
        assert self.pivots==self.n,(self.pivots,self.n)
        target_parts=[]
        for i,v in nonzero_rhs.items():
            if v:
                root,weight,offset=self.find(i)
                assert root is None,("missing exact pivot",i,root)
                target_parts.append((v,offset))
        node=self.nodes.linear(target_parts)
        coeffs=self.nodes.adjoints(node)
        return coeffs

def synthetic_regression():
    # C=[[1,0,1],[0,1,1],[0,0,1]], column-wise.
    cols=[[(0,1)],[(1,1)],[(0,1),(1,1),(2,1)]]
    rhs={0:Fraction(5,2),1:Fraction(3,4),2:Fraction(7,3)}
    solver=SparseExactInverse(3)
    for c in cols:solver.add_column(c)
    x=solver.solve(rhs)
    reconstructed=defaultdict(Fraction)
    for j,c in enumerate(cols):
        for i,v in c:reconstructed[i]+=x.get(j,0)*v
    assert all(reconstructed[i]==rhs.get(i,0) for i in range(3))
    assert x[2]==Fraction(7,3)
    # Independent nontrivial weighted graph cycle.
    cols=[[(0,2),(1,-1)],[(1,3),(2,2)],[(2,1)]]
    rhs={0:Fraction(7,5),1:Fraction(-4,3),2:Fraction(11,6)}
    solver=SparseExactInverse(3)
    for c in cols:solver.add_column(c)
    x=solver.solve(rhs)
    reconstructed=defaultdict(Fraction)
    for j,c in enumerate(cols):
        for i,v in c:reconstructed[i]+=x.get(j,0)*v
    assert all(reconstructed[i]==rhs.get(i,0) for i in range(3))
    print("BABEL19_SYNTHETIC_EXACT_DAG_SOLVER_PASS",len(solver.nodes.nodes),flush=True)

if __name__=="__main__":
    synthetic_regression()
