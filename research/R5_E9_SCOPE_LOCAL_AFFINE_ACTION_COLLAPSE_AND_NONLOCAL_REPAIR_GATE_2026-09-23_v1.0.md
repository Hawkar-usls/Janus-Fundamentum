# R5 E9 — Scope-Local Affine Action Collapse on Linear NAE3

**Date:** 2026-09-23  
**Status:** exact JANUS-derived ceiling theorem.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Setting

Let H=(V,E) be a connected linear 3-uniform hypergraph with minimum vertex degree at least two.

Consider the positive NAE instance

[
F_H=igwedge_{ein E}operatorname{NAE}(x_e).
]

Let

[
	au(y)=My+b
]

be an invertible affine map over (mathbb F_2^V).

Call (	au) **scope-local** if, for every vertex v and every hyperedge e containing v, the output coordinate (	au_v(y)) depends only on the variables indexed by e.

For an affine map this means

[
operatorname{supp}(M_{v,*})subseteq e
]

for every incident edge e.

## 2. Linearity forces diagonal support

Fix a vertex v.

Because degree(v)>=2, choose two distinct incident edges e,f.

Linearity of H implies

[
ecap f={v}.
]

Scope-locality gives

[
operatorname{supp}(M_{v,*})
subseteq ecap f
=
{v}.
]

Hence every row of M has support contained in its own diagonal coordinate.

So M is diagonal.

Over (mathbb F_2), invertibility forces every diagonal entry to equal 1.

Therefore

[
M=I.
]

Thus every invertible scope-local affine action is actually a pure translation

[
	au(y)=y+b.
]

## 3. NAE preservation collapses translations to component complement

A translation preserves one NAE3 constraint on edge e iff

[
b|_ein{000,111}.
]

Hence b is constant on every hyperedge.

Because the hypergraph is connected, this implies b is constant on all vertices:

[
b=0^V
quad	ext{or}quad
b=1^V.
]

### Theorem SLA-NAE

For every connected linear 3-uniform hypergraph with minimum degree >=2,

[
oxed{
operatorname{AffAut}_{m scope-local}(F_H)
=
{mathrm{id},mathrm{global complement}}.
}
]

The theorem is unconditional and purely structural.

## 4. Consequence for the DDD NAE4 benchmark

The connected linear 4-regular NAE3 hard benchmark satisfies the hypotheses.

Therefore:

- local NAE relation automorphisms that mix the three coordinates do exist in isolation;
- they cannot be glued into a global scope-local affine repair on the overlapping instance;
- after quotienting the one global complement dimension, **no nontrivial scope-local affine action remains**.

So the next repair action cannot come from simply enlarging:

[
	ext{XOR translations}
longrightarrow
	ext{scope-local affine maps}.
]

That route collapses exactly back to the translation calculus.

## 5. Why this matters for JANUS

The failure is caused by overlap geometry:

[
	ext{rich local action group}
+
	ext{linear multi-edge overlap}
Longrightarrow
	ext{global action rigidity}.
]

This is a direct analog of earlier sheet/gauge synchronization barriers, but now at the witness-action level.

It identifies the next required mechanism class:

[
oxed{	ext{NONLOCAL / CONDITIONAL REPAIR}}
]

where output variable values may depend on information propagated through the incidence structure, rather than only their own local constraint scopes.

## 6. First propagation control

A natural candidate is Kempe-like repair:

1. canonical complement has already fixed one anchor variable;
2. to fix another pivot, flip it;
3. every NAE edge made monochromatic emits a repair obligation;
4. repair the edge by flipping another vertex;
5. propagate until all constraints are restored.

A deterministic lexicographic single-vertex version of this procedure already cycles on a 12-variable linear four-partition NAE instance after two repairs.

Therefore naive local propagation does not provide a well-founded rank automatically.

This is only a counterexample to that frozen greedy policy, not to all propagation-based repair.

## 7. Updated action hierarchy

Current exact action layers:

1. **translation stabilizer quotient** — polynomial; removes dim H;
2. **scope-local affine extension** — collapses to layer 1 on connected linear NAE3;
3. **naive single-defect propagation** — frozen deterministic version has explicit cycles;
4. **missing layer** — nonlocal conditional repair with a proved global rank / potential.

## 8. New subgate

### R5_E9_NONLOCAL_REPAIR_PROPAGATION_RANK_GATE_V1

On a translation-rigid connected WDR survivor:

construct in polynomial time a conditional repair process whose obligations may propagate nonlocally, together with a polynomially represented well-founded rank (ho), such that every repair strictly decreases (ho) and eventually fixes at least one Boolean dimension.

Forbidden:
- local greedy repair without rank;
- semantic search for a target witness;
- exponential exploration of repair paths;
- hidden SAT/reconfiguration oracle.

Primary benchmark:
connected DDD linear 4-regular NAE3 after global-complement canonicalization.

D1 = EMPTY.  
P_VS_NP = OPEN.
