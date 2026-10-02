# R5 E9 — IF2E terminal is not global: exact three-external hostile control

Date: 2026-09-29

Status: `JANUS_EXACT_FINITE_SOURCE_VALID_COUNTERCONTROL__TWO_EXTERNAL_LOCAL_TO_GLOBAL_FALSIFIED__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_INDEPENDENT_FLAT_TWO_EXTERNAL_AUGMENTATION_ROUTER_2026-09-29_v1.0.md`

Checker:
- `experiments/r5_e9_independent_flat_two_external_augmentation.py`

Scientific ceiling:

```text
THIS IS A FINITE EXACT COUNTEREXAMPLE TO THE CLAIM
"IF2E TERMINAL => GLOBAL AFFINE-COSET MINIMUM".
IT DOES NOT RULE OUT HIGHER-LOCALITY OR NONLOCAL POLYNOMIAL AUGMENTATION.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source-valid n=15 carrier

Use `A=I+P+Q` with zero-based permutations

```text
P = [14,5,13,10,11,6,3,1,12,8,2,7,0,4,9]
Q = [ 7,8,11,13,14,0,1,12,3,2,6,9,4,5,10].
```

Every row and column has degree three; the three row entries are distinct; every pair of rows intersects in at most one column. Thus this is a square linear-cubic source instance.

Exact GF(2) elimination gives

```text
rank_F2(A)=13,
nullity_F2(A)=2.
```

The four kernel vectors have weights

```text
0, 6, 8, 8.
```

Hence the all-ones syndrome coset has true minimum weight

\[
15-8=7.
\]

Exhaustive Boolean verification finds zero Exact-One models; this is an UNSAT control, but the statement below concerns affine-coset optimization rather than the Exact-One verdict itself.

## 2. Deterministic IF2E replay

Start from the canonical syndrome-one point

```text
x0 = 1^15.
```

The deterministic Gaussian-elimination ordering used by the checker first removes the kernel support

```text
{2,3,5,6,8,13}
```

and reaches

```text
S = {0,1,4,7,9,10,11,12,14},
|S|=9.
```

The checker certifies exactly that:

1. `S` is independent;
2. `S` is closed in the ordinary column matroid;
3. no negative zero-external circuit exists;
4. no negative one-external circuit exists;
5. no negative two-external circuit exists.

So `S` is a genuine IF2E terminal.

## 3. Exact missing three-external circuit

A global minimum syndrome support is

```text
S* = {0,4,5,6,9,12,13},
|S*|=7.
```

Their symmetric difference is

```text
C = S triangle S*
  = {1,5,6,7,10,11,13,14}.
```

The checker verifies

```text
A 1_C = 0 mod 2.
```

Relative to the current support `S`, the circuit has

```text
inside / removed = {1,7,10,11,14}  size 5,
outside / added  = {5,6,13}         size 3.
```

Therefore

\[
\boxed{\Delta_S(C)=3-5=-2.}
\]

The same checker verifies that `C` is inclusion-minimal among nonzero kernel supports, hence it is a binary matroid circuit.

Thus the first improving move missed by IF2E uses **exactly three external elements**.

## 4. Consequence

The implication

```text
independent flat
+ no negative two-external circuit
=> global affine-coset minimum
```

is false even on the exact square linear-cubic source class.

The IF2E router remains valid and useful as polynomial preprocessing. What is falsified is only its promotion to a complete optimizer.

Freeze the next locality layer:

```text
R5_E9_THREE_EXTERNAL_NEGATIVE_CIRCUIT_ROUTER_GATE_V1
```

A fixed-three scan is still polynomial (`O(n^3)` candidate external triples times polynomial linear algebra), so the immediate next test is whether exhausting 3-external negative circuits gives a global theorem or whether a source-valid 4+-external hostile local minimum exists.

## 5. Ceiling

```text
IF2E ROUTER
= VALID POLYNOMIAL PREPROCESSING

IF2E TERMINAL => GLOBAL
= FALSIFIED

SMALLEST MISSING MOVE ON FROZEN CONTROL
= EXACTLY 3 EXTERNAL ELEMENTS

THREE-EXTERNAL ROUTER
= POLYNOMIALLY IMPLEMENTABLE

CONSTANT UNIVERSAL LOCALITY BOUND
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
