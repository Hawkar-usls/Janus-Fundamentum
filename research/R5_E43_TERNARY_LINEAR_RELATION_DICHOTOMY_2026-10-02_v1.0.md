# R5 E43 — Ternary Linear Relation Dichotomy

Date: 2026-10-02

Status:
`EXACT_RHS_STABLE_ASYMMETRIC_TERNARY_LINEAR_LANGUAGE__ONLY_EQUAL_MAGNITUDE_ROWS_CAN_CARRY_THREE_BOOLEAN_STATES__SIGNED_EXACTONE_CANONICAL_3CORE`

Scientific ceiling:

```text
THIS NOTE IDENTIFIES A NEW RHS-STABLE POLYNOMIAL LANGUAGE STRICTLY INSIDE
THE THREE-ENDPOINT LINEAR SECTOR.

FOR A TERNARY LINEAR EQUATION

  c1 x1 + c2 x2 + c3 x3 = h,
  xi in {0,1},
  ci != 0,

A LEVEL SET CAN CONTAIN THREE OR MORE BOOLEAN ASSIGNMENTS IF AND ONLY IF

  |c1| = |c2| = |c3|.

THEREFORE EVERY FULL-SUPPORT TERNARY ROW WITH UNEQUAL COEFFICIENT
MAGNITUDES HAS AT MOST TWO BOOLEAN STATES FOR EVERY RIGHT-HAND SIDE.
SUCH ROWS REDUCE EXACTLY TO FORCING PLUS EQUALITY/COMPLEMENT CONSTRAINTS,
SO SYSTEMS MADE ONLY OF THESE ROWS ARE POLYNOMIAL FOR ARBITRARY RHS.

AFTER EXHAUSTIVE LOCAL PEELING, THE ONLY IRREDUCIBLE TERNARY LINEAR ROW
LANGUAGE IS EQUAL-MAGNITUDE SIGNED EXACT-ONE / EXACT-TWO.

THIS DOES NOT SOLVE THAT REMAINING SIGNED 1-IN-3 CORE.
P_VS_NP = OPEN.
```

## 1. Local ternary equation

Consider

```text
c_1 x_1+c_2 x_2+c_3 x_3=h,
x_i in {0,1},
c_i in Q\{0}.
```

Scaling the entire equation by a nonzero rational changes nothing, so only the
projective coefficient triple matters.

For fixed `c=(c1,c2,c3)` define the Boolean level relation

```text
R_h(c)={x in {0,1}^3 : c^T x=h}.
```

We ask exactly when some level can contain at least three cube vertices.

## 2. Three cube vertices determine a plane

Any three distinct vertices of the Boolean cube `{0,1}^3` are non-collinear.

Indeed, if two cube vertices differ in some coordinate, every strict interior point
of their Euclidean segment has a fractional value in that coordinate. Hence the
segment contains no third cube vertex.

Therefore any three distinct Boolean solutions of one full-support ternary equation
determine its affine plane uniquely.

## 3. Cube-plane lemma

Assume

```text
|R_h(c)| >= 3
```

and every `c_i` is nonzero.

Choose one Boolean solution `p`. Complement every coordinate in which `p_i=1`.
Such a cube symmetry sends `p` to `000`; on the equation it only changes signs of
some coefficients and shifts the right-hand side. In particular it preserves the
absolute coefficient magnitudes.

So after cube symmetry we may assume three solutions include

```text
000,
u,
v,
```

with `u,v` distinct nonzero Boolean vectors satisfying

```text
c^T u=0,
c^T v=0.
```

Because every `c_i` is nonzero, neither `u` nor `v` can have Hamming weight one.

If one of them had weight three, say `u=111`, while the other had weight two, say
`v=110`, then

```text
c1+c2+c3=0,
c1+c2=0,
```

forcing `c3=0`, contradiction.

Thus both `u` and `v` have weight two. Up to permuting coordinates we may take

```text
u=110,
v=101.
```

Then

```text
c1+c2=0,
c1+c3=0,
```

so

```text
c2=c3=-c1.
```

Hence

```text
boxed:
|c1|=|c2|=|c3|.
```

Conversely, if the three absolute magnitudes are equal, sign flips of variables
reduce the coefficient pattern to `(1,1,1)` up to an RHS shift. The level

```text
x1+x2+x3=1
```

contains exactly three Boolean states.

Therefore:

### Theorem TERNARY-CUBE-DICHOTOMY

```text
boxed:
For c_i != 0,
max_h |R_h(c)| >= 3
iff
|c1|=|c2|=|c3|.
```

## 4. Asymmetric ternary rows have at most two states

Call a full-support ternary row **asymmetric** if

```text
not (|c1|=|c2|=|c3|).
```

By the theorem, for every right-hand side `h`,

```text
|R_h(c)| <= 2.
```

This is an RHS-stable property: changing `h` never creates a three-state relation.

## 5. Every at-most-two-state relation is parity/forcing structure

Let a ternary Boolean relation contain exactly two assignments

```text
a,b in {0,1}^3.
```

Coordinates on which `a_i=b_i` are forced.

On the remaining coordinates choose one pivot `p`. Since `a` and `b` differ at
all unforced coordinates, every other unforced coordinate `i` obeys exactly

```text
x_i xor x_p = a_i xor a_p.
```

Thus the two-point relation is represented exactly by

```text
unary forcing
+
equality/complement constraints.
```

A singleton relation simply forces all its coordinates; an empty relation is an
UNSAT certificate.

Therefore conjunctions of asymmetric ternary rows are solved by ordinary parity
union-find with forced component values.

The work is linear up to inverse-Ackermann factors once the local row relations are
enumerated.

## 6. RHS-stable polynomial language

Define `ASYM-3LIN` to be the class of integer/rational linear systems

```text
R x=h,
x in {0,1}^n,
```

such that every nonzero row has support at most three, and every support-three row
has coefficient magnitudes not all equal.

Support-zero, support-one and support-two rows are handled by the exact R5 E40
peeling rules. Every remaining support-three row has at most two Boolean states by
Section 4.

Hence:

### Theorem ASYM-3LIN-RHS

```text
boxed:
ASYM-3LIN Boolean feasibility is decidable in deterministic polynomial time
for arbitrary rational/integer right-hand side h.
```

So `ASYM-3LIN` is a genuinely new RHS-stable language in the sense of R5 E42.

Consequently, if deleting `t` columns from a kernel-equivalent representation leaves
an `ASYM-3LIN` system, R5 E42 immediately gives

```text
boxed:
O(2^t poly(n)).
```

## 7. This is genuinely beyond the previous base languages

The one-row matrix

```text
R=[1 1 2]
```

already belongs to `ASYM-3LIN`.

Its row space is the one-dimensional space spanned by `(1,1,2)`.

A rank-one TU representation with the same kernel would need the same primitive row
space, but any primitive generator contains the coefficient `2`, so it cannot be
TU.

Likewise a rank-one representation with every column carrying only signed
`{+1,-1}` incidences cannot span `(1,1,2)`: in rank one every nonzero row is a scalar
multiple of the unique primitive row, and the absolute nonzero entries would have
to be equal.

Thus `ASYM-3LIN` is not merely the previous TU or signed-graphic language written
with one redundant equation.

## 8. Equal-magnitude rows are exactly the irreducible local language

Now suppose

```text
|c1|=|c2|=|c3|.
```

Scale to coefficients in `{+1,-1}`. For every negative coefficient replace

```text
x_i = 1-z_i.
```

Then the equation becomes

```text
z_1+z_2+z_3=k
```

for some integer `k` determined by the original RHS and the number of negative
coefficients.

For Boolean variables:

```text
k outside {0,1,2,3} -> empty;
k=0 or 3             -> one assignment, hence forcing;
k=1                  -> Exact-One(z1,z2,z3);
k=2                  -> Exact-Two(z1,z2,z3)
                        = Exact-One(1-z1,1-z2,1-z3).
```

Therefore after exhaustive local forcing, every nontrivial equal-magnitude ternary
row is exactly a **signed Exact-One** constraint.

So:

```text
boxed:
FULLY PEELED 3-SPARSE LINEAR BOOLEAN SYSTEM
=
SIGNED 1-IN-3 CORE
+
POLYNOMIALLY ELIMINABLE ASYMMETRIC ROWS.
```

This is a canonical local normal form, not a complexity assumption.

## 9. Relation to the R5 E12 hard carrier

The R5 E12 square+cubic+linear target uses rows

```text
x_i+x_j+x_k=1.
```

Every hard-source row is exactly the equal-magnitude `k=1` survivor above.

Thus E43 explains locally why the E12 carrier sits precisely on the boundary left
unresolved by the asymmetric ternary theorem.

The NP-complete carrier does not obtain its difficulty from arbitrary ternary
coefficients. It already lives in the unique nontrivial three-state hyperplane type
of the Boolean 3-cube.

## 10. Router update

After R5 E40 low-degree peeling, add:

```text
TL0  inspect every support-three affine row relation;
TL1  unequal coefficient magnitudes -> <=2 states -> parity/forcing reduction;
TL2  equal magnitudes but <=1 surviving state -> force / reject;
TL3  equal magnitudes with 3 states -> normalize to signed Exact-One;
TL4  iterate until closure.
```

If no signed Exact-One row remains, solve polynomially.

If signed Exact-One rows remain, pass the reduced instance to the later global
language / backdoor / decomposition branches.

## 11. Updated hard core

After E43, a genuine three-endpoint survivor cannot rely on arbitrary coefficient
heterogeneity. All such rows collapse polynomially.

The local hard core is now exactly:

```text
SIGNED EXACT-ONE 3-CORE
```

with the earlier global requirements still active:

```text
no useful projective/gauge quotient,
large effective width/backdoor distance,
no TU representation,
no signed-graphic f-factor representation,
no root/potential normal form,
no bounded-interface decomposition,
and no other recognized RHS-stable polynomial language.
```

The next high-value target is therefore no longer "find a polynomial 3-endpoint
language" in the abstract. It is sharper:

```text
Find a polynomially recognizable global subclass of SIGNED 1-IN-3 whose
tractability is not already TU / factor / potential / width based,
or prove a new structural decomposition theorem for the fully reduced signed
1-in-3 core.
```

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e43_ternary_linear_relation_dichotomy.py
```
