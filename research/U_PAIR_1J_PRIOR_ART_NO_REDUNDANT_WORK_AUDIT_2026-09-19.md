# U-PAIR-1J Prior-Art / No-Redundant-Work Audit — 2026-09-19

**Authority:** READ_ONLY_LITERATURE_AUDIT__NO_SCIENTIFIC_PROMOTION  
**Purpose:** prevent Janus/TRUMP from spending experimental budget on synthesis phenomena that are already standard, analytically discharged, or covered by public benchmark/tooling literature.  
**Parent experimental checkpoint:** `80645e7ddae908f4f547569663d856bbe520fe9f` (mixed source freeze + independent source check).  
**This file does not mutate any frozen verdict, calculus, source family, or preregistration.**

## Executive finding

The current `SYNTHESIS_OF_MIXED_EXACT_GUARDS` family is useful as an **implementation legality/control case**, but—after the mandatory V1.1 typing/composition control passes—it is not a strong candidate for another full scientific scaling campaign.

Reason: the family has an explicit polynomial construction by inspection.

For each pair (j),

- (P_j,Q_j,R_j) are constant-width affine predicates;
- (O_j=P_j\lor Q_j\lor R_j) has a constant-size ITE realization;
- (
eg O_j) has a constant-size ITE realization;
- (G_v=A_v\oplus O_j) has a constant-size ITE realization once a verified DAG root may legally be used as a guard/child under frozen V1.1;
- a shared priority selector over (n) exact guards has the same (O(n\log n)) structure already used in the Tseitin hostile;
- (Pi_{domain}) has a direct linear symbolic certificate because every graph edge occurs twice, total charge is odd, and every OR3 block occurs exactly twice.

Therefore, once the mandatory mixed-composition killer control establishes that the frozen V1.1 typing rules accept the structural ITE composition, a constructor-specific symbolic upper bound can be written **before** any hostile scaling run.

A simple node accounting for the frozen source design is:

[
S_{guard} \le 5n+O(1)
]

(one (A_v) per vertex, (3n/2) raw OR3 affine atoms, (n) ITEs for all OR3 blocks, (n/2) ITEs for all negated OR3 blocks, and (n) mixed-guard ITEs), while the priority selector is

[
S_{select,exclusive}\le (n-1)\log_2 n
]

for the same binary witness-code strategy used in the frozen Tseitin constructor. The domain certificate is linear in (n+|E|). Thus this source family already has an explicit polynomial proof/witness architecture; another (n=16,32,64,128,256) series can at most validate engineering/accounting, not discover whether compact representation exists.

### Recommended handling of the frozen mixed prereg

Do **not** retroactively edit the preregistration.

After source freeze:
1. run only the mandatory `MIXED_EXACT_GUARD_COMPOSITION_CONTROL`;
2. if it FAILs, record `FAIL_CALCULUS_EXPRESSIVITY` and stop;
3. if it PASSes, write a separate successor/read-only analytical-discharge note establishing the constructor-specific (O(n\log n)) upper bound;
4. treat the five-size hostile series as optional engineering/reproducibility evidence, not as a necessary scientific discovery run;
5. move scientific effort to published hard/discriminating families.

If strict adherence to the old prereg requires the hostile series for that exact verdict label, either execute it explicitly as an **engineering confirmation** or retire the prereg without claiming `PASS_SCOPED_MIXED_GUARD_HOSTILE_SYNTHESIS`. Do not change the old success condition after seeing the analytical result.

---

## What is already established in the literature

### 1. DOMAIN + conditional WITNESS is standard Boolean functional synthesis semantics

Boolean functional synthesis asks for (G(Y)) such that

[
F(G(Y),Y)
]

holds whenever

[
\exists X F(X,Y)
]

holds. Equivalently, the projection/domain (exists X F) and a conditional Skolem witness are already the standard semantic object.

Useful references:
- Akshay et al., *What's Hard About Boolean Functional Synthesis?*, CAV 2018 / FMSD 2021.
- Akshay et al., *Knowledge Compilation for Boolean Functional Synthesis*, FMCAD 2019.
- Akshay et al., *Counterexample Guided Knowledge Compilation for Boolean Functional Synthesis*, CAV 2023.

**Janus-specific value:** explicit packaging as ((D,f,pi_D,pi_f)), independent domain proof, source freeze, forbidden-oracle audit, and local proof accounting. Do not claim the underlying domain/witness semantics as new.

### 2. Proof/certificate extraction of Skolem functions is established

Existing lines include:
- Q-resolution certificate extraction (e.g. QRPcert/QBFcert; Skolem/Herbrand functions emitted as AIGs);
- proof-based QBF strategy/function extraction;
- SAT 2026 SynQBF, a sound/complete QBF proof system with polynomial-time Skolem/Herbrand extraction from proofs and an optimality result among proof systems supporting efficient extraction.

Key current reference:
S. Akshay, O. Beyersdorff, S. Chakraborty, L. Kasche, M. Mahajan, L. N. Spachmann,
*Proof Systems for QBF Synthesis: Extracting Skolem and Herbrand Functions*, SAT 2026,
DOI 10.4230/LIPIcs.SAT.2026.3.

**Janus-specific value:** the frozen restricted local calculus and proof-carrying governance may still be distinct, but “proof-carrying Skolem extraction” itself is not a new concept.

### 3. Factored/local synthesis is established

John et al., *Skolem Functions for Factored Formulas*, FMCAD 2015, explicitly exploits conjunctions of small-support factors and gives a CEGAR-style synthesis algorithm.

This is directly relevant whenever a proposed hostile is built from many small local gadgets.

**No-redundant-work rule:** do not treat “we can exploit local factorization” as a new scientific result. A new hostile should demonstrate a separation or capability not already explained by generic factorization.

### 4. Tractable representations are heavily studied

- SynNNF (FMCAD 2019) guarantees polynomial-time synthesis for specifications represented in that form.
- SAUNF (LICS 2021) gives a characterization: polynomial-time synthesis corresponds to polynomial-time compilation to SAUNF; polynomial-size functional solutions correspond to polynomial-size equivalent SAUNF representations.
- Follow-up work on tractable representations appeared in Annals of Mathematics and Artificial Intelligence (2024).

**No-redundant-work gate:** before inventing a new synthetic “hard” family, first ask whether its compact witness follows from an obvious circuit construction or whether it is transparently compilable into a known tractable representation. If yes, do not spend a hostile scaling campaign rediscovering that fact.

### 5. Practical Boolean functional synthesis tooling already exists

Use as external baselines, not scientific authority:
- **BFSS** — public source and verifier;
- **Manthan / Manthan2** — data-driven synthesis + proof-guided/automated-reasoning repair;
- **c2syn / cnf2syn** — SynNNF knowledge-compilation implementations;
- public **BooleanFunctionalSynthesis/benchmarks** corpus with Arithmetic, Disjunctive Decomposition, Factorization, QBFEval 2017/2018, in AIG/Verilog/QDIMACS/CNF/NNF forms.

These tools and benchmark suites should replace hand-invented easy synthetic families whenever the research question is generic Skolem synthesis scalability.

### 6. XOR/parity handling itself is standard

Modern SAT tooling such as CryptoMiniSat includes native XOR handling and Gaussian/Gauss-Jordan elimination.

This does **not** invalidate Janus' no-SAT proof-carrying calculus, but it means “we can efficiently manipulate affine/XOR constraints” is not novel and should be treated as infrastructure, not a research frontier.

### 7. Tseitin hardness is proof-system-specific

SAT 2022 tight bounds show exponential/treewidth-dependent hardness for Tseitin formulas in regular resolution and OBDD-based refutation systems, with related DNNF bounds.

That does **not** imply that the total **Tseitin search witness relation** used by U-PAIR must have a large Skolem/search DAG. Janus' frozen Tseitin PASS is therefore compatible with the known literature.

**No-redundant-work rule:** never transfer a lower bound from refuting an unsatisfiable Tseitin CNF to the different object “find a violated parity vertex” unless an explicit reduction preserves the representation/proof model.

### 8. OBDD-only hard functions are not automatically V1.1-hard

Functions such as Hidden Weighted Bit have exponential OBDD lower bounds, but V1.1 uses a general hash-consed ITE/DAG calculus rather than a fixed ordered read-once branching program.

Do not spend time on HWB/ISA/multiplication merely because of OBDD lower bounds unless the V1.1 experiment first freezes restrictions that make the lower bound applicable.

---

## Published families that are more informative than another easy synthetic scaling run

### A. bPHP / collision witness family — HIGH PRIORITY

Juba & Meel, AAAI 2026, prove a family where:
- polynomial-size Skolem functions exist;
- resolution-based interpolation is forced to produce exponentially large circuits.

This is an excellent discriminator for Janus because a PASS would show the frozen calculus avoids a known interpolation bottleneck, while a FAIL can be localized without confusing “small witness does not exist” with “our synthesis route cannot find/certify it.”

Reference:
Brendan Juba, Kuldeep S. Meel,
*The Limitations and Power of NP-Oracle Based Functional Synthesis Techniques*,
AAAI 2026, DOI 10.1609/aaai.v40i17.38440.

Use the explicit bounded-pigeonhole collision family from their Theorem 5 as a concrete hostile/reference family.

### B. Sequential-synthesis trap family — CONCEPTUAL/HIGH VALUE, CHECK CONSTRUCTIVITY

The same AAAI 2026 paper gives relational families with small global Skolem functions where a natural sequential synthesis approach can be driven to exponentially large later functions.

Use this primarily as an **anti-pattern/specification for a hostile**, because the presentation uses a hard function (h) in the construction and may not directly give a convenient finite executable benchmark.

Scientific question for Janus:
does frozen local derivation avoid early local commitments that destroy later sharing?

### C. Public BFS benchmark corpus — REQUIRED BASELINE BEFORE MORE CUSTOM FAMILIES

Before claiming practical synthesis novelty, run/compare against the public BooleanFunctionalSynthesis benchmark corpus and, where feasible, Manthan2/BFSS/c2syn.

This is not to import their solver as Janus authority. It is to avoid spending weeks on instances that existing synthesizers already solve routinely.

### D. SynQBF 2026 — THEORY COMPARISON, NOT A BENCHMARK

Before trying to prove broad completeness/optimality properties of V1.1, compare the claimed property with SynQBF. SynQBF already gives soundness/completeness and efficient function extraction from proofs in a general QBF setting.

A useful Janus research question is narrower and sharper:
> Which SynQBF proof fragments can be translated into V1.1 with polynomial overhead, and which V1.1 proof families admit a compact SynQBF representation?

That is a real proof-system comparison; re-proving generic “proofs can carry Skolem functions” is redundant.

---

## Mandatory NO-REDUNDANT-WORK gate for future hostiles

Before freezing a new hostile, answer all of these:

1. **Exact same object?** Is the target a relational Skolem/BFS/QBF synthesis problem already covered by a standard framework?
2. **Explicit circuit check.** Can we write a polynomial-size witness circuit by inspection? If yes, representation blowup is not an open experimental question.
3. **Known tractable representation.** Is a polynomial SynNNF/SAUNF/factored compilation immediate or already published?
4. **Published hard family available?** Prefer a cited family with a known separation/lower bound over an invented random/synthetic family.
5. **Model match.** Does a cited lower bound apply to our exact proof/representation model? OBDD, resolution, regular resolution, DNNF and unrestricted ITE-DAG lower bounds are not interchangeable.
6. **External solver baseline.** Has the family already been run through BFSS/Manthan2/c2syn or public synthesis benchmarks?
7. **Novel separator.** What outcome would teach us something not already implied by the source construction or literature?
8. **Analytical discharge first.** If a symbolic upper bound is available, prove it before running a scaling series.
9. **Finite scaling role.** Use (n=16..256) only for implementation/resource validation after theory, not as a substitute for an asymptotic argument.
10. **Claim ceiling.** Keep `GENERAL_SAT_IN_P=NOT_PROVED`, `P_EQ_NP=NOT_PROVED`, `P_VS_NP=OPEN`.

---

## Recommended immediate decision

For the current frozen mixed exact-guard lineage:

- **keep** the source freeze and independent source check;
- **run** the mandatory tiny mixed-composition killer control because it tests a genuine V1.1 typing/expressivity issue;
- **do not treat** the five-size mixed hostile series as a necessary scientific discovery experiment after that control passes;
- **derive** the (O(n\log n)) constructor-specific proof size/work bound analytically;
- **move next scientific effort** to a published discriminating family, preferably the AAAI 2026 bounded-pigeonhole collision family, plus public BFSS/Manthan2/SynNNF baselines;
- **compare theory** against SAT 2026 SynQBF before any broad proof-system claim.

---

## Source index

1. Akshay et al., *What's Hard About Boolean Functional Synthesis?*, CAV 2018 / FMSD 2021.  
   https://arxiv.org/abs/1804.05507
2. John et al., *Skolem Functions for Factored Formulas*, FMCAD 2015.  
   https://arxiv.org/abs/1508.05497
3. Akshay et al., *Knowledge Compilation for Boolean Functional Synthesis*, FMCAD 2019.  
   https://arxiv.org/abs/1908.06275
4. Shah, Akshay, Chakraborty, *A Normal Form Characterization for Efficient Boolean Skolem Function Synthesis*, LICS 2021.  
   https://arxiv.org/abs/2104.14098
5. Golia, Roy, Meel, *Manthan: A Data-Driven Approach for Boolean Function Synthesis*, CAV 2020.  
   https://arxiv.org/abs/2005.06922
6. Golia et al., *Engineering an Efficient Boolean Functional Synthesis Engine* (Manthan2), ICCAD 2021.  
   https://arxiv.org/abs/2108.05717
7. Akshay, Chakraborty, Jain, *Counterexample Guided Knowledge Compilation for Boolean Functional Synthesis*, CAV 2023.  
   https://doi.org/10.1007/978-3-031-37706-8_19
8. Akshay et al., *Proof Systems for QBF Synthesis: Extracting Skolem and Herbrand Functions*, SAT 2026.  
   https://doi.org/10.4230/LIPIcs.SAT.2026.3
9. Juba, Meel, *The Limitations and Power of NP-Oracle Based Functional Synthesis Techniques*, AAAI 2026.  
   https://doi.org/10.1609/aaai.v40i17.38440
10. Itsykson, Riazanov, Smirnov, *Tight Bounds for Tseitin Formulas*, SAT 2022.  
    https://doi.org/10.4230/LIPIcs.SAT.2022.6
11. QRPcert / QBFcert Skolem-Herbrand certificate extraction.  
    https://fmv.jku.at/qrpcert/
12. BFSS source.  
    https://github.com/BooleanFunctionalSynthesis/bfss
13. Manthan source.  
    https://github.com/meelgroup/manthan
14. c2syn source.  
    https://github.com/BooleanFunctionalSynthesis/c2syn
15. cnf2syn source.  
    https://github.com/BooleanFunctionalSynthesis/cnf2syn
16. Public Boolean functional synthesis benchmarks.  
    https://github.com/BooleanFunctionalSynthesis/benchmarks
17. CryptoMiniSat XOR/Gauss-Jordan support.  
    https://github.com/msoos/cryptominisat

## Scientific firewall

This audit is a literature/prior-art map. It does not establish a new complexity theorem, does not promote V1.1, does not modify any frozen result, and does not change:

`GENERAL_SAT_IN_P = NOT_PROVED`  
`P_EQ_NP = NOT_PROVED`  
`P_VS_NP = OPEN`.
