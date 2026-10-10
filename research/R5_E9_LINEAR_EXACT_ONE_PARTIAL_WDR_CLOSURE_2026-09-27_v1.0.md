# R5 E9 — Linear Exact-One Partial WDR-Closure Theorem

Date: 2026-09-27

Authority:
`JANUS_DERIVED_EXACT_STRUCTURAL_THEOREM__PARTIAL_WDR_CLOSURE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_linear_exact_one_partial_wdr_closure.py`

Parents:
- `R5_E9_LINEAR_EXACT_ONE_DP_EXPANSION_CHARGE_2026-09-27_v1.0.md`
- `R5_E9_WDR_LEAN_NORMAL_FORM_SCHEDULER_CONTRACT_2026-09-23_v1.0.md`
- `R5_E9_WDR_SURVIVOR_CENSUS_AND_RESOLUTION_EXPANSION_CHARGE_2026-09-23_v1.0.md`

Scientific firewall:

```
THIS IS NOT FULL WDR CLOSURE.
R1 / R2 / R5 / R6 REMAIN OPEN.
D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let H be a linear 3-uniform hypergraph and encode every edge

```
{x,a,b}
```

as the standard monotone Exact-One CNF

```
(x OR a OR b)
AND (NOT x OR NOT a)
AND (NOT x OR NOT b)
AND (NOT a OR NOT b).
```

Assume every variable has hypergraph degree at least 2. The cubic application
has degree exactly 3.

## 2. R0: no initial units and no pure variables

Every clause has length two or three, so there are no unit clauses initially.

Every live variable x occurs positively in the one positive ternary clause of
each incident hyperedge. It also occurs negatively in two binary clauses per
incident hyperedge. Therefore every variable occurs in both polarities.

Hence initial

```
UNIT = NONE
PURE_VARIABLE = NONE.
```

There are also no tautological clauses. Linearity prevents duplicate positive
hyperedges and prevents a pair of variables from appearing in two distinct
hyperedges, so the standard pairwise-negative clauses are distinct as well.

## 3. R3: no blocked clause

Recall that a clause C is blocked by literal l in C when every clause D
containing the complementary literal -l has a tautological resolvent with C
on l.

### Positive ternary clauses

Take

```
C=(x OR a OR b)
```

from edge E_i={x,a,b}. Consider literal x.

Because degree(x)>=2, choose another x-incident edge

```
E_j={x,c,d},  j != i.
```

The Exact-One encoding contains

```
D=(NOT x OR NOT c).
```

Resolving C and D on x gives

```
(a OR b OR NOT c).
```

Linearity implies c is neither a nor b, otherwise E_i and E_j would share two
vertices. Hence this resolvent is non-tautological. So x does not block C.

The same argument applies to literals a and b, using another incident edge of
the corresponding variable.

Thus no positive ternary clause is blocked.

### Negative binary clauses

Take

```
C=(NOT x OR NOT a)
```

from E_i={x,a,b}. Consider literal NOT x.

Choose another x-incident edge

```
E_j={x,c,d}.
```

Its positive Exact-One clause is

```
D=(x OR c OR d).
```

The resolvent is

```
(NOT a OR c OR d).
```

Again linearity implies a is neither c nor d, so this resolvent is
non-tautological. Hence NOT x does not block C.

Using another a-incident edge proves that NOT a does not block C either.

Therefore no negative binary clause is blocked.

Combining both cases:

```
BCE_MOVE = NONE
```

for every linear Exact-One instance with minimum hypergraph degree at least 2.

## 4. R4: cubic instances have positive DP charge everywhere

The companion exact theorem proves

```
chi_F(x)=d(2d-5).
```

For cubic instances d=3, so

```
chi_F(x)=+3
```

for every live variable at the initial state.

The frozen WDR R4 rule admits ordinary exact Davis–Putnam variable elimination
only when its distinct non-tautological resolvent count does not exceed the
removed x-clause count, equivalently chi<=0.

Therefore on the cubic linear Exact-One initial state:

```
R4_NO_GROWTH_VE_MOVE = NONE.
```

## 5. R7 direct syntactic terminal classes do not apply

Every hyperedge contributes a positive 3-clause, so a nonempty instance is not
Krom and is not Horn.

Every hyperedge also contributes a negative binary clause with two negative
literals, so it is not dual-Horn.

Thus the immediate WDR v0.1 terminal tests

```
Horn / dual-Horn / Krom
```

do not classify a nonempty connected cubic linear Exact-One component.

This statement concerns these explicit syntactic terminal classes only; it does
not claim the instance is outside every polynomial SAT class.

## 6. What is now closed and what is still open

For the initial cubic linear Exact-One state, the following frozen WDR lanes are
structurally unavailable:

```
R0 unit/pure cleanup        CLOSED
R3 blocked-clause deletion CLOSED
R4 no-growth DP elimination CLOSED
R7 Horn/dual-Horn/Krom      CLOSED AS DIRECT TERMINAL TESTS
```

This theorem does NOT close:

```
R1 exact equivalence substitution
R2 matching/linear autarky synthesis
R5 signed structural dominance
R6 ranked / substitution-redundancy macro rules
other representation-changing polynomial carriers
```

Those are now the live selector frontier.

## 7. Finite selector-coverage control

The executable checker also uses the 3x3 affine-plane incidence family

```
rows + columns + one diagonal parallel class over Z_3
```

as a finite connected cubic linear satisfiable control.

It verifies:
- no units or pure variables initially;
- no blocked clauses;
- DP charge +3 at every variable;
- not Horn, dual-Horn, or Krom;
- ordinary failed-literal unit propagation returns UNKNOWN for both choices of
  every variable;
- offline exhaustive validation finds satisfying assignments with each variable
  taking both values across the model set.

The exhaustive model enumeration is explicitly

```
OFFLINE_FALSIFIER_ONLY
```

and is not an E8 algorithmic primitive.

## 8. Relation to universal selector

This structural closure gives the selector problem a concrete target.

A universal polynomial route cannot rely on the already-closed R0/R3/R4/R7
moves to make first progress on these cubic linear Exact-One states.

The next admissible successful step must come from one of the still-open
structural lanes, most notably a polynomially synthesizable non-Resolution
witness transformer / ranked contraction, or a representation change with
fully charged polynomial construction and reconstruction.

A finite stall does not prove P!=NP. A new rule firing on all tested instances
does not prove P=NP. Promotion requires an arbitrary-input coverage theorem.

## 9. Ceiling

```
LINEAR_EXACT_ONE_BCE_ABSENCE
=
PROVED FOR MIN DEGREE >= 2

CUBIC_LINEAR_INITIAL_DP_POSITIVE_CHARGE
=
PROVED

PARTIAL_WDR_CLOSURE
=
R0_R3_R4_R7_ONLY

FULL_WDR_CLOSURE
=
OPEN

UNIVERSAL_SELECTOR
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
