# JANUS TRUMP R48J — Pressure Bootstrap Circularity Barrier

Date: 2026-09-04

Status: **SYMBOLIC META-BARRIER; O4 REMAINS OPEN**

## Motivation

R48B introduced the weighted potential

\[
\Phi_a(F)=C(F)+aV(F)
\]

and the local pressure

\[
a_{req}(F,v)=\left\lceil\frac{\max(0,\Delta C_v)}{\Delta V_v}\right\rceil,
\qquad
a_*(F)=\min_v a_{req}(F,v),
\]

with verified terminals assigned pressure zero.

If one fixed coefficient `a` bounds every reachable state's `a_*`, then `C+aV` telescopes and persisted clause count is bounded.

R48E and R48G refuted small fixed coefficients `a=1` and `a<=2` for the current frozen grammar, so the natural next idea is to prove a polynomial bound on `a_*`.

This note identifies a crucial distinction:

\[
\boxed{a_*(F)\le poly(\lvert F\rvert)\text{ in the CURRENT state is not enough.}}
\]

The polynomial coefficient must be controlled in the size of the **original input**, or by another independently closed invariant.

## Lemma 1 — root-polynomial pressure gives a polynomial persisted envelope

Let the original normalized root be `F_0` with encoding length `N_0`, clause count `C_0`, and variable count `V_0`.

Assume every nonterminal persisted state `F_t` has a certified successor satisfying

- `DeltaV_t = V(F_t)-V(F_{t+1}) >= 1`;
- no fresh variables;
- `DeltaC_t = C(F_{t+1})-C(F_t) <= A(N_0) DeltaV_t`;
- `A(N_0) <= N_0^k` for a fixed constant `k`.

Then

\[
C(F_{t+1})\le C(F_t)+A(N_0)\Delta V_t.
\]

Summing over all accepted nonterminal steps gives

\[
C(F_t)\le C_0+A(N_0)(V_0-V(F_t))
\le C_0+A(N_0)V_0.
\]

Since `C_0,V_0 <= N_0`,

\[
\boxed{C(F_t)\le N_0+N_0^{k+1}=N_0^{O(1)}.}
\]

Thus a universal **root-polynomial** pressure bound closes the persisted clause envelope.

## Lemma 2 — current-state polynomial pressure is circular

Suppose instead one proves only

\[
a_*(F_t)\le C(F_t)^q
\]

for some fixed `q>=1`.

This is polynomial in the current representation, but the current representation is exactly what still needs to be bounded.

Consider the abstract certified-size sequence

\[
V_{t+1}=V_t-1,
\qquad
C_{t+1}=2C_t.
\]

Then

\[
\Delta V_t=1,
\qquad
\Delta C_t=C_t,
\qquad
a_{req,t}=C_t.
\]

So this sequence satisfies the apparently strong local condition

\[
a_{req,t}\le C_t
\]

— a degree-one polynomial in current clause count.

But after `t` steps,

\[
C_t=2^t C_0.
\]

With `V_0=Theta(N_0)` possible variable-decreasing steps,

\[
C_{V_0}=2^{Theta(N_0)}C_0,
\]

which is exponential in the original input size.

Therefore

\[
\boxed{a_*(F)\le poly(C(F))\not\Rightarrow C(F_t)\le poly(N_0).}
\]

The same obstruction applies a fortiori to bounds such as `a_* <= C^q` for `q>1`.

## Lemma 3 — polynomial per-current-state work does not repair the composition

Even if every candidate probe takes polynomial time in the current state size, an exponentially large persisted state makes that per-state polynomial itself exponential in `N_0`.

Hence

\[
\boxed{POLY(current\ state)\times EXP(current\ state\ growth)\neq POLY(root\ input).}
\]

This is the same hidden-debt firewall used throughout R47, now stated for the amortized-pressure route.

## Valid theorem targets after R48J

A polynomial-envelope proof must establish at least one of the following kinds of statements.

### Route A — root-polynomial pressure

There exists a fixed polynomial `A` such that for every valid root `F_0` and every reachable persisted nonterminal state `F_t`,

\[
\boxed{a_*(F_t)\le A(\lvert F_0\rvert).}
\]

This plugs directly into Lemma 1.

### Route B — independently bounded structural pressure

Find a structural quantity `S(F_t)` satisfying both

1. `a_*(F_t) <= poly(S(F_t))`, and
2. independently, `S(F_t) <= poly(N_0)` along every reachable trajectory.

The second bound must not itself assume the desired polynomial clause envelope.

### Route C — stronger nonlinear potential

Construct a polynomially representable well-founded potential `Psi(F)` whose local decrease directly controls both representation growth and the remaining trajectory length, with no hidden dependence on an already-unbounded state quantity.

## What would refute the root-polynomial route

A valid lower-bound family would require roots `F_n` of size `N_n` and reachable persisted states `G_n` such that

\[
a_*(G_n)
\]

grows faster than every fixed polynomial in `N_n`, or a stronger obstruction with no eligible certified variable-decreasing successor.

Finite observations `a_*=2,3,...` do not establish this.

## Relation to R48I

R48I symbolically gives raw exact-DP pressure

\[
\Delta C_{raw}=r(r-2)
\]

for its clean cyclic bipolar `r x r` construction.

Because the root formula size also grows with `r`, even an observed normalized pressure `Theta(r^2)` would still be polynomial in root size. Such a family can refute fixed-constant coefficients and reveal the correct scaling law, but it would **not by itself** refute the general root-polynomial pressure route.

This separation is mandatory.

## Canonical firewall

\[
\boxed{POLYNOMIAL\ IN\ CURRENT\ STATE\neq POLYNOMIAL\ IN\ ROOT\ INPUT.}
\]

\[
\boxed{LOCAL\ PRESSURE\ BOUND\neq GLOBAL\ POLYNOMIAL\ ENVELOPE\ UNLESS\ THE\ BOOTSTRAP\ CLOSES.}
\]

## Status

- `UNIVERSAL_FIXED_a_LE_2_COVERAGE = REFUTED_BY_EXPLICIT_REACHABLE_STATE`.
- `UNIVERSAL_ROOT_POLYNOMIAL_PRESSURE_BOUND = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_a_EXISTS = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
