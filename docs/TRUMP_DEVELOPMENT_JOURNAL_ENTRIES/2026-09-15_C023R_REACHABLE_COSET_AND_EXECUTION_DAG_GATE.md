# TRUMP Journal — C023R reachable-coset / execution-DAG theorem gate

Date: 2026-09-15  
Authority: `HQ_SYMBOLIC_RESEARCH__NO_SCIENTIFIC_PROMOTION`

## Branch

`research/trump-c023r-reachable-coset-theorem-2026-09-15`

## Starting point

The revealed C023R diagnostic had already established exact unfolding identities on MAJ3-K4 and isolated the candidate cache-fiber transfer:

`if max residual occurrence multiplicity is 2^{o(L)}, the C022 unfolded lower bound survives exact caching, conditional on the unchanged C022 proof-system premises.`

No finite multiplicity curve is used as asymptotic evidence.

## Preregistration v1.0

Commit:

`f440110051913efc19c310f50e3a52ab6b0f9dcd`

Primary theorem candidate:

`SUBEXPONENTIAL_REACHABLE_COSET_FIBER`.

Decisive falsifier:

an infinite subsequence with reachable byte-identical cache fibers of size `2^{Omega(L)}`.

## Pre-run self-correction

Source review of historical `Policy-0A / JANUS-FC_local` found that child inputs inherit clauses produced by deterministic local Resolution. Therefore a descendant cache key is not generally only a restricted source truth-table CNF.

The earlier intermediate source-scope recovery claim was explicitly retracted before any new theorem run.

Correction commit:

`b5c763815c6bc1558b6582ad89d802e4b9329261`

The correction defines `SOURCE_PROJECTION_AMBIGUITY` rather than silently assuming source provenance can be recovered from a key.

## Preregistration v1.1 repair

Commit:

`2034418894c3b55df7a7775986e710f6f8570d1a`

This is a legitimate pre-run repair: no new family data or asymptotic execution result was observed between v1.0 and v1.1.

New first obligation:

`P0_SOURCE_PROJECTION_AMBIGUITY`.

Historical H139 remains open; cache reuse is not ordinary Resolution DAG sharing.

## Exact execution-DAG reformulation

Commit:

`d8df2e7bd4218cd50f6849a21e6c97a956e79094`

For the directed labeled multigraph of unique historical cache keys:

`m(v) = number of directed root-to-v paths`.

Define ancestor merge surplus:

`mu(v)=sum_{u!=root}(indeg(u)-1)=|E|-|V|+1`.

Then exactly:

`m(v) <= 2^{mu(v)}`.

The global identity also gives:

`total cache-hit edges = |E(D)|-|V(D)|+1`.

The old revealed K4 values replay this identity exactly (`3314-2427+1=888`) but are not used asymptotically.

A decisive FAIL certificate can instead be given by `Omega(L)` compatible serial diamonds, which force `2^{Omega(L)}` root-to-target paths.

## Inherited-resolution fingerprint gate

Commit:

`edf07fb0228ac8d9f636127fe3bd26941dffbb40`

Exact dichotomy:

1. `NEAR_INJECTIVE_INHERITED_RESOLUTION_FINGERPRINT`: inherited clauses preserve all but `o(L)` independent history bits; or
2. `LINEAR_FINGERPRINT_FREE_SERIAL_DIAMONDS`: linearly many exact byte-identical merge diamonds survive, falsifying the cache-fiber transfer.

No heuristic signature is admissible.

## One-block 01/10 gate

Commit:

`dde83365034eca7006ffe46bef975deca7a78c80`

For two MAJ3 coordinates `a,b`, an exact two-step historical diamond exists iff the frozen transition operator satisfies:

- branch `a` at the common key;
- both first children exist;
- both next branch `b`;
- both second children exist; and
- exact byte-key equality

`T_1(T_0(K)) = T_0(T_1(K))`.

MAJ3 source equality `01 -> x` and `10 -> x` is insufficient by itself.

A symbolic counterfamily also proves the historical budgeted `resolution_trace` is not generally permutation-equivariant: numeric pivot order plus finite attempt/addition budgets can cause a variable renaming to change which resolvent prefix is retained.

Therefore gadget symmetry cannot be used as a shortcut to historical cache equality.

## Literature/model audit

The historical C023 registry already source-binds Formula Caching, pool resolution and clause-learning references. In particular the Formula Caching literature distinguishes basic exact cache reuse from reason-caching and shows stronger caching/reason systems can exceed ordinary Resolution strength.

Known Tseitin lower bounds for read-once branching programs / OBDD-style systems remain interesting but are not imported: an explicit simulation from historical `JANUS-FC_local` to the cited model is still missing.

## Current exact gate

`C023R_INHERITED_RESOLUTION_FINGERPRINT_VS_LINEAR_SERIAL_DIAMONDS`

Status:

`OPEN__SYMBOLIC_ONLY__NO_NEW_ASYMPTOTIC_RUN`

Next action:

derive, from frozen transition semantics, either a family-wide inherited-clause fingerprint retaining almost every MAJ3/cycle-space collision bit, or an exact symbolic template that composes into `Omega(L)` byte-identical serial diamonds on the frozen q=4 Morgenstern family.

## Claim ceiling

- C022 H135/H137 unchanged;
- C023 H139/H140 not promoted;
- no Policy-0A exponential lower bound yet;
- no SAT-in-P conclusion;
- `P_VS_NP = OPEN`;
- APMA global frontier unchanged.
