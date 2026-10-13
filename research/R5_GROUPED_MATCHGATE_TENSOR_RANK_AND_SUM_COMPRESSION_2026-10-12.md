# R5 — Exact two/four-node grouped Holant tensors: rank-rigidity barriers AND constructive matchgate-sum compression

Date: 2026-10-12, Europe/Kyiv.
Parent: PR #516, research branch `research/r5-cubic-flow-smith-pair-20261011`.
Previously checked HEAD: `76c066accb0794c594b4da3974999dacf42db13c`.
Do NOT merge on finite results; main remains unchanged.

## Ultimate theorem gate

Build ONE uniform polynomial-bit-time `SolveLinearCubicXSAT` which on EVERY legal square+cubic+linear Positive Exact-One source returns independently original-checked SAT+witness or original-source-proved UNSAT. This remains NOT CONSTRUCTED. P vs NP OPEN.

The new work is BOTH a verified obstruction to naive Pfaffian grouping and a genuine compact exact *local* decomposition as sums of valid matchgate signatures. Neither implies polynomial contraction of arbitrary SCL inputs.

## 1. Native TWO-node source cell

Start with any incidence of an ORIGINAL SCL Tanner row W=ExactOne3 and column GHZ=Equality3. Contract their common binary Tanner wire. The four remaining boundary legs are ordered (p,q,u,v), two row legs followed by two column legs. Exact contraction of original 0/1 tensors yields

```
 T4(p,q,u,v) = sum_z W(p,q,z) GHZ(z,u,v)
             = [p+q+u=1] [u=v]
             = |1000> + |0100> + |0011>.
```

Each source row/variable has degree3, and the original SCL linearity excludes parallel Tanner incidences, so this is the SAME native two-node tensor for EVERY legal source.

There are exactly three 2|2 bipartitions of four legs. Independent rational Gaussian elimination shows the three flattening ranks:

```
  12|34 : rank 2
  13|24 : rank 3
  14|23 : rank 3
```

Each invertible separate 2x2 basis on the four external legs sends a flattening M to `(B_i tensor B_j) M (B_k tensor B_l)^T`. This preserves its rank exactly. Reordering external legs only permutes the three bipartitions.

For an ordinary arity4 matchgate signature S, matchgate parity + the four-leg Grassmann-Plücker identity imply the TWO noncrossing 2|2 flattenings have rank in {0,1,2,4}, never 3. In the even branch, for split 12|34 its two parity blocks E,O have determinants `det(E)+det(O)=MGI_even=0`; thus either both have rank2 (total4) or both have rank<=1 (total<=2). The odd branch obeys the same condition with `-MGI_odd=det(E)+det(O)`. A cyclic shift of the four legs gives the second noncrossing split. Every cyclic order chooses TWO out of the THREE pair partitions as noncrossing, and T4 has TWO rank3 partitions. Therefore one noncrossing rank3 obstruction remains for EVERY order and for EVERY invertible boundary basis.

THEOREM: the native grouped W--GHZ TWO-node tensor is NEVER locally-GL2-equivalent to one standard arity4 matchgate, over characteristic zero.

Executable:
`experiments/r5_universal_grouped_two_node_matchgate_flatten_rank_nogo.py`
CI https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38298404026 — SUCCESS at commit `a000fdb45e46b78d77ecb5e563597566fd999c41`.
- Source cells reconstructed for Fano7, K4/SCL18, K3,3/SCL27, Petersen/SCL45.
- 800 exact controlled arity4 matchgate identity instances.
- All 24 external wire orders.
- 625 independent invertible 4-wire basis assignments.

## 2. Native FOUR-node path source cell (new stronger grouping)

EVERY legal SCL Tanner graph contains a four-node induced alternating path
`W0 -- GHZ0 -- W1 -- GHZ1`:
pick an original row r0, a variable v0 in it, another distinct row r1 containing v0 (column degree3), and a different variable v1 in r1. Source LINEARITY proves v1 is not in r0 (otherwise two source rows would share two distinct columns). Thus among these four nodes there are exactly three internal incidence wires, with six remaining external wires.

With the canonical boundary order (p,q,s,t,u,v), exact contraction gives

```
T6(p,q,s,t,u,v)
    = sum_(x,y,z) W(p,q,x) GHZ(x,s,y) W(y,t,z) GHZ(z,u,v)
    = [p+q+s=1] [s+t+u=1] [u=v].
```

There are exactly FIVE nonzero binary boundary entries, all equal to 1. For 3|3 flattening pairs, normalize the left side to contain leg 0. The following is the COMPLETE exact rank table:

| Left legs | Rank |
|---|---:|
| 012 | 2 |
| 013 | 3 |
| 014 | 3 |
| 015 | 3 |
| 023 | 4 |
| 024 | 5 |
| 025 | 5 |
| 034 | 5 |
| 035 | 5 |
| 045 | 4 |

The only 3 power-of-two-rank cuts are `012,023,045`. Their pairwise intersection-size multiset is `{1,1,2}`. But the THREE distinct cyclic contiguous 3|3 cuts of ANY circular ordering of six distinct legs (with left side normalized to contain leg0) always have pairwise intersection-size multiset `{1,2,2}`. Therefore at least one cyclic contiguous balanced cut has rank 3 or 5 no matter HOW the six external legs are cyclically ordered.

The *published matchgate rank rigidity theorem* states that the standard matrix form of an ordinary matchgate signature across a contiguous prefix/suffix boundary split has rank a power of 2 (or zero for degenerate null signature). For any chosen external ordering of T6, one of the three contiguous 3|3 flattenings violates this condition. Any independent invertible 2x2 local changes of external legs preserve exact flattening ranks.

Thus the canonical native FOUR-node alternating path cannot be turned into ONE ordinary arity6 matchgate under any external leg ordering and invertible edge-local GL2 basis changes. This is a theorem about this exact FOUR-node grouping, NOT all larger gadgets.

Executable:
`experiments/r5_universal_grouped_four_node_matchgate_rankrigidity_nogo.py`
CI https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38298808668 — SUCCESS at commit `90f9e1c5f8a27f95b946f54cff7a104a3f41d6b8`.
- Exact source path authentication in Fano7, K4, K3,3, Petersen and J5/SCL90.
- Independently built complete 64-entry tensor and all 10 balanced ranks.
- ALL 720 cyclic wire orderings independently checked.
- ALL 729 choices of three heterogeneous invertible boundary bases over six wires independently checked.
- Forged original source rejected.

IMPORTANT: proving this native cell is not ONE matchgate does not imply a lower bound for arbitrary tensor gadgets, nor any SAT decision complexity separation.

## 3. CONSTRUCTIVE exact matchgate-sum rank

A different mechanism works on precisely these cells: decompose them into a small SUM of distinct genuine standard matchgate signatures, NOT necessarily one matchgate.

For T4 split by tensor parity:

```
T4 = |0011>                         [even matchgate]
   + (|1000> + |0100>)              [odd matchgate].
```

Both summands satisfy ALL four-wire matchgate identities. Hence its matchgate-sum rank in the original boundary basis is <=2. The preceding rank obstruction rules out a ONE-matchgate representation even after arbitrary local GL2 gauges; therefore rank(T4) is EXACTLY 2, including local basis changes.

For the FOUR-node SIX-wire cell:

```
 T6 = E + S + C
 E = |100100> + |010100>         [even matchgate]
 S = |001000>                    [odd matchgate]
 C = |100011> + |010011>         [odd matchgate].
```

Each of E,S,C satisfies EVERY matchgate identity over all 64x64 pairs of input bitmasks, verified independently in a standalone proof checker. So matchgate-sum rank(T6) <=3.

It is also >=3 **in the original Boolean basis**. A sum of TWO standard matchgates would need exactly one even and one odd matchgate because T6 has nonzero entries of both parities. The even term would be its UNIQUE even projection E, and the odd term its UNIQUE odd projection O=S+C. But the odd projection O violates a SPECIFIC six-leg quadratic matchgate identity:

```
 alpha = 0
 beta  = 53
 flip positions 0,2,4,5 (zero based)
 MGI(alpha,beta,O) = +1 != 0.
```

This is an independent strict UNSAT certificate for the hypothesis 'O is one standard matchgate'. Hence original-basis `matchgate_sum_rank(T6)=3` EXACTLY. It is NOT yet established that the minimal SUM rank stays 3 after arbitrary heterogeneous GL2 changes on the SIX external legs; only ONE matchgate remains impossible under all such gauges.

Executable:
`experiments/r5_universal_grouped_cell_matchgate_sum_rank.py`
CI https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38299083758 — SUCCESS at `801e5ec9308a2fde810a6a24323b2c5cd9d64170`.
All complete matchgate identity checks pass; K4/K33/Petersen/Fano source authentication passes; a deliberately truncated summation and forged O-as-matchgate claim both correctly fail.

## 4. Independent published theory and scope

Exact arity4 matchgate conditions:
J.-Y. Cai, Z. Fu, *A Collapse Theorem for Holographic Algorithms with Matchgates on Domain Size at Most 4*, Information and Computation 239 (2014) 149–169, DOI 10.1016/j.ic.2014.10.002.
The four-leg even and odd quadratic identities are recorded there explicitly.

General matchgate identities and equivalence:
J.-Y. Cai, A. Gorenstein, *Matchgates Revisited*, Theory of Computing 10 (2014) 167–197, DOI 10.4086/toc.2014.v010a007.

General rank rigidity:
Sitan Chen, *Basis Collapse for Holographic Algorithms Over All Domain Sizes*, STOC 2016, pp. 776–789, DOI 10.1145/2897518.2897546, arXiv:1511.00778.
This paper proves the rank of the standard matrix form of a matchgate signature is a power of two. JANUS applies that PUBLISHED necessary property to the exact source-authenticated T6 tensor.

None of these mathematical ingredients should be claimed as newly invented literature results. The present claim is the original-source-aligned JANUS local obstruction/decomposition experiment.

## 5. The precise NEW open compression theorem

Local matchgate sums do NOT by themselves yield a polynomial all-SCL algorithm. Distributing a tensor-network product over p independent rank-3 cell sums naively generates up to 3^p terms. Even an individual matchgate network can only be evaluated by one Pfaffian under appropriate planar/perfect-matching conditions, not arbitrarily on all high-genus Tanner sources. Previous source-minor checkpoint proved families with linear Tanner treewidth.

Next legitimate theorem target: construct a compact *implicit* representation class `C` containing these source-aligned exact grouped tensors, together with polynomial-time operations:
  (i) all-native source gadget initialization;
  (ii) arbitrary original Tanner incidence contraction/composition;
  (iii) exact Boolean SAT-witness extraction OR independently replayable UNSAT acceptance;
  (iv) a polynomial encoding-size bound AND ONE uniform polynomial bit-time bound after ANY sequence of contractions.

In particular, a compact *sum-of-Pfaffians representation* must admit a polynomial-time zero/nonzero test and source SAT witness extraction without expanding 3^{number_of_cells}. The local 2/3-summand identity is not this theorem.

GATES:
```
ORIGINAL_SOURCE_TWO_NODE_T4_RANKS_2_3_3 = PROVED
ONE_MATCHGATE_TWO_NODE_GL2_GROUPING = REFUTED
ORIGINAL_SOURCE_FOUR_NODE_T6_RANKS_2_3_4_5 = PROVED
ONE_MATCHGATE_FOUR_NODE_PATH_GL2_GROUPING = REFUTED
T4_MATCHGATE_SUM_RANK = EXACTLY_2
T6_MATCHGATE_SUM_RANK_ORIGINAL_BASIS = EXACTLY_3
T6_MATCHGATE_SUM_RANK_ALL_GAUGES = OPEN
GENERAL_COMPACT_IMPLICIT_MATCHGATE_SUM_CONTRACTION = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```

Main unchanged. PR #516 remains draft.
