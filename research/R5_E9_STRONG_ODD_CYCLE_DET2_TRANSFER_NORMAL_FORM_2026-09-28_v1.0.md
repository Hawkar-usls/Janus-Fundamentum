# R5 E9 — Strong odd-cycle determinant-2 transfer normal form

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_FULL_BOUNDARY_TRANSFER_NORMAL_FORM__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`
- `research/R5_E9_ODD_HOLE_FULL_BOUNDARY_DELTA_MATROID_BARRIER_2026-09-26_v1.0.md`
- `research/R5_E9_SINGULAR_UNSAT_3CUT_IRREDUCIBLE_ODD_CYCLE_CONTROL_2026-09-28_v1.0.md`

Scientific ceiling:

```text
THIS GIVES AN EXACT TWO-STATE TRANSFER REPRESENTATION OF ONE STRONG ODD CYCLE,
INCLUDING ITS THIRD-OCCURRENCE BOUNDARY.
IT DOES NOT YET PROVE POLYNOMIAL CLOSURE UNDER MANY OVERLAPPING CYCLES.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source-local strong odd cycle

Let `k=2m+1` be odd.  Use indices modulo `k`.

Let `v_i` be the `k` cycle variables and let the `k` cycle rows be

```text
C_i = {v_i, v_(i+1), w_i}.
```

Thus Exact-One gives

```text
v_i + v_(i+1) + w_i = 1.                 (C_i)
```

Because the source is cubic, each `v_i` has a third occurrence in a row

```text
D_i = {v_i, a_i, b_i},
```

so the full local source boundary also obeys

```text
v_i + a_i + b_i = 1.                     (D_i)
```

No assumption is made that the external variables `w_i,a_i,b_i` are globally private; these equations describe the exact local projection before any further identifications outside the region.

## 2. Determinant-two cycle matrix

Let `C_k=I+S` where `S` is the cyclic shift.  The cycle equations are

```text
C_k v = 1-w.
```

For odd `k`,

```text
det(C_k)=2.
```

One direct proof uses the eigenvalues `1+zeta^j`: their product is
`1-(-1)^k=2`.  Equivalently, the recurrence below closes with a factor two after one odd circuit.

Thus the cycle variables are uniquely determined over `Q` by the belt boundary `w`.

## 3. Exact ±1 state transform

Define

```text
sigma_i = 1 - 2 v_i  in {-1,+1}.
```

Multiply `(C_i)` by two and substitute `2v_i=1-sigma_i`:

```text
(1-sigma_i) + (1-sigma_(i+1)) + 2 w_i = 2,
```

hence

```text
boxed( sigma_(i+1) = 2 w_i - sigma_i ).          (T_i)
```

Because `w_i` is Boolean, the only legal state transitions are

```text
sigma_i=-1, w_i=0 -> sigma_(i+1)=+1
sigma_i=+1, w_i=0 -> sigma_(i+1)=-1
sigma_i=+1, w_i=1 -> sigma_(i+1)=+1
```

while

```text
sigma_i=-1, w_i=1
```

would produce state `+3` and is forbidden.

Therefore the entire odd-cycle belt is an exact deterministic two-state cyclic automaton.

## 4. Closed alternating-sum formula

Put

```text
A_i(w)=sum_{t=0}^{k-1} (-1)^t w_(i+t).
```

Alternating the cycle equations gives

```text
2 v_i = 1 - A_i(w),
```

and hence

```text
boxed( sigma_i = A_i(w) ).
```

### Theorem SOC-1 — exact belt projection

A Boolean belt word `w` extends to Boolean cycle variables `v` iff

```text
A_i(w) in {-1,+1}
```

for every `i`.

When it does, the extension is unique and is reconstructed by

```text
v_i = (1-A_i(w))/2.
```

Equivalently, the cyclic zero-runs of `w` between consecutive ones all have even length; the all-zero word is impossible for odd `k`.

For `k=3`, the condition reduces exactly to

```text
w_0 XOR w_1 XOR w_2 = 1.
```

## 5. Full third-occurrence boundary

Now substitute `v_i=(1-sigma_i)/2` into `(D_i)`:

```text
(1-sigma_i)/2 + a_i + b_i = 1,
```

so

```text
boxed( 2(a_i+b_i)=1+sigma_i ).            (B_i)
```

Therefore

```text
sigma_i=-1 -> (a_i,b_i)=(0,0),
sigma_i=+1 -> (a_i,b_i) in {(1,0),(0,1)}.
```

### Theorem SOC-2 — exact full-boundary transfer form

The full projected relation on

```text
(w_0,...,w_(k-1), a_0,...,a_(k-1), b_0,...,b_(k-1))
```

is exactly the set of boundary words admitting a cyclic state sequence

```text
sigma_i in {-1,+1}
```

satisfying `(T_i)` and `(B_i)` for every `i`.

Thus its hidden state dimension is exactly bounded by two, uniformly in cycle length.

This representation keeps the full third-occurrence semantics that invalidated the earlier belt-only ordinary-matching shortcut.

## 6. Transfer-matrix form

For a fixed local boundary triple `(w_i,a_i,b_i)`, define the `2 x 2` Boolean transfer matrix `M_i`, with rows and columns indexed by `{-1,+1}`, by

```text
M_i[s,t]=1
iff
t=2 w_i-s
and
2(a_i+b_i)=1+s.
```

Then

```text
boundary word is extendable
iff
trace(M_0 M_1 ... M_(k-1)) > 0
```

where multiplication is ordinary Boolean-relation composition (or ordinary nonnegative integer multiplication for zero/nonzero testing).

The matrix dimension is constant; the representation size is `O(k)`.

## 7. Relation to the old matching barrier

The earlier full-boundary theorem proves that for the odd-hole family `k>=5`, the full relation is not a delta-matroid and therefore is not ordinary matching-realizable.

There is no contradiction:

```text
ordinary matching realization = blocked,
2-state cyclic transfer representation = exact / proved here.
```

The latter is a different symbolic carrier.

## 8. What is and is not algorithmic progress

This theorem removes one false concern: a single strong odd cycle does **not** require an exponentially large boundary table.  Its exact full-boundary semantics has a uniform two-state transfer representation.

However, the state `sigma_i` is in bijection with the original cycle variable `v_i`.  Therefore merely rewriting one cycle as the automaton is not by itself a dimension-dropping contraction.

The real new gate is closure under composition:

```text
R5_E9_STRONG_ODD_CYCLE_TRANSFER_CORRELATION_CLOSURE_GATE_V1
```

A PASS must show that after repeatedly eliminating/combining strong odd-cycle regions, the transfer objects can be maintained with polynomial total symbolic size and polynomial witness reconstruction, with a strict global progress measure.

A FAIL should exhibit a source-valid family for which any proposed transfer representation grows superpolynomially or recreates the original NP-complete EQ3/EXACT1 language without decrease.

## 9. Checker

Executable replay:

`experiments/r5_e9_strong_odd_cycle_det2_transfer.py`

It exhausts all belt and full-boundary assignments for `k=3,5,7`, compares direct existential Exact-One projection against the transfer equations, verifies the alternating-sum reconstruction, and checks the special `k=3` odd-parity collapse.

## 10. Ceiling

```text
ODD CYCLE MATRIX det = 2 = PROVED
BELT EXTENSION = UNIQUE WHEN FEASIBLE
BELT FEASIBILITY = ALL ALTERNATING SUMS ±1
FULL THIRD-OCCURRENCE BOUNDARY = EXACT 2-STATE CYCLIC TRANSFER
SINGLE-CYCLE BOUNDARY TABLE EXPLOSION = CLOSED
POLYNOMIAL CLOSURE UNDER MANY CYCLES = OPEN
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
