# JANUS TRUMP R50G4 — Prefix Closure by Exact R33 Microsteps

## Scope

Let `F` be a canonical Boolean CNF with `W(F) <= 4`.  Define

`mu(F) = (V(F), C(F), L(F))`

with lexicographic order, where `V` is the number of variables, `C` the number of clauses, and `L` the number of literal occurrences.

R50G4 does **not** add a heuristic.  It replaces one implementation-level batch decision by the deterministic first applicable rule of the already frozen R33 rule order.

## Definition: R33 microstep

At state `F`, inspect the frozen R33 priority order:

1. tautology deletion;
2. unit propagation;
3. pure-literal autarky;
4. subsumption;
5. blocked-clause elimination;
6. bounded variable elimination (BVE);
7. declared 2CNF/HORN terminal;
8. stalled lean core.

If the first applicable nonterminal rule constructs `G` and `W(G) <= 4`, authorize `F -> G` as one R33 microstep.  If it constructs `G` with `W(G) > 4`, record the exact proposal and certificate but do not persist `G`; continue from unchanged `F` to the existing R49H and exhaustive-R47J lanes.

No score, sampling, learned model, or SAT oracle selects the rule.

## Lemma 1 — first-rule conformance

The microstep rule is exactly the first rule that frozen `r33.simplify(F)` would append to its history.  This follows because the microstep uses the same total priority order and the same deterministic tie breaking as R33.  R50G4 additionally checks this mechanically.

## Lemma 2 — exactness and reconstruction

Every authorized microstep is an existing R33 rule instance.  Frozen R33 already records the data needed to replay and reconstruct:

- unit literal for unit propagation;
- pure literal for autarky;
- witness subclause for subsumption;
- blocking literal for BCE;
- positive/negative parent families and resolvents for BVE.

Therefore an authorized R33 microstep preserves SAT exactly, and a satisfying assignment of its successor can be lifted through the existing R33 reconstruction map.  No new semantic inference rule is introduced.

## Lemma 3 — W4 invariant and the only escape rule

For every non-BVE R33 rule, clause width cannot increase:

- deleting a tautology, subsumed clause, or blocked clause only removes clauses;
- pure-literal autarky only removes clauses;
- unit propagation removes satisfied clauses and removes one literal from touched clauses.

Hence a first transition from `W<=4` to `W>4` cannot be caused by any of those rules.

BVE may form a resolvent from two parent remainders and can therefore increase width.  Thus

`FIRST_R33_W4_ESCAPE => BVE`.

The authority predicate `W(G)<=4` makes W4 persistence immediate for every authorized microstep.

## Lemma 4 — strict descent of mu=(V,C,L)

Consider an authorized nonterminal microstep.

- Tautology deletion: `C` strictly decreases; `V` cannot increase.
- Unit propagation on variable `x`: all occurrences of `x` and `-x` disappear, so `V` strictly decreases.
- Pure-literal autarky on variable `x`: all occurrences of its only polarity disappear, so `V` strictly decreases.
- Subsumption: one clause is deleted, so `C` strictly decreases; `V` cannot increase.
- BCE: one clause is deleted, so `C` strictly decreases; `V` cannot increase.
- BVE on `x`: all clauses containing `x` or `-x` are removed and every resolvent omits `x`; no fresh variable is introduced, so `V` strictly decreases.

Therefore in every case

`mu(G) <_lex mu(F)`.

## Lemma 5 — polynomial first-step cost

On an explicit CNF with `C` clauses, `L` literal occurrences and `V` variables, each frozen R33 first-rule test is polynomial:

- tautology/unit/pure scans are polynomial in `L`;
- subsumption is bounded by pairwise clause comparison;
- BCE is bounded by clause/literal and opposite-occurrence scans;
- BVE inspects at most the explicit cross product of positive and negative occurrences for each candidate variable, hence polynomial in the explicit state size.

The W4 authority check is a linear scan of the produced clauses.  Thus one R33 microstep is polynomially computable and checkable in the current explicit state size.

## Theorem 6 — prefix closure

Suppose frozen full-batch R33 history from `F` begins

`F = F0 -> F1 -> ... -> Fk -> H`

where every `Fi` for `0<=i<=k` satisfies `W(Fi)<=4`, and the next batch rule either leaves W4 or the batch ends.

By Lemma 1, the first microstep from `F0` is exactly `F0->F1`.  Since `F1` is W4-safe, it is authorized.  Applying the same argument inductively at `F1,...,F{k-1}` authorizes every edge of the prefix.

Hence the whole safe prefix factors into authorized transitions of the refined controller:

`F0 => F1 => ... => Fk`.

Each edge is exact, W4-preserving, polynomially checkable, and strictly decreases `mu`.

Therefore every state of a nonempty W4-safe R33 prefix is reachable under the refined controller from the same predecessor.

## Corollary 7 — shape of a minimal OPEN state

Assume the refined controller `U_mu` has a reachable OPEN state and choose `F*` minimal under `mu`.

If the first R33 rule at `F*` produced a W4-safe successor `G`, then by Theorem 6 the transition is authorized and by Lemma 4 `mu(G)<mu(F*)`; hence `F*` would not be OPEN.  Contradiction.

So a minimal OPEN state has no nonempty safe R33 prefix.  Its R33 status is exactly one of:

1. `FIXED_POINT` / no R33 reduction; or
2. the **first** applicable R33 reduction is BVE and its candidate immediately leaves W4.

Thus the old `PREFIX_CLOSURE_OR_ESCAPE_ELIMINATION` gap is reduced to the single mathematical obligation

`IMMEDIATE_BVE_ESCAPE_ELIMINATION_OR_EXISTING_CERTIFIED_DOOR`.

## Firewall

This theorem defines a refined deterministic controller `U_mu`; it does not retroactively change the semantics of the previous full-batch guarded `U`.  Proving prefix closure alone does not prove universal progress, `SAT in P`, or `P=NP`.
