# R5 E10 — COPY Stabilizer, OR->COPY Coset, and Inclusion–Exclusion Closure

**Date:** 2026-09-23  
**Status:** first E10 subgate mathematically closed.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. COPY_d stabilizer for d >= 3

Let

[
C_d=e_0^{otimes d}+e_1^{otimes d}.
]

Suppose (T_1,dots,T_din GL_2(mathbb F)), over a field of characteristic not forcing the two basis vectors to coincide, and

[
(T_1otimescdotsotimes T_d)C_d=lambda C_d,
qquad lambda
e0.
]

For every i put

[
a_i=T_i e_0,qquad b_i=T_i e_1.
]

Because each (T_i) is invertible, (a_i,b_i) are linearly independent. Hence the left side is a rank-two product decomposition

[
a_1otimescdotsotimes a_d+
b_1otimescdotsotimes b_d.
]

For (dge3), a rank-two product decomposition with independent factor pairs is unique up to:
- exchanging the two summands globally;
- independent nonzero rescalings on the factors whose products agree.

Therefore there exists one common permutation
(sigmain S_2) and nonzero scalars
(alpha_i,eta_i) such that

[
T_i e_0=alpha_i e_{sigma(0)},qquad
T_i e_1=eta_i e_{sigma(1)}
]

for every i, with

[
prod_ialpha_i=prod_ieta_i=lambda.
]

Equivalently every (T_i) is monomial and all legs use the same basis permutation:

[
T_i=P_sigmaoperatorname{diag}(alpha_i,eta_i).
]

This exactly characterizes the projective local stabilizer of (C_d) for (dge3).

### Arity two exception

For

[
C_2=operatorname{vec}(I),
]

the stabilizer is larger:

[
(T_1otimes T_2)C_2=lambda C_2
iff
T_1T_2^T=lambda I
iff
T_2=lambda T_1^{-T}.
]

Thus degree-two variables have extra gauge freedom; degree >=3 variables do not.

## 2. Symmetric exact OR3 -> COPY3 transform

Let

[
O=operatorname{OR}_3.
]

Write

[
u=(1,1)^T,qquad e_0=(1,0)^T.
]

Then

[
O=u^{otimes3}-e_0^{otimes3}.
]

Define

[
B=
egin{pmatrix}
0&1\
-1&1
end{pmatrix}.
]

Then

[
Bu=e_0,qquad Be_0=-e_1,
]

hence

[
B^{otimes3}O
=
e_0^{otimes3}+e_1^{otimes3}
=
C_3.
]

This identity is symmetric in all three clause legs.

For a signed literal, let (X) be the swap matrix.
A clause with sign bits (s_1,s_2,s_3) is normalized by the base transforms

[
B X^{s_1},quad
B X^{s_2},quad
B X^{s_3}.
]

## 3. Full OR3 -> COPY3 coset

Because (B^{otimes3}O=C_3), every triple
((T_1,T_2,T_3)) satisfying

[
(T_1otimes T_2otimes T_3)O=lambda C_3
]

is exactly of the form

[
T_i=S_iB,
]

where ((S_1,S_2,S_3)) is in the projective stabilizer of (C_3).

Therefore every such (T_i) is:

[
T_i=
P_sigma
operatorname{diag}(alpha_i,eta_i)B,
]

with one common (sigma) across the clause and

[
prod_ialpha_i=prod_ieta_i.
]

For signed clauses append the literal swap (X^{s_i}).

Hence there is no hidden additional local gauge family beyond COPY-stabilizer rescaling/permutation of the symmetric B transform.

## 4. All-COPY synchronization is impossible at degree >=3 variables

In the exact tensor-network gauge convention, applying (T_e) on the clause side of incidence edge e forces (T_e^{-T}) on the variable side.

Suppose a variable v has degree (dge3) and we demand that its equality tensor (C_d) also remain projectively in the COPY family:

[
igotimes_{e
i v}T_e^{-T};C_d
sim C_d.
]

By Section 1 every (T_e^{-T}), hence every (T_e), must be monomial.

But every clause-normalizing transform has form

[
T_e=S_e B X^{s_e},
]

where (S_e) and (X^{s_e}) are monomial while B has three nonzero entries and is not monomial.

Left/right multiplication by monomial matrices preserves the zero pattern up to row/column permutation and scaling, so (S_eBX^{s_e}) is never monomial.

Contradiction.

Therefore:

> Any formula containing a degree >=3 variable cannot be transformed by local invertible edge gauges so that every OR3 clause and every variable equality tensor are simultaneously COPY tensors.

This is an unconditional algebraic obstruction, not a complexity assumption.

## 5. The symmetric B gauge is exactly clause inclusion–exclusion

Put every clause into COPY form using the symmetric B transform and contract the clause COPY node to one binary selector (z_Cin{0,1}).

For an original variable x, let (P_x) be its positive-occurrence clauses and (N_x) its negative-occurrence clauses.

The transformed variable factor (f_x) on the neighboring clause selectors has the exact values:

- (f_x=2) if all neighboring (z_C=0);
- (f_x=(-1)^t) if the selected neighboring clauses are a nonempty set of t clauses all from (P_x);
- (f_x=(-1)^t) if they are a nonempty set of t clauses all from (N_x);
- (f_x=0) if selected clauses contain both a positive and a negative occurrence of x.

Thus for a 3CNF F:

[
#SAT(F)
=
sum_{Ssubseteq Clauses(F)}
(-1)^{|S|}
mathbf 1[	ext{S is polarity-consistent}]
2^{,n-|Vars(S)|}.
]

Here polarity-consistent means that no variable occurs both positively and negatively among the clauses of S.

This is exactly ordinary inclusion–exclusion applied to the bad events “clause C is falsified”:
- a selected family S of bad events has empty intersection if it forces some variable to both Boolean values;
- otherwise its intersection contains exactly (2^{n-|Vars(S)|}) assignments.

The identity was independently brute-checked on random CNFs against direct model counting.

## 6. Consequence for the whole OR->COPY gauge coset

Section 3 shows that every local OR3->COPY3 gauge differs from B only by:
- local nonzero rescaling;
- common COPY-basis permutation.

Therefore an exact strategy whose central move is

> transform every clause to COPY and then exploit only the residual COPY stabilizer freedom

does not introduce a fundamentally new state representation. It is a reweighted/relabelled form of clause inclusion–exclusion.

This closes the immediate E10 OR3_COPY_GAUGE_SYNCHRONIZATION subgate as:

[
	exttt{PASS_IDENTITY / FAIL_AS_NEW_UNIVERSAL_CURRENCY}.
]

## 7. Counting-strength firewall

An invertible holographic/edge-gauge transformation preserves the full tensor contraction, not just zero/nonzero.

For the standard SAT factor network that contraction is exactly (#SAT(F)).

Therefore any generic polynomial-time exact contraction algorithm obtained solely through invertible gauges for arbitrary F would yield

[
FP=#P,
]

which is substantially stronger than the decision-level target (P=NP).

This does not prove the route impossible.
It says the route is aiming at a stronger target than necessary.

## 8. Strategic pivot

Keep as reusable:
- COPY stabilizer theorem;
- OR3->COPY3 exact coset;
- inclusion–exclusion dual formula;
- tensor/Holant language as a source of algebraic identities.

Demote as primary:
- exact invertible-gauge normalization whose endpoint requires polynomial exact contraction for arbitrary SAT.

The next mechanism should preserve only the required decision semantics:

[
Fin SAT
iff
Q(F)in YES,
]

with polynomial witness reconstruction, while being allowed to discard counting multiplicity.

Candidate mechanism class:

> **proof-carrying witness-preserving noninvertible normalization / extension compression**

The transformation may quotient, merge or introduce states provided every semantic loss has an explicit polynomial lifting certificate.

This deliberately targets P=NP rather than FP=#P.

D1 = EMPTY.  
P_VS_NP = OPEN.
