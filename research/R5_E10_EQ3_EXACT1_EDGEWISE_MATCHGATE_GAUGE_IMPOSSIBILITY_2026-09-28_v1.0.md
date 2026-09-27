# R5 E10 — EQ3 / Exact1 Edge-wise Matchgate Gauge Impossibility

Date: 2026-09-28

Status:
`JANUS_DERIVED_EXACT_GLOBAL_GAUGE_BARRIER__EDGEWISE_MATCHGATE_ROUTE_CLOSED`

Scientific ceiling:

```text
THIS RULES OUT THE INSTANCE-SPECIFIC EDGE-GAUGE -> TERNARY MATCHGATE ROUTE
FOR THE EQ3 | EXACT1_3 HOLANT FORM OF LINEAR-CUBIC POSITIVE 1-IN-3.
IT DOES NOT RULE OUT OTHER CANCELLATIVE CARRIERS.
NO UNIVERSAL POLYNOMIAL SAT DECIDER IS CLAIMED.
P_VS_NP = OPEN.
```

## 1. Exact Holant form

Represent each source variable by

```text
EQ3 = |000> + |111>
```

and each Exact-One clause by

```text
W = EXACT1_3 = |100> + |010> + |001>.
```

Each incidence edge carries one Boolean index.

Allow an arbitrary invertible edge gauge `T_e in GL_2(C)` on the variable side and the inverse-transpose gauge `(T_e^{-1})^T` on the clause side, so the total contraction is exactly preserved.

Assume, for contradiction, that all transformed ternary signatures are matchgate signatures.

For arity three, every nonzero matchgate signature obeys the parity condition: its support lies entirely in the even or entirely in the odd Hamming-weight sector. Equivalently it is an eigenvector of

```text
Z tensor Z tensor Z,
Z = diag(1,-1),
```

with eigenvalue `+1` or `-1`.

For an edge define

```text
X_e = T_e^{-1} Z T_e.
```

Then

```text
X_e^2 = I,
tr(X_e)=0.
```

On the clause side the pulled-back parity observable is exactly `X_e^T`.

## 2. GHZ product-symmetry lemma

### Lemma G-1

Let `X_1,X_2,X_3` be invertible traceless involutions. If

```text
(X_1 tensor X_2 tensor X_3) EQ3 = eps EQ3,
eps in {+1,-1},
```

then every `X_i` is anti-diagonal in the computational basis:

```text
X_i = [[0,b_i],[b_i^{-1},0]]
```

for some nonzero `b_i`, and the product parameters satisfy

```text
b_1 b_2 b_3 = eps.
```

(up to the equivalent simultaneous sign convention).

### Proof

`EQ3` has tensor rank two and its two product summands

```text
|000>, |111>
```

form the unique two-term product decomposition up to rescaling and permutation of the two summands. Therefore a local invertible product operator stabilizing `EQ3` must either:

1. preserve both product lines on every leg; or
2. swap the two product lines on every leg.

In the preserve branch each `X_i` is diagonal. Since it is a traceless involution, it is `+Z` or `-Z`. On three legs the eigenvalues of `|000>` and `|111>` then differ by a factor `(-1)^3=-1`, so their sum cannot be an eigenvector. The preserve branch is impossible.

Hence all three local operators swap `|0>` and `|1>`, i.e. each is anti-diagonal. Writing

```text
X_i = [[0,b_i],[c_i,0]]
```

and using `X_i^2=I` gives `b_i c_i=1`, hence `c_i=b_i^{-1}`. Acting on `EQ3` gives the stated product constraint. QED.

## 3. Clause contradiction

Every incidence edge is incident with an `EQ3` variable node. By Lemma G-1, **every edge observable `X_e` in the whole network is anti-diagonal**.

Therefore every transpose `X_e^T` is also anti-diagonal.

But an anti-diagonal one-qubit operator swaps the computational basis lines:

```text
|0> -> nonzero multiple of |1>,
|1> -> nonzero multiple of |0>.
```

Hence a tensor product of three anti-diagonal operators maps every weight-one basis vector to a weight-two basis vector. Consequently

```text
(X_1^T tensor X_2^T tensor X_3^T) W
```

is supported entirely on Hamming weight two.

It cannot equal `+W` or `-W`, because `W` is nonzero and supported entirely on Hamming weight one.

Contradiction.

## 4. Main theorem

### EDGEWISE_MATCHGATE_GAUGE_IMPOSSIBILITY

For any cubic `EQ3 | EXACT1_3` Holant network, on any underlying graph and over any characteristic-zero field containing the required gauge entries, there is **no** assignment of invertible edge gauges

```text
{T_e : e in E}
```

such that every transformed variable tensor and every transformed clause tensor is a ternary matchgate signature.

The obstruction is local-to-global and topology-independent.

## 5. Consequence for JANUS

The earlier common-basis barrier is strictly strengthened:

```text
ONE COMMON HOLOGRAPHIC BASIS        = IMPOSSIBLE
ARBITRARY INSTANCE-SPECIFIC EDGE GAUGES -> MATCHGATES = IMPOSSIBLE
```

Therefore the E10 cancellative route may not return to a Pfaffian/matchgate target merely by allowing a separate `GL_2` gauge on each incidence edge.

Still open are genuinely different cancellative targets, e.g. a non-matchgate determinant/group-algebra invariant or another certified polynomial zero-test representation.

## 6. Checker

Finite/exact sanity checker:

`experiments/r5_e10_eq3_exact1_edgewise_matchgate_gauge_impossibility.py`

It verifies with exact rational arithmetic that:

- anti-diagonal traceless involutions satisfying the product constraint stabilize `EQ3`;
- their transposes send every weight-one basis vector to weight two;
- therefore they cannot stabilize `EXACT1_3` under the parity observable condition.

The arbitrary-gauge theorem is the proof above, not finite enumeration.

## 7. Ceiling

```text
EDGE-WISE GL2 GAUGE DISCOVERY
-> ALL TERNARY MATCHGATES
= IMPOSSIBLE

COMMON-BASIS MATCHGATE ROUTE
= SUBSUMED / CLOSED

NON-MATCHGATE GLOBAL CANCELLATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
