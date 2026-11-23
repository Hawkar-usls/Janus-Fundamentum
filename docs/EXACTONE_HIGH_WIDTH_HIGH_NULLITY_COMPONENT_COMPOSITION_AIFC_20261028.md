# Exact-One decomposition at simultaneously high primal width and affine nullity

Date: 2026-10-28. **Special-class factorization**, not a general SAT/P=NP result.

## Theorem and algorithm

Let an Exact-One constraint instance be the conjunction F = F_1 AND ... AND F_t where the sets of variables of each F_i are mutually disjoint. The incidence graph's connected components provide a canonical such partition in polynomial time. Then SAT(F) iff SAT(F_i) for every i. A global satisfying assignment is the disjoint union of independently checked local witnesses. If one component is UNSAT, an independently checked local UNSAT certificate suffices. Each factor may contain an arbitrary number of cycles and have arbitrarily large primal treewidth.

Apply the exact GF(2)-affine-nullity local solver to each component, with local dimension k_i. Total time, including factorization, is O(poly(L)+ sum_i 2^(k_i) poly(L_i)), with L_i the component encoding length. Certificate size has the same (loose) bound, and is independently replayed. This is polynomial for families with all k_i bounded, even if total K=sum_i k_i grows linearly in the number of components. The algorithm returns OPEN_COMPONENT_CAP when a local component exceeds the configured resource threshold; it never replaces an unknown with UNSAT. No claim for *connected irreducible* high-width high-nullity instances.

Implementation: research/exactone_component_factorization.py. Independent verifier recomputes the actual component partition from original clause incidence, checks the exact variable renaming, each local original-clause affine certificate, the SAT/UNSAT composition and every global SAT literal. Faking an omitted component or a different variable ID is detected even if a new JSON checksum is computed.

## High-high benchmark family

Take t independent copies of a cubic Exact-One hub-pair clique on m+1 variables. Each copy enforces, for each pair of leaves i<j, EXACT1(h,u_i,u_j). Each block has primal K_(m+1) and affine nullity 1. The disjoint union has primal treewidth m and GF(2) nullity t, both arbitrarily large for t=m. Nonetheless it is exactly solvable by independently checking only 2 candidates per component, not 2^t global assignments.

Concrete test: t=16, m=16: **272 variables, 1,920 cubic clauses, primal treewidth 16, global affine nullity 16**. A second fixture adds one cubic leaf-only clause to the final component, producing a parity-consistent but unsatisfiable local factor. Both SAT witness composition and UNSAT reduction are independently checked. Small reference tests compare complete results against original full truth-table enumeration. Forged/rehashed component identities and a deliberately unsupported local-nullity case must be rejected.

**This is a standard disjoint-CSP factorization, not a novel universal complexity theorem.** The construction demonstrates that large total graph width plus large global XOR-nullity is not *by itself* sufficient to make an instance hard. The remaining genuinely difficult target is connected high-width, high-nullity irreducible structure that resists polynomial discovery of small separators or compact exact relations.

## AIFC integration boundary

The repository Hawkar-usls/AIFC (Apache-2.0) is a protocol for auditing independent-future random-target experiments, **not** an NP/SAT solving model. Its canonical strict JSON parser, domain-separated SHA-256 function, fail-closed status discipline and semantic-lineage provenance are useful for making JANUS research artifacts auditable. Cross-repo CI pins AIFC to commit 86bf957815911658edad330d5948e1bea2ea59b1, runs the genuine AIFC reference/verifier/canonical.py against our JSON mathematical certificate, independently rejects duplicate JSON keys/non-canonical payloads, and computes a *JANUS-defined* domain hash. This is not an AIFC-certified SAT proof; the Fundamentum SAT verifier independently checks the mathematical certificate. Lapis transports the mathematical result as annotation-only IR.

AURA Oracle / CHRONOS is the more natural scientific use case for AIFC: a future experiment can preregister and externally freeze its candidate before independent entropy generation, with full ledger/witness/selection safeguards. No physical retrocausality is claimed or experimentally established by a software-only integration.

No production changes, provider jobs, or Rowan credits. P_VS_NP=OPEN.
