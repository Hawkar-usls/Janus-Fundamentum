# R5 E9 — Cubic Exact-One Boundary Pinning Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__EXACT_DEGREE_PROFILE_PINNING_NOT_SOURCE_CLOSED`

Immediate parent:
`PA-0020-ODD-HOLE-CONTEXTUAL-MULTISELECTOR-DOMINANCE`

## G0 — exact object

The PA-0020 boundary argument uses arbitrary outside contexts to explain why
distinct projected states cannot be merged context-independently.

The changed question is stricter:

> Can the same distinction already be enforced by an outside context that stays
> entirely inside the **cubic positive Exact-One-3 source language**?

A full odd-hole boundary port already occurs once in its source block.  Therefore
a source-valid completion gadget must use each exposed boundary variable exactly

```
2 additional times,
```

while every new internal variable occurs exactly three times and every new
clause contains exactly three distinct positive variables.

The precise primitive to audit is a three-port gadget

```
G_t(x,y,z,U)
```

such that:

1. x,y,z each have gadget-degree exactly 2;
2. every u in U has gadget-degree exactly 3;
3. all constraints are positive Exact-One-3;
4. the projected relation on (x,y,z) is a prescribed singleton
   `{t}`, where `t in {0,1}^3`.

If all eight singleton patterns admit constant-size gadgets, arbitrary complete
boundary assignments of size divisible by three can be pinned by disjoint
composition while preserving cubic degree exactly.

## G1 — internal anti-duplication

Repository-first search covered:

- the cubic positive Exact-One / perfect-kernel normal form;
- the rank-3 local matching barrier;
- pin-activated XOR material in transformed NAE coordinates;
- boundary Myhill--Nerode semantics;
- witness-dominance / persistency;
- all current exact-one odd-hole artifacts.

No existing JANUS artifact was found that gives the exact three-port
degree-(2 boundary / 3 internal) singleton-pinning family above.

## G2 — canonical external language

The broad external languages are standard:

- Boolean CSP primitive-positive gadgets;
- forcing / pinning gadgets;
- Positive / Monotone 1-in-3 SAT;
- bounded-occurrence / cubic 1-in-3 SAT;
- degree-completion gadgets in hardness reductions.

Schaefer's Boolean CSP framework source-binds generalized satisfiability and
primitive-positive gadget reasoning at the broad level.

Moore--Robson prove NP-completeness for planar cubic monotone/positive 1-in-3
SAT, source-binding the exact source class in which every variable has degree
three.

These sources do not by themselves give the present boundary-degree profile.

## G3 — targeted public-source sweep

### S1 — general 1-in-3 forcing is standard

The literature contains many 1-in-3 reductions with auxiliary variables,
constant simulation, equality/negation simulation, and forcing gadgets.

Classification:

```
GENERAL 1-IN-3 GADGET / PP-DEFINITION LANGUAGE
=
SOURCE-BOUND.
```

This is not enough for the current claim because arbitrary gadgets may reuse
variables, introduce constants, leave auxiliary degree unconstrained, or use a
boundary variable the wrong number of times.

### S2 — cubic positive 1-in-3 source class is standard

Moore--Robson, *Hard Tiling Problems with Simple Tiles*,
Discrete & Computational Geometry 26 (2001), 573--590,
arXiv:math/0003039, prove the planar cubic monotone 1-in-3 source restriction.

Thus neither cubicity nor positive Exact-One is JANUS novelty.

Classification:

```
CUBIC POSITIVE / MONOTONE 1-IN-3 SOURCE CLASS
=
SOURCE-BOUND.
```

### S3 — planar / connectivity gadget papers are adjacent

Later positive planar 1-in-3 reductions use variable rings and forcing-style
structures, including bounded-occurrence and connectivity-preserving gadgets.

No located source in this pass states the exact universal singleton-pin
statement:

```
for every t in {0,1}^3
there is a constant-size positive Exact-One-3 gadget
with
boundary degrees exactly 2
and all internal degrees exactly 3
whose projection is {t}.
```

Classification:

```
EXACT DEGREE-BALANCED THREE-PORT SINGLETON PIN FAMILY
=
NO SOURCE CLOSURE LOCATED.
```

This is a scoped source audit, not a legal novelty certification.

## G4 — why this matters for PA-0020

If the exact pin family exists, a full odd-hole boundary has `3k` ports.
Partition them into triples and attach one pin gadget per triple.

Then any chosen complete boundary assignment can be enforced by a context that:

- uses only positive Exact-One-3 clauses;
- raises every old boundary variable from occurrence one to occurrence three;
- gives every new variable occurrence exactly three;
- keeps every clause size exactly three.

Hence two different exact boundary relations remain distinguishable by a
**source-valid cubic context**, not merely by an arbitrary CNF pin context.

This would strengthen the context-independent merge firewall without saying
anything against instance-specific witness dominance.

## Audit decision

```
PA-0021
=
PASS_SCOPED_GAP_CONFIRMED

GENERAL 1-IN-3 GADGET LANGUAGE
=
SOURCE-BOUND

CUBIC POSITIVE 1-IN-3 CLASS
=
SOURCE-BOUND

EXACT 3-PORT DEGREE-(2/3) SINGLETON PIN FAMILY
=
SCOPED GAP

NEW MATH AUTHORIZED ONLY INSIDE
=
R5_E9_CUBIC_SOURCE_BOUNDARY_PINNING_GATE_V1

P_VS_NP
=
OPEN
```

## Mandatory anti-loop controls

Do not:

- claim forcing gadgets in general as new;
- use repeated literals or constants while claiming the exact cubic source
  contract;
- leave internal variable degrees below three;
- count a gadget whose boundary variable appears other than exactly twice;
- infer P!=NP or any complexity lower bound from source-context
  distinguishability.
