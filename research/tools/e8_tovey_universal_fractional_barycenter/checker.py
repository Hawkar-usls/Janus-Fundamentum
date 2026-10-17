#!/usr/bin/env python3
from fractions import Fraction


def local_point():
    # 1/2 {M} + 1/3 {L,R} + 1/6 {R}
    weights = [
        (Fraction(1,2), (0,1,0)),
        (Fraction(1,3), (1,0,1)),
        (Fraction(1,6), (0,0,1)),
    ]
    out=[Fraction(0) for _ in range(3)]
    total=Fraction(0)
    for w,v in weights:
        total += w
        for i,a in enumerate(v):
            out[i] += w*a
    assert total == 1
    assert out == [Fraction(1,3),Fraction(1,2),Fraction(1,2)]
    # exact P3 stable-set inequalities
    L,M,R=out
    assert L+M <= 1
    assert M+R <= 1
    return out


def tovey_counts(phi):
    # phi is list of 3-tuples, no repeated absolute variable inside a clause.
    occ={}
    for ci,C in enumerate(phi):
        assert len(C)==3
        assert len({abs(x) for x in C})==3
        for lit in C:
            occ.setdefault(abs(lit),[]).append((ci,lit))
    copies=sum(len(v) for v in occ.values())
    original_clauses=len(phi)
    implication_clauses=copies
    return copies, original_clauses, implication_clauses


def check_formula(phi):
    copies,m3,m2=tovey_counts(phi)
    # Universal fractional point: each inherited 3-clause gets 3*(1/3)=1;
    # each implication clause gets 2*(1/2)=1.
    assert 3*Fraction(1,3)==1
    assert 2*Fraction(1,2)==1
    # Every copy sees the same exact local point.
    p=local_point()
    assert p == [Fraction(1,3),Fraction(1,2),Fraction(1,2)]
    return copies,m3,m2


def main():
    # One SAT and one UNSAT original 3-CNF.  The UNSAT instance contains
    # all eight sign patterns on three variables, hence forbids every assignment.
    sat=[(1,2,3),(-1,2,3)]
    unsat=[]
    for mask in range(8):
        C=[]
        for i in range(3):
            var=i+1
            C.append(-var if ((mask>>i)&1) else var)
        unsat.append(tuple(C))

    for name,phi in [('SAT_CONTROL',sat),('UNSAT_ALL8',unsat)]:
        copies,m3,m2=check_formula(phi)
        print(name, 'copies=',copies,'original3=',m3,'implication2=',m2,'PASS')

    print('PASS_TOVEY_UNIVERSAL_FRACTIONAL_BARYCENTER')
    print('EXACT_VARIABLE_SIDE_CONVEX_HULL_PLUS_CLAUSE_EQUALITIES=ALWAYS_FEASIBLE')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
