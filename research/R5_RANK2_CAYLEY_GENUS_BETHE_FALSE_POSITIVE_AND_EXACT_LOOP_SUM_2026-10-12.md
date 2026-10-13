# R5 — Cayley linear-genus obstruction, universal Bethe false positives, and exact generalized-loop correction

Date: 2026-10-12 (Europe/Kyiv). Research PR #516 DRAFT.
Previous authenticated checkpoint HEAD: `6473c242ef26fe76428e90e74e46abce6af063e2`.
Scientific target remains one deterministic original-source-certified polynomial-bit-time `SolveLinearCubicXSAT(F)` for EVERY legal square/cubic/linear positive Exact-One input. **NOT CONSTRUCTED. P vs NP OPEN.**

## 1. EXPLICIT infinite family: rank-two quotient graphs of linear orientable genus

Original source construction over every odd prime p: let
```
A = [[1,2],[0,1]], B = [[1,0],[2,1]]
G_p = SL(2,F_p), |G_p| = n = p(p^2-1).
```
For each g in G_p, make one positive Exact-One source clause
`{x_g,x_(gA),x_(gB)}`. Every column occurs in exactly
three clauses because multiplication by I,A,B is bijective.
The source is SCL-linear because the six quotients of distinct
elements of {I,A,B} are pairwise different (verified by absence
of short nontrivial relations).

Match source row g to original variable x_g. This is an explicit
source-authenticated Tanner perfect matching. Contract every
matching wire by previous universal rank-two T4 construction.
The resulting Q_p is EXACTLY the undirected Cayley graph of
G_p with generators {A,A^-1,B,B^-1} (n vertices, 2n edges,
4-regular and simple).

The finite integer-algebra checker exhausts ALL 160 nonempty
freely reduced words of length <=4 in A^+/-1,B^+/-1.
Every matrix differs from I, and the maximum absolute
entrywise DIFFERENCE from I is only 28.
Thus for EVERY prime p>=29 no such nontrivial short
word can equal I modulo p. This ensures Q_p has girth>=5
(no triangles, no quadrilaterals, no loops/double edges).
For every odd prime p, A and B generate SL2(F_p):
their powers yield every upper/lower elementary shear since
2 is invertible, and elementary matrices generate SL2(Fp).
Thus Q_p is CONNECTED with exactly p(p^2-1) vertices.

For any connected simple 4-regular graph with n vertices,
girth>=5, orientable genus gamma and f faces in a
minimum-genus cellular embedding, Euler gives
f=n+2-2gamma, and every face boundary has length>=5
(no bridges in a connected 4-regular graph), so
```
5f <= 2m=4n
=> 5(n+2-2gamma)<=4n
=> gamma >= n/10 + 1.
```

This establishes an EXPLICIT infinite source-legal family
of matched quartic rank-two Holant networks with genus Ω(n),
not merely a nonconstructive expander-width existence theorem.
The source family is not claimed NP-hard *on its own* and
does not prove any arbitrary-algorithm lower bound.

Code:
`experiments/r5_universal_rank2_cayley_linear_genus_obstruction.py`.
CI [#38310075119 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38310075119).
Source-replay tested p=5/7/11/29 with n=120/336/1320/24360
and genus lower bounds 13/35/133/2437. The p=29
case is the FIRST actual finite member of the uniform
asymptotic p>=29 theorem. It validated original
SCL legality, group source-to-quotient binding,
connectedness and absence of cycles length 3 or4.
Tampered source rows rejected.

The general all-SCL pairing/certificate verifier was
also hardened to precompute the original source
variable incidence index, rather than an O(n^2)
full-row scan inside the port replay. Same
authenticated certificate semantics, faster large
source processing.

Literature context only (finite short-word proof stands
independently): Sanov's free subgroup generated
by these integer shears, see
Chang, Jennings, Ree, *On Certain Pairs of Matrices
which Generate Free Groups*, Canadian Journal of
Mathematics 10 (1958) 279–284,
https://doi.org/10.4153/CJM-1958-029-2.
This checkpoint does not need to assume freeness
of ALL integer words; it enumerates only lengths<=4.

## 2. ALL-SCL strictly positive local LP/BP / Bethe is a FALSE SAT test

The universal matched T4 has exactly three allowed
four-bit configurations, written by port order as
`1000,0100,0011`.

Put probability 1/3 at each local valid configuration.
Then every one of the FOUR ports has marginal
P(bit=1)=1/3. Every global quotient wire connects
two such ports, so their pairwise marginal is
consistent. This is a complete rational 1-local
pseudo-distribution with zero factor constraint cost
on EVERY legal original SCL, SAT or UNSAT.

Even stronger, a strictly positive homogeneous
sum-product belief-propagation FIXED POINT exists
on the rank-two quotient for every legal source.
Let t>0 satisfy 2t^3=1. Set incoming message odds
r=t^2 to each row-side port and s=t to each
variable-side port. The T4 factor-to-row output odds are

  1/(r+s^2)=1/(2t^2)=t=s,

and factor-to-variable output odds are

  s/(2r)=t/(2t^2)=t^2=r.

Hence every directed message agrees with itself
after an update; all gate belief weights equal r,
so every allowed local state has probability 1/3.
The global wire belief has odds rs=t^3=1/2,
thus true probability1/3.

Compute ordinary Bethe normalization with unnormalized
fixed-point messages: at each T4 factor
`z_v=3r`, at each of the 2n quotient wires
`z_e=1+rs=3/2`. Therefore

```
Z_B(F) = ( (3r)/(3/2)^2 )^n
       = (2^(4/3)/3)^n >0,
Z_B(F)^3 = (16/27)^n .
```

This algebra is verified exactly in
Q[t]/(2t^3-1), not by tolerance floats.

Thus a local-consistency, positive-BP-existence
or homogeneous Bethe-positive criterion
cannot distinguish SAT from UNSAT for ANY legal SCL.
In particular two NON-HOLYER E61 original SCL12 inputs
with original solution counts 1 and 0 have
precisely the SAME n=12, local distributions,
homogeneous messages and Bethe value
`Z_B=(16/27)^4=65536/531441>0`.

Code:
`experiments/r5_universal_rank2_local_lp_bethe_spurious_fixedpoint.py`.
First CI #38309790790 SUCCESS; strengthened exact algebra CI
[#38309953050 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38309953050).
Source checks: Fano7=0, K4/SCL18=6, K33/SCL27=12,
Petersen/SCL45 known UNSAT, E61 SAT12=1,
E61 UNSAT12=0, plus Cayley high-genus SCL120.

This does NOT refute every approximation, global
message, higher-order relaxation or exact algebra.

## 3. NEW CONSTRUCTIVE UNIVERSAL EXACT LOOP POLYNOMIAL

The positive BP fixed point is unsuitable as a
SAT test, but does yield an exact source-preserving
transformation to global generalized-loop corrections.

For a quotient edge, use local endpoint copies a,b,
one-bit marginal `pi(0)=2/3, pi(1)=1/3`,
and the centred integer field `psi(0)=-1,psi(1)=2`.
The exact edge identity is

```
1[a=b] / pi(a) = 1 + psi(a)psi(b)/2
```

for ALL four pairs a,b; this is independently verified.
The identity is NOT approximate and every factor
normalization in the original Holant-to-Bethe ratio
cancels as derived by the ordinary BP edge/factor
normalization formula.

Let Q have n T4 cells and E(Q) have 2n edges.
Let the probability p_v be uniform over the
three allowed T4 configurations. Define exact
local moments at the 4 port positions:

```
M_v(J) = E_(p_v) [ product_(i in J) psi(b_i) ].
```

The exact global normalized partition equals

```
Z(F)/Z_B(F)
  = sum_(S subseteq E(Q))
      2^(-|S|)
      product_(v in V(Q)) M_v(S ∩ delta(v)).
```

For every original SCL, regardless of graph family,
the local 16-entry table indexed by 4-bit port mask is
```
M[0..15] =
(1, 0, 0, -1, 0, -1, -1, 2,
 0, -1,-1,  2, 2, -1, -1, 0).
```

Therefore local selected-edge DEGREE ONE and DEGREE FOUR
moments vanish EXACTLY. Only generalized-loop edge
subsets in which every node degree is 0,2 or3 survive.
Pair moments are -1 except the equality-port pair
(2,3), which is +2. Triple moments are 2 for
(0,1,2),(0,1,3), and -1 for (0,2,3),(1,2,3).
Four-port moments are 0.

This is a genuinely different EXACT local algebraic
grammar from the original 2^n Boolean selectors,
with an explicit signed cancellation mechanism
for global UNSAT. However no uniform polynomial
summation bound has been proven. The finite
checker uses resource-guarded EXPONENTIAL
edge-subset enumeration; if exhausted it returns
UNKNOWN, not a spurious UNSAT certificate.

Code:
`experiments/r5_universal_rank2_exact_bethe_loop_correction.py`.
CI [#38310389175 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38310389175).

Independently source-verified controls:

| Original legal SCL | Actual count Z | Exact loop sum L=Z/Z_B | DFS states | Nonzero loop terms | Negative terms |
|---|---:|---:|---:|---:|---:|
| Fano7 | 0 | 0 | 5,322 | 1,291 | 702 |
| E61 SAT12 | 1 | 531441/65536 | 975,754 | 216,082 | 107,616 |
| E61 UNSAT12 | 0 | 0 | 1,025,550 | 216,722 | 107,968 |

Both E61 source sizes =12 have identical positive
Bethe values 65536/531441. The exact loop correction
distinguishes the sources through a GLOBAL signed
sum. Its cancellation is genuine: both UNSAT controls
possess numerous nonzero positive and negative loop
terms that add to ZERO after including the constant
empty-loop term.

The exact identity holds for ALL original legal SCL
by the edgewise expansion proof; the finite cases
validate source alignment only, not a polynomial
runtime theorem.

## 4. Narrow remaining target

The new candidate is an exact **signed generalized-loop
Holant** with:
- 4-regular, source-authenticated quotient graph;
- identical finite local 16-entry integer moment tables;
- permitted selected loop degrees only 0,2,3;
- edge weight 1/2 per selected edge;
- known nonzero positive factor Z_B;
- `F SAT iff signed loop sum L != 0`.

This is still NP-complete to decide in general
because original SAT nonzero is NP-complete and
Z_B never vanishes. Rewriting into loops does
NOT magically give a polynomial evaluator.

Legitimate next theorem gate: find a UNIFORM
polynomial-time closed algebra of these signed
degree-(0,2,3) loop factors, with polynomial
composition on arbitrary high-genus / high-treewidth
quotient networks, and exact nonzero decision plus
source SAT witness or source-verified UNSAT proof.
The algorithm must avoid enumerating exponentially
many generalized loops or original selectors.

There is no evidence yet that such a compression
exists. No lower bound against every possible
polynomial algorithm is claimed.

```
ALL_SCL_CAYLEY_EXPLICIT_LINEAR_GENUS = PROVED
CAYLEY_P29_SCL24360_SOURCE_AUDIT = CI_SUCCESS
ALL_SCL_STRICT_POSITIVE_BETHE_FIXEDPOINT = PROVED
ALL_SCL_UNIFORM_LOCAL_LP_FEASIBLE = PROVED
ALL_SCL_BETHE_Z_CUBED=(16/27)^n = PROVED
ALL_SCL_EXACT_GENERALIZED_LOOP_IDENTITY = PROVED
LOCAL_LOOP_DEGREE_1_AND_4 = ZERO
E61_SAME_SIZE_SAT_UNSAT_LOOP_DISTINCTION = VERIFIED_FINITE
GLOBAL_POLY_GENERALIZED_LOOP_NONZERO = NOT_CONSTRUCTED
SolveLinearCubicXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```

PR remains DRAFT and main untouched.
