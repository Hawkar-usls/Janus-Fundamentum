# R5 E9 — Linear Exact-One Davis–Putnam Expansion-Charge Theorem

Date: 2026-09-27

Authority:
`JANUS_DERIVED_EXACT_COMBINATORIAL_THEOREM__SELECTOR_FRONTIER__NO_COMPLEXITY_CLAIM__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_linear_exact_one_dp_expansion_charge.py`

Parents:
- `R5_E9_WDR_SURVIVOR_CENSUS_AND_RESOLUTION_EXPANSION_CHARGE_2026-09-23_v1.0.md`
- `R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION_2026-09-23_v1.0.md`
- `R5_E9_WITNESS_DOMINANCE_EXISTENCE_COLLAPSE_AND_STRUCTURAL_TRANSFORMER_GATE_2026-09-23_v1.0.md`
- `R5_E9_PRESCRIBED_C10_POLYSIZE_2GROUP_COVER_THEOREM_2026-09-27_v1.0.md` (conditional downstream application only while that file remains a theorem candidate)

Global firewall:

```
D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT_PROVED
```

## 1. Setup

Let H be a linear 3-uniform hypergraph. Thus every hyperedge has three
vertices and two distinct hyperedges intersect in at most one vertex.

Encode every hyperedge

```
E={x,a,b}
```

by the standard monotone Exact-One / 1-in-3 CNF

```
(x OR a OR b)
AND (NOT x OR NOT a)
AND (NOT x OR NOT b)
AND (NOT a OR NOT b).
```

The four clauses are equivalent to saying exactly one variable of E is true.

Fix a variable x that belongs to exactly d hyperedges.

Following the existing WDR expansion-charge convention, let

```
P_x = { clauses containing x },
N_x = { clauses containing NOT x },
R_x = distinct non-tautological resolvents of P_x against N_x on x,
chi_F(x) = |R_x| - |P_x| - |N_x|.
```

## 2. Exact clause-count theorem

### Theorem EX1-DP-CHARGE

For every variable x of degree d in a linear 3-uniform Exact-One instance,

```
|P_x| = d,
|N_x| = 2d,
|R_x| = 2d(d-1),
```

and therefore

```
boxed: chi_F(x) = d(2d-5).
```

### Proof

For every x-incident hyperedge

```
E_i={x,a_i,b_i}
```

there is exactly one positive x-clause

```
C_i=(x OR a_i OR b_i),
```

so

```
|P_x|=d.
```

The same edge contributes exactly two negative x-clauses

```
D_i^a=(NOT x OR NOT a_i),
D_i^b=(NOT x OR NOT b_i).
```

Linearity prevents duplicate pairs {x,u} across different hyperedges, hence
all these clauses are distinct and

```
|N_x|=2d.
```

Resolve C_i against one of the two negative x-clauses from the same edge.
For example,

```
C_i resolve D_i^a
=
(a_i OR b_i OR NOT a_i),
```

which is tautological. Thus the two same-edge pairings for each i contribute
no member of R_x.

Now take different incident edges E_i and E_j, i != j. Resolving C_i against

```
(NOT x OR NOT u),  u in E_j-{x},
```

produces

```
(a_i OR b_i OR NOT u).
```

This is non-tautological: if u were a_i or b_i, then E_i and E_j would share
both x and u, contradicting linearity.

Every ordered pair i != j yields two such resolvents, one for each of the two
vertices u in E_j-{x}. They are all distinct. Indeed, the two positive
literals identify E_i, and the negative literal u identifies its unique
x-incident edge E_j by linearity.

Hence

```
|R_x| = d * 2(d-1) = 2d(d-1).
```

Therefore

```
chi_F(x)
= 2d(d-1) - d - 2d
= d(2d-5).
```

QED.

## 3. Exact literal-occurrence charge

The clauses removed by eliminating x contain

```
3d + 2*(2d) = 7d
```

literal occurrences.

Every surviving cross-edge resolvent has length three, so the new resolvents
contain

```
3 * 2d(d-1) = 6d(d-1)
```

literal occurrences.

Thus the exact local literal-occurrence change is

```
lambda_F(x)
= 6d(d-1)-7d
= d(6d-13).
```

## 4. Cubic consequence

For a cubic linear Exact-One instance, d=3 at every variable. Therefore

```
|P_x| = 3,
|N_x| = 6,
|R_x| = 12,
chi_F(x) = +3,
lambda_F(x) = +15.
```

So every variable initially fails the WDR R4 no-growth Davis–Putnam test:

```
chi_F(x) <= 0
```

is false for all x.

Equivalently, ordinary exact single-variable CNF projection must expand the
clause count by three at every possible first variable.

This is an exact local obstruction to that specific reduction rule. It is not
a SAT lower bound and does not rule out grouped elimination, witness repair,
non-CNF representations, algebraic methods, or another polynomial algorithm.

## 5. Why this hits the current JANUS family

A cubic bipartite incidence graph of girth at least 10 is automatically the
incidence graph of a linear 3-uniform 3-regular hypergraph: a pair of distinct
hyperedges sharing two variables would create an incidence 4-cycle.

Therefore any cubic girth-10 Exact-One cover produced by the current
prescribed-C10 cover theorem candidate lies in the d=3 case above.

Conditional on that cover theorem candidate surviving proof/governance review,
the assembled family has the exact initial invariant

```
FOR EVERY LIVE VARIABLE x:
    DP_CLAUSE_CHARGE(x) = +3
    DP_LITERAL_CHARGE(x) = +15
```

before any other preprocessing changes the representation.

This connects the construction branch directly to the older WDR survivor
frontier rather than creating a separate search lane.

## 6. Selector meaning

For one variable x, the exact Shannon/Davis–Putnam identity is

```
exists x F
=
C AND [ (AND_i A_i) OR (AND_j B_j) ].
```

Flattening both alternatives into CNF pays the Cartesian resolvent product.
The positive charge above measures that payment exactly on the linear
Exact-One family.

A sound structural selector / witness-repair contraction that certifies one
branch or one canonical ranked region as sufficient could avoid this product.

But the existing witness-dominance firewalls remain binding:

- arbitrary good-branch existence is not an algorithm;
- arbitrary witness-map existence collapses to semantic satisfiability;
- resolution-certified dominance cannot be the only universal currency due
  the known Resolution lower-bound barrier already recorded in this branch;
- synthesis, not merely verification, must be polynomial and oracle-free.

Thus the next genuine target is narrower than a generic “universal selector”:

```
NON_RESOLUTION_STRUCTURAL_SELECTOR / RANKED WITNESS TRANSFORMER
ON POSITIVE-CHARGE CUBIC LINEAR EXACT-ONE CORES
```

with strict potential drop and polynomial synthesis.

## 7. Finite regression

The checker uses the Fano plane as a finite cubic linear 3-uniform control:

```
123, 145, 167, 246, 257, 347, 356.
```

For all seven variables it verifies

```
(|P_x|, |N_x|, |R_x|, chi_F(x), lambda_F(x))
=
(3,6,12,3,15).
```

The finite regression checks implementation/accounting only; the arbitrary-d
statement is proved combinatorially above.

## 8. Literature anti-loop

The checked public literature confirms that monotone 1-in-3 SAT remains a
central hard CSP family, including current work on approximate 1-in-3 SAT.
The branch already contains the older WDR Davis–Putnam charge framework.

In the targeted search performed for this step, no source was found stating
the exact identity

```
chi_F(x)=d(2d-5)
```

for this standard linear Exact-One CNF encoding. This is not a novelty claim;
it records only that the exact off-the-shelf formula was not located in the
checked sources.

## 9. Scientific ceiling

```
LINEAR_EXACT_ONE_DP_CHARGE
=
EXACT_DERIVED_THEOREM

CUBIC_LINEAR_INITIAL_R4_CLOSURE
=
PROVED_FOR_THE_STANDARD_EXACT_ONE_CNF_ENCODING

PRESCRIBED_C10_COVER_APPLICATION
=
CONDITIONAL_ON_THE_EXISTING_THEOREM_CANDIDATE

UNIVERSAL_SELECTOR
=
OPEN

E8_D1
=
EMPTY

P_VS_NP
=
OPEN
```
