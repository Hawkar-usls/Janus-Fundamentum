# JANUS TRUMP R47B — polynomial R33/RUP resource envelope

Status: **symbolic proof for the frozen local grammar; universal coverage remains OPEN**.

## 1. Scope

This note proves a polynomial resource envelope for the already-frozen local macro

`exact DP -> R33 -> affine/RUP -> verification`

on any *single candidate pivot*, and for a deterministic scan of at most all current variables. It does **not** prove that an accepted pivot exists on every reachable nonterminal state.

Let a canonical input state have:

- `C` clauses,
- `V` variables,
- `L` literal occurrences.

For an accepted-state trajectory from original input `(C0,V0)`, the previously sealed CLV-height lemma gives `C <= C0`, `V <= V0`, and `L <= C0*V0` for accepted final states. Temporary exact-DP ascent is handled below separately.

## 2. Exact DP is polynomial

For pivot `v`, let `p` and `n` be positive and negative occurrence counts. Since `p+n <= C`,

`p*n <= floor(C^2/4)`.

The producer enumerates exactly these parent pairs, discards tautological resolvents, deduplicates, unions with the unaffected base, and performs pairwise subsumption minimization. Hence a raw/canonical DP pool has at most

`P = C + floor(C^2/4) + 1 = O(C^2)`

clauses. No resolvent contains a fresh variable, and a non-tautological canonical clause has at most `V` literals, so peak literal mass is `O(C^2 V)`. Pair generation and pairwise subsumption are polynomial. The independent DP replay repeats the same bounded construction and is polynomial as well.

## 3. R33 cannot require a magic constant

The implementation currently exposes a default `max_steps=100000`. That number must not be theorem authority.

For a canonical R33 input with `C` clauses and `V` variables, even before tautology deletion a canonical clause contains at most the two signed literals for each variable. Therefore a safe literal bound is

`Lmax = 2*C*max(1,V)`.

Every successful frozen R33 rule application strictly decreases the lexicographic measure

`CLV = (clauses, literal_mass, variables)`.

No rule introduces a fresh variable. Clause count never increases: deletion/unit/pure/subsumption/blocked rules reduce it, while BVE is admitted only when its resolvent count does not exceed the removed parent count and the final CLV is strict. Consequently every active state stays inside

`0 <= C' <= C`, `0 <= L' <= Lmax`, `0 <= V' <= V`.

There are at most

`H_R33(C,V) = (C+1)*(Lmax+1)*(V+1)`

distinct CLV triples in that box. A strictly descending trajectory has fewer than `H_R33` successful transformations. The loop needs at most one additional final inspection, and `range(H_R33)` is sufficient because at most `H_R33-1` successful transformations can precede that final inspection.

Thus the theorem-safe cap is input-dependent and

`H_R33 = O(C^2 V^2)`.

Each R33 inspection is polynomial: tautology/unit/pure scans are linear in represented size; subsumption is pairwise; blocked-clause checking is bounded by clause/literal cross-products; BVE scans at most `V` pivots and at most `C^2` parent pairs per pivot. Multiplying polynomial work per inspection by polynomially many inspections remains polynomial.

## 4. RUP vivification is polynomial despite being slow

Let the RUP input have literal mass `L` and `V` variables.

A deterministic unit-propagation call can have at most `V` assignment-growing sweeps plus one final sweep. Each sweep inspects at most the represented formula's `L` literals. Therefore one UP call uses at most `O((V+1)L)` literal inspections.

`first_rup_strengthening` tests at most one deletion for each current literal, so at most `L` proposals. Its search work is therefore `O((V+1)L^2)` literal inspections.

Every successful frozen strengthening removes exactly one literal and strictly decreases the RUP measure. There can be at most `L` successful strengthenings, followed by a final no-proposal/terminal check. A coarse bound for the entire producer is therefore

`O((V+1)L^3)`.

The independent checker replays at most `L` strengthening records. Each replayed RUP conflict check reaches a propagation fixpoint after at most `V+1` assignment-growing rounds and scans polynomial represented size. Hence independent replay is also polynomial (coarsely `O(V L^2)` plus canonicalization/hashing over polynomial-sized records).

This explains the observed performance problem without converting it into an exponential-complexity problem: RUP can be a high-degree polynomial and still be painfully slow. R46A/R46D remain performance work, not correctness authority.

## 5. Composition for one macro candidate

After exact DP, the R33/RUP input has at most `P=O(C^2)` clauses and `O(C^2 V)` literals. Substituting this polynomially enlarged representation into the R33 and RUP bounds still yields a polynomial in the pre-macro `(C,V)`.

Affine GF(2), Horn forward chaining and 2-SAT SCC terminal lanes are standard polynomial procedures and are independently verified by the frozen implementation. SAT model reconstruction reverses at most the polynomially many recorded R33 operations plus one eliminated DP pivot.

Therefore a single frozen macro candidate has polynomial construction, normalization, certificate generation and verification cost.

## 6. Deterministic all-variable scan

The current selector examines at most `V` variables. Multiplying the single-candidate polynomial by `V` remains polynomial. Independent replay is performed only for the selected accepted macro and is itself polynomial.

Thus, once R33 is invoked with the theorem-safe input-dependent cap rather than relying on the arbitrary `100000` default, the frozen local transition machinery has a polynomial resource envelope.

## 7. What this closes and what it does not

This supports:

`O3_POLYNOMIAL_WORK_PER_TRANSITION = SYMBOLICALLY_CLOSED_FOR_FROZEN_GRAMMAR_WITH_POLYCAP_R33`.

Together with the previously proved polynomial accepted-state CLV height, global polynomial composition becomes conditional primarily on the missing universal coverage statement.

It does **not** establish:

`FOR ALL reachable nonterminal F, EXISTS accepted certified macro`.

Therefore:

- `R47A_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`

The next theorem-critical wall remains universal existence/discovery of a certified terminal/descent transition on every reachable residual state.
