# R5 — Original-SCL symmetry-certified UNSAT compression and linear-treewidth atomic obstruction
Date: 2026-10-12 (Europe/Kyiv)
PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516 — DRAFT
Main not modified.

## Decision gates at beginning of this checkpoint

The entire third-ply J5/J7 GitHub matrix run completed SUCCESS:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38292987243
Individual branch statuses are NOT interchangeable with CI status:

| Original Holyer source | Initial condition | Full saturating depth-3 branch status | Inner one-ply calls | Consequence |
|---|---|---|---:|---|
| J5 / SCL90 | x0=0 | UNSAT, independently source-replayed | 70 | J5 refuted in this branch |
| J5 / SCL90 | x0=1 | UNSAT, independently source-replayed | 61 | J5 refuted in this branch |
| J7 / SCL126 | x0=0 | UNKNOWN | 251 | No UNSAT proof for this condition |
| J7 / SCL126 | x0=1 | UNKNOWN after 6 certified forces | 281 | No UNSAT proof for this condition |

Prior orbit-complete d<=2 failure for J5/J7 is recorded in
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38291137567.
Thus d(J5)=3 **for the precisely frozen saturation hierarchy**.
For J7 d>=3, and selected x0 branches of d3 are UNKNOWN; an ALL-VARIABLE
d3 barrier was NOT proved. Do not claim d(J7)>=4.

## 1. GENERAL theorem: refute positives modulo VERIFIED source automorphisms

For ANY original square/cubic/linear Positive Exact-One source F with
clauses C_0,...,C_(n-1), choose a source clause C={u,v,w}. Give explicit
variable-permutation generators g_1,...,g_t which, independently
replayed against ALL original source rows, each permute the clause
collection exactly onto itself. Let O_j be the resulting variable
orbits under the finite generated subgroup. Select a set of variables
R meeting EVERY orbit O_j that intersects C. If EACH positive
assumption F & x_r=1, r in R, has its own independently accepted
original-source UNSAT proof, then F is UNSAT.

PROOF. Any SAT witness satisfies exactly one variable x_c=1 in C.
There is r in R lying in the same group orbit as c. An authenticated
composition of the provided source automorphisms takes c to r
(or the inverse composition does; all generators are verified
permutations). Applying this composition to the witness preserves
EVERY original Exact-One source clause and yields x_r=1, which is
ruled out by the corresponding replayed conditional UNSAT proof.
Contradiction.

Proof verification is polynomial in n, total explicitly supplied
generator size and length of conditional certificates. There are at
most THREE distinct orbits hitting a triple C, so at most three
positive conditional UNSAT certificates need be retained. For
a Holyer edge-clause the three edge-colour variables form ONE
S3-colour orbit, hence ONE condition F & x_(e,0)=1 suffices.
This is a valid ALL-SCL certificate *checker*, not a universal
algorithm to CONSTRUCT all needed conditional refutations.

Implementation:
`experiments/r5_universal_source_symmetry_positive_orbit_unsat.py`
CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38295835963
SUCCESS on source HEAD `c7dd137e3f5c61a9ba6982cb1828c5c3c7eb3b02`.
- J5 UNSAT: ONE original positive-literal x0=1 refutation,
  61 source-audited inner calls and only 7 certificate events;
  no need to also regenerate x0=0.
- Deliberately forged same-size original automorphism rejected.
- Uncovered Exact-One literal orbit rejected, even with genuine
  refutation for another literal.
- Deliberately forged nested conditional UNSAT proof rejected.
- Independent SAT K4 validates source S3 but does NOT acquire
  any invented UNSAT proof.

External literature: Bogaerts–Gocht–McCreesh–Nordström, 2022,
Certified Symmetry and Dominance Breaking for Combinatorial
Optimisation (https://doi.org/10.1609/aaai.v36i4.20283).
This is a local JANUS source-indexed application of the general
well-known idea of proof-certified symmetry, not a claim that the
underlying symmetry-breaking concept was newly invented.

## 2. GENERAL structural theorem: original Holyer Tanner contains G as minor

For ANY finite connected simple cubic graph G=(V,E), construct the
original authenticated Holyer legal n-by-n SCL source A_G.
There is one Boolean variable X_(e,c) for each edge e and
colour c in {0,1,2}; the source Exact-One rows are:
- for each edge e: R_e=ExactOne(X_(e,0),X_(e,1),X_(e,2));
- for each graph vertex v and colour c:
  R_(v,c)=ExactOne(X_(e1,c),X_(e2,c),X_(e3,c)),
  where e1,e2,e3 meet v.

In the original bipartite Tanner graph, delete all row/variable
nodes EXCEPT row R_(v,0) for each v and variable X_(e,0)
for each e. Each X_(uv,0) now has exactly two neighbours,
R_(u,0) and R_(v,0), and these internal variable nodes are all
distinct. The retained induced graph is exactly the one-edge
subdivision of the original cubic graph G.

Hence `G is a topological minor of Tanner(A_G)`, and by
minor-monotonicity of treewidth:

  tw(Tanner(A_G)) >= tw(G).

For cubic |V|=v, |E|=3v/2 and the ORIGINAL SCL size
n=3|E|=9v/2. There exist infinite families of finite simple
connected cubic expanders G_v. Expanders possess linear-size
balanced vertex separators and therefore
`tw(G_v)=Omega(v)`, hence the legal original Holyer SCL
Tanner family satisfies:

  tw(Tanner(A_(G_v))) = Omega(n).

This result decisively refutes the attempted universal assertion
that every legal SCL source has constant or O(log n) Tanner
treewidth. Standard 2^O(tw) / 3^O(tw) boundary-signature DP
thus receives NO polynomial all-input guarantee from the
width parameter alone.

External existence/width evidence:
- M. Morgenstern (1994), Existence and Explicit Constructions
  of (q+1)-Regular Ramanujan Graphs for Every Prime Power q,
  JCTB 62 (1994) 44–62, DOI: 10.1006/jctb.1994.1054;
  its q=2 specialization provides degree-3 expander families.
- Böttcher, Pruessmann, Taraz, Würfl (2010),
  Bandwidth, Expansion, Treewidth, Separators and
  Universality for Bounded-Degree Graphs,
  Eur. J. Comb. 31 (2010), 1217–1227,
  DOI: 10.1016/j.ejc.2009.10.010.

New source-independent finite extractor/verifier:
`experiments/r5_universal_holyer_tanner_linear_treewidth_obstruction.py`
CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38296184052
SUCCESS. Reconstructs source-authenticated Tanner nodes from
canonically SORTED original rows (not guessed indices),
finds the exact one-subdivision of the original G for
K4, K33, cube, Petersen, J5, J7; rejects same-size
counterfeit graph and modified original source incidence.
The earlier initial CI #38296077277 FAILED because a
pre-sorting row index was improperly assumed; the corrected
source-content-based row index passed CI. Both immutable
workflow histories remain visible.

IMPORTANT LIMITATION: High treewidth does NOT prove exponential
worst-case runtime for arbitrary algorithms, does NOT rule
out implicit algebraic summaries, and does NOT prove P != NP.
The transfer proof on the odd flower family is an example of
constant-state compression despite a graph having nonzero
treewidth; the expander theorem rules out ONLY a universal
SMALL-WIDTH justification, not every possible compression.

## 3. What a real universal theorem still needs

The new all-input symmetry-discharge verifier and the exact
graph-minor obstruction sharpen the remaining proof obligation:

Find a deterministic uniform n^C-bit-time algorithm that for
EVERY legal SCL (including atomic high-treewidth/low-symmetry
instances) either constructs a completely original-checked
SAT witness or produces an original-source UNSAT certificate.

A universal 'small separator' or '8 state quotient for every
atom' is demonstrably insufficient without a global
representation theorem with POLYNOMIAL-TIME CONSTRUCTION.
An exponential-size state space could potentially be
implicitly compressed by circuits/algebra; NO lower bound
against such algorithms has been obtained.

For any proposed implicit signature method, require:
1. POLYNOMIAL encoding length for all original SCL inputs;
2. POLYNOMIAL construction time of leaf/interior signatures,
   including irreducible 3-edge-connected Tanner atoms;
3. polynomial source-proof-preserving composition;
4. polynomial satisfiable-witness extraction and independently
   checkable negative acceptance;
5. one UNIFORM polynomial n^C bit bound across all instances.

A result missing any requirement is an incomplete expert, not
the universal `SolveLinearCubicXSAT`.

GATES:
```
J5_MIN_DEPTH_FROZEN_HIERARCHY = 3 PROVED
J7_MIN_DEPTH_FROZEN_HIERARCHY = >=3; D3_X0_BRANCHES_UNKNOWN
ALL_SCL_SOURCE_SYMMETRY_ORBIT_UNSAT_RULE = PROVED
J5_SINGLE_POSITIVE_SOURCE_REFUTATION = CI_SUCCESS
HOLYER_G_TO_TANNER_TOPOLOGICAL_MINOR = PROVED
INFINITE_LEGAL_SCL_LINEAR_TANNER_TREEWIDTH = PROVED_USING_PUBLISHED_EXPANDERS
UNIFORM_LOG_TANNER_TREEWIDTH_ALL_SCL = REFUTED
GENERIC_POLYNOMIAL_SIGNATURE_CONSTRUCTION = OPEN
SolveLinearCubicXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
