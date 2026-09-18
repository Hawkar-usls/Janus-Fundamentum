# U-PAIR-1J Projected Semantic Debt Kernel — T1–T5 Abstract Soundness Theorem

**Date:** 2026-09-19  
**Authority:** `ABSTRACT_SOUNDNESS_THEOREM__NO_COMPLETENESS_OR_POLYTIME_CLAIM`  
**Parent formal specification:** `83b1d699aaeee65d921ff2fcb90f12ddf75fa3ac`  
**Well-founded reconstruction addendum:** `5760c65947c468d490d6990230866d9e0d07c27f`

## 1. Scope

Let the frozen original Boolean relation be

[
F_0(X,B),
]

where (X) is the finite set of original existential/witness obligations and (B) is the retained external interface.

The exact original domain is

[
D_0(B) := exists X,F_0(X,B).
]

A Debt-Kernel state carries a current exact relation (R(Z,B)), its exact external domain

[
D(B):=exists Z,R(Z,B),
]

the obligation partition

[
X=V_{m live};dotcup;V_{m debt};dotcup;V_{m cert},
]

projection/reconstruction receipts (Omega), accepted proof objects (Pi), and the remaining frozen metadata from the formal specification.

This theorem is about **soundness of accepted traces**. It does not state that a terminating trace always exists, can always be found efficiently, or has polynomial size.

The theorem assumes the strengthened well-founded conditions WF1–WF7 from the addendum. In particular:

1. every original obligation has one authoritative status;
2. projection-reconstruction dependencies form an acyclic DAG;
3. every certified receipt exports a total completion term;
4. every such term has a checked local extension proof;
5. semantic transitions preserve the exact external domain;
6. decomposed child witnesses are recomposition-compatible;
7. a terminal closes every receipt and every debt obligation.

---

## 2. Auxiliary Lemma A — Exact external-domain preservation

### Statement

For every accepted semantic transition from state (S) to (S'),

[
D_S(B)equiv D_{S'}(B).
]

Consequently every accepted trace preserves

[
D(B)equiv D_0(B).
]

### Proof

We inspect the legal semantic transitions.

### REVERSIBLE_NORMALIZE

The transition requires a checked exact bijection/isomorphism between the old and new carrier representatives. Therefore the represented Boolean relation is unchanged up to a bijective change of live coordinates. Existential quantification over the live coordinates is invariant under such a bijection, hence the external domain is unchanged.

### PROJECT

The transition supplies the exact equivalence

[
R_{m post}(Y,B)
iff
exists E,R_{m pre}(E,Y,B).
]

Therefore

[
egin{aligned}
D_{m post}(B)
&=exists Y,R_{m post}(Y,B)\
&=exists Y,exists E,R_{m pre}(E,Y,B)\
&=exists E,Y,R_{m pre}(E,Y,B)\
&=D_{m pre}(B).
end{aligned}
]

### DISCHARGE_WITNESS / DISCHARGE_VACUITY

Discharge changes obligation status and attaches reconstruction proof objects. It does not change the represented current relation (R). Hence (D) is unchanged.

### DECOMPOSE / RECOMPOSE

These transitions are admissible only with an exact factorization/recomposition theorem. By WF5–WF6, the portfolio denotes exactly the same parent relation on the external interface. Hence its existential external domain is unchanged.

### ROUTE_REUSE

A cached route has no semantic effect by itself. Only individually revalidated legal transitions affect the accepted state, and those transitions are already covered above.

Thus every accepted semantic transition preserves the exact external domain. By induction along a finite accepted trace,

[
D_{m terminal}equiv D_0.
]

QED.

---

## 3. Auxiliary Lemma B — Well-defined reverse reconstruction

### Statement

Suppose an accepted state has:

- no live original obligations,
- no undischarged debt,
- an acyclic receipt dependency graph,
- a total exported completion term for every certified receipt,
- compatible exact recomposition contracts.

Then every original obligation (xin X) has a well-defined total Boolean reconstruction term over (B) alone.

### Proof

For every projection block (E), its receipt may depend only on (B) and obligations that were still live immediately after (E) was projected. Direct an edge from (E) to every later obligation on which its completion term depends.

WF2 states that this dependency graph is acyclic. Therefore it admits a topological order.

At terminal, no original obligation remains live. Start with receipt blocks whose completion terms depend only on (B). These already define total Boolean functions of (B).

Proceed in reverse dependency order. Whenever a completion term

[
widehat f_E(Y,B)
]

depends on obligations (Y), each obligation in (Y) already has a total reconstruction term by the induction hypothesis. Substitute those terms into (widehat f_E). This yields a total Boolean term

[
f_E(B).
]

WF6 ensures that when decomposition created multiple local views of one obligation, recomposition supplies one compatible authoritative term rather than conflicting copies.

Since the graph is finite and acyclic, this process terminates and defines a total reconstructed value for every original obligation. Collecting the component terms yields

[
f_X(B).
]

Outside the exact domain the values may be arbitrary; T5 requires correctness only when (D_0(B)) holds.

QED.

---

# T1 — Partition Conservation

### Statement

Every accepted Debt-Kernel transition preserves the disjoint partition

[
X=V_{m live};dotcup;V_{m debt};dotcup;V_{m cert}.
]

### Proof

Assume the invariant holds before a transition.

- **REVERSIBLE_NORMALIZE:** all three obligation-status sets are unchanged.
- **PROJECT:** for a block (Esubseteq V_{m live}), remove exactly (E) from (V_{m live}) and add exactly (E) to (V_{m debt}). No other obligation changes status.
- **DISCHARGE_WITNESS:** for a covered block (Esubseteq V_{m debt}), remove exactly (E) from (V_{m debt}) and add exactly (E) to (V_{m cert}).
- **DISCHARGE_VACUITY:** the same set transfer occurs, with a different proof class.
- **DECOMPOSE:** WF1 gives every original obligation one authoritative global status; child occurrences are views and do not create new obligation identities.
- **RECOMPOSE:** WF6 deduplicates obligation identities and preserves the authoritative status of each obligation.
- **ROUTE_REUSE:** no status changes until replayed legal transitions are independently accepted.
- **TERMINATE:** termination reads the partition and does not create, delete, or duplicate obligations.

Thus no accepted transition loses an obligation, duplicates one, or puts one obligation in two authoritative status sets. By induction from the initial partition

[
V_{m live}=X,qquad V_{m debt}=V_{m cert}=arnothing,
]

the invariant holds throughout the trace.

QED.

**Verdict:** `T1_PROVED_UNDER_WF1_WF6`.

---

# T2 — Reversible Zero Progress

Define certified progress by

[
P(S):=|V_{m cert}|.
]

### Statement

For every accepted `REVERSIBLE_NORMALIZE` transition,

[
P(S')=P(S).
]

### Proof

By transition definition, a reversible normalization may change only the exact representative/carrier coordinates and the checked map (q). It leaves (V_{m live}), (V_{m debt}), and (V_{m cert}) unchanged.

Therefore

[
|V_{m cert}'|=|V_{m cert}|,
]

hence

[
P(S')=P(S).
]

This remains true for variable renamings, invertible XOR-basis changes, exact DAG refactorings and any other admitted exact bijective reparameterization.

QED.

**Verdict:** `T2_PROVED`.

---

# T3 — Projection Transfers Debt but Creates No Certified Progress

### Statement

Let an accepted `PROJECT` transition eliminate a block

[
Esubseteq V_{m live}
]

of (k=|E|) previously live original obligations. Then

[
|V_{m live}'|=|V_{m live}|-k,
]

[
|V_{m debt}'|=|V_{m debt}|+k,
]

and

[
P(S')=P(S).
]

Equivalently the unresolved burden

[
U(S):=|V_{m live}|+|V_{m debt}|
]

is unchanged by projection.

### Proof

By the typed `PROJECT` transition, exactly the obligations in (E) move from (V_{m live}) to (V_{m debt}). No obligation enters (V_{m cert}).

Therefore the two cardinality identities follow immediately, and

[
|V_{m cert}'|=|V_{m cert}|.
]

Thus

[
P(S')=P(S).
]

Furthermore,

[
egin{aligned}
U(S')
&=(|V_{m live}|-k)+(|V_{m debt}|+k)\
&=|V_{m live}|+|V_{m debt}|\
&=U(S).
end{aligned}
]

So syntactic elimination alone produces no certified progress.

QED.

**Verdict:** `T3_PROVED`.

---

# T4 — Sound One-Step Witness Discharge

Consider one exact projection receipt

[
delta_E:
R_{m post}(Y,B)
iff
exists E,R_{m pre}(E,Y,B).
]

Let its certified total completion term be

[
widehat f_E(Y,B).
]

### Statement

If the checker accepts the local extension proof

[
D_{m post}(B)land R_{m post}(Y,B)
Rightarrow
R_{m pre}(widehat f_E(Y,B),Y,B),
]

then every reachable post-state solution extends to a pre-state solution through this projection step.

### Proof

Take arbitrary (B=b) and (Y=y) such that

[
D_{m post}(b)=1
]

and

[
R_{m post}(y,b)=1.
]

The accepted local extension implication applies directly, giving

[
R_{m pre}(widehat f_E(y,b),y,b)=1.
]

Therefore assigning

[
E:=widehat f_E(y,b)
]

extends the post-state solution ((y,b)) to a satisfying pre-state assignment.

For a globally false-domain vacuity receipt, the premise (D_{m post}(B)) is identically false, so the conditional extension statement is vacuously valid and the recorded canonical default term suffices to keep the composed function total.

Thus every accepted discharge has the required one-step backward-extension property.

QED.

**Verdict:** `T4_PROVED_UNDER_WF3_WF4`.

---

# T5 — Terminal Reconstruction Theorem

### Statement

Let an open-interface Debt-Kernel trace start from the exact original relation (F_0(X,B)) and terminate in an accepted state satisfying WF1–WF7, in particular:

[
V_{m live}=arnothing,
qquad
V_{m debt}=arnothing.
]

Then the terminal proof package defines a total composed Boolean function

[
f_X(B)
]

such that

[
oxed{
D_0(B)Rightarrow F_0(f_X(B),B)
}
]

and the terminal exact domain satisfies

[
oxed{
D(B)iff D_0(B)=exists X,F_0(X,B).
}
]

Hence (f_X) is a valid conditional Skolem map for the original relation on its exact domain.

### Proof

By Auxiliary Lemma A, every accepted transition preserves the exact external domain. Therefore the terminal domain is exactly the original domain:

[
D_{m terminal}(B)equiv D_0(B).
]

By T1 and the terminal conditions,

[
X=V_{m cert}.
]

Thus every original witness obligation is certified and every projection receipt is closed.

By Auxiliary Lemma B, the acyclic receipt dependency graph and total completion terms define a total composed reconstruction map

[
f_X(B).
]

It remains to prove semantic correctness.

Fix an arbitrary boundary assignment (b) satisfying

[
D_0(b)=1.
]

By domain preservation,

[
D_{m terminal}(b)=1.
]

At the terminal relation there are no unresolved original live witness obligations. Follow the accepted semantic trace backwards.

For every certified projection receipt encountered in reverse dependency order, T4 states that the current reachable post-state solution extends through that projection by substituting the receipt's certified completion term.

For every reversible normalization, use the checked inverse isomorphism to return to the previous exact representative.

For every decomposed/recomposed segment, use its exact recomposition contract; WF6 guarantees compatibility of child assignments and prevents conflicting duplicate obligation values.

Inductively, after reversing the complete accepted trace, all projected original obligations have been reconstructed and the resulting assignment to (X) is exactly (f_X(b)). The backward extension invariant yields

[
F_0(f_X(b),b)=1.
]

Because (b) was arbitrary subject only to (D_0(b)=1),

[
D_0(B)Rightarrow F_0(f_X(B),B).
]

Together with

[
D_{m terminal}(B)equiv D_0(B),
]

the terminal package is a sound exact interface

[
(D_0,f_X,pi_D,pi_f,Omega_{m closed}).
]

QED.

**Verdict:** `T5_PROVED_FOR_THE_STRENGTHENED_ABSTRACT_TRANSITION_SYSTEM`.

---

# 4. Corollaries and boundaries

## Corollary 1 — Certified progress is semantic-accounting progress, not solver progress

T1–T5 justify the bookkeeping interpretation

[
P(S)=|V_{m cert}|
]

as the number of original witness obligations for which accepted reconstruction authority exists.

They do **not** imply that (P) must increase at every step, or that a scheduler can always find a discharge.

## Corollary 2 — Projection cannot prove tractability

By T3, a solver may project many variables while leaving

[
U(S)=|V_{m live}|+|V_{m debt}|
]

unchanged. Formula shrinkage therefore does not establish synthesis progress.

## Corollary 3 — Soundness is compatible with arbitrary proposal policy

The proofs above depend on accepted transition certificates, not on who proposed a transition. Therefore a heuristic, ML model, swarm agent or cached route may choose what to try without changing terminal soundness, provided it cannot bypass the immutable transition verifiers.

This is a soundness statement only; a poor scheduler may fail to terminate or may take exponential time.

---

# 5. What remains unproved

This theorem deliberately does **not** prove:

- completeness of the Debt Kernel for arbitrary Boolean functional synthesis;
- existence of polynomial-size receipts or witness DAGs for arbitrary inputs;
- polynomial-time discovery of legal projections or discharges;
- polynomial-time termination;
- p-simulation of SynQBF, M-Res, certified projected KC, SAUNF or any other proof system;
- historical novelty;
- `GENERAL_SAT_IN_P`;
- `P_EQ_NP`.

The global complexity status remains:

[
oxed{	ext{P_VS_NP = OPEN}}.
]

---

# 6. Authorized theorem status

Under the original formal specification plus the well-founded reconstruction addendum:

[
oxed{
	exttt{PASS_ABSTRACT_PROJECTED_SEMANTIC_DEBT_KERNEL_SOUNDNESS_T1_T5}
}
]

with the precise scope:

> Every **accepted finite trace** of the strengthened abstract transition system conserves original witness obligations, assigns zero certified progress to reversible normalization and projection, soundly discharges reconstruction debt, and yields a valid conditional Skolem map at an accepted debt-free terminal.

This is a soundness theorem for the accounting/calculus skeleton. It is not a general synthesis algorithm or complexity theorem.
