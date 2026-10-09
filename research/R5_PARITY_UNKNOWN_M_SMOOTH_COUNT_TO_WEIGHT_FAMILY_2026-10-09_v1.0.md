# R5 Parity — Unknown-M smooth-count to universal bounded weight family

Date: 2026-10-09

Predecessor:
`research/R5_PARITY_FIXED_M_TRADE_SPAN_NORMAL_FORM_2026-10-09_v1.0.md`

Scientific ceiling:

```text
THIS IS A ONE-ROUND WEIGHT-FAMILY LEMMA.
IT DOES NOT PROVE THE REQUIRED SMOOTH-COUNT BOUND.
IT DOES NOT PROVE POLYNOMIAL FULL ISOLATION.
P_VS_NP = OPEN.
```

## 1. Problem

The fixed-M structural normal form is useful for proof, but the algorithm does
not know a minimum perfect matching M.

A priori this looked fatal to any hashing lemma that first enumerated the
relevant M-trades and then selected a good hash.

Enumeration is not necessary.

## 2. Universal family lemma

Index the n global target variables by 0,...,n-1.

Assume a theorem supplies a uniform polynomial upper bound

```text
|D(M)| <= L(n)
```

for the relevant nonzero signed trade vectors for every possible minimum
matching M of every current minimum face.

No algorithm for finding M or enumerating D(M) is assumed.

Choose a prime

```text
p > (n-1)L(n),  p>2.
```

For every t in F_p define one global integer weight vector

```text
w_t(i) = t^i mod p,   0 <= w_t(i) < p.
```

For a nonzero trade d in {-1,0,1}^n define

```text
f_d(T) = sum_i d_i T^i in F_p.
```

Since p>2 and d is nonzero, f_d is a nonzero polynomial of degree at most n-1
and therefore has at most n-1 roots.

For a fixed but unknown M, all trades in D(M) together forbid fewer than

```text
(n-1)L(n) < p
```

values of t.

Hence at least one t in F_p satisfies

```text
<w_t,d> != 0 mod p
```

for every d in D(M).

Because a nonzero residue implies the ordinary integer circulation is nonzero,
that weighting kills every relevant trade in D(M).

Therefore the canonical family

```text
W_p = { w_t : t in F_p }
```

contains a successful member for every possible unknown M.

## 3. Constructivity

If L(n)=n^c for a fixed c, then:

* p can be chosen polynomially bounded;
* |W_p|=p=n^{O(1)};
* every weight is <p=n^{O(1)};
* W_p is generated in polynomial total time;
* construction does not query SAT, a perfect matching, the minimum face, or a
  trade-enumeration oracle.

Thus for the isolation route the desired smooth-count theorem need only give a
uniform polynomial COUNT bound with an explicit polynomial exponent.

It does not need to provide an enumeration algorithm.

## 4. Interaction with fixed-M analysis

The fixed-M graph R_M and block system B_m may therefore be used entirely as
an analysis object.

A proof may say:

```text
for an arbitrary minimum M,
the number of relevant near-minimum zero-circulation trades is <= L(n).
```

The actual algorithm still emits the same M-independent family W_p.

This removes the hidden circularity "find M in order to derandomize the
isolation needed to find M."

## 5. Remaining composition gap

This lemma is one-round.

If a successful weighting increases trade girth only by a constant factor,
then O(log n) successive refinement rounds are still needed.

Naively branching over all p choices at every round produces

```text
p^{O(log n)} = n^{O(log n)}
```

combined choices, i.e. a quasipolynomial family.

Encoding O(log n) lexicographic rounds into one integer weight similarly makes
the weight range quasipolynomial in the naive construction.

Therefore:

```text
POLYNOMIAL ONE-ROUND UNIVERSAL FAMILY = PROVED CONDITIONALLY ON SMOOTH COUNT.
POLYNOMIAL FULL ISOLATING FAMILY = STILL OPEN.
```

A full polynomial route still needs at least one of:

1. a constant-number-of-rounds jump;
2. an additive separator recursion handled without multiplicative weight-family
   branching;
3. a direct one-shot smooth-count theorem covering all relevant scales;
4. another composition theorem compressing the O(log n) refinements into a
   polynomial family.

## 6. Claim boundary

```text
UNKNOWN_M_IS_NOT_AN_OBSTRUCTION_TO_ONE_ROUND_HASHING = PROVED.
EXPLICIT_TRADE_ENUMERATION_IS_NOT_REQUIRED_FOR_ONE_ROUND_HASHING = PROVED.

TRADE_SMOOTH_COUNT = OPEN BEYOND THE LOGARITHMIC TERMINAL.
SPAN/INTEGER_SEPARATOR DICHOTOMY = OPEN.
POLYNOMIAL FULL ISOLATION = OPEN.
P_VS_NP = OPEN.
```
