# R5 — GF(3) Boolean polynomial-calculus proof frontier on all-SCL source atoms

Checkpoint date: 2026-10-13 Europe/Kyiv
Research PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516 (DRAFT).
Starting source HEAD: `807afb314016843f7716fab132ec24155f0ee779`.
Main not changed.

## PRIMARY SCIENTIFIC CONTRACT

The only universal goal is a deterministic polynomial BIT-time sound+complete `SolveLinearCubicXSAT(F)` on EVERY square+cubic+linear Positive Exact-One original source, returning original SAT witness or correct UNSAT. The universal `LoopZeroTest`, a degree-bounded complete source proof system, and P=NP remain UNPROVED.

The present checkpoint is a **concrete algebraic proof attack**:
- it upgrades prior source-native high-girth Fano modular-cut refutations to an EXPLICIT DEGREE-TWO polynomial identity;
- constructs a genuinely source-authenticated DEGREE-TWO DUAL pseudo-moment for UNSAT Petersen, proving the frozen degree-two method is INCOMPLETE;
- constructs a fully independent ORIGINAL-SOURCE DEGREE-THREE certificate for Petersen;
- honestly stress-tests but DOES NOT prove universal degree-three completeness on 16 deterministic random legal SCL27 UNSAT sources.

Every certificate has exactly scoped source premises, with finite adversarial replay.

## 1. Algebraic source encoding (over F3) and proof-system rules

For each ORIGINAL SCL source row C_i={a,b,c}, set
```
E_i(x)= x_a+x_b+x_c-1  ∈ F3[x_0,..,x_(n-1)].
```
For each original Boolean variable x_j, Boolean generator
```
B_j(x)=x_j²-x_j.
```
On x_j∈{0,1}, 0≤x_a+x_b+x_c≤3, so E_i≡0 (mod3) iff the ORIGINAL Exact-One row is satisfied: possible integer row counts are 0,1,2,3, and only 1 is 1 modulo3.

Thus F3 algebraic UNSAT refutations using ORIGINAL E_i and B_j are SOUND for original SCL.

For fixed d, consider the explicitly defined proof subspace in the Boolean quotient F3[x]/(B_j):
```
V_d(F) = Span_F3{ multilinear_reduce( E_i x_M )
                    : original source row i, |M|≤d-1 }.
```
An exact source refutation `1∈V_d` means `1=Σ c_(i,M) E_i x_M` modulo Boolean generators and F3. Because all products have total degree ≤d and Boolean reductions can be realized using degree≤d idempotency multiples, this is an ordinary bounded-degree Nullstellensatz/Boolean polynomial-calculus refutation.

Dimension of all multilinear monomials ≤d is Σ_(j=0)^d C(n,j); for FIXED d, exact source Gaussian membership testing and a dual certificate are polynomial. If the required d grows with n, this argument does NOT give a uniform n^C solver.

When `1∉V_d`, a DUAL linear functional
```
y(1)=1,  y(E_i x_M)=0 for all original i, |M|≤d-1
```
is an independently checkable certificate that the FROZEN proof system has no degree-d refutation. It is NOT an original SAT witness.

Both sides can be verified using ORIGINAL source IDs and integer coefficients only (no floating point or inferred answer).

## 2. ALL cyclic three-block modular-cut UNSAT Fano towers have degree-TWO certificates

Take ANY connected legal SCL source with m variables, m mod3=r∈{1,2}, and the three-copy cyclic Tanner rewire of the prior checkpoint. Denote by b_i the ORIGINAL selected variable at the cut in copy i, i mod3. Sum original source clause generators over each block i. Since every in-block original variable appears three times except its cut variable twice, and the next block's cut variable enters once:

```
F_i = Σ_(original rows in block i) E_row
    = b_(i+1) - b_i - r   over F3.
```

Let `g(b)=b²-b`. For i=0,1 define `c=2r mod3` and

```
T_i = g(b_(i+1))-g(b_i)
       - F_i*(b_(i+1)+b_i-1+r).
```

Expansion in the ORIGINAL field proves the EXACT polynomial identity

```
T_i = (2r)b_i + r(r-1)   over F3.
```

Subtract i=0 from i=1 and eliminate b_1−b_0 using F_0:

```
1 = r^(-1)*[(2r)^(-1)*(T_1-T_0)-F_0]   over F3.
```

Every term on the RHS belongs to the original-source ideal:
F_i sums ORIGINAL linear Exact-One equations, with coefficient of degree ≤1;
g(b_i) are ORIGINAL Boolean generators; no coefficient exceeds degree1 when multiplying E_i.
Hence a literal degree≤2 Nullstellensatz refutation of the ORIGINAL SCL source, with O(n) clause-generator occurrences (for 3m-size source).

This theorem is source-indexed and holds at every Fano homology cover tower level, even though its girth grows and global n=3m is divisible by3.

[CI #38327722986 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38327722986):
- all two residue cases r=1,2 checked as exact sparse F3 degree2 polynomial identities;
- original Fano7 linear Ax=1 over F3 INCONSISTENT (expected n%3);
- CONNECTED original UNSAT SCL21 from triple Fano7: linear Ax=1 over F3 CONSISTENT, exact source rank20 and a pseudowitness with some entries 2; nevertheless degree2 refutation exists;
- matched connected SAT SCL21 (from G10/G11) also linear GF3 CONSISTENT rank19, actual source #SAT=2;
- high-girth connected SCL5376 original UNSAT certificate independently source-replayed using 3584 original row generators and three Boolean generators;
- forged original source metadata correctly rejected.

**Crucial epistemic correction:** high girth and a divisible source size do NOT automatically create a hard test for polynomial-degree algebra. The earlier triple-Fano family is efficiently refutable in degree2. A new harder atom is necessary to evaluate universal algebraic methods.

Source: `experiments/r5_universal_triple_cut_degree2_gf3_certificate.py`.

## 3. COMPLETE frozen degree-2 Boolean polynomial-calculus audits

Proof system V_2 includes each original E_i and E_i*x_j, n(n+1) generators, in dimension 1+n+C(n,2) over F3.

The independent exact row-span evaluator carries:
- a source-original sparse Gaussian certificate for `1∈V_2`, verified by REBUILDING the original source polynomials and checking literal identity1;
- if `1∉V_2`, an independently original-source-verified DUAL linear functional y satisfying y(1)=1 and annihilating EVERY allowed original E_i*x_j. No inference about SAT is made.

[CI #38327964249 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38327964249):

| Original source | Ground truth | Frozen V2 conclusion | Verified detail |
|---|---|---|---|
| Fano7 | UNSAT | TRUE UNSAT refutation | 7 generator terms |
| triple-Fano21 (3|n) | UNSAT | TRUE UNSAT refutation | 20 terms |
| E61 UNSAT12 (non-Holyer) | UNSAT | TRUE UNSAT refutation | 25 terms |
| Petersen SCL45 | UNSAT | NO degree-2 refutation | source-dual y support 454; ambient dim 1036, rank 1015 |
| G10/G11 SCL21 | SAT count2 | No degree-2 refutation | rank230 |
| K4 SCL18 | SAT count6 | No degree-2 refutation | rank166 |
| K3,3 SCL27 | SAT count12 | No degree-2 refutation | rank361 |
| E61 SAT12 | SAT count1 | No degree-2 refutation | rank78 |

**Sharp rigor:** The Petersen dual y is a VALID independently original-source-checkable CERTIFICATE that the constant polynomial1 lies OUTSIDE V2 despite original SCL45 being UNSAT (source-verified snark). This STRICTLY REFUTES the proposal `V_2 COMPLETE FOR ALL LEGAL SCL`.

Source: `experiments/r5_universal_gf3_boolean_degree2_pc_frontier.py`.

## 4. Petersen SCL45 actually has a valid original-source DEGREE-3 refutation

For V3 use all E_i*x_M for |M|≤2, reduced modulo Boolean x²=x. The ambient multilinear space has dim Σ_(j≤3)C(n,j). For n=45, its dimension is 15,226; the full generator set has 45*(1+45+C(45,2))=46,620 elements.

First completed exact source row-span probe:
[#38328119136 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38328119136)
found constant1 in degree-three span for Petersen SCL45 after 40,407 source generators and 7,349,891 arithmetic cell updates. This is just a candidate until coefficients are independently source-verified.

An INDEPENDENT proof-producing pass stores a DAG of ORIGINAL row/multiplier generator reductions, unwinds it into coefficients `c_(i,M)`, and then a SEPARATE source-only checker reconstructs the complete identity `1=Σ c_(i,M)E_i x_M` modulo Boolean equations and F3. It rejects a deliberately falsified coefficient.

[#38328253626 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38328253626):
- TRIPLE-FANO21: VALID degree-three (not minimal) original-source UNSAT certificate, 20 nonzero source generator terms;
- PETERSEN SCL45: VALID original-source DEGREE THREE UNSAT certificate with EXACTLY 1337 nonzero generator terms, independently verified;
- forged Petersen degree-three coefficient rejected;
- V2 source-dual still correctly prevents degree-two refutation.

This is a scientifically SOUND finite source fact: Petersen requires degree at least3 in frozen V_d and admits degree3. It is NOT a uniform all-SCL degree upper bound.

Sources:
`experiments/r5_universal_gf3_boolean_degree3_pc_probe.py`,
`experiments/r5_universal_gf3_degree3_petersen_source_certificate.py`.

## 5. Deterministic adversarial search over legal SCL27, not a proof of universal d=3

Start from ORIGINAL source-valid K3,3/SCL27 and make 50 accepted random Tanner 2-switches preserving every SCL row/column degree and C4-freeness, fixed RNG seed20261013. Generate 16 connected candidate sources. A separate exponential exact-cover solver checks ORIGINAL row satisfiability; if UNSAT, a fully replayable DAG of uncovered original row sets certifies every exhaustive branch is covered, with no zero-uncovered leaf. The source Boolean truth is not inferred from any algebraic relaxation.

[#38328478919 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38328478919):
- 16 connected, original legal, source-verified SCL27 tested;
- all 16 are UNSAT, with small independently replayed exact-cover UNSAT DAGs of 8–27 nodes;
- all 16 have constant1 in the frozen V3 span (candidate refutation; NOT each independently coefficient-unwound), so NO degree3-resistant source found by this finite search;
- no claim whatsoever about other SCL sources or a universal V3 theorem.

Code:
`experiments/r5_universal_gf3_degree3_adversarial_scl27_search.py`.

**IMPORTANT:** Source-unverified / not-yet-unwound degree3 constant candidates in this search must NOT be reported as completed source certificates. The independently certified degree3 Petersen and triple-Fano proofs remain the authoritative proven positives.

## 6. Published mathematical context and transfer caveat

Known separate research points to serious possible obstacles for a GLOBAL FIXED polynomial-calculus degree theorem:
- Lauria–Nordström, *Graph Colouring is Hard for Algorithms Based on Hilbert's Nullstellensatz and Gröbner Bases*, CCC 2017, DOI 10.4230/LIPIcs.CCC.2017.2: bounded-degree graph k-colouring instances requiring linear polynomial-calculus degree in their specified ORIGINAL graph-colouring encoding.
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2017.2
- Conneryd, de Rezende, Nordström, Pang, Risse, *Graph Colouring Is Hard on Average for Polynomial Calculus and Nullstellensatz*, FOCS 2023, DOI 10.1109/FOCS57990.2023.00007; arXiv:2503.17022 updated manuscript: linear proof-degree lower bounds on suitable sparse random graph colourability sources.
  https://arxiv.org/abs/2503.17022

These theorems are **NOT proven to apply automatically to our native square/cubic/linear SCL Exact-One encoding**. An explicit reduction preserving the original source legality AND transferring polynomial-calculus degree lower bounds with constant blow-up/degree is necessary before importing any such unconditional proof lower bound. Do NOT cite generic graph-colouring degree bounds as a proved all-SCL degree lower bound.

Similarly, this checkpoint's exact SOURCE certificates do not establish any new `P=NP` result, nor unconditional `P≠NP`.

## 7. THE NEXT ACTUAL POSITIVE GLOBAL THEOREM

One must construct a truly uniform n^C-bit-time algorithm for exact ZERO/NONZERO of the signed-loop Holant (equivalently original positive Exact-One SCL) on EVERY legal source, not only a verifier of UNSAT when a low-degree certificate exists.

Any proposed `V_d` polynomial-calculus solver requires a GLOBAL theorem:
```
∃constant d such that FOR EVERY legal source UNSAT F,
  1 ∈ V_d(F)
```
and polynomial-size membership testing/certificate extraction, together with the earlier proven original source pin compiler for SAT witness recovery. No such all-input d bound is constructed. The existing source-near graph-colouring proof-complexity literature motivates PARTICULAR SCL-preserving lower-bound stress tests before attempting to assert it.

More generally, some other non-flat implicit algebra may decide all SCL in polynomial time even if no fixed-degree V_d theorem holds. Our restricted proof results cannot exclude such methods.

STATUS:
```
TRIPLE_FANO_HIGH_GIRTH_SOURCE_GF3_DEGREE2_UNSAT = PROVED
SAME_SIZE_SAT21_UNSAT21_LINEAR_GF3_CONSISTENT = PROVED
E61_UNSAT12_SOURCE_GF3_DEGREE2_UNSAT = PROVED
PETERSEN_SCL45_GF3_DEGREE2_DUAL_NO_REFUTATION = PROVED
PETERSEN_SCL45_GF3_DEGREE3_SOURCE_UNSAT = PROVED
SCL27_RANDOM16_DEGREE3_CANDIDATES = OBSERVED_ONLY
ALL_SCL_DEGREE3_COMPLETE = NOT_PROVED
POLYNOMIAL_GENERAL_LOOPZERO_TEST = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
