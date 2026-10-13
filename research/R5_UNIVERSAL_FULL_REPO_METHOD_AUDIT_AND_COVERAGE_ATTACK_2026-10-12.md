# R5 / JANUS — Whole-Repository Methods Audit and Universal Coverage Attack

Date: 2026-10-12 Europe/Kyiv.
Audit authority: **entire git-tracked checkout** of research branch
`Hawkar-usls/Janus-Fundamentum`, source SHA
`bd0b13a69c73f3b4db31d29522a14a6ab7927e0f` for the
first frozen inventory; refreshed after classification corrections.
The active audit PR is #516 stacked on #515, **not merged to main**.

## 0. User-requested scope and scientific boundary

First inspect **every repo folder and all tracked file paths**,
then examine which concrete methods can enter our cooperative
`SolveLinearCubicXSAT` without breaking provenance or soundness.
Only **after** this inventory attack global coverage; do not
conflate a large codebase or many successful finite gates with
a uniform worst-case polynomial SAT/UNSAT solver.

Machine outputs live at:

- `audits/r5_repository_inventory/source_manifest.json`:
  every audited file path, actual SHA256, byte count, extension,
  AST symbols/docstring/imports/workflow links for Python, and
  every tracked parent folder with content counts.
- `audits/r5_repository_inventory/review_queue.tsv`:
  full file-by-file triage table, not a handpicked shortlist.
- `audits/r5_repository_inventory/README.md`:
  all top-level directories plus manually scoped routing priorities.
- `tools/audit_r5_solver_method_inventory.py`:
  reproducible source-only scanner.
- `.github/workflows/r5-full-repository-method-audit.yml`:
  complete GitHub checkout audit and archive/commit to research branch.

Frozen successful scan:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38188870768 .
A refreshed scan after correcting transitive-module classification:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189058478 .

**Result:** 1,542 git-tracked source files, 126 folders,
12,181,876 source bytes, 425 Python source modules all
AST-parseable, 333 static local import edges, 95 workflow
definitions in the frozen full tree.
The scanner excludes its own generated inventory directory
to avoid self-reference. Generated files are versioned in PR.
Full path/AST/metadata coverage is established. Mathematical
manual review is **NOT** claimed for all 425 Python modules;
26 high-priority entrypoints were source-reviewed in the initial
classification, and remaining files are explicitly on the
review queue, never marked irrelevant on name alone.

## 1. Top-level directory dispositions (NO DELETE)

| Subtree | Files | Role for SCL solver |
| --- | ---: | --- |
| `experiments/` | 391 | Code, controls, finite falsifiers, existing SCL and graph algorithms; primary integration pool |
| `research/` | 652 | Mathematical proofs, falsification records, 123 `research/tools/` entries; preserve historical authority |
| `registry/` | 224 | Immutable JSON hypothesis/authority/provenance; check source gates, never execute as proof |
| `.github/` | 98 | 95 workflows plus issue templates; CI validation rather than solver expert |
| `docs/` | 92 | Published/sealed scientific gate context, often scoped to other tracks |
| `proof_attempts/` | 43 | Historical negative, conditional and incomplete proof objects, retain as anti-loop evidence |
| `tools/` | 19 | Independent validators, provenance observer, OdontoForge CNF search and new audit script |
| `proposals/` | 10 | Unadmitted mathematical ideas, NO automatic algorithm authority |
| `.janus/` | 4 | Governance/agent policy, no SAT decision permission |
| `reviews/` | 2 | External/internal review evidence, NOT source SAT oracle |
| `archive/` | 1 | Frozen archived controls, not default execution |
| root files | 6 | README/CONTRIBUTING/START_HERE/manifest/LICENSE/beacon; often historical routing |

Important anti-loop: the root `experiment_manifest.json` explicitly
describes `Janus-P-N-junction` and distributed heuristics, despite
living inside Fundamentum. Treat it as a separate lineage pointer,
NOT an admitted current Fundamentum all-input solver manifest.
Likewise `README.md` foregrounds the A3 and C023 public tracks;
read latest R5 source/PR authority before assuming it lists all
new private research-branch algorithms.

## 2. A concrete integration decision for the important methods

### P0 — retain and make share ORIGINAL proof-state immediately

1. `r5_universal_certified_expert_portfolio.py`:
   existing exact global interface; VALID bounded UNKNOWN and
   complete-but-possibly-exponential AND/OR fallback.
2. `r5_universal_certified_shared_proof_state.py`:
   checked sequential proof ledger, width<=2 nogoods, propagation,
   monotone O(n^2) accepted-knowledge potential. Knowledge closure
   is not automatically a SAT/UNSAT decision procedure.
3. `r5_universal_exact_support_hybrid_algebraic_dag.py`:
   exact root polynomial probes and guarded residual graph.
4. `r5_universal_exact_support_residual_dag_attack.py`:
   canonical original-SCL syntax, pins, exact residual transitions.
5. `r5_universal_exact_support_unsat_andor_certificate.py`:
   sound+complete final fallback and **independent UNSAT replay**;
   no all-input polynomial residual-count theorem.
6. `r5_universal_boolean_pc_degree3_global_attack.py`:
   all-input polynomial **SOUND UNSAT** refuter; non-refutation
   must be `UNKNOWN` because PC3 all-UNSAT completeness is OPEN.
7. `r5_universal_exact_support_mod9_dual_certificate.py`:
   already called TRANSITIVELY by old exact support; verified
   row-annihilator certificates are now lifted and replayed by
   main router, without duplicating the full MOD9 calculation.
8. `r5_universal_exact_support_pinned_oracle_attack.py`:
   already transitively used via Hybrid `ExactSupport`; exact
   pinned semantics/witness self-reduction and guarded branches.
9. `r5_universal_quadratic_gauss_mod4_attack.py`:
   transitively accessed by pinned root path, negative-only.

### P1 — conditionally useful, requires an explicit safe adapter

- `r5_universal_e118_c9_invariant_pc3.py` and
  `r5_universal_odd_automorphism_pc3_snark_probe.py`:
  provably no-loss GF2 PC3 compression **WHEN** an odd-order
  source automorphism is independently verified. Conditional
  input expert; no symmetry on arbitrary legal SCL is assumed.
- `r5_universal_cubic_three_edge_cut_factorization.py`,
  `r5_universal_cubic_nondegenerate_threecut_recognizer.py`:
  rigorous count factorization/constructive witness gluing
  for CUBIC GRAPH inputs; need recognition of graph-image
  or a bidirectionally sound representation adapter.
- `r5_universal_cubic_four_cut_21_state_interface.py`:
  exact 21-state four-edge cut boundary and witness coupling;
  evaluating arbitrary internal signatures remains unresolved.
- `r5_universal_cubic_edgecolor_direct_scl_bridge.py`:
  **graph -> SCL** reduction does NOT mean every arbitrary SCL
  has a trivial reverse recognition/decomposition.
- E108/E109 normal-span quotient and represented binary matroid
  connected components: valid `2^rank` or sum `2^rank_i`
  FPT/conditional. Need poly bounded rank gate per input;
  cannot attach as unconditional proof of P=NP.
- E78 delta-matroid XOR gluing + E74--E83/Koana-Wahlstrom:
  correct interface identities are useful, but the
  **efficiently constructible universal linear representation**
  premise is NOT available for every boundary and partition.
  Randomized polynomial representation of a SUBCLASS is
  insufficient for the deterministic all-input goal.
- E119 conflict/perfect graph recognition: conditional
  polynomial independent-set terminal **only after**
  certified perfectness of the SOURCE conflict graph.
- Fixed-perfect-matching Hall/DM trade passes, E119-E130,
  E77-E123 and parity trade paths: retain as selection
  hypotheses and exact witnesses after satisfying EACH
  local precondition, not as a blanket polynomial terminal.

### P2 — supporting engines or shadow-only witnesses, NOT UNSAT authorities

- `experiments/direct/` C022/C023 Formula-Caching:
  separate CNF calculus, precise residual DAG and independent
  proof-event counting. A provably semantic-preserving
  SCL->CNF reduction plus checked proof interface is needed
  before sharing conflict clauses. Cache hit is not a new
  mathematical SAT/UNSAT proof by itself.
- `tools/OdontoForge_PNP_EXP.py`: exact DIMACS/CNF branch search,
  independent SAT witness validation, guarded UNKNOWN;
  potential independent baseline and testing oracle, but
  no all-input polynomial bound.
- `experiments/v0.1-v2.0` Junction/GLADIUS/WalkSAT:
  randomized/heuristic SAT hints only. Cannot infer
  UNSAT from timeouts or finite failure.
- `research/tools/apma_*`: separate TRUMP/APMA admissibility,
  relation grammar, frozen raw provenance and often
  preregistered CANDIDATE/DIAGNOSTIC_ONLY gates. Preserve
  existing audit and exact common-core/orbit/quotient
  operations, but require explicit proof of conversion
  to *our original SCL relation* plus independent
  reconstructed witness AND all bit complexity.
  Current TRUMP context v3.23 restricts those tracks
  to provenance-gated checks; no blanket promotion.
- `tools/checkpoint_observer/`, `tools/validate_registry.py`
  and `tools/validate_lineage.py`: essential evidence
  infrastructure, not SAT experts.

### P3 — negative/superseded/disallowed-as-positive, PRESERVE as controls

- Pfaffian cube signed cancellation: K3,3 SAT but +6/-6=0.
- Single fixed modular normalized colouring-count tests:
  SAT false zeros for every fixed modulus q.
- E118/Tutte etc unbounded-width and exponential residual DAG
  source families: block assumption of globally polynomial
  states and globally bounded-treewidth decomposition.
- E118 UNSAT90 invalidates all-input degree-2 Boolean PC
  completeness; does NOT invalidate degree-3 by itself.
- Source-specific FAIL, NO-GO, FPT and finite survivor
  research attempts: **do not delete**. Their absence from
  a currently imported graph does not make them worthless.
- The exact fixed count and full 2-adic residue are correct
  decision identities but without a polynomial evaluator
  are NOT practical admitted polynomial experts.

## 3. Actual integration changes made after scanning

1. The existing MOD9 annihilator already returned from
   `ExactSupportHybrid` is now exposed through
   `SolveLinearCubicXSAT_Portfolio`, with independently
   replayed congruence equation:
   `lambda^T B=0 mod9`, `lambda^T b !=0 mod9`.
   No duplicate MOD9 solve is run merely for display.

   Evidence:
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38188968622
   SUCCESS; E129 base UNSAT12 emits a 12-entry independently
   checked certificate.

2. A full 11-source cross-family coverage audit was added:
   `experiments/r5_universal_certified_portfolio_coverage_matrix.py`.
   It constructs real legal SCL fixtures from E61, E129, E118,
   Tutte12 E123, Fano, K3,3, prism and snarks, independently
   preserves each source's known SAT/UNSAT truth, and asks the
   strictly polynomial budget profile
   `pc3_max_n=48, bounded_states=0` for its decision.

   CI:
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189027396
   SUCCESS.

   Observed verdict:
     5 / 11 => SAT/UNSAT DECIDED correctly;
     6 / 11 => UNKNOWN (source truth independently known).

   The exact UNKNOWN list is:
     E61_SAT12, K3,3_SAT27, Prism5_SAT45,
     Flower_J5_UNSAT90, E118_UNSAT90, E118_SAT90.

   This **refutes COMPLETE COVERAGE OF THIS SPECIFIC BUDGET
   CONFIGURATION**, not the possibility that a different
   polynomial budget, additional certified source transformations,
   or entirely different global theorem could cover all inputs.

3. The odd-order automorphism PC3 adapter is now **INTEGRATED**
   at `experiments/r5_universal_certified_odd_symmetry_adapter.py`.
   The router accepts an optional `certified_symmetry` input
   permutation, checks exact bijectivity, odd order bounded by n,
   original clause permutation and full-order row orbits, and
   then runs the already proof-replaying orbit-compressed PC3.
   An invalid permutation yields UNKNOWN; no automorphism
   discovery on general SCL is claimed.

   Verified CI:
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189176839
   SUCCESS: E118 UNSAT90 => admitted UNSAT; J5 snark SCL90 =>
   admitted UNSAT; E118 SAT90 => UNKNOWN; invalid symmetry
   => UNKNOWN. Full prior portfolio regression also passed:
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189176810 .

   Crucial anti-cheat: this changes the actual coverage of the
   **annotated, verified-symmetry** input protocol, but cannot
   yet be counted as a universal all-input automatic selector.
   The six-UNKNOWN baseline above did not supply any symmetry;
   it remains the frozen baseline for that unannotated budget.

## 4. Global-coverage theorem: attack AFTER complete inventory

Let `E_i` be a deterministic bounded expert with precise
soundness precondition `P_i(F)`, polynomial resource
limit `b_i(n)`, and certified source-level output semantics.
Define its actual DECIDED domain

  D_i(n) = {F legal SCL of size n :
              P_i(F) and E_i(F) in {verified SAT, proven UNSAT}
              within b_i(n)}.

A fixed finite or polynomially sized portfolio is universally
polynomial ONLY if:

  (1) for all n, all legal SCL_n subset union_i D_i(n);
  (2) sum_i [recognition_i + transformation_i + solve_i
             + reconstruction_i + verification_i
             + certificate_bits_i] <= n^C
      for one fixed C independent of n;
  (3) output soundness, completeness and SAT witness extraction
      hold under ORIGINAL Exact-One semantics, including pins.

The union `D_i` is a mathematical **set COVERAGE theorem**.
Proving monotone potential and O(n²) accepted shared facts
does NOT establish (1): information can saturate at UNKNOWN.
An unbounded exponential AND/OR fallback establishes total
correctness but not condition (2).

Existing proof-complexity theory gives serious prior warnings
against inferring constant-degree polynomial calculus
completeness or bounded-width CSP consistency from
finite tests. Relevant:
Buss, Grigoriev, Impagliazzo, Pitassi,
`Linear Gaps between Degrees for the Polynomial Calculus
Modulo Distinct Primes`, JCSS 62 (2001),
DOI 10.1006/jcss.2000.1726.
These results do NOT directly transfer to the exact JANUS
linear/cubic/square SCL encoding without a proved
degree-preserving reduction.

### Next legally decisive test

Use the **six actual UNKNOWN controls** rather than random
new easy SAT families. For each:
- locate a source-bound existing exact theorem/transformer,
- prove the explicit input precondition and full semantics,
- admit it as a certificate-carrying bounded expert with
  independent replay,
- rerun the full matrix and prove whether coverage improved;
- do NOT declare all-input coverage even if all 11 become decided.

Then seek either a SINGLE uncovered infinite adversarial
family for the saturated *entire* bounded portfolio, or
a true **uniform global contraction theorem** that produces
SAT witness/UNSAT within polynomial total cost on every SCL.

## 5. Admission ledger

FULL_TREE_PATH_FOLDER_CONTENT_METADATA_AUDIT = VERIFIED_CI.
ALL_PYTHON_AST_PARSE = VERIFIED_CI.
ALL_PYTHON_SEMANTIC_MATHEMATICAL_REVIEW = NOT_COMPLETE.
SOURCE_METHOD_ROLE_FIRST_PASS = PARTIALLY_MANUALLY_VERIFIED.
SOLVER_PORTFOLIO_MOD9_PROOF_UPLIFT = VERIFIED_CI.
CERTIFIED_ODD_SYMMETRY_PC3_ADAPTER = VERIFIED_CI_CONDITIONAL.
PORTFOLIO_11_FIXTURE_POLY_PROFILE_DECIDES_ALL = FALSE_FINITE.
PORTFOLIO_PROOF_STATE_MONOTONE_KNOWLEDGE_DESCENT = PREDECESSOR_PROVED.
ALL_SCL_POLYNOMIAL_EXPERTS_UNION_COVERAGE = OPEN.
ALL_SCL_POLYNOMIAL_CERTIFIED_WITNESS_EXTRACTION = OPEN.
UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
