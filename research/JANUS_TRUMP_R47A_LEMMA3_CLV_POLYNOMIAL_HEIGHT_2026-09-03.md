# R47A Lemma 3 — Accepted CLV descent has polynomial height

Status: **SYMBOLIC PROGRESS-HEIGHT LEMMA PROVED, CONDITIONAL ON ACCEPTED-STEP SEMANTICS**

Let the initial canonical formula be `F0` with

`C0 = #clauses(F0)`, `V0 = #variables(F0)`.

For every canonical reachable accepted state `F`, define the frozen TRUMP measure

`CLV(F) = (C(F), L(F), V(F))`

ordered lexicographically, where `L(F)` is total literal mass.

The frozen R45A acceptance rule accepts a nonterminal macro only when the final canonical formula has strict CLV descent relative to the input state. Exact DP, R33 simplification, affine recognition, and RUP do not introduce fresh variables; therefore every accepted state uses only variables from the original input and

`V(F) <= V0`.

Strict lexicographic descent from `F0` implies

`C(F) <= C0`.

A canonical non-tautological clause over at most `V0` variables contains at most one literal for each variable, hence has length at most `V0`. Therefore

`L(F) <= C(F)*V0 <= C0*V0`.

Thus every accepted state lies in the finite rectangular rank domain

`0 <= C <= C0`,
`0 <= L <= C0*V0`,
`0 <= V <= V0`.

The number of possible CLV triples in this domain is at most

`H(C0,V0) = (C0+1)(C0*V0+1)(V0+1)`.

Because every accepted nonterminal transition strictly decreases the lexicographic CLV tuple, no trajectory can contain more than `H(C0,V0)-1` accepted nonterminal transitions before termination or failure of universal coverage.

Since `C0` and `V0` are both bounded by the input encoding length `N`,

`H(C0,V0) = O(N^4)`

under the coarse substitution `C0<=N`, `V0<=N`.

Hence the accepted-step trajectory has polynomial height. The remaining theorem burden is not an exponential number of accepted descents; it is proving that every reachable nonterminal state has a polynomially discoverable accepted transition (or terminal certificate), and that each transition including normalization/verification has a polynomial resource bound in the original input size.

## Relation to the existing rank encoding

R42 already encodes the same bounded lexicographic idea numerically via

`Lmax = C0*V0`

and

`mu(F) = C*(Lmax+1)*(V0+1) + L*(V0+1) + V`,

with a rank-bound assertion when `C>C0`, `V>V0`, or `L>Lmax`. The argument above explains why those bounds hold for canonical accepted CLV-descending states when no macro introduces fresh variables.

## Important caveat: temporary intermediate ascent

R45A permits temporary internal ascent inside a macro. This lemma bounds the sequence of **accepted final states**, not every transient pool produced during exact DP. Polynomial per-transition intermediate-size bounds remain a separate obligation and must be composed with this height bound before any global runtime theorem can be claimed.

## Consequence for the Captain-obviousness charter

This closes the specific fear that strict CLV descent could hide exponentially many accepted macro steps merely because the measure is well-founded. Under the stated frozen accepted-step semantics, the height itself is polynomial.

It does not close universal coverage or total polynomial runtime.

## Firewall

- `O2_PROGRESS_HEIGHT = SYMBOLICALLY_PROVED_CONDITIONAL_ON_FROZEN_ACCEPTED_STEP_SEMANTICS`
- `O3_POLYNOMIAL_WORK_PER_TRANSITION = OPEN`
- `O4_UNIVERSAL_COVERAGE = OPEN`
- `O5_GLOBAL_COMPLEXITY_COMPOSITION = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
