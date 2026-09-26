# R5 E9 — Harries Nullity-Amplifying 2-Lift Filtered Family

Date: 2026-09-26

Authority:
JANUS_DERIVED_EXPLICIT_FILTERED_FAMILY_AFTER_PA0025_NM0029_NM0030__NO_HARDNESS_OR_SOLVER_CLAIM

Authorizing audit:
PA-0025-FILTERED-HIGH-NULLITY-GRAPH-COVER

Predecessors:
NM-0028-HIGH-GIRTH-ODD-HOLE-SPARSE-ATTACHMENT,
NM-0029-COPRIME-COVER-PHASE-PERSISTENCE,
NM-0030-POLYSIZE-2GROUP-FIXED-GIRTH-COVER.

Checker:
experiments/r5_e9_harries_nullity_amplifying_2lift_family.py

## 1. Stronger explicit route

NM-0030 leaves two obligations for the filtered family: a superlog-nullity
noncommuting phase-FAIL base family, and preservation of a specified 10-cycle.
Both are satisfied by one Harries-seeded 2-lift construction.

## 2. Harries seed

Use the Harries (3,10)-cage and NM-0028 frozen incidence 10-cycle

~~~text
0-1-2-3-4-5-6-7-40-41-0.
~~~

The ordinary 35x35 biadjacency matrix A0 is nonsingular over Q.

The checker deterministically decomposes the cubic bipartite edges into three
perfect matchings, normalizes the first to I and verifies for the resulting P,Q

~~~text
PQ != QP
Z3 phase = FAIL.
~~~

## 3. Explicit connected singular 2-lift

Sign exactly the incidence edges

~~~text
{0,1}, {3,4}, {58,59}
~~~

negative.

The signed biadjacency A_sigma has

~~~text
rank_Q(A_sigma)=33
nullity_Q(A_sigma)=2.
~~~

The signing is unbalanced: the 10-cycle

~~~text
58-45-44-31-30-17-16-3-2-59-58
~~~

contains exactly one negative edge. Hence the 2-lift is connected.

On the frozen NM-0028 10-cycle exactly two edges are negative, so it has
positive sign and lifts to actual 10-cycles.

For a bipartite 2-lift the rational fiber sum/difference basis changes the
lifted biadjacency to A0 direct-sum A_sigma. Therefore the first lift has

~~~text
d1 = 0 + 2 = 2.
~~~

It is connected, cubic, bipartite, girth 10 and retains the sparse NM-0028
conflict C5. NM-0029 preserves phase FAIL and noncommutativity.

## 4. Recursive lift

At stage t>=1 let C_t be the distinguished incidence 10-cycle and A_t have
nullity d_t.

Choose the lexicographically first nonbridge edge e_t outside C_t and make it
the unique negative edge.

Such an edge exists. With n_t variables a connected cubic incidence graph has
cycle-space dimension

~~~text
3n_t - 2n_t + 1 = n_t + 1 > 1.
~~~

If every nonbridge edge lay on C_t, the cycle space would have dimension at
most one.

Since e_t is nonbridge it lies on a cycle. With e_t the unique negative edge,
that cycle is negative, so the next 2-lift is connected.

All edges of C_t are positive, so C_t lifts to two 10-cycles. Covers cannot
decrease girth, hence girth remains at least 10 and NM-0028 sparse odd-hole
geometry persists.

## 5. Nullity amplification

The signed biadjacency is

~~~text
A_t^sigma = A_t - 2 e_r e_c^T.
~~~

This is rank one, so

~~~text
nullity(A_t^sigma) >= d_t - 1.
~~~

The 2-lift old/new block decomposition gives

~~~text
d_(t+1)
= d_t + nullity(A_t^sigma)
>= 2 d_t - 1.
~~~

Since d1=2,

~~~text
d_t >= 2^(t-1)+1.
~~~

The number of variables is n_t=35*2^t. Therefore

~~~text
d_t >= n_t/70 + 1.
~~~

The family has linear rational nullity, hence omega(log n_t).

## 6. Filtered promises

Every step is a degree-2 labelled cover using the inherited three perfect
matchings. NM-0029 gives phase FAIL and noncommutativity at every stage.

The preserved 10-cycle plus girth>=10 gives the NM-0028 sparse induced conflict
C5 at every stage.

Every member is still an untouched cubic source, so NM-0027 gives
|N(I)|>=2|I|. The induced C5 blocks the perfect-graph terminal and its true
claw centers block the claw-free terminal.

No claim is made that every other known or future polynomial reduction fails.

## 7. Verdict

~~~text
NM-0031
HARRIES NULLITY-AMPLIFYING 2-LIFT FILTERED FAMILY
=
PASS

CONNECTED CUBIC POSITIVE EXACT-ONE
=
YES

GIRTH >= 10
=
YES

SPARSE INDUCED CONFLICT C5
=
YES AT EVERY STAGE

RATIONAL NULLITY
=
Omega(n)
>= n/70 + 1

P,Q NONCOMMUTING
=
YES AT EVERY STAGE

Z3 PHASE
=
FAIL AT EVERY STAGE

PA-0025 FILTERED FAMILY EXISTENCE
=
CLOSED / CONSTRUCTED

HARDNESS
=
NOT CLAIMED

UNIVERSAL SOLVER
=
NOT PROVED

D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT PROVED
~~~

The next gate is to run the complete current polynomial preprocessor stack
against finite prefixes of this explicit family and identify the first rule
that still contracts it, or certify a stable reduction-lean pattern.
