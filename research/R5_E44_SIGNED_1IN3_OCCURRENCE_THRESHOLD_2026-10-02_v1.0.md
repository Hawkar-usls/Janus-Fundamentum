# R5 E44 — Signed 1-in-3 Occurrence Threshold

Date: 2026-10-02

Status:
`EXACT_OCCURRENCE_TWO_FFACTOR_TERMINAL__OCCURRENCE_THREE_ALREADY_NP_COMPLETE__E42_OCCURRENCE_BACKDOOR`

Scientific ceiling:

```text
AFTER R5 E43, EVERY FULLY PEELED THREE-SPARSE LINEAR BOOLEAN INSTANCE
REDUCES LOCALLY TO SIGNED 1-IN-3 CONSTRAINTS.

INSIDE THAT CANONICAL LANGUAGE THERE IS A SHARP OCCURRENCE BOUNDARY:

  EVERY VARIABLE OCCURS IN EXACTLY TWO CONSTRAINTS
      -> SIGNED-GRAPH / f-FACTOR -> POLYNOMIAL;

  EVERY VARIABLE OCCURS IN EXACTLY THREE CONSTRAINTS
      -> THE ALL-POSITIVE SQUARE+CUBIC+LINEAR SUBCLASS IS ALREADY
         NP-COMPLETE BY R5 E12.

MORE GENERALLY, IF ONLY t VARIABLES FAIL THE OCCURRENCE-TWO CONDITION,
R5 E42 GIVES O(2^t poly(n)).

P_VS_NP = OPEN.
```

## 1. Signed 1-in-3 normal form

A signed 1-in-3 constraint is

```text
ell_1(x_i)+ell_2(x_j)+ell_3(x_k)=1,
```

where each literal is either

```text
ell(x)=x
```

or

```text
ell(x)=1-x.
```

Let `n^-_r` be the number of negative literals in row `r`. Move the constants to
the right-hand side. The row becomes

```text
sum_v sigma_(r,v) x_v = 1-n^-_r,
```

with

```text
sigma_(r,v) in {+1,-1}.
```

Thus the complete signed 1-in-3 instance is an integer system

```text
S x = h,
x in {0,1}^n,
```

whose nonzero entries are signs.

## 2. Occurrence exactly two gives a signed graph

Assume every variable occurs in exactly two signed 1-in-3 constraints.

Then every column of `S` has exactly two nonzero entries, each in `{+1,-1}`.

Interpret rows as vertices and variables as signed edges. The two signs in a column
are the endpoint signs of that edge.

Therefore `S` is exactly a signed-graphic two-endpoint representation of the class
solved in R5 E37.

R5 E37 applies to arbitrary integral RHS, so the specific vector

```text
h_r=1-n^-_r
```

is certainly allowed.

Hence:

### Theorem OCC2-SIGNED-1IN3

```text
boxed:
Signed 1-in-3 with every variable occurring exactly twice is solvable in
deterministic polynomial time by the R5 E37 f-factor reduction.
```

SAT witnesses and UNSAT factor obstructions are reconstructed exactly as in E37.

## 3. Occurrence three already contains the hard carrier

R5 E12 proves NP-completeness for the all-positive square+cubic+linear class

```text
x_i+x_j+x_k=1,
```

with every row containing exactly three variables and every variable occurring in
exactly three rows.

This is a special case of signed 1-in-3 in which all literal signs are positive.

Therefore:

```text
boxed:
The occurrence-three signed 1-in-3 class is NP-complete in general.
```

No additional sign complexity is needed for hardness.

Thus the regular occurrence threshold is sharp:

```text
2-regular variables -> P,
3-regular variables -> NP-complete in general.
```

## 4. Occurrence backdoor

Now allow arbitrary occurrences, but suppose an explicit set `E` of `t` variables
contains every column whose support is not exactly two.

Delete/fix those variables. The remaining matrix `S_G` has exactly two signed
nonzeros in every column, regardless of the row degrees that remain after fixing.

For a branch assignment `a in {0,1}^E`, the residual RHS is

```text
h_a = h-S_E a.
```

R5 E37 solves

```text
S_G x_G=h_a
```

for arbitrary integral `h_a`.

Therefore R5 E42 gives immediately:

```text
boxed:
T=O(2^t poly(n)),
```

where `t` is the number of non-occurrence-two variables in the displayed signed
1-in-3 representation.

Consequences:

```text
t=O(1)     -> polynomial,
t=O(log n) -> polynomial.
```

## 5. Why this is a post-E43 statement

Before E43, arbitrary three-variable linear rows could have heterogeneous rational
coefficients. E43 proves that every such asymmetric row has at most two Boolean
states and is polynomially eliminable.

So the local irreducible language is signed 1-in-3. E44 then identifies the next
global combinatorial boundary inside that language:

```text
constraint arity three is not enough for hardness;
variable occurrence three is also necessary for the frozen E12 hard carrier.
```

The E37 matching/factor machinery closes the entire exactly-two occurrence sector.

## 6. Canonical cubic hard core

Combining E40, E43 and E44, a fully reduced survivor of the frozen NP-complete route
can be normalized to the regime

```text
three literals per active constraint,
three active occurrences per hard variable,
signed Exact-One local relations,
no low-degree row peeling,
no occurrence-two signed-graphic reduction.
```

The all-positive E12 carrier already lies in this regime.

So the remaining universal problem is genuinely a cubic-on-both-sides signed
1-in-3 core, subject to all the earlier quotient/global-language terminals.

## 7. Updated router

After E43 local normalization:

```text
OCC0  build signed constraint-variable incidence columns;
OCC1  if every column has support 2 -> E37 f-factor;
OCC2  if only t columns have support !=2 -> E42 branch on those t;
OCC3  otherwise retain the occurrence-three heavy core.
```

This branch is exact for any displayed signed 1-in-3 representation.

## 8. Frontier

E44 does not close the cubic core, because E12 proves that doing so in polynomial
time would imply P=NP.

It does, however, remove the entire occurrence-two sector and its logarithmic
backdoor neighborhood from the unresolved frontier.

The next useful attacks must therefore exploit structure *inside* the cubic signed
1-in-3 core rather than trying to lower variable occurrence globally.

```text
P_VS_NP = OPEN.
```
