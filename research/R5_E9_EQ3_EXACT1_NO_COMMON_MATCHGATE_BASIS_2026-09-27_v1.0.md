# R5 E9 — No Common Matchgate Basis for EQ3 / EXACT1_3

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_HOLOGRAPHIC_ANTI_LOOP__DIRECT_MATCHGATE_ESCAPE_CLOSED`

Scientific ceiling:

```text
THIS RULES OUT THE DIRECT COMMON-2x2-BASIS MATCHGATE ROUTE.
IT DOES NOT RULE OUT NON-MATCHGATE ALGEBRAIC ALGORITHMS.
IT DOES NOT PROVE P != NP.
P_VS_NP = OPEN.
```

## 1. Signatures

On the cubic Levi factor graph, variable nodes carry

```text
EQ3 = {000,111}
```

and clause nodes carry

```text
EXACT1_3 = {001,010,100}.
```

In symmetric-signature notation these are

```text
EQ3      = [1,0,0,1],
EXACT1_3 = [0,1,0,0].
```

A standard matchgate signature necessarily satisfies the parity condition: its support is contained entirely in even Hamming weights or entirely in odd Hamming weights. For arity three this condition is already mandatory before the remaining matchgate identities are considered.

## 2. General holographic basis

Let

```text
T = [[a,b],[c,d]]
```

be an invertible complex 2x2 matrix, with determinant

```text
Delta = ad-bc != 0.
```

For a bipartite holographic transformation, one shore is transformed by `T` and the other by `T^{-1}` (up to the standard transpose convention, irrelevant here because both signatures are symmetric). It is enough to ask whether

```text
T^(tensor 3) EXACT1_3
```

can be a matchgate signature while

```text
(T^{-1})^(tensor 3) EQ3
```

is also a matchgate signature.

## 3. Transform of EXACT1_3

The transformed symmetric entries by output Hamming weight k=0,1,2,3 are

```text
G0 = 3 a^2 b,
G1 = a^2 d + 2abc,
G2 = b c^2 + 2acd,
G3 = 3 c^2 d.
```

### Even-parity case

An even matchgate requires

```text
G1=G3=0.
```

From `G3=3c^2d=0`:

- if `c=0`, invertibility forces `a,d !=0`, but then `G1=a^2d !=0`, contradiction;
- hence `d=0`. Invertibility then forces `b,c !=0`, and `G1=2abc=0` forces `a=0`.

Therefore the only invertible bases making transformed EXACT1_3 even-parity are anti-diagonal:

```text
T = [[0,b],[c,0]],  bc !=0.
```

### Odd-parity case

An odd matchgate requires

```text
G0=G2=0.
```

From `G0=3a^2b=0`:

- if `a=0`, invertibility forces `b,c !=0`, but then `G2=bc^2 !=0`, contradiction;
- hence `b=0`. Invertibility forces `a,d !=0`, and `G2=2acd=0` forces `c=0`.

Therefore the only invertible bases making transformed EXACT1_3 odd-parity are diagonal:

```text
T = [[a,0],[0,d]],  ad !=0.
```

## 4. EQ3 cannot pass on either surviving basis

If `T` is diagonal, then `T^{-1}` is diagonal and transformed EQ3 still has precisely two nonzero entries, at weights zero and three:

```text
[alpha,0,0,beta],  alpha*beta !=0.
```

These weights have opposite parity, so the matchgate parity condition fails.

If `T` is anti-diagonal, then `T^{-1}` is anti-diagonal and merely swaps/scales the two EQ3 support points. Its transformed signature again has nonzero support at weights zero and three, so the parity condition again fails.

Hence:

### Theorem MGB-1

There is no invertible complex 2x2 holographic basis `T` for which `EXACT1_3` on one shore and `EQ3` on the other shore are simultaneously matchgate-realizable.

The result is independent of planarity: the obstruction occurs locally at arity three before any global Pfaffian orientation question is reached.

## 5. External source binding

The matchgate parity condition is standard and necessary. See, for example, Cai and Gorenstein, *Matchgates Revisited*, Theory of Computing 10 (2014): a standard signature is matchgate-realizable only if all entries of one Hamming-weight parity vanish; matchgate identities imply this parity condition.

This note uses only that necessary condition, so no stronger matchgate classification assumption is required.

## 6. Consequence

The tempting route

```text
linear-cubic Exact-One factor graph
-> one global holographic basis
-> ordinary matchgate network
-> Pfaffian/perfect-matching polynomial algorithm
```

is closed in this direct form.

Do not reopen it by trying Hadamard or another 2x2 basis: the calculation above quantifies over every invertible complex basis.

This does not rule out:

- a non-matchgate algebraic representation;
- a source-specific higher-domain transformation with separately proved polynomial evaluation;
- bounded-genus / planar special terminals;
- polynomial semantic compression by a mechanism unrelated to Pfaffians.

## 7. Ceiling

```text
COMMON 2x2 HOLOGRAPHIC MATCHGATE BASIS FOR EQ3 / EXACT1_3
= IMPOSSIBLE / PROVED

DIRECT PFAFFIAN-MATCHGATE UNIVERSAL ROUTE
= CLOSED

UNIVERSAL POLYNOMIAL DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
