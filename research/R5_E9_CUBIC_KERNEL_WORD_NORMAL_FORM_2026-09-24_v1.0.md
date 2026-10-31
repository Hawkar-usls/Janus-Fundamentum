# R5 E9 — Cubic Incidence Kernel-Word Normal Form

Date: 2026-09-24

Authority: JANUS_DERIVED_EXACT_NORMAL_FORM + SOURCE_BOUND_3REGULAR_BIPARTITE_FACTORIZATION__NO_D1_PROMOTION

Parent: R5_E9_CUBIC_3UNIFORM_GLOBAL_CONTRACTION_GATE_V1

Checker: experiments/r5_e9_cubic_kernel_word_normal_form_checker.py

## 1. Cubic incidence matrix

Let J be a Cubic Monotone Positive 1-in-3 instance.

Let A be its clause-by-variable incidence matrix.

Every clause contains exactly three variables and every variable occurs in exactly three clauses.

For each connected incidence component, the number of clause vertices equals the number of variable vertices because the bipartite component is 3-regular on both sides.

Hence each connected component has a square incidence matrix

A in {0,1}^{n x n}

with

A 1 = 3 1
and
1^T A = 3 1^T.

The exact source problem is

A x = 1,
x in {0,1}^n.

## 2. Exact kernel-word transform

Define

z = 3x - 1.

Then

z_i in {-1,2}.

Using A1=3 1:

A z = 3 A x - A1.

Therefore

A x = 1
iff
A z = 0 and z in {-1,2}^n.

The reverse map is

x = (z+1)/3.

Thus:

Cubic Positive 1-in-3
iff
ker_Q(A) intersect {-1,2}^n is nonempty.

This is an exact normal form, not a relaxation.

## 3. Immediate exact filters

### K1. Nonsingular filter

If det(A) != 0 then ker_Q(A)={0}.

Since 0 is not in {-1,2}^n:

det(A) != 0 => UNSAT.

Equivalently, the unique real solution of A x=1 is x=(1/3)1, which is non-Boolean.

### K2. Component size modulo 3

For any kernel word z:

0 = 1^T A z = 3 1^T z.

Hence sum_i z_i=0.

If t coordinates equal 2 and n-t equal -1,

2t-(n-t)=0
implies
3t=n.

Therefore every satisfiable connected cubic component has n divisible by 3 and exactly n/3 coordinates with z_i=2.

Thus

n mod 3 != 0 => UNSAT

componentwise.

## 4. Exact low-nullity solver

Let

d = dim_Q ker A.

Compute rational RREF of A and choose its d free coordinates.

Every kernel vector is uniquely determined by those actual coordinates.

An admissible kernel word assigns each free coordinate one of only two values:

-1 or 2.

Enumerate the 2^d assignments to the free coordinates.

For each assignment:

- reconstruct every pivot coordinate by rational back-substitution;
- reject if any reconstructed coordinate is not exactly -1 or 2;
- otherwise decode x=(z+1)/3 and verify A x=1.

Therefore

T(A) = O(2^d poly(n,bit(A))).

For 0/1 cubic incidence matrices bit(A)=O(1), so:

d=O(log n) => polynomial time.

This is an exact parameterized algorithm in rational nullity.

Large nullity is not claimed to imply hardness.

## 5. Three-perfect-matching factorization

The incidence graph is a 3-regular bipartite graph.

By Konig's line-coloring theorem, the edges of a bipartite graph can be partitioned into Delta matchings; for a 3-regular bipartite graph these are three perfect matchings.

Thus

A = P0 + P1 + P2

for three permutation matrices.

Permute rows and columns so P0 becomes the identity.

Then:

A = I + P + Q.

The exact kernel word equation becomes

z + Pz + Qz = 0,
z in {-1,2}^n.

So the full cubic NP core is representable by:

- two permutations P,Q;
- one two-letter word z;
- one local zero-sum rule per coordinate.

## 6. Equivalent exact-cover semantics inside the kernel word

Let

S={i : z_i=2}.

For any row i, the three values

z_i, z_{P(i)}, z_{Q(i)}

belong to {-1,2} and sum to zero.

The only possible multiset is

{2,-1,-1}.

Therefore every triple

{i,P(i),Q(i)}

contains exactly one element of S.

So the two-permutation kernel-word form is exactly the same cubic 1-in-3 core in a global overlay coordinate system.

It exposes nonlocal algebraic structure without weakening the combinatorial condition.

## 7. Toroidal family

For the triangular-torus family

C_{i,j}={v_{i,j},v_{i+1,j},v_{i,j+1}}

on Z_k^2, the incidence operator is

A_k = I + S_x + S_y.

Fourier characters diagonalize the commuting shifts.

The eigenvalues are

lambda_{a,b}=1+omega^a+omega^b,

where omega is a primitive k-th root of unity.

Three unit complex numbers 1,u,v sum to zero iff {1,u,v} is the rotated equilateral triple; with the first value fixed to 1 this requires u,v to be the two primitive cube roots.

Hence:

3 does not divide k => nullity_Q(A_k)=0,

3 divides k => nullity_Q(A_k)=2.

The checker independently verifies k=3,...,9.

## 8. Infinite satisfiable high-treewidth Kettani counterfamily

For every k divisible by 3 define

x_{i,j}=1 iff i-j is congruent to r mod 3

for any fixed r in {0,1,2}.

In clause

(i,j), (i+1,j), (i,j+1),

the three residues are

d, d+1, d-1 mod 3.

Thus exactly one variable has residue r and every clause has exactly one true variable.

So k=3,6,9,12,... give explicit SAT cubic-monotone instances.

Their associated triangular-torus graph contains the ordinary k x k square grid as a subgraph, so its treewidth is at least k.

Therefore the earlier Kettani bounded-treewidth counterfamily can be strengthened to an infinite YES-family of unbounded treewidth.

## 9. Polynomial preprocessing lane

Before any new global contraction, apply per connected cubic component:

1. component size mod 3 filter;
2. rational rank/nullity computation;
3. nullity=0 UNSAT filter;
4. exact 2^d solver when d is below the frozen logarithmic threshold;
5. any already certified balanced/set-partitioning polynomial lane;
6. otherwise normalize the incidence matrix to I+P+Q.

The survivor is:

connected,
3-uniform / 3-regular,
singular,
large rational nullity,
not already in a known balanced/poly carrier.

## 10. New active gate

Freeze:

R5_E9_TWO_PERMUTATION_KERNEL_WORD_CONTRACTION_GATE_V1

Input:

P,Q permutations and

(I+P+Q)z=0,
z in {-1,2}^n.

Allowed PASS exits:

A. polynomial nonlocal quotient strictly reducing rational kernel dimension while preserving existence and witness decoding;

B. polynomial decomposition into independent orbit/components whose total solve cost is polynomial;

C. exact normalization into a balanced, matching, affine, or other proved-P carrier;

D. a direct polynomial solver for the large-nullity overlay.

Forbidden:

- enumerate 2^d kernel words for superlogarithmic d;
- branch on z_i=-1 versus z_i=2;
- replace the two-letter kernel condition by unrestricted rational kernel membership;
- reduce only modulo 2 or another field and call it exact;
- analyze P and Q separately while ignoring their overlay;
- hide the same Boolean choice in a fresh selector;
- invoke SAT or exact-cover as an oracle.

## 11. Ceiling

CUBIC 1-IN-3 -> {-1,2} KERNEL WORD = EXACT PASS
COMPONENT n mod 3 FILTER = PASS
NULLITY 0 FILTER = PASS
NULLITY d SOLVER = O(2^d poly(n))
LOW NULLITY O(log n) = POLY ISLAND
A=I+P+Q NORMAL FORM = PASS
TORUS NULLITY LAW = PASS
INFINITE SAT HIGH-TREEWIDTH TORUS FAMILY = PASS
LARGE-NULLITY TWO-PERMUTATION CONTRACTION = OPEN
D1 = EMPTY
P_VS_NP = OPEN
