# R5 E9 — Hostile donor audit: PolaritySAT 2026 P=NP claim

Date: 2026-09-28

Status: `DONOR_REJECTED_BY_EXPLICIT_FORCED_ASSIGNMENT_COUNTEREXAMPLE__NO_D1_PROMOTION`

Scientific ceiling:

```text
THE EXTERNAL REPOSITORY CLAIMS A DETERMINISTIC O(n^2 m) SAT DECIDER AND P=NP.
JANUS DOES NOT IMPORT THAT CLAIM.
THE PUBLISHED FORCED-ASSIGNMENT LEMMA IS FALSE BY AN EXPLICIT REDUCED CNF.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

External donor inspected:

- `yinhao2026/P-NP--Complete-Archive`, public July 2026 release.
- The public proof states that a `globally unified` variable may be assigned according to its unified polarity without destroying satisfiability.

## 1. Frozen counterexample

Use variables ordered

```text
u > v > w > a > z
```

and the CNF

```text
(u OR v)
AND (NOT v OR w)
AND (NOT w OR a)
AND (NOT w OR NOT a)
AND (NOT u OR z)
AND (NOT z OR u).
```

This formula has:

```text
no unit clauses,
no pure variables,
no tautological clauses.
```

Its satisfying assignments are exactly

```text
(u,v,w,a,z) = (1,0,0,0,1)
(u,v,w,a,z) = (1,0,0,1,1).
```

In particular every model has `v=0`.

## 2. `v` is globally unified positive under the donor definition

The only variable greater than `v` is `u`.
The only clause containing both `u` and `v` is

```text
(u OR v),
```

where `v` occurs positively.

Therefore, under the donor's stated pairwise definition, `v` is globally unified with polarity `+`.

## 3. Assigning the claimed forced polarity destroys satisfiability

Set `v=1`.
Then

```text
(NOT v OR w)
```

forces `w=1`.
The two clauses

```text
(NOT w OR a)
(NOT w OR NOT a)
```

then force simultaneously

```text
a=1
a=0,
```

which is impossible.

Hence

```text
F is SAT,
v is globally unified positive,
F[v:=1] is UNSAT.
```

So the claimed forced-assignment lemma is false.

## 4. Consequence

The donor's completeness theorem depends on the false implication

```text
globally unified polarity
=> satisfiability-preserving forced assignment.
```

Therefore its claimed deterministic polynomial SAT algorithm and P=NP conclusion cannot be imported into JANUS.

This rejection is unconditional and does not assume `P != NP`.

## 5. Additional definitional warning

The public proof also treats a maximum variable as vacuously globally unified because there is no larger variable. Under the stated requirement of a **unique** polarity `p`, this is not automatic: when there are no relevant pairs, both polarities satisfy the universal condition, so uniqueness does not follow. This is a separate issue, but the counterexample above already kills the forced-assignment theorem without relying on it.

## 6. Anti-loop rule

Freeze:

```text
FORBIDDEN_DONOR_ROUTE
= POLARITYSAT_2026_GLOBAL_UNIFIED_FORCED_ASSIGNMENT
```

Do not re-import the claim without a genuinely repaired theorem that survives the frozen counterexample.

## 7. Current JANUS frontier unchanged

```text
PRIMARY
= R5_E9_HIGH_GIRTH_SAFE_NONLOCAL_GLOBAL_PIVOT_GATE_V1

TARGET
= exact deterministic polynomial cross-layer contraction for arbitrary signed 3CNF

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
