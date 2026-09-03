#!/usr/bin/env python3

BASE=[[2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],[1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]]
PIVOT=2
LOCAL=[1,3,4,5,6]
PI={1:-3,3:-5,4:6,5:-1,6:-4}


def simplify(F,v,val):
    sat=v if val else -v; false=-v if val else v; out=[]
    for C in F:
        if sat in C: continue
        out.append([l for l in C if l!=false])
    return out

def mapping_for_block(i): return {PIVOT:PIVOT, **{v:10*(i+1)+j+1 for j,v in enumerate(LOCAL)}}
def rename_clause(C,m): return [(1 if l>0 else -1)*m[abs(l)] for l in C]
def family(k):
    F=[]; maps=[]
    for i in range(k):
        m=mapping_for_block(i); maps.append(m); F.extend(rename_clause(C,m) for C in BASE)
    for i in range(k-1):
        for v in LOCAL:
            a=maps[i][v]; b=maps[i+1][v]
            F.append([-a,b]); F.append([a,-b])
    return F,maps

class UF:
    def __init__(self, xs): self.p={x:x for x in xs}
    def find(self,x):
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]; x=self.p[x]
        return x
    def union(self,a,b):
        a=self.find(a); b=self.find(b)
        if a!=b: self.p[max(a,b)]=min(a,b)

def vars_of(F): return {abs(l) for C in F for l in C}
def detect_equalities(F):
    bins={frozenset(C) for C in F if len(C)==2}
    uf=UF(vars_of(F))
    for C in list(bins):
        a,b=tuple(C)
        if a*b>=0: continue
        # detect (¬u∨v) together with (u∨¬v)
        comp=frozenset({-a,-b})
        if comp in bins:
            uf.union(abs(a),abs(b))
    return uf

def quotient(F,uf):
    out=set()
    for C in F:
        q=[]; taut=False
        for l in C:
            r=uf.find(abs(l)); lit=r if l>0 else -r
            if -lit in q: taut=True; break
            if lit not in q: q.append(lit)
        if taut: continue
        out.add(tuple(sorted(q,key=lambda z:(abs(z),z))))
    return sorted(out)

def normalize_tracks(Q,maps):
    reps={maps[0][v]:v for v in LOCAL}
    out=[]
    for C in Q:
        out.append(tuple(sorted(((1 if l>0 else -1)*reps[abs(l)] for l in C), key=lambda z:(abs(z),z))))
    return sorted(set(out))
def canon(F): return sorted(set(tuple(sorted(C,key=lambda z:(abs(z),z))) for C in F))
def pi_clause(C,pi): return {(pi[abs(l)] if l>0 else -pi[abs(l)]) for l in C}
def transport_valid(target,source,pi):
    return all(any(set(D).issubset(pi_clause(C,pi)) for D in source) for C in target)

def main():
    for k in [2,3,5]:
        F,maps=family(k)
        A=simplify(F,PIVOT,False); B=simplify(F,PIVOT,True)
        ufa=detect_equalities(A); ufb=detect_equalities(B)
        QA=quotient(A,ufa); QB=quotient(B,ufb)
        NA=normalize_tracks(QA,maps); NB=normalize_tracks(QB,maps)
        baseA=canon(simplify(BASE,PIVOT,False)); baseB=canon(simplify(BASE,PIVOT,True))
        assert NA==baseA
        assert NB==baseB
        assert transport_valid(baseA,baseB,PI)
    print('R44BW EXACT REPLAY PASS')
    print('connected_family_quotients_to_base_pair=true')
    print('quotient_variable_count=5')
    print('K5_transport_valid_on_quotient=true')
    print('raw_support_unbounded_but_quotient_support=5')
    print('TRUMP_finished=false')
    print('SAT_IN_P=NOT_PROVED')
    print('P_VS_NP=OPEN')

if __name__=='__main__': main()
