# R5 E8 — Net Projection Charge Identity and Initial Power-of-Two Selector Theorem

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_THEOREM__FROZEN_STRUCTURAL_AIG_ONLY__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

PR lineage: `#510 / codex/r5-e8-direct-contract-20260921-82493a57`

Parent objects:

- `research/tools/r5_e8_frozen_structural_aig_executor.py`
- `research/R5_B1B1C5B2B2_E8_CYCLIC_POWER_OF_TWO_SELECTOR_PREFIX_GATE_2026-09-22_v1.0.json`
- `research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`

## 1. Exact net-projection charge identity

Let `S` be a frozen live structural-AIG state with root `r`, and let

```text
N = |Reach(r)|
```

where reachable variable nodes and AND nodes are counted and constants are excluded, exactly as in the frozen executor.

For a currently reachable variable `v`, define:

```text
A_v
=
number of reachable AND gates whose transitive fanin contains v.
```

Let the isolated trial projection be

```text
Q_v
=
OR(
  Restrict(S,v=0),
  Restrict(S,v=1)
).
```

Define:

```text
kappa_v
=
number of old v-independent reachable nodes
that are not reachable from Q_v.

new_v
=
number of Q_v-reachable nodes
that were not already reachable in S.

sigma_v
=
(2 A_v + 1) - new_v.
```

The quantity `sigma_v` is the exact structural saving against the frozen worst-case allocation budget: at most one rebuilt node per dependent AND gate in each cofactor, plus at most one final OR node.

### Theorem

For every currently reachable `v`:

```text
cost(v)
=
|Reach(Q_v)|

=
N + A_v - sigma_v - kappa_v.
```

### Proof

All old reachable dependent AND gates disappear from the restricted result, and the old variable node `v` itself disappears. Hence old nodes lost are exactly

```text
A_v + 1 + kappa_v.
```

By definition the number of genuinely new reachable nodes is

```text
2 A_v + 1 - sigma_v.
```

Therefore

```text
cost(v)
=
N
- (A_v + 1 + kappa_v)
+ (2 A_v + 1 - sigma_v)

=
N + A_v - sigma_v - kappa_v.
```

QED.

### General absent-variable form

If `delta_v` is 1 when the variable node `v` is reachable and 0 otherwise, the exact identity is

```text
cost(v)
=
N + A_v + 1 - delta_v - sigma_v - kappa_v.
```

The E8 scheduler theorem concerns actually present unresolved variables, so `delta_v=1` and the shorter identity above applies.

## 2. Net charge

Define

```text
E_v
=
A_v - sigma_v - kappa_v.
```

For all trial variables in the same current state `S`, `N` is common. Hence the primary greedy key compares exactly `E_v`.

The frozen selector is therefore equivalent to the lexicographic key

```text
(
  E_v,
  A_v,
  variable_id(v)
)
```

for currently present variables.

This replacement is exact, not heuristic.

## 3. Initial state of the cyclic power-of-two family

Let

```text
m = 2^r,  r >= 2
```

and

```text
F_m =
AND_i [
  ( x_i OR z_i OR NOT z_{i+1} )
  AND
  ( NOT x_i OR z_{i+2} OR NOT z_{i+3} )
]
```

with payload indices cyclic modulo `m`.

The frozen compiler first forms two 3-clause AIGs per selector, then their block

```text
G_i
=
C_i^+ AND C_i^-,
```

then a complete balanced AND tree over `G_1,...,G_m`.

### Initial live size

Each power-of-two instance has:

```text
2m variable nodes
4m clause-AIG AND gates
m block gates G_i
m-1 block-tree gates.
```

Therefore

```text
N_0
=
8m - 1.
```

## 4. Exact selector profile at step 0

Each selector `x_i` occurs in exactly the two 3-clauses of one block `G_i`.

Its dependent cone contains:

```text
4 clause-AIG gates
1 block gate G_i
r block-tree ancestors.
```

Hence

```text
A_x
=
r + 5.
```

After either restriction, the local selector block reduces to its corresponding two-literal payload clause. Across the two cofactors, the frozen construction creates exactly

```text
2r + 3
```

new reachable nodes in total, including the final Shannon OR node.

Thus

```text
sigma_x
=
2(r+5)+1-(2r+3)
=
8.
```

At the initial state no old independent node is lost, so

```text
kappa_x
=
0.
```

Therefore

```text
E_x
=
A_x - sigma_x
=
r - 3.
```

and

```text
cost(x_i)
=
N_0 + r - 3
=
8m + r - 4.
```

All selectors tie on the first two coordinates, so among selectors the frozen ID rule prefers `x_1`.

## 5. Initial payload lower bound

Fix payload `z_j`.

It occurs in exactly four selector blocks:

```text
G_j,
G_{j-1},
G_{j-2},
G_{j-3}
```

with cyclic indices.

Let

```text
D_j
=
number of dependent clause-AIG gates
inside those four 3-clauses.

U_j
=
number of dependent block-tree gates
strictly above the four G-block roots.
```

All four `G)-roots are dependent on `z_j`, so

```text
A_{z_j}
=
D_j + 4 + U_j.
```

For the frozen 3-clause encoding, direct local case analysis gives

```text
D_j in {4,6,8}.
```

Under either payload restriction, all savings occur inside the four affected clause/block neighborhoods; the complete upper block-tree is rebuilt without semantic collapse. The exact frozen local count is

```text
sigma_{z_j}
=
D_j + 8.
```

Also

```text
kappa_{z_j}
=
0
```

at the initial state.

Hence

```text
E_{z_j}
=
A_{z_j} - sigma_{z_j}

=
(D_j + 4 + U_j)
-
(D_j + 8)

=
U_j - 4.
```

Now the four support blocks are four distinct leaves of the complete `m=2^r` block tree. The minimum possible number of internal block-tree nodes in the union of their root paths occurs when the four leaves are one aligned depth-2 complete subtree. In that case:

```text
U_j
=
2 pair parents
+ 1 four-block parent
+ (r-2) ancestors to the global root

=
r + 1.
```

Therefore for every payload variable:

```text
U_j >= r+1
```

and so

```text
E_{z_j}
>=
r - 3
=
E_x.
```

If equality holds, then

```text
A_{z_j}
=
D_j + 4 + U_j
>=
4 + 4 + (r+1)
=
r+9
>
r+5
=
A_x.
```

Thus a payload can at best tie a selector on the primary projected-size coordinate; it then loses on the frozen cone-size tie-break.

## 6. Initial selector theorem

### Theorem

For every

```text
m = 2^r >= 4,
```

the first frozen exact-greedy choice on `F_m` is a selector variable, and the canonical ID tie-break chooses

```text
x_1.
```

Equivalently:

```text
STEP_0_SELECTOR_WIN
=
PROVED FOR ARBITRARY r>=2.
```

This is an arbitrary-size theorem, not finite extrapolation.

## 7. Finite verification of the accounting identity on odd-prefix states

The frozen executor reproduces, for `m=16`, the following minimizing profiles:

```text
t   odd (A,sigma,kappa,E)   payload (A,sigma,kappa,E)

0   (  9, 8,0,  1)         ( 13,12,0,  1)
1   ( 11, 9,0,  2)         ( 15,12,0,  3)
2   ( 16, 8,0,  8)         ( 22,14,0,  8)
3   ( 24, 8,0, 16)         ( 30,14,0, 16)
4   ( 43,10,0, 33)         ( 47,12,0, 35)
5   ( 75, 9,0, 66)         ( 79,12,0, 67)
6   (143,10,0,133)         (147,12,0,135)
7   (271,10,0,261)         (275,12,0,263)
```

For `m=4,8,16`, every unresolved trial candidate inspected throughout the verified odd-selector prefix has

```text
kappa_v = 0.
```

For `m=32`, the first 16 diagnostic odd-prefix steps reproduce the same net-charge domination pattern:

```text
Delta cone
=
A_payload - A_odd

>=

sigma_payload - sigma_odd
=
Delta saving.
```

These finite observations are diagnostic only.

## 8. New exact open core

The scheduler theorem is now reduced to the local net-charge statement.

### Target

```text
R5_E8_ODD_PREFIX_NET_CHARGE_THEOREM_V1
```

For every `m=2^r` and every frozen odd-only prefix state before all odd selectors are eliminated, prove:

### I. No independent-node loss

For every relevant unresolved odd selector and every payload comparator:

```text
kappa_v = 0.
```

### II. Cone dominates savings

There exists an unresolved odd selector `o` such that for every payload `z`:

```text
A_z - A_o
>=
sigma_z - sigma_o.
```

Equivalently:

```text
E_o <= E_z.
```

If equality holds, prove:

```text
A_o < A_z.
```

The tertiary ID tie is automatically favorable to selectors because selector IDs are `1..m` and payload IDs are `m+1..2m`.

## 9. Consequence

If the net-charge theorem is proved, then:

```text
all m/2 odd selectors
are selected before payload

=>

Peak(F_m) >= 2^(m/2)

and

|F_m| = O(m log m)

=>

Peak(F_m)
>=
2^(Omega(L/log L)).
```

Therefore the exact frozen structural-greedy universal polynomial-peak theorem is falsified.

This would falsify only the exact frozen candidate mechanism.

```text
P_VS_NP
=
OPEN
```

## Claim ceiling

```text
NET_PROJECTION_CHARGE_IDENTITY
=
PROVED

STEP_0_SELECTOR_WIN_FOR_m=2^r
=
PROVED

ODD_PREFIX_kappa_ZERO
=
OPEN ARBITRARY-r

ODD_PREFIX_DELTA_CONE_GE_DELTA_SAVING
=
OPEN ARBITRARY-r

ODD_SELECTOR_GREEDY_PREFIX
=
OPEN

ARBITRARY-N_GREEDY_LOWER_BOUND
=
OPEN

P_VS_NP
=
OPEN
```
