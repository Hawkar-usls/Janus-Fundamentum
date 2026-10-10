# R5 E9 — Torsion Side-Code Composition Barrier and Schaefer Slice

**Date:** 2026-09-23  
**Status:** exact JANUS-derived representation barrier + tractable slice.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Context

For a full-rank signed interaction block B, write the signed NAE side choice as

B x = ell + s,

where s is Boolean and records, for every ternary row, which of its two admissible integer levels is chosen.

Smith normal form converts integer-lift existence into finite-abelian congruences on s.

This gives a useful local compression, as demonstrated by the frozen determinant-13 block.

The open question was whether arbitrary such side-codes could then be composed generically in polynomial time.

The answer is NO for the generic representation class: the side-code language itself already contains NP-complete Boolean CSPs.

## 2. Fixed Z3 torsion already realizes positive 1-in-3

Let s1,s2,s3 be Boolean.

Consider the single torsion-character constraint

s1+s2+s3 = 1 (mod 3).

Because each si is in {0,1},

0 <= s1+s2+s3 <= 3.

The only integer in this range congruent to 1 modulo 3 is 1.

Therefore

s1+s2+s3 = 1 (mod 3)

iff

exactly one of s1,s2,s3 equals 1.

So one fixed Z3 torsion side-code relation is exactly the positive 1-in-3 relation

R_1/3 = {100,010,001}.

## 3. Generic composition theorem

Define FIXED-Z3-SIDE-CODE-SAT:

Input:
Boolean variables S and constraints of the form

s_i+s_j+s_k = 1 (mod 3).

Question:
is there a Boolean assignment satisfying all constraints?

### Theorem TSC-1

FIXED-Z3-SIDE-CODE-SAT is NP-complete.

### Proof

Membership in NP is immediate.

By Section 2 each constraint is exactly a positive 1-in-3 constraint.

Thus the problem is Positive 1-in-3-SAT, which is NP-complete by Schaefer's Boolean CSP dichotomy / classic 1-in-3-SAT hardness.

QED.

## 4. Consequence for the proposed torsion composition currency

A composition engine with the interface

- arbitrary Boolean side bits;
- arbitrary finite-abelian torsion characters;
- exact feasibility / zero-membership;
- polynomial witness reconstruction;

cannot be justified merely by saying that every block has an SNF / finite abelian quotient.

Even the constant group

Z_3

with one arity-3 character per block already carries an NP-complete CSP.

Therefore:

SNF / torsion quotient
=
VALID LOCAL COMPRESSION,

but

GENERIC TORSION SIDE-CODE COMPOSITION
=
ALREADY AN NP-COMPLETE BOOLEAN CSP LAYER.

This is a representation barrier, not a proof that P!=NP.

A polynomial algorithm for the generic composition problem would itself imply P=NP.

## 5. Characteristic-2 tractable slice

The contrast is exact.

For Boolean side bits, a Z2 character constraint

sum_i a_i s_i = b (mod 2)

is an affine XOR equation.

Arbitrary conjunctions of such constraints are solved in polynomial time by Gaussian elimination.

Hence:

TORSION EXPONENT 2 / AFFINE SIDE-CODE
=
POLYNOMIAL.

But already:

FIXED Z3 + THREE UNIT COEFFICIENTS
=
POSITIVE 1-IN-3
=
NP-COMPLETE.

The important fault line is therefore not torsion size.

It is the interaction between the Boolean cube and non-characteristic-2 modular characters.

## 6. Why the determinant-13 micro-core compressed successfully

For the frozen determinant-13 basis, the Z13 character reduces 64 Boolean side words to exactly

000010
111101.

This two-word relation is an affine one-dimensional F2 coset: the two words differ by 111111.

Equivalently it is a complement-pair / equality-type relation after literal flips.

So although the underlying torsion group is odd (Z13), the **Boolean slice selected by the character happens to land back inside a Schaefer-tractable affine/Krom relation**.

That is why the local block is strongly compressible.

The number 13 itself is not the tractability source.

## 7. Corrected composition target

The missing object is not:

POLYNOMIAL COMPOSITION OF ALL TORSION SIDE-CODES.

That class already contains Positive 1-in-3-SAT.

The useful target is:

> detect and preserve a tractable Boolean structure of each block side-code under composition, or find a new witness-preserving quotient before the side-code family becomes a non-Schaefer CSP.

Candidate tractable side-code forms:

- affine / XOR;
- bijunctive / Krom;
- Horn;
- dual-Horn;
- product/equality components;
- balanced generalized-bicoloring blocks.

The determinant-13 block belongs to the affine/equality-type case after torsion filtering.

## 8. New killer criterion

Any proposed side-code representation must be tested on the fixed relation

R_1/3(s1,s2,s3)
iff
s1+s2+s3 = 1 (mod 3).

If the representation/composition rule treats this relation as a generic polynomially composable torsion character, then it has already swallowed an NP-complete problem.

Therefore every claimed polynomial composition theorem must explain why its admitted side-codes exclude, contract, or otherwise structurally neutralize this exact Z3 relation.

## 9. Updated active gate

### R5_E9_BOOLEAN_SLICE_OF_TORSION_GATE_V1

For every signed interaction block:

1. compute its SNF/torsion character system;
2. consider the induced Boolean side-code relation
   C_B subseteq {0,1}^{rows(B)};
3. determine a polynomial native representation of C_B when it falls into an admitted tractable class;
4. compose only through certified tractable side-code bridges;
5. if C_B contains / realizes the fixed Z3 1-in-3 hard atom, do not hide it behind the word "torsion".

Universal target:

find a new contraction that destroys the non-Schaefer Boolean side interaction before generic composition.

## 10. Strategic conclusion

The determinant-13 result remains a real compression success.

But the new theorem shows exactly why extending it naively would not finish SAT:

LOCAL SNF
-> finite abelian side-code
-> Boolean slice

and the Boolean slice can already be NP-complete.

The frontier has therefore moved from

"compress torsion"

to

"compress the non-Schaefer Boolean slice induced by torsion."

D1 = EMPTY.
P_VS_NP = OPEN.
