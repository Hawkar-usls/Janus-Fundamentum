# C047 — Proof-Carrying Offset-Aware Affine Functional Trellis

```text
P_VS_NP = OPEN
C047 = IMPLEMENTED / DRAFT / REVIEW_PENDING
```

## 1. Exact object

The input is a finite family of forbidden affine subspaces of `GF(2)^d`.
Each factor is represented canonically by an independent affine system

\[
U_i=\{x: n\cdot x=\beta_i(n)\ \text{for all }n\in N_i\},
\]

where `N_i` is the row span of the factor normals and `beta_i:N_i->GF(2)`
is the distinguished linear functional determined by the offsets.

C046 proved that the normal spaces alone are insufficient. C047 keeps the
distinguished functionals in every leaf transition.

## 2. Charged deterministic order

C047 does not receive a free good layout. It deterministically groups equal
normal spaces into parallel blocks in order of first appearance and preserves
input order inside each block.

For the resulting order define

\[
P_t=N_1+\cdots+N_t,\qquad
S_t=N_{t+1}+\cdots+N_m,\qquad
B_t=P_t\cap S_t.
\]

The cut width is `max_t dim(B_t)`. If it exceeds the fixed capability, the
compiler returns `OPEN_CUT_WIDTH` before state enumeration.

## 3. State semantics

A state at cut `t` is one linear functional

\[
\sigma:B_t\to GF(2).
\]

It is reachable exactly when there exists a prefix functional
`f:P_t->GF(2)` whose restriction to `B_t` is `sigma` and for every
processed factor `i<=t`,

\[
f|_{N_i}\ne\beta_i.
\]

The inequality is the exact avoidance condition `x notin U_i`.

## 4. Exact recurrence lemma

Let `W=N_t`. Then

\[
B_t\subseteq B_{t-1}+W.
\]

Proof: for `b in B_t`, write `b=p+w` with `p in P_{t-1}` and `w in W`.
Since `b in S_t` and `w in W subseteq S_{t-1}`, we have
`p=b+w in S_{t-1}`. Therefore `p in P_{t-1} intersect S_{t-1}=B_{t-1}`.

Consequently, a predecessor state and a functional on `W` determine the
new boundary value. C047 tests a transition `sigma->tau` by one polynomial
linear-algebra query on

\[
\operatorname{span}(B_{t-1},B_t,W),
\]

requiring both boundary restrictions and at least one basis row of `W` to
differ from `beta_t`.

Any reachable predecessor realization with restriction `sigma` can be
combined with the accepted `W` functional: their overlap
`P_{t-1} intersect W` lies in `B_{t-1}`. The displayed inclusion then proves
that the combined prefix realizes `tau`. Thus the recurrence neither loses
nor invents feasible prefixes.

## 5. Complexity

If every cut has dimension at most fixed `k`, there are at most `2^k` states
per layer and at most `2^(2k)` tested state pairs per factor. Every transition,
join, restriction and witness lift is Gaussian elimination of polynomial
dimension.

\[
T(I)=2^{O(k)}\operatorname{poly}(|I|).
\]

The certificate records every tested transition, all reachable states,
prefix-functional witnesses, the deterministic order, cut bases, work ledger
and fixed-point byte count. Work and certificate caps are explicit.

This is an alignment with subspace-layout width, matroid pathwidth and
linear-code trellis complexity, not a newly named width parameter.

## 6. SAT and UNSAT evidence

At the root `B_m={0}`.

- A reachable empty functional yields a functional on the span of all normals.
  Gaussian elimination extends it to an ambient point, which is checked
  against every forbidden affine subspace.
- An empty root state set is an UNSAT certificate. The independent verifier
  rebuilds every cut, state and transition without importing the producer.

## 7. Strict separation from global signed support

For forty independent factors

\[
U_i=\{x:x_i=0\},
\]

global inclusion-exclusion has `2^40-1` nonzero intersections, while every
trellis cut has width zero. C047 returns SAT with the all-ones witness.

For the C045 hidden-basis prefix-normal family, dense coordinate supports
again have trellis width zero. Thus the message language is basis-invariant
at the factor-normal level and can remove coordinate-primal density.

## 8. Offset control

For the C046 pair in dimension 24:

```text
duplicate offsets (0,0)      -> SAT
complementary offsets (0,1)  -> UNSAT
maximum trellis width         -> 1
```

The same normal layout is used in both cases. Different leaf functionals
produce the correct different terminal.

## 9. Hard-image boundary

The registered 24-variable NAND3 pressure image exceeds the fixed cut-width
cap and returns `OPEN_CUT_WIDTH`. This is a refusal for the deterministic
layout and capability only. It is not a lower bound and does not imply
`P != NP`.

## 10. Frozen audit

```text
260 random affine arrangements
241 exact terminals
19 OPEN_CUT_WIDTH
0 SAT/UNSAT mismatches
0 false witnesses
0 independent-verifier failures

C046 equal-normal/different-offset pair   PASS
40 independent factors, width 0           PASS
40-dimensional hidden-basis family       PASS
whole ambient space forbidden             UNSAT
work exhaustion                           OPEN_WORK_BUDGET
certificate exhaustion                    OPEN_CERTIFICATE_VOLUME
tampered SAT witness                      REJECTED
```

Frozen digest:

```text
2bcc3878076d693d48989e3c15708141310b65bf825dda24c40d7eb309f89789
```

## 11. Surviving gate

```text
POLYNOMIAL_AFFINE_LAYOUT_DISCOVERY
OR
BRANCH_DECOMPOSITION_WITH_OFFSET_AWARE_MESSAGES
```

C047 proves the compiler for one charged deterministic order. It does not
prove that this order, or any polynomial frozen portfolio, has bounded width
for every instance. General branch-decomposition discovery and composition
remain open.
