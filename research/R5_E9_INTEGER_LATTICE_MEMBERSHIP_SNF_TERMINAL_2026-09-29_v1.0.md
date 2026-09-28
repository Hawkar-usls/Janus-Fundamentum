# R5 E9 — Integer-lattice membership / Smith terminal

Date: 2026-09-29
Status: PROVED POLYNOMIAL NECESSARY TERMINAL
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## 1. Exact terminal

Let `A` be any integer source matrix and let `b=1` be the Exact-One right-hand side. A Boolean witness is an integer vector, so

```math
Ax=b,\qquad x\in\{0,1\}^n
```

implies

```math
b\in A\mathbb Z^n.
```

Therefore

```text
b not in A Z^n  =>  exact UNSAT.
```

This test is stronger than checking solvability over selected finite fields. It asks membership in the full integer column lattice.

## 2. Smith/Hermite decision rule

Compute a Smith normal form

```math
UAV=D=\operatorname{diag}(d_1,\ldots,d_r,0,\ldots,0),
```

where `U,V` are unimodular and `d_i | d_{i+1}`. Then

```math
b\in A\mathbb Z^n
```

iff, writing `c=Ub`,

```text
d_i divides c_i for i <= r,
c_i = 0 for i > r.
```

Equivalently one may use column-Hermite normal form / integer-lattice membership.

Kannan and Bachem, *Polynomial Algorithms for Computing the Smith and Hermite Normal Forms of an Integer Matrix*, SIAM J. Comput. 8(4), 499–507 (1979), DOI 10.1137/0208040, give polynomial algorithms with polynomially bounded intermediate bit lengths. Hence this is an admitted polynomial preprocessing terminal under the JANUS total-cost firewall.

## 3. Determinantal-divisor form

If `rank_Q(A)=rank_Q([A|b])=r`, let

```math
\Delta_r(M)=\gcd\{\text{all }r\times r\text{ minors of }M\}.
```

The product of the nonzero Smith invariant factors equals `Delta_r`. Since

```math
A\mathbb Z^n \subseteq [A|b]\mathbb Z^{n+1},
```

with equal rational span, the lattice index is

```math
[[A|b]\mathbb Z^{n+1}:A\mathbb Z^n]
=\frac{\Delta_r(A)}{\Delta_r([A|b])}.
```

Thus a ratio greater than one is an exact certificate that `b` is not in the original integer column lattice.

## 4. Strict separation from the old F2/F3 screens

Use the repaired Paley-voltage control `B` from

`R5_E9_PALEY_VOLTAGE_POST_RKPR_LINEAR_NULLITY_FAMILY_2026-09-29_v1.0.md`.

It has

```text
shape(B)       = 165 x 165
rank_Q(B)      = 149
rank_F2(B)     = 149
rank_F2([B|1]) = 149
rank_F3(B)     = 148
rank_F3([B|1]) = 148
```

so both the parity and ternary phase systems are consistent.

However exact Smith arithmetic gives

```text
nonzero SNF invariants of B end in ... , 1, 9
product(nonzero invariants of B)       = 9

nonzero SNF invariants of [B|1] end in ... , 1, 3
product(nonzero invariants of [B|1])   = 3
```

and both matrices have rational rank 149. Therefore

```math
[[B|1]\mathbb Z^{166}:B\mathbb Z^{165}]=9/3=3,
```

so

```math
\boxed{\mathbf1\notin B\mathbb Z^{165}}.
```

Hence this source is UNSAT before any Boolean-specific reasoning: there is no integer solution at all.

This proves that the integer-lattice terminal is strictly stronger than the existing `F2 + F3` consistency screens on the frozen source carrier.

## 5. Explicit mod-9 witness

The companion checker stores a vector `y in (Z/9Z)^165` satisfying

```math
y^T B \equiv 0 \pmod 9,
```

but

```math
y^T\mathbf1 \equiv 6 \pmod 9.
```

Therefore any integer solution of `Bx=1` would imply

```math
0\equiv y^TBx=y^T\mathbf1\equiv6\pmod9,
```

a contradiction.

So the Smith obstruction has a short directly checkable modular certificate on this control.

## 6. Algorithmic consequence

Add the following exact polynomial router before rational-kernel tope enumeration:

```text
INTEGER_LATTICE_TERMINAL(A):
    compute SNF/HNF membership of 1 in A Z^n
    if 1 not in A Z^n:
        return UNSAT with lattice certificate
    else:
        continue
```

This does not solve the integer-feasible or Boolean-feasible residual. In particular,

```text
1 in A Z^n
```

does not imply a `{0,1}` solution.

But every instance rejected here is removed in deterministic polynomial time, including instances invisible to the previous mod-2/mod-3 screens.

## 7. Firewall

Proved:

```text
BOOLEAN SAT => INTEGER LATTICE MEMBERSHIP
INTEGER LATTICE NONMEMBERSHIP => UNSAT
SNF/HNF MEMBERSHIP TEST = POLYNOMIAL BIT COMPLEXITY
TERMINAL STRICTLY STRONGER THAN F2+F3 ON THE PALey-VOLTAGE CONTROL
```

Not proved:

```text
INTEGER LATTICE MEMBERSHIP => SAT
UNIVERSAL POLYNOMIAL EXACT-ONE SOLVER
P = NP
```

Canonical state remains

```text
E8_D1   = EMPTY
P_VS_NP = OPEN
```
