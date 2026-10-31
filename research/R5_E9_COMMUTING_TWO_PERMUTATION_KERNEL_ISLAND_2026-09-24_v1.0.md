# R5 E9 — Commuting Two-Permutation Kernel Island

Date: 2026-09-24

Authority: JANUS_DERIVED_EXACT_POLY_ISLAND__NO_D1_PROMOTION

Parent: R5_E9_TWO_PERMUTATION_KERNEL_WORD_CONTRACTION_GATE_V1

Checker: experiments/r5_e9_commuting_permutation_kernel_island.py

## 1. Setting

Take one connected cubic component in the normalized form

A = I + P + Q

with P,Q permutation matrices and

(I+P+Q)z=0,
z in {-1,2}^n.

Assume

PQ = QP.

Because the original cubic incidence component is connected, the permutation group

G=<P,Q>

acts transitively on the n coordinates.

Since P and Q commute, G is abelian.

Fix a coordinate with stabilizer H. Because G is abelian, H is normal; transitivity identifies the coordinate set with G/H, and the induced action of G/H is regular. Therefore the permutation representation is the regular representation of the finite abelian quotient G/H. In particular, every character of G/H occurs with multiplicity exactly one.

## 2. Simultaneous character decomposition

Commuting permutation matrices are commuting normal matrices.
Hence over C they are simultaneously diagonalizable.

Every common eigenspace is represented by a character chi of the transitive abelian action:

P v_chi = chi(P) v_chi,
Q v_chi = chi(Q) v_chi,

with |chi(P)|=|chi(Q)|=1.

On this eigenspace

(I+P+Q)v_chi =
(1+chi(P)+chi(Q)) v_chi.

So a character contributes to the kernel iff

1+chi(P)+chi(Q)=0.

## 3. Only the two cube-root characters can vanish

If u,v lie on the complex unit circle and

1+u+v=0,

then the three unit vectors form an equilateral triangle centered at zero.

With the first value fixed to 1, necessarily

{u,v}={omega,omega^2},

where omega is a primitive cube root of unity.

Since P,Q generate the transitive abelian action, a character is uniquely determined by its values on P and Q. By the regular-representation multiplicity argument above, each such character occurs with multiplicity exactly one.

Therefore at most two one-dimensional eigenspaces can satisfy the kernel equation:

(chi(P),chi(Q))=(omega,omega^2)

or

(omega^2,omega).

These are complex conjugates.

Because A is rational/real, its nullity over Q equals its nullity over C.

Hence:

dim_Q ker(I+P+Q) is either 0 or 2.

There is no connected commuting large-nullity sector.

## 4. Exact solution count in the nullity-2 case

Suppose nullity is 2.

One kernel character gives a surjective homomorphism

phi : G -> Z_3

with

phi(P)=1,
phi(Q)=-1

up to swapping the two orientations.

The coordinate set splits into three equal phase classes

phi^{-1}(0), phi^{-1}(1), phi^{-1}(2).

The real kernel is the two-dimensional space of functions that are constant on the three phase classes with class-values summing to zero.

An admissible kernel word may use only -1 and 2.

The only three triples of class-values from {-1,2} summing to zero are the permutations of

(2,-1,-1).

Therefore there are exactly three admissible kernel words.

Equivalently, there are exactly three exact-one witnesses, one for each Z3 phase class.

Thus connected commuting overlays are solved in polynomial time:

- nullity 0 -> UNSAT;
- nullity 2 -> construct/check the three phase witnesses or simply invoke the existing 2^d low-nullity solver with d=2.

## 5. Toroidal family as a special case

The triangular torus has commuting shifts

P=S_x, Q=S_y.

The earlier Fourier theorem is exactly this commuting-island theorem:

- if the required Z3 character does not descend to the finite torus, nullity=0;
- if it does, nullity=2 and the three residue-class witnesses appear.

## 6. Structural consequence

A connected survivor with rational nullity larger than 2 must satisfy

PQ != QP.

So the hard large-nullity frontier is not merely 'two permutations'.
It is a genuinely noncommuting permutation overlay.

Noncommutativity itself is not claimed to imply hardness.
It is only a necessary condition for surviving the current polynomial preprocessing.

## 7. New active gate

Freeze:

R5_E9_NONCOMMUTING_TWO_PERMUTATION_KERNEL_WORD_GATE_V1

Input:

connected normalized cubic component

(I+P+Q)z=0,
z in {-1,2}^n,

with

- large rational nullity;
- PQ != QP;
- not already in balanced/matching/other proved-P lanes.

Target:

a polynomial nonlocal quotient/solver exploiting the interaction structure of the noncommuting overlay.

Candidate structural diagnostics:

- commutator subgroup/orbits;
- representation blocks of <P,Q>;
- simultaneous invariant subspaces;
- quotient actions reducing kernel dimension;
- bounded nonabelian interaction width.

Forbidden:

- treat P and Q independently;
- enumerate kernel words;
- branch on z coordinates;
- replace exact two-letter kernel membership by unrestricted linear algebra.

## 8. Ceiling

COMMUTING CONNECTED OVERLAY = POLY
COMMUTING NULLITY = 0 OR 2
NULLITY 2 EXACT KERNEL WORDS = 3
LARGE-NULLITY SURVIVOR => NONCOMMUTING
NONCOMMUTING GLOBAL CONTRACTION = OPEN
D1 = EMPTY
P_VS_NP = OPEN
