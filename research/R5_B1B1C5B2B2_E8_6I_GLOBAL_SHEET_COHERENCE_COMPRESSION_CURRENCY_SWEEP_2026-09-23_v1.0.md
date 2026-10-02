# R5 E8 6I — Global Sheet Coherence Compression-Currency Sweep

Date: 2026-09-23

Authority: `SOURCE_FIRST_CURRENCY_SWEEP__ONE_PROVED_ANTILOOP_PLUS_ONE_NEW_EXACT_GATE__NO_D1_PROMOTION`

Parent:

`JANUS_KEYMASTER_LOCKPICK_GLOBAL_SHEET_COHERENCE_2026-09-23_v1.0`

## 1. Frozen target

We require an exact polynomial interface for

```text
THREE_SHEET_DISJUNCTIVE_CSP
->
GLOBAL COHERENT TRACTABLE REPRESENTATION
```

without:

- explicit per-clause SAT-equivalent selectors;
- bounded-backdoor enumeration without a universal bound;
- the frozen direct 1-independence route;
- fixed finite local pp interpretation of full signed 3SAT;
- e_p compactification used only as a repackaging layer.

## 2. Candidate currency A — PGP / switchability

Source notion:

A finite algebra A has polynomially generated powers (PGP) if there is a polynomial p such that every A^n has a generating set of size at most p(n). Switchability is equivalent to PGP for finite algebras in the cited QCSP line.

Primary/source-bound references:

- Carvalho, Madelaine, Martin, Zhuk, *The complexity of quantified constraints: collapsibility, switchability and the algebraic formulation*, TOCL 24(1), 2023 / arXiv:2106.13154.
- Zhuk / related QCSP PGP literature as summarized in the above source.

### Derived blocker for full Boolean 3SAT polymorphism algebra

The already frozen Fundamentum source fact is:

```text
Pol(Gamma_3SAT) = projections.
```

Let A be the two-element algebra whose term operations are only projections.

For any S subseteq A^n, closure under coordinatewise term operations does not add a new tuple:

```text
Sg(S) = S.
```

Reason: every term operation is a projection, so applying a term to any list of generators returns one of those generators.

Therefore generating A^n requires every tuple of A^n:

```text
minimum generator count(A^n)
=
|A|^n
=
2^n.
```

Hence:

```text
FULL BOOLEAN 3SAT PROJECTION ALGEBRA
=
EGP

PGP
=
FAIL

SWITCHABILITY
=
FAIL
```

This is unconditional and does not assume P != NP.

### Scope

This blocks only a **uniform polymorphism-algebra PGP/switchability compression currency** for the full visible signed-3SAT template.

It does not block an instance-specific non-pp representation-changing certificate before the tractable stage.

## 3. Candidate currency B — consistency reductions / Datalog^union

Dalmau and Oprsal introduce Datalog^union / k-consistency reductions.

Source facts:

1. The reductions strictly generalize ordinary gadget reductions.
2. They compose.
3. They can map CSP/PCSP instances to fixed tractable targets such as systems of affine equations.
4. Sherali-Adams levels can be described as consistency reductions to linear programming.
5. In the Boolean tractable world, Datalog^union reductions collapse HornSAT / 2SAT / affine tractable behavior toward XOR-SAT.
6. The source gives a polymorphism characterization for the arc-consistency fragment via a weak minion-homomorphism construction.

Reference:

Victor Dalmau, Jakub Oprsal,
*Local consistency as a reduction between constraint satisfaction problems*,
LICS 2024 / arXiv:2301.05084v3.

### Why this is not already blocked by the pp barrier

A consistency reduction is not merely a fixed local pp gadget.

Its local-consistency closure can add globally implied bounded-arity information before the target instance is produced.

Therefore:

```text
UNIFORM PP SIGGERS/EDGE BARRIER
!=
AUTOMATIC BLOCKER
FOR CONSISTENCY REDUCTIONS.
```

### Why this is not yet a solution

For arbitrary signed 3SAT we do not possess a theorem that a fixed k consistency reduction produces an exact affine/tractable target.

The known fixed-width-local-consistency incompleteness remains a strong negative control, but it does not by itself prove that every consistency **reduction to another solver** is impossible.

Therefore this route requires its own exact gate.

## 4. Candidate currency C — CLAP / LP + affine-IP state

Ciardo and Zivny's CLAP combines constraint basic LP with affine integer programming.

Source facts:

- CLAP has an exact algebraic characterization by a minion homomorphism from a fixed CLAP minion C.
- CLAP solves some PCSP templates not solved by BLP+AIP and not reducible to tractable finite-domain CSPs.
- H-symmetric polymorphisms of arbitrarily large arity are a sufficient tractability condition.

Reference:

Lorenzo Ciardo, Stanislav Zivny,
*CLAP: A New Algorithm for Promise CSPs*,
SIAM J. Comput. 52(1), 2023 / arXiv:2107.05018v4.

This is structurally relevant because it is a global LP/affine certificate rather than an explicit per-clause selector.

However the full signed-3SAT template has only projection polymorphisms, so no CLAP success claim is made here.

The exact task is to test the frozen three-sheet **representation** against the CLAP/consistency-reduction criteria rather than apply CLAP directly to the visible 3SAT template.

## 5. New exact gate

Freeze:

```text
R5_E8_6I
THREE_SHEET_CONSISTENCY_TO_AFFINE_GATE_V1
```

### Input

The frozen exact three-sheet threshold-two representation of arbitrary signed 3-CNF.

### Question

Does there exist one fixed constant k and one source-defined Datalog^union / k-consistency reduction which maps every frozen three-sheet instance, in polynomial time and polynomial output size, to a fixed polynomial-time affine/module/CLAP-compatible target while preserving SAT exactly?

### Required PASS contract

```text
EXACT YES/NO PRESERVATION
=
PROVED

FIXED k
=
INDEPENDENT OF INPUT SIZE

CONSTRUCTION
=
POLY(L)

INTERMEDIATE CONSISTENCY STATE
=
POLY(L)

TARGET SOLVE
=
POLY(L)

RECONSTRUCTION
=
POLY(L)

VERIFICATION
=
POLY(L)

NO EXPLICIT CLAUSE SELECTOR
=
PROVED

NO HIDDEN SAT SEARCH
=
PROVED
```

### First subgate

Because Dalmau-Oprsal characterize the arc-consistency fragment algebraically, test first:

```text
ARC_CONSISTENCY_REDUCTION
THREE_SHEET
->
AFFINE / XOR TARGET
```

using the source weak-minion criterion.

Only if this passes should larger fixed k be considered.

If it fails, preserve the exact algebraic obstruction as a barrier receipt.

## 6. Anti-loop ledger

```text
EXPLICIT SELECTOR
=
BLOCKED AS NP-COMPLETE REPACKAGING

DIRECT 1-INDEPENDENCE
=
BLOCKED

FIXED LOCAL PP -> TRACTABLE EDGE/SIGGERS
=
BLOCKED

e_p AS EXTRA DECISION POWER
=
REPACKAGING / NO NEW POWER

PGP / SWITCHABILITY
ON FULL 3SAT PROJECTION ALGEBRA
=
BLOCKED BY EGP

CONSISTENCY REDUCTION / DATALOG^union
=
OPEN <<< NEW DONOR CLASS

CLAP REPRESENTATION TEST
=
OPEN AS SECONDARY DONOR
```

## 7. Ceiling

```text
D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT_PROVED

GLOBAL_SHEET_COHERENCE
=
OPEN

NEXT EXACT TEST
=
ARC_CONSISTENCY REDUCTION
THREE_SHEET -> AFFINE/XOR
```
