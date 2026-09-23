# R5 E9 — Leaf Projection to Binary Repair Core

**Date:** 2026-09-23  
**Status:** exact JANUS-derived polynomial selector-synthesis island.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Motivation

Berge-acyclic repair dependencies are polynomial because the entire repair-mask CSP is a factor tree.

But full acyclicity is stronger than necessary.

The repair factors have arity three and Boolean domain. Therefore tree-like fringe variables can be existentially projected exactly before any global search.

If all genuine ternary interaction disappears after this peeling, the remaining instance is merely a Boolean binary CSP and is therefore reducible to 2-SAT.

## 2. Input repair CSP

As in the escape-selector framework, fix:
- a known NAE model y;
- pivot p with h_p=1;
- protected set A with h_a=0;
- one repair factor per NAE edge e.

For oriented edge e=(m;u,v), the local repair relation is

Q_e={0,1}^3\{100,011}.

A satisfying repair assignment h is exactly a valid repair mask.

## 3. Exact leaf projection

Maintain:
- one explicit relation table for each current factor, arity at most 3;
- one Boolean domain D_v subseteq {0,1} for each live variable;
- a typed inverse reconstruction stack.

Whenever a live variable x occurs in at most one non-unary factor:

### Degree zero

Choose its unique forced value if D_x is singleton; otherwise choose a deterministic canonical value.

Record the choice and remove x.

### Degree one

Let R(x,Y) be its unique incident factor.

Filter R by D_x and the current domains of Y, then compute

R'(Y)=exists x R(x,Y).

Because R has at most eight tuples, projection is constant-time.

For every tuple a in R', store one deterministic witness value w_x(a) such that

R(w_x(a),a)=1.

Append the inverse record

(Y assignment a) -> x=w_x(a).

Replace R by R'.

If R' is unary, intersect it into the remaining variable domain and delete the factor.

After every successful projection, continue deterministically until no variable of factor-degree <=1 remains.

## 4. Reconstruction theorem

Every leaf-projection step preserves repair-mask existence exactly.

Given any satisfying assignment of the post-state, reverse the stored records.

At a projection record for x, the values of the surviving scope Y are already known because reconstruction is reversed.

Lookup w_x(Y) and restore x.

Thus every post-state repair witness lifts in polynomial time to a valid pre-state repair mask.

## 5. Binary-core theorem

Suppose the deterministic leaf-projection closure reaches a residual in which every surviving factor has arity at most two.

Then repair-mask existence and construction are polynomial.

For every binary factor R(x,z), each forbidden pair (a,b) is encoded by the 2-CNF clause

(x != a) OR (z != b).

A Boolean binary relation excludes at most four pairs, hence contributes at most four binary clauses.

Unary domains contribute unit clauses.

Therefore the residual is exactly a 2-SAT instance of linear size.

Solve it by the implication graph / SCC algorithm, then replay the leaf-projection records in reverse.

### Theorem LPBC-1

If the ternary repair core is empty after deterministic exact leaf projection, then protected-set-avoiding repair-mask synthesis is polynomial.

Combining with the previously proved repair-mask -> escape-selector construction yields polynomial escape-selector synthesis.

## 6. Strict extension beyond the acyclic island

Berge-acyclic factor graphs are included: repeated leaf projection eliminates the whole connected component.

But LPBC-1 is strictly broader.

Example shape:
- several ternary repair factors form a cycle through two variables each;
- every factor has one tree-leaf variable.

Projecting those leaf variables converts every ternary factor to a binary relation.
The remaining cyclic binary CSP is still 2-SAT-solvable.

Therefore:

FACTOR-GRAPH CYCLE
!=
OBSTRUCTION.

The relevant obstruction is survival of a genuine ternary interaction core after exact fringe projection.

## 7. New structural object

Define

TCORE(F;y,p,A)

as the deterministic residual repair CSP after leaf projection and unary cleanup.

The next structural census records:

- number of surviving variables;
- number of surviving ternary factors;
- binary factor graph;
- ternary-factor incidence degrees;
- protected/pivot domains;
- chi_min inherited from the original CNF;
- translation-action quotient status.

The first new selector rule should target a motif that survives in TCORE.

## 8. Primary hard control

For a connected linear 4-regular 3-uniform DDD NAE instance:

- every variable has factor degree 4;
- every factor has arity 3;
- no leaf projection is initially available.

After the global complement quotient only unary canonical information changes; the regular ternary incidence core remains.

Thus DDD NAE4 survives this positive island intact.

## 9. Execution evidence

An executable prototype was cross-checked against exhaustive repair-mask search on 602 random small instances for which the ternary core vanished.

Result:

LPBC repair existence/reconstruction = 602/602 exact matches.

This is finite validation, not an asymptotic proof; the asymptotic guarantee is given by the exact projection theorem plus 2-SAT reduction above.

## 10. Updated gate

### R5_E9_TERNARY_REPAIR_CORE_ACTION_GATE_V1

Run, in order:

1. translation-action quotient;
2. deterministic leaf projection;
3. binary-core extraction/2-SAT solve where possible.

Only if a genuine ternary core survives may a new nonlocal selector/action rule be invoked.

Target:

synthesize a polynomial structural contraction of the surviving ternary core without solving the full shifted NAE repair CSP by search.

D1 = EMPTY.  
P_VS_NP = OPEN.
