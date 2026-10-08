# General SAT — Uniform Gaussian Implication Closure Audit

Date: 2026-10-08

Status:
`GAUSSIAN_IMPLICATION_CLOSURE_SOUND_AND_POLYNOMIAL__NOT_COMPLETE__LOW_NORMAL_RANK_RESIDUE_HAS_EXACT_POLYNOMIAL_TERMINAL`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE GENERAL SAT IN P OR P=NP.

IT AUDITS THE CURRENT UNIFORM-CLOSURE IDEA WITHOUT HIDING BRANCHING.

THE BRANCH-FREE CLOSURE
  Gaussian reduction
  + implication graph
  + SCC equalities
  + failed-lineral equations
IS SOUND AND POLYNOMIAL, BUT NOT COMPLETE.

A FROZEN 3-VARIABLE / 4-CLAUSE 2-XNF INSTANCE IS UNSAT WHILE THE CLOSURE
REACHES A FIXPOINT WITH NO LEARNED AFFINE EQUATION AND RETURNS OPEN.

THE CORRECT NEXT LAYER IS THE SAME AFFINE-FLAT / NORMAL-SPAN QUOTIENT
ALREADY DEVELOPED IN R5 E105-E111.

LOW NORMAL-SPAN RANK r=O(log L) IS A FULLY EXACT POLYNOMIAL TERMINAL.
THE HIGH-RANK CONNECTED RESIDUE REMAINS OPEN.
```

## 1. Repository/review context

The current default branch does not yet contain the uncommitted
`Uniform closure review` implementation described in the active review notes.

The older branch

```text
research/general-sat-universal-closure-v1
```

already preregisters the correct universal contract:

```text
* exact semantics;
* no final OPEN status;
* no hidden unbounded branching;
* total construction + discovery + solving + reconstruction + verification
  bounded by one fixed polynomial.
```

This audit is isolated on a new review branch so it does not overwrite or
pretend to see uncommitted work.

## 2. External anti-loop: 2-XNF already contains the same architecture

Andraschko, Danner and Kreuzer, *SAT Solving Using XOR-OR-AND Normal Forms*,
Mathematics in Computer Science 18, 20 (2024),
DOI 10.1007/s11786-024-00594-x, prove:

```text
* every CNF formula can be converted to equisatisfiable 2-XNF in polynomial
  time;
* consequently 2-XNF SAT is NP-complete;
* implication graph structures can be combined with Gaussian Constraint
  Propagation;
* SCC and failed-lineral in-processing learn new affine equations;
* their complete solver still uses DPLL decisions after closure.
```

Therefore the current repository gap is mathematically real:

```text
finite/polynomial closure != total branch-free solver.
```

A universal completion rule for arbitrary 2-XNF would itself be a P=NP
theorem.

## 3. Representation

A lineral is represented as

```text
L(x)=a dot x XOR c,
```

with a in GF(2)^n and c in GF(2).

A 2-XNF clause

```text
L1 OR L2
```

is false exactly on the affine fiber

```text
L1=0,
L2=0.
```

Hence every 2-XNF clause forbids one affine flat of relative codimension at
most two.

This is the exact same object isolated independently by R5 E105.

## 4. Uniform Gaussian implication closure

Maintain an affine equation system

```text
A x = b.
```

Repeat:

1. Gaussian-reduce every lineral modulo A x=b.
2. Delete clauses already true.
3. Convert a false/linear clause into a forced affine equation.
4. Build the implication graph
   ```text
   NOT L1 -> L2,
   NOT L2 -> L1.
   ```
5. If L and NOT L lie in one SCC, return UNSAT.
6. Mutual reachability of L and M gives the affine equality L=M.
7. A path L -> NOT L forces L=0.
8. A path NOT L -> L forces L=1.
9. Add all learned affine equations by Gaussian elimination and repeat.

Every strict learning round increases the affine rank.

Therefore there are at most n strict Gaussian-learning rounds.

This is a sound branch-free closure.

## 5. Polynomial resource bound

Let:

```text
n = number of base Boolean variables,
m = number of 2-XNF clauses,
q = O(m) distinct linerals in the active graph.
```

A deliberately conservative implementation bound is:

```text
Gaussian reduction / consistency per round:
  poly(n,m), e.g. O(m n^3) with non-incremental elimination;

graph construction:
  O(m);

SCC:
  O(q+m);

all-source reachability / failed-lineral audit:
  O(q(q+m)) <= O(m^2);

number of strict affine-rank rounds:
  <= n.
```

Thus even a simple implementation is bounded by a fixed polynomial such as

```text
O(n m n^3 + n m^2)
```

up to representation constants.

The exact exponent is not the scientific point here. The important property is:

```text
NO BRANCHING IS HIDDEN INSIDE THE CLOSURE.
```

## 6. Why XOR expressions may not be treated as independent Boolean nodes

Take

```text
y1=x1,
y2=x2,
y3=x1 XOR x2.
```

The abstract Boolean truth vector

```text
(y1,y2,y3)=(1,1,1)
```

is impossible.

Gaussian reconstruction sees

```text
x1=1,
x2=1,
x1 XOR x2=1
```

and immediately derives inconsistency.

Therefore any implication-graph assignment must be reconstructed in the
original affine variable space.

A graph-only model over independent lineral nodes is unsound.

The companion checker freezes this exact hazard.

## 7. Frozen closure obstruction

Use three base variables x1,x2,x3 and four clauses:

```text
C1:
  x3
  OR
  (x1 XOR x3)

C2:
  NOT x1
  OR
  NOT(x1 XOR x2)

C3:
  (x1 XOR x2)
  OR
  NOT(x1 XOR x2 XOR x3)

C4:
  NOT x2
  OR
  (x1 XOR x2 XOR x3).
```

Exact enumeration gives:

```text
SAT assignments = 0.
```

Deleting any one clause gives at least one satisfying assignment.

So the witness is irredundantly UNSAT under clause deletion.

## 8. Exact affine-cover structure of the obstruction

Each clause forbids exactly two of the eight points of GF(2)^3.

In integer encoding x1+2x2+4x3, the four forbidden sets are:

```text
B1={0,2}
B2={1,5}
B3={4,7}
B4={3,6}.
```

They are pairwise disjoint and

```text
B1 union B2 union B3 union B4
=
GF(2)^3.
```

Thus UNSAT is a global exact affine cover.

No one clause is locally contradictory and no pairwise overlap is needed.

## 9. Closure result on the obstruction

The Gaussian implication closure reaches a fixed point with:

```text
learned affine rank = 0,
active clauses       = 4,
SCC contradiction    = none,
failed lineral       = none,
verdict               = OPEN.
```

Yet exact semantics is UNSAT.

Therefore:

```text
boxed:
GAUSSIAN + SCC + FAILED-LINERAL CLOSURE IS NOT COMPLETE FOR 2-XNF.
```

This is the required firewall against promoting the current closure merely
because it solves the saved examples.

## 10. The bridge to R5 E105-E111

The remaining 2-XNF problem after Gaussian implication closure is exactly an
affine-flat avoidance problem.

This matches the independent R5 pipeline:

```text
E105:
  one forbidden affine fiber per check;

E106:
  polynomial rank-0/rank-1 affine propagation;

E108:
  quotient by the span of active flat normals;

E109:
  direct-sum normal-matroid component decomposition;

E110:
  exact branch-DP on a supplied low-width rank-2 subspace arrangement;

E111:
  constructive polynomial terminal for sufficiently small branchwidth.
```

So these two research lanes should be unified rather than duplicated.

## 11. Branch-free low-normal-rank terminal

At the closure fixed point, let W be the span of all active affine-flat
normals and let

```text
r=dim W.
```

Every active clause depends only on the quotient by W-perp.

Therefore the complete residual decision factors through exactly

```text
2^r
```

quotient states.

This is exact, not heuristic.

Hence:

```text
r <= C log_2 L
=> 2^r <= L^C
=> exact residual solving is polynomial.
```

The frozen four-clause obstruction has

```text
r=3,
2^r=8,
```

and is therefore solved immediately by this branch-free quotient terminal.

## 12. What remains genuinely OPEN

The universal closure gap is now sharpened.

A hard residual must survive all of:

```text
1. Gaussian equation reduction;
2. implication/SCC closure;
3. failed-lineral closure;
4. exact assignment reconstruction;
5. rank-0/rank-1 affine propagation;
6. low-normal-rank quotient solving;
7. normal-matroid direct-sum decomposition;
8. any polynomially constructible low-width subspace DP terminal.
```

What remains is:

```text
HIGH-RANK,
MATROID-CONNECTED,
HIGH-BRANCHWIDTH
2-XNF AFFINE-FLAT AVOIDANCE
AT A CLOSURE FIXPOINT.
```

For arbitrary 2-XNF this class cannot be dismissed by finite testing because
2-XNF SAT is NP-complete.

## 13. Scalable PHP OPEN-family firewall

The 3-variable obstruction proves incompleteness, but a finite fixture does not
identify the asymptotic gap.  The companion scalable checker therefore uses
the standard pigeonhole family

```text
PHP_{k+1}^k,  k>=3,
```

and converts every wide positive pigeon clause to exact equisatisfiable 2-XNF
using the standard chained auxiliary-variable construction.

For the resulting 2-XNF instance:

```text
original variables     = k(k+1)
auxiliary variables    = (k+1)(k-2)
total variables N_k    = 2(k^2-1)

total 2-XNF clauses M_k
                       = (k+1)(2k^2+3k-6)/2.
```

The checker independently truth-table verifies the local CNF-to-2-XNF
conversion for clause widths 3 through 6.

### 13.1 Symbolic closure stall

For every k>=3 the implication graph admits a four-level acyclic grading:

```text
level 0:
  positive chained XOR linerals R=Y XOR Z,
  negative auxiliary Y linerals

level 1:
  positive original pigeon variables X

level 2:
  negative original pigeon variables X

level 3:
  negative chained XOR linerals,
  positive auxiliary Y linerals.
```

Every implication edge is strictly level-increasing.

The complementary lineral of a node lies at a distinct incompatible level, and
the conversion-label structure prevents any directed path from a lineral to its
complement.

Therefore at the closure fixed point:

```text
SCC contradiction       = none
failed linerals          = none
learned affine equations = 0
verdict                   = OPEN
```

for the whole family.

But the source formula is UNSAT for every k by the pigeonhole principle.

Hence the Uniform Gaussian implication closure has an explicit infinite UNSAT
family on which it does no affine learning.

### 13.2 Normal rank is asymptotically large

Complete every active rank-two clause pair {a,b} to the binary line

```text
{a,b,a XOR b}.
```

Every original coordinate normal and every auxiliary coordinate normal occurs
in this line system.

Therefore:

```text
normal-span rank = N_k = 2(k^2-1).
```

The circuit-overlap graph of these lines is connected:

```text
* original pigeon variables are connected by the row/hole at-most-one
  constraints;
* each auxiliary variable is connected into that component by its conversion
  clauses.
```

So E109 direct-sum decomposition does not split this family into bounded-rank
components.

### 13.3 Branchwidth is also asymptotically large

Fix one hole and look only at its at-most-one clauses.

For q=k+1 pigeons they contain every pair subspace

```text
span(e_i,e_j),  1<=i<j<=q.
```

This is the K_q edge-subspace arrangement with

```text
M = C(q,2)
```

leaves.

Any subcubic branch tree has a balanced cut whose two leaf sides each contain
at least M/3 leaves.

Let S be the coordinate vertices that occur on both sides of that cut.

Because K_q is complete, all vertices outside S must belong to the same side
type.  Hence the opposite side's at least M/3 edges lie entirely inside S.

Therefore

```text
C(|S|,2) >= C(q,2)/3.
```

The cut boundary is exactly the span of the shared coordinate directions, so
its dimension is |S|.

Consequently

```text
branchwidth
  >= min{s : C(s,2) >= C(q,2)/3}
  = Omega(q)
  = Omega(k).
```

Since N_k=Theta(k^2), this is Omega(sqrt(N_k)).

Thus the constructive low-width terminal from E110-E111 does not provide a
polynomial universal bound on this family.

### 13.4 Scientific consequence

This closes a critical methodological gap:

```text
THE OPEN RESIDUE IS NOT A HANDFUL OF SAVED EXAMPLES.
```

There is an explicit infinite family that simultaneously has:

```text
* exact UNSAT semantics;
* zero affine learning under UGIC;
* full growing normal rank;
* one connected normal-matroid block;
* growing subspace branchwidth.
```

Therefore any next "uniform closure" rule must explain a genuinely global
property of this family.  Solving only the frozen fixtures cannot establish
universality.

For PHP the missing property is visible at the macro level as a global
cardinality/Hall obstruction.  That observation is only a scoped clue:
adding one pigeonhole/Hall recognizer does not solve arbitrary 2-XNF.

The correct next question is whether the high-rank closure-fixed residue admits
a **uniformly discoverable polynomial global certificate class** that strictly
contains Hall/counting contradictions and still covers every residual input.

No such theorem is currently proved.

## 14. Choice-resource Hall terminal

The scalable PHP firewall identifies the first genuinely global information
missing from Gaussian/implication closure: a capacity obstruction.

A sound polynomial terminal can be added without recognizing a benchmark by
name.

From the source CNF retained by the solver's own exact normalization, detect a
clean family of pairwise-disjoint positive choice clauses

```text
G_i = OR_{x in G_i} x
```

such that all negative binary pairs inside each G_i are present.  Each G_i is
therefore an exact-one choice group.

Now inspect negative binary clauses between different choice groups.  If their
connected components are cliques and contain at most one variable from each
choice group, each component is a unit-capacity resource.

Every satisfying assignment then induces an injection

```text
choice groups -> resources.
```

Construct the bipartite choice/resource graph and compute a maximum matching.

If the matching does not saturate all choice groups, the standard alternating
reachable sets give an explicit Hall witness

```text
S subseteq choice groups,
N(S) subseteq resources,
|N(S)| < |S|.
```

This is a polynomially replayable UNSAT certificate.  No Boolean value
branching is used.

On PHP_{k+1}^k the detector recovers exactly:

```text
k+1 choice groups,
k resource components,
maximum matching size k,
Hall witness |S|=k+1 > |N(S)|=k.
```

Thus the entire scalable PHP OPEN-family is eliminated by one uniform
branch-free macro rule.

This is deliberately a scoped terminal.  If the clean choice/resource
structure is absent, or if a saturating matching exists while other clauses
remain, the rule returns OPEN rather than overclaiming SAT/UNSAT.

Therefore Hall closure demonstrates what a useful next-layer rule looks like,
but does not establish a universal closure theorem.

## 15. Bit-pigeonhole firewall beyond simple Hall closure

The choice/resource Hall terminal closes the unary PHP family, but it does not
close the same counting obstruction when choices are encoded in binary.

Let

```text
h=2^ell,
p=h+1.
```

Represent each pigeon i by ell address bits and require every pair of pigeons
to have distinct addresses:

```text
OR_b (x_{i,b} XOR x_{j,b}).
```

This is native XNF and is UNSAT by the pigeonhole principle.

After exact conversion to 2-XNF, the companion checker verifies for
ell=2,3,4:

```text
UGIC verdict             = OPEN
learned affine rank       = 0
choice/resource Hall      = OPEN
normal-matroid components = 1.
```

The family has

```text
N =
  p*ell + C(p,2)(ell-2)
```

2-XNF variables for ell>=2, and its active normal-span rank is

```text
r =
  ell(p-1) + C(p,2)(ell-2).
```

The first term is the direct sum of the even-difference spaces of the ell
complete pigeon graphs; the second term consists of the independent auxiliary
coordinates created by the exact 2-XNF conversion.

Thus r grows linearly with the full normalized variable count.

The represented normal matroid on the **actual ground normals of the converted
2-XNF** is connected.  The checker certifies this by exact represented-matroid
fundamental-circuit decomposition.

A subtle correction matters here: a source difference vector d_{ij,b} need not
itself remain a ground element after conversion; it may only lie in the span
of one conversion block.  Therefore source K_p triangle identities cannot be
used as if every d_{ij,b} were literally present in the ground set.

The structural reason connectivity nevertheless survives is that each
conversion block spans its source difference directions, while the identities

```text
d_{ij,b} XOR d_{jk,b} XOR d_{ik,b}=0
```

create dependencies across pigeon-pair block spans.  The frozen checker uses
the safer exact matroid-component computation rather than promoting these
hidden span vectors to ground elements.

So bit-PHP is an explicit infinite residue that survives:

```text
Gaussian implication closure,
failed-lineral closure,
the simple unary choice/resource Hall terminal,
low normal-rank quotienting,
and normal-matroid direct-sum splitting.
```

### 15.1 Resolution-over-parities anti-loop

This family is also a warning against replacing the OPEN status by unrestricted
parity-resolution saturation and then assuming the saturation is polynomial.

Kamil Braun, *An exponential lower bound for the bit pigeonhole principle in
resolution over parities* (2026, arXiv:2609.23015), proves an exponential lower
bound for unrestricted DAG-like Res(oplus) refutations of bit pigeonhole.

That is a proof-system lower bound, not a lower bound for SAT decision and not
evidence that P!=NP.

Its role here is narrower:

```text
A polynomial universal closure theorem cannot be justified merely by saying
"close under all Res(oplus) consequences."
```

The next rule must exploit structure beyond generic parity resolution, or use a
different algorithmic certificate altogether.

## 16. Binary-domain AllDifferent capacity terminal

Bit-PHP shows that the same capacity obstruction can be hidden behind a compact
binary address encoding rather than a one-hot choice encoding.

A second sound polynomial macro terminal detects this directly from native XNF
syntax, without benchmark names.

Assume every clause has width ell and every lineral is a positive XOR of two
base variables.

Build the graph whose vertices are base variables and whose edges are those
weight-two XOR normals.

The accepted normal form requires:

```text
* exactly ell connected components;
* every component is a clique K_p of the same size p;
* every XNF clause contains exactly one edge from each clique;
* there are exactly C(p,2) clauses;
* the clause-induced edge correspondence between each clique and a reference
  clique preserves edge incidence.
```

For p>=4, the edge correspondence determines a vertex bijection: the star of
one reference vertex maps to edges with one unique common endpoint in every
other layer.

Thus the syntax itself reconstructs

```text
p abstract objects,
ell Boolean address bits per object,
one inequality clause for every object pair.
```

Every satisfying assignment would therefore assign p pairwise-distinct
ell-bit strings.

The address domain contains exactly

```text
2^ell
```

values.

Hence

```text
p > 2^ell
=> UNSAT.
```

The certificate consists only of:

```text
layer cliques,
the reconstructed layer bijections,
complete pair coverage,
p > 2^ell.
```

All checks are graph scans / incidence tests and integer comparison, so the
terminal is polynomial and branch-free.

The companion checker replays ell=2,3,4,5 for standard bit-PHP and confirms:

```text
UGIC                    = OPEN
simple one-hot Hall     = OPEN
binary AllDifferent     = UNSAT.
```

This demonstrates a useful pattern:

```text
a high-rank affine residue may still collapse when a polynomially recognizable
global finite-domain macro is restored.
```

Again, the rule is scoped.  An arbitrary 2-XNF residual need not expose a
complete AllDifferent macro.

## 17. Updated universal frontier

Do not add another unrestricted branch fallback.

Build a generator/search for closure-fixed residuals and classify them by

```text
normal rank,
normal-matroid components,
subspace branchwidth,
SAT/UNSAT,
minimum affine-cover multiplicity,
number of forced equations under one hypothetical decision.
```

The target theorem is a genuine dichotomy:

```text
UNIFORM CLOSURE DICHOTOMY

Every closure-fixed 2-XNF residual either

A. has a polynomially bounded normal-span / branchwidth decomposition;

or

B. satisfies a new globally forced affine equality discoverable without
   branching;

or

C. belongs to an explicit high-rank obstruction family.
```

Only A or B with a universal symbolic resource bound would advance the
P=NP route.

C would precisely identify why branching is still necessary.

Scientific status:

```text
UNIFORM_GAUSSIAN_IMPLICATION_CLOSURE = SOUND_POLYNOMIAL_INCOMPLETE.
LOW_NORMAL_RANK_RESIDUE = EXACT_POLYNOMIAL_TERMINAL.
HIGH_RANK_CONNECTED_RESIDUE = OPEN.
GENERAL_SAT_IN_P = NOT_PROVED.
P_VS_NP = OPEN.
```

## 18. Polynomial two-sided Gaussian probing closure

The review next adds a stronger closure layer without introducing recursive DPLL.

For every active nonzero normal (m), temporarily run the existing UGIC under

```text
m dot x = 0
```

and

```text
m dot x = 1.
```

There are three sound outcomes.

1. Both probes are UNSAT.

   Then the current global affine context is UNSAT.

2. Exactly one probe is UNSAT.

   Then the opposite value of (m dot x) is globally forced and is added as
   one affine equation.

3. Both probes survive.

   Compute the intersection of the two complete affine-equation consequence
   spaces.

   The intersection must be performed on the augmented GF(2) row spaces

   ```text
   (mask | rhs)
   ```

   rather than by comparing RREF rows syntactically.

   Every common affine equation is true in both possible values of (m dot x),
   hence globally implied by excluded middle.

No probe recursively launches another probe layer.

The outer loop repeats only after global affine rank increases, so there are at
most (n) strict global learning rounds.

If (q=O(m)) active normals are probed, the complete procedure makes

```text
O(n q)
```

calls to a polynomial UGIC routine plus polynomial Gaussian row-space
intersection work.

Therefore:

```text
boxed:
TWO-SIDED GAUSSIAN PROBING IS SOUND AND POLYNOMIAL.
```

It is strictly stronger than the baseline closure.

### 18.1 Frozen obstruction

The original 3-variable / 4-clause exact affine-cover obstruction is now
detected as UNSAT after only two probe calls.

So the old finite OPEN witness no longer survives the strengthened closure.

### 18.2 Unary PHP replay

For normalized PHP samples the probing layer gives:

```text
k=3 : UNSAT
k=4 : OPEN, learned affine rank 15
k=5 : OPEN, learned affine rank 24
k=6 : OPEN, learned affine rank 35
```

The ranks satisfy

```text
15,24,35 = k^2-1.
```

This equals

```text
(k+1)
+
(k+1)(k-2),
```

matching exactly:

```text
one exact-one parity equation per pigeon
+
one affine definition per chained conversion auxiliary.
```

Thus the probing layer is not merely assigning Boolean values.  On this family
it recovers a semantic affine quotient hidden by the 2-XNF normalization.

The remaining PHP contradiction is still global capacity/Hall information and
is closed by the existing Hall terminal.

### 18.3 Bit-PHP replay

For bit-PHP:

```text
ell=2 : UNSAT under probing
ell=3 : OPEN, learned affine rank 0.
```

So even the two-sided polynomial probe closure does not subsume the
AllDifferent capacity layer.

Scientific consequence:

```text
finite-depth polynomial probing is a genuine strengthening,
but it is not a universal completion theorem.
```

Companion checker:

```text
research/tools/general_sat_uniform_closure/
  two_sided_gaussian_probe_closure.py
```

## 19. Basis-invariant subspace AllDifferent terminal

The first Binary AllDifferent terminal is intentionally syntax-specific: it
expects each address-difference lineral to be one weight-two XOR.

That condition is not invariant under Gaussian coordinate changes.

For each object (i), replace its address (x_i in GF(2)^ell) by

```text
y_i = T x_i
```

for any invertible (T in GL(ell,2)).

The capacity semantics is unchanged:

```text
p pairwise-distinct y_i values
inside a domain of size 2^ell.
```

But a row of (T) with weight greater than one turns one bit-difference
lineral into a dense XOR over the two endpoint object blocks.

The original weight-two detector therefore returns OPEN on such a scrambled
encoding.

### 19.1 Clause-normal subspaces

For every native XNF inequality clause (c), forget its chosen lineral basis
and retain only the span of its normals

```text
L_c <= W.
```

In a complete binary AllDifferent system:

```text
dim L_c = ell
```

and clauses correspond to the edges of a complete graph (K_p).

If two edge-subspaces share one object, their sum contains exactly one further
clause subspace: the third edge of that triangle.

This triangle-closure relation reconstructs the line graph (L(K_p)) and,
for (p>=5), its (p) star cliques.

### 19.2 Root-star direct sum

Choose one reconstructed object as root.

The (p-1) clause subspaces incident with the root must form a direct sum

```text
S_1 direct_sum ... direct_sum S_{p-1},
dim S_i=ell.
```

Every remaining edge-subspace (L_{ij}) must lie inside

```text
S_i + S_j
```

and its projections to both endpoint blocks must have full rank (ell).

Therefore (L_{ij}) is the graph of a linear isomorphism

```text
M_{ij}: S_i -> S_j.
```

The detector then verifies the triangle cocycle

```text
M_{ik} = M_{jk} o M_{ij}.
```

This proves that all reconstructed object blocks admit one common
(ell)-dimensional label space, up to invertible basis transport.

### 19.3 Capacity theorem

Any global assignment induces one transported label for each of the (p)
objects.

The clause on edge (ij) is false exactly when the two transported labels
coincide.

Thus satisfying all clauses requires (p) pairwise-distinct elements of one
domain of size (2^ell).

Hence

```text
boxed:
p > 2^ell
=> UNSAT.
```

The certificate is entirely linear-algebraic:

```text
clause subspaces,
triangle relation,
reconstructed K_p stars,
root-star direct-sum basis,
edge graph-isomorphisms,
transport cocycle,
p > 2^ell.
```

All operations are polynomial GF(2) rank/containment tests and graph scans.
No Boolean branching is used.

### 19.4 Scrambled regression

The checker applies an invertible unitriangular transform to every object
address of bit-PHP.

Results:

```text
ell=2:
  old syntactic detector = OPEN
  subspace detector       = UNSAT

ell=3:
  old syntactic detector = OPEN
  two-sided probing      = OPEN, learned rank 0
  subspace detector      = UNSAT

ell=4:
  old syntactic detector = OPEN
  subspace detector       = UNSAT.
```

So the new terminal closes a high-rank capacity family that is invisible to
both the old weight-two recognizer and, for the nontrivial ell=3 control, the
new probing layer.

Companion checker:

```text
research/tools/general_sat_uniform_closure/
  subspace_alldifferent_capacity_terminal.py
```

## 20. Updated frontier after probing and subspace transport

The closure stack now contains three conceptually distinct polynomial layers:

```text
LOCAL / AFFINE:
  Gaussian reduction,
  implication/SCC,
  failed linerals,
  two-sided nonrecursive Gaussian probing.

STRUCTURAL DECOMPOSITION:
  rank-0/rank-1 propagation,
  low normal-rank quotient,
  normal-matroid components,
  low-width subspace DP.

GLOBAL FINITE-DOMAIN CAPACITY:
  choice/resource Hall,
  syntax-level binary AllDifferent,
  basis-invariant subspace AllDifferent transport.
```

This is materially stronger than a collection of solved fixtures.

But it is still not a universal SAT algorithm.

The remaining high-rank residue may fail to expose a complete (K_p)
AllDifferent arrangement, a Hall injection structure, or any currently known
low-width quotient.

The next theorem target should therefore be representation-invariant:

```text
UNIFORM FINITE-DOMAIN QUOTIENT DISCOVERY

Given a high-rank, closure-fixed 2-XNF affine-flat system, discover in
polynomial time either

A. a nontrivial affine quotient whose fibers behave as finite-domain object
   labels and whose conflict graph admits a polynomial capacity/matching
   certificate;

B. a polynomially bounded normal-span / branchwidth decomposition;

C. a new globally forced affine equation;

or

D. an explicit scalable family proving that all three mechanisms can fail.
```

Only a universal A/B/C theorem with one fixed polynomial resource bound would
close the current GENERAL SAT gap.

Scientific status:

```text
UNIFORM_GAUSSIAN_IMPLICATION_CLOSURE = SOUND_POLYNOMIAL_INCOMPLETE.
TWO_SIDED_GAUSSIAN_PROBING = SOUND_POLYNOMIAL_STRONGER_INCOMPLETE.
SUBSPACE_ALLDIFFERENT_CAPACITY = SOUND_POLYNOMIAL_SCOPED_TERMINAL.
HIGH_RANK_CONNECTED_RESIDUE = OPEN.
GENERAL_SAT_IN_P = NOT_PROVED.
P_VS_NP = OPEN.
```

