# R5 E9 — Perfect-Kernel Known-Method Audit

Date: 2026-09-24

Authority: SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

## G0 — Exact frozen object

Current JANUS residual object:

- connected finite coordinate set `Omega`;
- two permutations `P,Q` generating a transitive action;
- directed permutation/Schreier digraph with arcs
  `i -> P(i)` and `i -> Q(i)`;
- therefore indegree = outdegree = 2;
- noncommuting residual;
- Z3 phase/coboundary test FAIL;
- no one-dimensional zero-mode contribution;
- low-nullity and previously certified polynomial lanes removed.

Decision problem:

find `S subset Omega` such that

```
Omega
=
S disjoint-union P^-1 S disjoint-union Q^-1 S.
```

Equivalently:

```
x_i + x_{P(i)} + x_{Q(i)} = 1
for every i.
```

## G1 — Internal anti-duplication audit

Reviewed internal predecessors:

- R5_B1B1C5B2B2_E8_CORPUS_FIRST_MECHANISM_SYNTHESIS_DOCTRINE;
- R5_B1B1C5B2B2_E8_AIG_QE_AND_INTERNAL_ANTI_DUPLICATION_SOURCE_AUDIT;
- R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM;
- R5_E9_THREE_TRANSLATE_TILING_NORMAL_FORM;
- R5_E9_COMMUTING_TWO_PERMUTATION_KERNEL_ISLAND;
- R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND.

Conclusion:

no older independent JANUS program closing the precise residual class was located.
Several latest E9 results independently rederive known external language/mechanisms and are source-bound or JANUS corollaries rather than novelty.

## G2 — Canonical external naming

### Primary canonical object

```
PERFECT KERNEL
IN A CONNECTED
2-IN / 2-OUT
TWO-PERMUTATION / SCHREIER DIGRAPH
```

Wang–Yuan–Zhao (2024) define an independent set `S` to be a **perfect kernel** when every vertex outside `S` has exactly one outgoing arc into `S`.

That is the direction used by the JANUS equation.

They separately define:

- **perfect solution** — every outside vertex has exactly one incoming arc from `S`;
- **perfect directed code** — both perfect-kernel and perfect-solution conditions simultaneously.

Therefore `perfect directed code` is related but strictly stronger in their terminology and must not be used as the primary canonical name for the JANUS residual.

### Exact Cayley collision

For `Cay(G,X)`, Wang–Yuan–Zhao Lemma 3.1(2) proves:

```
S is a perfect kernel

iff

the |X|+1 subsets
S and x^-1 S, x in X,
partition G.
```

For `X={p,q}` this is literally:

```
G = S disjoint-union p^-1 S disjoint-union q^-1 S.
```

Thus the regular-Cayley form of the JANUS three-translate equation is exact prior-art language, not a novel normal form.

### Safe aliases / adjacent language

- one-sided directed efficient domination;
- perfect kernel;
- perfect solution under global arc reversal;
- Cayley translate factorization;
- exact one-sided closed-neighborhood partition;
- perfect-code / efficient-domination language only when orientation convention and one-sided/two-sided scope are made explicit.

### Terminology firewall

Do NOT conflate:

```
perfect kernel
!=
ordinary kernel
!=
kernel-perfect digraph
!=
perfect directed code.
```

An ordinary digraph kernel only requires at least one outgoing arc from every outside vertex into an independent set.

A kernel-perfect digraph is one whose every induced subdigraph has an ordinary kernel.

Neither term supplies the uniqueness condition central to the JANUS object.

## G3 — Public-source exhaustion

### S1 — Wang, Yuan, Zhao (2024): exact canonical collision / arbitrary-group donor

Yan Wang, Kai Yuan, Ying Zhao,
*Perfect directed codes in Cayley digraphs*,
AIMS Mathematics 9(9), 23878–23889,
DOI 10.3934/math.20241160.

Audited directly from the paper:

- perfect kernel / perfect solution / perfect directed code are distinct notions;
- Lemma 3.1(2) gives the exact perfect-kernel translate-partition theorem for arbitrary finite groups;
- Example 3.3 exhibits a perfect kernel that is not a perfect solution, proving the distinction operationally.

Classification:

```
REGULAR CAYLEY TRANSLATE FORMULATION
=
EXACT_LANGUAGE_COLLISION

ARBITRARY-GROUP CAYLEY RESULTS
=
KNOWN_DONOR

GENERAL NONABELIAN TWO-GENERATOR
PERFECT-KERNEL EXISTENCE CLASSIFICATION
=
NOT PROVIDED BY THIS PAPER.
```

### S2 — Yu, Yang, Fan, Ma (2024): abelian 2-valent complete classification

*Perfect codes in 2-valent Cayley digraphs on abelian groups*,
Discrete Applied Mathematics 357 (2024), 236–240,
DOI 10.1016/j.dam.2024.06.002.

They classify strongly connected 2-valent Cayley digraphs on abelian groups admitting a perfect code and determine all perfect codes.

Classification:

```
COMMUTING / ABELIAN CAYLEY LANE
=
STRONGER_KNOWN_RESULT.
```

### S3 — Wang and Zhang (2023): vertex-transitive / coset prior art

*Perfect codes in vertex-transitive graphs*,
Journal of Combinatorial Theory A 196 (2023), 105737,
DOI 10.1016/j.jcta.2023.105737.

This gives established coset-graph language and subgroup-perfect-code structure in the undirected vertex-transitive setting.

It does not close arbitrary non-subgroup perfect-kernel existence in the present directed two-permutation setting.

Classification:

```
COSET/SCHREIER LANGUAGE
=
KNOWN PRIOR ART

PRECISE DIRECTED RESIDUAL
=
NOT CLOSED.
```

### S4 — Donno, Marino, Neri (2025): Schreier special family

*A perfect code on the Schreier graphs of an automaton group*.

They explicitly construct and classify a perfect code for a specific orbital Schreier-graph family of the Tangled Odometers automaton group.

Classification:

```
SCHREIER PERFECT-CODE SPECIAL FAMILY
=
SPECIAL_CASE_COLLISION / DONOR

GENERAL DIRECTED SCHREIER RESIDUAL
=
NOT CLOSED.
```

### S5 — Barkauskas–Host complexity barrier, independently reported by Schwenk–Yue

Schwenk and Yue,
*Efficient dominating sets in labeled rooted oriented trees*,
Discrete Mathematics 305 (2005), 276–298,
DOI 10.1016/j.disc.2005.07.008,
report the 1993 Barkauskas–Host theorem that deciding whether an arbitrary oriented graph has an efficient dominating set is NP-complete.

Classification:

```
GENERAL ORIENTED-GRAPH EXISTENCE
=
KNOWN NP-COMPLETE BARRIER

SPECIAL CONNECTED 2-IN/2-OUT
TWO-PERMUTATION RESIDUAL
=
NOT CLOSED BY THIS GENERAL RESULT.
```

### S6 — Gain/phase and representation ingredients

The Z3 phase potential is standard gain/potential machinery; one-dimensional character/abelianization ingredients are standard representation theory.

JANUS-specific coupling to `1+u+v=0` is retained only as a scoped corollary/preprocessor.

## Five required search directions — completion status

1. **Directed perfect kernel / efficient domination complexity**  
   COMPLETE for the purpose of this gate: a general oriented-graph NP-completeness barrier is known; no theorem located that collapses the exact 2-in/2-out two-permutation class.

2. **Nonabelian 2-valent Cayley digraphs**  
   COMPLETE for the purpose of this gate: Wang–Yuan–Zhao provide arbitrary-group perfect-kernel translate language and directed-code results, while the located complete 2-valent existence classification is the abelian Yu–Yang–Fan–Ma result. No complete existence classification for arbitrary perfect kernels in the nonabelian two-generator case was located.

3. **Directed Schreier / coset setting**  
   COMPLETE for the purpose of this gate: coset/subgroup theory and specific Schreier perfect-code families were located; no complete classification of arbitrary perfect kernels in connected directed two-generator Schreier actions was located.

4. **Arbitrary / non-subgroup vertex-transitive codes**  
   COMPLETE for the purpose of this gate: broad vertex-transitive/coset literature was located, but the searched results do not close the present arbitrary directed perfect-kernel residual.

5. **Two-permutation / 2-in-2-out class**  
   COMPLETE for the purpose of this gate: direct searches for perfect-kernel / efficient-domination existence on unions of two permutations and 2-in/2-out digraphs did not locate a theorem closing this exact class.

This is a public-source research audit, not a legal/exhaustive novelty certification.

## G4 — Collision matrix

| JANUS object | Correct external status | Audit classification | Required action |
| --- | --- | --- | --- |
| `Omega=S ⊔ P^-1S ⊔ Q^-1S` in regular Cayley action | Perfect-kernel translate partition | EXACT_LANGUAGE_COLLISION | Source-bind Wang–Yuan–Zhao |
| Three-translate tiling | Perfect-kernel / factorization language | JANUS_REDERIVATION | Keep only as bridge |
| Connected commuting / abelian lane | Classified 2-valent abelian Cayley perfect-code case | STRONGER_KNOWN_RESULT | Source-bind Yu et al. |
| Z3 phase potential | Gain/potential machinery | KNOWN_DONOR | Cheap preprocessor only |
| Phase ↔ 1D character | Standard representation ingredients + JANUS specialization | JANUS_COROLLARY | No novelty claim |
| Arbitrary oriented efficient domination | NP-complete | KNOWN_BARRIER_ONLY | Does not close special class |
| Schreier automaton family | Explicit special family | SPECIAL_CASE_COLLISION | Donor/control |
| Precise nonabelian phase-inconsistent two-permutation perfect-kernel residual | No located theorem closes it | SCOPED_GAP_SURVIVES | New math permitted only here |

## Scoped PASS

Audit decision:

```
PASS_SCOPED_GAP_CONFIRMED
```

The authorization applies **only** to:

```
CONNECTED
2-IN / 2-OUT
TWO-PERMUTATION / SCHREIER DIGRAPH

PERFECT-KERNEL EXISTENCE

P,Q NONCOMMUTING

Z3 PHASE FAIL

NO 1D ZERO-MODE

LOW-NULLITY LANE REMOVED

ABELIAN / KNOWN PERFECT-CODE
SPECIAL CLASSES REMOVED
```

Claim ceiling:

```
AFTER CANONICALIZATION
AND THE REQUIRED SOURCE-EXHAUSTION PASS,

NO LOCATED PUBLIC THEOREM
CLOSES THIS PRECISE RESIDUAL CLASS.

THIS IS NOT
A CLAIM THAT THE CLASS
HAS NEVER BEEN STUDIED.

THIS IS NOT
A NOVELTY CERTIFICATE.

THIS DOES AUTHORIZE
NEW JANUS MATHEMATICS
ONLY ON THE FROZEN RESIDUAL.
```

## Next authorized mathematical gate

```
R5_E9_NONABELIAN_PHASE_INCONSISTENT_PERFECT_KERNEL_GATE_V1
```

Any new artifact under that gate must cite this audit receipt as its `authorizing_audit_id` in the global pre-math ledger.

`D1 = EMPTY`

`P_VS_NP = OPEN`
