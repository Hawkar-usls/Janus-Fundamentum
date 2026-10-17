# R5 E9 — Cubic Linear Exact-One Matching-Lean Theorem

Date: 2026-09-27

Authority:
`JANUS_DERIVED_EXACT_COMBINATORIAL_THEOREM__MATCHING_AUTARKY_LANE_CLOSED__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_cubic_linear_exact_one_matching_lean.py`

Parents:
- `R5_E9_LINEAR_EXACT_ONE_PARTIAL_WDR_CLOSURE_2026-09-27_v1.0.md`
- `R5_E9_WDR_LEAN_NORMAL_FORM_SCHEDULER_CONTRACT_2026-09-23_v1.0.md`
- `R5_E9_AUTARKY_AS_WITNESS_DOMINANCE_DONOR_2026-09-23_v1.0.md`

External donor:
Oliver Kullmann, *Lean clause-sets: generalizations of minimally unsatisfiable
clause-sets*, Discrete Applied Mathematics 130 (2003), 209–249.

The source characterization used here is:

```
F is matching-lean
iff
for every proper sub-clause-set F' subset F:
    deficiency(F') < deficiency(F),
```

where for Boolean clause-sets

```
deficiency(F)=number_of_clauses(F)-number_of_variables(F).
```

Scientific firewall:

```
MATCHING-LEAN != GENERAL-AUTARKY-LEAN
MATCHING-LEAN != SAT HARDNESS
D1 = EMPTY
P_VS_NP = OPEN
```

## 1. Setup

Let H=(V,E) be a linear 3-uniform 3-regular hypergraph with

```
|V|=n.
```

Because H is simultaneously 3-uniform and 3-regular,

```
3|E| = 3|V|,
```

so

```
|E|=n.
```

Encode every hyperedge {x,a,b} by the standard monotone Exact-One CNF

```
(x OR a OR b)
AND (NOT x OR NOT a)
AND (NOT x OR NOT b)
AND (NOT a OR NOT b).
```

Call the resulting Boolean clause-set F_H.

Linearity guarantees that no negative pair clause is duplicated across two
hyperedges, and distinct hyperedges give distinct positive ternary clauses.
Therefore every hyperedge contributes four distinct clauses and

```
c(F_H)=4n.
```

Every hypergraph vertex is a CNF variable, so

```
n(F_H)=n
```

and hence

```
deficiency(F_H)=4n-n=3n.
```

## 2. Every variable has nine distinct clause incidences

Fix a variable x.

It lies in exactly three hyperedges.

Each incident hyperedge contributes:
- one positive ternary clause containing x;
- two negative binary clauses containing NOT x.

Thus x occurs in exactly

```
3*(1+2)=9
```

distinct clauses.

The clauses are distinct by linearity.

## 3. Proper sub-clause-sets lose deficiency

Take any proper sub-clause-set

```
F' proper-subset F_H.
```

Let

```
S = Var(F'),
T = V-S,
t = |T|.
```

### Case A: t=0

Then F' still uses all n variables. Since F' is proper, it contains at most
4n-1 clauses. Therefore

```
deficiency(F')
<= (4n-1)-n
= 3n-1
< 3n.
```

### Case B: t>=1

Every clause of F' avoids every variable of T. Let q(T) be the number of
clauses of F_H touching at least one variable of T. All q(T) clauses are absent
from F'.

The variables of T contribute exactly

```
9t
```

variable-clause incidences.

Any CNF clause in the standard Exact-One encoding has size at most three, so
one excluded clause contains at most three variables from T and therefore
accounts for at most three of these incidences.

Hence

```
q(T) >= 9t/3 = 3t.
```

Therefore

```
c(F') <= 4n-3t.
```

Since Var(F')=S,

```
n(F')=|S|=n-t.
```

Thus

```
deficiency(F')
<= (4n-3t)-(n-t)
= 3n-2t
< 3n
= deficiency(F_H).
```

So in every case

```
for every proper F' subset F_H:
    deficiency(F') < deficiency(F_H).
```

## 4. Matching-lean conclusion

By the standard matching-lean deficiency characterization,

```
boxed: F_H is matching-lean.
```

Equivalently, the standard CNF encoding admits no nontrivial matching autarky.

This is an arbitrary-size theorem for the whole cubic linear Exact-One class,
not a finite census result.

## 5. WDR consequence

The previous partial WDR-closure theorem already closes, at the initial state:

```
R0 unit / pure
R3 blocked-clause elimination
R4 no-growth Davis-Putnam elimination
R7 direct Horn / dual-Horn / Krom terminal tests.
```

The present theorem now additionally closes the matching-autarky part of

```
R2 matching/linear autarky modules.
```

Precisely:

```
R2_MATCHING_AUTARKY = CLOSED
R2_LINEAR_AUTARKY = NOT CLOSED BY THIS THEOREM
GENERAL_AUTARKY = NOT CLOSED BY THIS THEOREM
```

A satisfying total assignment is of course an autarky, so no satisfiable
family can be claimed general-autarky-lean merely from this result. The point
is specifically that the polynomial matching-autarky subsystem cannot make a
nontrivial move.

## 6. Selector frontier after this theorem

For cubic linear Exact-One cores, the live WDR selector lanes narrow to:

```
R1 exact equivalence / other certified substitutions
R2 linear-autarky and other non-matching polynomial autarky donors
R5 structural witness dominance
R6 ranked / substitution-redundancy macro rules
representation-changing polynomial carriers
```

The strongest presently targeted lane remains a deterministic polynomially
synthesizable non-Resolution witness transformer / ranked contraction with
strict Boolean-dimension decrease.

## 7. Finite checker

The executable checker validates the deficiency characterization on two small
cubic linear controls by enumerating all variable subsets S and taking the
maximum-deficiency sub-clause-set supported on S:

- the 7-variable Fano plane control;
- the 9-variable Z3 affine rows/columns/diagonal-class control.

For both controls, the full clause-set is the unique maximum-deficiency state
under this support enumeration, consistent with the theorem.

This finite check is not the proof; Sections 1–4 are the arbitrary-n proof.

## 8. Ceiling

```
CUBIC_LINEAR_EXACT_ONE_MATCHING_LEAN
=
PROVED

R2_MATCHING_AUTARKY
=
CLOSED ON THIS CLASS

R2_LINEAR_AUTARKY
=
OPEN

GENERAL_AUTARKY
=
OPEN

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
