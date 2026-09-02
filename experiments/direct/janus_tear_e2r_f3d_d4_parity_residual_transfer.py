#!/usr/bin/env python3
from itertools import product

def parity(bits):
    r=0
    for b in bits:r^=b
    return r

def block(V,a): return tuple((v,1-b) for v,b in zip(V,a))
def cnf(V,c): return tuple(sorted(block(V,a) for a in product((0,1),repeat=len(V)) if parity(a)!=c))
def rc(C,rho):
    out=[]
    for v,p in C:
        if v not in rho: out.append((v,p)); continue
        val=rho[v] if p else 1-rho[v]
        if val:return None
    return tuple(out)
def restrict(F,rho): return tuple(sorted(set(D for C in F if (D:=rc(C,rho)) is not None)))
def residual_c(c,V,rho): return c ^ parity([rho[v] for v in V if v in rho])

def main():
    V=("x","y","z","w")
    for c in (0,1):
        for states in product((-1,0,1),repeat=len(V)):
            rho={v:s for v,s in zip(V,states) if s!=-1}
            lhs=restrict(cnf(V,c),rho)
            free=tuple(v for v in V if v not in rho)
            if free:
                rhs=cnf(free,residual_c(c,V,rho))
            else:
                rhs=() if parity([rho[v] for v in V])==c else ((),)
            assert lhs==rhs
    eps=1/16; Delta=16
    assert (1-2*eps)*Delta-1 >= 6*eps*Delta
    assert (1-8*eps)*Delta >= 1
    hoods=[{"x","y"},{"y","z"},{"w"}]
    assert any({"x","y"}<=H for H in hoods)
    assert not any({"x","z"}<=H for H in hoods)
    print("C025_E2R_F3D_D4_X_DIRECT_PARITY_RESTRICTION_IDENTITY = PASS")
    print("C025_E2R_F3D_D4_X_RESIDUAL_BALANCEDNESS_ARITHMETIC = PASS")
    print("C025_E2R_F3D_D4_X_LOCAL_FUNCTION_ADMISSION = PASS")
    print("C025_E2R_F3D_D4_X_CLAIM_CEILING = FINITE_MECHANICS_ONLY")
    print("P_VS_NP = OPEN")
if __name__=='__main__':main()
