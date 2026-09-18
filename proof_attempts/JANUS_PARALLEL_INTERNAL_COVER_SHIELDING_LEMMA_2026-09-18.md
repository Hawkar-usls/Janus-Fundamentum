# JANUS Parallel Internal-Cover Shielding Lemma

**Lineage:** parallel research branch from `main@4f21bb08f8198096cb285a16e17c96d6c0f75be2`.

**Isolation rule:** this branch does not modify, merge, or claim authority over the existing Mantequilla/WALL branches. The Mantequilla observation is treated as read-only inspiration; all claims below are restated and checked independently for JANUS.

## Setup

Let

[
F_C(X_C,B_C)=igwedge_{Dinmathcal C_C} D
]

be a local CNF over internal variables (X_C) and boundary variables (B_C).

For an internal assignment (alpha), define the residual branch

[
R_alpha(B_C)=F_C(alpha,B_C).
]

The existential boundary relation is

[
R_C(B_C)=igvee_alpha R_alpha(B_C).
]

If (R_Cequiv	op), let (kappa_C) be the minimum number of residual branches whose disjunction is (	op). Otherwise (kappa_C) is undefined/infinite.

For clause (D), let (I(D)) be the disjunction of its internal literals and (B(D)) the disjunction of its boundary literals.

## Exact tautology-safe theorem

A clause whose boundary projection (B(D)) is already tautological needs no internal shielding. Therefore define

[
U_C^*(X_C)=igwedge_{D:;B(D)
otequiv	op} I(D).
]

Then, for arbitrary finite CNF syntax,

[
oxed{U_C^*in SATiff existsalpha;R_alpha(B_C)equiv	opiff kappa_C=1.}
]

### Proof

Fix (alpha). After substituting (alpha) into clause (D):

* if (I(D)) is satisfied by (alpha), the whole clause becomes (	op);
* otherwise the residual clause is exactly (B(D)).

Hence (R_alphaequiv	op) iff every clause either is internally satisfied by (alpha) or has a tautological boundary projection. This is exactly the satisfaction condition for (U_C^*). Therefore

[
U_C^*in SATiffexistsalpha:R_alphaequiv	op.
]

If such a branch exists, one residual branch covers all boundary assignments, so (kappa_C=1). Conversely (kappa_C=1) means one residual branch is already (	op).

## Normalized-clause corollary

If local clauses are normalized so no clause contains a complementary literal pair, then no boundary projection can be tautological. In that standard setting

[
U_C^*=U_C
]

where

[
U_C=igwedge_D I(D).
]

Thus the Mantequilla form follows exactly:

[
oxed{U_Cin SATiff existsalpha;R_alpha=	opiffkappa_C=1.}
]

The normalization condition is essential. Without it, the single clause ((blor
eg b)) has (R_alphaequiv	op) for every (alpha) while the naive internal cover contains an empty clause and is UNSAT.

## Mechanistic classification

For a routed local object:

* (U_C^*in SAT): **UNIVERSAL_BRANCH_SHIELDING**, therefore (R_C=	op) and (kappa_C=1).
* (U_C^*in UNSAT) but (R_C=	op): **DISTRIBUTED_SHIELDING**, necessarily (kappa_C>1).
* (R_C
otin{	op,ot}): **SEMANTIC_SIGNAL**.
* (R_C=ot): **TRIVIAL_FALSE**.

This classification explains a (kappa_C=1) trivial escape without requiring full boundary-relation enumeration once a witness to (U_C^*) is known.

## Complexity firewall

The theorem is a semantic characterization, **not** a general polynomial-time algorithm. Deciding (U_C^*in SAT) can itself be SAT-hard when the internal component is unrestricted. JANUS may use the test as a bounded/local/mechanistic filter only when its own resource envelope is independently justified.

No claim here establishes general connected-mixed tractability, general SAT in P, or either direction of P versus NP.

[
oxed{P_VS_NP=OPEN}
]
