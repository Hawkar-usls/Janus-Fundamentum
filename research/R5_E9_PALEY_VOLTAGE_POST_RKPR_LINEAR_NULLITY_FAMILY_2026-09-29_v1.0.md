# R5 E9 — Paley voltage post-RKPR linear-nullity family

Date: 2026-09-29
Status: PROVED STRUCTURAL FALSIFIER
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## Scope

This note closes one proposed shortcut only. It proves an infinite family of connected square linear-cubic Exact-One sources which:

- pass the global `3 | n` counting prerequisite;
- pass the binary and ternary linear-consistency screens;
- survive rational-kernel projective-ratio pinning (RKPR) with equality classes only;
- have rational nullity linear in source size.

Therefore the route

```text
linear cubic
+ connected
+ parity/phase consistent
+ exhaustive RKPR
=> rational nullity O(log n)
```

is false.

This is **not** a polynomial SAT algorithm and does **not** imply `P=NP`.

---

## 1. Paley(11) seed

Let `T_11` be the Paley tournament on `Z_11`, with arc `i -> j` iff

```text
j-i mod 11 in {1,3,4,5,9}.
```

Let rows be the 55 cyclic directed triangles of `T_11`, and columns be the 55 tournament arcs. Let `A0` be the triangle-versus-arc incidence matrix.

Exact finite arithmetic gives:

```text
shape(A0)        = 55 x 55
row degree       = 3
column degree    = 3
Levi connected   = true
linear source    = true
rank_Q(A0)       = 45
nullity_Q(A0)    = 10
zero kernel rows = 0
projective proportional kernel-row pairs = 0
```

The raw `A0` Exact-One instance is not itself a hard residual because `55` is not divisible by `3`.

---

## 2. A repaired 3-cover B

Order the 55 cyclic triangles lexicographically as 3-subsets of `0,...,10`, and order tournament arcs lexicographically by tail then head. Form a cyclic 3-cover of `A0`. Every incidence has voltage `0` except these eight incidences:

| base row | triangle | base column | arc | voltage mod 3 |
|---:|---|---:|---|---:|
| 14 | `(0,9,10)` | 50 | `(10,0)` | 1 |
| 13 | `(0,7,9)` | 4 | `(0,9)` | 1 |
| 43 | `(3,8,9)` | 44 | `(8,9)` | 1 |
| 44 | `(4,5,6)` | 21 | `(4,5)` | 1 |
| 12 | `(0,5,10)` | 3 | `(0,5)` | 2 |
| 41 | `(3,6,10)` | 52 | `(10,3)` | 1 |
| 8 | `(0,4,7)` | 35 | `(7,0)` | 2 |
| 30 | `(2,5,8)` | 27 | `(5,8)` | 2 |

For an incidence `(r,c)` with voltage `v`, sheet `t` of row `r` is incident with sheet `t+v mod 3` of column `c`.

Call the resulting `165 x 165` incidence matrix `B`.

Exact arithmetic gives:

```text
shape(B)                  = 165 x 165
row degree                = 3
column degree             = 3
Levi connected            = true
linear source             = true
rank_Q(B)                 = 149
nullity_Q(B)              = 16
rank_F2(B)                = 149
rank_F2([B|1])            = 149
rank_F3(B)                = 148
rank_F3([B|1])            = 148
zero rational kernel rows = 0
```

Thus both `B x = 1 (mod 2)` and `B x = 1 (mod 3)` are consistent.

The rational-kernel coordinate rows of `B` have exactly:

```text
28 projective classes of size 3, all with ratio +1;
81 singleton classes;
no ratio -2;
no ratio -1/2;
no illegal projective ratios.
```

Every source row meets three distinct RKPR classes, so equality substitution alone creates no forced pin and no local contradiction.

Take

```text
r* = lifted row 0 = ((0,1,2), sheet 0)
c* = lifted column 0 = ((0,1), sheet 0).
```

The class of `c*` is a singleton. Also

```text
rank_Q([B | e_{r*}]) = 150 > rank_Q(B)=149,
```

so `e_{r*}` is not in the rational column space of `B`.

---

## 3. Infinite one-edge cyclic cover family

For every integer `m >= 1`, define `C_m` as the cyclic `m`-cover of `B` in which all incidences have voltage `0` except the single incidence `(r*,c*)`, which has voltage `1 mod m`.

Equivalently, with `P_m` the cyclic shift permutation matrix,

```math
C_m = B \otimes I_m + E_{r*,c*}\otimes(P_m-I_m).
```

### 3.1 Cubic, linear, connected

Every `C_m` is square and 3-regular on both sides, with

```math
N_m = 165m.
```

A graph cover preserves the absence of 4-cycles, hence linearity of the hypergraph source.

The incidence `(r*,c*)` lies on a cycle of the Levi graph of `B`. Its voltage is `1`, which generates `Z_m`; hence the derived cyclic cover is connected.

Also

```math
3\mid N_m
```

for every `m`, so the global counting prerequisite does not eliminate this family.

### 3.2 Exact rational kernel

Let `K = ker_Q(B)`, so `dim K=16`. For a vector in sheet form `z_0,...,z_{m-1}`, write

```math
s_t=(z_t)_{c*}.
```

If `C_m z=0`, multiply by a left-kernel vector `ell` of `B` with `ell_{r*} != 0`, which exists because `e_{r*}` is not in `col_Q(B)`. This gives

```math
(P_m-I_m)s=0.
```

Hence all `s_t` are equal. The rank-one-cover perturbation then vanishes, and therefore every `z_t` lies in `K`.

Conversely, any `m` vectors `z_t in K` with equal `c*` coordinate give a kernel vector of `C_m`.

Because the `c*` coordinate functional is nonzero on `K`, the equality of its `m` sheet values imposes exactly `m-1` independent conditions. Therefore

```math
\boxed{\nu_Q(C_m)=16m-(m-1)=15m+1.}
```

Since `N_m=165m`,

```math
\nu_Q(C_m)=\frac{N_m}{11}+1.
```

Thus rational nullity remains linear after all stated structural screens.

### 3.3 RKPR structure for every m

The kernel description above also determines every proportional coordinate pair.

- Within one sheet, proportionality is exactly the proportionality already present in `B`: the 28 equality triples and no other ratios.
- Between two different sheets, a non-special coordinate functional can be varied independently by changing the corresponding sheet in `K` while keeping the common `c*` value fixed. Because `c*` is a singleton RKPR class in `B`, such a coordinate cannot become proportional to a coordinate from another sheet.
- The `m` copies of `c*` are equal on every kernel vector and therefore form one equality class of size `m`.

Hence `C_m` has only ratio-`+1` RKPR classes:

```text
28m equality classes of size 3,
1 equality class of size m (the c* fibre),
80m singleton classes,
no zero kernel rows,
no -2 or -1/2 pinning ratios,
no illegal projective ratio.
```

After equality quotient the number of projective variables is

```math
q_m=108m+1,
```

while the rational nullity remains

```math
15m+1=Theta(N_m).
```

Each lifted source row still meets three distinct equality classes, so the equality quotient does not generate an immediate repeated-variable Exact-One pin.

### 3.4 Parity and phase consistency persist

Because `B x = 1` is solvable over both `F_2` and `F_3`, repeat any such base solution identically on all `m` sheets. The special-coordinate fibre is constant, so `(P_m-I_m)` annihilates it. Therefore

```math
C_m x = 1
```

is solvable over both `F_2` and `F_3` for every `m`.

---

## 4. Consequence

The following implication is rigorously falsified:

```text
connected
+ square linear cubic source
+ 3 | n
+ F2 consistency
+ F3 consistency
+ exhaustive RKPR (including equality quotient)
=> rational nullity O(log n).
```

Indeed the explicit family `C_m` satisfies every premise while

```math
\nu_Q(C_m)=N_m/11+1.
```

Therefore generic rational-nullity enumeration remains exponential on this residual class and cannot be promoted to a universal polynomial route merely by adding linearity, parity/phase consistency, connectivity, and RKPR.

The live universal target remains the global witness-selection problem (cycle/endpoint syndrome or an equivalently strong representation change), not another nullity bound.

---

## 5. Epistemic firewall

This theorem is a **negative structural result**. It removes a proposed shortcut and narrows the search space. It does not prove that the family is computationally hard, does not prove a lower bound for SAT, and does not solve P versus NP.

Canonical status after this note:

```text
E8_D1    = EMPTY
P_VS_NP  = OPEN
```
