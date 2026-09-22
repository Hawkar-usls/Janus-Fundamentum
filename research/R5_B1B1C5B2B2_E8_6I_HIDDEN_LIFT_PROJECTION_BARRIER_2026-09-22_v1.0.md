# R5 E8 6I — Hidden Lift Projection-to-Visible Subalgebra Barrier

Date: 2026-09-22

Authority: `PROVED_SCOPED_ALGEBRAIC_BARRIER__CURRENT_6I_BRIDGE_CONTROL__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_6I_A3_SBM_MAJORITY_LIFT_POSITIVE_CONTROL_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_BIJUNCTIVE_THRESHOLD_2_TO_1_PP_BARRIER_2026-09-22_v1.0.md`
- `registry/R5_B1B1C5B2B2_E8_6I_INDUCED_ALGEBRA_ADMISSION_CHECKPOINT_2026-09-22_v1.0.json`

## 1. Purpose

The active 6I gap is:

```text
A3 exact lift admission
=
AT_LEAST_2_OF_3

universal signed 3-SAT needs
=
AT_LEAST_1_OF_3.
```

A natural old mechanism is to add hidden lifted variables and existentially project them away.

This theorem determines exactly what that can and cannot do when the visible algebra assignments and visible decoders are fixed.

## 2. Setup

Let the three visible coordinates use finite algebras:

```text
A_1, A_2, A_3
```

with a common operation signature.

Let the visible coordinate decoders be:

```text
pi_i : A_i -> {0,1}.
```

Let hidden lifted coordinates use arbitrary finite algebras:

```text
H_1,...,H_k
```

of the same operation signature.

Suppose a hidden-variable lifted constraint is represented by a subalgebra

```text
T
<=
A_1 x A_2 x A_3 x H_1 x ... x H_k.
```

Let:

```text
proj_vis(T)
```

be the projection of T onto the first three coordinates.

## 3. Projection lemma

### Lemma

```text
proj_vis(T)
<=
A_1 x A_2 x A_3.
```

### Proof

Take any basic operation symbol `f` of arity `q`.

Take any `q` tuples from `proj_vis(T)`.

Choose arbitrary witnesses in `T` for those visible tuples.

Since `T` is a subalgebra, coordinate-wise application of `f` to the witness tuples produces another tuple of `T`.

Projecting that result onto the visible coordinates gives exactly the coordinate-wise `f` result of the original visible tuples.

Hence `proj_vis(T)` is closed under every basic operation and therefore is a subalgebra of the visible product.

QED.

## 4. Decoder-image preservation

Define the visible decoded image of the hidden lift by:

```text
R_T
=
{
(pi_1(a_1),pi_2(a_2),pi_3(a_3))
:
exists h_1,...,h_k
with
(a_1,a_2,a_3,h_1,...,h_k) in T
}.
```

But this is exactly:

```text
R_T
=
(pi_1 x pi_2 x pi_3)(
  proj_vis(T)
).
```

Therefore every relation obtained by:

```text
hidden lifted variables
+
subalgebra constraint
+
existential projection
```

is already the decoder image of a **direct visible ternary subalgebra**.

## 5. Barrier theorem

### R5_E8_6I_HIDDEN_LIFT_PROJECTION_BARRIER_V1

Fix visible algebras `A_1,A_2,A_3` and visible decoders `pi_1,pi_2,pi_3`.

If there is no direct ternary subalgebra

```text
S
<=
A_1 x A_2 x A_3
```

such that

```text
(pi_1 x pi_2 x pi_3)(S)
=
R,
```

then there is no hidden-variable lifted construction over arbitrary additional compatible algebra coordinates whose existential visible image is exactly `R`.

Equivalently:

```text
HIDDEN LIFTED AUXILIARIES
DO NOT ENLARGE
EXACT VISIBLE DECODER-IMAGE COVERAGE
WHEN THE VISIBLE ALGEBRAS/DECODERS ARE FIXED.
```

## 6. Consequence for the A3 SBM positive control

The exhaustive A3 checker already classifies direct exact ternary lifts.

For a fixed visible decoder triple:

```text
exact signed 3-clause lift exists
iff
at least two sign-adjusted coarse decoder bits
satisfy the clause.
```

Therefore for any decoder triple failing that condition:

```text
NO DIRECT A3 TERNARY LIFT.
```

By the barrier theorem:

```text
NO NUMBER OF HIDDEN A3/SAME-SIGNATURE
LIFTED AUXILIARY VARIABLES
CAN TURN THAT SAME VISIBLE DECODER TRIPLE
INTO AN EXACT OR3 LIFT.
```

Thus the universal threshold defect:

```text
2_OF_3
->
1_OF_3
```

cannot be repaired merely by:

```text
ADD HIDDEN LIFTED VARIABLES
+
KEEP THE SAME VISIBLE A3 ALGEBRAS
+
KEEP THE SAME VISIBLE DECODERS
+
EXISTENTIALLY PROJECT AUXILIARIES.
```

## 7. What remains genuinely open

The theorem does **not** rule out:

```text
A. different visible lifted algebras;

B. different visible decoder maps;

C. a multi-sorted visible carrier;

D. a different source-bound tractable prototype language;

E. a representation-changing preprocessing theorem
   before algebra assignment;

F. a composition of old mechanisms that changes
   the visible algebraic interface itself.
```

Therefore the active 6I search narrows from:

```text
"maybe auxiliaries repair A3"
```

to:

```text
"find a new visible algebra/decoder interface
or tractable prototype principle
whose direct visible exact lift
already covers ordinary OR3."
```

## 8. Corpus-first interpretation

This theorem is an example of the corpus-first doctrine:

- existential auxiliary variables are an old mechanism;
- projection of subalgebras is an old algebraic fact;
- their composition yields a precise modern E8 barrier;
- novelty is irrelevant;
- the value is that one entire class of bridge attempts is now removed.

## 9. Claim ceiling

```text
A3 HIDDEN-LIFT AUXILIARY REPAIR
=
BLOCKED FOR FIXED VISIBLE ALGEBRAS/DECODERS

A3 UNIVERSAL COVERAGE
=
STILL FAILS

GENERAL LIFTED-DOMAIN / MULTI-SORTED BRIDGE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
