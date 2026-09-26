# R5 E9 — Standard Exact-One CNF is linearly lean

Date: 2026-09-27
Status: THEOREM_CANDIDATE__NOT_LEDGER_PROMOTED
Global status: `P_VS_NP = OPEN`

## Scope

This note closes the `R2` **simple/linear-autarky** donor for the standard CNF encoding of Exact-One constraints. It does **not** claim absence of arbitrary autarkies and does not prove a universal SAT selector.

An Exact-One constraint on distinct Boolean variables `a,b,c` is represented by

\[
(a\vee b\vee c)\wedge(\neg a\vee\neg b)\wedge(\neg a\vee\neg c)\wedge(\neg b\vee\neg c).
\]

We use the standard linear-autarky matrix convention in which a positive literal contributes `+1`, a negative literal contributes `-1`, and a simple linear autarky vector `x` satisfies `Ax >= 0`.

## Local theorem

For one Exact-One triple, write the coordinates as `a,b,c`. The four clause rows impose

\[
a+b+c\ge 0,
\]
\[
-a-b\ge0,\qquad -a-c\ge0,\qquad -b-c\ge0.
\]

Twice the first left-hand side plus the other three left-hand sides is identically zero:

\[
2(a+b+c)+(-a-b)+(-a-c)+(-b-c)=0.
\]

Every summand in this identity is nonnegative under `Ax >= 0`; hence every summand is zero. In particular

\[
a+b=0,\qquad a+c=0,\qquad b+c=0.
\]

Subtracting the first two gives `b=c`; with `b+c=0` this gives `b=c=0`, and then `a=0`.

Therefore every coordinate occurring in an Exact-One triple is zero in every simple linear-autarky vector.

## Global corollary

Let `F` be any CNF obtained only by conjoining standard Exact-One triples, with every variable occurring in at least one triple. Apply the local theorem to every triple. Every variable coordinate is forced to zero. Thus the only vector satisfying the simple-linear autarky inequalities is the zero vector.

Hence:

\[
\boxed{F\text{ has no nontrivial simple linear autarky.}}
\]

Since a simple-linear reduction needs a nonzero first autarky vector, the iterated simple/linear-autarky reduction cannot make a first nontrivial step. In the corresponding autarky system, the untouched Exact-One carrier is linearly lean.

No regularity, cubic-degree, hypergraph-linearity, phase, or girth assumption is used.

## Prior-art binding

This uses the established linear-autarky framework rather than claiming that framework as JANUS novelty. Kullmann's work introduces linear autarkies found in polynomial time by linear programming and the corresponding notion of linearly lean clause-sets; Kullmann's later lean-clause-set framework treats general, linear, and matching autarky systems and their canonical normal forms.

Sources checked before promotion:

- Oliver Kullmann, *Investigations on autark assignments*, Discrete Applied Mathematics 107 (2000), 99–137, DOI `10.1016/S0166-218X(00)00262-6`.
- Oliver Kullmann, *Lean clause-sets: generalizations of minimally unsatisfiable clause-sets*, Discrete Applied Mathematics 130 (2003), 209–249, DOI `10.1016/S0166-218X(02)00406-7`.
- Existing JANUS WDR scheduler and matching-autarky theorem in this branch.

The JANUS contribution here is the elementary Exact-One specialization above: the four standard clause inequalities force every simple-linear autarky coordinate on the carrier to vanish.

## Consequence for the frozen WDR frontier

For the standard Exact-One carrier:

```text
R0 forced / cleanup                    CLOSED (prior)
R1 exact equivalence substitution      OPEN
R2 matching autarky                    CLOSED on cubic-linear class (prior)
R2 simple/linear autarky               CLOSED on all standard Exact-One carriers (this theorem)
R3 blocked-clause deletion             CLOSED (prior)
R4 no-growth DP elimination            CLOSED (prior)
R5 signed structural dominance         OPEN
R6 ranked / SR macros                  OPEN
R7 direct tractable extraction         CLOSED as direct terminal tests (prior)
representation-changing carriers       OPEN
```

## Epistemic firewall

```text
THEOREM_SCOPE
= SIMPLE_LINEAR_AUTARKY_ON_STANDARD_EXACT_ONE_CNF

GENERAL_AUTARKY
= NOT_CLOSED_BY_THIS_RESULT

UNIVERSAL_SELECTOR
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
