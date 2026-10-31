# R5 E8 6I — Rank-One Affine + AND Schaefer Barrier

Date: 2026-09-23

Authority:

`SOURCE_BOUND_SCOPED_BARRIER__GENERIC_MIXED_LANGUAGE_ONLY__NO_D1_PROMOTION`

Parent:

`R5_E8_6I_RANK1_NONAFFINE_TRACTABLE_CUT_CURRENCY_GATE_V1`

## 1. Natural repair being tested

After the affine-hull barrier, the first nonlinear defect predicate is

```text
Z_ij = Z_0i Z_0j.
```

Over Boolean variables this is the graph of AND:

```text
R_AND(x,y,z)
iff
z = x AND y.
```

Since `R_AND` is Horn, a tempting composition is:

```text
Gaussian elimination
for affine moment equations

+

Horn propagation
for multiplicative cuts.
```

This artifact checks whether the **generic mixed Boolean language** obtained this
way is one of Schaefer's polynomial classes.

## 2. Fixed relations

Use

```text
R_AND
=
{000,010,100,111}

R_XOR
=
{x in {0,1}^3 : x1+x2+x3 = 0 mod 2}.
```

Constants are allowed; the JANUS moment system already contains the distinguished
constant coordinate `w_0=1`.

Schaefer's dichotomy with constants states that a fixed Boolean language is
polynomial-time solvable exactly when all of its relations lie simultaneously in
one of the following four classes:

```text
Horn
dual-Horn
bijunctive / 2-SAT
affine.
```

Otherwise the CSP is NP-complete.

Source:

Patrick Schnider, Simon Weber,
*A Topological Version of Schaefer's Dichotomy Theorem*,
SoCG 2024, Theorem 1, which restates Schaefer's dichotomy with constants.

## 3. Closure audit

The graph of AND is Horn, but:

- not dual-Horn: OR of `010` and `100` is `110`, not in `R_AND`;
- not bijunctive: majority of `010,100,111` is `110`, not in `R_AND`;
- not affine: XOR of `000,010,100` is `110`, not in `R_AND`.

The parity relation `R_XOR` is affine, but:

- not Horn: AND of `011` and `101` is `001`, not in `R_XOR`;
- not dual-Horn: OR of `011` and `101` is `111`, not in `R_XOR`;
- not bijunctive: majority of `000,011,101` is `001`, not in `R_XOR`.

Therefore the language

```text
Gamma_mix
=
{R_AND, R_XOR, constants}
```

belongs to none of the four Schaefer tractable classes.

Hence:

```text
CSP(Gamma_mix)
=
NP-COMPLETE.
```

This is an unconditional complexity classification.

## 4. JANUS consequence

The result does **not** say that a JANUS-specific structured subclass cannot be
solved in polynomial time.

It says that the following is not a valid donor theorem:

```text
"AND cuts are Horn"
+
"base equations are affine"
therefore
"the combined refined abstraction is tractable."
```

Tractability of each side separately does not compose.

Any RAIL instantiation using multiplicative AND cuts must additionally prove a
structural theorem specific to its generated instances, or use a different
recursive representation whose exact solver is independently polynomial.

## 5. Stronger algebraic identity

For Boolean values,

```text
x OR y
=
x + y + xy
over F2.
```

Thus affine operations plus explicit product variables already have enough
expressive power to reconstruct ordinary Boolean disjunctions.

This explains why generic affine+AND composition can recover SAT-like behavior;
the nonlinear interaction is exactly where the hardness can live.

## 6. Scope firewall

Blocked:

```text
GENERIC
AFFINE-EQUATION CSP
+
UNRESTRICTED AND-CUT CSP
as a supposedly Schaefer-tractable lower-level solver.
```

Still open:

- a special graph/matroidal subclass of the generated AND cuts;
- bounded-width or acyclic instances with a **universal** structural proof;
- recursive quotient/interface representations;
- other nonaffine cut languages with a source-proved tractable composition law.

## 7. Ceiling

```text
SAME-MOMENT AFFINE CUTS
=
BLOCKED BY AFFINE-HULL WITNESS

GENERIC AFFINE + AND CUT MIXTURE
=
NP-COMPLETE BY SCHAEFER

JANUS-SPECIFIC STRUCTURED NONLINEAR CUT CURRENCY
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
