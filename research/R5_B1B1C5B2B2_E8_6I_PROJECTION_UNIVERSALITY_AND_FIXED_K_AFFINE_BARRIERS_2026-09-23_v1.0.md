# R5 E8 6I — Projection-Universality Transfer and Fixed-k Affine Barriers

Date: 2026-09-23

Authority: `PROVED_SOURCE_BOUND_TRANSFER_LEMMA_PLUS_FIXED_K_BARRIERS__NO_D1_PROMOTION`

## 1. New 2026 source that closes the reduction interface

Barto, Hadek, Zhuk,
*Toward a Uniform Algorithm and Uniform Reduction for Constraint Problems*,
arXiv:2604.06335v1 (2026).

The paper supplies the exact higher-level criterion that was previously missing.

For PCSP source template with polymorphism minion `M'` and target template with
polymorphism minion `M`, Theorem 6.14 states:

```text
source
<= via k-consistency reduction
target

iff

lvl_k(omega M)
->
M'

by a minion homomorphism.
```

Theorem 6.11 also states that a minion relaxation `R` solves a finite-template
PCSP with polymorphism minion `N` iff there is a minion homomorphism

```text
R -> N.
```

Proposition 6.10 supplies the corresponding compactness / finite-LC-obstruction
principle when the target minion is locally finite.

## 2. Projection-universality transfer lemma

Let `P` be the projection minion.

### Lemma

For any minion `R`:

```text
R -> P
```

implies

```text
R -> Pol(T)
```

for every finite relational template `T`.

### Proof

Every relational structure is preserved by every coordinate projection.
Therefore there is the canonical minion homomorphism

```text
P -> Pol(T),
p_i^n |-> p_i^n.
```

Composition gives

```text
R -> P -> Pol(T).
```

By Barto--Hadek--Zhuk Theorem 6.11, the `R`-relaxation would then solve
`CSP(T)`.

QED.

### Contrapositive

If one finite template `T` has a No-instance accepted by the `R`-relaxation,
then

```text
R -/-> P.
```

This is unconditional. It does not assume `P != NP`.

## 3. Binding to full signed Boolean 3SAT

Frozen source fact:

```text
Pol(Gamma_3SAT) = P.
```

The visible/extensional frozen three-sheet language has exact union equal to
signed OR3. Therefore, whenever a proposed relaxation is applied directly to
that visible language, solving it requires

```text
R -> P.
```

The transfer lemma can therefore convert any source-exact failure of `R` on
another finite CSP template into a barrier for direct visible three-sheet /
signed-3SAT solving.

## 4. Fixed-k affine reduction barrier

Let `LIN_p` be the canonical finite affine CSP over the prime field
`F_p`, with constants included. Its polymorphism minion is the affine minion

```text
Z_p^(n)
=
{(a_1,...,a_n) in F_p^n :
 a_1+...+a_n = 1}.
```

The corresponding operation is

```text
f(x_1,...,x_n)
=
a_1 x_1 + ... + a_n x_n.
```

Barto--Hadek--Zhuk Theorem 6.14 says that a fixed-k consistency reduction

```text
Gamma_3SAT
->
LIN_p
```

exists iff

```text
lvl_k(omega Z_p)
->
P.
```

### Source counterexample

Lichter--Pago,
*Limitations of Affine Integer Relaxations for Solving Constraint Satisfaction Problems*,
ICALP 2025 / arXiv:2407.09097v3.

Their Theorem 1 / Theorem 29 supplies one fixed finite Maltsev template
`T_LP` such that Z-affine k-consistency fails to solve `CSP(T_LP)`
for every fixed `k` (indeed the construction is robust for sublinear width).

Concretely, for each k they construct a No-instance that survives k-consistency
and whose resulting affine marginal system has an integral solution.

Reduce that integral solution modulo p. All normalization and marginalization
equations have integer coefficients, so the reduced weights form an
`F_p`-affine solution on the same surviving local supports.

Therefore the corresponding mod-p affine k-level also accepts the same No-instance.

Equivalently, the relaxation described by

```text
R_{p,k}
=
lvl_k(omega Z_p)
```

does not solve `CSP(T_LP)`.

By the projection-universality transfer lemma:

```text
R_{p,k}
-/->
P.
```

Hence by Barto--Hadek--Zhuk Theorem 6.14:

```text
FOR EVERY PRIME p
AND EVERY FIXED k,

FULL SIGNED 3SAT
NOT <=_{k-consistency}
LIN_p.
```

In particular:

```text
FIXED-k CONSISTENCY REDUCTION
VISIBLE THREE-SHEET
->
BOOLEAN XOR
=
BLOCKED.
```

This strictly strengthens the earlier arc-only cyclic barrier.

## 5. Direct CLAP barrier

Ciardo--Zivny characterize CLAP by a fixed minion `C_CLAP`: CLAP solves
a finite-template PCSP exactly when

```text
C_CLAP -> Pol(T).
```

Lichter--Pago Theorem 1 / Theorem 21 gives a fixed tractable Maltsev template
`T_LP` not solved by CLAP.

If CLAP solved full signed 3SAT, we would have

```text
C_CLAP -> P.
```

The canonical map

```text
P -> Pol(T_LP)
```

would then imply

```text
C_CLAP -> Pol(T_LP),
```

contradicting the source counterexample.

Therefore:

```text
DIRECT CLAP
ON VISIBLE SIGNED 3SAT / EXTENSIONAL THREE-SHEET
=
BLOCKED.
```

This does NOT block an instance-specific representation-changing compiler whose
output belongs to a different PCSP template solved by CLAP.

## 6. Direct fixed-k cohomological barrier

Barto--Hadek--Zhuk explain that cohomological k-consistency is captured by
levels of a singleton AC+AIP minion.

Lichter--Pago Theorem 3 / Theorem 23 gives an NP-complete finite template
`T_coh` such that, for every constant k, cohomological k-consistency fails
to solve `CSP(T_coh)`.

Apply the same transfer lemma to the relaxation minion `R_coh,k`.

If

```text
R_coh,k -> P,
```

then

```text
R_coh,k -> P -> Pol(T_coh),
```

contradicting the explicit source failure.

Thus:

```text
FOR EVERY FIXED k,

DIRECT COHOMOLOGICAL k-CONSISTENCY
ON FULL SIGNED 3SAT
=
BLOCKED.
```

Again, this is a direct-relaxation barrier, not a barrier to arbitrary
representation-changing preprocessing.

## 7. What is now closed

```text
ARC -> XOR / FINITE AFFINE
=
BLOCKED

ANY FIXED-k CONSISTENCY REDUCTION
VISIBLE 3SAT -> PRIME-FIELD AFFINE
=
BLOCKED

DIRECT CLAP
=
BLOCKED

DIRECT FIXED-k COHOMOLOGICAL
=
BLOCKED
```

No complexity assumption was used.

## 8. What remains genuinely open

The surviving route must change the representation before the blocked
relaxation/minion sees the full projection template.

Possible admissible shape:

```text
SIGNED 3SAT
   |
   | exact polynomial
   v
INSTANCE-SPECIFIC CERTIFICATE / REPRESENTATION R(F)
   |
   | proved non-selector compression
   v
TRACTABLE GLOBAL RELAXATION / CARRIER
   |
   v
BOOLEAN WITNESS
```

The preprocessing must itself have a complete polynomial lifecycle and cannot
hide SAT search.

## 9. New exact gate

Freeze:

```text
R5_E8_6I
REPRESENTATION_CHANGE_BEFORE_RELAXATION_GATE_V1
```

Question:

Can the frozen three-sheet interaction be transformed, in exact deterministic
polynomial time, into an instance-specific representation whose polymorphism /
relaxation minion is not the projection minion, while preserving one global
Boolean witness and without exposing SAT-equivalent selector choices?

Required:

```text
T_construct
+
T_certificate
+
T_relax
+
T_solve
+
T_reconstruct
+
T_verify
<=
poly(L).
```

## 10. Ceiling

```text
D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT_PROVED

VISIBLE DIRECT RELAXATION ESCAPES
=
SEVERELY NARROWED

REPRESENTATION_CHANGE_BEFORE_RELAXATION
=
OPEN
```
