# C025 Unified Proof-Carrying Akinator / JEC v1

Status: `EXPLORATORY / EXECUTABLE / FAIL-CLOSED / P_VS_NP_OPEN`

This branch does **not** invent another SAT heuristic. It composes previously separated JANUS mechanisms into one deterministic proof-carrying algorithm candidate.

## Claim boundary

This is not a proof that `P = NP`.

Proof-state promotion by heuristic, probability, random choice, activity score, ML prediction, estimated Walsh balance, physical randomness, general SAT oracle, or semantic-equivalence oracle is forbidden.

If the fixed proof/cap rules cannot certify a next move, the only legal result is `OPEN`.

## One organism

```text
CANONICAL RESIDUAL / QUOTIENT DISCIPLINE
        |
        v
CERTIFICATE PORTFOLIO
  2-SAT SCC / explicit GF(2) / fixed-width Resolution
        |
        v
AKINATOR EXACT QUESTION
  ELIM_x(F) = exists x . F
        |
        | if a pivot fits the fixed N^C state cap
        v
EXACT RECOMPRESSION + WITNESS LEDGER
        |
        +-----------------------------+
        | no pivot fits N^C           |
        v                             |
JUNCTION EXTENSION COMPRESSION        |
  B2 proof-carrying macro             |
        |                             |
        v                             |
RESTORE A CAPPED ROOT PIVOT ----------+
        |
        v
MONOTONE GLOBAL PROGRESS
```

No layer may compensate for another by guessing.

## Akinator without heuristics

For pivot variable `x`, partition CNF clauses into:

- `P_x`: clauses containing `x`;
- `N_x`: clauses containing `NOT x`;
- `R_x`: clauses not containing the pivot.

Generate every distinct non-tautological Resolution resolvent between `P_x` and `N_x`, remove all pivot clauses, keep `R_x`, and canonically normalize.

Call this `ELIM_x(F)`.

The exact semantic identity is:

```text
ELIM_x(F) == exists x . F
```

on all remaining variables. Therefore this is not a branch prediction: it is exact existential projection and preserves satisfiability without a SAT oracle.

The selector scans live variables in frozen canonical order and accepts the first pivot whose complete materialized result stays within a fixed cap:

```text
STATE_CAP(N) = N^C
```

where `C` is fixed before seeing the input.

The current implementation charges the pre-subsumption deduplicated elimination output against the cap, which is conservative and monotone during construction.

## Why this does not already prove P=NP

One elimination step can square the clause population:

```text
M_(t+1) <= O(M_t^2)
```

so "each step is polynomial in the current state" does not imply one uniform polynomial in original input size.

The exact open statement is:

```text
UNIVERSAL_ELIM_CAP_C_AVAILABILITY
```

Does some universal fixed `C` guarantee that every nonterminal state reached by the deterministic selector has a capped exact pivot, possibly after the admitted macro restore below?

## Junction Extension Compression: concrete v1 macro

When no exact pivot fits the cap, the engine does not branch. It enumerates repeated literal pairs in canonical order.

For a repeated `(a OR b)` fragment, introduce one fresh topologically greater extension variable `e` using the frozen B2 AND rule:

```text
e <-> ((NOT a) AND (NOT b))
```

with definitional CNF:

```text
(NOT e OR NOT a)
(NOT e OR NOT b)
(e OR a OR b)
```

Then every occurrence

```text
(a OR b OR R)
```

is replaced by

```text
(NOT e OR R)
```

because under the definition `NOT e <-> (a OR b)`.

This is a conservative extension, not a heuristic compression guess.

A repeated pair is only a candidate. The macro is admitted only if:

1. the transformation reconstructs exactly under the independent local checker;
2. the transformed state remains inside `N^C`;
3. it immediately restores an exact capped elimination of an **original root variable**;
4. macro + root elimination is treated as one atomic transition;
5. the frozen progress potential strictly decreases.

Speculative extension accumulation is forbidden.

## Fixed extension budget

Freeze another universal constant `k` and charge:

```text
EXTENSION_CAP(N) = N^k
```

The engine returns `OPEN` if this budget is exhausted.

## Monotone progress

Let:

- `r` = number of live original/root variables;
- `v` = total number of live variables, including extensions;
- `K_max = N^k`;
- `n0` = original root variable count.

Use:

```text
Phi_ext = r * (n0 + K_max + 1) + v
```

Pure exact elimination strictly decreases `Phi_ext`.

A macro-assisted step is admitted only when it introduces a bounded extension and eliminates at least one original root in the same atomic step; therefore it also strictly decreases `Phi_ext`.

This proves termination of the **capped machine**. It does not prove that the machine avoids `OPEN` on every CNF.

## Certificate portfolio before general elimination

The executable v1 tries exact polynomial lanes before the general projection selector:

1. unit propagation / canonical simplification;
2. exact 2-SAT via implication SCCs;
3. exact explicit XOR-block recognition followed by GF(2) elimination/RREF;
4. fixed-width Resolution refutation search with explicit width charge.

These lanes may decide or simplify instances, but they are never promoted into a universal theorem merely because they succeed on a finite corpus.

## Residual quotient / hash discipline

Every residual state is canonicalized, fingerprinted and recorded. Revisited identical states are cache hits rather than new semantic work.

No unrestricted semantic hash is used: equality is syntactic after proof-carrying normalization, not an oracle for CNF equivalence.

## Witness recovery

Every exact elimination records its pre-state and pivot. If the terminal projected formula is satisfiable, the engine walks the elimination ledger backward, choosing a pivot value only when the stored pre-state is directly satisfied. The final root assignment is independently checked against the original CNF.

`SAT` without a verified root witness is illegal.

## Explicit resource ledger

The current engine charges separately:

```text
proposal_work
certificate_discovery_work
verification_work
max_state_units
proof_bytes
extension_definition_bytes
extension_count
residual_state_count
residual_cache_hits
question_count
elimination_pair_work
recompression_work
witness_recovery_work
bounded_width_resolution_work
two_sat_work
gf2_work
```

No quantity may hide another.

## Exact remaining theorem

For fixed universal constants `C,k`, prove that for every CNF input of size `N` the machine never reaches:

```text
NO_CAPPED_CERTIFIED_MOVE
```

Equivalently, every nonterminal reachable state must have either:

1. a directly capped exact elimination pivot; or
2. a deterministically discoverable, proof-carrying bounded JEC macro that restores such a pivot while preserving the caps and progress.

Together with the already explicit polynomial work bounds of the capped search space, that would yield a deterministic polynomial SAT algorithm.

This universal availability theorem is **not proved**.

## Required falsifiers

Attack the combined organism, not the components separately:

- pigeonhole contradictions;
- Tseitin contradictions;
- pebbling contradictions;
- random hard SAT/UNSAT;
- blocked-equality / hostile elimination orders;
- formulas maximizing elimination boundary width;
- formulas maximizing repeated-pair macro candidates;
- large-root-support ER3 families;
- cheap-verification / hard-discovery controls;
- cases requiring more than one speculative macro before any root pivot becomes capped.

The last family is particularly important because v1 deliberately forbids speculative macro chains.

## Current status

```text
EXACT_ELIMINATION_SEMANTICS = IMPLEMENTED
HEURISTIC_AKINATOR = REMOVED
2SAT_PORTFOLIO = IMPLEMENTED
EXPLICIT_GF2_PORTFOLIO = IMPLEMENTED
FIXED_WIDTH_RESOLUTION_REFUTATION = IMPLEMENTED
B2_PAIR_MACRO = IMPLEMENTED
ATOMIC_MACRO_PLUS_ROOT_ELIM_PROGRESS = IMPLEMENTED
FIXED_STATE_AND_EXTENSION_CAPS = IMPLEMENTED
WITNESS_LIFT = IMPLEMENTED
UNIVERSAL_CAP_AVAILABILITY = OPEN
P_VS_NP = OPEN
```
