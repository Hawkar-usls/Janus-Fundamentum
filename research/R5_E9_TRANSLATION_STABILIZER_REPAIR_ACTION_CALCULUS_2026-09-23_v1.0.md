# R5 E9 — Translation-Stabilizer Repair-Action Calculus

**Date:** 2026-09-23  
**Status:** exact JANUS-derived action theorem + scoped polynomial synthesis algorithm.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.  
**Novelty boundary:** no claim that translation symmetries, CSP symmetries, or symmetry breaking are new; the contribution here is their explicit integration into the JANUS ranked witness-repair / choice-dimension contraction framework.

## 1. Local translation stabilizer

Let

[
Rsubseteq mathbb F_2^k.
]

Define

[
H_R
:=
{hinmathbb F_2^k: R+h=R},
]

where

[
R+h={a+h:ain R}.
]

### Lemma TS-1

(H_R) is a linear subspace of (mathbb F_2^k).

### Proof

The zero vector stabilizes R.

If (h,gin H_R), then

[
R+(h+g)=(R+h)+g=R+g=R.
]

Since every element of (mathbb F_2^k) is its own additive inverse, closure under addition is enough. ∎

For fixed/bounded arity relations, (H_R) can be precomputed exactly from the truth table.  
For native affine relations it is obtained directly from the homogeneous kernel.

Examples:

[
H_{mathrm{OR}_3}={000},
]

[
H_{mathrm{NAE}_3}={000,111},
]

[
H_{mathrm{EQ}_2}={00,11},
]

and for

[
R={y:Ay=b},
]

[
H_R=ker A.
]

## 2. Global structural translation space

Consider a Boolean CSP / grouped-CNF representation

[
I=igwedge_{cinmathcal C}R_c(x_{S_c}),
]

where every admitted block (R_c) has a polynomially computable translation stabilizer (H_{R_c}).

Define

[
H(I)
=
left{
hinmathbb F_2^V:
h|_{S_c}in H_{R_c}
	ext{ for every }c
ight}.
]

### Theorem TS-2 — polynomial synthesis

(H(I)) is a linear subspace and, provided each local (H_{R_c}) is supplied by polynomial-size linear equations, a basis of (H(I)) is deterministically computable in polynomial time by Gaussian elimination.

### Proof

For every c choose a parity-check matrix (Q_c) satisfying

[
H_{R_c}=ker Q_c.
]

Embed every (Q_c) into the global variable coordinates. Stacking all rows gives one global matrix Q such that

[
H(I)=ker Q.
]

Gaussian elimination gives a basis in polynomial time. ∎

## 3. Every synthesized mask is a model-preserving action

### Theorem TS-3

For every (hin H(I)),

[
ymodels I
iff
y+hmodels I.
]

### Proof

For every constraint c,

[
h|_{S_c}in H_{R_c},
]

so

[
y|_{S_c}in R_c
iff
y|_{S_c}+h|_{S_c}in R_c.
]

Conjoin over c. ∎

Thus

[
	au_h(y)=y+h
]

is an explicit polynomial-time structural witness transformer.

## 4. Canonical orbit quotient removes dim H(I) Boolean dimensions at once

Let

[
r=dim H(I).
]

Choose a basis matrix M of H(I), with basis vectors as rows, and row-reduce M.

Let

[
P={p_1,ldots,p_r}
]

be its pivot columns.

The projection

[
pi_P:H(I)	omathbb F_2^P
]

is a linear isomorphism.

Therefore for every assignment y there exists a unique (h_yin H(I)) satisfying

[
h_y|_P=y|_P.
]

Put

[
operatorname{can}(y)=y+h_y.
]

Then

[
operatorname{can}(y)|_P=0.
]

If y is a model, TS-3 implies (operatorname{can}(y)) is a model.

### Theorem TS-4 — translation-orbit contraction

[
oxed{
SAT(I)
iff
SATleft(Iwedgeigwedge_{pin P}
eg pight).
}
]

The contraction removes exactly

[
|P|=dim H(I)
]

Boolean choice dimensions in one polynomially synthesized action quotient.

No branch enumeration is used.

### Reconstruction

A model of the canonical slice is already a model of I, so reverse reconstruction is trivial.

If canonicalization of a pre-existing model is desired, compute (h_y) by solving the r-dimensional basis-coordinate system and output (y+h_y).

## 5. Ranked-repair interpretation

The direct orbit theorem is stronger than needing an iterative rank, but it can be embedded into the ranked-repair framework.

Order the pivot tuple lexicographically:

[
ho_P(y)=y|_P.
]

Whenever (ho_P(y)
e0), the canonicalizer sends y directly to rank zero while preserving I.

Thus structural translation quotient is an exact Class-S -> immediate Class-R macro-step:

[
	ext{synthesize action space}
	o
	ext{canonical slice}
	o
	ext{remove r dimensions}.
]

## 6. Affine positive control

Let

[
I:Ay=b.
]

Then

[
H(I)=ker A.
]

Gaussian elimination computes a basis.

If

[
r=dimker A=n-operatorname{rank}(A),
]

TS-4 removes all r affine free directions by fixing a pivot set of r original variables canonically.

Equivalently for a single variable x:

- if there exists (hinker A) with (h_x=1), translation by h toggles x and allows canonical fixing;
- if no such h exists, x is constant on every affine solution coset; if the system is consistent its forced value is polynomially recoverable from elimination.

Thus the affine repair-action theorem is a special case of TS-4.

## 7. NAE complement positive control recovered

For one NAE3 constraint,

[
H_{mathrm{NAE}_3}
=
operatorname{span}{111}.
]

For a NAE hypergraph, the local conditions say:

[
h_u=h_v=h_w
]

on every hyperedge ({u,v,w}).

Hence h is constant on every connected component of the hypergraph.

Therefore:

[
dim H(I)
=
#	ext{connected components}.
]

For a connected NAE instance:

[
H(I)={0^n,1^n}.
]

So TS-4 fixes exactly one canonical variable, recovering the global-complement ranked-repair theorem.

## 8. Immediate hard-family ceiling

The DDD linear 4-regular NAE3 stress instances are connected in the relevant hard regime / connected samples.

For every connected member,

[
dim H(I)=1.
]

Therefore translation-stabilizer quotient removes only one global Boolean dimension.

After that symmetry is fixed, the translation action space is exhausted.

Hence:

[
	exttt{TRANSLATION_ACTION_CALCULUS}
=
	exttt{REAL POLY CONTRACTION}
]

but

[
	exttt{UNIVERSAL}
=
	exttt{FALSE}.
]

This is a useful exact ceiling: the next missing action on connected NAE4 cannot be another global XOR-mask symmetry.

## 9. Clause-level warning and grouped-block requirement

If NAE3 is represented as two ordinary clauses,

[
(xee yee z)
wedge
(
eg xee
eg yee
eg z),
]

each individual OR-clause has trivial translation stabilizer.

The nontrivial (111) action appears only when the pair is recognized as one grouped NAE relation.

Therefore the calculus operates on a deterministic, proof-carrying block decomposition, not blindly clause-by-clause.

Unrestricted semantic grouping is forbidden because it could hide hard equivalence/search.

Admitted grouping must be recognized by a polynomial syntactic/native certificate.

## 10. Prior-art firewall

General SAT/CSP symmetry breaking is a broad established area.

Complete symmetry-breaking predicates are not assumed polynomially synthesizable; current complexity results show significant barriers even for general symmetry groups.

JANUS therefore claims only the restricted subgroup obtained by intersecting **local XOR-translation stabilizers of explicitly recognized relation blocks**.

This subgroup is polynomially synthesizable by linear algebra.

No complete-automorphism or complete-SBP claim is made.

## 11. New calculus layer

The repair-action library now contains:

[
egin{array}{rcl}
	ext{NAE} &	o& 	ext{component complement translations},\
	ext{AFFINE} &	o& ker A	ext{ translations},\
	ext{EQUALITY} &	o& 	ext{component flips},\
	ext{AUTARKY} &	o& 	ext{partial assignment repair},\
	ext{BCE} &	o& 	ext{conditional literal flip}.
end{array}
]

The first three belong to a common global translation-action algebra.
The last two are conditional/noninvertible repair actions.

## 12. Updated frontier

### R5_E9_CONDITIONAL_REPAIR_ACTION_SYNTHESIS_GATE_V1

First apply the polynomial translation quotient to exhaustion.

On the resulting translation-rigid WDR survivor, synthesize a **conditional structural action**

[
mu(y)
]

which need not be a global automorphism, but which satisfies

[
ymodels Fwedge
eg C
Longrightarrow
mu(y)models F
]

and strictly lowers an admitted rank / immediately fixes at least one Boolean dimension.

The key hard benchmark is now:

> connected DDD NAE4 after one global-complement quotient.

That benchmark has positive irredundant DP charge and no remaining nonzero global translation mask.

So the new action must use local context, conditional repair, or a richer algebra than XOR translation.

D1 = EMPTY.  
P_VS_NP = OPEN.
