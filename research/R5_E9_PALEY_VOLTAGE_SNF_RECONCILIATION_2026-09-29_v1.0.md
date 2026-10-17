# R5 E9 — Paley voltage family / SNF reconciliation

Date: 2026-09-29
Status: SCOPE CORRECTION
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## Correction

The theorem

`R5_E9_PALEY_VOLTAGE_POST_RKPR_LINEAR_NULLITY_FAMILY_2026-09-29_v1.0.md`

remains valid exactly for the route it falsifies:

```text
connected + square linear cubic + 3|n + F2/F3 consistency + RKPR
=> rational nullity O(log n)
```

The family has exact rational nullity

```math
\nu_Q(C_m)=15m+1=N_m/11+1.
```

However a later polynomial terminal was discovered:

`R5_E9_INTEGER_LATTICE_MEMBERSHIP_SNF_TERMINAL_2026-09-29_v1.0.md`.

Therefore this family must **not** be cited as a current post-SNF hard residual without an additional integer-lattice check.

## Exact checks already completed

For the repaired `165 x 165` base `B`:

```text
F2 consistency                    = PASS
F3 consistency                    = PASS
RKPR                              = PASS (equality classes only)
integer lattice 1 in B Z^165      = FAIL
Smith lattice index               = 3
```

Equivalently there is an explicit `mod 9` certificate

```math
y^TB\equiv0\pmod9,\qquad y^T\mathbf1\equiv6\pmod9.
```

For the one-edge cyclic cover with `m=2`:

```text
N=330
nullity_Q=31
integer-lattice membership = FAIL
Smith lattice index         = 3
```

For `m=3`, a full symbolic Smith computation was not completed.  Instead exact Hensel lifting from mod `3` to mod `9` gave

```text
rank_F3(lift system)            = 446
rank_F3(augmented lift system)  = 447
```

so the `m=3` cover is inconsistent mod `9` and therefore also fails integer-lattice membership.

No claim is made here that **every** `m` is killed by the SNF terminal; that requires a separate arbitrary-`m` proof.

## Canonical use

The Paley-voltage family remains a valid arbitrary-size falsifier for **pre-SNF** low-nullity claims.  It is no longer an admissible witness for statements containing the premise

```text
1 in A Z^n.
```

The live structural gate after this reconciliation is

```text
R5_E9_POST_SNF_RKPR_LINEAR_CUBIC_SUFFICIENCY_FALSIFIER_GATE_V1
```

and the newer polynomial preprocessing layer is

```text
INTEGER_LATTICE_PAIR_PROJECTION_2SAT
```

from `R5_E9_INTEGER_LATTICE_PAIR_PROJECTION_2SAT_TERMINAL_2026-09-29_v1.0.md`.

## Firewall

```text
PALEY NULLITY THEOREM             = VALID IN ORIGINAL PRE-SNF SCOPE
PALEY FAMILY AS POST-SNF WITNESS  = NOT ESTABLISHED
P_VS_NP                           = OPEN
E8_D1                             = EMPTY
```
