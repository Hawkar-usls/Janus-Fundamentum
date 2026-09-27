# R5 E9 — EQ3 Gauge-Nullity UNSAT Counterfamily

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_ANTI_LOOP_THEOREM__RAW_F2_NULLITY_NOT_SEMANTIC_COMPLEXITY`

Parents:
- `R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`
- `R5_E9_CUBIC_KERNEL_CIRCUIT_CONNECTED_CONTRACTION_2026-09-27_v1.0.md`

Scientific ceiling:

```text
THIS IS AN ANTI-LOOP THEOREM.
IT DOES NOT SUPPLY A POLYNOMIAL SAT DECIDER.
RAW BINARY NULLITY IS NOT A VALID UNIVERSAL SAT/UNSAT PROGRESS MEASURE.
P_VS_NP = OPEN.
```

## 1. Equality gadget and its terminal-invisible parity mode

Use the 10-variable / 9-clause linear cubic EQ3 gadget from the companion universality theorem, with terminals `0,1,2` and clauses

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6)
```

Over `F_2`, define

```text
g = (0,0,0,1,1,1,1,1,1,0).
```

Each gadget clause meets `supp(g)={3,4,5,6,7,8}` in exactly two variables. Therefore the gadget parity matrix `B` satisfies

```text
B g = 0 mod 2.
```

Crucially,

```text
g_0=g_1=g_2=0.
```

So this nonzero parity-kernel vector is invisible on all three terminals.

## 2. Survival after occurrence regularization

Let `Phi` be any cubic Positive 1-in-3 instance with `n` variables and `n` clauses. Apply the companion regularizer independently to every source variable:

- split its three occurrences into the three gadget terminals;
- keep the original source clauses on those terminal copies;
- add the nine gadget clauses.

Call the resulting linear cubic instance `R(Phi)` and its binary incidence matrix `A_R`.

For each original source variable `v`, let `g_v` be the vector equal to `g` on the six auxiliary positions `{3,4,5,6,7,8}` of the gadget of `v`, and zero on every other variable.

The gadget rows annihilate `g_v` by Section 1. Every retained source clause uses only terminals, where `g_v` is zero. Hence

```text
A_R g_v = 0 mod 2.
```

Different variable gadgets are disjoint, so the supports of the vectors `g_v` are pairwise disjoint. Therefore they are linearly independent.

Thus

```text
dim_F2 ker(A_R) >= n.
```

Since `R(Phi)` has exactly `10n` variables,

```text
boxed(dim_F2 ker(A_R) >= |V(R(Phi))|/10).
```

The large binary nullity comes from local terminal-invisible gauge modes and is present independently of whether `Phi` is SAT or UNSAT.

## 3. Infinite connected linear-cubic UNSAT family

Use the explicit connected linear cubic UNSAT seed `U_0` from

`R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`.

It has `n_0=15` variables.

Define recursively

```text
U_(t+1) = R(U_t).
```

The companion EQ3 theorem proves exact semantic equivalence

```text
U_(t+1) SAT iff U_t SAT.
```

Hence every `U_t` is UNSAT.

The same theorem proves that regularization preserves:

```text
3-uniform,
3-regular,
linear,
square incidence.
```

Connectedness is also preserved: every replacement gadget has connected incidence graph and its three terminals attach to the three source clauses formerly incident with the replaced variable; contracting each gadget back to one variable recovers the connected source Levi graph. Therefore the expanded Levi graph is connected.

The size recurrence is

```text
n_(t+1)=10 n_t,
```

so

```text
n_t = 15 * 10^t.
```

Applying Section 2 at the outermost regularization level gives

```text
dim_F2 ker(A_t) >= n_(t-1) = n_t/10.
```

Therefore:

### Theorem EGN-1

There is an explicit polynomially constructible infinite family of connected, linear, cubic, positive Exact-One instances satisfying

```text
UNSAT,
n_t = 15*10^t,
dim_F2 ker(A_t) >= n_t/10.
```

In particular the binary nullity is `Omega(n)` on an UNSAT family inside the exact NP-complete JANUS carrier.

## 4. Consequence for the affine/cycle endgame

The current exact normal form is

```text
Ax=1 mod 2
AND
supp(x) independent in the matching-normalized cycle 2-factor C_M.
```

A complexity measure based on

```text
dim_F2 ker(A)
```

cannot distinguish hard global semantic freedom from local gadget gauge freedom. The family above has linear kernel dimension while remaining UNSAT by inherited source semantics.

Thus the following shortcut is forbidden:

```text
large F2 nullity => abundant Exact-One witnesses / easy SAT
```

and so is its contrapositive-style use as a progress theorem.

The next representation must quotient terminal-invisible kernel directions before charging dimension.

## 5. Semantic quotient direction

For a decomposition or gadget boundary `T`, define the terminal restriction map

```text
rho_T : ker_F2(A_local) -> F_2^T.
```

The gauge subspace is

```text
K_gauge = ker(rho_T),
```

consisting of local parity motions invisible at the semantic interface.

Only the quotient / image

```text
K_sem = ker_F2(A_local) / K_gauge
```

(or equivalently `im(rho_T)`) is allowed to count toward cross-boundary state complexity.

For the EQ3 gadget above, `g` lies in `K_gauge`; therefore the linear raw-nullity blowup disappears after semantic quotienting.

This observation does not yet prove a universal polynomial quotient decomposition. It identifies the correct invariant that a successful compression theorem must bound.

Freeze next gate:

```text
R5_E9_SEMANTIC_KERNEL_QUOTIENT_COMPRESSION_GATE_V1
```

PASS requires a deterministic polynomial construction that, on every linear cubic source, decomposes or eliminates terminal-invisible kernel freedom and proves a polynomial bound on the remaining exact interface state, with witness reconstruction.

## 6. External anti-loop

Recent work on minimum distance for regular LDPC codes proves NP-completeness even for `(3,3)`-regular Tanner graphs. This does not by itself prove hardness of the exact JANUS affine-cycle query, but it confirms that raw sparse regular parity structure is not a free polynomial decoding donor.

Therefore no future argument may promote `degree=3`, `LDPC`, or large/small raw kernel dimension alone into a universal solver theorem.

## 7. Ceiling

```text
TERMINAL-INVISIBLE EQ3 KERNEL MODE
= EXPLICIT / PROVED

ITERATED CONNECTED LINEAR-CUBIC UNSAT FAMILY
= PROVED

F2 NULLITY ON THAT FAMILY
>= n/10
= LINEAR

RAW F2 NULLITY AS UNIVERSAL SEMANTIC COMPLEXITY
= FALSIFIED

SEMANTIC KERNEL QUOTIENT COMPRESSION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT YET PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
