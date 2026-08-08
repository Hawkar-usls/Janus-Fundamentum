# Fundamentum Multidirectional Frontier v1

Fundamentum is not a `P = NP` advocacy project. Its primary target is now the symmetric resolution problem

\[
P \stackrel{?}{=} NP,
\]

with **no preferred terminal**. `P = NP` and `P != NP` require separate proof-carrying admission chains. A failed upper-bound route may become useful lower-bound evidence, but failure is never automatically promoted to separation.

The same rule applies to every target in `research_targets/FUNDAMENTUM_RESEARCH_TARGET_REGISTRY_V1.json`.

## Frozen target levels

| Level | Targets | Fundamentum relation |
|---|---|---|
| A0 | `P = NP` / `P != NP` | primary |
| A1 | `NP = coNP`, `FPT = W[1]`, `NP subseteq P/poly`, ETH, SETH | very high / high |
| A2 | PH collapse, `P = PSPACE`, `L = NL`, `NC = P`, `P = BPP`, `VP = VNP`, Permanent vs Determinant, deterministic PIT, Graph Isomorphism in P | adjacent complexity frontier |
| A3 | strong proof-complexity lower bounds, Frege/Extended Frege lower bounds, new matroid/trellis/rank-width theorems | structural and lower-bound frontier |
| A4 | Riemann, BSD, Hodge, Yang-Mills mass gap, Navier-Stokes | architecture may generalize; mathematical domain bridge absent |

There are **23 separately registered targets** because the A4 family is represented as five independent conjecture/problem surfaces rather than one bundled terminal.

## Machine search

`experiments/direct/janus_fundamentum_multidirectional_frontier_v1.py` performs a repository-wide route search. It:

1. loads the frozen target registry;
2. scans committed UTF-8 research/code/document surfaces for each target's explicit search markers;
3. computes only explicitly registered implication paths;
4. ranks the frontier by declared relation, existing repository surfaces, and explicit implication reachability;
5. emits `OPEN` globally and `NOT_PROVED_BY_THIS_SEARCH` for every target.

The independent verifier `janus_fundamentum_multidirectional_frontier_verifier_v1.py` does not import the producer. It independently rescans the repository, recomputes marker counts, implication closure, ranking, semantic digests, and target classifications.

The CI tamper suite repairs the outer report digest after each attack, then requires semantic replay to reject fabricated theorem promotion, changed terminal direction, altered evidence counts, ranking manipulation, corpus/registry rebinding, B5-complete promotion, polynomial-runtime promotion, and A4 domain-bridge promotion.

## Explicit implication routes currently admitted only as logic edges

The v1 registry records these implication edges for search/ranking purposes:

```text
NP not subseteq P/poly -> P != NP
NP != coNP            -> P != NP
ETH true               -> P != NP
SETH true              -> ETH true
PH does not collapse   -> P != NP
```

An implication edge does **not** establish its premise. It only states what may be concluded if that premise later receives an admitted proof.

## Current inherited boundary

This frontier branch starts from the admitted B5.4 evidence head:

```text
B5.4 evidence head = e7663ed9be87ebd37bfa51c01501e74c9d5b2603
B5.4 proof head    = 135740e9ee06030ad0d029cc65cbace95af82cc1
```

The new frontier work may not modify B5.4 admitted proof surfaces. CI rebinds the B5.4 admission receipt and rejects such modifications.

The inherited ceiling remains:

```text
B5_4_CORRECTED_DISCOVERY_TO_PHASE_A_C047_REBOUND = ADMITTED_IN_STATED_VERIFIED_SCOPE
ALL_INPUT_TERMINATION = NOT_ESTABLISHED
POLYNOMIAL_RUNTIME = NOT_ESTABLISHED
B5_COMPLETE = FALSE
P_VS_NP = OPEN
```

## Interpretation rule

The route search answers only:

> Where does the current repository already contain mathematical machinery or evidence surfaces relevant to a target, and what bridge is missing next?

It does **not** answer:

> Which unresolved conjecture has been proved?

That distinction is part of the proof boundary, not a disclaimer added after the fact.
