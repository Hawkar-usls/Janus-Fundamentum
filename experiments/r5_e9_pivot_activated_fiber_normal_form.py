#!/usr/bin/env python3
from itertools import product

def pix_project(q0,q1):
    out=set()
    for x,y in product((0,1),repeat=2):
        ok=False
        for a,b,c,d in product((0,1),repeat=4):
            vals={"x":x,"y":y,"a":a,"b":b,"c":c,"d":d,"q0":q0,"q1":q1}
            edges=(("x","a","b"),("y","c","d"),("a","c","q0"),
                   ("a","d","q1"),("b","c","q1"),("b","d","q0"))
            if all(len({vals[v] for v in e})>1 for e in edges):
                ok=True; break
        if ok: out.add((x,y))
    return out

def gated_formula(r,p,x,y):
    # e=1 iff x=y.
    e = 1 ^ x ^ y
    return (p*e==0) and (e*(x^r)==0)

def main():
    for r,p,x,y in product((0,1),repeat=4):
        got=(x,y) in pix_project(r,r^p)
        want=gated_formula(r,p,x,y)
        assert got==want

    for r in (0,1):
        assert {
            (x,y) for x,y in product((0,1),repeat=2)
            if gated_formula(r,1,x,y)
        } == {(0,1),(1,0)}

    # Mandatory pivot condition p=1 eliminates r from the hard fiber.
    for r0,r1 in product((0,1),repeat=2):
        hard0={(x,y) for x,y in product((0,1),repeat=2)
               if gated_formula(r0,1,x,y)}
        hard1={(x,y) for x,y in product((0,1),repeat=2)
               if gated_formula(r1,1,x,y)}
        assert hard0==hard1=={(0,1),(1,0)}

    print("PIX_GATED_INTERFACE_NORMAL_FORM = PASS")
    print("G_r(p,x,y) <=> p*e=0 AND e*(x XOR r)=0")
    print("where e=1 XOR x XOR y")
    print("MANDATORY_PIVOT_FIBER_p1 = NEQ_INDEPENDENT_OF_r")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
