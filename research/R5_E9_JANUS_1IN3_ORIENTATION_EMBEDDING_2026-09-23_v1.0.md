# R5 E9 — JANUS Positive 1-in-3 Orientation Embedding

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_REALIZABILITY_PASS__NO_D1_PROMOTION

Parent: R5_E9_JANUS_1IN3_REALIZABILITY_GATE_V1

Checker: experiments/r5_e9_janus_1in3_orientation_embedding_checker.py

## 1. Source problem

Let J be an arbitrary Positive 1-in-3-SAT instance on Boolean variables X with clauses

C_e=(x_i,x_j,x_k).

J asks for an assignment with exactly one true variable in every clause.

Positive 1-in-3-SAT is NP-complete by Schaefer's Boolean CSP dichotomy.

## 2. JANUS row-side encoding

For every source clause C_e create the same positive signed-NAE3 row.

For a Boolean assignment x satisfying this NAE row, define its JANUS row-side bit

s_e = x_i+x_j+x_k-1.

Because NAE3 allows exactly one or exactly two true coordinates,

s_e is always in {0,1}.

Interpretation:

s_e=0  iff the clause has exactly one true variable;
s_e=1  iff the clause has exactly two true variables.

This is exactly the row-side variable already used by the signed-NAE / Smith side-code formalism.

## 3. Global orientation gluing

Add only equality interfaces between row-side bits so that all clauses belong to one orientation class.

It is enough to use a chain

s_1=s_2, s_2=s_3, ..., s_{m-1}=s_m.

This gives linear overhead and keeps the side-interface degree bounded.

No source satisfying assignment is needed to build the chain.

Call the resulting JANUS side network N(J).

## 4. Exact satisfiability theorem

### Theorem J13-1

J is satisfiable iff N(J) is satisfiable.

### Forward direction

Let x satisfy J.

Every source clause has exactly one true coordinate, so every corresponding NAE row is satisfied with side bit s_e=0.

All side equalities are therefore satisfied.

Hence N(J) is satisfiable.

### Reverse direction

Let x and side bits satisfy N(J).

All row-side bits are equal to one common value s.

Case s=0:

Every row has exactly one true coordinate, so x is directly a Positive 1-in-3 witness.

Case s=1:

Every row has exactly two true coordinates.

Globally complement all source variables:

x' = 1-x.

Every positive three-variable row then has exactly one true coordinate.

So x' is a Positive 1-in-3 witness.

Therefore J is satisfiable.

QED.

## 5. Witness maps

Encode:

a source witness x maps to the same source-variable assignment with all side bits zero.

Decode:

given any accepted JANUS witness, inspect the common side bit.

- if s=0, output x;
- if s=1, output 1-x.

Both maps are linear-time in the number of source variables/clauses.

## 6. Realizability contract audit

R1 BLOCK REALIZATION = PASS

Each source clause is an actual positive signed-NAE3 row with its genuine JANUS row-side bit. No handwritten Z3 relation is inserted.

R2 OCCURRENCE SHARING = PASS

Occurrences of one source Boolean variable are the same representative Boolean variable across the corresponding rows. Side orientation sharing uses only equality interfaces already admitted by the side-code gluing formalism.

R3 EXACTNESS = PASS

Proved by Theorem J13-1.

R4 WITNESS MAPS = PASS

Encode/decode are explicit; the only nonidentity decode operation is global complement.

R5 SIZE = PASS

One NAE row per source clause plus O(m) side equalities. Total construction/state/reconstruction/verification overhead is linear.

R6 NO HIDDEN ORACLE = PASS

The construction depends only on the source incidence list.

Therefore:

R5_E9_JANUS_1IN3_REALIZABILITY_GATE_V1 = PASS.

## 7. Why the previous direct census returned NONE

The restricted census asked whether one block with three exposed side bits could have exact side image

{100,010,001}.

The orientation embedding does not do that.

Each individual clause block has a single side bit with both values possible.

Hardness appears globally from:

- shared source variables between NAE rows;
- equality of all row-side orientation bits.

So direct one-block relation realization is unnecessary.

## 8. Complement symmetry is the mechanism, not an obstruction

Every constant-free signed NAE system is invariant under global complement.

Under x -> 1-x, every row-side bit flips:

s -> 1-s.

Hence direct exposed side images are complement-closed.

This proves a stronger version of the direct-realization negative control: the non-self-dual relation {100,010,001} cannot be the direct exposed side image of any constant-free signed-NAE block/network built only with complement-preserving equality/projection.

But the orientation embedding exploits this symmetry instead of fighting it.

The two global sectors are:

all rows exact-one
and
all rows exact-two.

They are exchanged by complement and decode to the same Positive 1-in-3 witness class.

Thus the JANUS embedding is a quotient by a global Z2 orientation symmetry.

## 9. Complexity consequence

The admissible JANUS row-side network class already contains a polynomial image of arbitrary Positive 1-in-3-SAT.

Therefore the three-state / non-Schaefer frontier is not merely an artifact of allowing arbitrary abstract torsion relations.

A universal polynomial algorithm that solves the entire admitted JANUS side-network class would yield a polynomial algorithm for Positive 1-in-3-SAT.

This is not a proof that P!=NP.

It establishes that the remaining JANUS side-network frontier contains a full NP-complete core.

## 10. Updated frontier

The realizability bifurcation is resolved on the PASS side.

Do not spend effort searching for a hidden structural restriction excluding arbitrary Positive 1-in-3.

The next universal mechanism must directly attack an NP-complete composition layer.

Useful remaining targets must therefore provide a genuine P=NP-level contraction, for example:

- a polynomial global compatibility certificate that collapses the orientation-coupled NAE network into a common Schaefer lane;
- a witness-preserving ranked quotient with strict global progress;
- a representation change that destroys the hard source-variable coupling rather than renaming it;
- a multi-block contraction not expressible as local state merging.

## 11. Ceiling

JANUS DIRECT ONE-BLOCK 1-IN-3 SIDE IMAGE = IMPOSSIBLE UNDER COMPLEMENT-CLOSED CONSTANT-FREE INTERFACE
JANUS ARBITRARY POSITIVE 1-IN-3 NETWORK REALIZABILITY = PASS
OVERHEAD = LINEAR
WITNESS ENCODE/DECODE = PASS
JANUS THREE-STATE FRONTIER CONTAINS FULL NP-COMPLETE CORE = PASS
P_EQ_NP = NOT PROVED
D1 = EMPTY
P_VS_NP = OPEN
