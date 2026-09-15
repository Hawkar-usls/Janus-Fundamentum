# JANUS Algebraic Compression / Proof-Volume Paradox (JACP) v1

**Status:** finite proof-carrying resource witness; **not** a logical contradiction and **not** a proof of `P=NP` or `P!=NP`.

`P_VS_NP = OPEN`

## 1. Frozen witness

Subject: `PHP_5_4_C1` under the unchanged frozen bound

```text
C = 1
state_cap = 256
fingerprint = 990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6
state_units = 241
live_variables = 13
Phi = 13
```

The 13 live variables are all extension variables:

```text
21,
(23,24,25),
(26,27,28),
(29,30,31),
(32,33,34)
```

All `24/24` permutations of the four triplets preserve the frozen residual exactly. Thus the four blocks form an exact syntactic `S4` orbit around variable `21`.

## 2. Local Boolean algebra

For each orbit block write

```text
(a,b,c)
```

The frozen residual contains the two gate clauses

\[
(\neg a\lor\neg b),\qquad(a\lor\neg c).
\]

Therefore

\[
b\Rightarrow\neg a,\qquad c\Rightarrow a.
\]

Only four assignments to `(a,b,c)` satisfy these gates:

```text
000
010
100
101
```

Define a new coordinate

\[
e=b\lor c.
\]

On the gated relation the inverse is exact:

\[
b=e\land\neg a,
\qquad
c=e\land a.
\]

Hence

\[
\{(a,b,c): (\neg a\lor\neg b)\land(a\lor\neg c)\}
\cong
\{(a,e):a,e\in\{0,1\}\}.
\]

This is an exact `3 -> 2` coordinate description: four valid semantic states remain four valid semantic states, but one Boolean degree of freedom is removed from the representation.

## 3. The ordinary extension route

The conservative selector definition

\[
e\leftrightarrow(b\lor c)
\]

is encoded by

\[
(\neg b\lor e),\quad(\neg c\lor e),\quad(b\lor c\lor\neg e).
\]

For each of the four symmetric blocks this definition is proof-carrying and fits the frozen cap:

```text
241 -> 251 state units
251 <= 256
```

But exact Davis-Putnam elimination of either `b` or `c` immediately exceeds the same cap in both orders for every block.

Materializing all four orbit selectors simultaneously gives

```text
281 > 256
```

Thus a small algebraic definition and a small orbit certificate do not imply a small explicit proof state.

## 4. Direct coordinate rewrite

To separate the algebraic map from the Resolution intermediate, JANUS also performs a direct proof-carrying coordinate rewrite.

For every source clause it considers only the constant four-row local table of `(a,e)`, reconstructs

\[
b=e\land\neg a,\qquad c=e\land a,
\]

and emits exactly the clauses needed to preserve that source clause in the new coordinates. No SAT oracle, model-counting oracle, or general semantic-equivalence oracle is used.

Replay succeeds for all four symmetric blocks.

For each block:

```text
live variables: 13 -> 12
Phi:            13 -> 12
state units:   241 -> 595
```

Therefore

\[
\Delta d_{semantic}=-1
\]

while

\[
\Delta V_{proof}=+354,
\qquad
\frac{595}{241}\approx2.469.
\]

The semantic state description becomes strictly lower-dimensional while the explicit certified CNF representation becomes more than twice as large and violates the frozen cap.

## 5. JACP statement

> **JANUS Algebraic Compression / Proof-Volume Paradox.**  In a fixed proof language, an exact algebraic change of Boolean coordinates can strictly reduce semantic dimension while strictly increasing the volume of the explicit proof-carrying representation needed to realize that reduction.

For the frozen witness:

\[
13\to12\quad\text{semantic live variables}
\]

but

\[
241\to595\quad\text{certified state units}.
\]

There is no logical contradiction. The paradox is a counterintuitive **resource anti-monotonicity**:

```text
SEMANTIC SIMPLIFICATION
        does not imply
PROOF-REPRESENTATION SIMPLIFICATION.
```

## 6. Three nested versions

### JACP-A — Add-to-Subtract Extension Paradox

A new variable is introduced to remove old variables. The definition itself fits the resource bound, yet the subsequent exact elimination becomes unavailable.

### JACP-B — Certificate/Materialization Paradox

The complete `S4` symmetry of four blocks has a compact generator certificate, but materializing the corresponding coordinate helpers exceeds the same state cap.

### JACP-C — Semantic-Dimension / Proof-Volume Paradox

Even bypassing ordinary Resolution and applying the exact `3->2` coordinate map directly gives `Phi 13->12` but state volume `241->595`.

JACP-C is the strongest frozen formulation.

## 7. Relation to established complexity phenomena

This phenomenon sits close to several established themes, but is not identical to any of them:

- **Haken / Extended Resolution:** pigeonhole formulas are exponentially hard for Resolution while Extended Resolution has polynomial proofs; proof complexity can depend dramatically on proof language.
- **Mahaney:** sufficiently sparse NP-complete representation would force `P=NP`.
- **Fortnow-Santhanam:** sufficiently strong uniform instance compression for SAT/OR-SAT has major complexity-collapse consequences.
- **Baker-Gill-Solovay:** relativizing methods cannot settle `P` vs `NP` because oracle worlds realize both outcomes.
- **Razborov-Rudich:** natural-proof methodology encounters a conditional barrier under strong pseudorandomness.
- **Aaronson-Wigderson:** algebrization identifies a further barrier beyond ordinary relativization and Natural Proofs.
- **Mulmuley GCT Flip:** the P-vs-NP program already contains a documented self-referential/explicit-proof perspective; hardness certificates themselves must be explicit enough to verify/construct/decode.

The historical claim is therefore deliberately narrow: **we do not claim to have invented the first P-vs-NP paradox.** The candidate novelty is this particular frozen algebraic-compression/proof-volume resource phenomenon and its proof-carrying formulation.

## 8. Connection to classical paradoxes

These are analogies, not proofs:

- **Parrondo:** stalled mechanisms can become productive when alternated. JANUS observed `0 -> 248` admissible second eliminations after interleaved recompression.
- **Braess:** adding an apparently helpful network edge can worsen the global equilibrium. Adding an extension coordinate can worsen proof-state volume.
- **Simpson:** local and aggregate trends can disagree. Local elimination progress can coexist with flat global `Phi`.
- **Skolem:** apparent size can depend on the representational/model viewpoint. Semantic dimension and internal proof volume are different notions of size.
- **Berry / Kolmogorov-Chaitin:** short descriptions and effective discovery/certification of minimal descriptions are different resources.
- **Banach-Tarski:** group action and orbit decomposition can defeat naive volume intuition; exact orbit symmetry does not itself give a free computational quotient.

## 9. Master synthesis: Compression Self-Collapse Principle

The paradox atlas suggests a common principle:

> The more uniformly an NP-hard search space can be compressed by exact, polynomial-time discoverable, polynomial-size, polynomially verifiable certificates with a strictly decreasing globally bounded potential, the closer the compression procedure itself is to being the polynomial-time solver.

A universal JANUS theorem would therefore have to prove all of:

```text
POLY_DISCOVERY
EXACT_MACRO_SEMANTICS
POLY_CERTIFICATE_BYTES
POLY_VERIFICATION
POLY_STATE_VOLUME
STRICT_GLOBAL_PROGRESS
POLY_PROGRESS_STEPS
ARBITRARY_CNF_COVERAGE
```

If all gates held for arbitrary CNF, SAT would be in P and hence `P=NP`.

They are not proved.

## 10. Next falsification gate

The immediate question is no longer whether the `3->2` algebra exists; it does on this frozen residual.

The question is:

> **Can the exact block isomorphism be realized in a proof-carrying representation whose retained state stays `<=256`, without a SAT/equivalence oracle, hidden exponential enumeration, or loss of reconstructability?**

This is the current **bounded coordinate realization gate**.

If yes, rerun `PHP_5_4_C1` and demand a real `Phi < 13` trajectory under the unchanged cap.

If no for a sufficiently broad certified representation class, the local wall strengthens from `pair-language barrier` to a genuine **semantic-compression / proof-representation barrier** for this frozen residual.

---

### Claim firewall

```text
FINITE_RESOURCE_PARADOX != LOGICAL_INCONSISTENCY
FINITE_PHP_WITNESS != ASYMPTOTIC_LOWER_BOUND
EXACT_S4_SYMMETRY != FREE_QUOTIENT
EXACT_3_TO_2_MAP != BOUNDED_PROOF_REALIZATION
P_VS_NP = OPEN
```
