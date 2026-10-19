# R5: All-future Hall constraints as a static independent-set dual; Petersen convexification gap
Date: 2026-10-15. Proof status: ALL-N identities; finite exact controls. Scientific target remains universal deterministic polynomial `GlobalCutImprove`.

## Provenance
- Repository `Hawkar-usls/Janus-Fundamentum`; parent research branch `research/r5-tutte-deficit-local-trap-20261014`.
- Starting branch HEAD verified `4b91bf1031630cc0530b4b4e68f2645a87c79767` with CI SUCCESS `38643681037`.
- Separate `main` observed at `a278d68534cbc9eba6fadbf4ff26182c03c792a2`. Do not overwrite main.
- Proof-carrying executable: `experiments/r5_static_independent_hall_dual_20261015.py`.
- PRIOR gates: polynomial fixed-state Hall certificate; exact cut-space matching exchange; quantitative necessary cut repairs (NOT sufficient).
- All-n universal polynomial global search: NOT CONSTRUCTED. `P vs NP`: OPEN.

## Theorem A: One fixed-family dual represents **all** future Hall deficits exactly
Let G=(V,E) be a finite simple cubic graph. Fix any **admissible** binary
labeling s:V->{0,1} with monochromatic edges
`M_s={uv:s(u)=s(v)}` forming a matching.
Let U_s be the vertices not touched by M_s and
`r_s(v)=1[v in U_s]`. The induced residual graph
`R_s=G[U_s]` is bipartite: every edge between exposed vertices
must join opposite label classes.

For each original-graph independent set X in I(G) (including empty),
write `L_X(r)=r(X)-r(N_G(X))` with
`r(Y)=sum_{v in Y}r(v)`. Note N_G(X) is an OPEN original-graph
neighborhood and X cap N_G(X)=empty.

**Exact universal identity:**
```text
Delta(s) := |U_s| - 2 nu(R_s)
          = max_{X in I(G)} L_X(r_s).
```

*Upper bound.* For any independent X of G put Y=X cap U_s.
Then Y is independent in R_s. Each edge of a fixed maximum matching
of R_s covering a vertex in Y must use a **distinct** vertex of
N_{R_s}(Y); thus at least |Y|-|N_{R_s}(Y)| vertices of Y are unmatched.
The total number of unmatched residual vertices is Delta(s), so
`|Y|-|N_{R_s}(Y)|<=Delta(s)`. Further,
`N_{R_s}(Y) subseteq N_G(X) cap U_s`, whence
`L_X(r_s)<=|Y|-|N_{R_s}(Y)|<=Delta(s)`.

*Attainment.* Since R_s is bipartite, König's theorem gives
`alpha(R_s)=|U_s|-nu(R_s)`. Choose a maximum independent set
X* of R_s, which is also independent in original G since
R_s=G[U_s]. Every maximum independent set is inclusion-maximal,
therefore `N_{R_s}(X*)=U_s\\X*`. Hence
`L_X*(r_s)=2|X*|-|U_s|=|U_s|-2nu(R_s)=Delta(s)`. QED.

**Consequence (exact, all n):** For every admissible candidate s',
`Delta(s')=0` iff
`r_{s'}(X)<=r_{s'}(N_G(X))` for **every** independent set
X of the one fixed original graph G. The index family I(G) does
not change with the candidate vertex flips; only the exposure vector does.

This is a special weighted/bipartite manifestation of the classical
*critical independent-set difference* and König–Egerváry duality.
Do not claim the underlying critical-difference theory is novel.
Literature: Levit & Mandrescu, *Critical independent sets and
König–Egerváry graphs*, arXiv:0906.4609,
https://arxiv.org/abs/0906.4609 .

## Theorem B: Convexifying admissible exposures is NOT an exact SAT test
Define the independent-set Hall polyhedron
```text
P_G={r in [0,1]^V : L_X(r)<=0 for ALL X in I(G)}.
```
Let `A_G` be the set of admissible binary labelings and
`Q_G=conv{r_s:s in A_G}`.

On the Petersen cubic graph, **P_G cap Q_G is nonempty although
every admissible labeling is strictly positive-deficit (UNSAT)**.

*Proof/certificate.* On the fixed standard Petersen presentation
(two pentagons with five spokes):
- Exhaustive exact script enumerates precisely 10 admissible labels.
- Every one has Delta(s)=4 and |U_s|=4.
- Every vertex belongs to U_s in exactly **four** of those ten labels.
Therefore their equal-weight convex average is
`rbar(v)=4/10=2/5` for every vertex v; clearly rbar is in Q_G.

The spokes `(0,5),(1,6),(2,7),(3,8),(4,9)` form a perfect matching
of Petersen. For ANY independent set X in G, its vertices inject into
their distinct partners under this perfect matching, so
`|X|<=|N_G(X)|`. Consequently
`L_X(rbar)=(2/5)(|X|-|N_G(X)|)<=0`.
Thus rbar is in P_G, satisfying **all** independent-set Hall constraints.
Yet Petersen is 3-edge-uncolourable and every admissible exposure r_s
has `max_X L_X(r_s)=4>0`.

Quantitatively:
```text
min_{s admissible} max_{X independent} L_X(r_s) = 4,
min_{r in conv{r_s}} max_{X independent} L_X(r) = 0.
```
The second minimum is zero because the empty independent set
guarantees objective >=0 and rbar achieves 0. QED.

This is a rigorous **integrality/convexification gap of 4** for
THIS relaxation, even with the exact convex hull of all admissible
exposure vectors. Do not extrapolate to all nonlinear/extended
formulations or to impossibility of P=NP.

The finite regression independently tests each of Petersen's 76
independent sets, all 10 exposed states, and the averaged 2/5 vector
using exact integer arithmetic.

## Theorem B2: Unbounded all-k gap on cubic direct sums (NOT connected)
Let `P` be Petersen and let `G_k` be the disjoint union of k
copies of P (a simple cubic graph with n=10k vertices).
For every admissible vertex labeling of `G_k`, its restriction to
each component is admissible, and `Delta` is additive under disjoint
union. Since every admissible label of P has Delta=4:
```text
min_{s admissible on G_k} Delta(s) = 4k.
```
Uniformly independently sample one of the 10 admissible Petersen
labels in each component. The average exposure is identically 2/5
at all 10k vertices. A perfect matching exists in every component,
so their disjoint union has a perfect matching. As above, every
independent X in G_k satisfies |X|<=|N(X)|, hence the averaged
exposure satisfies all static independent-set Hall inequalities.
The convex min-max relaxation has value 0.

Thus the integrality gap is **4k = (2/5)n**, unbounded with n,
even when ALL fixed-index independent-set inequalities are retained.
The n=10 Petersen example already provides a CONNECTED obstruction;
the linear-growth construction here is a *disconnected* direct-sum
family. Do NOT claim it proves a linear gap for connected inputs.

The executable independently replays k=2 by Cartesian products of
the 10 admissible Petersen states: 100 admissible two-block states,
5776 independent-set pairs, integer deficit 8,
averaged exposure 40/100 at every vertex and convex value 0.
This is a finite regression and an analytic all-k proof, not a
universal complexity lower bound on nonlinear algorithms.

## Theorem C: All future Hall checks have a UNIFORM polynomial-size circuit
For each fixed simple cubic graph G on n vertices, a Boolean circuit
`C_G(a)` with input a in {0,1}^n and size n^O(1) can be
**constructed in polynomial time** such that
```text
C_G(a)=1 iff a is admissible and Delta(a)=0.
```
*Proof.* Construct the incidence bit indicators
`m_uv(a)=1-a_u-a_v+2*a_u*a_v` (or Boolean XNOR).
Check `sum_{e incident v}m_e<=1` at each degree-3 vertex.
Set `r_v=product_{e incident v}(1-m_e)`. For admissible a,
form the bipartite graph on exposed vertices with edges from
`a=0` to `a=1`. Test whether this graph admits a perfect
matching by a deterministic augmenting-path bipartite-matching
algorithm (or any deterministic polynomial matching algorithm).
The routine has a polynomial worst-case time bound on EVERY a,
including inadmissible a. Its fixed-size loops, array operations and
branches can be unrolled into a **uniformly constructible polynomial
Boolean circuit** using ordinary AND/OR/NOT and multiplexers.

This is a genuine polynomial-size SYMBOLIC PREDICATE for all 2^n
assignments simultaneously, not an evaluated table or an exponential
list of Hall witnesses. However deciding
`exists a in {0,1}^n : C_G(a)=1` is NP-complete by Holyer's
3-edge-colouring theorem. Merely **constructing** C_G or evaluating
it for one specified a does not eliminate the existential parameters.
The key missing gate is uniform deterministic polynomial
`Exists(C_G)` on this restricted circuit family.

## Theorem D: Explicit linear-size quadratic 0/1 lift
Introduce a binary vertex-label variable a_v for every v and
one binary z_e for each edge (n+3n/2 binary variables).
For e=uv define the *integer* quadratic polynomial
```text
mono_e(a)=1-a_u-a_v+2*a_u*a_v.
```
Consider n equations, one at each vertex:
```text
sum_{e incident v} (mono_e(a)+z_e) = 1.
```
All variables a_v,z_e must be Boolean and equations hold over the
INTEGERS, not modulo 2 or modulo 3.

**Theorem.** This 0/1 quadratic system is feasible iff G has a proper
3-edge-coloring.

*Proof.* In a solution, each vertex is incident with exactly one
edge of the union of all monochromatic edges and edges with z_e=1.
Therefore this union P is a perfect matching, monochromatic edges
are necessarily disjoint, and no z edge is monochromatic. The
complementary spanning 2-factor G-P has all edges bichromatic under a,
hence has even cycles; alternate two edge colors around these cycles,
with P in the third color. Conversely, in any proper 3-edge-coloring,
take one color class as P. Every cycle of the complementary 2-factor
is even; assign alternating vertex bits a around each such cycle.
Every monochromatic edge of G lies in P. Set z_e=1 on edges of P
that are NOT monochromatic, and 0 elsewhere. Then each integer
vertex equation holds exactly. QED.

The system has O(n) equations and O(n) variables, of uniformly
bounded degree and local support. Thus **all** dynamic Hall conditions
can be existentially encoded in linear size without materializing
independent-set inequalities. But satisfiability of this special
quadratic Boolean family remains NP-complete, by Holyer.
It is NOT a polynomial algorithm to eliminate a and z.

### Why this matters for JANUS
The request "compress every future Hall obstacle symbolically" is
achievable in polynomial size in at least TWO exact ways:
(i) a uniform polynomial Boolean checker circuit, and
(ii) a linear-size quadratic 0/1 existential lifting.

What remains OPEN is **efficient existential elimination / recognition
of nonzero support** for these compact representations. On Petersen,
even the complete static Hall family becomes insufficient if we
convexify exposure vectors. Both syntax-size and linear relaxation
are definitively distinguished from algorithmic tractability.

## Reproducible finite regression
From repo root:
```bash
python3 experiments/r5_static_independent_hall_dual_20261015.py
```
The checker independently enumerates every admissible labeling and
every independent set for five tiny controls:
- K4: 6 admissible masks, all Delta0, 5 independent sets;
- K3,3: 2 admissible masks, all Delta0, 15 independent sets;
- Petersen: 10 admissible masks, all Delta4, 76 independent sets;
- n=10 connected bridgeless SAT Hall trap: 16 masks (12 Delta0, 4 Delta2), 72 independent sets;
- n=12 connected bridgeless SAT imbalance trap: 10 masks (8 Delta0, 2 Delta4), 184 independent sets.

The new checker compares static-max dual against an INDEPENDENT
small-graph exact maximum-matching implementation and a polynomial-time
fixed-s bipartite matching routine. For K4 and K3,3 it also brute-force
checks the quadratic lift across ALL vertex bit assignments and ALL
possible z assignments. For every zero-deficit finite state it
reconstructs z and verifies EVERY local integer quadratic equality.

Finite enumeration is exponential in n. It is reproducibility control,
not a proof of universal polynomial runtime.

## Next legitimate scientific gate
Construct and prove an algorithm that solves
```text
exists a,z Boolean: forall v, sum_{e incident v}
  (1-a_u-a_v+2*a_u*a_v+z_e)=1
```
in deterministic O(n^C) time for EVERY legal cubic graph,
with SAT witness or sound UNSAT and a uniform C. It must explicitly
avoid both integer-state exponential branching and Petersen's
convexification trap. Only this would advance the universal P=NP goal.

Ledger:
- Static all-state critical-difference identity: PROVED all n.
- Petersen integer-versus-convex Hall gap: PROVED finite exact witness.
- Uniform polynomial checker circuit for fixed a: PROVED (standard simulation).
- Linear-size quadratic Boolean lift: PROVED all n.
- Polynomial existential parameter elimination: NOT CONSTRUCTED.
- Polynomial GlobalCutImprove: NOT CONSTRUCTED.
- Universal SolveLinearCubicXSAT: NOT CONSTRUCTED.
- P vs NP: OPEN.
