# C025 Unified Proof-Carrying Akinator / JEC

Status: `EXPLORATORY / FAIL-CLOSED / P_VS_NP_OPEN`

This document freezes a single deterministic composition of mechanisms that previously lived in separate JANUS research lanes.

## Claim boundary

This is **not** a proof that `P = NP`. The purpose of this branch is to remove heuristic promotions and test whether the already-developed mechanisms compose into one honest algorithmic candidate.

No heuristic, probability score, random tie-break, ML prediction, activity score, physical signal, or externally supplied SAT/equivalence answer is allowed to advance the proof state.

If no independently checkable move is available, the only legal terminal is `OPEN`.

## Unified state

For CNF input `F` of encoded length `N`, maintain:

- `R`: canonical residual representation;
- `L`: proof-carrying extension-macro library;
- `Pi`: append-only proof ledger;
- `Q`: certified residual quotient / hash-consed state graph;
- `B`: explicit resource ledger;
- `mu`: lexicographic progress tuple.

## Allowed proof languages

A transition may be justified only by an admitted checker for one of:

1. exact syntactic/canonical normalization;
2. clause subsumption;
3. implication/SCC closure (2-SAT lane);
4. GF(2) row-space/RREF lane;
5. bounded-width Resolution when the width bound is explicitly charged;
6. supplied RUP-style trace, without assuming a universal polynomial finder;
7. B2/Extended-Resolution extension definitions of the frozen form `e <-> (a AND b)` and their conservative definitional CNF;
8. previously verified extension macros reachable from the same root fingerprint.

A supplied certificate never implies cheap discovery. Discovery work is charged separately.

## Deterministic algorithm candidate

```text
UNIFIED_JANUS(F):
    S := ROOT_STATE(F)

    while not terminal(S):
        S := CANONICALIZE_WITH_REPLAY(S)

        if SAT_TERMINAL_CERTIFIED(S):
            return SAT + witness + ledger

        if UNSAT_TERMINAL_CERTIFIED(S):
            return UNSAT + proof + ledger

        M := ALL_CHEAP_CERTIFIED_MERGES(S)
        if M is nonempty:
            S' := APPLY_CANONICAL_MERGE_SET(S, M)
            REQUIRE(PROGRESS(S', S))
            S := S'
            continue

        Q := FIRST_CERTIFIED_PROGRESS_QUESTION(S)
        if Q exists:
            S' := APPLY_CERTIFIED_QUESTION(S, Q)
            REQUIRE(PROGRESS(S', S))
            S := S'
            continue

        E := FIRST_CERTIFIED_EXTENSION(S)
        if E exists:
            # E is an explicitly derived reusable macro, never a guessed one.
            S' := INTRODUCE_EXTENSION_AND_RECOMPRESS(S, E)
            REQUIRE(PROGRESS(S', S))
            S := S'
            continue

        return OPEN + complete refusal/resource ledger
```

## No heuristic Akinator

The Akinator layer is retained only as a **question scheduler** over proof-carrying moves.

It may rank nothing by an unproved score. Instead it enumerates an explicitly bounded deterministic candidate set and chooses the lexicographically first candidate that comes with a verifier-accepted certificate and satisfies the progress gate.

There is no `best-looking split`, no estimated Walsh balance, no probabilistic branch, and no oracle answer.

`QUESTION_COUNT` and `ANSWER_COST` remain separately charged.

## Deterministic DISCOVER_MACRO interface

The old Junction Extension Compression idea becomes this exact interface:

```text
DISCOVER_MACRO(S):
    C := GENERATE_BOUNDED_CANDIDATES(S)
    for candidate in canonical_order(C):
        cert := DERIVE_EXTENSION_CERTIFICATE(S, candidate)
        if VERIFY_EXTENSION(S, candidate, cert)
           and MACRO_IS_REUSABLE(S, candidate)
           and PROGRESS_AFTER_RECOMPRESSION(S, candidate):
            return (candidate, cert)
    return NONE
```

Every generator has an explicit polynomial budget. Exhausting that budget yields `NONE`, never a guessed candidate.

## Progress measure

Freeze the first composite potential as a **test target**, not a proved universal theorem:

```text
mu(S) = (
    unresolved_original_variables,
    uncertified_residual_classes,
    explicit_residual_literal_volume,
    unresolved_frontier_volume,
    unshared_repeated_proof_fragments
)
```

ordered lexicographically after canonicalization.

A state transition is admitted only when the independent verifier recomputes `mu` and proves strict decrease.

This guarantees termination only if each component is polynomially bounded in `N`; that universal bound remains an open theorem obligation.

## Resource firewall

The engine must charge separately:

```text
proposal_work
certificate_discovery_work
verification_work
state_bytes
proof_bytes
extension_definition_bytes
extension_count
residual_state_count
question_count
recompression_work
witness_recovery_work
```

No one quantity may be hidden inside another.

## Exact theorem obligations

The branch may advance beyond `EXPLORATORY` only after all of the following are proved:

```text
TOTAL_CORRECTNESS = PROVED
EXTENSION_SOUNDNESS = PROVED
STATE_REUSE_COMPLETENESS = PROVED
QUESTION_DISCOVERY_TOTAL <= poly(N) = PROVED
NUMBER_OF_EXTENSIONS <= poly(N) = PROVED
CERTIFIED_RESIDUAL_VOLUME <= poly(N) = PROVED
TOTAL_PROOF_SEARCH <= poly(N) = PROVED
TOTAL_RECOMPRESSION <= poly(N) = PROVED
WITNESS_RECOVERY <= poly(N) = PROVED
```

Only then would the construction imply `SAT in P` and therefore `P = NP`.

## Immediate falsifiers

Every implementation must be attacked by at least:

- pigeonhole formulas;
- Tseitin contradictions;
- pebbling contradictions;
- random hard UNSAT;
- blocked-equality / bad-order residual-width families;
- formulas maximizing extension-candidate multiplicity;
- formulas forcing large root-support ER3 macros;
- instances where supplied proof verification is cheap but proof discovery is expensive.

## Central research question

The unified composition reduces the current missing bridge to two coupled statements:

1. `DISCOVER_MACRO` always finds a useful proof-carrying macro/question in polynomial total work when the state is nonterminal; and
2. the verified progress potential and all explicit state/proof resources remain polynomially bounded for every CNF.

Until both are proved:

```text
P_VS_NP = OPEN
UNIFIED_ENGINE = ALGORITHMIC_CANDIDATE
HEURISTIC_PROMOTION = FORBIDDEN
```
