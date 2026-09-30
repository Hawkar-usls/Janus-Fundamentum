# C024 — POLYNOMIAL RESIDUAL-CACHE BRIDGE, PURE-MATH REFORMULATION

**Status:** conditional bridge theorem proved; correctness/call-graph/local-budget lemmas proved; universal polynomial state-count and state-size bounds remain open.

**Claim ceiling:** this document does **not** prove `P = NP` or `P != NP`.

## 0. Evidence firewall

This line contains no mythological, historical, symbolic, semantic, paranormal, or associative operator in its mathematics.

The only admissible promotion classes are:

- definition;
- lemma with proof;
- theorem with proof;
- explicit counterexample;
- finite reproducible computation carrying an explicit asymptotic claim ceiling.

Heuristics may choose what theorem to attack next. They have zero proof authority.

---

## 1. Exact machine under study

Let `F` be a CNF and let `|F|` denote the bit length of a fixed deterministic canonical encoding. Let `N = |F_0|` for the input formula.

For every recursive call, Policy-0A performs:

1. exhaustive unit propagation `U(F)`;
2. exact cache lookup on the canonical pre-resolution residual `K = U(F)`;
3. one deterministic one-layer Resolution pass `R(K)` with

   - `width_limit = max_clause_width(K) + 1`,
   - `attempt_budget = max(64, 4 * literal_occurrences(K))`,
   - `addition_budget = max(8, clause_count(K) // 4)`;

4. a second exhaustive unit propagation `U(R(K))`;
5. deterministic branching on a most-frequent variable, tie-broken by smallest variable id, false branch first;
6. exact memoization of the completed key `K` and its Boolean answer.

No step introduces a new propositional variable.

---

## 2. Correctness lemmas

### Lemma 2.1 — unit propagation preserves satisfiability

For every CNF `F`, exhaustive unit propagation either derives contradiction, or returns a residual `U(F)` such that

`SAT(F) iff SAT(U(F))`.

**Proof.** Each propagated unit literal is forced in every satisfying assignment. Restricting by a forced literal preserves existence of satisfying assignments. A conflicting forced assignment is an explicit contradiction. Repeating the argument to the fixpoint proves the claim. □

### Lemma 2.2 — the local Resolution pass preserves satisfiability

If `C` is a resolvent of clauses of `F`, then `F |= C`. Hence adding any finite sequence of accepted resolvents leaves satisfiability unchanged:

`SAT(F) iff SAT(F ∧ C_1 ∧ ... ∧ C_t)`.

**Proof.** Soundness of the Resolution rule. □

### Lemma 2.3 — deterministic branching is complete

For every nonterminal residual `F` containing variable `x`,

`SAT(F) iff SAT(F|x=0) or SAT(F|x=1)`.

**Proof.** Every total assignment fixes `x` to exactly one Boolean value, and restriction preserves precisely the assignments having that value. □

### Lemma 2.4 — exact-cache reuse is sound

If a completed cache entry stores `(K,b)` and a later call has canonical key exactly equal to `K`, returning `b` is sound.

**Proof.** The two keys are the same CNF, not merely similar formulas. The cached answer is therefore the answer to the same decision problem. Completion-before-reuse prevents cyclic self-justification. □

### Theorem 2.5 — Policy-0A is a sound and complete SAT decision procedure when run without a resource cap

**Proof.** Apply Lemmas 2.1–2.4 recursively. Every branch removes at least the chosen branch variable, no rule creates variables, so recursive depth is finite. The Boolean returned at every node equals the satisfiability value of that node, hence the root answer equals `SAT(F_0)`. □

This theorem is a correctness theorem only. It gives no polynomial-time bound.

---

## 3. Structural complexity lemmas already available without solving P vs NP

Let `S(F_0)` be the number of unique nonterminal pre-resolution cache keys created during a complete run.

### Lemma 3.1 — depth bound

`maximum_depth <= number_of_input_variables <= N`.

**Proof.** A branch chooses a variable still present in the current residual and both child restrictions eliminate that variable. Neither unit propagation nor Resolution introduces a new variable. Thus no root-to-leaf path branches on more distinct variables than occur in the input. A fixed bit encoding uses at least one bit per represented variable occurrence/identifier, so the number of variables is at most `N`. □

### Lemma 3.2 — recursive-call bound from unique states

For an uncapped complete run,

`recursive_calls <= 2*S(F_0) + 1`.

Consequently `memo_hits <= 2*S(F_0) + 1` and recursive branch edges are at most `2*S(F_0)`.

**Proof.** Only a newly created nonterminal state can spawn recursive children. Each such state spawns at most two child calls. Cache-hit calls and terminal calls spawn no children. The recursion graph explored by the depth-first execution therefore has at most two outgoing recursive edges per unique state, plus the root call. □

This closes a previously implicit gap: a polynomial unique-state bound would automatically give a polynomial **number of calls**.

### Lemma 3.3 — local inference count is polynomial in the current representation size

At a key `K` having `L` literal occurrences and `m` clauses, one local Resolution pass performs at most

`max(64,4L)`

charged complementary-pair attempts and accepts at most

`max(8,floor(m/4))`

new clauses.

**Proof.** This is the exact frozen rule of `limited_resolution`. □

This is a per-state polynomial bound in the **current state size**. It is not yet a polynomial bound in the original input length `N`.

---

## 4. Newly exposed hidden gap: polynomial state count alone is insufficient

The old bridge was often summarized as

`polynomial number of residual states => polynomial time`.

That implication needs a second invariant: every encountered residual must itself have polynomial representation size in the original input length.

Let `m_t` be the clause count on one branch immediately before the local Resolution pass at depth `t`. Ignoring clause deletion by restriction gives the valid worst-case recurrence

`m_(t+1) <= m_t + max(8,floor(m_t/4))`.

For `m_t >= 32`,

`m_(t+1) <= (5/4)m_t`.

More uniformly,

`m_(t+1) + 32 <= (5/4)(m_t + 32)`

and therefore

`m_t + 32 <= (5/4)^t (m_0 + 32)`.

Because `t <= N`, the current rules by themselves provide only an exponential worst-case upper bound on accumulated clause count. This does **not** prove that exponential growth occurs; it proves that the desired polynomial state-size invariant does not follow from the present budgets.

### Required new invariant

We must separately establish constants `a,b` such that every encountered key and post-resolution residual obeys

`bit_length(state) <= N^a`

and every canonicalization/lookup/verification operation costs at most `N^b` worst-case time.

Without this, even `S(F_0) <= N^c` is not sufficient for the full bridge.

---

## 5. Pure conditional bridge theorem

### Theorem 5.1 — Polynomial residual-cache bridge, conditional form

Assume there exist fixed constants `a,c,q >= 1` and a deterministic implementation of Policy-0A such that for every input CNF `F_0` of encoded length `N`:

1. **Polynomial unique-state bound:** `S(F_0) <= N^c`.
2. **Polynomial state-size bound:** every canonical key and derived residual created by the run has bit length at most `N^a`.
3. **Polynomial primitive bound:** unit propagation, canonicalization, exact cache lookup/insert, one frozen local Resolution pass, branch selection, child restriction, certificate emission, verification, and SAT-witness reconstruction each cost at most `N^q` per call/state under the fixed representation.

Then Policy-0A decides CNF-SAT in deterministic polynomial time.

More precisely, by Lemma 3.2 the run has at most `2N^c+1` recursive calls, so its total charged time is

`O(N^(c+q))`

up to fixed encoding/logarithmic factors already absorbed into `q`.

Since CNF-SAT is NP-complete, this implies `P = NP`.

**Proof.** Correctness is Theorem 2.5. Lemma 3.2 bounds the number of calls by a polynomial. Assumptions 2–3 bound the cost of each call/state and all proof/witness bookkeeping by a polynomial in the original input length. Multiplication yields polynomial total deterministic time. A deterministic polynomial-time algorithm for an NP-complete language implies `P = NP`. □

### What has and has not been proved

`CONDITIONAL_BRIDGE_THEOREM = PROVED`

`UNIVERSAL_POLYNOMIAL_STATE_COUNT = OPEN`

`UNIVERSAL_POLYNOMIAL_STATE_SIZE = OPEN`

`P_EQUALS_NP = NOT_ESTABLISHED`

---

## 6. External lower-bound barrier that any positive proof must defeat

Beame, Impagliazzo, Pitassi, and Segerlind's Formula-Caching analysis proves an exponential lower bound for the graph-tautology family `GT_n` even for the stronger basic caching variant with Weakening/Subsumption: any `FC^WS` refutation requires at least `2^(n-2)` nodes. Their result also shows that adding a returned reusable reason changes the proof-system strength substantially.

Primary reference:

Paul Beame, Russell Impagliazzo, Toniann Pitassi, Nathan Segerlind, **Formula Caching in DPLL**, ACM Transactions on Computation Theory 1(3), 2010; earlier ECCC TR06-140 / CCC version.

This theorem does not automatically lower-bound `JANUS-FC_local`, because Policy-0A inserts a deterministic local Resolution layer before branching. Therefore the current positive bridge cannot be proved by any argument that treats exact memoization alone as sufficient.

The local Resolution layer is the exact mathematical fork:

- either prove that it collapses the historical exponential witness structure to polynomially many polynomial-size residuals on **all** CNFs;
- or prove that a hard family remains superpolynomial under this layer, which would refute the current bridge for Policy-0A.

---

## 7. TOPA adversarial pass translated into mathematics

TOPA is used here only as a falsification protocol. Its non-mathematical subject matter has zero authority in C024.

### Attack T1 — "memoization should make the search polynomial"

**Status: REFUTED AS A GENERAL ARGUMENT.**

Known Formula-Caching lower bounds provide explicit polynomial-size CNFs whose residual-caching proof requires exponentially many nodes in the basic/WS model.

### Attack T2 — "the Resolution budget is polynomial, therefore the whole run is polynomial"

**Status: REFUTED.**

A polynomial amount of work **per state** multiplied by an unknown number of states is not a polynomial total bound.

### Attack T3 — "polynomial unique states alone would close the bridge"

**Status: REFUTED AS STATED.**

Current local clauses can accumulate along a branch; a separate polynomial state-size invariant is required. Section 4 gives the explicit recurrence exposing this gap.

### Attack T4 — "finite GT_3..GT_10 growth proves the asymptotic direction"

**Status: QUARANTINED.**

Finite growth can falsify a preregistered envelope but cannot establish a universal asymptotic polynomial or exponential theorem.

### Attack T5 — "a small local Resolution budget cannot destroy an exponential lower-bound witness"

**Status: OPEN.**

One strategically placed derived clause can remove exponentially many future branches. The effect must be proved at the invariant level.

### Attack T6 — "Python dict/set behavior is a worst-case mathematical complexity proof"

**Status: REJECTED.**

A formal polynomial-time claim must use a deterministic worst-case representation model. Hash-table average-case behavior is not admissible as the complexity theorem.

### Survivor after the TOPA pass

The only positive route that survives is the following exact two-part theorem target:

`PURE_BRIDGE_CORE = POLY_STATE_COUNT + POLY_STATE_SIZE`.

Everything else is already reducible to proved correctness and polynomial bookkeeping lemmas.

---

## 8. The two remaining killer lemmas

### Killer Lemma A — universal residual-count bound

Find fixed `c` and prove for every CNF `F_0` of length `N`:

`S(F_0) <= N^c`.

This must be a theorem over the exact Policy-0A transition relation, not a fitted benchmark envelope.

### Killer Lemma B — universal residual-size bound

Find fixed `a` and prove every state created on every Policy-0A run satisfies

`bit_length(state) <= N^a`.

The proof must charge all retained local resolvents across recursive depth.

If both lemmas are proved, Theorem 5.1 closes the bridge and yields `P = NP`.

If either lemma is disproved by an explicit infinite family, the current Policy-0A bridge is dead and the counterexample becomes the next design constraint.

---

## 9. Next proof program — no heuristics

### Lane A: attack the positive bridge

1. Define a polynomial potential `Phi(F)` over canonical residuals.
2. Prove every newly created exact key consumes a distinct unit of a universe of size `poly(N)`.
3. Prove the local Resolution layer cannot increase the potential universe beyond `poly(N)`.
4. Prove all retained clauses admit a polynomial-size canonical basis, with redundant derived clauses discarded by a sound polynomial normalization.
5. Only after 1–4, promote `POLY_STATE_COUNT` and `POLY_STATE_SIZE`.

### Lane B: try to kill the bridge first

1. Reconstruct the `GT_n` Formula-Caching novelty invariant line by line.
2. Classify every Policy-0A one-layer resolvent by the order information it adds.
3. Prove or refute a bounded-witness-destruction lemma for one accepted resolvent.
4. Sum over the frozen addition budget without hiding an exponential support term.
5. In parallel, test a Tseitin/lifted family where any useful short derivation must cross a known proof-complexity bottleneck.

The first rigorous result wins. No preferred conclusion is encoded.

---

## 10. Canonical status

```text
POLYNOMIAL_RESIDUAL_CACHE_BRIDGE_FOR_CNF_SAT
  CORRECTNESS                         = PROVED
  MAX_RECURSION_DEPTH                 = POLYNOMIAL_PROVED
  CALLS_FROM_POLY_UNIQUE_STATES       = POLYNOMIAL_PROVED
  LOCAL_BUDGET_PER_STATE              = POLYNOMIAL_IN_CURRENT_STATE_SIZE_PROVED
  CONDITIONAL_TOTAL_TIME_THEOREM      = PROVED
  UNIVERSAL_POLYNOMIAL_STATE_COUNT    = OPEN
  UNIVERSAL_POLYNOMIAL_STATE_SIZE     = OPEN
  GT_LOCAL_RESOLUTION_ROBUSTNESS      = OPEN
  P_EQUALS_NP                         = NOT_ESTABLISHED
  P_NOT_EQUALS_NP                     = NOT_ESTABLISHED
```

The research target is now smaller and cleaner: **prove or refute two universal bounds.**
