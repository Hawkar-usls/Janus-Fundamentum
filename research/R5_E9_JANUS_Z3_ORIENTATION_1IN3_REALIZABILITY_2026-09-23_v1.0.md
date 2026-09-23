# R5 E9 — JANUS Z3 Orientation-Lift Realizability of Positive 1-in-3

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_REALIZABILITY_PASS__FULL_NP_COMPLETE_CORE_REACHED__NO_P_EQ_NP_CLAIM

Parents:
- R5_E9_JANUS_1IN3_REALIZABILITY_GATE_V1
- R5_E9_BOOLEAN_SLICE_TWO_STATE_THRESHOLD_2026-09-23_v1.0
- R5_E9_TORSION_SIDE_CODE_COMPOSITION_BARRIER_2026-09-23_v1.0

Checker:
experiments/r5_e9_janus_z3_orientation_1in3_realizability.py

## 1. A universal self-duality invariant for unpinned signed-NAE side images

Consider any signed NAE3 row with literal truth values l1,l2,l3.
On every satisfying assignment their sum is 1 or 2.

The JANUS row-side bit is

s = (l1+l2+l3)-1.

Equivalently, s is the majority value of the three signed literals.

Complement every underlying primal Boolean variable.
Every signed literal truth value flips, so the new literal sum is

3-(l1+l2+l3).

Hence the new side bit is

s' = [3-(l1+l2+l3)]-1 = 1-s.

Signed NAE itself is preserved by this global complement.

Therefore for every unpinned signed-NAE block, if side vector s is realizable then its bitwise complement 1-s is realizable.

### Theorem SD-1

Every unpinned JANUS signed-NAE side-image relation is self-dual/complement-closed.

Equality identification and existential quantification preserve this global complement symmetry as long as no absolute 0/1 pin is inserted.

## 2. Why direct three-state 1-in-3 cannot appear

The Positive 1-in-3 relation is

R_1/3={100,010,001}.

Its complement is

{011,101,110},

which is disjoint from R_1/3.

Thus R_1/3 is not self-dual.

By SD-1:

NO unpinned signed-NAE/SNF side block, of any size, can expose exactly R_1/3 on three side coordinates.

This strengthens the previous finite direct census from a bounded negative control to an exact all-size impossibility theorem for the unoriented direct-block ansatz.

## 3. The correct self-dual orientation lift

Introduce one orientation bit q and define

G(q,a,b,c)

iff

a+b+c = 1+q

over ordinary integers with q,a,b,c Boolean.

Thus:

q=0 -> exactly one of a,b,c is 1;
q=1 -> exactly two of a,b,c are 1.

G contains six tuples and is self-dual:

(q,a,b,c) in G
iff
(1-q,1-a,1-b,1-c) in G.

If source Boolean values are decoded as

alpha_a=a XOR q,
alpha_b=b XOR q,
alpha_c=c XOR q,

then

G(q,a,b,c)
iff
exactly one of alpha_a,alpha_b,alpha_c is 1.

## 4. An actual four-row JANUS signed-NAE/SNF block

Use four internal Boolean variables x=(x0,x1,x2,x3).

Take the signed incidence matrix

B =
[[-1,-1,-1, 0],
 [ 1, 1, 0,-1],
 [ 1, 0, 1,-1],
 [ 0, 1, 1,-1]].

The four signed NAE rows are therefore:

NAE(not x0, not x1, not x2),
NAE(x0, x1, not x3),
NAE(x0, x2, not x3),
NAE(x1, x2, not x3).

The lower-level vector is

ell=(-2,0,0,0).

For the four row-side bits s=(q,a,b,c), the exact row equations are

B x = ell + s.

The checker proves:

det(B)=-3,
SNF(B)=diag(1,1,1,3).

So this is literally a Z3 torsion block in the signed-NAE/SNF pipeline.

## 5. Exact Z3 torsion character

A left null character modulo 3 is

w=(1,2,2,2).

It satisfies

w^T B = 0 mod 3.

Also

w dot ell = 1 mod 3.

Therefore integer liftability forces

q + 2a + 2b + 2c = 2 mod 3.

Equivalently

a+b+c-q = 1 mod 3.

On Boolean q,a,b,c, the exact realizable slice is

a+b+c = 1+q.

The checker exhaustively verifies that:

- exactly the six tuples of G occur;
- every such side tuple has a unique Boolean internal lift x;
- no other side tuple is feasible.

Thus the abstract Z3 atom is not merely representable in principle: the orientation-lift is realized by an explicit full-rank signed-NAE/SNF block.

## 6. Polynomial embedding of arbitrary Positive 1-in-3

Let J be an arbitrary Positive 1-in-3-SAT instance with source variables v and clauses C=(u,v,w).

Construct a JANUS side network N(J):

1. create one global side variable q;
2. create one side variable t_v for every source variable v;
3. for every source clause (u,v,w), instantiate one fresh copy of the four-row Z3 block;
4. identify that block's four exposed side coordinates with

(q,t_u,t_v,t_w);

5. all internal x variables of different clause blocks are fresh.

Only equality/variable-identification of exposed side coordinates is used for occurrence sharing.
This is exactly the same side-coordinate gluing interface already admitted by the two-state composition framework.

## 7. Exactness

### Forward witness map

If alpha satisfies J, choose

q=0,
t_v=alpha_v.

Every source clause has exactly one t-bit equal to 1, hence its four exposed bits satisfy G.
The checker/the block inverse gives a Boolean internal lift for each clause block.

### Reverse witness map

Given any JANUS network witness, define

alpha_v = t_v XOR q.

For every clause, G(q,t_u,t_v,t_w) implies exactly one of

alpha_u,alpha_v,alpha_w

is 1.

Therefore alpha satisfies J.

Hence

J in SAT
iff
N(J) in SAT.

## 8. Complexity contract

For a source instance with n variables and m clauses:

- side variables: n+1;
- internal block variables: 4m;
- signed NAE rows: 4m;
- block construction: O(m);
- equality sharing: O(total occurrences);
- source-to-JANUS witness map: O(n+m);
- JANUS-to-source decoding: O(n);
- block lift verification: constant work per clause.

No SAT oracle, correct representative, or satisfying target witness is used during construction.

Thus all R1-R6 requirements of R5_E9_JANUS_1IN3_REALIZABILITY_GATE_V1 pass.

## 9. Source-theoretic interpretation

The relation NAE3 is a standard base for the Boolean self-dual co-clone IN2: primitive-positive constructions from NAE3 generate self-dual Boolean relations.

The explicit block above is stronger for JANUS purposes because it avoids relying on an existential co-clone theorem: it gives the actual determinant-3/SNF block, exact side coordinates, exact decoder, and constant-size occurrence gadget.

## 10. Consequence

### Theorem J1IN3-REAL

Arbitrary Positive 1-in-3-SAT embeds with linear overhead into the admissible JANUS signed-NAE/SNF torsion-side network language under side-coordinate identification.

Therefore the JANUS three-state/torsion-side frontier contains a full NP-complete core.

This does NOT prove P=NP.

It proves that any universal polynomial breaker for this entire side-network layer, with exact witness reconstruction and the previously frozen lifecycle contract, would already yield a polynomial algorithm for Positive 1-in-3-SAT and hence would constitute a P=NP-level breakthrough.

## 11. Frontier update

R5_E9_JANUS_1IN3_REALIZABILITY_GATE_V1
=
PASS.

The earlier direct-unoriented three-state target is impossible by self-duality, but one global orientation bit is sufficient and is realized by an actual Z3 block.

The active frontier is no longer a realizability question.

Freeze:

R5_E9_JANUS_FULL_1IN3_CORE_BREAKER_GATE_V1.

Any claimed breaker must work on the explicit network produced above and obey:

- SAT equivalence;
- polynomial witness decode;
- polynomial total lifecycle;
- strict progress or entry into a globally common Schaefer lane;
- no hidden 3-way selector;
- no 2-bit renaming of the same choice;
- no branching on the surviving state;
- no assumed correct representative;
- no context-independent merge of CTX-distinguishable states.

## 12. Ceiling

DIRECT UNORIENTED R_1/3 SIDE BLOCK = IMPOSSIBLE BY SELF-DUALITY
ORIENTATION-LIFT G = ACTUAL DET-3 / Z3 JANUS SIDE BLOCK
ARBITRARY POSITIVE 1-IN-3 JANUS REALIZABILITY = PASS
JANUS THREE-STATE LAYER CONTAINS FULL NP-COMPLETE CORE = PROVED
UNIVERSAL POLY BREAKER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT_PROVED
