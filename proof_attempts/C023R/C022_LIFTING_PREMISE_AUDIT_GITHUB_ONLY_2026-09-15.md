# C022 registered 2026 lifting theorem premise audit — GitHub-only

Authority: `HQ_SOURCE_AUDIT__NO_SCIENTIFIC_PROMOTION`

## Registered source

`R073` identifies Itsykson–Podolskii–Shekhovtsov, ECCC TR26-018 (2026), and records the summary:

- base unsatisfiable CNF has Resolution width at least `w`;
- gadget is constant-size and 1-stifling;
- a `Res(⊕)` refutation of lifted formula of size `S` has depth `Omega(w^2/log S)`;
- MAJ3 is listed as an example.

The C022 theorem-chain note repeats this summary and applies it to the MAJ3 lift.

## What GitHub currently contains

The repository contains:

- the bibliographic registry entry and theorem summary;
- the C022 conditional derivation;
- the JANUS implementation of the clause-wise lift construction;
- a general algebraic proof that this clause-wise construction equals the direct exact truth-table CNF used by JANUS;
- the explicit q=4 base-family width binding.

It does NOT currently contain the primary theorem text, theorem-number extract, PDF, or a source-bound quotation of all hypotheses sufficient to independently verify the exact lifting convention and proof-system conventions.

## Verdict

`OPEN_SOURCE_TEXT_INSUFFICIENT_IN_GITHUB`

This is not evidence that the registered theorem application is wrong. It means the requested independent premise audit cannot be completed under the GitHub-only execution rule from the repository evidence presently available.

## Already checked independently of the source text

- MAJ3 is 1-stifling by an exact finite gadget proof/audit.
- For every degree `d`, JANUS clause-wise lift and direct exact-relation CNF are symbolically identical.
- The q=4 degree-5 family has explicit linear base Resolution width in the frozen binding.
- H135 survives the current HQ formal red-team, though genuinely independent/external review remains distinct.

## Required source-bound completion

Archive in GitHub either the primary paper or a provenance-preserving theorem extract containing:

1. the exact definition of `1-stifling` used by the theorem;
2. the exact definition of the lifted CNF `phi o g`;
3. the target `Res(⊕)` proof system and size/depth conventions;
4. the quantified theorem statement and hidden parameter dependencies;
5. any restrictions on base CNF width, gadget arity, clause encoding, or formula size.

Only then may this gate move from OPEN to PASS/FAIL.

## Claim ceiling

C022 remains a conditional theorem chain. No C023/Policy-0A lower bound and no global complexity conclusion is promoted by this audit.