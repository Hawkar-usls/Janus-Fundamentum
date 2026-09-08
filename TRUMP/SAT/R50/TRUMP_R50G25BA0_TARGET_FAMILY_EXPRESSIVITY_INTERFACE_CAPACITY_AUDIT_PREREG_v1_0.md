# R50G25BA0 — TARGET FAMILY EXPRESSIVITY / INTERFACE CAPACITY AUDIT

Status: **FROZEN BEFORE BA0 IMPLEMENTATION/TESTING**

## Parent boundary

- sealed AZ source branch head at BA0 branch creation: `aa0a6114c4e9a437a0aa1b60f05df605e4f0cc3d`
- AZ preregistration: `85b5d55e563d919585fff16efb08bcb5ecea68f8`
- AZ result receipt: `6de0ca8283c2289d5a38f8eb1f37e1550b7fda93`
- AZ journal V43: `4539dd539d0d33cec8241524627b2c9a85cb298f`
- AZ meta final: `7e7ddf58a5358fbbc9ee1f104cf0b5a411f7a141`
- AZ restricted-family relation state: `69_GENERIC_FAMILY`

BA0 MUST NOT modify AZ, rerun the AY finite ladder, or broaden the AZ theorem.

## Frozen BA0 purpose

Audit the exact target class certified by AZ before any arbitrary-CNF reduction is attempted.

BA0 is NOT the arbitrary-CNF reduction theorem. BA1 is forbidden in this gate.

The audit asks:

1. Is there exactly one target formula `F_g` for each integer `g>=1`, or are there additional source-dependent degrees of freedom?
2. What is `SAT(F_g)` generically?
3. Where could source formula information live in any mapping `phi -> F_g` under the exact frozen target syntax?
4. What semantic information actually crosses an AZ MID boundary?
5. Does the current constant-width representation have enough semantic interface capacity for arbitrary source structure?
6. If not, what is the minimal explicit semantic parameter that a future extension would have to add without pretending that proof metadata is target semantics?

## Exact frozen target definition

Let `U` be the exact sealed Y unit inherited by AZ, with canonical CNF `(C,L,V)=(63,155,20)`, variable set

`[2,3,4,5,8,9,10,11,12,13,15,16,20,24,25,26,27,28,29,30]`

and maximum variable id 30.

For integer `g>=1`, define exactly:

- `U_j = shift(U,30*j)` for `j=0..g-1`;
- `B_j = (30+30*j, 32+30*j)` for `j=0..g-2`;
- `F_g = canonical_union(U_0,...,U_{g-1},B_0,...,B_{g-2})`.

No gadget choice, sign choice, clause choice, source-dependent payload, adaptive bridge, or certificate metadata is part of `F_g` unless BA0 discovers an already-sealed degree of freedom in the AZ definition. Discovery of such a degree of freedom must be recorded exactly; it may not be invented post hoc.

## BA0-Q1 — Parameter audit

Determine from the frozen generator/definition whether `g` is the only free parameter.

Required output:

- parameter list;
- whether the map `g -> F_g` is deterministic;
- whether two executions with the same `g` can yield semantically different target instances without violating the sealed definition.

## BA0-Q2 — Generic SAT status

Use the sealed unit fact that `U` has 60 satisfying assignments and realizes every endpoint pair

`(x_2,x_30) in {(0,0),(0,1),(1,0),(1,1)}`.

Prove or refute for all integers `g>=1`:

`SAT(F_g)`.

A proof must be constructive and uniform in g. It may use endpoint-pair extension induction, but not finite tested rungs as theorem evidence.

If `FOR_ALL_g SAT(F_g)` is proved, BA0 MUST freeze the immediate corollary:

No total SAT-preserving mapping from arbitrary CNF into the exact target set `{F_g:g>=1}` can cover any UNSAT source formula, because every target is SAT.

The smallest explicit decision obstruction should be minimized under ordinary CNF syntax. Prefer the empty-clause CNF `{{}}` if accepted by the repository's CNF semantics; otherwise use the smallest explicit contradictory-unit CNF `{(x),(-x)}`.

This obstruction refutes only arbitrary decision expressivity of the exact target family, never AZ.

## BA0-Q3 — Source-information audit

For a hypothetical mapping `R(phi)=F_g`, enumerate every semantic/syntactic channel available in the exact target:

- integer `g` / total chain length;
- fixed shifted copies of `U`;
- fixed positive binary bridges;
- no other target-semantic fields unless found in the sealed definition.

Certificate-only metadata is explicitly excluded from target semantics:

`PROOF_METADATA != TARGET_SEMANTICS`.

If source information can only affect `g`, quantify the number of target choices available under an output-size bound `|F_g|<=p(|phi|)` and distinguish syntactic information capacity from SAT-decision capacity.

## BA0-Q4 — Exact MID semantic interface

Do not equate AZ's internal induced-width bound `w<=13` with the final inter-block semantic interface without checking the actual MID certificate.

Recompute the frozen MID projection. Let its surviving boundary variable be `q` and its residual Boolean relation be

`M(q) in {0,1}`.

Define two prefix behaviours as interface-distinguishable iff they induce different residual Boolean functions on the retained boundary variables.

Let

`N_boundary = number of pairwise distinct residual Boolean functions exposed by the CURRENT frozen MID template across one chain cut`.

Required:

- exact surviving scope;
- exact truth table;
- exact `N_boundary` for the frozen representation;
- comparison to the loose valuation bound `2^w` with `w<=13`;
- no claim that `2^13` distinct semantic behaviours are available merely because an internal bucket can have width 13.

If MID is the full unary relation `{q=0,q=1}`, check whether it is semantically the constant-TRUE function and therefore transmits zero constraint bits from the eliminated prefix.

## BA0-Q4 adversarial source-state witness

Instantiate a concrete source residual-family requiring more distinct cut behaviours than the exact MID exposes.

Preferred minimal witness over one boundary Boolean `x`:

- `P_+(x) = x`;
- `P_-(x) = not x`.

These are two distinct residual Boolean functions. If current MID exposes only one residual function, freeze this as an interface-capacity obstruction.

Optionally record the full one-bit function family `{FALSE, x, not x, TRUE}` as a four-state reference, but do not substitute it for the smallest witness.

## BA0-Q5 — Constant-width classification

Classify the CURRENT representation as exactly one of:

A. sufficient because a proved compression invariant identifies all source residual behaviours needed for arbitrary CNF;
B. insufficient for a concrete source family under the current representation contract;
C. open.

A constant width number alone is neither success nor failure. The proof must identify the actual semantic interface and the information that cannot cross it.

## BA0-Q6 — Minimal extension audit

If exact `F_g` is insufficient, preserve AZ and specify only the smallest semantic extension candidate needed to make source dependence explicit.

The audit may propose a contract `F_{g,sigma}` but MUST NOT claim arbitrary-CNF coverage unless separately proved.

Any proposed `sigma` must:

1. be part of target semantics, not only a certificate;
2. have a distinguished neutral value `sigma_0` with `F_{g,sigma_0}=F_g` exactly;
3. be explicitly serialized with polynomial size in the source size for any future intended mapping;
4. be constructible without a SAT oracle or hindsight;
5. have controlled independently replayable semantics;
6. state how SAT-model reconstruction would have to return to the original source;
7. state induced separator-width consequences rather than hiding them;
8. expose certificate-size and total-time obligations;
9. not assume that arbitrary constraint information compresses to constant width.

The preferred minimal *interface* extension candidate, if needed, is a source-dependent semantic boundary relation `sigma_j` on an explicitly named separator set `B_j`. The neutral payload is the full relation. This is only a representation contract; whether arbitrary CNF admits a polynomial construction with polynomial solver complexity remains OPEN.

## Frozen falsifiers / outcomes

BA0-A `EXACT_F_g_HAS_SUFFICIENT_EXPRESSIVITY` requires a proof that the exact target can preserve arbitrary SAT decision information under the existing semantics.

BA0-B `EXACT_F_g_EXPRESSIVITY_BLOCKED` requires a generic target limitation plus a smallest explicit source obstruction.

BA0-C `TARGET_REQUIRES_PARAMETERIZED_EXTENSION` requires an exact `F_{g,sigma}` representation contract; it does not itself prove arbitrary-CNF reducibility.

BA0-D `OPEN` is used if the exact semantic capacity cannot be resolved.

If Q2 proves `FOR_ALL_g SAT(F_g)`, BA0-A is impossible for SAT-preserving arbitrary-CNF coverage of both SAT and UNSAT instances. BA0 should normally classify BA0-B unless a stronger reason requires BA0-D. A proposed future `F_{g,sigma}` contract may be recorded inside BA0-B as a necessary extension candidate without promoting BA0 to an arbitrary-reduction theorem.

## Firewalls

- `P_VS_NP = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `TRUMP_finished = false`
- `AZ_RESTRICTED_FAMILY_69_GENERIC_RELATION_CERTIFIED` remains unchanged
- `FOR_ALL_g SAT(F_g)` if proved is a limitation of target expressivity, not a solver failure
- `BOUNDARY_WIDTH != SEMANTIC_CAPACITY` unless the exact relation proves equality
- `CERTIFICATE_METADATA != INSTANCE_SEMANTICS`
- `BA0 != BA1`
- no arbitrary-CNF theorem is started here
