# R5 — Rigorous loop-compression proof obligations: infinite high-girth UNSAT family and all-SCL integer gap

Date: 2026-10-13 (Europe/Kyiv).
Parent: PR #516 DRAFT on `research/r5-cubic-flow-smith-pair-20261011`.
Starting verified parent HEAD: `70285ba0a3ccad18298270baa4e55c71e3d1ef0f`.
**Scientific status:** the universal deterministic polynomial-bit-time `SolveLinearCubicXSAT` remains NOT CONSTRUCTED. `P_VS_NP=OPEN`. This checkpoint gives two exact all-input/family mathematical theorems, neither a P=NP proof.

## 0. PROOF GOAL

Previous source-verified R5 work obtains a polynomially built n-node, 2n-edge rank-two T4 matched quotient for EVERY valid square/linear/cubic Positive Exact-One source. The quotient's EXACT partition function Z is #SAT of the ORIGINAL rows. An exact generalized-loop expansion yields

```
  L(F) = Z(F)/Z_B(F)
       = sum_(S subset of E(Q)) 2^{-|S|}
           product_(v in V(Q)) M_v(S∩delta(v)),
  M=(1,0,0,-1,0,-1,-1,2,0,-1,-1,2,2,-1,-1,0).
```

Only loop-node degrees 0,2,3 contribute; source-backed CI
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38310593356
is SUCCESS at the previous checkpoint HEAD.

The M-table is an INSTANCE-SPECIFIC specialization of the
published generalized-loop / belief-propagation series, NOT a
claim that the general loop calculus is a new invention:
Chertkov & Chernyak (2006), Phys. Rev. E 73, 065102,
DOI https://doi.org/10.1103/PhysRevE.73.065102;
and detailed loop series J. Stat. Mech. P06009,
https://doi.org/10.1088/1742-5468/2006/06/P06009.

A correct universal solver must compute exact Z=0/nonzero
and witness / independently checked negative acceptance with
a uniform all-input n^C bit bound. Loop expansion alone
is not such an algorithm.

## 1. Infinite EXPLICIT UNSAT SCL with unbounded Tanner and quotient girth

**BASE.** Original Fano7 source `cyclic(7)`, n0=7. Its bipartite
incidence Tanner graph H0 has 14 nodes, 21 edges, cubic,
connected, C4-free, girth=6. Its n0=7 is nondivisible by3,
so it is UNSAT by the original-source integer identity:
```
If every source clause has sum of chosen literals 1,
then n=sum_rows1=3*sum_variables x. If 3∤n, impossible.
```

**CONSTRUCTIVE VOLTAGE LIFT.** For ANY current connected
cubic Tanner graph Hj with nj original row nodes and nj
variable nodes, pick a spanning tree T. There are
```
r=|E(Hj)|-|V(Hj)|+1=3nj-2nj+1=nj+1
```
off-tree edges. Label every off-tree edge independently
by one of the r standard basis vectors of the group
G=F2^r; label the tree edges by 0.

Construct the regular cover H_(j+1) with vertices (v,g)
for v in Hj and g in G. An old edge u--v labelled delta
lifts to all the edges (u,g)--(v,g+delta).
There are |G|=2^r sheets. It is connected because each
fundamental base cycle corresponding to an off-tree edge
has voltage exactly one generator of F2^r. It remains
3-regular bipartite, with no C4, and its original
source has n_(j+1)=nj*2^r rows and columns.

**STRICT GIRTH THEOREM.** If old girth is g, a cycle
in the cover of length ≤g projects to a closed
nonbacktracking base walk of length ≤g. Because base
girth is g, this projection must be a simple base
cycle of exactly length g. A simple cycle of the base
contains at least one off-tree edge, traversed
exactly once, so its independent chord-basis voltage
sum is NONZERO. Hence it CANNOT lift to a closed
cycle, contradiction. Thus girth(H_(j+1))>girth(Hj).
Girth is integer and strictly increases, so it
diverges along the explicitly defined tower.

**ALL TOWER INPUTS ARE LEGAL UNSAT.** The sheet counts
are powers of two. Starting from n0=7 not divisible
by3, every nj=7*(power of two) stays nondivisible
by3, so every original SCL source is UNSAT with the
same authenticated one-line integer certificate.
Thus this is an infinite constructive high-girth
source family, not merely existential random graphs.

**MATCHED QUOTIENT GIRTH.** Contract ANY perfect Tanner
matching (Hall), obtaining the n_j-cell quartic Qj.
A simple k-cycle in Qj pulls back to a closed
nonbacktracking Tanner walk with k unmatched edges
and at most k matched edges; hence H_j has a cycle
of length ≤2k. Therefore
```
girth(Qj) >= girth(Hj)/2
```
and the quotient girth also diverges for EVERY
source-valid choice of matching.

**FIXED-LOOP TRUNCATION REFUTED.** Every nonempty
edge-selected subgraph contributing to L has
vertex degrees 2 or3 on its occupied vertices:
all degree1 and degree4 local moments vanish.
A nonempty finite graph of minimum occupied degree≥2
contains a simple cycle, so its number of selected
edges is at least girth(Qj).
For ANY FIXED integer cutoff ell, choose a tower
level with girth(Qj)>ell. Then the signed generalized
loop series truncated to |S|≤ell contains only the
EMPTY subset contribution `L_ell=1`, yet the TRUE
exact loop correction `L=Z/Z_B=0` because source is
UNSAT. Hence fixed-size truncation cannot serve
as a complete all-input SAT/UNSAT test.

This no-go does NOT rule out a loop cutoff that grows
with n, implicit polynomial compression, or a
completely different global algorithm. We have NOT
proved exponential lower bounds on general algorithms.

**INDEPENDENT GITHUB CI.**
`experiments/r5_universal_loop_high_girth_fano_homology_cover_nogo.py`,
`.github/workflows/r5-fano-homology-loop-cutoff-gate.yml`.
[#38312460448 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38312460448)
at `a9169b34d565eab28161be58fa457d4057d006bc`.

Finite original source case: first Fano homology cover has
r=8 chord basis bits, 256 sheets and n=7*256=1792
original SCL variables. Exact source validator confirms
square/cubic/linear source, n mod3 obstruction, source
Tanner girth >9 (no cycle ≤9), and ANY-CHECKED constructed
rank2 quotient has no cycle ≤5. Thus
```
SOURCE n=1792 UNSAT;
EXACT signed loop correction = 0;
TRUNCATED to ≤5 selected edges = 1 (FALSE POSITIVE).
```
The second cover has 2^(1792+1) sheets and was NOT
materialized; the unbounded tower is a symbolic all-level
proof, not an infeasible memory attempt.

## 2. Global integer divisibility of the signed loop numerator

For EVERY legal SCL with n=3k, original exact
solutions satisfy exactly k= n/3 true variables.
The previous Bethe normalization is an explicit
positive rational number for n divisible3:
```
Z_B=(16/27)^k = 2^(4k) / 3^(3k).
```

The loop correction L is a rational with denominator
dividing 2^(2n), since Q has exactly 2n edges and
every local moment M is an INTEGER.
Define the exactly integer signed loop numerator
```
K(F)=2^(2n)*L(F)
    = sum_(S subset E(Q)) 2^(2n-|S|) product_v M_v(...).
```
As Z=Z_B L and n=3k,
```
Z = [2^(4k)/3^(3k)] [K/2^(6k)]
  = K / [2^(2k)*3^n].
```

**THEOREM (ALL LEGAL SCL):**
```
If 3|n,     K(F)=2^(2n/3) 3^n * #SAT(F);
if 3∤n,     #SAT(F)=0, L(F)=K(F)=0.
```

The first line implies K is divisible by
`2^(2k)3^n` with an exactly integer quotient.
This is a global 2-adic and 3-adic cancellation
identity valid for ALL sources; it does not
supply an efficient algorithm to compute K.

For an independent, direct and transparent derivation
of the loop normalization (no assumed BP miracle):
at each matched T4 cell put the uniform 1/3
probability on its 3 allowed configurations.
Each port marginal is pi(0)=2/3,pi(1)=1/3 and
the edge equality resolves exactly as
```
delta(a,b)/pi(a)
  = 1 + psi(a)psi(b)/2, psi(0)=-1,psi(1)=2.
```
In a globally satisfying quotient assignment x,
there are k=n/3 selected E4 cells and the source
defines exactly 2k=2n/3 TRUE quotient wire bits
(each selected variable appears twice outside the
contracted matching). Thus every surviving
assignment has the SAME equality/edge denominator
```
product_e pi(x_e)^(-1)
 =(3/2)^(2n-2k) * 3^(2k)
 = 3^(2n)/2^(4k).
```
Combining this with the n factors of 1/3 in the
product local law gives `3^n/2^(4k)=1/Z_B`,
and proves `L=Z/Z_B` exactly, including
cases when Z=0. If 3∤n there simply are no
surviving assignments on either side.

## 3. A striking exact-output GAP and approximation theorem

For n=3k:
```
L(F)=(27/16)^k * Z(F).
```
Thus if UNSAT then L=0. If SAT, since Z is an
integer at least 1, `L>= (27/16)^k>1`.
Although L consists of exponentially many
positive and negative signed summands, its
POSSIBLE OUTPUTS are quantized in a rational
lattice with spacing `(27/16)^k`.

**THEOREM (ALL SCL).** Suppose a deterministic uniform
algorithm runs in time n^C and for EVERY valid
SCL input with n=3k returns a rational estimate
Lhat satisfying

```
abs(Lhat-L) < 0.5 * (27/16)^k.
```

Multiplying Lhat by `Z_B=(16/27)^k` gives a
rational within less than 1/2 of the ORIGINAL
integer solution count Z. Hence rounding exactly
recovers Z, and a fortiori decides this NP-complete
SCL SAT class in deterministic polynomial time,
implying P=NP.

The tolerance grows exponentially with k!
Even such an exponentially coarse additive
estimate of the NORMALIZED signed loop sum
would be enough to recover the exact answer,
due to the output lattice gap.

This is a reduction/necessary proof obligation,
NOT a construction of that estimator, NOR
an unconditional impossibility proof.
Do not infer P!=NP from the absence of
such an algorithm.

**SOURCE-AUDITED FINITE CI:**
`experiments/r5_universal_loop_signed_integer_gap_certificate.py`
`.github/workflows/r5-loop-integer-gap-gate.yml`
Initial failed workflow #38312660540 is preserved:
it contained a reversed normalization test
`D=2^(2n)*Z_B` instead of the proven
`D=2^(2n)/Z_B`. Corrected source and rerun:
[#38312712282 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38312712282)
at `462a780dbbbea9650fa31d60ed6a5f7dfe7f9fc5`.

Exact signed loop enumerator, ORIGINAL source counts
and rational proof checks:
- Fano7 n=7: original UNSAT and signed K=0;
- E61 SAT12: Z=1, K=136048896=2^8*3^12,
  L=531441/65536;
- E61 UNSAT12: Z=0, K=0;
- independent rational rounding tests at
  ±(27/16)^4/3 reproduce the exact original
  count for both n=12 sources.

## 4. Published complexity boundaries

The general R5 exact generalized-loop technique is
a source-specialized version of well-known loop calculus
(Chertkov–Chernyak 2006), not a new literature-level
invention of the method.

Published #P-hardness of counting Holant
`([0,1,0,0]|Equality3)` on 3-regular bipartite
graphs is established in Austen Z. Fan and
Jin-Yi Cai, *Dichotomy Result on 3-Regular
Bipartite Non-negative Functions*,
Theoretical Computer Science 949 (2023):113745,
DOI https://doi.org/10.1016/j.tcs.2023.113745,
in particular Lemma 12.
Their input promise is 3-regular bipartite; it
does not AUTOMATICALLY prove counting hardness
under the EXTRA C4-free/linear restriction.
Our all-SCL NP-hard DECISION claim is instead
grounded in the separately source-validated
Holyer cubic graph 3-edge-colouring reduction.
Do not conflate counting and decision hardness.

## 5. The only meaningful universal successor

The new proofs rule out:
- any SAT criterion that truncates loop correction
  at a fixed selected-edge cardinality independent of n;
- interpreting local polynomial source certificate
  size or the rational gap as proof that the giant
  signed cancellation sum can be evaluated quickly;
- mistaking constant-precision / coarse numerical
  approximations without a proved all-source guarantee
  for SAT/UNSAT certificates.

The remaining universal positive theorem requires
an explicitly constructible UNIFORM polynomial-size
boundary-signature/cancellation algebra C:
  (A) closed under arbitrary source-authenticated
      rank2 quartic Q graph composition, including
      connected large-girth/high-genus/high-width atoms;
  (B) every intermediate encoding length <=n^C
      for one universal C;
  (C) all local updates and exact zero/nonzero
      tests worst-case n^C BIT time;
  (D) sound source SAT-witness extraction or
      independently verifiable UNSAT output for
      EVERY original SCL instance.

This is still OPEN. Replacing signed-loop subset
enumeration by an equivalent NP-complete predicate
is NOT progress towards satisfying A-D.

GATES:
```
FANO_HOMOLOGY_2GROUP_UNSAT_COVER_TOWER = PROVED
UNBOUNDED_GIRTH_ORIGINAL_AND_RANK2_QUOTIENT = PROVED
EVERY_FIXED_LENGTH_GENERALIZED_LOOP_CUTOFF = REFUTED
FIRST_COVER_SCL1792_FALSE_POSITIVE_THROUGH_5 = CI_SUCCESS
ALL_SCL_SIGNED_LOOP_K_DIVISIBLE_2POW2K_TIMES_3POWN = PROVED
ALL_SCL_NORMALIZED_SIGNED_LOOP_OUTPUT_LATTICE_GAP = PROVED
POLY_ADDITIVE_ESTIMATOR_BELOW_HALF_GAP_IMPLIES_P_EQUALS_NP = PROVED
ALL_SCL_POLY_IMPLICIT_LOOP_SUM_EVALUATION = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
