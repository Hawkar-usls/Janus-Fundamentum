# C026 — JANUS Certificate Portfolio

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

Base:

```text
994dd693604d1f557c367acc7b1b3ed6083ee4a8
```

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend,
external LLM, BCI, biological sample, physical P–N junction, or quantum device
was touched.

## Question

C025 separated two costs of residual-state compression:

```text
STATE VOLUME
MERGE PROOF VOLUME
```

C026 asks which useful merges have certificates that are both independently
checkable and constructible without a hidden SAT/equivalence oracle.

## Certificate portfolio

### 1. TWO_SAT_CLOSURE

A 2-CNF is converted into its complete implication closure. Every added unit or
binary clause carries explicit implication paths in the original graph.

```text
256 raw presentations
256 states after subsumption
1 certified 2-SAT closure
```

### 2. GF2_ROW_SPACE

An affine system is converted to reduced row echelon form. Every row swap and
row XOR is replayed independently.

```text
256 raw row systems
1 certified RREF state
```

### 3. WIDTH_W_RESOLUTION

All non-tautological resolvents of width at most `w` are generated and then
subsumption-normalized.

The construction costs `n^O(w)`, so it is polynomial only for fixed `w`.

A family with optional width-3 resolvents gives:

```text
256 raw states
256 width-2 states
1 width-3 state
```

Thus width 3 opens a merge that width 2 cannot prove.

### 4. RUP_TRACE

A supplied learned clause is accepted only when reverse unit propagation yields
a replayable contradiction.

A width-4 control family gives:

```text
256 raw states
256 width-3 Resolution states
1 RUP-trace state
```

The supplied trace is easy to replay, but unrestricted learned-clause search on
40 variables has:

```text
3^40 - 1 = 12157665459056928800
```

non-tautological candidates.

## Independent replay

The extended local audit checked all four systems against complete truth tables
or complete GF(2) assignment spaces:

```text
120 holdout cases per language
16064 assignments checked
0 2-SAT failures
0 GF(2) failures
0 Resolution failures
0 RUP failures
```

The compact repository CI repeats the adversarial exponential-family checks.

## Genuine continuation width remains

For blocked equality at `n=12`:

```text
4096 boundary assignments
4096 complete 2-SAT canonical states
```

Complete class-specific semantic closure cannot merge them because the
continuation functions are truly different.

## General equivalence barrier

For arbitrary CNF `F`:

```text
F equivalent to FALSE  <=>  F is UNSAT
```

The general balanced control contains 40 SAT and 40 UNSAT formulas. The
portfolio returns `OPEN` on all 80 unsupported cases and produces no false
accepts.

## Located bottleneck

# CERTIFICATE_DISCOVERY_COMPLEXITY

Definition:

> The total work required to choose a proof language, discover the relevant
> merge certificate or canonical form, and verify it.

C026 separates four regimes:

```text
2-SAT       polynomial construction + polynomial verification
GF(2)       polynomial construction + polynomial verification
width-w Res n^O(w) search + polynomial replay
RUP         polynomial replay of a supplied trace; no universal finder
```

Polynomial verification alone is insufficient.

## What changed

C026 removes four kinds of exponential presentation artifact without using a
semantic-equivalence oracle. It also shows that each stronger verifier moves the
unresolved cost into proof discovery.

The problem is no longer merely:

```text
Can JANUS verify this merge?
```

It is:

```text
Can JANUS find the correct proof language and certificate in polynomial total work?
```

## Next target

### C027 — Instance-Specific Proof Discovery

The next cycle should compare:

```text
bounded-width proof search
failed-literal / RUP discovery
implication and parity extraction
formula-caching reuse
learned-clause dependency DAGs
```

Every candidate must pay for:

- candidate generation;
- rejected candidates;
- proof search;
- proof replay;
- residual-state reduction;
- witness or Tear recovery.

The red-team controls remain:

```text
blocked equality   -> true 2^n continuation states
F equiv FALSE      -> hidden UNSAT equivalence
wide RUP family    -> short proof, huge unrestricted candidate space
```

## Certificate Portfolio Criterion

If a polynomially generable portfolio contains, for every necessary residual
merge of every CNF, a polynomial-size certificate whose language and certificate
are both discoverable and verifiable in polynomial total work, and the certified
residual state volume is polynomial, then SAT is in P.

This is an algorithmic criterion, not a proof of `P=NP`.

## Claim boundary

C026 does not prove `P=NP`, `P!=NP`, `NP=coNP`, or a lower bound against all
algorithms. It constructs and attacks a concrete certificate portfolio and
isolates proof discovery as the next bottleneck.

## Reproduction

```bash
python experiments/direct/janus_certificate_portfolio.py
```

## References

- Eli Ben-Sasson and Avi Wigderson, *Short Proofs Are Narrow—Resolution Made
  Simple*, Journal of the ACM 48(2), 2001.
- Albert Atserias and Maria Luisa Bonet, *On the Automatizability of Resolution
  and Related Propositional Proof Systems*, Information and Computation 189(2),
  2004.
- Marijn J. H. Heule, *The DRAT Format and DRAT-trim Checker*, arXiv:1610.06229.
- Luís Cruz-Filipe et al., *Efficient Certified RAT Verification*,
  arXiv:1612.02353.
