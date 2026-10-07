# R5 E103 — Signed Phase-Clash Geometry Firewall and F2^3 Flow Normal Form

Date: 2026-10-07

Status:
`GEOMETRY_ONLY_PHASE_CLASH_KILLER_FALSIFIED__BAD_HOLONOMY_REQUIRES_MINIMALITY_OR_NO_RAW8_LEVERAGE`

Scientific ceiling:

```text
E103 DOES NOT PROVE TARGET6 => RAW8.

IT PROVES THAT THE FIRST E102 SIGNATURE OBSTRUCTION
    H_a^0 versus H_a^1
CANNOT BE ELIMINATED FROM C4-FREENESS, CUBICITY AND SIX-EXACT-COVER
GEOMETRY ALONE.

AN EXPLICIT CONNECTED 27x27 SQUARE-CUBIC-C4-FREE SOURCE HAS:
  * SIX EXACT COVERS;
  * NO RIGID CHECK;
  * ONE NONZERO HOLONOMY COMPONENT;
  * BOTH H_(1,0)^0 AND H_(1,0)^1 IN THAT COMPONENT;
  * EMPTY COMPONENT-WIDE Good INTERSECTION.

THE SAME EXAMPLE HAS EIGHT TOTAL EXACT COVERS.
THIS POINTS TO THE CORRECT NEXT LEVERAGE:
WITNESS MINIMALITY / EXCHANGE SWITCHING / EXACT NO-RAW8 PARENT SEMANTICS.

P_VS_NP = OPEN.
```

## 1. A cleaner variable invariant

For one variable with six-witness support

```text
S subseteq {XA,XB,XC,QAB,QAC,QBC},
```

define the three opposite-pair atoms

```text
O0={XA,QBC},
O1={XB,QAC},
O2={XC,QAB}.
```

Define

```text
d_i(S)=|S cap O_i| mod2.
```

So

```text
d(S)=(d0,d1,d2) in GF(2)^3
```

records membership of that variable in the three opposite-cover symmetric
differences.

The E102 quantities are recovered linearly:

```text
p(S)=|S| mod2 = d0+d1+d2,

h(S)=(
  d0+d1,
  d0+d2
).
```

Thus the pair

```text
(parity, holonomy color)
```

is equivalent to the full three-bit exchange-membership vector d.

## 2. The four E95/E102 candidates are the four odd functionals

For correction

```text
k=(a,b) in GF(2)^2
```

the selected bit is

```text
e_k(S)
=
1+p(S)+a h1(S)+b h2(S).
```

Substituting the d-normal form gives

```text
e_k(S)=1+w(k) dot d(S)
```

with

```text
w(00)=111,
w(10)=001,
w(01)=010,
w(11)=100.
```

Therefore the four canonical raw8 parity candidates are exactly the four
odd-weight linear functionals on GF(2)^3.

This explains the finite 4-state correction space geometrically.

## 3. Check conservation

At every ordinary ExactOne check, the three incident six-witness supports
partition the six labels.

For each opposite pair O_i, the number of incident variables containing
exactly one label of O_i is even.

Hence the incident d-vectors satisfy

```text
boxed:
d(u) xor d(v) xor d(w) = 000.
```

So the E102 holonomy system is a cubic GF(2)^3 flow.

The local Good-set of a check depends only on these d-vectors, not on the full
six-bit supports.

## 4. Signed phase interpretation

For a nonzero E102 color h there are exactly two compatible d-vectors.

They are complements in GF(2)^3:

```text
one has Hamming weight 1,
the other has Hamming weight 2.
```

Call them single phase and double phase.

For example, for direction

```text
a=(1,0)
```

the two nonzero d-types are

```text
010
and
101.
```

Then:

```text
H_a^0 check:
  000, 010, 010

H_a^1 check:
  000, 101, 101

neutral phase bridge:
  111, 010, 101.
```

The last triple is one Fano line in GF(2)^3 and has unrestricted Good-set K.

Thus the smallest E102 phase clash has a simple local transport mechanism:
a universal 111 exchange variable converts single phase into double phase.

## 5. Explicit Pappus construction

Take three disjoint 9x9 Pappus Tanner components.

Each Pappus component is:

```text
square,
cubic,
connected,
C4-free,
```

and has three exact-cover classes.

Assign the six target labels to those three cover classes as follows.

### Component 0 — H_(1,0)^0

```text
empty
{0,1,2,3,5}
{4}
```

Every one of its nine checks therefore has Good-set

```text
H_(1,0)^0.
```

### Component 1 — neutral bridge

```text
{0,1,2}
{3,5}
{4}
```

Every check has

```text
Good=GF(2)^2.
```

Its nonzero supports carry the two opposite phases of the same E102 color.

### Component 2 — H_(1,0)^1

```text
empty
{0,1,2,4}
{3,5}
```

Every check has Good-set

```text
H_(1,0)^1.
```

## 6. Two support-preserving 2-switches

A Tanner 2-switch between variables with identical six-witness support
preserves every one of the six exact covers.

Indeed every target witness selects either both swapped variables or neither,
so the two affected checks retain exactly the same selected-count pattern.

E103 performs two such switches:

```text
component 0 <-> component 1
through support {4},

component 1 <-> component 2
through support {3,5}.
```

The checker verifies after both switches:

```text
27 variables,
27 checks,
all variable degrees = 3,
all check degrees = 3,
connected Tanner graph,
no pair of variables shares two checks.
```

Hence the final source is square, cubic, connected and C4-free.

## 7. Exact phase-clash result

All six labeled exact covers survive the switches.

Across the 27 checks:

```text
9 checks : Good=H_(1,0)^0
9 checks : Good=GF(2)^2
9 checks : Good=H_(1,0)^1
```

There are no rigid checks.

All variables with nonzero E102 color form one connected holonomy component.

Therefore its allowed-correction intersection is

```text
H_(1,0)^0
cap GF(2)^2
cap H_(1,0)^1
=
empty.
```

So:

```text
boxed:
A RIGID-FREE CONNECTED C4-FREE CUBIC SIX-COVER GEOMETRY
CAN REALIZE THE MINIMAL TWO-CHECK SIGNED PHASE CLASH.
```

This falsifies a geometry-only E103-A killer.

## 8. Why this does not refute the active TARGET6 parent route

The constructed 27x27 source is a closed six-cover geometry.

It does not claim to realize an exact five-port parent boundary relation equal
to TARGET6.

Therefore it does not refute:

```text
exact TARGET6 parent impossible,
or
exact delta parent => raw8.
```

It proves a narrower but essential firewall:

```text
C4-freeness + cubicity + six exact covers + rigid-free
are insufficient assumptions for killing H_a^0/H_a^1.
```

Any valid universal proof must use additional information specific to the
parent problem.

## 9. The example exposes the next leverage

The final 27x27 source has exactly

```text
8
```

exact covers.

The six target labels use only three distinct internal covers.

So the bad holonomy component coexists with additional exact covers.

That strongly suggests the correct next question is not

```text
"can the phase clash exist geometrically?"
```

but

```text
"can it survive after choosing the six boundary witnesses minimally under
same-boundary exchange switches?"
```

In a genuine TARGET6 parent, a terminal-free exchange component can switch one
witness without changing its boundary state.

E98 already proves minimum opposite witness pairs have no such terminal-free
component.

The next step should combine that minimality with the E103 d-flow.

## 10. Correct E104 target

```text
E104 MINIMAL-WITNESS PHASE-CLASH KILLER

Choose the six TARGET6 witnesses lexicographically minimal under:
  1. total opposite-pair symmetric-difference size;
  2. total nonzero d-support;
  3. number of bad holonomy components.

Use the GF(2)^3 d-flow normal form.

Goal:
  prove an H_a^0/H_a^1 clash in one bad component creates either

  A. a terminal-free exchange switch reducing the chosen witness tuple;
  B. a 2+2 E98 rectangle allowing a coherent re-choice;
  C. an additional exact raw boundary state, ideally raw8;

or freeze the first minimal exact TARGET6 parent obstruction.
```

A proof of A/B/C would kill the size-2 holonomy obstructions for the right
reason.

Scientific status:

```text
E103 = GF(2)^3 EXCHANGE-MEMBERSHIP NORMAL FORM
       + EXPLICIT 27x27 GEOMETRY-ONLY PHASE-CLASH COUNTEREXAMPLE.

GEOMETRY_ONLY_PHASE_CLASH_KILLER = FALSE.
E102 BAD_HOLONOMY_LOCALIZATION = VALID.
E98 MINIMAL EXCHANGE COMPONENT THEOREM = VALID.
MINIMAL_WITNESS_PHASE_CLASH = OPEN.
EXACT TARGET6 PARENT = OPEN.
P_VS_NP = OPEN.
```
