# JANUS TRUMP R48B — Weighted Clause/Variable Amortization Theorem

Status: **CONDITIONAL SYMBOLIC POLYNOMIAL-COMPOSITION THEOREM; UNIVERSAL LOCAL AMORTIZED SUCCESSOR EXISTENCE OPEN**

## Motivation

R47X refuted the exact persistent root-cap invariant `C<=C0` for the frozen R47M projection controller.

R47Z then showed that the explicit R47X witness is rescued by a fixed persistent envelope `B=C0+4`, while the final terminal-producing exact-DP probe may temporarily exceed that persistent envelope before certified normalization closes the formula.

The fixed-envelope theorem is therefore correct but still globally phrased. R48B turns it into a local amortized condition.

## Weighted potential

Fix the original input encoding length `N`. Before execution choose a deterministic nonnegative coefficient

\[
a(N)=N^{O(1)}.
\]

For every normalized nonterminal state `F`, define

\[
\boxed{\Phi_a(F):=C(F)+a(N)V(F)}.
\]

A certified nonterminal successor `F -> F'` is **a-amortized-safe** when

1. the frozen exact-DP + certified normalization/replay checks pass;
2. no fresh variables are introduced;
3. `V(F') < V(F)`;
4. weighted potential does not increase:
   \[
   \boxed{C(F')+aV(F')\le C(F)+aV(F).}
   \]

A verified terminal is accepted independently of this persisted-state inequality, because no further state must be stored or projected from it; its transient work remains subject to the already-required polynomial intermediate envelope and independent certificate verification.

## Lemma 1 — telescoping persistent envelope

For any chain of a-amortized-safe nonterminal successors,

\[
\Phi_a(F_t)\le\Phi_a(F_0)=C_0+aV_0.
\]

Because `aV(F_t)>=0`,

\[
\boxed{C(F_t)\le C_0+aV_0.}
\]

Thus weighted local amortization induces the fixed persistent clause envelope

\[
\boxed{B_a(N)=C_0+a(N)V_0.}
\]

If `a(N)` is polynomial and `C0,V0<=N`, then `B_a(N)` is polynomial.

## Lemma 2 — polynomial trajectory height

No fresh variables are introduced and every selected nonterminal transition strictly lowers `V`. Therefore

\[
\boxed{T\le V_0\le N.}
\]

This does not require clause count or literal mass to decrease locally.

## Lemma 3 — polynomial persisted representation

Every canonical non-tautological clause contains at most one literal per current/root variable, hence length at most `V0`. From Lemma 1,

\[
L(F_t)\le C(F_t)V_0\le(C_0+aV_0)V_0=N^{O(1)}.
\]

So every persisted normalized state has polynomial explicit size.

## Lemma 4 — polynomial candidate production under the induced envelope

At a persisted state, clause count is at most `B_a(N)`. For any pivot, exact DP considers at most

\[
p_vn_v\le B_a(N)^2/4
\]

parent pairs. Every explicit resolvent has length at most `V0`, giving a coarse forced-DP literal bound

\[
O(B_a(N)^2V_0)=N^{O(1)}.
\]

The frozen R47M producer additionally requires its existing polynomial intermediate-envelope check and all independent replays. Therefore each candidate probe is polynomial when `a(N)` is fixed polynomial.

## Lemma 5 — deterministic discovery bound

At each normalized state scan current variables in deterministic order and stop at the first verified terminal or a-amortized-safe nonterminal successor.

There are at most `V0` candidate pivots per state and at most `V0` selected nonterminal states, hence

\[
\boxed{\text{candidate probes}\le V_0^2.}
\]

No sequence enumeration is required.

## Conditional theorem

If there exists one fixed polynomial coefficient `a(N)` such that every reachable normalized nonterminal state produced by this controller admits a polynomially discoverable verified terminal or a-amortized-safe successor, then the complete deterministic trajectory has polynomial total work.

The only theorem-critical missing statement is the universal local successor existence condition:

\[
\boxed{\forall F\in Reach_a,\ F\text{ nonterminal}\Rightarrow\exists v:\ TERMINAL_v\ \lor\ \Phi_a(F_v)\le\Phi_a(F).}
\]

This is a strictly local form of the fixed polynomial-envelope coverage problem.

## Exact local amortization coefficient

For one certified nonterminal candidate `F -> F_v`, define

\[
\Delta C_v:=C(F_v)-C(F),
\]

\[
\Delta V_v:=V(F)-V(F_v)>0.
\]

The least nonnegative integer coefficient that makes this transition weighted-safe is

\[
\boxed{a_{req}(F,v)=\left\lceil\frac{\max(0,\Delta C_v)}{\Delta V_v}\right\rceil.}
\]

For a state define the best certified local pressure

\[
\boxed{a_*(F)=\min_v a_{req}(F,v),}
\]

with a verified terminal candidate assigned pressure `0` because it closes the trajectory.

Therefore universal weighted coverage with coefficient `a(N)` is exactly the assertion that every reachable nonterminal state has a certified candidate with

\[
\boxed{a_*(F)\le a(N).}
\]

This gives a direct measurable quantity for adversarial search.

## R47Z witness calibration

The minimum-envelope rescue chain on the sealed R47X witness is

\[
[75,199,22]\xrightarrow{v=2}[76,204,21]
\xrightarrow{v=7}[76,207,20]
\xrightarrow{v=9}[79,218,19]
\xrightarrow{v=5}\text{SAT}.
\]

For the three nonterminal selected transitions:

- `v=2`: `Delta C=1`, `Delta V=1`, hence `a_req=1`;
- `v=7`: `Delta C=0`, `Delta V=1`, hence `a_req=0`;
- `v=9`: `Delta C=3`, `Delta V=1`, hence `a_req=3`.

Thus

\[
\boxed{a=3}
\]

amortizes all persisted nonterminal debt on this finite rescue trajectory. The last `v=5` probe is terminal and is governed by transient polynomial-envelope plus verification requirements rather than persisted-state potential.

The induced static bound would be `C<=C0+3V0=141`, much looser than the observed minimum fixed envelope `79`; this is expected. Weighted amortization trades tightness for a simpler local proof obligation.

## Why this is useful

The fixed-envelope question asks whether every reachable state stays below some global `B(N)` after choosing a suitable pivot.

R48B instead asks whether each state can pay its clause growth using the variables eliminated by that same certified transition. The debt is local and additive:

\[
\boxed{\text{CLAUSE GROWTH}\le a(N)\times\text{VARIABLES ELIMINATED}.}
\]

If a polynomial `a(N)` can be proved universally, repeated projections cannot compound explicit representation size exponentially: the total paid clause growth telescopes against at most `V0` eliminated variables.

## Next killer test

On the same frozen reachable frontier as R48A, measure

\[
a_*(F)
\]

for every persisted state actually visited by deterministic certified chains, and aggressively search for a family in which required `a_*` grows superpolynomially with original input length.

Finite bounded values cannot prove the theorem. An explicit superpolynomially growing coupled family would refute a proposed polynomial `a(N)`; a symbolic polynomial upper bound on `a_*` for every reachable normalized state would close the representation-reset wall for this grammar.

## Epistemic firewall

- `WEIGHTED_TELESCOPING_ENVELOPE = PROVED`
- `POLYNOMIAL_COMPOSITION_IF_POLYNOMIAL_a_AND_UNIVERSAL_LOCAL_COVERAGE = PROVED_CONDITIONAL`
- `a_EQ_3_SUFFICES_FOR_THE_SEALED_R47Z_PERSISTED_TRAJECTORY = FINITE_FACT`
- `UNIVERSAL_POLYNOMIAL_a_EXISTS = NOT_PROVED`
- `B_C0_PLUS_V0_UNIVERSAL_COVERAGE = OPEN`
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`
- `O4_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_EQ_NP = NOT_PROVED`
- `P_NE_NP = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`
