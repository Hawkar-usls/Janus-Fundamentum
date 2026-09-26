# R5 E9 — Pair-Defect Syndrome as a 3-Partite Incidence Polytope

**Date:** 2026-09-23  
**Status:** exact JANUS-derived reformulation + source-bound polynomial island + exact LP counterexample.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. From syndrome zero to a 3-partite degree system

In the DDD source geometry let:

- D1 be the partition of variables into pairs;
- D2,D3 be the two partitions into positive NAE3 triples;
- B := D2 union D3.

The pair-defect syndrome is

[
e_i = 1oplus x_{a_i}oplus x_{b_i}.
]

Therefore

[
E(x)=0
]

is exactly

[
x_{a_i}+x_{b_i}=1
]

over Boolean variables for every D1 pair.

For a positive NAE3 triple T,

[
NAE(x_T)
iff
1le sum_{jin T}x_jle 2.
]

Hence zero membership in the syndrome image is exactly the 0/1 feasibility problem

[
M_1x=mathbf 1,
]

[
mathbf 1le M_2xle 2mathbf 1,
]

[
mathbf 1le M_3xle 2mathbf 1,
]

[
xin{0,1}^n,
]

where M_i is the incidence block of D_i.

Every variable occurs once in each partition, so every column of

[
M=egin{pmatrix}M_1\M_2\M_3end{pmatrix}
]

has exactly three ones.

Thus the activated syndrome-zero core is a degree-constrained 3-partite, 3-uniform incidence problem.

## 2. Universal fractional center

The vector

[
x^*=rac12mathbf 1
]

is feasible for the LP relaxation of **every** such instance:

- every D1 pair sums to 1;
- every D2/D3 triple sums to 3/2.

Therefore the LP relaxation is never empty.

The entire decision problem is an **integrality question**:

> does this universally feasible fractional polytope contain a 0/1 point?

This cleanly separates the easy base B from the activated hard fiber.

## 3. Balanced-incidence polynomial YES island

A 0/1 matrix is balanced iff it contains no square odd-order submatrix with exactly two ones in every row and column; hypergraphically this is absence of a strong odd cycle.

Balanced matrices are recognizable in polynomial time (Conforti–Cornuéjols–Rao; Conforti–Cornuéjols–Kapoor–Vušković; Zambelli).

For a hypergraph of rank at most three, balancedness implies unimodularity / total unimodularity of its incidence matrix.

Our M has column sum exactly three, hence rank three.

Therefore:

### Theorem BIS-1

If M is balanced, then M is totally unimodular.

The constraint matrix of

[
M_1x=1,quad
M_{23}xge1,quad
M_{23}xle2,quad
0le xle1
]

is obtained from row submatrices of M by duplicating rows and changing row signs, plus identity rows.

Total unimodularity is preserved by these operations.

The right-hand sides are integral.

Hence the LP polytope is integral.

Since (x^*=rac12mathbf1) proves nonemptiness, the polytope has an integral vertex.

Therefore:

[
oxed{
M	ext{ balanced}
Longrightarrow
0in E(Mod(B))
}
]

and an integral witness is constructible in polynomial time by linear programming.

### Corollary BIS-2

Every NO-instance of the pair-defect syndrome-zero problem has an unbalanced incidence matrix and therefore contains a strong odd-cycle certificate.

This is a one-sided structural theorem:

BALANCED = guaranteed YES.

UNBALANCED does not imply NO.

## 4. Why this is stronger than raw General Factor

Without D1, the variables are edges of the cubic bipartite graph between D2 and D3 clause nodes and B asks for a [1,2]-factor.

That is a 2-partite network/general-factor object.

Adding D1 makes every Boolean variable participate in one row from each of three partition classes.

The hardness migration can therefore be written as

[
	ext{2-partite degree system / flow-like}
longrightarrow
	ext{3-partite rank-3 incidence integrality}.
]

This is the polyhedral form of the pair-glue migration previously observed syntactically as fanout 2+2 -> 4.

## 5. Half-integrality is false even in the exact linear source geometry

A natural next hope would be:

> perhaps every extreme point is at least half-integral, enabling a Nemhauser–Trotter-style quotient.

This is false.

Consider n=12 with partitions:

D1 pairs:

[
(8,10),(2,4),(6,7),(3,5),(0,1),(9,11).
]

D2 triples:

[
(2,5,10),(0,8,11),(4,6,9),(1,3,7).
]

D3 triples:

[
(3,6,10),(2,8,9),(1,5,11),(0,4,7).
]

Every two constraints from different partitions intersect in at most one variable, so this is a linear 3-disjoint incidence geometry.

The LP has the exact feasible point

[
x=
rac1{13}
(4,9,5,3,8,10,12,1,2,6,11,7).
]

All D1 row sums are exactly 1.

D2 row sums are

[
(2,1,2,1),
]

and D3 row sums are

[
(2,1,2,1).
]

Hence every displayed row is active at an allowed integral bound.

Take all six D1 rows, D2 rows 0,1,2, and D3 rows 0,1,2.

The resulting 12x12 active incidence matrix has determinant

[
oxed{13}.
]

Therefore those active equations have a unique solution, namely the point above.

So this point is an LP vertex with denominator 13.

### Consequence

The syndrome polytope is not:
- integral in general;
- half-integral;
- quarter-integral;
- controlled by any denominator-2 local odd-cycle picture.

A single strong odd cycle gives the familiar determinant-2 obstruction, but interacting odd-cycle/non-TU structure can amplify to much larger determinants.

## 6. Minimal local unbalanced token in the denominator-13 example

The same incidence matrix already contains the 3x3 submatrix on:

rows:
- D1 pair (8,10),
- D2 triple (2,5,10),
- D3 triple (2,8,9);

columns:
- 2,8,10.

The submatrix is

[
egin{pmatrix}
0&1&1\
1&0&1\
1&1&0
end{pmatrix}
]

with determinant 2.

This is a strong odd 3-cycle.

Thus the denominator-13 vertex contains local determinant-2 obstructions, but its full fractional geometry is **not** explained by one such obstruction in isolation.

The correct missing object is therefore an interaction calculus for overlapping non-TU/strong-odd-cycle structure.

## 7. New preprocessing rule

Add before any new syndrome-image representation attempt:

### BALANCED-SYNDROME CHECK

1. build the 3-partite incidence matrix M;
2. test balancedness in polynomial time;
3. if balanced:
   - solve the LP;
   - output an integral zero-syndrome witness;
   - reconstruct the original SAT witness;
4. if unbalanced:
   - retain a strong odd-cycle certificate and pass to the obstruction layer.

This is an exact polynomial Class-R terminal rule on the balanced island.

## 8. New active gate

### R5_E9_STRONG_ODD_CYCLE_INTERACTION_QUOTIENT_GATE_V1

Input:
an unbalanced linear 3-partite syndrome core, together with a polynomially found strong odd-cycle certificate.

Goal:
construct a polynomial witness-preserving quotient that reduces the interacting non-TU core and eventually restores balancedness, **without branching on cycle assignments and without expanding back to the signed degree-4 SAT core**.

A valid progress measure must not be:
- number of fractional coordinates;
- denominator 2 / half-integrality;
- one-cycle elimination count unless global monotonicity is proved.

The determinant-13 control is mandatory: any proposed local odd-cycle repair must explain how it handles interaction amplification beyond one determinant-2 cycle.

## 9. Strategic interpretation

The syndrome frontier is now:

[
	ext{easy B / 2-partite factor}
]

[
+ D1	ext{ pair equations}
]

[
Downarrow
]

[
	ext{3-partite rank-3 incidence polytope}
]

[
Downarrow
]

[
egin{cases}
	ext{balanced} &Rightarrow 	ext{LP integral, YES in P},\
	ext{unbalanced} &Rightarrow 	ext{strong odd-cycle interaction core}.
end{cases}
]

The missing compression currency is no longer generic syndrome representation.

It is a contraction law for the **interaction of non-TU odd-cycle blocks**.

D1 = EMPTY.  
P_VS_NP = OPEN.
