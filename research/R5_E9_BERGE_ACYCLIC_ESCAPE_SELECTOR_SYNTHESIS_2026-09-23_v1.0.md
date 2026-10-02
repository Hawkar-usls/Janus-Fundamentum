# R5 E9 — Berge-Acyclic Escape-Selector Synthesis

**Date:** 2026-09-23  
**Status:** exact positive island for the escape-selector synthesis gate.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Input

Let H=(V,E) be a linear 3-uniform NAE hypergraph.

Fix:
- a known model y of the NAE instance;
- a pivot p that must be flipped;
- a protected set A whose variables must not be flipped.

For each edge e, relative to y let:
- m_e be the minority vertex;
- u_e,v_e be the two majority vertices.

A repair mask W subseteq V is valid exactly when, for every edge e,

W cap e != {m_e}
and
W cap e != {u_e,v_e}.

Equivalently y xor 1_W is again a NAE model.

The escape-selector theorem established earlier says that a valid W with

p in W,
W cap A = empty

exists iff there is an escape selector sigma such that

Closure_sigma({p}) cap A = empty.

## 2. Repair-mask CSP

Introduce one Boolean h_v for each v in V.

For edge e=(m;u,v), the local repair relation is

Q_e
=
{0,1}^3 \ {100,011},

where coordinates are ordered (m,u,v).

Add unary domains:
- h_p=1;
- h_a=0 for every a in A;
- all other h_v in {0,1}.

Then:

GOOD REPAIR MASK
iff
the resulting Boolean CSP is satisfiable.

Each factor table has only six tuples.

## 3. Acyclicity specialization

For linear hypergraphs, alpha-acyclicity is equivalent to Berge-acyclicity: the incidence factor graph is a forest.

Thus on the linear JANUS repair instances, an acyclic dependency component can be recognized by testing whether its bipartite incidence graph is a forest.

This gives a particularly simple exact synthesis algorithm.

## 4. Linear-time factor-tree messages

Consider the connected incidence component containing p; all other components may use the zero repair mask because y is already a model there.

Root the bipartite incidence tree at variable p.

### Variable -> edge message

For a variable v with parent edge e, let

M_{v->e}
subseteq {0,1}

contain exactly those values b allowed by the unary domain of v and by every child-factor message.

Because the domain is Boolean, each message has size at most two.

### Edge -> variable message

For an edge factor e with parent variable v, enumerate the at most four assignments to the other two variables consistent with their incoming messages.

A value b for v is retained iff one such pair creates a tuple in Q_e.

Again the message has size at most two.

### Root decision

At root p require value 1.

If 1 survives all child-factor messages, backtrack through stored local witnesses and obtain a full repair mask W.

Otherwise no protected-set-avoiding repair mask exists.

Every factor performs only constant work after its child messages are known.

Hence the algorithm is linear in the incidence size.

This is the Boolean bounded-arity specialization of the standard join-tree/Yannakakis algorithm for acyclic CSPs.

## 5. Deterministic synthesis of sigma from W

Once W is constructed:

For every edge e=(m;u,v):

- if m in W, validity of W forbids W cap e={m}; therefore at least one of u,v lies in W. Choose the lexicographically first such majority vertex as sigma(e);
- if m notin W, choose the lexicographically first of u,v.

### Closure containment lemma

Starting with S={p}, every monotone closure step preserves S subseteq W.

Proof by induction.

E1:
if m in S subseteq W, the synthesis rule chose sigma(e) in W, so adding sigma(e) stays inside W.

E2:
if u,v in S subseteq W, validity of W forbids W cap e={u,v}; hence m in W, so adding m stays inside W.

Therefore:

Closure_sigma(p) subseteq W.

Since W cap A=empty,

Closure_sigma(p) cap A=empty.

Thus the algorithm synthesizes a valid escape selector, not merely a repair mask.

## 6. Exact theorem

### Theorem BAES-1

For every linear Berge-acyclic 3-uniform NAE repair instance with known model y, pivot p and protected set A, one can deterministically decide and, when possible, synthesize an escape selector sigma satisfying

Closure_sigma(p) cap A=empty

in time linear in the incidence size.

No selector enumeration is used.

## 7. Importance and ceiling

PASS:

ACYCLIC / JOIN-TREE ESCAPE-SELECTOR SYNTHESIS
=
POLYNOMIAL EXACT.

But the obstruction is not merely “a cycle”.

The DDD k=3 family is polynomial despite potentially cyclic linear hypergraphs, while k>=4 is NP-complete under the stronger regular/perfect-matching restrictions.

Therefore:

CYCLE PRESENT
!=
HARDNESS CERTIFICATE.

Acyclicity gives the first positive island for structural selector synthesis, but the next frontier must identify a richer cyclic interaction invariant.

## 8. New immediate comparison gate

### R5_E9_ESCAPE_SELECTOR_CYCLIC_INTERACTION_CENSUS_V1

Compare:
1. Berge-acyclic repair instances — exact selector synthesis PASS;
2. polynomial cyclic controls (especially degree-3 linear NAE);
3. DDD degree-4 hard benchmark.

Measure:
- incidence-cycle structure;
- overlap of closure obligations;
- minimum/maximum selector feedback depth;
- irredundant DP charge;
- square-condenser structure;
- translation quotient dimension;
- protected-set interaction.

The next new repair rule may only be promoted from a motif that separates the cyclic polynomial controls from the DDD hard survivors.

D1 = EMPTY.  
P_VS_NP = OPEN.
