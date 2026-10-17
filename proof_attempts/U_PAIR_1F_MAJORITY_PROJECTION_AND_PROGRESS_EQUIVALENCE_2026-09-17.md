# U-PAIR-1F — majority projection killer and progress-equivalence theorem

Date: 2026-09-17

Status: `SCOPED_KILLER_FOR_NO_FRESH_AUX_AOR_DAG__UMBRELLA_PROGRESS_GATE_EQUIVALENT_TO_GENERAL_SOLVING__NO_P_EQ_NP_PROMOTION`

## 1. Frozen target

The preregistered concrete candidate `AOR_DAG_NO_FRESH_AUX_V1` stores:

- a GF(2) affine subsystem in reduced row-echelon form;
- a hash-consed CNF clause DAG over the live variables;
- no fresh auxiliaries after initialization.

Exact elimination uses affine pivot substitution when possible and otherwise exact Davis-Putnam resolution, with tautology deletion and subsumption. The frozen progress potential is the number of live variables.

The claim under attack is that every `PAIR+OR_3` input can be reduced to variable-free TRUE/FALSE while every intermediate description and the total work stay polynomial.

## 2. Majority projection family

For `2 <= t <= n-1`, define

`THR_{n,t}(x)=1 iff sum_i x_i >= t`.

Take `t=ceil(n/2)`.

A bounded-fanin Boolean circuit for `THR_{n,t}` has polynomial size. Applying an ordinary Tseitin encoding gives a polynomial-size 3CNF `F_n(x,z)` such that

`THR_{n,t}(x) iff exists z F_n(x,z)`.

The standard exact pair-selector compiler therefore yields a polynomial-size `PAIR+OR_3` source whose exact projection onto the original visible variables is `THR_{n,t}`.

## 3. Affine factors cannot compress majority

### Lemma 1

For `t <= n-1`, the affine hull over GF(2) of the satisfying assignments of `THR_{n,t}` is the whole cube `GF(2)^n`.

### Proof

The all-ones vector `1^n` is satisfying. For every coordinate `i`, the vector `1^n xor e_i` has Hamming weight `n-1 >= t`, so it is also satisfying. Differences from `1^n` therefore contain every basis vector `e_i`; hence the affine hull is all of `GF(2)^n`. QED.

Consequently any affine equation valid on every satisfying assignment of majority is trivial on the full cube. Affine factors do not reduce the required CNF description.

## 4. Exponential CNF lower bound

### Lemma 2

Every CNF equivalent to `THR_{n,t}` contains at least

`binom(n,t-1)`

clauses.

### Proof

Consider a maximal false assignment `a` of Hamming weight exactly `t-1`. Let `Z(a)` be its zero coordinates, so `|Z(a)|=n-t+1`.

Because the CNF rejects `a`, at least one clause `C_a` is falsified by `a`.

For every `z in Z(a)`, flip only coordinate `z` from 0 to 1. The resulting assignment has weight `t` and must satisfy the CNF. Relative to `a`, the only literal that can change from false to true is the positive literal `x_z`; a negative literal `not x_z` could not occur in a clause already falsified by `a` because `x_z=0` there. Therefore `C_a` must contain the positive literal `x_z` for every `z in Z(a)`.

If `a` and `a'` are two distinct weight-`t-1` assignments, their zero sets differ. Pick `z in Z(a) \ Z(a')`. Clause `C_a` contains `x_z`, which is true under `a'`, so `C_a` is not falsified by `a'`.

Hence distinct maximal false assignments require distinct clauses. Their number is `binom(n,t-1)`. QED.

For `t=ceil(n/2)`, this is `2^{Omega(n)}/poly(n)`.

## 5. Consequence for the frozen concrete candidate

After all Tseitin auxiliaries are exactly eliminated, `AOR_DAG_NO_FRESH_AUX_V1` must represent the projected majority relation using only affine factors and CNF clauses on the visible variables.

Lemma 1 makes every nontrivial affine restriction unavailable. Lemma 2 forces exponentially many clauses.

Therefore the candidate cannot maintain polynomial intermediate/final representation volume on this family.

Frozen verdict:

`FAIL_AOR_DAG_NO_FRESH_AUX_V1_POLYNOMIAL_CLOSURE`

This is stronger than the earlier wide-OR obstruction: allowing arbitrary clause width does not save the no-fresh-aux affine+CNF grammar.

## 6. Why a generic progress potential is not yet a new algorithmic theorem

Define an umbrella U-PAIR-1F process as any uniform deterministic exact procedure which, on every `PAIR_SELECTOR_HITTING_3` instance of length `L`:

1. initializes in polynomial time;
2. maintains only polynomial-size states;
3. makes at most `poly(L)` transitions;
4. computes every transition in `poly(L)` time;
5. preserves exact satisfiability/witness semantics;
6. ends in TRUE or FALSE with replayable reconstruction/verification.

### Theorem 3 — terminalization equivalence

Such an umbrella process exists **iff** `PAIR_SELECTOR_HITTING_3` is decidable in deterministic polynomial time.

### Proof

Forward: execute the polynomially many polynomial-cost transitions and read the terminal verdict.

Reverse: given a deterministic polynomial-time decision/reconstruction algorithm, use a one-transition symbolic process whose terminal state is its exact output. QED.

Since 3SAT reduces linearly and witness-preservingly to `PAIR_SELECTOR_HITTING_3`, proving the unrestricted umbrella gate would already prove SAT in P and hence P=NP.

Therefore a progress potential is governance/accounting, not by itself a source of algorithmic power. To make further mathematical progress the transition grammar must be narrower than an arbitrary polynomial-time symbolic operation.

## 7. Surviving frontier

Fresh auxiliaries remain the only escape from the majority projection size lower bound, because a polynomial-size circuit/Tseitin factorization can represent majority compactly.

But fresh auxiliaries must not be allowed to merely rename the same unresolved semantic state indefinitely.

The next admissible gate is therefore a **concrete** auxiliary-safe grammar, not another unrestricted umbrella:

`U-PAIR-1G__GF2_RREF_PLUS_SHARED_BOOLEAN_DAG_WITH_FROZEN_PROGRESS_ACCOUNTING`

It must specify before hostile testing:

- exact node/gate grammar;
- exact elimination/rewrite rules;
- fresh-aux creation rules;
- a polynomially bounded progress potential;
- an anti-alias theorem showing that semantic degrees of freedom cannot be reintroduced under fresh names without charged progress;
- polynomial size/time for every step;
- polynomially many steps to TRUE/FALSE;
- SAT witness reconstruction and independent UNSAT replay.

Scientific firewall:

`GENERAL_SAT_IN_P = NOT_PROVED`

`P_VS_NP = OPEN`
