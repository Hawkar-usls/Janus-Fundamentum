# R5 E8 6I — Prior-Art / Novelty Audit for Effective pp-Normalization

**Date:** 2026-09-23  
**Candidate:** fixed finite residually-small cube-term family K; polynomial compiler from generators/compact representations of invariant relations to polynomial-size pp-definitions over a fixed finite basis.  
**Status:** PRIOR_ART_AUDIT_PASS_NO_EXACT_PUBLIC_COLLISION_FOUND. This is not a legal novelty opinion and not a theorem seal.

## 1. Exact claim audited

The candidate claim audited here is deliberately narrower than Bulín–Kompatscher Question 30 (Section 6.3) in full generality:

> For a fixed finite family K of finite algebras with a common cube/edge term, assuming V(K) is residually small, construct in polynomial time from arbitrary generators (or a polynomial compact representation) of an invariant relation R <= A_1 x ... x A_n, A_i in HS(K), a pp-definition over one fixed finite basis, with polynomial construction time and output length O(n^max(2,k-1)).

No claim is made for arbitrary few-subpowers languages, arbitrary residual-finite algebras outside the BMS residual-small algorithmic scope, unrestricted 3-edge algebras, or SAT/P-vs-NP.

## 2. Baseline source status

Bulín–Kompatscher, arXiv:2305.01984v3 (27 Jan 2026), Section 6.3, explicitly asks whether a short pp-definition can be computed in polynomial time from generators and states that the answer is known over the Boolean domain but is unknown even in the context of residual finiteness.

Therefore the existence theorem for short pp-definitions in their residual-finite cube/edge setting is not itself prior art for an effective compiler from generators.

The current v3 location is **Section 6.3, Question 30**. Earlier Janus references to “Question 6.3” were a section/question conflation and must not be used in final theorem/novelty statements.

## 3. Closest direct overlap found: Kalampakas 2026

Antonios Kalampakas, *Automatic constraints with few subpowers and graphoid recognition*, arXiv:2609.07891v1 (7 Sep 2026), is the strongest direct prior-art overlap found.

The paper:
- explicitly cites Bulín–Kompatscher Question 30 (Section 6.3);
- for one explicit family of 3-edge algebras built from a prime field plus an inactive state, gives a canonical O(k^2)-bit normal form computable from either an NFA or arbitrary generators;
- Proposition 5.6 constructs a polynomial-time O(k^2)-size pp-definition from that normal form;
- explicitly says the result concerns this displayed family and leaves equally small effective encodings for arbitrary 3-edge algebras open.

### Consequence for novelty language

The Janus candidate must **not** claim:
- first constructive answer to Question 30 (Section 6.3) in any non-Boolean setting;
- first generator-to-short-pp compiler for a 3-edge algebra;
- first effective short pp-definition result beyond Mal'tsev/near-unanimity.

The possible novelty is instead:

> a uniform construction for the entire fixed finite residually-small cube-term regime covered by BMS SMP/CompactRep machinery, rather than a specially characterized algebra family.

Kalampakas is therefore a **partial collision / special-family predecessor**, not an exact collision with the audited theorem.

## 4. Older few-subpowers learnability results

Idziak–Marković–McKenzie–Valeriote–Willard prove global tractability for k-edge languages and polynomial exact learnability using improper equivalence queries. These results provide compact/few-subpowers structure and learning algorithms, but the located statements do not give the audited direct transformation

generators(R) -> explicit short pp-formula defining R.

Thus they are background prior art and possible technique donors, but not an exact theorem collision.

## 5. BMS 2019

Bulatov–Mayr–Szendrei provide the crucial algorithmic substrate:
- SMP(K) polynomially equivalent to compact-representation computation;
- transfer to HS(K);
- polynomial SMP in the residually-small cube-term regime;
- canonical/d-coherent reductions and the abelian-block machinery.

The located BMS results do **not** state a polynomial algorithm producing a short pp-definition from arbitrary generators. They are source dependencies of the Janus compiler, not an earlier statement of the same compiler theorem.

## 6. 2024–2026 nilpotent / clonoid route

The following current work was checked as possible renamed prior art:

### Kompatscher, STACS 2024 — subpower membership of 2-nilpotent algebras
The paper discusses short pp-definitions as a possible route to coNP certificates and asks whether finite nilpotent Mal'tsev algebras have short pp-definitions. It does not provide a general generator-to-pp compiler.

### Fioravanti–Kompatscher–Rossi, arXiv:2602.04034 — *Clonoids over vector spaces*
The paper proves uniform-generation results for clonoids and polynomial SMP for certain 2-nilpotent Mal'tsev algebras. No primitive-positive / pp-definition synthesis theorem matching the audited compiler was located.

### Patrick Wynne, arXiv:2608.18917 — *Structure and Complexity of 2-Nilpotent Mal'cev Algebras*
The paper develops central extensions and difference clonoids and obtains polynomial SMP for a large class of 2-nilpotent Mal'tsev algebras. No primitive-positive / pp-definition synthesis theorem matching the audited compiler was located.

These papers are adjacent algorithmic work, but they solve SMP/structure questions rather than the audited effective short-pp normalization problem.

## 7. Boolean and small-domain prior art

Bulín–Kompatscher explicitly record a positive answer to their effective-construction question over the Boolean domain. Earlier Boolean “polynomial closedness” work is therefore genuine special-case prior art.

Their existence theorem also covers three-element languages under the residual-finite hypothesis, but v3 still distinguishes existence of short definitions from an efficient generator-to-definition algorithm.

The Janus novelty claim must therefore remain scoped to the uniform constructive residual-small cube-term compiler, not Boolean/small-domain existence.

## 8. Current author/project sweep

Current public pages checked:
- Michael Kompatscher's publication/preprint list;
- Jakub Bulín / COLA:ULOM project results;
- current arXiv title/version for arXiv:2305.01984;
- Vojtěch David's recent short-pp talks/work.

The latest public Bulín–Kompatscher version found is v3 dated 27 Jan 2026; it still states Question 30 (Section 6.3) as open. The current author/project publication lists checked do not list a later paper announcing a general effective generator-to-short-pp construction.

This is evidence against an obvious public collision, but is not an exhaustive proof that no unpublished/submitted/obscure result exists.

## 9. Novelty matrix

| Result class | Prior art located? | Collision with Janus candidate? |
| --- | --- | --- |
| Existence of polynomial-size pp-definitions in residual-finite cube/edge setting | Yes — Bulín–Kompatscher | YES for existence only; Janus must not claim novelty there |
| Boolean effective generator -> short pp | Yes | YES special case |
| Explicit prime-field + inactive-state 3-edge family, generators -> short pp | Yes — Kalampakas 2026 | YES special family; strongest direct overlap |
| Arbitrary fixed 3-edge algebra, generators -> short pp | No general result located; Kalampakas says open in his setting | No exact collision located |
| Fixed finite residually-small cube-term K, arbitrary generators -> short pp uniformly | **No exact public result located** | Candidate novelty survives this audit |
| General Question 30 (Section 6.3) for every language with short pp-definitions | Open in BK v3 | Janus does not claim this generality |
| SMP in residual-small cube-term | Yes — BMS | Dependency, not novelty |
| Few-subpowers learnability/global tractability | Yes | Related, not the same output problem |
| 2-nilpotent/clonoid SMP algorithms | Yes | Related, not pp synthesis |

## 10. Recommended claim wording

Safe pre-seal wording:

> We give a candidate polynomial-time construction of short pp-definitions from generators for invariant relations of a fixed finite family of algebras with a cube term generating a residually-small variety. To the best of our public-source search through 23 Sep 2026, we found no prior result covering this full uniform scope. The closest direct overlap is Kalampakas (2026), which gives an explicit generator-to-short-pp construction for a particular 3-edge family.

Do **not** write:
- “we solve Question 30 (Section 6.3)” without qualification;
- “first effective short pp-definition algorithm”;
- “first non-Boolean positive answer”;
- “general 3-edge compiler”;
- “residual-finite in full generality” if the proof relies on residual-small BMS algorithms.

Better:
> “a scoped positive result candidate for Question 30 (Section 6.3) in the fixed finite residually-small cube-term regime.”

## 11. Audit verdict

PRIOR_ART_EXACT_COLLISION
=
NONE FOUND IN PUBLIC SOURCES SEARCHED

CLOSEST_DIRECT_OVERLAP
=
KALAMPAKAS_2026_SPECIAL_3_EDGE_FAMILY

NOVELTY_BOUNDARY
=
UNIFORM_FIXED_FINITE_RESIDUALLY_SMALL_CUBE_TERM_GENERATORS_TO_SHORT_PP

NOVELTY_CONFIDENCE
=
MODERATE_TO_HIGH_PUBLIC_SOURCE_CONFIDENCE
NOT A LEGAL OR EXHAUSTIVE NOVELTY CERTIFICATION

THEOREM_SEAL
=
HOLD

Remaining pre-seal work:
1. final dependency ledger with exact source theorem numbering and corrected current-v3 Question 30 (Section 6.3) numbering;
2. editorial/source-binding cleanup of the standalone manuscript;
3. preferably one external human expert review because the result addresses an explicitly open question in a substantial scoped regime.

D1 = EMPTY.
P_VS_NP = OPEN.
