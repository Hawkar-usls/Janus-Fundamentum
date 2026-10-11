# R5 — Exact Rank/Nullity Portfolio for Universal SCL Decision

Date: 2026-10-11  
Repository: `Hawkar-usls/Janus-Fundamentum`  
Base commit: `f91ed13f23f027277aeda85ec9b8cbbe1b8b3e8f`  
Research branch: `research/rank-nullity-portfolio-20261011`  
Executable object: `experiments/r5_universal_rank_nullity_exact_portfolio.py`  
Executable-object commit: `8f5204e29427cd3cd995b53f3672f459472859cf`

## Status

```text
ALL_INPUT_SOUNDNESS = PROVED
ALL_INPUT_COMPLETENESS = PROVED
SAT_WITNESS = EXPLICIT_AND_REVERIFIED
UNSAT = EXACT_FINITE_STATE_EXHAUSTION
WORST_CASE = O*(1.328470^n)
UNIVERSAL_POLYNOMIAL_RUNTIME = NOT_PROVED
P_VS_NP = OPEN
```

This checkpoint constructs a complete deterministic solver for every legal
square+cubic+linear Positive Exact-One instance.  Its current proved
worst-case bound is exponential.  Therefore it is a solver checkpoint, not the
requested final `SolveLinearCubicXSAT` polynomial theorem.

No timeout, optimizer failure, modular consistency result, numerical fit, or
hash is interpreted as SAT or UNSAT.

## 1. Exact predecessor equivalence

Let (A) be the (n	imes n) binary incidence matrix.  Every row and column
has weight three.  For (kinker_{mathbb F_2}A), each integer row sum of
(k) is zero or two.  If (t_2(k)) rows have sum two, double counting gives

[
3|k|=2t_2(k)le 2n.
]

Consequently

[
|k|le rac{2n}{3}.
]

Equality holds exactly when every row of (k) contains two ones.  Then its
Boolean complement (x=mathbf1+k) contains exactly one one in every row.
Thus

[
oxed{operatorname{ExactOne}(A)
iff exists kinker_{mathbb F_2}A: |k|=2n/3.}
]

This is the already-proved E58 endpoint.  The new object supplies two explicit
search engines for that endpoint and a rank/nullity portfolio bound.

## 2. Rank engine: exact cardinality/syndrome DP

Let (r=operatorname{rank}_{2}A), and retain (r) independent parity-check
rows.  Column (j) is an (r)-bit syndrome (c_j).

For the first (i) columns define

[
D_i(q,s)=1
]

iff some (q)-element subset of those columns has XOR syndrome (s).
The recurrence is

[
D_{i+1}(q,s)=
D_i(q,s) lorD_i(q-1,soplus c_i).
]

The initial state is (D_0(0,0)=1).  A cap word exists exactly when

[
D_n(2n/3,0)=1.
]

One predecessor bit mask is retained per reachable state, so a positive result
returns the actual (k), not only a count.  The implementation independently
checks (Ak=0), (|k|=2n/3), constructs (x=mathbf1+k), and checks every
integer Exact-One row.

There are at most ((2n/3+1)2^r) states.  Hence the bit-complexity is

[
O(n^2 2^r)operatorname{poly}(n)
]

with (O(n2^r)) witness-bearing state space.

This is a standard exact subset-syndrome dynamic program.  No literature
novelty is claimed for the primitive.

## 3. Nullity engine: exact affine 2-Sub-SAT branching

Let (d=n-r) and write (k=Bt), (tinmathbb F_2^d).

For a row ({a,b,c}), kernel parity gives

[
k_c=k_a+k_b.
]

The row has weight two exactly when ((k_a,k_b)
e(0,0)).  Therefore every
row contributes one clause

[
ell_i(t)lor m_i(t),
]

where (ell_i,m_i) are homogeneous linear forms.

At every affine residual state, constants and equal/complementary forms are
propagated exactly.  For two independent remaining forms, satisfying
assignments partition disjointly as

[
ell=1
quadlorquad
(ell=0 land m=1).
]

The first child loses one affine dimension and the second loses two, so

[
T(d)le T(d-1)+T(d-2)=O^*(arphi^d).
]

Every leaf is either an explicit inconsistent row or an affine state on which
all clauses hold.  Thus the recursion is sound and complete.  A successful
leaf returns (t), then (k=Bt), then the independently verified Exact-One
witness.

Arvind and Guruswami study this general 2-Sub-SAT / union-of-subspaces
avoidance language and give the same deterministic golden-ratio branching
bound; the relation here is `DIRECT_APPLICATION_TO_THE_E58_SCL_KERNEL`, not
an independent novelty claim:

V. Arvind and V. Guruswami, “CNF Satisfiability in a Subspace and Related
Problems,” arXiv:2108.05914.

## 4. Deterministic portfolio envelope

The solver chooses the smaller of

[
2^r
quad	ext{and}quad
arphi^{n-r}
]

up to polynomial factors.  Let (a=log_2arphi).  The worst balance point is

[
r=a(n-r),
qquad
rac rn=rac{a}{1+a}=0.4097655169ldots
]

and therefore

[
oxed{
T(n)=O^*!left(2^{0.409765517n}ight)
     =O^*(1.328469879^n).
}
]

This is a strict all-input upper bound for the implemented portfolio.  It is
not a polynomial bound.

## 5. Why this parameter portfolio does not cross the polynomial gate

The direct cubic-edge-colouring bridge is an exact hard control.  For a
connected simple cubic graph with (V) vertices and (E=3V/2) edges, the
legal SCL target has

[
N=3E=rac{9V}{2}
]

variables.  After the edge-row equations, a kernel word is a pair of binary
cycle-space flows.  The cycle-space dimension is (E-V+1=V/2+1), hence

[
d=V+2,
qquad
r=N-d=rac{7V}{2}-2.
]

Both are linear in (N).  In particular, the rank/nullity portfolio cannot be
promoted to polynomial time merely by claiming that one of its two parameters
is (O(log N)).

Holyer proved that edge colouring remains NP-complete for cubic graphs:

I. Holyer, “The NP-Completeness of Edge-Coloring,” SIAM J. Comput. 10(4),
718–720 (1981), DOI: 10.1137/0210055.

The repository’s direct bridge is bijective and legal, so a universal
polynomial promotion of this solver would be a P-vs-NP-scale result.

## 6. Frozen controls

The executable contains four legal controls:

| Control | (N) | rank | nullity | Expected |
|---|---:|---:|---:|---|
| E61 SAT12 | 12 | 10 | 2 | SAT |
| E61 UNSAT12 | 12 | 11 | 1 | UNSAT |
| direct K4 SCL | 18 | 12 | 6 | SAT |
| direct Petersen SCL | 45 | 33 | 12 | UNSAT |

An independent exact in-session implementation produced:

```text
SAT12 rank-DP       = SAT, witness rechecked
UNSAT12 rank-DP     = UNSAT
K4 kernel count at cap       = 6
Petersen kernel count at cap = 0
```

The Python file contains the same fixtures and assertions.

Provenance ceiling at this commit:

```text
INDEPENDENT_CONTROL_ARITHMETIC = PASS
PYTHON_FILE_CREATED = PASS
PYTHON_FILE_RUNTIME_REPLAY = NOT_RUN
REASON = local executor unavailable during construction
```

The missing runtime replay is an engineering verification gap, not evidence of
a mathematical negative result and not an UNSAT claim for any new instance.

## 7. Gates

| Gate | Previous | New | Basis |
|---|---|---|---|
| Kernel cap equivalence | PASSED | PASSED | E58 theorem |
| Rank-parameter exact search | OPEN | PASSED | syndrome DP + witness reconstruction |
| Nullity-parameter exact search | known language | PASSED/IMPLEMENTED | affine exhaustive branching |
| All-input soundness/completeness | OPEN for this object | PASSED | exhaustive dichotomy of states |
| Deterministic sub-(2^n) envelope | OPEN for this object | PASSED | rank/nullity balance |
| Polynomial runtime | LOCKED | LOCKED | both parameters can be linear |
| Direct local matchgate route | handled separately | see port-dependent firewall | parity obstruction |
| P vs NP | OPEN | OPEN | no universal polynomial theorem |

## 8. Next admissible step

The next step is not another finite benchmark and not another renaming of the
kernel cap.  It must compress one of the two exact state spaces on the
simultaneous large-rank/large-nullity residual:

1. quotient the syndrome DP by a proved equivalence preserving target
   cardinality and witness recovery; or
2. combine E110 subspace branch-width states with the rank DP and prove a
   polynomial bound on the remaining high-width pieces; or
3. find a new invariant that decides the direct cubic nowhere-zero
   (mathbb F_2^2)-flow subclass without enumerating a linear number of
   independent flow bits.

Until one of those is proved with polynomial bit complexity:

```text
SolveLinearCubicXSAT universal polynomial = NOT CONSTRUCTED
P_VS_NP = OPEN
```
