# C024 — Safe-Pivot Double-Count Candidate

Status: **PROOF_CANDIDATE / NOT YET ADMITTED**  
Direction: positive safe-pivot availability for the concrete descendant class behind the N=58 `25:25` obstruction.  
Global claim ceiling: `P_VS_NP = OPEN`.

## Scope

Let `F` be a non-tautological CNF over exactly 7 live variables with

- `m = 79` clauses,
- `L = 350` literal occurrences,
- minimum variable incidence degree `d_min = 50`.

Because every variable degree is at least 50 and the degree sum is 350,

```text
deg(v) = 50 for every one of the 7 live variables.
```

Hence eliminating any pivot leaves exactly

```text
c = 79 - 50 = 29
```

retained clauses.

No assumption is made that every variable has sign split `25:25`.

## Pairwise opposite-sign count

For two distinct clauses `A,B`, define

```text
t(A,B) = number of live variables whose literals occur with opposite signs in A and B.
```

For a pivot `v`, write

- `p_v` = number of clauses containing `+v`,
- `q_v` = number of clauses containing `-v`,
- `T_v` = number of `(+v parent, -v parent)` pairs whose resolvent on `v` is tautological because some other live variable remains with opposite signs.

Then `p_v q_v - T_v` counts the non-tautological parent pairs for pivot `v` before duplicate-resolvent collapse.

A fixed unordered clause pair `{A,B}` contributes to `p_v q_v` once for each variable where it has opposite signs.

- If `t(A,B)=0`, it contributes nothing.
- If `t(A,B)=1`, it contributes exactly one non-tautological pivot-parent incidence.
- If `t(A,B)>=2`, then resolving on any one of its opposite-sign variables leaves at least one other complementary literal pair, so every such resolvent is tautological. It contributes zero to `sum_v (p_v q_v - T_v)`.

Therefore the exact double-count identity is

```text
sum_v (p_v q_v - T_v)
= number of unordered clause pairs {A,B} with t(A,B)=1.
```

The right side is at most the total number of unordered pairs of 79 clauses:

```text
C(79,2) = 3081.
```

By averaging across 7 pivots, there exists a pivot `v*` such that

```text
p_v* q_v* - T_v* <= floor(3081 / 7) = 440.
```

## Raw-state bound for that pivot

The selected pivot has 29 retained clauses. It produces at most 440 non-tautological parent-pair resolvents before duplicate collapse. Hence the raw clause set has at most

```text
29 + 440 = 469
```

clauses.

After eliminating one of 7 live variables, every non-tautological resulting clause uses at most 6 live variables, hence has width at most 6.

Under the JANUS charged-unit convention

```text
state_units = 1 + number_of_clauses + sum_of_clause_widths,
```

we obtain the deliberately coarse bound

```text
raw_units
<= 1 + 469 + 6*469
= 3284.
```

For the N=58 cap,

```text
N^2 = 3364,
```

therefore

```text
3284 < 3364.
```

## Candidate conclusion

For every concrete CNF satisfying the stated `(n,m,L,d_min)=(7,79,350,50)` scope, **there exists at least one pivot whose raw ordinary-elimination state is below the N=58 cap**.

This is an existential safe-pivot statement. It does **not** prove that the previously chosen `25:25` pivot is safe, and it does not justify a selector until the theorem path specifies how the safe pivot is found without invalid search cost.

## Why this matters

The previous abstract obstruction treated one candidate action at a time. C024 changes the quantifier from

```text
this chosen pivot must LAND
```

to

```text
there exists a pivot that LANDs.
```

That is exactly the theorem-shaped content needed by the Minimum Certified Safe Selector / JUXTAPOSE availability route.

## Required audits before admission

1. Verify that `d=50` in the imported descendant state has the theorem-side meaning `minimum incidence degree`.
2. Verify that the concrete state has exactly 7 live variables, 79 distinct canonical clauses and 350 literal occurrences at the moment the cap is charged.
3. Verify that raw ordinary elimination charges the deduplicated non-tautological raw clause set and no larger pre-set multiset quantity.
4. Verify width <= 6 after pivot deletion under the exact representation.
5. Replay the argument through an independent finite pair-type checker.
6. Keep static realizability, forward reachability, selector complexity, global progress, and end-to-end polynomiality as separate gates.

## Claim ceiling

```text
C024_SAFE_PIVOT_DOUBLE_COUNT = PROOF_CANDIDATE_NOT_ADMITTED
C024_LOCAL_EXISTENTIAL_AVAILABILITY = CANDIDATE
POLYNOMIAL_SELECTOR = OPEN
POLYNOMIAL_PROGRESS = OPEN
UNBOUNDED_TOTALITY = OPEN
P_VS_NP = OPEN
```
