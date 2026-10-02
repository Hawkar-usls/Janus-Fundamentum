# R5 E27 — Projective-Diversity vs Separator Firewall

Date: 2026-10-02

Status:
`EXACT_LINEAR_Q_FIREWALL__E16_RING_HAS_Q_THETA_N__SEPARATOR_BRANCH_STILL_CLOSES`

Scientific ceiling:

```text
THIS NOTE KILLS THE NAIVE HOPE THAT THE R5 E26 FREE KERNEL-PROJECTIVE
DIVERSITY q IS ALWAYS O(log n).

THE CONNECTED R5 E16 k-BLOCK RING HAS
  n = 9k,
  nullity_Q = k+1,
  q = 2k+1 = 2n/9+1.

SO q GROWS LINEARLY.

HOWEVER THE SAME FAMILY HAS THE R5 E16 CONSTANT-SIZE SEPARATOR STRUCTURE,
SO IT REMAINS POLYNOMIALLY DECOMPOSABLE.

THE CORRECT FRONTIER IS THEREFORE HIGH PROJECTIVE DIVERSITY PLUS HIGH ADHESION,
NOT HIGH q ALONE.

P_VS_NP = OPEN.
```

## 1. Recall the R5 E16 family

R5 E16 constructs a connected square+cubic+linear source from `k` copies of the
`3 x 3` toroidal block.  The blocks are linked cyclically by redirecting one
`Q`-incidence per block.

The family satisfies

```text
n = 9k,
nullity_Q(A_k)=k+1,
distance to the displayed commuting centralizer = k,
```

and is Exact-One SAT.

It also has a nontrivial constant-size interface: each block is separated from the
rest by a two-edge cut in the Levi graph.

## 2. Kernel-projective diversity

Let

```text
B in Q^{n x (k+1)}
```

be any basis matrix for the rational kernel and partition its coordinate rows into
projective classes.

The companion exact checker computes these classes for `k=2,...,8` and reveals the
exact pattern

```text
2k classes of size 3,
1 class of size 3k.
```

Hence the number of projective classes is

```text
boxed:
q(A_k)=2k+1.
```

Since `n=9k`,

```text
boxed:
q(A_k)=2n/9+1=Theta(n).
```

Thus the R5 E26 FPT terminal

```text
O(2^q poly(n))
```

cannot by itself be promoted to a universal polynomial algorithm.

## 3. Why this does not refute the router

The E16 family was designed as a firewall against a different false dichotomy:
large nullity does not imply small distance to commuting.

It now supplies a second firewall:

```text
large projective diversity does not imply hardness.
```

Although

```text
q=Theta(n),
```

the interaction between projective classes is arranged through constant-size
interfaces.  The R5 E16 separator branch can therefore compose finite boundary
states exactly in polynomial time.

So this family belongs to

```text
HIGH q + LOW ADHESION,
```

not to the true hard core.

## 4. New two-axis parameter

The post-E26 trade-compression search must track at least two independent axes:

```text
projective diversity q
```

and

```text
adhesion / interface width a.
```

The already known controls occupy different regions:

```text
R5 E25 torus:
  q=O(1),
  global trade support Theta(n),
  algebraically compact.

R5 E16 ring:
  q=Theta(n),
  adhesion O(1),
  separator-decomposable.

R5 E17 hardness gadget:
  large raw nullity,
  but local gauge quotient collapses effective freedom.

R5 E19 Paley lift:
  nonlocal moment firewall,
  but KPROJ/KLOC closes it.
```

Therefore neither support size, raw nullity, nor projective diversity alone is the
right universal complexity measure.

## 5. Updated trade-compression dichotomy target

A genuine survivor should now simultaneously have

```text
q = omega(log n),
no bounded-interface decomposition,
large effective/global kernel after local-gauge quotient,
no KPROJ forcing/equality quotient,
no KLOC-3/4 obstruction,
integer feasibility,
no source-aligned/clique obstruction,
no commuting/near-commuting normal form,
and no known compact global trade parametrization.
```

This motivates a sharper target:

```text
HIGH-q / HIGH-ADHESION TRADE-COMPRESSION DICHOTOMY

For every projectively reduced integer-feasible square+cubic+linear source,
either
  (A) q=O(log n),
  (B) the Levi interaction of projective classes has bounded adhesion,
  (C) a polynomial exact obstruction/forcing rule applies,
  (D) a compact algebraic normal form describes the trade lattice,
  or
  (E) expose an explicit high-q high-adhesion survivor family.
```

Branch (E), not merely high `q`, is now the correct firewall target.

## 6. Next attack

The most useful next experiment is to search specifically for connected carriers
with

```text
q=Theta(n)
```

and Levi edge/vertex connectivity at least three or four after all exact quotient
steps, then test whether KLOC-4, integer saturation, clique/source-aligned
certificates, or commuting-distance terminals close them.

If such a family survives, it becomes the first real high-description trade core.
If every candidate collapses to one of the known branches, that pattern is evidence
for the desired structural dichotomy, but not yet a proof.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e27_e16_projective_diversity_firewall.py
```
