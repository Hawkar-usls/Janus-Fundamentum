# R5 E8 — Frozen Structural Greedy Projector Postmortem

Date: 2026-09-22

Authority: `POSTMORTEM__ANTI_DUPLICATION_BOUND__NO_SUCCESSOR_AUTHORIZATION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Counterfamily authority:

- `research/R5_B1B1C5B2B2_E8_CYCLIC_POWER_OF_TWO_COUNTERFAMILY_RESULT_2026-09-22_v1.0.json`
- `research/R5_B1B1C5B2B2_E8_FROZEN_GREEDY_COUNTERFAMILY_SECOND_PASS_AUDIT_2026-09-22_v1.0.md`

## Verdict

```text
EXACT FROZEN STRUCTURAL-GREEDY PROJECTOR
=
REJECTED AS D1 CANDIDATE

P_VS_NP
=
OPEN
```

## 1. What failed

The failure is not semantic hardness of the cyclic family.

Each selector block has the form

```text
G_i
=
(x_i OR A_i)
AND
(NOT x_i OR B_i).
```

Exact existential elimination gives

```text
exists x_i G_i
iff
A_i OR B_i.
```

For the cyclic family, `A_i` and `B_i` are two-literal clauses, so `A_i OR B_i` is one clause of width at most four.

Therefore the projected Boolean function remains locally compact.

The frozen structural-only projector instead materializes

```text
G_i[x_i=0]
OR
G_i[x_i=1]
```

inside the existing AIG and permits only:

```text
CONST
IDEMPOTENCE
COMPLEMENT
COMMUTATIVE structural interning.
```

Those rules cannot discover the compact clause `A_i OR B_i`.

The arbitrary-size counterfamily proves that this missing compaction is enough to force

```text
Peak(F_m)
>=
2^(m/2).
```

## 2. Exact missing capability

The missing capability is:

```text
SEMANTICALLY SOUND LOCAL
EXISTENTIAL-COMPACTION REWRITE

that recognizes / constructs
a compact representation of

exists x P(x,Y)

without materializing the full
Shannon branch DAG.
```

On this family a sufficient rewrite is simply the classic resolvent/projection identity

```text
(x OR A)
AND
(NOT x OR B)

-- exists x -->

A OR B.
```

This is not a new E8 mechanism.

It is a special case of classical Davis-Putnam variable elimination / resolution, already source-audited in E8.

## 3. Why the successor is not “add resolution”

The reference DP route is already closed as a universal polynomial candidate in the current E8 lineage.

Authority:

`research/R5_B1B1C5B2B2_E8_D1_REFERENCE_ELIMINATION_ADMISSION_AUDIT_2026-09-21_v1.0.md`

Already established:

```text
REF-SOUND
=
PASS

REF-COMPLETE
=
PASS

REF-TERMINATES
=
PASS

REF-POLY
=
FALSIFIED
for fixed-order explicit flat-CNF representation.
```

The parity projection control gives exponential flat-CNF growth.

Therefore:

```text
STRUCTURAL AIG SHANNON
fails on the cyclic family

BUT

FLAT-CNF DP / RESOLUTION
has a different known blow-up family.
```

Switching from one representation failure to the other is not a D1 advance.

## 4. Internal anti-duplication bindings

Before any successor is proposed, check:

### C023 / C023R

Exact residual/cache DAG and serial-diamond multiplicity are already represented internally.

Do not rename stronger caching as a new solution.

### Factorized payload theorem

If a proposed successor avoids Cartesian growth only because exact cross-independence holds, it belongs to the already-sealed factorized-portfolio route.

### Guarded bounded-output elimination

If polynomiality holds only while each elimination output stays below a polynomial guard, the correct general verdict remains `OPEN` once the guard fails.

### ER / BVA selector inventory

Auxiliary-variable compression and extension discovery are already separated into:

```text
representation existence
!=
representation discovery
!=
global event-count / terminal proof.
```

Do not reopen “invent a helpful extension” without a polynomial provenance and global progress theorem.

### SynNNF / knowledge compilation

Restricted representations may support polynomial projection/synthesis after successful compilation.

The unresolved universal issue is still the construction/size guarantee from arbitrary CNF.

## 5. Representation lesson from the counterfamily

The cyclic family gives a clean separation:

```text
SEMANTIC PROJECTION SIZE
=
LINEAR / COMPACT ON SELECTOR ELIMINATION

FROZEN STRUCTURAL AIG SIZE
=
SUPERPOLYNOMIAL PEAK
```

Hence:

```text
small exact projected formula exists

does not imply

this representation/compiler
finds or preserves it cheaply.
```

This is the E8 analogue of the earlier internal firewall:

```text
semantic irrelevance
!=
syntactic disappearance.
```

## 6. What a genuine successor would have to add

A successor cannot merely combine known operations informally.

It must state an exact representation and constructor for which all of the following are charged to original input length `L`:

```text
1. detect when compact semantic elimination is available;

2. construct the compact replacement in poly(L);

3. avoid known flat-CNF DP blow-up controls;

4. avoid structural Shannon duplication controls;

5. keep auxiliary definitions functionally controlled;

6. keep aggregate state/history poly(L);

7. preserve exact SAT/UNSAT semantics;

8. retain polynomial reconstruction;

9. provide an arbitrary-input global progress/terminal theorem.
```

Without all nine, the successor is not D1.

## 7. Current successor decision

```text
NEW SUCCESSOR ALGORITHM
=
NOT AUTHORIZED YET
```

Reason:

The obvious repairs are already known mechanisms with already-audited limitations:

```text
resolution / DP
ER / BVA
semantic sweeping
knowledge compilation
factorization.
```

The next legitimate step is a source/history synthesis asking:

```text
Is there a previously uncombined
proof-carrying representation invariant
that simultaneously avoids

the cyclic structural-AIG blow-up

and

the parity / flat-CNF elimination blow-up

without hiding work in
semantic-equivalence or extension discovery?
```

This must be answered before a successor gate is opened.

## Claim ceiling

```text
FROZEN GREEDY FAILURE CAUSE
=
IDENTIFIED

OBVIOUS LOCAL REPAIR
=
KNOWN PRIOR ART

SUCCESSOR
=
LOCKED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
