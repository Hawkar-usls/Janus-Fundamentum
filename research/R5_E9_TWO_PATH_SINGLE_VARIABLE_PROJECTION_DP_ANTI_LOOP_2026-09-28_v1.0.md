# R5 E9 — Two-Path Single-Variable Projection = Davis–Putnam Anti-Loop

Date: 2026-09-28

Status:
`JANUS_SOURCE_BOUND_EXACT_ANTI_LOOP_CLASSIFICATION__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_PATH_XOR_AND_OVERLAY_NORMAL_FORM_2026-09-23_v1.0.md`
- `research/R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION_2026-09-23_v1.0.md`

Checker:
- `experiments/r5_e9_two_path_single_variable_projection_dp_anti_loop.py`

Scientific firewall:

```text
THIS IDENTIFIES THE EXACT SEMANTIC PROJECTION OF ONE COMPLETE VARIABLE PATH.
THE PROJECTION IS THE CLASSICAL DAVIS–PUTNAM ELIMINATION RULE.
THIS IS AN ANTI-LOOP CLASSIFICATION, NOT A NOVEL SAT ALGORITHM.
IT DOES NOT GIVE A UNIVERSAL POLYNOMIAL ELIMINATION ORDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Why this matters for the current primary frontier

The exact two-path XOR/AND overlay represents arbitrary signed 3CNF with:

- one XOR2 coherence path for the occurrences of each original variable;
- one private two-AND product path for each clause;
- all hardness living in the cross-layer overlay.

A tempting `GLOBAL_PIVOT` proposal is to eliminate one entire coherence path at once and replace its interaction with the product layer by an exact boundary relation.

This note classifies that move completely.

## 2. Collapse the coherence path back to one Boolean variable

Let the original variable be `x`.  Exact XOR-path coherence reconstructs one unique Boolean value `x` from all of its signed occurrences.  After substituting those occurrence values into the adjacent clause gadgets, write the surrounding CNF as

```text
F(x,Y)
=
C(Y)
AND
AND_{i=1..p} (x OR P_i(Y))
AND
AND_{j=1..q} (NOT x OR N_j(Y)),
```

where `C` contains no occurrence of `x`, and `P_i,N_j` are the remaining disjunctions of the clauses touching the variable path.

For the initial 3CNF encoding every `P_i,N_j` has size at most two.  After previous exact eliminations they may be longer; the theorem below is independent of their arity.

## 3. Exact projection theorem

Conditioning on `x` gives

```text
F[x=0]
=
C(Y) AND AND_i P_i(Y),
```

and

```text
F[x=1]
=
C(Y) AND AND_j N_j(Y).
```

Therefore

```text
exists x F(x,Y)
iff
C(Y)
AND
(
  (AND_i P_i(Y))
  OR
  (AND_j N_j(Y))
).
```

Distributivity gives the exact CNF identity

\[
\boxed{
\exists x\,F(x,Y)
\equiv
C(Y)\land
\bigwedge_{i=1}^{p}\bigwedge_{j=1}^{q}
(P_i(Y)\lor N_j(Y)).
}
\]

Each clause `P_i OR N_j` is exactly the resolvent of

```text
(x OR P_i)
```

and

```text
(NOT x OR N_j)
```

on `x`.

### Theorem SVP-1

Exact existential projection of one complete original-variable coherence path in `TWO_PATH_XOR_AND_OVERLAY_CSP`, while retaining the surrounding literal boundary, is exactly classical Davis–Putnam variable elimination:

1. delete all clauses containing `x` or `NOT x`;
2. add all non-tautological cross-polarity resolvents;
3. canonically delete duplicate/subsumed clauses if desired.

The XOR-path and product-path presentation does not create a stronger one-variable quotient.

## 4. Polynomial witness reconstruction

The projection is search-preserving, not only decision-preserving.

Given an assignment `y` satisfying the projected formula:

- if `q=0`, choose `x=1`;
- if `p=0`, choose `x=0`;
- otherwise, if every `P_i(y)=1`, choose `x=0`;
- otherwise choose some `i*` with `P_{i*}(y)=0`.  Every resolvent
  `P_{i*} OR N_j` then forces `N_j(y)=1` for every `j`, so choose `x=1`.

Thus `x` is reconstructed in polynomial time and the original XOR occurrence path and private clause-product variables are then reconstructed by the parent exact overlay maps.

Hence this single-path projection satisfies SOUND / COMPLETE / RECONSTRUCT exactly.  Its universal obstruction is representation growth under repeated elimination, not semantic correctness.

## 5. Exact low-current-degree preprocessing island

Let

```text
d = p+q
```

be the current number of clauses containing the variable.

Davis–Putnam removes `d` clauses and creates at most

```text
p*q
```

resolvents before tautology/duplicate/subsumption cleanup.

If both polarities occur and `d<=3`, then

```text
p*q <= d-1.
```

If only one polarity occurs, the variable is pure and no resolvent is required.

Therefore:

### Theorem SVP-2

Eliminating any current variable of clause-occurrence degree at most three by exact single-path projection strictly decreases the clause count by at least one.

A repeated preprocessing phase that applies only while such a variable exists has polynomial total work under canonical clause representation:

- at most the initial number of successful clause-count decreases;
- constant many resolvent pairs per eliminated low-degree variable;
- every canonical clause contains at most one literal of each live variable.

This is a genuine polynomial preprocessing island, but it is not universal: the residual may reach minimum current occurrence degree at least four.

## 6. Sharp local boundary for the clause-count potential

The strict clause-count argument stops immediately above degree three.

For example:

```text
d=4,
p=q=2
=>
p*q=4=d.
```

So even before considering duplicates, no strict clause-count drop is forced.

For

```text
d=6,
p=q=3,
```

the raw replacement count is nine resolvents for six removed clauses.

This does not prove superpolynomial growth for every ordering.  It only proves that the low-degree monotone potential does not extend automatically to the hard residual.

## 7. Anti-loop consequence for GLOBAL_PIVOT

The current primary frontier requires a genuinely cross-layer exact contraction.

SVP-1 closes the following pseudo-progress:

```text
TAKE ONE ORIGINAL VARIABLE PATH
-> EXISTENTIALLY PROJECT ITS OCCURRENCES / PRODUCT CONTACTS
-> CALL THE RESULT A NEW CROSS-LAYER QUOTIENT
```

as false novelty.  If the boundary is retained exactly, the operation is Davis–Putnam elimination in overlay coordinates.

Therefore any genuinely new primary `GLOBAL_PIVOT` must do more than one complete variable path in isolation.  In particular it must exploit a joint object such as:

- at least two original variable paths coupled through clause-product paths;
- an alternating cross-layer circuit / cycle;
- a multi-path syndrome relation whose exact quotient is smaller than the corresponding sequence of ordinary single-variable eliminations;
- a witness-dominance contraction that deletes a branch rather than merely materializing all resolvents.

The next smallest admissible block is thus a nonlocal two-variable / alternating overlay block, not a single variable star.

## 8. Prior-art boundary

The semantic rule identified here is classical Davis–Putnam variable elimination / resolution.  JANUS claims no novelty for the elimination identity.

The JANUS-specific role of this note is only to bind that classical operation exactly to the `TWO_PATH_XOR_AND_OVERLAY_CSP` representation and freeze it as an anti-loop rule for the current primary frontier.

Known tractable elimination-order classes such as DP-simplicial formulas do not by themselves supply a universal ordering for arbitrary 3CNF; no such theorem is assumed here.

## 9. Updated scoped target

Freeze candidate subgate:

```text
R5_E9_TWO_PATH_MULTI_VARIABLE_ALTERNATING_OVERLAY_PIVOT_GATE_V1
```

Input:

```text
exact two-path XOR/AND overlay,
all single-variable-path projections classified as ordinary DP,
low-current-degree <=3 variables stripped whenever available.
```

Required progress:

1. find a polynomially discoverable nonempty multi-path block or alternating cross-layer circuit;
2. replace it by an exact polynomial-size quotient / dominance contraction;
3. reconstruct a source witness in polynomial time;
4. strictly decrease a polynomially bounded joint cross-layer potential;
5. prove universal coverage of every nonterminal residual or route the remainder to another proved polynomial terminal.

Forbidden:

- rename a sequence of ordinary DP eliminations as a new quotient;
- introduce a fresh selector for the eliminated choices;
- rely only on affine-layer or product-layer width separately;
- hide exponential boundary tables in a compactness claim;
- promote E8_D1 without a universal polynomial coverage theorem.

## 10. Ceiling

```text
ONE COMPLETE VARIABLE-PATH PROJECTION
= EXACT DAVIS–PUTNAM ELIMINATION

SOUND / COMPLETE / WITNESS RECONSTRUCTION
= PROVED

CURRENT OCCURRENCE DEGREE <=3
= POLYNOMIAL STRICT CLAUSE-COUNT PREPROCESSING

SINGLE-PATH PROJECTION AS NEW GLOBAL PIVOT
= CLOSED / ANTI-LOOP

MULTI-PATH / ALTERNATING CROSS-LAYER PIVOT
= OPEN <<< PRIMARY MICRO-GAP

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
