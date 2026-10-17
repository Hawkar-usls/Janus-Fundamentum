# R5 E9 — Paley(87211) order-13 4-Ore character-gain positive control

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY87211_ORE13_POSITIVE_CONTROL__NO_MINIMALITY_CLAIM__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY5419_EXACT_MINIMUM_BALANCED_4CRITICAL_ORDER10_ORE_CHAIN_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_EXACT_F3_CONSTANT_GRADIENT_KERNEL_AFFINE_CHART_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley87211_ore13_character_gain_positive_control.py`

## 1. Frozen member

Take

```text
q = 87211,
r = -2 mod q,
L = ord_q(r) = 27.
```

Since `3|L`, this is an AF3-consistent Paley-orbit member.  The exact affine chart is again

```text
z = r0 + c + grad(p),
```

with `c in F3`, support connection set

```text
S=<r> union -<r>,
|S|=54,
```

and slice gain `phi_c` defined from the multiplicative-character exponent exactly as in the preceding family artifacts.

## 2. Canonical 4-Ore extension family

Starting from the exact q=5419 order-10 graph

```text
graph6 = ICOcePkL_
```

a K4 Ore-composition is obtained by choosing one vertex, splitting its neighbours into two nonempty parts, and gluing the two split copies to the endpoints of `K4-e`.

Up to graph isomorphism the finite set of such one-step extensions of this particular `G10` has ten types.

A complete exact scan of those ten types found a balanced embedding in every affine slice for

```text
graph6 = LCOcaPkL_AO@_B.
```

The checker freezes a direct construction of this graph, so the result does not depend on any graph catalogue:

```text
split G10 vertex 0,
neighbours {3,6,7} -> {3,6} | {7},
then glue K4-e across the split pair.
```

The resulting graph has

```text
|V|=13,
|E|=21,
```

and the checker independently verifies that it is connected, non-3-colourable, and edge-4-critical.

## 3. Exact gain witnesses

Using graph vertices `0..12` in graph6 order, the checker verifies the following injective embeddings and switching gauges.

### c=0

```text
x=[0,2581,517,1,10757,2561,512,10773,2565,513,65280,65408,87083]
g=[0,2,1,0,1,2,0,0,0,0,0,1,2]
```

### c=1

```text
x=[0,2581,517,1,10757,2561,512,10773,2565,513,54379,54443,87147]
g=[0,1,0,2,2,0,1,0,0,0,0,2,1]
```

### c=2

```text
x=[0,2597,517,1,73424,2561,512,73456,2565,513,65280,65408,87083]
g=[0,1,2,1,2,1,2,0,0,0,0,0,0]
```

For every selected graph edge `uv`, exact arithmetic verifies

```text
x(v)-x(u) in S,
g(v)-g(u)=phi_c(x(v)-x(u)) mod 3.
```

Therefore every one of the three affine slices has a balanced order-13 ordinary 4-critical obstruction.

## 4. Four-member Ore-chain pattern

Together with the earlier exact controls we now have

```text
q=19,    L=9   -> balanced order 4  -> K4
q=331,   L=15  -> balanced order 7  -> Ore(K4,K4)
q=5419,  L=21  -> balanced order 10 -> Ore(K4,G7)
q=87211, L=27  -> balanced order 13 -> Ore(K4,G10)
```

All four satisfy

```text
order = (L-1)/2.
```

This remains a conjectural family pattern, not a theorem.  In particular, this artifact does **not** prove that 13 is the minimum balanced obstruction order for q=87211.

## 5. Next constructive gate

Freeze

```text
R5_E9_PALEY_CHARACTER_ORE_RECURSION_GATE_V2
```

The next task is no longer generic motif enumeration.  It is to derive an algebraic recurrence that maps a balanced Ore witness for orbit length `L` to one for `L+6` directly in the multiplicative-character coordinates.

Concrete next controls:

1. prove the exact relation between the split vertex coordinates and the new three Ore vertices in terms of powers of `r=-2`;
2. test the same recurrence at `L=33` on primes with `ord_q(-2)=33` (for example q=67 and q=20857), without searching arbitrary graph subsets;
3. if the recurrence succeeds, state and prove the family constructor by induction;
4. then return to the real algorithmic question: whether the resulting recursive critical obstruction can be extracted from an arbitrary source instance in polynomial time, not merely from the highly symmetric Paley controls;
5. keep lower-bound/minimality questions separate from existence of the recursive obstruction.

## 6. Ceiling

```text
q=87211 AF3 branch                             = CONSISTENT
balanced order-13 4-Ore obstruction            = PRESENT in all three slices
explicit polynomial-size witness               = YES for this frozen member
minimum balanced critical order                = OPEN
Ore recursion family theorem                   = OPEN
arbitrary-source extractor                      = OPEN
rho_min(Paley87211)                             = OPEN
universal polynomial SAT solver                = NOT PROVED
E8_D1                                          = EMPTY
P_VS_NP                                        = OPEN
```
