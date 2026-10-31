# R5 E9 — NAE Repair-Mask Self-Similarity and Reconfiguration Barrier

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_SELF_SIMILARITY_THEOREM + SOURCE_RECONFIGURATION_BARRIER__NO_D1_PROMOTION

Parent: R5_E9_NONLOCAL_REPAIR_PROPAGATION_RANK_GATE_V1

Checker: experiments/r5_e9_nae_repair_mask_self_similarity_checker.py

## 1. Model-relative repair masks

Let F be a positive NAE instance on variable set V and let y be any satisfying assignment.
For a Boolean mask h in F2^V define the repaired assignment

z = y XOR h.

For every hyperedge e, define the model-relative mask constraint

R^y_e(h|e)  iff  NAE(y|e XOR h|e).

Let Repair_y(F) be the conjunction of these mask constraints over all e.

## 2. Exact self-similarity theorem

### Theorem RMS-1

The map

T_y : h -> y XOR h

is a bijection

Mod(Repair_y(F))  <->  Mod(F).

### Proof

For each edge e:

h satisfies R^y_e
iff NAE(y|e XOR h|e)
iff T_y(h)|e satisfies the original NAE constraint.

Conjoining over all edges proves membership equivalence.
XOR with fixed y is its own inverse, hence the map is bijective.

QED.

Consequences:

- h=0 is always a repair mask;
- h=1^V is always a repair mask for constant-free NAE, corresponding to global complement;
- the number of repair masks equals the number of original models;
- Hamming distances are preserved by T_y.

## 3. Canonical-anchor and pivot slices

After the translation quotient fixes an anchor a, impose h_a=0.

Under T_y this is exactly the original model slice

z_a = y_a.

If we additionally demand that a pivot p be flipped, h_p=1, this is exactly

z_a = y_a
and
z_p != y_p.

Thus the problem

'find a global repair mask that preserves all constraints, keeps the anchor, and flips the pivot'

is not a simpler auxiliary CSP. It is an isomorphic slice of the original NAE model space.

## 4. Local relation form

For one satisfied NAE edge with local pattern t=y|e, the admissible mask relation is

R_t = {h in F2^3 : NAE(t XOR h)}.

Because t is non-monochromatic, R_t excludes exactly the complementary pair {t, t XOR 111}.

These are translated NAE relations. The translation is globally consistent because every t coordinate comes from the same model y.

This explains why local defect propagation can look simpler while the full global endpoint problem retains the original model-space structure.

## 5. Reconfiguration-graph corollary

Let G(F) be the solution graph whose vertices are models and whose edges join assignments differing in one variable.
Let G(Repair_y(F)) be defined identically for repair masks.

Because XOR with fixed y preserves Hamming distance exactly, T_y is a graph isomorphism

G(Repair_y(F)) ~= G(F).

So changing coordinates from models to repair masks does not improve single-flip reconfiguration complexity or diameter.

## 6. External source barrier

Gopalan, Kolaitis, Maneva and Papadimitriou, 'The Connectivity of Boolean Satisfiability: Computational and Structural Dichotomies', show that Positive Not-All-Equal 3-SAT is on the hard side of the solution-graph dichotomy: ST-CONN and CONN are PSPACE-complete and hard families can have exponential solution-graph diameter.

Cardinal, Demaine, Eppstein, Hearn and Winslow, 'Reconfiguration of Satisfying Assignments and Subset Sums: Easy to Find, Hard to Connect' (2018), prove PSPACE-completeness even for planar monotone NAE-3SAT reconfiguration under single-variable flips.

Therefore a generic algorithm of the form

'search through satisfying local repair moves until the desired pivot is repaired'

cannot be assumed to have a polynomially bounded path/rank on all NAE instances.

This is a route barrier only; it is not a statement about P versus NP.

## 7. Consequence for JANUS rank synthesis

The active mechanism must NOT obtain mu(y) by solving Repair_y(F), searching the solution graph, or invoking a reconfiguration oracle.

The missing object must instead be a symbolically synthesized transformer whose total action is known directly from the syntax/recognized structure and whose descent proof is universal over all models violating the canonical condition.

Admitted shape:

SYNTHESIZE(F) -> (C, mu, rho, certificate)

with polynomial synthesis and verification, such that

for every y:
  y models F and y violates C
  => mu(y) models F and rho(mu(y)) < rho(y).

The transformer may be nonlocal, but computing mu(y) for a supplied y must be polynomial and must not solve another SAT/reconfiguration instance.

## 8. Positive examples that survive the barrier

- translation stabilizer action: mu is explicit XOR by a synthesized kernel vector;
- NAE complement: mu is whole-component complement;
- BCE repair: mu is a syntactically chosen literal flip conditioned on the deleted blocked clause;
- autarky: mu extends/replaces a known partial assignment;
- affine kernel canonicalization: mu is explicit Gaussian-synthesized translation.

All of these give the action directly; none searches for a repair endpoint.

## 9. Updated gate

Freeze:

R5_E9_SYMBOLIC_NONLOCAL_DESCENT_TRANSFORMER_GATE_V1

Question:

On translation-rigid WDR survivors with positive irredundant expansion charge, can one deterministically synthesize a nonlocal transformer and a well-founded rank directly from structural data, without solving the model-relative repair-mask CSP?

Required:

- polynomial synthesis;
- polynomial per-witness action;
- polynomial universal verification certificate;
- exact model preservation on the bad region;
- strict rank descent;
- immediate or amortized Boolean-dimension drop;
- no repair-endpoint search;
- no hidden SAT/reconfiguration oracle.

## 10. Ceiling

REPAIR-MASK REPRESENTATION = EXACT BUT SELF-SIMILAR
GENERIC REPAIR-ENDPOINT SEARCH = NO NEW COMPRESSION
SINGLE-FLIP RECONFIGURATION = SOURCE-HARD IN GENERAL
SYMBOLIC NONLOCAL DESCENT TRANSFORMER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
