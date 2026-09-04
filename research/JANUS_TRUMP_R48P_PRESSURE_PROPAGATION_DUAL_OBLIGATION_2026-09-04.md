# JANUS TRUMP R48P — Pressure/Propagation Dual Obligation

Date: 2026-09-04

Status: **SYMBOLIC RESEARCH CONTRACT; O4 REMAINS OPEN**

## Motivation

R48I and R48M expose a sharp distinction between raw projection pressure and actual normalized hardness.

The clean cyclic bipolar family has exact raw pressure

\[
\Delta C_{raw}=r(r-2)
\]

on **every** pivot and saturates the generic occurrence bound. Yet the finite members behave differently under the full frozen authority:

- `r=3`: no pivot is terminal after one DP; normalized local pressure `a_*=3`;
- `r=6`: all 49 pivots become `RUP_UNSAT` immediately after one DP, with zero R33 applications first;
- `r=9`: all 73 pivots behave the same way.

Direct RUP on the unprojected `r=6,9` roots stalls. The terminal contradiction is therefore exposed by projection itself.

## Definition — pressure candidate

For a persisted nonterminal state `F` and pivot `v`, let

\[
P(F,v)=\max(0,C(N(DP_v(F)))-C(F)),
\]

where `N` is the frozen certified normalization authority.

The weighted pressure route is interested in pivots where `P(F,v)` is large relative to the eliminated variable count.

## Definition — propagation escape

Call a pivot `v` **terminally propagation-fragile** if the frozen exact-DP record is valid and the subsequent normalization reaches a verified `RUP_UNSAT` terminal.

Call a state **post-DP propagation-evasive** if at least one pivot relevant to a proposed pressure lower-bound path remains nonterminal after the complete certified normalization stack.

For an all-pivot lower-bound state, every pivot considered in the lower-bound claim must avoid semantic terminalization; a single polynomially discoverable verified terminal already supplies coverage.

## Dual obligation for a genuine pressure lower-bound family

A family intended to show that the weighted-pressure route needs a large coefficient cannot be certified hard from raw projection growth alone.

It must establish simultaneously:

### Obligation A — normalized survivor pressure

For the claimed hard state `F_n`, every eligible nonterminal certified successor must require the claimed pressure, e.g.

\[
a_{req}(F_n,v)\ge A_n.
\]

This must be measured **after** the full frozen normalization authority, not from raw parent-pair counts.

### Obligation B — terminal evasion

No polynomially discoverable pivot in the same authority may reach a verified semantic terminal.

In particular, if any pivot gives `RUP_UNSAT`, the state is covered regardless of how large its raw DP expansion was.

Therefore a pressure lower-bound family must satisfy

\[
\boxed{\text{HIGH NORMALIZED PRESSURE} \land \text{NO VERIFIED TERMINAL ESCAPE}.}
\]

## R48I/R48M counterexample to raw-pressure-only reasoning

For `r=6` and `r=9`:

1. every pivot has large exact raw pressure;
2. direct RUP on the preprojection root stalls;
3. exact DP on any pivot changes the formula;
4. R33 applies zero rules in normalization round zero;
5. RUP then independently verifies UNSAT for every pivot.

Hence

\[
\boxed{\text{RAW PRESSURE GROWTH} \not\Rightarrow \text{NORMALIZED HARDNESS}.}
\]

Projection can expose a global propagation contradiction that is invisible before projection.

## Consequence for construction searches

Future pressure-amplifying searches should treat terminal fragility as a first-class negative objective. A useful adversarial score must prefer states with both:

1. larger minimum normalized `a_req` over nonterminal eligible pivots; and
2. zero terminal-candidate count.

A construction that increases raw `p*n` while also increasing the probability that projection reveals an UP contradiction is not moving toward an O4 obstruction.

## Potential collapse theorem direction

The opposite route is equally valuable: characterize a structural condition `Q(F)` such that

\[
Q(F) \Rightarrow \exists v:\ Normalize(DP_v(F))=\text{verified terminal}.
\]

R48M suggests a stronger special case on its finite cyclic members:

\[
Q_r(F) \Rightarrow \forall v:\ Normalize(DP_v(F))=RUP\_UNSAT.
\]

A symbolic theorem explaining the r=6/r=9 all-pivot collapse could become a universal **collapse lemma** for a dense subclass, shrinking O4 rather than producing a hard family.

## Interaction with the width route

R48N supplies another possible escape from pressure: a high-pressure persisted state can still be polynomially bounded if its maximum persisted clause width stays under a universal constant.

Thus a genuine representation-growth obstruction must ultimately defeat all certified polynomial envelopes available to the frozen grammar, not merely make one scalar pressure large.

## Canonical research law

\[
\boxed{PRESSURE\ WITHOUT\ TERMINAL\ EVASION\ IS\ NOT\ A\ HARDNESS\ WITNESS.}
\]

\[
\boxed{HIGH\ a_*\ WITHOUT\ WIDTH/REPRESENTATION\ GROWTH\ IS\ NOT\ YET\ A\ SUPERPOLYNOMIAL\ WITNESS.}
\]

## Firewalls

- `UNBOUNDED_NORMALIZED_PRESSURE = NOT_PROVED`.
- `UNIVERSAL_POST_DP_PROPAGATION_COLLAPSE = NOT_PROVED`.
- `UNIVERSAL_CONSTANT_WIDTH_COVERAGE = NOT_PROVED`.
- `UNIVERSAL_ROOT_POLYNOMIAL_PRESSURE_BOUND = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
