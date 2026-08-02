# C019 pre-admission — JANUS Tear condensation

## Status

`EXPLORATORY / NOT ADMITTED TO THE CANONICAL REGISTRY`

This note connects the JANUS meta-registry image of a tear as a compact liquid
packet with the proof-search laboratory. It does not claim that tears, emotion,
water, salt, semiconductor hardware, or the C019 experiment resolve `P` versus
`NP`.

## The useful part of the metaphor

The meta-registry calls a tear a **Crystalline Data Packet** and maps it through
`tear -> river -> ocean`. For computation, the defensible translation is:

- **tear** — a compact, independently checkable summary extracted from a local
  conflict;
- **river** — transport of that summary between search branches or swarm nodes;
- **ocean** — persistent deduplicated memory shared by the whole solver;
- **salt / conductivity** — only a metaphor for transport, not evidence that an
  emotion is digitally encoded in tear fluid.

The mathematical value is therefore not in the chemistry. It is in the proposed
**condensation operation**: many failed local states are compressed into one
reusable invariant.

## P–N junction translation

| P–N laboratory term | JANUS Tear interpretation |
|---|---|
| unresolved clause charge | accumulated pressure from constraints that remain false |
| depletion depth | depth of a locally trapped partial assignment |
| avalanche episode | a conflict that exposes an inconsistent combination |
| tear | a verified invariant learned from that conflict |
| ocean | a global cache of non-duplicate invariants |
| recombination | a satisfying assignment verified clause by clause |
| no recombination with witness | an independently checkable UNSAT certificate |

A physical swarm can test latency, communication cost, verifier cost, and
memory reuse. It cannot turn exponential logical work into polynomial work by
parallelism alone.

## Formal candidate

For a CNF formula `F` and a conflicting partial assignment `alpha`, define

```text
tau = TEAR(F, alpha)
```

A useful tear system must satisfy all of the following.

1. **Soundness** — `F entails tau`.
2. **Blocking** — the conflicting state `alpha` violates `tau`.
3. **Polynomial extraction** — `tau` is found in polynomial time.
4. **Polynomial verification** — soundness or the attached derivation is
   checkable in polynomial time.
5. **Polynomial total budget** — only polynomially many non-redundant tears of
   polynomial total size are needed on every input.
6. **Quotient completeness** — once two residual search states have the same
   tear signature, merging them cannot change satisfiability or destroy all
   witnesses.
7. **Terminal completeness** — saturation of the tear store yields either a
   satisfying assignment or a polynomially checkable UNSAT certificate.

## Conditional consequence

If one deterministic algorithm satisfied conditions 1–7 for every CNF formula
of length `L`, with polynomial running time and polynomial total tear volume,
then SAT would be decidable in polynomial time. Therefore `P = NP`.

This implication is straightforward. The unsolved content is the existence of
such a universal tear extractor and, especially, quotient completeness.

## Relation to known solver behavior

A learned clause, an UNSAT core, a parity invariant, a cut, or an extension
variable can all be treated as kinds of tears. Ordinary conflict learning is
therefore already a restricted tear system.

The new hypothesis would have to go beyond renaming clause learning. It must
show that every exponential search tree can be folded into a polynomial-size
DAG of residual states using efficiently discovered, sound global invariants.
Without that theorem, `JANUS Tear` is an architecture for memory reuse rather
than a route to `P = NP`.

## First exact attack from C018

C018 produced toroidal Tseitin twins with opposite satisfiability but identical
bounded-radius local signed-incidence views. This attacks every tear whose
content is determined only by a fixed local neighborhood.

The new executable audit simplifies the same obstruction to charge markers:

```bash
python experiments/direct/janus_tear_condensation.py --self-test
python experiments/direct/janus_tear_condensation.py --radius 3
```

For the generated pair:

```text
SAT charge distribution:    (2,0)
UNSAT charge distribution:  (1,1)
```

The multiset of every bounded-local tear signature is equal. A local tear cannot
see whether the two charges occupy one component or two components.

## The first positive result

A **global component-parity tear** stores one XOR bit per connected component.
For a pure Tseitin system:

```text
all component parity bits = 0  -> SAT
at least one parity bit = 1    -> UNSAT
```

The C019 audit therefore distinguishes the C018 twins immediately:

```text
SAT tear:    (0,0)
UNSAT tear:  (1,1)
```

This is a real compression result for that formula family. A large local search
is replaced by a tiny global invariant computable from the graph and charge
vector.

It is not a general SAT result. The representation already exposes the exact
algebraic invariant. The hard universal question is whether an equally compact
invariant can always be discovered from an arbitrary CNF without first solving
the instance.

## Main hypothesis candidate

### Janus Tear Polynomial Quotient Conjecture

For every CNF formula `F` of length `L`, there exists a polynomial-time
procedure that constructs a polynomial-size set of sound tears whose canonical
signature partitions all residual search states into only `poly(L)`
satisfiability-preserving equivalence classes.

### Consequence if true

```text
polynomial tear extraction
  + polynomial number of quotient states
  + sound witness recovery
  + complete UNSAT certification
  -> SAT in P
  -> P = NP
```

### First unproved theorem

The extractor must find the right global invariant without hiding SAT, formula
equivalence, circuit minimization, or proof search inside the extraction step.

## Immediate attacks

1. **Clause-learning collapse** — if tears are only clauses derived by ordinary
   conflict resolution, the proposal is merely a CDCL/resolution strategy and
   does not establish a polynomial worst-case bound.
2. **Locality failure** — C018 twins show that bounded-local tears miss global
   component parity.
3. **Canonicalization trap** — deciding that two residual formulas have the
   same solution set may itself contain the original hard problem.
4. **Verifier trap** — an expressive small tear is useless if checking that
   `F entails tau` requires an unbounded proof search.
5. **State explosion** — every tear may be small while the number of distinct
   non-redundant tears remains exponential.
6. **Representation dependence** — the parity tear solves a Tseitin family
   because the correct algebraic language is given in advance.
7. **Parallelism accounting** — Gladius, Anchor, and Holocron may lower latency,
   but total work, energy, communication, and duplicated proof effort must be
   charged separately.

## Swarm protocol candidate

- **Gladius** proposes a tear after a conflict episode.
- **Anchor** independently verifies the derivation and rejects unsound tears.
- **Holocron** canonicalizes, deduplicates, records provenance, and measures how
  many residual states the tear actually merges.
- The untouched control lane runs without imported tears.

Required metrics:

```text
tear bytes
generation work
verification work
communication bytes
deduplication ratio
residual-state merge count
witness recovery success
SAT/UNSAT correctness
total work versus control
```

## Admission gate

C019 should enter the canonical hypothesis registry only after all of the
following exist:

1. an exact definition of residual-state equivalence;
2. a verifier format for tears;
3. a proof that the experiment measures more than ordinary learned clauses;
4. a benchmark containing C018 toroidal twins and non-Tseitin crafted CNFs;
5. an explicit attack showing where local tears fail;
6. one measurable positive compression result beyond the family-specific parity
   tear;
7. honest accounting of total work and proof size.

## Claim boundary

The current result is:

> A tear can be made mathematically meaningful as a compact verified invariant.
> On Tseitin formulas, one global parity tear collapses a hard-looking local
> search. The path to `P = NP` would require proving that every SAT instance has
> a polynomially discoverable, polynomially complete tear basis. That missing
> theorem is essentially the heart of the problem, not something established by
> the metaphor or the experiment.
