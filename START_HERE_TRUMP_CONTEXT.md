# TRUMP / JANUS — mandatory context-recovery bootstrap

Authority: `CONTEXT_RECOVERY_PROTOCOL__NON_SCIENTIFIC__MANDATORY_BEFORE_NEW_GATE`

Purpose: prevent context-loss loops across chats, models, tools and long-lived development history. Project continuity must not depend on conversational memory.

## Hard rule

Before proposing, repairing, promoting, rerunning, or naming any TRUMP/APMA/JANUS gate, the active worker/HQ chat MUST reconstruct context from repository and indexed external continuity sources.

No scientific action is admissible from conversational memory alone.

## Startup sequence

1. Read `registry/TRUMP_CURRENT_STATE_2026-09-15.json` **first**. This is the latest successor-state anchor.
2. Read its parent `registry/TRUMP_CURRENT_STATE.json` for the full historical C022/C023R/v1.1/v1.3 continuity. The parent is historical and must not be silently shortened or overwritten.
3. Read `docs/TRUMP_DEVELOPMENT_JOURNAL.md` plus the journal entries referenced by both state files for the active lineage.
4. Read `registry/TRUMP_CONTEXT_MANIFEST.json` and resolve every mechanism alias relevant to the requested work.
5. Verify the latest frozen scientific authority/seal and distinguish historical FAIL, diagnostic PASS, scoped PASS, classification barrier, and current global frontier.
6. Search repository history/default-branch code for the mechanism and its aliases before treating an idea as new.
7. If the mechanism is indexed as living outside this repository, recover it from the named persistent source before reasoning from it.
8. Build a short `CONTEXT_RECOVERY_RECEIPT` containing: recovered global frontier, current scoped open surface, active lineage, frozen verdicts, known predecessor mechanisms, unresolved blockers, and the exact next allowed action.
9. Only after that receipt may Captain Obvious/Akinator/JUXTAPOSE/TRUMP select or execute a new proof/falsification gate.

## Anti-loop test

Every proposed mechanism must be classified before work begins as exactly one of:

- `NEW_MECHANISM`
- `REDISCOVERY_OF_EXISTING_MECHANISM`
- `SUCCESSOR_REPAIR`
- `DIAGNOSTIC_ONLY`
- `SUPERSEDED_ROUTE`

If classification cannot be made from recovered provenance, status is `CONTEXT_INCOMPLETE__DO_NOT_ADVANCE_GATE`.

## Required role separation

- `AKINATOR`: asks discriminating exact questions / narrows candidate space; it does not certify truth.
- `CAPTAIN_OBVIOUS`: finds the nearest missing obligation, detects circular work and unnecessary redesign; it does not promote scientific claims.
- `JUXTAPOSE`: may prioritize which exact-backed candidate/search path to test first; search priority is never authority.
- `JANUS_DEMIURGE`: constructs exact candidates/transitions/certificates.
- `TRUMP`: enforces exact semantics, proof obligations, falsification, replay and total complexity accounting.
- `JANUS_SOVEREIGN`: governance only; may COMMIT/ROLLBACK/OPEN/HALT based on admissible evidence, but cannot manufacture scientific PASS.

## Permanent scientific firewalls

`proof-system lower bound != problem lower bound != general SAT lower bound`

`representation change admissible iff semantics is preserved exactly`

`T_construct + T_discover + T_solve + T_reconstruct + T_verify + certificate_bytes <= poly(|F|)`

Finite calibration/revealed/holdout success is not theorem evidence unless the preregistered claim explicitly concerns that finite domain.

A parameterized/FPT theorem is not automatically a polynomial-in-original-input theorem: an explicit input-relative polynomial envelope is required.

## Context sources

Primary scientific authority: `Hawkar-usls/Janus-Fundamentum`.

Historical/semantic archive: `Hawkar-usls/janus-meta-registry` plus persistent ChatGPT Library artifacts listed in `registry/TRUMP_CONTEXT_MANIFEST.json`.

Conversation memory is advisory only; repository and source-bound artifacts outrank it.

## Write-back rule

After every material development, update the journal and `registry/TRUMP_CURRENT_STATE_2026-09-15.json`; preserve `registry/TRUMP_CURRENT_STATE.json` as the parent historical state. If a new durable mechanism or alias was introduced, update `registry/TRUMP_CONTEXT_MANIFEST.json` in the same development cycle.

## Failure mode this protocol closes

The project has repeatedly rediscovered prior mechanisms because recent-chat memory was mistaken for the full project state. This protocol makes historical recovery an explicit first-class algorithmic step rather than an optional recollection step.

Status: `ACTIVE_MANDATORY_BOOTSTRAP`.
