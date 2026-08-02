# C037.1 — Proof-Carrying Pairwise Parity Aliases

**Status:** `CONSTRUCTIVE RESTRICTED LEMMA + DECISIVE ARITY OBSTRUCTION / P_VS_NP=OPEN`

## Purpose

C037 proved a complete affine-to-Horn direction and a sound unary negotiation protocol, then exhibited a jointly UNSAT equality/disequality pair on which constants-only exchange reaches `OPEN_FIXPOINT`.

C037.1 enlarges the exchanged fact algebra by one rigorously bounded layer:

```text
x XOR y = 0
```

for shared-variable equalities entailed by an arbitrary Horn formula. Every emitted alias carries native Horn conflict proofs and is injected into the affine module as a verified GF(2) row.

No unrestricted Horn-affine SAT or equivalence oracle is called.

## Lemma 1 — complete pairwise Horn equality extraction

For shared variables `x` and `y`,

```text
H |= (x XOR y = 0)
```

iff both Horn clauses are entailed:

```text
not x OR y
x OR not y
```

Each clause-entailment query is decided by adding the units that falsify that clause and running the deterministic Horn least-model procedure.

- SAT gives a concrete Horn model violating the proposed implication, so the alias is not emitted.
- UNSAT gives a replayable least-model conflict trace proving the implication.

Thus every pairwise equality consequence over a supplied shared set `S` is discoverable in uniform polynomial time. The implementation charges every pair query, Horn call, clause scan, proof byte and total work unit.

A binary implication-graph SCC shortcut is insufficient for general Horn formulas. The control

```text
(not x OR z)
AND (not x OR not z OR y)
AND (not y OR x)
```

entails `x=y`, but the forward direction uses a ternary Horn rule and is missed by a binary-only graph. C037.1 therefore uses complete Horn entailment, not SCC reachability.

## Lemma 2 — spanning-forest compression

Equality is transitive. After discovering a certified equality edge, C037.1 joins its endpoints in a deterministic union-find structure and emits the edge only when it connects two previously distinct components.

For `k=|S|` shared variables:

```text
all semantic pair equalities: up to k(k-1)/2
emitted proof-carrying basis:  at most k-1
```

The emitted forest is sufficient for affine injection because XOR-combining its rows reconstructs every equality in each component. Discovery work remains separately charged; compression does not erase the cost of tested pairs.

## Lemma 3 — Horn disequality collapses to unary facts

Let satisfiable Horn `H` entail

```text
x XOR y = 1.
```

Horn model sets are closed under coordinatewise conjunction. If one model projected to `01` and another to `10`, their conjunction would project to `00`, contradicting the disequality. Therefore all Horn models use only one orientation:

```text
x=0, y=1
```

or

```text
x=1, y=0.
```

Hence both variables are already unary consequences. A nontrivial pairwise Horn disequality contributes no information beyond complete literal propagation.

The executable independently checks this consequence against exhaustive small Horn semantics; the production extractor does not use exhaustive enumeration.

## Negotiation Trace v1.1

```text
schema = janus.cross_language_negotiation.v1.1
policy = PAIRWISE_HORN_EQUALITY_BASIS_V1
```

A parity-alias event contains:

```json
{
  "seq": 3,
  "kind": "ENTAILED_PARITY_ALIAS",
  "producer": "HORN",
  "left": 4,
  "right": 9,
  "rhs": 0,
  "clauses": [[-4, 9], [4, -9]],
  "native_proofs": [
    {"status": "UNSAT", "trace": []},
    {"status": "UNSAT", "trace": []}
  ],
  "fact_id": "content-addressed-id"
}
```

The verifier reconstructs the accumulated unary facts, reruns both Horn entailment checks, verifies that the edge joins two previously separate equality components, injects the corresponding GF(2) row, and replays the terminal affine conflict or final fixpoint.

A fixpoint is still only `OPEN_FIXPOINT`; it never certifies compatibility.

## Polynomial accounting

Under deterministic rescanning:

```text
accepted unary events       <= |S|
accepted equality events    <= |S|-1
pairwise equality queries   <= O(|S|^3)
Horn implication checks     = 2 per tested equality pair
```

The cubic discovery bound reflects repeated scans after newly derived literals or aliases. Native Horn least-model work, affine row XORs, proof volume, certificate bytes and total standard-model work are all metered. Budget exhaustion returns `OPEN_BUDGET`.

## Constructive controls

### Equality joined to affine disequality

```text
H = (not x OR y) AND (x OR not y)
A = x XOR y = 1
```

C037 returned `OPEN_FIXPOINT`. C037.1 emits `x XOR y = 0`, injects it into `A`, and returns a replayable affine conflict.

### Nonbinary Horn alias

The ternary-rule control above also closes by a certified equality alias, showing that the result is not restricted to 2-CNF Horn.

### NAND3 + NEQ image

A reduction-image fixture with no certified unary fact or pairwise equality still returns:

```text
OPEN_FIXPOINT
```

The extension does not silently become a general SAT solver.

### Proof-volume compression

For one Horn equality class of 20 variables:

```text
true pair relations     190
emitted basis edges      19
```

Every emitted edge is independently replayed.

## Frozen audit

```bash
python experiments/direct/janus_c037_1_proof_carrying_parity_aliases.py --self-test
```

The deterministic audit includes:

```text
400 satisfiable random Horn/affine cases
2963 pairwise equality entailment checks
201 Horn disequality consequences checked
all disequalities collapsed to opposite unary constants
200 certified mixed conflicts
200 honest OPEN fixpoints
equality/NEQ obstruction -> CERTIFIED_CONFLICT
nonbinary Horn alias -> CERTIFIED_CONFLICT
NAND3/NEQ fixture -> OPEN_FIXPOINT
190 equality relations -> 19 emitted basis edges
corrupt alias -> REJECTED
explicit tiny budget -> OPEN_BUDGET
```

Finite experiments validate the implementation only.

## Relation to the route matrix

- C025 separates state volume from proof volume.
- C032 aligns cut rows with PS-width.
- C034 charges bounded heterogeneous composition.
- C035 supplies certified merging.
- C036 supplies complete same-language separators.
- C036.1 aligns explicit fixed-order refinement with OBDD minimization.
- C037 supplies one-way Horn-affine separation and unary negotiation.
- C037.1 supplies a strictly stronger proof-carrying fact algebra without naming a new width invariant.

The construction aligns with Horn closure, cooperating decision procedures and DPLL(XOR)-style implied equations. It is not promoted as a novel representation class.

## New gate

```text
HIGHER_ARITY_HORN_TO_AFFINE_CONSEQUENCE_DISCOVERY_OR_DECISIVE_ARITY_OBSTRUCTION
```

Pairwise aliases close equality-style interactions. The remaining route must either discover a polynomially bounded, replayable higher-arity Horn consequence basis useful to affine composition, or prove a decisive obstruction for an explicit bounded-arity enlargement. Fixed arity without a universal theorem, supplied consequences, polynomial verification without polynomial discovery, and failure to find a consequence do not pass the gate.

## Claim boundary

C037.1 is complete only for unary Horn consequences and pairwise Horn equalities over the supplied shared interface. It remains `OPEN` on unrestricted Horn-affine mixtures and NAND3+NEQ reduction images. It does not prove `P=NP` or `P!=NP`.

```text
P_VS_NP=OPEN
```
