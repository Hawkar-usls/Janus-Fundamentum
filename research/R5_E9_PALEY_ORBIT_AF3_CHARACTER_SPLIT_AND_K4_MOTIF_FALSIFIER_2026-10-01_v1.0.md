# R5 E9 — Paley-orbit AF3 character split and gain-K4 motif falsifier

Date: 2026-10-01

Status:
`JANUS_EXACT_FAMILY_SPLIT_AND_SOURCE_SPECIFIC_MOTIF_FALSIFIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY_ORBIT_GRADIENT_KERNEL_INFINITE_POST_RKPR_FAMILY_2026-09-29_v1.0.md`
- `research/R5_E9_AFFINE_F3_PALEY19_EXACT_MINIMUM_COVER_RANK6_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley_orbit_af3_character_split_k4_falsifier.py`

## 1. Frozen family

Use the existing Paley-orbit family for a prime `q>3`, `q=3 mod 8`, with

```text
r=-2 mod q,
O=<r> subset QR(q),
L=ord_q(-2),
variables X(t,s), t in Z_q, s in O,
constraints C(t,s)={X(t,s),X(t+s,s),X(t+2s,rs)}.
```

The family is square, cubic, linear, Levi-connected, RKPR-clean and has exact rational gradient kernel.

This note studies only the affine-F3 equation

```text
A z = 1.
```

## 2. Exact AF3 consistency split

### Theorem

For the frozen orbit source,

```text
A z = 1 over F3
```

is consistent if and only if

```text
3 divides L=ord_q(-2).
```

### Necessity

Every column has degree three, hence over `F3`

```text
1^T A = 0.
```

If `A z=1`, left multiplication by `1^T` gives

```text
0 = number_of_rows = qL mod 3.
```

Because `q>3` is prime, `q!=0 mod 3`, so `L=0 mod 3`.

### Sufficiency

Assume `3|L`. Choose one orbit representative `s0` and define a translation-invariant particular solution on the difference orbit by

```text
r0(r^k s0)=k mod 3.
```

One source row has differences `s,s,rs`, so

```text
2 r0(s)+r0(rs)
=2k+(k+1)
=1 mod 3.
```

The definition is consistent around the orbit exactly because `3|L`. Therefore `A r0=1`.

Thus the AF3 branch of the infinite Paley-orbit family splits polynomially at once:

```text
3 does not divide L  -> linear inconsistency terminal;
3 divides L          -> genuine affine-hyperplane avoidance branch.
```

## 3. Relation to Paley19

For `q=19`,

```text
L=9,
O=QR(19).
```

Hence the affine system is consistent. After an additive constant / generator reindexing, the recurrence above is exactly the order-three multiplicative-character particular solution used in the Paley19 minimum-rank-six theorem.

The three gain-K4 cover found there is therefore a character-compatible source motif, not an arbitrary finite accident.

## 4. The motif is not universal across the frozen family

Take

```text
q=331.
```

Then

```text
331=3 mod 8,
L=ord_331(-2)=15,
3 divides L.
```

So `q=331` lies in the genuine AF3-consistent branch and has the canonical character particular solution.

Let the underlying variable-support graph be

```text
Gamma_331 = Cay(Z_331, S),
S=O union (-O).
```

Here

```text
|O|=15,
|S|=30.
```

A gain-K4 obstruction requires a `K4` in this support graph before gain consistency can even be tested.

By translation invariance any `K4` can be translated to contain vertex zero. Its other three vertices must be three elements of `S` which are pairwise adjacent. Hence it is sufficient and complete to enumerate

```text
C(30,3)=4060
```

triples in the neighbourhood of zero.

Exact result:

```text
K4 containing 0 = 0.
```

Therefore

```text
Gamma_331 is K4-free,
```

and no gain-K4 obstruction exists for any of the three `c`-slices.

Consequently the Paley19 motif

```text
three character-shifted gain-K4 obstructions
```

is **not** a universal terminal for the already frozen infinite Paley-orbit source family.

## 5. Consequence

The family-level structural target must move one level up:

```text
character-compatible 4-critical gain obstructions
```

rather than `K4` specifically.

A selected edge family whose gains are a coboundary becomes, after gauge shift, an ordinary graph 3-colouring obstruction. Paley19 realizes the smallest such obstruction `K4`; q=331 proves that any universal theorem must permit other 4-critical graphs or genuinely non-coboundary gain obstructions.

## 6. Next constructive gate

Freeze

```text
R5_E9_PALEY_AF3_4CRITICAL_GAIN_OBSTRUCTION_GATE_V1
```

For every AF3-consistent orbit member (`3|L`):

1. build the exact gain graph from the character particular solution;
2. search in increasing fixed size for source-supported 4-critical coboundary subgraphs (odd wheels first, then the finite catalog of small 4-critical graphs);
3. require a polynomial recognition/construction algorithm, not subset enumeration as the final theorem;
4. if the minimum obstruction size grows with `q`, measure that growth and test whether a bounded-rank cover theorem is false;
5. in parallel allow non-coboundary gain obstructions, because q=331 only kills the `K4` subclass;
6. keep the prime SAT/UNSAT lift towers as independent source controls.

The success condition is a family theorem producing, from source incidence, a polynomial-size unsatisfiability cover/witness without exponential search.

## 7. Ceiling

```text
Paley-orbit AF3 consistency iff 3|ord_q(-2) = PROVED
Paley19 gain-K4 motif                       = EXACT
q=331 AF3 consistent                        = YES
q=331 support K4                            = NONE
universal gain-K4 terminal                  = FALSIFIED
universal 4-critical gain terminal          = OPEN
universal polynomial solver                 = NOT PROVED
E8_D1                                       = EMPTY
P_VS_NP                                     = OPEN
```
