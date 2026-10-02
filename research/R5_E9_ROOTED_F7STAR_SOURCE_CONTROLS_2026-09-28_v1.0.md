# R5 E9 — Rooted F7* Source Controls

Date: 2026-09-28

Status: `JANUS_EXACT_FINITE_SOURCE_CONTROLS__ROOTED_F7STAR_IS_NOT_A_SAT_STATUS_BIT__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_ROOTED_MFMC_SYNDROME_POLY_TERMINAL_2026-09-28_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_rooted_f7star_source_controls.py`

Scientific ceiling:

```text
THESE ARE EXACT FINITE MINOR CENSUSES.
THEY DO NOT PROVE A UNIVERSAL ROOTED-F7* CONTRACTION.
THEY DO PROVE THAT THE PRESENCE OF A ROOTED F7* MINOR THROUGH e_b
CANNOT ITSELF BE USED AS AN UNSAT CERTIFICATE.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact rooted-F7* fingerprint

For a seven-element binary minor `N`, the following exact fingerprint is used:

```text
rank(N)=4,
cycle-space dimension=3,
all seven nonzero cycles have cardinality four.
```

This is the binary simplex/Hamming dual fingerprint of `F7*`.

For a represented matroid `M` with a contraction set `C` and seven kept elements `K`, a kept subset `S` is a cycle of `M/C` iff

```text
XOR(columns in S) belongs to span(C).
```

Therefore the checker performs the minor test directly over `F2`, with no graph-isomorphism heuristic.

The root is always the augmented syndrome element

```text
e_b = final column of [A | 1].
```

Only minors retaining `e_b` are counted.

## 2. Fano 7_3 source control

Use the standard Fano configuration lines

```text
012, 034, 056, 135, 146, 236, 245.
```

Its incidence matrix is square, linear and cubic.  Append the all-ones syndrome column.

Exact census:

```text
rooted F7* minors obtained by deleting one original column = 7.
```

For every original column `j`, deleting `j` leaves seven elements including `e_b`; that restriction is `F7*`.

This proves that rooted `F7*` is genuinely source-generated, not an artifact of a generic binary-matroid representation.

The control is trivially Exact-One UNSAT because `n=7` is not divisible by three, so it is not by itself a hard SAT/UNSAT separator.

## 3. AFFINE_3X3 SAT control

Use the nine point set `Z_3^2` and the nine blocks from:

```text
three vertical classes,
three horizontal classes,
three slope +1 classes.
```

This is a square linear cubic `9_3` configuration with exactly three Exact-One witnesses.

There are ten augmented elements.  A seven-element rooted minor therefore removes exactly three original elements; each removed element may be deleted or contracted.

The checker exhausts

```text
C(9,3) * 2^3 = 672
```

rooted delete/contract scenarios.

Result:

```text
rooted F7* minors through e_b = 0.
```

Thus this SAT control lies inside the rooted-MFMC polynomial terminal.

## 4. SAT 12_3 rooted-F7* countercontrol

Now use the following twelve column supports on rows `0..11`:

```text
c0  = 012
c1  = 345
c2  = 678
c3  = 9,10,11
c4  = 10,1,8
c5  = 11,2,3
c6  = 3,1,6
c7  = 10,4,0
c8  = 8,4,11
c9  = 9,5,6
c10 = 2,9,7
c11 = 7,5,0
```

The checker verifies exactly:

```text
row degree    = 3,
column degree = 3,
linearity     = PASS,
Exact-One models = 1,
unique witness = {c0,c1,c2,c3}.
```

The four selected columns are pairwise row-disjoint and cover all twelve rows.

Nevertheless the augmented binary matroid has rooted `F7*` minors.  One explicit witness is:

```text
keep original columns = {1,2,3,4,5,7}, together with e_b,
contract              = {0,6,10,11},
delete                = {8,9}.
```

For this minor:

```text
rank(contracted span) = 4,
minor rank             = 4,
nonzero minor cycles   = 7,
cycle weights          = [4,4,4,4,4,4,4].
```

The seven cycles, with `e_b` denoted by `b`, are

```text
{2,3,4,5}
{1,2,4,7}
{1,3,5,7}
{1,2,3,b}
{1,4,5,b}
{3,4,7,b}
{2,5,7,b}.
```

An exhaustive rooted-minor census on this finite control finds

```text
144
```

rooted `F7*` delete/contract witnesses.

Hence

\[
\boxed{
SAT \centernot\Rightarrow \text{rooted-MFMC}.
}
\]

Equivalently, the live rooted-`F7*` side contains genuine satisfiable source instances.

## 5. Consequence for the active gate

The new rooted-MFMC terminal remains a strict polynomial positive region, but its complement cannot be classified by the one-bit test

```text
e_b belongs to an F7* minor -> UNSAT.
```

That rule is false.

The surviving obligation is therefore semantic rather than merely recognitional:

```text
R5_E9_ROOTED_SYNDROME_F7STAR_GLOBAL_CONTRACTION_GATE_V1
```

must preserve the minimum circuit-through-`e_b` threshold under a decomposition/contraction of rooted `F7*` structure.

A valid next theorem must explain how rooted `F7*` pieces interact with the distinguished shortest-route objective across the rest of the source-generated matroid, with polynomial total state and witness reconstruction.

## 6. Ceiling

```text
FANO_7_3 ROOTED F7* SOURCE OCCURRENCE
= YES, EXACT

AFFINE_3X3 SAT ROOTED F7*
= NO ACROSS ALL 672 ROOTED 7-ELEMENT MINORS

SAT 12_3 WITH ROOTED F7*
= YES, EXACT

ROOTED F7* PRESENCE AS UNSAT CERTIFICATE
= FALSIFIED

ROOTED MFMC TERMINAL
= STILL VALID POSITIVE REGION

ROOTED F7* SEMANTIC CONTRACTION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
