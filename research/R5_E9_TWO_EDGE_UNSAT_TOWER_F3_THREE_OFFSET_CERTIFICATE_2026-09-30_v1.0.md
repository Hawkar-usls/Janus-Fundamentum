# R5 E9 — Two-Edge UNSAT Tower: Persistent F3 Three-Offset Certificate

Date: 2026-09-30

Status:
`JANUS_ARBITRARY_SIZE_UNSAT_CERTIFICATE_THEOREM__THREE_COORDINATE_F3_COVER_PERSISTS_UNDER_RECURSIVE_LIFT__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THE INFINITE PRIME UNSAT TOWER IS RECOGNIZED BY A CONSTANT-SIZE
AFFINE-F3 THREE-OFFSET CERTIFICATE AT EVERY LEVEL.
THIS REMOVES THAT TOWER AS A HOSTILE RESIDUAL FOR THE AF3/APSQ ROUTE.
IT DOES NOT PROVE UNIVERSAL COVERAGE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Tower and first recursive level

Let `A_0` be the frozen 15_3 UNSAT seed and let `A_1` be its first two-edge lift using

```text
F_0={(0,12),(2,9)}.
```

For all later levels, the parent tower uses the recursive distinguished pair

```text
F_1={(0,5),(1,1)}
```

and then its two upper-right crossed copies at each lift.

Work over `F3`.

The affine equation

\[
A_1r=\mathbf1
\]

is consistent, but has no nowhere-zero solution.

## 2. A constant three-coordinate obstruction on A1

Exact Gaussian elimination over `F3` gives the following affine-coordinate identity for every solution of `A_1r=1`:

\[
\boxed{
r_{16}-r_{12}=2,
\qquad
r_{20}-r_{12}=1.
}
\]

Equivalently, for some `s in F3`,

\[
\boxed{
(r_{12},r_{16},r_{20})=(s,s+2,s+1).
}
\]

Therefore the three coordinates are always exactly the three field symbols in some order.  One of them is zero for every affine solution, so AF3-1 gives UNSAT.

This is exactly a three-offset parallel class in APSQ.

## 3. Explicit row-space certificates

The two affine identities are certified by row combinations of `A_1`.

For `e_16-e_12`, take

```text
y16 =
(0,0,2,2,2,2,1,2,1,0,2,1,2,0,0,1,2,0,1,1,0,0,1,2,2,2,2,1,0,0).
```

For `e_20-e_12`, take

```text
y20 =
(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,2,1,1,0,0,2,0,0,1,0,1,0).
```

Direct multiplication over `F3` gives

\[
y16^TA_1=e_{16}-e_{12},
\qquad
y20^TA_1=e_{20}-e_{12}.
\]

Crucially,

```text
y16[0]=y16[1]=0,
y20[0]=y20[1]=0.
```

The later recursive twist matrix `E_1` has nonzero rows only `0` and `1`. Therefore

\[
y16^TE_1=y20^TE_1=0.
\]

Hence the same certificates also lie in the row space of the signed block `A_1-E_1` and are unaffected by the recursive twist.

## 4. Preservation under one recursive lift

Write one recursive lift as

\[
A'=
\begin{pmatrix}
A-E&E\\
E&A-E
\end{pmatrix},
\]

where the distinguished rows are `0,1` and both certificate vectors `y` vanish on those rows.

If

\[
y^TA=q
\]

and `y^TE=0`, then using the row vector `(y,0)` on the lifted matrix gives

\[
(y,0)^TA'
=
(y^T(A-E),y^TE)
=
(q,0).
\]

Thus every row-space relation among upper-sheet coordinates certified by such a `y` lifts verbatim to the next level.

Moreover `(y,0)` still has zero coefficients on the next distinguished upper-sheet rows `0,1`, so the same argument iterates indefinitely.

### Lemma U3O-1

For every `t>=1`, in `A_t` the upper-sheet descendants of coordinates `12,16,20` satisfy

\[
\boxed{
e_{16}-e_{12},\ e_{20}-e_{12}\in\operatorname{row}_{F3}(A_t),
}
\]

with certificates vanishing on the current distinguished rows.

## 5. Affine constants also persist

Choose any particular solution `r_1^(0)` of

\[
A_1r=\mathbf1.
\]

The first-level exact elimination has

\[
(r_{12}^{(0)},r_{16}^{(0)},r_{20}^{(0)})=(0,2,1)
\]

after the canonical affine parameterization used by the checker.

For every later lift use the diagonal particular solution

\[
r_{t+1}^{(0)}=(r_t^{(0)},r_t^{(0)}).
\]

The three tracked upper-sheet constants are unchanged.
Together with U3O-1 this proves that every affine solution at every level has

\[
(r_{12},r_{16},r_{20})=(s,s+2,s+1)
\]
for some `s`.

Therefore the three tracked coordinates form a persistent full three-offset parallel class.

## 6. Main theorem

### Theorem U3O-2

For every recursive level `t>=1` of the frozen two-edge exact-UNSAT prime tower, APSQ returns `UNSAT` from a constant-size three-coordinate certificate.

The certificate consists of:

```text
tracked coordinates: 12,16,20 in the recursively chosen upper sheet;
row-space relation 1: r16-r12=2;
row-space relation 2: r20-r12=1.
```

Hence one tracked coordinate is zero in every `F3` solution of `A_tr=1`, so no nowhere-zero affine solution exists and Exact-One is UNSAT by AF3-1.

Certificate verification is ordinary `F3` matrix multiplication and is polynomial; certificate discovery for this explicit tower is supplied recursively by the theorem and requires no affine-point enumeration.

## 7. Finite regression

The checker replays

```text
n = 15,30,60,120,240,480
```

and verifies that APSQ detects a three-offset class immediately at every level.
For `t>=1` it separately verifies the persistent tracked triple `12,16,20` and the lifted row-space certificates.

The observed ternary nullities are

```text
1,2,3,5,9,17,
```

showing that the UNSAT certificate remains constant-size while the affine dimension grows.

## 8. Strategic consequence

The two prime towers that previously survived many rational/integer structural attacks are now both polynomially separated by the finite-field route:

```text
UNIQUE-MODEL SAT TOWER
-> every projective class is polarity-complete
-> APSQ pins the entire affine displacement
-> SAT witness reconstructed.

PRIME UNSAT TOWER
-> persistent three-offset projective class
-> APSQ returns UNSAT immediately.
```

Therefore the next canonical adversary for AF3/APSQ must satisfy all of:

```text
positive residual affine dimension after saturation,
no three-offset parallel class,
no complete polarity pinning,
not already covered by graphic/TU/binet/regular terminals.
```

PG15 remains the smallest frozen positive example of this type.

## 9. Ceiling

```text
PERSISTENT 3-COORDINATE F3 UNSAT CERTIFICATE
= PROVED FOR ALL RECURSIVE LEVELS t>=1

PRIME UNSAT TOWER UNDER APSQ
= COMPLETE / POLYNOMIAL

PRIME SAT TOWER UNDER APSQ
= COMPLETE BY COMPANION THEOREM

BOTH OLD PRIME HOSTILE TOWERS
= REMOVED FROM AF3 RESIDUAL

GENERAL PARALLEL-SIMPLE RESIDUAL
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
