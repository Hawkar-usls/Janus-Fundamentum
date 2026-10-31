# R5 E9 — Paley-orbit L=33 order-16 4-Ore character-gain positive control

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY_L33_ORE16_POSITIVE_CONTROL__TWO_PRIME_REPLAY__NO_MINIMALITY_CLAIM__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY87211_ORE13_CHARACTER_GAIN_POSITIVE_CONTROL_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY5419_EXACT_MINIMUM_BALANCED_4CRITICAL_ORDER10_ORE_CHAIN_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley_l33_ore16_character_gain_positive_control.py`

## 1. Two independent L=33 prime controls

Use

```text
q=67     with ord_q(-2)=33,
q=20857  with ord_q(-2)=33.
```

Both are prime and AF3-consistent because `3|33`.

For q=67 the support set `S=< -2 > union -< -2 >` is all 66 nonzero field elements.  This is therefore a deliberately degenerate dense sanity control.

For q=20857 the same orbit length gives only 66 supported differences out of 20856 nonzero field elements.  This is the nontrivial sparse control.

## 2. Recursive Ore16 graph

Start from the exact order-13 witness

```text
graph6 = LCOcaPkL_AO@_B.
```

Split vertex `0`, whose neighbours are

```text
{3,6,11,12},
```

into the fixed partition

```text
{3,6} | {11,12},
```

and glue a new `K4-e` across the split pair.  With the inherited labelling and new vertices `13,14,15`, the resulting graph is

```text
graph6 = OCOcaPkL_A?@?B?@o?K?B.
```

It has

```text
|V|=16,
|E|=26,
```

and is an exact one-step 4-Ore extension of the order-13 graph.  The checker independently verifies connectedness, non-3-colourability, and edge-4-criticality.

## 3. Exact q=20857 sparse-control embeddings

For the nontrivial q=20857 member the checker verifies the following translation/switching-normalized embeddings.

### c=0

```text
x=[0,4099,2050,1,2051,4097,2048,2052,4098,2049,4915,4923,9396,9404,10428,19833]
g=[0,1,2,0,2,1,2,2,1,2,0,0,2,2,1,1]
```

### c=1

```text
x=[0,4099,2050,1,2051,4097,2048,2052,4098,2049,1540,13435,13451,4489,8,4481]
g=[0,0,1,2,0,2,0,2,1,2,1,1,2,2,1,1]
```

### c=2

```text
x=[0,4099,2050,1,6146,4097,2048,6147,4098,2049,14339,14467,2607,2735,11732,11860]
g=[0,2,0,1,2,0,1,0,1,2,0,0,2,2,1,1]
```

On every graph edge `uv`, exact modular arithmetic verifies

```text
x(v)-x(u) in S,
g(v)-g(u)=phi_c(x(v)-x(u)) mod 3.
```

The exact normalized DFS found these witnesses after respectively

```text
25345,
39265,
8618
```

recursive states.  These counts are regression controls, not complexity claims.

## 4. q=67 dense sanity control

The same Ore16 graph embeds in all three q=67 slices.  Because its support graph is complete, q=67 is not used as evidence that sparse Paley geometry alone forces the construction; it is only a second exact arithmetic replay of the L=33 character labels.

## 5. Five-step structural sequence

The exact positive controls now give

```text
L=9   -> order 4  -> K4
L=15  -> order 7  -> Ore(K4,K4)
L=21  -> order 10 -> Ore(K4,G7)
L=27  -> order 13 -> Ore(K4,G10)
L=33  -> order 16 -> Ore(K4,G13)
```

and every displayed order satisfies

```text
order=(L-1)/2.
```

This is still **not** a family theorem and does not establish minimum order at L=27 or L=33.

## 6. New constructive frontier

The next target is not another graph catalogue.  Freeze

```text
R5_E9_PALEY_CHARACTER_ORE_RECURSION_GATE_V3
```

and derive a symbolic induction step in multiplicative-character coordinates:

```text
balanced G_{(L-1)/2}
    -> balanced Ore(K4,G_{(L-1)/2})
    = balanced G_{(L+5)/2}
```

for the next admissible orbit length `L+6`.

The proof obligation is to express the split vertex, its two inherited neighbour classes, and the three new Ore vertices by fixed algebraic functions of powers of `r=-2`, rather than discovering them by DFS.

Only after such a constructor is proved should this Paley control line be considered for transfer back to arbitrary AF3 source instances.

## 7. Ceiling

```text
L=33 Ore16 sparse q=20857 control              = PASS for c=0,1,2
L=33 Ore16 dense q=67 sanity control            = PASS for c=0,1,2
five-step Ore-chain positive-control sequence   = ESTABLISHED
symbolic Ore recursion theorem                  = OPEN
minimum balanced order at L=33                  = OPEN
arbitrary-source polynomial extractor           = OPEN
universal polynomial SAT solver                 = NOT PROVED
E8_D1                                           = EMPTY
P_VS_NP                                         = OPEN
```
