# R5 E9 — Signed-Balanced Pair-Glue Normal Form

**Date:** 2026-09-23  
**Status:** exact JANUS-derived normal form + source-bound TDI polynomial island.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Eliminate the pair layer algebraically, not combinatorially

For every D1 pair choose an orientation

[
(a_i,b_i)
]

and introduce one representative variable

[
t_i:=x_{a_i}.
]

The zero-syndrome condition on the pair gives exactly

[
x_{b_i}=1-t_i.
]

This removes every D1 equation and half of the Boolean coordinates without any branching.

Because the source geometry is linear, a D2/D3 triple contains at most one member of any D1 pair.

Therefore every ternary row becomes a signed row with three nonzero coefficients.

## 2. Canonical signed inequality form

Let a ternary row use:
- representatives with coefficient +1;
- pair-mates with coefficient -1.

Let

[
a_rin{0,pm1}^m
]

be the resulting signed row and let

[
n(a_r)
]

be the number of negative entries.

The original NAE condition

[
1le sum x_jle2
]

becomes exactly

[
1-n(a_r)le a_rtle2-n(a_r).
]

The lower inequality is the canonical balanced-matrix form

[
a_rtge1-n(a_r).
]

For the upper inequality use -a_r.
Since every row has exactly three nonzero entries,

[
n(-a_r)=3-n(a_r),
]

hence

[
(-a_r)tge1-n(-a_r)
=
n(a_r)-2,
]

which is exactly

[
a_rtle2-n(a_r).
]

Thus the whole zero-syndrome problem is

[
A tge 1-n(A),
]

[
(-A)tge 1-n(-A),
]

[
0le tle1,
]

plus integrality of t.

## 3. Universal fractional center survives pair substitution

For every signed ternary row,

[
a_rleft(rac12mathbf1ight)
=
rac12igl(#(+1)-#(-1)igr).
]

Adding the substitution constant n(a_r) reconstructs a triple sum of 3/2.

Therefore

[
t^*=rac12mathbf1
]

is feasible for every signed pair-glue LP.

Again the decision question is pure integrality.

## 4. Signed-balanced polynomial island

A 0,±1 matrix is balanced when every square submatrix with exactly two nonzero entries in each row and column has total entry-sum divisible by four.

Conforti and Cornuéjols prove that for a balanced 0,±1 matrix the canonical systems

[
a_i x ge 1-n(a_i),
quad
a_i x le 1-n(a_i),
quad
a_i x = 1-n(a_i),
quad
0le xle1
]

are totally dual integral in the appropriate row partition.

Balanced 0,±1 matrices are polynomially recognizable (Conforti–Cornuéjols–Kapoor–Vušković; Zambelli).

Row sign changes preserve balancedness, and duplicating a row with either sign does not create a new forbidden cycle.

Hence if A is balanced, the stacked lower/upper system using A and -A is TDI.

Its right-hand side is integral.

Since t*=1/2 proves feasibility, the polytope has an integral point.

### Theorem SBPG-1

[
oxed{
A	ext{ signed-balanced}
Longrightarrow
0in E(Mod(B))
}
]

and a zero-syndrome witness is constructible in polynomial time.

No enumeration of pair orientations is used.

## 5. Orientation invariance

Choosing the opposite representative in one D1 pair replaces

[
t_imapsto1-t_i.
]

At the signed matrix level this flips the sign of column i and shifts row constants accordingly.

Balancedness of a 0,±1 matrix is invariant under column sign flips.

Therefore signed-balanced recognition is independent of the arbitrary orientation chosen for D1 pairs.

It is a structural property of the pair-glued instance.

## 6. Strictness over the unsigned 3-partite balanced test

The signed test is genuinely stronger.

Consider n=12 with:

D1:
[
(1,5),(6,7),(0,10),(3,11),(4,9),(2,8).
]

D2:
[
(0,1,8),(3,5,9),(4,7,10),(2,6,11).
]

D3:
[
(1,4,11),(3,7,8),(0,6,9),(2,5,10).
]

This is linear across the three partitions.

The original 0/1 3-partite incidence matrix is unbalanced.

Orient each D1 pair by its first coordinate.
The reduced signed matrix is

[
A=
egin{pmatrix}
 1& 0& 1& 0& 0&-1\
-1& 0& 0& 1&-1& 0\
 0&-1&-1& 0& 1& 0\
 0& 1& 0&-1& 0& 1\
 1& 0& 0&-1& 1& 0\
 0&-1& 0& 1& 0&-1\
 0& 1& 1& 0&-1& 0\
-1& 0&-1& 0& 0& 1
end{pmatrix}.
]

An exhaustive forbidden-cycle check verifies that this signed matrix is balanced.

Therefore:

[
	ext{unsigned-balanced island}
subsetneq
	ext{signed-balanced pair-glue island}.
]

## 7. Signed obstruction token

If A is not balanced, polynomial recognition supplies a forbidden signed cycle submatrix:

- exactly two nonzeros in every selected row and column;
- total signed sum congruent to 2 mod 4.

This is the signed analogue of a strong odd cycle.

Call it a **frustrated pair-glue cycle**.

Every zero-syndrome NO-instance must survive the signed-balanced test and therefore contains such a frustrated cycle.

Again the converse is false: an unbalanced signed matrix may still have integral witnesses.

## 8. Updated preprocessing chain

For the pair-defect syndrome gate:

1. exact D1 pair substitution;
2. build signed ternary matrix A;
3. test signed balancedness;
4. if balanced:
   - solve the TDI LP;
   - obtain integral t;
   - reconstruct all original x variables;
5. if unbalanced:
   - extract a frustrated signed-cycle certificate;
   - pass only this residual interaction layer to the new quotient machinery.

This strictly dominates the earlier unsigned-balanced check.

## 9. Current hard frontier

The denominator-13 control from the previous artifact remains mandatory.

Its pair-substituted active signed system has determinant magnitude 13.

Thus the unbalanced side cannot be modeled as independent determinant-2 cycles or as half-integral rounding.

The missing object is an exact calculus for **interacting frustrated signed cycles**.

### Active gate

[
oxed{
R5_E9_SIGNED_CYCLE_INTERACTION_QUOTIENT_GATE_V1
}
]

Target:
poly-synthesize a witness-preserving contraction of an unbalanced signed pair-glue core until signed balancedness is restored, without:
- branching over cycle assignments;
- expanding back to degree-4 SAT;
- assuming bounded denominator;
- enumerating all forbidden cycles.

D1 = EMPTY.  
P_VS_NP = OPEN.
