# C039.1 — Horn Projection Boundary

**Status:** `CONSTRUCTIVE_RESTRICTED_LEMMA + DECISIVE OBSTRUCTION / P_VS_NP=OPEN`

## Purpose

C039 closes symbolic vtree factor construction for affine `GF(2)` messages. C039.1 asks whether the analogous boundary message can remain a polynomial-size Horn CNF under the complete recursive contract:

```text
LEAF / RESTRICT / JOIN / PROJECT / MERGE / SEPARATE / DECIDE
SAT witness recovery / independently checkable UNSAT
```

The answer splits sharply.

1. **Single-head Horn** admits an exact proof-carrying polynomial projector and guarded join.
2. **General boundary-only Horn CNF** does not admit a universal polynomial-size projection: an explicit linear-size Horn family requires exactly `2^n` Horn clauses after forgetting its hidden variables.

Thus Horn expressibility survives forgetting, but polynomial Horn-CNF size does not.

## Message language

A Horn clause is represented as

```text
x_1 AND ... AND x_k -> h
```

where `h=FALSE` denotes a negative Horn clause. A formula is `single-head` when every positive variable occurs as the head of at most one clause. Negative constraints may be multiple.

The executable uses normalized explicit Horn CNF messages. This is intentionally narrower than arbitrary Horn circuits or existential Horn modules.

## Exact operations

### LEAF and RESTRICT

A leaf message is a normalized Horn clause set. Restriction by a partial assignment:

- deletes a clause whose body contains a false variable;
- deletes true body variables;
- removes a clause whose head is already true;
- turns a head fixed false into `FALSE`.

The verifier replays the transformation clause by clause.

### JOIN

General Horn conjunction is exact clause union followed by normalization.

For the polynomial single-head language, a join is admitted only when the normalized conjunction remains single-head. A collision in positive heads returns

```text
OPEN_JOIN_LANGUAGE
```

rather than silently leaving the proved language.

### PROJECT

To forget variable `x`, partition the current clauses into:

```text
producers: P_i -> x
consumers: B_j AND x -> h_j
untouched: clauses not mentioning x
```

For every producer-consumer pair emit

```text
P_i AND B_j -> h_j
```

then remove all original clauses mentioning `x` and normalize. This is exact Horn Davis-Putnam elimination.

Every elimination step records:

- input digest;
- producer and consumer clauses;
- untouched clauses;
- every generated resolvent;
- normalized output and output digest;
- charged work and certificate volume.

For unrestricted Horn this algorithm is exact but output-sensitive. If generated clauses or certificate volume exceed the explicit budget it returns `OPEN`.

### MERGE and SEPARATE

Horn implication and equivalence are polynomial on explicit Horn CNFs.

To test whether formula `F` entails target Horn clause `B -> h`, run the Horn least-model procedure under assumptions

```text
all variables in B = TRUE
h = FALSE, when h is positive.
```

- conflict gives a replayable implication proof;
- a model gives an explicit assignment satisfying `F` and falsifying the target clause.

Testing all clauses in both directions gives either:

```text
MERGE      mutual Horn entailment
SEPARATOR  explicit assignment in the symmetric difference
```

Therefore `OPEN_EQUIVALENCE` is not the Horn bottleneck for explicit messages. Projection volume is.

### DECIDE and certificates

The least-model Horn engine returns:

- SAT with a complete assignment;
- UNSAT with a deterministic derivation/conflict trace.

For a single-head projection, a projected SAT assignment lifts through forgotten variables in reverse elimination order. A forgotten variable is set true exactly when the body of its unique producer is true; otherwise it is false. The verifier checks the reconstructed assignment against the original formula.

## Constructive theorem — single-head Horn

Let `F` be a single-head Horn formula and let `X` be any set of variables to forget.

For each eliminated variable there is at most one producer. Therefore every consumer generates at most one resolvent. Each clause mentioning the eliminated variable is removed, so the number of clauses does not increase during that elimination. Generated clauses preserve the single-head invariant because each consumer keeps its original head.

Consequently the deterministic projection procedure constructs

```text
exists X . F
```

as a single-head Horn CNF in polynomial time and polynomial certificate volume.

The same package supplies:

- exact restriction;
- guarded joins whose positive head sets remain compatible;
- polynomial Horn merge/separation;
- SAT decision and reverse witness lifting;
- independently replayed UNSAT traces;
- strict `OPEN` on any budget or language failure.

This theorem is uniform. It does not treat a supplied decomposition, consequence set, or equivalence oracle as free.

## Decisive obstruction — exponential general Horn projection

For each `n`, introduce boundary variables

```text
a_1,...,a_n, b_1,...,b_n, z
```

and hidden variables

```text
q_1,...,q_n.
```

Define the definite Horn formula

```text
a_i -> q_i
b_i -> q_i                 for every i
q_1 AND ... AND q_n -> z.
```

The input has `2n+1` clauses. After forgetting all `q_i`, the boundary relation is

```text
(AND_i (a_i OR b_i)) -> z.
```

An equivalent boundary-only Horn CNF requires exactly `2^n` non-tautological clauses.

### Lower-bound proof

1. Every assignment with `z=TRUE` satisfies the projected relation. Therefore every non-tautological valid Horn clause must have positive head `z`; a negative clause or a clause headed by another boundary variable would exclude some `z=TRUE` assignment.
2. The body of a valid clause headed by `z` must contain at least one variable from every pair `{a_i,b_i}`. Otherwise set the omitted pair to `00`, satisfy the clause body, set `z=FALSE`, and obtain a valid projected model that violates the clause.
3. There are `2^n` minimal false assignments: set `z=FALSE` and choose exactly one true variable from every pair.
4. A valid Horn clause falsified by one such assignment can contain only variables true in that assignment. Combined with step 2, its body must be exactly that assignment's chosen `n` variables.
5. Distinct minimal false assignments therefore require distinct clauses.

The `2^n` clauses choosing one variable from every pair and implying `z` are sufficient, so the bound is exact.

At `n=64` this is

```text
18446744073709551616
```

required boundary Horn clauses from a 129-clause input.

This lower bound concerns one explicit representation language: boundary-only Horn CNF. It is not a lower bound against richer Horn circuits, existentially quantified modules, structured representations, or all SAT algorithms, and it does not imply `P!=NP`.

## Frozen executable audit

```bash
python experiments/direct/janus_c039_1_horn_projection_boundary.py --self-test
```

The deterministic audit requires:

```text
300 random single-head Horn projections on up to 8 variables
exact comparison with exhaustive projected semantics on bounded domains
reverse SAT witness recovery
200 complete Horn MERGE/SEPARATOR checks
150 exact restriction checks
120 guarded disjoint-head JOIN checks
overlapping-head JOIN -> OPEN_JOIN_LANGUAGE
explicit blow-up family n=1..9 -> exactly 2^n projected clauses
n=14 under 2000-clause budget -> OPEN_PROJECTION_VOLUME
symbolic n=64 lower-bound certificate -> exactly 2^64 clauses
single-head equality controls n=4,8,16,32 remain compact
corrupt projection certificate -> rejected
Horn-affine, NAND3+NEQ, Tseitin parity, non-Horn beta-acyclic and deterministic 3-CNF -> OPEN_LANGUAGE
```

Exhaustive enumeration is used only by bounded test validators. It is not used by the projector, merge/separator procedure, or certificate verifier.

## Relation to the active route

### C025 and C032

C025 distinguishes semantic state volume from certificate and representation volume. C032 identifies explicit cut-signature tables with PS-width views. C039.1 shows that Horn projection is not controlled merely by tractable Horn satisfiability: the exact boundary CNF itself can require `2^n` clauses.

### C034–C036

C034 supplies bounded-interface composition, C035 certified congruence, and C036 complete same-language Horn separation. C039.1 composes these Horn operations with an exact projector and identifies projection size—not equivalence discovery—as the missing unrestricted operation.

### Horn-affine side branches

Unary negotiation and pairwise equality aliases remain useful cross-language facts, but they do not make unrestricted Horn projection compact. C039.1 does not infer compatibility from propagation fixpoints and does not inject unsupported higher-arity consequences into the affine engine.

### C037, C038 and C039

C037 and C038 characterize explicit continuation quotients under an order or vtree. C039 replaces explicit affine continuation rows by a polynomial RREF algebra. C039.1 demonstrates why the same replacement with plain Horn CNF is only conditionally successful: single-head structure prevents branching, while unrestricted producer multiplicity creates an exponential projection antichain.

### Literature alignment

The result is aligned with classical Horn least-model algorithms and resolution-based forgetting. Prior work establishes Horn expressibility under forgetting, warns that Horn results may grow exponentially, and identifies single-head restrictions with polynomial forgetting behavior. C039.1 does not name a new forgetting operator or width parameter; it adds a replayable vtree-message interpretation, an exact family-specific lower bound, and the active-route redirect.

## Adversarial controls

- **Order-sensitive equality:** single-head Horn equality pairs project compactly; the obstruction is not inherited from equality order sensitivity.
- **NAND3+NEQ deterministic 3-CNF images:** `OPEN_LANGUAGE`.
- **Tseitin/parity:** `OPEN_LANGUAGE`; C039 remains the affine compiler.
- **Parity/Horn mixtures:** `OPEN_LANGUAGE`.
- **Beta-acyclic non-Horn formulas:** `OPEN_LANGUAGE`; C033 remains their separate engine.
- **General Horn blow-up:** exact output-sensitive construction or `OPEN_PROJECTION_VOLUME`, never a false compact message.

## Redirected gate

Plain boundary-only Horn CNF is decisively blocked as the universal message language. The surviving target is

```text
RICHER_HORN_MESSAGE_LANGUAGE_OR_PORTFOLIO_GUIDED_HEAD_DISJOINT_ISOLATION
```

A future cycle must do at least one of:

1. construct a polynomial proof-carrying richer Horn representation closed under join, projection, equivalence/separation, decision and witness recovery;
2. discover a charged vtree/module decomposition that isolates single-head-compatible Horn regions and returns `OPEN` when head-disjointness cannot be preserved;
3. prove a decisive obstruction for one explicit richer representation.

Introducing hidden variables or retaining existential modules is not automatically progress: construction, decision, composition, equivalence, witness recovery and certificate volume must all be polynomial and replayable.

## Lineage note

This draft is stacked directly on PR #52 / canonical C039 affine symbolic factors. Older sibling draft PR descriptions currently contain a different provisional allocation for C036.1/C037/C037.1. C039.1 does not rewrite or silently depend on that side lineage; canonical admission must reconcile it separately.

## Claim boundary

C039.1 closes symbolic projection for single-head Horn under guarded joins and proves an exact exponential obstruction for unrestricted boundary-only Horn CNF projection. It does not rule out richer Horn message languages, solve unrestricted Horn-affine mixtures, decide arbitrary CNF, or resolve P versus NP.

```text
P_VS_NP=OPEN
```
