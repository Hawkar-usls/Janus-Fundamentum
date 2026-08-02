# C010 — Proof compression and audit hardening

C010 continues the inherited JANUS cycle without manufacturing terminal results.

## Cycle output

- eight descendants: `H084-H091`;
- forty attacks: `A217-A256`;
- eight inherited hypotheses re-attacked: `H075-H079`, `H081-H083`;
- no terminal result;
- cumulative inversion matrix: `40 × 40 = 1600` logical cells;
- inherited share: `32/40 = 80%`.

## Why no graveyard entry

No previous exact statement received a decisive theorem or counterexample.
Several routes were weakened or narrowed, but pressure alone is not sufficient
for `DESTROYED` or `REJECTED`.

## Proof-compression branch

### H084 — signed-coordinate monomial transport

H084 extracts the exact algebraic core of H075. Coordinate permutations and
complementations act by an invertible integer matrix on the squarefree
degree-at-most-k monomial basis. Gram matrices move by congruence, preserving
degree and positive semidefiniteness.

Artifacts:

```bash
python experiments/theta/symmetry_transport.py --self-test
```

and:

```text
proof_attempts/H075/SYMMETRY_TRANSPORT.md
```

The proof artifact is not an independent review and does not promote H075 or
H084 to `PROVED`.

### H085 — bounded-depth functional pullback

H085 isolates the compositional theorem needed by H077. For fixed fan-in and
depth, substitution should transform an extension certificate into an original
certificate with degree bounded by `2k*s^d`.

The unresolved points are:

- DAG sharing versus full polynomial expansion;
- coefficient growth;
- exact quotient-ring elimination of extension axioms;
- conversion from certificate pullback to full theta-rank comparison.

### H086 — projection-fiber necessity

H086 classifies any surviving H076 collapse into explicit resources:

1. nonfunctional fibers;
2. unbounded dependency depth;
3. superpolynomial coefficient growth;
4. superpolynomial expanded size.

It is conditional on H085 and remains open.

## Canonical twin branch

### H087 — level-one exact target

H087 narrows H078 to:

- level one;
- one standard clause-literal conflict graph;
- exact variable canonicalization;
- rational moment witnesses;
- a finite answer-independent field list.

The profile tool now performs exhaustive variable relabeling for at most eight
used variables. It refuses larger instances rather than labeling a heuristic
hash as canonical.

Exact alpha and SAT labels are removed from the profile. They live only in:

```bash
python experiments/theta/diagnostics.py formula.cnf
```

which is explicitly exponential and test-only.

## Parser integrity

`conflict_graph.py` now:

- requires one valid `p cnf` header;
- validates declared variable and clause counts;
- validates literal ranges;
- preserves empty clauses;
- requires every clause to terminate with zero;
- rejects data before the header and duplicate headers.

Run:

```bash
python experiments/theta/conflict_graph.py --self-test
```

## Local gadget and mixed-family branch

- `H088` asks for pseudoexpectation transport through fixed-radius gadgets.
- `H090` asks for one explicit restriction-closed mixed XOR/non-affine
  generator.
- `H091` asks for a measure-preserving bridge into a fixed bounded-degree
  parity proof fragment.

These hypotheses connect H079 and H083 to the older H062-H064 proof-complexity
branch.

## Exact rational verification

H089 introduces a certificate language based on exact rational Gram factors,
zero residuals, and rational threshold margins.

Run:

```bash
python experiments/theta/rational_gram_verifier.py --self-test
```

The verifier checks a supplied artifact. It does not solve an SDP and does not
assert that a short factor exists.

## Validator hardening

C010 removes duplicated policy constants from validators.

`registry/schema.json` now selects:

- the current matrix file and dimensions;
- the inherited fraction;
- current-cycle hypothesis IDs;
- attack-pressure thresholds;
- the reverse-lineage start point and ledger.

`validate_lineage.py` also checks append-only reverse edges for every C010
child. Historical genealogy files are not rewritten.

## Reproduction

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python experiments/theta/conflict_graph.py --self-test
python experiments/theta/canonical_profile.py --self-test
python experiments/theta/symmetry_transport.py --self-test
python experiments/theta/rational_gram_verifier.py --self-test
```

## Claim boundary

C010 does not prove:

- `P = NP`;
- `P != NP`;
- a universal theta/SoS lower bound;
- existence of theta twins;
- efficient SDP certificate discovery;
- novelty of the lemma candidates.

Its progress is narrower: two broad ambiguities were split into explicit
algebraic obligations, and the experimental interface now refuses several
previously silent sources of false evidence.
