# U-PAIR-1J × Mantequilla: Proof-Carrying Shielding Bridge

## Status

This document is a successor research artifact to the frozen U-PAIR-1J preregistration.
It does **not** mutate `SKOLEM_LOCAL_DERIVATION_V1` and does not promote any general SAT claim.

## Exact local interface

For a local relation

[
F_C(X_C,B_C),
]

define the exact boundary domain

[
D_C(B_C) := exists X_C,F_C(X_C,B_C).
]

A proof-carrying local interface is

[
Pi_C=(D_C,f_C,pi_D,pi_f),
]

where

[
pi_D:quad D_C(B_C)iffexists X_C,F_C(X_C,B_C)
]

and

[
pi_f:quad D_C(B_C)Rightarrow F_C(f_C(B_C),B_C).
]

No witness obligation exists outside the exact domain.

Thus the bridge separates two obligations that must not be conflated:

1. **DOMAIN:** which boundary assignments admit an internal completion?
2. **WITNESS:** on that domain, how is an internal completion reconstructed?

This is the precise interface between the Mantequilla boundary relation and U-PAIR Skolem discharge.

## New V1.1 rule: INTERNAL_COVER_WITNESS

For clause (D), let (I(D)) be the disjunction of its internal literals and (B(D)) the disjunction of its boundary literals.

Use the tautology-safe cover

[
U_C^*=igwedge_{D:,B(D)
otequiv	op} I(D).
]

A certificate `INTERNAL_COVER_WITNESS(alpha)` is accepted iff for every local clause (D),

[
B(D)equiv	op
quad	ext{or}quad
alphamodels I(D).
]

Then every clause is true independently of boundary values, so

[
F_C(alpha,B_C)equiv	op.
]

Therefore

[
D_Cequiv	op,qquad f_C(B_C)=alpha.
]

Verification is clause-local and linear in the local clause/literal representation once (alpha) is supplied.

This is a **verification rule only**. No polynomial synthesis claim is made for finding (alpha).

## Guarded composition

A `GUARDED_ITE(g, Pi_true, Pi_false)` node is accepted only with an exact complementary split (g,
eg g).

If the two children carry

[
(D_t,f_t),qquad (D_f,f_f),
]

then the parent carries

[
D=(gland D_t)lor(
eg gland D_f)
]

and

[
f=operatorname{ITE}(g,f_t,f_f).
]

Coverage is obtained **by construction** from the complementary split. The verifier is not allowed to invoke a generic Boolean-DAG tautology oracle to prove that an arbitrary list of guards covers the domain.

Hash-consed sharing is part of the representation accounting.

## Taxonomy

### Universal-branch shielding

[
D_C=	op,qquad f_C(B)=alpha.
]

A constant witness is carried by `INTERNAL_COVER_WITNESS(alpha)`.

### Distributed shielding

[
D_C=	op
]

but no constant universal branch exists. The witness is nonconstant and may be represented by a shared guarded derivation DAG.

The first frozen control is

[
F(x,b)=(xlor b)land(
eg xlor
eg b).
]

Here

[
U_C^*in UNSAT,qquad D_C=	op,qquad kappa_C=2,
]

and

[
f(b)=
eg b.
]

The required certificate is a genuine complementary split on (b) with constant leaves.

### Semantic signal

If

[
D_C
otin{	op,ot},
]

a Skolem function may still exist. The interface must retain the exact domain.

For

[
F(x,b)=(xlor b)land(
eg xlor b),
]

we have

[
D_C(b)=b.
]

A witness such as (x=0) is valid on the domain, but any certificate that relabels the interface as total shielding must fail.

## Cost measure

Define

[
mathrm{PCShieldSize}(C)
]

as the minimum size of an accepted proof DAG for a **total shielding** certificate under the frozen calculus.

It differs from (kappa_C):

- (kappa_C) counts semantic residual branches;
- (mathrm{PCShieldSize}) counts the actual proof-carrying representation accepted by the verifier.

Any universal algorithmic claim must separately bound

[
T_{m synth},qquad |Pi|,qquad T_{m verify}
]

by one fixed polynomial in original input length.

Cheap verification is not cheap synthesis.

## Firewall

The bridge does not establish a polynomial algorithm for finding internal-cover witnesses, exact domains, or guarded proofs.

No generic `SKOLEM_VALID` oracle, generic DAG tautology oracle, unbounded truth-table enumeration, or hidden SAT solver is authorized.

[
oxed{	exttt{GENERAL\_SAT\_IN\_P=NOT\_PROVED}}
]

[
oxed{	exttt{P\_VS\_NP=OPEN}}
]
